"""
MCP Agent Bridge Configuration Settings

Author: Wojciech Wiesner
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Settings:
    """Configuration settings for MCP Agent Bridge."""

    # Agent Zero Configuration
    AGENT_ZERO_HOST: str = os.getenv("AGENT_ZERO_HOST", "localhost")
    AGENT_ZERO_PORT: int = int(os.getenv("AGENT_ZERO_PORT", "50001"))
    AGENT_ZERO_TOKEN: str = os.getenv("AGENT_ZERO_TOKEN", "")

    # Proxy Ports
    CODEX_PROXY_PORT: int = int(os.getenv("CODEX_PROXY_PORT", "50010"))
    CLAUDE_PROXY_PORT: int = int(os.getenv("CLAUDE_PROXY_PORT", "50011"))

    # Timeouts
    MCP_TIMEOUT: float = float(os.getenv("MCP_TIMEOUT", "300"))
    HTTP_TIMEOUT: float = float(os.getenv("HTTP_TIMEOUT", "120"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "/var/log/mcp-agent-bridge/bridge.log")

    @classmethod
    def get_agent_zero_url(cls) -> str:
        """Get the full Agent Zero MCP URL."""
        return f"http://{cls.AGENT_ZERO_HOST}:{cls.AGENT_ZERO_PORT}/mcp/t-{cls.AGENT_ZERO_TOKEN}/http/"

    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []

        if not cls.AGENT_ZERO_TOKEN:
            errors.append("AGENT_ZERO_TOKEN is not set")

        if cls.AGENT_ZERO_PORT < 1 or cls.AGENT_ZERO_PORT > 65535:
            errors.append(f"Invalid AGENT_ZERO_PORT: {cls.AGENT_ZERO_PORT}")

        return errors


# Global settings instance
settings = Settings()
