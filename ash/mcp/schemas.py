"""Strict, versioned MCP input schemas and safe error vocabulary."""
from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, Mapping

SCHEMA_VERSION = "nexus.mcp.v1"
MAX_TASK_BYTES = 8 * 1024
MAX_CONSTRAINTS = 16
MAX_CONSTRAINT_BYTES = 8 * 1024
MAX_RESPONSE_BYTES = 64 * 1024
# R2 serializes the safe envelope into TextContent. Keep the envelope well below
# the wire limit because JSON-RPC must escape it once more inside that text field.
MAX_SAFE_ENVELOPE_BYTES = 24 * 1024
WORKSPACE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


class NexusMcpError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.safe_message = message


@dataclass(frozen=True)
class PlanRequest:
    task: str
    workspace_id: str
    project_context_mode: str
    constraints: tuple[str, ...]


def _bytes(value: str) -> int:
    return len(value.encode("utf-8"))


def _object(value: Any, allowed: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise NexusMcpError("INVALID_REQUEST", "arguments must be an object")
    unknown = set(value) - allowed
    if unknown:
        raise NexusMcpError("INVALID_REQUEST", "arguments contain unsupported fields")
    return value


def parse_plan_request(value: Any) -> PlanRequest:
    data = _object(value, {"task", "workspace_id", "project_context_mode", "constraints"})
    task = data.get("task")
    workspace_id = data.get("workspace_id")
    mode = data.get("project_context_mode", "governance")
    constraints = data.get("constraints", [])
    if not isinstance(task, str) or not task.strip():
        raise NexusMcpError("INVALID_REQUEST", "task must be a non-empty string")
    if _bytes(task) > MAX_TASK_BYTES:
        raise NexusMcpError("REQUEST_LIMIT", "task exceeds the 8 KiB limit")
    if not isinstance(workspace_id, str) or not WORKSPACE_ID_RE.fullmatch(workspace_id):
        raise NexusMcpError("INVALID_REQUEST", "workspace_id is invalid")
    if mode not in {"none", "governance"}:
        raise NexusMcpError("INVALID_REQUEST", "project_context_mode is invalid")
    if not isinstance(constraints, list) or len(constraints) > MAX_CONSTRAINTS or not all(isinstance(item, str) and item.strip() and len(item) <= 512 for item in constraints):
        raise NexusMcpError("INVALID_REQUEST", "constraints are invalid")
    if sum(_bytes(item) for item in constraints) > MAX_CONSTRAINT_BYTES:
        raise NexusMcpError("REQUEST_LIMIT", "constraints exceed the 8 KiB limit")
    return PlanRequest(task.strip(), workspace_id, mode, tuple(item.strip() for item in constraints))


def parse_discover_request(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    data = _object(value, {"capability_tags"})
    tags = data.get("capability_tags", [])
    if not isinstance(tags, list) or len(tags) > 8 or not all(isinstance(item, str) and re.fullmatch(r"[a-z0-9_-]{1,64}", item) for item in tags):
        raise NexusMcpError("INVALID_REQUEST", "capability_tags are invalid")
    return tuple(sorted(set(tags)))


HEALTH_INPUT_SCHEMA: dict[str, Any] = {"type": "object", "additionalProperties": False, "properties": {}}
DISCOVER_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False,
    "properties": {"capability_tags": {"type": "array", "maxItems": 8, "items": {"type": "string", "pattern": "^[a-z0-9_-]{1,64}$"}}},
}
PLAN_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False, "required": ["task", "workspace_id"],
    "properties": {
        "task": {"type": "string", "minLength": 1, "maxLength": MAX_TASK_BYTES},
        "workspace_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$"},
        "project_context_mode": {"type": "string", "enum": ["none", "governance"], "default": "governance"},
        "constraints": {"type": "array", "maxItems": MAX_CONSTRAINTS, "items": {"type": "string", "minLength": 1, "maxLength": 512}},
    },
}

def ensure_response_limit(value: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(value)
    if len(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > MAX_SAFE_ENVELOPE_BYTES:
        raise NexusMcpError("INTERNAL_ERROR", "safe response exceeds the configured limit")
    return result
