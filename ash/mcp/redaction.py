"""One allowlist-oriented outbound representation for the R2 MCP boundary."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping
from uuid import uuid4

from ash.runtime_decision import RuntimeDecisionError, host_runtime_decision

from .handoff import (
    HANDOFF_SCHEMA_VERSION,
    HOST_NATIVE_PRESENTATIONS_MODE,
    HOST_PRESENTATIONS_CAPABILITY,
    PLAN_VERSION,
    issue_window,
)
from .enhancement import (
    ENHANCEMENT_HANDOFF_SCHEMA_VERSION,
    HOST_ARTIFACT_STATE_SCHEMA_VERSION,
    enhancement_issue_window,
    select_enhancement,
)
from .host_mapping import presentation_profile
from .host_inventory import (
    HOST_CAPABILITY_ASSESSMENT_SCHEMA_VERSION,
    HOST_CAPABILITY_TICKET_SCHEMA_VERSION,
    HostCapabilityTicket,
    assessment_issue_window,
    assess_host_capabilities,
)
from .schemas import SCHEMA_VERSION, NexusMcpError, ensure_response_limit

PRODUCT = {"name": "Nexus", "subtitle": "Adaptive AI Capability Hub"}


def safe_error(request_id: str, error: NexusMcpError) -> dict[str, Any]:
    return ensure_response_limit({"schema_version": SCHEMA_VERSION, "request_id": request_id, "product": PRODUCT, "status": "blocked", "error": {"code": error.code, "message": error.safe_message}})


def safe_health() -> dict[str, Any]:
    return ensure_response_limit({
        "schema_version": SCHEMA_VERSION, "product": PRODUCT, "status": "ready",
        "transport": "stdio", "capabilities": {
            "read_only": True,
            "plan_only": True,
            "host_handoff_only": True,
            "network_listener": False,
            "persistent_state": False,
            "ephemeral_security_state": "bounded_runtime_local",
        },
        "supported_tools": ["nexus.health", "nexus.discover_capabilities", "nexus.plan_task", "nexus.route_capabilities", "nexus.scout_candidates", "nexus.begin_host_capability_assessment", "nexus.assess_host_capabilities", "nexus.prepare_host_handoff", "nexus.prepare_enhancement_handoff"],
        "core_baseline": "Nexus V1.2 plus Runtime R1",
    })


def safe_catalog(records: list[Mapping[str, Any]], tags: tuple[str, ...]) -> dict[str, Any]:
    filtered: list[dict[str, Any]] = []
    for record in records[:1024]:
        record_tags = sorted({str(tag) for tag in record.get("tags", []) if isinstance(tag, str)})
        if tags and not set(tags).intersection(record_tags):
            continue
        filtered.append({
            "resource_id": str(record.get("id", "")), "display_name": str(record.get("name", "")),
            "resource_kind": str(record.get("kind", "skill")), "capability_tags": record_tags,
            "availability": str(record.get("status", "unknown")),
            "source_scope": str(record.get("provenance", {}).get("source_scope", record.get("scope", "unknown"))),
            "runtime_compatibility": str(record.get("runtime_compatibility", "directly_usable_by_codex")),
        })
    available = len(filtered)
    # The catalog is metadata-only, but it can still be large. Return the largest
    # prefix that fits the fixed MCP boundary and report that truncation honestly.
    while filtered:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "product": PRODUCT,
            "status": "ready",
            "catalog_scope": "nexus_local_skill_metadata",
            "host_inventory_authority": "none",
            "capability_count": len(filtered),
            "available_capability_count": available,
            "truncated": len(filtered) < available,
            "capabilities": filtered,
        }
        try:
            return ensure_response_limit(payload)
        except NexusMcpError:
            filtered.pop()
    return ensure_response_limit({
        "schema_version": SCHEMA_VERSION,
        "product": PRODUCT,
        "status": "ready",
        "catalog_scope": "nexus_local_skill_metadata",
        "host_inventory_authority": "none",
        "capability_count": 0,
        "available_capability_count": available,
        "truncated": bool(available),
        "capabilities": [],
    })


def safe_plan(plan: Any, loads: list[Mapping[str, Any]], validation: Mapping[str, Any], request_id: str,
              *, project_memory: Mapping[str, Any] | None = None) -> dict[str, Any]:
    # Project Memory is attached separately after this unchanged authority and
    # capability projection; it is never fed back into planner rules or coverage.
    load_by_path: dict[str, list[Mapping[str, Any]]] = {}
    for item in loads:
        path = item.get("path")
        if isinstance(path, str):
            load_by_path.setdefault(path.casefold(), []).append(item)
    selected: list[dict[str, Any]] = []
    for resource in plan.selected:
        if resource.resource_type != "skill":
            continue
        matches = load_by_path.get(str(resource.path).casefold(), [])
        item = matches[0] if len(matches) == 1 else {}
        loaded = len(matches) == 1 and "load_error" not in item and isinstance(item.get("sha256"), str) and isinstance(item.get("characters"), int)
        if not loaded:
            raise NexusMcpError("SKILL_LOAD_FAILED", "selected Skill load evidence could not be verified")
        selected.append({
            "resource_id": resource.resource_id, "name": resource.name,
            "source_scope": resource.provenance.get("source_scope", resource.trust),
            "runtime_compatibility": resource.runtime_compatibility,
            "content_sha256": item["sha256"], "characters": item["characters"], "load_status": "loaded",
        })
    status = "planned" if validation.get("status") == "passed" else "fallback_needed"
    payload = ensure_response_limit({
        "schema_version": SCHEMA_VERSION, "request_id": request_id, "product": PRODUCT, "status": status,
        "task_summary": {"task_type": plan.task_profile.task_type, "required_capabilities": list(plan.task_profile.required_capabilities)},
        "reference_research": plan.reference_research.to_dict(),
        "selected_skills": selected,
        "execution_steps": [{"capability": step.capability, "summary": f"complete the {step.capability} contribution", "validation": list(step.validation)} for step in plan.steps],
        "validation_plan": [{"kind": item.get("kind", "validation"), "summary": "perform the planned validation"} for item in plan.validation_plan.checks],
        "advisory_agents": [item.name for item in plan.advisory_agents],
        "fallback": {"kind": plan.fallback.get("kind"), "status": plan.fallback.get("status"), "reason_code": "CAPABILITY_NOT_COVERED" if plan.fallback.get("status") == "needed" else "NOT_NEEDED"},
        "applied_rules": [{"rule_id": item.rule_id, "effect": item.enforcement, "target": item.target} for item in plan.rules if item.source in {"system", "current_user"} or item.scope == "project"],
        "warnings": ["project_context_items_excluded" for _ in plan.project_context.skipped[:1]],
    })
    if project_memory is not None:
        from ash.project_memory_context import attach_context
        return ensure_response_limit(attach_context(payload, project_memory))
    return payload


def safe_host_inventory_ticket(ticket: HostCapabilityTicket) -> dict[str, Any]:
    """Return the fixed, redacted purpose of a one-use runtime-local ticket."""
    return ensure_response_limit({
        "schema_version": HOST_CAPABILITY_TICKET_SCHEMA_VERSION,
        "ticket_id": ticket.ticket_id,
        "issued_at": ticket.issued_at.isoformat().replace("+00:00", "Z"),
        "expires_at": ticket.expires_at.isoformat().replace("+00:00", "Z"),
        "status": "inventory_submission_requested",
        "host_surface": ticket.host_surface,
        "inventory_scope": ticket.inventory_scope,
        "inventory_completeness": ticket.inventory_completeness,
        "task_category": ticket.task_category,
        "required_interfaces": list(ticket.required_interfaces),
        "security_result": {
            "code": "HOST_INVENTORY_TICKET_READY",
            "lifecycle": "server_issued_single_use",
            "session_binding": "nexus_stdio_runtime_process",
            "turn_authentication": "not_provided_by_host",
            "inventory_authority": "host_asserted_non_authoritative",
            "mcp_execution_authority": "none",
            "private_host_state_access": "none",
            "persistent_state": "none",
        },
    })


def safe_host_capability_assessment(
    snapshot: Any, ticket: HostCapabilityTicket, *, now: datetime | None = None,
) -> dict[str, Any]:
    """Return an advisory classification of current-turn Host metadata.

    The snapshot is a caller assertion, not authenticated Host state.  This
    response stops at considered/selected and cannot load or execute anything.
    """
    decision = assess_host_capabilities(snapshot)
    # Slice 1 routes the already-validated current-turn Host facts through the
    # Capability Foundation as a fail-closed compatibility cross-check.  The
    # general runtime envelope is intentionally not duplicated into the frozen
    # R5 assessment schema; the existing redacted R5 fields remain authoritative
    # for Host handoff and execution-start validation.
    try:
        host_runtime_decision(snapshot, decision)
    except RuntimeDecisionError as exc:
        raise NexusMcpError(
            "RUNTIME_CAPABILITY_DECISION_BLOCKED",
            "Host capability decision failed the runtime eligibility gate",
        ) from exc
    issued_at, expires_at = assessment_issue_window(ticket, now=now)

    def safe_item(item: Any) -> dict[str, Any]:
        capability = item.capability
        value = {
            "capability_id": capability.capability_id,
            "provider_id": capability.provider_id,
            "resource_kind": capability.resource_kind,
            "availability": capability.availability,
            "evidence": list(capability.evidence),
            "interfaces": list(capability.interfaces),
            "logical_capability": capability.logical_capability,
            "execution_binding_kind": capability.execution_binding_kind,
            "functional_role": item.functional_role,
            "classification": item.classification,
            "decision_state": item.decision_state,
            "reason_codes": list(item.reason_codes),
            "covered_interfaces": list(item.covered_interfaces),
            "execution_eligibility": (
                f"mapped_{item.execution_binding_kind}"
                if item.mapping_id else "not_execution_eligible"
            ),
        }
        if item.decision_state == "selected" and item.mapping_id:
            value["mapping_id"] = item.mapping_id
            value["requested_execution_mode"] = item.requested_execution_mode
        return value

    considered = [safe_item(item) for item in decision.assessments]
    selected = [
        {
            "capability_id": item["capability_id"],
            "provider_id": item["provider_id"],
            "logical_capability": item["logical_capability"],
            "mapping_id": item["mapping_id"],
            "requested_execution_mode": item["requested_execution_mode"],
            "execution_binding_kind": item["execution_binding_kind"],
        }
        for item in considered
        if item["decision_state"] == "selected"
    ]
    rejected = [
        {
            "capability_id": item["capability_id"],
            "provider_id": item["provider_id"],
            "classification": item["classification"],
            "decision_state": "rejected",
            "reason_codes": item["reason_codes"],
        }
        for item in considered
        if item["decision_state"] == "rejected"
    ]
    return ensure_response_limit({
        "schema_version": HOST_CAPABILITY_ASSESSMENT_SCHEMA_VERSION,
        "ticket_id": ticket.ticket_id,
        "ticket_issued_at": ticket.issued_at.isoformat().replace("+00:00", "Z"),
        "assessment_id": str(uuid4()),
        "snapshot_id": snapshot.snapshot_id,
        "snapshot_sha256": decision.snapshot_digest,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "status": decision.status,
        "host_surface": snapshot.host_surface,
        "inventory_scope": snapshot.inventory_scope,
        "inventory_completeness": snapshot.inventory_completeness,
        "task_category": snapshot.task_category,
        "required_interfaces": list(snapshot.required_interfaces),
        "considered_capabilities": considered,
        "selected_capabilities": selected,
        "rejected_capabilities": rejected,
        "fallback": {
            "status": "not_needed" if selected else "needed",
            "reason_code": "NOT_NEEDED" if selected else decision.result_code,
        },
        "security_result": {
            "code": decision.result_code,
            "inventory_authority": "host_asserted_non_authoritative",
            "mcp_execution_authority": "none",
            "private_host_state_access": "none",
        },
    })


def safe_host_handoff(plan: Any, loads: list[Mapping[str, Any]], validation: Mapping[str, Any]) -> dict[str, Any]:
    """Return a single-skill, host-owned R4 execution intent.

    Internal paths are used solely to associate selected resources with loader
    evidence; none are emitted.  This function cannot perform an action.
    """
    if validation.get("status") != "passed" or plan.fallback.get("status") != "not_needed":
        raise NexusMcpError("HANDOFF_NOT_ELIGIBLE", "selected Skill is not eligible for host handoff")
    selected = [resource for resource in plan.selected if resource.resource_type == "skill"]
    if len(selected) != 1:
        raise NexusMcpError("HANDOFF_NOT_ELIGIBLE", "R4 requires exactly one selected Skill")
    resource = selected[0]
    if resource.name.casefold() != "presentations":
        raise NexusMcpError("HANDOFF_NOT_ELIGIBLE", "R4 supports only the Presentations Skill")
    matches = [item for item in loads if str(item.get("path", "")).casefold() == str(resource.path).casefold()]
    if len(matches) != 1:
        raise NexusMcpError("SKILL_LOAD_FAILED", "selected Skill load evidence could not be verified")
    loaded = matches[0]
    digest = loaded.get("sha256")
    characters = loaded.get("characters")
    if not isinstance(digest, str) or len(digest) != 64 or not all(char in "0123456789abcdef" for char in digest.casefold()) or not isinstance(characters, int) or characters < 0:
        raise NexusMcpError("SKILL_INTEGRITY_FAILED", "selected Skill integrity could not be verified")
    issued_at, expires_at = issue_window()
    return ensure_response_limit({
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "handoff_id": str(uuid4()),
        "issued_at": issued_at,
        "expires_at": expires_at,
        "plan_version": PLAN_VERSION,
        "status": "execution_requested",
        "task_category": plan.task_profile.task_type,
        "selected_skill": {
            "resource_id": resource.resource_id,
            "name": resource.name,
            "content_sha256": digest,
            "load_verification_state": "loaded_verified",
        },
        "logical_host_capability": HOST_PRESENTATIONS_CAPABILITY,
        "requested_execution_mode": HOST_NATIVE_PRESENTATIONS_MODE,
        # This is an allowlisted, content-free mapping profile.  It resolves
        # normal authoring defaults so the Host need not turn an otherwise
        # executable request into a clarification loop.  It is never an MCP
        # command or a replacement for the Host's approval/tool policy.
        "host_execution_profile": presentation_profile(),
        "validation_requirements": ["artifact_created", "artifact_editable", "presentation_open_render"],
        "fallback": {"kind": plan.fallback.get("kind"), "status": plan.fallback.get("status")},
        "security_result": {"code": "HOST_HANDOFF_READY", "mcp_execution_authority": "none"},
    })


def safe_enhancement_handoff(state: Any) -> dict[str, Any]:
    """Return a content-free R5 Host enhancement intent or a no-op result.

    ``state`` is already parsed against a closed enum schema. Even then, this
    result is only an analysis request: the Host must prove current primary
    execution provenance, retain the actual artifact privately, create a
    checkpoint, and validate any modification before it can report success.
    """
    decision = select_enhancement(state)
    base = {
        "schema_version": ENHANCEMENT_HANDOFF_SCHEMA_VERSION,
        "artifact_state_schema_version": HOST_ARTIFACT_STATE_SCHEMA_VERSION,
        "artifact_kind": state.artifact_kind,
        "base_mapping_id": state.base_mapping_id,
        "enhancement_pass": state.enhancement_pass,
        "max_enhancement_passes": 1,
        "host_provenance_required": "current_validated_r4_receipt",
        "security_result": {"mcp_execution_authority": "none", "artifact_access": "none"},
    }
    if decision.status != "enhancement_requested" or decision.profile is None:
        return ensure_response_limit({
            **base,
            "status": "no_enhancement_needed",
            "reason_codes": list(decision.reason_codes),
            "security_result": {**base["security_result"], "code": "NO_ENHANCEMENT_NEEDED"},
        })
    profile = decision.profile
    issued_at, expires_at = enhancement_issue_window()
    return ensure_response_limit({
        **base,
        "handoff_id": str(uuid4()),
        "issued_at": issued_at,
        "expires_at": expires_at,
        "status": "enhancement_requested",
        "selected_candidate": {
            "candidate_id": profile["candidate_id"],
            "reason_codes": list(decision.reason_codes),
        },
        "logical_host_capability": profile["logical_host_capability"],
        "requested_execution_mode": profile["requested_execution_mode"],
        "required_checkpoint": "host_copy_on_write",
        "host_execution_profile": {
            "mapping_id": profile["mapping_id"],
            "operation_scope": list(profile["operation_scope"]),
            "continuation_policy": "apply_only_if_host_can_validate_improvement",
            "artifact_mutation_policy": "host_copy_on_write",
            "improvement_requirement": "host_observed_quality_improvement",
        },
        "validation_requirements": list(profile["validation_requirements"]),
        "security_result": {**base["security_result"], "code": "HOST_ENHANCEMENT_HANDOFF_READY"},
    })
