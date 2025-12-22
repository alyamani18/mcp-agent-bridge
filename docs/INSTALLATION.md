# Installation Guide

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Runtime |
| pip | Latest | Package management |
| Docker | 24+ | Agent Zero container |
| Node.js | 18+ | CLI tools |
| npm | 9+ | CLI tool installation |

### Optional Software

| Software | Purpose |
|----------|---------|
| systemd | Service management |
| nginx | Reverse proxy (production) |

## Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/mcp-agent-bridge.git
cd mcp-agent-bridge
```

## Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies List

```
fastmcp>=0.1.0
httpx>=0.27.0
uvicorn>=0.30.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

## Step 3: Install CLI Tools

### OpenAI Codex CLI

```bash
npm install -g @openai/codex

# Verify installation
codex --version

# Configure API key
export OPENAI_API_KEY="your-api-key"
```

### Anthropic Claude CLI

```bash
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version

# Configure API key
export ANTHROPIC_API_KEY="your-api-key"
```

### Google Gemini CLI (Optional)

```bash
npm install -g @google/gemini-cli

# Verify installation
gemini --version

# Configure API key
export GEMINI_API_KEY="your-api-key"
```

## Step 4: Configure Agent Zero

### Get MCP Token

```bash
# If Agent Zero is running in Docker
docker exec agent-zero python3 -c "
from python.helpers.mcp_server import get_mcp_token
print(get_mcp_token())
"
```

### Verify Agent Zero MCP Endpoint

```bash
# Test connection
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":"1"}' \
  http://localhost:50001/mcp/t-YOUR_TOKEN/http/
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {...},
    "serverInfo": {"name": "agent-zero", "version": "..."}
  },
  "id": "1"
}
```

## Step 5: Configure Environment

```bash
# Copy example configuration
cp config/example.env .env

# Edit configuration
nano .env
```

### Environment Variables

```bash
# Agent Zero Configuration
AGENT_ZERO_HOST=192.168.100.160
AGENT_ZERO_PORT=50001
AGENT_ZERO_TOKEN=your-mcp-token

# Proxy Ports
CODEX_PROXY_PORT=50010
CLAUDE_PROXY_PORT=50011

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/mcp-agent-bridge/bridge.log

# Timeouts (seconds)
MCP_TIMEOUT=300
HTTP_TIMEOUT=120
```

## Step 6: Configure CLI Tools

### Codex CLI Configuration

Create/edit `~/.codex/config.toml`:

```toml
model = "gpt-4"
approval_policy = "untrusted"

[[mcp_servers]]
name = "agent-zero"
command = "python3"
args = ["/path/to/mcp-agent-bridge/src/agent_zero_mcp_stdio.py"]
```

### Claude CLI Configuration

Create/edit `~/.claude/mcp_servers.json`:

```json
{
  "agent-zero": {
    "type": "stdio",
    "command": "python3",
    "args": ["/path/to/mcp-agent-bridge/src/agent_zero_mcp_stdio.py"]
  }
}
```

### Gemini CLI Configuration

Create/edit `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "agent-zero": {
      "command": "python3",
      "args": ["/path/to/mcp-agent-bridge/src/agent_zero_mcp_stdio.py"]
    }
  }
}
```

## Step 7: Start Services

### Development Mode

```bash
# Terminal 1: Codex Proxy
python3 src/codex_mcp_proxy.py

# Terminal 2: Claude Proxy
python3 src/claude_mcp_proxy.py
```

### Production Mode (systemd)

```bash
# Install systemd services
sudo cp config/systemd/*.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable --now codex-mcp-proxy
sudo systemctl enable --now claude-mcp-proxy

# Check status
sudo systemctl status codex-mcp-proxy
sudo systemctl status claude-mcp-proxy
```

## Step 8: Verify Installation

### Test STDIO→HTTP Bridge

```bash
# Test Agent Zero bridge
echo '{"jsonrpc":"2.0","method":"tools/list","id":"1"}' | \
    python3 src/agent_zero_mcp_stdio.py
```

### Test HTTP→STDIO Proxies

```bash
# Test Codex proxy
curl -X POST http://localhost:50010/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":"1"}'

# Test Claude proxy
curl -X POST http://localhost:50011/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":"1"}'
```

### End-to-End Test

```bash
# From Codex CLI
codex "Use agent-zero to list files in /tmp"

# Expected: Agent Zero executes 'ls /tmp' and returns results
```

## Troubleshooting

### Common Issues

#### 1. "MCP token not found"

```bash
# Regenerate token
docker exec agent-zero python3 -c "
from python.helpers.mcp_server import create_new_mcp_token
print(create_new_mcp_token())
"
```

#### 2. "Connection refused on port 50001"

```bash
# Check Agent Zero container
docker ps --filter name=agent-zero

# Check port mapping
docker port agent-zero

# Restart if needed
docker restart agent-zero
```

#### 3. "Module 'mcp' not found"

```bash
# Reinstall MCP package
pip install --force-reinstall mcp httpx
```

#### 4. "STDIO bridge hangs"

```bash
# Check for blocking I/O
strace -p $(pgrep -f agent_zero_mcp_stdio)

# Increase timeout
export MCP_TIMEOUT=600
```

### Log Files

| Service | Log Location |
|---------|--------------|
| Codex Proxy | `/var/log/mcp-agent-bridge/codex-proxy.log` |
| Claude Proxy | `/var/log/mcp-agent-bridge/claude-proxy.log` |
| systemd | `journalctl -u codex-mcp-proxy` |

## Next Steps

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
2. Review [implementation_guide_codex_claude_cli_mcp_agentzero.md](implementation_guide_codex_claude_cli_mcp_agentzero.md) for integration specifics
3. Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
