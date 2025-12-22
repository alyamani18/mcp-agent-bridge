#!/usr/bin/env python3
"""
Base class for STDIO→HTTP MCP bridges.
Bridges CLI MCP clients (STDIO) to HTTP MCP servers.

Author: Wojciech Wiesner
"""
import asyncio
import json
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class STDIOToHTTPBridge(ABC):
    """
    Abstract base class for bridging STDIO MCP clients
    to HTTP MCP servers.

    Subclasses must implement:
    - get_tools(): Return list of tools to expose
    - handle_tool_call(): Handle tool invocation
    """

    def __init__(
        self,
        name: str,
        target_url: str,
        timeout: float = 300.0,
        accept_header: str = "application/json, text/event-stream"
    ):
        """
        Initialize the STDIO→HTTP bridge.

        Args:
            name: Server name for MCP identification
            target_url: HTTP URL of target MCP server
            timeout: Request timeout in seconds
            accept_header: Accept header for HTTP requests
        """
        self.name = name
        self.target_url = target_url
        self.timeout = timeout
        self.accept_header = accept_header
        self.session_id: Optional[str] = None
        self.server = Server(name)
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server handlers."""

        @self.server.list_tools()
        async def list_tools():
            return self.get_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            try:
                result = await self.handle_tool_call(name, arguments)
                return [TextContent(type="text", text=result)]
            except Exception as e:
                logger.error(f"Tool call error: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    @abstractmethod
    def get_tools(self) -> list[Tool]:
        """
        Return list of tools to expose via MCP.

        Returns:
            List of Tool objects
        """
        pass

    @abstractmethod
    async def handle_tool_call(self, name: str, arguments: dict) -> str:
        """
        Handle tool invocation.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result as string
        """
        pass

    async def initialize_session(self) -> dict:
        """
        Initialize MCP session with target HTTP server.

        Returns:
            Initialize response from server
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": self.accept_header
        }

        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": self.name, "version": "1.0"}
            },
            "id": str(uuid.uuid4())
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.target_url,
                json=payload,
                headers=headers
            )

            if "mcp-session-id" in response.headers:
                self.session_id = response.headers["mcp-session-id"]
                logger.info(f"Session initialized: {self.session_id}")

            # Send initialized notification
            if self.session_id:
                headers["Mcp-Session-Id"] = self.session_id
                await client.post(
                    self.target_url,
                    json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                    headers=headers
                )

            return response.json()

    async def forward_request(
        self,
        method: str,
        params: Optional[dict] = None
    ) -> dict:
        """
        Forward JSON-RPC request to target HTTP server.

        Args:
            method: JSON-RPC method name
            params: Method parameters

        Returns:
            JSON-RPC response
        """
        if not self.session_id:
            await self.initialize_session()

        headers = {
            "Content-Type": "application/json",
            "Accept": self.accept_header,
            "Mcp-Session-Id": self.session_id
        }

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": str(uuid.uuid4())
        }

        if params:
            payload["params"] = params

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.target_url,
                json=payload,
                headers=headers
            )
            return response.json()

    async def call_remote_tool(self, name: str, arguments: dict) -> Any:
        """
        Call a tool on the remote MCP server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        result = await self.forward_request(
            "tools/call",
            {"name": name, "arguments": arguments}
        )

        if "error" in result:
            raise Exception(f"MCP Error: {result['error']}")

        if "result" in result:
            content = result["result"].get("content", [])
            if content and len(content) > 0:
                first = content[0]
                if isinstance(first, dict):
                    return first.get("text", str(first))
                return str(first)

        return str(result)

    async def run(self):
        """Start the STDIO MCP server."""
        logger.info(f"Starting {self.name} STDIO bridge...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
