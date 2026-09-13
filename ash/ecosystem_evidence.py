"""Deterministic, subject-bound evidence and classification for Slice 3C."""
from __future__ import annotations

import hashlib
from pathlib import PurePosixPath
import re
import unicodedata
from typing import Any, Mapping, Sequence

from .ecosystem_models import (
    EcosystemError,
    GENESIS_STATE,
    IMPLICIT_STATE,
    build_component_identity,
    build_component_revision_identity,
    canonical_json_bytes,
    canonical_sha256,
    parse_json_bytes,
    typed_id,
    validate_authority,
    validate_exact_keys,
    validate_reason_codes,
    validate_sha256,
    validate_state_record,
    validate_transition_receipt,
    validate_typed_id,
    zero_authority,
)
from .ecosystem_policy import TrustedEcosystemSourcePolicy, _require_trusted_source_policy
from .ecosystem_storage import QuarantineStore


_WINDOWS_PATH_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:[A-Z]:[\\/]|(?:\\\\|//)[^\\/\r\n]+[\\/])[^\r\n]*"
)
_UNIX_PRIVATE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9])/(?:home|Users|root|private|var/folders|tmp)/(?:[^\r\n]*)", re.IGNORECASE
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
    r"\bglpat-[A-Za-z0-9_-]{20,}|\b(?:AKIA|ASIA)[0-9A-Z]{16}\b|"
    r"\bxox[A-Za-z]-[A-Za-z0-9-]{8,}|\bxapp-[A-Za-z0-9-]{8,})"
)
_CREDENTIAL_URL_RE = re.compile(r"(?i)\b[A-Za-z][A-Za-z0-9+.-]{1,15}://[^\s/:@]+:[^@\s]+@[^\r\n]+")
_PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]{0,64}PRIVATE KEY-----.*", re.IGNORECASE | re.DOTALL)
_INJECTION_RE = re.compile(
    r"(?i)(?:ignore\s+(?:all\s+|the\s+)?(?:previous\s+|prior\s+)?(?:policy|instructions?)"
    r"|validation_result\s*=\s*pass|validator_id\s*=\s*trusted[-_a-z0-9]*"
    r"|execution_succeeded\s*=\s*true|review_complete\s*=\s*true|host_handoff_ready"
    r"|mcp_execution_authority\s*=\s*granted)"
)
_REDACTION_MARKER_RE = re.compile(
    r"\[REDACTED_(?:AUTHORIZATION|SECRET|ENVIRONMENT|TOKEN|PRIVATE_PATH|CREDENTIAL_URL|"
    r"PRIVATE_KEY|UNTRUSTED_INSTRUCTION|CONTENT)\]"
)

_BIDI_CONTROLS = frozenset(
    chr(value)
    for value in (0x061C, 0x200E, 0x200F, 0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069)
)
_DEPENDENCY_BASENAMES = frozenset(
    {
        "Cargo.lock",
        "Cargo.toml",
        "Gemfile",
        "Gemfile.lock",
        "go.mod",
        "go.sum",
        "package-lock.json",
        "package.json",
        "pnpm-lock.yaml",
        "poetry.lock",
        "pyproject.toml",
        "requirements.txt",
        "setup.cfg",
        "setup.py",
        "uv.lock",
        "yarn.lock",
    }
)
_CREDENTIAL_BASENAMES = frozenset(
    {".env", ".npmrc", ".pypirc", "credentials", "credentials.json", "id_rsa", "id_ed25519"}
)
_CREDENTIAL_SUFFIXES = (".pem", ".key", ".p12", ".pfx")
_SPDX_RE = re.compile(r"^[A-Za-z0-9.+() -]{1,128}$")
_INSTRUCTION_PHRASES = (
    "ignore previous instructions",
    "ignore system instructions",
    "grant host authority",
    "grant mcp authority",
    "grant agent authority",
    "execute without approval",
    "install automatically",
)
_NETWORK_TOKENS = frozenset({"socket", "requests", "urllib", "fetch", "webhook"})
_PERMISSION_TOKENS = frozenset(
    {"allowed-tools", "permissions", "mcp", "shell", "subprocess", "sudo", "delegate", "spawn-agent"}
)
_SECRET_SCAN_CHUNK_CHARS = 65_536
_SECRET_SCAN_OVERLAP_CHARS = 4_095

_STATIC_RULES: dict[str, tuple[str, str, str]] = {
    "archive.nested": ("ARCHIVE_SAFETY", "MEDIUM", "REQUIRES_REVIEW"),
    "automation.workflow": ("HOOK_OR_AUTOMATION", "HIGH", "BLOCKS_REVIEW_COMPLETION"),
    "binary.executable-magic": ("EXECUTABLE_OR_BINARY", "HIGH", "BLOCKS_REVIEW_COMPLETION"),
    "content.bidi-control": ("OBFUSCATION", "HIGH", "BLOCKS_REVIEW_COMPLETION"),
    "content.invalid-role-text": ("UNSUPPORTED_CONTENT", "HIGH", "BLOCKS_REVIEW_COMPLETION"),
    "credential.content": ("NETWORK_OR_CREDENTIAL", "CRITICAL", "BLOCKS_REVIEW_COMPLETION"),
    "credential.filename": ("NETWORK_OR_CREDENTIAL", "CRITICAL", "REJECTS_CANDIDATE"),
    "dependency.manifest": ("DEPENDENCY_OR_INSTALL", "MEDIUM", "REQUIRES_REVIEW"),
    "evidence.license-incomplete": ("LICENSE_CHANGE", "HIGH", "BLOCKS_REVIEW_COMPLETION"),
    "evidence.provenance-inexact": ("PROVENANCE_MISMATCH", "CRITICAL", "BLOCKS_REVIEW_COMPLETION"),
    "hook.git-control": ("HOOK_OR_AUTOMATION", "HIGH", "BLOCKS_REVIEW_COMPLETION"),
    "install.declaration": ("DEPENDENCY_OR_INSTALL", "HIGH", "BLOCKS_REVIEW_COMPLETION"),
    "instruction.control-claim": ("INSTRUCTION_INJECTION", "HIGH", "REQUIRES_REVIEW"),
    "mode.executable": ("EXECUTABLE_OR_BINARY", "HIGH", "BLOCKS_REVIEW_COMPLETION"),
    "network.declaration": ("NETWORK_OR_CREDENTIAL", "MEDIUM", "REQUIRES_REVIEW"),
    "permission.declaration": ("PERMISSION_DECLARATION", "HIGH", "REQUIRES_REVIEW"),
}


def redact_public_summary(value: str) -> tuple[str, bool, bool]:
    """Apply the frozen Slice 3B patterns and then a 256-byte UTF-8 ceiling."""
    if type(value) is not str:
        raise EcosystemError("POLICY_SCHEMA_INVALID", "Public summary must be text")
    redacted = unicodedata.normalize("NFC", value)
    applied = False
    for pattern, replacement in (
        (_REDACTION_MARKER_RE, "[REDACTED_UNTRUSTED_INSTRUCTION]"),
        (_AUTHORIZATION_RE, "[REDACTED_AUTHORIZATION]"),
        (_SECRET_ASSIGNMENT_RE, "[REDACTED_SECRET]"),
        (_ENVIRONMENT_ASSIGNMENT_RE, "[REDACTED_ENVIRONMENT]"),
        (_TOKEN_VALUE_RE, "[REDACTED_TOKEN]"),
        (_CREDENTIAL_URL_RE, "[REDACTED_CREDENTIAL_URL]"),
        (_PRIVATE_KEY_RE, "[REDACTED_PRIVATE_KEY]"),
        (_WINDOWS_PATH_RE, "[REDACTED_PRIVATE_PATH]"),
        (_UNIX_PRIVATE_PATH_RE, "[REDACTED_PRIVATE_PATH]"),
        (_INJECTION_RE, "[REDACTED_UNTRUSTED_INSTRUCTION]"),
    ):
        redacted, count = pattern.subn(replacement, redacted)
        applied = applied or bool(count)
    truncated = len(redacted.encode("utf-8")) > 256
    if truncated:
        encoded = redacted.encode("utf-8")
        limit = 253
        while limit > 0:
            try:
                redacted = encoded[:limit].decode("utf-8") + "…"
                break
            except UnicodeDecodeError:
                limit -= 1
        if applied and not _REDACTION_MARKER_RE.search(redacted):
            prefix = "[REDACTED_CONTENT] "
            remainder = 256 - len(prefix.encode("utf-8")) - len("…".encode("utf-8"))
            # Keep truncation downstream of redaction. Reusing the original
            # value here would reintroduce the very secret/path that was just
            # removed whenever its marker fell beyond the byte boundary.
            encoded = redacted.encode("utf-8")
            while remainder > 0:
                try:
                    redacted = prefix + encoded[:remainder].decode("utf-8") + "…"
                    break
                except UnicodeDecodeError:
                    remainder -= 1
    if any(ord(char) < 32 or ord(char) == 127 for char in redacted):
        redacted = "[REDACTED_CONTENT]"
        applied = True
    return redacted, applied, truncated


