#!/bin/bash
# Stop all MCP Agent Bridge proxies
# Author: Wojciech Wiesner

echo "Stopping MCP Agent Bridge proxies..."

# Stop Codex proxy
if [ -f "/tmp/codex-mcp-proxy.pid" ]; then
    CODEX_PID=$(cat /tmp/codex-mcp-proxy.pid)
    if kill -0 "$CODEX_PID" 2>/dev/null; then
        echo "Stopping Codex proxy (PID: $CODEX_PID)..."
        kill "$CODEX_PID"
    fi
    rm -f /tmp/codex-mcp-proxy.pid
fi

# Stop Claude proxy
if [ -f "/tmp/claude-mcp-proxy.pid" ]; then
    CLAUDE_PID=$(cat /tmp/claude-mcp-proxy.pid)
    if kill -0 "$CLAUDE_PID" 2>/dev/null; then
        echo "Stopping Claude proxy (PID: $CLAUDE_PID)..."
        kill "$CLAUDE_PID"
    fi
    rm -f /tmp/claude-mcp-proxy.pid
fi

# Kill any remaining proxy processes
pkill -f "codex_mcp_proxy.py" 2>/dev/null || true
pkill -f "claude_mcp_proxy.py" 2>/dev/null || true

echo "All proxies stopped."
