"""Bounded inert reference metadata. Reads during planning; explicit Host writes only.

This is not a Skill catalog, execution authority, network client or Project Memory.
The library is same-user local data; approval receipts are provenance, not signatures.
"""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Callable
from urllib.parse import urlsplit, urlunsplit

from .common import tokenize

SCHEMA = "nexus.reusable-reference-library.v1"
MAX_RECORDS = 256
MAX_BYTES = 1024 * 1024
MAX_RECORD_BYTES = 4096
MAX_DISCOVERY_BYTES = 8 * 1024
ID = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
ROLES = {"official_documentation", "mature_project", "alternative_implementation",
         "design_reference", "interaction_reference", "engineering_reference"}
REQUIRED_ROLES = ("official_documentation", "mature_project", "alternative_implementation")
STACK_FAMILIES = ({"react", "vue", "angular", "svelte"}, {"django", "flask", "fastapi", "laravel"})
FIELDS = {"id", "name", "url", "revision", "tags", "use_for", "patterns", "avoid_for", "roles",
          "workspace", "acceptance", "approval_evidence", "license", "license_evidence", "reuse",
          "last_checked_at", "compatibility", "provenance"}
ALIASES = {"网站": "website", "网页": "website", "应用": "application", "设计": "design",
           "重构": "refactor", "报表": "reporting", "安全": "security", "接口": "api",
           "交互": "interaction", "工程": "engineering", "修复": "fix", "功能": "feature"}


class LibraryError(ValueError):
    """Invalid local metadata; never include raw source text or paths in errors."""


@dataclass(frozen=True)
class LibrarySnapshot:
    status: str
    records: tuple[dict, ...] = ()
    sha256: str | None = None


def workspace_binding(root: Path) -> str:
    return hashlib.sha256(os.path.normcase(str(root.resolve())).encode("utf-8")).hexdigest()


def local_data_root() -> Path:
    explicit = os.environ.get("NEXUS_DATA_ROOT")
    if explicit:
        return Path(explicit)
    local = os.environ.get("LOCALAPPDATA")
    return Path(local) / "Nexus" if local else Path.home() / ".nexus"


def _text(value: object, limit: int = 512) -> str:
    if not isinstance(value, str) or len(value.encode("utf-8")) > limit or any(ord(c) < 32 for c in value):
        raise LibraryError("invalid_text")
    if re.search(r"(?i)(?:password|secret|token|api[_-]?key|credential)\s*[:=]", value):
        raise LibraryError("secret_like_metadata")
    if re.search(r"(?:^|\s)(?:[A-Za-z]:[\\/]|\\\\|/(?:home|Users|etc|tmp)/)", value):
        raise LibraryError("private_path_metadata")
    return value


def public_url(value: object) -> str:
    text = _text(value)
    try:
        parsed = urlsplit(text)
        host = parsed.hostname
        if (parsed.scheme != "https" or not host or parsed.username or parsed.password
                or parsed.port not in (None, 443) or parsed.query or "\\" in text or "%" in text):
            raise LibraryError("invalid_public_url")
        if "." not in host or host.endswith((".local", ".localhost", ".internal", ".test", ".invalid")):
            raise LibraryError("non_public_url")
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
        if address is not None and not address.is_global:
            raise LibraryError("non_public_url")
        return urlunsplit(("https", host.lower(), parsed.path.rstrip("/"), "", ""))
    except (ValueError, UnicodeError) as exc:
        raise LibraryError("invalid_public_url") from exc


def _strings(value: object, maximum: int = 12) -> list[str]:
    if not isinstance(value, list) or len(value) > maximum:
        raise LibraryError("invalid_list")
    return [_text(item, 64) for item in value]