def validate_redacted_summary(summary: Any, redaction_applied: Any, truncation_applied: Any) -> str:
    if type(summary) is not str or type(redaction_applied) is not bool or type(truncation_applied) is not bool:
        raise EcosystemError("POLICY_SCHEMA_INVALID", "Public summary metadata is invalid")
    if unicodedata.normalize("NFC", summary) != summary or len(summary.encode("utf-8")) > 256:
        raise EcosystemError("POLICY_SCHEMA_INVALID", "Public summary boundary is invalid")
    if redaction_applied != bool(_REDACTION_MARKER_RE.search(summary)):
        raise EcosystemError("POLICY_SCHEMA_INVALID", "Public summary redaction flag is untruthful")
    if truncation_applied:
        # The generator keeps up to 253 original UTF-8 bytes and appends the
        # three-byte ellipsis, backing up at most three bytes to a code-point
        # boundary.  A short caller-authored ellipsis is therefore not proof
        # that truncation occurred.
        encoded_length = len(summary.encode("utf-8"))
        if not summary.endswith("…") or encoded_length < 253:
            raise EcosystemError(
                "POLICY_SCHEMA_INVALID", "Public summary truncation flag is untruthful"
            )
    for pattern in (
        _AUTHORIZATION_RE,
        _SECRET_ASSIGNMENT_RE,
        _ENVIRONMENT_ASSIGNMENT_RE,
        _TOKEN_VALUE_RE,
        _CREDENTIAL_URL_RE,
        _PRIVATE_KEY_RE,
        _WINDOWS_PATH_RE,
        _UNIX_PRIVATE_PATH_RE,
        _INJECTION_RE,
    ):
        if pattern.search(summary):
            raise EcosystemError("POLICY_SCHEMA_INVALID", "Public summary still contains private content")
    return summary


def _validate_revision(record: Any, policy: TrustedEcosystemSourcePolicy) -> dict[str, Any]:
    fields = {
        "schema_version",
        "revision_id",
        "source_key",
        "source_id",
        "commit_object_format",
        "commit_oid",
        "input_sha256",
        "input_size",
        "tree_id",
        "policy_semantic_sha256",
        "intake_attempt_result_id",
        "authority",
    }
    revision = validate_exact_keys(record, fields, "revision record")
    if revision["schema_version"] != "nexus.ecosystem-revision.v1":
        raise EcosystemError("PROVENANCE_CONFLICT", "Revision schema is unsupported")
    trusted = _require_trusted_source_policy(policy)
    source = trusted.source(revision["source_key"])
    from .ecosystem_models import build_revision_identity

    expected = build_revision_identity(
        source_id=revision["source_id"],
        commit_object_format=revision["commit_object_format"],
        commit_oid=revision["commit_oid"],
        input_sha256=revision["input_sha256"],
        tree_id=revision["tree_id"],
    )
    if (
        revision["revision_id"] != expected
        or revision["source_id"] != source["source_id"]
        or revision["policy_semantic_sha256"] != trusted.policy_semantic_sha256
        or type(revision["input_size"]) is not int
        or revision["input_size"] < 0
    ):
        raise EcosystemError("PROVENANCE_CONFLICT", "Revision binding is invalid")
    validate_typed_id(revision["intake_attempt_result_id"], "intake-attempt-result")
    validate_authority(revision["authority"])
    return {key: record[key] for key in record}


def _validate_tree(record: Any) -> dict[str, Any]:
    tree = validate_exact_keys(
        record, {"schema_version", "tree_id", "entries", "stripped_prefix_sha256", "authority"}, "tree record"
    )
    if tree["schema_version"] != "nexus.ecosystem-tree.v1" or type(tree["entries"]) is not list:
        raise EcosystemError("ARCHIVE_INTEGRITY_INVALID", "Tree record is invalid")
    from .ecosystem_models import build_tree

    expected, body = build_tree(tree["entries"])
    if tree["tree_id"] != expected or body["entries"] != tree["entries"]:
        raise EcosystemError("ARCHIVE_INTEGRITY_INVALID", "Tree identity is invalid")
    validate_sha256(tree["stripped_prefix_sha256"], "stripped-prefix digest")
    validate_authority(tree["authority"])
    return {key: record[key] for key in record}


def _policy_source_for_id(
    policy: TrustedEcosystemSourcePolicy, source_id: str
) -> dict[str, Any]:
    validate_typed_id(source_id, "source")
    matches: list[dict[str, Any]] = []
    for source in policy.to_dict()["sources"]:
        candidate = policy.source(source["source_key"])
        if candidate["source_id"] == source_id:
            matches.append(candidate)
    if len(matches) != 1:
        raise EcosystemError("SOURCE_IDENTITY_CONFLICT", "Subject source is absent or ambiguous")
    return matches[0]


def _validate_intake_attempt(
    value: Any,
    *,
    revision: Mapping[str, Any],
    policy: TrustedEcosystemSourcePolicy,
) -> dict[str, Any]:
    fields = {
        "schema_version",
        "attempt_id",
        "attempt_result_id",
        "bridge_id",
        "source_key",
        "source_id",
        "commit_object_format",
        "commit_oid",
        "input_sha256",
        "input_size",
        "policy_semantic_sha256",
        "intake_algorithm_id",
        "intake_algorithm_version",
        "result",
        "tree_id",
        "revision_id",
        "reason_codes",
        "authority",
    }
    record = validate_exact_keys(value, fields, "intake attempt")
    if record["schema_version"] != "nexus.ecosystem-intake-attempt.v1":
        raise EcosystemError("PROVENANCE_CONFLICT", "Intake attempt schema is unsupported")
    checked_revision = _validate_revision(revision, policy)
    validate_typed_id(record["bridge_id"], "bridge")
    base = {
        key: record[key]
        for key in (
            "bridge_id",
            "source_key",
            "source_id",
            "commit_object_format",
            "commit_oid",
            "input_sha256",
            "input_size",
            "policy_semantic_sha256",
            "intake_algorithm_id",
            "intake_algorithm_version",
        )
    }
    if (
        record["attempt_id"] != typed_id("intake-attempt", base)
        or record["result"] != "REVISION_CREATED"
        or record["tree_id"] != checked_revision["tree_id"]
        or record["revision_id"] != checked_revision["revision_id"]
        or record["attempt_result_id"] != checked_revision["intake_attempt_result_id"]
        or any(
            record[field] != checked_revision[field]
            for field in (
                "source_key",
                "source_id",
                "commit_object_format",
                "commit_oid",
                "input_sha256",
                "input_size",
                "policy_semantic_sha256",
            )
        )
        or record["reason_codes"] != []
    ):
        raise EcosystemError("PROVENANCE_CONFLICT", "Successful intake binding is inconsistent")
    validate_typed_id(record["attempt_id"], "intake-attempt")
    validate_typed_id(record["attempt_result_id"], "intake-attempt-result")
    result_body = {
        "attempt_id": record["attempt_id"],
        **base,
        "result": record["result"],
        "tree_id": record["tree_id"],
        "revision_id": record["revision_id"],
        "reason_codes": record["reason_codes"],
        "authority": record["authority"],
    }
    if record["attempt_result_id"] != typed_id("intake-attempt-result", result_body):
        raise EcosystemError("PROVENANCE_CONFLICT", "Intake result identity is inconsistent")
    validate_authority(record["authority"])
    return dict(record)


