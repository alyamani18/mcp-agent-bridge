#!/bin/bash
# Start all MCP Agent Bridge proxies
# Author: Wojciech Wiesner

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Load environment
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create log directory
sudo mkdir -p /var/log/mcp-agent-bridge
sudo chown $USER:$USER /var/log/mcp-agent-bridge

echo "Starting MCP Agent Bridge proxies..."

# Start Codex proxy
echo "Starting Codex MCP proxy on port ${CODEX_PROXY_PORT:-50010}..."
python3 src/codex_mcp_proxy.py > /var/log/mcp-agent-bridge/codex-proxy.log 2>&1 &
CODEX_PID=$!
echo "Codex proxy PID: $CODEX_PID"

# Start Claude proxy
echo "Starting Claude MCP proxy on port ${CLAUDE_PROXY_PORT:-50011}..."
python3 src/claude_mcp_proxy.py > /var/log/mcp-agent-bridge/claude-proxy.log 2>&1 &
CLAUDE_PID=$!
echo "Claude proxy PID: $CLAUDE_PID"

# Save PIDs
echo "$CODEX_PID" > /tmp/codex-mcp-proxy.pid
echo "$CLAUDE_PID" > /tmp/claude-mcp-proxy.pid

echo ""
echo "All proxies started successfully!"
echo "Codex proxy: http://localhost:${CODEX_PROXY_PORT:-50010}"
echo "Claude proxy: http://localhost:${CLAUDE_PROXY_PORT:-50011}"
echo ""
echo "Logs: /var/log/mcp-agent-bridge/"
echo "Use ./scripts/stop_all.sh to stop all proxies"
