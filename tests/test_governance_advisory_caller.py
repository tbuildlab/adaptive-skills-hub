"""Bounded synthetic tests of the existing CLI handoff, never source truth."""
import builtins
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from ash.common import sha256_text
from ash.v2 import ContextItem, ProjectContext, plan_task, validate_plan
from prototypes.governance_assessment_offline_v1 import review_bytes
from scripts import hub
from tests.test_governance_assessment_offline import CORPUS, base, encode


class GovernanceAdvisoryCallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def source_plan(self, data=None):
        data = encode(base()) if data is None else data
        content = data.decode("utf-8")
        item = ContextItem("assessment.json", "explicit_task_file", "project_evidence",
                           sha256_text(content), len(data), "explicitly named by task", content)
        context = ProjectContext(str(self.root), items=[item])
        return plan_task("Review assessment.json", {"skills": [], "agents": []}, self.root,
                         context_reader=lambda *args, **kwargs: context)

    def advice(self, plan, selector="assessment.json"):
        validation = validate_plan(plan)
        before = copy.deepcopy(plan.to_dict())
        original = hub._plan_handoff(plan, [], validation, self.root)
        result = hub._plan_handoff(plan, [], validation, self.root,
                                   governance_advisory_context=selector)
        advice = result.pop("governance_advisory")
        self.assertEqual(result, original)
        self.assertEqual(plan.to_dict(), before)
        self.assertEqual(advice["authority"], "none")
        self.assertIs(advice["dispatch_requested"], False)
        self.assertEqual(advice["handling"], "PRESERVE_UNKNOWN")
        self.assertEqual(advice["freshness"], "UNKNOWN")
        self.assertEqual(advice["source_evidence_status"], "UNVERIFIED")
        self.assertEqual(advice["selection_completeness"], "UNVERIFIED")
        self.assertEqual(advice["subject_scope_binding"], "UNVERIFIED")
        return advice

    def test_all_corpus_reports_match_without_changing_handling_or_legacy_handoff(self):
        for case in CORPUS["cases"]:
            with self.subTest(case=case["id"]):
                data = encode(case["record"])
                advice = self.advice(self.source_plan(data))
                self.assertEqual(advice["report"], review_bytes(data))
                self.assertEqual(advice["report"]["handling"], case["expected_offline"])
                self.assertEqual(advice["source_sha256"], advice["report"]["input_sha256"])

    def test_source_unknown_remains_unknown(self):
        report = self.advice(self.source_plan(encode(base("F"))))["report"]
        self.assertEqual(report["handling"], "PRESERVE_UNKNOWN")
        self.assertTrue(report["unresolved_required_checks"])

    def test_missing_dependency_is_rejected_not_passed(self):
        record = base()
        record["checks"][0]["requires"] = ["absent"]
        report = self.advice(self.source_plan(encode(record)))["report"]
        self.assertEqual(report["handling"], "REJECT_RECORD")
        self.assertEqual(report["diagnostics"][0]["code"], "UNRESOLVED_REFERENCE")

    def test_declared_pass_never_grants_or_changes_plan_validation(self):
        advice = self.advice(self.source_plan())
        self.assertTrue(advice["report"]["unverified_pass_claims"])
        self.assertEqual(advice["report"]["handling"], "REQUIRE_REVIEW")
        self.assertEqual(advice["report"]["authority"], "none")

    def test_callable_does_not_imply_execution_or_application(self):
        report = self.advice(self.source_plan(encode(base("G"))))["report"]
        self.assertEqual(report, review_bytes(encode(base("G"))))
        self.assertTrue(report["unresolved_required_checks"])
        self.assertIn("UNKNOWN", [check["outcome"] for check in report["declared_checks"]])

    def test_executed_does_not_imply_applied(self):
        record = base("G")
        dims = []
        for check in record["checks"]:
            if check.get("capability", {}).get("dimension") == "EXECUTED":
                check["outcome"]["state"] = "PASS"
                check["outcome"]["evidence_refs"] = [check["capability"]["ref"]]
            if check.get("capability", {}).get("dimension") == "APPLIED":
                check["outcome"]["state"] = "UNKNOWN"
                dims.append(record["checks"].index(check))
        self.assertTrue(dims)
        report = self.advice(self.source_plan(encode(record)))["report"]
        self.assertTrue(all(report["declared_checks"][i]["outcome"] == "UNKNOWN" for i in dims))

    def test_effect_checkpoint_does_not_settle_unresolved_effect(self):
        record = base("F")
        before = copy.deepcopy(record)
        report = self.advice(self.source_plan(encode(record)))["report"]
        self.assertEqual(report["handling"], "PRESERVE_UNKNOWN")
        self.assertTrue(report["unresolved_required_checks"])
        self.assertEqual(record, before)

    def test_malformed_unsupported_and_missing_reference_fail_safely(self):
        unsupported = base()
        unsupported["schema_version"] = "2.0"
        missing = base()
        missing["checks"][0]["outcome"]["evidence_refs"] = ["absent"]
        for data in (b"{", encode(unsupported), encode(missing)):
            with self.subTest(data_length=len(data)):
                self.assertEqual(self.advice(self.source_plan(data))["report"]["handling"], "REJECT_RECORD")

    def test_context_binding_mismatch_and_absent_source_are_not_evaluated(self):
        for change in ("bytes", "sha256", "content", "absent", "duplicate"):
            with self.subTest(change=change):
                plan = self.source_plan()
                item = plan.project_context.items[0]
                if change == "bytes":
                    item.bytes += 1
                elif change == "sha256":
                    item.sha256 = "a" * 64
                elif change == "content":
                    item.content += " "
                elif change == "absent":
                    plan.project_context.items.clear()
                else:
                    plan.project_context.items.append(copy.deepcopy(item))
                with patch("prototypes.governance_assessment_offline_v1.review_bytes") as evaluator:
                    self.assertIsNone(self.advice(plan)["report"])
                    evaluator.assert_not_called()

    def test_stale_claims_and_captured_old_file_cannot_gain_freshness(self):
        record = base()
        for ref in record["references"]:
            ref["captured_at"] = "2000-01-01"
            ref["valid_until"] = "2000-01-02"
        data = encode(record)
        plan = self.source_plan(data)
        (self.root / "assessment.json").write_bytes(b"new unrelated bytes")
        advice = self.advice(plan)
        self.assertEqual(advice["report"], review_bytes(data))
        self.assertEqual(advice["freshness"], "UNKNOWN")
        self.assertEqual(advice["binding_scope"], "captured_project_context_bytes_only")

    def test_noncanonical_selection_and_governing_file_not_used(self):
        for value in ("../assessment.json", "/assessment.json", "C:/assessment.json",
                      "./assessment.json", "assessment\\x.json", "a//b.json", "", "x\n"):
            with self.subTest(selector=value):
                self.assertIsNone(self.advice(self.source_plan(), value)["report"])
        plan = self.source_plan()
        plan.project_context.items[0].kind = "project_rule"
        self.assertIsNone(self.advice(plan)["report"])

    def test_invalid_capture_envelopes_do_not_invoke_evaluator(self):
        for value in (None, "\ud800", "x" * 1_048_577):
            with self.subTest(value_type=type(value).__name__):
                plan = self.source_plan()
                plan.project_context.items[0].content = value
                with patch("prototypes.governance_assessment_offline_v1.review_bytes") as evaluator:
                    self.assertIsNone(self.advice(plan)["report"])
                    evaluator.assert_not_called()
        plan = self.source_plan()
        plan.project_context.items[0].bytes = True
        self.assertIsNone(self.advice(plan)["report"])

    def test_evaluator_exception_is_content_free_and_never_pass(self):
        with patch("prototypes.governance_assessment_offline_v1.review_bytes",
                   side_effect=RuntimeError("SYNTHETIC_PRIVATE_MARKER")):
            advice = self.advice(self.source_plan())
        self.assertIsNone(advice["report"])
        self.assertEqual(advice["diagnostic"], "EVALUATOR_FAILED")
        self.assertNotIn("SYNTHETIC_PRIVATE_MARKER", json.dumps(advice))

    def test_unavailable_and_import_failure_are_safe(self):
        original_import = builtins.__import__
        for error in (ImportError, RuntimeError):
            def unavailable(name, *args, **kwargs):
                if name == "prototypes.governance_assessment_offline_v1":
                    raise error("SYNTHETIC_PRIVATE_MARKER")
                return original_import(name, *args, **kwargs)
            with self.subTest(error=error.__name__), patch("builtins.__import__", side_effect=unavailable):
                advice = self.advice(self.source_plan())
                self.assertIsNone(advice["report"])
                self.assertNotIn("SYNTHETIC_PRIVATE_MARKER", json.dumps(advice))

    def test_invalid_evaluator_result_does_not_gain_authority(self):
        for update in ({"authority": "owner"}, {"dispatch_requested": True},
                       {"handling": "PASS"}, {"input_sha256": "a" * 64}):
            report = review_bytes(encode(base()))
            report.update(update)
            with self.subTest(update=update), patch("prototypes.governance_assessment_offline_v1.review_bytes", return_value=report):
                advice = self.advice(self.source_plan())
                self.assertIsNone(advice["report"])
                self.assertEqual(advice["diagnostic"], "EVALUATOR_RESULT_INVALID")

    def test_evaluator_output_schema_drift_is_not_forwarded(self):
        for change in ("extra", "missing", "unsupported"):
            report = review_bytes(encode(base()))
            if change == "extra":
                report["raw_source"] = "SYNTHETIC_PRIVATE_MARKER"
            elif change == "missing":
                report.pop("unverified_pass_claims")
            else:
                report["structure"] = "NEW_VERSION"
            with self.subTest(change=change), patch("prototypes.governance_assessment_offline_v1.review_bytes", return_value=report):
                advice = self.advice(self.source_plan())
                self.assertIsNone(advice["report"])
                self.assertEqual(advice["diagnostic"], "EVALUATOR_RESULT_INVALID")
                self.assertNotIn("SYNTHETIC_PRIVATE_MARKER", json.dumps(advice))

    def test_advisory_is_pure_deterministic_and_redacted(self):
        plan = self.source_plan()
        with patch.object(Path, "read_bytes", side_effect=AssertionError("unexpected file read")), \
             patch.object(Path, "write_text", side_effect=AssertionError("unexpected file write")), \
             patch.object(Path, "resolve", side_effect=AssertionError("unexpected resolution")):
            first = self.advice(plan)
            self.assertEqual(first, self.advice(plan))
        rendered = json.dumps(first)
        self.assertNotIn("assessment.json", rendered)
        for text in ("criterion", "locator", "configuration_id", "record_id"):
            self.assertNotIn(text, rendered)

    def test_disable_does_not_invoke_evaluator_or_change_required_validation(self):
        plan = self.source_plan(encode(base("F")))
        validation = validate_plan(plan)
        with patch("prototypes.governance_assessment_offline_v1.review_bytes") as evaluator:
            result = hub._plan_handoff(plan, [], validation, self.root)
            evaluator.assert_not_called()
        self.assertNotIn("governance_advisory", result)
        self.assertEqual(result["plan_validation"], validation)
        self.assertEqual(result["fallback"], plan.fallback)

    def cli(self, *extra):
        argv = ["hub.py", "plan", "Review assessment.json", "--project", str(self.root), *extra]
        stream = io.StringIO()
        with patch.object(sys, "argv", argv), patch.object(hub, "ROOT", self.root), \
             patch.object(hub, "_v2_catalog", return_value={"skills": [], "agents": []}), \
             patch.object(hub, "_sources", return_value=[]), \
             patch.object(hub, "execute_route", side_effect=AssertionError("execution forbidden")), \
             patch("sys.stdout", stream):
            code = hub.main()
        return code, json.loads(stream.getvalue().split("Handoff:\n", 1)[1])

    def test_actual_cli_explicit_context_and_disable_are_stateless(self):
        (self.root / "assessment.json").write_bytes(encode(base("F")))
        files_before = sorted(self.root.iterdir())
        code, enabled = self.cli("--handoff", "--governance-advisory-context", "assessment.json")
        self.assertEqual(code, 0)
        self.assertEqual(enabled["governance_advisory"]["report"]["handling"], "PRESERVE_UNKNOWN")
        _, disabled = self.cli("--handoff")
        enabled.pop("governance_advisory")
        self.assertEqual(enabled, disabled)
        self.assertEqual(sorted(self.root.iterdir()), files_before)
        self.assertFalse((self.root / "state").exists())

    def test_cli_option_without_handoff_rejected_before_acquisition(self):
        with patch.object(sys, "argv", ["hub.py", "plan", "Review", "--governance-advisory-context", "assessment.json"]), \
             patch.object(hub, "_v2_catalog") as catalog, patch("sys.stderr", io.StringIO()):
            with self.assertRaises(SystemExit) as exit_info:
                hub.main()
            self.assertEqual(exit_info.exception.code, 2)
            catalog.assert_not_called()

    def test_existing_file_not_named_in_task_is_not_automatically_read(self):
        (self.root / "assessment.json").write_bytes(encode(base()))
        stream = io.StringIO()
        argv = ["hub.py", "plan", "Review project", "--project", str(self.root),
                "--handoff", "--governance-advisory-context", "assessment.json"]
        with patch.object(sys, "argv", argv), patch.object(hub, "ROOT", self.root), \
             patch.object(hub, "_v2_catalog", return_value={"skills": [], "agents": []}), \
             patch.object(hub, "_sources", return_value=[]), patch("sys.stdout", stream):
            self.assertEqual(hub.main(), 0)
        advice = json.loads(stream.getvalue().split("Handoff:\n", 1)[1])["governance_advisory"]
        self.assertEqual(advice["diagnostic"], "SOURCE_MISSING_OR_AMBIGUOUS")
        self.assertIsNone(advice["report"])
        self.assertIsNone(advice["source_sha256"])


if __name__ == "__main__":
    unittest.main()
