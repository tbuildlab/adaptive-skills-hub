"""Validation for Nexus's static, provenance-first upstream source registry.

The registry is deliberately data-only. Reading it never clones, downloads,
installs, updates, imports, or executes an upstream component. That separation
lets Nexus retain source review evidence without turning a GitHub URL, Agent
persona, framework, or frontend library into an executable Skill.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


REGISTRY_SCHEMA_VERSION = "nexus.upstream-source-registry.v1"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SOURCE_STATES = frozenset({
    "approved_advisory_only",
    "approved_local_skill_verified",
    "reference_only",
    "license_decision_required",
    "rejected_unresolved",
})
COMPONENT_STATES = frozenset({
    "advisory_only",
    "locally_usable_verified",
    "reference_only",
    "rejected_incompatible",
    "rejected_deprecated",
    "license_decision_required",
    "unresolved",
})


class UpstreamRegistryError(ValueError):
    """Raised for a malformed static registry before it can be trusted."""


def _require_string(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise UpstreamRegistryError(f"source registry field is invalid: {key}")
    return value


def _validate_component(component: Any) -> None:
    if not isinstance(component, Mapping):
        raise UpstreamRegistryError("source registry component is invalid")
    _require_string(component, "component_id")
    _require_string(component, "component_type")
    state = _require_string(component, "state")
    if state not in COMPONENT_STATES:
        raise UpstreamRegistryError("source registry component state is invalid")
    path = component.get("upstream_path")
    if path is not None and (not isinstance(path, str) or not path or Path(path).is_absolute() or ".." in Path(path).parts):
        raise UpstreamRegistryError("source registry component path is invalid")
    digest = component.get("content_sha256")
    if digest is not None and (not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)):
        raise UpstreamRegistryError("source registry component digest is invalid")


def validate_upstream_registry(payload: Any) -> dict[str, Any]:
    """Validate a closed, non-executable source registry and return a copy."""
    if not isinstance(payload, Mapping) or payload.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        raise UpstreamRegistryError("source registry schema is invalid")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise UpstreamRegistryError("source registry sources are invalid")
    seen_ids: set[str] = set()
    seen_repositories: set[str] = set()
    for source in sources:
        if not isinstance(source, Mapping):
            raise UpstreamRegistryError("source registry source is invalid")
        source_id = _require_string(source, "source_id")
        if source_id in seen_ids:
            raise UpstreamRegistryError("source registry source ID is duplicated")
        seen_ids.add(source_id)
        state = _require_string(source, "state")
        if state not in SOURCE_STATES:
            raise UpstreamRegistryError("source registry source state is invalid")
        _require_string(source, "category")
        _require_string(source, "license")
        _require_string(source, "trust_tier")
        _require_string(source, "discovered_from")
        _require_string(source, "last_reviewed")
        _require_string(source, "risk_status")
        repository = source.get("repository")
        commit = source.get("commit")
        if state == "rejected_unresolved":
            if repository is not None or commit is not None:
                raise UpstreamRegistryError("unresolved source must not claim a repository or commit")
        else:
            if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
                raise UpstreamRegistryError("source registry repository is invalid")
            if repository.casefold() in seen_repositories:
                raise UpstreamRegistryError("source registry repository is duplicated")
            seen_repositories.add(repository.casefold())
            if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
                raise UpstreamRegistryError("source registry commit is invalid")
        accepted = source.get("accepted_components")
        rejected = source.get("rejected_components")
        if not isinstance(accepted, list) or not isinstance(rejected, list):
            raise UpstreamRegistryError("source registry component lists are invalid")
        component_ids: set[str] = set()
        for component in [*accepted, *rejected]:
            _validate_component(component)
            component_id = str(component["component_id"])
            if component_id in component_ids:
                raise UpstreamRegistryError("source registry component is duplicated")
            component_ids.add(component_id)
    # A JSON round-trip guarantees consumers receive plain data, not mappings
    # with unexpected custom behavior.
    return json.loads(json.dumps(payload, ensure_ascii=False))


def load_upstream_registry(path: Path) -> dict[str, Any]:
    """Load a reviewed registry from a caller-selected local file only."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UpstreamRegistryError("source registry is unavailable") from exc
    return validate_upstream_registry(payload)


def component_state_summary(payload: Mapping[str, Any]) -> dict[str, int]:
    """Produce an audit summary without resolving or activating anything."""
    validated = validate_upstream_registry(payload)
    counts: dict[str, int] = {}
    for source in validated["sources"]:
        for component in [*source["accepted_components"], *source["rejected_components"]]:
            state = component["state"]
            counts[state] = counts.get(state, 0) + 1
    return dict(sorted(counts.items()))
