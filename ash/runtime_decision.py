"""Versioned, non-authorizing Capability Foundation runtime adapter.

The adapter is deliberately narrower than an execution runtime.  It accepts a
closed normalized requirement object, revalidates reviewed capability facts,
runs the bounded exact selector, and returns a redacted decision envelope.
Selection is never load, execution, validation, or Host authorization evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence
from uuid import UUID, uuid4

from .capabilities import (
    AVAILABILITY_STATES,
    CAPABILITY_ID_RE,
    EXECUTABLE_TRUST_TIERS,
    EXECUTION_MECHANISMS,
    HOST_ENUMERATION_STATES,
    HOST_VISIBILITY_SCOPES,
    LIFECYCLE_STATES,
    MAX_CONSIDERED_CAPABILITIES,
    PERMISSIONS,
    SELECTION_ROLES,
    TRUST_TIERS,
    CapabilityCatalogError,
    CapabilitySelectionError,
    select_minimum_sufficient_capabilities,
    validate_capability,
    validate_capability_catalog,
)
from .upstream import UpstreamRegistryError, validate_upstream_registry


RUNTIME_REQUIREMENTS_SCHEMA_VERSION = "nexus.runtime-requirements.v1"
RUNTIME_REQUIREMENTS_VERSION = "1"
RUNTIME_DECISION_SCHEMA_VERSION = "nexus.runtime-capability-decision.v1"
RUNTIME_SELECTOR_VERSION = "nexus.minimum-sufficient-selector.v1"
MAX_REQUIREMENT_ITEMS = 8
MAX_REQUIREMENT_TOKENS = 18

RUNTIME_SAFE_PERMISSIONS = frozenset(
    {"read_metadata", "read_skill_instructions", "read_workspace_allowlist", "write_artifact"}
)
RUNTIME_SAFE_MECHANISMS = frozenset(
    {"host_native", "host_mediated_skill", "nexus_local_read_plan", "advisory_only"}
)
TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,63}$")
REQUIREMENTS_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

HOST_CREATOR_INTERFACES = frozenset(
    {"editable_pptx_create", "presentation_create", "presentation_edit", "presentation_enhance"}
)
HOST_VALIDATION_INTERFACES = frozenset(
    {"presentation_review", "pptx_open_render_validate"}
)

_DECISION_FIELDS = {
    "schema_version",
    "decision_id",
    "issued_at",
    "requirements",
    "selector_version",
    "status",
    "result_code",
    "candidate_capability_ids",
    "considered_capabilities",
    "selected_capabilities",
    "rejected_capabilities",
    "advisory_capabilities",
    "quality_loop",
    "compatibility",
    "evidence_states",
    "security_result",
}
_CAPABILITY_DECISION_FIELDS = {
    "capability_id",
    "decision_state",
    "assigned_role",
    "reason_code",
    "covered_requirements",
    "lifecycle_state",
    "trust_tier",
    "availability_state",
    "host_observation",
    "execution_mechanism",
    "execution_eligibility",
}
_HOST_MAPPING_FIELDS = {
    "mapping_id", "provider_id", "capability_id", "execution_binding_kind",
}
_FORBIDDEN_ENVELOPE_KEYS = frozenset(
    {
        "display_name",
        "path",
        "relative_path",
        "repository",
        "raw_skill",
        "skill_instructions",
        "prompt",
        "project_context",
        "credentials",
        "secrets",
        "artifact_reference",
        "executed_capability_ids",
    }
)


class RuntimeDecisionError(ValueError):
    """Raised when the runtime decision boundary cannot remain fail closed."""


@dataclass(frozen=True)
class RuntimeRequirements:
    requirements_id: str
    requirements_version: str
    task_category: str
    domains: tuple[str, ...]
    outputs: tuple[str, ...]
    validation_requirements: tuple[str, ...]
    allowed_permissions: tuple[str, ...]
    allowed_execution_mechanisms: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": RUNTIME_REQUIREMENTS_SCHEMA_VERSION,
            "requirements_id": self.requirements_id,
            "requirements_version": self.requirements_version,
            "task_category": self.task_category,
            "domains": list(self.domains),
            "outputs": list(self.outputs),
            "validation_requirements": list(self.validation_requirements),
            "allowed_permissions": list(self.allowed_permissions),
            "allowed_execution_mechanisms": list(self.allowed_execution_mechanisms),
        }


def _token_list(value: Any, field: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > MAX_REQUIREMENT_ITEMS:
        raise RuntimeDecisionError(f"runtime requirement list is invalid: {field}")
    if not allow_empty and not value:
        raise RuntimeDecisionError(f"runtime requirement list is empty: {field}")
    if any(not isinstance(item, str) or not TOKEN_RE.fullmatch(item) for item in value):
        raise RuntimeDecisionError(f"runtime requirement token is invalid: {field}")
    if len(set(value)) != len(value):
        raise RuntimeDecisionError(f"runtime requirement list is duplicated: {field}")
    return tuple(value)


def parse_runtime_requirements(value: Any) -> RuntimeRequirements:
    """Parse a content-free normalized requirements envelope."""
    required = {
        "schema_version",
        "requirements_id",
        "requirements_version",
        "task_category",
        "domains",
        "outputs",
        "validation_requirements",
        "allowed_permissions",
        "allowed_execution_mechanisms",
    }
    if not isinstance(value, Mapping) or set(value) != required:
        raise RuntimeDecisionError("runtime requirements are malformed")
    if value.get("schema_version") != RUNTIME_REQUIREMENTS_SCHEMA_VERSION:
        raise RuntimeDecisionError("runtime requirements schema is unsupported")
    requirements_id = value.get("requirements_id")
    task_category = value.get("task_category")
    if not isinstance(requirements_id, str) or not REQUIREMENTS_ID_RE.fullmatch(requirements_id):
        raise RuntimeDecisionError("runtime requirements identity is invalid")
    if value.get("requirements_version") != RUNTIME_REQUIREMENTS_VERSION:
        raise RuntimeDecisionError("runtime requirements version is unsupported")
    if not isinstance(task_category, str) or not TOKEN_RE.fullmatch(task_category):
        raise RuntimeDecisionError("runtime task category is invalid")
    domains = _token_list(value.get("domains"), "domains")
    outputs = _token_list(value.get("outputs"), "outputs")
    validations = _token_list(value.get("validation_requirements"), "validation_requirements")
    if not domains and not outputs and not validations:
        raise RuntimeDecisionError("runtime requirements are empty")
    if len(domains) + len(outputs) + len(validations) > MAX_REQUIREMENT_TOKENS:
        raise RuntimeDecisionError("runtime requirements exceed the bounded token budget")
    permissions = _token_list(value.get("allowed_permissions"), "allowed_permissions")
    mechanisms = _token_list(
        value.get("allowed_execution_mechanisms"),
        "allowed_execution_mechanisms",
        allow_empty=False,
    )
    if not set(permissions) <= RUNTIME_SAFE_PERMISSIONS or not set(permissions) <= PERMISSIONS:
        raise RuntimeDecisionError("runtime permission boundary is unsupported")
    if not set(mechanisms) <= RUNTIME_SAFE_MECHANISMS or not set(mechanisms) <= EXECUTION_MECHANISMS:
        raise RuntimeDecisionError("runtime execution boundary is unsupported")
    return RuntimeRequirements(
        requirements_id=requirements_id,
        requirements_version=RUNTIME_REQUIREMENTS_VERSION,
        task_category=task_category,
        domains=domains,
        outputs=outputs,
        validation_requirements=validations,
        allowed_permissions=permissions,
        allowed_execution_mechanisms=mechanisms,
    )


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _quarantined(record: Mapping[str, Any], reason: str) -> dict[str, Any]:
    result = copy.deepcopy(dict(record))
    result["lifecycle_state"] = "quarantined"
    result["execution"]["directly_executable"] = False
    result["availability"] = {"state": "unavailable", "reason": reason}
    return validate_capability(result)


def _unavailable(record: Mapping[str, Any], reason: str) -> dict[str, Any]:
    result = copy.deepcopy(dict(record))
    result["execution"]["directly_executable"] = False
    result["availability"] = {"state": "unavailable", "reason": reason}
    return validate_capability(result)


def _source_map(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    validated = validate_upstream_registry(registry)
    return {str(item["source_id"]): item for item in validated["sources"]}


def _reviewed_revision_matches(
    record: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]],
) -> bool:
    provenance = record["provenance"]
    source = sources.get(str(provenance["source_id"]))
    if source is None or source.get("execution_status") != "directly_usable_verified":
        return False
    if source.get("repository") != provenance.get("repository") or source.get("commit") != provenance.get("commit"):
        return False
    digest = provenance.get("content_sha256")
    return any(
        component.get("state") == "locally_usable_verified"
        and component.get("content_sha256") == digest
        for component in source.get("accepted_components", [])
        if isinstance(component, Mapping)
    )


def _verified_local_file(
    record: Mapping[str, Any], local_roots: Mapping[str, Path],
) -> str:
    provenance = record["provenance"]
    source_id = str(provenance["source_id"])
    relative = provenance.get("relative_path")
    root = local_roots.get(source_id)
    if root is None or not isinstance(relative, str):
        return "local_component_not_present"
    try:
        if not root.is_absolute() or root.is_symlink():
            return "local_component_not_present"
        resolved_root = root.resolve(strict=True)
        candidate = resolved_root / Path(relative)
        if candidate.is_symlink():
            return "local_component_not_present"
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError):
        return "local_component_not_present"
    if resolved_root.is_symlink() or not resolved_root.is_dir() or resolved.is_symlink() or not resolved.is_file():
        return "local_component_not_present"
    try:
        before = resolved.stat()
        contents = resolved.read_bytes()
        after = resolved.stat()
    except OSError:
        return "local_component_not_present"
    fingerprint = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns)
    if fingerprint(before) != fingerprint(after) or len(contents) != after.st_size:
        return "content_hash_changed_quarantined"
    digest = hashlib.sha256(contents).hexdigest()
    if digest != provenance.get("content_sha256"):
        return "content_hash_changed_quarantined"
    return "verified"


def prepare_catalog_runtime_candidates(
    catalog: Mapping[str, Any],
    upstream_registry: Mapping[str, Any],
    *,
    local_roots: Mapping[str, Path],
) -> list[dict[str, Any]]:
    """Recheck executable catalog entries without discovering new sources."""
    try:
        validated = validate_capability_catalog(catalog)
        sources = _source_map(upstream_registry)
    except (CapabilityCatalogError, UpstreamRegistryError) as exc:
        raise RuntimeDecisionError("runtime capability provenance is unavailable") from exc
    prepared: list[dict[str, Any]] = []
    for original in validated["capabilities"]:
        record = validate_capability(original)
        # Current-turn Host evidence is ephemeral and can only enter through
        # ``host_runtime_decision`` after the R5 ticket/snapshot gate.  A
        # persisted catalog record cannot make that assertion authoritative,
        # even when its static fields claim a current-turn observation.
        if record["execution"]["mechanism"] == "host_native":
            prepared.append(_unavailable(
                record,
                "static_catalog_cannot_establish_host_eligibility",
            ))
            continue
        if not record["execution"]["directly_executable"]:
            prepared.append(record)
            continue
        if record["trust"]["tier"] not in EXECUTABLE_TRUST_TIERS:
            prepared.append(_quarantined(record, "insufficient_trust_state"))
            continue
        if not _reviewed_revision_matches(record, sources):
            prepared.append(_quarantined(record, "reviewed_revision_mismatch"))
            continue
        local_state = _verified_local_file(record, local_roots)
        if local_state == "content_hash_changed_quarantined":
            prepared.append(_quarantined(record, local_state))
        elif local_state != "verified":
            prepared.append(_unavailable(record, local_state))
        else:
            prepared.append(record)
    return prepared


def _safe_host_mapping(mapping: Mapping[str, Any] | None) -> dict[str, str] | None:
    if mapping is None:
        return None
    if set(mapping) != _HOST_MAPPING_FIELDS or any(not isinstance(value, str) for value in mapping.values()):
        raise RuntimeDecisionError("runtime Host mapping evidence is malformed")
    if any(not TOKEN_RE.fullmatch(value) for value in mapping.values()):
        raise RuntimeDecisionError("runtime Host mapping evidence is invalid")
    return dict(mapping)


def _safe_capability_decision(
    record: Mapping[str, Any],
    disposition: Mapping[str, Any],
    *,
    selected: bool,
    host_mapping: Mapping[str, Any] | None,
) -> dict[str, Any]:
    mapping = _safe_host_mapping(host_mapping)
    result: dict[str, Any] = {
        "capability_id": record["capability_id"],
        "decision_state": "selected" if selected else "not_selected",
        "assigned_role": disposition["role"],
        "reason_code": disposition["reason"],
        "covered_requirements": list(disposition["coverage"]),
        "lifecycle_state": record["lifecycle_state"],
        "trust_tier": record["trust"]["tier"],
        "availability_state": record["availability"]["state"],
        "host_observation": {
            "scope": record["host_visibility"]["scope"],
            "enumeration": record["host_visibility"]["enumeration"],
            "observed_current_turn": record["host_visibility"]["observed_current_turn"],
        },
        "execution_mechanism": record["execution"]["mechanism"],
        "execution_eligibility": (
            "mapped_host_selection_only"
            if mapping is not None
            else "selection_only"
            if record["execution"]["directly_executable"]
            else "not_execution_eligible"
        ),
    }
    if mapping is not None:
        result["host_mapping"] = mapping
    return result


def build_runtime_decision(
    requirements: RuntimeRequirements,
    capabilities: Sequence[Mapping[str, Any]],
    *,
    host_mappings: Mapping[str, Mapping[str, Any]] | None = None,
    no_selection_result_code: str | None = None,
    compatibility_path: str | None = None,
    allow_internal_host_mappings: bool = False,
    decision_id: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build one redacted decision envelope with no execution authority."""
    try:
        records = [validate_capability(item) for item in capabilities]
        selector = select_minimum_sufficient_capabilities(
            records,
            {
                "domains": list(requirements.domains),
                "outputs": list(requirements.outputs),
                "validation_requirements": list(requirements.validation_requirements),
                "allowed_permissions": list(requirements.allowed_permissions),
                "allowed_execution_mechanisms": list(requirements.allowed_execution_mechanisms),
            },
        )
    except (CapabilityCatalogError, CapabilitySelectionError) as exc:
        raise RuntimeDecisionError("runtime capability selection failed closed") from exc
    record_by_id = {item["capability_id"]: item for item in records}
    disposition_by_id = {item["capability_id"]: item for item in selector["dispositions"]}
    selected_ids = set(selector["selected"])
    mappings = dict(host_mappings or {})
    if not set(mappings) <= set(record_by_id):
        raise RuntimeDecisionError("runtime Host mapping references an unknown capability")
    if mappings and not allow_internal_host_mappings:
        raise RuntimeDecisionError("runtime Host mapping must come from the R5 internal assessment")
    if any(
        record_by_id[identifier]["execution"]["mechanism"] == "host_native"
        and identifier not in mappings
        for identifier in selected_ids
    ):
        raise RuntimeDecisionError("runtime Host-native selection lacks an R5 internal mapping")

    considered = [
        _safe_capability_decision(
            record_by_id[identifier],
            disposition_by_id[identifier],
            selected=identifier in selected_ids,
            host_mapping=mappings.get(identifier),
        )
        for identifier in sorted(record_by_id)
    ]
    selected = [item for item in considered if item["decision_state"] == "selected"]
    rejected = [item for item in considered if item["decision_state"] == "not_selected"]
    advisory = [item["capability_id"] for item in considered if item["assigned_role"] == "advisory"]

    if selected:
        status = "selection_ready"
        result_code = "RUNTIME_CAPABILITY_SELECTION_READY"
        resolved_compatibility = "none"
        fallback_status = "not_needed"
    else:
        status = "compatibility_required" if compatibility_path else "fallback_required"
        result_code = no_selection_result_code or "CAPABILITY_NOT_COVERED"
        resolved_compatibility = compatibility_path or "legacy_v1_v2_or_native_codex"
        fallback_status = "needed"

    creator_ids = [item["capability_id"] for item in selected if item["assigned_role"] == "primary_creator"]
    reviewer_ids = [item["capability_id"] for item in selected if item["assigned_role"] == "reviewer"]
    enhancer_ids = [item["capability_id"] for item in selected if item["assigned_role"] == "enhancer"]
    issued = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    envelope = {
        "schema_version": RUNTIME_DECISION_SCHEMA_VERSION,
        "decision_id": decision_id or str(uuid4()),
        "issued_at": issued.isoformat().replace("+00:00", "Z"),
        "requirements": requirements.to_dict(),
        "selector_version": RUNTIME_SELECTOR_VERSION,
        "status": status,
        "result_code": result_code,
        "candidate_capability_ids": sorted(record_by_id),
        "considered_capabilities": considered,
        "selected_capabilities": selected,
        "rejected_capabilities": rejected,
        "advisory_capabilities": advisory,
        "quality_loop": {
            "creator_ids": creator_ids,
            "reviewer_ids": reviewer_ids,
            "enhancer_ids": enhancer_ids,
            "max_review_cycles": 2,
            "max_enhancement_passes": 1,
            "enhancement_policy": "only_after_validated_finding_and_material_improvement",
            "artifact_policy": "copy_on_write_preserve_original",
            "execution_status": "deferred_to_host_or_approved_runtime",
        },
        "compatibility": {
            "route": resolved_compatibility,
            "fallback_status": fallback_status,
        },
        "evidence_states": {
            "selection": "selected" if selected else "not_selected",
            "execution": "not_executed",
            "validation": "not_validated",
        },
        "security_result": {
            "code": result_code,
            "mcp_execution_authority": "none",
            "selection_is_execution_evidence": False,
            "private_host_state_access": "none",
            "skill_content_exposure": "none",
            "replay_authority": "none_non_authorizing_decision",
        },
    }
    return validate_runtime_decision_envelope(envelope)


