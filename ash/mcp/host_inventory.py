"""Bounded assessment of Host-surfaced capability metadata.

This module does not enumerate ChatGPT Desktop, inspect plugin state, or grant
execution authority.  It classifies a small metadata snapshot that the Host
has already surfaced in the current conversation.  The snapshot is advisory
and untrusted; only a separately reviewed Host mapping plus a fresh Host-side
eligibility check can lead to execution.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any, Mapping, MutableSet
from uuid import UUID

from .handoff import (
    HOST_NATIVE_PRESENTATIONS_MODE,
    HOST_PRESENTATIONS_CAPABILITY,
    validate_host_receipt,
)
from .host_mapping import PRESENTATIONS_MAPPING_ID


HOST_CAPABILITY_SNAPSHOT_SCHEMA_VERSION = "nexus.host-capability-snapshot.v1"
HOST_CAPABILITY_ASSESSMENT_SCHEMA_VERSION = "nexus.host-capability-assessment.v1"
HOST_CAPABILITY_RECEIPT_SCHEMA_VERSION = "nexus.host-capability-receipt.v1"
HOST_INVENTORY_TTL_SECONDS = 120

PRESENTATION_INTERFACES = frozenset({
    "editable_pptx_create",
    "presentation_create",
    "presentation_edit",
    "presentation_enhance",
    "presentation_review",
    "pptx_open_render_validate",
})

# This is an execution-policy allowlist, not a discovery list.  Display names
# never select a mapping.  New mappings require an explicit reviewed code
# change and Host acceptance evidence.
APPROVED_HOST_MAPPINGS: dict[str, dict[str, Any]] = {
    HOST_PRESENTATIONS_CAPABILITY: {
        "mapping_id": PRESENTATIONS_MAPPING_ID,
        "requested_execution_mode": HOST_NATIVE_PRESENTATIONS_MODE,
        "interfaces": frozenset({
            "editable_pptx_create",
            "presentation_create",
            "presentation_edit",
            "presentation_enhance",
            "presentation_review",
            "pptx_open_render_validate",
        }),
    },
}


@dataclass(frozen=True)
class HostCapability:
    capability_id: str
    provider_id: str
    display_name: str
    resource_kind: str
    availability: str
    evidence: tuple[str, ...]
    interfaces: tuple[str, ...]
    logical_capability: str


@dataclass(frozen=True)
class HostCapabilitySnapshot:
    captured_at: datetime
    snapshot_id: str
    host_surface: str
    inventory_scope: str
    inventory_completeness: str
    task_category: str
    required_interfaces: tuple[str, ...]
    capabilities: tuple[HostCapability, ...]


@dataclass(frozen=True)
class CapabilityAssessment:
    capability: HostCapability
    functional_role: str
    classification: str
    decision_state: str
    reason_codes: tuple[str, ...]
    covered_interfaces: tuple[str, ...]
    mapping_id: str | None = None
    requested_execution_mode: str | None = None


@dataclass(frozen=True)
class HostCapabilityDecision:
    snapshot_digest: str
    status: str
    result_code: str
    assessments: tuple[CapabilityAssessment, ...]
    selected_identities: tuple[tuple[str, str], ...]


def _functional_role(capability: HostCapability) -> str:
    interfaces = set(capability.interfaces)
    if "editable_pptx_create" in interfaces:
        return "primary_creator"
    if "presentation_create" in interfaces:
        return "alternative"
    if interfaces & {"presentation_edit", "presentation_enhance"}:
        return "enhancer"
    if interfaces & {"presentation_review", "pptx_open_render_validate"}:
        return "reviewer"
    return "incompatible"


def _mapping_for(capability: HostCapability) -> dict[str, Any] | None:
    mapping = APPROVED_HOST_MAPPINGS.get(capability.logical_capability)
    if mapping is None:
        return None
    if capability.availability != "tool_callable_current_turn":
        return None
    if "current_turn_tool_catalog" not in capability.evidence:
        return None
    if not set(capability.interfaces) <= set(mapping["interfaces"]):
        return None
    return mapping


def _evidence_rank(capability: HostCapability) -> int:
    evidence = set(capability.evidence)
    if "current_turn_tool_catalog" in evidence:
        return 3
    if "current_turn_skill_metadata" in evidence:
        return 2
    if "current_turn_plugin_metadata" in evidence:
        return 1
    return 0


def snapshot_digest(snapshot: HostCapabilitySnapshot) -> str:
    """Return a deterministic integrity binding, never an authenticity claim."""
    value = {
        "schema_version": HOST_CAPABILITY_SNAPSHOT_SCHEMA_VERSION,
        "captured_at": snapshot.captured_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "snapshot_id": snapshot.snapshot_id,
        "host_surface": snapshot.host_surface,
        "inventory_scope": snapshot.inventory_scope,
        "inventory_completeness": snapshot.inventory_completeness,
        "task_category": snapshot.task_category,
        "required_interfaces": list(snapshot.required_interfaces),
        "capabilities": [
            {
                "capability_id": item.capability_id,
                "provider_id": item.provider_id,
                "display_name": item.display_name,
                "resource_kind": item.resource_kind,
                "availability": item.availability,
                "evidence": list(item.evidence),
                "interfaces": list(item.interfaces),
                "logical_capability": item.logical_capability,
            }
            for item in snapshot.capabilities
        ],
    }
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def assess_host_capabilities(snapshot: HostCapabilitySnapshot) -> HostCapabilityDecision:
    """Classify and choose the smallest mapped current-turn capability set."""
    required = set(snapshot.required_interfaces)
    assessments: list[CapabilityAssessment] = []
    eligible: list[tuple[HostCapability, dict[str, Any], str, set[str]]] = []

    for capability in snapshot.capabilities:
        role = _functional_role(capability)
        mapping = _mapping_for(capability)
        covered = required & set(capability.interfaces)
        reasons: list[str] = []
        classification = role
        if role == "incompatible":
            classification = "incompatible"
            reasons.append("NO_REQUIRED_INTERFACE_COVERAGE")
        elif not covered:
            classification = role
            reasons.append("NO_REQUIRED_INTERFACE_COVERAGE")
        elif capability.availability in {"disabled", "unavailable"}:
            classification = "unavailable"
            reasons.append("HOST_CAPABILITY_UNAVAILABLE")
        elif capability.availability in {
            "metadata_visible", "enabled_unverified", "installed_unverified",
            "skill_loadable_current_turn",
        }:
            classification = "unavailable"
            reasons.append("HOST_CAPABILITY_UNVERIFIED")
        elif mapping is None:
            classification = "alternative" if role == "primary_creator" else role
            reasons.append("HOST_MAPPING_UNAPPROVED")
        else:
            eligible.append((capability, mapping, role, covered))
            reasons.append("CURRENT_TURN_MAPPING_ELIGIBLE")
        assessments.append(CapabilityAssessment(
            capability=capability,
            functional_role=role,
            classification=classification,
            decision_state="considered",
            reason_codes=tuple(reasons),
            covered_interfaces=tuple(sorted(covered)),
            mapping_id=str(mapping["mapping_id"]) if mapping else None,
            requested_execution_mode=str(mapping["requested_execution_mode"]) if mapping else None,
        ))

    # Evidence and coverage dominate; names are never ranking signals. Stable
    # IDs are only the final deterministic tie-breaker.
    eligible.sort(key=lambda item: (
        -len(item[3]),
        -_evidence_rank(item[0]),
        item[0].provider_id.casefold(),
        item[0].capability_id.casefold(),
    ))
    required_order = tuple(sorted(required))
    interface_bits = {name: 1 << index for index, name in enumerate(required_order)}
    full_mask = (1 << len(required_order)) - 1

    def coverage_mask(covered: set[str]) -> int:
        value = 0
        for interface in covered:
            value |= interface_bits[interface]
        return value

    def selection_key(indices: tuple[int, ...]) -> tuple[Any, ...]:
        return (
            len(indices),
            -sum(_evidence_rank(eligible[index][0]) for index in indices),
            tuple(
                (
                    eligible[index][0].provider_id.casefold(),
                    eligible[index][0].capability_id.casefold(),
                )
                for index in indices
            ),
        )

    # The interface vocabulary is capped at eight, so an exact dynamic program
    # has at most 256 coverage states. This proves minimum cardinality instead
    # of relying on a greedy approximation.
    selections: dict[int, tuple[int, ...]] = {0: ()}
    for index, (_capability, _mapping, _role, covered) in enumerate(eligible):
        candidate_mask = coverage_mask(covered)
        for mask, indices in list(selections.items()):
            combined = mask | candidate_mask
            proposed = indices + (index,)
            current = selections.get(combined)
            if current is None or selection_key(proposed) < selection_key(current):
                selections[combined] = proposed

    selected_indices = selections.get(full_mask)
    selected_identities: list[tuple[str, str]] = []
    if selected_indices is not None:
        selected_identities = [
            (
                eligible[index][0].provider_id.casefold(),
                eligible[index][0].capability_id.casefold(),
            )
            for index in selected_indices
        ]

    if selected_indices is None:
        selected_identities = []
        status = "no_executable_host_capability"
        result_code = "HOST_CAPABILITY_UNAVAILABLE"
    else:
        status = "selection_ready"
        result_code = "HOST_CAPABILITY_SELECTION_READY"

    updated: list[CapabilityAssessment] = []
    eligible_identities = {
        (item[0].provider_id.casefold(), item[0].capability_id.casefold())
        for item in eligible
    }
    selected_coverage: set[str] = set()
    if selected_indices is not None:
        for index in selected_indices:
            selected_coverage.update(eligible[index][3])
    for assessment in assessments:
        identity = (
            assessment.capability.provider_id.casefold(),
            assessment.capability.capability_id.casefold(),
        )
        if identity in selected_identities:
            updated.append(replace(
                assessment,
                decision_state="selected",
                reason_codes=("MINIMUM_REQUIRED_INTERFACE_COVERAGE",),
            ))
        elif identity in eligible_identities:
            if selected_indices is None:
                updated.append(replace(
                    assessment,
                    decision_state="rejected",
                    reason_codes=("INCOMPLETE_REQUIRED_COVERAGE",),
                ))
            else:
                updated.append(replace(
                    assessment,
                    classification="redundant" if assessment.functional_role == "primary_creator" else assessment.functional_role,
                    decision_state="rejected",
                    reason_codes=("REDUNDANT_REQUIRED_COVERAGE",),
                ))
        elif (
            selected_indices is not None
            and assessment.capability.availability == "tool_callable_current_turn"
            and assessment.functional_role == "primary_creator"
            and assessment.covered_interfaces
            and set(assessment.covered_interfaces) <= selected_coverage
        ):
            updated.append(replace(
                assessment,
                classification="redundant",
                decision_state="rejected",
                reason_codes=tuple(dict.fromkeys((*assessment.reason_codes, "REDUNDANT_REQUIRED_COVERAGE"))),
            ))
        else:
            updated.append(replace(assessment, decision_state="rejected"))

    return HostCapabilityDecision(
        snapshot_digest=snapshot_digest(snapshot),
        status=status,
        result_code=result_code,
        assessments=tuple(updated),
        selected_identities=tuple(selected_identities),
    )


def assessment_issue_window(
    captured_at: datetime, now: datetime | None = None,
) -> tuple[str, str]:
    """Issue an assessment without extending the source snapshot lifetime."""
    issued = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    snapshot_expiry = captured_at.astimezone(timezone.utc) + timedelta(
        seconds=HOST_INVENTORY_TTL_SECONDS,
    )
    expires = min(
        issued + timedelta(seconds=HOST_INVENTORY_TTL_SECONDS),
        snapshot_expiry,
    )
    return (
        issued.isoformat().replace("+00:00", "Z"),
        expires.isoformat().replace("+00:00", "Z"),
    )


def _current_assessment(
    assessment: Mapping[str, Any], now: datetime | None = None,
) -> bool:
    if assessment.get("schema_version") != HOST_CAPABILITY_ASSESSMENT_SCHEMA_VERSION:
        return False
    assessment_id = assessment.get("assessment_id")
    digest = assessment.get("snapshot_sha256")
    issued_at = assessment.get("issued_at")
    expires_at = assessment.get("expires_at")
    if not all(isinstance(value, str) for value in (assessment_id, digest, issued_at, expires_at)):
        return False
    try:
        UUID(assessment_id)
    except (ValueError, AttributeError):
        return False
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest.casefold()):
        return False
    try:
        issued = datetime.fromisoformat(issued_at.replace("Z", "+00:00"))
        expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    if issued.tzinfo is None or expires.tzinfo is None:
        return False
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    issued = issued.astimezone(timezone.utc)
    expires = expires.astimezone(timezone.utc)
    return (
        issued <= current + timedelta(seconds=30)
        and issued <= expires
        and current < expires
        and expires <= issued + timedelta(seconds=HOST_INVENTORY_TTL_SECONDS)
    )


def validate_inventory_bound_host_receipt(
    assessment: Mapping[str, Any],
    handoff: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    seen_assessment_ids: MutableSet[str] | None = None,
    seen_handoff_ids: MutableSet[str] | None = None,
    now: datetime | None = None,
) -> str:
    """Validate a Host-held inventory/R4 receipt binding.

    This helper is intentionally not an MCP tool and performs no action. The
    Host keeps the assessment, handoff, replay sets, artifact, and receipt in
    its own execution context. Nexus only provides a deterministic validator
    for integration tests and future supported Host adapters.
    """
    if not isinstance(assessment, Mapping) or not _current_assessment(assessment, now):
        return "HOST_INVENTORY_ASSESSMENT_EXPIRED"
    security = assessment.get("security_result")
    if (
        assessment.get("status") != "selection_ready"
        or assessment.get("host_surface") != "chatgpt_desktop"
        or assessment.get("inventory_scope") != "current_turn_host_visible_subset"
        or assessment.get("inventory_completeness") != "not_globally_enumerated"
        or assessment.get("task_category") != "presentation"
        or not isinstance(security, Mapping)
        or security.get("code") != "HOST_CAPABILITY_SELECTION_READY"
        or security.get("inventory_authority") != "host_asserted_non_authoritative"
        or security.get("mcp_execution_authority") != "none"
        or security.get("private_host_state_access") != "none"
    ):
        return "HOST_INVENTORY_ASSESSMENT_INVALID"
    required = {
        "schema_version", "assessment_id", "snapshot_sha256",
        "inventory_states", "selected_capabilities", "r4_receipt",
    }
    if not isinstance(receipt, Mapping) or set(receipt) != required:
        return "HOST_INVENTORY_RECEIPT_MALFORMED"
    if receipt.get("schema_version") != HOST_CAPABILITY_RECEIPT_SCHEMA_VERSION:
        return "HOST_INVENTORY_RECEIPT_MALFORMED"
    assessment_id = assessment.get("assessment_id")
    if receipt.get("assessment_id") != assessment_id:
        return "HOST_INVENTORY_ASSESSMENT_MISMATCH"
    if receipt.get("snapshot_sha256") != assessment.get("snapshot_sha256"):
        return "HOST_INVENTORY_DIGEST_MISMATCH"
    if receipt.get("inventory_states") != ["considered", "selected"]:
        return "HOST_INVENTORY_STATE_INVALID"

    selected = assessment.get("selected_capabilities")
    if not isinstance(selected, list) or len(selected) != 1:
        return "HOST_INVENTORY_SELECTION_INVALID"
    selected_item = selected[0]
    selected_required = {
        "capability_id", "provider_id", "logical_capability", "mapping_id",
        "requested_execution_mode",
    }
    if not isinstance(selected_item, Mapping) or set(selected_item) != selected_required:
        return "HOST_INVENTORY_SELECTION_INVALID"
    if receipt.get("selected_capabilities") != [dict(selected_item)]:
        return "HOST_INVENTORY_SELECTION_MISMATCH"

    profile = handoff.get("host_execution_profile")
    if (
        not isinstance(profile, Mapping)
        or selected_item.get("mapping_id") != profile.get("mapping_id")
        or selected_item.get("logical_capability") != handoff.get("logical_host_capability")
        or selected_item.get("requested_execution_mode") != handoff.get("requested_execution_mode")
    ):
        return "HOST_INVENTORY_HANDOFF_MISMATCH"

    r4_receipt = receipt.get("r4_receipt")
    if not isinstance(r4_receipt, Mapping):
        return "HOST_INVENTORY_RECEIPT_MALFORMED"
    result = validate_host_receipt(handoff, r4_receipt, now=now)
    if result != "EXECUTION_SUCCEEDED":
        return result

    handoff_id = handoff.get("handoff_id")
    if seen_assessment_ids is not None and isinstance(assessment_id, str):
        if assessment_id in seen_assessment_ids:
            return "HOST_INVENTORY_ASSESSMENT_REPLAYED"
    if seen_handoff_ids is not None and isinstance(handoff_id, str):
        if handoff_id in seen_handoff_ids:
            return "HANDOFF_REPLAYED"
    if seen_assessment_ids is not None and isinstance(assessment_id, str):
        seen_assessment_ids.add(assessment_id)
    if seen_handoff_ids is not None and isinstance(handoff_id, str):
        seen_handoff_ids.add(handoff_id)
    return "EXECUTION_SUCCEEDED"
