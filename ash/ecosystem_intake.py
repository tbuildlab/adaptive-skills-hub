"""Bounded ZIP-only intake into the inert Slice 3C quarantine CAS."""
from __future__ import annotations

import binascii
from dataclasses import dataclass
import hashlib
import io
from pathlib import PurePosixPath
import stat
import struct
import time
from typing import Any, BinaryIO, Mapping
import zipfile
import zlib

from .ecosystem_bridge import ValidatedIntakeBridge, _require_validated_bridge
from .ecosystem_models import (
    EcosystemError,
    GENESIS_STATE,
    IMPLICIT_STATE,
    build_revision_identity,
    build_state_record,
    build_transition_receipt,
    build_tree,
    canonical_json_bytes,
    typed_id,
    validate_sha256,
    zero_authority,
)
from .ecosystem_policy import TrustedEcosystemSourcePolicy, _require_trusted_source_policy
from .ecosystem_storage import (
    QuarantineStore,
    StableInput,
    _INTAKE_RECORD_WRITER,
    _require_stable_input,
)


INTAKE_ALGORITHM_ID = "nexus.ecosystem-zip-intake"
INTAKE_ALGORITHM_VERSION = "1"
_EOCD = struct.Struct("<IHHHHIIH")
_CENTRAL = struct.Struct("<IHHHHHHIIIHHHHHII")
_LOCAL = struct.Struct("<IHHHHHIIIHH")
_EOCD_SIGNATURE = 0x06054B50
_CENTRAL_SIGNATURE = 0x02014B50
_LOCAL_SIGNATURE = 0x04034B50
_ALLOWED_FLAGS = 0x0800
_ALLOWED_METHODS = {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}
_WINDOWS_UNSAFE_FILE_ATTRIBUTES = 0x0200 | 0x0400  # sparse file | reparse point


@dataclass(frozen=True, slots=True)
class _InventoryEntry:
    original_name: str
    path: str
    is_directory: bool
    executable: bool
    compression_method: int
    crc32: int
    compressed_size: int
    expanded_size: int
    local_offset: int
    data_offset: int
    data_end: int


def _archive_error(code: str, message: str) -> EcosystemError:
    return EcosystemError(code, message)


def _decode_name(raw: bytes, flags: int) -> str:
    try:
        name = raw.decode("utf-8" if flags & 0x0800 else "cp437", errors="strict")
    except UnicodeDecodeError:
        raise _archive_error("ARCHIVE_INVALID", "ZIP member name encoding is invalid") from None
    if "\x00" in name or not name:
        raise _archive_error("ARCHIVE_INVALID", "ZIP member name is invalid")
    return name


def _extra_fields(raw: bytes) -> list[tuple[int, bytes]]:
    fields: list[tuple[int, bytes]] = []
    cursor = 0
    while cursor < len(raw):
        if cursor + 4 > len(raw):
            raise _archive_error("ARCHIVE_INVALID", "ZIP extra field is malformed")
        identifier, length = struct.unpack_from("<HH", raw, cursor)
        cursor += 4
        if cursor + length > len(raw):
            raise _archive_error("ARCHIVE_INVALID", "ZIP extra field is truncated")
        value = raw[cursor : cursor + length]
        cursor += length
        fields.append((identifier, value))
    return fields


def _raw_path_guard(name: str) -> list[str]:
    if name.startswith(("/", "\\")) or "\\" in name or ":" in name:
        raise _archive_error("PATH_INVALID", "ZIP member path is absolute or non-POSIX")
    stripped = name[:-1] if name.endswith("/") else name
    parts = stripped.split("/")
    if not stripped or any(part in {"", ".", ".."} for part in parts):
        raise _archive_error("PATH_INVALID", "ZIP member path traverses or is empty")
    return parts


