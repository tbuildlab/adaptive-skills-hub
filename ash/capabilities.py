"""Data-only heterogeneous capability governance for Nexus.

This module does not load or execute Skills, Agents, libraries, frameworks, or
upstream code.  It validates reviewed metadata, computes a minimum sufficient
set from already-approved capabilities, and produces an auditable disposition
for every considered capability.
"""
from __future__ import annotations

import itertools
import json
import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping, Sequence


CATALOG_SCHEMA_VERSION = "nexus.capability-foundation.v1"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CAPABILITY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]*$")

CAPABILITY_TYPES = frozenset(
    {
        "skill",
        "agent",
        "agent_collection",
        "runtime",
        "harness",
        "framework",
        "library",
        "reference_architecture",
        "example_collection",
        "skill_factory",
        "registry_infrastructure",
        "design_resource",
    }
)
TRUST_TIERS = frozenset(
    {
        "official_vendor",
        "trusted_seed",
        "reviewed_community",
        "local_maintained",
        "candidate",
        "untrusted",
    }
)
LIFECYCLE_STATES = frozenset(
    {
        "discovered",
        "classified",
        "provenance_verified",
        "security_reviewed",
        "tested",
        "approved",
        "available",
        "quarantined",
        "deprecated",
        "rejected",
    }
)
COMPATIBILITY_STATES = frozenset({"compatible", "adaptable", "reference_only", "incompatible"})
EXECUTION_MECHANISMS = frozenset(
    {
        "host_native",
        "host_mediated_skill",
        "nexus_local_read_plan",
        "advisory_only",
        "reference_only",
        "none",
    }
)
AVAILABILITY_STATES = frozenset(
    {"available", "not_installed", "not_observed", "disabled", "unavailable", "reference_only"}
)
HOST_VISIBILITY_SCOPES = frozenset(
    {"current_turn_host_visible_subset", "local_registry", "not_applicable"}
)
HOST_ENUMERATION_STATES = frozenset({"not_globally_enumerated", "not_applicable"})
PERMISSIONS = frozenset(
    {
        "read_metadata",
        "read_skill_instructions",
        "read_workspace_allowlist",
        "write_artifact",
        "network",
        "subprocess",
        "shell",
        "install",
        "update",
        "agent_delegation",
    }
)
SELECTION_ROLES = frozenset(
    {
        "primary_creator",
        "enhancer",
        "reviewer",
        "alternative",
        "advisory",
        "redundant",
        "unavailable",
        "incompatible",
        "rejected",
    }
)
EXECUTABLE_TYPES = frozenset({"skill"})
MAX_EXACT_SELECTION_CANDIDATES = 18

_FORBIDDEN_STATIC_PERMISSIONS = frozenset({"shell", "install", "update", "agent_delegation"})
_REFERENCE_TYPES = CAPABILITY_TYPES - {"skill", "agent"}


class CapabilityCatalogError(ValueError):
    """Raised when capability metadata violates a closed safety invariant."""


class CapabilitySelectionError(ValueError):
    """Raised when a safe minimum-sufficient selection cannot be computed."""


