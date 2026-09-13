"""Closed, deterministic data primitives for Slice 3C quarantine records.

This module deliberately exposes data validation and identity construction only.
It has no acquisition, routing, installation, execution, Host, MCP, or Agent
delegation capability.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
import unicodedata
from typing import Any, Iterable, Mapping, NoReturn, Sequence


MAX_JSON_DEPTH = 32
MAX_INT = 9_223_372_036_854_775_807
MAX_RECORD_BYTES = 2_097_152
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TOKEN_RE = re.compile(r"^[a-z][a-z0-9._-]{0,63}$")
SOURCE_KEY_RE = re.compile(
    r"^github/[a-z0-9](?:[a-z0-9-]{0,38})/[a-z0-9](?:[a-z0-9._-]{0,99})$"
)
SECRET_IDENTIFIER_RE = re.compile(
    r"(?i)^(?:sk[-_][A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20,}"
    r"|(?:AKIA|ASIA)[0-9A-Z]{16}|xox[A-Za-z]-[A-Za-z0-9-]{8,}|xapp-[A-Za-z0-9-]{8,})$"
)
GIT_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
GIT_SHA256_RE = SHA256_RE

ZERO_AUTHORITY: dict[str, str] = {
    "approval_authority": "none",
    "promotion_authority": "none",
    "activation_authority": "none",
    "routing_authority": "none",
    "installation_authority": "none",
    "execution_authority": "none",
    "host_mapping_authority": "none",
    "mcp_connection_authority": "none",
    "agent_delegation_authority": "none",
}

REASON_CODES = frozenset(
    {
        "ANALYZER_UNAVAILABLE",
        "ARCHIVE_INTEGRITY_INVALID",
        "ARCHIVE_INVALID",
        "ARCHIVE_UNSAFE_ENTRY",
        "CAS_OBJECT_CONFLICT",
        "CAS_QUOTA_EXCEEDED",
        "CAS_ROOT_INVALID",
        "CLASSIFICATION_CONFLICT",
        "CLASSIFICATION_UNRESOLVED",
        "EVALUATION_RECEIPT_INVALID",
        "EVALUATION_RESULT_BLOCKED",
        "INPUT_DIGEST_MISMATCH",
        "INPUT_UNSTABLE",
        "INTERNAL_FAILURE",
        "LICENSE_AMBIGUOUS",
        "LICENSE_CHANGED",
        "LICENSE_MISMATCH",
        "LICENSE_MISSING",
        "LICENSE_UNSUPPORTED",
        "PATH_COLLISION",
        "PATH_INVALID",
        "POLICY_INTEGRITY_INVALID",
        "POLICY_SCHEMA_INVALID",
        "POLICY_UNTRUSTED",
        "PROVENANCE_CONFLICT",
        "PROVENANCE_INSUFFICIENT",
        "RESOURCE_LIMIT_EXCEEDED",
        "SCOUT_DISPOSITION_BLOCKED",
        "SCOUT_RECEIPT_INVALID",
        "SOURCE_IDENTITY_CONFLICT",
        "SOURCE_NOT_ALLOWED",
        "STATE_TRANSITION_INVALID",
        "STATIC_FINDING_BLOCKING",
        "STATIC_FINDING_REJECTED",
        "STATIC_REVIEW_REQUIRED",
        "SUBJECT_MISMATCH",
        "TIME_LIMIT_EXCEEDED",
        "UNSUPPORTED_INPUT",
    }
)

ID_DOMAINS: dict[str, str] = {
    "source": "nexus.ecosystem-source-identity.v1",
    "tree": "nexus.ecosystem-tree-identity.v1",
    "revision": "nexus.ecosystem-revision-identity.v1",
    "component": "nexus.ecosystem-component-identity.v1",
    "component-revision": "nexus.ecosystem-component-revision-identity.v1",
    "comparison": "nexus.ecosystem-comparison-identity.v1",
    "bridge": "nexus.ecosystem-intake-bridge.v1",
    "intake-attempt": "nexus.ecosystem-intake-attempt-identity.v1",
    "intake-attempt-result": "nexus.ecosystem-intake-attempt-result.v1",
    "transition": "nexus.ecosystem-state-transition-receipt.v1",
    "state-record": "nexus.ecosystem-state-record.v1",
    "finding": "nexus.ecosystem-static-finding.v1",
    "static-report": "nexus.ecosystem-static-report.v1",
    "classification": "nexus.ecosystem-component-classification.v1",
    "classification-report": "nexus.ecosystem-classification-report.v1",
}

EVIDENCE_DOMAINS = frozenset(
    {
        "nexus.ecosystem-provenance-evidence.v1",
        "nexus.ecosystem-license-evidence.v1",
    }
)

POSSESSION_STATES = (
    "NOT_PRESENT",
    "MIRRORED_UNREVIEWED",
    "SNAPSHOT_INTEGRITY_VERIFIED",
)
REVIEW_STATES = (
    "NOT_REVIEWED",
    "PROVENANCE_EVIDENCE_COMPLETE",
    "STATIC_SECURITY_EVIDENCE_COMPLETE",
    "SEMANTIC_CLASSIFICATION_COMPLETE",
    "VALIDATION_EVIDENCE_COMPLETE",
    "REVIEW_EVIDENCE_COMPLETE",
)
EVIDENCE_OUTCOMES = ("IN_PROGRESS", "COMPLETE", "INSUFFICIENT_EVIDENCE")
DISPOSITIONS = ("QUARANTINED", "REJECTED")

_BIDI_CONTROLS = frozenset(
    chr(value)
    for value in (
        0x061C,
        0x200E,
        0x200F,
        0x202A,
        0x202B,
        0x202C,
        0x202D,
        0x202E,
        0x2066,
        0x2067,
        0x2068,
        0x2069,
    )
)
_WINDOWS_RESERVED = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{index}" for index in range(1, 10)}
    | {f"lpt{index}" for index in range(1, 10)}
)


class EcosystemError(ValueError):
    """One bounded fail-closed Slice 3C error."""

    def __init__(self, reason_code: str, message: str = "Slice 3C validation failed") -> None:
        if reason_code not in REASON_CODES:
            reason_code = "INTERNAL_FAILURE"
        safe_message = message if isinstance(message, str) else "Slice 3C validation failed"
        safe_message = " ".join(safe_message.split())[:256]
        self.reason_code = reason_code
        super().__init__(safe_message)


def _fail(code: str, message: str) -> NoReturn:
    raise EcosystemError(code, message)


def _parse_int(value: str) -> int:
    if not re.fullmatch(r"0|-?[1-9][0-9]*", value) or len(value.lstrip("-")) > 19:
        _fail("POLICY_SCHEMA_INVALID", "JSON integer is outside the closed representation")
    number = int(value)
    if number < 0 or number > MAX_INT:
        _fail("POLICY_SCHEMA_INVALID", "JSON integer is outside the closed range")
    return number


def _reject_number(_value: str) -> NoReturn:
    _fail("POLICY_SCHEMA_INVALID", "Non-integer JSON number is forbidden")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("POLICY_SCHEMA_INVALID", "Duplicate JSON object key")
        result[key] = value
    return result


def _validate_json_graph(value: Any, *, maximum_depth: int = MAX_JSON_DEPTH) -> None:
    stack: list[tuple[Any, int]] = [(value, 0)]
    while stack:
        item, depth = stack.pop()
        if type(item) is dict:
            if depth >= maximum_depth:
                _fail("POLICY_SCHEMA_INVALID", "JSON nesting limit exceeded")
            for key, nested in item.items():
                if type(key) is not str:
                    _fail("POLICY_SCHEMA_INVALID", "JSON object key must be a string")
                if unicodedata.normalize("NFC", key) != key:
                    _fail("POLICY_SCHEMA_INVALID", "JSON object key is not NFC normalized")
                stack.append((nested, depth + 1))
        elif type(item) is list:
            if depth >= maximum_depth:
                _fail("POLICY_SCHEMA_INVALID", "JSON nesting limit exceeded")
            stack.extend((nested, depth + 1) for nested in item)
        elif type(item) is str:
            if unicodedata.normalize("NFC", item) != item:
                _fail("POLICY_SCHEMA_INVALID", "JSON string is not NFC normalized")
        elif type(item) is int:
            if item < 0 or item > MAX_INT:
                _fail("POLICY_SCHEMA_INVALID", "JSON integer is outside the closed range")
        elif item is None or type(item) is bool:
            continue
        else:
            _fail("POLICY_SCHEMA_INVALID", "JSON value has a forbidden concrete type")


def parse_json_bytes(
    raw: bytes,
    *,
    maximum_bytes: int = MAX_RECORD_BYTES,
    label: str = "Slice 3C JSON",
) -> Any:
    """Parse strict bounded JSON into exact built-in containers."""
    if type(raw) is not bytes or len(raw) > maximum_bytes:
        _fail("RESOURCE_LIMIT_EXCEEDED", f"{label} exceeds its byte limit")
    if raw.startswith(b"\xef\xbb\xbf"):
        _fail("POLICY_SCHEMA_INVALID", f"{label} contains a UTF-8 BOM")
    try:
        text = raw.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_pairs,
            parse_int=_parse_int,
            parse_float=_reject_number,
            parse_constant=_reject_number,
        )
    except EcosystemError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise EcosystemError("POLICY_SCHEMA_INVALID", f"{label} is malformed") from None
    _validate_json_graph(value)
    return value


def canonical_json_bytes(value: Any, *, maximum_bytes: int = MAX_RECORD_BYTES) -> bytes:
    _validate_json_graph(value)
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        _fail("POLICY_SCHEMA_INVALID", "Value is not canonical JSON")
    if len(raw) > maximum_bytes:
        _fail("RESOURCE_LIMIT_EXCEEDED", "Canonical record exceeds its byte limit")
    return raw


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def domain_sha256(domain: str, body: Mapping[str, Any]) -> str:
    if type(domain) is not str or not domain.startswith("nexus.ecosystem-"):
        _fail("POLICY_SCHEMA_INVALID", "Identity domain is invalid")
    if type(body) is not dict:
        _fail("POLICY_SCHEMA_INVALID", "Identity body must be an exact object")
    return hashlib.sha256(domain.encode("utf-8") + b"\n" + canonical_json_bytes(body)).hexdigest()


def typed_id(kind: str, body: Mapping[str, Any], *, domain: str | None = None) -> str:
    selected = domain or ID_DOMAINS.get(kind)
    if selected is None:
        _fail("POLICY_SCHEMA_INVALID", "Typed identity kind is unknown")
    return f"{kind}/{domain_sha256(selected, body)}"


def validate_sha256(value: Any, label: str = "digest") -> str:
    if type(value) is not str or not SHA256_RE.fullmatch(value):
        _fail("POLICY_SCHEMA_INVALID", f"{label} is invalid")
    return value


def validate_typed_id(value: Any, kind: str | None = None) -> str:
    if type(value) is not str or "/" not in value:
        _fail("POLICY_SCHEMA_INVALID", "Typed identifier is invalid")
    prefix, digest = value.split("/", 1)
    # ``candidate`` is the frozen Slice 2 external reference.  Slice 3C can
    # validate it but never constructs or reuses it as a Slice 3C identity.
    allowed = set(ID_DOMAINS) | {"evidence", "candidate"}
    if prefix not in allowed or (kind is not None and prefix != kind):
        _fail("POLICY_SCHEMA_INVALID", "Typed identifier kind is invalid")
    validate_sha256(digest, "typed identifier digest")
    return value


def validate_token(value: Any, label: str = "token") -> str:
    if (
        type(value) is not str
        or not TOKEN_RE.fullmatch(value)
        or SECRET_IDENTIFIER_RE.fullmatch(value)
    ):
        _fail("POLICY_SCHEMA_INVALID", f"{label} is invalid")
    return value


def validate_exact_keys(value: Any, fields: Iterable[str], label: str) -> dict[str, Any]:
    expected = set(fields)
    if type(value) is not dict or set(value) != expected:
        _fail("POLICY_SCHEMA_INVALID", f"{label} schema is not closed")
    return value


def validate_authority(value: Any) -> dict[str, str]:
    validate_exact_keys(value, ZERO_AUTHORITY, "authority")
    if any(type(value[key]) is not str or value[key] != expected for key, expected in ZERO_AUTHORITY.items()):
        _fail("POLICY_SCHEMA_INVALID", "Authority must remain exactly none")
    return dict(ZERO_AUTHORITY)


def zero_authority() -> dict[str, str]:
    return dict(ZERO_AUTHORITY)


def validate_reason_codes(value: Any, *, required: bool = False) -> list[str]:
    if type(value) is not list or len(value) > 32:
        _fail("POLICY_SCHEMA_INVALID", "Reason-code list is invalid")
    if any(type(item) is not str or item not in REASON_CODES for item in value):
        _fail("POLICY_SCHEMA_INVALID", "Reason-code list contains an unknown value")
    if value != sorted(set(value)):
        _fail("POLICY_SCHEMA_INVALID", "Reason-code list is not canonical")
    if required and not value:
        _fail("POLICY_SCHEMA_INVALID", "A failure result requires a reason code")
    return list(value)


def source_identity(provider: str, canonical_repository: str) -> str:
    if provider != "github" or type(canonical_repository) is not str:
        _fail("SOURCE_IDENTITY_CONFLICT", "Source identity is invalid")
    pieces = canonical_repository.split("/")
    if len(pieces) != 2:
        _fail("SOURCE_IDENTITY_CONFLICT", "Repository identity is invalid")
    if any(SECRET_IDENTIFIER_RE.fullmatch(piece) for piece in pieces):
        _fail("SOURCE_IDENTITY_CONFLICT", "Repository identity is invalid")
    repository = "/".join(piece.lower() for piece in pieces)
    if not SOURCE_KEY_RE.fullmatch(f"github/{repository}"):
        _fail("SOURCE_IDENTITY_CONFLICT", "Repository identity is invalid")
    return typed_id("source", {"provider": "github", "repository": repository})


def normalize_candidate_path(path: Any) -> str:
    if type(path) is not str:
        _fail("PATH_INVALID", "Candidate path is not text")
    normalized = unicodedata.normalize("NFC", path)
    if not normalized or len(normalized.encode("utf-8")) > 512:
        _fail("PATH_INVALID", "Candidate path length is invalid")
    if normalized.startswith(("/", "\\")) or "\\" in normalized or ":" in normalized:
        _fail("PATH_INVALID", "Candidate path must be relative POSIX form")
    if re.match(r"^[A-Za-z]:", normalized) or normalized.casefold().startswith(("file:", "http:", "https:")):
        _fail("PATH_INVALID", "Candidate path form is forbidden")
    segments = normalized.split("/")
    if not 1 <= len(segments) <= 32:
        _fail("PATH_INVALID", "Candidate path depth is invalid")
    for segment in segments:
        if (
            not segment
            or segment in {".", ".."}
            or segment.endswith((".", " "))
            or len(segment.encode("utf-8")) > 128
            or any(ord(char) < 32 or ord(char) == 127 for char in segment)
            or any(char in _BIDI_CONTROLS for char in segment)
        ):
            _fail("PATH_INVALID", "Candidate path segment is unsafe")
        base = segment.split(".", 1)[0].casefold()
        if base in _WINDOWS_RESERVED:
            _fail("PATH_INVALID", "Candidate path uses a reserved device name")
    return normalized


def _canonical_sorted_unique_strings(values: Any, *, maximum: int, label: str) -> list[str]:
    if type(values) is not list or len(values) > maximum or any(type(item) is not str for item in values):
        _fail("POLICY_SCHEMA_INVALID", f"{label} list is invalid")
    if values != sorted(set(values), key=lambda item: item.encode("utf-8")):
        _fail("POLICY_SCHEMA_INVALID", f"{label} list is not canonical")
    return list(values)


def build_tree(entries: Sequence[Mapping[str, Any]]) -> tuple[str, dict[str, Any]]:
    if type(entries) is not list:
        _fail("POLICY_SCHEMA_INVALID", "Tree entries are invalid")
    checked: list[dict[str, Any]] = []
    collision_keys: set[str] = set()
    for raw in entries:
        if type(raw) is not dict:
            _fail("POLICY_SCHEMA_INVALID", "Tree entry is invalid")
        allowed = {"path", "kind", "mode", "size", "sha256"}
        if "link_target_sha256" in raw:
            allowed.add("link_target_sha256")
        validate_exact_keys(raw, allowed, "tree entry")
        path = normalize_candidate_path(raw["path"])
        collision = path.casefold()
        if collision in collision_keys:
            _fail("PATH_COLLISION", "Tree paths collide")
        if any(
            collision.startswith(existing + "/") or existing.startswith(collision + "/")
            for existing in collision_keys
        ):
            _fail("PATH_COLLISION", "Tree file paths have an ancestor collision")
        collision_keys.add(collision)
        kind = raw["kind"]
        mode = raw["mode"]
        if kind not in {"regular", "symlink", "hardlink", "gitlink", "archive", "special"}:
            _fail("POLICY_SCHEMA_INVALID", "Tree entry kind is invalid")
        if mode not in {"regular_non_executable", "regular_executable", "link", "gitlink", "special"}:
            _fail("POLICY_SCHEMA_INVALID", "Tree entry mode is invalid")
        has_target = "link_target_sha256" in raw
        valid_pair = (
            (kind in {"regular", "archive"} and mode in {"regular_non_executable", "regular_executable"} and not has_target)
            or (kind in {"symlink", "hardlink"} and mode == "link" and has_target)
            or (kind == "gitlink" and mode == "gitlink" and has_target)
            or (kind == "special" and mode == "special" and not has_target)
        )
        if not valid_pair:
            _fail("POLICY_SCHEMA_INVALID", "Tree kind, mode, and link-target fields disagree")
        size = raw["size"]
        if type(size) is not int or not 0 <= size <= MAX_INT:
            _fail("POLICY_SCHEMA_INVALID", "Tree entry size is invalid")
        item = {
            "path": path,
            "kind": kind,
            "mode": mode,
            "size": size,
            "sha256": validate_sha256(raw["sha256"], "tree entry digest"),
        }
        if "link_target_sha256" in raw:
            item["link_target_sha256"] = validate_sha256(raw["link_target_sha256"], "link target digest")
        checked.append(item)
    checked.sort(key=lambda item: item["path"].encode("utf-8"))
    body = {"entries": checked}
    return typed_id("tree", body), body


def build_revision_identity(
    *, source_id: str, commit_object_format: str, commit_oid: str, input_sha256: str, tree_id: str
) -> str:
    validate_typed_id(source_id, "source")
    validate_typed_id(tree_id, "tree")
    validate_sha256(input_sha256, "input digest")
    if commit_object_format == "git_sha1":
        valid = type(commit_oid) is str and GIT_SHA1_RE.fullmatch(commit_oid)
    elif commit_object_format == "git_sha256":
        valid = type(commit_oid) is str and GIT_SHA256_RE.fullmatch(commit_oid)
    else:
        valid = False
    if not valid:
        _fail("PROVENANCE_CONFLICT", "Commit identity is invalid")
    return typed_id(
        "revision",
        {
            "source_id": source_id,
            "commit_object_format": commit_object_format,
            "commit_oid": commit_oid,
            "input_sha256": input_sha256,
            "tree_id": tree_id,
        },
    )


def build_component_identity(*, source_id: str, component_root: str) -> str:
    validate_typed_id(source_id, "source")
    root = normalize_candidate_path(component_root)
    return typed_id("component", {"source_id": source_id, "component_root": root})


def build_component_revision_identity(
    *, revision_id: str, component_id: str, component_manifest_sha256: str
) -> str:
    validate_typed_id(revision_id, "revision")
    validate_typed_id(component_id, "component")
    validate_sha256(component_manifest_sha256, "component manifest digest")
    return typed_id(
        "component-revision",
        {
            "revision_id": revision_id,
            "component_id": component_id,
            "component_manifest_sha256": component_manifest_sha256,
        },
    )


@dataclass(frozen=True, slots=True)
class StateVector:
    possession_state: str
    review_state: str
    evidence_outcome: str
    disposition: str

    def as_dict(self) -> dict[str, str]:
        return {
            "possession_state": self.possession_state,
            "review_state": self.review_state,
            "evidence_outcome": self.evidence_outcome,
            "disposition": self.disposition,
        }


IMPLICIT_STATE = StateVector("NOT_PRESENT", "NOT_REVIEWED", "IN_PROGRESS", "QUARANTINED")
GENESIS_STATE = StateVector("MIRRORED_UNREVIEWED", "NOT_REVIEWED", "IN_PROGRESS", "QUARANTINED")


def parse_state_vector(value: Any) -> StateVector:
    validate_exact_keys(
        value,
        {"possession_state", "review_state", "evidence_outcome", "disposition"},
        "state vector",
    )
    state = StateVector(
        value["possession_state"],
        value["review_state"],
        value["evidence_outcome"],
        value["disposition"],
    )
    validate_state_vector(state)
    return state


def validate_state_vector(state: StateVector) -> StateVector:
    if type(state) is not StateVector or (
        type(state.possession_state) is not str
        or state.possession_state not in POSSESSION_STATES
        or type(state.review_state) is not str
        or state.review_state not in REVIEW_STATES
        or type(state.evidence_outcome) is not str
        or state.evidence_outcome not in EVIDENCE_OUTCOMES
        or type(state.disposition) is not str
        or state.disposition not in DISPOSITIONS
    ):
        _fail("STATE_TRANSITION_INVALID", "State vector contains an unknown state")
    progressed = state.review_state != "NOT_REVIEWED" or state.evidence_outcome != "IN_PROGRESS"
    if progressed and state.possession_state != "SNAPSHOT_INTEGRITY_VERIFIED":
        _fail("STATE_TRANSITION_INVALID", "Review requires verified snapshot possession")
    if progressed and state.disposition != "QUARANTINED":
        _fail("STATE_TRANSITION_INVALID", "Review progress must remain quarantined")
    if (state.evidence_outcome == "COMPLETE") != (state.review_state == "REVIEW_EVIDENCE_COMPLETE"):
        _fail("STATE_TRANSITION_INVALID", "Terminal review and evidence state disagree")
    if state.disposition == "REJECTED" and state.evidence_outcome == "COMPLETE":
        _fail("STATE_TRANSITION_INVALID", "Rejected state cannot be review-complete")
    if state.disposition not in DISPOSITIONS:
        _fail("STATE_TRANSITION_INVALID", "Disposition is invalid")
    return state


def _next_review_state(current: str) -> str | None:
    index = REVIEW_STATES.index(current)
    return REVIEW_STATES[index + 1] if index + 1 < len(REVIEW_STATES) else None


def build_transition_receipt(
    *,
    subject_id: str,
    subject_sha256: str,
    from_state: StateVector,
    to_state: StateVector,
    transition_axis: str,
    evidence_ids: list[str],
    evaluation_receipt_sha256s: list[str],
    evaluation_profile_id: str | None,
    evaluation_profile_sha256: str | None,
    policy_semantic_sha256: str,
    reason_codes: list[str],
) -> dict[str, Any]:
    _validate_lifecycle_subject_id(subject_id)
    validate_sha256(subject_sha256, "subject digest")
    validate_state_vector(from_state)
    validate_state_vector(to_state)
    if from_state.disposition == "REJECTED":
        _fail("STATE_TRANSITION_INVALID", "Rejected state is terminal")
    if type(evidence_ids) is not list or len(evidence_ids) > 32:
        _fail("STATE_TRANSITION_INVALID", "Transition evidence list is invalid")
    for evidence_id in evidence_ids:
        validate_typed_id(evidence_id)
    if evidence_ids != sorted(set(evidence_ids)):
        _fail("STATE_TRANSITION_INVALID", "Transition evidence list is not canonical")
    if type(evaluation_receipt_sha256s) is not list or len(evaluation_receipt_sha256s) > 16:
        _fail("STATE_TRANSITION_INVALID", "Evaluation receipt list is invalid")
    for digest in evaluation_receipt_sha256s:
        validate_sha256(digest, "evaluation receipt digest")
    if evaluation_receipt_sha256s != sorted(set(evaluation_receipt_sha256s)):
        _fail("STATE_TRANSITION_INVALID", "Evaluation receipt list is not canonical")
    codes = validate_reason_codes(reason_codes, required=transition_axis == "disposition")

    differences = [
        name
        for name in ("possession_state", "review_state", "evidence_outcome", "disposition")
        if getattr(from_state, name) != getattr(to_state, name)
    ]
    review_edge = False
    if transition_axis == "possession":
        allowed = (
            (from_state.possession_state, to_state.possession_state)
            in {
                ("NOT_PRESENT", "MIRRORED_UNREVIEWED"),
                ("MIRRORED_UNREVIEWED", "SNAPSHOT_INTEGRITY_VERIFIED"),
            }
            and differences == ["possession_state"]
        )
    elif transition_axis == "review":
        allowed = (
            _next_review_state(from_state.review_state) == to_state.review_state
            and to_state.review_state != "REVIEW_EVIDENCE_COMPLETE"
            and differences == ["review_state"]
        )
        review_edge = True
    elif transition_axis == "review_evidence_terminal":
        allowed = (
            from_state.review_state == "VALIDATION_EVIDENCE_COMPLETE"
            and from_state.evidence_outcome == "IN_PROGRESS"
            and to_state.review_state == "REVIEW_EVIDENCE_COMPLETE"
            and to_state.evidence_outcome == "COMPLETE"
            and differences == ["review_state", "evidence_outcome"]
        )
        review_edge = True
    elif transition_axis == "evidence_outcome":
        allowed = (
            (from_state.evidence_outcome, to_state.evidence_outcome)
            in {("IN_PROGRESS", "INSUFFICIENT_EVIDENCE"), ("INSUFFICIENT_EVIDENCE", "IN_PROGRESS")}
            and differences == ["evidence_outcome"]
            and bool(evidence_ids)
        )
    elif transition_axis == "disposition":
        allowed = (
            from_state.disposition == "QUARANTINED"
            and to_state.disposition == "REJECTED"
            and differences == ["disposition"]
        )
    else:
        allowed = False
    if not allowed:
        _fail("STATE_TRANSITION_INVALID", "State transition is not permitted")
    if review_edge:
        if (
            len(evaluation_receipt_sha256s) != 1
            or type(evaluation_profile_id) is not str
            or type(evaluation_profile_sha256) is not str
        ):
            _fail("STATE_TRANSITION_INVALID", "Review transition lacks exact evaluation evidence")
        validate_token(evaluation_profile_id, "evaluation profile identifier")
        validate_sha256(evaluation_profile_sha256, "evaluation profile digest")
    elif evaluation_receipt_sha256s or evaluation_profile_id is not None or evaluation_profile_sha256 is not None:
        _fail("STATE_TRANSITION_INVALID", "Non-review transition cannot carry evaluation profile evidence")

    body: dict[str, Any] = {
        "subject_id": subject_id,
        "subject_sha256": subject_sha256,
        "from_state": from_state.as_dict(),
        "to_state": to_state.as_dict(),
        "transition_axis": transition_axis,
        "evidence_ids": list(evidence_ids),
        "evaluation_receipt_sha256s": list(evaluation_receipt_sha256s),
        "evaluation_profile_id": evaluation_profile_id,
        "evaluation_profile_sha256": evaluation_profile_sha256,
        "policy_semantic_sha256": validate_sha256(policy_semantic_sha256, "policy digest"),
        "reason_codes": codes,
        "permitted": True,
        "applied": False,
        "authority": zero_authority(),
    }
    return {
        "schema_version": "nexus.ecosystem-state-transition-receipt.v1",
        "transition_id": typed_id("transition", body),
        **body,
    }


def build_state_record(
    *,
    subject_id: str,
    subject_sha256: str,
    previous_state_record_id: str | None,
    transition: Mapping[str, Any],
) -> dict[str, Any]:
    _validate_lifecycle_subject_id(subject_id)
    validate_sha256(subject_sha256, "subject digest")
    if previous_state_record_id is not None:
        validate_typed_id(previous_state_record_id, "state-record")
    checked_transition = validate_transition_receipt(transition)
    if checked_transition["subject_id"] != subject_id or checked_transition["subject_sha256"] != subject_sha256:
        _fail("SUBJECT_MISMATCH", "Transition subject does not match state subject")
    transition_id = checked_transition["transition_id"]
    from_state = parse_state_vector(checked_transition["from_state"])
    state = parse_state_vector(checked_transition["to_state"])
    if previous_state_record_id is None and not (
        from_state == IMPLICIT_STATE
        and state == GENESIS_STATE
        and checked_transition["transition_axis"] == "possession"
    ):
        _fail("STATE_TRANSITION_INVALID", "A null-parent state record requires the exact genesis edge")
    if previous_state_record_id is not None and from_state == IMPLICIT_STATE:
        _fail("STATE_TRANSITION_INVALID", "Only the null-parent record may consume the implicit state")
    body: dict[str, Any] = {
        "subject_id": subject_id,
        "subject_sha256": subject_sha256,
        "previous_state_record_id": previous_state_record_id,
        "transition_id": transition_id,
        "state": state.as_dict(),
        "evidence_ids": list(checked_transition["evidence_ids"]),
        "policy_semantic_sha256": validate_sha256(
            checked_transition["policy_semantic_sha256"], "policy digest"
        ),
        "authority": zero_authority(),
    }
    return {
        "schema_version": "nexus.ecosystem-state-record.v1",
        "state_record_id": typed_id("state-record", body),
        **body,
    }


def validate_transition_receipt(value: Any) -> dict[str, Any]:
    """Recompute a closed transition proposal before it can affect lineage."""
    fields = {
        "schema_version",
        "transition_id",
        "subject_id",
        "subject_sha256",
        "from_state",
        "to_state",
        "transition_axis",
        "evidence_ids",
        "evaluation_receipt_sha256s",
        "evaluation_profile_id",
        "evaluation_profile_sha256",
        "policy_semantic_sha256",
        "reason_codes",
        "permitted",
        "applied",
        "authority",
    }
    record = validate_exact_keys(value, fields, "state transition receipt")
    if record["schema_version"] != "nexus.ecosystem-state-transition-receipt.v1":
        _fail("STATE_TRANSITION_INVALID", "Transition receipt schema is unsupported")
    validate_typed_id(record["transition_id"], "transition")
    if type(record["permitted"]) is not bool or record["permitted"] is not True:
        _fail("STATE_TRANSITION_INVALID", "Transition must be an explicitly permitted proposal")
    if type(record["applied"]) is not bool or record["applied"] is not False:
        _fail("STATE_TRANSITION_INVALID", "Transition proposal cannot claim application")
    validate_authority(record["authority"])
    expected = build_transition_receipt(
        subject_id=record["subject_id"],
        subject_sha256=record["subject_sha256"],
        from_state=parse_state_vector(record["from_state"]),
        to_state=parse_state_vector(record["to_state"]),
        transition_axis=record["transition_axis"],
        evidence_ids=record["evidence_ids"],
        evaluation_receipt_sha256s=record["evaluation_receipt_sha256s"],
        evaluation_profile_id=record["evaluation_profile_id"],
        evaluation_profile_sha256=record["evaluation_profile_sha256"],
        policy_semantic_sha256=record["policy_semantic_sha256"],
        reason_codes=record["reason_codes"],
    )
    if record != expected:
        _fail("STATE_TRANSITION_INVALID", "Transition receipt digest or semantics are inconsistent")
    return dict(expected)


def validate_state_record(value: Any) -> dict[str, Any]:
    fields = {
        "schema_version",
        "state_record_id",
        "subject_id",
        "subject_sha256",
        "previous_state_record_id",
        "transition_id",
        "state",
        "evidence_ids",
        "policy_semantic_sha256",
        "authority",
    }
    record = validate_exact_keys(value, fields, "state record")
    if record["schema_version"] != "nexus.ecosystem-state-record.v1":
        _fail("STATE_TRANSITION_INVALID", "State record schema is unsupported")
    validate_typed_id(record["state_record_id"], "state-record")
    _validate_lifecycle_subject_id(record["subject_id"])
    validate_sha256(record["subject_sha256"], "state subject digest")
    if record["previous_state_record_id"] is not None:
        validate_typed_id(record["previous_state_record_id"], "state-record")
    validate_typed_id(record["transition_id"], "transition")
    parse_state_vector(record["state"])
    state = parse_state_vector(record["state"])
    if state.possession_state == "NOT_PRESENT":
        _fail("STATE_TRANSITION_INVALID", "The implicit possession vector is not a public state record")
    if record["previous_state_record_id"] is None and state != GENESIS_STATE:
        _fail("STATE_TRANSITION_INVALID", "A null-parent state record must be the genesis vector")
    if type(record["evidence_ids"]) is not list or len(record["evidence_ids"]) > 32:
        _fail("STATE_TRANSITION_INVALID", "State evidence list is invalid")
    for evidence_id in record["evidence_ids"]:
        validate_typed_id(evidence_id)
    if record["evidence_ids"] != sorted(set(record["evidence_ids"])):
        _fail("STATE_TRANSITION_INVALID", "State evidence list is not canonical")
    validate_sha256(record["policy_semantic_sha256"], "state policy digest")
    validate_authority(record["authority"])
    body = {key: record[key] for key in record if key not in {"schema_version", "state_record_id"}}
    if record["state_record_id"] != typed_id("state-record", body):
        _fail("STATE_TRANSITION_INVALID", "State record identity is inconsistent")
    return dict(record)


def _validate_lifecycle_subject_id(value: Any) -> str:
    checked = validate_typed_id(value)
    if not checked.startswith(("revision/", "component-revision/")):
        _fail("STATE_TRANSITION_INVALID", "Lifecycle exists only for revision subjects")
    return checked


def validate_identity_record(record: Any, *, id_field: str, kind: str, domain: str) -> dict[str, Any]:
    if type(record) is not dict or type(record.get(id_field)) is not str:
        _fail("POLICY_SCHEMA_INVALID", "Identity record is malformed")
    body = {key: value for key, value in record.items() if key not in {"schema_version", id_field}}
    expected = typed_id(kind, body, domain=domain)
    if record[id_field] != expected:
        _fail("POLICY_INTEGRITY_INVALID", "Identity record digest does not match its semantics")
    canonical_json_bytes(record)
    return dict(record)
