"""Stable local-file and inert repository-external CAS primitives for Slice 3C.

Candidate bytes are never materialized as an executable working tree.  This
module has no delete/GC API and no network, subprocess, loader, or execution
integration.
"""
from __future__ import annotations

from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
import threading
import time
import uuid
import weakref
from typing import Any, BinaryIO, Iterator, Mapping

from .ecosystem_models import (
    EcosystemError,
    canonical_json_bytes,
    parse_json_bytes,
    validate_sha256,
    validate_typed_id,
    zero_authority,
)


ROOT_MARKER = {
    "schema_version": "nexus.ecosystem-root-marker.v1",
    "storage_mode": "inert_quarantine",
    "authority": zero_authority(),
}
ROOT_MARKER_BYTES = canonical_json_bytes(ROOT_MARKER)
_HANDLE_SEAL = object()
_STORE_CONSTRUCTION_TOKEN = object()
_INTAKE_RECORD_WRITER = object()
_STATE_RECORD_WRITER = object()
_COMPARISON_RECORD_WRITER = object()
_BINARY = getattr(os, "O_BINARY", 0)
_STORE_SEALS: "weakref.WeakKeyDictionary[QuarantineStore, tuple[Any, ...]]" = weakref.WeakKeyDictionary()
_RECORD_WRITER_SCHEMAS = {
    _INTAKE_RECORD_WRITER: {
        "intake-attempts": frozenset({"nexus.ecosystem-intake-attempt.v1"}),
        "trees": frozenset({"nexus.ecosystem-tree.v1"}),
        "revisions": frozenset({"nexus.ecosystem-revision.v1"}),
        "evidence": frozenset(
            {
                "nexus.ecosystem-intake-attempt.v1",
                "nexus.ecosystem-state-transition-receipt.v1",
            }
        ),
        "state": frozenset({"nexus.ecosystem-state-record.v1"}),
        "quarantine": frozenset({"nexus.ecosystem-quarantine-view.v1"}),
    },
    _STATE_RECORD_WRITER: {
        "components": frozenset({"nexus.ecosystem-component-revision.v1"}),
        "evidence": frozenset(
            {
                "nexus.ecosystem-tree.v1",
                "nexus.ecosystem-component-revision.v1",
                "nexus.ecosystem-provenance-evidence.v1",
                "nexus.ecosystem-license-evidence.v1",
                "nexus.ecosystem-static-finding.v1",
                "nexus.ecosystem-static-report.v1",
                "nexus.ecosystem-component-classification.v1",
                "nexus.ecosystem-classification-report.v1",
                "nexus.ecosystem-intake-attempt.v1",
                "nexus.ecosystem-state-transition-receipt.v1",
                "nexus.evaluation-contract.v1",
            }
        ),
        "state": frozenset({"nexus.ecosystem-state-record.v1"}),
    },
    _COMPARISON_RECORD_WRITER: {
        "comparisons": frozenset({"nexus.ecosystem-revision-comparison.v1"}),
    },
}
_RECORD_SCHEMA_NAMESPACES = {
    "nexus.ecosystem-tree.v1": frozenset({"trees", "evidence"}),
    "nexus.ecosystem-revision.v1": frozenset({"revisions"}),
    "nexus.ecosystem-component-revision.v1": frozenset({"components", "evidence"}),
    "nexus.ecosystem-provenance-evidence.v1": frozenset({"evidence"}),
    "nexus.ecosystem-license-evidence.v1": frozenset({"evidence"}),
    "nexus.ecosystem-static-finding.v1": frozenset({"evidence"}),
    "nexus.ecosystem-static-report.v1": frozenset({"evidence"}),
    "nexus.ecosystem-component-classification.v1": frozenset({"evidence"}),
    "nexus.ecosystem-classification-report.v1": frozenset({"evidence"}),
    "nexus.ecosystem-revision-comparison.v1": frozenset({"comparisons"}),
    "nexus.ecosystem-intake-attempt.v1": frozenset({"intake-attempts", "evidence"}),
    "nexus.ecosystem-state-transition-receipt.v1": frozenset({"evidence"}),
    "nexus.ecosystem-state-record.v1": frozenset({"state"}),
    "nexus.ecosystem-quarantine-view.v1": frozenset({"quarantine"}),
    "nexus.evaluation-contract.v1": frozenset({"evidence"}),
}
_DIGEST_RECORD_NAMESPACES = frozenset(
    {"trees", "revisions", "components", "evidence", "comparisons", "state"}
)
_RECORD_ID_FIELDS = {
    "nexus.ecosystem-tree.v1": ("tree_id", "tree"),
    "nexus.ecosystem-revision.v1": ("revision_id", "revision"),
    "nexus.ecosystem-component-revision.v1": ("component_revision_id", "component-revision"),
    "nexus.ecosystem-provenance-evidence.v1": ("evidence_id", "evidence"),
    "nexus.ecosystem-license-evidence.v1": ("evidence_id", "evidence"),
    "nexus.ecosystem-static-finding.v1": ("finding_id", "finding"),
    "nexus.ecosystem-static-report.v1": ("report_id", "static-report"),
    "nexus.ecosystem-component-classification.v1": ("classification_id", "classification"),
    "nexus.ecosystem-classification-report.v1": ("report_id", "classification-report"),
    "nexus.ecosystem-revision-comparison.v1": ("comparison_id", "comparison"),
    "nexus.ecosystem-intake-attempt.v1": ("attempt_result_id", "intake-attempt-result"),
    "nexus.ecosystem-state-transition-receipt.v1": ("transition_id", "transition"),
    "nexus.ecosystem-state-record.v1": ("state_record_id", "state-record"),
}
_STORE_LAYOUT = (
    "incoming",
    "objects/sha256",
    "intake-attempts/sha256",
    "trees/sha256",
    "revisions/sha256",
    "components/sha256",
    "evidence/sha256",
    "comparisons/sha256",
    "quarantine",
    "state/sha256",
    "locks",
    "tmp",
)
_REMOTE_POSIX_FILESYSTEMS = frozenset(
    {
        "9p",
        "afs",
        "ceph",
        "cifs",
        "fuse.ceph",
        "fuse.glusterfs",
        "fuse.sshfs",
        "glusterfs",
        "ncpfs",
        "nfs",
        "nfs4",
        "smb3",
        "smbfs",
        "sshfs",
    }
)
_LOCAL_POSIX_FILESYSTEMS = frozenset(
    {
        "bcachefs",
        "btrfs",
        "ext2",
        "ext3",
        "ext4",
        "f2fs",
        "jfs",
        "xfs",
        "zfs",
    }
)
_MOUNTINFO_MAX_BYTES = 1_048_576


def _bounded_error(code: str, message: str) -> EcosystemError:
    return EcosystemError(code, message)


def _is_reparse_stat(info: os.stat_result) -> bool:
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def _identity(info: os.stat_result) -> tuple[int, int, int, int]:
    return (int(info.st_dev), int(info.st_ino), int(info.st_size), int(info.st_mtime_ns))


