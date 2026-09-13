"""Deterministic, zero-authority Slice 3C revision comparison.

The comparison engine consumes only already quarantined, integrity-bound
records and inert CAS bytes.  It does not acquire, execute, install, route, or
promote candidate content.
"""
from __future__ import annotations

import hashlib
from pathlib import PurePosixPath
from typing import Any, Mapping

from .ecosystem_evidence import (
    _DEPENDENCY_BASENAMES,
    _BIDI_CONTROLS,
    _read_entry,
    _secret_match,
    _text_tokens,
    _validate_authoritative_revision_snapshot,
    _validate_component_record,
    _validate_revision,
    _validate_tree,
    validate_component_classification,
    validate_license_evidence,
    validate_provenance_evidence,
)
from .ecosystem_models import (
    EcosystemError,
    canonical_json_bytes,
    canonical_sha256,
    typed_id,
    validate_authority,
    validate_exact_keys,
    validate_reason_codes,
    validate_sha256,
    validate_typed_id,
    zero_authority,
)
from .ecosystem_policy import TrustedEcosystemSourcePolicy, _require_trusted_source_policy
from .ecosystem_storage import QuarantineStore, _COMPARISON_RECORD_WRITER


COMPARISON_SCHEMA_VERSION = "nexus.ecosystem-revision-comparison.v1"
COMPARISON_ALGORITHM_ID = "nexus.ecosystem-revision-comparison"
COMPARISON_ALGORITHM_VERSION = "1"
_ANCESTRY_STATES = {"SAME", "FAST_FORWARD", "REWIND", "DIVERGED", "UNKNOWN"}
_RESULTS = {
    "NO_TREE_CHANGE",
    "CHANGED",
    "SECURITY_SENSITIVE_CHANGE",
    "INCOMPARABLE",
    "INSUFFICIENT_EVIDENCE",
}
_SECURITY_CODES = {
    "BINARY_ADDED",
    "COMPONENT_ADDED",
    "COMPONENT_CHANGED",
    "COMPONENT_REMOVED",
    "COMPONENT_ROOT_CHANGED",
    "DEPENDENCY_ADDED",
    "DEPENDENCY_CHANGED",
    "DEPENDENCY_REMOVED",
    "EXECUTABLE_ADDED",
    "FILE_ADDED",
    "FILE_CONTENT_CHANGED",
    "FILE_MODE_CHANGED",
    "FILE_REMOVED",
    "FILE_TYPE_CHANGED",
    "HOOK_OR_INSTALLER_CHANGED",
    "LICENSE_ADDED",
    "LICENSE_CHANGED",
    "LICENSE_REMOVED",
    "LINK_OR_SPECIAL_FILE_CHANGED",
    "LOCKFILE_CHANGED",
    "NETWORK_OR_CREDENTIAL_CHANGED",
    "PERMISSION_CHANGED",
    "POLICY_RELEVANT_FILE_CHANGED",
    "PROVENANCE_CHANGED",
    "SIGNATURE_OR_ATTESTATION_CHANGED",
    "SKILL_OR_AGENT_INSTRUCTION_CHANGED",
    "UNSUPPORTED_CONTENT_CHANGED",
    "WORKFLOW_CHANGED",
}
_SENSITIVE_CODES = _SECURITY_CODES - {
    "FILE_ADDED",
    "FILE_CONTENT_CHANGED",
    "FILE_MODE_CHANGED",
    "FILE_REMOVED",
    "FILE_TYPE_CHANGED",
    "COMPONENT_ADDED",
    "COMPONENT_CHANGED",
    "COMPONENT_REMOVED",
}
_LOCKFILES = {
    "Cargo.lock",
    "Gemfile.lock",
    "go.sum",
    "package-lock.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    "yarn.lock",
}
_LICENSE_PREFIXES = ("license", "licence", "copying", "notice")
_EXECUTABLE_MAGIC = (
    b"\x00asm",
    b"MZ",
    b"\x7fELF",
    b"\xca\xfe\xba\xbe",
    b"\xce\xfa\xed\xfe",
    b"\xcf\xfa\xed\xfe",
    b"\xfe\xed\xfa\xce",
    b"\xfe\xed\xfa\xcf",
)
_COMPARISON_FIELDS = {
    "schema_version",
    "comparison_id",
    "source_id",
    "old_revision_id",
    "new_revision_id",
    "old_tree_id",
    "new_tree_id",
    "comparison_policy_semantic_sha256",
    "ancestry_state",
    "added_path_sha256s",
    "removed_path_sha256s",
    "modified_path_sha256s",
    "type_changed_path_sha256s",
    "mode_changed_path_sha256s",
    "component_changes",
    "license_changes",
    "dependency_changes",
    "security_change_codes",
    "comparison_result",
    "algorithm_id",
    "algorithm_version",
    "reason_codes",
    "authority",
}


