"""Synthetic compatibility tests only; no production mapping or state update."""
from pathlib import Path
import copy
import hashlib
import unittest

from ash.evaluation import (
    EvaluationError,
    _load_test_validator_registry,
    canonical_sha256,
    evaluate_contract,
    validate_evaluation_receipt,
)
from tests.test_governance_assessment_offline import CORPUS, base, candidate, encode

ROOT = Path(__file__).resolve().parents[1]


def subject(digest):
    # Synthetic unasserted lifecycle: no invented task-execution/stage evidence.
    return {
        "subject_type": "artifact",
        "subject_id": "synthetic-assessment-bytes",
        "subject_sha256": digest,
        "parent_subject_sha256": None,
        "lifecycle": {
            "creation": "not_created", "selection": "not_selected",
            "execution": "not_executed", "review": "not_reviewed",
            "enhancement": "not_enhanced", "validation": "not_validated",
            "reporting": "not_reported",
        },
        "stage_receipts": {key: None for key in ("creator", "execution", "reviewer", "enhancer", "reporter")},
    }


def check(identity, observed, expected=None, operator="equals"):
    return {
        "check_id": identity, "operator": operator, "required": True,
        "expected": expected, "observed": observed,
        "evidence": {
            "evidence_id": "synthetic-" + identity,
            "content_sha256": canonical_sha256(observed),
            "summary": "Synthetic structural metadata only; no evidence truth or task acceptance.",
        },
    }


def request(digest, validator, checks):
    return {
        "schema_version": "nexus.evaluation-request.v1",
        "validator_id": validator, "validator_version": "1",
        "subject": subject(digest), "checks": checks,
    }


class AdvisoryCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = _load_test_validator_registry(root=ROOT)

    def receipts(self, data, report):
        digest = hashlib.sha256(data).hexdigest()
        digest_receipt = evaluate_contract(request(digest, "nexus.validator.digest-integrity", [check("exact-bytes", report["input_sha256"], operator="sha256_matches_subject")]), registry=self.registry)
        schema_receipt = evaluate_contract(request(digest, "nexus.validator.schema", [check("declared-structure", report["structure"], "CONSISTENT"), check("declared-authority", report["authority"], "none")]), registry=self.registry)
        for receipt in (digest_receipt, schema_receipt):
            self.assertEqual(validate_evaluation_receipt(receipt, registry=self.registry, expected_subject_sha256=digest), receipt)
            self.assertEqual(set(receipt["authority"].values()), {"none", False})
            self.assertFalse(receipt["state_transition"]["applied"])
            self.assertEqual(receipt["proof_scope"]["proves"], "declared_checks_for_exact_subject_digest_only")
            self.assertEqual(receipt["subject"]["lifecycle"]["execution"], "not_executed")
        return digest_receipt, schema_receipt

    def test_structural_pass_does_not_settle_unknown_effect(self):
        data = encode(base("F"))
        before = bytes(data)
        report = candidate.review_bytes(data)
        receipts = self.receipts(data, report)
        self.assertTrue(all(r["result"]["state"] == "PASS" for r in receipts))
        self.assertEqual(report["handling"], "PRESERVE_UNKNOWN")
        self.assertTrue(report["unresolved_required_checks"])
        self.assertEqual(data, before)

    def test_structural_pass_does_not_promote_capability(self):
        data = encode(base("G"))
        report = candidate.review_bytes(data)
        self.assertTrue(all(r["result"]["state"] == "PASS" for r in self.receipts(data, report)))
        self.assertEqual(report["handling"], "PRESERVE_UNKNOWN")
        self.assertGreaterEqual(len(report["unresolved_required_checks"]), 2)

    def test_entire_corpus_integrity_is_distinct_from_structure_and_truth(self):
        for case in CORPUS["cases"]:
            with self.subTest(case=case["id"]):
                data = encode(case["record"])
                report = candidate.review_bytes(data)
                integrity, shape = self.receipts(data, report)
                self.assertEqual(integrity["result"]["state"], "PASS")
                self.assertEqual(shape["result"]["state"], "FAIL" if report["structure"] == "INVALID" else "PASS")
                self.assertEqual(report["handling"], case["expected_offline"])

    def test_replaced_or_reordered_bytes_invalidate_current_subject_binding(self):
        data = encode(base("F"))
        receipts = self.receipts(data, candidate.review_bytes(data))
        changed = data + b" "
        self.assertEqual(candidate.review_bytes(changed)["handling"], "PRESERVE_UNKNOWN")
        for receipt in receipts:
            with self.assertRaises(EvaluationError):
                validate_evaluation_receipt(receipt, registry=self.registry, expected_subject_sha256=hashlib.sha256(changed).hexdigest())

    def test_fabricated_report_claims_are_not_a_trusted_computation_chain(self):
        data = encode(base("F"))
        fake = {"input_sha256": hashlib.sha256(data).hexdigest(), "structure": "CONSISTENT", "authority": "none", "handling": "REQUIRE_REVIEW"}
        # Existing equality/digest operators cannot prove derivation from input.
        self.assertTrue(all(r["result"]["state"] == "PASS" for r in self.receipts(data, fake)))
        self.assertEqual(candidate.review_bytes(data)["handling"], "PRESERVE_UNKNOWN")
        # This demonstrated limit prohibits production evidence promotion.

    def test_report_and_record_are_not_existing_request_or_receipt(self):
        record = base()
        report = candidate.review_bytes(encode(record))
        for payload in (record, report):
            with self.assertRaises(EvaluationError):
                evaluate_contract(payload, registry=self.registry)
            with self.assertRaises(EvaluationError):
                validate_evaluation_receipt(payload, registry=self.registry)

    def test_unsupported_consumer_cannot_be_registered_by_name(self):
        payload = request("a" * 64, "nexus.validator.governance-assessment-offline", [check("shape", "CONSISTENT", "CONSISTENT")])
        with self.assertRaises(EvaluationError):
            evaluate_contract(payload, registry=self.registry)

    def test_applicability_null_unknown_and_deferred_cannot_map_to_boolean(self):
        for required in (None, "UNKNOWN", "DEFERRED", "NOT_APPLICABLE", 1):
            payload = request("a" * 64, "nexus.validator.schema", [check("shape", "CONSISTENT", "CONSISTENT")])
            payload["checks"][0]["required"] = required
            with self.subTest(required=required), self.assertRaises(EvaluationError):
                evaluate_contract(payload, registry=self.registry)

    def test_static_subject_cannot_satisfy_executed_artifact_requirement(self):
        payload = request("a" * 64, "nexus.validator.artifact-metadata", [check("shape", "CONSISTENT", "CONSISTENT")])
        receipt = evaluate_contract(payload, registry=self.registry)
        self.assertEqual(receipt["result"]["state"], "INVALID_REQUEST")
        self.assertIn("EXECUTED_SUBJECT_EVIDENCE_REQUIRED", receipt["result"]["reason_codes"])

    def test_more_than_sixteen_checks_cannot_be_silently_truncated(self):
        payload = request("a" * 64, "nexus.validator.schema", [check("check-" + str(i), True, True) for i in range(17)])
        with self.assertRaises(EvaluationError):
            evaluate_contract(payload, registry=self.registry)

    def test_digest_operator_cannot_be_sent_to_schema_validator(self):
        payload = request("a" * 64, "nexus.validator.schema", [check("digest", "a" * 64, operator="sha256_matches_subject")])
        receipt = evaluate_contract(payload, registry=self.registry)
        self.assertEqual(receipt["result"]["state"], "INVALID_REQUEST")

    def test_result_or_authority_substitution_cannot_revalidate_receipt(self):
        payload = request("a" * 64, "nexus.validator.schema", [check("shape", "INVALID", "CONSISTENT")])
        original = evaluate_contract(payload, registry=self.registry)
        for key in ("result", "authority"):
            forged = copy.deepcopy(original)
            if key == "result":
                forged[key]["state"] = "PASS"
            else:
                forged[key]["execution_authority"] = "granted"
            with self.subTest(key=key), self.assertRaises(EvaluationError):
                validate_evaluation_receipt(forged, registry=self.registry)


if __name__ == "__main__":
    unittest.main()
