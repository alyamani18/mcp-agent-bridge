#!/usr/bin/env python3
"""
HTTP→STDIO Proxy for Claude CLI MCP Server
Allows Agent Zero (HTTP) to call Claude CLI (STDIO).

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
CLAUDE_PROXY_PORT = int(os.getenv("CLAUDE_PROXY_PORT", "50011"))


class ClaudeMCPProxy(HTTPToSTDIOProxy):
    """
    HTTP→STDIO proxy for Claude CLI.

    Exposes Claude CLI's MCP server tools via HTTP,
    allowing Agent Zero to query Claude for analysis and reasoning.
    """

    def __init__(self, port: int = CLAUDE_PROXY_PORT):
        super().__init__(
            name="claude-proxy",
            port=port,
            cli_command=["claude", "mcp", "serve"],
            timeout=300.0
        )

    def setup_tools(self):
        """Register Claude tools with FastMCP."""

        @self.mcp.tool(description="Send a query to Claude CLI for analysis, reasoning, code review, or complex problem solving.")
        async def claude_query(prompt: str, context: str = "") -> str:
            """Query Claude CLI."""
            return await self._handle_claude_query(prompt, context)

        @self.mcp.tool(description="Request Claude to review code for bugs, security issues, and best practices.")
        async def claude_code_review(code: str, language: str = "auto", focus: str = "all") -> str:
            """Request Claude code review."""
            return await self._handle_code_review(code, language, focus)

    async def _handle_claude_query(self, prompt: str, context: str = "") -> str:
        """Handle claude_query tool call."""
        if not prompt:
            return "Error: No prompt provided"

        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nQuery:\n{prompt}"

        try:
            result = await self.call_subprocess_tool("query", {"prompt": full_prompt})
            return result
        except Exception as e:
            logger.error(f"Claude query error: {e}")
            return f"Error querying Claude: {str(e)}"

    async def _handle_code_review(self, code: str, language: str = "auto", focus: str = "all") -> str:
        """Handle claude_code_review tool call."""
        if not code:
            return "Error: No code provided"

        review_prompt = f"""Please review the following {language} code.
Focus on: {focus}

```{language}
{code}
```

Provide a structured review with:
1. Issues found (bugs, security, etc.)
2. Improvement suggestions
3. Overall assessment
"""
        try:
            result = await self.call_subprocess_tool("query", {"prompt": review_prompt})
            return result
        except Exception as e:
            logger.error(f"Claude code review error: {e}")
            return f"Error during code review: {str(e)}"

    async def handle_tool_call(self, name: str, arguments: dict) -> str:
        """Handle incoming tool calls."""
        logger.info(f"Claude tool call: {name} with args: {arguments}")

        if name == "claude_query":
            prompt = arguments.get("prompt", "")
            context = arguments.get("context", "")

            if not prompt:
                return "Error: No prompt provided"

            # Combine prompt and context
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{context}\n\nQuery:\n{prompt}"

            try:
                # Claude MCP server typically has a 'query' or similar tool
                result = await self.call_subprocess_tool(
                    "query",
                    {"prompt": full_prompt}
                )
                return result
            except Exception as e:
                logger.error(f"Claude query error: {e}")
                return f"Error querying Claude: {str(e)}"

        elif name == "claude_code_review":
            code = arguments.get("code", "")
            language = arguments.get("language", "auto")
            focus = arguments.get("focus", "all")

            if not code:
                return "Error: No code provided"

            review_prompt = f"""Please review the following {language} code.
Focus on: {focus}

```{language}
{code}
```

Provide a structured review with:
1. Issues found (bugs, security, etc.)
2. Improvement suggestions
3. Overall assessment
"""

            try:
                result = await self.call_subprocess_tool(
                    "query",
                    {"prompt": review_prompt}
                )
                return result
            except Exception as e:
                logger.error(f"Claude code review error: {e}")
                return f"Error during code review: {str(e)}"

        else:
            return f"Unknown tool: {name}"


def main():
    """Main entry point."""
    proxy = ClaudeMCPProxy()
    proxy.run()


if __name__ == "__main__":
    main()