def _forbidden_key_present(value: Any) -> bool:
    if isinstance(value, Mapping):
        return bool(set(value) & _FORBIDDEN_ENVELOPE_KEYS) or any(
            _forbidden_key_present(item) for item in value.values()
        )
    if isinstance(value, list):
        return any(_forbidden_key_present(item) for item in value)
    return False


def validate_runtime_decision_envelope(value: Any) -> dict[str, Any]:
    """Strictly validate an audit envelope without turning it into authority."""
    if not isinstance(value, Mapping) or set(value) != _DECISION_FIELDS:
        raise RuntimeDecisionError("runtime decision envelope is malformed")
    if _forbidden_key_present(value):
        raise RuntimeDecisionError("runtime decision envelope contains forbidden data")
    if value.get("schema_version") != RUNTIME_DECISION_SCHEMA_VERSION:
        raise RuntimeDecisionError("runtime decision schema is unsupported")
    try:
        UUID(str(value.get("decision_id")))
        issued = datetime.fromisoformat(str(value.get("issued_at")).replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise RuntimeDecisionError("runtime decision identity or timestamp is invalid") from None
    if issued.tzinfo is None:
        raise RuntimeDecisionError("runtime decision timestamp is invalid")
    requirements = parse_runtime_requirements(value.get("requirements"))
    if value.get("selector_version") != RUNTIME_SELECTOR_VERSION:
        raise RuntimeDecisionError("runtime selector version is invalid")
    candidate_ids = value.get("candidate_capability_ids")
    considered = value.get("considered_capabilities")
    selected = value.get("selected_capabilities")
    rejected = value.get("rejected_capabilities")
    advisory = value.get("advisory_capabilities")
    if (
        not isinstance(candidate_ids, list)
        or candidate_ids != sorted(candidate_ids)
        or len(candidate_ids) != len(set(candidate_ids))
        or len(candidate_ids) > MAX_CONSIDERED_CAPABILITIES
        or any(not isinstance(item, str) for item in candidate_ids)
        or not all(isinstance(items, list) for items in (considered, selected, rejected, advisory))
    ):
        raise RuntimeDecisionError("runtime decision candidate set is invalid")

    def validate_item(item: Any, expected_state: str) -> None:
        if not isinstance(item, Mapping):
            raise RuntimeDecisionError("runtime decision capability is invalid")
        allowed = set(_CAPABILITY_DECISION_FIELDS)
        if "host_mapping" in item:
            allowed.add("host_mapping")
        if set(item) != allowed or item.get("decision_state") != expected_state:
            raise RuntimeDecisionError("runtime decision capability is malformed")
        capability_id = item.get("capability_id")
        if (
            capability_id not in candidate_ids
            or not isinstance(capability_id, str)
            or not CAPABILITY_ID_RE.fullmatch(capability_id)
            or item.get("assigned_role") not in SELECTION_ROLES
        ):
            raise RuntimeDecisionError("runtime decision capability identity or role is invalid")
        reason = item.get("reason_code")
        coverage = item.get("covered_requirements")
        if (
            not isinstance(reason, str)
            or not TOKEN_RE.fullmatch(reason)
            or not isinstance(coverage, list)
            or coverage != sorted(coverage)
            or len(coverage) != len(set(coverage))
            or any(not isinstance(token, str) or not TOKEN_RE.fullmatch(token) for token in coverage)
        ):
            raise RuntimeDecisionError("runtime decision capability rationale is invalid")
        if (
            item.get("lifecycle_state") not in LIFECYCLE_STATES
            or item.get("trust_tier") not in TRUST_TIERS
            or item.get("availability_state") not in AVAILABILITY_STATES
            or item.get("execution_eligibility") not in {
                "mapped_host_selection_only", "selection_only", "not_execution_eligible",
            }
        ):
            raise RuntimeDecisionError("runtime decision capability governance state is invalid")
        if item.get("execution_mechanism") not in EXECUTION_MECHANISMS:
            raise RuntimeDecisionError("runtime decision execution mechanism is invalid")
        observation = item.get("host_observation")
        if not isinstance(observation, Mapping) or set(observation) != {
            "scope", "enumeration", "observed_current_turn",
        } or not isinstance(observation.get("observed_current_turn"), bool) or (
            observation.get("scope") not in HOST_VISIBILITY_SCOPES
            or observation.get("enumeration") not in HOST_ENUMERATION_STATES
        ):
            raise RuntimeDecisionError("runtime decision Host observation is invalid")
        if "host_mapping" in item:
            _safe_host_mapping(item["host_mapping"])
            if (
                observation.get("scope") != "current_turn_host_visible_subset"
                or observation.get("enumeration") != "not_globally_enumerated"
                or observation.get("observed_current_turn") is not True
                or item.get("execution_mechanism") != "host_native"
            ):
                raise RuntimeDecisionError("runtime decision Host mapping lacks current-turn evidence")

    for item in considered:
        validate_item(item, str(item.get("decision_state")) if isinstance(item, Mapping) else "")
    for item in selected:
        validate_item(item, "selected")
    for item in rejected:
        validate_item(item, "not_selected")
    considered_ids = [item["capability_id"] for item in considered]
    selected_ids = [item["capability_id"] for item in selected]
    rejected_ids = [item["capability_id"] for item in rejected]
    if (
        considered_ids != candidate_ids
        or sorted(selected_ids + rejected_ids) != candidate_ids
        or set(selected_ids) & set(rejected_ids)
        or any(item not in candidate_ids for item in advisory)
    ):
        raise RuntimeDecisionError("runtime decision disposition partition is invalid")
    considered_by_id = {item["capability_id"]: item for item in considered}
    if any(considered_by_id[item["capability_id"]] != item for item in [*selected, *rejected]):
        raise RuntimeDecisionError("runtime decision capability evidence is inconsistent")
    if advisory != sorted(
        item["capability_id"] for item in considered if item["assigned_role"] == "advisory"
    ):
        raise RuntimeDecisionError("runtime advisory capability list is invalid")

    status = value.get("status")
    result_code = value.get("result_code")
    compatibility = value.get("compatibility")
    evidence = value.get("evidence_states")
    security = value.get("security_result")
    if status not in {"selection_ready", "compatibility_required", "fallback_required"}:
        raise RuntimeDecisionError("runtime decision status is invalid")
    if not isinstance(result_code, str) or not TOKEN_RE.fullmatch(result_code.casefold()):
        raise RuntimeDecisionError("runtime decision result code is invalid")
    if status == "selection_ready" and (not selected or result_code != "RUNTIME_CAPABILITY_SELECTION_READY"):
        raise RuntimeDecisionError("runtime decision selected state is inconsistent")
    if status != "selection_ready" and selected:
        raise RuntimeDecisionError("runtime decision fallback state is inconsistent")
    if (
        not isinstance(compatibility, Mapping)
        or set(compatibility) != {"route", "fallback_status"}
        or compatibility.get("route") not in {
            "none",
            "r5_current_turn_host_capability_assessment",
            "r5_native_host_fallback_only_if_independently_allowed",
            "legacy_v1_v2_or_native_codex",
        }
        or compatibility.get("fallback_status") not in {"needed", "not_needed"}
    ):
        raise RuntimeDecisionError("runtime compatibility path is invalid")
    if evidence != {
        "selection": "selected" if selected else "not_selected",
        "execution": "not_executed",
        "validation": "not_validated",
    }:
        raise RuntimeDecisionError("runtime execution evidence is invalid")
    if security != {
        "code": result_code,
        "mcp_execution_authority": "none",
        "selection_is_execution_evidence": False,
        "private_host_state_access": "none",
        "skill_content_exposure": "none",
        "replay_authority": "none_non_authorizing_decision",
    }:
        raise RuntimeDecisionError("runtime security result is invalid")
    quality = value.get("quality_loop")
    if not isinstance(quality, Mapping) or set(quality) != {
        "creator_ids", "reviewer_ids", "enhancer_ids", "max_review_cycles",
        "max_enhancement_passes", "enhancement_policy", "artifact_policy", "execution_status",
    } or (
        quality.get("max_review_cycles") != 2
        or quality.get("max_enhancement_passes") != 1
        or quality.get("enhancement_policy") != "only_after_validated_finding_and_material_improvement"
        or quality.get("artifact_policy") != "copy_on_write_preserve_original"
    ):
        raise RuntimeDecisionError("runtime quality loop is invalid")
    selected_role_ids = {
        role: sorted(item["capability_id"] for item in selected if item["assigned_role"] == role)
        for role in ("primary_creator", "reviewer", "enhancer")
    }
    if (
        quality.get("creator_ids") != selected_role_ids["primary_creator"]
        or quality.get("reviewer_ids") != selected_role_ids["reviewer"]
        or quality.get("enhancer_ids") != selected_role_ids["enhancer"]
        or quality.get("execution_status") != "deferred_to_host_or_approved_runtime"
    ):
        raise RuntimeDecisionError("runtime quality role assignment is invalid")
    # Keep the normalized object live in validation so future schema changes do
    # not accidentally make this a permissive pass-through.
    if requirements.requirements_version != RUNTIME_REQUIREMENTS_VERSION:
        raise RuntimeDecisionError("runtime requirements version is invalid")
    return json.loads(json.dumps(value, ensure_ascii=False))


class RuntimeCapabilityAdapter:
    """Load only the reviewed local metadata and emit a bounded decision."""

    def __init__(
        self,
        capability_catalog_path: Path,
        upstream_registry_path: Path,
        *,
        local_roots: Mapping[str, Path],
        integrity_manifest_path: Path | None = None,
    ) -> None:
        self.capability_catalog_path = capability_catalog_path
        self.upstream_registry_path = upstream_registry_path
        self.local_roots = dict(local_roots)
        root = capability_catalog_path.parent.parent
        release_manifest = root / "release-manifest.json"
        self.integrity_manifest_path = integrity_manifest_path or (
            release_manifest if release_manifest.is_file() else root / "MANIFEST.json"
        )

    @staticmethod
    def _stable_bytes(path: Path) -> bytes:
        try:
            if path.is_symlink() or not path.is_file():
                raise OSError("not a regular file")
            before = path.stat()
            contents = path.read_bytes()
            after = path.stat()
        except OSError as exc:
            raise RuntimeDecisionError("runtime capability metadata is unavailable") from exc
        fingerprint = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns)
        if fingerprint(before) != fingerprint(after) or len(contents) != after.st_size:
            raise RuntimeDecisionError("runtime capability metadata changed during verification")
        return contents

    @staticmethod
    def _manifest_digest(contents: bytes, *, normalize_text: bool) -> str:
        if normalize_text:
            try:
                contents = contents.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
            except UnicodeDecodeError:
                pass
        return hashlib.sha256(contents).hexdigest()

    def _verify_metadata_integrity(self) -> tuple[bytes, bytes]:
        try:
            manifest_contents = self._stable_bytes(self.integrity_manifest_path)
            payload = json.loads(manifest_contents.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeDecisionError("runtime capability integrity manifest is unavailable") from exc
        if not isinstance(payload, Mapping):
            raise RuntimeDecisionError("runtime capability integrity manifest is invalid")
        release_manifest = "files" in payload
        entries = payload.get("files") if release_manifest else payload
        if not isinstance(entries, Mapping):
            raise RuntimeDecisionError("runtime capability integrity manifest is invalid")
        root = self.integrity_manifest_path.parent
        verified_contents: list[bytes] = []
        for path in (self.capability_catalog_path, self.upstream_registry_path):
            try:
                relative = path.resolve(strict=True).relative_to(root.resolve(strict=True)).as_posix()
            except (OSError, ValueError) as exc:
                raise RuntimeDecisionError("runtime capability metadata is outside its integrity root") from exc
            metadata = entries.get(relative)
            contents = self._stable_bytes(path)
            if (
                not isinstance(metadata, Mapping)
                or not isinstance(metadata.get("sha256"), str)
                or not SHA256_RE.fullmatch(str(metadata["sha256"]))
                or self._manifest_digest(contents, normalize_text=not release_manifest) != metadata["sha256"]
            ):
                raise RuntimeDecisionError("runtime capability metadata integrity check failed")
            verified_contents.append(contents)
        return verified_contents[0], verified_contents[1]

    def decide(self, requirements: RuntimeRequirements) -> dict[str, Any]:
        catalog_contents, registry_contents = self._verify_metadata_integrity()
        try:
            catalog = json.loads(catalog_contents.decode("utf-8"))
            registry = json.loads(registry_contents.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeDecisionError("runtime capability metadata is unavailable") from exc
        candidates = prepare_catalog_runtime_candidates(
            catalog,
            registry,
            local_roots=self.local_roots,
        )
        needs_host = requirements.task_category == "presentation"
        return build_runtime_decision(
            requirements,
            candidates,
            no_selection_result_code="HOST_EVIDENCE_REQUIRED" if needs_host else "CAPABILITY_NOT_COVERED",
            compatibility_path=(
                "r5_current_turn_host_capability_assessment"
                if needs_host
                else "legacy_v1_v2_or_native_codex"
            ),
        )


def host_runtime_decision(snapshot: Any, host_decision: Any) -> dict[str, Any]:
    """Adapt an already-validated R5 current-turn decision to the foundation.

    This function never parses caller payloads and never creates a Host mapping.
    Its inputs come only from the existing R5 parser/selector path.
    """
    required_interfaces = set(snapshot.required_interfaces)
    requirements = RuntimeRequirements(
        requirements_id=f"host-assessment:{snapshot.snapshot_id}",
        requirements_version=RUNTIME_REQUIREMENTS_VERSION,
        task_category=snapshot.task_category,
        domains=("presentation",),
        outputs=tuple(sorted(required_interfaces & HOST_CREATOR_INTERFACES)),
        validation_requirements=tuple(sorted(required_interfaces & HOST_VALIDATION_INTERFACES)),
        allowed_permissions=("write_artifact",),
        allowed_execution_mechanisms=("host_native",),
    )
    capabilities: list[dict[str, Any]] = []
    mappings: dict[str, dict[str, str]] = {}
    selected_host_ids: set[str] = set()
    for assessment in host_decision.assessments:
        capability = assessment.capability
        identifier = f"host/{capability.provider_id}/{capability.capability_id}"
        mapped = assessment.mapping_id is not None
        if mapped:
            mapping = {
                "mapping_id": str(assessment.mapping_id),
                "provider_id": capability.provider_id,
                "capability_id": capability.capability_id,
                "execution_binding_kind": capability.execution_binding_kind,
            }
            _safe_host_mapping(mapping)
            mappings[identifier] = mapping
            mapping_digest = _canonical_sha256(mapping)
        else:
            mapping_digest = None
        interfaces = set(capability.interfaces)
        role = assessment.functional_role
        roles_supported = [role] if role in {
            "primary_creator", "enhancer", "reviewer", "alternative"
        } else ["alternative"]
        record = {
            "capability_id": identifier,
            "display_name": identifier,
            "capability_type": "skill",
            "lifecycle_state": "available" if mapped else "classified",
            "trust": {
                "tier": "official_vendor" if mapped else "untrusted",
                "risk_status": "current-turn reviewed Host mapping" if mapped else "unmapped Host assertion",
            },
            "compatibility": "compatible" if mapped else "incompatible",
            "execution": {
                "mechanism": "host_native" if mapped else "none",
                "directly_executable": bool(mapped),
                "permissions": ["write_artifact"] if mapped else [],
            },
            "availability": {
                "state": "available" if mapped else "unavailable",
                "reason": "current_turn_mapping_eligible" if mapped else "host_mapping_unapproved",
            },
            "host_visibility": {
                "scope": snapshot.inventory_scope,
                "enumeration": snapshot.inventory_completeness,
                "observed_current_turn": True,
            },
            "provenance": {
                "source_id": f"host-map:{assessment.mapping_id}" if mapped else "host-asserted-unmapped",
                "source_scope": "chatgpt_desktop",
                "content_sha256": mapping_digest,
                "import_mode": "no_import",
            },
            "dependencies": ["current_turn_host_execution_substrate"] if mapped else [],
            "inputs": ["current_turn_host_visible_metadata"],
            "outputs": sorted(interfaces & HOST_CREATOR_INTERFACES),
            "domains": ["presentation"] if interfaces else [],
            "validation_requirements": sorted(interfaces & HOST_VALIDATION_INTERFACES),
            "roles_supported": roles_supported,
            "update_strategy": "Require a fresh current-turn R5 assessment; never persist Host eligibility.",
        }
        capabilities.append(validate_capability(record))
        if assessment.decision_state == "selected":
            selected_host_ids.add(identifier)

    envelope = build_runtime_decision(
        requirements,
        capabilities,
        host_mappings=mappings,
        allow_internal_host_mappings=True,
        no_selection_result_code=host_decision.result_code,
        compatibility_path="r5_native_host_fallback_only_if_independently_allowed",
    )
    foundation_selected = {item["capability_id"] for item in envelope["selected_capabilities"]}
    if foundation_selected != selected_host_ids:
        raise RuntimeDecisionError("Capability Foundation and R5 Host selection disagree")
    return envelope