def _string(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise CapabilityCatalogError(f"capability field is invalid: {key}")
    return value


def _string_list(record: Mapping[str, Any], key: str, *, allow_empty: bool = True) -> list[str]:
    value = record.get(key)
    if not isinstance(value, list) or (not allow_empty and not value):
        raise CapabilityCatalogError(f"capability list is invalid: {key}")
    if any(not isinstance(item, str) or not item for item in value):
        raise CapabilityCatalogError(f"capability list item is invalid: {key}")
    if len(set(value)) != len(value):
        raise CapabilityCatalogError(f"capability list contains duplicates: {key}")
    return list(value)


def _is_absolute_or_traversal(value: str) -> bool:
    return (
        PurePosixPath(value).is_absolute()
        or PureWindowsPath(value).is_absolute()
        or ".." in PurePosixPath(value.replace("\\", "/")).parts
    )


def _validate_provenance(record: Mapping[str, Any], lifecycle: str) -> None:
    provenance = record.get("provenance")
    if not isinstance(provenance, Mapping):
        raise CapabilityCatalogError("capability provenance is invalid")
    _string(provenance, "source_id")
    scope = _string(provenance, "source_scope")
    if scope not in {"codex_user", "codex_project", "local_library", "chatgpt_desktop", "external_upstream"}:
        raise CapabilityCatalogError("capability source scope is invalid")
    import_mode = _string(provenance, "import_mode")
    if import_mode not in {"referenced", "adapted", "vendored", "local_in_place", "no_import"}:
        raise CapabilityCatalogError("capability import mode is invalid")
    repository = provenance.get("repository")
    commit = provenance.get("commit")
    digest = provenance.get("content_sha256")
    local_path = provenance.get("relative_path")
    if scope == "external_upstream" or repository is not None:
        if not isinstance(repository, str) or repository.count("/") != 1:
            raise CapabilityCatalogError("external capability repository is invalid")
        if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
            raise CapabilityCatalogError("external capability commit is not pinned")
    elif commit is not None and (not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit)):
        raise CapabilityCatalogError("capability commit is invalid")
    if digest is not None and (not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)):
        raise CapabilityCatalogError("capability content digest is invalid")
    if local_path is not None:
        if not isinstance(local_path, str) or not local_path or _is_absolute_or_traversal(local_path):
            raise CapabilityCatalogError("capability relative path is unsafe")
    if lifecycle in {"tested", "approved", "available"} and scope != "external_upstream" and digest is None:
        raise CapabilityCatalogError("approved local capability requires a content digest")


def _validate_host_visibility(record: Mapping[str, Any], mechanism: str) -> None:
    visibility = record.get("host_visibility")
    if not isinstance(visibility, Mapping):
        raise CapabilityCatalogError("capability host visibility is invalid")
    scope = _string(visibility, "scope")
    enumeration = _string(visibility, "enumeration")
    if scope not in HOST_VISIBILITY_SCOPES or enumeration not in HOST_ENUMERATION_STATES:
        raise CapabilityCatalogError("capability host visibility state is invalid")
    observed = visibility.get("observed_current_turn")
    if not isinstance(observed, bool):
        raise CapabilityCatalogError("capability host observation state is invalid")
    if mechanism == "host_native":
        if scope != "current_turn_host_visible_subset" or enumeration != "not_globally_enumerated":
            raise CapabilityCatalogError("host-native capability cannot claim global discovery")
        if not observed:
            raise CapabilityCatalogError("host-native capability was not observed in the current turn")
    elif observed and scope != "current_turn_host_visible_subset":
        raise CapabilityCatalogError("current-turn observation has an invalid scope")


