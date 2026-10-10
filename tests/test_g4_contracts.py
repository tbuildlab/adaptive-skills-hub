from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
import unittest

from ash import g4_contracts as c
from tests.g4_fixtures import *


class G4ContractTests(unittest.TestCase):
    def reject(self, args, code=None):
        with self.assertRaises(c.G4Error) as caught:
            c.validate_domain_bundle(**args)
        if code:
            self.assertEqual(str(caught.exception), code)

    def test_both_pack_positive_controls_are_structural_only(self):
        for pack in c.PACK_EVIDENCE:
            with self.subTest(pack=pack):
                verdict = c.validate_domain_bundle(**bundle(pack))
                self.assertEqual(verdict["status"], "PASS_STRUCTURAL_ONLY")
                self.assertEqual(verdict["basis"], "NON_AUTHORITATIVE")
                self.assertEqual(verdict["dispatch_authority"], "none")

    def test_five_record_round_trips_and_canonical_identity(self):
        for kind in c.FIELDS:
            with self.subTest(kind=kind):
                body = domain_body(kind)
                r = c.record(kind, body)
                self.assertEqual(r, c.record(kind, c.parse(json.dumps(body).encode())))
                self.assertEqual(r, c.record(kind, dict(reversed(list(body.items())))))
                self.assertEqual(r, c.record(kind, r.to_dict()))

    def test_every_schema_rejects_missing_extra_and_unknown_fields(self):
        for kind in c.FIELDS:
            body = domain_body(kind)
            for key in body:
                missing = {k: v for k, v in body.items() if k != key}
                with self.subTest(kind=kind, key=key), self.assertRaises(c.G4Error):
                    c.record(kind, missing)
            for changed in ({**body, "raw_reasoning": "secret"}, {**body, "schema_version": "v99"}):
                with self.assertRaises(c.G4Error):
                    c.record(kind, changed)

    def test_duplicate_keys_bounds_cycles_and_non_json(self):
        cycle = []; cycle.append(cycle)
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'"' + b'x' * 65536 + b'"'):
            with self.assertRaises(c.G4Error): c.parse(raw)
        for value in (cycle, {"x": [0] * 65}, {"x": "a" * 513}, {"x": object()}, {"x": -1}):
            with self.assertRaises(c.G4Error): c.canonical(value)

    def test_exact_binding_all_fields_and_evidence_corruption(self):
        for key, value in {"workspace_id": "other", "project_id": "other", "task_id": "other",
                           "action_id": "other", "execution_id": "other", "generation": 2,
                           "incarnation": "other", "input_sha256": ORIGINAL}.items():
            args = bundle(); args["expected_binding"][key] = value
            with self.subTest(key=key): self.reject(args, "G4_BINDING_MISMATCH")
        args = bundle(); args["impact"] = replace(args["impact"], record_id=ORIGINAL)
        self.reject(args, "G4_EVIDENCE_CORRUPT")

    def test_poisoned_confirmation_proposal_dispute_and_stale(self):
        for state in ("PROPOSED", "DISPUTED", "SUPERSEDED"):
            args = bundle(); args["decisions"] = (c.record("project-decision", domain_body("project-decision", state=state)),)
            self.reject(args, "G4_DECISION_NOT_CURRENT")
        args = bundle(); args["confirmation_refs"] = []
        self.reject(args, "G4_CONFIRMATION_UNVERIFIED")
        args = bundle(); args["now"] = NOW + 100
        self.reject(args, "G4_SOURCE_UNAVAILABLE")

    def test_independent_decision_slots_and_repository_source_oracles(self):
        args = bundle()
        args["decisions"] += (c.record("project-decision", domain_body("project-decision", decision_key="other-slot", content_sha256=ORIGINAL)),)
        self.assertEqual(c.validate_domain_bundle(**args)["status"], "PASS_STRUCTURAL_ONLY")
        for changes, code in (({"task_class": "other"}, "G4_PACK_INAPPLICABLE"),
                              ({"expected_repository_id": "other"}, "G4_REPOSITORY_MISMATCH"),
                              ({"expected_base_commit": "2" * 40}, "G4_REPOSITORY_MISMATCH"),
                              ({"source_digests": {SOURCE: ORIGINAL}}, "G4_SOURCE_DIGEST_MISMATCH")):
            self.reject({**bundle(), **changes}, code)

    def test_cross_namespace_disclosure_and_original_availability(self):
        for key in ("project_id", "task_id"):
            body = domain_body("context-manifest"); body["sources"][0][key] = "other"
            args = bundle(); args["context"] = c.record("context-manifest", body)
            self.reject(args, "G4_NAMESPACE_MISMATCH")
        args = bundle(); args["permitted_recipients"] = []
        self.reject(args, "G4_DISCLOSURE_DENIED")
        body = domain_body("context-manifest"); body["sources"][0].update(transformation="DERIVED", original_ref=ENDPOINT)
        args = bundle(); args["context"] = c.record("context-manifest", body)
        self.reject(args, "G4_ORIGINAL_REQUIRED")

    def test_reduction_loss_unresolved_forgetting_and_conflicts(self):
        args = bundle(); args["context"] = c.record("context-manifest", domain_body("context-manifest", preserved_obligations=[]))
        self.reject(args, "G4_REDUCTION_LOSS")
        args = bundle(); args["decisions"] = (c.record("project-decision", domain_body("project-decision", retention="FORGET_AUTHORIZED")),)
        self.reject(args, "G4_FORGET_UNRESOLVED")
        args = bundle(); args["decisions"] += (c.record("project-decision", domain_body("project-decision", content_sha256=ORIGINAL)),)
        self.reject(args, "G4_DECISION_CONFLICT")

    def test_supersession_requires_accessible_exact_history(self):
        args = bundle(); args["decisions"] = (c.record("project-decision", domain_body("project-decision", supersedes=ORIGINAL)),)
        self.assertEqual(c.validate_domain_bundle(**args)["status"], "PASS_STRUCTURAL_ONLY")
        args["source_refs"] = [SOURCE]
        self.reject(args, "G4_SUPERSESSION_INVALID")

    def test_relation_versions_provenance_conflicts_and_cycles(self):
        args = bundle(); args["endpoint_versions"][ENDPOINT] = "v2"
        self.reject(args, "G4_ENDPOINT_MISMATCH")
        args = bundle(); args["relations"] = (c.record("capability-relation", domain_body("capability-relation", provenance_refs=[ENDPOINT])),)
        self.reject(args, "G4_RELATION_UNVERIFIED")
        args = bundle(); args["relations"] = (c.record("capability-relation", domain_body("capability-relation", relation="conflicts_with")),)
        self.reject(args, "G4_RELATION_CONFLICT")
        args = bundle(); edge = domain_body("capability-relation", relation="depends_on")
        reverse = {**edge, "from_endpoint": edge["to_endpoint"], "to_endpoint": edge["from_endpoint"]}
        args["relations"] = (c.record("capability-relation", edge), c.record("capability-relation", reverse))
        self.reject(args, "G4_DEPENDENCY_CYCLE")

    def test_closed_relation_vocabulary(self):
        for relation in c.RELATIONS:
            c.record("capability-relation", domain_body("capability-relation", relation=relation))
        with self.assertRaises(c.G4Error):
            c.record("capability-relation", domain_body("capability-relation", relation="grants"))

    def test_dirty_input_shared_consumers_and_unexamined_areas(self):
        for fields, code in (({"consumers": ["page"]}, "G4_IMPACT_COVERAGE"),
                             ({"validation_obligations": ["other"]}, "G4_IMPACT_COVERAGE"),
                             ({"unexamined": ["shared-control"]}, "G4_IMPACT_UNKNOWN")):
            args = bundle(); args["impact"] = c.record("change-impact", domain_body("change-impact", **fields))
            self.reject(args, code)
        args = bundle(); args["observations"]["boundary"]["input_sha256"] = ORIGINAL
        self.reject(args, "G4_BINDING_MISMATCH")

    def test_pack_restrictions_and_missing_capabilities(self):
        args = bundle(); args["pack"] = c.record("workflow-pack", domain_body("workflow-pack", allowed_operations=["network"]))
        self.reject(args, "G4_POLICY_EXPANSION")
        args = bundle(); args["available_capabilities"] = []
        self.reject(args, "G4_CAPABILITY_UNAVAILABLE")

    def test_each_mandatory_acceptance_missing_failed_unknown_cancelled(self):
        for pack in c.PACK_EVIDENCE:
            for name in c.PACK_EVIDENCE[pack]:
                args = bundle(pack); del args["observations"][name]
                with self.subTest(pack=pack, name=name): self.reject(args, "G4_ACCEPTANCE_COVERAGE")
                for status in ("FAIL", "UNKNOWN", "CANCELLED"):
                    args = bundle(pack); args["observations"][name]["status"] = status
                    self.reject(args, "G4_OBSERVATION_NOT_PASS")

    def test_omitted_failure_mixed_artifact_and_forged_source(self):
        args = bundle(); args["observations"]["omitted-test"] = {**args["observations"]["boundary"], "status": "FAIL"}
        self.reject(args, "G4_OBSERVATION_NOT_PASS")
        args = bundle(); args["observations"]["boundary"]["artifact_sha256"] = ORIGINAL
        self.reject(args, "G4_ARTIFACT_MISMATCH")
        args = bundle(); args["observations"]["boundary"]["source_refs"] = [ENDPOINT]
        self.reject(args, "G4_OBSERVATION_SOURCE")

    def test_secret_paths_and_arbitrary_metadata_not_accepted(self):
        for value in ("Bearer secret-value", "password=secret", "C:/private/file", "sk-test-secret-value"):
            body = domain_body("change-impact", repository_id=value)
            with self.assertRaises(c.G4Error) as caught: c.record("change-impact", body)
            self.assertNotIn(value, str(caught.exception))

    def test_no_pack_removal_of_mandatory_evidence(self):
        with self.assertRaises(c.G4Error):
            c.record("workflow-pack", domain_body("workflow-pack", required_evidence=["boundary"]))

    def test_canonical_list_order_and_no_mutable_record_alias(self):
        body = domain_body("change-impact")
        original = c.record("change-impact", body)
        body["consumers"].reverse()
        self.assertEqual(original, c.record("change-impact", body))
        body["consumers"].append("other")
        self.assertNotEqual(original, c.record("change-impact", body))


if __name__ == "__main__": unittest.main()
