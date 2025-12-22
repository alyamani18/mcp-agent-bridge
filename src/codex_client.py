#!/usr/bin/env python3
"""
Codex MCP Client for Agent Zero
Allows Agent Zero to call Codex CLI for coding tasks.

Usage in Agent Zero:
    from codex_client import codex_task
    result = await codex_task("Write a Python function to calculate fibonacci")

Author: Wojciech Wiesner
"""
import httpx
import uuid
import asyncio
from typing import Optional

CODEX_PROXY_URL = "http://192.168.100.160:50010/mcp"


class CodexClient:
    """MCP client for Codex proxy."""

    def __init__(self, url: str = CODEX_PROXY_URL):
        self.url = url
        self.session_id: Optional[str] = None
        self.timeout = 300.0

    async def _request(self, method: str, params: dict = None) -> dict:
        """Send MCP request."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": str(uuid.uuid4())
        }
        if params:
            payload["params"] = params

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.url, json=payload, headers=headers)

            # Handle SSE response
            text = response.text
            if text.startswith("event:"):
                # Parse SSE format
                for line in text.split("\n"):
                    if line.startswith("data:"):
                        import json
                        return json.loads(line[5:].strip())

            if "mcp-session-id" in response.headers:
                self.session_id = response.headers["mcp-session-id"]

            return response.json()

    async def initialize(self):
        """Initialize MCP session."""
        result = await self._request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "agent-zero-codex-client", "version": "1.0"}
        })

        # Send initialized notification
        await self._request("notifications/initialized")

        return result

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Call a Codex tool."""
        if not self.session_id:
            await self.initialize()

        result = await self._request("tools/call", {
            "name": name,
            "arguments": arguments
        })

        if "error" in result:
            return f"Error: {result['error']}"

        if "result" in result:
            content = result["result"].get("content", [])
            if content:
                return content[0].get("text", str(content[0]))

        return str(result)


async def codex_task(task: str) -> str:
    """
    Send a coding task to Codex CLI.

    Args:
        task: The coding task description

    Returns:
        Codex's response with the code
    """
    client = CodexClient()
    return await client.call_tool("codex_task", {"task": task})


async def codex_reply(message: str) -> str:
    """
    Send a follow-up message to Codex.

    Args:
        message: Follow-up message or correction

    Returns:
        Codex's response
    """
    client = CodexClient()
    return await client.call_tool("codex_reply", {"message": message})


# Test
if __name__ == "__main__":
    async def test():
        print("Testing Codex client...")
        result = await codex_task("What is 2+2? Reply with just the number.")
        print(f"Result: {result}")

    asyncio.run(test())