def validate_capability(record: Any) -> dict[str, Any]:
    """Validate one non-executing capability record and return plain data."""
    if not isinstance(record, Mapping):
        raise CapabilityCatalogError("capability record is invalid")
    capability_id = _string(record, "capability_id")
    if not CAPABILITY_ID_RE.fullmatch(capability_id):
        raise CapabilityCatalogError("capability ID is invalid")
    _string(record, "display_name")
    capability_type = _string(record, "capability_type")
    if capability_type not in CAPABILITY_TYPES:
        raise CapabilityCatalogError("capability type is invalid")
    lifecycle = _string(record, "lifecycle_state")
    if lifecycle not in LIFECYCLE_STATES:
        raise CapabilityCatalogError("capability lifecycle state is invalid")
    trust = record.get("trust")
    if not isinstance(trust, Mapping) or _string(trust, "tier") not in TRUST_TIERS:
        raise CapabilityCatalogError("capability trust tier is invalid")
    _string(trust, "risk_status")
    compatibility = _string(record, "compatibility")
    if compatibility not in COMPATIBILITY_STATES:
        raise CapabilityCatalogError("capability compatibility is invalid")
    execution = record.get("execution")
    if not isinstance(execution, Mapping):
        raise CapabilityCatalogError("capability execution metadata is invalid")
    mechanism = _string(execution, "mechanism")
    if mechanism not in EXECUTION_MECHANISMS:
        raise CapabilityCatalogError("capability execution mechanism is invalid")
    directly_executable = execution.get("directly_executable")
    if not isinstance(directly_executable, bool):
        raise CapabilityCatalogError("capability execution flag is invalid")
    permissions = _string_list(execution, "permissions")
    if not set(permissions) <= PERMISSIONS:
        raise CapabilityCatalogError("capability permission is invalid")
    if set(permissions) & _FORBIDDEN_STATIC_PERMISSIONS:
        raise CapabilityCatalogError("capability requests authority forbidden in this phase")
    if capability_type == "agent" and (mechanism != "advisory_only" or directly_executable):
        raise CapabilityCatalogError("Agent capabilities are advisory-only")
    if capability_type in _REFERENCE_TYPES and (mechanism not in {"reference_only", "none"} or directly_executable):
        raise CapabilityCatalogError("non-Skill source cannot receive execution authority")
    if directly_executable:
        if capability_type not in EXECUTABLE_TYPES or mechanism not in {
            "host_native",
            "host_mediated_skill",
            "nexus_local_read_plan",
        }:
            raise CapabilityCatalogError("capability execution authority is incompatible with its type")
        if lifecycle != "available" or compatibility != "compatible":
            raise CapabilityCatalogError("executable capability is not approved and available")
    availability = record.get("availability")
    if not isinstance(availability, Mapping):
        raise CapabilityCatalogError("capability availability is invalid")
    availability_state = _string(availability, "state")
    if availability_state not in AVAILABILITY_STATES:
        raise CapabilityCatalogError("capability availability state is invalid")
    _string(availability, "reason")
    if directly_executable and availability_state != "available":
        raise CapabilityCatalogError("executable capability is unavailable")
    _validate_host_visibility(record, mechanism)
    _validate_provenance(record, lifecycle)
    for key in ("dependencies", "inputs", "outputs", "domains", "validation_requirements", "roles_supported"):
        _string_list(record, key)
    roles = set(record["roles_supported"])
    if not roles <= {"primary_creator", "enhancer", "reviewer", "advisory", "alternative"}:
        raise CapabilityCatalogError("capability supported role is invalid")
    _string(record, "update_strategy")
    return json.loads(json.dumps(record, ensure_ascii=False))


def validate_capability_catalog(payload: Any) -> dict[str, Any]:
    """Validate a complete capability catalog without activating any entry."""
    if not isinstance(payload, Mapping) or payload.get("schema_version") != CATALOG_SCHEMA_VERSION:
        raise CapabilityCatalogError("capability catalog schema is invalid")
    policy = payload.get("catalog_policy")
    if not isinstance(policy, str) or "no automatic execution" not in policy.casefold():
        raise CapabilityCatalogError("capability catalog policy is invalid")
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise CapabilityCatalogError("capability catalog entries are invalid")
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in capabilities:
        item = validate_capability(record)
        identifier = item["capability_id"]
        if identifier in seen:
            raise CapabilityCatalogError("capability ID is duplicated")
        seen.add(identifier)
        validated.append(item)
    result = json.loads(json.dumps(payload, ensure_ascii=False))
    result["capabilities"] = validated
    return result