def _validate_unix_kind(version_made: int, external_attributes: int, is_directory: bool) -> bool:
    creator = version_made >> 8
    mode = (external_attributes >> 16) & 0xFFFF
    if creator != 3 or mode == 0:
        return False
    kind = stat.S_IFMT(mode)
    if is_directory:
        if kind not in {0, stat.S_IFDIR}:
            raise _archive_error("ARCHIVE_UNSAFE_ENTRY", "ZIP directory has a special file mode")
    elif kind not in {0, stat.S_IFREG}:
        raise _archive_error("ARCHIVE_UNSAFE_ENTRY", "ZIP links and special files are forbidden")
    return bool(mode & 0o111)


def _inventory_zip(
    raw: bytes,
    limits: Mapping[str, int],
    *,
    deadline: float | None = None,
    _clock: Any | None = None,
) -> tuple[str, list[_InventoryEntry]]:
    clock = time.monotonic if _clock is None else _clock
    if deadline is not None and clock() > deadline:
        raise _archive_error("TIME_LIMIT_EXCEEDED", "ZIP intake exceeded its deadline")
    # ZIP64 is rejected from the outer archive's structural fields below
    # (EOCD sentinels, required version, and ZIP64 extra records).  Do not scan
    # arbitrary member bytes for ZIP64 signatures: nested archives are inert
    # candidate content and must never be parsed as outer-container metadata.
    if not raw.startswith(b"PK\x03\x04"):
        raise _archive_error("ARCHIVE_INVALID", "Input is not a supported non-ZIP64 ZIP")
    search_start = max(0, len(raw) - (65_535 + _EOCD.size))
    eocd_offset = raw.rfind(b"PK\x05\x06", search_start)
    if eocd_offset < 0 or eocd_offset + _EOCD.size > len(raw):
        raise _archive_error("ARCHIVE_INVALID", "ZIP end record is absent")
    fields = _EOCD.unpack_from(raw, eocd_offset)
    (
        signature,
        disk_number,
        central_disk,
        disk_entries,
        total_entries,
        central_size,
        central_offset,
        comment_length,
    ) = fields
    if signature != _EOCD_SIGNATURE or eocd_offset + _EOCD.size + comment_length != len(raw):
        raise _archive_error("ARCHIVE_INVALID", "ZIP has a trailer or malformed end record")
    if (
        disk_number != 0
        or central_disk != 0
        or disk_entries != total_entries
        or total_entries in {0, 0xFFFF}
        or central_size == 0xFFFFFFFF
        or central_offset == 0xFFFFFFFF
        or total_entries > limits["max_entries"]
    ):
        raise _archive_error("ARCHIVE_INVALID", "ZIP is empty, split, ZIP64, or over the entry limit")
    if central_offset + central_size != eocd_offset:
        raise _archive_error("ARCHIVE_INVALID", "ZIP central directory bounds are inconsistent")

    cursor = central_offset
    parsed: list[tuple[str, bool, bool, int, int, int, int, int, int, int]] = []
    spans: list[tuple[int, int]] = []
    top_levels: list[str] = []
    directories = 0
    declared_expanded = 0
    declared_compressed = 0
    for _index in range(total_entries):
        if deadline is not None and clock() > deadline:
            raise _archive_error("TIME_LIMIT_EXCEEDED", "ZIP intake exceeded its deadline")
        if cursor + _CENTRAL.size > eocd_offset:
            raise _archive_error("ARCHIVE_INVALID", "ZIP central directory is truncated")
        central = _CENTRAL.unpack_from(raw, cursor)
        (
            signature,
            version_made,
            version_needed,
            flags,
            method,
            _mtime,
            _mdate,
            crc32,
            compressed_size,
            expanded_size,
            name_length,
            extra_length,
            member_comment_length,
            disk_start,
            _internal_attributes,
            external_attributes,
            local_offset,
        ) = central
        if signature != _CENTRAL_SIGNATURE:
            raise _archive_error("ARCHIVE_INVALID", "ZIP central header is malformed")
        end = cursor + _CENTRAL.size + name_length + extra_length + member_comment_length
        if end > eocd_offset or name_length == 0:
            raise _archive_error("ARCHIVE_INVALID", "ZIP central member metadata is truncated")
        name_raw = raw[cursor + _CENTRAL.size : cursor + _CENTRAL.size + name_length]
        extra = raw[
            cursor + _CENTRAL.size + name_length : cursor + _CENTRAL.size + name_length + extra_length
        ]
        if (
            version_needed > 20
            or flags & ~_ALLOWED_FLAGS
            or flags & 0x0001
            or method not in _ALLOWED_METHODS
            or disk_start != 0
            or member_comment_length != 0
            or any(identifier not in {0x5455} for identifier, _value in _extra_fields(extra))
        ):
            raise _archive_error("UNSUPPORTED_INPUT", "ZIP uses an unsupported safe feature")
        name = _decode_name(name_raw, flags)
        parts = _raw_path_guard(name)
        top_levels.append(parts[0])
        is_directory = name.endswith("/")
        if external_attributes & _WINDOWS_UNSAFE_FILE_ATTRIBUTES:
            raise _archive_error(
                "ARCHIVE_UNSAFE_ENTRY",
                "ZIP sparse files and reparse points are forbidden",
            )
        dos_directory = bool(external_attributes & 0x10)
        if dos_directory != is_directory:
            raise _archive_error(
                "ARCHIVE_UNSAFE_ENTRY",
                "ZIP directory name and external attributes disagree",
            )
        if is_directory:
            directories += 1
            if compressed_size or expanded_size:
                raise _archive_error("ARCHIVE_INVALID", "ZIP directory carries data")
        executable = _validate_unix_kind(version_made, external_attributes, is_directory)
        if local_offset + _LOCAL.size > central_offset:
            raise _archive_error("ARCHIVE_INVALID", "ZIP local header is outside the data region")
        local = _LOCAL.unpack_from(raw, local_offset)
        (
            local_signature,
            local_version,
            local_flags,
            local_method,
            _local_time,
            _local_date,
            local_crc,
            local_compressed,
            local_expanded,
            local_name_length,
            local_extra_length,
        ) = local
        local_name_start = local_offset + _LOCAL.size
        data_offset = local_name_start + local_name_length + local_extra_length
        data_end = data_offset + compressed_size
        if (
            local_signature != _LOCAL_SIGNATURE
            or local_version != version_needed
            or local_flags != flags
            or local_method != method
            or local_crc != crc32
            or local_compressed != compressed_size
            or local_expanded != expanded_size
            or local_name_length != name_length
            or raw[local_name_start : local_name_start + local_name_length] != name_raw
            or data_end > central_offset
        ):
            raise _archive_error("ARCHIVE_INTEGRITY_INVALID", "ZIP local and central headers disagree")
        local_extra = raw[local_name_start + local_name_length : data_offset]
        if local_extra != extra:
            raise _archive_error("ARCHIVE_INTEGRITY_INVALID", "ZIP local and central extras disagree")
        spans.append((local_offset, data_end))
        declared_expanded += expanded_size
        declared_compressed += compressed_size
        if expanded_size > limits["max_file_bytes"] or declared_expanded > limits["max_expanded_bytes"]:
            raise _archive_error("RESOURCE_LIMIT_EXCEEDED", "ZIP declared expansion exceeds a limit")
        if expanded_size and expanded_size / max(1, compressed_size) > limits["max_entry_compression_ratio"]:
            raise _archive_error("RESOURCE_LIMIT_EXCEEDED", "ZIP member compression ratio exceeds a limit")
        parsed.append(
            (
                name,
                is_directory,
                executable,
                method,
                crc32,
                compressed_size,
                expanded_size,
                local_offset,
                data_offset,
                data_end,
            )
        )
        cursor = end
    if cursor != eocd_offset:
        raise _archive_error("ARCHIVE_INVALID", "ZIP central directory has unindexed bytes")
    if declared_expanded and declared_expanded / max(1, declared_compressed) > limits["max_aggregate_compression_ratio"]:
        raise _archive_error("RESOURCE_LIMIT_EXCEEDED", "ZIP aggregate compression ratio exceeds a limit")
    ordered_spans = sorted(spans)
    if (
        not ordered_spans
        or ordered_spans[0][0] != 0
        or ordered_spans[-1][1] != central_offset
        or any(right[0] != left[1] for left, right in zip(ordered_spans, ordered_spans[1:]))
    ):
        raise _archive_error(
            "ARCHIVE_INTEGRITY_INVALID",
            "ZIP local records overlap or contain unindexed bytes",
        )
    if len({name.casefold() for name in top_levels}) != 1 or len(set(top_levels)) != 1:
        raise _archive_error("ARCHIVE_INVALID", "ZIP must have exactly one unambiguous top-level directory")
    prefix = top_levels[0]
    # Reuse the full cross-platform segment validator for the stripped prefix.
    from .ecosystem_models import normalize_candidate_path

    normalize_candidate_path(prefix)
    inventory: list[_InventoryEntry] = []
    collisions: set[str] = set()
    file_keys: set[str] = set()
    effective_directories: set[str] = set()
    files = 0
    for item in parsed:
        name, is_directory, executable, method, crc32, compressed_size, expanded_size, local_offset, data_offset, data_end = item
        parts = _raw_path_guard(name)
        if parts[0] != prefix:
            raise _archive_error("ARCHIVE_INVALID", "ZIP top-level directory is inconsistent")
        if len(parts) == 1:
            if not is_directory:
                raise _archive_error("ARCHIVE_INVALID", "ZIP top-level entry must be a directory")
            continue
        normalized = normalize_candidate_path("/".join(parts[1:]))
        key = normalized.casefold()
        if key in collisions:
            raise _archive_error("PATH_COLLISION", "ZIP member paths collide")
        collisions.add(key)
        segments = normalized.split("/")
        directory_depth = len(segments) if is_directory else len(segments) - 1
        for depth in range(1, directory_depth + 1):
            effective_directories.add("/".join(segments[:depth]).casefold())
        if not is_directory:
            files += 1
            file_keys.add(key)
        inventory.append(
            _InventoryEntry(
                name,
                normalized,
                is_directory,
                executable,
                method,
                crc32,
                compressed_size,
                expanded_size,
                local_offset,
                data_offset,
                data_end,
            )
        )
    if len(effective_directories) > limits["max_directories"]:
        raise _archive_error("RESOURCE_LIMIT_EXCEEDED", "ZIP directory inventory exceeds a bound")
    if any(
        candidate != file_key and candidate.startswith(file_key + "/")
        for file_key in file_keys
        for candidate in collisions
    ):
        raise _archive_error("PATH_COLLISION", "ZIP file path is an ancestor of another member")
    if files == 0:
        raise _archive_error("ARCHIVE_INVALID", "ZIP contains no regular files")
    if deadline is not None and clock() > deadline:
        raise _archive_error("TIME_LIMIT_EXCEEDED", "ZIP intake exceeded its deadline")
    inventory.sort(key=lambda item: item.path.encode("utf-8"))
    return prefix, inventory


