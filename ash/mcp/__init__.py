"""Nexus Runtime R2: local, stdio, read/plan-only MCP adapter."""

from .server import create_server, run_stdio

__all__ = ["create_server", "run_stdio"]
