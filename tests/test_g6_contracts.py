from copy import deepcopy
import unittest

from ash import g6_contracts as c
from ash import g6_host_adapter as a
from tests import g6_fixtures as f
from tests import g4_fixtures as g4


class G6ContractsTests(unittest.TestCase):
    def rejected(self, b, code=None):
        with self.assertRaises(c.G6Error) as raised: c.validate_bundle(**b)
        if code: self.assertEqual(str(raised.exception),code)
        self.assertEqual(a.evaluate_preparation(b)["status"],"DENY")

    def replace(self,b,key,**changes):
        old=b[key]; b[key]=c.record(old.kind,old.to_dict() | changes)

    def test_five_contracts_round_trip_immutable_digest_and_non_authority(self):
        b=f.bundle()
        for rec in [b[k] for k in ["suite","protocol","release","freeze"]]+[b["qualifications"][0]]:
            self.assertEqual(c.record(rec.kind,c.parse(rec.canonical_body)),rec)
            body=rec.to_dict(); body["subject_id"]="changed"
            self.assertNotEqual(body,rec.to_dict())
        result=c.validate_bundle(**b)
        self.assertEqual(result["status"],"PASS_STRUCTURAL_ONLY")
        self.assertEqual(result["value_qualification"],"UNMEASURED")
        self.assertFalse(result["real_admission_enabled"])
        self.assertTrue(result["unknown_measurements_retained"])

    def test_schema_extra_missing_version_authority_and_basis_rejected(self):
        for key,value in [("schema_version","v99"),("basis","LIVE"),("dispatch_authority","execute"),("unknown_field","x")]:
            for rec in [f.bundle()[k] for k in ["suite","protocol","release","freeze"]]:
                with self.subTest(kind=rec.kind,key=key), self.assertRaises(c.G6Error):
                    c.record(rec.kind,rec.to_dict() | {key:value})
        value=f.suite_body(); del value["binding"]
        with self.assertRaises(c.G6Error): c.record("acceptance-suite",value)

    def test_bindings_principal_task_generation_incarnation_and_input(self):
        for key in f.binding():
            b=f.bundle(); b["expected_binding"][key]=2 if key=="generation" else ("f"*64 if key=="input_sha256" else "other")
            with self.subTest(key=key): self.rejected(b,"G6_BINDING_MISMATCH")

    def test_expiry_future_observation_retirement_and_restart(self):
        for changes in [{"now":f.NOW+100},{"now":f.NOW-1}]:
            b=f.bundle(); b.update(changes); self.rejected(b,"G6_EVIDENCE_NOT_CURRENT")
        b=f.bundle(); self.replace(b,"suite",state="RETIRED"); self.rejected(b,"G6_EVIDENCE_NOT_CURRENT")
        original=f.bundle(); restored=deepcopy(original)
        self.assertEqual(c.validate_bundle(**original),c.validate_bundle(**restored))
        restored["expected_binding"]["incarnation"]="restart"; self.rejected(restored)

    def test_record_forgery_corrupted_bytes_and_identity(self):
        b=f.bundle(); original=b["suite"]
        for body,ref in [(original.canonical_body,"f"*64),(b"{}",original.record_id),(b"not-json",original.record_id)]:
            changed=deepcopy(b); changed["suite"]=c.QualificationRecord("acceptance-suite",body,ref)
            self.rejected(changed)
        b["suite"]=b["suite"].to_dict(); self.rejected(b)

    def test_scope_requires_all_scenarios_native_cases_and_useful_success(self):
        for field in ["scenarios","native_cases"]:
            v=f.suite_body(); v[field].pop()
            with self.assertRaises(c.G6Error): c.record("acceptance-suite",v)
        v=f.suite_body(); v["scenarios"][0]["capability_requirement"]="GOVERNANCE_ONLY"
        with self.assertRaises(c.G6Error): c.record("acceptance-suite",v)

    def test_substitution_requires_material_profiles_and_private_restrictions(self):
        v=f.suite_body(); v["configurations"][1]["host_ref"]=v["configurations"][0]["host_ref"]; v["configurations"][1]["model_ref"]=None
        with self.assertRaises(c.G6Error): c.record("acceptance-suite",v)
        for restriction in ["local_private","no_frontier","no_agents","no_remote_mcp"]:
            v=f.suite_body(); v["configurations"][1]["restrictions"].remove(restriction)
            with self.assertRaises(c.G6Error): c.record("acceptance-suite",v)

    def test_g5_disabled_and_config_policy_drift(self):
        v=f.suite_body(); v["delegation_mode"]="ENABLED"
        with self.assertRaises(c.G6Error): c.record("acceptance-suite",v)
        for key in ["policy_sha256","host_ref","configuration_sha256","qualification_state"]:
            b=f.bundle(); b["configuration_profiles"]["offline"][key]="UNQUALIFIED" if key=="qualification_state" else "f"*64
            # qualification_state already UNQUALIFIED; use an actual drift.
            if key=="qualification_state": b["configuration_profiles"]["offline"][key]="OFFLINE_ONLY"
            self.rejected(b,"G6_CONFIGURATION_DRIFT")

    def test_value_comparator_cannot_weaken_inputs_permissions_native_features(self):
        for key in ["host_ref","model_ref","input_sha256","policy_sha256","criteria_sha256","native_features_ref"]:
            p=f.protocol_body("a"*64); p["arms"][1][key]="f"*64
            with self.subTest(key=key), self.assertRaises(c.G6Error): c.record("value-protocol",p)

    def test_preregistration_requires_pilot_locked_thresholds_and_precedes_runs(self):
        p=f.protocol_body("a"*64); p["registration_state"]="PREREGISTERED"
        with self.assertRaises(c.G6Error): c.record("value-protocol",p)
        p["pilot_ref"]="b"*64
        for m in p["metrics"]: m.update(minimum_benefit=1,maximum_overhead=1)
        with self.assertRaises(c.G6Error): c.record("value-protocol",p)
        p["stopping_rules"]["repetitions_per_arm"]=1
        self.assertEqual(c.record("value-protocol",p).to_dict()["registration_state"],"PREREGISTERED")
        p["registered_at"]=p["evaluation_starts_at"]
        with self.assertRaises(c.G6Error): c.record("value-protocol",p)
        b=f.bundle(); pilot=f.add_document(b,"pilot")
        p=b["protocol"].to_dict(); p.update(registration_state="PREREGISTERED",pilot_ref=pilot)
        for m in p["metrics"]: m.update(minimum_benefit=1,maximum_overhead=1)
        p["stopping_rules"]["repetitions_per_arm"]=1
        b["protocol"]=c.record("value-protocol",p)
        self.replace(b,"release",protocol_ref=b["protocol"].record_id)
        self.replace(b,"freeze",release_ref=b["release"].record_id)
        self.rejected(b,"G6_POSTHOC_PROTOCOL")

    def test_retention_stopping_rules_are_explicit_and_bounded(self):
        for key,value in [("max_attempts",65),("max_attempts",0),("max_duration_ms",0),("repetitions_per_arm",0),("repetitions_per_arm",33),("unknown_cost","CONTINUE"),("failure_retention","SUCCESS_ONLY"),("missing_measurements","PASS")]:
            p=f.protocol_body("a"*64); p["stopping_rules"][key]=value
            with self.assertRaises(c.G6Error): c.record("value-protocol",p)

    def test_record_links_exact_artifact_source_and_component_identity(self):
        for field,value in [("expected_artifact_sha256","f"*64),("expected_source_commit","2"*40),("expected_components",{"source":"f"*64})]:
            b=f.bundle(); b[field]=value; self.rejected(b)
        b=f.bundle(); self.replace(b,"release",suite_ref="f"*64); self.rejected(b,"G6_RECORD_LINK_MISMATCH")

    def test_missing_attempt_inventory_duplicate_records_and_duplicate_ids(self):
        b=f.bundle(); b["qualifications"].pop(); self.rejected(b,"G6_ATTEMPT_INVENTORY_MISMATCH")
        b=f.bundle(); b["qualifications"].append(b["qualifications"][0]); self.rejected(b,"G6_ATTEMPT_INVENTORY_MISMATCH")
        b=f.bundle(); b["expected_attempt_refs"].append(b["expected_attempt_refs"][0]); self.rejected(b)
        b=f.bundle(); b["qualifications"].append(b["qualifications"][0]); b["expected_attempt_refs"].append(b["qualifications"][0].record_id)
        self.rejected(b)

    def test_native_coverage_is_required_for_each_profile(self):
        b=f.bundle(); i=next(i for i,q in enumerate(b["qualifications"]) if q.to_dict()["scenario_id"] in c.NATIVE_CASES)
        b["qualifications"].pop(i); b["expected_attempt_refs"].pop(i)
        self.rejected(b,"G6_NATIVE_COVERAGE")

    def test_all_refusal_does_not_establish_product_success(self):
        b=f.bundle()
        for i in range(len(b["qualifications"])): f.replace_qualification(b,i,capability_result="BLOCKED",artifact_sha256=None,effect_outcome="NONE")
        self.rejected(b,"G6_REFUSAL_ONLY_NOT_USEFUL")

    def test_failed_attempts_are_retained_without_becoming_governance_pass(self):
        b=f.bundle(); original=b["qualifications"][0]
        b["qualifications"].append(original); b["expected_attempt_refs"].append(original.record_id)
        f.replace_qualification(b,len(b["qualifications"])-1,attempt_id="failed",capability_result="FAIL",effect_outcome="NONE")
        self.assertEqual(c.validate_bundle(**b)["status"],"PASS_STRUCTURAL_ONLY")
        b["qualifications"].pop(); self.rejected(b,"G6_ATTEMPT_INVENTORY_MISMATCH")
        b=f.bundle(); f.replace_qualification(b,0,governance_result="FAIL"); self.rejected(b,"G6_GOVERNANCE_NOT_PASS")

    def test_unknown_timeout_cancellation_and_partial_effects_cannot_qualify(self):
        for outcome in ["UNKNOWN","CANCEL_REQUESTED"]:
            b=f.bundle(); f.replace_qualification(b,0,effect_outcome=outcome,capability_result="CANCELLED")
            self.rejected(b,"G6_UNRESOLVED_OUTCOME")
        b=f.bundle(); f.replace_qualification(b,0,governance_result="UNKNOWN"); self.rejected(b,"G6_GOVERNANCE_NOT_PASS")

    def test_evidence_content_corruption_scope_and_missing_requirement(self):
        b=f.bundle(); ref=b["qualifications"][0].to_dict()["evidence_refs"][0]
        b["evidence"][ref]["attempt_id"]="other"; self.rejected(b,"G6_EVIDENCE_CORRUPTED")
        b=f.bundle(); i=next(i for i,q in enumerate(b["qualifications"]) if q.to_dict()["scenario_id"] in c.SCENARIOS)
        q=b["qualifications"][i]; v=q.to_dict(); ref=v["evidence_refs"][0]
        e=b["evidence"].pop(ref); e["evidence_type"]="irrelevant"; newref=c.digest(e); b["evidence"][newref]=e
        updated=c.record("qualification",v | {"evidence_refs":[newref]}); b["qualifications"][i]=updated; b["expected_attempt_refs"][i]=updated.record_id
        self.rejected(b,"G6_REQUIRED_EVIDENCE_MISSING")

    def test_measurements_units_basis_and_cost_are_bound_to_evidence(self):
        b=f.bundle(); f.replace_qualification(b,0,measurements=[{"metric_id":"latency","unit":"COUNT","value":1}])
        self.rejected(b,"G6_MEASUREMENT_UNIT_MISMATCH")
        for key,value in [("monetary_cost_microunits",1),("evidence_basis","LIVE_SOURCE_REPORTED")]:
            b=f.bundle(); v=b["qualifications"][0].to_dict(); b["qualifications"][0]=c.record("qualification",v | {key:value}); b["expected_attempt_refs"][0]=b["qualifications"][0].record_id
            self.rejected(b,"G6_EVIDENCE_SUBSTITUTED")

    def test_release_checks_cannot_use_unrelated_success_or_unknown(self):
        b=f.bundle(); v=b["release"].to_dict(); v["checks"][0]["evidence_ref"]=b["qualifications"][0].to_dict()["evidence_refs"][0]
        b["release"]=c.record("release-evidence",v); self.replace(b,"freeze",release_ref=b["release"].record_id); self.rejected(b)
        b=f.bundle(); v=b["release"].to_dict(); v["checks"][0]["result"]="UNKNOWN"
        b["release"]=c.record("release-evidence",v); self.replace(b,"freeze",release_ref=b["release"].record_id); self.rejected(b,"G6_RELEASE_CHECK_NOT_PASS")

    def test_critical_findings_require_fix_retest_and_independent_review(self):
        b=f.bundle(); finding={"finding_id":"fixture-finding", "severity":"HIGH", "disposition":"FIXED",
            "evidence_refs":[f.add_document(b,"finding","fixture-finding")],
            "fix_ref":f.add_document(b,"fix","fixture-finding"), "retest_refs":[f.add_document(b,"retest","fixture-finding")]}
        self.replace(b,"freeze",findings=[finding]); self.rejected(b,"G6_INDEPENDENT_REVIEW_MISSING")
        self.replace(b,"freeze",independent_review_ref=f.add_document(b,"independent_review"))
        self.assertEqual(c.validate_bundle(**b)["production_freeze"],"DENY")
        finding["disposition"]="OPEN"; self.replace(b,"freeze",findings=[finding]); self.rejected(b,"G6_SECURITY_FINDING_OPEN")

    def test_freeze_review_owner_and_pilot_references_require_purpose_binding(self):
        b=f.bundle(); self.replace(b,"freeze",owner_acceptance_ref=f.add_document(b,"pilot")); self.rejected(b,"G6_EVIDENCE_SUBSTITUTED")
        for change in [{"freeze_mode":"PRODUCTION"},{"reopening_triggers":["code"]}]:
            v=f.bundle()["freeze"].to_dict()
            with self.assertRaises(c.G6Error): c.record("security-freeze",v | change)

    def test_bounded_input_secret_redaction_and_deterministic_diagnostics(self):
        class Trap:
            def __eq__(self, other):
                raise AssertionError("untrusted equality callback reached")
            def __hash__(self):
                raise AssertionError("untrusted hash callback reached")
        with self.assertRaises(c.G6Error): c.record(Trap(),{})
        b=f.bundle(); b["expected_source_commit"]=Trap(); self.rejected(b)
        for field in ["kind","record_id"]:
            b=f.bundle(); q=b["qualifications"][0]
            b["qualifications"][0]=c.QualificationRecord(Trap() if field=="kind" else q.kind,
                q.canonical_body,Trap() if field=="record_id" else q.record_id)
            self.rejected(b)
        domain=g4.bundle(); domain["expected_binding"]=Trap()
        self.assertEqual(a.evaluate_preparation(f.bundle(),domain_bundle=domain)["status"],"DENY")
        for value in [None,[],{"authorization":"Bearer synthetic-secret"},{"cookie":"synthetic-cookie"}]:
            with self.assertRaises(c.G6Error) as err: c.record("acceptance-suite",value)
            self.assertEqual(str(err.exception),"G6_INVALID_INPUT")
        v=f.suite_body(); v["subject_id"]="x"*513
        with self.assertRaises(c.G6Error): c.record("acceptance-suite",v)
        cycle={}; cycle["loop"]=cycle
        self.assertEqual(a.evaluate_preparation(cycle)["reason"],"G6_INVALID_INPUT")

    def test_host_adapter_production_deny_fixtures_recovery_and_malformed(self):
        b=f.bundle(); verdict=a.evaluate_preparation(b)
        self.assertEqual(verdict["g3_dependency"],"BLOCKED_BY_G3")
        for authority in [None,b["freeze"],verdict,{"status":"PASS","d03":"QUALIFIED"}]:
            for req in [g4.request(),g4.request(requires_recovery=True),{}]:
                d=a.release_gate(req,authority,now=f.NOW)
                self.assertEqual(d["status"],"DENY"); self.assertFalse(d["real_admission_enabled"])
        self.assertEqual(a.release_gate(g4.request(requires_recovery=True),now=f.NOW)["d03_dependency"],"BLOCKED_BY_D03")

    def test_g4_website_report_composition_and_wrong_artifact_binding(self):
        for pack in g4.c.PACK_EVIDENCE:
            domain=g4.bundle(pack)
            self.assertEqual(a.evaluate_preparation(f.bundle(),domain_bundle=domain)["status"],"PASS_STRUCTURAL_ONLY")
            for o in domain["observations"].values(): o["artifact_sha256"]="f"*64
            self.assertEqual(a.evaluate_preparation(f.bundle(),domain_bundle=domain)["status"],"DENY")


if __name__ == "__main__": unittest.main()
