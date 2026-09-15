"""Deterministic G1 eligibility, policy intersection and selection/refusal.

No I/O, LLM, fallback execution, mutable ledger, reservation, or dispatch.
Trusted observations are evidence about one scope, never permission grants.
"""
from __future__ import annotations

from typing import Any

from .runtime_decision import RuntimeDecisionError, parse_runtime_requirements
from .g1_profiles import (
    CLASSES, MAX_CONSIDERED_CAPABILITIES, STATES, bounded, binding_digest,
    candidate, conformance, digest, enum, exact, fail, fresh, integer,
    observations, token, tokens,
)

REQUIREMENTS_SCHEMA = "nexus.executor-requirements.v1"
POLICY_SCHEMA = "nexus.executor-policy.v1"
DECISION_SCHEMA = "nexus.selection-decision.v1"
POLICY_FIELDS = {
    "provider", "model_family", "model_id", "deployment_kind", "path.provider",
    "path.location", "path.delegated", "path.remote_mcp", "host_native",
    "privacy.residency", "privacy.retention", "privacy.data_use", "cost.basis",
}
# Identity exclusions are deterministic filters. Behavior/privacy restrictions
# additionally require a verified control over every requested operation.
BEHAVIOR_FIELDS = {"path.location", "path.delegated", "path.remote_mcp",
                   "privacy.residency", "privacy.retention", "privacy.data_use"}


def requirements(value: Any) -> dict:
    bounded(value)
    exact(value, {"schema_version", "requirements_id", "revision", "task", "required_capabilities",
                  "operations", "hard_restrictions", "acceptance", "max_expected_cost"})
    if value["schema_version"] != REQUIREMENTS_SCHEMA:
        fail()
    token(value["requirements_id"])
    token(value["revision"])
    try:
        parse_runtime_requirements(value["task"])
    except (RuntimeDecisionError, TypeError):
        fail()
    for key in ("required_capabilities", "operations", "acceptance"):
        tokens(value[key], nonempty=key == "operations")
    if type(value["hard_restrictions"]) is not list or len(value["hard_restrictions"]) > 16:
        fail()
    seen = set()
    for control in value["hard_restrictions"]:
        exact(control, {"control_id", "operations", "minimum_classification"})
        identity = token(control["control_id"])
        if identity in seen:
            fail("G1_AMBIGUOUS_IDENTITY")
        seen.add(identity)
        tokens(control["operations"], nonempty=True)
        if not set(control["operations"]) <= set(value["operations"]):
            fail()
        enum(control["minimum_classification"], {"GOVERNED_HANDOFF", "ENFORCED_INTEGRATION"})
    ceiling = value["max_expected_cost"]
    if ceiling is not None:
        exact(ceiling, {"currency", "microunits", "allow_estimates"})
        token(ceiling["currency"])
        integer(ceiling["microunits"])
        if type(ceiling["allow_estimates"]) is not bool:
            fail()
    return value


def policy(value: Any) -> dict:
    bounded(value)
    exact(value, {"schema_version", "policy_id", "revision", "rules", "preferences"})
    if value["schema_version"] != POLICY_SCHEMA:
        fail()
    token(value["policy_id"])
    token(value["revision"])
    if type(value["rules"]) is not list or len(value["rules"]) > 32:
        fail()
    seen = set()
    for rule in value["rules"]:
        exact(rule, {"rule_id", "field", "operator", "values"})
        identity = token(rule["rule_id"])
        if identity in seen:
            fail("G1_AMBIGUOUS_IDENTITY")
        seen.add(identity)
        enum(rule["field"], POLICY_FIELDS)
        enum(rule["operator"], {"allow_only", "deny"})
        tokens(rule["values"], nonempty=True)
    preferences = tokens(value["preferences"])
    if not set(preferences) <= {"lowest_expected_cost", "host_native", "privacy_first"}:
        fail()
    return value