class _MemberStream:
    __slots__ = ("_source", "_maximum", "_deadline", "count", "crc32")

    def __init__(self, source: BinaryIO, *, maximum: int, deadline: float) -> None:
        self._source = source
        self._maximum = maximum
        self._deadline = deadline
        self.count = 0
        self.crc32 = 0

    def read(self, size: int = -1) -> bytes:
        if time.monotonic() > self._deadline:
            raise _archive_error("TIME_LIMIT_EXCEEDED", "ZIP intake exceeded its deadline")
        remaining = self._maximum - self.count
        if remaining < 0:
            raise _archive_error("RESOURCE_LIMIT_EXCEEDED", "ZIP member exceeds its expansion bound")
        amount = min(65_536 if size < 0 else size, remaining + 1)
        chunk = self._source.read(amount)
        if type(chunk) is not bytes:
            raise _archive_error("ARCHIVE_INTEGRITY_INVALID", "ZIP reader returned non-byte content")
        self.count += len(chunk)
        if self.count > self._maximum:
            raise _archive_error("RESOURCE_LIMIT_EXCEEDED", "ZIP member exceeds its expansion bound")
        self.crc32 = binascii.crc32(chunk, self.crc32) & 0xFFFFFFFF
        return chunk


def _attempt_base(bridge: Mapping[str, Any], policy: TrustedEcosystemSourcePolicy) -> dict[str, Any]:
    return {
        "bridge_id": bridge["bridge_id"],
        "source_key": bridge["source_key"],
        "source_id": bridge["source_id"],
        "commit_object_format": bridge["commit_object_format"],
        "commit_oid": bridge["commit_oid"],
        "input_sha256": bridge["requested_input_sha256"],
        "input_size": bridge["requested_input_size"],
        "policy_semantic_sha256": policy.policy_semantic_sha256,
        "intake_algorithm_id": INTAKE_ALGORITHM_ID,
        "intake_algorithm_version": INTAKE_ALGORITHM_VERSION,
    }


