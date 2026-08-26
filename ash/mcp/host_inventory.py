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
from uuid import UUID, uuid4

from .handoff import (
    HOST_NATIVE_PRESENTATIONS_MODE,
    HOST_PRESENTATIONS_CAPABILITY,
    strict_handoff_digest_for_execution_start,
    validate_host_receipt,
)
from .host_mapping import (
    DIRECT_HOST_TOOL_BINDING,
    HOST_SKILL_WORKFLOW_BINDING,
    NO_EXECUTION_BINDING,
    PRESENTATIONS_HOST_CAPABILITY_ID,
    PRESENTATIONS_HOST_PROVIDER_ID,
    PRESENTATIONS_HOST_RESOURCE_KIND,
    PRESENTATIONS_MAPPING_ID,
)


HOST_CAPABILITY_TICKET_REQUEST_SCHEMA_VERSION = "nexus.host-capability-ticket-request.v1"
HOST_CAPABILITY_TICKET_SCHEMA_VERSION = "nexus.host-capability-ticket.v1"
HOST_CAPABILITY_SNAPSHOT_SCHEMA_VERSION = "nexus.host-capability-snapshot.v3"
HOST_CAPABILITY_ASSESSMENT_SCHEMA_VERSION = "nexus.host-capability-assessment.v3"
HOST_CAPABILITY_RECEIPT_SCHEMA_VERSION = "nexus.host-capability-receipt.v3"
HOST_INVENTORY_TTL_SECONDS = 120
MAX_OUTSTANDING_HOST_INVENTORY_TICKETS = 16

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
        "approved_identities": frozenset({
            (
                PRESENTATIONS_HOST_PROVIDER_ID,
                PRESENTATIONS_HOST_CAPABILITY_ID,
                PRESENTATIONS_HOST_RESOURCE_KIND,
            ),
        }),
        "binding_requirements": {
            HOST_SKILL_WORKFLOW_BINDING: {
                "availability": "skill_workflow_ready_current_turn",
                "evidence": frozenset({
                    "current_turn_skill_metadata",
                    "current_turn_skill_instructions",
                    "current_turn_tool_catalog",
                    "current_turn_execution_substrate",
                }),
                "resource_kind": "skill",
            },
        },
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
    execution_binding_kind: str


@dataclass(frozen=True)
class HostCapabilityTicketRequest:
    host_surface: str
    inventory_scope: str
    inventory_completeness: str
    task_category: str
    required_interfaces: tuple[str, ...]


@dataclass(frozen=True)
class HostCapabilityTicket:
    ticket_id: str
    issued_at: datetime
    expires_at: datetime
    monotonic_issued_at: float
    monotonic_deadline: float
    host_surface: str
    inventory_scope: str
    inventory_completeness: str
    task_category: str
    required_interfaces: tuple[str, ...]


@dataclass(frozen=True)
class HostInventoryExecutionStartClaim:
    """Host-local proof that freshness was checked before execution started.

    This object is never an MCP payload and grants no execution authority.  It
    only lets a later artifact receipt remain bound to an assessment/handoff
    that were current when the Host actually started work.
    """

    claim_id: str
    claimed_at: datetime
    ticket_id: str
    assessment_id: str
    snapshot_sha256: str
    handoff_id: str
    handoff_sha256: str
    capability_id: str
    provider_id: str
    logical_capability: str
    mapping_id: str
    requested_execution_mode: str
    execution_binding_kind: str
    selected_skill_resource_id: str
    selected_skill_content_sha256: str


@dataclass(frozen=True)
class HostCapabilitySnapshot:
    ticket_id: str
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
    execution_binding_kind: str = NO_EXECUTION_BINDING


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