def _resolve(policies: list[dict]) -> tuple[dict, bool]:
    resolved = {}
    for p in policies:
        for rule in p["rules"]:
            state = resolved.setdefault(rule["field"], {"allow": None, "deny": set()})
            values = set(rule["values"])
            if rule["operator"] == "deny":
                state["deny"] |= values
            else:
                state["allow"] = values if state["allow"] is None else state["allow"] & values
    conflict = False
    for state in resolved.values():
        if state["allow"] is not None:
            state["allow"] -= state["deny"]
            conflict |= not state["allow"]
    return resolved, conflict


def _boolean(value: Any) -> str:
    return "unknown" if value is None else ("true" if value else "false")


def _policy_values(c: dict, field: str) -> list[str]:
    if field == "cost.basis":
        return [c["cost"]["basis"]]
    if field == "host_native":
        return [_boolean(c["path"]["host_native"])]
    if field.startswith("path."):
        key = field.split(".")[1]
        if c["path"]["complete"] is not True:
            return ["unknown"]
        result = []
        for node in c["path"]["nodes"]:
            v = node[key]
            if key == "delegated" and node["kind"] == "agent":
                v = True
            if key == "remote_mcp" and node["kind"] in {"mcp", "proxy"} and node["location"] == "remote":
                v = True
            result.append(_boolean(v) if key in {"delegated", "remote_mcp"} else v)
        return result
    model = c["model"]
    if model is None:
        # Absence of a model is not a claim that an unknown model is local.
        return ["not_applicable"]
    if field.startswith("privacy."):
        v = model["privacy"][field.split(".")[1]]
        return v if type(v) is list else [v]
    return [model[field]]


def _required_capabilities(req: dict) -> set[str]:
    result = set(req["required_capabilities"])
    for key, prefix in (("domains", "domain"), ("outputs", "output"), ("validation_requirements", "validation")):
        result.update(prefix + ":" + v for v in req["task"][key])
    return result


def policy_digest(policies: list[dict]) -> str:
    return digest(sorted([policy(p) for p in policies], key=lambda p: p["policy_id"]))


def _cost_summary(value: dict) -> dict:
    total = None if value["basis"] == "unknown" else sum(value["components"].values())
    return {"basis": value["basis"], "currency": value["currency"], "total_microunits": total,
            "components": value["components"], "evidence_refs": sorted(value["evidence_refs"])}


