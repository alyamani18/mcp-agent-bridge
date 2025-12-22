#!/usr/bin/env python3
"""
HTTP→STDIO Proxy for Codex CLI MCP Server
Allows Agent Zero (HTTP) to call Codex CLI (STDIO).

Author: Wojciech Wiesner
"""
import asyncio
import os
import sys
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base.http_stdio_proxy import HTTPToSTDIOProxy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CODEX_PROXY_PORT = int(os.getenv("CODEX_PROXY_PORT", "50010"))


class CodexMCPProxy(HTTPToSTDIOProxy):
    """
    HTTP→STDIO proxy for Codex CLI.

    Exposes Codex CLI's MCP server tools via HTTP,
    allowing Agent Zero to submit coding tasks.
    """

    def __init__(self, port: int = CODEX_PROXY_PORT):
        super().__init__(
            name="codex-proxy",
            port=port,
            cli_command=["codex", "mcp-server"],
            timeout=300.0
        )

    def setup_tools(self):
        """Register Codex tools with FastMCP."""

        @self.mcp.tool(description="Run a Codex coding session. Codex will analyze, plan, and execute the task with full access to the local filesystem.")
        async def codex(prompt: str, model: str = "", cwd: str = "") -> str:
            """Submit a coding task to Codex CLI."""
            return await self._handle_codex(prompt, model, cwd)

        @self.mcp.tool(description="Continue a Codex conversation by providing the conversation ID and next prompt.")
        async def codex_reply(conversationId: str, prompt: str) -> str:
            """Continue a Codex conversation."""
            return await self._handle_codex_reply(conversationId, prompt)

    async def _handle_codex(self, prompt: str, model: str = "", cwd: str = "") -> str:
        """Handle codex tool call."""
        if not prompt:
            return "Error: No prompt provided"
        try:
            args = {"prompt": prompt}
            if model:
                args["model"] = model
            if cwd:
                args["cwd"] = cwd
            result = await self.call_subprocess_tool("codex", args)
            return result
        except Exception as e:
            logger.error(f"Codex error: {e}")
            return f"Error executing Codex: {str(e)}"

    async def _handle_codex_reply(self, conversationId: str, prompt: str) -> str:
        """Handle codex_reply tool call."""
        if not conversationId or not prompt:
            return "Error: Both conversationId and prompt are required"
        try:
            result = await self.call_subprocess_tool("codex-reply", {
                "conversationId": conversationId,
                "prompt": prompt
            })
            return result
        except Exception as e:
            logger.error(f"Codex reply error: {e}")
            return f"Error sending Codex reply: {str(e)}"

    async def handle_tool_call(self, name: str, arguments: dict) -> str:
        """Handle incoming tool calls."""
        logger.info(f"Codex tool call: {name} with args: {arguments}")

        if name == "codex_task":
            task = arguments.get("task", "")
            if not task:
                return "Error: No task provided"

            try:
                # Call Codex's 'codex' tool via subprocess
                result = await self.call_subprocess_tool("codex", {"task": task})
                return result
            except Exception as e:
                logger.error(f"Codex task error: {e}")
                return f"Error executing Codex task: {str(e)}"

        elif name == "codex_reply":
            message = arguments.get("message", "")
            if not message:
                return "Error: No message provided"

            try:
                result = await self.call_subprocess_tool("codex-reply", {"message": message})
                return result
            except Exception as e:
                logger.error(f"Codex reply error: {e}")
                return f"Error sending Codex reply: {str(e)}"

        else:
            return f"Unknown tool: {name}"


def main():
    """Main entry point."""
    proxy = CodexMCPProxy()
    proxy.run()


if __name__ == "__main__":
    main()