def approved_mapping_identity(
    logical_capability: str,
    provider_id: str,
    capability_id: str,
    resource_kind: str,
) -> bool:
    """Check a reviewed stable Host identity without consulting its label."""
    mapping = APPROVED_HOST_MAPPINGS.get(logical_capability)
    if mapping is None:
        return False
    identity = (provider_id.casefold(), capability_id.casefold(), resource_kind)
    return identity in mapping.get("approved_identities", ())


def _declared_mapping_for(capability: HostCapability) -> dict[str, Any] | None:
    mapping = APPROVED_HOST_MAPPINGS.get(capability.logical_capability)
    if mapping is None:
        return None
    if not approved_mapping_identity(
        capability.logical_capability,
        capability.provider_id,
        capability.capability_id,
        capability.resource_kind,
    ):
        return None
    return mapping


def _mapping_for(capability: HostCapability) -> dict[str, Any] | None:
    mapping = _declared_mapping_for(capability)
    if mapping is None:
        return None
    requirement = mapping["binding_requirements"].get(capability.execution_binding_kind)
    if requirement is None:
        return None
    if capability.resource_kind != requirement["resource_kind"]:
        return None
    if capability.availability != requirement["availability"]:
        return None
    if not set(requirement["evidence"]) <= set(capability.evidence):
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
        "ticket_id": snapshot.ticket_id,
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
                "execution_binding_kind": item.execution_binding_kind,
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
        declared_mapping = _declared_mapping_for(capability)
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
        elif declared_mapping is not None and mapping is None:
            classification = "unavailable"
            reasons.append("HOST_EXECUTION_BINDING_UNAVAILABLE")
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
            execution_binding_kind=capability.execution_binding_kind,
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
        result_code = (
            "HOST_EXECUTION_BINDING_UNAVAILABLE"
            if any("HOST_EXECUTION_BINDING_UNAVAILABLE" in item.reason_codes for item in assessments)
            else "HOST_CAPABILITY_UNAVAILABLE"
        )
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
            and assessment.capability.availability in {
                "tool_callable_current_turn", "skill_workflow_ready_current_turn",
            }
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
    ticket: HostCapabilityTicket, now: datetime | None = None,
) -> tuple[str, str]:
    """Issue an assessment without extending the server ticket lifetime."""
    issued = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    expires = min(issued + timedelta(seconds=HOST_INVENTORY_TTL_SECONDS), ticket.expires_at)
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
    ticket_id = assessment.get("ticket_id")
    digest = assessment.get("snapshot_sha256")
    ticket_issued_at = assessment.get("ticket_issued_at")
    issued_at = assessment.get("issued_at")
    expires_at = assessment.get("expires_at")
    if not all(
        isinstance(value, str)
        for value in (
            assessment_id, ticket_id, digest, ticket_issued_at, issued_at, expires_at,
        )
    ):
        return False
    try:
        UUID(assessment_id)
        UUID(ticket_id)
    except (ValueError, AttributeError):
        return False
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest.casefold()):
        return False
    try:
        ticket_issued = datetime.fromisoformat(ticket_issued_at.replace("Z", "+00:00"))
        issued = datetime.fromisoformat(issued_at.replace("Z", "+00:00"))
        expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    if ticket_issued.tzinfo is None or issued.tzinfo is None or expires.tzinfo is None:
        return False
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    ticket_issued = ticket_issued.astimezone(timezone.utc)
    issued = issued.astimezone(timezone.utc)
    expires = expires.astimezone(timezone.utc)
    return (
        issued <= current + timedelta(seconds=30)
        and ticket_issued <= issued <= expires
        and current < expires
        and expires <= ticket_issued + timedelta(seconds=HOST_INVENTORY_TTL_SECONDS)
    )


def _assessment_security_ready(assessment: Mapping[str, Any]) -> bool:
    security = assessment.get("security_result")
    return (
        assessment.get("status") == "selection_ready"
        and assessment.get("host_surface") == "chatgpt_desktop"
        and assessment.get("inventory_scope") == "current_turn_host_visible_subset"
        and assessment.get("inventory_completeness") == "not_globally_enumerated"
        and assessment.get("task_category") == "presentation"
        and isinstance(security, Mapping)
        and security.get("code") == "HOST_CAPABILITY_SELECTION_READY"
        and security.get("inventory_authority") == "host_asserted_non_authoritative"
        and security.get("mcp_execution_authority") == "none"
        and security.get("private_host_state_access") == "none"
    )


