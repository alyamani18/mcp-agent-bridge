"""Base classes for MCP bridges"""
from .stdio_http_bridge import STDIOToHTTPBridge
from .http_stdio_proxy import HTTPToSTDIOProxy

__all__ = ["STDIOToHTTPBridge", "HTTPToSTDIOProxy"]