def _write_all(descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    written = 0
    while written < len(view):
        count = os.write(descriptor, view[written:])
        if count <= 0:
            raise _bounded_error("CAS_OBJECT_CONFLICT", "Bounded file write did not progress")
        written += count


def _reject_unsafe_path_text(path: Path) -> None:
    raw = str(path)
    if not raw or raw.startswith(("\\\\", "//", "\\?\\", "\\.\\")):
        raise _bounded_error("CAS_ROOT_INVALID", "Network or device paths are forbidden")
    if "\x00" in raw:
        raise _bounded_error("CAS_ROOT_INVALID", "Path contains a NUL character")


def _unescape_mountinfo(value: str) -> str:
    for escaped, replacement in (
        ("\\040", " "),
        ("\\011", "\t"),
        ("\\012", "\n"),
        ("\\134", "\\"),
    ):
        value = value.replace(escaped, replacement)
    return value


def _mountinfo_root_risk(path: Path, text: str) -> str | None:
    """Classify a Linux mount-table projection without trusting path aliases."""
    if type(text) is not str:
        return "unverifiable"
    target = str(path).replace("\\", "/")
    if not target.startswith("/"):
        return "unverifiable"
    target = "/" + target.strip("/")
    mounts: list[tuple[int, str, str, str, str, str, tuple[str, ...]]] = []
    for raw_line in text.splitlines():
        fields = raw_line.split()
        try:
            separator = fields.index("-")
        except ValueError:
            continue
        if separator < 6 or len(fields) < separator + 3:
            continue
        device = fields[2]
        mount_root = _unescape_mountinfo(fields[3])
        mount_point = _unescape_mountinfo(fields[4])
        filesystem = fields[separator + 1].casefold()
        source = _unescape_mountinfo(fields[separator + 2])
        mount_point = "/" + mount_point.strip("/")
        options = tuple(fields[5].split(",")) + tuple(fields[6:separator])
        if re.fullmatch(r"[0-9]+:[0-9]+", device):
            mounts.append(
                (len(mount_point), mount_point, device, filesystem, source, mount_root, options)
            )
    matches = [
        item
        for item in mounts
        if item[1] == "/" or target == item[1] or target.startswith(item[1] + "/")
    ]
    if not matches:
        return "unverifiable"
    _length, mount_point, device, filesystem, source, mount_root, options = max(
        matches, key=lambda item: item[0]
    )
    if (
        filesystem in _REMOTE_POSIX_FILESYSTEMS
        or source.startswith("//")
        or (":" in source and not source.startswith("/dev/"))
    ):
        return "network"
    if filesystem not in _LOCAL_POSIX_FILESYSTEMS:
        return "unverifiable"
    if filesystem != "zfs" and not source.startswith("/dev/"):
        return "unverifiable"
    if filesystem == "zfs" and (
        not source
        or source.startswith(("/", "."))
        or "//" in source
        or ":" in source
    ):
        return "unverifiable"
    if "bind" in options or "rbind" in options:
        return "alias"
    # A non-root subtree mounted from an ordinary block filesystem is the
    # observable mountinfo shape of a bind alias.  Btrfs/ZFS subvolume roots
    # are native filesystem identities and are not treated as aliases here.
    if mount_root != "/" and filesystem not in {"btrfs", "zfs"}:
        return "alias"
    # Linux does not reliably retain a ``bind`` option in mountinfo. An
    # identical filesystem/device/source/root mounted at a second mount point
    # is therefore an alias even when both roots are rendered as ``/``.
    if any(
        other_point != mount_point
        and other_device == device
        and other_filesystem == filesystem
        and other_source == source
        and other_root == mount_root
        for (
            _other_length,
            other_point,
            other_device,
            other_filesystem,
            other_source,
            other_root,
            _other_options,
        ) in mounts
    ):
        return "alias"
    return None


def _runtime_platform_identity() -> tuple[str, str]:
    """Private deterministic seam for platform-locality regression tests."""
    return os.name, sys.platform


def _read_linux_mountinfo() -> str:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = -1
    try:
        descriptor = os.open("/proc/self/mountinfo", flags)
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65_536, _MOUNTINFO_MAX_BYTES - total + 1))
            if not chunk:
                break
            total += len(chunk)
            if total > _MOUNTINFO_MAX_BYTES:
                raise _bounded_error("CAS_ROOT_INVALID", "Mount identity evidence is unbounded")
            chunks.append(chunk)
        return b"".join(chunks).decode("utf-8", errors="strict")
    except (OSError, UnicodeDecodeError):
        raise _bounded_error("CAS_ROOT_INVALID", "Mount identity evidence is unavailable") from None
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _reject_posix_remote_or_alias_root(path: Path) -> None:
    operating_system, platform = _runtime_platform_identity()
    if operating_system == "nt":
        return
    if operating_system != "posix" or not platform.startswith("linux"):
        raise _bounded_error(
            "CAS_ROOT_INVALID", "Local-volume identity proof is unavailable on this POSIX platform"
        )
    risk = _mountinfo_root_risk(path, _read_linux_mountinfo())
    if risk is not None:
        raise _bounded_error(
            "CAS_ROOT_INVALID", "CAS root is not positively verified as a local non-aliased volume"
        )


if os.name == "nt":
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
    _GENERIC_READ = 0x80000000
    _GENERIC_WRITE = 0x40000000
    _FILE_SHARE_READ = 0x00000001
    _FILE_SHARE_WRITE = 0x00000002
    _FILE_SHARE_DELETE = 0x00000004
    _OPEN_EXISTING = 3
    _FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
    _FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
    _FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
    _FILE_TYPE_DISK = 1
    _DRIVE_FIXED = 3
    _FILE_ID_INFO_CLASS = 18

    class _FILE_ID_128(ctypes.Structure):
        _fields_ = [("Identifier", ctypes.c_ubyte * 16)]

    class _FILE_ID_INFO(ctypes.Structure):
        _fields_ = [("VolumeSerialNumber", ctypes.c_ulonglong), ("FileId", _FILE_ID_128)]

    class _BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("dwFileAttributes", wintypes.DWORD),
            ("ftCreationTime", wintypes.FILETIME),
            ("ftLastAccessTime", wintypes.FILETIME),
            ("ftLastWriteTime", wintypes.FILETIME),
            ("dwVolumeSerialNumber", wintypes.DWORD),
            ("nFileSizeHigh", wintypes.DWORD),
            ("nFileSizeLow", wintypes.DWORD),
            ("nNumberOfLinks", wintypes.DWORD),
            ("nFileIndexHigh", wintypes.DWORD),
            ("nFileIndexLow", wintypes.DWORD),
        ]

    _kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    _kernel32.CreateFileW.restype = wintypes.HANDLE
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.CloseHandle.restype = wintypes.BOOL
    _kernel32.GetFileType.argtypes = [wintypes.HANDLE]
    _kernel32.GetFileType.restype = wintypes.DWORD
    _kernel32.GetFileInformationByHandleEx.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
    ]
    _kernel32.GetFileInformationByHandleEx.restype = wintypes.BOOL
    _kernel32.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(_BY_HANDLE_FILE_INFORMATION)]
    _kernel32.GetFileInformationByHandle.restype = wintypes.BOOL
    _kernel32.GetDriveTypeW.argtypes = [wintypes.LPCWSTR]
    _kernel32.GetDriveTypeW.restype = wintypes.UINT


def _win_close(handle: int) -> None:
    if os.name == "nt" and handle not in (0, _INVALID_HANDLE_VALUE):
        _kernel32.CloseHandle(wintypes.HANDLE(handle))


def _win_handle(
    path: Path,
    *,
    directory: bool,
    share_mutation: bool = False,
    share_write: bool = False,
    write: bool = False,
) -> int:
    _reject_unsafe_path_text(path)
    absolute = Path(os.path.abspath(path))
    drive, _tail = os.path.splitdrive(str(absolute))
    if not drive or _kernel32.GetDriveTypeW(f"{drive}\\") != _DRIVE_FIXED:
        raise _bounded_error("CAS_ROOT_INVALID", "Only a fixed local volume is accepted")
    flags = _FILE_FLAG_OPEN_REPARSE_POINT | (_FILE_FLAG_BACKUP_SEMANTICS if directory else 0)
    sharing = _FILE_SHARE_READ
    if share_write:
        sharing |= _FILE_SHARE_WRITE
    if share_mutation:
        sharing |= _FILE_SHARE_WRITE | _FILE_SHARE_DELETE
    handle = _kernel32.CreateFileW(
        str(absolute),
        _GENERIC_READ | (_GENERIC_WRITE if write else 0),
        sharing,
        None,
        _OPEN_EXISTING,
        flags,
        None,
    )
    numeric = int(handle)
    if numeric == _INVALID_HANDLE_VALUE:
        raise _bounded_error("INPUT_UNSTABLE", "Stable local handle could not be opened")
    if _kernel32.GetFileType(wintypes.HANDLE(numeric)) != _FILE_TYPE_DISK:
        _win_close(numeric)
        raise _bounded_error("INPUT_UNSTABLE", "Input is not a disk file")
    details = _BY_HANDLE_FILE_INFORMATION()
    if not _kernel32.GetFileInformationByHandle(wintypes.HANDLE(numeric), ctypes.byref(details)):
        _win_close(numeric)
        raise _bounded_error("INPUT_UNSTABLE", "Input metadata is unavailable")
    if details.dwFileAttributes & _FILE_ATTRIBUTE_REPARSE_POINT:
        _win_close(numeric)
        raise _bounded_error("INPUT_UNSTABLE", "Reparse points are forbidden")
    return numeric


def _win_identity(handle: int) -> tuple[int, bytes, int, int, int]:
    file_id = _FILE_ID_INFO()
    details = _BY_HANDLE_FILE_INFORMATION()
    if not _kernel32.GetFileInformationByHandleEx(
        wintypes.HANDLE(handle), _FILE_ID_INFO_CLASS, ctypes.byref(file_id), ctypes.sizeof(file_id)
    ) or not _kernel32.GetFileInformationByHandle(wintypes.HANDLE(handle), ctypes.byref(details)):
        raise _bounded_error("INPUT_UNSTABLE", "Windows file identity is unavailable")
    size = (int(details.nFileSizeHigh) << 32) | int(details.nFileSizeLow)
    written = (int(details.ftLastWriteTime.dwHighDateTime) << 32) | int(details.ftLastWriteTime.dwLowDateTime)
    return (
        int(file_id.VolumeSerialNumber),
        bytes(file_id.FileId.Identifier),
        size,
        written,
        int(details.nNumberOfLinks),
    )


