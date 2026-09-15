"""Synthetic G1 observations: no real model quality or Host authority claims."""
from __future__ import annotations

import copy

from ash.g1_profiles import (
    CANDIDATE_SCHEMA, CONFORMANCE_SCHEMA, COST_PARTS, FACILITIES, HOST_SCHEMA,
    MODEL_SCHEMA, OBSERVATION_SCHEMA, STATES, _issue_observations, binding_digest, digest,
)
from ash.g1_selection import POLICY_SCHEMA, REQUIREMENTS_SCHEMA, policy_digest, select_capabilities

NOW = 2000
SCOPE = "g1-unit-scope"
CAPS = ["domain:governance", "output:selection", "validation:bounded"]


def cost(basis="known", amount=100, currency="usd"):
    return {"basis": basis, "currency": currency,
            "components": {k: (amount if k == "execution" else 0) if basis != "unknown" else None for k in COST_PARTS},
            "evidence_refs": ["fixture-cost"] if basis != "unknown" else []}


def common(identity, schema):
    return {"schema_version": schema, "profile_id": identity, "revision": "1",
            "configuration_id": "config-1", "adapter_sha256": "a" * 64,
            "observed_at": 1000, "expires_at": 3000, "scope_id": SCOPE,
            "evidence_refs": ["fixture-observation"], "limitations": [], "uncertainty": []}


def model(identity="model-a", provider="synthetic", model_id="fixture-model", location="local"):
    return {**common(identity, MODEL_SCHEMA), "provider": provider, "model_family": model_id,
            "model_id": model_id, "deployment_id": "deployment-1", "deployment_kind": location,
            "capabilities": {"claimed": [], "measured": [{"capability_id": c, "task_classes": ["governance"],
                               "evidence_refs": ["fixture-measurement"]} for c in CAPS],
                             "host_reported": [], "runtime_observed": []},
            "limits": {"context_tokens": None, "input_tokens": None, "output_tokens": None},
            "tool_use": False, "structured_output": True, "delegation": False,
            "latency": {"basis": "unknown", "p50_ms": None, "p95_ms": None, "evidence_refs": []},
            "cost": cost(), "privacy": {"residency": ["local"], "retention": "none",
                                         "data_use": "none", "evidence_refs": ["fixture-privacy"]}}


def host(identity="host-a"):
    return {**common(identity, HOST_SCHEMA), "host_id": "fixture-host", "surface_id": "fixture-surface",
            "binding_id": "fixture-binding", "inventory_scope": "authorized_probe_visible_subset",
            "inventory_completeness": "not_globally_enumerated", "states": {k: True for k in STATES},
            "facilities": {k: None for k in FACILITIES},
            "lifecycle": {k: None for k in ("installed", "enabled", "loaded", "approved", "routable")},
            "enforcement_mechanisms": ["nexus_boundary"]}


def candidate(identity="candidate-a", *, with_model=True, provider="synthetic", model_id="fixture-model", location="local", amount=100):
    result = {"schema_version": CANDIDATE_SCHEMA, "candidate_id": identity,
            "model": model(identity + "-model", provider, model_id, location) if with_model else None,
            "host": host(identity + "-host"), "cost": cost(amount=amount),
            "required_permissions": ["read_metadata"], "execution_mechanism": "nexus_local_read_plan",
            "path": {"complete": True, "host_native": True,
                     "nodes": [{"node_id": identity + "-node", "kind": "model" if with_model else "host",
                                "location": location, "provider": provider, "delegated": False,
                                "remote_mcp": False, "evidence_refs": ["fixture-path"], "model_profile_sha256": None}]}}
    if with_model:
        result["path"]["nodes"][0]["model_profile_sha256"] = digest(result["model"])
    return result


def request():
    return {"schema_version": REQUIREMENTS_SCHEMA, "requirements_id": "fixture-requirements", "revision": "1",
            "task": {"schema_version": "nexus.runtime-requirements.v1", "requirements_id": "fixture-task",
                     "requirements_version": "1", "task_category": "governance", "domains": ["governance"],
                     "outputs": ["selection"], "validation_requirements": ["bounded"],
                     "allowed_permissions": ["read_metadata"], "allowed_execution_mechanisms": ["nexus_local_read_plan"]},
            "required_capabilities": [], "operations": ["route"],
            "hard_restrictions": [{"control_id": "no-dispatch", "operations": ["route"],
                                   "minimum_classification": "ENFORCED_INTEGRATION"}],
            "acceptance": ["decision-schema"], "max_expected_cost": None}


def policy(rules=None, preferences=None, identity="fixture-policy"):
    return {"schema_version": POLICY_SCHEMA, "policy_id": identity, "revision": "1",
            "rules": rules or [], "preferences": preferences or []}


def rule(field, values, operator="allow_only", identity="rule-1"):
    return {"rule_id": identity, "field": field, "operator": operator, "values": values}


def record(c, classification="ENFORCED_INTEGRATION", control="no-dispatch"):
    layer = {"ADVISORY": "instructions", "GOVERNED_HANDOFF": "host_handoff", "ENFORCED_INTEGRATION": "nexus_boundary"}[classification]
    return {"schema_version": CONFORMANCE_SCHEMA, "record_id": c["candidate_id"] + "-" + control,
            "subject_sha256": digest(c), "binding_sha256": binding_digest(c), "control_id": control,
            "operations": ["route"], "enforcing_layer": layer, "classification": classification,
            "probe_result": "pass", "evidence_refs": ["fixture-probe"], "scope_id": SCOPE,
            "observed_at": 1000, "expires_at": 3000, "limitations": ["Synthetic unit-test coverage only."]}


def observation(c, req, records, policies=None):
    return {"schema_version": OBSERVATION_SCHEMA, "subject_sha256": digest(c),
            "binding_sha256": binding_digest(c), "requirements_sha256": digest(req), "policy_sha256": policy_digest(policies or [policy()]),
            "scope_id": SCOPE, "observed_at": 1000, "expires_at": 3000,
            "states": copy.deepcopy(c["host"]["states"]), "task_classes": ["governance"],
            "capabilities": list(CAPS), "acceptance": ["decision-schema"], "budget_eligible": True,
            "path_verified": True, "conformance_sha256": [digest(r) for r in records if r["subject_sha256"] == digest(c)],
            "evidence_refs": ["fixture-observation"]}


def inputs(candidates=None, req=None, policies=None, records=None, rows=None):
    candidates = candidates if candidates is not None else [candidate()]
    req = req if req is not None else request()
    records = records if records is not None else [record(c) for c in candidates]
    rows = rows if rows is not None else [observation(c, req, records, policies) for c in candidates]
    return {"candidates": candidates, "request": req, "policies": policies or [policy()],
            "conformance_records": records, "trusted_observations": _issue_observations(rows, source="hermetic-fixture"),
            "now": NOW, "scope_id": SCOPE}


def run(**kwargs):
    return select_capabilities(**inputs(**kwargs))
