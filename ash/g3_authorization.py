"""G3 Phase 2A pure contracts. Real Owner admission is deliberately disabled.

Records and decisions are data, never execution grants. The private fixture
predicate labels every result TEST_FIXTURE_ONLY. It is not an Owner adapter.
No consumer, CLI, dispatcher, persistence, credential or provider integration.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
from typing import Any
from .g1_profiles import G1Error, integer, sha
from .g3_grant_codec import (
    ApprovalGrant,
    DECISION_SCHEMA,
    G3Error,
    GRANT_SCHEMA,
    MAX_BYTES,
    MAX_RECORDS,
    OPERATIONS,
    REASON_CODES,
    REVOCATION_SCHEMA,
    Revocation,
    SUBJECT_SCHEMA,
    Subject,
    _TOOL,
    _canonical,
    _capability,
    _check,
    _evidence,
    _fail,
    _id,
    _reference,
    _scope,
    approval_grant,
    parse_input,
    revocation,
    subject,
)


def _covers(granted: dict, request: dict) -> bool:
    return (
        all(granted[key] == request[key] for key in ("workspace_id", "project_id"))
        and set(request["task_classes"]) <= set(granted["task_classes"])
        and set(request["operations"]) <= set(granted["operations"])
        and all(key not in granted or granted[key] == request.get(key)
                for key in ("task_id", "account_context"))
    )


@dataclass(frozen=True, slots=True)
class EligibilityDecision:
    status: str
    reason_codes: tuple[str, ...]
    subject_id: str | None
    grant_id: str | None
    request_sha256: str | None
    evaluated_at: int | None
    basis: str
    schema_version: str = DECISION_SCHEMA
    dispatch_authority: str = "none"

    def __post_init__(self) -> None:
        try:
            if (self.schema_version != DECISION_SCHEMA or self.dispatch_authority != "none"
                    or self.basis not in ("REAL_ADMISSION_DISABLED", "TEST_FIXTURE_ONLY")
                    or type(self.reason_codes) is not tuple or not 1 <= len(self.reason_codes) <= 16
                    or any(type(code) is not str or code not in REASON_CODES for code in self.reason_codes)
                    or len(set(self.reason_codes)) != len(self.reason_codes)
                    or self.status != ("ELIGIBLE" if self.reason_codes == ("G3_ELIGIBLE",) else "NOT_ELIGIBLE")):
                _fail()
            if self.status == "ELIGIBLE" and (self.basis != "TEST_FIXTURE_ONLY" or any(
                    value is None for value in (self.grant_id, self.subject_id, self.request_sha256, self.evaluated_at))):
                _fail()
            for value, kind in ((self.subject_id, "subject"), (self.grant_id, "grant")):
                if value is not None:
                    _reference(value, kind)
            if self.request_sha256 is not None:
                sha(self.request_sha256)
            integer(self.evaluated_at, nullable=True)
        except G1Error:
            _fail()


def _evaluate(
    requested_subject: Subject, grants: tuple[ApprovalGrant, ...], revocations: tuple[Revocation, ...],
    requested_scope: dict, *, now: int, technical_available: bool, task_authorized: bool,
    host_authorized: bool, g1_passed: bool, g2_passed: bool,
    fixture_grant_ids: frozenset[str] | None = None,
    fixture_revocation_ids: frozenset[str] | None = None,
) -> EligibilityDecision:
    """Internal predicate: supplying fixture IDs can only produce TEST_FIXTURE_ONLY."""
    basis = "REAL_ADMISSION_DISABLED" if fixture_grant_ids is None else "TEST_FIXTURE_ONLY"
    subject_id = request_digest = checked_now = None

    def decision(codes: list[str], grant_id: str | None = None) -> EligibilityDecision:
        return EligibilityDecision("ELIGIBLE" if codes == ["G3_ELIGIBLE"] else "NOT_ELIGIBLE",
                                   tuple(codes), subject_id, grant_id, request_digest, checked_now, basis)

    try:
        integer(now)
        checked_now = now
        if type(requested_subject) is not Subject or subject(requested_subject.to_dict()) != requested_subject:
            _fail()
        subject_id = requested_subject.subject_id
        request = _scope(parse_input(_canonical(requested_scope)))
        request_digest = hashlib.sha256(_canonical(request)).hexdigest()
        gates = (technical_available, task_authorized, host_authorized, g1_passed, g2_passed)
        if any(type(value) is not bool for value in gates):
            _fail()
        if type(grants) is not tuple or type(revocations) is not tuple or max(len(grants), len(revocations)) > MAX_RECORDS:
            _fail()
        for rows, cls, factory in ((grants, ApprovalGrant, approval_grant), (revocations, Revocation, revocation)):
            if any(type(row) is not cls or factory(row.to_dict()) != row for row in rows):
                _fail()
        if len({g.grant_id for g in grants}) != len(grants) or len({r.revocation_id for r in revocations}) != len(revocations):
            _fail()
        if fixture_grant_ids is None:
            return decision(["G3_APPROVAL_ORIGIN_UNVERIFIED"])
        if type(fixture_grant_ids) is not frozenset or type(fixture_revocation_ids) is not frozenset:
            _fail()
        # Caller-supplied JSON never reaches this private, explicitly test-only seam.
        if any(g.grant_id not in fixture_grant_ids for g in grants) or any(
                r.revocation_id not in fixture_revocation_ids for r in revocations):
            return decision(["G3_APPROVAL_ORIGIN_UNVERIFIED"])
        if not grants:
            return decision(["G3_CAPABILITY_UNAPPROVED"])
        material = requested_subject.to_dict()
        denials = []
        for grant in sorted(grants, key=lambda row: row.grant_id):
            body = grant.to_dict()
            code = None
            if body["capability_id"] != material["capability_id"]:
                code = "G3_CAPABILITY_UNAPPROVED"
            elif body["subject_id"] != subject_id:
                code = "G3_CAPABILITY_SUBJECT_MISMATCH"
            elif material["kind"] == "local_component" and "review" not in body:
                code = "G3_CAPABILITY_EVIDENCE_UNVERIFIED"
            elif any(r.to_dict()["grant_id"] == grant.grant_id and r.to_dict()["effective_at"] <= now
                     for r in revocations):
                code = "G3_CAPABILITY_REVOKED"
            elif now < body["effective_at"]:
                code = "G3_APPROVAL_NOT_EFFECTIVE"
            elif body["expires_at"] is not None and now >= body["expires_at"]:
                code = "G3_CAPABILITY_EXPIRED"
            elif not _covers(body["scope"], request) or (
                    "account_context" in material and (
                        material["account_context"] != request.get("account_context") or
                        material["account_context"] != body["scope"].get("account_context"))):
                code = "G3_CAPABILITY_SCOPE_DENIED"
            if code:
                if code not in denials:
                    denials.append(code)
                continue
            constraints = [code for passed, code in zip(gates, (
                "G3_CAPABILITY_UNAVAILABLE", "G3_TASK_AUTHORITY_REQUIRED", "G3_HOST_AUTHORITY_REQUIRED",
                "G3_G1_RESTRICTION_FAILED", "G3_G2_RESTRICTION_FAILED")) if not passed]
            return decision(constraints or ["G3_ELIGIBLE"], grant.grant_id)
        return decision(denials)
    except (G3Error, G1Error):
        return decision(["G3_INVALID_INPUT"])


def evaluate_eligibility(
    requested_subject: Subject, grants: tuple[ApprovalGrant, ...], revocations: tuple[Revocation, ...],
    requested_scope: dict, *, now: int, technical_available: bool, task_authorized: bool,
    host_authorized: bool, g1_passed: bool, g2_passed: bool,
) -> EligibilityDecision:
    """Production-facing contract only: no U1 adapter exists, so always deny.

    Explicit upstream gates are supplied facts for composition, not observations
    or new grants. Copied EligibilityDecision JSON is not accepted as an input.
    """
    return _evaluate(requested_subject, grants, revocations, requested_scope, now=now,
                     technical_available=technical_available, task_authorized=task_authorized,
                     host_authorized=host_authorized, g1_passed=g1_passed, g2_passed=g2_passed)
