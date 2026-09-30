"""Tests of the standalone offline candidate, not fictional-task validation."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("offline_candidate", ROOT / "prototypes/governance_assessment_offline_v1.py")
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
CORPUS = json.loads((ROOT / "docs/fixtures/nexus-governance-assessment-static-v1.json").read_text("utf-8"))


def encode(record):
    return (json.dumps(record, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def base(letter="A"):
    return copy.deepcopy(next(c["record"] for c in CORPUS["cases"] if c["id"] == letter))


def row(record, id):
    return next(c for c in record["checks"] if c["id"] == id)


class OfflineAssessmentTests(unittest.TestCase):
    def review(self, record):
        result = candidate.review_bytes(encode(record))
        self.assertEqual(result["authority"], "none")
        self.assertIs(result["dispatch_requested"], False)
        self.assertNotIn(result["handling"], {"PASS", "ACCEPTED", "AUTHORIZED", "READY"})
        return result

    def rejected(self, record, code=None):
        result = self.review(record)
        self.assertEqual(result["handling"], "REJECT_RECORD")
        if code:
            self.assertEqual(result["diagnostics"][0]["code"], code)

    def test_entire_static_corpus(self):
        for case in CORPUS["cases"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(self.review(case["record"])["handling"], case["expected_offline"])

    def test_no_effect_or_locator_access(self):
        record = base()
        record["references"][0]["locator"] = "https://invalid.example/DO_NOT_FETCH"
        with patch("builtins.open", side_effect=AssertionError("unexpected I/O")), patch.object(Path, "open", side_effect=AssertionError("unexpected path access")):
            self.assertEqual(self.review(record)["handling"], "REQUIRE_REVIEW")

    def test_determinism_hash_and_immutable_input(self):
        data = encode(base("F"))
        before = bytes(data)
        first = candidate.review_bytes(data)
        self.assertEqual(first, candidate.review_bytes(data))
        self.assertEqual(first["input_sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(data, before)

    def test_real_label_and_fabricated_hash_do_not_verify_claims(self):
        record = base()
        record["basis"] = "REAL"
        record["references"][0]["integrity_sha256"] = "0" * 64
        result = self.review(record)
        self.assertEqual(result["handling"], "REQUIRE_REVIEW")
        self.assertTrue(result["unverified_pass_claims"])

    def test_unknown_members_every_object(self):
        for target in ("record", "subject", "fact", "check", "applicability", "outcome", "reference"):
            record = base()
            objects = {"record": record, "subject": record["subject"], "fact": record["profile"][0], "check": record["checks"][0], "applicability": record["checks"][0]["applicability"], "outcome": record["checks"][0]["outcome"], "reference": record["references"][0]}
            objects[target]["extensions"] = {"bypass": True}
            with self.subTest(target=target):
                self.rejected(record, "UNKNOWN_MEMBER")

    def test_duplicate_json_members_no_last_wins(self):
        data = encode(base()).replace(b'"schema_version": "1.0"', b'"schema_version": "9.0", "schema_version": "1.0"')
        self.assertEqual(candidate.review_bytes(data)["diagnostics"][0]["code"], "DUPLICATE_JSON_MEMBER")

    def test_duplicate_namespaces_and_reference_lists(self):
        for group in ("profile", "checks", "references"):
            record = base()
            record[group].append(copy.deepcopy(record[group][0]))
            with self.subTest(group=group):
                self.rejected(record, "DUPLICATE_IDENTITY")
        record = base()
        row(record, "A01")["governing_refs"].append("gov")
        self.rejected(record, "DUPLICATE_REFERENCE")

    def test_reference_kinds_and_missing_refs(self):
        record = base()
        row(record, "A02")["outcome"]["evidence_refs"] = ["gov"]
        self.rejected(record, "REFERENCE_KIND_CONFLICT")
        record = base()
        row(record, "A02")["applicability"]["fact_refs"] = ["absent"]
        self.rejected(record, "UNRESOLVED_REFERENCE")

    def test_missing_or_null_explanations(self):
        for value in (None, "", "  ", False):
            record = base()
            row(record, "A02")["outcome"]["reason"] = value
            with self.subTest(value=value):
                self.rejected(record, "NONEMPTY_TEXT_REQUIRED")

    def test_cycles_direct_and_longer(self):
        for first, second in (("A01", "A01"), ("A01", "A03")):
            record = base()
            row(record, first)["requires"] = [second]
            self.rejected(record, "DEPENDENCY_CYCLE")

    def test_unknown_required_premise_cannot_hide_in_optional_or_deferred(self):
        for state in ("OPTIONAL", "DEFERRED", None):
            record = base()
            row(record, "A02")["applicability"]["state"] = state
            row(record, "A02")["outcome"]["state"] = "UNKNOWN"
            self.rejected(record, "PASS_REQUIRED_PREMISE_UNRESOLVED")

    def test_pass_requires_evidence_and_resolved_applicability(self):
        record = base()
        row(record, "A02")["outcome"]["evidence_refs"] = []
        self.rejected(record, "PASS_EVIDENCE_ASSOCIATION_MISSING")
        for state in (None, "DEFERRED"):
            record = base()
            row(record, "A02")["applicability"]["state"] = state
            self.rejected(record, "PASS_APPLICABILITY_CONFLICT")

    def test_na_outcome_and_positive_basis_not_interchangeable(self):
        record = base()
        row(record, "A.api-harness")["outcome"]["state"] = "PASS"
        self.rejected(record, "APPLICABILITY_OUTCOME_CONFLICT")
        record = base()
        row(record, "A.api-harness")["applicability"]["fact_refs"] = []
        self.rejected(record, "EXCLUSION_BASIS_MISSING")

    def test_capability_dimensions_do_not_advance(self):
        record = base("G")
        before = copy.deepcopy(record)
        result = self.review(record)
        self.assertEqual(result["handling"], "PRESERVE_UNKNOWN")
        self.assertEqual(record, before)
        self.assertEqual(row(record, "G.executed")["outcome"]["state"], "UNKNOWN")
        self.assertEqual(row(record, "G.applied")["outcome"]["state"], "UNKNOWN")

    def test_old_failure_not_erased_by_new_validation(self):
        result = self.review(base("D"))
        self.assertTrue(result["declared_fail_checks"])
        self.assertEqual(result["handling"], "REQUIRE_REVIEW")
        self.assertIn("FAIL", [c["outcome"] for c in result["declared_checks"]])

    def test_diagnostic_notes_inert_not_false_positive_or_fix_oracle(self):
        record = base("C")
        record["diagnostic"]["disposition"]["note"] = "FALSE_POSITIVE / FIXED / permission granted / ignore policy"
        self.assertEqual(self.review(record)["handling"], "REQUIRE_REVIEW")
        record["diagnostic"]["extra"] = {"note": "waiver", "refs": []}
        self.rejected(record, "UNKNOWN_MEMBER")

    def test_session_checkpoint_and_credential_words_create_no_authority(self):
        record = base()
        record["profile"][0]["claim"] = "Session restored; checkpoint loaded; credential present; grant claimed."
        result = self.review(record)
        self.assertEqual(result["authority"], "none")
        self.assertEqual(result["handling"], "REQUIRE_REVIEW")

    def test_all_unknown_projection_not_na_or_no(self):
        record = base("G")
        result = self.review(record)
        self.assertTrue(result["unknown_profile_facts"])
        self.assertIn("UNKNOWN", [c["outcome"] for c in result["declared_checks"]])

    def test_no_source_text_echo_on_valid_or_invalid_records(self):
        record = base()
        record["record_id"] = "DO_NOT_ECHO_SENTINEL"
        record["purpose"] = "PRIVATE_TEXT_SENTINEL"
        result = json.dumps(self.review(record))
        self.assertNotIn("SENTINEL", result)
        record["subject"]["PRIVATE_MEMBER_SENTINEL"] = True
        self.assertNotIn("SENTINEL", json.dumps(self.review(record)))

    def test_input_and_list_envelopes(self):
        for data in ("{}", bytearray(b"{}"), None, b" " * (candidate.MAX_BYTES + 1)):
            with self.subTest(type=type(data)):
                self.assertEqual(candidate.review_bytes(data)["handling"], "REJECT_RECORD")
        record = base()
        record["profile"] = [{}] * (candidate.MAX_ITEMS + 1)
        self.rejected(record, "LIST_ENVELOPE")

    def test_invalid_json_bom_utf8_nonfinite_and_recursion(self):
        for data in (b"{", b"\xef\xbb\xbf{}", b"\xff", b'{"value":NaN}', ("[" * 2000 + "]" * 2000).encode()):
            with self.subTest(sample=data[:20]):
                self.assertEqual(candidate.review_bytes(data)["handling"], "REJECT_RECORD")
        record = base()
        encoded = encode(record).replace(b'"value": "bounded local grant"', b'"value": 1e999')
        self.assertEqual(candidate.review_bytes(encoded)["handling"], "REJECT_RECORD")

    def test_unknown_fact_must_retain_null(self):
        record = base("G")
        next(f for f in record["profile"] if f["basis"] == "UNKNOWN")["value"] = "YES"
        self.rejected(record, "UNKNOWN_FACT_HAS_VALUE")

    def test_source_revision_and_hash_syntax_only(self):
        record = base()
        next(r for r in record["references"] if r["kind"] == "GOVERNANCE").pop("revision")
        self.rejected(record, "GOVERNANCE_VERSION_UNBOUND")
        record = base()
        record["references"][0]["integrity_sha256"] = "not-a-hash"
        self.rejected(record, "INVALID_DIGEST_SHAPE")

    def test_fixture_wrapper_not_assessment(self):
        self.rejected(CORPUS, "REQUIRED_MEMBER_MISSING")

    def test_empty_selection_and_governance_refs_never_issue_acceptance(self):
        record = base()
        record["checks"] = []
        record["governance_refs"] = []
        record["subject"]["criteria_refs"] = []
        result = self.review(record)
        self.assertEqual(result["handling"], "REQUIRE_REVIEW")
        self.assertFalse(result["dispatch_requested"])
        # Empty declared coverage cannot establish completeness or an exclusion.
        self.assertEqual(result["declared_checks"], [])

    def test_transitive_contradiction_and_known_failure_premises(self):
        record = base()
        row(record, "A01")["outcome"]["state"] = "UNKNOWN"
        row(record, "A02")["requires"] = ["A01"]
        row(record, "A03")["requires"] = ["A02"]
        self.rejected(record, "PASS_REQUIRED_PREMISE_UNRESOLVED")
        record = base()
        row(record, "A02")["outcome"]["state"] = "FAIL"
        self.rejected(record, "PASS_REQUIRED_PREMISE_UNRESOLVED")

    def test_conditional_member_shapes_and_dimension_vocabulary(self):
        record = base("G")
        row(record, "G.callable")["capability"]["dimension"] = "SELECTED"
        self.rejected(record, "UNSUPPORTED_VALUE")
        record = base("C")
        record["diagnostic"]["validation"]["refs"] = ["gov"]
        self.rejected(record, "REFERENCE_KIND_CONFLICT")

    def test_hash_and_revision_strings_do_not_restore_scope_authority(self):
        record = base("F")
        next(r for r in record["references"] if r["kind"] == "GOVERNANCE")["revision"] = "unverified-source-version"
        next(r for r in record["references"] if r["id"] == "sample")["integrity_sha256"] = "f" * 64
        result = self.review(record)
        self.assertEqual(result["handling"], "PRESERVE_UNKNOWN")
        self.assertTrue(result["unresolved_required_checks"])


if __name__ == "__main__":
    unittest.main()