def _attempt_record(
    base: Mapping[str, Any], *, result: str, tree_id: str | None, revision_id: str | None, reason_codes: list[str]
) -> dict[str, Any]:
    attempt_id = typed_id("intake-attempt", dict(base))
    result_body: dict[str, Any] = {
        "attempt_id": attempt_id,
        **dict(base),
        "result": result,
        "tree_id": tree_id,
        "revision_id": revision_id,
        "reason_codes": sorted(set(reason_codes)),
        "authority": zero_authority(),
    }
    return {
        "schema_version": "nexus.ecosystem-intake-attempt.v1",
        "attempt_id": attempt_id,
        "attempt_result_id": typed_id("intake-attempt-result", result_body),
        **dict(base),
        "result": result,
        "tree_id": tree_id,
        "revision_id": revision_id,
        "reason_codes": sorted(set(reason_codes)),
        "authority": zero_authority(),
    }


def _write_attempt(store: QuarantineStore, record: dict[str, Any], maximum: int) -> None:
    attempt_digest = record["attempt_id"].split("/", 1)[1]
    result_digest = record["attempt_result_id"].split("/", 1)[1]
    existing = store.list_record_names(
        f"intake-attempts/sha256/{attempt_digest}",
        maximum_count=2,
        create=True,
        writer_token=_INTAKE_RECORD_WRITER,
    )
    if existing and existing != (f"{result_digest}.json",):
        raise _archive_error("CAS_OBJECT_CONFLICT", "Intake attempt already has a different terminal result")
    store._publish_record(
        f"intake-attempts/sha256/{attempt_digest}/{result_digest}.json",
        record,
        maximum_bytes=maximum,
        writer_token=_INTAKE_RECORD_WRITER,
    )