def _validate_component_record(
    value: Any,
    *,
    revision: Mapping[str, Any],
    tree: Mapping[str, Any],
    policy: TrustedEcosystemSourcePolicy,
) -> dict[str, Any]:
    fields = {
        "schema_version",
        "component_revision_id",
        "component_id",
        "source_id",
        "revision_id",
        "component_root",
        "component_manifest_sha256",
        "entries",
        "authority",
    }
    record = validate_exact_keys(value, fields, "component revision")
    if record["schema_version"] != "nexus.ecosystem-component-revision.v1":
        raise EcosystemError("CLASSIFICATION_UNRESOLVED", "Component revision schema is unsupported")
    checked_revision = _validate_revision(revision, policy)
    checked_tree = _validate_tree(tree)
    if (
        checked_tree["tree_id"] != checked_revision["tree_id"]
        or record["source_id"] != checked_revision["source_id"]
        or record["revision_id"] != checked_revision["revision_id"]
    ):
        raise EcosystemError("SUBJECT_MISMATCH", "Component parent binding is inconsistent")
    component_id = build_component_identity(
        source_id=record["source_id"], component_root=record["component_root"]
    )
    if record["component_id"] != component_id:
        raise EcosystemError("SUBJECT_MISMATCH", "Component identity is inconsistent")
    if type(record["entries"]) is not list:
        raise EcosystemError("CLASSIFICATION_UNRESOLVED", "Component manifest is invalid")
    entries: list[dict[str, Any]] = []
    tree_entries = {item["path"]: item for item in checked_tree["entries"]}
    for item in record["entries"]:
        checked = validate_exact_keys(
            item, {"path", "mode", "size", "sha256"}, "component manifest entry"
        )
        if not (
            checked["path"] == record["component_root"]
            or checked["path"].startswith(record["component_root"] + "/")
        ):
            raise EcosystemError(
                "SUBJECT_MISMATCH", "Component entry escapes its immutable component root"
            )
        if checked["path"] not in tree_entries:
            raise EcosystemError("SUBJECT_MISMATCH", "Component entry is absent from its tree")
        expected_tree = tree_entries[checked["path"]]
        if any(checked[key] != expected_tree[key] for key in ("path", "mode", "size", "sha256")):
            raise EcosystemError("SUBJECT_MISMATCH", "Component entry does not match its tree")
        entries.append(dict(checked))
    if entries != sorted(entries, key=lambda item: item["path"].encode("utf-8")):
        raise EcosystemError("CLASSIFICATION_UNRESOLVED", "Component manifest order is invalid")
    if len({item["path"] for item in entries}) != len(entries):
        raise EcosystemError("CLASSIFICATION_UNRESOLVED", "Component manifest repeats a path")
    manifest_sha256 = canonical_sha256({"entries": entries})
    expected_revision_id = build_component_revision_identity(
        revision_id=record["revision_id"],
        component_id=record["component_id"],
        component_manifest_sha256=manifest_sha256,
    )
    if (
        record["component_manifest_sha256"] != manifest_sha256
        or record["component_revision_id"] != expected_revision_id
    ):
        raise EcosystemError("SUBJECT_MISMATCH", "Component manifest identity is inconsistent")
    validate_authority(record["authority"])
    return dict(record)


