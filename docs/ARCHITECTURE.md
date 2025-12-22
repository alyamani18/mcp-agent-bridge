# Architecture Documentation

## System Overview

MCP Agent Bridge provides bidirectional communication between AI agent systems using the Model Context Protocol (MCP).

## Component Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                         MCP Agent Bridge System                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      Bridge Layer (Python)                       │  │
│  │                                                                  │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │  │
│  │  │ STDIO→HTTP     │  │ HTTP→STDIO     │  │ MCP Client     │    │  │
│  │  │ Bridge Base    │  │ Bridge Base    │  │ Library        │    │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘    │  │
│  │         │                   │                   │               │  │
│  │         ▼                   ▼                   ▼               │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │  │
│  │  │ agent_zero_    │  │ codex_mcp_     │  │ claude_mcp_    │    │  │
│  │  │ mcp_stdio.py   │  │ proxy.py       │  │ proxy.py       │    │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘    │  │
│  │                                                                  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      Transport Layer                             │  │
│  │                                                                  │  │
│  │  STDIO ◄──────────────────────────────────────────────► HTTP    │  │
│  │  (subprocess pipes)                  (TCP/HTTP JSON-RPC)         │  │
│  │                                                                  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      External Systems                            │  │
│  │                                                                  │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │  │
│  │  │  Agent Zero    │  │   Codex CLI    │  │  Claude CLI    │    │  │
│  │  │  (Docker)      │  │   (Node.js)    │  │  (Node.js)     │    │  │
│  │  │  FastMCP       │  │   mcp-server   │  │  mcp serve     │    │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘    │  │
│  │                                                                  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Direction 1: CLI Tool → Agent Zero

```
┌──────────┐    JSON-RPC     ┌──────────────┐    HTTP POST    ┌──────────┐
│ CLI Tool │ ──────────────► │ STDIO→HTTP   │ ─────────────► │  Agent   │
│ (Client) │    via STDIO    │ Bridge       │    /mcp/...    │  Zero    │
└──────────┘                 └──────────────┘                 └──────────┘
     │                             │                               │
     │ 1. tools/list              │ 2. Forward                    │
     │ 2. tools/call              │    request                    │
     │                             │                               │
     │◄────────────────────────────│◄──────────────────────────────│
     │    Response via STDIO       │     HTTP Response             │
```

### Direction 2: Agent Zero → CLI Tool

```
┌──────────┐    HTTP POST    ┌──────────────┐    JSON-RPC     ┌──────────┐
│  Agent   │ ──────────────► │ HTTP→STDIO   │ ─────────────► │ CLI Tool │
│  Zero    │    /mcp/...     │ Proxy        │    via STDIO   │ (Server) │
└──────────┘                 └──────────────┘                 └──────────┘
     │                             │                               │
     │ 1. Call proxy               │ 2. Spawn                      │
     │    tool                     │    subprocess                 │
     │                             │                               │
     │◄────────────────────────────│◄──────────────────────────────│
     │    HTTP Response            │     STDIO Response            │
```

## Protocol Details

### MCP JSON-RPC 2.0 Message Format

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "send_message",
    "arguments": {
      "message": "Hello from Codex"
    }
  },
  "id": "uuid-string"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Response from Agent Zero"
      }
    ]
  },
  "id": "uuid-string"
}
```

### Session Management

```
┌─────────────┐                    ┌─────────────┐
│   Client    │                    │   Server    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │──── initialize ─────────────────►│
       │◄─── capabilities + session_id ───│
       │                                  │
       │──── notifications/initialized ──►│
       │                                  │
       │──── tools/list ─────────────────►│
       │◄─── tool definitions ────────────│
       │                                  │
       │──── tools/call ─────────────────►│
       │◄─── tool result ─────────────────│
       │                                  │
```

## Security Model

### Authentication

| Layer | Mechanism | Implementation |
|-------|-----------|----------------|
| Agent Zero | Token in URL path | `/mcp/t-TOKEN/http/` |
| Codex CLI | Environment variable | `OPENAI_API_KEY` |
| Claude CLI | Environment variable | `ANTHROPIC_API_KEY` |
| Gemini CLI | Environment variable | `GEMINI_API_KEY` |

### Network Security

- Proxies bind to `localhost` by default
- External access requires explicit configuration
- TLS recommended for production deployments

## Error Handling

### Bridge Error Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────┐
│  Client  │         │    Bridge    │         │  Server  │
└────┬─────┘         └──────┬───────┘         └────┬─────┘
     │                      │                      │
     │─── request ─────────►│                      │
     │                      │─── forward ─────────►│
     │                      │                      │
     │                      │◄─── error (500) ─────│
     │                      │                      │
     │                      │ [Retry logic]        │
     │                      │─── forward ─────────►│
     │                      │                      │
     │                      │◄─── success ─────────│
     │◄── response ─────────│                      │
```

### Error Categories

| Code | Category | Action |
|------|----------|--------|
| -32700 | Parse Error | Return error, log |
| -32600 | Invalid Request | Return error |
| -32601 | Method Not Found | Return error |
| -32602 | Invalid Params | Return error |
| -32603 | Internal Error | Retry, then error |
| 500 | Server Error | Retry with backoff |
| Timeout | Connection Timeout | Retry, then error |

## Scalability Considerations

### Single-Instance Mode (Default)

```
┌─────────────────────────────────────────────┐
│              Single Host                     │
│                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Proxy 1 │  │ Proxy 2 │  │ Agent 0 │    │
│  └─────────┘  └─────────┘  └─────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

### Multi-Instance Mode (Future)

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                         │
└─────────────────────────┬───────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │  Proxy 1   │  │  Proxy 2   │  │  Proxy 3   │
   │  Instance  │  │  Instance  │  │  Instance  │
   └────────────┘  └────────────┘  └────────────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                  ┌────────────┐
                  │ Agent Zero │
                  │  Cluster   │
                  └────────────┘
```

## Performance Characteristics

| Metric | STDIO Bridge | HTTP Proxy | Notes |
|--------|--------------|------------|-------|
| Latency (p50) | ~10ms | ~5ms | Local network |
| Latency (p99) | ~50ms | ~20ms | Local network |
| Throughput | ~100 req/s | ~500 req/s | Per instance |
| Memory | ~50MB | ~30MB | Per process |

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.10+ |
| MCP Server | FastMCP | Latest |
| HTTP Client | httpx | 0.27+ |
| HTTP Server | uvicorn | 0.30+ |
| Process Mgmt | systemd | System |
| Container | Docker | 24+ |