def _existing_ancestors(path: Path) -> list[Path]:
    absolute = Path(os.path.abspath(path))
    result: list[Path] = []
    cursor = absolute.parent
    while cursor != cursor.parent:
        if cursor.exists():
            result.append(cursor)
        cursor = cursor.parent
    result.reverse()
    return result


def _verify_path_chain_no_links(path: Path, *, include_final: bool = True) -> None:
    absolute = Path(os.path.abspath(path))
    targets = _existing_ancestors(absolute)
    if include_final and absolute.exists():
        targets.append(absolute)
    for target in targets:
        try:
            info = os.lstat(target)
        except OSError:
            raise _bounded_error("INPUT_UNSTABLE", "Path metadata is unavailable") from None
        if stat.S_ISLNK(info.st_mode) or _is_reparse_stat(info):
            raise _bounded_error("INPUT_UNSTABLE", "Symlink or reparse path is forbidden")


def _posix_directory_identity(descriptor: int) -> tuple[int, int, int]:
    info = os.fstat(descriptor)
    if not stat.S_ISDIR(info.st_mode):
        raise _bounded_error("INPUT_UNSTABLE", "Stable ancestor is not a directory")
    return (int(info.st_dev), int(info.st_ino), stat.S_IFMT(info.st_mode))


def _open_posix_path(path: Path) -> tuple[int, tuple[int, int, int, int], list[int], list[tuple[Any, ...]]]:
    """Traverse every POSIX component relative to held no-follow dir fds."""
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    if not nofollow or not directory_flag:
        raise _bounded_error("INPUT_UNSTABLE", "Stable no-follow directory opens are unavailable")
    absolute = Path(os.path.abspath(path))
    parts = absolute.parts
    if not parts or not absolute.anchor:
        raise _bounded_error("INPUT_UNSTABLE", "Stable input path is invalid")
    directory_flags = os.O_RDONLY | directory_flag | nofollow | getattr(os, "O_CLOEXEC", 0)
    parent_handles: list[int] = []
    parent_identities: list[tuple[Any, ...]] = []
    try:
        current = os.open(absolute.anchor, directory_flags)
        parent_handles.append(current)
        parent_identities.append(_posix_directory_identity(current))
        for component in parts[1:-1]:
            current = os.open(component, directory_flags, dir_fd=current)
            parent_handles.append(current)
            parent_identities.append(_posix_directory_identity(current))
        descriptor = os.open(
            parts[-1],
            os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
            dir_fd=current,
        )
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            os.close(descriptor)
            raise _bounded_error("INPUT_UNSTABLE", "Input must be a single-link regular file")
        return descriptor, _identity(info), parent_handles, parent_identities
    except Exception:
        for handle in reversed(parent_handles):
            os.close(handle)
        raise


class StableInput:
    """A sealed, already-open, no-follow local file used by production intake."""

    __slots__ = (
        "_seal",
        "_path",
        "_stream",
        "_identity",
        "_parent_handles",
        "_parent_identities",
        "_closed",
    )

    def __init__(
        self,
        *,
        seal: object,
        path: Path,
        stream: BinaryIO,
        identity: tuple[Any, ...],
        parent_handles: list[int],
        parent_identities: list[tuple[Any, ...]],
    ) -> None:
        if seal is not _HANDLE_SEAL:
            raise _bounded_error("UNSUPPORTED_INPUT", "Stable input must come from the trusted opener")
        self._seal = seal
        self._path = path
        self._stream = stream
        self._identity = identity
        self._parent_handles = parent_handles
        self._parent_identities = parent_identities
        self._closed = False

    @property
    def size(self) -> int:
        return int(self._identity[2] if os.name == "nt" else self._identity[2])

    @property
    def name(self) -> str:
        return self._path.name

    def read(self, size: int = -1) -> bytes:
        if self._closed:
            raise _bounded_error("INPUT_UNSTABLE", "Stable input is closed")
        return self._stream.read(size)

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if self._closed:
            raise _bounded_error("INPUT_UNSTABLE", "Stable input is closed")
        return self._stream.seek(offset, whence)

    def tell(self) -> int:
        return self._stream.tell()

    def verify_unchanged(self) -> None:
        if self._closed or type(self) is not StableInput or self._seal is not _HANDLE_SEAL:
            raise _bounded_error("INPUT_UNSTABLE", "Stable input authority is invalid")
        if os.name == "nt":
            import msvcrt

            current = _win_identity(msvcrt.get_osfhandle(self._stream.fileno()))
        else:
            current = _identity(os.fstat(self._stream.fileno()))
        if current != self._identity:
            raise _bounded_error("INPUT_UNSTABLE", "Input changed during stable use")
        if os.name == "nt":
            for handle, expected in zip(self._parent_handles, self._parent_identities, strict=True):
                # Directory size and last-write time legitimately change when
                # an unrelated sibling is created.  The security identity of
                # a held ancestor is its fixed-volume FileId, while the final
                # file retains the stricter size/time/link-count comparison.
                if _win_identity(handle)[:2] != expected:
                    raise _bounded_error("INPUT_UNSTABLE", "Input ancestor changed during stable use")
            reopened: list[int] = []
            try:
                current_parent_ids: list[tuple[Any, ...]] = []
                for parent in _existing_ancestors(self._path):
                    handle = _win_handle(parent, directory=True)
                    reopened.append(handle)
                    current_parent_ids.append(_win_identity(handle)[:2])
                final_handle = _win_handle(self._path, directory=False)
                reopened.append(final_handle)
                if current_parent_ids != self._parent_identities or _win_identity(final_handle) != self._identity:
                    raise _bounded_error("INPUT_UNSTABLE", "Stable input path identity changed")
            finally:
                for handle in reversed(reopened):
                    _win_close(handle)
        else:
            for handle, expected in zip(self._parent_handles, self._parent_identities, strict=True):
                if _posix_directory_identity(handle) != expected:
                    raise _bounded_error("INPUT_UNSTABLE", "Input ancestor changed during stable use")
            reopened_file = -1
            reopened_parents: list[int] = []
            try:
                reopened_file, reopened_identity, reopened_parents, reopened_parent_ids = _open_posix_path(
                    self._path
                )
                if reopened_identity != self._identity or reopened_parent_ids != self._parent_identities:
                    raise _bounded_error("INPUT_UNSTABLE", "Stable input path identity changed")
            finally:
                if reopened_file != -1:
                    os.close(reopened_file)
                for handle in reversed(reopened_parents):
                    os.close(handle)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            try:
                self._stream.close()
            finally:
                for handle in reversed(self._parent_handles):
                    if os.name == "nt":
                        _win_close(handle)
                    else:
                        os.close(handle)
                self._parent_handles.clear()

    def __enter__(self) -> "StableInput":
        return self

    def __exit__(self, _exc_type: Any, _exc: Any, _tb: Any) -> None:
        self.close()


def _require_stable_input(value: Any) -> StableInput:
    if type(value) is not StableInput or value._seal is not _HANDLE_SEAL or value._closed:
        raise _bounded_error("UNSUPPORTED_INPUT", "Production intake requires a trusted stable input")
    value.verify_unchanged()
    return value


def open_stable_input(path: Path, *, maximum_bytes: int) -> StableInput:
    """Open one existing regular local file without following path indirection."""
    if not isinstance(path, Path) or type(maximum_bytes) is not int or maximum_bytes < 0:
        raise _bounded_error("UNSUPPORTED_INPUT", "Stable input request is malformed")
    _reject_unsafe_path_text(path)
    absolute = Path(os.path.abspath(path))
    _verify_path_chain_no_links(absolute)
    parent_handles: list[int] = []
    parent_identities: list[tuple[Any, ...]] = []
    try:
        if os.name == "nt":
            for parent in _existing_ancestors(absolute):
                handle = _win_handle(parent, directory=True)
                parent_handles.append(handle)
                parent_identities.append(_win_identity(handle)[:2])
            handle = _win_handle(absolute, directory=False)
            identity = _win_identity(handle)
            if identity[4] != 1:
                _win_close(handle)
                raise _bounded_error("INPUT_UNSTABLE", "Hard-linked input is forbidden")
            import msvcrt

            descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
            stream = os.fdopen(descriptor, "rb", closefd=True)
        else:
            descriptor, identity, parent_handles, parent_identities = _open_posix_path(absolute)
            stream = os.fdopen(descriptor, "rb", closefd=True)
        if identity[2] > maximum_bytes:
            stream.close()
            raise _bounded_error("RESOURCE_LIMIT_EXCEEDED", "Input exceeds its byte limit")
        return StableInput(
            seal=_HANDLE_SEAL,
            path=absolute,
            stream=stream,
            identity=identity,
            parent_handles=parent_handles,
            parent_identities=parent_identities,
        )
    except Exception:
        for handle in reversed(parent_handles):
            if os.name == "nt":
                _win_close(handle)
            else:
                os.close(handle)
        raise


