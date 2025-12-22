#!/usr/bin/env python3
"""
MCP STDIO Bridge for Agent Zero
Bridges CLI MCP clients (Codex, Claude, Gemini) to Agent Zero FastMCP HTTP server.

Author: Wojciech Wiesner
"""
import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.types import Tool
from src.base.stdio_http_bridge import STDIOToHTTPBridge

# Configuration from environment or defaults
AGENT_ZERO_HOST = os.getenv("AGENT_ZERO_HOST", "192.168.100.160")
AGENT_ZERO_PORT = os.getenv("AGENT_ZERO_PORT", "50001")
AGENT_ZERO_TOKEN = os.getenv("AGENT_ZERO_TOKEN", "T7kevcXi6oDxfrhK")

AGENT_ZERO_MCP_URL = f"http://{AGENT_ZERO_HOST}:{AGENT_ZERO_PORT}/mcp/t-{AGENT_ZERO_TOKEN}/http/"


class AgentZeroBridge(STDIOToHTTPBridge):
    """
    STDIO→HTTP bridge for Agent Zero.

    Allows CLI tools like Codex, Claude, and Gemini to communicate
    with Agent Zero through the Model Context Protocol.
    """

    def get_tools(self) -> list[Tool]:
        """Return Agent Zero tools to expose."""
        return [
            Tool(
                name="send_message",
                description=(
                    "Send a message to Agent Zero AI assistant. "
                    "Agent Zero can execute commands, write code, browse web, "
                    "manage files in its isolated Linux environment."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message/task to send to Agent Zero"
                        }
                    },
                    "required": ["message"]
                }
            )
        ]

    async def handle_tool_call(self, name: str, arguments: dict) -> str:
        """Handle tool invocation for Agent Zero."""
        if name != "send_message":
            return f"Unknown tool: {name}"

        message = arguments.get("message", "")
        if not message:
            return "Error: No message provided"

        try:
            result = await self.call_remote_tool("send_message", {"message": message})
            return result
        except Exception as e:
            return f"Error communicating with Agent Zero: {str(e)}"


async def main():
    """Main entry point."""
    bridge = AgentZeroBridge(
        name="agent-zero-bridge",
        target_url=AGENT_ZERO_MCP_URL,
        timeout=300.0
    )
    await bridge.run()


if __name__ == "__main__":
    asyncio.run(main())
