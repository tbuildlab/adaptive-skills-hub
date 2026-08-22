"""No-retention, opt-in safe local diagnostics. stdout is never used."""
from __future__ import annotations

import os
import sys
from typing import Iterable


def emit(request_id: str, tool: str, status: str, elapsed_ms: int, selected_ids: Iterable[str] = ()) -> None:
    if os.environ.get("NEXUS_MCP_SAFE_DIAGNOSTICS") != "1":
        return
    ids = ",".join(sorted(str(item) for item in selected_ids))
    print(f"nexus_mcp request={request_id} tool={tool} status={status} elapsed_ms={elapsed_ms} selected={ids}", file=sys.stderr, flush=True)
