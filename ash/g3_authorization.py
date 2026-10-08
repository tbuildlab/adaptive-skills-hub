"""G3 Phase 2A pure contracts. Real Owner admission is deliberately disabled.

Records and decisions are data, never execution grants. The private fixture
predicate labels every result TEST_FIXTURE_ONLY. It is not an Owner adapter.
No consumer, CLI, dispatcher, persistence, credential or provider integration.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Any

from .capabilities import CAPABILITY_ID_RE
from .ecosystem_models import (
    EcosystemError, canonical_json_bytes, parse_json_bytes, validate_typed_id,
)
from .g1_profiles import G1Error, SECRET_IDENTIFIER_RE, bounded, exact, integer, sha, token, tokens

MAX_BYTES = 65536
MAX_RECORDS = 64
SUBJECT_SCHEMA = "nexus.g3.subject.v1"
GRANT_SCHEMA = "nexus.g3.grant.v1"
REVOCATION_SCHEMA = "nexus.g3.revocation.v1"
DECISION_SCHEMA = "nexus.g3.eligibility-decision.v1"
OPERATIONS = frozenset({"read", "write", "execute", "network", "delegate"})
_TOOL = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,95}\Z")
REASON_CODES = frozenset({
    "G3_INVALID_INPUT", "G3_APPROVAL_ORIGIN_UNVERIFIED",
    "G3_CAPABILITY_UNAPPROVED", "G3_CAPABILITY_SUBJECT_MISMATCH",
    "G3_CAPABILITY_EVIDENCE_UNVERIFIED", "G3_APPROVAL_NOT_EFFECTIVE",
    "G3_CAPABILITY_EXPIRED", "G3_CAPABILITY_REVOKED",
    "G3_CAPABILITY_SCOPE_DENIED", "G3_CAPABILITY_UNAVAILABLE",
    "G3_TASK_AUTHORITY_REQUIRED", "G3_HOST_AUTHORITY_REQUIRED",
    "G3_G1_RESTRICTION_FAILED", "G3_G2_RESTRICTION_FAILED", "G3_ELIGIBLE",
})


class G3Error(ValueError):
    """Invalid data; no input values appear in diagnostics."""


def _fail() -> None:
    raise G3Error("G3_INVALID_INPUT")


def _canonical(value: Any) -> bytes:
    try:
        bounded(value)
        return canonical_json_bytes(value, maximum_bytes=MAX_BYTES)
    except (G1Error, EcosystemError, UnicodeError, RecursionError):
        _fail()


def parse_input(raw: bytes) -> Any:
    """Duplicate-key-safe bounded JSON, sharing the frozen parser unchanged."""
    try:
        value = parse_json_bytes(raw, maximum_bytes=MAX_BYTES, label="G3 input")
        _canonical(value)
        return value
    except EcosystemError:
        _fail()


def _id(kind: str, body: bytes) -> str:
    # Isolated domain: do not extend Slice 3C's frozen typed-ID domains.
    digest = hashlib.sha256(("nexus.g3." + kind + ".v1\0").encode() + body).hexdigest()
    return "nexus.g3." + kind + ".v1:" + digest


def _reference(value: Any, kind: str) -> str:
    prefix = "nexus.g3." + kind + ".v1:"
    if type(value) is not str or not value.startswith(prefix):
        _fail()
    sha(value[len(prefix):])
    return value


def _capability(value: Any) -> str:
    if (type(value) is not str or len(value) > 128 or not CAPABILITY_ID_RE.fullmatch(value)
            or SECRET_IDENTIFIER_RE.fullmatch(value)):
        _fail()
    return value


def _check(value: Any, fields: set[str], schema: str) -> dict:
    result = exact(value, fields)
    if result["schema_version"] != schema:
        _fail()
    return result


def _scope(value: Any) -> dict:
    required = {"workspace_id", "project_id", "task_classes", "operations"}
    if type(value) is not dict or not required <= set(value) <= required | {"task_id", "account_context"}:
        _fail()
    result = dict(value)
    token(result["workspace_id"])
    token(result["project_id"])
    result["task_classes"] = tokens(result["task_classes"], nonempty=True)
    result["operations"] = tokens(result["operations"], nonempty=True)
    if not set(result["operations"]) <= OPERATIONS:
        _fail()
    for key in ("task_id", "account_context"):
        if key in result:
            token(result[key])
    return result


def _covers(granted: dict, request: dict) -> bool:
    return (
        all(granted[key] == request[key] for key in ("workspace_id", "project_id"))
        and set(request["task_classes"]) <= set(granted["task_classes"])
        and set(request["operations"]) <= set(granted["operations"])
        and all(key not in granted or granted[key] == request.get(key)
                for key in ("task_id", "account_context"))
    )


def _evidence(value: Any) -> None:
    exact(value, {"ref", "sha256"})
    token(value["ref"])
    sha(value["sha256"])


@dataclass(frozen=True, slots=True)
class Subject:
    canonical_body: bytes
    subject_id: str

    def to_dict(self) -> dict:
        return parse_input(self.canonical_body)


@dataclass(frozen=True, slots=True)
class ApprovalGrant:
    canonical_body: bytes
    grant_id: str

    def to_dict(self) -> dict:
        return parse_input(self.canonical_body)


@dataclass(frozen=True, slots=True)
class Revocation:
    canonical_body: bytes
    revocation_id: str

    def to_dict(self) -> dict:
        return parse_input(self.canonical_body)


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


def subject(value: Any) -> Subject:
    """Three closed material envelopes; only explicit display_title is cosmetic."""
    try:
        _canonical(value)
        common = {"schema_version", "capability_id", "kind", "provider", "action"}
        kinds = {
            "local_adapter": {"source_ref", "revision", "content_sha256", "config_sha256"},
            "local_component": {"source_id", "component_revision_id", "config_sha256"},
            "mcp_tool": {"server_ref", "tool_name", "revision", "contract_sha256",
                         "config_sha256", "account_context"},
        }
        if type(value) is not dict or type(value.get("kind")) is not str or value["kind"] not in kinds:
            _fail()
        fields = common | kinds[value["kind"]]
        if set(value) not in (fields, fields | {"display_title"}):
            _fail()
        body = {key: value[key] for key in fields}
        _check(body, fields, SUBJECT_SCHEMA)
        _capability(body["capability_id"])
        for key in ("provider", "action", "source_ref", "server_ref", "revision", "account_context"):
            if key in body:
                token(body[key])
        for key in ("content_sha256", "contract_sha256", "config_sha256"):
            if key in body:
                sha(body[key])
        if body["kind"] == "local_component":
            validate_typed_id(body["source_id"], "source")
            validate_typed_id(body["component_revision_id"], "component-revision")
        if "tool_name" in body and (type(body["tool_name"]) is not str or not _TOOL.fullmatch(body["tool_name"])
                                    or SECRET_IDENTIFIER_RE.fullmatch(body["tool_name"])):
            _fail()
        if "display_title" in value and type(value["display_title"]) is not str:
            _fail()
        raw = _canonical(body)
        return Subject(raw, _id("subject", raw))
    except (G1Error, EcosystemError):
        _fail()


def approval_grant(value: Any) -> ApprovalGrant:
    """Validate shape/identity, never authenticate the issuer or evidence."""
    try:
        _canonical(value)
        fields = {"schema_version", "capability_id", "subject_id", "subject_sha256", "scope",
                  "effective_at", "expires_at", "issuer_ref", "decision_evidence"}
        if type(value) is not dict or set(value) not in (fields, fields | {"review"}):
            _fail()
        body = dict(value)
        _check(body, set(body), GRANT_SCHEMA)
        _capability(body["capability_id"])
        _reference(body["subject_id"], "subject")
        sha(body["subject_sha256"])
        if body["subject_id"].rsplit(":", 1)[1] != body["subject_sha256"]:
            _fail()
        body["scope"] = _scope(body["scope"])
        integer(body["effective_at"])
        integer(body["expires_at"], nullable=True)
        if body["expires_at"] is not None and body["expires_at"] <= body["effective_at"]:
            _fail()
        token(body["issuer_ref"])
        _evidence(body["decision_evidence"])
        if "review" in body:
            review = exact(body["review"], {"subject_id", "evidence", "provenance_ref"})
            if review["subject_id"] != body["subject_id"]:
                _fail()
            _evidence(review["evidence"])
            token(review["provenance_ref"])
        raw = _canonical(body)
        return ApprovalGrant(raw, _id("grant", raw))
    except G1Error:
        _fail()


def revocation(value: Any) -> Revocation:
    try:
        _canonical(value)
        body = _check(value, {"schema_version", "grant_id", "effective_at", "issuer_ref",
                              "decision_evidence", "reason"}, REVOCATION_SCHEMA)
        _reference(body["grant_id"], "grant")
        integer(body["effective_at"])
        token(body["issuer_ref"])
        _evidence(body["decision_evidence"])
        token(body["reason"])
        raw = _canonical(body)
        return Revocation(raw, _id("revocation", raw))
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
