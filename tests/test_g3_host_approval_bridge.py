"""Synthetic installed-schema-shaped transcripts; TEST / CONTRACT EVIDENCE ONLY."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, asdict, replace
import json
import unittest
from unittest.mock import patch

from ash import g3_authorization as g3
from ash import g3_host_approval_bridge as bridge
from tests.g3_fixtures import NOW, grant_body, revoke_body, scope, subject_body


def native_request(request_id="request-1", **changes):
    return {"id": request_id, "method": bridge.REQUEST_METHOD,
            "params": {"threadId": "thread-1", "turnId": "turn-1", "itemId": "item-1",
                       "startedAtMs": 1000000, "command": "fixture-read input-1", "cwd": "/fixture/project",
                       "approvalId": "callback-1", "environmentId": "fixture-env", "kind": "command", **changes}}


def native_response(request_id="request-1", decision="accept"):
    return {"id": request_id, "result": {"decision": decision}}


def native_resolved(request_id="request-1", thread_id="thread-1"):
    return {"method": bridge.RESOLVED_METHOD, "params": {"threadId": thread_id, "requestId": request_id}}


def effects(operations=None, targets_sha256="f" * 64):
    return {"operations": ["read"] if operations is None else operations, "targets_sha256": targets_sha256}


HUMAN = {"reviewer": "user", "resolution": "explicit"}


class HostApprovalBridgeTests(unittest.TestCase):
    def setUp(self):
        self.s = g3.subject(subject_body())
        self.p = bridge.proposal(native_request(), self.s, scope(), effects())
        self.e = bridge.event(self.p, native_response(), observation=HUMAN)

    def changed_event(self, **changes):
        # A well-shaped but hostile offline event, with a recomputed content ID.
        body = {**self.e.to_dict(), **changes}
        raw = g3._canonical(body)
        return bridge.HostApprovalEvent(raw, g3._id("host-approval-event", raw))

    def assertRejected(self, disposition, event, proposal=None, consumed=frozenset()):
        result = bridge.correlate(proposal or self.p, event, consumed)
        self.assertEqual(result.disposition, disposition)
        self.assertIsNone(result.candidate_evidence)
        self.assertEqual(result.dispatch_authority, "none")
        self.assertFalse(result.owner_authenticated)
        return result

    def test_exact_explicit_approval_candidate(self):
        result = bridge.correlate(self.p, self.e, frozenset())
        self.assertEqual(result.disposition, "EXPLICIT_APPROVE")
        candidate = g3.parse_input(result.candidate_evidence)
        self.assertEqual(candidate["proposal_id"], self.p.proposal_id)
        self.assertEqual(candidate["subject_id"], self.s.subject_id)
        self.assertEqual(candidate["scope_sha256"], self.p.to_dict()["scope_sha256"])
        self.assertEqual(candidate["identity"]["request_id"], "request-1")
        self.assertEqual(candidate["explicit_decision"], "accept")
        self.assertEqual(candidate["basis"], "OFFLINE_CONTRACT_ONLY")
        self.assertFalse(candidate["owner_authenticated"])
        self.assertEqual(candidate["approval_authority"], "none")
        self.assertEqual(candidate["dispatch_authority"], "none")
        self.assertEqual(len(result.consumed_tokens), 3)
        self.assertEqual(result, bridge.correlate(self.p, self.e, frozenset()))

    def test_explicit_decline_and_cancel_remain_denied(self):
        for decision in ("decline", "cancel"):
            with self.subTest(decision=decision):
                event = bridge.event(self.p, native_response(decision=decision), observation=HUMAN)
                result = self.assertRejected("EXPLICIT_DENY", event)
                self.assertRejected("DUPLICATE", self.e, consumed=result.consumed_tokens)

    def test_subject_mismatch(self):
        other = g3.subject({**subject_body(), "revision": "r2"})
        proposal = bridge.proposal(native_request(), other, scope(), effects())
        self.assertNotEqual(proposal.proposal_id, self.p.proposal_id)
        self.assertRejected("MISMATCH", bridge.event(proposal, native_response(), observation=HUMAN))
        self.assertRejected("MISMATCH", self.changed_event(subject_id=other.subject_id))

    def test_broader_scope_and_workspace_project_changes(self):
        for changes in ({"operations": ["read", "write"]}, {"workspace_id": "workspace-2"},
                        {"project_id": "project-2"}, {"task_classes": ["governance", "other"]},
                        {"task_id": "task-2"}):
            with self.subTest(changes=changes):
                requested = scope(**changes)
                proposal = bridge.proposal(native_request(), self.s, requested, effects(requested["operations"]))
                self.assertNotEqual(proposal.proposal_id, self.p.proposal_id)
                self.assertRejected("MISMATCH", bridge.event(proposal, native_response(), observation=HUMAN))

    def test_duplicate_request_id_with_changed_event_and_approval_id(self):
        first = bridge.correlate(self.p, self.e, frozenset())
        other = bridge.proposal(native_request(approvalId="callback-2"), self.s, scope(), effects())
        event = bridge.event(other, native_response(decision="decline"), observation=HUMAN)
        self.assertRejected("DUPLICATE", event, other, first.consumed_tokens)

    def test_duplicate_approval_id_with_different_request_id(self):
        first = bridge.correlate(self.p, self.e, frozenset())
        other = bridge.proposal(native_request("request-2"), self.s, scope(), effects())
        event = bridge.event(other, native_response("request-2"), observation=HUMAN)
        self.assertRejected("DUPLICATE", event, other, first.consumed_tokens)

    def test_replay_after_success_under_other_subject_or_scope(self):
        first = bridge.correlate(self.p, self.e, frozenset())
        second = self.assertRejected("DUPLICATE", self.e, consumed=first.consumed_tokens)
        self.assertEqual(second.consumed_tokens, first.consumed_tokens)
        for proposal in (bridge.proposal(native_request(), g3.subject({**subject_body(), "revision": "r2"}), scope(), effects()),
                         bridge.proposal(native_request(), self.s, scope(operations=["read", "write"]), effects(["read", "write"]))):
            self.assertRejected("DUPLICATE", self.e, proposal, first.consumed_tokens)
            self.assertRejected("MISMATCH", self.e, proposal)

    def test_clear_timeout_auto_resolution_are_terminal(self):
        for resolution, disposition in (("cleared", "CLEARED"), ("timed_out", "TIMED_OUT"),
                                        ("auto_resolved", "AUTO_RESOLVED")):
            with self.subTest(resolution=resolution):
                event = bridge.event(self.p, native_resolved(), observation={"reviewer": "user", "resolution": resolution})
                result = self.assertRejected(disposition, event)
                self.assertRejected("DUPLICATE", self.e, consumed=result.consumed_tokens)

    def test_auto_review_accept_cannot_masquerade_as_human_choice(self):
        event = bridge.event(self.p, native_response(), observation={"reviewer": "auto_review", "resolution": "explicit"})
        result = self.assertRejected("AUTO_RESOLVED", event)
        self.assertRejected("DUPLICATE", self.e, consumed=result.consumed_tokens)

    def test_accept_or_resolution_alone_never_proves_approval(self):
        self.assertRejected("UNKNOWN", bridge.event(self.p, native_response()))
        self.assertRejected("UNKNOWN", bridge.event(self.p, native_resolved(), observation=HUMAN))
        self.assertRejected("UNKNOWN", bridge.event(self.p, native_response(decision="acceptForSession"), observation=HUMAN))

    def test_wrong_thread_turn_item(self):
        for key in ("threadId", "turnId", "itemId"):
            with self.subTest(key=key):
                other = bridge.proposal(native_request(**{key: "other"}), self.s, scope(), effects())
                self.assertRejected("MISMATCH", bridge.event(other, native_response(), observation=HUMAN))
        self.assertRejected("MISMATCH", bridge.event(self.p, native_resolved(thread_id="other"), observation=HUMAN))

    def test_proposal_scope_digest_and_approval_id_mismatch(self):
        other = bridge.proposal(native_request(command="fixture-read changed-input"), self.s, scope(), effects())
        self.assertRejected("MISMATCH", self.changed_event(proposal_id=other.proposal_id))
        self.assertRejected("MISMATCH", self.changed_event(scope_sha256="c" * 64))
        identity = {**self.e.to_dict()["identity"], "approval_id": None}
        self.assertRejected("MISMATCH", self.changed_event(identity=identity))

    def test_native_response_request_id_mismatch(self):
        self.assertRejected("MISMATCH", bridge.event(self.p, native_response("request-2"), observation=HUMAN))
        self.assertRejected("MISMATCH", bridge.event(self.p, native_resolved("request-2"), observation=HUMAN))
        self.assertRejected("MISMATCH", bridge.event(self.p, native_response(1), observation=HUMAN))

    def test_missing_request_tuple_and_event_fields_fail_closed(self):
        for key in ("id", "method", "params"):
            bad = native_request()
            del bad[key]
            with self.subTest(key=key), self.assertRaises(g3.G3Error):
                bridge.proposal(bad, self.s, scope(), effects())
        for key in ("threadId", "turnId", "itemId", "startedAtMs", "command", "cwd"):
            bad = native_request()
            del bad["params"][key]
            with self.subTest(key=key), self.assertRaises(g3.G3Error):
                bridge.proposal(bad, self.s, scope(), effects())
        for key in self.e.to_dict()["identity"]:
            identity = self.e.to_dict()["identity"]
            del identity[key]
            with self.subTest(key=key), self.assertRaises(g3.G3Error):
                bridge.correlate(self.p, self.changed_event(identity=identity), frozenset())

    def test_optional_approval_id_null_is_not_missing_request_identity(self):
        request = native_request()
        del request["params"]["approvalId"]
        proposal = bridge.proposal(request, self.s, scope(), effects())
        explicit_null = bridge.proposal(native_request(approvalId=None), self.s, scope(), effects())
        self.assertEqual(proposal, explicit_null)
        result = bridge.correlate(proposal, bridge.event(proposal, native_response(), observation=HUMAN), frozenset())
        self.assertEqual(result.disposition, "EXPLICIT_APPROVE")
        self.assertEqual(len(result.consumed_tokens), 2)

    def test_changed_effect_action_and_host_material_change_digest(self):
        other_effects = bridge.proposal(native_request(), self.s, scope(), effects(targets_sha256="e" * 64))
        action = g3.subject({**subject_body(), "action": "inspect"})
        other_action = bridge.proposal(native_request(), action, scope(), effects())
        for proposal in (other_effects, other_action, bridge.proposal(native_request(startedAtMs=1000001), self.s, scope(), effects()),
                         bridge.proposal(native_request(cwd="/fixture/other"), self.s, scope(), effects())):
            self.assertNotEqual(proposal.proposal_id, self.p.proposal_id)
            self.assertRejected("MISMATCH", bridge.event(proposal, native_response(), observation=HUMAN))
        with self.assertRaises(g3.G3Error):
            bridge.proposal(native_request(), self.s, scope(), effects(["write"]))

    def test_cosmetics_key_order_and_set_order_are_stable(self):
        cosmetic = g3.subject({**subject_body(), "display_title": "Cosmetic title"})
        first = bridge.proposal(native_request(reason="Presentation A"), cosmetic, scope(), effects())
        second = bridge.proposal(native_request(reason="Presentation B"), self.s, scope(), effects())
        self.assertEqual(first, self.p)
        self.assertEqual(second, self.p)
        request = g3.parse_input(json.dumps(native_request(), indent=4).encode())
        self.assertEqual(bridge.proposal(dict(reversed(list(request.items()))), self.s, scope(), effects()), self.p)
        first = bridge.proposal(native_request(), self.s, scope(operations=["read", "write"]), effects(["write", "read"]))
        second = bridge.proposal(native_request(), self.s, scope(operations=["write", "read"]), effects(["read", "write"]))
        self.assertEqual(first, second)

    def test_numeric_and_string_ids_are_distinct(self):
        integer_id = bridge.proposal(native_request(1, approvalId=None), self.s, scope(), effects())
        string_id = bridge.proposal(native_request("1", approvalId=None), self.s, scope(), effects())
        self.assertNotEqual(integer_id.proposal_id, string_id.proposal_id)
        self.assertRejected("MISMATCH", bridge.event(integer_id, native_response("1"), observation=HUMAN), integer_id)
        first = bridge.correlate(integer_id, bridge.event(integer_id, native_response(1), observation=HUMAN), frozenset())
        second = bridge.correlate(string_id, bridge.event(string_id, native_response("1"), observation=HUMAN), first.consumed_tokens)
        self.assertEqual(second.disposition, "EXPLICIT_APPROVE")

    def test_closed_bounded_parsing_and_unsupported_variants(self):
        for raw in (b'{"id":1,"id":2}', b'{"x":1.5}', b' ' * (g3.MAX_BYTES + 1)):
            with self.subTest(raw=raw[:30]), self.assertRaises(g3.G3Error):
                g3.parse_input(raw)
        for changes in ({"unknownMaterial": "value"}, {"kind": "writeStdin"},
                        {"networkApprovalContext": {"host": "fixture"}}, {"command": "x" * 513},
                        {"approvalId": ""}, {"threadId": ""}, {"startedAtMs": True}):
            with self.subTest(changes=changes), self.assertRaises(g3.G3Error):
                bridge.proposal(native_request(**changes), self.s, scope(), effects())
        for message in ({"id": True, "result": {"decision": "accept"}},
                        {"id": "request-1", "result": {"decision": "accept", "owner": True}},
                        {"id": "request-1", "result": {"decision": "madeUp"}},
                        {"id": "request-1", "result": {"decision": {"acceptWithExecpolicyAmendment": {"execpolicy_amendment": ["fixture"]}}}}):
            with self.subTest(message=message), self.assertRaises(g3.G3Error):
                bridge.event(self.p, message, observation=HUMAN)

    def test_immutable_detachment_and_recomputed_identity_checks(self):
        request = native_request()
        proposal = bridge.proposal(request, self.s, scope(), effects())
        request["params"]["command"] = "mutated"
        self.assertEqual(proposal, self.p)
        message = native_response()
        event = bridge.event(self.p, message, observation=HUMAN)
        message["result"]["decision"] = "decline"
        self.assertEqual(event, self.e)
        with self.assertRaises(FrozenInstanceError):
            event.event_id = "replacement"
        for bad_proposal, bad_event in ((replace(self.p, proposal_id=self.p.proposal_id + "0"), self.e),
                                        (self.p, replace(self.e, event_id=self.e.event_id + "0"))):
            with self.assertRaises(g3.G3Error):
                bridge.correlate(bad_proposal, bad_event, frozenset())

    def test_mismatch_does_not_poison_another_pending_request(self):
        bad = bridge.event(self.p, native_response("foreign"), observation=HUMAN)
        result = self.assertRejected("MISMATCH", bad)
        self.assertEqual(result.consumed_tokens, frozenset())
        self.assertEqual(bridge.correlate(self.p, self.e, result.consumed_tokens).disposition, "EXPLICIT_APPROVE")

    def test_bounded_replay_set_never_silently_evicts_or_renews(self):
        full = frozenset("event:" + format(n, "064x") for n in range(bridge.MAX_CONSUMED_TOKENS))
        result = self.assertRejected("UNKNOWN", self.e, consumed=full)
        self.assertEqual(result.consumed_tokens, full)
        for bad in (set(), frozenset({"unrecognized"}), full | {"event:" + "f" * 64}):
            with self.subTest(size=len(bad)), self.assertRaises(g3.G3Error):
                bridge.correlate(self.p, self.e, bad)

    def test_candidate_evidence_and_copied_results_never_bear_authority(self):
        result = bridge.correlate(self.p, self.e, frozenset())
        candidate = g3.parse_input(result.candidate_evidence)
        with self.assertRaises(g3.G3Error):
            g3.approval_grant(candidate)
        for record in (candidate, asdict(result)):
            decision = g3.evaluate_eligibility(self.s, (record,), (), scope(), now=NOW,
                technical_available=True, task_authorized=True, host_authorized=True, g1_passed=True, g2_passed=True)
            self.assertEqual(decision.reason_codes, ("G3_INVALID_INPUT",))
        # Repackaging the candidate hash into a shape-valid grant cannot create origin.
        grant = g3.approval_grant(grant_body(self.s, issuer_ref="owner", decision_evidence={
            "ref": "offline-host-candidate", "sha256": bridge._digest(candidate)}))
        revoke = g3.revocation(revoke_body(grant))
        for revocations in ((), (revoke,)):
            decision = g3.evaluate_eligibility(self.s, (grant,), revocations, scope(), now=NOW,
                technical_available=True, task_authorized=True, host_authorized=True, g1_passed=True, g2_passed=True)
            self.assertIsInstance(decision, g3.EligibilityDecision)
            self.assertEqual(decision.reason_codes, ("G3_APPROVAL_ORIGIN_UNVERIFIED",))
            self.assertEqual(decision.dispatch_authority, "none")

    def test_correlation_contract_cannot_claim_authenticated_authority(self):
        result = bridge.correlate(self.p, self.e, frozenset())
        for changes in ({"owner_authenticated": True}, {"dispatch_authority": "execute"},
                        {"basis": "OWNER"}, {"disposition": "APPROVED"},
                        {"candidate_evidence": None}, {"consumed_tokens": set()}):
            with self.subTest(changes=changes), self.assertRaises(g3.G3Error):
                replace(result, **changes)
        candidate = g3.parse_input(result.candidate_evidence)
        for changes in ({"approval_authority": "owner"}, {"owner_authenticated": True}, {"event_id": self.e.event_id + "0"}):
            with self.subTest(changes=changes), self.assertRaises(g3.G3Error):
                replace(result, candidate_evidence=g3._canonical({**candidate, **changes}))

    def test_zero_external_effects_for_positive_and_negative_transcripts(self):
        from ash import core, managed_execution, openai_hosted

        class ForbiddenEnvironment(dict):
            def get(self, *args):
                raise AssertionError("environment probe")

            def __getitem__(self, key):
                raise AssertionError("environment read")

            def __contains__(self, key):
                raise AssertionError("environment presence")

        with patch("builtins.open", side_effect=AssertionError("I/O")), \
                patch("os.environ", ForbiddenEnvironment()), \
                patch("os.getenv", side_effect=AssertionError("credential access")), \
                patch("urllib.request.urlopen", side_effect=AssertionError("HTTP")), \
                patch("subprocess.Popen", side_effect=AssertionError("process/Host/hook")), \
                patch.object(core, "_dispatch", side_effect=AssertionError("dispatch")), \
                patch.object(core, "_save", side_effect=AssertionError("DISPATCH_INTENT")), \
                patch.object(managed_execution, "_save", side_effect=AssertionError("intent")), \
                patch.object(managed_execution, "export_handoff", side_effect=AssertionError("handoff")), \
                patch.object(openai_hosted.OpenAIHTTPS, "credential_available", side_effect=AssertionError("credential")), \
                patch.object(openai_hosted.OpenAIHostedExecutionBackend, "submit", side_effect=AssertionError("provider")):
            proposal = bridge.proposal(native_request(), self.s, scope(), effects())
            result = bridge.correlate(proposal, bridge.event(proposal, native_response(), observation=HUMAN), frozenset())
            self.assertEqual(result.disposition, "EXPLICIT_APPROVE")
            self.assertRejected("DUPLICATE", self.e, consumed=result.consumed_tokens)
            self.assertRejected("MISMATCH", bridge.event(proposal, native_response("other"), observation=HUMAN))
            for resolution, disposition in (("cleared", "CLEARED"), ("timed_out", "TIMED_OUT"), ("auto_resolved", "AUTO_RESOLVED")):
                self.assertRejected(disposition, bridge.event(proposal, native_resolved(), observation={"reviewer": "user", "resolution": resolution}))


if __name__ == "__main__":
    unittest.main()
