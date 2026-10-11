"""Pure bounded subject/grant/revocation encoding; no issuer or evaluator.

Shape and hashes never authenticate supplied evidence or create authority.
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