def _subject_scope(
    *,
    subject_id: str,
    subject_record: Mapping[str, Any],
    tree: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    parent_revision: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    validate_typed_id(subject_id)
    if subject_id.startswith("revision/"):
        checked_subject, checked_tree, _attempt = _validate_authoritative_revision_snapshot(
            revision=subject_record,
            tree=tree,
            store=store,
            policy=policy,
        )
        if subject_id != checked_subject["revision_id"]:
            raise EcosystemError("SUBJECT_MISMATCH", "Revision subject and tree do not match")
        return checked_subject, list(checked_tree["entries"]), checked_subject["source_id"]
    if subject_id.startswith("component-revision/"):
        if parent_revision is None:
            raise EcosystemError("SUBJECT_MISMATCH", "Component subject requires its parent revision")
        checked_subject, _parent, checked_tree, _attempt = (
            _validate_authoritative_component_snapshot(
                component=subject_record,
                parent_revision=parent_revision,
                tree=tree,
                store=store,
                policy=policy,
            )
        )
        if subject_id != checked_subject["component_revision_id"]:
            raise EcosystemError("SUBJECT_MISMATCH", "Component subject identity does not match")
        tree_by_path = {item["path"]: item for item in checked_tree["entries"]}
        entries = [tree_by_path[item["path"]] for item in checked_subject["entries"]]
        return checked_subject, entries, checked_subject["source_id"]
    raise EcosystemError("SUBJECT_MISMATCH", "Evidence subject type is unsupported")


def _read_entry(
    store: QuarantineStore,
    entry: Mapping[str, Any],
    *,
    maximum_bytes: int,
) -> bytes:
    if type(store) is not QuarantineStore:
        raise EcosystemError("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    if (
        type(maximum_bytes) is not int
        or maximum_bytes < 0
        or type(entry.get("size")) is not int
        or entry["size"] < 0
    ):
        raise EcosystemError("POLICY_SCHEMA_INVALID", "Evidence byte boundary is invalid")
    if entry["size"] > maximum_bytes:
        raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", "Evidence bytes exceed their role limit")
    raw = store.read_blob(entry["sha256"], maximum_bytes=maximum_bytes)
    if len(raw) != entry["size"] or hashlib.sha256(raw).hexdigest() != entry["sha256"]:
        raise EcosystemError("CAS_OBJECT_CONFLICT", "Evidence bytes do not match the tree entry")
    return raw


def _validate_authoritative_revision_snapshot(
    *,
    revision: Mapping[str, Any],
    tree: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    intake_attempt: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Rebind caller projections to the exact persisted revision snapshot."""
    trusted = _require_trusted_source_policy(policy)
    if type(store) is not QuarantineStore:
        raise EcosystemError("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    store._require_policy(trusted)
    checked_revision = _validate_revision(revision, trusted)
    checked_tree = _validate_tree(tree)
    if checked_revision["tree_id"] != checked_tree["tree_id"]:
        raise EcosystemError("SUBJECT_MISMATCH", "Revision and tree identities disagree")
    maximum = trusted.resource_limits["max_record_bytes"]
    revision_digest = checked_revision["revision_id"].split("/", 1)[1]
    tree_digest = checked_tree["tree_id"].split("/", 1)[1]
    result_digest = checked_revision["intake_attempt_result_id"].split("/", 1)[1]
    stored_revision = store.read_record(
        f"revisions/sha256/{revision_digest}.json", maximum_bytes=maximum
    )
    stored_tree = store.read_record(
        f"trees/sha256/{tree_digest}.json", maximum_bytes=maximum
    )
    stored_attempt = store.read_record(
        f"evidence/sha256/{result_digest}.json", maximum_bytes=maximum
    )
    if stored_revision != checked_revision or stored_tree != checked_tree:
        raise EcosystemError("SUBJECT_MISMATCH", "Snapshot projection is not the authoritative record")
    if intake_attempt is not None and (
        type(intake_attempt) is not dict or dict(intake_attempt) != stored_attempt
    ):
        raise EcosystemError("PROVENANCE_CONFLICT", "Intake projection is not the authoritative record")
    checked_attempt = _validate_intake_attempt(
        stored_attempt, revision=checked_revision, policy=trusted
    )
    attempt_digest = checked_attempt["attempt_id"].split("/", 1)[1]
    canonical_attempt = store.read_record(
        f"intake-attempts/sha256/{attempt_digest}/{result_digest}.json",
        maximum_bytes=maximum,
    )
    if canonical_attempt != checked_attempt:
        raise EcosystemError(
            "PROVENANCE_CONFLICT", "Canonical intake result and evidence mirror disagree"
        )

    quarantine_view = store.read_record(
        f"quarantine/{revision_digest}.json", maximum_bytes=maximum
    )
    expected_quarantine_fields = {
        "schema_version",
        "revision_id",
        "source_id",
        "genesis_state_record_id",
        "initial_disposition",
        "authority",
    }
    if (
        set(quarantine_view) != expected_quarantine_fields
        or quarantine_view["schema_version"] != "nexus.ecosystem-quarantine-view.v1"
        or quarantine_view["revision_id"] != checked_revision["revision_id"]
        or quarantine_view["source_id"] != checked_revision["source_id"]
        or quarantine_view["initial_disposition"] != "QUARANTINED"
    ):
        raise EcosystemError("PROVENANCE_CONFLICT", "Quarantine completion marker is invalid")
    validate_authority(quarantine_view["authority"])
    validate_typed_id(quarantine_view["genesis_state_record_id"], "state-record")

    state_digest = quarantine_view["genesis_state_record_id"].split("/", 1)[1]
    genesis_state = validate_state_record(
        store.read_record(f"state/sha256/{state_digest}.json", maximum_bytes=maximum)
    )
    transition_digest = genesis_state["transition_id"].split("/", 1)[1]
    genesis_transition = validate_transition_receipt(
        store.read_record(
            f"evidence/sha256/{transition_digest}.json", maximum_bytes=maximum
        )
    )
    subject_sha256 = canonical_sha256(checked_revision)
    if (
        genesis_state["state_record_id"] != quarantine_view["genesis_state_record_id"]
        or genesis_state["subject_id"] != checked_revision["revision_id"]
        or genesis_state["subject_sha256"] != subject_sha256
        or genesis_state["previous_state_record_id"] is not None
        or genesis_state["transition_id"] != genesis_transition["transition_id"]
        or genesis_state["state"] != GENESIS_STATE.as_dict()
        or genesis_state["evidence_ids"] != [checked_attempt["attempt_result_id"]]
        or genesis_state["policy_semantic_sha256"] != trusted.policy_semantic_sha256
        or genesis_transition["subject_id"] != checked_revision["revision_id"]
        or genesis_transition["subject_sha256"] != subject_sha256
        or genesis_transition["from_state"] != IMPLICIT_STATE.as_dict()
        or genesis_transition["to_state"] != GENESIS_STATE.as_dict()
        or genesis_transition["transition_axis"] != "possession"
        or genesis_transition["evidence_ids"] != [checked_attempt["attempt_result_id"]]
        or genesis_transition["evaluation_receipt_sha256s"]
        or genesis_transition["evaluation_profile_id"] is not None
        or genesis_transition["evaluation_profile_sha256"] is not None
        or genesis_transition["policy_semantic_sha256"] != trusted.policy_semantic_sha256
        or genesis_transition["reason_codes"]
    ):
        raise EcosystemError("PROVENANCE_CONFLICT", "Genesis intake lineage is incomplete or invalid")
    _read_entry(
        store,
        {"sha256": checked_revision["input_sha256"], "size": checked_revision["input_size"]},
        maximum_bytes=trusted.resource_limits["max_input_bytes"],
    )
    for entry in checked_tree["entries"]:
        _read_entry(
            store,
            entry,
            maximum_bytes=trusted.resource_limits["max_file_bytes"],
        )
    return checked_revision, checked_tree, checked_attempt


def _validate_authoritative_component_snapshot(
    *,
    component: Mapping[str, Any],
    parent_revision: Mapping[str, Any],
    tree: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    intake_attempt: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    parent, checked_tree, checked_attempt = _validate_authoritative_revision_snapshot(
        revision=parent_revision,
        tree=tree,
        store=store,
        policy=policy,
        intake_attempt=intake_attempt,
    )
    checked_component = _validate_component_record(
        component, revision=parent, tree=checked_tree, policy=policy
    )
    digest = checked_component["component_revision_id"].split("/", 1)[1]
    stored_component = store.read_record(
        f"components/sha256/{digest}.json",
        maximum_bytes=policy.resource_limits["max_record_bytes"],
    )
    if stored_component != checked_component:
        raise EcosystemError("SUBJECT_MISMATCH", "Component projection is not authoritative")
    return checked_component, parent, checked_tree, checked_attempt


def build_provenance_evidence(
    *,
    revision: Mapping[str, Any],
    tree: Mapping[str, Any],
    intake_attempt: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    observed_ref: str | None = None,
    provider_repository_id: str | None = None,
    signature_state: str = "NOT_EVALUATED",
    signature_evidence_sha256: str | None = None,
) -> dict[str, Any]:
    trusted = _require_trusted_source_policy(policy)
    for label, value in (
        ("observed ref", observed_ref),
        ("provider repository identifier", provider_repository_id),
    ):
        if value is not None:
            if type(value) is not str:
                raise EcosystemError("PROVENANCE_INSUFFICIENT", f"{label} is invalid")
            try:
                encoded = value.encode("utf-8", errors="strict")
            except UnicodeEncodeError:
                raise EcosystemError("PROVENANCE_INSUFFICIENT", f"{label} is invalid") from None
            if not encoded or len(encoded) > trusted.resource_limits["max_text_evidence_bytes"]:
                raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", f"{label} exceeds its private bound")
    checked, checked_tree, _checked_attempt = _validate_authoritative_revision_snapshot(
        revision=revision,
        tree=tree,
        intake_attempt=intake_attempt,
        store=store,
        policy=trusted,
    )
    if signature_state not in {"NOT_EVALUATED", "MISSING", "PRESENT_UNVERIFIED"}:
        raise EcosystemError("PROVENANCE_INSUFFICIENT", "Signature state is unsupported")
    if (signature_state == "PRESENT_UNVERIFIED") != (signature_evidence_sha256 is not None):
        raise EcosystemError("PROVENANCE_INSUFFICIENT", "Signature evidence binding is inconsistent")
    if signature_evidence_sha256 is not None:
        validate_sha256(signature_evidence_sha256, "signature evidence digest")
        # PRESENT_UNVERIFIED means that the signature has not been
        # cryptographically trusted, not that its evidence locator may be
        # caller-invented. Re-read the bounded CAS object so validation binds
        # the digest to immutable bytes while retaining zero signature
        # verification authority.
        store.read_blob(
            signature_evidence_sha256,
            maximum_bytes=trusted.resource_limits["max_text_evidence_bytes"],
        )
    body: dict[str, Any] = {
        "source_key": checked["source_key"],
        "source_id": checked["source_id"],
        "revision_id": checked["revision_id"],
        "input_kind": "pre_supplied_zip",
        "input_sha256": checked["input_sha256"],
        "tree_id": checked["tree_id"],
        "commit_object_format": checked["commit_object_format"],
        "commit_oid": checked["commit_oid"],
        "observed_ref_sha256": hashlib.sha256(observed_ref.encode("utf-8")).hexdigest() if observed_ref is not None else None,
        "provider_repository_id_sha256": hashlib.sha256(provider_repository_id.encode("utf-8")).hexdigest() if provider_repository_id is not None else None,
        "signature_state": signature_state,
        "signature_evidence_sha256": signature_evidence_sha256,
        "source_policy_id": trusted.policy_id,
        "source_policy_version": trusted.policy_version,
        "source_policy_semantic_sha256": trusted.policy_semantic_sha256,
        "integrity_manifest_sha256": trusted.integrity_manifest_sha256,
        "result": "EXACT_SUBJECT_BOUND",
        "reason_codes": [],
        "authority": zero_authority(),
    }
    return {
        "schema_version": "nexus.ecosystem-provenance-evidence.v1",
        "evidence_id": typed_id(
            "evidence", body, domain="nexus.ecosystem-provenance-evidence.v1"
        ),
        **body,
    }


def validate_provenance_evidence(
    value: Any,
    *,
    revision: Mapping[str, Any],
    tree: Mapping[str, Any],
    intake_attempt: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
) -> dict[str, Any]:
    if type(value) is not dict:
        raise EcosystemError("PROVENANCE_CONFLICT", "Provenance evidence schema is invalid")
    fields = {
        "schema_version",
        "evidence_id",
        "source_key",
        "source_id",
        "revision_id",
        "input_kind",
        "input_sha256",
        "tree_id",
        "commit_object_format",
        "commit_oid",
        "observed_ref_sha256",
        "provider_repository_id_sha256",
        "signature_state",
        "signature_evidence_sha256",
        "source_policy_id",
        "source_policy_version",
        "source_policy_semantic_sha256",
        "integrity_manifest_sha256",
        "result",
        "reason_codes",
        "authority",
    }
    if set(value) != fields:
        raise EcosystemError("PROVENANCE_CONFLICT", "Provenance evidence schema is invalid")
    if value["schema_version"] != "nexus.ecosystem-provenance-evidence.v1":
        raise EcosystemError("PROVENANCE_CONFLICT", "Provenance evidence schema is unsupported")
    for field in ("observed_ref_sha256", "provider_repository_id_sha256"):
        if value[field] is not None:
            validate_sha256(value[field], field)
    # The informational values are already projected to digests. Build the
    # exact mandatory binding from current CAS/tree/attempt state, then insert
    # only those validated digest projections before recomputing the identity.
    expected = build_provenance_evidence(
        revision=revision,
        tree=tree,
        intake_attempt=intake_attempt,
        store=store,
        policy=policy,
        observed_ref=None,
        provider_repository_id=None,
        signature_state=value["signature_state"],
        signature_evidence_sha256=value["signature_evidence_sha256"],
    )
    expected["observed_ref_sha256"] = value["observed_ref_sha256"]
    expected["provider_repository_id_sha256"] = value["provider_repository_id_sha256"]
    body = {key: expected[key] for key in expected if key not in {"schema_version", "evidence_id"}}
    expected["evidence_id"] = typed_id(
        "evidence", body, domain="nexus.ecosystem-provenance-evidence.v1"
    )
    if value != expected:
        raise EcosystemError("PROVENANCE_CONFLICT", "Provenance evidence does not match its subject")
    return dict(expected)


def _license_marker(expression: str, text: str) -> bool:
    folded = " ".join(text.casefold().split())
    if expression.casefold() == "mit":
        return "mit license" in folded and "permission is hereby granted" in folded
    if expression.casefold() == "apache-2.0":
        return "apache license" in folded and "version 2.0" in folded
    return False


def _validate_spdx_claim(value: Any) -> str | None:
    if value is None:
        return None
    if type(value) is not str or not value.isascii() or not _SPDX_RE.fullmatch(value):
        raise EcosystemError("LICENSE_UNSUPPORTED", "SPDX declaration is outside the v1 claim grammar")
    return value


def inspect_license_evidence(
    *,
    subject_id: str,
    subject_record: Mapping[str, Any],
    tree: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    parent_revision: Mapping[str, Any] | None = None,
    declared_spdx_expression: str | None = None,
) -> dict[str, Any]:
    trusted = _require_trusted_source_policy(policy)
    checked_subject, entries, source_id = _subject_scope(
        subject_id=subject_id,
        subject_record=subject_record,
        tree=tree,
        store=store,
        policy=trusted,
        parent_revision=parent_revision,
    )
    source = _policy_source_for_id(trusted, source_id)
    frozen = source["frozen_evidence"]
    policy_claim = (
        frozen["spdx_expression"]
        if frozen["license_state"] == "VERIFIED_DECLARATION"
        else None
    )
    policy_claim = _validate_spdx_claim(policy_claim)
    if declared_spdx_expression is not None and declared_spdx_expression != policy_claim:
        raise EcosystemError("LICENSE_MISMATCH", "Caller license claim does not match trusted policy")
    declared_spdx_expression = policy_claim
    subject_sha256 = canonical_sha256(checked_subject)
    license_items: list[dict[str, Any]] = []
    notice_items: list[dict[str, Any]] = []
    matching_markers = 0
    for entry in entries:
        basename = PurePosixPath(entry["path"]).name.casefold()
        is_license = basename.startswith(("license", "licence", "copying"))
        is_notice = basename.startswith("notice")
        if not is_license and not is_notice:
            continue
        if len(license_items) + len(notice_items) >= trusted.resource_limits["max_license_files"]:
            raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", "License-file count exceeds policy")
        raw = _read_entry(
            store,
            entry,
            maximum_bytes=trusted.resource_limits["max_license_or_dependency_file_bytes"],
        )
        item = {
            "path_sha256": hashlib.sha256(entry["path"].encode("utf-8")).hexdigest(),
            "content_sha256": entry["sha256"],
            "size": len(raw),
        }
        if is_license:
            license_items.append(item)
            try:
                text = raw.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                text = ""
            if declared_spdx_expression is not None and _license_marker(declared_spdx_expression, text):
                matching_markers += 1
        else:
            notice_items.append(item)
    license_items.sort(key=lambda item: item["path_sha256"])
    notice_items.sort(key=lambda item: item["path_sha256"])
    if not license_items:
        result, reasons = "MISSING", ["LICENSE_MISSING"]
    elif declared_spdx_expression is None or len(license_items) > 1:
        result, reasons = "AMBIGUOUS", ["LICENSE_AMBIGUOUS"]
    elif declared_spdx_expression not in {"MIT", "Apache-2.0"}:
        result, reasons = "UNSUPPORTED", ["LICENSE_UNSUPPORTED"]
    elif matching_markers == 1:
        result, reasons = "MATCHES_POLICY_DECLARATION", []
    else:
        result, reasons = "MISMATCH", ["LICENSE_MISMATCH"]
    body: dict[str, Any] = {
        "subject_id": subject_id,
        "subject_sha256": subject_sha256,
        "declared_spdx_expression": declared_spdx_expression,
        "license_files": license_items,
        "notice_files": notice_items,
        "license_result": result,
        "redistribution_state": "LOCAL_REFERENCE_ONLY" if result == "MATCHES_POLICY_DECLARATION" else "NOT_EVALUATED",
        "policy_semantic_sha256": trusted.policy_semantic_sha256,
        "reason_codes": reasons,
        "authority": zero_authority(),
    }
    return {
        "schema_version": "nexus.ecosystem-license-evidence.v1",
        "evidence_id": typed_id("evidence", body, domain="nexus.ecosystem-license-evidence.v1"),
        **body,
    }


def validate_license_evidence(
    value: Any,
    *,
    subject_record: Mapping[str, Any],
    tree: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    parent_revision: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if type(value) is not dict:
        raise EcosystemError("LICENSE_MISMATCH", "License evidence schema is invalid")
    expected = inspect_license_evidence(
        subject_id=value.get("subject_id"),
        subject_record=subject_record,
        tree=tree,
        store=store,
        policy=policy,
        parent_revision=parent_revision,
        declared_spdx_expression=value.get("declared_spdx_expression"),
    )
    if value != expected:
        raise EcosystemError("LICENSE_MISMATCH", "License evidence does not match current subject bytes")
    return dict(expected)


def _role_text(path: str) -> bool:
    basename = PurePosixPath(path).name
    first = path.split("/", 1)[0]
    return (
        basename == "SKILL.md"
        or (first in {"agents", ".agents", "docs"} and PurePosixPath(path).suffix.casefold() in {".md", ".rst", ".txt"})
        or basename in _DEPENDENCY_BASENAMES
        or basename.casefold().startswith(("license", "licence", "copying", "notice"))
        or bool(_candidate_kinds(path))
    )


def _role_text_limit(path: str, policy: TrustedEcosystemSourcePolicy) -> int | None:
    basename = PurePosixPath(path).name
    first = path.split("/", 1)[0]
    if basename in _DEPENDENCY_BASENAMES or basename.casefold().startswith(
        ("license", "licence", "copying", "notice")
    ):
        return policy.resource_limits["max_license_or_dependency_file_bytes"]
    if _role_text(path) or basename == "README.md" or first in {"agents", ".agents", "docs"}:
        return policy.resource_limits["max_instruction_file_bytes"]
    return None


def _secret_match(raw: bytes) -> bool:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return False
    patterns = (
        _SECRET_ASSIGNMENT_RE,
        _ENVIRONMENT_ASSIGNMENT_RE,
        _TOKEN_VALUE_RE,
        _CREDENTIAL_URL_RE,
        _PRIVATE_KEY_RE,
    )
    # The policy freezes a 4,096-byte maximum detector match and therefore a
    # 4,095-byte overlap.  Scan bounded windows rather than treating an entire
    # candidate file as one regex subject.  A match that begins immediately
    # before a chunk boundary remains visible in the next window, while memory
    # and regex work stay proportional to the already-bounded input.
    cursor = 0
    while cursor < len(text):
        end = min(
            len(text),
            cursor + _SECRET_SCAN_CHUNK_CHARS + _SECRET_SCAN_OVERLAP_CHARS,
        )
        window = text[cursor:end]
        if any(pattern.search(window) for pattern in patterns):
            return True
        if end == len(text):
            break
        cursor += _SECRET_SCAN_CHUNK_CHARS
    return False


def _text_tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z][a-z0-9_-]*", text.casefold()))


def _matched_rules(
    path: str,
    entry: Mapping[str, Any],
    raw: bytes,
    policy: TrustedEcosystemSourcePolicy,
) -> list[str]:
    rules: list[str] = []
    basename = PurePosixPath(path).name
    lower_basename = basename.casefold()
    lower_path = path.casefold()
    magic = raw[:512]
    nested = entry["kind"] == "archive" or magic.startswith(
        (b"PK\x03\x04", b"\x1f\x8b", b"7z\xbc\xaf'\x1c", b"Rar!\x1a\x07")
    ) or (len(magic) >= 262 and magic[257:262] == b"ustar")
    if nested:
        rules.append("archive.nested")
    if path in {"Jenkinsfile", ".gitlab-ci.yml", ".circleci/config.yml"} or lower_path.startswith(".github/workflows/"):
        rules.append("automation.workflow")
    if magic.startswith((b"MZ", b"\x7fELF", b"\x00asm", b"\xca\xfe\xba\xbe", b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf")):
        rules.append("binary.executable-magic")
    role = entry["kind"] == "regular" and _role_text(path)
    text: str | None
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        text = None
    if text is not None and any(char in _BIDI_CONTROLS for char in text):
        rules.append("content.bidi-control")
    role_limit = _role_text_limit(path, policy)
    if role and (text is None or b"\x00" in raw or (role_limit is not None and len(raw) > role_limit)):
        rules.append("content.invalid-role-text")
    if _secret_match(raw):
        rules.append("credential.content")
    if lower_basename in _CREDENTIAL_BASENAMES or lower_basename.endswith(_CREDENTIAL_SUFFIXES):
        rules.append("credential.filename")
    if basename in _DEPENDENCY_BASENAMES:
        rules.append("dependency.manifest")
    if lower_path.startswith(".git/hooks/") or path in {".gitattributes", ".gitmodules"}:
        rules.append("hook.git-control")
    installer = lower_basename in {"install.py", "bootstrap.py"}
    if basename == "package.json" and text is not None:
        try:
            payload = parse_json_bytes(
                raw,
                maximum_bytes=policy.resource_limits["max_license_or_dependency_file_bytes"],
                label="candidate package manifest",
            )
            installer = installer or (
                type(payload) is dict
                and type(payload.get("scripts")) is dict
                and bool(set(payload["scripts"]) & {"preinstall", "install", "postinstall", "prepare"})
            )
        except EcosystemError:
            rules.append("content.invalid-role-text")
    if basename == "pyproject.toml" and text is not None and re.search(r"(?m)^\[build-system\]\s*$", text):
        installer = True
    if installer:
        rules.append("install.declaration")
    if text is not None and role:
        collapsed = " ".join(text.casefold().split())
        if any(phrase in collapsed for phrase in _INSTRUCTION_PHRASES):
            rules.append("instruction.control-claim")
        tokens = _text_tokens(text)
        if re.search(r"(?i)\b(?:https?|wss?)://", text) or tokens & _NETWORK_TOKENS:
            rules.append("network.declaration")
        if tokens & _PERMISSION_TOKENS:
            rules.append("permission.declaration")
    if entry["mode"] == "regular_executable":
        rules.append("mode.executable")
    return sorted(set(rules))


def _finding(
    *, subject_id: str, subject_sha256: str, rule_id: str, path: str | None, evidence_sha256: str, policy: TrustedEcosystemSourcePolicy
) -> dict[str, Any]:
    category, severity, disposition = _STATIC_RULES[rule_id]
    reason = {
        "REQUIRES_REVIEW": "STATIC_REVIEW_REQUIRED",
        "BLOCKS_REVIEW_COMPLETION": "STATIC_FINDING_BLOCKING",
        "REJECTS_CANDIDATE": "STATIC_FINDING_REJECTED",
    }[disposition]
    path_digest = hashlib.sha256(path.encode("utf-8")).hexdigest() if path is not None else None
    summary, redacted, truncated = redact_public_summary(
        f"Static rule {rule_id} matched exact evidence {evidence_sha256[:16]}."
    )
    body: dict[str, Any] = {
        "subject_id": subject_id,
        "subject_sha256": subject_sha256,
        "rule_id": rule_id,
        "rule_version": "1",
        "analyzer_id": "nexus.ecosystem-static",
        "analyzer_version": "1",
        "analyzer_config_sha256": policy.static_analyzer_config_sha256,
        "category": category,
        "severity": severity,
        "disposition": disposition,
        "path_sha256": path_digest,
        "evidence_sha256": evidence_sha256,
        "reason_code": reason,
        "summary": summary,
        "redaction_applied": redacted,
        "truncation_applied": truncated,
        "authority": zero_authority(),
    }
    return {
        "schema_version": "nexus.ecosystem-static-finding.v1",
        "finding_id": typed_id("finding", body),
        **body,
    }


def _build_static_report(
    *,
    subject_id: str,
    subject_sha256: str,
    findings: list[dict[str, Any]],
    status: str,
    result: str,
    reasons: list[str],
    policy: TrustedEcosystemSourcePolicy,
) -> dict[str, Any]:
    findings.sort(key=lambda item: item["finding_id"])
    validate_reason_codes(reasons, required=status == "INSUFFICIENT_EVIDENCE")
    counts = {
        "observed": sum(item["disposition"] == "OBSERVED" for item in findings),
        "requires_review": sum(item["disposition"] == "REQUIRES_REVIEW" for item in findings),
        "blocking": sum(item["disposition"] == "BLOCKS_REVIEW_COMPLETION" for item in findings),
        "rejecting": sum(item["disposition"] == "REJECTS_CANDIDATE" for item in findings),
    }
    body: dict[str, Any] = {
        "subject_id": subject_id,
        "subject_sha256": subject_sha256,
        "analyzer_id": "nexus.ecosystem-static",
        "analyzer_version": "1",
        "analyzer_config_sha256": policy.static_analyzer_config_sha256,
        "finding_ids": [item["finding_id"] for item in findings],
        "counts": counts,
        "analysis_status": status,
        "result": result,
        "reason_codes": reasons,
        "authority": zero_authority(),
    }
    report = {
        "schema_version": "nexus.ecosystem-static-report.v1",
        "report_id": typed_id("static-report", body),
        **body,
    }
    return report


def analyze_static_evidence(
    *,
    subject_id: str,
    subject_record: Mapping[str, Any],
    tree: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    provenance_evidence: Mapping[str, Any] | None = None,
    license_evidence: Mapping[str, Any] | None = None,
    intake_attempt: Mapping[str, Any] | None = None,
    parent_revision: Mapping[str, Any] | None = None,
    analyzer_available: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    trusted = _require_trusted_source_policy(policy)
    if type(analyzer_available) is not bool:
        raise EcosystemError("POLICY_SCHEMA_INVALID", "Analyzer availability must be boolean")
    checked_subject, entries, _source_id = _subject_scope(
        subject_id=subject_id,
        subject_record=subject_record,
        tree=tree,
        store=store,
        policy=trusted,
        parent_revision=parent_revision,
    )
    subject_sha256 = canonical_sha256(checked_subject)

    def insufficient(reason: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return [], _build_static_report(
            subject_id=subject_id,
            subject_sha256=subject_sha256,
            findings=[],
            status="INSUFFICIENT_EVIDENCE",
            result="INSUFFICIENT_EVIDENCE",
            reasons=[reason],
            policy=trusted,
        )

    if not analyzer_available:
        return insufficient("ANALYZER_UNAVAILABLE")
    if provenance_evidence is None or license_evidence is None or intake_attempt is None:
        return insufficient("PROVENANCE_INSUFFICIENT")
    provenance_revision = checked_subject if subject_id.startswith("revision/") else parent_revision
    if provenance_revision is None:
        return insufficient("PROVENANCE_INSUFFICIENT")
    try:
        checked_provenance = validate_provenance_evidence(
            provenance_evidence,
            revision=provenance_revision,
            tree=tree,
            intake_attempt=intake_attempt,
            store=store,
            policy=trusted,
        )
        checked_license = validate_license_evidence(
            license_evidence,
            subject_record=checked_subject,
            tree=tree,
            store=store,
            policy=trusted,
            parent_revision=parent_revision,
        )
    except EcosystemError as exc:
        return insufficient(exc.reason_code)
    except Exception:
        # Evidence-validation internals are not an authority boundary.  An
        # unexpected implementation failure must never escape as a raw
        # interpreter error or be mistaken for a clean scan.
        return insufficient("ANALYZER_UNAVAILABLE")
    dependency_count = sum(
        PurePosixPath(entry["path"]).name in _DEPENDENCY_BASENAMES for entry in entries
    )
    if dependency_count > trusted.resource_limits["max_dependency_manifests"]:
        return insufficient("RESOURCE_LIMIT_EXCEEDED")
    findings: list[dict[str, Any]] = []
    try:
        for entry in entries:
            raw = _read_entry(
                store,
                entry,
                maximum_bytes=trusted.resource_limits["max_file_bytes"],
            )
            for rule_id in _matched_rules(entry["path"], entry, raw, trusted):
                findings.append(
                    _finding(
                        subject_id=subject_id,
                        subject_sha256=subject_sha256,
                        rule_id=rule_id,
                        path=entry["path"],
                        evidence_sha256=entry["sha256"],
                        policy=trusted,
                    )
                )
                if len(findings) > trusted.resource_limits["max_findings_per_subject"]:
                    raise EcosystemError(
                        "RESOURCE_LIMIT_EXCEEDED", "Static finding set exceeds policy"
                    )
    except EcosystemError as exc:
        return insufficient(exc.reason_code)
    except Exception:
        # Analyzer internals must fail closed without inventing a finding or
        # exposing the implementation exception through the public result.
        return insufficient("ANALYZER_UNAVAILABLE")
    if checked_provenance["result"] != "EXACT_SUBJECT_BOUND":
        findings.append(
            _finding(
                subject_id=subject_id,
                subject_sha256=subject_sha256,
                rule_id="evidence.provenance-inexact",
                path=None,
                evidence_sha256=canonical_sha256(checked_provenance),
                policy=trusted,
            )
        )
    if checked_license["license_result"] != "MATCHES_POLICY_DECLARATION":
        findings.append(
            _finding(
                subject_id=subject_id,
                subject_sha256=subject_sha256,
                rule_id="evidence.license-incomplete",
                path=None,
                evidence_sha256=canonical_sha256(checked_license),
                policy=trusted,
            )
        )
    findings.sort(key=lambda item: item["finding_id"])
    if len(findings) > trusted.resource_limits["max_findings_per_subject"]:
        return insufficient("RESOURCE_LIMIT_EXCEEDED")
    dispositions = {item["disposition"] for item in findings}
    if "REJECTS_CANDIDATE" in dispositions:
        result = "REJECTED"
    elif "BLOCKS_REVIEW_COMPLETION" in dispositions:
        result = "BLOCKED"
    else:
        result = "DECLARED_STATIC_RULES_PASSED"
    reasons = sorted({item["reason_code"] for item in findings})
    return findings, _build_static_report(
        subject_id=subject_id,
        subject_sha256=subject_sha256,
        findings=findings,
        status="COMPLETE",
        result=result,
        reasons=reasons,
        policy=trusted,
    )


def validate_static_evidence(
    findings: Any,
    report: Any,
    **analysis_inputs: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if type(findings) is not list or type(report) is not dict:
        raise EcosystemError("POLICY_SCHEMA_INVALID", "Static evidence containers are invalid")
    expected_findings, expected_report = analyze_static_evidence(**analysis_inputs)
    if findings != expected_findings or report != expected_report:
        raise EcosystemError("SUBJECT_MISMATCH", "Static evidence is stale, forged, or incomplete")
    return [dict(item) for item in expected_findings], dict(expected_report)


_SOURCE_TO_COMPONENT = {
    "GRANULAR_SKILL_SOURCE": "GRANULAR_SKILL",
    "ADVISORY_AGENT_SOURCE": "ADVISORY_AGENT",
    "REFERENCE_ARCHITECTURE": "REFERENCE_ARCHITECTURE",
    "MEMORY_PATTERN_SOURCE": "MEMORY_PATTERN",
    "WORKFLOW_PATTERN_SOURCE": "WORKFLOW_PATTERN",
    "LIBRARY_DEPENDENCY_REFERENCE": "LIBRARY_DEPENDENCY_REFERENCE",
}


def _candidate_kinds(path: str) -> set[str]:
    pure = PurePosixPath(path)
    basename = pure.name
    suffix = pure.suffix.casefold()
    segments = [item.casefold() for item in pure.parts]
    matches: set[str] = set()
    if any(segment in {"memory", "memories", "wiki", "codegraph", "code-graph"} for segment in segments) and suffix in {".json", ".md", ".py", ".txt", ".yaml", ".yml"}:
        matches.add("MEMORY_PATTERN")
    if (
        any(segment in {"example", "examples", "pattern", "patterns", "workflow", "workflows"} for segment in segments)
        and suffix in {".json", ".md", ".py", ".rst", ".ts", ".tsx", ".txt", ".yaml", ".yml"}
        and not path.casefold().startswith(".github/workflows/")
    ):
        matches.add("WORKFLOW_PATTERN")
    if basename in _DEPENDENCY_BASENAMES:
        matches.add("LIBRARY_DEPENDENCY_REFERENCE")
    if basename == "README.md" or (pure.parts and pure.parts[0] == "docs" and suffix in {".md", ".rst", ".txt"}):
        matches.add("REFERENCE_ARCHITECTURE")
    return matches


def _classification_report(
    *,
    revision: Mapping[str, Any],
    classifications: list[dict[str, Any]],
    unresolved_paths: list[str],
    status: str,
    reasons: list[str],
    policy: TrustedEcosystemSourcePolicy,
) -> dict[str, Any]:
    classifications.sort(key=lambda item: item["classification_id"])
    unresolved_paths = sorted(set(unresolved_paths))
    if len(unresolved_paths) > 128:
        raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", "Unresolved classification set exceeds policy")
    validate_reason_codes(reasons, required=status != "COMPLETE")
    body = {
        "subject_id": revision["revision_id"],
        "subject_sha256": canonical_sha256(dict(revision)),
        "classifier_id": "nexus.ecosystem-component-classifier",
        "classifier_version": "1",
        "classifier_config_sha256": policy.component_classifier_config_sha256,
        "classification_ids": [item["classification_id"] for item in classifications],
        "unresolved_path_sha256s": unresolved_paths,
        "report_status": status,
        "reason_codes": reasons,
        "authority": zero_authority(),
    }
    return {
        "schema_version": "nexus.ecosystem-classification-report.v1",
        "report_id": typed_id("classification-report", body),
        **body,
    }


def classify_components(
    *,
    revision: Mapping[str, Any],
    tree: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    classifier_available: bool = True,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    trusted = _require_trusted_source_policy(policy)
    if type(classifier_available) is not bool:
        raise EcosystemError("POLICY_SCHEMA_INVALID", "Classifier availability must be boolean")
    checked_revision, checked_tree, _attempt = _validate_authoritative_revision_snapshot(
        revision=revision,
        tree=tree,
        store=store,
        policy=trusted,
    )
    if not classifier_available:
        return [], [], _classification_report(
            revision=checked_revision,
            classifications=[],
            unresolved_paths=[],
            status="INSUFFICIENT_EVIDENCE",
            reasons=["ANALYZER_UNAVAILABLE"],
            policy=trusted,
        )
    source = trusted.source(checked_revision["source_key"])
    allowed = {_SOURCE_TO_COMPONENT[item] for item in source["source_classifications"]}
    entries = checked_tree["entries"]
    regular_entries = [entry for entry in entries if entry["kind"] == "regular"]
    entry_by_path = {entry["path"]: entry for entry in regular_entries}
    skill_roots = sorted(
        {
            str(PurePosixPath(path).parent)
            for path in entry_by_path
            if PurePosixPath(path).name == "SKILL.md" and str(PurePosixPath(path).parent) != "."
        }
    )
    root_skill = "SKILL.md" in entry_by_path
    if len(skill_roots) > trusted.resource_limits["max_components"]:
        return [], [], _classification_report(
            revision=checked_revision,
            classifications=[],
            unresolved_paths=[],
            status="INSUFFICIENT_EVIDENCE",
            reasons=["RESOURCE_LIMIT_EXCEEDED"],
            policy=trusted,
        )
    assigned: set[str] = set()
    candidates: list[tuple[str, set[str], list[dict[str, Any]]]] = []
    for root in skill_roots:
        nested = [other for other in skill_roots if other != root and other.startswith(root + "/")]
        closure = [
            entry
            for entry in regular_entries
            if entry["path"].startswith(root + "/")
            and not any(entry["path"] == child or entry["path"].startswith(child + "/") for child in nested)
        ]
        candidates.append((root, {"GRANULAR_SKILL"}, closure))
        assigned.update(entry["path"] for entry in closure)
    for entry in regular_entries:
        path = entry["path"]
        if path in assigned:
            continue
        pure = PurePosixPath(path)
        if pure.parts and pure.parts[0] in {"agents", ".agents"} and pure.suffix.casefold() == ".md":
            candidates.append((path, {"ADVISORY_AGENT"}, [entry]))
            assigned.add(path)
    for entry in regular_entries:
        if entry["path"] in assigned:
            continue
        kinds = _candidate_kinds(entry["path"])
        if kinds:
            candidates.append((entry["path"], kinds, [entry]))

    dependency_count = sum(
        PurePosixPath(entry["path"]).name in _DEPENDENCY_BASENAMES for entry in entries
    )
    if (
        len(candidates) > trusted.resource_limits["max_components"]
        or dependency_count > trusted.resource_limits["max_dependency_manifests"]
    ):
        return [], [], _classification_report(
            revision=checked_revision,
            classifications=[],
            unresolved_paths=[],
            status="INSUFFICIENT_EVIDENCE",
            reasons=["RESOURCE_LIMIT_EXCEEDED"],
            policy=trusted,
        )

    try:
        for _root, _kinds, closure in candidates:
            if (
                len(closure) > trusted.resource_limits["max_component_entries"]
                or sum(item["size"] for item in closure)
                > trusted.resource_limits["max_component_bytes"]
            ):
                raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", "Component closure exceeds policy")
            for entry in closure:
                raw = _read_entry(
                    store,
                    entry,
                    maximum_bytes=trusted.resource_limits["max_file_bytes"],
                )
                if _role_text(entry["path"]):
                    limit = _role_text_limit(entry["path"], trusted)
                    if limit is not None and len(raw) > limit:
                        raise EcosystemError(
                            "RESOURCE_LIMIT_EXCEEDED", "Component instruction exceeds its role limit"
                        )
                    try:
                        text = raw.decode("utf-8", errors="strict")
                    except UnicodeDecodeError:
                        raise EcosystemError(
                            "CLASSIFICATION_UNRESOLVED", "Component instruction is not strict UTF-8"
                        ) from None
                    if "\x00" in text:
                        raise EcosystemError(
                            "CLASSIFICATION_UNRESOLVED", "Component instruction contains NUL"
                        )
    except EcosystemError as exc:
        return [], [], _classification_report(
            revision=checked_revision,
            classifications=[],
            unresolved_paths=[],
            status="INSUFFICIENT_EVIDENCE",
            reasons=[exc.reason_code],
            policy=trusted,
        )

    unresolved_paths = [hashlib.sha256(b"SKILL.md").hexdigest()] if root_skill else []
    components: list[dict[str, Any]] = []
    classifications: list[dict[str, Any]] = []
    for root, kinds, closure in sorted(candidates, key=lambda item: item[0].encode("utf-8")):
        manifest_entries = [
            {key: entry[key] for key in ("path", "mode", "size", "sha256")} for entry in closure
        ]
        manifest_entries.sort(key=lambda item: item["path"].encode("utf-8"))
        manifest_sha256 = canonical_sha256({"entries": manifest_entries})
        component_id = build_component_identity(source_id=checked_revision["source_id"], component_root=root)
        component_revision_id = build_component_revision_identity(
            revision_id=checked_revision["revision_id"],
            component_id=component_id,
            component_manifest_sha256=manifest_sha256,
        )
        component_record = {
            "schema_version": "nexus.ecosystem-component-revision.v1",
            "component_revision_id": component_revision_id,
            "component_id": component_id,
            "source_id": checked_revision["source_id"],
            "revision_id": checked_revision["revision_id"],
            "component_root": root,
            "component_manifest_sha256": manifest_sha256,
            "entries": manifest_entries,
            "authority": zero_authority(),
        }
        status: str
        kind: str | None
        reasons: list[str]
        if len(kinds) > 1:
            status, kind, reasons = "CONFLICTING", None, ["CLASSIFICATION_CONFLICT"]
            unresolved_paths.append(hashlib.sha256(root.encode("utf-8")).hexdigest())
        else:
            proposed = next(iter(kinds))
            if proposed not in allowed:
                status, kind, reasons = "UNRESOLVED", None, ["CLASSIFICATION_UNRESOLVED"]
                unresolved_paths.append(hashlib.sha256(root.encode("utf-8")).hexdigest())
            else:
                status, kind, reasons = "OBSERVED", proposed, []
        body: dict[str, Any] = {
            "source_id": checked_revision["source_id"],
            "revision_id": checked_revision["revision_id"],
            "component_id": component_id,
            "component_revision_id": component_revision_id,
            "component_manifest_sha256": manifest_sha256,
            "component_kind": kind,
            "classification_status": status,
            "evidence_ids": [],
            "reason_codes": reasons,
            "disposition": "QUARANTINED",
            "authority": zero_authority(),
        }
        classification = {
            "schema_version": "nexus.ecosystem-component-classification.v1",
            "classification_id": typed_id("classification", body),
            **body,
        }
        components.append(component_record)
        classifications.append(classification)
    unresolved_paths = sorted(set(unresolved_paths))
    statuses = {item["classification_status"] for item in classifications}
    if "CONFLICTING" in statuses:
        report_status, reasons = "CONFLICTING", ["CLASSIFICATION_CONFLICT"]
    elif "UNRESOLVED" in statuses or unresolved_paths:
        report_status, reasons = "UNRESOLVED", ["CLASSIFICATION_UNRESOLVED"]
    else:
        report_status, reasons = "COMPLETE", []
    report = _classification_report(
        revision=checked_revision,
        classifications=classifications,
        unresolved_paths=unresolved_paths,
        status=report_status,
        reasons=reasons,
        policy=trusted,
    )
    return components, classifications, report


def validate_component_classification(
    components: Any,
    classifications: Any,
    report: Any,
    **classifier_inputs: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if type(components) is not list or type(classifications) is not list or type(report) is not dict:
        raise EcosystemError("POLICY_SCHEMA_INVALID", "Classification evidence containers are invalid")
    expected_components, expected_classifications, expected_report = classify_components(
        **classifier_inputs
    )
    if (
        components != expected_components
        or classifications != expected_classifications
        or report != expected_report
    ):
        raise EcosystemError("SUBJECT_MISMATCH", "Classification evidence is stale, forged, or incomplete")
    return (
        [dict(item) for item in expected_components],
        [dict(item) for item in expected_classifications],
        dict(expected_report),
    )
