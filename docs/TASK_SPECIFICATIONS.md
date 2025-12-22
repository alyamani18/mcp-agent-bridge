# Task Specifications Document

## Project: MCP Agent Bridge
## Developer: Wojciech Wiesner
## Created: 2024-12-22

---

## Task Dependency Graph

```
                    ┌──────────────────────────────────────┐
                    │         PHASE 0: Setup               │
                    │    (All tasks run in parallel)       │
                    └──────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
    ┌──────────┐               ┌──────────┐               ┌──────────┐
    │ T0.1     │               │ T0.2     │               │ T0.3     │
    │ Project  │               │ Git      │               │ Deps     │
    │ Structure│               │ Init     │               │ Setup    │
    └──────────┘               └──────────┘               └──────────┘
          │                           │                           │
          └───────────────────────────┼───────────────────────────┘
                                      ▼
                    ┌──────────────────────────────────────┐
                    │         PHASE 1: Core                │
                    │    (Sequential - Base Classes)       │
                    └──────────────────────────────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │ T1.1         │
                              │ Base Bridge  │
                              │ Classes      │
                              └──────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
                    ┌──────────────────────────────────────┐
                    │         PHASE 2: Bridges             │
                    │    (Parallel Implementation)         │
                    └──────────────────────────────────────┘
          │                           │                           │
    ┌──────────┐               ┌──────────┐               ┌──────────┐
    │ T2.1     │               │ T2.2     │               │ T2.3     │
    │ Agent0   │               │ Codex    │               │ Claude   │
    │ STDIO    │               │ Proxy    │               │ Proxy    │
    └──────────┘               └──────────┘               └──────────┘
          │                           │                           │
          └───────────────────────────┼───────────────────────────┘
                                      ▼
                    ┌──────────────────────────────────────┐
                    │         PHASE 3: Services            │
                    │    (Parallel - After Phase 2)        │
                    └──────────────────────────────────────┘
          │                           │                           │
    ┌──────────┐               ┌──────────┐               ┌──────────┐
    │ T3.1     │               │ T3.2     │               │ T3.3     │
    │ Systemd  │               │ Config   │               │ Scripts  │
    │ Services │               │ Files    │               │ Start/   │
    └──────────┘               └──────────┘               │ Stop     │
                                                          └──────────┘
          │                           │                           │
          └───────────────────────────┼───────────────────────────┘
                                      ▼
                    ┌──────────────────────────────────────┐
                    │         PHASE 4: Testing             │
                    │    (After Phase 3 Complete)          │
                    └──────────────────────────────────────┘
                                      │
                              ┌──────────────┐
                              │ T4.1         │
                              │ Test Suite   │
                              └──────────────┘
                                      │
                                      ▼
                    ┌──────────────────────────────────────┐
                    │         PHASE 5: Deploy              │
                    │    (Final Phase)                     │
                    └──────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
    ┌──────────┐               ┌──────────┐               ┌──────────┐
    │ T5.1     │               │ T5.2     │               │ T5.3     │
    │ GitHub   │               │ Docs     │               │ Release  │
    │ Repo     │               │ Polish   │               │ Tag      │
    └──────────┘               └──────────┘               └──────────┘
```

---

## Parallel Execution Matrix

| Phase | Task | Can Run With | Dependencies |
|-------|------|--------------|--------------|
| 0 | T0.1 Project Structure | T0.2, T0.3 | None |
| 0 | T0.2 Git Init | T0.1, T0.3 | None |
| 0 | T0.3 Dependencies | T0.1, T0.2 | None |
| 1 | T1.1 Base Classes | None | T0.* |
| 2 | T2.1 Agent Zero Bridge | T2.2, T2.3 | T1.1 |
| 2 | T2.2 Codex Proxy | T2.1, T2.3 | T1.1 |
| 2 | T2.3 Claude Proxy | T2.1, T2.2 | T1.1 |
| 3 | T3.1 Systemd | T3.2, T3.3 | T2.* |
| 3 | T3.2 Config | T3.1, T3.3 | T2.* |
| 3 | T3.3 Scripts | T3.1, T3.2 | T2.* |
| 4 | T4.1 Tests | None | T3.* |
| 5 | T5.1 GitHub | T5.2, T5.3 | T4.1 |
| 5 | T5.2 Docs | T5.1, T5.3 | T4.1 |
| 5 | T5.3 Release | T5.1, T5.2 | T4.1 |