def _path_sha256(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8")).hexdigest()


def _validate_role_file_limits(
    entries: list[dict[str, Any]], policy: TrustedEcosystemSourcePolicy
) -> None:
    """Apply policy ceilings before comparison reads role-sensitive bytes."""
    dependency_count = 0
    license_count = 0
    maximum_role_bytes = policy.resource_limits[
        "max_license_or_dependency_file_bytes"
    ]
    for entry in entries:
        basename = PurePosixPath(entry["path"]).name
        is_dependency = basename in _DEPENDENCY_BASENAMES
        is_license = basename.casefold().startswith(_LICENSE_PREFIXES)
        if is_dependency:
            dependency_count += 1
        if is_license:
            license_count += 1
        if (is_dependency or is_license) and entry["size"] > maximum_role_bytes:
            raise EcosystemError(
                "RESOURCE_LIMIT_EXCEEDED",
                "Comparison role-sensitive file exceeds the policy byte ceiling",
            )
    if dependency_count > policy.resource_limits["max_dependency_manifests"]:
        raise EcosystemError(
            "RESOURCE_LIMIT_EXCEEDED",
            "Comparison dependency-manifest count exceeds policy",
        )
    if license_count > policy.resource_limits["max_license_files"]:
        raise EcosystemError(
            "RESOURCE_LIMIT_EXCEEDED",
            "Comparison license-file count exceeds policy",
        )


def _validate_digest_list(value: Any, maximum: int, label: str) -> list[str]:
    if type(value) is not list:
        raise EcosystemError("PROVENANCE_CONFLICT", f"{label} is not a list")
    if len(value) > maximum:
        raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", f"{label} exceeds its bound")
    checked = [validate_sha256(item, label) for item in value]
    if checked != sorted(set(checked)):
        raise EcosystemError("PROVENANCE_CONFLICT", f"{label} is not canonical")
    return checked


def _validate_change_objects(
    value: Any, *, maximum: int, component: bool, label: str
) -> list[dict[str, Any]]:
    if type(value) is not list:
        raise EcosystemError("PROVENANCE_CONFLICT", f"{label} is not a list")
    if len(value) > maximum:
        raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", f"{label} exceeds its bound")
    fields = (
        {
            "component_id",
            "old_component_revision_id",
            "new_component_revision_id",
            "change_kind",
        }
        if component
        else {"path_sha256", "old_sha256", "new_sha256", "change_kind"}
    )
    checked: list[dict[str, Any]] = []
    for item in value:
        record = validate_exact_keys(item, fields, label)
        if component:
            validate_typed_id(record["component_id"], "component")
            old_value = record["old_component_revision_id"]
            new_value = record["new_component_revision_id"]
            for candidate in (old_value, new_value):
                if candidate is not None:
                    validate_typed_id(candidate, "component-revision")
        else:
            validate_sha256(record["path_sha256"], "comparison path digest")
            old_value = record["old_sha256"]
            new_value = record["new_sha256"]
            for candidate in (old_value, new_value):
                if candidate is not None:
                    validate_sha256(candidate, "comparison content digest")
        kind = record["change_kind"]
        valid_shape = (
            kind == "ADDED" and old_value is None and new_value is not None
        ) or (
            kind == "REMOVED" and old_value is not None and new_value is None
        ) or (
            kind == "MODIFIED"
            and old_value is not None
            and new_value is not None
            and old_value != new_value
        )
        if not valid_shape:
            raise EcosystemError("PROVENANCE_CONFLICT", f"{label} change is invalid")
        checked.append(record)
    if checked != sorted(checked, key=canonical_json_bytes):
        raise EcosystemError("PROVENANCE_CONFLICT", f"{label} is not ordered")
    encoded = [canonical_json_bytes(item) for item in checked]
    if len(encoded) != len(set(encoded)):
        raise EcosystemError("PROVENANCE_CONFLICT", f"{label} contains duplicates")
    return checked


def _canonical_objects(values: list[dict[str, Any]], maximum: int, label: str) -> list[dict[str, Any]]:
    if len(values) > maximum:
        raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", f"{label} exceeds its comparison bound")
    values.sort(key=canonical_json_bytes)
    encoded = [canonical_json_bytes(item) for item in values]
    if len(encoded) != len(set(encoded)):
        raise EcosystemError("PROVENANCE_CONFLICT", f"{label} contains duplicates")
    return values


def _validate_components(
    values: Any,
    *,
    revision: Mapping[str, Any],
    tree: Mapping[str, Any],
    policy: TrustedEcosystemSourcePolicy,
) -> list[dict[str, Any]]:
    if type(values) is not list or len(values) > 256:
        raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", "Component comparison input is unbounded")
    checked = [
        _validate_component_record(item, revision=revision, tree=tree, policy=policy)
        for item in values
    ]
    ids = [item["component_id"] for item in checked]
    if len(ids) != len(set(ids)):
        raise EcosystemError("CLASSIFICATION_CONFLICT", "Component comparison input is duplicated")
    return checked


def _component_changes(
    old: list[dict[str, Any]], new: list[dict[str, Any]], codes: set[str]
) -> list[dict[str, Any]]:
    old_by_id = {item["component_id"]: item for item in old}
    new_by_id = {item["component_id"]: item for item in new}
    changes: list[dict[str, Any]] = []
    for component_id in sorted(set(old_by_id) | set(new_by_id)):
        before = old_by_id.get(component_id)
        after = new_by_id.get(component_id)
        if before is None:
            kind = "ADDED"
            codes.add("COMPONENT_ADDED")
        elif after is None:
            kind = "REMOVED"
            codes.add("COMPONENT_REMOVED")
        elif before["component_revision_id"] != after["component_revision_id"]:
            kind = "MODIFIED"
            codes.add("COMPONENT_CHANGED")
        else:
            continue
        changes.append(
            {
                "component_id": component_id,
                "old_component_revision_id": None if before is None else before["component_revision_id"],
                "new_component_revision_id": None if after is None else after["component_revision_id"],
                "change_kind": kind,
            }
        )
    def relocation_signature(item: Mapping[str, Any]) -> str:
        root = item["component_root"]
        projection = []
        for entry in item["entries"]:
            path = entry["path"]
            relative = "." if path == root else path[len(root) + 1 :]
            projection.append({**entry, "path": relative})
        return canonical_sha256({"entries": projection})

    removed_by_manifest = {
        relocation_signature(item): item
        for item in old
        if item["component_id"] not in new_by_id
    }
    added_by_manifest = {
        relocation_signature(item): item
        for item in new
        if item["component_id"] not in old_by_id
    }
    if set(removed_by_manifest) & set(added_by_manifest):
        codes.add("COMPONENT_ROOT_CHANGED")
    return _canonical_objects(changes, 256, "Component changes")


def _file_evidence_changes(
    old_by_path: Mapping[str, Mapping[str, Any]],
    new_by_path: Mapping[str, Mapping[str, Any]],
    *,
    predicate: Any,
    maximum: int,
) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for path in sorted(set(old_by_path) | set(new_by_path)):
        if not predicate(path):
            continue
        before = old_by_path.get(path)
        after = new_by_path.get(path)
        old_sha = None if before is None else before["sha256"]
        new_sha = None if after is None else after["sha256"]
        if old_sha == new_sha:
            continue
        kind = "ADDED" if before is None else "REMOVED" if after is None else "MODIFIED"
        changes.append(
            {
                "path_sha256": _path_sha256(path),
                "old_sha256": old_sha,
                "new_sha256": new_sha,
                "change_kind": kind,
            }
        )
    return _canonical_objects(changes, maximum, "File evidence changes")


def _text_security(raw: bytes) -> tuple[bool, bool, bool]:
    credential = _secret_match(raw)
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return credential, False, True
    tokens = _text_tokens(text)
    permission = bool(tokens & {"allowed-tools", "delegate", "mcp", "permissions", "shell", "spawn-agent", "subprocess", "sudo"})
    network = credential or any(scheme in text.casefold() for scheme in ("http://", "https://", "ws://", "wss://")) or bool(tokens & {"fetch", "requests", "socket", "urllib", "webhook"})
    unsupported = "\x00" in text or any(char in _BIDI_CONTROLS for char in text)
    return network, permission, unsupported


def _path_security_codes(
    path: str,
    before: Mapping[str, Any] | None,
    after: Mapping[str, Any] | None,
    old_raw: bytes | None,
    new_raw: bytes | None,
) -> set[str]:
    result: set[str] = set()
    pure = PurePosixPath(path)
    basename = pure.name
    folded = path.casefold()
    if basename in _DEPENDENCY_BASENAMES:
        result.add("DEPENDENCY_ADDED" if before is None else "DEPENDENCY_REMOVED" if after is None else "DEPENDENCY_CHANGED")
        result.add("POLICY_RELEVANT_FILE_CHANGED")
    if basename in _LOCKFILES:
        result.add("LOCKFILE_CHANGED")
    if basename.casefold().startswith(_LICENSE_PREFIXES):
        result.add("LICENSE_ADDED" if before is None else "LICENSE_REMOVED" if after is None else "LICENSE_CHANGED")
        result.add("POLICY_RELEVANT_FILE_CHANGED")
    if (
        folded.startswith(".github/workflows/")
        or path in {".circleci/config.yml", ".gitlab-ci.yml", "Jenkinsfile"}
    ):
        result.update({"WORKFLOW_CHANGED", "POLICY_RELEVANT_FILE_CHANGED"})
    if (
        path in {".gitattributes", ".gitmodules", "install.py", "bootstrap.py"}
        or folded.startswith(".git/hooks/")
        or basename == "pyproject.toml"
        or basename == "package.json"
    ):
        result.update({"HOOK_OR_INSTALLER_CHANGED", "POLICY_RELEVANT_FILE_CHANGED"})
    if basename in {"SKILL.md", "AGENTS.md"} or (
        pure.parts and pure.parts[0].casefold() in {"agents", ".agents"}
    ):
        result.update({"SKILL_OR_AGENT_INSTRUCTION_CHANGED", "POLICY_RELEVANT_FILE_CHANGED"})
    if after is not None and after["mode"] == "regular_executable" and (
        before is None or before["mode"] != "regular_executable"
    ):
        result.add("EXECUTABLE_ADDED")
    if after is not None and new_raw is not None and new_raw.startswith(_EXECUTABLE_MAGIC) and (
        before is None or old_raw is None or not old_raw.startswith(_EXECUTABLE_MAGIC)
    ):
        result.add("BINARY_ADDED")
    if any(
        item is not None and item["kind"] in {"symlink", "hardlink", "gitlink", "special"}
        for item in (before, after)
    ):
        result.add("LINK_OR_SPECIAL_FILE_CHANGED")
    old_network, old_permission, old_unsupported = _text_security(old_raw or b"")
    new_network, new_permission, new_unsupported = _text_security(new_raw or b"")
    if old_network != new_network or (old_network and old_raw != new_raw):
        result.add("NETWORK_OR_CREDENTIAL_CHANGED")
    if old_permission != new_permission or (old_permission and old_raw != new_raw):
        result.add("PERMISSION_CHANGED")
    if old_unsupported != new_unsupported or (old_unsupported and old_raw != new_raw):
        result.add("UNSUPPORTED_CONTENT_CHANGED")
    return result


def compare_revisions(
    *,
    old_revision: Mapping[str, Any],
    new_revision: Mapping[str, Any],
    old_tree: Mapping[str, Any],
    new_tree: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    ancestry_state: str = "UNKNOWN",
    old_components: list[Mapping[str, Any]] | None = None,
    new_components: list[Mapping[str, Any]] | None = None,
    old_classifications: list[Mapping[str, Any]] | None = None,
    new_classifications: list[Mapping[str, Any]] | None = None,
    old_classification_report: Mapping[str, Any] | None = None,
    new_classification_report: Mapping[str, Any] | None = None,
    old_license_evidence: Mapping[str, Any] | None = None,
    new_license_evidence: Mapping[str, Any] | None = None,
    old_provenance_evidence: Mapping[str, Any] | None = None,
    new_provenance_evidence: Mapping[str, Any] | None = None,
    old_intake_attempt: Mapping[str, Any] | None = None,
    new_intake_attempt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare two current quarantined revision snapshots for one source."""
    trusted = _require_trusted_source_policy(policy)
    if type(store) is not QuarantineStore:
        raise EcosystemError("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    store._require_policy(trusted)
    if type(ancestry_state) is not str or ancestry_state not in _ANCESTRY_STATES:
        raise EcosystemError("PROVENANCE_CONFLICT", "Comparison ancestry state is invalid")
    before_revision, before_tree, _before_attempt = _validate_authoritative_revision_snapshot(
        revision=old_revision,
        tree=old_tree,
        store=store,
        policy=trusted,
        intake_attempt=old_intake_attempt,
    )
    after_revision, after_tree, _after_attempt = _validate_authoritative_revision_snapshot(
        revision=new_revision,
        tree=new_tree,
        store=store,
        policy=trusted,
        intake_attempt=new_intake_attempt,
    )
    if before_revision["source_id"] != after_revision["source_id"]:
        raise EcosystemError("SOURCE_IDENTITY_CONFLICT", "Comparison requires one exact source")
    # Slice 3C has no Git/network ancestry provider.  Only SAME can be derived
    # locally from the exact immutable revision identity; every other
    # relationship remains UNKNOWN until a future, separately approved and
    # subject-bound provider exists.  A raw caller assertion must not become
    # persistent comparison evidence merely by being supplied again during
    # validation.
    derived_ancestry_state = (
        "SAME"
        if before_revision["revision_id"] == after_revision["revision_id"]
        else "UNKNOWN"
    )
    if ancestry_state not in {"UNKNOWN", derived_ancestry_state}:
        raise EcosystemError(
            "PROVENANCE_INSUFFICIENT",
            "Comparison ancestry lacks authoritative subject-bound evidence",
        )
    ancestry_state = derived_ancestry_state

    before_entries = {item["path"]: item for item in before_tree["entries"]}
    after_entries = {item["path"]: item for item in after_tree["entries"]}
    _validate_role_file_limits(list(before_entries.values()), trusted)
    _validate_role_file_limits(list(after_entries.values()), trusted)
    all_paths = sorted(set(before_entries) | set(after_entries), key=lambda item: item.encode("utf-8"))
    added: list[str] = []
    removed: list[str] = []
    modified: list[str] = []
    type_changed: list[str] = []
    mode_changed: list[str] = []
    codes: set[str] = set()
    raw_cache: dict[tuple[str, str], bytes] = {}

    def raw(side: str, entry: Mapping[str, Any] | None) -> bytes | None:
        if entry is None:
            return None
        key = (side, entry["sha256"])
        if key not in raw_cache:
            raw_cache[key] = _read_entry(
                store, entry, maximum_bytes=trusted.resource_limits["max_file_bytes"]
            )
        return raw_cache[key]

    for path in all_paths:
        before = before_entries.get(path)
        after = after_entries.get(path)
        digest = _path_sha256(path)
        changed = False
        if before is None:
            added.append(digest)
            codes.add("FILE_ADDED")
            changed = True
        elif after is None:
            removed.append(digest)
            codes.add("FILE_REMOVED")
            changed = True
        else:
            if before["sha256"] != after["sha256"]:
                modified.append(digest)
                codes.add("FILE_CONTENT_CHANGED")
                changed = True
            if before["kind"] != after["kind"]:
                type_changed.append(digest)
                codes.add("FILE_TYPE_CHANGED")
                changed = True
            if before["mode"] != after["mode"]:
                mode_changed.append(digest)
                codes.add("FILE_MODE_CHANGED")
                changed = True
        if changed:
            codes.update(_path_security_codes(path, before, after, raw("old", before), raw("new", after)))
        else:
            # Rehash every referenced object even when the two trees are equal.
            raw("old", before)
            raw("new", after)

    path_change_count = sum(map(len, (added, removed, modified, type_changed, mode_changed)))
    if path_change_count > 8192:
        raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", "Comparison path changes exceed the v1 bound")
    for values in (added, removed, modified, type_changed, mode_changed):
        values.sort()
        if len(values) != len(set(values)):
            raise EcosystemError("PROVENANCE_CONFLICT", "Comparison path changes are duplicated")

    evidence_values = (
        old_components,
        new_components,
        old_classifications,
        new_classifications,
        old_classification_report,
        new_classification_report,
        old_license_evidence,
        new_license_evidence,
        old_provenance_evidence,
        new_provenance_evidence,
        old_intake_attempt,
        new_intake_attempt,
    )
    complete_comparison_evidence = all(value is not None for value in evidence_values)
    if complete_comparison_evidence:
        checked_old_components, _checked_old_classifications, _checked_old_report = (
            validate_component_classification(
                old_components,
                old_classifications,
                old_classification_report,
                revision=before_revision,
                tree=before_tree,
                store=store,
                policy=trusted,
            )
        )
        checked_new_components, _checked_new_classifications, _checked_new_report = (
            validate_component_classification(
                new_components,
                new_classifications,
                new_classification_report,
                revision=after_revision,
                tree=after_tree,
                store=store,
                policy=trusted,
            )
        )
        if (
            _checked_old_report["report_status"] != "COMPLETE"
            or _checked_new_report["report_status"] != "COMPLETE"
        ):
            complete_comparison_evidence = False
            checked_old_components = []
            checked_new_components = []
    else:
        # A partial caller projection must not influence a record that could be
        # mistaken for complete comparison evidence.
        checked_old_components = []
        checked_new_components = []
    component_changes = _component_changes(checked_old_components, checked_new_components, codes)
    license_changes = _file_evidence_changes(
        before_entries,
        after_entries,
        predicate=lambda path: PurePosixPath(path).name.casefold().startswith(_LICENSE_PREFIXES),
        maximum=64,
    )
    dependency_changes = _file_evidence_changes(
        before_entries,
        after_entries,
        predicate=lambda path: PurePosixPath(path).name in _DEPENDENCY_BASENAMES,
        maximum=128,
    )

    if complete_comparison_evidence:
        assert old_license_evidence is not None and new_license_evidence is not None
        assert old_provenance_evidence is not None and new_provenance_evidence is not None
        assert old_intake_attempt is not None and new_intake_attempt is not None
        checked_old_license = validate_license_evidence(
            old_license_evidence,
            subject_record=before_revision,
            tree=before_tree,
            store=store,
            policy=trusted,
        )
        checked_new_license = validate_license_evidence(
            new_license_evidence,
            subject_record=after_revision,
            tree=after_tree,
            store=store,
            policy=trusted,
        )
        if canonical_sha256(checked_old_license) != canonical_sha256(checked_new_license):
            codes.add("LICENSE_CHANGED")
        checked_old_provenance = validate_provenance_evidence(
            old_provenance_evidence,
            revision=before_revision,
            tree=before_tree,
            intake_attempt=old_intake_attempt,
            store=store,
            policy=trusted,
        )
        checked_new_provenance = validate_provenance_evidence(
            new_provenance_evidence,
            revision=after_revision,
            tree=after_tree,
            intake_attempt=new_intake_attempt,
            store=store,
            policy=trusted,
        )
        if checked_old_provenance["signature_state"] != checked_new_provenance["signature_state"] or checked_old_provenance["signature_evidence_sha256"] != checked_new_provenance["signature_evidence_sha256"]:
            codes.add("SIGNATURE_OR_ATTESTATION_CHANGED")
        if canonical_sha256(checked_old_provenance) != canonical_sha256(checked_new_provenance):
            codes.add("PROVENANCE_CHANGED")
    if any(
        before_revision[key] != after_revision[key]
        for key in ("commit_object_format", "commit_oid", "input_sha256")
    ):
        codes.add("PROVENANCE_CHANGED")

    security_codes = sorted(codes)
    if len(security_codes) > 32 or not set(security_codes) <= _SECURITY_CODES:
        raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", "Comparison security codes exceed the v1 catalog")
    reasons: list[str] = []
    if not complete_comparison_evidence:
        result = "INSUFFICIENT_EVIDENCE"
        reasons = ["PROVENANCE_INSUFFICIENT"]
    elif ancestry_state == "SAME" and before_revision["revision_id"] != after_revision["revision_id"]:
        result = "INCOMPARABLE"
        reasons = ["PROVENANCE_CONFLICT"]
    elif not security_codes and before_tree["tree_id"] == after_tree["tree_id"]:
        result = "NO_TREE_CHANGE"
    elif set(security_codes) & _SENSITIVE_CODES:
        result = "SECURITY_SENSITIVE_CHANGE"
    else:
        result = "CHANGED"
    body: dict[str, Any] = {
        "source_id": before_revision["source_id"],
        "old_revision_id": before_revision["revision_id"],
        "new_revision_id": after_revision["revision_id"],
        "old_tree_id": before_tree["tree_id"],
        "new_tree_id": after_tree["tree_id"],
        "comparison_policy_semantic_sha256": trusted.policy_semantic_sha256,
        "ancestry_state": ancestry_state,
        "added_path_sha256s": added,
        "removed_path_sha256s": removed,
        "modified_path_sha256s": modified,
        "type_changed_path_sha256s": type_changed,
        "mode_changed_path_sha256s": mode_changed,
        "component_changes": component_changes,
        "license_changes": license_changes,
        "dependency_changes": dependency_changes,
        "security_change_codes": security_codes,
        "comparison_result": result,
        "algorithm_id": COMPARISON_ALGORITHM_ID,
        "algorithm_version": COMPARISON_ALGORITHM_VERSION,
        "reason_codes": reasons,
        "authority": zero_authority(),
    }
    record = {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "comparison_id": typed_id("comparison", body),
        **body,
    }
    canonical_json_bytes(record, maximum_bytes=trusted.resource_limits["max_record_bytes"])
    return record


def validate_revision_comparison(value: Any, **comparison_inputs: Any) -> dict[str, Any]:
    """Recompute a comparison against current records and CAS bytes."""
    record = validate_exact_keys(value, _COMPARISON_FIELDS, "revision comparison")
    if record["schema_version"] != COMPARISON_SCHEMA_VERSION:
        raise EcosystemError("PROVENANCE_CONFLICT", "Comparison schema is unsupported")
    validate_typed_id(record["comparison_id"], "comparison")
    validate_typed_id(record["source_id"], "source")
    for field in ("old_revision_id", "new_revision_id"):
        validate_typed_id(record[field], "revision")
    for field in ("old_tree_id", "new_tree_id"):
        validate_typed_id(record[field], "tree")
    validate_sha256(record["comparison_policy_semantic_sha256"], "comparison policy digest")
    if type(record["ancestry_state"]) is not str or record["ancestry_state"] not in _ANCESTRY_STATES:
        raise EcosystemError("PROVENANCE_CONFLICT", "Comparison ancestry state is invalid")
    path_lists = [
        _validate_digest_list(record[field], 8192, field)
        for field in (
            "added_path_sha256s",
            "removed_path_sha256s",
            "modified_path_sha256s",
            "type_changed_path_sha256s",
            "mode_changed_path_sha256s",
        )
    ]
    if sum(len(items) for items in path_lists) > 8192:
        raise EcosystemError(
            "RESOURCE_LIMIT_EXCEEDED", "Comparison path changes exceed the aggregate bound"
        )
    _validate_change_objects(
        record["component_changes"], maximum=256, component=True, label="Component changes"
    )
    _validate_change_objects(
        record["license_changes"], maximum=64, component=False, label="License changes"
    )
    _validate_change_objects(
        record["dependency_changes"], maximum=128, component=False, label="Dependency changes"
    )
    security_codes = record["security_change_codes"]
    if type(security_codes) is not list or len(security_codes) > 32:
        raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", "Comparison security codes exceed their bound")
    if (
        not all(type(item) is str and item in _SECURITY_CODES for item in security_codes)
        or security_codes != sorted(set(security_codes))
    ):
        raise EcosystemError("PROVENANCE_CONFLICT", "Comparison security codes are invalid")
    if type(record["comparison_result"]) is not str or record["comparison_result"] not in _RESULTS:
        raise EcosystemError("PROVENANCE_CONFLICT", "Comparison result is invalid")
    if type(record["algorithm_id"]) is not str or type(record["algorithm_version"]) is not str:
        raise EcosystemError("PROVENANCE_CONFLICT", "Comparison algorithm identity is invalid")
    validate_reason_codes(record["reason_codes"])
    validate_authority(record["authority"])
    expected = compare_revisions(**comparison_inputs)
    if record != expected:
        raise EcosystemError("SUBJECT_MISMATCH", "Comparison is stale, forged, or incomplete")
    return dict(expected)


def persist_revision_comparison(value: Any, **comparison_inputs: Any) -> dict[str, Any]:
    """Publish one current comparison under its immutable typed identity."""
    store = comparison_inputs.get("store")
    policy = comparison_inputs.get("policy")
    if type(store) is not QuarantineStore:
        raise EcosystemError("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    trusted = _require_trusted_source_policy(policy)
    checked = validate_revision_comparison(value, **comparison_inputs)
    digest = checked["comparison_id"].split("/", 1)[1]
    relative = f"comparisons/sha256/{digest}.json"
    store._publish_record(
        relative,
        checked,
        maximum_bytes=trusted.resource_limits["max_record_bytes"],
        writer_token=_COMPARISON_RECORD_WRITER,
    )
    persisted = store.read_record(
        relative,
        maximum_bytes=trusted.resource_limits["max_record_bytes"],
    )
    if persisted.get("comparison_id") != checked["comparison_id"]:
        raise EcosystemError("CAS_OBJECT_CONFLICT", "Persisted comparison locator is inconsistent")
    return validate_revision_comparison(persisted, **comparison_inputs)


def load_revision_comparison(
    comparison_id: Any, **comparison_inputs: Any
) -> dict[str, Any]:
    """Load and recompute one immutable comparison at its sensitive use."""
    validate_typed_id(comparison_id, "comparison")
    store = comparison_inputs.get("store")
    policy = comparison_inputs.get("policy")
    if type(store) is not QuarantineStore:
        raise EcosystemError("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    trusted = _require_trusted_source_policy(policy)
    store._require_policy(trusted)
    digest = comparison_id.split("/", 1)[1]
    persisted = store.read_record(
        f"comparisons/sha256/{digest}.json",
        maximum_bytes=trusted.resource_limits["max_record_bytes"],
    )
    if persisted.get("comparison_id") != comparison_id:
        raise EcosystemError("CAS_OBJECT_CONFLICT", "Persisted comparison locator is inconsistent")
    return validate_revision_comparison(persisted, **comparison_inputs)