def _verify_revision_identity_set(
    *,
    store: QuarantineStore,
    revision_record: dict[str, Any],
    policy: TrustedEcosystemSourcePolicy,
) -> None:
    """Bind one source/commit to exactly one immutable ZIP and tree."""
    from .ecosystem_evidence import _validate_revision

    maximum = policy.resource_limits["max_record_bytes"]
    total_bound = (
        policy.resource_limits["max_sources"]
        * policy.resource_limits["max_quarantined_revisions_per_source"]
    )
    names = store.list_record_names(
        "revisions/sha256", maximum_count=total_bound
    )
    source_revisions: set[str] = set()
    for name in names:
        try:
            existing = _validate_revision(
                store.read_record(
                    f"revisions/sha256/{name}", maximum_bytes=maximum
                ),
                policy,
            )
        except EcosystemError:
            raise _archive_error(
                "CAS_OBJECT_CONFLICT", "Stored revision record is not current and valid"
            ) from None
        if name[:-5] != existing["revision_id"].split("/", 1)[1]:
            raise _archive_error(
                "CAS_OBJECT_CONFLICT", "Stored revision locator is inconsistent"
            )
        if existing["source_id"] != revision_record["source_id"]:
            continue
        source_revisions.add(existing["revision_id"])
        same_commit = (
            existing["commit_object_format"]
            == revision_record["commit_object_format"]
            and existing["commit_oid"] == revision_record["commit_oid"]
        )
        if same_commit and any(
            existing[field] != revision_record[field]
            for field in ("input_sha256", "tree_id", "revision_id")
        ):
            raise _archive_error(
                "PROVENANCE_CONFLICT",
                "One immutable commit cannot identify different ZIP or tree bytes",
            )
    if (
        revision_record["revision_id"] not in source_revisions
        and len(source_revisions)
        >= policy.resource_limits["max_quarantined_revisions_per_source"]
    ):
        raise _archive_error(
            "RESOURCE_LIMIT_EXCEEDED", "Source revision quarantine limit is reached"
        )


