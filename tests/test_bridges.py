"""
Unit tests for MCP Agent Bridge

Author: Wojciech Wiesner
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base.stdio_http_bridge import STDIOToHTTPBridge
from src.base.http_stdio_proxy import HTTPToSTDIOProxy
from mcp.types import Tool


class MockSTDIOBridge(STDIOToHTTPBridge):
    """Mock implementation of STDIOToHTTPBridge for testing."""

    def get_tools(self):
        return [
            Tool(
                name="test_tool",
                description="A test tool",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    },
                    "required": ["message"]
                }
            )
        ]

    async def handle_tool_call(self, name: str, arguments: dict) -> str:
        if name == "test_tool":
            return f"Received: {arguments.get('message', '')}"
        return f"Unknown tool: {name}"


class MockHTTPProxy(HTTPToSTDIOProxy):
    """Mock implementation of HTTPToSTDIOProxy for testing."""

    def setup_tools(self):
        """Register test tools."""
        @self.mcp.tool(description="A proxy test tool")
        async def proxy_tool(input_text: str) -> str:
            return await self.handle_tool_call("proxy_tool", {"input": input_text})

    async def handle_tool_call(self, name: str, arguments: dict) -> str:
        if name == "proxy_tool":
            return f"Proxied: {arguments.get('input', '')}"
        return f"Unknown tool: {name}"


class TestSTDIOToHTTPBridge:
    """Tests for STDIOToHTTPBridge base class."""

    @pytest.fixture
    def bridge(self):
        return MockSTDIOBridge(
            name="test-bridge",
            target_url="http://localhost:50001/mcp/",
            timeout=30.0
        )

    def test_initialization(self, bridge):
        """Test bridge initializes correctly."""
        assert bridge.name == "test-bridge"
        assert bridge.target_url == "http://localhost:50001/mcp/"
        assert bridge.timeout == 30.0
        assert bridge.session_id is None

    def test_get_tools(self, bridge):
        """Test tools are returned correctly."""
        tools = bridge.get_tools()
        assert len(tools) == 1
        assert tools[0].name == "test_tool"

    @pytest.mark.asyncio
    async def test_handle_tool_call(self, bridge):
        """Test tool calls are handled correctly."""
        result = await bridge.handle_tool_call("test_tool", {"message": "hello"})
        assert result == "Received: hello"

    @pytest.mark.asyncio
    async def test_handle_unknown_tool(self, bridge):
        """Test unknown tools return error."""
        result = await bridge.handle_tool_call("unknown", {})
        assert "Unknown tool" in result

    @pytest.mark.asyncio
    async def test_initialize_session(self, bridge):
        """Test session initialization."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.headers = {"mcp-session-id": "test-session-123"}
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "result": {"protocolVersion": "2024-11-05"},
                "id": "1"
            }

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await bridge.initialize_session()

            assert bridge.session_id == "test-session-123"
            assert "result" in result


class TestHTTPToSTDIOProxy:
    """Tests for HTTPToSTDIOProxy base class."""

    @pytest.fixture
    def proxy(self):
        return MockHTTPProxy(
            name="test-proxy",
            port=50010,
            cli_command=["echo", "test"],
            timeout=30.0
        )

    def test_initialization(self, proxy):
        """Test proxy initializes correctly."""
        assert proxy.name == "test-proxy"
        assert proxy.port == 50010
        assert proxy.cli_command == ["echo", "test"]
        assert proxy.timeout == 30.0
        assert proxy.process is None

    def test_mcp_server_created(self, proxy):
        """Test MCP server is created."""
        assert proxy.mcp is not None
        assert proxy.mcp.name == "test-proxy"

    @pytest.mark.asyncio
    async def test_handle_tool_call(self, proxy):
        """Test tool calls are handled correctly."""
        result = await proxy.handle_tool_call("proxy_tool", {"input": "test"})
        assert result == "Proxied: test"

    @pytest.mark.asyncio
    async def test_handle_unknown_tool(self, proxy):
        """Test unknown tools return error."""
        result = await proxy.handle_tool_call("unknown", {})
        assert "Unknown tool" in result

    def test_next_id_increments(self, proxy):
        """Test request ID increments."""
        id1 = proxy._next_id()
        id2 = proxy._next_id()
        assert id2 == id1 + 1


class TestIntegration:
    """Integration tests."""

    @pytest.mark.asyncio
    async def test_bridge_to_proxy_communication(self):
        """Test bridge can communicate with proxy."""
        # This would require running actual servers
        # Placeholder for integration test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
