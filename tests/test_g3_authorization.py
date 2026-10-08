from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, asdict, replace
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from ash import g3_authorization as g3
from tests.g3_fixtures import (
    NOW, evaluate_fixture, grant_body, revoke_body, scope, subject_body,
)


class G3AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.s = g3.subject(subject_body())
        self.g = g3.approval_grant(grant_body(self.s))

    def assertReason(self, code, result):
        self.assertEqual(result.status, "NOT_ELIGIBLE")
        self.assertIn(code, result.reason_codes)
        self.assertEqual(result.dispatch_authority, "none")

    def real(self, grants=None, revocations=(), **changes):
        arguments = {"now": NOW, "technical_available": True, "task_authorized": True,
                     "host_authorized": True, "g1_passed": True, "g2_passed": True, **changes}
        return g3.evaluate_eligibility(self.s, grants if grants is not None else (self.g,),
                                       revocations, scope(), **arguments)

    def test_canonical_golden_and_round_trip(self):
        body = subject_body()
        reordered = dict(reversed(list(body.items())))
        self.assertEqual(g3.subject(reordered), self.s)
        self.assertEqual(g3.subject(g3.parse_input(json.dumps(body, indent=4).encode())), self.s)
        self.assertEqual(self.s.subject_id, "nexus.g3.subject.v1:72898871ad181521fbeebabbee77cbae525071df16a2f28855ace4c37ed5aa99")

    def test_cosmetic_title_only(self):
        self.assertEqual(g3.subject({**subject_body(), "display_title": "Alpha"}), self.s)
        self.assertEqual(g3.subject({**subject_body(), "display_title": "Beta"}), self.s)
        for key in ("description", "icon", "observed_at", "telemetry", "unknown_material"):
            with self.subTest(key=key), self.assertRaises(g3.G3Error):
                g3.subject({**subject_body(), key: "value"})

    def test_every_material_local_field_changes_identity(self):
        for key, value in {"revision": "r2", "source_ref": "source2", "provider": "provider2",
                           "action": "write", "content_sha256": "c" * 64,
                           "config_sha256": "d" * 64}.items():
            with self.subTest(key=key):
                changed = g3.subject({**subject_body(), key: value})
                self.assertNotEqual(changed.subject_id, self.s.subject_id)
                self.assertReason("G3_CAPABILITY_SUBJECT_MISMATCH", evaluate_fixture(changed, (self.g,)))

    def test_mcp_account_action_tool_and_contract_exact(self):
        s = g3.subject(subject_body("mcp_tool"))
        account_scope = scope(account_context="fixture-account")
        grant = g3.approval_grant(grant_body(s, scope=account_scope))
        self.assertEqual(evaluate_fixture(s, (grant,), requested_scope=account_scope).status, "ELIGIBLE")
        for key, value in {"account_context": "other", "action": "write", "tool_name": "read",
                           "contract_sha256": "c" * 64, "server_ref": "other-server",
                           "revision": "r2", "config_sha256": "d" * 64}.items():
            with self.subTest(key=key):
                other = g3.subject({**s.to_dict(), key: value})
                self.assertReason("G3_CAPABILITY_SUBJECT_MISMATCH",
                                  evaluate_fixture(other, (grant,), requested_scope=account_scope))
        for request in (scope(), scope(account_context="other")):
            self.assertReason("G3_CAPABILITY_SCOPE_DENIED", evaluate_fixture(s, (grant,), requested_scope=request))
        broad = g3.approval_grant(grant_body(s))
        self.assertReason("G3_CAPABILITY_SCOPE_DENIED",
                          evaluate_fixture(s, (broad,), requested_scope=account_scope))

    def test_component_reuses_frozen_identity_and_requires_review(self):
        s = g3.subject(subject_body("local_component"))
        grant = g3.approval_grant(grant_body(s))
        self.assertReason("G3_CAPABILITY_EVIDENCE_UNVERIFIED", evaluate_fixture(s, (grant,)))
        review = {"subject_id": s.subject_id, "evidence": {"ref": "review", "sha256": "f" * 64},
                  "provenance_ref": "fixture-provenance"}
        reviewed = g3.approval_grant(grant_body(s, review=review))
        self.assertEqual(evaluate_fixture(s, (reviewed,)).status, "ELIGIBLE")
        from ash.ecosystem_models import typed_id
        changed = g3.subject({**s.to_dict(), "component_revision_id": typed_id(
            "component-revision", {"fixture": "changed-revision"})})
        self.assertReason("G3_CAPABILITY_SUBJECT_MISMATCH", evaluate_fixture(changed, (reviewed,)))
        with self.assertRaises(g3.G3Error):
            g3.approval_grant(grant_body(s, review={**review, "subject_id": self.s.subject_id}))
        for key in ("source_id", "component_revision_id"):
            with self.subTest(key=key), self.assertRaises(g3.G3Error):
                g3.subject({**s.to_dict(), key: "not-a-typed-id"})

    def test_bounded_duplicate_safe_closed_input(self):
        for raw in (b'{"kind":"a","kind":"b"}', b'{"x":1.5}', b'{"x":NaN}',
                    b'{"x":-1}', b'{"x":9223372036854775808}', b' ' * (g3.MAX_BYTES + 1)):
            with self.subTest(raw=raw[:45]), self.assertRaises(g3.G3Error):
                g3.parse_input(raw)
        cyclic = {}
        cyclic["self"] = cyclic
        with self.assertRaises(g3.G3Error):
            g3.subject(cyclic)
        for key, value in {"kind": [], "capability_id": "CAP", "provider": "*",
                           "content_sha256": "A" * 64, "config_sha256": "short",
                           "revision": "r" * 513, "display_title": True}.items():
            with self.subTest(key=key), self.assertRaises(g3.G3Error):
                g3.subject({**subject_body(), key: value})

    def test_immutable_records_detach_caller_data(self):
        body = grant_body(self.s)
        grant = g3.approval_grant(body)
        body["scope"]["operations"].append("write")
        detached = grant.to_dict()
        detached["scope"]["operations"].append("execute")
        self.assertEqual(grant.to_dict()["scope"]["operations"], ["read"])
        with self.assertRaises(FrozenInstanceError):
            grant.grant_id = "replacement"
        tampered = replace(grant, grant_id=self.g.grant_id + "0")
        self.assertReason("G3_INVALID_INPUT", self.real((tampered,)))

    def test_grant_closed_shape_and_body_identity(self):
        for changes in ({"extra": True}, {"subject_sha256": "c" * 64}, {"issuer_ref": "*"},
                        {"effective_at": True}, {"expires_at": 1000}, {"expires_at": 999},
                        {"decision_evidence": {"ref": "e", "sha256": "bad"}},
                        {"schema_version": "future"}):
            with self.subTest(changes=changes), self.assertRaises(g3.G3Error):
                g3.approval_grant({**grant_body(), **changes})
        renewal = g3.approval_grant(grant_body(self.s, expires_at=4000))
        self.assertNotEqual(renewal.grant_id, self.g.grant_id)
        with self.assertRaises(g3.G3Error):
            g3.approval_grant({"issuer": "owner", "approved": True})

    def test_valid_fixture_is_eligible_but_never_authority(self):
        result = evaluate_fixture(self.s, (self.g,))
        self.assertEqual(result.status, "ELIGIBLE")
        self.assertEqual(result.reason_codes, ("G3_ELIGIBLE",))
        self.assertEqual(result.basis, "TEST_FIXTURE_ONLY")
        self.assertEqual(result.dispatch_authority, "none")
        self.assertEqual(result.grant_id, self.g.grant_id)
        self.assertEqual(result, evaluate_fixture(self.s, (self.g,)))

    def test_decision_contract_closed_and_bounded(self):
        result = evaluate_fixture(self.s, (self.g,))
        for changes in ({"dispatch_authority": "execute"}, {"basis": "OWNER"},
                        {"basis": "REAL_ADMISSION_DISABLED"}, {"reason_codes": ("FAKE",)},
                        {"reason_codes": ("G3_ELIGIBLE",) * 17}, {"evaluated_at": True},
                        {"request_sha256": "bad"}, {"schema_version": "future"},
                        {"subject_id": None}, {"request_sha256": None}, {"evaluated_at": None}):
            with self.subTest(changes=changes), self.assertRaises(g3.G3Error):
                replace(result, **changes)

    def test_production_and_owner_string_and_fixture_never_admitted(self):
        for issuer in ("owner", "test-fixture", "auto-review"):
            grant = g3.approval_grant(grant_body(self.s, issuer_ref=issuer))
            result = self.real((grant,))
            self.assertReason("G3_APPROVAL_ORIGIN_UNVERIFIED", result)
            self.assertEqual(result.basis, "REAL_ADMISSION_DISABLED")
        owner = g3.approval_grant(grant_body(self.s, issuer_ref="owner"))
        self.assertReason("G3_APPROVAL_ORIGIN_UNVERIFIED", evaluate_fixture(self.s, (owner,)))
        changed_evidence = g3.approval_grant(grant_body(self.s, decision_evidence={"ref": "other", "sha256": "e" * 64}))
        self.assertReason("G3_APPROVAL_ORIGIN_UNVERIFIED", evaluate_fixture(self.s, (changed_evidence,)))

    def test_effective_expiry_boundaries_and_no_renewal(self):
        self.assertReason("G3_APPROVAL_NOT_EFFECTIVE", evaluate_fixture(self.s, (self.g,), now=999))
        self.assertEqual(evaluate_fixture(self.s, (self.g,), now=1000).status, "ELIGIBLE")
        self.assertEqual(evaluate_fixture(self.s, (self.g,), now=2999).status, "ELIGIBLE")
        for now in (3000, 3001, 9000):
            self.assertReason("G3_CAPABILITY_EXPIRED", evaluate_fixture(self.s, (self.g,), now=now))
        persistent = g3.approval_grant(grant_body(self.s, expires_at=None))
        self.assertEqual(evaluate_fixture(self.s, (persistent,), now=9000).status, "ELIGIBLE")

    def test_exact_revocation_terminal_and_new_grant(self):
        revoke = g3.revocation(revoke_body(self.g))
        self.assertEqual(evaluate_fixture(self.s, (self.g,), (revoke,), now=1499).status, "ELIGIBLE")
        for now in (1500, 2000, 9000):
            self.assertReason("G3_CAPABILITY_REVOKED", evaluate_fixture(self.s, (self.g,), (revoke,), now=now))
        new = g3.approval_grant(grant_body(self.s, effective_at=1600))
        self.assertNotEqual(new.grant_id, self.g.grant_id)
        result = evaluate_fixture(self.s, (self.g, new), (revoke,))
        self.assertEqual(result.status, "ELIGIBLE")
        self.assertEqual(result.grant_id, new.grant_id)
        self.assertEqual(result, evaluate_fixture(self.s, (new, self.g), (revoke,)))

    def test_unrelated_revocation_no_poison_and_untrusted_deny(self):
        other = g3.approval_grant(grant_body(self.s, effective_at=1100))
        unrelated = g3.revocation(revoke_body(other))
        self.assertEqual(evaluate_fixture(self.s, (self.g,), (unrelated,)).status, "ELIGIBLE")
        untrusted = g3.revocation(revoke_body(self.g, issuer_ref="owner"))
        self.assertReason("G3_APPROVAL_ORIGIN_UNVERIFIED", evaluate_fixture(self.s, (self.g,), (untrusted,)))
        for changes in ({"grant_id": "*"}, {"reason": "*"}, {"effective_at": -1}, {"extra": True}):
            with self.subTest(changes=changes), self.assertRaises(g3.G3Error):
                g3.revocation({**revoke_body(self.g), **changes})

    def test_scope_no_expansion_or_union(self):
        for changes in ({"workspace_id": "other"}, {"project_id": "other"},
                        {"task_classes": ["other"]}, {"operations": ["read", "write"]}):
            self.assertReason("G3_CAPABILITY_SCOPE_DENIED", evaluate_fixture(
                self.s, (self.g,), requested_scope=scope(**changes)))
        read_grant = self.g
        write_grant = g3.approval_grant(grant_body(self.s, scope=scope(operations=["write"])))
        self.assertReason("G3_CAPABILITY_SCOPE_DENIED", evaluate_fixture(
            self.s, (read_grant, write_grant), requested_scope=scope(operations=["read", "write"])))
        narrowed = g3.approval_grant(grant_body(self.s, scope=scope(task_id="task1")))
        for request in (scope(), scope(task_id="task2")):
            self.assertReason("G3_CAPABILITY_SCOPE_DENIED", evaluate_fixture(self.s, (narrowed,), requested_scope=request))
        self.assertEqual(evaluate_fixture(self.s, (narrowed,), requested_scope=scope(task_id="task1")).status, "ELIGIBLE")

    def test_scope_closed_sets_canonical_and_empty_denied(self):
        for changes in ({"operations": []}, {"task_classes": []}, {"operations": ["*"]},
                        {"task_classes": ["governance", "governance"]}, {"roles": ["owner"]},
                        {"workspace_id": "*"}, {"operations": ["deploy"]}):
            with self.subTest(changes=changes), self.assertRaises(g3.G3Error):
                g3.approval_grant(grant_body(self.s, scope=scope(**changes)))
        first = g3.approval_grant(grant_body(self.s, scope=scope(operations=["read", "write"])))
        second = g3.approval_grant(grant_body(self.s, scope=scope(operations=["write", "read"])))
        self.assertEqual(first, second)

    def test_missing_grant_and_all_independent_gates(self):
        self.assertReason("G3_CAPABILITY_UNAPPROVED", evaluate_fixture(self.s, ()))
        codes = {"technical_available": "G3_CAPABILITY_UNAVAILABLE",
                 "task_authorized": "G3_TASK_AUTHORITY_REQUIRED", "host_authorized": "G3_HOST_AUTHORITY_REQUIRED",
                 "g1_passed": "G3_G1_RESTRICTION_FAILED", "g2_passed": "G3_G2_RESTRICTION_FAILED"}
        for gate, code in codes.items():
            with self.subTest(gate=gate):
                self.assertReason(code, evaluate_fixture(self.s, (self.g,), **{gate: False}))
        result = evaluate_fixture(self.s, (self.g,), **{gate: False for gate in codes})
        self.assertEqual(result.reason_codes, tuple(codes.values()))
        self.assertReason("G3_INVALID_INPUT", self.real(g1_passed=1))

    def test_candidate_json_and_copied_decision_are_not_bearers(self):
        candidate = {"approved": True, "issuer": "owner", "grant": self.g.to_dict()}
        self.assertReason("G3_INVALID_INPUT", self.real((candidate,)))
        copied = asdict(evaluate_fixture(self.s, (self.g,)))
        self.assertReason("G3_INVALID_INPUT", self.real((copied,)))
        self.assertReason("G3_INVALID_INPUT", g3.evaluate_eligibility(
            copied, (self.g,), (), scope(), now=NOW, technical_available=True,
            task_authorized=True, host_authorized=True, g1_passed=True, g2_passed=True))

    def test_records_limits_and_identity_tampering(self):
        self.assertReason("G3_INVALID_INPUT", self.real((self.g, self.g)))
        self.assertReason("G3_INVALID_INPUT", self.real(tuple(self.g for _ in range(65))))
        self.assertReason("G3_INVALID_INPUT", self.real([self.g]))
        forged = replace(self.s, subject_id=self.s.subject_id + "0")
        self.assertReason("G3_INVALID_INPUT", evaluate_fixture(forged, (self.g,)))

    def test_negative_decisions_have_no_effects(self):
        # After imports, trap real effect boundaries and filesystem/env access.
        from ash import core, managed_execution, openai_hosted

        class ForbiddenEnvironment(dict):
            def get(self, *args):
                raise AssertionError("environment probe")

            def __getitem__(self, key):
                raise AssertionError("environment read")

            def __contains__(self, key):
                raise AssertionError("environment presence check")

        with patch("builtins.open", side_effect=AssertionError("file access")), \
                patch("os.getenv", side_effect=AssertionError("credential/environment access")), \
                patch("os.environ", ForbiddenEnvironment()), \
                patch("urllib.request.urlopen", side_effect=AssertionError("HTTP")) as http, \
                patch.object(core, "_dispatch", side_effect=AssertionError("dispatch/hook")) as dispatch, \
                patch.object(core, "_save", side_effect=AssertionError("DISPATCH_INTENT")), \
                patch.object(managed_execution, "_save", side_effect=AssertionError("intent")), \
                patch.object(managed_execution, "export_handoff", side_effect=AssertionError("handoff")), \
                patch.object(openai_hosted.OpenAIHTTPS, "credential_available", side_effect=AssertionError("credential")), \
                patch.object(openai_hosted.OpenAIHostedExecutionBackend, "submit", side_effect=AssertionError("provider")):
            self.assertReason("G3_APPROVAL_ORIGIN_UNVERIFIED", self.real())
            self.assertReason("G3_CAPABILITY_EXPIRED", evaluate_fixture(self.s, (self.g,), now=3000))
            self.assertReason("G3_CAPABILITY_REVOKED", evaluate_fixture(
                self.s, (self.g,), (g3.revocation(revoke_body(self.g)),)))
            http.assert_not_called()
            dispatch.assert_not_called()

    def test_no_runtime_consumer_or_test_issuer_import(self):
        root = Path(g3.__file__).resolve().parent
        for path in root.rglob("*.py"):
            if path.name == "g3_authorization.py":
                continue
            self.assertNotIn("g3_authorization", path.read_text(encoding="utf-8"), path)
        tree = ast.parse(Path(g3.__file__).read_text(encoding="utf-8"))
        imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        self.assertFalse(any(name.startswith("tests") for name in imports))
        self.assertFalse(any(name in {"core", "openai_hosted", "managed_execution", "execution"} for name in imports))


if __name__ == "__main__":
    unittest.main()
