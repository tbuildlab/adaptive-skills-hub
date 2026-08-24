"""Strict, versioned MCP input schemas and safe error vocabulary."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import re
from typing import Any, Mapping
from uuid import UUID

from .host_inventory import (
    HOST_CAPABILITY_SNAPSHOT_SCHEMA_VERSION,
    HOST_INVENTORY_TTL_SECONDS,
    PRESENTATION_INTERFACES,
    HostCapability,
    HostCapabilitySnapshot,
)

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
MAX_HOST_CAPABILITIES = 16
MAX_HOST_INTERFACES = 8
HOST_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
HOST_CAPABILITY_KINDS = frozenset({"skill", "plugin", "tool"})
HOST_CAPABILITY_AVAILABILITY = frozenset({
    "tool_callable_current_turn",
    "skill_loadable_current_turn",
    "metadata_visible",
    "enabled_unverified",
    "installed_unverified",
    "disabled",
    "unavailable",
})
HOST_CAPABILITY_EVIDENCE = frozenset({
    "current_turn_tool_catalog",
    "current_turn_skill_metadata",
    "current_turn_plugin_metadata",
})
HOST_LOGICAL_CAPABILITIES = frozenset({"chatgpt.presentations", "unmapped"})


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


def _safe_display_name(value: Any) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > 96
        or _bytes(value.strip()) > 128
    ):
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability display name is invalid")
    name = value.strip()
    if any(ord(char) < 32 or char in "\\/" for char in name) or re.search(r"(?:^|\s)[a-zA-Z]:", name):
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability display name contains unsafe content")
    return name


def _utc_timestamp(value: Any, now: datetime) -> datetime:
    if not isinstance(value, str) or len(value) > 40:
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host inventory timestamp is invalid")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host inventory timestamp is invalid") from exc
    if parsed.tzinfo is None:
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host inventory timestamp must be UTC")
    parsed = parsed.astimezone(timezone.utc)
    if parsed < now - timedelta(seconds=HOST_INVENTORY_TTL_SECONDS) or parsed > now + timedelta(seconds=30):
        raise NexusMcpError("HOST_INVENTORY_STALE", "Host inventory is not current")
    return parsed


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


def parse_host_capability_snapshot(
    value: Any, *, now: datetime | None = None,
) -> HostCapabilitySnapshot:
    """Parse a non-authoritative current-turn Host metadata snapshot.

    The schema deliberately excludes descriptions, instructions, paths, URLs,
    invocation handles, permissions, and environment data.  The accepted
    enums can support bounded classification, but never authorize execution.
    """
    data = _object(value, {
        "schema_version", "captured_at", "snapshot_id", "host_surface",
        "inventory_scope", "inventory_completeness", "task_category",
        "required_interfaces", "capabilities",
    })
    required = {
        "schema_version", "captured_at", "snapshot_id", "host_surface",
        "inventory_scope", "inventory_completeness", "task_category",
        "required_interfaces", "capabilities",
    }
    if set(data) != required:
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability snapshot is incomplete")
    if data.get("schema_version") != HOST_CAPABILITY_SNAPSHOT_SCHEMA_VERSION:
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability snapshot schema is invalid")
    if data.get("host_surface") != "chatgpt_desktop":
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host surface is unsupported")
    if data.get("inventory_scope") != "current_turn_host_visible_subset":
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host inventory scope is invalid")
    if data.get("inventory_completeness") != "not_globally_enumerated":
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host inventory must not claim global completeness")
    if data.get("task_category") != "presentation":
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host inventory task category is unsupported")
    snapshot_id = data.get("snapshot_id")
    if not isinstance(snapshot_id, str):
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host inventory snapshot ID is invalid")
    try:
        UUID(snapshot_id)
    except (ValueError, AttributeError) as exc:
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host inventory snapshot ID is invalid") from exc
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    captured_at = _utc_timestamp(data.get("captured_at"), current)

    required_interfaces = data.get("required_interfaces")
    if (
        not isinstance(required_interfaces, list)
        or not required_interfaces
        or len(required_interfaces) > MAX_HOST_INTERFACES
        or not all(isinstance(item, str) and item in PRESENTATION_INTERFACES for item in required_interfaces)
        or len(set(required_interfaces)) != len(required_interfaces)
    ):
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host required interfaces are invalid")

    raw_capabilities = data.get("capabilities")
    if not isinstance(raw_capabilities, list) or len(raw_capabilities) > MAX_HOST_CAPABILITIES:
        raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability count is invalid")
    capabilities: list[HostCapability] = []
    identities: set[tuple[str, str]] = set()
    mapped_logical_capabilities: set[str] = set()
    for raw in raw_capabilities:
        item = _object(raw, {
            "capability_id", "provider_id", "display_name", "resource_kind",
            "availability", "evidence", "interfaces", "logical_capability",
        })
        if len(item) != 8:
            raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability descriptor is incomplete")
        capability_id = item.get("capability_id")
        provider_id = item.get("provider_id")
        if not isinstance(capability_id, str) or not HOST_ID_RE.fullmatch(capability_id):
            raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability ID is invalid")
        if not isinstance(provider_id, str) or not HOST_ID_RE.fullmatch(provider_id):
            raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability provider ID is invalid")
        identity = (provider_id.casefold(), capability_id.casefold())
        if identity in identities:
            raise NexusMcpError("HOST_CAPABILITY_DUPLICATE_CONFLICT", "Host capability identity is duplicated")
        identities.add(identity)
        resource_kind = item.get("resource_kind")
        availability = item.get("availability")
        evidence = item.get("evidence")
        interfaces = item.get("interfaces")
        logical_capability = item.get("logical_capability")
        if resource_kind not in HOST_CAPABILITY_KINDS:
            raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability kind is invalid")
        if availability not in HOST_CAPABILITY_AVAILABILITY:
            raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability availability is invalid")
        if (
            not isinstance(evidence, list)
            or not evidence
            or len(evidence) > 4
            or not all(isinstance(entry, str) and entry in HOST_CAPABILITY_EVIDENCE for entry in evidence)
            or len(set(evidence)) != len(evidence)
        ):
            raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability evidence is invalid")
        if (
            not isinstance(interfaces, list)
            or len(interfaces) > MAX_HOST_INTERFACES
            or not all(isinstance(entry, str) and entry in PRESENTATION_INTERFACES for entry in interfaces)
            or len(set(interfaces)) != len(interfaces)
        ):
            raise NexusMcpError("HOST_INVENTORY_INVALID", "Host capability interfaces are invalid")
        if logical_capability not in HOST_LOGICAL_CAPABILITIES:
            raise NexusMcpError("HOST_INVENTORY_INVALID", "Host logical capability is invalid")
        if logical_capability != "unmapped":
            if logical_capability in mapped_logical_capabilities:
                raise NexusMcpError("HOST_CAPABILITY_DUPLICATE_CONFLICT", "Host execution mapping is duplicated")
            mapped_logical_capabilities.add(str(logical_capability))
        if availability == "tool_callable_current_turn" and "current_turn_tool_catalog" not in evidence:
            raise NexusMcpError("HOST_CAPABILITY_UNVERIFIED", "Callable Host capability lacks current tool evidence")
        if availability == "skill_loadable_current_turn" and "current_turn_skill_metadata" not in evidence:
            raise NexusMcpError("HOST_CAPABILITY_UNVERIFIED", "Loadable Host Skill lacks current metadata evidence")
        if logical_capability != "unmapped" and (
            availability != "tool_callable_current_turn" or "current_turn_tool_catalog" not in evidence
        ):
            raise NexusMcpError("HOST_CAPABILITY_UNVERIFIED", "Mapped Host capability is not currently callable")
        capabilities.append(HostCapability(
            capability_id=capability_id,
            provider_id=provider_id,
            display_name=_safe_display_name(item.get("display_name")),
            resource_kind=str(resource_kind),
            availability=str(availability),
            evidence=tuple(sorted(evidence)),
            interfaces=tuple(sorted(interfaces)),
            logical_capability=str(logical_capability),
        ))
    capabilities.sort(key=lambda entry: (entry.provider_id.casefold(), entry.capability_id.casefold()))
    return HostCapabilitySnapshot(
        captured_at=captured_at,
        snapshot_id=snapshot_id,
        host_surface="chatgpt_desktop",
        inventory_scope="current_turn_host_visible_subset",
        inventory_completeness="not_globally_enumerated",
        task_category="presentation",
        required_interfaces=tuple(sorted(required_interfaces)),
        capabilities=tuple(capabilities),
    )


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
ASSESS_HOST_CAPABILITIES_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False,
    "required": [
        "schema_version", "captured_at", "snapshot_id", "host_surface",
        "inventory_scope", "inventory_completeness", "task_category",
        "required_interfaces", "capabilities",
    ],
    "properties": {
        "schema_version": {"const": HOST_CAPABILITY_SNAPSHOT_SCHEMA_VERSION},
        "captured_at": {"type": "string", "minLength": 20, "maxLength": 40},
        "snapshot_id": {"type": "string", "minLength": 36, "maxLength": 36},
        "host_surface": {"const": "chatgpt_desktop"},
        "inventory_scope": {"const": "current_turn_host_visible_subset"},
        "inventory_completeness": {"const": "not_globally_enumerated"},
        "task_category": {"const": "presentation"},
        "required_interfaces": {
            "type": "array", "minItems": 1, "maxItems": MAX_HOST_INTERFACES,
            "uniqueItems": True,
            "items": {"type": "string", "enum": sorted(PRESENTATION_INTERFACES)},
        },
        "capabilities": {
            "type": "array", "maxItems": MAX_HOST_CAPABILITIES,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": [
                    "capability_id", "provider_id", "display_name", "resource_kind",
                    "availability", "evidence", "interfaces", "logical_capability",
                ],
                "properties": {
                    "capability_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9._:-]{0,127}$"},
                    "provider_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9._:-]{0,127}$"},
                    "display_name": {"type": "string", "minLength": 1, "maxLength": 96},
                    "resource_kind": {"type": "string", "enum": sorted(HOST_CAPABILITY_KINDS)},
                    "availability": {"type": "string", "enum": sorted(HOST_CAPABILITY_AVAILABILITY)},
                    "evidence": {
                        "type": "array", "minItems": 1, "maxItems": 4, "uniqueItems": True,
                        "items": {"type": "string", "enum": sorted(HOST_CAPABILITY_EVIDENCE)},
                    },
                    "interfaces": {
                        "type": "array", "maxItems": MAX_HOST_INTERFACES, "uniqueItems": True,
                        "items": {"type": "string", "enum": sorted(PRESENTATION_INTERFACES)},
                    },
                    "logical_capability": {"type": "string", "enum": sorted(HOST_LOGICAL_CAPABILITIES)},
                },
            },
        },
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