def select_capabilities(*, candidates: list[dict], policies: list[dict], request: dict,
                        conformance_records: list[dict], trusted_observations: Any,
                        now: int, scope_id: str) -> dict:
    """Return an auditable allowed pool. Even SELECTED grants authority=none."""
    bounded({"candidates": candidates, "policies": policies, "request": request,
             "conformance_records": conformance_records})
    integer(now)
    token(scope_id)
    req = requirements(request)
    if type(candidates) is not list or len(candidates) > MAX_CONSIDERED_CAPABILITIES:
        fail()
    if type(policies) is not list or not 1 <= len(policies) <= 8:
        fail()
    candidates = sorted([candidate(c) for c in candidates], key=lambda c: c["candidate_id"])
    policies = sorted([policy(p) for p in policies], key=lambda p: p["policy_id"])
    for values in ([c["candidate_id"] for c in candidates], [p["policy_id"] for p in policies]):
        if len(values) != len(set(values)):
            fail("G1_AMBIGUOUS_IDENTITY")
    # One profile identity/revision may not denote different subjects in a pool.
    profiles = {}
    for c in candidates:
        for p in (c["model"], c["host"]):
            if p is not None:
                key = (p["schema_version"], p["profile_id"], p["revision"])
                if key in profiles and profiles[key] != digest(p):
                    fail("G1_AMBIGUOUS_IDENTITY")
                profiles[key] = digest(p)
    if type(conformance_records) is not list or len(conformance_records) > 64:
        fail()
    records = [conformance(r) for r in conformance_records]
    if len({r["record_id"] for r in records}) != len(records):
        fail("G1_AMBIGUOUS_IDENTITY")
    source = observations(trusted_observations)
    observed = {r["subject_sha256"]: r for r in source["rows"]}
    resolved, conflict = _resolve(policies)
    req_sha = digest(req)
    policies_sha = policy_digest(policies)
    policy_refs = [{"policy_id": p["policy_id"], "revision": p["revision"], "sha256": digest(p)} for p in policies]
    required_caps = _required_capabilities(req)
    hard_restrictions = list(req["hard_restrictions"])
    hard_restrictions.extend({"control_id": "policy:" + field, "operations": sorted(req["operations"]),
                              "minimum_classification": "ENFORCED_INTEGRATION"}
                             for field in sorted(set(resolved) & BEHAVIOR_FIELDS))
    considered = []
    for c in candidates:
        reasons = set()
        uncertainty = set()
        subject = digest(c)
        binding = binding_digest(c)
        row = observed.get(subject)
        host = c["host"]
        if conflict:
            reasons.add("POLICY_CONFLICT")
        if not host["binding_id"]:
            reasons.add("BINDING_MISSING")
        for profile in (host, c["model"]):
            if profile is not None and not fresh(profile, now, scope_id):
                reasons.add("PROFILE_STALE")
            if profile is not None and not profile["evidence_refs"]:
                reasons.add("PROFILE_EVIDENCE_MISSING")
        valid_observation = (row is not None and row["binding_sha256"] == binding and
                             row["requirements_sha256"] == req_sha and row["policy_sha256"] == policies_sha and fresh(row, now, scope_id) and
                             bool(row["evidence_refs"]))
        if not valid_observation:
            reasons.add("OBSERVATION_MISSING_STALE_OR_MISMATCHED")
        states = {key: None for key in STATES}
        if valid_observation:
            states = dict(row["states"])
            for key in STATES:
                if host["states"][key] != states[key]:
                    reasons.add("HOST_CLAIM_OBSERVATION_MISMATCH")
                if key != "documented_possible" and states[key] is not True:
                    reasons.add(key.upper() + "_NOT_TRUE")
            if row["budget_eligible"] is not True:
                reasons.add("BUDGET_ELIGIBILITY_UNKNOWN_OR_FALSE")
            if row["path_verified"] is not True or c["path"]["complete"] is not True:
                reasons.add("DATA_PATH_UNVERIFIED")
            if req["task"]["task_category"] not in row["task_classes"] or not required_caps <= set(row["capabilities"]):
                reasons.add("TASK_UNSUITABLE_OR_UNMEASURED")
            if not set(req["acceptance"]) <= set(row["acceptance"]):
                reasons.add("ACCEPTANCE_UNSUPPORTED")
        if not set(c["required_permissions"]) <= set(req["task"]["allowed_permissions"]):
            reasons.add("PERMISSION_INTERSECTION_EMPTY")
        if c["execution_mechanism"] not in req["task"]["allowed_execution_mechanisms"]:
            reasons.add("EXECUTION_MECHANISM_FORBIDDEN")
        if c["execution_mechanism"] in {"none", "reference_only", "advisory_only"}:
            reasons.add("NON_EXECUTING_MECHANISM")
        for field, rule in sorted(resolved.items()):
            values = _policy_values(c, field)
            if not values or "unknown" in values or any(v in rule["deny"] for v in values) or (
                    rule["allow"] is not None and not set(values) <= rule["allow"]):
                reasons.add("POLICY_REJECTED:" + field)
        coverage = []
        for record in sorted(records, key=lambda r: r["record_id"]):
            if record["subject_sha256"] != subject:
                continue
            verified = (valid_observation and record["binding_sha256"] == binding and
                        fresh(record, now, scope_id) and record["probe_result"] == "pass" and
                        bool(record["evidence_refs"]) and digest(record) in row["conformance_sha256"])
            coverage.append({"record_id": record["record_id"], "sha256": digest(record),
                             "control_id": record["control_id"], "operations": sorted(record["operations"]),
                             "classification": record["classification"], "verified": bool(verified)})
            if not verified and record["classification"] != "ADVISORY":
                reasons.add("UNVERIFIED_CONFORMANCE")
        for control in hard_restrictions:
            covered_operations = set()
            for record in coverage:
                if record["verified"] and record["classification"] != "ADVISORY" and record["control_id"] == control["control_id"] and CLASSES[record["classification"]] >= CLASSES[control["minimum_classification"]]:
                    covered_operations.update(record["operations"])
            if not set(control["operations"]) <= covered_operations:
                reasons.add("ENFORCEMENT_UNSUPPORTED:" + control["control_id"])
        costs = _cost_summary(c["cost"])
        if costs["basis"] == "unknown":
            uncertainty.add("MONEY_UNKNOWN")
        elif costs["basis"] == "estimated":
            uncertainty.add("MONEY_ESTIMATED")
        ceiling = req["max_expected_cost"]
        if ceiling is not None and (costs["total_microunits"] is None or costs["currency"] != ceiling["currency"] or
                costs["total_microunits"] > ceiling["microunits"] or
                (costs["basis"] == "estimated" and not ceiling["allow_estimates"])):
            reasons.add("EXPECTED_COST_UNSUPPORTED_OR_EXCEEDED")
        considered.append({"candidate_id": c["candidate_id"], "subject_sha256": subject,
                           "binding_sha256": binding, "model_profile_sha256": digest(c["model"]) if c["model"] else None,
                           "host_profile_sha256": digest(host), "states": states,
                           "eligible": not reasons, "executable_now": not reasons,
                           "rejection_reasons": sorted(reasons), "conformance": coverage,
                           "suitability_evidence": sorted(row["evidence_refs"]) if valid_observation else [],
                           "cost": costs, "uncertainty": sorted(uncertainty)})
    eligible = [item for item in considered if item["eligible"]]
    preferences = set(v for p in policies for v in p["preferences"])
    candidate_by_id = {c["candidate_id"]: c for c in candidates}
    selection_uncertainty = set()
    comparable = bool(eligible) and all(i["cost"]["total_microunits"] is not None for i in eligible) and len({i["cost"]["currency"] for i in eligible}) == 1
    if eligible and "lowest_expected_cost" in preferences and not comparable:
        selection_uncertainty.add("COSTS_NOT_COMPARABLE")

    def rank(item):
        c = candidate_by_id[item["candidate_id"]]
        return (
            0 if "host_native" not in preferences or c["path"]["host_native"] is True else 1,
            0 if "privacy_first" not in preferences or all(n["location"] == "local" for n in c["path"]["nodes"]) else 1,
            item["cost"]["total_microunits"] if comparable and "lowest_expected_cost" in preferences else 0,
            item["candidate_id"],
        )

    selected = min(eligible, key=rank) if eligible else None
    body = {"schema_version": DECISION_SCHEMA,
            "requirements_ref": {"requirements_id": req["requirements_id"], "revision": req["revision"], "sha256": req_sha},
            "policy_refs": policy_refs, "required_capabilities": sorted(required_caps),
            "hard_restrictions": sorted(hard_restrictions, key=lambda r: (r["control_id"], r["minimum_classification"])),
            "acceptance": sorted(req["acceptance"]), "observation_source": source["source"],
            "scope_id": scope_id, "evaluated_at": now, "considered": considered,
            "rejected_candidates": [i["candidate_id"] for i in considered if not i["eligible"]],
            "eligible_candidates": [i["candidate_id"] for i in eligible],
            "status": "SELECTED" if selected else "UNSUPPORTED",
            "result_code": "ELIGIBLE_STRATEGY_IDENTIFIED" if selected else ("POLICY_CONFLICT" if conflict else "NO_ELIGIBLE_CAPABILITY"),
            "selected_strategy": {"candidate_id": selected["candidate_id"], "kind": "single_executor",
                                  "dispatch": "not_requested"} if selected else None,
            "uncertainty": sorted(selection_uncertainty),
            "authority": {"execution": "none", "permission_grants": "none", "trust_grants": "none",
                          "installation": "none", "delegation": "none"}}
    return {**body, "decision_id": "selection:" + digest(body)}


def validate_selection_decision(value: Any, **inputs) -> dict:
    """Recompute from the original trusted inputs; a digest alone is not proof."""
    bounded(value)
    expected = select_capabilities(**inputs)
    if digest(value) != digest(expected):
        fail("G1_SELECTION_MISMATCH")
    return expected