def _timestamp(value: object) -> datetime | None:
    if value is None:
        return None
    try:
        result = datetime.fromisoformat(_text(value, 40).replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError()
        return result
    except ValueError as exc:
        raise LibraryError("invalid_check_time") from exc


def validate_record(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise LibraryError("invalid_record_fields")
    if len(json.dumps(value, ensure_ascii=False).encode("utf-8")) > MAX_RECORD_BYTES:
        raise LibraryError("record_limit")
    item = dict(value)
    if not isinstance(item["id"], str) or not ID.fullmatch(item["id"]):
        raise LibraryError("invalid_id")
    for key in ("name", "revision", "use_for", "patterns", "avoid_for", "provenance", "approval_evidence"):
        item[key] = _text(item[key], 128 if key in {"name", "revision"} else 512)
    if not item["name"] or not item["provenance"]:
        raise LibraryError("missing_provenance")
    item["url"] = public_url(item["url"])
    item["tags"] = _strings(item["tags"])
    item["roles"] = _strings(item["roles"], 6)
    if not set(item["roles"]) <= ROLES:
        raise LibraryError("invalid_role")
    if item["workspace"] != "shared" and not re.fullmatch(r"[a-f0-9]{64}", str(item["workspace"])):
        raise LibraryError("invalid_scope")
    if item["acceptance"] not in {"accepted", "preferred", "rejected"}:
        raise LibraryError("invalid_acceptance")
    if item["acceptance"] == "preferred" and not item["approval_evidence"]:
        raise LibraryError("preference_requires_explicit_evidence")
    if item["workspace"] == "shared" and not item["approval_evidence"]:
        raise LibraryError("shared_scope_requires_explicit_evidence")
    if item["license"] not in {"unknown", "compatible", "restricted", "incompatible"}:
        raise LibraryError("invalid_license")
    if item["reuse"] not in {"patterns_only", "conditional_code_reuse", "no_reuse"}:
        raise LibraryError("invalid_reuse")
    if item["compatibility"] not in {"compatible", "unknown", "incompatible"}:
        raise LibraryError("invalid_compatibility")
    item["license_evidence"] = public_url(item["license_evidence"]) if item["license_evidence"] else ""
    if item["reuse"] == "conditional_code_reuse" and (item["license"] != "compatible" or not item["license_evidence"]):
        raise LibraryError("unproven_code_reuse")
    _timestamp(item["last_checked_at"])
    return item


def validate_library(value: object) -> tuple[dict, ...]:
    if not isinstance(value, dict) or set(value) != {"schema_version", "records"} or value["schema_version"] != SCHEMA:
        raise LibraryError("invalid_library_schema")
    records = value["records"]
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise LibraryError("record_count_limit")
    result = tuple(validate_record(item) for item in records)
    if len({item["id"] for item in result}) != len(result):
        raise LibraryError("duplicate_id")
    return result


def _closed_json(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise LibraryError("duplicate_json_field")
        result[key] = value
    return result


def load_library(data_root: Path | None = None) -> LibrarySnapshot:
    """Read exactly one bounded file; no mkdir, writes, timestamps or network."""
    from .mcp.authorization import _canonical_root, guard_regular_file, verify_unchanged
    from .mcp.schemas import NexusMcpError
    root = data_root if data_root is not None else local_data_root()
    try:
        # Validate ancestors before any lookup through them: even an existence
        # probe must not traverse a junction to an SMB/network destination.
        root = _canonical_root(root)
        directory = root / "references"
        if not os.path.lexists(directory):
            return LibrarySnapshot("unavailable")
        directory = _canonical_root(directory)
        path = directory / "library.json"
        if not os.path.lexists(path):
            return LibrarySnapshot("unavailable")
        guarded, before = guard_regular_file(path, [root])
        if before.st_size > MAX_BYTES:
            return LibrarySnapshot("oversized")
        with guarded.open("rb") as handle:
            opened = os.fstat(handle.fileno())
            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                raise LibraryError("unstable_input")
            raw = handle.read(MAX_BYTES + 1)
        verify_unchanged(guarded, before)
        guard_regular_file(path, [root])
        if len(raw) > MAX_BYTES:
            return LibrarySnapshot("oversized")
        records = validate_library(json.loads(raw, object_pairs_hook=_closed_json))
        return LibrarySnapshot("loaded" if records else "empty", records, hashlib.sha256(raw).hexdigest())
    except (OSError, ValueError, TypeError, RecursionError, NexusMcpError):
        return LibrarySnapshot("invalid")


def _tokens(text: str) -> set[str]:
    result = tokenize(text)
    result.update(word for chinese, word in ALIASES.items() if chinese in text)
    return result - {"new", "create", "build", "make", "project", "please"}


def discover_references(task: str, plan, workspace: Path, *, hold: bool = False,
                        reader: Callable[[], LibrarySnapshot] | None = None,
                        now: datetime | None = None) -> dict:
    """Consume the shared work classification; references never affect coverage."""
    result = {"schema_version": "nexus.reusable-reference-discovery.v1", "status": "skipped",
              "work_category": plan.work_category, "library_status": "not_read", "matches": [],
              "research_gaps": [], "fresh_candidate_budget": 0, "total_candidate_limit": plan.candidate_limit,
              "fresh_query_limit": 3, "fresh_time_limit_seconds": 120,
              "authority": "none", "content_trust": "untrusted_reference_data"}
    if hold:
        result["status"] = "HOLD_owner_decision"
        return result
    if plan.status == "skipped" or plan.work_category == "none":
        return result
    try:
        snapshot = (reader or load_library)()
    except (OSError, LibraryError):
        snapshot = LibrarySnapshot("unavailable")
    result["library_status"] = snapshot.status
    now = now or datetime.now(timezone.utc)
    scope = workspace_binding(workspace)
    groups: dict[str, list[dict]] = {}
    # Revalidate even injected snapshots: no unchecked metadata crosses the handoff.
    try:
        records = validate_library({"schema_version": SCHEMA, "records": list(snapshot.records)})
    except (ValueError, TypeError):
        records = ()
        result["library_status"] = "invalid"
    for item in records:
        if item["workspace"] in {scope, "shared"}:
            groups.setdefault(item["url"], []).append(item)
    ranked = []
    task_tokens = _tokens(task)
    for url, items in groups.items():
        # Conflicting duplicate restrictions must not be bypassed by preference.
        if any(r["acceptance"] == "rejected" or r["compatibility"] == "incompatible"
               or r["license"] == "incompatible" or r["reuse"] == "no_reuse" for r in items):
            continue
        if len({(r["license"], r["reuse"], r["revision"]) for r in items}) > 1:
            continue
        for item in items:
            reference_tokens = _tokens(" ".join(item["tags"]) + " " + item["use_for"])
            if any(task_tokens & family and reference_tokens & family
                   and not task_tokens & reference_tokens & family for family in STACK_FAMILIES):
                continue
            overlap = sorted(task_tokens & reference_tokens)
            if not overlap:
                continue
            if plan.status == "reduced" and not ("official_documentation" in item["roles"]
                    or set(overlap) & {"compatibility", "implementation", "security", "risk", "api"}):
                continue
            observed = _timestamp(item["last_checked_at"])
            current = observed is not None and now - timedelta(days=30) <= observed <= now
            preference = item["acceptance"] == "preferred"
            match = {k: item[k] for k in ("id", "name", "url", "revision", "use_for", "patterns", "avoid_for", "roles", "license", "license_evidence", "approval_evidence", "provenance", "last_checked_at", "compatibility")}
            match.update(score=len(overlap) * 10 + int(preference) * 2 + int(current),
                         match_reasons=["task_overlap:" + word for word in overlap[:12]],
                         preferred=preference, needs_revalidation=not current,
                         reuse="patterns_only" if not current or item["compatibility"] != "compatible" else item["reuse"])
            if preference:
                match["match_reasons"].append("explicit_user_preference")
            ranked.append(match)
    ranked.sort(key=lambda r: (-r["score"], r["url"], r["id"]))
    chosen = []
    seen = set()
    for item in ranked:
        if item["url"] not in seen:
            chosen.append(item)
            seen.add(item["url"])
    chosen = chosen[:plan.candidate_limit]
    def gaps():
        # A source can fill only one comparison role. Tiny bounded matching
        # prevents one multi-tagged URL from impersonating a multi-source set.
        def assign(position, used):
            if position == len(REQUIRED_ROLES):
                return []
            role = REQUIRED_ROLES[position]
            options = [[role, *assign(position + 1, used)]]
            for index, item in enumerate(chosen):
                if index not in used and role in item["roles"]:
                    options.append(assign(position + 1, used | {index}))
            return min(options, key=lambda value: (len(value), tuple(value)))
        missing = (["targeted_compatibility_implementation_risk"] if plan.status == "reduced" and not chosen
                   else [] if plan.status == "reduced" else assign(0, set()))
        if any(item["needs_revalidation"] for item in chosen):
            missing.append("revalidate_known_references")
        return missing
    while chosen and len(chosen) + len(gaps()) > plan.candidate_limit:
        chosen.pop()
    while chosen and len(json.dumps(chosen, ensure_ascii=False).encode("utf-8")) > MAX_DISCOVERY_BYTES:
        chosen.pop()
    missing = gaps()
    result.update(status="library_matches" if chosen else "no_library_match", matches=chosen,
                  research_gaps=missing,
                  fresh_candidate_budget=plan.candidate_limit - len(chosen) if missing else 0)
    result["sufficiency"] = "advisory_host_must_verify_and_synthesize"
    return result


@contextmanager
def _host_lock(path: Path):
    handle = path.open("xb")
    try:
        yield
    finally:
        handle.close()
        path.unlink()


def host_upsert(record: dict, *, authorized: bool, expected_sha256: str | None,
                data_root: Path | None = None) -> str:
    """Explicit same-user Host enrollment; no MCP tool or completion hook calls this.

    Caller supplies provenance and explicit preference/shared-scope evidence, never
    inferred by this API. expected_sha256=None permits initial creation only.
    """
    from .mcp.authorization import _canonical_root, guard_regular_file
    if authorized is not True:
        raise LibraryError("host_authorization_required")
    item = validate_record(record)
    root = _canonical_root(data_root if data_root is not None else local_data_root())
    directory = root / "references"
    if os.path.lexists(directory):
        _canonical_root(directory)
    else:
        directory.mkdir()
    _canonical_root(directory)
    target = directory / "library.json"
    lock = directory / ".enrollment.lock"
    # Exclusive cooperating-writer lock; never remove an existing writer's lock.
    with _host_lock(lock):
        old = load_library(root)
        if old.status not in {"loaded", "empty", "unavailable"} or old.sha256 != expected_sha256:
            raise LibraryError("library_changed_or_invalid")
        records = {r["id"]: r for r in old.records}
        records[item["id"]] = item
        payload = {"schema_version": SCHEMA, "records": [records[key] for key in sorted(records)]}
        validate_library(payload)
        raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if len(raw) > MAX_BYTES:
            raise LibraryError("library_size_limit")
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=directory, prefix=".reference-", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            _canonical_root(directory)
            if os.path.lexists(target):
                guard_regular_file(target, [root])
            if load_library(root).sha256 != expected_sha256:
                raise LibraryError("library_changed")
            os.replace(temporary, target)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return hashlib.sha256(raw).hexdigest()