def stable_read_bytes(path: Path, *, maximum_bytes: int, reason_code: str = "INPUT_UNSTABLE") -> bytes:
    try:
        with open_stable_input(path, maximum_bytes=maximum_bytes) as stable:
            chunks: list[bytes] = []
            count = 0
            while True:
                chunk = stable.read(min(65_536, maximum_bytes - count + 1))
                if not chunk:
                    break
                count += len(chunk)
                if count > maximum_bytes:
                    raise _bounded_error("RESOURCE_LIMIT_EXCEEDED", "Stable read exceeds its byte limit")
                chunks.append(chunk)
            stable.verify_unchanged()
            return b"".join(chunks)
    except EcosystemError as exc:
        if exc.reason_code in {"RESOURCE_LIMIT_EXCEEDED", reason_code}:
            raise
        raise EcosystemError(reason_code, "Stable local read failed") from None
    except (OSError, ValueError):
        raise EcosystemError(reason_code, "Stable local read failed") from None


def _is_within(path: Path, parent: Path) -> bool:
    # Normalize filesystem aliases (including Windows 8.3 short names) before
    # the lexical containment comparison.  This is only one conservative
    # precondition: the caller still performs no-follow chain inspection and
    # held-handle/file-identity verification before trusting either path.
    try:
        candidate = os.path.normcase(os.path.realpath(os.path.abspath(path)))
        boundary = os.path.normcase(os.path.realpath(os.path.abspath(parent)))
        return os.path.commonpath((candidate, boundary)) == boundary
    except (OSError, ValueError):
        return False


def _default_forbidden_roots(repository_root: Path) -> list[Path]:
    roots = [repository_root]
    for name in ("CODEX_HOME", "VIRTUAL_ENV"):
        value = os.environ.get(name)
        if value:
            roots.append(Path(value))
    for value in os.environ.get("PATH", "").split(os.pathsep):
        if value:
            roots.append(Path(value))
    return roots


def _validate_external_root(root: Path, repository_root: Path) -> Path:
    if not isinstance(root, Path) or not isinstance(repository_root, Path):
        raise _bounded_error("CAS_ROOT_INVALID", "CAS root request is malformed")
    root = Path(os.path.abspath(root))
    repository_root = Path(os.path.abspath(repository_root))
    _reject_unsafe_path_text(root)
    if root == Path(root.anchor) or _is_within(root, repository_root):
        raise _bounded_error("CAS_ROOT_INVALID", "CAS root must be repository-external and narrow")
    lowered = "/" + str(root).replace("\\", "/").strip("/").casefold() + "/"
    if any(token in lowered for token in ("/.codex/plugins/", "/.codex/skills/", "/plugin/cache/")):
        raise _bounded_error("CAS_ROOT_INVALID", "CAS root overlaps a Host, plugin, or Skill root")
    for forbidden in _default_forbidden_roots(repository_root):
        forbidden = Path(os.path.abspath(forbidden))
        if _is_within(root, forbidden) or _is_within(forbidden, root):
            raise _bounded_error("CAS_ROOT_INVALID", "CAS root overlaps a forbidden runtime root")
    _reject_posix_remote_or_alias_root(root)
    _verify_path_chain_no_links(root, include_final=True)
    return root


