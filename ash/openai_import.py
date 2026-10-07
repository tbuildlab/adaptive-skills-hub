"""Bounded import diagnostics. Never store exception text, headers or raw logs."""
from pathlib import Path
import re

from .core import _atomic, _bytes
from .core_capabilities import safe_path, sha
from .core_host import exclusive_run
from .managed_execution import ExecutionError


class ImportRefusal(ExecutionError):
    def __init__(self, code, reason):
        self.code, self.reason = code, reason
        super().__init__(code + ": " + reason)


def bounded(value, depth=0):
    """Metadata only; no arbitrary error/body/command/config fields accepted."""
    if depth > 5:
        return "OMITTED_DEPTH"
    if value is None or type(value) in {bool, int}:
        return value
    if type(value) is str:
        if (re.search(r"sk-[A-Za-z0-9_-]{24,}|Bearer\s|PRIVATE KEY|Authorization", value, re.I)
                or any(ord(c) < 32 or ord(c) == 127 for c in value)):
            return "REDACTED_METADATA"
        return value[:240]
    if type(value) is list:
        return [bounded(v, depth + 1) for v in value[:100]]
    if type(value) is dict:
        allowed = {"path", "id", "container_id", "bytes", "source", "object", "has_more",
                   "files", "file_id", "count", "sha256", "type", "status", "paths",
                   "max_bytes", "total_bytes", "expected_sha256", "verification",
                   "response_id", "request_digest", "exists", "exit_code",
                   "http_status", "provider_failure_code"}
        return {k: bounded(v, depth + 1) for k, v in value.items() if k in allowed}
    return "INVALID_" + type(value).__name__


def inventory_metadata(value):
    if type(value) is not dict:
        return {"type": type(value).__name__}
    files = value.get("data")
    return {"has_more": bounded(value.get("has_more")),
            "count": len(files) if type(files) is list else None,
            "files": bounded(files) if type(files) is list else [],
            "type": type(files).__name__}


def record_inventory(directory, state, listing):
    record = {"schema": "nexus.openai.inventory-evidence.v1",
              "response_id": state["provider_reference"], "request_digest": state["request_digest"],
              "metadata": inventory_metadata(listing), "content_downloaded": False}
    path = safe_path(directory, "provider-inventory.json")
    if path.exists():
        raise ImportRefusal("IMPORT_INVENTORY_REPLAY", "Inventory evidence already exists; reconcile separately.")
    _atomic(path, _bytes(record) + b"\n")


def record_refusal(directory, state, context, code, reason):
    """Append a diagnostic without rewriting the execution ledger or prior evidence."""
    record = {"schema": "nexus.openai.import-refusal.v1", "code": code, "reason": reason,
              "stage": context.get("stage", "admission"),
              "subject": bounded(context.get("subject")),
              "expected": bounded(context.get("expected", {})),
              "observed": bounded(context.get("observed", {})),
              "ambiguity": "IMPORT_NOT_VERIFIED_REMOTE_EFFECT_AND_COST_UNKNOWN",
              "response_id": state.get("provider_reference") if state else None,
              "request_digest": state.get("request_digest") if state else None,
              "exception_details_persisted": False}
    with exclusive_run(directory):
        for sequence in range(1, 101):
            path = safe_path(directory, f"import-refusal-{sequence:04d}.json")
            if not path.exists():
                _atomic(path, _bytes(record) + b"\n")
                return path
    raise ExecutionError("bounded import diagnostic capacity exhausted; STOP")
