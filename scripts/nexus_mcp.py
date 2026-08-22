"""Explicit local stdio entry point for Nexus Runtime R2."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ash.mcp.adapter import NexusMcpRuntime  # noqa: E402
from ash.mcp.authorization import WorkspaceAuthorizer  # noqa: E402
from ash.mcp.server import run_stdio  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Nexus Runtime R2 local stdio MCP server")
    parser.add_argument("--workspace-config", required=True, help="Trusted local workspace allowlist JSON; never supplied through MCP tool input")
    args = parser.parse_args()
    try:
        runtime = NexusMcpRuntime(WorkspaceAuthorizer.from_file(Path(args.workspace_config)))
        asyncio.run(run_stdio(runtime))
        return 0
    except Exception:
        # No traceback or configuration path is written to stdout. The SDK owns the
        # stdio protocol while active; startup failures are intentionally opaque.
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
