"""Offline App Server correlation only; no authenticated Owner or grant issuer.

Native request/response/notification messages remain separate from Nexus binding
and declared observation metadata. Results are contract evidence, never authority.
No I/O, persistence, runtime integration, callbacks or live App Server startup.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Any

from . import g3_authorization as g3
from .g1_profiles import G1Error, SECRET_IDENTIFIER_RE, exact, integer, sha

from .g3_proposal_codec import (
    PROPOSAL_SCHEMA,
    REQUEST_METHOD,
    _OPAQUE,
    _digest,
    _fail,
    _opaque,
    _proposal_body,
    _request,
    _request_id,
)

EVENT_SCHEMA = "nexus.g3.host-approval-event.v1"
CORRELATION_SCHEMA = "nexus.g3.host-approval-correlation.v1"
CANDIDATE_SCHEMA = "nexus.g3.host-decision-evidence-candidate.v1"
RESOLVED_METHOD = "serverRequest/resolved"
MAX_CONSUMED_TOKENS = 192
DISPOSITIONS = frozenset({"EXPLICIT_APPROVE", "EXPLICIT_DENY", "AUTO_RESOLVED", "CLEARED",
                          "TIMED_OUT", "DUPLICATE", "MISMATCH", "UNKNOWN"})
_CONSUMED = re.compile(r"(?:request|approval|event):[0-9a-f]{64}\Z")


def _replay_state(value: Any) -> None:
    if type(value) is not frozenset or len(value) > MAX_CONSUMED_TOKENS or any(
            type(item) is not str or not _CONSUMED.fullmatch(item) for item in value):
        _fail()


def _identity(request: dict) -> dict:
    params = request["params"]
    return {"request_id": request["id"], "thread_id": params["threadId"],
            "turn_id": params["turnId"], "item_id": params["itemId"],
            "approval_id": params["approvalId"]}


def _checked_identity(value: Any) -> dict:
    identity = exact(value, {"request_id", "thread_id", "turn_id", "item_id", "approval_id"})
    _request_id(identity["request_id"])
    for key in ("thread_id", "turn_id", "item_id"):
        _opaque(identity[key])
    if identity["approval_id"] is not None:
        _opaque(identity["approval_id"])
    return identity


@dataclass(frozen=True, slots=True)
class HostApprovalProposal:
    canonical_body: bytes
    proposal_id: str

    def to_dict(self) -> dict:
        return g3.parse_input(self.canonical_body)


@dataclass(frozen=True, slots=True)
class HostApprovalEvent:
    canonical_body: bytes
    event_id: str

    def to_dict(self) -> dict:
        return g3.parse_input(self.canonical_body)


@dataclass(frozen=True, slots=True)
class HostApprovalCorrelation:
    disposition: str
    proposal_id: str
    event_id: str
    consumed_tokens: frozenset[str]
    candidate_evidence: bytes | None
    schema_version: str = CORRELATION_SCHEMA
    basis: str = "OFFLINE_CONTRACT_ONLY"
    owner_authenticated: bool = False
    dispatch_authority: str = "none"

    def __post_init__(self) -> None:
        try:
            if (type(self.disposition) is not str or self.disposition not in DISPOSITIONS
                    or self.schema_version != CORRELATION_SCHEMA or self.basis != "OFFLINE_CONTRACT_ONLY"
                    or self.owner_authenticated is not False or self.dispatch_authority != "none"):
                _fail()
            g3._reference(self.proposal_id, "host-approval-proposal")
            g3._reference(self.event_id, "host-approval-event")
            _replay_state(self.consumed_tokens)
            if (self.candidate_evidence is not None) != (self.disposition == "EXPLICIT_APPROVE"):
                _fail()
            if self.candidate_evidence is not None:
                candidate = g3.parse_input(self.candidate_evidence)
                exact(candidate, {"schema_version", "proposal_id", "subject_id", "scope_sha256", "event_id",
                                  "identity", "explicit_decision", "disposition", "basis", "owner_authenticated",
                                  "approval_authority", "dispatch_authority"})
                if (candidate["schema_version"] != CANDIDATE_SCHEMA or candidate["proposal_id"] != self.proposal_id
                        or candidate["event_id"] != self.event_id or candidate["explicit_decision"] != "accept"
                        or candidate["disposition"] != self.disposition or candidate["basis"] != self.basis
                        or candidate["owner_authenticated"] is not False or candidate["approval_authority"] != "none"
                        or candidate["dispatch_authority"] != "none"):
                    _fail()
                g3._reference(candidate["subject_id"], "subject")
                sha(candidate["scope_sha256"])
                _checked_identity(candidate["identity"])
        except G1Error:
            _fail()


def _checked_proposal(value: Any) -> dict:
    if type(value) is not HostApprovalProposal:
        _fail()
    body = _proposal_body(value.to_dict())
    raw = g3._canonical(body)
    if raw != value.canonical_body or g3._id("host-approval-proposal", raw) != value.proposal_id:
        _fail()
    return body


def proposal(native_request: Any, requested_subject: g3.Subject, requested_scope: Any,
             effect_summary: Any) -> HostApprovalProposal:
    """Bind a native command request to the exact, independently supplied G3 use."""
    try:
        # Detach all caller-owned structures before normalization.
        native_request = g3.parse_input(g3._canonical(native_request))
        requested_scope = g3.parse_input(g3._canonical(requested_scope))
        effect_summary = g3.parse_input(g3._canonical(effect_summary))
        if type(requested_subject) is not g3.Subject or g3.subject(requested_subject.to_dict()) != requested_subject:
            _fail()
        normalized_scope = g3._scope(requested_scope)
        material = requested_subject.to_dict()
        if "account_context" in material and material["account_context"] != normalized_scope.get("account_context"):
            _fail()
        body = _proposal_body({"schema_version": PROPOSAL_SCHEMA, "native_request": native_request,
                               "subject_id": requested_subject.subject_id, "scope": normalized_scope,
                               "scope_sha256": _digest(normalized_scope), "requested_action": material["action"],
                               "effect_summary": effect_summary})
        raw = g3._canonical(body)
        return HostApprovalProposal(raw, g3._id("host-approval-proposal", raw))
    except G1Error:
        _fail()


def _event_body(value: Any) -> dict:
    exact(value, {"schema_version", "proposal_id", "subject_id", "scope_sha256", "identity",
                  "native_message", "observation"})
    if value["schema_version"] != EVENT_SCHEMA:
        _fail()
    g3._reference(value["proposal_id"], "host-approval-proposal")
    g3._reference(value["subject_id"], "subject")
    sha(value["scope_sha256"])
    _checked_identity(value["identity"])
    observation = exact(value["observation"], {"reviewer", "resolution"})
    if (observation["reviewer"] not in ("user", "auto_review", "unknown") or
            observation["resolution"] not in ("explicit", "auto_resolved", "cleared", "timed_out", "unknown")):
        _fail()
    message = value["native_message"]
    if type(message) is not dict:
        _fail()
    if set(message) == {"id", "result"}:
        _request_id(message["id"])
        result = exact(message["result"], {"decision"})
        if result["decision"] not in ("accept", "decline", "cancel", "acceptForSession"):
            _fail()
    elif set(message) == {"method", "params"}:
        if message["method"] != RESOLVED_METHOD:
            _fail()
        params = exact(message["params"], {"threadId", "requestId"})
        _opaque(params["threadId"])
        _request_id(params["requestId"])
    else:
        _fail()
    return value


def event(bound_proposal: HostApprovalProposal, native_message: Any, *, observation: Any = None) -> HostApprovalEvent:
    """Record a declared observation and its pending-request context, not human proof.

    Native responses have no G3 subject/scope fields. Context is bound separately
    by the offline adapter; it is never invented as a field on the native wire.
    """
    try:
        pending = _checked_proposal(bound_proposal)
        body = {"schema_version": EVENT_SCHEMA, "proposal_id": bound_proposal.proposal_id,
                "subject_id": pending["subject_id"], "scope_sha256": pending["scope_sha256"],
                "identity": _identity(pending["native_request"]), "native_message": native_message,
                "observation": observation if observation is not None else {"reviewer": "unknown", "resolution": "unknown"}}
        body = _event_body(g3.parse_input(g3._canonical(body)))
        raw = g3._canonical(body)
        return HostApprovalEvent(raw, g3._id("host-approval-event", raw))
    except G1Error:
        _fail()


def _replay_token(kind: str, value: Any) -> str:
    return kind + ":" + _digest({"kind": kind, "value": value})


def correlate(pending_proposal: HostApprovalProposal, observed_event: HostApprovalEvent,
              consumed_tokens: frozenset[str]) -> HostApprovalCorrelation:
    """Pure one-use transition; callers must carry forward the returned replay set.

    Replay state is mandatory: there is no implicit new/reset trace on each call.
    This bounded set is ordinary caller-owned data, not a durable protected store.
    Matching terminal outcomes consume IDs, including deny/clear/timeout/unknown.
    Mismatched messages do not consume another pending request. Nothing issues a grant.
    """
    try:
        pending = _checked_proposal(pending_proposal)
        if type(observed_event) is not HostApprovalEvent:
            _fail()
        observed = _event_body(observed_event.to_dict())
        raw = g3._canonical(observed)
        if raw != observed_event.canonical_body or g3._id("host-approval-event", raw) != observed_event.event_id:
            _fail()
        _replay_state(consumed_tokens)

        def result(disposition: str, consumed=consumed_tokens, candidate=None):
            return HostApprovalCorrelation(disposition, pending_proposal.proposal_id, observed_event.event_id,
                                           consumed, candidate)

        identity = observed["identity"]
        native = observed["native_message"]
        native_id = native["id"] if "id" in native else native["params"]["requestId"]
        keys = {_replay_token("request", identity["request_id"]), _replay_token("request", native_id),
                _replay_token("event", observed_event.event_id)}
        if identity["approval_id"] is not None:
            keys.add(_replay_token("approval", identity["approval_id"]))
        if keys & consumed_tokens:
            return result("DUPLICATE")
        if (observed["proposal_id"] != pending_proposal.proposal_id or observed["subject_id"] != pending["subject_id"]
                or observed["scope_sha256"] != pending["scope_sha256"] or identity != _identity(pending["native_request"])
                or type(native_id) is not type(identity["request_id"]) or native_id != identity["request_id"]
                or ("params" in native and native["params"]["threadId"] != identity["thread_id"])):
            return result("MISMATCH")
        next_consumed = consumed_tokens | keys
        if len(next_consumed) > MAX_CONSUMED_TOKENS:
            return result("UNKNOWN")
        observation = observed["observation"]
        resolution = observation["resolution"]
        if resolution == "cleared":
            disposition = "CLEARED"
        elif resolution == "timed_out":
            disposition = "TIMED_OUT"
        elif resolution == "auto_resolved" or observation["reviewer"] == "auto_review":
            disposition = "AUTO_RESOLVED"
        elif observation["reviewer"] == "user" and resolution == "explicit" and "result" in native:
            decision = native["result"]["decision"]
            disposition = "EXPLICIT_APPROVE" if decision == "accept" else (
                "EXPLICIT_DENY" if decision in ("decline", "cancel") else "UNKNOWN")
        else:
            disposition = "UNKNOWN"
        candidate = None
        if disposition == "EXPLICIT_APPROVE":
            candidate = g3._canonical({"schema_version": CANDIDATE_SCHEMA,
                "proposal_id": pending_proposal.proposal_id, "subject_id": pending["subject_id"],
                "scope_sha256": pending["scope_sha256"], "event_id": observed_event.event_id,
                "identity": identity, "explicit_decision": "accept", "disposition": disposition,
                "basis": "OFFLINE_CONTRACT_ONLY", "owner_authenticated": False,
                "approval_authority": "none", "dispatch_authority": "none"})
        return result(disposition, next_consumed, candidate)
    except G1Error:
        _fail()
