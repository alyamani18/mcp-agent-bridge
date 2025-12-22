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

    def get_tools(self) -> list[dict]:
        """Return Claude tools to expose."""
        return [
            {
                "name": "claude_query",
                "description": (
                    "Send a query to Claude CLI for analysis, reasoning, "
                    "code review, or complex problem solving. "
                    "Claude will process the request with full context awareness."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The prompt or question for Claude"
                        },
                        "context": {
                            "type": "string",
                            "description": "Optional additional context"
                        }
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "claude_code_review",
                "description": (
                    "Request Claude to review code for bugs, security issues, "
                    "and best practices. Provide the code as a string."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to review"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (e.g., 'python', 'javascript')"
                        },
                        "focus": {
                            "type": "string",
                            "description": "Focus area: 'security', 'performance', 'style', or 'all'"
                        }
                    },
                    "required": ["code"]
                }
            }
        ]

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
