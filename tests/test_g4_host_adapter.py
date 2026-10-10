from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import unittest
from unittest.mock import Mock

from ash import g4_host_adapter as a
from ash.g4_contracts import G4Error, parse
from ash.g3_authorization import EligibilityDecision
from tests.g4_fixtures import *


class G4HostAdapterTests(unittest.TestCase):
    def start(self, r=None):
        r = r or request()
        session = a.StructuralSession()
        fixture = session.fixture(r, now=NOW)
        decision = session.check(r, fixture, now=NOW)
        self.assertEqual(decision["status"], "ALLOW_STRUCTURAL_TEST_ONLY")
        self.assertEqual(decision["dispatch_authority"], "none")
        return session, fixture, decision

    def test_real_admission_missing_malformed_typed_and_fixtures_deny(self):
        s, fixture, _ = self.start()
        typed = EligibilityDecision("NOT_ELIGIBLE", ("G3_APPROVAL_ORIGIN_UNVERIFIED",), None, None, None, NOW, "REAL_ADMISSION_DISABLED")
        positive = EligibilityDecision("ELIGIBLE", ("G3_ELIGIBLE",), "nexus.g3.subject.v1:" + SOURCE,
                                       "nexus.g3.grant.v1:" + ORIGINAL, SOURCE, NOW, "TEST_FIXTURE_ONLY")
        for authority in (None, {}, fixture, typed, positive):
            with self.subTest(authority=type(authority).__name__):
                verdict = a.pre_execution_gate(request(), authority, now=NOW)
                self.assertEqual(verdict["status"], "DENY")
                self.assertFalse(verdict["real_admission_enabled"])
        self.assertEqual(a.pre_execution_gate(request(), positive, now=NOW)["reason"], "G4_PRODUCTION_FIXTURE_REJECTED")

    def test_two_packs_compose_request_gate_result_and_production_deny(self):
        for pack in c.PACK_EVIDENCE:
            s = a.StructuralSession(); r = request(); fixture = s.fixture(r, now=NOW)
            domain = bundle(pack)
            decision = s.check_domain(r, fixture, bundle=domain, now=NOW)
            self.assertEqual(decision["status"], "ALLOW_STRUCTURAL_TEST_ONLY")
            self.assertEqual(decision["domain_pack_ref"], domain["pack"].record_id)
            output = s.record_result(decision["request_ref"], result(), now=NOW+1)
            self.assertEqual(output["status"], "VERIFICATION_REQUIRED")
            self.assertEqual(a.pre_execution_gate(r, fixture, now=NOW)["status"], "DENY")

    def test_domain_failure_and_request_substitution_deny_before_consumption(self):
        s = a.StructuralSession(); r = request(); fixture = s.fixture(r, now=NOW)
        domain = bundle(); domain["observations"]["boundary"]["status"] = "FAIL"
        self.assertEqual(s.check_domain(r, fixture, bundle=domain, now=NOW)["status"], "DENY")
        self.assertEqual(parse(s.restart_snapshot())["pending_request_refs"], [])
        domain = bundle(); domain["expected_binding"]["execution_id"] = "other"
        self.assertEqual(s.check_domain(r, fixture, bundle=domain, now=NOW)["reason"], "G4_BINDING_MISMATCH")
        self.assertEqual(s.check_domain(r, fixture, bundle=bundle(), now=NOW)["status"], "ALLOW_STRUCTURAL_TEST_ONLY")

    def test_every_binding_field_mismatch(self):
        for key, value in {"workspace_id": "other", "project_id": "other", "task_id": "other", "action_id": "other",
                           "execution_id": "other", "generation": 2, "incarnation": "other", "input_sha256": SOURCE}.items():
            s = a.StructuralSession(); f = s.fixture(request(), now=NOW); f["binding"][key] = value
            self.assertEqual(s.check(request(), f, now=NOW)["reason"], "G4_BINDING_MISMATCH")

    def test_authority_scope_expiry_schema_and_basis(self):
        for key, value, reason in (("operations", ["write"], "G4_SCOPE_MISMATCH"),
                                  ("expires_at", NOW, "G4_AUTHORITY_EXPIRED"),
                                  ("issued_at", NOW+1, "G4_AUTHORITY_EXPIRED"),
                                  ("basis", "PRODUCTION", "G4_INVALID_INPUT"),
                                  ("schema_version", "v2", "G4_INVALID_INPUT")):
            s = a.StructuralSession(); f = s.fixture(request(), now=NOW); f[key] = value
            self.assertEqual(s.check(request(), f, now=NOW)["reason"], reason)

    def test_duplicate_action_and_concurrent_replay(self):
        s = a.StructuralSession(); r = request(); f = s.fixture(r, now=NOW)
        with ThreadPoolExecutor(max_workers=4) as pool:
            decisions = list(pool.map(lambda _: s.check(r, f, now=NOW), range(8)))
        self.assertEqual(sum(d["status"] == "ALLOW_STRUCTURAL_TEST_ONLY" for d in decisions), 1)
        changed = request(binding=binding(execution_id="other", generation=2))
        self.assertEqual(s.check(changed, s.fixture(changed, now=NOW), now=NOW)["reason"], "G4_ACTION_REPLAY")

    def test_default_unqualified_recovery_mock_and_exception_cannot_allow(self):
        for fence in (None, Mock(status=Mock(return_value="QUALIFIED")), Mock(status=Mock(side_effect=RuntimeError("private")))):
            s = a.StructuralSession(fence); r = request(requires_recovery=True)
            verdict = s.check(r, s.fixture(r, now=NOW), now=NOW)
            self.assertEqual(verdict["status"], "DENY")
            self.assertEqual(verdict["reason"], "G4_RECOVERY_FENCE_UNQUALIFIED")

    def test_completed_failure_cancellation_unknown_are_separate_and_one_use(self):
        expected = {"COMPLETED": "VERIFICATION_REQUIRED", "FAILED": "FAILED",
                    "CANCELLED": "CANCEL_REQUESTED", "UNKNOWN": "OUTCOME_UNKNOWN"}
        for status in expected:
            s, _, d = self.start()
            record = s.record_result(d["request_ref"], result(status), now=NOW+1)
            self.assertEqual(record["status"], expected[status])
            self.assertEqual(record["verification"], "STRUCTURAL_ONLY_NOT_RUNTIME_QUALIFIED")
            with self.assertRaises(G4Error): s.record_result(d["request_ref"], result(status), now=NOW+1)
            self.assertEqual(s.check(request(), s.fixture(request(), now=NOW), now=NOW)["reason"], "G4_ACTION_REPLAY")

    def test_result_wrong_binding_stale_future_expired_and_unsupported(self):
        for changed in (result(binding=binding(task_id="other")), result(observed_at=NOW+2),
                        result(schema_version="v99"), result(basis="PRODUCTION"), {**result(), "status": "SUCCESS"}):
            s, _, d = self.start()
            with self.assertRaises(G4Error): s.record_result(d["request_ref"], changed, now=NOW+1)
        s, _, d = self.start()
        self.assertEqual(s.record_result(d["request_ref"], result(), now=NOW+100)["status"], "VERIFICATION_REQUIRED")
        self.assertEqual(s.check(request(), s.fixture(request(), now=NOW), now=NOW+100)["status"], "DENY")
        with self.assertRaises(G4Error): a.result(result(observed_at=0), binding(), now=NOW)

    def test_corrupt_nested_evidence_and_completed_contradiction(self):
        for changes in ({"ref": "bad"}, {"source": "PRODUCTION"}, {"observed_at": NOW+2},
                        {"result": "FAIL"}, {"type": "unknown"}, {"password": "private"}):
            value = result(); value["evidence"][0].update(changes)
            with self.assertRaises(G4Error): a.result(value, binding(), now=NOW+1)
        value = result(); value["evidence"] *= 2
        with self.assertRaises(G4Error): a.result(value, binding(), now=NOW+1)

    def test_result_missing_required_evidence(self):
        for status in ("COMPLETED", "FAILED", "CANCELLED", "UNKNOWN"):
            value = result(status); value["evidence"][0]["type"] = "validation"
            with self.assertRaises(G4Error): a.result(value, binding(), now=NOW+1)

    def test_restart_snapshot_is_inert_and_old_session_fixture_rejected(self):
        s, fixture, decision = self.start(); snapshot = parse(s.restart_snapshot())
        self.assertEqual(snapshot["resume"], "DENY")
        new_session = a.StructuralSession()
        self.assertEqual(new_session.check(request(), fixture, now=NOW)["reason"], "G4_SESSION_MISMATCH")
        with self.assertRaises(G4Error): new_session.record_result(decision["request_ref"], result(), now=NOW+1)
        self.assertEqual(a.pre_execution_gate(request(), snapshot, now=NOW)["status"], "DENY")

    def test_audit_redacts_by_closed_projection_and_fixed_errors(self):
        s, _, d = self.start()
        record = s.record_result(d["request_ref"], result(), now=NOW+1)
        serialized = str(record)
        for text in ("fixture-project", "fixture-task", "fixture-execution", "raw_reasoning"):
            self.assertNotIn(text, serialized)
        for key in ("stdout", "stderr", "metadata", "chain_of_thought", "password", "jwt"):
            value = result(); value[key] = "sensitive-untrusted-value"
            with self.assertRaises(G4Error) as caught: a.result(value, binding(), now=NOW+1)
            self.assertNotIn("sensitive-untrusted-value", str(caught.exception))

    def test_requests_size_types_and_extra_fields_fail_closed(self):
        for changes in ({"expires_at": True}, {"requires_recovery": "false"}, {"operations": []},
                        {"operations": ["read"] * 65}, {"operations": ["sudo"]}, {"raw_command": "secret"}):
            self.assertEqual(a.pre_execution_gate(request(**changes), now=NOW)["status"], "DENY")

    def test_bounded_session_never_evicts_consumed_actions(self):
        s = a.StructuralSession()
        for index in range(a.MAX_ACTIONS):
            r = request(binding=binding(action_id="action-" + str(index)))
            self.assertEqual(s.check(r, s.fixture(r, now=NOW), now=NOW)["status"], "ALLOW_STRUCTURAL_TEST_ONLY")
        r = request(binding=binding(action_id="extra"))
        self.assertEqual(s.check(r, s.fixture(r, now=NOW), now=NOW)["reason"], "G4_SESSION_LIMIT")

    def test_no_transports_dispatch_or_provider_calls(self):
        import ast
        from pathlib import Path
        for module in (a, c):
            tree = ast.parse(Path(module.__file__).read_text())
            imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | {name.name for n in ast.walk(tree) if isinstance(n, ast.Import) for name in n.names}
            self.assertFalse(imported & {"subprocess", "requests", "openai", "socket", "urllib"})
        self.assertFalse(hasattr(a.StructuralSession, "submit"))
        self.assertFalse(hasattr(a.StructuralSession, "restore"))


if __name__ == "__main__": unittest.main()
