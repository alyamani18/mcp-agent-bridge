#!/usr/bin/env python3
"""
Base class for HTTP→STDIO MCP proxies.
Proxies HTTP MCP requests to STDIO MCP servers (CLI tools).

Author: Wojciech Wiesner
"""
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTTPToSTDIOProxy(ABC):
    """
    Abstract base class for proxying HTTP MCP requests
    to STDIO MCP servers (CLI tools).

    Subclasses must implement:
    - get_tools(): Return tool definitions
    - handle_tool_call(): Handle incoming tool calls
    """

    def __init__(
        self,
        name: str,
        port: int,
        cli_command: list[str],
        timeout: float = 300.0
    ):
        """
        Initialize the HTTP→STDIO proxy.

        Args:
            name: Proxy server name
            port: HTTP port to listen on
            cli_command: Command to start CLI tool MCP server
            timeout: Request timeout in seconds
        """
        self.name = name
        self.port = port
        self.cli_command = cli_command
        self.timeout = timeout
        self.mcp = FastMCP(name)
        self.process: Optional[asyncio.subprocess.Process] = None
        self._request_id = 0
        self._setup_tools()

    def _setup_tools(self):
        """Setup MCP tools from subclass definitions."""
        for tool_def in self.get_tools():
            self._register_tool(tool_def)

    def _register_tool(self, tool_def: dict):
        """Register a single tool with FastMCP."""
        name = tool_def["name"]
        description = tool_def.get("description", "")

        @self.mcp.tool(name=name, description=description)
        async def tool_handler(**kwargs):
            return await self.handle_tool_call(name, kwargs)

    @abstractmethod
    def get_tools(self) -> list[dict]:
        """
        Return tool definitions to expose.

        Returns:
            List of tool definition dicts with 'name', 'description', 'parameters'
        """
        pass

    @abstractmethod
    async def handle_tool_call(self, name: str, arguments: dict) -> str:
        """
        Handle incoming tool call.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result as string
        """
        pass

    async def start_subprocess(self):
        """Start the CLI tool as MCP server subprocess."""
        if self.process is not None:
            logger.warning("Subprocess already running")
            return

        logger.info(f"Starting subprocess: {' '.join(self.cli_command)}")

        self.process = await asyncio.create_subprocess_exec(
            *self.cli_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Initialize the MCP session
        await self._initialize_subprocess()

    async def _initialize_subprocess(self):
        """Initialize MCP session with subprocess."""
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": f"{self.name}-proxy", "version": "1.0"}
            },
            "id": self._next_id()
        }

        response = await self.send_to_subprocess(init_request)
        logger.info(f"Subprocess initialized: {response}")

        # Send initialized notification
        await self.send_to_subprocess({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })

    def _next_id(self) -> int:
        """Generate next request ID."""
        self._request_id += 1
        return self._request_id

    async def send_to_subprocess(self, request: dict) -> Optional[dict]:
        """
        Send JSON-RPC request to subprocess.

        Args:
            request: JSON-RPC request dict

        Returns:
            JSON-RPC response dict, or None for notifications
        """
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("Subprocess not started")

        # Write request with newline delimiter
        request_bytes = json.dumps(request).encode() + b'\n'
        self.process.stdin.write(request_bytes)
        await self.process.stdin.drain()

        # Notifications don't have responses
        if "id" not in request:
            return None

        # Read response
        if self.process.stdout is None:
            raise RuntimeError("Subprocess stdout not available")

        try:
            response_line = await asyncio.wait_for(
                self.process.stdout.readline(),
                timeout=self.timeout
            )
            return json.loads(response_line.decode())
        except asyncio.TimeoutError:
            logger.error("Subprocess response timeout")
            raise

    async def call_subprocess_tool(self, name: str, arguments: dict) -> str:
        """
        Call a tool on the subprocess MCP server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result as string
        """
        if self.process is None:
            await self.start_subprocess()

        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            },
            "id": self._next_id()
        }

        response = await self.send_to_subprocess(request)

        if response is None:
            raise RuntimeError("No response from subprocess")

        if "error" in response:
            raise Exception(f"Subprocess error: {response['error']}")

        if "result" in response:
            content = response["result"].get("content", [])
            if content and len(content) > 0:
                first = content[0]
                if isinstance(first, dict):
                    return first.get("text", str(first))
                return str(first)

        return str(response)

    async def stop_subprocess(self):
        """Stop the subprocess gracefully."""
        if self.process is None:
            return

        logger.info("Stopping subprocess...")

        try:
            self.process.terminate()
            await asyncio.wait_for(self.process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Subprocess did not terminate, killing...")
            self.process.kill()
            await self.process.wait()

        self.process = None

    def run(self, host: str = "0.0.0.0"):
        """
        Start the HTTP MCP server.

        Args:
            host: Host to bind to
        """
        logger.info(f"Starting {self.name} HTTP proxy on {host}:{self.port}")

        # Start subprocess before running server
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.start_subprocess())
            self.mcp.run(transport="http", host=host, port=self.port)
        finally:
            loop.run_until_complete(self.stop_subprocess())
            loop.close()
