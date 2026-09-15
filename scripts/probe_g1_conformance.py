#!/usr/bin/env python3
"""Separately authorized, read-only G1 pilot of the existing route operation.

This diagnostic is not a product executor or MCP tool. It accepts no candidate,
policy, command, workspace, or endpoint inputs. Invoke explicitly from a trusted
checkout. Its observation handle remains inside this process and grants no
authority. The printed receipt cannot be imported as a trusted observation.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ash.g1_profiles import (  # noqa: E402
    CANDIDATE_SCHEMA, CONFORMANCE_SCHEMA, COST_PARTS, FACILITIES, HOST_SCHEMA,
    OBSERVATION_SCHEMA, STATES, _issue_observations, binding_digest, digest,
)
from ash.g1_selection import (  # noqa: E402
    POLICY_SCHEMA, REQUIREMENTS_SCHEMA, policy_digest, select_capabilities,
)
from ash.mcp.adapter import NexusMcpRuntime  # noqa: E402
from ash.mcp.authorization import WorkspaceAuthorizer, guard_regular_file  # noqa: E402
from ash.mcp.schemas import MAX_SAFE_ENVELOPE_BYTES, NexusMcpError  # noqa: E402
from ash.runtime_decision import RuntimeCapabilityAdapter, validate_runtime_decision_envelope  # noqa: E402

SOURCE_FILES = (
    "ash/capabilities.py", "ash/runtime_decision.py", "ash/upstream.py",
    "ash/mcp/adapter.py", "ash/mcp/schemas.py", "ash/mcp/authorization.py",
    "ash/g1_profiles.py", "ash/g1_selection.py", "ash/ecosystem_models.py", "ash/evaluation.py",
    "config/capability-foundation.json", "config/upstream-source-registry.json",
    "scripts/probe_g1_conformance.py",
)
CONTROLS = ("closed-route-input", "no-dispatch-authority", "bounded-route-output")
OPERATION = "nexus.route_capabilities"


def _material() -> dict:
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    members = {}
    for name in SOURCE_FILES:
        path = ROOT / name
        # Reuse the accepted no-reparse, stable-regular-file boundary.
        guard_regular_file(path, [ROOT])
        raw = RuntimeCapabilityAdapter._stable_bytes(path).replace(b"\r\n", b"\n")
        actual = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        if actual != manifest.get(name):
            raise RuntimeError("G1_PILOT_SOURCE_INTEGRITY_FAILED")
        members[name] = actual
    return {"files": members, "python_version": list(sys.version_info[:3]),
            "local_roots": "empty", "invocation": "direct_existing_method_after_initialization"}


def _semantic_result(value: dict) -> dict:
    return {key: item for key, item in value.items() if key not in {"decision_id", "issued_at"}}


def run_probe() -> dict:
    """Observe only this owned method/configuration; never certify the Host."""
    before = _material()
    configuration = digest(before)
    adapter = RuntimeCapabilityAdapter(ROOT / "config/capability-foundation.json",
                                       ROOT / "config/upstream-source-registry.json", local_roots={})
    runtime = NexusMcpRuntime(WorkspaceAuthorizer({}), capability_adapter=adapter)
    req = {"schema_version": REQUIREMENTS_SCHEMA, "requirements_id": "g1-route-pilot", "revision": "1",
           "task": {"schema_version": "nexus.runtime-requirements.v1", "requirements_id": "g1-route-task",
                    "requirements_version": "1", "task_category": "governance", "domains": ["governance"],
                    "outputs": ["selection"], "validation_requirements": ["bounded"],
                    "allowed_permissions": ["read_metadata"], "allowed_execution_mechanisms": ["nexus_local_read_plan"]},
           "required_capabilities": [], "operations": [OPERATION],
           "hard_restrictions": [{"control_id": c, "operations": [OPERATION],
                                  "minimum_classification": "ENFORCED_INTEGRATION"} for c in CONTROLS],
           "acceptance": ["decision-schema"], "max_expected_cost": None}
    policies = [{"schema_version": POLICY_SCHEMA, "policy_id": "g1-pilot-policy", "revision": "1",
                 "rules": [], "preferences": []}]
    attempts = {"active": False, "write": 0, "network": 0, "process": 0, "filesystem_mutation": 0}

    def audit(event, args):
        if not attempts["active"]:
            return
        if event == "open":
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else 0
            write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
            if (isinstance(mode, str) and any(c in mode for c in "wax+")) or (isinstance(flags, int) and flags & write_flags):
                attempts["write"] += 1
        elif event in {"socket.connect", "socket.bind", "socket.getaddrinfo"}:
            attempts["network"] += 1
        elif event in {"subprocess.Popen", "os.system", "os.posix_spawn", "os.exec", "os.spawn"}:
            attempts["process"] += 1
        elif event in {"os.remove", "os.rename", "os.mkdir", "os.rmdir", "os.truncate"}:
            attempts["filesystem_mutation"] += 1

    # Read-only observation, not a hook that blocks effects to manufacture PASS.
    sys.addaudithook(audit)
    checks = {}
    attempts["active"] = True
    try:
        first = runtime.route_capabilities(req["task"])
        second = runtime.route_capabilities(req["task"])
        validate_runtime_decision_envelope(first)
        checks["deterministic-route-semantics"] = _semantic_result(first) == _semantic_result(second)
        checks["no-dispatch-authority"] = (first["security_result"]["mcp_execution_authority"] == "none" and
                                            first["security_result"]["selection_is_execution_evidence"] is False)
        checks["bounded-route-output"] = len(json.dumps(first, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) <= MAX_SAFE_ENVELOPE_BYTES
        rejections = []
        for mutation in ({"command": "forbidden"}, {"candidate_profiles": []}, {"allowed_permissions": ["shell"]},
                         {"domains": ["x"] * 65}):
            try:
                runtime.route_capabilities({**req["task"], **mutation})
                rejections.append(False)
            except NexusMcpError as exc:
                rejections.append(exc.code == "INVALID_REQUEST")
        checks["closed-route-input"] = all(rejections)
    finally:
        attempts["active"] = False
    effects = {key: value for key, value in attempts.items() if key != "active"}
    checks["observed-no-external-effects"] = not any(effects.values())
    checks["binding-unchanged"] = before == _material()
    if not all(checks.values()):
        return {"status": "FAILED", "checks": checks, "observed_effects": effects, "authority": "none"}
    now = int(time.time())
    scope = "g1-route-probe"
    unknown_cost = {"basis": "unknown", "currency": None, "components": {c: None for c in COST_PARTS}, "evidence_refs": []}
    host = {"schema_version": HOST_SCHEMA, "profile_id": "nexus-direct-route-host", "revision": "1",
            "configuration_id": "route-empty-local-roots", "adapter_sha256": configuration,
            "observed_at": now, "expires_at": now + 60, "scope_id": scope,
            "evidence_refs": ["pilot-source-and-probe"], "limitations": ["Only the existing initialized direct route operation."],
            "uncertainty": ["Whole-Host enforcement and monetary attribution remain unknown."],
            "host_id": "authorized-local-python-probe", "surface_id": "existing-route-method",
            "binding_id": "nexus.route_capabilities", "inventory_scope": "authorized_probe_visible_subset",
            "inventory_completeness": "not_globally_enumerated", "states": {k: True for k in STATES},
            "facilities": {k: None for k in FACILITIES},
            "lifecycle": {k: None for k in ("installed", "enabled", "loaded", "approved", "routable")},
            "enforcement_mechanisms": ["nexus_boundary"]}
    c = {"schema_version": CANDIDATE_SCHEMA, "candidate_id": "existing-route-operation", "model": None,
         "host": host, "cost": unknown_cost, "required_permissions": ["read_metadata"],
         "execution_mechanism": "nexus_local_read_plan",
         "path": {"complete": True, "host_native": True,
                  "nodes": [{"node_id": "owned-metadata-route", "kind": "host", "location": "local", "provider": "nexus",
                             "delegated": False, "remote_mcp": False, "evidence_refs": ["pilot-source-and-probe"],
                             "model_profile_sha256": None}]}}
    records = [{"schema_version": CONFORMANCE_SCHEMA, "record_id": "pilot-" + control,
                "subject_sha256": digest(c), "binding_sha256": binding_digest(c), "control_id": control,
                "operations": [OPERATION], "enforcing_layer": "nexus_boundary", "classification": "ENFORCED_INTEGRATION",
                "probe_result": "pass", "evidence_refs": ["pilot-" + control], "scope_id": scope,
                "observed_at": now, "expires_at": now + 60,
                "limitations": ["Declared parser/decision/output boundary only; no whole-Host guarantee."]} for control in CONTROLS]
    row = {"schema_version": OBSERVATION_SCHEMA, "subject_sha256": digest(c), "binding_sha256": binding_digest(c),
           "requirements_sha256": digest(req), "policy_sha256": policy_digest(policies),
           "scope_id": scope, "observed_at": now, "expires_at": now + 60, "states": dict(host["states"]),
           "task_classes": ["governance"], "capabilities": ["domain:governance", "output:selection", "validation:bounded"],
           "acceptance": ["decision-schema"], "budget_eligible": True, "path_verified": True,
           "conformance_sha256": [digest(r) for r in records], "evidence_refs": ["pilot-source-and-probe"]}
    observed = _issue_observations([row], source="authorized-existing-route-probe")
    args = {"candidates": [c], "policies": policies, "request": req, "conformance_records": records,
            "trusted_observations": observed, "now": now, "scope_id": scope}
    decision = select_capabilities(**args)
    reproducible = decision == select_capabilities(**args)
    # A mandatory restriction outside the reviewed pilot coverage must refuse.
    narrow_req = copy.deepcopy(req)
    narrow_req["hard_restrictions"].append({"control_id": "whole-host-network-isolation", "operations": [OPERATION],
                                           "minimum_classification": "ENFORCED_INTEGRATION"})
    narrow_row = {**row, "requirements_sha256": digest(narrow_req)}
    narrow = select_capabilities(**{**args, "request": narrow_req, "trusted_observations":
                                 _issue_observations([narrow_row], source="authorized-existing-route-probe")})
    return {"schema_version": "nexus.g1-pilot-report.v1", "status": "PASS" if decision["status"] == "SELECTED" and reproducible and narrow["status"] == "UNSUPPORTED" else "FAILED",
            "binding_material": before, "checks": checks, "observed_effects": effects,
            "legacy_route_result": first["result_code"], "candidate": c, "conformance_records": records,
            "decision": decision, "unsupported_whole_host_result": narrow["status"], "deterministic": reproducible,
            "permission_basis": "separately_authorized_local_probe_only", "budget_basis": "no_monetary_ceiling_requested",
            "scope_limit": "Initialized direct route method; no transport or whole-Host attestation; no product task executed.",
            "authority": "none"}


if __name__ == "__main__":
    report = run_probe()
    print(json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