def _write_success_records(
    *,
    store: QuarantineStore,
    attempt: dict[str, Any],
    tree_record: dict[str, Any],
    revision_record: dict[str, Any],
    policy: TrustedEcosystemSourcePolicy,
) -> dict[str, Any]:
    maximum = policy.resource_limits["max_record_bytes"]
    tree_digest = attempt["tree_id"].split("/", 1)[1]
    revision_digest = attempt["revision_id"].split("/", 1)[1]
    with store._exclusive("intake.lock"):
        _verify_revision_identity_set(
            store=store,
            revision_record=revision_record,
            policy=policy,
        )
        store._ensure_revision_capacity(
            source_id=attempt["source_id"],
            revision_id=attempt["revision_id"],
            policy=policy,
            writer_token=_INTAKE_RECORD_WRITER,
        )
        store._publish_record(
            f"trees/sha256/{tree_digest}.json",
            tree_record,
            maximum_bytes=maximum,
            writer_token=_INTAKE_RECORD_WRITER,
        )
        store._publish_record(
            f"revisions/sha256/{revision_digest}.json",
            revision_record,
            maximum_bytes=maximum,
            writer_token=_INTAKE_RECORD_WRITER,
        )
        # Capacity is checked before the terminal attempt is published.  Once
        # it exists, every referenced identity record already exists; the
        # transition is persisted before the state record that cites it.
        _write_attempt(store, attempt, maximum)
        # State/evidence consumers have one immutable digest-addressed lookup
        # for every cited evidence ID.  The canonical attempt remains in its
        # attempt/result namespace as well; this mirror cannot overwrite or
        # diverge because both stores are immutable and byte-compared.
        store._publish_record(
            f"evidence/sha256/{attempt['attempt_result_id'].split('/', 1)[1]}.json",
            attempt,
            maximum_bytes=maximum,
            writer_token=_INTAKE_RECORD_WRITER,
        )
        transition = build_transition_receipt(
            subject_id=attempt["revision_id"],
            subject_sha256=hashlib.sha256(canonical_json_bytes(revision_record)).hexdigest(),
            from_state=IMPLICIT_STATE,
            to_state=GENESIS_STATE,
            transition_axis="possession",
            evidence_ids=[attempt["attempt_result_id"]],
            evaluation_receipt_sha256s=[],
            evaluation_profile_id=None,
            evaluation_profile_sha256=None,
            policy_semantic_sha256=policy.policy_semantic_sha256,
            reason_codes=[],
        )
        state_record = build_state_record(
            subject_id=attempt["revision_id"],
            subject_sha256=transition["subject_sha256"],
            previous_state_record_id=None,
            transition=transition,
        )
        transition_digest = transition["transition_id"].split("/", 1)[1]
        state_digest = state_record["state_record_id"].split("/", 1)[1]
        store._publish_record(
            f"evidence/sha256/{transition_digest}.json",
            transition,
            maximum_bytes=maximum,
            writer_token=_INTAKE_RECORD_WRITER,
        )
        store._publish_record(
            f"state/sha256/{state_digest}.json",
            state_record,
            maximum_bytes=maximum,
            writer_token=_INTAKE_RECORD_WRITER,
        )
        quarantine_view = {
            "schema_version": "nexus.ecosystem-quarantine-view.v1",
            "revision_id": attempt["revision_id"],
            "source_id": attempt["source_id"],
            "genesis_state_record_id": state_record["state_record_id"],
            "initial_disposition": "QUARANTINED",
            "authority": zero_authority(),
        }
        store._publish_record(
            f"quarantine/{revision_digest}.json",
            quarantine_view,
            maximum_bytes=maximum,
            writer_token=_INTAKE_RECORD_WRITER,
        )
        return state_record


