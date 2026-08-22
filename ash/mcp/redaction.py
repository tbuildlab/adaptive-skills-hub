"""One allowlist-oriented outbound representation for the R2 MCP boundary."""
from __future__ import annotations

from typing import Any, Mapping

from .schemas import SCHEMA_VERSION, NexusMcpError, ensure_response_limit

PRODUCT = {"name": "Nexus", "subtitle": "Adaptive AI Capability Hub"}


def safe_error(request_id: str, error: NexusMcpError) -> dict[str, Any]:
    return ensure_response_limit({"schema_version": SCHEMA_VERSION, "request_id": request_id, "product": PRODUCT, "status": "blocked", "error": {"code": error.code, "message": error.safe_message}})


def safe_health() -> dict[str, Any]:
    return ensure_response_limit({
        "schema_version": SCHEMA_VERSION, "product": PRODUCT, "status": "ready",
        "transport": "stdio", "capabilities": {"read_only": True, "plan_only": True, "network_listener": False, "persistent_state": False},
        "supported_tools": ["nexus.health", "nexus.discover_capabilities", "nexus.plan_task"],
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
        payload = {"schema_version": SCHEMA_VERSION, "product": PRODUCT, "status": "ready", "capability_count": len(filtered), "available_capability_count": available, "truncated": len(filtered) < available, "capabilities": filtered}
        try:
            return ensure_response_limit(payload)
        except NexusMcpError:
            filtered.pop()
    return ensure_response_limit({"schema_version": SCHEMA_VERSION, "product": PRODUCT, "status": "ready", "capability_count": 0, "available_capability_count": available, "truncated": bool(available), "capabilities": []})


def safe_plan(plan: Any, loads: list[Mapping[str, Any]], validation: Mapping[str, Any], request_id: str) -> dict[str, Any]:
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
    return ensure_response_limit({
        "schema_version": SCHEMA_VERSION, "request_id": request_id, "product": PRODUCT, "status": status,
        "task_summary": {"task_type": plan.task_profile.task_type, "required_capabilities": list(plan.task_profile.required_capabilities)},
        "selected_skills": selected,
        "execution_steps": [{"capability": step.capability, "summary": f"complete the {step.capability} contribution", "validation": list(step.validation)} for step in plan.steps],
        "validation_plan": [{"kind": item.get("kind", "validation"), "summary": "perform the planned validation"} for item in plan.validation_plan.checks],
        "advisory_agents": [item.name for item in plan.advisory_agents],
        "fallback": {"kind": plan.fallback.get("kind"), "status": plan.fallback.get("status"), "reason_code": "CAPABILITY_NOT_COVERED" if plan.fallback.get("status") == "needed" else "NOT_NEEDED"},
        "applied_rules": [{"rule_id": item.rule_id, "effect": item.enforcement, "target": item.target} for item in plan.rules if item.source in {"system", "current_user"} or item.scope == "project"],
        "warnings": ["project_context_items_excluded" for _ in plan.project_context.skipped[:1]],
    })
