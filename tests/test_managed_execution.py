"""Deterministic contract fixtures; never provider qualification evidence."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from ash.core_capabilities import ScopeError, sha
from ash.managed_execution import (ExecutionError, cancel_execution, execution_summary,
    export_handoff, parse_receipt, prepare_execution, read_execution, receive_execution,
    retry_execution, route_backend)


class ManagedExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "project"
        self.project.mkdir()
        (self.project / "README.md").write_bytes(b"Approved non-secret fixture.\n")
        self.output = self.base / "download"
        self.output.mkdir()
        self.data = b"Expected artifact.\n"
        (self.output / "report.txt").write_bytes(self.data)
        self.directory = self.base / "execution"
        self.spec = {"schema": "nexus.execution.spec.v1", "category": "coding", "files": ["README.md"],
                     "effects": ["output_artifacts"], "artifacts": [{"path": "report.txt", "verification": "sha256",
                     "expected_sha256": sha(self.data)}], "ttl_seconds": 3600}

    def prepare(self):
        return prepare_execution("Create the specified report artifact.", self.project, self.spec, self.directory)

    def handoff(self):
        state = self.prepare()
        return export_handoff(self.directory, state["request_digest"])

    def receipt(self, state, **updates):
        result = {"schema": "nexus.execution.receipt.v1", "execution_id": "fixture-only-execution-1",
                  "backend_id": state["request"]["backend_id"], "task_id": state["request"]["task_id"],
                  "request_digest": state["request_digest"], "attempt": state["request"]["attempt"],
                  "start_status": "STARTED", "end_status": "completed", "artifacts": [{"path": "report.txt",
                  "sha256": sha(self.data), "bytes": len(self.data)}], "changed_files": [], "checks": ["fixture-check"],
                  "exit_status": 0, "warnings": [], "ambiguity": False, "continuation_reference": None,
                  "provider_metadata": {}, "usage": None, "failure": None, "cancel_phase": None,
                  "actual_effects": ["output_artifacts"]}
        result.update(updates)
        return result

    def receive(self, value):
        path = self.base / "receipt.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return receive_execution(self.directory, path, self.output)

    def failure(self, state, kind="provider_unavailable", **updates):
        fields = {"start_status": "NOT_STARTED", "end_status": "failed", "artifacts": [],
                  "actual_effects": [], "exit_status": None, "failure": {"kind": kind, "no_effects_confirmed": True}}
        return self.receipt(state, **{**fields, **updates})

    def test_route_local_supported_profile(self):
        self.assertEqual(route_backend("local", ["output_artifacts"], local_supported=True)["backend"], "LOCAL_CORE")

    def test_route_reviewed_managed_candidate(self):
        self.assertEqual(route_backend("coding", ["output_artifacts"], managed_supported=True)["backend"], "OPENAI_MANAGED")

    def test_current_coding_browser_app_use_handoff(self):
        for category in ("coding", "browser", "app"):
            self.assertEqual(route_backend(category, ["output_artifacts"], host_supported=True)["backend"], "HOST_HANDOFF")

    def test_unsupported_does_not_invent_local_fallback(self):
        self.assertEqual(route_backend("coding", ["output_artifacts"], local_supported=True)["backend"], "UNSUPPORTED")
        self.assertEqual(route_backend("unknown", ["output_artifacts"], host_supported=True)["backend"], "UNSUPPORTED")

    def test_owner_boundaries_override_every_available_backend(self):
        for effect in ("credentials", "payments", "destructive", "account_creation", "deployment", "elevation", "irreversible", "high_cost", "unsupported_authority"):
            self.assertEqual(route_backend("coding", [effect], local_supported=True, managed_supported=True, host_supported=True)["backend"], "OWNER_BOUNDARY")

    def test_effect_class_unsupported(self):
        self.assertEqual(route_backend("coding", ["arbitrary_filesystem"], host_supported=True)["backend"], "UNSUPPORTED")

    def test_prepare_no_effects_and_bound_contract(self):
        state = self.prepare()
        self.assertEqual(state["status"], "PREPARED")
        self.assertEqual(state["request"]["project_scope"]["inputs"], {"README.md": sha(b"Approved non-secret fixture.\n")})
        self.assertEqual(state["request"]["capability"]["version"], "1")
        self.assertFalse(state["request"]["budget"]["hard_financial_cap"])
        self.assertEqual(state["attempts"], 0)
        self.assertFalse((self.directory / "handoff-1.json").exists())

    def test_owner_boundary_does_not_read_declared_input(self):
        self.spec["effects"] = ["credentials"]
        self.spec["files"] = ["missing.txt"]
        state = self.prepare()
        self.assertEqual(state["status"], "BLOCKED")
        self.assertEqual(state["request"]["project_scope"]["inputs"], {})
        with self.assertRaises(ExecutionError):
            export_handoff(self.directory, state["request_digest"])

    def test_spec_unknown_keys_budget_and_duplicates_refused(self):
        original = copy.deepcopy(self.spec)
        for changes in ({"command": "run anything"}, {"ttl_seconds": True}, {"ttl_seconds": 86401}, {"files": ["README.md", "README.md"]}):
            self.spec = {**original, **changes}
            with self.subTest(changes=changes), self.assertRaises((ExecutionError, ScopeError)):
                self.prepare()
            self.assertFalse(self.directory.exists())

    def test_private_and_traversing_inputs_refused(self):
        for name in ("../README.md", "password.txt", ".env", "C:/temp/x", "README.md:ads", "CON", "a\\b"):
            self.spec["files"] = [name]
            with self.subTest(name=name), self.assertRaises((ExecutionError, ScopeError)):
                self.prepare()

    def test_git_baseline_drift_refuses_dispatch(self):
        with patch("ash.managed_execution._baseline", return_value="a" * 40):
            state = self.prepare()
        with patch("ash.managed_execution._baseline", return_value="b" * 40), self.assertRaises(ExecutionError):
            export_handoff(self.directory, state["request_digest"])

    def test_hardlinked_input_is_refused(self):
        os.link(self.project / "README.md", self.project / "second.md")
        with self.assertRaises(ScopeError):
            self.prepare()

    def test_hardlinked_artifact_is_not_accepted(self):
        state = self.handoff()
        os.link(self.output / "report.txt", self.output / "second.txt")
        final = self.receive(self.receipt(state))
        self.assertEqual(final["status"], "VERIFICATION_FAILED")

    def test_hardlinked_state_is_refused(self):
        self.prepare()
        os.link(self.directory / "execution.json", self.base / "ledger-copy.json")
        with self.assertRaises(ExecutionError):
            read_execution(self.directory)

    def test_overlapping_artifact_paths_refused_at_preparation(self):
        self.spec["artifacts"].append({"path": "report.txt/other.txt", "verification": "sha256", "expected_sha256": sha(self.data)})
        with self.assertRaises(ExecutionError):
            self.prepare()

    def test_concurrent_mutation_lock_refuses_handoff(self):
        from ash.core_host import LocalHookError, exclusive_run
        state = self.prepare()
        with exclusive_run(self.directory), self.assertRaises(LocalHookError):
            export_handoff(self.directory, state["request_digest"])

    def test_approval_does_not_mutate_when_missing_or_wrong(self):
        state = self.prepare()
        with self.assertRaises(ExecutionError):
            export_handoff(self.directory, "0" * 64)
        self.assertEqual(read_execution(self.directory), state)

    def test_input_drift_refuses_export(self):
        state = self.prepare()
        (self.project / "README.md").write_bytes(b"Drift")
        with self.assertRaises(ExecutionError):
            export_handoff(self.directory, state["request_digest"])

    def test_expiry_does_not_reset_on_resume(self):
        state = self.prepare()
        with patch("ash.managed_execution.time.time", return_value=state["request"]["expires_at"] + 1):
            with self.assertRaises(ExecutionError):
                export_handoff(self.directory, state["request_digest"])
        self.assertEqual(read_execution(self.directory)["attempts"], 0)

    def test_export_contains_only_declared_inputs_no_local_path(self):
        state = self.handoff()
        handoff = json.loads((self.directory / "handoff-1.json").read_text())
        self.assertEqual(handoff["inputs"], {"README.md": "Approved non-secret fixture.\n"})
        self.assertNotIn(str(self.project), json.dumps(handoff))
        self.assertFalse(handoff["provider_execution_started"])
        self.assertEqual(state["attempts"], 1)
        with self.assertRaises(ExecutionError):
            export_handoff(self.directory, state["request_digest"])

    def test_interrupted_export_intent_persists_and_cannot_replay(self):
        state = self.prepare()
        import ash.managed_execution as managed
        atomic = managed._atomic
        def fail_handoff(path, data):
            if path.name.startswith("handoff-"):
                raise OSError("fixture interrupted export")
            atomic(path, data)
        with patch.object(managed, "_atomic", side_effect=fail_handoff), self.assertRaises(OSError):
            export_handoff(self.directory, state["request_digest"])
        self.assertEqual(read_execution(self.directory)["status"], "HANDOFF_INTENT")
        with self.assertRaises(ExecutionError):
            export_handoff(self.directory, state["request_digest"])

    def test_receipt_binding_and_closed_fields(self):
        state = self.handoff()
        for field, value in (("task_id", "other"), ("backend_id", "other"), ("request_digest", "0" * 64), ("attempt", 2), ("attempt", True), ("unreviewed", True)):
            receipt = self.receipt(state, **{field: value})
            with self.subTest(field=field), self.assertRaises(ExecutionError):
                parse_receipt(receipt, state["request"], state["request_digest"])

    def test_duplicate_json_keys_refused(self):
        self.handoff()
        path = self.base / "receipt.json"
        path.write_text('{"schema":1,"schema":2}')
        with self.assertRaises((ScopeError, ExecutionError)):
            receive_execution(self.directory, path, self.output)

    def test_reported_effect_expansion_refused(self):
        state = self.handoff()
        for updates in ({"changed_files": ["source.py"]}, {"actual_effects": ["deployment"]}, {"provider_metadata": {"secret": "unsafe"}}):
            with self.subTest(updates=updates), self.assertRaises(ExecutionError):
                self.receive(self.receipt(state, **updates))

    def test_provider_success_then_independent_complete(self):
        state = self.handoff()
        final = self.receive(self.receipt(state))
        self.assertEqual(final["status"], "TASK_VERIFIED_COMPLETE")
        self.assertEqual(final["verification"], "EXPECTED_HASHES_PASSED")
        self.assertEqual((self.directory / "artifacts-1/report.txt").read_bytes(), self.data)
        self.assertEqual([e["status"] for e in final["events"]][-2:], ["EXECUTION_COMPLETED", "TASK_VERIFIED_COMPLETE"])
        self.assertEqual(execution_summary(final)["provider_provenance"], "HOST_REPORTED_UNAUTHENTICATED")

    def test_provider_hash_alone_cannot_equal_task_complete(self):
        state = self.handoff()
        unexpected = b"Self-consistent but wrong result"
        (self.output / "report.txt").write_bytes(unexpected)
        final = self.receive(self.receipt(state, artifacts=[{"path": "report.txt", "sha256": sha(unexpected), "bytes": len(unexpected)}]))
        self.assertEqual(final["status"], "VERIFICATION_FAILED")
        self.assertEqual(execution_summary(final)["FINAL_RESULT"], "NOT_COMPLETE")

    def test_owner_review_never_auto_completes(self):
        self.spec["artifacts"][0].update(verification="owner_review", expected_sha256=None)
        state = self.handoff()
        final = self.receive(self.receipt(state))
        self.assertEqual(final["status"], "VERIFICATION_REQUIRED")

    def test_missing_extra_warning_and_bad_artifact_hash_fail(self):
        for index, updates in enumerate(({"artifacts": []}, {"warnings": ["Uncertain output"]}, {"artifacts": [{"path": "report.txt", "sha256": "0" * 64, "bytes": len(self.data)}]}, {"actual_effects": []})):
            self.directory = self.base / f"execution-{index}"
            state = self.handoff()
            final = self.receive(self.receipt(state, **updates))
            self.assertEqual(final["status"], "VERIFICATION_FAILED")

    def test_completed_and_failed_receipt_consistency(self):
        state = self.handoff()
        for updates in ({"exit_status": True}, {"exit_status": 1}, {"start_status": "NOT_STARTED"}, {"end_status": "failed"}, {"cancel_phase": "EXECUTION_STOPPED"}, {"usage": {"input_tokens": -1, "output_tokens": 1}}):
            with self.subTest(updates=updates), self.assertRaises(ExecutionError):
                self.receive(self.receipt(state, **updates))

    def test_receipt_artifact_paths_and_byte_budget(self):
        state = self.handoff()
        for artifact in ({"path": "../x", "sha256": sha(self.data), "bytes": 1}, {"path": "report.txt", "sha256": sha(self.data), "bytes": 262145}):
            with self.subTest(artifact=artifact), self.assertRaises((ExecutionError, ScopeError)):
                self.receive(self.receipt(state, artifacts=[artifact]))

    def test_provider_ambiguity_cannot_retry_or_complete(self):
        state = self.handoff()
        final = self.receive(self.receipt(state, ambiguity=True))
        self.assertEqual(final["status"], "AMBIGUOUS")
        with self.assertRaises(ExecutionError):
            retry_execution(self.directory, final["request_digest"])

    def test_safe_preexecution_retry_requires_new_approval_and_preserves_expiry(self):
        state = self.handoff()
        self.receive(self.failure(state))
        retried = retry_execution(self.directory, state["request_digest"])
        self.assertEqual(retried["request"]["expires_at"], state["request"]["expires_at"])
        self.assertNotEqual(retried["request_digest"], state["request_digest"])
        with self.assertRaises(ExecutionError):
            export_handoff(self.directory, state["request_digest"])
        second = export_handoff(self.directory, retried["request_digest"])
        self.assertEqual(second["attempts"], 2)
        final = self.receive(self.failure(second))
        self.assertFalse(final["retry_eligible"])
        with self.assertRaises(ExecutionError):
            retry_execution(self.directory, final["request_digest"])

    def test_failure_classifications_not_blindly_retried(self):
        for index, kind in enumerate(("implementation", "wrong_capability", "missing_capability", "owner_boundary", "verification")):
            self.directory = self.base / f"execution-{index}"
            state = self.handoff()
            final = self.receive(self.failure(state, kind))
            self.assertFalse(final["retry_eligible"])

    def test_started_transient_failure_requires_manual_reconciliation(self):
        state = self.handoff()
        final = self.receive(self.failure(state, start_status="STARTED"))
        self.assertFalse(final["retry_eligible"])

    def test_cancel_request_not_provider_stop(self):
        self.handoff()
        state = cancel_execution(self.directory)
        self.assertEqual(state["status"], "CANCEL_REQUESTED")
        self.assertEqual(cancel_execution(self.directory), state)
        with self.assertRaises(ExecutionError):
            export_handoff(self.directory, state["request_digest"])

    def test_cancellation_distinct_phases_never_complete(self):
        state = self.handoff()
        cancel_execution(self.directory)
        for phase in ("PROVIDER_ACKNOWLEDGED", "EXECUTION_STOPPED", "RESULT_RECONCILED"):
            final = self.receive(self.receipt(state, end_status="cancelled", artifacts=[], actual_effects=[], exit_status=None, cancel_phase=phase))
            self.assertEqual(final["status"], phase)
            self.assertEqual(execution_summary(final)["FINAL_RESULT"], "NOT_COMPLETE")
        with self.assertRaises(ExecutionError):
            retry_execution(self.directory, final["request_digest"])

    def test_cancel_does_not_accept_late_success_as_completion(self):
        state = self.handoff()
        cancel_execution(self.directory)
        final = self.receive(self.receipt(state))
        self.assertEqual(final["status"], "CANCEL_REQUESTED")
        self.assertFalse((self.directory / "artifacts-1").exists())

    def test_cancel_ack_cannot_regress_or_change_execution_reference(self):
        state = self.handoff()
        cancel_execution(self.directory)
        value = self.receipt(state, end_status="cancelled", artifacts=[], actual_effects=[], exit_status=None, cancel_phase="PROVIDER_ACKNOWLEDGED")
        self.receive(value)
        with self.assertRaises(ExecutionError):
            self.receive(value)
        with self.assertRaises(ExecutionError):
            self.receive({**value, "cancel_phase": "EXECUTION_STOPPED", "execution_id": "other"})

    def test_resume_inspects_without_redispatch_and_replay_refused(self):
        state = self.handoff()
        self.assertEqual(read_execution(self.directory), state)
        value = self.receipt(state)
        final = self.receive(value)
        self.assertEqual(read_execution(self.directory), final)
        with self.assertRaises(ExecutionError):
            self.receive(value)

    def test_expired_receipt_can_reconcile_but_cannot_dispatch(self):
        state = self.handoff()
        with patch("ash.managed_execution.time.time", return_value=state["request"]["expires_at"] + 1):
            final = self.receive(self.receipt(state))
        self.assertEqual(final["status"], "TASK_VERIFIED_COMPLETE")

    def test_state_corruption_refuses_replay(self):
        self.prepare()
        path = self.directory / "execution.json"
        value = json.loads(path.read_text())
        value["payload"]["attempts"] = 0.5
        path.write_text(json.dumps(value))
        with self.assertRaises(ExecutionError):
            read_execution(self.directory)

    def test_cli_prepare_handoff_status_and_no_execution(self):
        request = self.base / "spec.json"
        request.write_text(json.dumps(self.spec))
        root = Path(__file__).resolve().parents[1]
        command = [sys.executable, str(root / "scripts/nexus.py")]
        result = subprocess.run(command + ["managed-plan", "Create the specified report artifact.", "--project", str(self.project), "--request", str(request), "--task-dir", str(self.directory)], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        view = json.loads(result.stdout)
        exported = subprocess.run(command + ["managed-handoff", str(self.directory), "--approve", view["APPROVAL"]], capture_output=True, text=True, timeout=20)
        self.assertEqual(exported.returncode, 0, exported.stderr)
        self.assertEqual(json.loads(exported.stdout)["STATUS"], "HANDOFF_PREPARED")
        status = subprocess.run(command + ["managed-status", str(self.directory)], capture_output=True, text=True, timeout=20)
        self.assertEqual(json.loads(status.stdout)["FINAL_RESULT"], "NOT_COMPLETE")


if __name__ == "__main__":
    unittest.main()