@contextmanager
def _file_lock(path: Path) -> Iterator[None]:
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | _BINARY, 0o600)
    try:
        if os.name == "nt":
            import msvcrt

            os.lseek(descriptor, 0, os.SEEK_SET)
            if os.fstat(descriptor).st_size == 0:
                _write_all(descriptor, b"\0")
                os.fsync(descriptor)
            os.lseek(descriptor, 0, os.SEEK_SET)
            msvcrt.locking(descriptor, msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt

                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


class QuarantineStore:
    """Immutable inert CAS and append-only record store."""

    __slots__ = (
        "root",
        "repository_root",
        "max_cas_bytes",
        "_thread_lock",
        "_seal",
        "_policy_semantic_sha256",
        "_integrity_manifest_sha256",
        "_policy_trust_mode",
        "_policy_repository_root",
        "_construction_mode",
        "_root_handle",
        "_root_identity",
        "__weakref__",
    )

    def __init_subclass__(cls, **_kwargs: Any) -> None:
        raise TypeError("QuarantineStore is final")

    def __init__(
        self,
        root: Path,
        *,
        repository_root: Path,
        max_cas_bytes: int,
        policy_semantic_sha256: str | None = None,
        integrity_manifest_sha256: str | None = None,
        policy_trust_mode: str | None = None,
        policy_repository_root: str | None = None,
        construction_mode: str | None = None,
        token: object | None = None,
    ) -> None:
        if token is not _STORE_CONSTRUCTION_TOKEN:
            raise _bounded_error(
                "CAS_ROOT_INVALID", "Trusted quarantine store construction is private"
            )
        if type(max_cas_bytes) is not int or max_cas_bytes <= 0:
            raise _bounded_error("CAS_ROOT_INVALID", "CAS byte ceiling is invalid")
        if construction_mode not in {"production", "hermetic_test"}:
            raise _bounded_error("CAS_ROOT_INVALID", "Quarantine store construction mode is invalid")
        self.root = _validate_external_root(root, repository_root)
        self.repository_root = Path(os.path.abspath(repository_root))
        self.max_cas_bytes = max_cas_bytes
        self._thread_lock = threading.Lock()
        self._seal = object()
        self._policy_semantic_sha256 = validate_sha256(
            policy_semantic_sha256, "store policy digest"
        )
        self._integrity_manifest_sha256 = validate_sha256(
            integrity_manifest_sha256, "store integrity manifest digest"
        )
        if policy_trust_mode not in {"production", "hermetic_test"}:
            raise _bounded_error("POLICY_UNTRUSTED", "Store policy trust mode is invalid")
        if type(policy_repository_root) is not str or not Path(policy_repository_root).is_absolute():
            raise _bounded_error("POLICY_UNTRUSTED", "Store policy root is invalid")
        self._policy_trust_mode = policy_trust_mode
        self._policy_repository_root = policy_repository_root
        self._construction_mode = construction_mode
        self._root_handle = -1
        self._root_identity: tuple[Any, ...] = ()
        self._initialize()
        if os.name == "nt":
            self._root_handle = _win_handle(self.root, directory=True, share_mutation=True)
            self._root_identity = _win_identity(self._root_handle)[:2]
        else:
            flags = (
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_CLOEXEC", 0)
            )
            if not getattr(os, "O_DIRECTORY", 0) or not getattr(os, "O_NOFOLLOW", 0):
                raise _bounded_error("CAS_ROOT_INVALID", "Stable CAS-root handles are unavailable")
            self._root_handle = os.open(self.root, flags)
            self._root_identity = _posix_directory_identity(self._root_handle)
        _STORE_SEALS[self] = (
            self._seal,
            str(self.root),
            str(self.repository_root),
            self.max_cas_bytes,
            self._root_identity,
            self._policy_semantic_sha256,
            self._integrity_manifest_sha256,
            self._policy_trust_mode,
            self._policy_repository_root,
            self._construction_mode,
        )

    def _require_integrity(self) -> None:
        baseline = _STORE_SEALS.get(self)
        if (
            type(self) is not QuarantineStore
            or type(baseline) is not tuple
            or len(baseline) != 10
            or baseline[0] is not self._seal
            or baseline[1] != str(self.root)
            or baseline[2] != str(self.repository_root)
            or baseline[3] != self.max_cas_bytes
            or baseline[4] != self._root_identity
            or baseline[5] != self._policy_semantic_sha256
            or baseline[6] != self._integrity_manifest_sha256
            or baseline[7] != self._policy_trust_mode
            or baseline[8] != self._policy_repository_root
            or baseline[9] != self._construction_mode
        ):
            raise _bounded_error("CAS_ROOT_INVALID", "Quarantine store integrity changed")
        if os.name == "nt":
            current = _win_handle(self.root, directory=True, share_mutation=True)
            try:
                path_identity = _win_identity(current)[:2]
                held_identity = _win_identity(self._root_handle)[:2]
            finally:
                _win_close(current)
        else:
            path_descriptor = os.open(
                self.root,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_CLOEXEC", 0),
            )
            try:
                path_identity = _posix_directory_identity(path_descriptor)
                held_identity = _posix_directory_identity(self._root_handle)
            finally:
                os.close(path_descriptor)
        if path_identity != self._root_identity or held_identity != self._root_identity:
            raise _bounded_error("CAS_ROOT_INVALID", "Quarantine root identity changed")

    def _require_policy(self, policy: Any) -> None:
        """Rebind every authority-sensitive operation to one sealed policy."""
        self._require_integrity()
        try:
            # Delayed import avoids the policy -> stable-read storage cycle.
            from .ecosystem_policy import _require_trusted_source_policy

            trusted = _require_trusted_source_policy(policy)
        except (ImportError, AttributeError, TypeError, EcosystemError):
            raise _bounded_error("POLICY_UNTRUSTED", "Trusted store policy is unavailable") from None
        if (
            not hmac.compare_digest(
                trusted.policy_semantic_sha256, self._policy_semantic_sha256
            )
            or not hmac.compare_digest(
                trusted.integrity_manifest_sha256, self._integrity_manifest_sha256
            )
            or trusted._trust_mode != self._policy_trust_mode
            or trusted._repository_root != self._policy_repository_root
            or self.max_cas_bytes > trusted.resource_limits["max_cas_bytes"]
        ):
            raise _bounded_error("POLICY_UNTRUSTED", "Quarantine store policy binding changed")

    def _require_registry(self, registry: Any) -> None:
        """Bind evaluation authority to the same sealed production/test context."""
        self._require_integrity()
        try:
            from .evaluation import _require_trusted_registry

            trusted = _require_trusted_registry(registry)
        except (ImportError, AttributeError, TypeError, ValueError):
            raise _bounded_error("POLICY_UNTRUSTED", "Trusted registry is unavailable") from None
        if (
            trusted._trust_mode != self._policy_trust_mode
            or trusted._repository_root != self._policy_repository_root
            or not hmac.compare_digest(
                trusted._integrity_manifest_sha256,
                self._integrity_manifest_sha256,
            )
        ):
            raise _bounded_error("POLICY_UNTRUSTED", "Registry trust context differs from the store")

    @staticmethod
    def _relative_parts(relative: str) -> tuple[str, ...]:
        if (
            type(relative) is not str
            or not relative
            or relative.startswith(("/", "\\"))
            or "\\" in relative
        ):
            raise _bounded_error("CAS_ROOT_INVALID", "Store locator is invalid")
        parts = tuple(Path(relative).parts)
        if not parts or any(part in {"", ".", ".."} or ":" in part for part in parts):
            raise _bounded_error("CAS_ROOT_INVALID", "Store locator is invalid")
        return parts

    @classmethod
    def _record_parts(cls, relative: str) -> tuple[str, ...]:
        parts = cls._relative_parts(relative)
        valid = False
        if (
            len(parts) == 3
            and parts[0] in _DIGEST_RECORD_NAMESPACES
            and parts[1] == "sha256"
            and re.fullmatch(r"[0-9a-f]{64}\.json", parts[2])
        ):
            valid = True
        elif (
            len(parts) == 4
            and parts[:2] == ("intake-attempts", "sha256")
            and re.fullmatch(r"[0-9a-f]{64}", parts[2])
            and re.fullmatch(r"[0-9a-f]{64}\.json", parts[3])
        ):
            valid = True
        elif (
            len(parts) == 2
            and parts[0] == "quarantine"
            and re.fullmatch(r"[0-9a-f]{64}\.json", parts[1])
        ):
            valid = True
        if not valid:
            raise _bounded_error("CAS_ROOT_INVALID", "Record locator is outside the closed schema")
        return parts

    @classmethod
    def _listing_parts(cls, relative: str) -> tuple[str, ...]:
        parts = cls._relative_parts(relative)
        if parts in {
            ("revisions", "sha256"),
            ("comparisons", "sha256"),
            ("state", "sha256"),
            ("quarantine",),
        }:
            return parts
        if (
            len(parts) == 3
            and parts[:2] == ("intake-attempts", "sha256")
            and re.fullmatch(r"[0-9a-f]{64}", parts[2])
        ):
            return parts
        raise _bounded_error("CAS_ROOT_INVALID", "Record namespace is outside the closed schema")

    @staticmethod
    def _record_payload_digest(parts: tuple[str, ...], payload: Mapping[str, Any]) -> str:
        schema = payload.get("schema_version")
        if parts[0] == "quarantine":
            field, prefix = "revision_id", "revision"
        elif schema == "nexus.evaluation-contract.v1":
            return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
        else:
            identity = _RECORD_ID_FIELDS.get(schema)
            if identity is None:
                raise _bounded_error("POLICY_SCHEMA_INVALID", "Record schema is not publishable")
            field, prefix = identity
        value = payload.get(field)
        validate_typed_id(value, prefix)
        return value.split("/", 1)[1]

    @classmethod
    def _validate_record_binding(
        cls, parts: tuple[str, ...], payload: Mapping[str, Any]
    ) -> None:
        schema = payload.get("schema_version")
        allowed_namespaces = _RECORD_SCHEMA_NAMESPACES.get(schema)
        if allowed_namespaces is None or parts[0] not in allowed_namespaces:
            raise _bounded_error(
                "POLICY_SCHEMA_INVALID", "Record schema and namespace are inconsistent"
            )
        digest = cls._record_payload_digest(parts, payload)
        if parts[0] == "intake-attempts":
            attempt_id = payload.get("attempt_id")
            validate_typed_id(attempt_id, "intake-attempt")
            if parts[2] != attempt_id.split("/", 1)[1] or parts[3][:-5] != digest:
                raise _bounded_error("CAS_OBJECT_CONFLICT", "Intake record locator is inconsistent")
        elif parts[-1][:-5] != digest:
            raise _bounded_error("CAS_OBJECT_CONFLICT", "Immutable record locator is inconsistent")

    @contextmanager
    def _held_directory(self, relative: str, *, create: bool = False) -> Iterator[tuple[Path, int | None]]:
        """Hold every below-root directory component without following links."""
        self._require_integrity()
        parts = self._relative_parts(relative)
        cursor = self.root
        handles: list[int] = []
        identities: list[tuple[Any, ...]] = []
        try:
            if os.name == "nt":
                root_handle = _win_handle(
                    self.root, directory=True, share_mutation=False, share_write=True
                )
                handles.append(root_handle)
                identities.append(_win_identity(root_handle)[:2])
                if identities[0] != self._root_identity:
                    raise _bounded_error("CAS_ROOT_INVALID", "Quarantine root identity changed")
                for part in parts:
                    target = cursor / part
                    if create:
                        try:
                            target.mkdir(mode=0o700)
                        except FileExistsError:
                            pass
                    handle = _win_handle(
                        target, directory=True, share_mutation=False, share_write=True
                    )
                    handles.append(handle)
                    identities.append(_win_identity(handle)[:2])
                    cursor = target
            else:
                flags = (
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0)
                    | getattr(os, "O_CLOEXEC", 0)
                )
                current = os.dup(self._root_handle)
                handles.append(current)
                identities.append(_posix_directory_identity(current))
                if identities[0] != self._root_identity:
                    raise _bounded_error("CAS_ROOT_INVALID", "Quarantine root identity changed")
                for part in parts:
                    if create:
                        try:
                            os.mkdir(part, 0o700, dir_fd=current)
                        except FileExistsError:
                            pass
                    current = os.open(part, flags, dir_fd=current)
                    handles.append(current)
                    identities.append(_posix_directory_identity(current))
                    cursor /= part
        except EcosystemError:
            for handle in reversed(handles):
                if os.name == "nt":
                    _win_close(handle)
                else:
                    os.close(handle)
            raise
        except OSError:
            for handle in reversed(handles):
                if os.name == "nt":
                    _win_close(handle)
                else:
                    os.close(handle)
            raise _bounded_error("CAS_ROOT_INVALID", "Store directory is unavailable or unsafe") from None

        try:
            yield cursor, None if os.name == "nt" else handles[-1]
            if os.name == "nt":
                for handle, expected in zip(handles, identities, strict=True):
                    if _win_identity(handle)[:2] != expected:
                        raise _bounded_error("CAS_ROOT_INVALID", "Store directory identity changed")
            else:
                for handle, expected in zip(handles, identities, strict=True):
                    if _posix_directory_identity(handle) != expected:
                        raise _bounded_error("CAS_ROOT_INVALID", "Store directory identity changed")
        finally:
            for handle in reversed(handles):
                if os.name == "nt":
                    _win_close(handle)
                else:
                    os.close(handle)

    @staticmethod
    def _open_created(path: Path, directory_fd: int | None, *, read_write: bool = False) -> int:
        flags = (os.O_RDWR if read_write else os.O_WRONLY) | os.O_CREAT | os.O_EXCL | _BINARY
        if os.name != "nt":
            flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
            return os.open(path.name, flags, 0o600, dir_fd=directory_fd)
        return os.open(path, flags, 0o600)

    @staticmethod
    def _unlink_member(path: Path, directory_fd: int | None) -> None:
        if os.name == "nt":
            path.unlink(missing_ok=True)
            return
        try:
            os.unlink(path.name, dir_fd=directory_fd)
        except FileNotFoundError:
            pass

    @staticmethod
    def _stat_member(path: Path, directory_fd: int | None) -> os.stat_result:
        if os.name == "nt":
            return os.lstat(path)
        return os.stat(path.name, dir_fd=directory_fd, follow_symlinks=False)

    @staticmethod
    def _member_exists(path: Path, directory_fd: int | None) -> bool:
        try:
            QuarantineStore._stat_member(path, directory_fd)
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def _read_member(
        path: Path,
        directory_fd: int | None,
        *,
        maximum_bytes: int,
        reason_code: str,
    ) -> bytes:
        descriptor = -1
        try:
            if os.name == "nt":
                handle = _win_handle(path, directory=False, share_mutation=False)
                import msvcrt

                descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
            else:
                descriptor = os.open(
                    path.name,
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=directory_fd,
                )
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > maximum_bytes:
                raise _bounded_error(reason_code, "Store member metadata is invalid")
            chunks: list[bytes] = []
            count = 0
            while True:
                chunk = os.read(descriptor, min(65_536, maximum_bytes - count + 1))
                if not chunk:
                    break
                count += len(chunk)
                if count > maximum_bytes:
                    raise _bounded_error(reason_code, "Store member exceeds its byte limit")
                chunks.append(chunk)
            after = os.fstat(descriptor)
            if _identity(after) != _identity(info):
                raise _bounded_error(reason_code, "Store member changed during read")
            return b"".join(chunks)
        except EcosystemError:
            raise
        except OSError:
            raise _bounded_error(reason_code, "Store member is unavailable") from None
        finally:
            if descriptor != -1:
                os.close(descriptor)

    @contextmanager
    def _store_file_lock(self, name: str) -> Iterator[None]:
        if name not in {"cas.lock", "state.lock", "intake.lock"}:
            raise _bounded_error("CAS_ROOT_INVALID", "Store lock name is invalid")
        with self._held_directory("locks") as (directory, directory_fd):
            path = directory / name
            descriptor = -1
            locked = False
            try:
                if os.name == "nt":
                    if not path.exists():
                        try:
                            created = self._open_created(path, directory_fd, read_write=True)
                        except FileExistsError:
                            pass
                        else:
                            os.close(created)
                    handle = _win_handle(
                        path, directory=False, share_mutation=True, write=True
                    )
                    import msvcrt

                    descriptor = msvcrt.open_osfhandle(handle, os.O_RDWR | os.O_BINARY)
                else:
                    descriptor = os.open(
                        name,
                        os.O_RDWR
                        | os.O_CREAT
                        | getattr(os, "O_NOFOLLOW", 0)
                        | getattr(os, "O_CLOEXEC", 0),
                        0o600,
                        dir_fd=directory_fd,
                    )
                info = os.fstat(descriptor)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise _bounded_error("CAS_ROOT_INVALID", "Store lock is unsafe")
                if info.st_size == 0:
                    _write_all(descriptor, b"\0")
                    os.fsync(descriptor)
                os.lseek(descriptor, 0, os.SEEK_SET)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(descriptor, msvcrt.LK_LOCK, 1)
                else:
                    import fcntl

                    fcntl.flock(descriptor, fcntl.LOCK_EX)
                locked = True
                yield
            finally:
                if descriptor != -1:
                    try:
                        if locked and os.name == "nt":
                            import msvcrt

                            os.lseek(descriptor, 0, os.SEEK_SET)
                            msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
                        elif locked:
                            import fcntl

                            fcntl.flock(descriptor, fcntl.LOCK_UN)
                    finally:
                        os.close(descriptor)

    @contextmanager
    def _exclusive(self, name: str) -> Iterator[None]:
        """Process/thread serialization for one bounded immutable namespace."""
        with self._thread_lock, self._store_file_lock(name):
            yield

    def close(self) -> None:
        handle = getattr(self, "_root_handle", -1)
        if handle != -1:
            self._root_handle = -1
            if os.name == "nt":
                _win_close(handle)
            else:
                os.close(handle)
            _STORE_SEALS.pop(self, None)

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def _initialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        _verify_path_chain_no_links(self.root)
        if os.name != "nt":
            os.chmod(self.root, 0o700)
            if stat.S_IMODE(os.stat(self.root, follow_symlinks=False).st_mode) & 0o077:
                raise _bounded_error("CAS_ROOT_INVALID", "CAS root is not user-private")
        marker = self.root / ".nexus-ecosystem-root.json"
        if marker.exists():
            raw = stable_read_bytes(marker, maximum_bytes=16_384, reason_code="CAS_ROOT_INVALID")
            if raw != ROOT_MARKER_BYTES or parse_json_bytes(raw, maximum_bytes=16_384) != ROOT_MARKER:
                raise _bounded_error("CAS_ROOT_INVALID", "CAS ownership marker is invalid")
        else:
            descriptor = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL | _BINARY, 0o600)
            try:
                _write_all(descriptor, ROOT_MARKER_BYTES)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        for relative in _STORE_LAYOUT:
            target = self.root / relative
            target.mkdir(parents=True, exist_ok=True, mode=0o700)
            _verify_path_chain_no_links(target)

    def _object_path(self, digest: str) -> Path:
        self._require_integrity()
        validate_sha256(digest, "CAS digest")
        return self.root / "objects" / "sha256" / digest[:2] / digest

    def _cas_usage(self) -> int:
        self._require_integrity()
        total = 0
        with self._held_directory("objects/sha256") as (base, base_fd):
            with os.scandir(base if os.name == "nt" else base_fd) as prefixes:
                prefix_names = sorted(item.name for item in prefixes)
            for name in prefix_names:
                if not re.fullmatch(r"[0-9a-f]{2}", name):
                    raise _bounded_error("CAS_ROOT_INVALID", "CAS object namespace is unsafe")
                with self._held_directory(f"objects/sha256/{name}") as (directory, directory_fd):
                    with os.scandir(directory if os.name == "nt" else directory_fd) as candidates:
                        for candidate in candidates:
                            info = (
                                os.lstat(directory / candidate.name)
                                if os.name == "nt"
                                else candidate.stat(follow_symlinks=False)
                            )
                            if (
                                not re.fullmatch(r"[0-9a-f]{64}", candidate.name)
                                or not candidate.name.startswith(name)
                                or stat.S_ISLNK(info.st_mode)
                                or _is_reparse_stat(info)
                                or not stat.S_ISREG(info.st_mode)
                                or info.st_nlink != 1
                            ):
                                raise _bounded_error("CAS_OBJECT_CONFLICT", "CAS contains an unsafe object")
                            total += info.st_size
                            if total > self.max_cas_bytes:
                                raise _bounded_error("CAS_QUOTA_EXCEEDED", "CAS quota is exceeded")
        return total

    def put_blob(
        self,
        stream: BinaryIO,
        *,
        maximum_bytes: int,
        expected_sha256: str | None = None,
        expected_size: int | None = None,
        deadline: float | None = None,
    ) -> tuple[str, int]:
        if type(maximum_bytes) is not int or maximum_bytes < 0 or not hasattr(stream, "read"):
            raise _bounded_error("UNSUPPORTED_INPUT", "CAS stream request is invalid")
        if expected_sha256 is not None:
            validate_sha256(expected_sha256, "expected CAS digest")
        if expected_size is not None and (
            type(expected_size) is not int or not 0 <= expected_size <= maximum_bytes
        ):
            raise _bounded_error("UNSUPPORTED_INPUT", "Expected CAS size is invalid")
        self._require_integrity()
        # Capacity is decided after the staged bytes have been hashed, under
        # cas.lock, so an already-present identical object remains reusable at
        # the exact quota boundary.  A pessimistic pre-reservation here would
        # incorrectly reject that idempotent case; concurrent new objects are
        # still serialized and checked immediately before atomic publication.
        with self._thread_lock, self._store_file_lock("cas.lock"):
            self._cas_usage()
        temporary = self.root / "tmp" / f"{uuid.uuid4().hex}.partial"
        return self._put_blob_staged(
            temporary,
            stream,
            maximum_bytes=maximum_bytes,
            expected_sha256=expected_sha256,
            expected_size=expected_size,
            deadline=deadline,
        )

    def _put_blob_staged(
        self,
        temporary: Path,
        stream: BinaryIO,
        *,
        maximum_bytes: int,
        expected_sha256: str | None,
        expected_size: int | None,
        deadline: float | None,
    ) -> tuple[str, int]:
        with self._held_directory("tmp") as (_tmp_directory, tmp_fd):
            try:
                descriptor = self._open_created(temporary, tmp_fd, read_write=True)
                digest = hashlib.sha256()
                count = 0
                try:
                    while True:
                        if deadline is not None and time.monotonic() > deadline:
                            raise _bounded_error("TIME_LIMIT_EXCEEDED", "CAS operation exceeded its deadline")
                        chunk = stream.read(65_536)
                        if not chunk:
                            break
                        if type(chunk) is not bytes:
                            raise _bounded_error("UNSUPPORTED_INPUT", "CAS stream yielded a non-byte chunk")
                        count += len(chunk)
                        if count > maximum_bytes:
                            raise _bounded_error("RESOURCE_LIMIT_EXCEEDED", "CAS object exceeds its byte limit")
                        _write_all(descriptor, chunk)
                        digest.update(chunk)
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
                actual = digest.hexdigest()
                if expected_size is not None and count != expected_size:
                    raise _bounded_error("INPUT_DIGEST_MISMATCH", "CAS input size does not match")
                if expected_sha256 is not None and actual != expected_sha256:
                    raise _bounded_error("INPUT_DIGEST_MISMATCH", "CAS input digest does not match")
                reread = self._read_member(
                    temporary,
                    tmp_fd,
                    maximum_bytes=maximum_bytes,
                    reason_code="CAS_OBJECT_CONFLICT",
                )
                if len(reread) != count or hashlib.sha256(reread).hexdigest() != actual:
                    raise _bounded_error("CAS_OBJECT_CONFLICT", "CAS staging revalidation failed")
                destination = self._object_path(actual)
                relative_parent = f"objects/sha256/{actual[:2]}"
                with self._held_directory(relative_parent, create=True) as (_destination_parent, destination_fd):
                    with self._thread_lock, self._store_file_lock("cas.lock"):
                        existing_usage = self._cas_usage()
                        if self._member_exists(destination, destination_fd):
                            existing = self._read_member(
                                destination,
                                destination_fd,
                                maximum_bytes=maximum_bytes,
                                reason_code="CAS_OBJECT_CONFLICT",
                            )
                            if len(existing) != count or hashlib.sha256(existing).hexdigest() != actual or existing != reread:
                                raise _bounded_error("CAS_OBJECT_CONFLICT", "Existing CAS object conflicts")
                            return actual, count
                        if existing_usage + count > self.max_cas_bytes:
                            raise _bounded_error("CAS_QUOTA_EXCEEDED", "CAS quota would be exceeded")
                        try:
                            if os.name == "nt":
                                os.link(temporary, destination, follow_symlinks=False)
                            else:
                                os.link(
                                    temporary.name,
                                    destination.name,
                                    src_dir_fd=tmp_fd,
                                    dst_dir_fd=destination_fd,
                                    follow_symlinks=False,
                                )
                        except FileExistsError:
                            existing = self._read_member(
                                destination,
                                destination_fd,
                                maximum_bytes=maximum_bytes,
                                reason_code="CAS_OBJECT_CONFLICT",
                            )
                            if existing != reread:
                                raise _bounded_error("CAS_OBJECT_CONFLICT", "Concurrent CAS object conflicts")
                        except OSError:
                            raise _bounded_error("CAS_OBJECT_CONFLICT", "Atomic no-overwrite publication is unavailable") from None
                        self._unlink_member(temporary, tmp_fd)
                        published = self._stat_member(destination, destination_fd)
                        if not stat.S_ISREG(published.st_mode) or published.st_nlink != 1 or _is_reparse_stat(published):
                            raise _bounded_error("CAS_OBJECT_CONFLICT", "Published CAS object metadata is invalid")
                        if os.name != "nt":
                            os.chmod(
                                destination.name,
                                0o600,
                                dir_fd=destination_fd,
                                follow_symlinks=False,
                            )
                self.read_blob(actual, maximum_bytes=maximum_bytes)
                return actual, count
            finally:
                self._unlink_member(temporary, tmp_fd)

    def read_blob(self, digest: str, *, maximum_bytes: int) -> bytes:
        self._require_integrity()
        path = self._object_path(digest)
        with self._held_directory(f"objects/sha256/{digest[:2]}") as (_directory, directory_fd):
            raw = self._read_member(
                path,
                directory_fd,
                maximum_bytes=maximum_bytes,
                reason_code="CAS_OBJECT_CONFLICT",
            )
        if hashlib.sha256(raw).hexdigest() != digest:
            raise _bounded_error("CAS_OBJECT_CONFLICT", "CAS object digest is invalid")
        return raw

    def _publish_record(
        self,
        relative: str,
        payload: Mapping[str, Any],
        *,
        maximum_bytes: int,
        writer_token: object,
    ) -> Path:
        """Publish through one module-held, namespace-limited writer capability."""
        self._require_integrity()
        parts = self._record_parts(relative)
        if type(payload) is not dict:
            raise _bounded_error("POLICY_SCHEMA_INVALID", "Record must be an exact object")
        allowed = _RECORD_WRITER_SCHEMAS.get(writer_token)
        if allowed is None or payload.get("schema_version") not in allowed.get(parts[0], ()):
            raise _bounded_error("CAS_ROOT_INVALID", "Record publication authority is unavailable")
        self._validate_record_binding(parts, payload)
        raw = canonical_json_bytes(payload, maximum_bytes=maximum_bytes)
        destination = self.root.joinpath(*parts)
        temporary = self.root / "tmp" / f"{uuid.uuid4().hex}.record"
        return self._put_record_staged(
            temporary,
            destination,
            raw,
            record_parts=parts,
            relative_parent="/".join(parts[:-1]),
            maximum_bytes=maximum_bytes,
            writer_token=writer_token,
        )

    def _put_record_staged(
        self,
        temporary: Path,
        destination: Path,
        raw: bytes,
        *,
        record_parts: tuple[str, ...],
        relative_parent: str,
        maximum_bytes: int,
        writer_token: object,
    ) -> Path:
        # Repeat the capability, locator, schema, and canonical-byte checks at
        # the lowest publication primitive.  This prevents a caller from
        # bypassing _publish_record and treating the staging helper as a
        # general filesystem write capability.
        self._require_integrity()
        allowed = _RECORD_WRITER_SCHEMAS.get(writer_token)
        if (
            type(record_parts) is not tuple
            or not record_parts
            or allowed is None
            or record_parts[0] not in allowed
            or self._record_parts("/".join(record_parts)) != record_parts
            or destination != self.root.joinpath(*record_parts)
            or relative_parent != "/".join(record_parts[:-1])
            or temporary.parent != self.root / "tmp"
            or not re.fullmatch(r"[0-9a-f]{32}\.record", temporary.name)
            or type(raw) is not bytes
            or not 0 < len(raw) <= maximum_bytes
        ):
            raise _bounded_error("CAS_ROOT_INVALID", "Record staging authority is unavailable")
        payload = parse_json_bytes(
            raw,
            maximum_bytes=maximum_bytes,
            label="quarantine record publication",
        )
        if type(payload) is not dict:
            raise _bounded_error("POLICY_SCHEMA_INVALID", "Record must be an exact object")
        if payload.get("schema_version") not in allowed.get(record_parts[0], ()):
            raise _bounded_error("CAS_ROOT_INVALID", "Record staging authority is unavailable")
        self._validate_record_binding(record_parts, payload)
        if raw != canonical_json_bytes(payload, maximum_bytes=maximum_bytes):
            raise _bounded_error("POLICY_SCHEMA_INVALID", "Record bytes are not canonical")
        with self._held_directory("tmp") as (_tmp_directory, tmp_fd):
            try:
                descriptor = self._open_created(temporary, tmp_fd)
                try:
                    _write_all(descriptor, raw)
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
                with self._held_directory(relative_parent, create=True) as (
                    _destination_parent,
                    destination_fd,
                ):
                    if self._member_exists(destination, destination_fd):
                        current = self._read_member(
                            destination,
                            destination_fd,
                            maximum_bytes=maximum_bytes,
                            reason_code="CAS_OBJECT_CONFLICT",
                        )
                        if current != raw:
                            raise _bounded_error(
                                "CAS_OBJECT_CONFLICT", "Immutable record already has different bytes"
                            )
                        return destination
                    try:
                        if os.name == "nt":
                            os.link(temporary, destination, follow_symlinks=False)
                        else:
                            os.link(
                                temporary.name,
                                destination.name,
                                src_dir_fd=tmp_fd,
                                dst_dir_fd=destination_fd,
                                follow_symlinks=False,
                            )
                    except FileExistsError:
                        current = self._read_member(
                            destination,
                            destination_fd,
                            maximum_bytes=maximum_bytes,
                            reason_code="CAS_OBJECT_CONFLICT",
                        )
                        if current != raw:
                            raise _bounded_error(
                                "CAS_OBJECT_CONFLICT", "Concurrent immutable record conflicts"
                            )
                    except OSError:
                        raise _bounded_error(
                            "CAS_OBJECT_CONFLICT", "Atomic record publication is unavailable"
                        ) from None
                    self._unlink_member(temporary, tmp_fd)
                    published = self._stat_member(destination, destination_fd)
                    if (
                        not stat.S_ISREG(published.st_mode)
                        or published.st_nlink != 1
                        or _is_reparse_stat(published)
                    ):
                        raise _bounded_error(
                            "CAS_OBJECT_CONFLICT", "Published record metadata is invalid"
                        )
                self._require_integrity()
                return destination
            finally:
                self._unlink_member(temporary, tmp_fd)

    def read_record(self, relative: str, *, maximum_bytes: int) -> dict[str, Any]:
        self._require_integrity()
        parts = self._record_parts(relative)
        path = self.root.joinpath(*parts)
        with self._held_directory("/".join(parts[:-1])) as (_directory, directory_fd):
            raw = self._read_member(
                path,
                directory_fd,
                maximum_bytes=maximum_bytes,
                reason_code="CAS_OBJECT_CONFLICT",
            )
        value = parse_json_bytes(
            raw,
            maximum_bytes=maximum_bytes,
            label="quarantine record",
        )
        if type(value) is not dict:
            raise _bounded_error("CAS_OBJECT_CONFLICT", "Quarantine record is not an object")
        try:
            self._validate_record_binding(parts, value)
        except EcosystemError:
            raise _bounded_error(
                "CAS_OBJECT_CONFLICT", "Quarantine record binding is invalid"
            ) from None
        return value

    def list_record_names(
        self,
        relative: str,
        *,
        maximum_count: int,
        create: bool = False,
        writer_token: object | None = None,
    ) -> tuple[str, ...]:
        """List one immutable digest-named record namespace through held handles."""
        self._require_integrity()
        if type(maximum_count) is not int or maximum_count <= 0 or type(create) is not bool:
            raise _bounded_error("RESOURCE_LIMIT_EXCEEDED", "Record listing bound is invalid")
        parts = self._listing_parts(relative)
        if create:
            allowed = _RECORD_WRITER_SCHEMAS.get(writer_token)
            if allowed is None or parts[0] not in allowed:
                raise _bounded_error("CAS_ROOT_INVALID", "Record namespace creation is unauthorized")
        with self._held_directory("/".join(parts), create=create) as (directory, directory_fd):
            with os.scandir(directory if os.name == "nt" else directory_fd) as candidates:
                names = sorted(item.name for item in candidates)
            if len(names) > maximum_count:
                raise _bounded_error("RESOURCE_LIMIT_EXCEEDED", "Record namespace exceeds its bound")
            for name in names:
                if not re.fullmatch(r"[0-9a-f]{64}\.json", name):
                    raise _bounded_error("CAS_OBJECT_CONFLICT", "Record namespace is unsafe")
                info = self._stat_member(directory / name, directory_fd)
                if (
                    not stat.S_ISREG(info.st_mode)
                    or info.st_nlink != 1
                    or _is_reparse_stat(info)
                ):
                    raise _bounded_error("CAS_OBJECT_CONFLICT", "Record namespace member is unsafe")
            return tuple(names)

    def _ensure_revision_capacity(
        self,
        *,
        source_id: str,
        revision_id: str,
        policy: Any,
        writer_token: object,
    ) -> None:
        """Fail before publishing a ninth quarantined revision for one source."""
        if writer_token is not _INTAKE_RECORD_WRITER:
            raise _bounded_error("CAS_ROOT_INVALID", "Revision capacity authority is unavailable")
        self._require_policy(policy)

        validate_typed_id(source_id, "source")
        validate_typed_id(revision_id, "revision")
        maximum_count = policy.resource_limits["max_quarantined_revisions_per_source"]
        maximum_record_bytes = policy.resource_limits["max_record_bytes"]
        target_digest = revision_id.split("/", 1)[1]
        seen: set[str] = set()
        with self._held_directory("quarantine") as (quarantine, quarantine_fd):
            with os.scandir(quarantine if os.name == "nt" else quarantine_fd) as candidates:
                names = sorted(item.name for item in candidates)
            for name in names:
                if not re.fullmatch(r"[0-9a-f]{64}\.json", name):
                    raise _bounded_error("CAS_OBJECT_CONFLICT", "Quarantine namespace is unsafe")
                path = quarantine / name
                raw = self._read_member(
                    path,
                    quarantine_fd,
                    maximum_bytes=maximum_record_bytes,
                    reason_code="CAS_OBJECT_CONFLICT",
                )
                record = parse_json_bytes(
                    raw, maximum_bytes=maximum_record_bytes, label="quarantine view"
                )
                if type(record) is not dict or set(record) != {
                    "schema_version",
                    "revision_id",
                    "source_id",
                    "genesis_state_record_id",
                    "initial_disposition",
                    "authority",
                }:
                    raise _bounded_error("CAS_OBJECT_CONFLICT", "Quarantine view is malformed")
                if (
                    record["schema_version"] != "nexus.ecosystem-quarantine-view.v1"
                    or record["initial_disposition"] != "QUARANTINED"
                    or name[:-5] != record["revision_id"].split("/", 1)[-1]
                ):
                    raise _bounded_error("CAS_OBJECT_CONFLICT", "Quarantine view is inconsistent")
                validate_typed_id(record["revision_id"], "revision")
                validate_typed_id(record["source_id"], "source")
                validate_typed_id(record["genesis_state_record_id"], "state-record")
                from .ecosystem_models import validate_authority

                validate_authority(record["authority"])
                if record["source_id"] == source_id:
                    seen.add(record["revision_id"])
        if revision_id not in seen and len(seen) >= maximum_count:
            raise _bounded_error("RESOURCE_LIMIT_EXCEEDED", "Source revision quarantine limit is reached")
        if target_digest in {item.split("/", 1)[1] for item in seen} and revision_id not in seen:
            raise _bounded_error("CAS_OBJECT_CONFLICT", "Quarantine revision digest conflicts")