---

## Detailed Task Specifications

### PHASE 0: Project Setup

#### T0.1 - Create Project Structure

**Priority**: High
**Estimated Complexity**: Low
**Parallelizable**: Yes (with T0.2, T0.3)

**Specification**:
```
mcp-agent-bridge/
├── src/
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   ├── stdio_http_bridge.py
│   │   └── http_stdio_proxy.py
│   ├── agent_zero_mcp_stdio.py
│   ├── codex_mcp_proxy.py
│   └── claude_mcp_proxy.py
├── config/
│   ├── example.env
│   ├── settings.py
│   └── systemd/
│       ├── codex-mcp-proxy.service
│       └── claude-mcp-proxy.service
├── scripts/
│   ├── start_all.sh
│   ├── stop_all.sh
│   └── install.sh
├── tests/
│   ├── __init__.py
│   ├── test_bridges.py
│   └── test_integration.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   └── implementation_guide_codex_claude_cli_mcp_agentzero.md
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
└── .gitignore
```

**Acceptance Criteria**:
- [ ] All directories created
- [ ] Empty `__init__.py` files in place
- [ ] Directory permissions correct (755)

---

#### T0.2 - Initialize Git Repository

**Priority**: High
**Estimated Complexity**: Low
**Parallelizable**: Yes (with T0.1, T0.3)

**Specification**:
- Initialize git repository
- Create `.gitignore` with Python, Node.js, IDE patterns
- Create initial commit

**Acceptance Criteria**:
- [ ] `.git` directory exists
- [ ] `.gitignore` covers common patterns
- [ ] Initial commit with project structure

---

#### T0.3 - Setup Dependencies

**Priority**: High
**Estimated Complexity**: Low
**Parallelizable**: Yes (with T0.1, T0.2)

**Specification**:

`requirements.txt`:
```
fastmcp>=0.1.0
httpx>=0.27.0
uvicorn>=0.30.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

**Acceptance Criteria**:
- [ ] All packages installable
- [ ] No version conflicts
- [ ] Virtual environment works

---

### PHASE 1: Core Implementation

#### T1.1 - Create Base Bridge Classes

**Priority**: Critical
**Estimated Complexity**: High
**Parallelizable**: No (blocking for Phase 2)

**Specification**:

`src/base/stdio_http_bridge.py`:
```python
"""
Base class for STDIO→HTTP MCP bridges
"""
import asyncio
import json
import uuid
from abc import ABC, abstractmethod
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

class STDIOToHTTPBridge(ABC):
    """
    Abstract base class for bridging STDIO MCP clients
    to HTTP MCP servers.
    """

    def __init__(self, name: str, target_url: str, timeout: float = 300.0):
        self.name = name
        self.target_url = target_url
        self.timeout = timeout
        self.session_id = None
        self.server = Server(name)
        self._setup_handlers()

    @abstractmethod
    def get_tools(self) -> list[Tool]:
        """Return list of tools to expose"""
        pass

    @abstractmethod
    async def handle_tool_call(self, name: str, arguments: dict) -> str:
        """Handle tool invocation"""
        pass

    async def initialize_session(self) -> dict:
        """Initialize MCP session with target server"""
        # Implementation
        pass

    async def forward_request(self, method: str, params: dict) -> dict:
        """Forward JSON-RPC request to target server"""
        # Implementation
        pass

    async def run(self):
        """Start the STDIO server"""
        async with stdio_server() as (read, write):
            await self.server.run(read, write,
                self.server.create_initialization_options())
```

`src/base/http_stdio_proxy.py`:
```python
"""
Base class for HTTP→STDIO MCP proxies
"""
import asyncio
import json
from abc import ABC, abstractmethod
from fastmcp import FastMCP

