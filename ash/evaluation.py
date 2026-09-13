"""Deterministic, bounded, non-authorizing evaluation contracts.

This module evaluates caller-supplied, content-bounded facts with a small set
of closed operators.  Validator configuration is data-only and must be loaded
from the Nexus integrity manifest.  It cannot name Python, shell, plugins,
tools, providers, or any other executable implementation.

An evaluation PASS proves only that the declared checks for the exact subject
digest passed under the declared validator definition.  No function in this
module executes, installs, connects, delegates, mutates, or reports a result.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import hmac
import json
import os
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping, Sequence
import unicodedata
import weakref


EVALUATION_REQUEST_SCHEMA_VERSION = "nexus.evaluation-request.v1"
EVALUATION_CONTRACT_SCHEMA_VERSION = "nexus.evaluation-contract.v1"
VALIDATOR_REGISTRY_SCHEMA_VERSION = "nexus.validator-registry.v1"
VALIDATOR_REGISTRY_VERSION = "1"
VALIDATOR_VERSION = "1"
EXPECTED_VALIDATOR_REGISTRY_SHA256 = "ba1645ba3c85ed00a72daadbb112897bd54af33783808b44dd0fc878b07535a0"

MAX_REGISTRY_BYTES = 32 * 1024
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_VALIDATORS = 32
MAX_CHECKS = 16
MAX_EVIDENCE_ITEMS = 16
MAX_REASON_CODES = 16
MAX_RECEIPT_BYTES = 48 * 1024
MAX_REQUEST_BYTES = 64 * 1024
MAX_EVIDENCE_STRING = 512
MAX_OUTPUT_SUMMARY = 160
MAX_VALUE_ITEMS = 16
MAX_VALUE_DEPTH = 3
MAX_VALUE_STRING = 512

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RELEASE_VERSION_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._-]{0,63}$")
TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
SUBJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SECRET_IDENTIFIER_RE = re.compile(
    r"(?i)^(?:sk[-_][A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20,}"
    r"|(?:AKIA|ASIA)[0-9A-Z]{16}"
    r"|xox[A-Za-z]-[A-Za-z0-9-]{8,}|xapp-[A-Za-z0-9-]{8,})$"
)

VALIDATOR_TYPES = frozenset(
    {
        "schema",
        "digest_integrity",
        "bounded_predicate",
        "artifact_metadata",
        "state_consistency",
        "receipt_consistency",
    }
)
OPERATORS = frozenset(
    {
        "equals",
        "not_equals",
        "present",
        "sha256_matches_subject",
        "state_consistent",
        "receipt_consistent",
    }
)
OPERATORS_BY_TYPE = {
    "schema": frozenset({"equals", "present"}),
    "digest_integrity": frozenset({"sha256_matches_subject"}),
    "bounded_predicate": frozenset({"equals", "not_equals", "present"}),
    "artifact_metadata": frozenset({"equals", "present", "sha256_matches_subject"}),
    "state_consistency": frozenset({"state_consistent"}),
    "receipt_consistency": frozenset({"receipt_consistent"}),
}
RESULT_STATES = frozenset(
    {
        "PASS",
        "FAIL",
        "NOT_APPLICABLE",
        "INSUFFICIENT_EVIDENCE",
        "INVALID_REQUEST",
        "VALIDATOR_UNAVAILABLE",
    }
)
CHECK_STATES = RESULT_STATES

CREATION_STATES = frozenset({"not_created", "created"})
SELECTION_STATES = frozenset({"not_selected", "selected"})
EXECUTION_STATES = frozenset({"not_executed", "execution_succeeded", "execution_failed"})
REVIEW_STATES = frozenset({"not_reviewed", "review_completed", "review_failed"})
ENHANCEMENT_STATES = frozenset({"not_enhanced", "enhancement_succeeded", "enhancement_failed"})
VALIDATION_STATES = frozenset({"not_validated", "validation_passed", "validation_failed"})
REPORTING_STATES = frozenset({"not_reported", "reported"})

_REGISTRY_FIELDS = {"schema_version", "registry_version", "validators"}
_VALIDATOR_FIELDS = {
    "validator_id",
    "display_name",
    "validator_version",
    "validator_type",
    "subject_types",
    "operators",
    "output_schema_version",
    "minimum_checks",
    "requires_executed_subject",
    "pass_transition",
    "availability",
    "definition_source",
}
_REQUEST_FIELDS = {"schema_version", "validator_id", "validator_version", "subject", "checks"}
_SUBJECT_FIELDS = {
    "subject_type",
    "subject_id",
    "subject_sha256",
    "parent_subject_sha256",
    "lifecycle",
    "stage_receipts",
}
_LIFECYCLE_FIELDS = {
    "creation",
    "selection",
    "execution",
    "review",
    "enhancement",
    "validation",
    "reporting",
}
_STAGE_RECEIPT_FIELDS = {"creator", "execution", "reviewer", "enhancer", "reporter"}
_CHECK_REQUEST_FIELDS = {"check_id", "operator", "required", "expected", "observed", "evidence"}
_EVIDENCE_REQUEST_FIELDS = {"evidence_id", "content_sha256", "summary"}
_CHECK_OUTPUT_FIELDS = {
    "check_id",
    "operator",
    "required",
    "expected_sha256",
    "observed_sha256",
    "subject_binding_sha256",
    "evidence_id",
    "evidence_sha256",
    "status",
    "reason_code",
}
_EVIDENCE_OUTPUT_FIELDS = {
    "evidence_id",
    "content_sha256",
    "summary",
    "redacted",
    "truncated",
}
_RECEIPT_FIELDS = {
    "schema_version",
    "evaluation_id",
    "validator",
    "subject",
    "checks",
    "result",
    "evidence",
    "state_transition",
    "provenance",
    "redaction",
    "proof_scope",
    "authority",
}

_WINDOWS_PATH_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:[A-Z]:[\\/]|(?:\\\\|//)[^\\/\r\n]+[\\/])[^\r\n]*"
)
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
_FORBIDDEN_INTEGRITY_PARTS = frozenset(
    {
        ".git",
        ".pytest_cache",
        ".venv",
        "__pycache__",
        "comparisons",
        "components",
        "decisions",
        "ecosystem",
        "evidence",
        "incoming",
        "intake-attempts",
        "locks",
        "node_modules",
        "objects",
        "observations",
        "output",
        "quarantine",
        "receipts",
        "revisions",
        "staging",
        "state",
        "tmp",
        "trees",
        "venv",
    }
)
_FORBIDDEN_INTEGRITY_NAMES = frozenset(
    {
        ".env",
        ".nexus-ecosystem-root.json",
        "manifest.json",
        "nexus-desktop-plugin.json",
        "registry.json",
        "workspaces.json",
    }
)
_SECRET_FILE_SUFFIXES = (".key", ".pem", ".p12", ".pfx")
_UNIX_PRIVATE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9])/(?:home|Users|root|private|var/folders|tmp)/(?:[^\r\n]*)",
    re.IGNORECASE,
)
_AUTHORIZATION_RE = re.compile(r"(?i)\bauthorization\s*:\s*[^\r\n]+")
_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:api[_-]?key|secret[_-]?access[_-]?key|access[_-]?token|"
    r"private[_-]?key|database[_-]?url|connection[_-]?string|token|secret|password|"
    r"credential)[\"']?\s*(?:=|:)\s*[^\r\n]+"
)
_ENVIRONMENT_ASSIGNMENT_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:username|userprofile|userdomain|user|logname|homedrive|"
    r"homepath|home|computername|hostname)[\"']?\s*(?:=|:)\s*[^\r\n]+"
)
_TOKEN_VALUE_RE = re.compile(
    r"(?i)(?:\bbearer\s+[A-Za-z0-9._~+/=-]{8,}|\bsk[-_][A-Za-z0-9._~+/=-]{8,}|"
    r"\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}|"
    r"\bglpat-[A-Za-z0-9_-]{20,}|"
    r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b|\bxox[A-Za-z]-[A-Za-z0-9-]{8,}|"
    r"\bxapp-[A-Za-z0-9-]{8,})"
)
_CREDENTIAL_URL_RE = re.compile(
    r"(?i)\b[A-Za-z][A-Za-z0-9+.-]{1,15}://[^\s/:@]+:[^@\s]+@[^\r\n]+"
)
_PRIVATE_KEY_MATERIAL_RE = re.compile(
    r"-----BEGIN [A-Z0-9 ]{0,64}PRIVATE KEY-----.*", re.IGNORECASE | re.DOTALL
)
_INJECTION_RE = re.compile(
    r"(?i)(?:ignore\s+(?:all\s+|the\s+)?(?:previous\s+|prior\s+)?(?:policy|instructions?)"
    r"|validation_result\s*=\s*pass"
    r"|validator_id\s*=\s*trusted[-_a-z0-9]*"
    r"|execution_succeeded\s*=\s*true"
    r"|review_complete\s*=\s*true"
    r"|host_handoff_ready"
    r"|mcp_execution_authority\s*=\s*granted)"
)
_REDACTION_MARKER_RE = re.compile(
    r"\[REDACTED_(?:AUTHORIZATION|SECRET|ENVIRONMENT|TOKEN|PRIVATE_PATH|"
    r"CREDENTIAL_URL|PRIVATE_KEY|UNTRUSTED_INSTRUCTION|CONTENT)\]"
)
_TRUSTED_REGISTRY_SEAL = object()
_PRODUCTION_REGISTRY_LOAD_TOKEN = object()
_HERMETIC_TEST_REGISTRY_LOAD_TOKEN = object()
_PRODUCTION_TRUST_MODE = "production"
_HERMETIC_TEST_TRUST_MODE = "hermetic_test"
_TRUSTED_REGISTRY_BASELINES: "weakref.WeakKeyDictionary[TrustedValidatorRegistry, tuple[Any, ...]]"


class EvaluationError(ValueError):
    """Raised when an evaluation boundary cannot remain deterministic and closed."""


def _reject_secret_identifier(value: str, label: str) -> None:
    if SECRET_IDENTIFIER_RE.fullmatch(value):
        raise EvaluationError(f"{label} resembles secret material")


@dataclass(frozen=True)
class ValidatorDefinition:
    validator_id: str
    display_name: str
    validator_version: str
    validator_type: str
    subject_types: tuple[str, ...]
    operators: tuple[str, ...]
    output_schema_version: str
    minimum_checks: int
    requires_executed_subject: bool
    pass_transition: str
    availability: str
    definition_source: str

    def canonical_record(self) -> dict[str, Any]:
        return {
            "validator_id": self.validator_id,
            "display_name": self.display_name,
            "validator_version": self.validator_version,
            "validator_type": self.validator_type,
            "subject_types": list(self.subject_types),
            "operators": list(self.operators),
            "output_schema_version": self.output_schema_version,
            "minimum_checks": self.minimum_checks,
            "requires_executed_subject": self.requires_executed_subject,
            "pass_transition": self.pass_transition,
            "availability": self.availability,
            "definition_source": self.definition_source,
        }


@dataclass(frozen=True, eq=False)
class TrustedValidatorRegistry:
    validators: tuple[ValidatorDefinition, ...]
    registry_sha256: str
    _integrity_seal: object = field(init=False, repr=False, compare=False)
    _integrity_sha256: str = field(init=False, repr=False, compare=False)
    _integrity_manifest_sha256: str = field(init=False, repr=False, compare=False)
    _trust_mode: str = field(init=False, repr=False, compare=False)
    _repository_root: str = field(init=False, repr=False, compare=False)

    def resolve(self, validator_id: str, validator_version: str) -> ValidatorDefinition:
        matching_id = [item for item in self.validators if item.validator_id == validator_id]
        if not matching_id:
            raise EvaluationError("evaluation validator is unknown")
        matching_version = [item for item in matching_id if item.validator_version == validator_version]
        if len(matching_version) != 1:
            raise EvaluationError("evaluation validator version is unsupported")
        return matching_version[0]


_TRUSTED_REGISTRY_BASELINES = weakref.WeakKeyDictionary()


def _registry_semantic_sha256(value: TrustedValidatorRegistry) -> str:
    if (
        type(value.validators) is not tuple
        or any(type(item) is not ValidatorDefinition for item in value.validators)
    ):
        raise EvaluationError("evaluation registry is not integrity-verified")
    canonical = {
        "schema_version": VALIDATOR_REGISTRY_SCHEMA_VERSION,
        "registry_version": VALIDATOR_REGISTRY_VERSION,
        "validators": [item.canonical_record() for item in value.validators],
    }
    return canonical_sha256(canonical)


def _require_trusted_registry(value: Any) -> TrustedValidatorRegistry:
    baseline = (
        _TRUSTED_REGISTRY_BASELINES.get(value)
        if type(value) is TrustedValidatorRegistry
        else None
    )
    if (
        type(value) is not TrustedValidatorRegistry
        or type(baseline) is not tuple
        or len(baseline) != 5
        or baseline[0] is not getattr(value, "_integrity_seal", None)
        or baseline[1] != value.registry_sha256
        or baseline[2] != getattr(value, "_integrity_manifest_sha256", None)
        or baseline[3] != getattr(value, "_trust_mode", None)
        or baseline[4] != getattr(value, "_repository_root", None)
        or getattr(value, "_integrity_seal", None) is not _TRUSTED_REGISTRY_SEAL
        or getattr(value, "_integrity_sha256", None) != value.registry_sha256
        or getattr(value, "_trust_mode", None)
        not in {_PRODUCTION_TRUST_MODE, _HERMETIC_TEST_TRUST_MODE}
        or not isinstance(getattr(value, "_repository_root", None), str)
        or not isinstance(getattr(value, "_integrity_manifest_sha256", None), str)
        or not SHA256_RE.fullmatch(value._integrity_manifest_sha256)
        or not isinstance(value.registry_sha256, str)
        or not SHA256_RE.fullmatch(value.registry_sha256)
        or not hmac.compare_digest(_registry_semantic_sha256(value), value.registry_sha256)
    ):
        raise EvaluationError("evaluation registry is not integrity-verified")
    return value


def _require_production_registry(value: Any) -> TrustedValidatorRegistry:
    trusted = _require_trusted_registry(value)
    if (
        trusted._trust_mode != _PRODUCTION_TRUST_MODE
        or trusted._repository_root != str(Path(os.path.abspath(__file__)).parents[1])
        or not hmac.compare_digest(
            trusted.registry_sha256, EXPECTED_VALIDATOR_REGISTRY_SHA256
        )
    ):
        raise EvaluationError("evaluation production registry is not approved")
    return trusted


def _canonical_json(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError) as exc:
        raise EvaluationError("evaluation value is not canonical JSON") from exc


def canonical_sha256(value: Any) -> str:
    """Return the deterministic JSON digest used by evaluation evidence."""
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def evaluation_receipt_sha256(value: Mapping[str, Any]) -> str:
    """Bind a validated evaluation receipt for a later quality-stage receipt."""
    validated = validate_evaluation_receipt(value)
    return canonical_sha256(validated)


def _ensure_json_size(value: Any, limit: int, label: str) -> bytes:
    try:
        encoder = json.JSONEncoder(
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        chunks: list[bytes] = []
        size = 0
        for chunk in encoder.iterencode(value):
            encoded = chunk.encode("utf-8")
            size += len(encoded)
            if size > limit:
                raise EvaluationError(f"{label} exceeds its bounded size")
            chunks.append(encoded)
        return b"".join(chunks)
    except EvaluationError:
        raise
    except (TypeError, ValueError, RecursionError) as exc:
        raise EvaluationError(f"{label} is not canonical JSON") from exc


def _bounded_value(value: Any, *, depth: int = 0) -> Any:
    if depth > MAX_VALUE_DEPTH:
        raise EvaluationError("evaluation value nesting is unbounded")
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        if not -(2**63) <= value <= 2**63 - 1:
            raise EvaluationError("evaluation integer is out of range")
        return value
    if isinstance(value, str):
        if len(value) > MAX_VALUE_STRING:
            raise EvaluationError("evaluation string is oversized")
        return value
    if isinstance(value, list):
        if len(value) > MAX_VALUE_ITEMS:
            raise EvaluationError("evaluation list is oversized")
        return [_bounded_value(item, depth=depth + 1) for item in value]
    if isinstance(value, Mapping):
        if len(value) > MAX_VALUE_ITEMS:
            raise EvaluationError("evaluation object is oversized")
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key or len(key) > 64:
                raise EvaluationError("evaluation object key is invalid")
            if key in result:
                raise EvaluationError("evaluation object key is duplicated")
            result[key] = _bounded_value(item, depth=depth + 1)
        return result
    raise EvaluationError("evaluation value type is unsupported")


def _stable_bytes(path: Path, maximum: int) -> bytes:
    """Read one integrity input through the Slice 3C stable-handle boundary."""
    try:
        # Delayed imports avoid a module-import cycle when the quarantine store
        # later revalidates a registry.  The shared reader holds no-follow
        # handles, rejects hardlinks/reparse points, and verifies Windows
        # FileId/POSIX inode identity before and after the bounded read.
        from .ecosystem_models import EcosystemError as _EcosystemError
        from .ecosystem_storage import stable_read_bytes
    except (ImportError, AttributeError):
        raise EvaluationError("evaluation stable integrity reader is unavailable") from None
    try:
        return stable_read_bytes(
            path,
            maximum_bytes=maximum,
            reason_code="INPUT_UNSTABLE",
        )
    except (OSError, ValueError, _EcosystemError):
        raise EvaluationError("evaluation integrity file is unavailable or unstable") from None


def _reject_duplicate_json_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationError("evaluation JSON contains a duplicate key")
        result[key] = value
    return result


def _json_loads(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_json_keys)
    except EvaluationError:
        raise
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise EvaluationError(f"{label} is invalid") from exc


def _validate_integrity_manifest_entries(
    value: Any, *, size_key: str
) -> dict[str, dict[str, Any]]:
    """Validate every integrity entry before any registry authority is issued."""
    if type(value) is not dict or not value:
        raise EvaluationError("evaluation integrity manifest entries are invalid")
    collision_keys: set[str] = set()
    for raw_name, metadata in value.items():
        if (
            type(raw_name) is not str
            or not raw_name
            or unicodedata.normalize("NFC", raw_name) != raw_name
            or len(raw_name.encode("utf-8")) > 512
            or "\\" in raw_name
            or "\x00" in raw_name
            or any(ord(character) < 32 or ord(character) == 127 for character in raw_name)
        ):
            raise EvaluationError("evaluation integrity manifest path is invalid")
        parts = raw_name.split("/")
        folded_parts = tuple(part.casefold() for part in parts)
        folded_name = folded_parts[-1] if folded_parts else ""
        if (
            len(parts) > 32
            or any(part in _FORBIDDEN_INTEGRITY_PARTS for part in folded_parts)
            or folded_name in _FORBIDDEN_INTEGRITY_NAMES
            or folded_name.startswith(".env.")
            or folded_name.endswith(_SECRET_FILE_SUFFIXES)
            or any(
                part in {"", ".", ".."}
                or ":" in part
                or part.endswith((".", " "))
                or len(part.encode("utf-8")) > 128
                or any(character in _BIDI_CONTROLS for character in part)
                or part.split(".", 1)[0].casefold() in _WINDOWS_RESERVED
                for part in parts
            )
        ):
            raise EvaluationError("evaluation integrity manifest path is invalid")
        path = PurePosixPath(raw_name)
        if path.is_absolute() or path.as_posix() != raw_name:
            raise EvaluationError("evaluation integrity manifest path is invalid")
        collision = raw_name.casefold()
        if collision in collision_keys:
            raise EvaluationError("evaluation integrity manifest paths collide")
        collision_keys.add(collision)
        if (
            type(metadata) is not dict
            or set(metadata) != {size_key, "sha256"}
            or type(metadata[size_key]) is not int
            or not 0 <= metadata[size_key] <= 9_223_372_036_854_775_807
            or type(metadata["sha256"]) is not str
            or not SHA256_RE.fullmatch(metadata["sha256"])
        ):
            raise EvaluationError("evaluation integrity manifest metadata is invalid")
    return value


def _bounded_token_list(value: Any, *, maximum: int, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or len(value) > maximum:
        raise EvaluationError(f"validator {label} is invalid or unbounded")
    if any(not isinstance(item, str) or not TOKEN_RE.fullmatch(item) for item in value):
        raise EvaluationError(f"validator {label} is invalid")
    if len(set(value)) != len(value):
        raise EvaluationError(f"validator {label} is duplicated")
    return tuple(sorted(value))


def _parse_registry(payload: Any) -> TrustedValidatorRegistry:
    if not isinstance(payload, Mapping) or set(payload) != _REGISTRY_FIELDS:
        raise EvaluationError("validator registry schema is malformed")
    if payload.get("schema_version") != VALIDATOR_REGISTRY_SCHEMA_VERSION:
        raise EvaluationError("validator registry schema is unsupported")
    if payload.get("registry_version") != VALIDATOR_REGISTRY_VERSION:
        raise EvaluationError("validator registry version is unsupported")
    raw_validators = payload.get("validators")
    if not isinstance(raw_validators, list) or not raw_validators or len(raw_validators) > MAX_VALIDATORS:
        raise EvaluationError("validator registry is empty or unbounded")
    definitions: list[ValidatorDefinition] = []
    identities: set[str] = set()
    for raw in raw_validators:
        if not isinstance(raw, Mapping) or set(raw) != _VALIDATOR_FIELDS:
            raise EvaluationError("validator definition schema is malformed")
        validator_id = raw.get("validator_id")
        display_name = raw.get("display_name")
        validator_type = raw.get("validator_type")
        if not isinstance(validator_id, str) or not TOKEN_RE.fullmatch(validator_id):
            raise EvaluationError("validator identity is invalid")
        _reject_secret_identifier(validator_id, "validator identity")
        if validator_id in identities:
            raise EvaluationError("validator registry contains a duplicate validator ID")
        identities.add(validator_id)
        if (
            not isinstance(display_name, str)
            or not display_name.strip()
            or len(display_name) > 96
            or any(ord(char) < 32 for char in display_name)
        ):
            raise EvaluationError("validator display name is invalid")
        if raw.get("validator_version") != VALIDATOR_VERSION:
            raise EvaluationError("validator definition version is unsupported")
        if validator_type not in VALIDATOR_TYPES:
            raise EvaluationError("validator type is unsupported")
        subject_types = _bounded_token_list(
            raw.get("subject_types"), maximum=8, label="subject applicability"
        )
        operators = _bounded_token_list(raw.get("operators"), maximum=8, label="operator list")
        if not set(operators) <= OPERATORS_BY_TYPE[str(validator_type)]:
            raise EvaluationError("validator operators exceed the declared validator type")
        minimum_checks = raw.get("minimum_checks")
        if not isinstance(minimum_checks, int) or isinstance(minimum_checks, bool) or not 1 <= minimum_checks <= MAX_CHECKS:
            raise EvaluationError("validator minimum check count is invalid")
        if not isinstance(raw.get("requires_executed_subject"), bool):
            raise EvaluationError("validator execution-evidence requirement is invalid")
        if raw.get("pass_transition") not in {"none", "validation_passed"}:
            raise EvaluationError("validator pass transition is invalid")
        if raw.get("availability") not in {"available", "unavailable"}:
            raise EvaluationError("validator availability is invalid")
        if raw.get("definition_source") != "nexus_core":
            raise EvaluationError("validator definition source is not trusted")
        if raw.get("output_schema_version") != EVALUATION_CONTRACT_SCHEMA_VERSION:
            raise EvaluationError("validator output schema is unsupported")
        definitions.append(
            ValidatorDefinition(
                validator_id=validator_id,
                display_name=display_name.strip(),
                validator_version=VALIDATOR_VERSION,
                validator_type=str(validator_type),
                subject_types=subject_types,
                operators=operators,
                output_schema_version=EVALUATION_CONTRACT_SCHEMA_VERSION,
                minimum_checks=minimum_checks,
                requires_executed_subject=raw["requires_executed_subject"],
                pass_transition=raw["pass_transition"],
                availability=raw["availability"],
                definition_source="nexus_core",
            )
        )
    ordered = tuple(sorted(definitions, key=lambda item: item.validator_id))
    canonical = {
        "schema_version": VALIDATOR_REGISTRY_SCHEMA_VERSION,
        "registry_version": VALIDATOR_REGISTRY_VERSION,
        "validators": [item.canonical_record() for item in ordered],
    }
    return TrustedValidatorRegistry(ordered, canonical_sha256(canonical))


def _load_trusted_validator_registry_at(
    *,
    root: Path,
    integrity_manifest_path: Path | None,
    load_token: object,
) -> TrustedValidatorRegistry:
    """Load one integrity-bound registry in an explicitly selected trust context."""
    if load_token is _PRODUCTION_REGISTRY_LOAD_TOKEN:
        trust_mode = _PRODUCTION_TRUST_MODE
        expected_registry_sha256: str | None = EXPECTED_VALIDATOR_REGISTRY_SHA256
    elif load_token is _HERMETIC_TEST_REGISTRY_LOAD_TOKEN:
        trust_mode = _HERMETIC_TEST_TRUST_MODE
        expected_registry_sha256 = None
    else:
        raise EvaluationError("validator registry loader authority is unavailable")
    if not isinstance(root, Path):
        raise EvaluationError("validator registry root is invalid")
    if integrity_manifest_path is not None and not isinstance(integrity_manifest_path, Path):
        raise EvaluationError("validator registry integrity path is invalid")
    try:
        # Preserve the lexical root so the stable reader can reject a linked
        # or reparse ancestor before issuing the trusted registry seal.
        root = Path(os.path.abspath(root))
    except (OSError, ValueError, TypeError) as exc:
        raise EvaluationError("validator registry root is invalid") from exc
    if not root.is_dir():
        raise EvaluationError("validator registry root is invalid")
    registry_path = root / "config" / "validator-registry.json"
    release_manifest = root / "release-manifest.json"
    manifest_path = integrity_manifest_path or (
        release_manifest if os.path.lexists(release_manifest) else root / "MANIFEST.json"
    )
    try:
        # Preserve the lexical path until the stable reader has inspected every
        # component. Calling resolve() here would erase symlink/reparse evidence
        # before the no-follow boundary sees it.
        manifest_path = Path(os.path.abspath(manifest_path))
        manifest_path.relative_to(root)
    except (OSError, ValueError) as exc:
        raise EvaluationError("validator registry integrity path is invalid") from exc
    manifest_raw = _stable_bytes(manifest_path, MAX_MANIFEST_BYTES)
    manifest = _json_loads(manifest_raw, "evaluation integrity manifest")
    if type(manifest) is not dict:
        raise EvaluationError("evaluation integrity manifest is invalid")
    # The manifest contract is selected by the trusted path, never by a key
    # that an attacker can place in an otherwise valid static MANIFEST.json.
    is_release = manifest_path.name == "release-manifest.json"
    if is_release:
        release_fields = {"schema_version", "product", "distribution", "version", "files"}
        if (
            set(manifest) != release_fields
            or manifest["schema_version"] != "nexus.release.manifest.v1"
            or manifest["product"] != "Nexus"
            or manifest["distribution"] != "github-release"
            or type(manifest["version"]) is not str
            or not RELEASE_VERSION_RE.fullmatch(manifest["version"])
        ):
            raise EvaluationError("evaluation release integrity manifest is invalid")
        entries = _validate_integrity_manifest_entries(manifest["files"], size_key="size")
    else:
        entries = _validate_integrity_manifest_entries(manifest, size_key="bytes")
    # This path was constructed from the lexical root and a fixed relative
    # name.  Resolving it here would hide a link before _stable_bytes can
    # inspect the original path through its no-follow boundary.
    relative = registry_path.relative_to(root).as_posix()
    registry_raw = _stable_bytes(registry_path, MAX_REGISTRY_BYTES)
    metadata = entries.get(relative)
    expected_metadata_fields = {"size", "sha256"} if is_release else {"bytes", "sha256"}
    if type(metadata) is not dict or set(metadata) != expected_metadata_fields:
        raise EvaluationError("validator registry integrity entry is invalid")
    size_key = "size" if is_release else "bytes"
    try:
        digest_bytes = (
            registry_raw
            if is_release
            else registry_raw.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
        )
    except UnicodeDecodeError as exc:
        raise EvaluationError("validator registry encoding is invalid") from exc
    if (
        type(metadata.get("sha256")) is not str
        or not SHA256_RE.fullmatch(str(metadata["sha256"]))
        or hashlib.sha256(digest_bytes).hexdigest() != metadata["sha256"]
        or type(metadata.get(size_key)) is not int
        or metadata[size_key] != len(digest_bytes)
    ):
        raise EvaluationError("validator registry integrity check failed")
    registry = _parse_registry(_json_loads(registry_raw, "validator registry"))
    if expected_registry_sha256 is not None and not hmac.compare_digest(
        registry.registry_sha256, expected_registry_sha256
    ):
        raise EvaluationError("validator registry differs from the approved production baseline")
    object.__setattr__(registry, "_integrity_seal", _TRUSTED_REGISTRY_SEAL)
    object.__setattr__(registry, "_integrity_sha256", registry.registry_sha256)
    object.__setattr__(
        registry, "_integrity_manifest_sha256", hashlib.sha256(manifest_raw).hexdigest()
    )
    object.__setattr__(registry, "_trust_mode", trust_mode)
    object.__setattr__(registry, "_repository_root", str(root))
    _TRUSTED_REGISTRY_BASELINES[registry] = (
        _TRUSTED_REGISTRY_SEAL,
        registry.registry_sha256,
        registry._integrity_manifest_sha256,
        registry._trust_mode,
        registry._repository_root,
    )
    return registry


def load_trusted_validator_registry() -> TrustedValidatorRegistry:
    """Load only the approved registry beside the executing Nexus module."""
    return _load_trusted_validator_registry_at(
        root=Path(os.path.abspath(__file__)).parents[1],
        integrity_manifest_path=None,
        load_token=_PRODUCTION_REGISTRY_LOAD_TOKEN,
    )


def _load_test_validator_registry(
    *, root: Path, integrity_manifest_path: Path | None = None
) -> TrustedValidatorRegistry:
    """Private hermetic-fixture seam; it cannot authorize a production context."""
    return _load_trusted_validator_registry_at(
        root=root,
        integrity_manifest_path=integrity_manifest_path,
        load_token=_HERMETIC_TEST_REGISTRY_LOAD_TOKEN,
    )


def _nullable_sha256(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise EvaluationError(f"{label} digest is invalid")
    return value


def _parse_subject(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _SUBJECT_FIELDS:
        raise EvaluationError("evaluation subject schema is malformed")
    subject_type = value.get("subject_type")
    subject_id = value.get("subject_id")
    subject_sha256 = value.get("subject_sha256")
    if not isinstance(subject_type, str) or not TOKEN_RE.fullmatch(subject_type):
        raise EvaluationError("evaluation subject type is invalid")
    if not isinstance(subject_id, str) or not SUBJECT_ID_RE.fullmatch(subject_id):
        raise EvaluationError("evaluation subject identity is invalid")
    _reject_secret_identifier(subject_type, "evaluation subject type")
    _reject_secret_identifier(subject_id, "evaluation subject identity")
    if not isinstance(subject_sha256, str) or not SHA256_RE.fullmatch(subject_sha256):
        raise EvaluationError("evaluation subject digest is invalid")
    parent = _nullable_sha256(value.get("parent_subject_sha256"), "evaluation parent subject")
    lifecycle = value.get("lifecycle")
    receipts = value.get("stage_receipts")
    if not isinstance(lifecycle, Mapping) or set(lifecycle) != _LIFECYCLE_FIELDS:
        raise EvaluationError("evaluation subject lifecycle is malformed")
    if not isinstance(receipts, Mapping) or set(receipts) != _STAGE_RECEIPT_FIELDS:
        raise EvaluationError("evaluation subject stage receipts are malformed")
    allowed_states = {
        "creation": CREATION_STATES,
        "selection": SELECTION_STATES,
        "execution": EXECUTION_STATES,
        "review": REVIEW_STATES,
        "enhancement": ENHANCEMENT_STATES,
        "validation": VALIDATION_STATES,
        "reporting": REPORTING_STATES,
    }
    for key, states in allowed_states.items():
        if lifecycle.get(key) not in states:
            raise EvaluationError(f"evaluation subject {key} state is invalid")
    normalized_receipts = {
        key: _nullable_sha256(receipts.get(key), f"evaluation {key} receipt")
        for key in sorted(_STAGE_RECEIPT_FIELDS)
    }
    state_receipt_rules = (
        (lifecycle["creation"] == "created", normalized_receipts["creator"] is not None, "creation"),
        (lifecycle["execution"] != "not_executed", normalized_receipts["execution"] is not None, "execution"),
        (lifecycle["review"] != "not_reviewed", normalized_receipts["reviewer"] is not None, "review"),
        (lifecycle["enhancement"] != "not_enhanced", normalized_receipts["enhancer"] is not None, "enhancement"),
        (lifecycle["reporting"] == "reported", normalized_receipts["reporter"] is not None, "reporting"),
    )
    for state_claim, receipt_present, label in state_receipt_rules:
        if state_claim != receipt_present:
            raise EvaluationError(f"evaluation subject {label} state lacks matching receipt evidence")
    if lifecycle["validation"] != "not_validated" and normalized_receipts["reviewer"] is None:
        raise EvaluationError("evaluation subject validation state lacks review evidence")
    if lifecycle["enhancement"] == "enhancement_succeeded":
        if parent is None or parent == subject_sha256:
            raise EvaluationError("enhanced subject does not preserve a distinct parent digest")
    elif lifecycle["enhancement"] == "not_enhanced" and parent is not None:
        raise EvaluationError("unenhanced subject cannot claim an enhancement parent")
    return {
        "subject_type": subject_type,
        "subject_id": subject_id,
        "subject_sha256": subject_sha256,
        "parent_subject_sha256": parent,
        "lifecycle": {key: lifecycle[key] for key in sorted(_LIFECYCLE_FIELDS)},
        "stage_receipts": normalized_receipts,
    }


def _redact_summary(value: str) -> tuple[str, bool, bool]:
    redacted = value
    applied = False
    for pattern, replacement in (
        (_REDACTION_MARKER_RE, "[REDACTED_UNTRUSTED_INSTRUCTION]"),
        (_AUTHORIZATION_RE, "[REDACTED_AUTHORIZATION]"),
        (_SECRET_ASSIGNMENT_RE, "[REDACTED_SECRET]"),
        (_ENVIRONMENT_ASSIGNMENT_RE, "[REDACTED_ENVIRONMENT]"),
        (_TOKEN_VALUE_RE, "[REDACTED_TOKEN]"),
        (_CREDENTIAL_URL_RE, "[REDACTED_CREDENTIAL_URL]"),
        (_PRIVATE_KEY_MATERIAL_RE, "[REDACTED_PRIVATE_KEY]"),
        (_WINDOWS_PATH_RE, "[REDACTED_PRIVATE_PATH]"),
        (_UNIX_PRIVATE_PATH_RE, "[REDACTED_PRIVATE_PATH]"),
        (_INJECTION_RE, "[REDACTED_UNTRUSTED_INSTRUCTION]"),
    ):
        redacted, count = pattern.subn(replacement, redacted)
        applied = applied or bool(count)
    truncated = len(redacted) > MAX_OUTPUT_SUMMARY
    if truncated:
        redacted = redacted[: MAX_OUTPUT_SUMMARY - 1] + "…"
        if applied and not _REDACTION_MARKER_RE.search(redacted):
            prefix = "[REDACTED_CONTENT] "
            redacted = prefix + redacted[: MAX_OUTPUT_SUMMARY - len(prefix) - 1] + "…"
    return redacted, applied, truncated


def _check_request(value: Any) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if not isinstance(value, Mapping) or set(value) != _CHECK_REQUEST_FIELDS:
        raise EvaluationError("evaluation check schema is malformed")
    check_id = value.get("check_id")
    operator = value.get("operator")
    if not isinstance(check_id, str) or not TOKEN_RE.fullmatch(check_id):
        raise EvaluationError("evaluation check identity is invalid")
    _reject_secret_identifier(check_id, "evaluation check identity")
    if not isinstance(operator, str) or not TOKEN_RE.fullmatch(operator):
        raise EvaluationError("evaluation check operator is invalid")
    _reject_secret_identifier(operator, "evaluation check operator")
    if not isinstance(value.get("required"), bool):
        raise EvaluationError("evaluation check required flag is invalid")
    expected = _bounded_value(value.get("expected"))
    observed = _bounded_value(value.get("observed"))
    raw_evidence = value.get("evidence")
    evidence: dict[str, Any] | None = None
    if raw_evidence is not None:
        if not isinstance(raw_evidence, Mapping) or set(raw_evidence) != _EVIDENCE_REQUEST_FIELDS:
            raise EvaluationError("evaluation evidence schema is malformed")
        evidence_id = raw_evidence.get("evidence_id")
        content_sha256 = raw_evidence.get("content_sha256")
        summary = raw_evidence.get("summary")
        if not isinstance(evidence_id, str) or not TOKEN_RE.fullmatch(evidence_id):
            raise EvaluationError("evaluation evidence identity is invalid")
        _reject_secret_identifier(evidence_id, "evaluation evidence identity")
        if not isinstance(content_sha256, str) or not SHA256_RE.fullmatch(content_sha256):
            raise EvaluationError("evaluation evidence digest is invalid")
        if not isinstance(summary, str) or len(summary) > MAX_EVIDENCE_STRING:
            raise EvaluationError("evaluation evidence summary is invalid or oversized")
        safe_summary, redacted, truncated = _redact_summary(summary)
        evidence = {
            "evidence_id": evidence_id,
            "content_sha256": content_sha256,
            "summary": safe_summary,
            "redacted": redacted,
            "truncated": truncated,
        }
    return {
        "check_id": check_id,
        "operator": operator,
        "required": value["required"],
        "expected": expected,
        "observed": observed,
    }, evidence


def _evaluate_check(
    request: Mapping[str, Any], evidence: Mapping[str, Any] | None,
    definition: ValidatorDefinition, subject: Mapping[str, Any],
) -> dict[str, Any]:
    operator = str(request["operator"])
    expected = request["expected"]
    observed = request["observed"]
    expected_sha = canonical_sha256(expected) if expected is not None else None
    observed_sha = canonical_sha256(observed) if observed is not None else None
    subject_binding: str | None = None
    evidence_id = str(evidence["evidence_id"]) if evidence is not None else None
    evidence_sha = str(evidence["content_sha256"]) if evidence is not None else None

    status = "PASS"
    reason = "CHECK_PASSED"
    if operator not in OPERATORS or operator not in definition.operators:
        status, reason = "INVALID_REQUEST", "CHECK_OPERATOR_NOT_ALLOWED"
    elif observed is None and evidence is not None:
        status, reason = "INVALID_REQUEST", "EVIDENCE_WITHOUT_OBSERVED_VALUE"
    elif observed is not None and evidence is None:
        status, reason = "INSUFFICIENT_EVIDENCE", "EVIDENCE_MISSING"
    elif observed_sha is not None and evidence_sha != observed_sha:
        status, reason = "FAIL", "EVIDENCE_DIGEST_MISMATCH"
    elif operator == "present":
        if expected is not None:
            status, reason = "INVALID_REQUEST", "CHECK_EXPECTATION_NOT_ALLOWED"
        elif observed is None:
            status, reason = "INSUFFICIENT_EVIDENCE", "EVIDENCE_MISSING"
    elif operator in {"equals", "receipt_consistent"}:
        if expected is None or observed is None:
            status, reason = "INSUFFICIENT_EVIDENCE", "EVIDENCE_MISSING"
        elif expected_sha != observed_sha:
            status, reason = "FAIL", "CHECK_VALUE_MISMATCH"
    elif operator == "not_equals":
        if expected is None or observed is None:
            status, reason = "INSUFFICIENT_EVIDENCE", "EVIDENCE_MISSING"
        elif expected_sha == observed_sha:
            status, reason = "FAIL", "CHECK_VALUE_UNEXPECTEDLY_EQUAL"
    elif operator == "sha256_matches_subject":
        if expected is not None:
            status, reason = "INVALID_REQUEST", "CHECK_EXPECTATION_NOT_ALLOWED"
        elif not isinstance(observed, str) or not SHA256_RE.fullmatch(observed):
            status, reason = "INVALID_REQUEST", "SUBJECT_BINDING_DIGEST_INVALID"
        else:
            subject_binding = observed
            if observed != subject["subject_sha256"]:
                status, reason = "FAIL", "SUBJECT_DIGEST_MISMATCH"
    elif operator == "state_consistent":
        if expected is not None:
            status, reason = "INVALID_REQUEST", "CHECK_EXPECTATION_NOT_ALLOWED"
        else:
            expected_sha = canonical_sha256(subject["lifecycle"])
            if observed is None:
                status, reason = "INSUFFICIENT_EVIDENCE", "EVIDENCE_MISSING"
            elif observed_sha != expected_sha:
                status, reason = "FAIL", "STATE_EVIDENCE_MISMATCH"
    return {
        "check_id": request["check_id"],
        "operator": operator,
        "required": request["required"],
        "expected_sha256": expected_sha,
        "observed_sha256": observed_sha,
        "subject_binding_sha256": subject_binding,
        "evidence_id": evidence_id,
        "evidence_sha256": evidence_sha,
        "status": status,
        "reason_code": reason,
    }


def _derive_result(
    definition: ValidatorDefinition, subject: Mapping[str, Any], checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    reasons: list[str] = []
    if any(item["status"] == "INVALID_REQUEST" for item in checks):
        state, reasons = "INVALID_REQUEST", ["EVALUATION_REQUEST_INVALID"]
    elif len(checks) < definition.minimum_checks:
        state, reasons = "INVALID_REQUEST", ["MINIMUM_CHECK_COUNT_NOT_MET"]
    elif definition.requires_executed_subject and subject["lifecycle"]["execution"] != "execution_succeeded":
        state, reasons = "INVALID_REQUEST", ["EXECUTED_SUBJECT_EVIDENCE_REQUIRED"]
    elif definition.availability != "available":
        state, reasons = "VALIDATOR_UNAVAILABLE", ["VALIDATOR_DEFINITION_UNAVAILABLE"]
    elif subject["subject_type"] not in definition.subject_types:
        state, reasons = "NOT_APPLICABLE", ["SUBJECT_TYPE_NOT_APPLICABLE"]
    elif any(item["status"] == "FAIL" for item in checks):
        state, reasons = "FAIL", ["DECLARED_CHECK_FAILED"]
    elif any(item["status"] == "INSUFFICIENT_EVIDENCE" for item in checks):
        state, reasons = "INSUFFICIENT_EVIDENCE", ["REQUIRED_EVIDENCE_INSUFFICIENT"]
    elif checks and all(item["status"] == "PASS" for item in checks):
        state, reasons = "PASS", ["DECLARED_CHECKS_PASSED"]
    else:
        state, reasons = "INVALID_REQUEST", ["EVALUATION_RESULT_UNRESOLVED"]
    if state != "PASS":
        reasons.extend(
            sorted(
                {
                    str(item["reason_code"])
                    for item in checks
                    if item["reason_code"] != "CHECK_PASSED"
                }
            )
        )
    reasons = list(dict.fromkeys(reasons))
    if len(reasons) > MAX_REASON_CODES:
        raise EvaluationError("evaluation result reason list is unbounded")
    return {
        "state": state,
        "reason_codes": reasons,
        "declared_check_count": len(checks),
        "required_check_count": sum(1 for item in checks if item["required"]),
        "passed_check_count": sum(1 for item in checks if item["status"] == "PASS"),
        "failed_check_count": sum(1 for item in checks if item["status"] == "FAIL"),
    }


def _state_transition(
    definition: ValidatorDefinition, subject: Mapping[str, Any], result_state: str,
) -> dict[str, Any]:
    before = subject["lifecycle"]["validation"]
    target = before
    permitted = False
    if result_state == "PASS" and definition.pass_transition == "validation_passed":
        target = "validation_passed"
        permitted = before != target
    elif result_state == "FAIL":
        target = "validation_failed"
        permitted = before != target
    return {
        "from_validation_state": before,
        "to_validation_state": target,
        "permitted": permitted,
        "applied": False,
    }


def _validator_output(definition: ValidatorDefinition) -> dict[str, Any]:
    return {
        "validator_id": definition.validator_id,
        "validator_version": definition.validator_version,
        "validator_type": definition.validator_type,
        "output_schema_version": definition.output_schema_version,
    }


def _provenance_output(
    definition: ValidatorDefinition, registry: TrustedValidatorRegistry,
) -> dict[str, Any]:
    return {
        "definition_source": definition.definition_source,
        "registry_schema_version": VALIDATOR_REGISTRY_SCHEMA_VERSION,
        "registry_version": VALIDATOR_REGISTRY_VERSION,
        "registry_sha256": registry.registry_sha256,
    }


def _fixed_proof_scope() -> dict[str, Any]:
    return {
        "proves": "declared_checks_for_exact_subject_digest_only",
        "does_not_prove": [
            "agent_delegation_authority",
            "artifact_global_correctness",
            "execution_success",
            "host_mapping_eligibility",
            "installation_authority",
            "mcp_connection_authority",
            "reporting_completion",
        ],
    }


def _fixed_authority() -> dict[str, Any]:
    return {
        "execution_authority": "none",
        "installation_authority": "none",
        "mcp_connect_authority": "none",
        "host_mapping_authority": "none",
        "agent_delegation_authority": "none",
        "state_transition_applied": False,
    }


def evaluate_contract(
    request: Any, *, registry: TrustedValidatorRegistry | None = None,
) -> dict[str, Any]:
    """Evaluate one exact, bounded request and return a reproducible receipt."""
    _ensure_json_size(request, MAX_REQUEST_BYTES, "evaluation request")
    if not isinstance(request, Mapping) or set(request) != _REQUEST_FIELDS:
        raise EvaluationError("evaluation request schema is malformed")
    if request.get("schema_version") != EVALUATION_REQUEST_SCHEMA_VERSION:
        raise EvaluationError("evaluation request schema is unsupported")
    validator_id = request.get("validator_id")
    validator_version = request.get("validator_version")
    if not isinstance(validator_id, str) or not TOKEN_RE.fullmatch(validator_id):
        raise EvaluationError("evaluation validator identity is invalid")
    if not isinstance(validator_version, str) or not TOKEN_RE.fullmatch(validator_version):
        raise EvaluationError("evaluation validator version is invalid")
    trusted = _require_trusted_registry(
        load_trusted_validator_registry() if registry is None else registry
    )
    definition = trusted.resolve(validator_id, validator_version)
    subject = _parse_subject(request.get("subject"))
    raw_checks = request.get("checks")
    if not isinstance(raw_checks, list) or len(raw_checks) > MAX_CHECKS:
        raise EvaluationError("evaluation checks are invalid or unbounded")
    parsed: list[tuple[dict[str, Any], dict[str, Any] | None]] = [
        _check_request(item) for item in raw_checks
    ]
    check_ids = [item[0]["check_id"] for item in parsed]
    if len(check_ids) != len(set(check_ids)):
        raise EvaluationError("evaluation check identity is duplicated")
    evidence_ids = [item[1]["evidence_id"] for item in parsed if item[1] is not None]
    if len(evidence_ids) > MAX_EVIDENCE_ITEMS or len(evidence_ids) != len(set(evidence_ids)):
        raise EvaluationError("evaluation evidence identity is duplicated or unbounded")
    ordered = sorted(parsed, key=lambda item: item[0]["check_id"])
    checks = [_evaluate_check(item, evidence, definition, subject) for item, evidence in ordered]
    evidence_items = [dict(evidence) for _, evidence in ordered if evidence is not None]
    evidence_items.sort(key=lambda item: item["evidence_id"])
    result = _derive_result(definition, subject, checks)
    redaction = {
        "applied": any(item["redacted"] for item in evidence_items),
        "summary_truncated": any(item["truncated"] for item in evidence_items),
        "authoritative_data_truncated": False,
    }
    body = {
        "schema_version": EVALUATION_CONTRACT_SCHEMA_VERSION,
        "validator": _validator_output(definition),
        "subject": subject,
        "checks": checks,
        "result": result,
        "evidence": {
            "item_count": len(evidence_items),
            "items": evidence_items,
            "evidence_sha256": canonical_sha256(
                [
                    {"evidence_id": item["evidence_id"], "content_sha256": item["content_sha256"]}
                    for item in evidence_items
                ]
            ),
        },
        "state_transition": _state_transition(definition, subject, result["state"]),
        "provenance": _provenance_output(definition, trusted),
        "redaction": redaction,
        "proof_scope": _fixed_proof_scope(),
        "authority": _fixed_authority(),
    }
    receipt = {**body, "evaluation_id": "evaluation:" + canonical_sha256(body)}
    # Keep the stable field order used by the public schema rather than the
    # construction order above, where evaluation_id is computed last.
    receipt = {
        "schema_version": receipt["schema_version"],
        "evaluation_id": receipt["evaluation_id"],
        "validator": receipt["validator"],
        "subject": receipt["subject"],
        "checks": receipt["checks"],
        "result": receipt["result"],
        "evidence": receipt["evidence"],
        "state_transition": receipt["state_transition"],
        "provenance": receipt["provenance"],
        "redaction": receipt["redaction"],
        "proof_scope": receipt["proof_scope"],
        "authority": receipt["authority"],
    }
    _ensure_json_size(receipt, MAX_RECEIPT_BYTES, "evaluation receipt")
    return receipt


def _recompute_check(
    value: Any, definition: ValidatorDefinition, subject: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _CHECK_OUTPUT_FIELDS:
        raise EvaluationError("evaluation receipt check schema is malformed")
    check_id = value.get("check_id")
    operator = value.get("operator")
    if not isinstance(check_id, str) or not TOKEN_RE.fullmatch(check_id):
        raise EvaluationError("evaluation receipt check identity is invalid")
    _reject_secret_identifier(check_id, "evaluation receipt check identity")
    if not isinstance(operator, str) or not TOKEN_RE.fullmatch(operator):
        raise EvaluationError("evaluation receipt check operator is invalid")
    _reject_secret_identifier(operator, "evaluation receipt check operator")
    if not isinstance(value.get("required"), bool):
        raise EvaluationError("evaluation receipt check required flag is invalid")
    expected_sha = _nullable_sha256(value.get("expected_sha256"), "evaluation expected value")
    observed_sha = _nullable_sha256(value.get("observed_sha256"), "evaluation observed value")
    binding_sha = _nullable_sha256(value.get("subject_binding_sha256"), "evaluation subject binding")
    evidence_sha = _nullable_sha256(value.get("evidence_sha256"), "evaluation evidence")
    evidence_id = value.get("evidence_id")
    if evidence_id is not None and (not isinstance(evidence_id, str) or not TOKEN_RE.fullmatch(evidence_id)):
        raise EvaluationError("evaluation receipt evidence identity is invalid")
    if isinstance(evidence_id, str):
        _reject_secret_identifier(evidence_id, "evaluation receipt evidence identity")
    if (evidence_id is None) != (evidence_sha is None):
        raise EvaluationError("evaluation receipt evidence identity and digest disagree")

    if operator != "sha256_matches_subject" and binding_sha is not None:
        raise EvaluationError("evaluation receipt check result is contradictory")

    status, reason = "PASS", "CHECK_PASSED"
    if operator not in OPERATORS or operator not in definition.operators:
        status, reason = "INVALID_REQUEST", "CHECK_OPERATOR_NOT_ALLOWED"
    elif observed_sha is None and evidence_sha is not None:
        status, reason = "INVALID_REQUEST", "EVIDENCE_WITHOUT_OBSERVED_VALUE"
    elif observed_sha is not None and evidence_sha is None:
        status, reason = "INSUFFICIENT_EVIDENCE", "EVIDENCE_MISSING"
    elif observed_sha is not None and evidence_sha != observed_sha:
        status, reason = "FAIL", "EVIDENCE_DIGEST_MISMATCH"
    elif operator == "present":
        if expected_sha is not None:
            status, reason = "INVALID_REQUEST", "CHECK_EXPECTATION_NOT_ALLOWED"
        elif observed_sha is None:
            status, reason = "INSUFFICIENT_EVIDENCE", "EVIDENCE_MISSING"
    elif operator in {"equals", "receipt_consistent"}:
        if expected_sha is None or observed_sha is None:
            status, reason = "INSUFFICIENT_EVIDENCE", "EVIDENCE_MISSING"
        elif expected_sha != observed_sha:
            status, reason = "FAIL", "CHECK_VALUE_MISMATCH"
    elif operator == "not_equals":
        if expected_sha is None or observed_sha is None:
            status, reason = "INSUFFICIENT_EVIDENCE", "EVIDENCE_MISSING"
        elif expected_sha == observed_sha:
            status, reason = "FAIL", "CHECK_VALUE_UNEXPECTEDLY_EQUAL"
    elif operator == "sha256_matches_subject":
        if expected_sha is not None:
            status, reason = "INVALID_REQUEST", "CHECK_EXPECTATION_NOT_ALLOWED"
        elif observed_sha is None or evidence_sha is None:
            status, reason = "INVALID_REQUEST", "SUBJECT_BINDING_DIGEST_INVALID"
        elif binding_sha is None:
            status, reason = "INVALID_REQUEST", "SUBJECT_BINDING_DIGEST_INVALID"
        elif observed_sha != canonical_sha256(binding_sha):
            status, reason = "INVALID_REQUEST", "SUBJECT_BINDING_DIGEST_INVALID"
        elif binding_sha != subject["subject_sha256"]:
            status, reason = "FAIL", "SUBJECT_DIGEST_MISMATCH"
    elif operator == "state_consistent":
        expected_state_sha = canonical_sha256(subject["lifecycle"])
        if expected_sha != expected_state_sha:
            status, reason = "INVALID_REQUEST", "CHECK_EXPECTATION_NOT_ALLOWED"
        elif observed_sha is None:
            status, reason = "INSUFFICIENT_EVIDENCE", "EVIDENCE_MISSING"
        elif observed_sha != expected_state_sha:
            status, reason = "FAIL", "STATE_EVIDENCE_MISMATCH"
    expected = {
        "check_id": check_id,
        "operator": operator,
        "required": value["required"],
        "expected_sha256": expected_sha,
        "observed_sha256": observed_sha,
        "subject_binding_sha256": binding_sha,
        "evidence_id": evidence_id,
        "evidence_sha256": evidence_sha,
        "status": status,
        "reason_code": reason,
    }
    if dict(value) != expected:
        raise EvaluationError("evaluation receipt check result is contradictory")
    return expected


def validate_evaluation_receipt(
    payload: Any,
    *,
    registry: TrustedValidatorRegistry | None = None,
    expected_subject_id: str | None = None,
    expected_subject_sha256: str | None = None,
) -> dict[str, Any]:
    """Recompute a receipt and optionally bind it to the current subject."""
    _ensure_json_size(payload, MAX_RECEIPT_BYTES, "evaluation receipt")
    if not isinstance(payload, Mapping) or set(payload) != _RECEIPT_FIELDS:
        raise EvaluationError("evaluation receipt schema is malformed")
    if payload.get("schema_version") != EVALUATION_CONTRACT_SCHEMA_VERSION:
        raise EvaluationError("evaluation receipt schema is unsupported")
    trusted = _require_trusted_registry(
        load_trusted_validator_registry() if registry is None else registry
    )
    validator = payload.get("validator")
    if not isinstance(validator, Mapping) or set(validator) != {
        "validator_id", "validator_version", "validator_type", "output_schema_version"
    }:
        raise EvaluationError("evaluation receipt validator schema is malformed")
    definition = trusted.resolve(str(validator.get("validator_id")), str(validator.get("validator_version")))
    if dict(validator) != _validator_output(definition):
        raise EvaluationError("evaluation receipt validator definition is inconsistent")
    subject = _parse_subject(payload.get("subject"))
    if expected_subject_id is not None and subject["subject_id"] != expected_subject_id:
        raise EvaluationError("evaluation receipt subject identity does not match current subject")
    if expected_subject_sha256 is not None:
        if (
            not isinstance(expected_subject_sha256, str)
            or not SHA256_RE.fullmatch(expected_subject_sha256)
            or subject["subject_sha256"] != expected_subject_sha256
        ):
            raise EvaluationError("evaluation receipt subject digest does not match current subject")
    raw_checks = payload.get("checks")
    if not isinstance(raw_checks, list) or len(raw_checks) > MAX_CHECKS:
        raise EvaluationError("evaluation receipt checks are invalid or unbounded")
    checks = [_recompute_check(item, definition, subject) for item in raw_checks]
    check_ids = [item["check_id"] for item in checks]
    if check_ids != sorted(check_ids) or len(check_ids) != len(set(check_ids)):
        raise EvaluationError("evaluation receipt check ordering or identity is invalid")
    evidence = payload.get("evidence")
    if not isinstance(evidence, Mapping) or set(evidence) != {"item_count", "items", "evidence_sha256"}:
        raise EvaluationError("evaluation receipt evidence schema is malformed")
    items = evidence.get("items")
    if (
        not isinstance(items, list)
        or len(items) > MAX_EVIDENCE_ITEMS
        or type(evidence.get("item_count")) is not int
        or evidence.get("item_count") != len(items)
    ):
        raise EvaluationError("evaluation receipt evidence is invalid or unbounded")
    normalized_items: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping) or set(item) != _EVIDENCE_OUTPUT_FIELDS:
            raise EvaluationError("evaluation receipt evidence item is malformed")
        evidence_id = item.get("evidence_id")
        content_sha = item.get("content_sha256")
        summary = item.get("summary")
        if not isinstance(evidence_id, str) or not TOKEN_RE.fullmatch(evidence_id):
            raise EvaluationError("evaluation receipt evidence identity is invalid")
        _reject_secret_identifier(evidence_id, "evaluation receipt evidence identity")
        if not isinstance(content_sha, str) or not SHA256_RE.fullmatch(content_sha):
            raise EvaluationError("evaluation receipt evidence digest is invalid")
        if not isinstance(summary, str) or len(summary) > MAX_OUTPUT_SUMMARY:
            raise EvaluationError("evaluation receipt evidence summary is invalid")
        if not isinstance(item.get("redacted"), bool) or not isinstance(item.get("truncated"), bool):
            raise EvaluationError("evaluation receipt evidence disclosure flags are invalid")
        if item["redacted"] != bool(_REDACTION_MARKER_RE.search(summary)):
            raise EvaluationError("evaluation receipt evidence disclosure flags are invalid")
        if item["truncated"] and (
            len(summary) != MAX_OUTPUT_SUMMARY or not summary.endswith("…")
        ):
            raise EvaluationError("evaluation receipt evidence disclosure flags are invalid")
        if any(pattern.search(summary) for pattern in (
            _WINDOWS_PATH_RE, _UNIX_PRIVATE_PATH_RE, _AUTHORIZATION_RE,
            _SECRET_ASSIGNMENT_RE, _ENVIRONMENT_ASSIGNMENT_RE, _TOKEN_VALUE_RE,
            _CREDENTIAL_URL_RE, _PRIVATE_KEY_MATERIAL_RE, _INJECTION_RE,
        )):
            raise EvaluationError("evaluation receipt evidence summary is not redacted")
        normalized_items.append(dict(item))
    evidence_ids = [item["evidence_id"] for item in normalized_items]
    if evidence_ids != sorted(evidence_ids) or len(evidence_ids) != len(set(evidence_ids)):
        raise EvaluationError("evaluation receipt evidence ordering or identity is invalid")
    check_evidence = sorted(
        (item["evidence_id"], item["evidence_sha256"])
        for item in checks if item["evidence_id"] is not None
    )
    receipt_evidence = [(item["evidence_id"], item["content_sha256"]) for item in normalized_items]
    if check_evidence != receipt_evidence:
        raise EvaluationError("evaluation receipt evidence does not bind its checks")
    expected_evidence_sha = canonical_sha256(
        [
            {"evidence_id": item["evidence_id"], "content_sha256": item["content_sha256"]}
            for item in normalized_items
        ]
    )
    if evidence.get("evidence_sha256") != expected_evidence_sha:
        raise EvaluationError("evaluation receipt evidence digest is inconsistent")
    expected_result = _derive_result(definition, subject, checks)
    result = payload.get("result")
    count_fields = (
        "declared_check_count", "required_check_count",
        "passed_check_count", "failed_check_count",
    )
    if (
        not isinstance(result, Mapping)
        or any(type(result.get(field)) is not int for field in count_fields)
        or result != expected_result
    ):
        raise EvaluationError("evaluation receipt result is contradictory")
    expected_transition = _state_transition(definition, subject, expected_result["state"])
    transition = payload.get("state_transition")
    if (
        not isinstance(transition, Mapping)
        or type(transition.get("permitted")) is not bool
        or type(transition.get("applied")) is not bool
        or transition != expected_transition
    ):
        raise EvaluationError("evaluation receipt state transition is contradictory")
    if payload.get("provenance") != _provenance_output(definition, trusted):
        raise EvaluationError("evaluation receipt provenance is inconsistent")
    expected_redaction = {
        "applied": any(item["redacted"] for item in normalized_items),
        "summary_truncated": any(item["truncated"] for item in normalized_items),
        "authoritative_data_truncated": False,
    }
    redaction = payload.get("redaction")
    if (
        not isinstance(redaction, Mapping)
        or any(type(redaction.get(field)) is not bool for field in expected_redaction)
        or redaction != expected_redaction
    ):
        raise EvaluationError("evaluation receipt redaction status is inconsistent")
    authority = payload.get("authority")
    if (
        payload.get("proof_scope") != _fixed_proof_scope()
        or not isinstance(authority, Mapping)
        or type(authority.get("state_transition_applied")) is not bool
        or authority != _fixed_authority()
    ):
        raise EvaluationError("evaluation receipt authority boundary is invalid")
    body = {key: payload[key] for key in payload if key != "evaluation_id"}
    if payload.get("evaluation_id") != "evaluation:" + canonical_sha256(body):
        raise EvaluationError("evaluation receipt identity is inconsistent")
    return json.loads(json.dumps(payload, ensure_ascii=False))