def _selected_assessment_item(assessment: Mapping[str, Any]) -> Mapping[str, Any] | None:
    selected = assessment.get("selected_capabilities")
    if not isinstance(selected, list) or len(selected) != 1:
        return None
    selected_item = selected[0]
    selected_required = {
        "capability_id", "provider_id", "logical_capability", "mapping_id",
        "requested_execution_mode", "execution_binding_kind",
    }
    if not isinstance(selected_item, Mapping) or set(selected_item) != selected_required:
        return None
    logical_capability = selected_item.get("logical_capability")
    mapping = APPROVED_HOST_MAPPINGS.get(logical_capability)
    if not isinstance(mapping, Mapping):
        return None
    binding = selected_item.get("execution_binding_kind")
    requirements = mapping.get("binding_requirements")
    if not isinstance(requirements, Mapping):
        return None
    requirement = requirements.get(binding)
    if not isinstance(requirement, Mapping):
        return None
    provider_id = selected_item.get("provider_id")
    capability_id = selected_item.get("capability_id")
    resource_kind = requirement.get("resource_kind")
    if not all(isinstance(value, str) for value in (provider_id, capability_id, resource_kind)):
        return None
    identity = (provider_id.casefold(), capability_id.casefold(), resource_kind)
    if (
        identity not in mapping.get("approved_identities", ())
        or selected_item.get("mapping_id") != mapping.get("mapping_id")
        or selected_item.get("requested_execution_mode") != mapping.get("requested_execution_mode")
    ):
        return None
    return selected_item


def claim_inventory_bound_execution_start(
    assessment: Mapping[str, Any],
    handoff: Mapping[str, Any],
    *,
    seen_assessment_ids: MutableSet[str] | None = None,
    seen_handoff_ids: MutableSet[str] | None = None,
    now: datetime | None = None,
) -> tuple[str, HostInventoryExecutionStartClaim | None]:
    """Claim a fresh assessment/handoff pair before Host execution begins.

    The caller owns and serializes the optional replay ledgers.  The returned
    frozen object stays Host-local; it is not a token and must never be accepted
    from user or MCP input.
    """
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if not isinstance(assessment, Mapping) or not _current_assessment(assessment, current):
        return "HOST_INVENTORY_ASSESSMENT_EXPIRED", None
    if not _assessment_security_ready(assessment):
        return "HOST_INVENTORY_ASSESSMENT_INVALID", None
    if not isinstance(handoff, Mapping):
        return "HANDOFF_NOT_ELIGIBLE", None
    handoff_sha256 = strict_handoff_digest_for_execution_start(handoff, current)
    if handoff_sha256 is None:
        return "HANDOFF_NOT_ELIGIBLE", None
    selected_item = _selected_assessment_item(assessment)
    if selected_item is None:
        return "HOST_INVENTORY_SELECTION_INVALID", None
    profile = handoff.get("host_execution_profile")
    if (
        not isinstance(profile, Mapping)
        or selected_item.get("mapping_id") != profile.get("mapping_id")
        or selected_item.get("logical_capability") != handoff.get("logical_host_capability")
        or selected_item.get("requested_execution_mode") != handoff.get("requested_execution_mode")
        or selected_item.get("execution_binding_kind") not in {
            DIRECT_HOST_TOOL_BINDING, HOST_SKILL_WORKFLOW_BINDING,
        }
    ):
        return "HOST_INVENTORY_HANDOFF_MISMATCH", None
    assessment_id = assessment.get("assessment_id")
    handoff_id = handoff.get("handoff_id")
    if not isinstance(assessment_id, str) or not isinstance(handoff_id, str):
        return "HOST_INVENTORY_ASSESSMENT_INVALID", None
    if seen_assessment_ids is not None and assessment_id in seen_assessment_ids:
        return "HOST_INVENTORY_ASSESSMENT_REPLAYED", None
    if seen_handoff_ids is not None and handoff_id in seen_handoff_ids:
        return "HANDOFF_REPLAYED", None
    if seen_assessment_ids is not None:
        seen_assessment_ids.add(assessment_id)
    if seen_handoff_ids is not None:
        seen_handoff_ids.add(handoff_id)
    return "EXECUTION_START_CLAIMED", HostInventoryExecutionStartClaim(
        claim_id=str(uuid4()),
        claimed_at=current,
        ticket_id=str(assessment.get("ticket_id")),
        assessment_id=assessment_id,
        snapshot_sha256=str(assessment.get("snapshot_sha256")),
        handoff_id=handoff_id,
        handoff_sha256=handoff_sha256,
        capability_id=str(selected_item.get("capability_id")),
        provider_id=str(selected_item.get("provider_id")),
        logical_capability=str(selected_item.get("logical_capability")),
        mapping_id=str(selected_item.get("mapping_id")),
        requested_execution_mode=str(selected_item.get("requested_execution_mode")),
        execution_binding_kind=str(selected_item.get("execution_binding_kind")),
        selected_skill_resource_id=str(handoff["selected_skill"]["resource_id"]),
        selected_skill_content_sha256=str(handoff["selected_skill"]["content_sha256"]),
    )