class HTTPToSTDIOProxy(ABC):
    """
    Abstract base class for proxying HTTP MCP requests
    to STDIO MCP servers (CLI tools).
    """

    def __init__(self, name: str, port: int, cli_command: list[str]):
        self.name = name
        self.port = port
        self.cli_command = cli_command
        self.mcp = FastMCP(name)
        self.process = None
        self._setup_tools()

    @abstractmethod
    def get_tools(self) -> list[dict]:
        """Return tool definitions to expose"""
        pass

    @abstractmethod
    async def handle_tool_call(self, name: str, arguments: dict) -> str:
        """Handle incoming tool call"""
        pass

    async def start_subprocess(self):
        """Start the CLI tool as MCP server"""
        self.process = await asyncio.create_subprocess_exec(
            *self.cli_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    async def send_to_subprocess(self, request: dict) -> dict:
        """Send JSON-RPC request to subprocess"""
        # Implementation with proper framing
        pass

    def run(self):
        """Start the HTTP MCP server"""
        self.mcp.run()
```

**Acceptance Criteria**:
- [ ] Both base classes implemented
- [ ] Session management works
- [ ] Error handling complete
- [ ] Logging integrated
- [ ] Type hints complete

---

### PHASE 2: Bridge Implementations

#### T2.1 - Agent Zero STDIO Bridge

**Priority**: Critical
**Estimated Complexity**: Medium
**Parallelizable**: Yes (with T2.2, T2.3)

**Specification**:
Inherit from `STDIOToHTTPBridge`, implement Agent Zero specific logic.

**Tools Exposed**:
- `send_message(message: str)` - Send message to Agent Zero

**Acceptance Criteria**:
- [ ] Extends base class correctly
- [ ] Session initialization works
- [ ] Tool calls succeed
- [ ] Error responses handled

---

#### T2.2 - Codex HTTP→STDIO Proxy

**Priority**: High
**Estimated Complexity**: Medium
**Parallelizable**: Yes (with T2.1, T2.3)

**Specification**:
Inherit from `HTTPToSTDIOProxy`, spawn `codex mcp-server`.

**Tools Exposed**:
- `codex_task(task: str)` - Submit coding task
- `codex_reply(message: str)` - Continue conversation

**Acceptance Criteria**:
- [ ] Subprocess management works
- [ ] JSON-RPC framing correct
- [ ] Tool results parsed correctly
- [ ] Cleanup on shutdown

---

#### T2.3 - Claude HTTP→STDIO Proxy

**Priority**: High
**Estimated Complexity**: Medium
**Parallelizable**: Yes (with T2.1, T2.2)

**Specification**:
Inherit from `HTTPToSTDIOProxy`, spawn `claude mcp serve`.

**Tools Exposed**:
- `claude_query(prompt: str, context?: str)` - Query Claude

**Acceptance Criteria**:
- [ ] Subprocess management works
- [ ] JSON-RPC framing correct
- [ ] Tool results parsed correctly
- [ ] Context passing works

---

### PHASE 3: Services & Configuration

#### T3.1 - Systemd Service Files

**Priority**: Medium
**Estimated Complexity**: Low
**Parallelizable**: Yes (with T3.2, T3.3)

**Specification**:

`config/systemd/codex-mcp-proxy.service`:
```ini
[Unit]
Description=Codex MCP HTTP Proxy
After=network.target

[Service]
Type=simple
User=vizi
WorkingDirectory=/home/vizi/mcp-agent-bridge
Environment=PYTHONPATH=/home/vizi/mcp-agent-bridge
ExecStart=/usr/bin/python3 /home/vizi/mcp-agent-bridge/src/codex_mcp_proxy.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Acceptance Criteria**:
- [ ] Services start correctly
- [ ] Auto-restart on failure
- [ ] Logs to journald
- [ ] Correct user/permissions

---

#### T3.2 - Configuration Files

**Priority**: Medium
**Estimated Complexity**: Low
**Parallelizable**: Yes (with T3.1, T3.3)

**Specification**:

`config/settings.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AGENT_ZERO_HOST = os.getenv("AGENT_ZERO_HOST", "localhost")
    AGENT_ZERO_PORT = int(os.getenv("AGENT_ZERO_PORT", "50001"))
    AGENT_ZERO_TOKEN = os.getenv("AGENT_ZERO_TOKEN", "")

    CODEX_PROXY_PORT = int(os.getenv("CODEX_PROXY_PORT", "50010"))
    CLAUDE_PROXY_PORT = int(os.getenv("CLAUDE_PROXY_PORT", "50011"))

    MCP_TIMEOUT = float(os.getenv("MCP_TIMEOUT", "300"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
```

**Acceptance Criteria**:
- [ ] All settings configurable
- [ ] Defaults sensible
- [ ] Validation present

---

#### T3.3 - Management Scripts

**Priority**: Medium
**Estimated Complexity**: Low
**Parallelizable**: Yes (with T3.1, T3.2)

**Specification**:

`scripts/start_all.sh`:
```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source venv/bin/activate
python3 src/codex_mcp_proxy.py &
python3 src/claude_mcp_proxy.py &
echo "All proxies started"
```

**Acceptance Criteria**:
- [ ] Scripts executable
- [ ] Error handling present
- [ ] PID tracking works

---

### PHASE 4: Testing

#### T4.1 - Test Suite

**Priority**: High
**Estimated Complexity**: High
**Parallelizable**: No (requires all Phase 3)

**Specification**:

`tests/test_bridges.py`:
```python
import pytest
from src.base.stdio_http_bridge import STDIOToHTTPBridge

class TestSTDIOBridge:
    @pytest.mark.asyncio
    async def test_session_initialization(self):
        """Test MCP session can be initialized"""
        pass

    @pytest.mark.asyncio
    async def test_tool_call_forward(self):
        """Test tool calls are forwarded correctly"""
        pass

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test errors are handled gracefully"""
        pass
```

**Acceptance Criteria**:
- [ ] Unit tests for base classes
- [ ] Integration tests for proxies
- [ ] End-to-end test with mock servers
- [ ] Coverage > 80%

---

### PHASE 5: Deployment

#### T5.1 - Create GitHub Repository

**Priority**: High
**Estimated Complexity**: Low
**Parallelizable**: Yes (with T5.2, T5.3)

**Specification**:
- Create public repository: `mcp-agent-bridge`
- Add description and topics
- Push all code and documentation

**Acceptance Criteria**:
- [ ] Repository public
- [ ] All code pushed
- [ ] README visible
- [ ] Topics set for SEO

---

#### T5.2 - Polish Documentation

**Priority**: Medium
**Estimated Complexity**: Low
**Parallelizable**: Yes (with T5.1, T5.3)

**Specification**:
- Review all markdown files
- Add badges to README
- Create CONTRIBUTING.md
- Add CODE_OF_CONDUCT.md

**Acceptance Criteria**:
- [ ] All docs spell-checked
- [ ] Links valid
- [ ] Examples tested

---

#### T5.3 - Create Release Tag

**Priority**: Low
**Estimated Complexity**: Low
**Parallelizable**: Yes (with T5.1, T5.2)

**Specification**:
- Create tag v0.1.0
- Write release notes
- Consider PyPI publication

**Acceptance Criteria**:
- [ ] Tag created
- [ ] Release notes complete
- [ ] Binary artifacts (if any)

---

## Execution Order

### Sequential Execution (Minimum Time)

```
T0.1 ─┬─ T0.2 ─┬─ T0.3 ─► T1.1 ─► T2.1 ─┬─ T2.2 ─┬─ T2.3 ─► T3.1 ─┬─ T3.2 ─┬─ T3.3 ─► T4.1 ─► T5.1 ─┬─ T5.2 ─┬─ T5.3
      │        │         │         │        │        │         │        │        │         │        │        │
      └────────┴─────────┘         └────────┴────────┘         └────────┴────────┘         └────────┴────────┘
       PARALLEL                     PARALLEL                    PARALLEL                    PARALLEL
```

### Recommended Execution (Balanced)

1. **Wave 1** (Parallel): T0.1, T0.2, T0.3
2. **Wave 2** (Sequential): T1.1
3. **Wave 3** (Parallel): T2.1, T2.2, T2.3
4. **Wave 4** (Parallel): T3.1, T3.2, T3.3
5. **Wave 5** (Sequential): T4.1
6. **Wave 6** (Parallel): T5.1, T5.2, T5.3