def _module_repository_root() -> Path:
    """Return the installed Nexus repository/release root without caller input."""
    return Path(os.path.abspath(Path(__file__).parent.parent))


def _production_store_root() -> Path:
    operating_system, _platform = _runtime_platform_identity()
    if operating_system == "nt":
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            raise _bounded_error("CAS_ROOT_INVALID", "LOCALAPPDATA is unavailable")
        return Path(local) / "Nexus" / "ecosystem" / "v1"
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    if not base.is_absolute():
        raise _bounded_error("CAS_ROOT_INVALID", "Per-user data root is not absolute")
    return base / "nexus" / "ecosystem" / "v1"


def _construct_store(
    root: Path,
    *,
    policy: Any,
    max_cas_bytes: int,
    construction_mode: str,
) -> QuarantineStore:
    try:
        from .ecosystem_policy import (
            _HERMETIC_TEST_TRUST_MODE,
            _require_production_source_policy,
            _require_trusted_source_policy,
        )

        trusted = _require_trusted_source_policy(policy)
        if construction_mode == "production":
            trusted = _require_production_source_policy(trusted)
        elif construction_mode == "hermetic_test":
            if trusted._trust_mode != _HERMETIC_TEST_TRUST_MODE:
                raise _bounded_error(
                    "POLICY_UNTRUSTED", "Hermetic store requires a hermetic fixture policy"
                )
        else:
            raise _bounded_error("CAS_ROOT_INVALID", "Quarantine store mode is invalid")
    except (ImportError, AttributeError, TypeError, EcosystemError):
        raise _bounded_error("POLICY_UNTRUSTED", "Trusted store policy is unavailable") from None
    if (
        type(max_cas_bytes) is not int
        or max_cas_bytes <= 0
        or max_cas_bytes > trusted.resource_limits["max_cas_bytes"]
    ):
        raise _bounded_error("CAS_ROOT_INVALID", "CAS byte ceiling exceeds trusted policy")
    return QuarantineStore(
        root,
        repository_root=_module_repository_root(),
        max_cas_bytes=max_cas_bytes,
        policy_semantic_sha256=trusted.policy_semantic_sha256,
        integrity_manifest_sha256=trusted.integrity_manifest_sha256,
        policy_trust_mode=trusted._trust_mode,
        policy_repository_root=trusted._repository_root,
        construction_mode=construction_mode,
        token=_STORE_CONSTRUCTION_TOKEN,
    )


def open_quarantine_store(*, policy: Any) -> QuarantineStore:
    """Open the fixed production per-user quarantine root under trusted policy."""
    try:
        maximum = policy.resource_limits["max_cas_bytes"]
    except (AttributeError, KeyError, TypeError):
        raise _bounded_error("POLICY_UNTRUSTED", "Trusted store policy is unavailable") from None
    return _construct_store(
        _production_store_root(),
        policy=policy,
        max_cas_bytes=maximum,
        construction_mode="production",
    )


def _open_test_quarantine_store(
    root: Path,
    *,
    policy: Any,
    max_cas_bytes: int | None = None,
) -> QuarantineStore:
    """Private hermetic seam: only the external root/quota may be narrowed."""
    try:
        policy_maximum = policy.resource_limits["max_cas_bytes"]
    except (AttributeError, KeyError, TypeError):
        raise _bounded_error("POLICY_UNTRUSTED", "Trusted store policy is unavailable") from None
    return _construct_store(
        root,
        policy=policy,
        max_cas_bytes=policy_maximum if max_cas_bytes is None else max_cas_bytes,
        construction_mode="hermetic_test",
    )