def load_capability_catalog(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CapabilityCatalogError("capability catalog is unavailable") from exc
    return validate_capability_catalog(payload)


_FORWARD_LIFECYCLE = {
    "discovered": "classified",
    "classified": "provenance_verified",
    "provenance_verified": "security_reviewed",
    "security_reviewed": "tested",
    "tested": "approved",
    "approved": "available",
}


def validate_lifecycle_transition(current: str, target: str) -> str:
    """Enforce monotonic review gates and explicit quarantine/rejection exits."""
    if current not in LIFECYCLE_STATES or target not in LIFECYCLE_STATES:
        raise CapabilityCatalogError("capability lifecycle transition is invalid")
    if current == target:
        return target
    if target in {"quarantined", "deprecated", "rejected"}:
        return target
    if current in {"quarantined", "deprecated", "rejected"}:
        raise CapabilityCatalogError("terminal capability lifecycle requires a fresh review record")
    if _FORWARD_LIFECYCLE.get(current) != target:
        raise CapabilityCatalogError("capability lifecycle gate was skipped or reversed")
    return target


def updated_revision_state(previous: Mapping[str, Any], candidate: Mapping[str, Any]) -> str:
    """Quarantine a changed pin/hash instead of inheriting prior approval."""
    old = validate_capability(previous)
    new = validate_capability(candidate)
    old_provenance = old["provenance"]
    new_provenance = new["provenance"]
    changed = any(
        old_provenance.get(key) != new_provenance.get(key)
        for key in ("repository", "commit", "content_sha256")
    )
    if changed and old["lifecycle_state"] in {"approved", "available"}:
        return "quarantined"
    return new["lifecycle_state"]


def _requirement_tokens(requirements: Mapping[str, Any]) -> frozenset[str]:
    tokens: set[str] = set()
    for key, prefix in (
        ("domains", "domain"),
        ("outputs", "output"),
        ("validation_requirements", "validation"),
    ):
        values = requirements.get(key, [])
        if not isinstance(values, list) or any(not isinstance(item, str) or not item for item in values):
            raise CapabilitySelectionError(f"selection requirements are invalid: {key}")
        tokens.update(f"{prefix}:{value}" for value in values)
    if not tokens:
        raise CapabilitySelectionError("selection requirements are empty")
    return frozenset(tokens)


def _coverage(record: Mapping[str, Any]) -> frozenset[str]:
    tokens = {f"domain:{item}" for item in record["domains"]}
    tokens.update(f"output:{item}" for item in record["outputs"])
    tokens.update(f"validation:{item}" for item in record["validation_requirements"])
    return frozenset(tokens)


def _permission_rank(record: Mapping[str, Any]) -> tuple[int, str]:
    return (len(record["execution"]["permissions"]), record["capability_id"])


def select_minimum_sufficient_capabilities(
    capabilities: Sequence[Mapping[str, Any]],
    requirements: Mapping[str, Any],
) -> dict[str, Any]:
    """Select an exact minimum set and classify every considered capability.

    This function only reasons over caller-supplied, current availability facts.
    It does not discover Host state, load instructions, or execute a component.
    """
    required = _requirement_tokens(requirements)
    allowed_permissions = set(requirements.get("allowed_permissions", []))
    if not allowed_permissions <= PERMISSIONS:
        raise CapabilitySelectionError("selection permission boundary is invalid")
    allowed_mechanisms = set(requirements.get("allowed_execution_mechanisms", []))
    if not allowed_mechanisms or not allowed_mechanisms <= EXECUTION_MECHANISMS:
        raise CapabilitySelectionError("selection execution boundary is invalid")

    dispositions: dict[str, dict[str, Any]] = {}
    eligible: list[dict[str, Any]] = []
    for raw in capabilities:
        record = validate_capability(raw)
        identifier = record["capability_id"]
        coverage = _coverage(record) & required
        reason = ""
        role = ""
        if record["lifecycle_state"] == "rejected":
            role, reason = "rejected", "lifecycle_rejected"
        elif record["capability_type"] == "agent" or record["execution"]["mechanism"] == "advisory_only":
            role, reason = "advisory", "agent_advisory_only"
        elif record["availability"]["state"] != "available":
            role, reason = "unavailable", record["availability"]["state"]
        elif record["compatibility"] != "compatible":
            role, reason = "incompatible", record["compatibility"]
        elif record["execution"]["mechanism"] not in allowed_mechanisms:
            role, reason = "incompatible", "execution_mechanism_not_allowed"
        elif not set(record["execution"]["permissions"]) <= allowed_permissions:
            role, reason = "incompatible", "permission_boundary_exceeded"
        elif not record["execution"]["directly_executable"]:
            role, reason = "incompatible", "no_execution_authority"
        elif not coverage:
            role, reason = "alternative", "not_relevant_to_required_coverage"
        else:
            eligible.append(record)
            role, reason = "alternative", "eligible_not_yet_selected"
        dispositions[identifier] = {
            "capability_id": identifier,
            "role": role,
            "reason": reason,
            "coverage": sorted(coverage),
        }

    if len(eligible) > MAX_EXACT_SELECTION_CANDIDATES:
        raise CapabilitySelectionError("too many eligible capabilities for bounded exact selection")
    selected: tuple[dict[str, Any], ...] | None = None
    for size in range(1, len(eligible) + 1):
        sufficient: list[tuple[dict[str, Any], ...]] = []
        for combination in itertools.combinations(eligible, size):
            covered = frozenset().union(*(_coverage(record) for record in combination))
            if required <= covered:
                sufficient.append(combination)
        if sufficient:
            selected = min(
                sufficient,
                key=lambda combination: tuple(_permission_rank(item) for item in sorted(combination, key=_permission_rank)),
            )
            break
    if selected is None:
        return {
            "status": "CAPABILITY_NOT_COVERED",
            "selected": [],
            "required_coverage": sorted(required),
            "dispositions": [dispositions[key] for key in sorted(dispositions)],
        }

    selected_ids = {item["capability_id"] for item in selected}
    selected_coverage = frozenset().union(*(_coverage(record) for record in selected))
    creator_assigned = False
    for record in sorted(selected, key=lambda item: item["capability_id"]):
        identifier = record["capability_id"]
        roles = set(record["roles_supported"])
        if "primary_creator" in roles and set(record["outputs"]) & set(requirements.get("outputs", [])) and not creator_assigned:
            role = "primary_creator"
            creator_assigned = True
        elif "reviewer" in roles and set(record["validation_requirements"]) & set(requirements.get("validation_requirements", [])):
            role = "reviewer"
        elif "enhancer" in roles:
            role = "enhancer"
        else:
            role = "alternative"
        dispositions[identifier].update(role=role, reason="minimum_sufficient_set")
    for record in eligible:
        identifier = record["capability_id"]
        if identifier in selected_ids:
            continue
        coverage = _coverage(record) & required
        if coverage <= selected_coverage:
            dispositions[identifier].update(role="redundant", reason="coverage_already_satisfied")
        else:
            dispositions[identifier].update(role="alternative", reason="not_in_minimum_sufficient_set")

    return {
        "status": "MINIMUM_SUFFICIENT_SET_SELECTED",
        "selected": [item["capability_id"] for item in sorted(selected, key=lambda item: item["capability_id"])],
        "required_coverage": sorted(required),
        "dispositions": [dispositions[key] for key in sorted(dispositions)],
    }


def catalog_state_summary(payload: Mapping[str, Any]) -> dict[str, int]:
    validated = validate_capability_catalog(payload)
    counts: dict[str, int] = {}
    for record in validated["capabilities"]:
        state = record["lifecycle_state"]
        counts[state] = counts.get(state, 0) + 1
    return dict(sorted(counts.items()))


def iter_capabilities(payload: Mapping[str, Any]) -> Iterable[dict[str, Any]]:
    """Yield defensive copies after catalog validation."""
    validated = validate_capability_catalog(payload)
    for record in validated["capabilities"]:
        yield json.loads(json.dumps(record, ensure_ascii=False))