def intake_pre_supplied_zip(
    *,
    bridge: ValidatedIntakeBridge,
    zip_input: StableInput,
    policy: TrustedEcosystemSourcePolicy,
    store: QuarantineStore,
) -> dict[str, Any]:
    """The only production intake entry point: validated bridge + stable ZIP."""
    trusted_policy = _require_trusted_source_policy(policy)
    validated_bridge = _require_validated_bridge(bridge)
    stable = _require_stable_input(zip_input)
    if type(store) is not QuarantineStore:
        raise _archive_error("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    store._require_policy(trusted_policy)
    if not stable.name.casefold().endswith(".zip"):
        raise _archive_error("UNSUPPORTED_INPUT", "Production intake requires a .zip input")
    bridge_record = validated_bridge.record()
    if not validated_bridge.accepted:
        raise _archive_error("SCOUT_DISPOSITION_BLOCKED", "Blocked bridge cannot start intake")
    limits = trusted_policy.resource_limits
    if bridge_record["source_policy_semantic_sha256"] != trusted_policy.policy_semantic_sha256:
        raise _archive_error("POLICY_UNTRUSTED", "Bridge policy digest is stale")
    if stable.size != bridge_record["requested_input_size"]:
        raise _archive_error("INPUT_DIGEST_MISMATCH", "Stable ZIP size does not match bridge")
    deadline = time.monotonic() + limits["max_ingest_seconds"]
    stable.seek(0)
    raw_sha256, raw_size = store.put_blob(
        stable,
        maximum_bytes=limits["max_input_bytes"],
        expected_sha256=bridge_record["requested_input_sha256"],
        expected_size=bridge_record["requested_input_size"],
        deadline=deadline,
    )
    stable.verify_unchanged()
    if raw_size != bridge_record["requested_input_size"]:
        raise _archive_error("INPUT_DIGEST_MISMATCH", "Stable ZIP byte count does not match bridge")
    base = _attempt_base(bridge_record, trusted_policy)
    raw = store.read_blob(raw_sha256, maximum_bytes=limits["max_input_bytes"])
    try:
        prefix, inventory = _inventory_zip(raw, limits, deadline=deadline)
        entries: list[dict[str, Any]] = []
        expanded_total = 0
        with zipfile.ZipFile(io.BytesIO(raw), mode="r", allowZip64=False) as archive:
            by_offset = {item.header_offset: item for item in archive.infolist()}
            if len(by_offset) != len(archive.infolist()):
                raise _archive_error("ARCHIVE_INTEGRITY_INVALID", "ZIP repeats a local member header")
            for item in inventory:
                if time.monotonic() > deadline:
                    raise _archive_error(
                        "TIME_LIMIT_EXCEEDED", "ZIP intake exceeded its deadline"
                    )
                if item.is_directory:
                    continue
                info = by_offset.get(item.local_offset)
                if info is None or info.filename != item.original_name:
                    raise _archive_error("ARCHIVE_INTEGRITY_INVALID", "ZIP inventory changed during streaming")
                with archive.open(info, mode="r") as source:
                    bounded = _MemberStream(source, maximum=limits["max_file_bytes"], deadline=deadline)
                    digest, count = store.put_blob(
                        bounded,
                        maximum_bytes=limits["max_file_bytes"],
                        expected_size=item.expanded_size,
                        deadline=deadline,
                    )
                if count != item.expanded_size or bounded.crc32 != item.crc32:
                    raise _archive_error("ARCHIVE_INTEGRITY_INVALID", "ZIP member size or CRC is invalid")
                expanded_total += count
                if expanded_total > limits["max_expanded_bytes"]:
                    raise _archive_error("RESOURCE_LIMIT_EXCEEDED", "ZIP expansion exceeds its aggregate limit")
                prefix_bytes = store.read_blob(digest, maximum_bytes=min(count, 512) if count <= 512 else count)[:512]
                nested = prefix_bytes.startswith(
                    (b"PK\x03\x04", b"\x1f\x8b", b"7z\xbc\xaf'\x1c", b"Rar!\x1a\x07")
                ) or (len(prefix_bytes) >= 262 and prefix_bytes[257:262] == b"ustar")
                entries.append(
                    {
                        "path": item.path,
                        "kind": "archive" if nested else "regular",
                        "mode": "regular_executable" if item.executable else "regular_non_executable",
                        "size": count,
                        "sha256": digest,
                    }
                )
        if time.monotonic() > deadline:
            raise _archive_error("TIME_LIMIT_EXCEEDED", "ZIP intake exceeded its deadline")
        tree_id, tree_body = build_tree(entries)
        revision_id = build_revision_identity(
            source_id=bridge_record["source_id"],
            commit_object_format=bridge_record["commit_object_format"],
            commit_oid=bridge_record["commit_oid"],
            input_sha256=raw_sha256,
            tree_id=tree_id,
        )
        attempt = _attempt_record(
            base, result="REVISION_CREATED", tree_id=tree_id, revision_id=revision_id, reason_codes=[]
        )
        tree_record = {
            "schema_version": "nexus.ecosystem-tree.v1",
            "tree_id": tree_id,
            "entries": tree_body["entries"],
            "stripped_prefix_sha256": hashlib.sha256(prefix.encode("utf-8")).hexdigest(),
            "authority": zero_authority(),
        }
        revision_record = {
            "schema_version": "nexus.ecosystem-revision.v1",
            "revision_id": revision_id,
            "source_key": bridge_record["source_key"],
            "source_id": bridge_record["source_id"],
            "commit_object_format": bridge_record["commit_object_format"],
            "commit_oid": bridge_record["commit_oid"],
            "input_sha256": raw_sha256,
            "input_size": raw_size,
            "tree_id": tree_id,
            "policy_semantic_sha256": trusted_policy.policy_semantic_sha256,
            "intake_attempt_result_id": attempt["attempt_result_id"],
            "authority": zero_authority(),
        }
        canonical_json_bytes(tree_record, maximum_bytes=limits["max_record_bytes"])
        canonical_json_bytes(revision_record, maximum_bytes=limits["max_record_bytes"])
        state_record = _write_success_records(
            store=store,
            attempt=attempt,
            tree_record=tree_record,
            revision_record=revision_record,
            policy=trusted_policy,
        )
        return {
            "attempt": attempt,
            "tree": tree_record,
            "revision": revision_record,
            "state": state_record,
        }
    except EcosystemError as exc:
        if exc.reason_code == "TIME_LIMIT_EXCEEDED":
            raise
        rejected = exc.reason_code in {
            "ARCHIVE_INTEGRITY_INVALID",
            "ARCHIVE_INVALID",
            "ARCHIVE_UNSAFE_ENTRY",
            "CAS_OBJECT_CONFLICT",
            "PATH_COLLISION",
            "PATH_INVALID",
        }
        attempt = _attempt_record(
            base,
            result="REJECTED_BEFORE_REVISION" if rejected else "INSUFFICIENT_BEFORE_REVISION",
            tree_id=None,
            revision_id=None,
            reason_codes=[exc.reason_code],
        )
        with store._exclusive("intake.lock"):
            _write_attempt(store, attempt, limits["max_record_bytes"])
        return {"attempt": attempt, "tree": None, "revision": None, "state": None}
    except (zipfile.BadZipFile, RuntimeError, OSError, EOFError, struct.error, zlib.error, ValueError, OverflowError):
        attempt = _attempt_record(
            base,
            result="REJECTED_BEFORE_REVISION",
            tree_id=None,
            revision_id=None,
            reason_codes=["ARCHIVE_INTEGRITY_INVALID"],
        )
        with store._exclusive("intake.lock"):
            _write_attempt(store, attempt, limits["max_record_bytes"])
        return {"attempt": attempt, "tree": None, "revision": None, "state": None}
