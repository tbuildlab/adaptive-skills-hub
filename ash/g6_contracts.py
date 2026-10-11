"""Pure G6 evidence contracts. Structural validity never qualifies a live product.

Reuse frozen validation/encoding. No models, dispatch, storage or approval service.
Caller-provided reference oracles establish consistency, not authenticity.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any

from .g1_profiles import G1Error, exact, token, tokens, sha, integer, enum
from .g4_contracts import G4Error, canonical, parse, binding, refs, digest

SCENARIOS = frozenset({"deterministic_governance", "repository_change", "source_backed_artifact",
    "interrupted_recovery", "quarantined_candidate", "configuration_substitution",
    "delegation_disabled", "public_release"})
NATIVE_CASES = frozenset({"deferred_tool_admission", "indirect_tool_admission",
    "transitive_delegation", "configuration_drift", "observation_gap", "compaction_loss",
    "revoked_resume", "cancellation_late_effect", "unknown_revised_cost", "whole_path_privacy"})
REQUIRED_CASES = SCENARIOS | NATIVE_CASES
RELEASE_CHECKS = frozenset({"artifact_integrity", "package_integrity", "provenance",
    "private_data_exclusion", "portable_paths", "installer_integrity", "revocation_update"})
REOPENING = frozenset({"code", "dependency", "policy", "binding", "threat_model"})
RESTRICTIONS = frozenset({"no_frontier", "local_private", "no_agents", "no_remote_mcp", "deterministic_only"})
RESULTS = frozenset({"PASS", "FAIL", "UNKNOWN", "UNSUPPORTED", "CANCELLED", "BLOCKED"})
UNITS = frozenset({"COUNT", "MILLISECONDS", "MICROCURRENCY", "SCORE_UNITS"})
METRICS = {"policy_violations":"COUNT", "evidence_completeness":"SCORE_UNITS",
    "recovery_accuracy":"SCORE_UNITS", "acceptance":"SCORE_UNITS", "retries":"COUNT",
    "cost":"MICROCURRENCY", "latency":"MILLISECONDS", "human_intervention":"COUNT",
    "transparency":"SCORE_UNITS"}
COMMON = {"schema_version", "basis", "binding", "subject_id", "observed_at", "expires_at", "state", "dispatch_authority"}
FIELDS = {
 "acceptance-suite": {"delegation_mode", "configurations", "scenarios", "native_cases"},
 "value-protocol": {"suite_ref", "registration_state", "registered_at", "evaluation_starts_at",
    "pilot_ref", "arms", "metrics", "primary_metric", "stopping_rules"},
 "qualification": {"suite_ref", "configuration_id", "scenario_id", "attempt_id",
    "capability_result", "governance_result", "effect_outcome", "evidence_basis", "evidence_refs",
    "artifact_sha256", "measurements", "monetary_cost_microunits"},
 "release-evidence": {"suite_ref", "protocol_ref", "artifact_sha256", "source_commit",
    "components", "checks", "approval_ref", "publication_authority_ref", "limitations"},
 "security-freeze": {"release_ref", "findings", "regression_ref", "independent_review_ref",
    "owner_acceptance_ref", "reopening_triggers", "freeze_mode"},
}


class G6Error(ValueError):
    """Fixed diagnostics; never echo untrusted evidence or Host output."""


def require(condition: bool, code: str = "G6_INVALID_INPUT") -> None:
    if not condition:
        raise G6Error(code)


def optional_sha(value: Any) -> None:
    if value is not None:
        sha(value)


def rows(value: Any, fields: set[str], key: str) -> list[dict]:
    require(type(value) is list and 0 < len(value) <= 64)
    seen = set()
    for row in value:
        exact(row, fields)
        token(row[key])
        require(row[key] not in seen, "G6_DUPLICATE_IDENTITY")
        seen.add(row[key])
    return value


def validate_body(kind: str, value: Any) -> dict:
    try:
        require(type(kind) is str and kind in FIELDS)
        canonical(value)
        exact(value, COMMON | FIELDS[kind])
        require(value["schema_version"] == f"nexus.g6.{kind}.v1")
        require(value["basis"] == "NON_AUTHORITATIVE" and value["dispatch_authority"] == "none")
        binding(value["binding"])
        token(value["subject_id"])
        integer(value["observed_at"]); integer(value["expires_at"])
        require(0 < value["expires_at"] - value["observed_at"] <= 86400)
        enum(value["state"], {"CURRENT", "RETIRED"})
        if kind == "acceptance-suite":
            require(value["delegation_mode"] == "DISABLED", "G6_G5_NOT_ENABLED")
            configurations = rows(value["configurations"], {"configuration_id", "host_ref", "model_ref",
                "configuration_sha256", "policy_sha256", "mode", "restrictions", "qualification_state"}, "configuration_id")
            for c in configurations:
                sha(c["host_ref"]); optional_sha(c["model_ref"])
                sha(c["configuration_sha256"]); sha(c["policy_sha256"])
                enum(c["mode"], {"DETERMINISTIC_ONLY", "GOVERNED_HOST", "LOCAL_PRIVATE"})
                enum(c["qualification_state"], {"OFFLINE_ONLY", "HISTORICAL_ONLY", "UNQUALIFIED"})
                restrictions = set(tokens(c["restrictions"], nonempty=True))
                require(restrictions <= RESTRICTIONS and "no_agents" in restrictions)
                if c["mode"] == "DETERMINISTIC_ONLY":
                    require(c["model_ref"] is None and "deterministic_only" in restrictions)
                if c["mode"] == "LOCAL_PRIVATE":
                    require({"local_private", "no_frontier", "no_agents", "no_remote_mcp"} <= restrictions)
            ids = {c["configuration_id"] for c in configurations}
            cases = rows(value["scenarios"], {"scenario_id", "configuration_ids", "capability_requirement",
                "evidence_requirements"}, "scenario_id")
            require({s["scenario_id"] for s in cases} == SCENARIOS, "G6_SCENARIO_COVERAGE")
            require(set(tokens(value["native_cases"], nonempty=True)) == NATIVE_CASES, "G6_NATIVE_COVERAGE")
            for s in cases:
                require(set(tokens(s["configuration_ids"], nonempty=True)) <= ids)
                enum(s["capability_requirement"], {"USEFUL_SUCCESS", "GOVERNANCE_ONLY"})
                tokens(s["evidence_requirements"], nonempty=True)
                if s["scenario_id"] in {"repository_change", "source_backed_artifact", "configuration_substitution"}:
                    require(s["capability_requirement"] == "USEFUL_SUCCESS", "G6_REFUSAL_ONLY_NOT_USEFUL")
                if s["scenario_id"] == "configuration_substitution":
                    selected = [c for c in configurations if c["configuration_id"] in s["configuration_ids"]]
                    require(len({(c["host_ref"], c["model_ref"]) for c in selected}) >= 2, "G6_SUBSTITUTION_NOT_MATERIAL")
                    require(any(c["mode"] == "LOCAL_PRIVATE" for c in selected), "G6_PRIVATE_SUCCESS_REQUIRED")
        elif kind == "value-protocol":
            sha(value["suite_ref"]); optional_sha(value["pilot_ref"])
            enum(value["registration_state"], {"DRAFT", "PREREGISTERED"})
            integer(value["registered_at"]); integer(value["evaluation_starts_at"])
            require(value["registered_at"] < value["evaluation_starts_at"], "G6_POSTHOC_PROTOCOL")
            arms = rows(value["arms"], {"arm_id", "host_ref", "model_ref", "configuration_sha256",
                "input_sha256", "policy_sha256", "criteria_sha256", "native_features_ref", "nexus_enabled"}, "arm_id")
            require({a["arm_id"] for a in arms} == {"native", "nexus"}, "G6_G5_NOT_ENABLED")
            for a in arms:
                for key in {"host_ref", "configuration_sha256", "input_sha256", "policy_sha256", "criteria_sha256", "native_features_ref"}:
                    sha(a[key])
                optional_sha(a["model_ref"])
                require(type(a["nexus_enabled"]) is bool and a["nexus_enabled"] == (a["arm_id"] == "nexus"))
            comparable = {"host_ref", "model_ref", "input_sha256", "policy_sha256", "criteria_sha256", "native_features_ref"}
            require(all(arms[0][k] == arms[1][k] for k in comparable), "G6_WEAKENED_COMPARATOR")
            metrics = rows(value["metrics"], {"metric_id", "unit", "direction", "minimum_benefit", "maximum_overhead"}, "metric_id")
            require({m["metric_id"] for m in metrics} == set(METRICS), "G6_VALUE_METRIC_COVERAGE")
            for m in metrics:
                enum(m["unit"], UNITS); enum(m["direction"], {"INCREASE", "DECREASE"})
                require(m["unit"] == METRICS[m["metric_id"]], "G6_MEASUREMENT_UNIT_MISMATCH")
                integer(m["minimum_benefit"], nullable=True); integer(m["maximum_overhead"], nullable=True)
            require(value["primary_metric"] in {m["metric_id"] for m in metrics})
            stop = exact(value["stopping_rules"], {"max_attempts", "max_duration_ms", "max_cost_microunits",
                "repetitions_per_arm", "unknown_cost", "failure_retention", "missing_measurements"})
            integer(stop["max_attempts"]); integer(stop["max_duration_ms"])
            integer(stop["repetitions_per_arm"], nullable=True)
            integer(stop["max_cost_microunits"], nullable=True)
            require(0 < stop["max_attempts"] <= 64 and stop["max_duration_ms"] > 0)
            require(stop["repetitions_per_arm"] is None or 0 < stop["repetitions_per_arm"] * 2 <= stop["max_attempts"])
            require(stop["unknown_cost"] == "STOP" and stop["failure_retention"] == "ALL_ATTEMPTS" and stop["missing_measurements"] == "UNKNOWN")
            if value["registration_state"] == "PREREGISTERED":
                require(value["pilot_ref"] is not None and all(m["minimum_benefit"] is not None and m["maximum_overhead"] is not None for m in metrics), "G6_VALUE_NOT_LOCKED")
                require(stop["repetitions_per_arm"] is not None, "G6_VALUE_NOT_LOCKED")
                require(value["observed_at"] <= value["registered_at"], "G6_POSTHOC_PROTOCOL")
        elif kind == "qualification":
            sha(value["suite_ref"])
            token(value["configuration_id"]); token(value["scenario_id"]); token(value["attempt_id"])
            require(value["scenario_id"] in REQUIRED_CASES)
            enum(value["capability_result"], RESULTS); enum(value["governance_result"], {"PASS", "FAIL", "UNKNOWN"})
            enum(value["effect_outcome"], {"NONE", "SETTLED", "UNKNOWN", "CANCEL_REQUESTED"})
            enum(value["evidence_basis"], {"STRUCTURAL_FIXTURE", "LOCAL_OBSERVATION", "HISTORICAL_SOURCE", "LIVE_SOURCE_REPORTED"})
            refs(value["evidence_refs"], nonempty=True); optional_sha(value["artifact_sha256"])
            integer(value["monetary_cost_microunits"], nullable=True)
            if value["capability_result"] == "PASS":
                require(value["artifact_sha256"] is not None, "G6_ARTIFACT_REQUIRED")
            require(type(value["measurements"]) is list)
            if value["measurements"]:
                for m in rows(value["measurements"], {"metric_id", "unit", "value"}, "metric_id"):
                    enum(m["unit"], UNITS); integer(m["value"], nullable=True)
        elif kind == "release-evidence":
            for key in {"suite_ref", "protocol_ref", "artifact_sha256"}: sha(value[key])
            optional_sha(value["approval_ref"]); optional_sha(value["publication_authority_ref"])
            require(type(value["source_commit"]) is str and len(value["source_commit"]) in {40, 64})
            require(all(c in "0123456789abcdef" for c in value["source_commit"]))
            for c in rows(value["components"], {"component_id", "sha256"}, "component_id"): sha(c["sha256"])
            for c in rows(value["checks"], {"check_id", "result", "artifact_sha256", "evidence_ref"}, "check_id"):
                require(c["check_id"] in RELEASE_CHECKS); enum(c["result"], {"PASS", "FAIL", "UNKNOWN"})
                sha(c["artifact_sha256"]); sha(c["evidence_ref"])
            tokens(value["limitations"])
        elif kind == "security-freeze":
            sha(value["release_ref"])
            for key in {"regression_ref", "independent_review_ref", "owner_acceptance_ref"}: optional_sha(value[key])
            require(set(tokens(value["reopening_triggers"], nonempty=True)) == REOPENING)
            require(value["freeze_mode"] == "PREPARATION_ONLY", "G6_PRODUCTION_FREEZE_DISABLED")
            require(type(value["findings"]) is list)
            if value["findings"]:
                for f in rows(value["findings"], {"finding_id", "severity", "disposition", "evidence_refs", "fix_ref", "retest_refs"}, "finding_id"):
                    enum(f["severity"], {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"})
                    enum(f["disposition"], {"OPEN", "FIXED", "FALSE_POSITIVE", "ACCEPTED_RISK", "DEFERRED"})
                    refs(f["evidence_refs"], nonempty=True); refs(f["retest_refs"]); optional_sha(f["fix_ref"])
                    if f["disposition"] == "FIXED": require(f["fix_ref"] is not None and bool(f["retest_refs"]), "G6_FIX_RETEST_REQUIRED")
        return parse(canonical(value))
    except G6Error:
        raise
    except (G1Error, G4Error, KeyError, TypeError, ValueError, RecursionError):
        raise G6Error("G6_INVALID_INPUT") from None


@dataclass(frozen=True, slots=True)
class QualificationRecord:
    """Immutable untrusted bytes, not a trusted approval/qualification receipt."""
    kind: str
    canonical_body: bytes
    record_id: str

    def to_dict(self) -> dict:
        return parse(self.canonical_body)


def record(kind: str, value: Any) -> QualificationRecord:
    body = canonical(validate_body(kind, value))
    identifier = hashlib.sha256(b"nexus.g6.evidence.v1\0" + kind.encode("ascii") + b"\0" + body).hexdigest()
    return QualificationRecord(kind, body, identifier)


def checked(value: Any, kind: str, expected_binding: dict, *, now: int) -> dict:
    try:
        binding(expected_binding); integer(now)
        require(type(value) is QualificationRecord)
        require(type(value.kind) is str and value.kind == kind)
        require(type(value.canonical_body) is bytes and type(value.record_id) is str)
        body = validate_body(kind, parse(value.canonical_body))
        rebuilt = record(kind, body)
        require(rebuilt == value, "G6_RECORD_CORRUPTED")
        require(body["binding"] == expected_binding, "G6_BINDING_MISMATCH")
        require(body["state"] == "CURRENT" and body["observed_at"] <= now < body["expires_at"], "G6_EVIDENCE_NOT_CURRENT")
        return body
    except G6Error:
        raise
    except (G1Error, G4Error, TypeError, ValueError, AttributeError):
        raise G6Error("G6_INVALID_INPUT") from None


def validate_bundle(*, suite: QualificationRecord, protocol: QualificationRecord,
    qualifications: list[QualificationRecord], release: QualificationRecord,
    freeze: QualificationRecord, expected_binding: dict, expected_artifact_sha256: str,
    expected_source_commit: str, expected_components: dict, configuration_profiles: dict,
    expected_attempt_refs: list[str], evidence: dict, now: int) -> dict:
    """Cross-record structural consistency only. Positive live claims stay unqualified.

    Expected identities/attempt inventory come from the independent caller. This
    function cannot authenticate that caller, measurements, reviewers or approvals.
    """
    try:
        sha(expected_artifact_sha256); canonical(expected_components); canonical(configuration_profiles); canonical(evidence)
        require(type(expected_source_commit) is str)
        refs(expected_attempt_refs, nonempty=True)
        require(len(set(expected_attempt_refs)) == len(expected_attempt_refs), "G6_DUPLICATE_ATTEMPT")
        s=checked(suite,"acceptance-suite",expected_binding,now=now)
        p=checked(protocol,"value-protocol",expected_binding,now=now)
        r=checked(release,"release-evidence",expected_binding,now=now)
        f=checked(freeze,"security-freeze",expected_binding,now=now)
        require(p["suite_ref"] == r["suite_ref"] == suite.record_id and r["protocol_ref"] == protocol.record_id and f["release_ref"] == release.record_id, "G6_RECORD_LINK_MISMATCH")
        if p["registration_state"] == "PREREGISTERED":
            require(p["registered_at"] <= now, "G6_POSTHOC_PROTOCOL")
        require(all(arm["input_sha256"] == expected_binding["input_sha256"] for arm in p["arms"]), "G6_BINDING_MISMATCH")
        require(r["artifact_sha256"] == expected_artifact_sha256 and r["source_commit"] == expected_source_commit, "G6_RELEASE_SUBSTITUTED")
        require({c["component_id"]:c["sha256"] for c in r["components"]} == expected_components, "G6_COMPONENT_SUBSTITUTED")
        for key,value in expected_components.items(): token(key); sha(value)
        cfgs={c["configuration_id"]:c for c in s["configurations"]}
        require(cfgs == configuration_profiles, "G6_CONFIGURATION_DRIFT")
        for ref, item in evidence.items():
            sha(ref)
            require(digest(item) == ref, "G6_EVIDENCE_CORRUPTED")
            require(item["binding_sha256"] == digest(expected_binding), "G6_EVIDENCE_SUBSTITUTED")
            integer(item["observed_at"])
            require(s["observed_at"] <= item["observed_at"] <= now, "G6_EVIDENCE_NOT_CURRENT")
        require(type(qualifications) is list and 0 < len(qualifications) <= 64)
        require(all(type(q) is QualificationRecord for q in qualifications))
        require(all(type(q.kind) is str and type(q.record_id) is str and type(q.canonical_body) is bytes for q in qualifications))
        actual_refs=[q.record_id for q in qualifications]
        require(len(set(actual_refs)) == len(actual_refs) and set(actual_refs) == set(expected_attempt_refs), "G6_ATTEMPT_INVENTORY_MISMATCH")
        require(len(qualifications) <= p["stopping_rules"]["max_attempts"], "G6_ATTEMPT_BOUND_EXCEEDED")
        attempts=set(); cells={}; cell_types={}; unavailable_measurements=False
        for q in qualifications:
            v=checked(q,"qualification",expected_binding,now=now)
            require(v["suite_ref"] == suite.record_id and v["configuration_id"] in cfgs, "G6_QUALIFICATION_SCOPE")
            attempt=(v["configuration_id"],v["scenario_id"],v["attempt_id"])
            require(attempt not in attempts,"G6_DUPLICATE_ATTEMPT")
            attempts.add(attempt)
            if p["registration_state"] == "PREREGISTERED":
                require(v["observed_at"] >= p["evaluation_starts_at"], "G6_POSTHOC_PROTOCOL")
            for ref in v["evidence_refs"]:
                require(ref in evidence,"G6_EVIDENCE_UNAVAILABLE")
                e=exact(evidence[ref],{"kind","evidence_type","binding_sha256","configuration_id","scenario_id","attempt_id","artifact_sha256","capability_result","governance_result","effect_outcome","observed_at","evidence_basis","measurements","monetary_cost_microunits"})
                require(e["kind"] == "qualification", "G6_EVIDENCE_SUBSTITUTED")
                token(e["evidence_type"])
                require(all(e[k] == v[k] for k in {"configuration_id","scenario_id","attempt_id","artifact_sha256","capability_result","governance_result","effect_outcome","observed_at"}),"G6_EVIDENCE_SUBSTITUTED")
                require(all(e[k] == v[k] for k in {"evidence_basis","measurements","monetary_cost_microunits"}), "G6_EVIDENCE_SUBSTITUTED")
                cell_types.setdefault(attempt[:2],set()).add(e["evidence_type"])
            require(v["effect_outcome"] not in {"UNKNOWN","CANCEL_REQUESTED"},"G6_UNRESOLVED_OUTCOME")
            require(v["governance_result"] == "PASS","G6_GOVERNANCE_NOT_PASS")
            if v["artifact_sha256"] is not None:
                require(v["artifact_sha256"] == expected_artifact_sha256,"G6_ARTIFACT_SUBSTITUTED")
            for m in v["measurements"]:
                metrics={m["metric_id"]:m for m in p["metrics"]}
                require(m["metric_id"] in metrics and m["unit"] == metrics[m["metric_id"]]["unit"],"G6_MEASUREMENT_UNIT_MISMATCH")
            unavailable_measurements |= (v["monetary_cost_microunits"] is None
                or {m["metric_id"] for m in v["measurements"]} != set(METRICS)
                or any(m["value"] is None for m in v["measurements"]))
            cells.setdefault((v["configuration_id"],v["scenario_id"]),[]).append(v)
        for case in s["scenarios"]:
            for cfg in case["configuration_ids"]:
                cell=cells.get((cfg,case["scenario_id"]),[])
                require(bool(cell),"G6_SCENARIO_COVERAGE")
                require(set(case["evidence_requirements"]) <= cell_types.get((cfg,case["scenario_id"]),set()), "G6_REQUIRED_EVIDENCE_MISSING")
                if case["capability_requirement"] == "USEFUL_SUCCESS":
                    require(any(v["capability_result"] == "PASS" for v in cell),"G6_REFUSAL_ONLY_NOT_USEFUL")
        require(all((cfg,scenario) in cells for cfg in cfgs for scenario in s["native_cases"]),"G6_NATIVE_COVERAGE")
        require({c["check_id"] for c in r["checks"]} == RELEASE_CHECKS,"G6_RELEASE_CHECK_COVERAGE")
        for c in r["checks"]:
            require(c["result"] == "PASS" and c["artifact_sha256"] == expected_artifact_sha256,"G6_RELEASE_CHECK_NOT_PASS")
            require(c["evidence_ref"] in evidence,"G6_EVIDENCE_UNAVAILABLE")
            e=exact(evidence[c["evidence_ref"]], {"kind","binding_sha256","check_id","result","artifact_sha256","observed_at"})
            require(e["kind"] == "release_check" and all(e[k] == c[k] for k in {"check_id","result","artifact_sha256"}), "G6_EVIDENCE_SUBSTITUTED")
        def document(ref: str | None, purpose: str, subject_id: str | None = None) -> None:
            if ref is None:
                return
            require(ref in evidence,"G6_EVIDENCE_UNAVAILABLE")
            e=exact(evidence[ref], {"kind","binding_sha256","purpose","subject_id","artifact_sha256","observed_at","source_ref"})
            require(e["kind"] == "document" and e["purpose"] == purpose and e["artifact_sha256"] == expected_artifact_sha256, "G6_EVIDENCE_SUBSTITUTED")
            token(e["subject_id"])
            require(subject_id is None or e["subject_id"] == subject_id, "G6_EVIDENCE_SUBSTITUTED")
            sha(e["source_ref"])
        for finding in f["findings"]:
            for ref in finding["evidence_refs"]: document(ref,"finding",finding["finding_id"])
            for ref in finding["retest_refs"]: document(ref,"retest",finding["finding_id"])
            document(finding["fix_ref"],"fix",finding["finding_id"])
            if finding["severity"] in {"CRITICAL","HIGH"}:
                require(finding["disposition"] in {"FIXED","FALSE_POSITIVE"},"G6_SECURITY_FINDING_OPEN")
                require(f["independent_review_ref"] is not None, "G6_INDEPENDENT_REVIEW_MISSING")
        for ref,purpose in [(p["pilot_ref"],"pilot"),(r["approval_ref"],"approval"),(r["publication_authority_ref"],"publication"),(f["regression_ref"],"regression"),(f["independent_review_ref"],"independent_review"),(f["owner_acceptance_ref"],"owner_acceptance")]:
            document(ref,purpose)
        return {"status":"PASS_STRUCTURAL_ONLY","basis":"NON_AUTHORITATIVE","dispatch_authority":"none",
            "suite_ref":suite.record_id,"release_ref":release.record_id,"binding_sha256":digest(expected_binding),
            "capability_qualification":"NOT_LIVE_QUALIFIED","governance_qualification":"STRUCTURAL_ONLY",
            "value_qualification":"UNMEASURED","unknown_measurements_retained":unavailable_measurements,
            "protocol_preregistered":p["registration_state"] == "PREREGISTERED",
            "production_freeze":"DENY","real_admission_enabled":False}
    except G6Error:
        raise
    except (G1Error,G4Error,KeyError,TypeError,ValueError,AttributeError,RecursionError):
        raise G6Error("G6_INVALID_INPUT") from None
