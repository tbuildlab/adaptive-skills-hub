"""Adversarial synthetic pairing tests; never authenticate the underlying task."""
import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from prototypes.governance_advisory_traceability_v1 import review_pair
from tests.test_governance_assessment_offline import CORPUS, base, candidate, encode


def serialized(report):
    return (json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


class AdvisoryTraceabilityTests(unittest.TestCase):
    def compare(self, data, derived):
        result = review_pair(data, derived)
        self.assertEqual(result["authority"], "none")
        self.assertIs(result["dispatch_requested"], False)
        self.assertEqual(result["source_evidence_status"], "UNVERIFIED")
        self.assertEqual(result["selection_completeness"], "UNVERIFIED")
        return result

    def test_entire_corpus_matches_without_promoting_any_original_handling(self):
        for case in CORPUS["cases"]:
            with self.subTest(case=case["id"]):
                data = encode(case["record"])
                report = candidate.review_bytes(data)
                result = self.compare(data, serialized(report))
                self.assertEqual(result["comparison"], "MATCH")
                self.assertEqual(result["recomputed_report"], report)
                self.assertEqual(report["handling"], case["expected_offline"])
                self.assertEqual(report["input_sha256"], hashlib.sha256(data).hexdigest())
                self.assertEqual(result["declared_check_count"], len(case["record"]["checks"]) if report["structure"] == "CONSISTENT" else None)

    def test_fake_report_from_compatibility_gap_is_rejected_as_inconsistent(self):
        data = encode(base("F"))
        fake = {"input_sha256": hashlib.sha256(data).hexdigest(), "structure": "CONSISTENT", "authority": "none", "handling": "REQUIRE_REVIEW"}
        result = self.compare(data, serialized(fake))
        self.assertEqual(result["comparison"], "MISMATCH")
        self.assertEqual(result["recomputed_report"]["handling"], "PRESERVE_UNKNOWN")
        self.assertTrue(result["recomputed_report"]["unresolved_required_checks"])

    def test_hand_constructed_identical_report_is_not_producer_attestation(self):
        data = encode(base("F"))
        supplied = serialized(copy.deepcopy(candidate.review_bytes(data)))
        result = self.compare(data, supplied)
        self.assertEqual(result["comparison"], "MATCH")
        self.assertEqual(result["proof_scope"], "recomputed_offline_report_matches_supplied_bytes_only")
        self.assertNotIn("producer_verified", result)
        self.assertEqual(result["recomputed_report"]["handling"], "PRESERVE_UNKNOWN")

    def test_stale_modified_and_reordered_sources_cannot_reuse_old_report(self):
        record = base("F")
        original = encode(record)
        derived = serialized(candidate.review_bytes(original))
        reordered = copy.deepcopy(record)
        reordered["checks"].reverse()
        changed = copy.deepcopy(record)
        changed["purpose"] = "Different scope supplied; not implicitly accepted."
        for data in (original + b" ", encode(reordered), encode(changed)):
            with self.subTest(digest=hashlib.sha256(data).hexdigest()):
                result = self.compare(data, derived)
                self.assertEqual(result["comparison"], "MISMATCH")
                self.assertEqual(result["recomputed_report"]["input_sha256"], hashlib.sha256(data).hexdigest())

    def test_unknown_dependency_projection_or_authority_tampering_mismatches(self):
        data = encode(base("F"))
        report = candidate.review_bytes(data)
        mutations = {
            "authority": "granted", "dispatch_requested": True,
            "unresolved_required_checks": [], "handling": "REQUIRE_REVIEW",
            "unverified_pass_claims": [],
        }
        for name, value in mutations.items():
            bad = copy.deepcopy(report)
            bad[name] = value
            with self.subTest(field=name):
                self.assertEqual(self.compare(data, serialized(bad))["comparison"], "MISMATCH")

    def test_capability_gaps_and_original_failure_survive_matching(self):
        for letter, projection in (("G", "unresolved_required_checks"), ("D", "declared_fail_checks")):
            data = encode(base(letter))
            report = candidate.review_bytes(data)
            result = self.compare(data, serialized(report))
            self.assertEqual(result["comparison"], "MATCH")
            self.assertEqual(result["recomputed_report"], report)
            self.assertTrue(result["recomputed_report"][projection])

    def test_invalid_and_unsupported_source_matching_never_becomes_valid(self):
        record = base()
        record["schema_version"] = "2.0"
        for data in (b"{", b"\xff", encode(record)):
            result = self.compare(data, serialized(candidate.review_bytes(data)))
            self.assertEqual(result["comparison"], "MATCH")
            self.assertEqual(result["recomputed_report"]["handling"], "REJECT_RECORD")
            self.assertIsNone(result["declared_check_count"])

    def test_empty_check_list_does_not_establish_complete_coverage(self):
        record = base()
        record["checks"] = []
        data = encode(record)
        result = self.compare(data, serialized(candidate.review_bytes(data)))
        self.assertEqual(result["comparison"], "MATCH")
        self.assertEqual(result["declared_check_count"], 0)
        self.assertEqual(result["selection_completeness"], "UNVERIFIED")
        self.assertEqual(result["recomputed_report"]["handling"], "REQUIRE_REVIEW")

    def test_noncanonical_duplicate_missing_extra_and_future_result_bytes_mismatch(self):
        data = encode(base())
        report = candidate.review_bytes(data)
        normal = serialized(report)
        missing = copy.deepcopy(report)
        missing.pop("authority")
        extra = {**report, "accepted": True}
        duplicates = normal.replace(b'"authority":"none"', b'"authority":"granted","authority":"none"')
        for supplied in (normal.rstrip(), b" " + normal, b"\xef\xbb\xbf" + normal, duplicates, serialized(missing), serialized(extra), b"{", b"\xff"):
            with self.subTest(size=len(supplied)):
                self.assertEqual(self.compare(data, supplied)["comparison"], "MISMATCH")

    def test_wrong_type_or_oversize_has_no_inspection_hash_echo_or_callbacks(self):
        class Hostile:
            def __len__(self):
                raise AssertionError("input callback")

            def __eq__(self, other):
                raise AssertionError("input callback")

        large = b" " * (candidate.MAX_BYTES + 1)
        for source, derived in ((Hostile(), b"{}"), (b"{}", Hostile()), (bytearray(b"{}"), b"{}"), (large, b"{}"), (b"{}", large)):
            result = self.compare(source, derived)
            self.assertEqual(result["comparison"], "INVALID_INPUT")
            self.assertIsNone(result["recomputed_report"])
            self.assertIsNone(result["declared_check_count"])

    def test_deterministic_repeated_pair_preserves_input_bytes(self):
        data = encode(base("F"))
        derived = serialized(candidate.review_bytes(data))
        before = (bytes(data), bytes(derived))
        self.assertEqual(self.compare(data, derived), self.compare(data, derived))
        self.assertEqual((data, derived), before)

    def test_no_locator_environment_access_or_raw_input_echo(self):
        record = base()
        record["purpose"] = "DO_NOT_ECHO_SOURCE_SENTINEL"
        record["references"][0]["locator"] = "https://invalid.example/DO_NOT_FETCH"
        data = encode(record)
        derived = serialized(candidate.review_bytes(data))
        with patch("builtins.open", side_effect=AssertionError("I/O")), patch.object(Path, "open", side_effect=AssertionError("I/O")), patch.object(os, "getenv", side_effect=AssertionError("environment")):
            result = self.compare(data, derived)
        self.assertEqual(result["comparison"], "MATCH")
        output = json.dumps(result)
        self.assertNotIn("SENTINEL", output)
        self.assertNotIn("DO_NOT_FETCH", output)
        mismatched = self.compare(data, b"DO_NOT_ECHO_DERIVED_SENTINEL")
        self.assertNotIn("SENTINEL", json.dumps(mismatched))


if __name__ == "__main__":
    unittest.main()
