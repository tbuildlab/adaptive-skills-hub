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
ARTIFACT_STATE_SCHEMA_VERSION = "nexus.host-artifact-state.v1"
ALLOWED_ARTIFACT_OBSERVATIONS = frozenset({
    "layout_density_high",
    "visual_hierarchy_weak",
    "text_legibility_low",
    "contrast_needs_review",
})
REQUIRED_PRESENTATION_CHECKS = frozenset({
    "artifact_created",
    "artifact_editable",
    "presentation_open_render",
})


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


@dataclass(frozen=True)
class HostArtifactState:
    """A fixed, content-free Host assertion used only to request R5 analysis.

    It deliberately has no artifact reference, filesystem path, task text,
    user context, previous handoff, or Skill hash. The Host must independently
    bind it to its current validated R4 receipt before acting on a result.
    """

    artifact_kind: str
    base_mapping_id: str
    base_execution_state: str
    base_validation_state: str
    checks: tuple[tuple[str, str], ...]
    observations: tuple[str, ...]
    enhancement_pass: int


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

# R4 intentionally takes the same bounded planning inputs as ``plan_task``.
# It never accepts a path, selected Skill, hash, existing handoff, or host
# result.  The server independently replans and re-verifies before issuing an
# execution intent.
PREPARE_HOST_HANDOFF_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False, "required": ["task", "workspace_id"],
    "properties": {
        "task": {"type": "string", "minLength": 1, "maxLength": MAX_TASK_BYTES},
        "workspace_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$"},
        "project_context_mode": {"type": "string", "enum": ["none", "governance"], "default": "governance"},
        "constraints": {"type": "array", "maxItems": MAX_CONSTRAINTS, "items": {"type": "string", "minLength": 1, "maxLength": 512}},
    },
}

# R5 takes only a strict, redacted artifact-state assertion. It does not accept
# a path, artifact reference, task, prior handoff, receipt, Skill, Agent, hash,
# or caller-selected candidate. The Host must derive this state from its current
# validated R4 result before it can act on the returned intent.
PREPARE_ENHANCEMENT_HANDOFF_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False,
    "required": [
        "schema_version", "artifact_kind", "base_mapping_id",
        "base_execution_state", "base_validation_state", "checks",
        "observations", "enhancement_pass",
    ],
    "properties": {
        "schema_version": {"const": ARTIFACT_STATE_SCHEMA_VERSION},
        "artifact_kind": {"const": "pptx"},
        "base_mapping_id": {"const": "nexus.host-map.presentations.v1"},
        "base_execution_state": {"const": "execution_succeeded"},
        "base_validation_state": {"const": "validation_passed"},
        "checks": {
            "type": "object", "additionalProperties": False,
            "required": sorted(REQUIRED_PRESENTATION_CHECKS),
            "properties": {item: {"const": "passed"} for item in sorted(REQUIRED_PRESENTATION_CHECKS)},
        },
        "observations": {
            "type": "array", "maxItems": 3, "uniqueItems": True,
            "items": {"type": "string", "enum": sorted(ALLOWED_ARTIFACT_OBSERVATIONS)},
        },
        "enhancement_pass": {"type": "integer", "minimum": 0, "maximum": 1},
    },
}


def parse_prepare_host_handoff_request(value: Any) -> PlanRequest:
    """Parse R4 inputs with the frozen R2 planning boundary."""
    return parse_plan_request(value)


def parse_prepare_enhancement_handoff_request(value: Any) -> HostArtifactState:
    """Parse the intentionally closed R5 host-artifact-state envelope.

    This only establishes that a request is well formed; it cannot make
    caller-supplied state authoritative. The Desktop Host remains responsible
    for deriving the state from the current, validated R4 execution receipt.
    """
    data = _object(value, {
        "schema_version", "artifact_kind", "base_mapping_id",
        "base_execution_state", "base_validation_state", "checks",
        "observations", "enhancement_pass",
    })
    required = {
        "schema_version", "artifact_kind", "base_mapping_id",
        "base_execution_state", "base_validation_state", "checks",
        "observations", "enhancement_pass",
    }
    if set(data) != required:
        raise NexusMcpError("INVALID_REQUEST", "host artifact state is incomplete")
    if data.get("schema_version") != ARTIFACT_STATE_SCHEMA_VERSION:
        raise NexusMcpError("INVALID_REQUEST", "host artifact state schema is invalid")
    if data.get("artifact_kind") != "pptx":
        raise NexusMcpError("HOST_ARTIFACT_UNSUPPORTED", "artifact kind is not supported for enhancement")
    if data.get("base_mapping_id") != "nexus.host-map.presentations.v1":
        raise NexusMcpError("HOST_ARTIFACT_UNVERIFIED", "base host mapping is not eligible for enhancement")
    if data.get("base_execution_state") != "execution_succeeded" or data.get("base_validation_state") != "validation_passed":
        raise NexusMcpError("HOST_ARTIFACT_UNVERIFIED", "base artifact has not passed host execution and validation")
    checks = data.get("checks")
    if not isinstance(checks, Mapping) or set(checks) != REQUIRED_PRESENTATION_CHECKS or any(item != "passed" for item in checks.values()):
        raise NexusMcpError("HOST_ARTIFACT_UNVERIFIED", "required host validation checks are not passed")
    observations = data.get("observations")
    if not isinstance(observations, list) or len(observations) > 3 or not all(isinstance(item, str) and item in ALLOWED_ARTIFACT_OBSERVATIONS for item in observations):
        raise NexusMcpError("INVALID_REQUEST", "host artifact observations are invalid")
    if len(set(observations)) != len(observations):
        raise NexusMcpError("INVALID_REQUEST", "host artifact observations must not repeat")
    enhancement_pass = data.get("enhancement_pass")
    if isinstance(enhancement_pass, bool) or not isinstance(enhancement_pass, int) or enhancement_pass < 0 or enhancement_pass > 1:
        raise NexusMcpError("INVALID_REQUEST", "enhancement pass is invalid")
    return HostArtifactState(
        artifact_kind="pptx",
        base_mapping_id="nexus.host-map.presentations.v1",
        base_execution_state="execution_succeeded",
        base_validation_state="validation_passed",
        checks=tuple(sorted((str(key), str(item)) for key, item in checks.items())),
        observations=tuple(sorted(observations)),
        enhancement_pass=enhancement_pass,
    )

def ensure_response_limit(value: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(value)
    if len(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > MAX_SAFE_ENVELOPE_BYTES:
        raise NexusMcpError("INTERNAL_ERROR", "safe response exceeds the configured limit")
    return result
