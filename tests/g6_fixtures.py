"""NON_AUTHORITATIVE synthetic G6 examples. No runtime or reviewer evidence.

Only tests import this module. Even a complete synthetic bundle cannot dispatch.
"""
from copy import deepcopy
from ash import g6_contracts as c
from tests.g4_fixtures import binding, NOW, ARTIFACT, SOURCE


def base(kind, **fields):
    return {"schema_version": f"nexus.g6.{kind}.v1", "basis": "NON_AUTHORITATIVE",
            "binding": binding(), "subject_id": "fixture-g6", "observed_at": NOW,
            "expires_at": NOW+100, "state": "CURRENT", "dispatch_authority": "none", **fields}


def configurations():
    return [{"configuration_id": name, "host_ref": h*64, "model_ref": None if h == "a" else "d"*64,
             "configuration_sha256": h*64, "policy_sha256": SOURCE, "mode": mode,
             "restrictions": restrictions, "qualification_state": "UNQUALIFIED"}
            for name,h,mode,restrictions in [
                ("offline", "a", "DETERMINISTIC_ONLY", ["no_agents", "deterministic_only"]),
                ("private", "b", "LOCAL_PRIVATE", ["local_private", "no_frontier", "no_agents", "no_remote_mcp"])]]


def suite_body():
    return base("acceptance-suite", delegation_mode="DISABLED", configurations=configurations(),
        scenarios=[{"scenario_id": name, "configuration_ids": ["offline", "private"],
                    "capability_requirement": "USEFUL_SUCCESS" if name in {
                        "repository_change", "source_backed_artifact", "configuration_substitution"} else "GOVERNANCE_ONLY",
                    "evidence_requirements": ["observation"]} for name in sorted(c.SCENARIOS)],
        native_cases=sorted(c.NATIVE_CASES))


def protocol_body(suite_ref):
    return base("value-protocol", suite_ref=suite_ref, registration_state="DRAFT",
        registered_at=NOW, evaluation_starts_at=NOW+1, pilot_ref=None,
        arms=[{"arm_id": arm, "host_ref": SOURCE, "model_ref": None,
               "configuration_sha256": ("a" if arm == "native" else "b")*64,
               "input_sha256": "0"*64, "policy_sha256": SOURCE, "criteria_sha256": SOURCE,
               "native_features_ref": SOURCE, "nexus_enabled": arm == "nexus"} for arm in ["native", "nexus"]],
        metrics=[{"metric_id": name, "unit": unit, "direction": "DECREASE" if unit in {"COUNT","MICROCURRENCY","MILLISECONDS"} else "INCREASE",
                  "minimum_benefit": None, "maximum_overhead": None} for name,unit in c.METRICS.items()], primary_metric="latency",
        stopping_rules={"max_attempts": 64, "max_duration_ms": 100000, "max_cost_microunits": None,
                        "repetitions_per_arm": None,
                        "unknown_cost": "STOP", "failure_retention": "ALL_ATTEMPTS", "missing_measurements": "UNKNOWN"})


def add_document(bundle, purpose, subject_id="fixture-g6"):
    e={"kind": "document", "binding_sha256": c.digest(binding()), "purpose": purpose,
       "subject_id": subject_id, "artifact_sha256": ARTIFACT, "observed_at": NOW, "source_ref": SOURCE}
    ref=c.digest(e); bundle["evidence"][ref]=e
    return ref


def replace_qualification(bundle, index, **changes):
    """Rebuild record and oracle, allowing negative tests past integrity checks."""
    old=bundle["qualifications"][index]
    value={**old.to_dict(), **changes}
    e={k:deepcopy(value[k]) for k in ["configuration_id", "scenario_id", "attempt_id",
        "artifact_sha256", "capability_result", "governance_result", "effect_outcome", "observed_at",
        "evidence_basis", "measurements", "monetary_cost_microunits"]}
    e.update(kind="qualification", evidence_type="observation", binding_sha256=c.digest(value["binding"]))
    ref=c.digest(e); bundle["evidence"][ref]=e
    for previous in value["evidence_refs"]:
        if not any(previous in other.to_dict()["evidence_refs"] for i,other in enumerate(bundle["qualifications"]) if i != index):
            bundle["evidence"].pop(previous, None)
    value["evidence_refs"]=[ref]
    updated=c.record("qualification",value)
    bundle["qualifications"][index]=updated
    bundle["expected_attempt_refs"][index]=updated.record_id
    return updated


def bundle():
    suite=c.record("acceptance-suite",suite_body())
    protocol=c.record("value-protocol",protocol_body(suite.record_id))
    b={"suite":suite, "protocol":protocol, "expected_binding":binding(), "now":NOW,
       "expected_artifact_sha256":ARTIFACT, "expected_source_commit":"1"*40,
       "expected_components":{"source":SOURCE}, "configuration_profiles":{
           cfg["configuration_id"]:cfg for cfg in configurations()}, "evidence":{},
       "qualifications":[], "expected_attempt_refs":[]}
    for cfg in ["offline", "private"]:
        for scenario in sorted(c.REQUIRED_CASES):
            q=c.record("qualification", base("qualification", suite_ref=suite.record_id,
                configuration_id=cfg, scenario_id=scenario, attempt_id="first",
                capability_result="PASS", governance_result="PASS", effect_outcome="SETTLED",
                evidence_basis="STRUCTURAL_FIXTURE", evidence_refs=[SOURCE], artifact_sha256=ARTIFACT,
                measurements=[{"metric_id":"latency", "unit":"MILLISECONDS", "value":None}],
                monetary_cost_microunits=None))
            b["qualifications"].append(q); b["expected_attempt_refs"].append(q.record_id)
            replace_qualification(b,len(b["qualifications"])-1)
    checks=[]
    for name in sorted(c.RELEASE_CHECKS):
        e={"kind":"release_check", "binding_sha256":c.digest(binding()), "check_id":name,
           "result":"PASS", "artifact_sha256":ARTIFACT, "observed_at":NOW}
        ref=c.digest(e); b["evidence"][ref]=e
        checks.append({k:e[k] for k in ["check_id","result","artifact_sha256"]} | {"evidence_ref":ref})
    release=c.record("release-evidence", base("release-evidence", suite_ref=suite.record_id,
        protocol_ref=protocol.record_id, artifact_sha256=ARTIFACT, source_commit="1"*40,
        components=[{"component_id":"source", "sha256":SOURCE}], checks=checks,
        approval_ref=None, publication_authority_ref=None, limitations=["blocked_by_g3", "blocked_by_d03", "value_unmeasured"]))
    b["release"]=release
    b["freeze"]=c.record("security-freeze", base("security-freeze", release_ref=release.record_id,
        findings=[], regression_ref=None, independent_review_ref=None, owner_acceptance_ref=None,
        reopening_triggers=sorted(c.REOPENING), freeze_mode="PREPARATION_ONLY"))
    return b
