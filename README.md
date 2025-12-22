# MCP Agent Bridge

> **Bidirectional Model Context Protocol (MCP) Integration for AI Agent Systems**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)

Connect **OpenAI Codex CLI**, **Anthropic Claude CLI**, and **Google Gemini CLI** with **Agent Zero** through bidirectional MCP communication.

## Features

- **Bidirectional MCP Communication** - AI agents can call each other's tools
- **HTTP ↔ STDIO Bridge Proxies** - Transparent protocol translation
- **Multi-Agent Orchestration** - Chain AI capabilities across platforms
- **Production-Ready** - Systemd services, logging, error handling
- **Extensible Architecture** - Easy to add new AI tool integrations

## Quick Start

```bash
# Clone the repository
git clone https://github.com/vizi2000/mcp-agent-bridge.git
cd mcp-agent-bridge

# Install dependencies
pip install -r requirements.txt

# Configure your environment
cp config/example.env .env
# Edit .env with your API keys and Agent Zero URL

# Start the bridge proxies
python src/codex_mcp_proxy.py &
python src/claude_mcp_proxy.py &
```

## Integration Matrix

| AI Tool | → Agent Zero | Agent Zero → | Status |
|---------|--------------|--------------|--------|
| **Codex CLI** | ✅ Working | ✅ Working | Full Bidirectional |
| **Claude CLI** | ✅ Working | ✅ Working | Full Bidirectional |
| **Gemini CLI** | ✅ Working | ❌ No MCP Server | One-way Only |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Agent Bridge                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Codex Proxy  │    │ Claude Proxy │    │ Agent Zero   │  │
│  │ :50010       │◄──►│ :50011       │◄──►│ :50001       │  │
│  │ HTTP↔STDIO   │    │ HTTP↔STDIO   │    │ FastMCP      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         ▲                   ▲                   ▲          │
│         │ STDIO             │ STDIO             │ HTTP     │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Codex CLI   │    │  Claude CLI  │    │ AI Clients   │  │
│  │  mcp-server  │    │  mcp serve   │    │ (any HTTP)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.10+
- Agent Zero running with MCP enabled
- One or more CLI tools installed:
  - `npm install -g @openai/codex`
  - `npm install -g @anthropic-ai/claude-code`
  - `npm install -g @google/gemini-cli`

### Step 1: Install Dependencies

```bash
pip install fastmcp httpx uvicorn
```

### Step 2: Configure Agent Zero Connection

```bash
# Get your Agent Zero MCP token
docker exec agent-zero python3 -c "
from python.helpers.mcp_server import get_mcp_token
print(get_mcp_token())
"
```

### Step 3: Update Configuration

Edit `config/settings.py`:

```python
AGENT_ZERO_URL = "http://192.168.100.160:50001"
AGENT_ZERO_TOKEN = "your-token-here"
```

### Step 4: Start Services

```bash
# Start all proxies
./scripts/start_all.sh

# Or use systemd (recommended for production)
sudo cp config/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now codex-mcp-proxy claude-mcp-proxy
```

## Configuration

### Codex CLI

Add to `~/.codex/config.toml`:

```toml
[[mcp_servers]]
name = "agent-zero"
command = "python3"
args = ["/path/to/mcp-agent-bridge/src/agent_zero_mcp_stdio.py"]
```

### Claude CLI

Add to `~/.claude/mcp_servers.json`:

```json
{
  "agent-zero": {
    "type": "stdio",
    "command": "python3",
    "args": ["/path/to/mcp-agent-bridge/src/agent_zero_mcp_stdio.py"]
  }
}
```

### Gemini CLI

Add to `~/.gemini/settings.json`:

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

## Usage Examples

### Example 1: Codex CLI calls Agent Zero

```bash
codex "Use Agent Zero to check system status"
```

### Example 2: Agent Zero calls Codex CLI

From Agent Zero chat:
```
Use the codex_task tool to write a Python function that calculates fibonacci numbers
```

### Example 3: Chain Multiple Agents

```python
# Agent Zero orchestrating multiple AI tools
result = await agent_zero.execute("""
1. Use codex_task to generate a REST API
2. Use claude_query to review the code for security issues
3. Deploy the validated code
""")
```

## API Reference

### STDIO→HTTP Bridge Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `send_message` | Send message to Agent Zero | `message: str` |

### HTTP→STDIO Bridge Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `codex_task` | Execute Codex coding task | `task: str` |
| `codex_reply` | Continue Codex conversation | `message: str` |
| `claude_query` | Query Claude CLI | `prompt: str, context?: str` |

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Adding New Integrations

1. Create proxy in `src/your_tool_mcp_proxy.py`
2. Add systemd service in `config/systemd/`
3. Update documentation
4. Submit PR

## Troubleshooting

### Agent Zero Connection Failed

```bash
# Check Agent Zero is running
docker ps --filter name=agent-zero

# Test MCP endpoint
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","id":1,"params":{}}' \
  http://localhost:50001/mcp/t-TOKEN/http/
```

### STDIO Bridge Timeout

Increase timeout in proxy configuration:

```python
TIMEOUT = 300.0  # 5 minutes
```

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) before submitting PRs.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Wojciech Wiesner** - Lead Developer & Architect

## Keywords

MCP, Model Context Protocol, Agent Zero, Codex CLI, Claude CLI, Gemini CLI, AI integration, multi-agent systems, LLM orchestration, AI tool bridge, STDIO HTTP proxy, FastMCP, bidirectional AI communication, autonomous agents, AI workflow automation

---

*Built with FastMCP and love for AI interoperability*