def validate_inventory_bound_host_receipt(
    assessment: Mapping[str, Any],
    handoff: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    execution_start_claim: HostInventoryExecutionStartClaim | None = None,
    seen_assessment_ids: MutableSet[str] | None = None,
    seen_handoff_ids: MutableSet[str] | None = None,
    seen_execution_claim_ids: MutableSet[str] | None = None,
    now: datetime | None = None,
) -> str:
    """Validate a Host-held inventory/R4 receipt binding.

    This helper is intentionally not an MCP tool and performs no action. The
    Host keeps the assessment, handoff, replay sets, artifact, and receipt in
    its own execution context. Nexus only provides a deterministic validator
    for integration tests and future supported Host adapters.
    """
    if not isinstance(assessment, Mapping):
        return "HOST_INVENTORY_ASSESSMENT_EXPIRED"
    if execution_start_claim is None:
        if not _current_assessment(assessment, now):
            return "HOST_INVENTORY_ASSESSMENT_EXPIRED"
    elif not isinstance(execution_start_claim, HostInventoryExecutionStartClaim):
        return "HOST_EXECUTION_START_CLAIM_INVALID"
    elif not _current_assessment(assessment, execution_start_claim.claimed_at):
        return "HOST_EXECUTION_START_CLAIM_INVALID"
    if not _assessment_security_ready(assessment):
        return "HOST_INVENTORY_ASSESSMENT_INVALID"
    required = {
        "schema_version", "ticket_id", "assessment_id", "snapshot_sha256",
        "inventory_states", "selected_capabilities", "r4_receipt",
    }
    if not isinstance(receipt, Mapping) or set(receipt) != required:
        return "HOST_INVENTORY_RECEIPT_MALFORMED"
    if receipt.get("schema_version") != HOST_CAPABILITY_RECEIPT_SCHEMA_VERSION:
        return "HOST_INVENTORY_RECEIPT_MALFORMED"
    assessment_id = assessment.get("assessment_id")
    if receipt.get("ticket_id") != assessment.get("ticket_id"):
        return "HOST_INVENTORY_TICKET_MISMATCH"
    if receipt.get("assessment_id") != assessment_id:
        return "HOST_INVENTORY_ASSESSMENT_MISMATCH"
    if receipt.get("snapshot_sha256") != assessment.get("snapshot_sha256"):
        return "HOST_INVENTORY_DIGEST_MISMATCH"
    if receipt.get("inventory_states") != ["considered", "selected"]:
        return "HOST_INVENTORY_STATE_INVALID"

    selected_item = _selected_assessment_item(assessment)
    if selected_item is None:
        return "HOST_INVENTORY_SELECTION_INVALID"
    if receipt.get("selected_capabilities") != [dict(selected_item)]:
        return "HOST_INVENTORY_SELECTION_MISMATCH"

    if not isinstance(handoff, Mapping):
        return (
            "HOST_EXECUTION_START_CLAIM_MISMATCH"
            if execution_start_claim is not None
            else "HOST_INVENTORY_HANDOFF_MISMATCH"
        )
    profile = handoff.get("host_execution_profile")
    if (
        not isinstance(profile, Mapping)
        or selected_item.get("mapping_id") != profile.get("mapping_id")
        or selected_item.get("logical_capability") != handoff.get("logical_host_capability")
        or selected_item.get("requested_execution_mode") != handoff.get("requested_execution_mode")
    ):
        return "HOST_INVENTORY_HANDOFF_MISMATCH"

    receipt_validation_time = now
    if execution_start_claim is not None:
        claim = execution_start_claim
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        if claim.claimed_at.tzinfo is None or claim.claimed_at.astimezone(timezone.utc) > current + timedelta(seconds=30):
            return "HOST_EXECUTION_START_CLAIM_INVALID"
        handoff_sha256 = strict_handoff_digest_for_execution_start(handoff, claim.claimed_at)
        selected_skill = handoff.get("selected_skill")
        if handoff_sha256 is None or not isinstance(selected_skill, Mapping):
            return "HOST_EXECUTION_START_CLAIM_MISMATCH"
        selected_resource_id = selected_skill.get("resource_id")
        selected_content_sha256 = selected_skill.get("content_sha256")
        if not isinstance(selected_resource_id, str) or not isinstance(selected_content_sha256, str):
            return "HOST_EXECUTION_START_CLAIM_MISMATCH"
        expected_claim = (
            assessment.get("ticket_id"), assessment_id,
            assessment.get("snapshot_sha256"), handoff.get("handoff_id"),
            handoff_sha256,
            selected_item.get("capability_id"), selected_item.get("provider_id"),
            selected_item.get("logical_capability"), selected_item.get("mapping_id"),
            selected_item.get("requested_execution_mode"),
            selected_item.get("execution_binding_kind"),
            selected_resource_id,
            selected_content_sha256,
        )
        observed_claim = (
            claim.ticket_id, claim.assessment_id, claim.snapshot_sha256,
            claim.handoff_id, claim.handoff_sha256,
            claim.capability_id, claim.provider_id,
            claim.logical_capability, claim.mapping_id,
            claim.requested_execution_mode,
            claim.execution_binding_kind,
            claim.selected_skill_resource_id,
            claim.selected_skill_content_sha256,
        )
        if observed_claim != expected_claim:
            return "HOST_EXECUTION_START_CLAIM_MISMATCH"
        if seen_execution_claim_ids is not None and claim.claim_id in seen_execution_claim_ids:
            return "HOST_EXECUTION_START_CLAIM_REPLAYED"
        if seen_execution_claim_ids is not None:
            seen_execution_claim_ids.add(claim.claim_id)
        receipt_validation_time = claim.claimed_at

    handoff_id = handoff.get("handoff_id")
    if execution_start_claim is None:
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

    r4_receipt = receipt.get("r4_receipt")
    if not isinstance(r4_receipt, Mapping):
        return "HOST_INVENTORY_RECEIPT_MALFORMED"
    result = validate_host_receipt(handoff, r4_receipt, now=receipt_validation_time)
    if result != "EXECUTION_SUCCEEDED":
        return result

    return "EXECUTION_SUCCEEDED"
