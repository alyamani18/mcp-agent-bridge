# MCP Agent Bridge: Bidirectional Integration Guide for Codex CLI, Claude CLI & Agent Zero

> **Keywords**: MCP, Model Context Protocol, Agent Zero, Codex CLI, Claude CLI, Gemini CLI, AI Agent Integration, Multi-Agent Systems, LLM Orchestration, OpenAI Codex, Anthropic Claude, Google Gemini, AI Tool Integration, STDIO to HTTP Bridge, FastMCP, AI Agents Communication

## Table of Contents

1. [Overview](#overview)
2. [Integration Feasibility Matrix](#integration-feasibility-matrix)
3. [Architecture](#architecture)
4. [Codex CLI Integration](#codex-cli-integration)
5. [Claude CLI Integration](#claude-cli-integration)
6. [Gemini CLI Integration](#gemini-cli-integration)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Technical Specifications](#technical-specifications)
9. [Troubleshooting](#troubleshooting)

---

## Overview

**MCP Agent Bridge** is an open-source framework enabling **bidirectional communication** between AI agent systems using the **Model Context Protocol (MCP)**. This guide covers integration of:

- **OpenAI Codex CLI** - AI coding assistant with shell access
- **Anthropic Claude CLI** - Advanced reasoning AI assistant
- **Google Gemini CLI** - Multimodal AI assistant
- **Agent Zero** - Autonomous AI agent framework with FastMCP

### Why Bidirectional MCP?

Traditional AI integrations are one-way: you call an API, get a response. **Bidirectional MCP** enables:

- **Agent-to-Agent Communication**: AI agents can delegate tasks to specialized AI tools
- **Tool Composition**: Chain multiple AI capabilities seamlessly
- **Autonomous Workflows**: Agents can invoke other agents without human intervention
- **Cross-Platform AI Orchestration**: Unify OpenAI, Anthropic, and Google AI under one protocol

---

## Integration Feasibility Matrix

| AI Tool | Agent Zero → Tool | Tool → Agent Zero | Bidirectional Support |
|---------|-------------------|-------------------|----------------------|
| **Codex CLI** | Possible (via HTTP→STDIO proxy) | Working | Full Bidirectional |
| **Claude CLI** | Possible (via HTTP→STDIO proxy) | Possible (native MCP client) | Full Bidirectional |
| **Gemini CLI** | Not Possible (no MCP server) | Possible (native MCP client) | One-way Only |

### Key Insight

Agent Zero uses **HTTP/SSE transport** for MCP, while CLI tools expose **STDIO-based MCP servers**. The solution: **HTTP↔STDIO bridge proxies**.

---

## Architecture

### Current State: One-Way Integration

```
┌─────────────┐    STDIO→HTTP Bridge    ┌──────────────┐
│  Codex CLI  │ ──────────────────────► │  Agent Zero  │
│  (MCP Client)│    agent_zero_mcp_     │  (FastMCP    │
└─────────────┘    stdio.py             │   Server)    │
                                        └──────────────┘
```

### Target State: Full Bidirectional Integration

```
                         ┌──────────────────────────────────┐
                         │     MCP Agent Bridge Proxies      │
                         │  ┌────────────┐ ┌────────────┐   │
                         │  │ Claude     │ │ Codex      │   │
                         │  │ Proxy:50011│ │ Proxy:50010│   │
                         │  └────────────┘ └────────────┘   │
                         └──────────────────────────────────┘
                                    ▲         ▲
                                    │   HTTP  │
                    ┌───────────────┴─────────┴───────────────┐
                    │                                         │
        ┌───────────▼───────────┐         ┌───────────────────▼───────────┐
        │      Agent Zero       │◄───────►│        CLI AI Tools           │
        │  (FastMCP + Client)   │   MCP   │  Codex | Claude | Gemini      │
        │  http://host:50001    │         │  (STDIO MCP Servers)          │
        └───────────────────────┘         └───────────────────────────────┘
```

---

## Codex CLI Integration

### Direction 1: Codex CLI → Agent Zero (WORKING)

**Status**: ✅ Fully Operational

Codex CLI calls Agent Zero tools via STDIO→HTTP bridge.

**Bridge Script**: `src/agent_zero_mcp_stdio.py`

```python
AGENT_ZERO_MCP_URL = "http://192.168.100.160:50001/mcp/t-TOKEN/http/"
```

**Codex Configuration** (`~/.codex/config.toml`):

```toml
[[mcp_servers]]
name = "agent-zero"
command = "python3"
args = ["/path/to/agent_zero_mcp_stdio.py"]
```

### Direction 2: Agent Zero → Codex CLI (IMPLEMENTATION REQUIRED)

**Mechanism**: Codex exposes `codex mcp-server` (STDIO transport)

**Exposed Tools**:
- `codex` - Submit coding task
- `codex-reply` - Send follow-up message

**Solution**: HTTP→STDIO Proxy (`src/codex_mcp_proxy.py`)

```python
#!/usr/bin/env python3
"""
HTTP Proxy for Codex MCP Server
Enables Agent Zero (HTTP) to call Codex CLI (STDIO)
"""
from fastmcp import FastMCP
import asyncio
import json

mcp = FastMCP("codex-proxy")

@mcp.tool()
async def codex_task(task: str) -> str:
    """Send a coding task to Codex CLI via MCP"""
    # Implementation forwards to Codex STDIO server
    pass
```

---

## Claude CLI Integration

### Direction 1: Claude CLI → Agent Zero

**Status**: ✅ Implementable (Native MCP Client)

Claude CLI supports HTTP transport natively.

**Configuration** (`~/.claude/mcp_servers.json`):

```json
{
  "agent-zero": {
    "type": "http",
    "url": "http://192.168.100.160:50001/mcp/t-TOKEN/http/",
    "headers": {
      "Accept": "application/json, text/event-stream"
    }
  }
}
```

**Alternative STDIO Configuration**:

```json
{
  "agent-zero": {
    "type": "stdio",
    "command": "python3",
    "args": ["/path/to/agent_zero_mcp_stdio.py"]
  }
}
```

### Direction 2: Agent Zero → Claude CLI

**Mechanism**: Claude exposes `claude mcp serve` (STDIO transport)

**Solution**: HTTP→STDIO Proxy (`src/claude_mcp_proxy.py`)

---

## Gemini CLI Integration

### Direction 1: Gemini CLI → Agent Zero

**Status**: ✅ Implementable

**Configuration** (`~/.gemini/settings.json`):

```json
{
  "mcpServers": {
    "agent-zero": {
      "command": "python3",
      "args": ["/path/to/agent_zero_mcp_stdio.py"]
    }
  }
}
```

### Direction 2: Agent Zero → Gemini CLI

**Status**: ❌ Not Possible

**Reason**: Gemini CLI lacks MCP server mode (`gemini mcp-server` does not exist)

**Workarounds**:
1. Use Gemini API directly from Agent Zero
2. Shell execution with output parsing
3. Wait for Google to add MCP server support

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Parallel Tasks)
- [ ] Create STDIO→HTTP bridge base class
- [ ] Create HTTP→STDIO bridge base class
- [ ] Setup systemd service templates
- [ ] Create test framework

### Phase 2: Codex Integration
- [ ] Implement `codex_mcp_proxy.py`
- [ ] Create systemd service for Codex proxy
- [ ] Test bidirectional Codex ↔ Agent Zero

### Phase 3: Claude Integration
- [ ] Implement `claude_mcp_proxy.py`
- [ ] Configure Claude CLI MCP settings
- [ ] Test bidirectional Claude ↔ Agent Zero

### Phase 4: Gemini Partial Integration
- [ ] Configure Gemini CLI MCP client
- [ ] Test one-way Gemini → Agent Zero
- [ ] Document limitations

### Phase 5: Documentation & Release
- [ ] Complete API documentation
- [ ] Create usage examples
- [ ] Publish to PyPI

---

## Technical Specifications

### Transport Protocol Matrix

| Component | Server Transport | Client Transport | Protocol |
|-----------|-----------------|------------------|----------|
| Agent Zero | HTTP/SSE | HTTP (needs implementation) | JSON-RPC 2.0 |
| Codex CLI | STDIO | HTTP, STDIO | JSON-RPC 2.0 |
| Claude CLI | STDIO | HTTP, SSE, STDIO | JSON-RPC 2.0 |
| Gemini CLI | None | STDIO, SSE, HTTP | JSON-RPC 2.0 |

### Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| Agent Zero MCP | 50001 | FastMCP server |
| Codex Proxy | 50010 | HTTP→STDIO bridge |
| Claude Proxy | 50011 | HTTP→STDIO bridge |

### Authentication

- **Agent Zero**: Token-based (`/mcp/t-TOKEN/http/`)
- **Codex CLI**: Environment-based (OpenAI API key)
- **Claude CLI**: Environment-based (Anthropic API key)
- **Gemini CLI**: Environment-based (Google API key)

---

## Troubleshooting

### Common Issues

**1. Connection Refused on Port 50001**
```bash
# Check Agent Zero is running
docker ps --filter name=agent-zero
```

**2. MCP Session Timeout**
```bash
# Verify Accept header includes SSE
curl -H "Accept: application/json, text/event-stream" \
     http://host:50001/mcp/t-TOKEN/http/
```

**3. STDIO Bridge Not Responding**
```bash
# Test bridge manually
echo '{"jsonrpc":"2.0","method":"initialize","id":1}' | \
    python3 agent_zero_mcp_stdio.py
```

---

## Developer

**Wojciech Wiesner** - Lead Developer & Architect

---

## License

MIT License - See [LICENSE](../LICENSE) for details.

---

## SEO Keywords

MCP integration, Model Context Protocol tutorial, Agent Zero setup, Codex CLI MCP, Claude CLI MCP configuration, Gemini CLI integration, multi-agent AI systems, AI agent orchestration, LLM tool integration, STDIO HTTP bridge, FastMCP Python, bidirectional AI communication, autonomous AI agents, AI workflow automation, cross-platform AI tools
