"""Manifest-bound, integrity-sealed source policy for Slice 3C."""
from __future__ import annotations

import copy
import hashlib
import hmac
import os
from pathlib import Path
import re
import weakref
from typing import Any, Mapping

from .ecosystem_models import (
    EcosystemError,
    SOURCE_KEY_RE,
    canonical_json_bytes,
    domain_sha256,
    normalize_candidate_path,
    parse_json_bytes,
    source_identity,
    validate_authority,
    validate_exact_keys,
    validate_sha256,
)
from .ecosystem_storage import stable_read_bytes


POLICY_RELATIVE_PATH = "config/ecosystem-source-policy.json"
POLICY_SCHEMA_VERSION = "nexus.ecosystem-source-policy.v1"
MAX_MANIFEST_BYTES = 2_097_152
MAX_POLICY_BYTES = 65_536

RESOURCE_LIMITS: dict[str, int] = {
    "max_policy_bytes": 65_536,
    "max_sources": 32,
    "max_input_bytes": 134_217_728,
    "max_expanded_bytes": 536_870_912,
    "max_entries": 20_000,
    "max_directories": 5_000,
    "max_file_bytes": 33_554_432,
    "max_path_utf8_bytes": 512,
    "max_path_segment_utf8_bytes": 128,
    "max_path_depth": 32,
    "max_components": 128,
    "max_component_entries": 10_000,
    "max_component_bytes": 268_435_456,
    "max_archive_nesting": 1,
    "max_entry_compression_ratio": 100,
    "max_aggregate_compression_ratio": 20,
    "max_findings_per_subject": 1_024,
    "max_license_files": 32,
    "max_dependency_manifests": 64,
    "max_instruction_file_bytes": 262_144,
    "max_license_or_dependency_file_bytes": 1_048_576,
    "max_record_bytes": 2_097_152,
    "max_text_evidence_bytes": 65_536,
    "max_ingest_seconds": 60,
    "max_cas_bytes": 2_147_483_648,
    "max_quarantined_revisions_per_source": 8,
}

PROVIDER_POLICY = {
    "allowed_providers": ["github"],
    "network_acquisition": "disabled",
    "accepted_intake_kinds": ["pre_supplied_zip"],
    "archive_formats": ["zip"],
}

SOURCE_CLASSIFICATIONS = frozenset(
    {
        "GRANULAR_SKILL_SOURCE",
        "ADVISORY_AGENT_SOURCE",
        "REFERENCE_ARCHITECTURE",
        "MEMORY_PATTERN_SOURCE",
        "WORKFLOW_PATTERN_SOURCE",
        "LIBRARY_DEPENDENCY_REFERENCE",
    }
)

_ROOT_FIELDS = {
    "schema_version",
    "policy_id",
    "policy_version",
    "mode",
    "provider_policy",
    "resource_limits",
    "analysis_profiles",
    "evaluation_profiles",
    "sources",
}
_SOURCE_FIELDS = {
    "source_key",
    "provider",
    "canonical_repository",
    "identity_state",
    "source_classifications",
    "whole_repository_disposition",
    "frozen_evidence",
    "authority",
}
_FROZEN_EVIDENCE_FIELDS = {
    "evidence_state",
    "commit_object_format",
    "commit_oid",
    "license_state",
    "spdx_expression",
    "evidence_date",
    "evidence_scope",
}
_ANALYSIS_FIELDS = {"static_analyzer_profile", "component_classifier_profile"}
_STATIC_PROFILE_FIELDS = {"schema_version", "analyzer_id", "analyzer_version", "rules"}
_STATIC_RULE_FIELDS = {
    "rule_id",
    "rule_version",
    "predicate_id",
    "parameters",
    "category",
    "severity",
    "disposition",
}
_CLASSIFIER_PROFILE_FIELDS = {"schema_version", "classifier_id", "classifier_version", "rules"}
_CLASSIFIER_RULE_FIELDS = {
    "rule_id",
    "rule_version",
    "predicate_id",
    "parameters",
    "component_kind",
}
_EVALUATION_PROFILE_FIELDS = {
    "profile_id",
    "profile_version",
    "validator_id",
    "validator_version",
    "subject_types",
    "from_review_state",
    "to_review_state",
    "precondition_set",
    "required_checks",
}
_CHECK_PROFILE_FIELDS = {
    "check_id",
    "operator",
    "required",
    "expected_source",
    "observed_source",
    "evidence_id",
}
_POLICY_ID_RE = re.compile(r"^nexus\.ecosystem-source-policy\.[a-z0-9][a-z0-9._-]{0,63}$")
_TOKEN_RE = re.compile(r"^[a-z][a-z0-9._-]{0,63}$")
_SPDX_RE = re.compile(r"^[A-Za-z0-9.+() -]{1,128}$")
_DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_RELEASE_VERSION_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._-]{0,63}$")
_SECRET_IDENTIFIER_RE = re.compile(
    r"(?i)^(?:sk[-_][A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20,}"
    r"|(?:AKIA|ASIA)[0-9A-Z]{16}|xox[A-Za-z]-[A-Za-z0-9-]{8,}|xapp-[A-Za-z0-9-]{8,})$"
)


def _contains_secret_identifier(value: Any) -> bool:
    """Reject credential-shaped complete identifier components."""
    if type(value) is not str:
        return False
    return any(_SECRET_IDENTIFIER_RE.fullmatch(component) for component in value.split("/"))

EXPECTED_STATIC_PROFILE_SHA256 = "8414bb099dacd82bb30886cb79b3cd927051f2930be6af176f8c909a2cd4bdf9"
EXPECTED_CLASSIFIER_PROFILE_SHA256 = "e41da303f8f22fc0c11efda9d58206a4644854399dfc51354f5df7a3c56bf5f0"
EXPECTED_EVALUATION_SET_SHA256 = "570b38e012148b083bf962f3eeb6e8b6c8b6464ea553c964341b22520e4497f6"
EXPECTED_POLICY_SEMANTIC_SHA256 = "feffb555c65ee623aa0ccd264b0180b7fdc321454fc1e0099783349c2879c6d1"

_STATIC_RULE_IDS = (
    "archive.nested",
    "automation.workflow",
    "binary.executable-magic",
    "content.bidi-control",
    "content.invalid-role-text",
    "credential.content",
    "credential.filename",
    "dependency.manifest",
    "evidence.license-incomplete",
    "evidence.provenance-inexact",
    "hook.git-control",
    "install.declaration",
    "instruction.control-claim",
    "mode.executable",
    "network.declaration",
    "permission.declaration",
)
_CLASSIFIER_RULE_IDS = (
    "component.skill-directory",
    "component.advisory-agent",
    "component.memory-pattern",
    "component.workflow-pattern",
    "component.dependency-reference",
    "component.reference-architecture",
)
_VALIDATOR_IDS = (
    "nexus.validator.ecosystem-classification",
    "nexus.validator.ecosystem-comparison-consistency",
    "nexus.validator.ecosystem-intake-bridge-consistency",
    "nexus.validator.ecosystem-provenance",
    "nexus.validator.ecosystem-review-bundle",
    "nexus.validator.ecosystem-static-security",
    "nexus.validator.ecosystem-validation-bundle",
)

_CONSTRUCTION_TOKEN = object()
_PRODUCTION_LOAD_TOKEN = object()
_HERMETIC_TEST_LOAD_TOKEN = object()
_TRUSTED_SEALS: "weakref.WeakKeyDictionary[TrustedEcosystemSourcePolicy, tuple[Any, ...]]" = weakref.WeakKeyDictionary()
_PRODUCTION_TRUST_MODE = "production"
_HERMETIC_TEST_TRUST_MODE = "hermetic_test"
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


def _policy_error(code: str, message: str) -> EcosystemError:
    return EcosystemError(code, message)


def _closed_token(value: Any, label: str) -> str:
    if type(value) is not str or not _TOKEN_RE.fullmatch(value) or _SECRET_IDENTIFIER_RE.fullmatch(value):
        raise _policy_error("POLICY_SCHEMA_INVALID", f"{label} is invalid")
    return value


def _plain_copy(value: Any) -> Any:
    if type(value) is dict:
        return {key: _plain_copy(nested) for key, nested in value.items()}
    if type(value) is list:
        return [_plain_copy(nested) for nested in value]
    return value


def _validate_manifest_entries(
    value: Any, *, size_key: str
) -> dict[str, dict[str, Any]]:
    if type(value) is not dict or not value:
        raise _policy_error("POLICY_INTEGRITY_INVALID", "Integrity manifest entries are invalid")
    collisions: set[str] = set()
    for raw_name, metadata in value.items():
        try:
            name = normalize_candidate_path(raw_name)
        except EcosystemError:
            raise _policy_error(
                "POLICY_INTEGRITY_INVALID", "Integrity manifest path is invalid"
            ) from None
        if name != raw_name:
            raise _policy_error(
                "POLICY_INTEGRITY_INVALID", "Integrity manifest path is not canonical"
            )
        folded_parts = tuple(part.casefold() for part in name.split("/"))
        folded_name = folded_parts[-1]
        if (
            any(part in _FORBIDDEN_INTEGRITY_PARTS for part in folded_parts)
            or folded_name in _FORBIDDEN_INTEGRITY_NAMES
            or folded_name.startswith(".env.")
            or folded_name.endswith(_SECRET_FILE_SUFFIXES)
        ):
            raise _policy_error(
                "POLICY_INTEGRITY_INVALID", "Integrity manifest path is forbidden"
            )
        collision = name.casefold()
        if collision in collisions:
            raise _policy_error(
                "POLICY_INTEGRITY_INVALID", "Integrity manifest paths collide"
            )
        collisions.add(collision)
        if (
            type(metadata) is not dict
            or set(metadata) != {size_key, "sha256"}
            or type(metadata[size_key]) is not int
            or not 0 <= metadata[size_key] <= 9_223_372_036_854_775_807
            or type(metadata["sha256"]) is not str
            or not re.fullmatch(r"[0-9a-f]{64}", metadata["sha256"])
        ):
            raise _policy_error(
                "POLICY_INTEGRITY_INVALID", "Integrity manifest metadata is invalid"
            )
    return value


def _validate_profile_shapes(policy: dict[str, Any]) -> tuple[str, str, dict[str, str]]:
    analysis = validate_exact_keys(policy["analysis_profiles"], _ANALYSIS_FIELDS, "analysis profiles")
    static = validate_exact_keys(analysis["static_analyzer_profile"], _STATIC_PROFILE_FIELDS, "static profile")
    if (
        static["schema_version"] != "nexus.ecosystem-static-analyzer-profile.v1"
        or static["analyzer_id"] != "nexus.ecosystem-static"
        or static["analyzer_version"] != "1"
        or type(static["rules"]) is not list
        or [item.get("rule_id") if type(item) is dict else None for item in static["rules"]] != list(_STATIC_RULE_IDS)
    ):
        raise _policy_error("POLICY_SCHEMA_INVALID", "Static analyzer profile is not the frozen v1 catalog")
    for item in static["rules"]:
        validate_exact_keys(item, _STATIC_RULE_FIELDS, "static analyzer rule")
        if item["rule_version"] != "1" or type(item["parameters"]) is not dict:
            raise _policy_error("POLICY_SCHEMA_INVALID", "Static analyzer rule is invalid")
        _closed_token(item["predicate_id"], "static predicate")
    static_digest = domain_sha256("nexus.ecosystem-static-analyzer-profile.v1", static)
    if not hmac.compare_digest(static_digest, EXPECTED_STATIC_PROFILE_SHA256):
        raise _policy_error("POLICY_SCHEMA_INVALID", "Static analyzer profile differs from the frozen catalog")

    classifier = validate_exact_keys(
        analysis["component_classifier_profile"], _CLASSIFIER_PROFILE_FIELDS, "classifier profile"
    )
    if (
        classifier["schema_version"] != "nexus.ecosystem-component-classifier-profile.v1"
        or classifier["classifier_id"] != "nexus.ecosystem-component-classifier"
        or classifier["classifier_version"] != "1"
        or type(classifier["rules"]) is not list
        or [item.get("rule_id") if type(item) is dict else None for item in classifier["rules"]]
        != list(_CLASSIFIER_RULE_IDS)
    ):
        raise _policy_error("POLICY_SCHEMA_INVALID", "Classifier profile is not the frozen v1 catalog")
    for item in classifier["rules"]:
        validate_exact_keys(item, _CLASSIFIER_RULE_FIELDS, "classifier rule")
        if item["rule_version"] != "1" or type(item["parameters"]) is not dict:
            raise _policy_error("POLICY_SCHEMA_INVALID", "Classifier rule is invalid")
        _closed_token(item["predicate_id"], "classifier predicate")
    classifier_digest = domain_sha256("nexus.ecosystem-component-classifier-profile.v1", classifier)
    if not hmac.compare_digest(classifier_digest, EXPECTED_CLASSIFIER_PROFILE_SHA256):
        raise _policy_error("POLICY_SCHEMA_INVALID", "Classifier profile differs from the frozen catalog")

    profiles = policy["evaluation_profiles"]
    if type(profiles) is not list or len(profiles) != 7:
        raise _policy_error("POLICY_SCHEMA_INVALID", "Evaluation profile set is invalid")
    if [item.get("validator_id") if type(item) is dict else None for item in profiles] != list(_VALIDATOR_IDS):
        raise _policy_error("POLICY_SCHEMA_INVALID", "Evaluation profiles are absent, duplicated, or unsorted")
    profile_digests: dict[str, str] = {}
    for profile in profiles:
        validate_exact_keys(profile, _EVALUATION_PROFILE_FIELDS, "evaluation profile")
        if (
            profile["profile_version"] != "1"
            or profile["validator_version"] != "1"
            or profile["profile_id"] != profile["validator_id"].replace("nexus.validator.", "nexus.profile.", 1)
            or type(profile["subject_types"]) is not list
            or profile["subject_types"] != sorted(set(profile["subject_types"]))
            or type(profile["required_checks"]) is not list
            or not profile["required_checks"]
            or [item.get("check_id") if type(item) is dict else None for item in profile["required_checks"]]
            != sorted(item.get("check_id") if type(item) is dict else "" for item in profile["required_checks"])
        ):
            raise _policy_error("POLICY_SCHEMA_INVALID", "Evaluation profile is invalid")
        _closed_token(profile["profile_id"], "evaluation profile identifier")
        _closed_token(profile["precondition_set"], "evaluation precondition set")
        for check in profile["required_checks"]:
            validate_exact_keys(check, _CHECK_PROFILE_FIELDS, "evaluation check profile")
            if check["required"] is not True:
                raise _policy_error("POLICY_SCHEMA_INVALID", "Evaluation check must be mandatory")
            for key in _CHECK_PROFILE_FIELDS - {"required"}:
                _closed_token(check[key], f"evaluation check {key}")
        profile_digests[profile["profile_id"]] = domain_sha256(
            "nexus.ecosystem-evaluation-profile.v1", profile
        )
    evaluation_set_digest = domain_sha256(
        "nexus.ecosystem-evaluation-profiles.v1", {"evaluation_profiles": profiles}
    )
    if not hmac.compare_digest(evaluation_set_digest, EXPECTED_EVALUATION_SET_SHA256):
        raise _policy_error("POLICY_SCHEMA_INVALID", "Evaluation profiles differ from the frozen v1 set")
    return static_digest, classifier_digest, profile_digests


def _validate_sources(value: Any) -> dict[str, dict[str, Any]]:
    if type(value) is not list or len(value) != 8:
        raise _policy_error("POLICY_SCHEMA_INVALID", "The v1 policy requires exactly eight sources")
    if any(type(item) is not dict for item in value):
        raise _policy_error("POLICY_SCHEMA_INVALID", "Source policy records require exact objects")
    keys = [item.get("source_key") if type(item) is dict else None for item in value]
    if any(type(key) is not str for key in keys) or keys != sorted(keys) or len(keys) != len(set(keys)):
        raise _policy_error("POLICY_SCHEMA_INVALID", "Sources are duplicated or unsorted")
    result: dict[str, dict[str, Any]] = {}
    for source in value:
        validate_exact_keys(source, _SOURCE_FIELDS, "source policy record")
        source_key = source["source_key"]
        repository = source["canonical_repository"]
        if (
            type(source_key) is not str
            or not SOURCE_KEY_RE.fullmatch(source_key)
            or type(repository) is not str
            or source_key != f"github/{repository.lower()}"
            or source["provider"] != "github"
            or source["identity_state"] != "SOURCE_IDENTITY_ONLY"
            or source["whole_repository_disposition"] != "QUARANTINE_UNTIL_REVIEW"
            or _contains_secret_identifier(source_key)
            or _contains_secret_identifier(repository)
        ):
            raise _policy_error("POLICY_SCHEMA_INVALID", "Source identity is inconsistent")
        classifications = source["source_classifications"]
        if (
            type(classifications) is not list
            or not classifications
            or classifications != sorted(set(classifications))
            or not set(classifications) <= SOURCE_CLASSIFICATIONS
        ):
            raise _policy_error("POLICY_SCHEMA_INVALID", "Source classifications are invalid")
        evidence = validate_exact_keys(source["frozen_evidence"], _FROZEN_EVIDENCE_FIELDS, "frozen evidence")
        if (
            evidence["evidence_scope"] != "historical_local_review_only"
            or evidence["evidence_state"] not in {"VERIFIED_HISTORICAL_SNAPSHOT", "UNVERIFIED"}
            or evidence["license_state"] not in {"VERIFIED_DECLARATION", "UNVERIFIED"}
        ):
            raise _policy_error("POLICY_SCHEMA_INVALID", "Frozen evidence state is invalid")
        verified = evidence["evidence_state"] == "VERIFIED_HISTORICAL_SNAPSHOT"
        if verified:
            if evidence["commit_object_format"] != "git_sha1" or type(evidence["commit_oid"]) is not str or not re.fullmatch(r"[0-9a-f]{40}", evidence["commit_oid"]):
                raise _policy_error("POLICY_SCHEMA_INVALID", "Frozen commit evidence is invalid")
        elif evidence["commit_object_format"] != "none" or evidence["commit_oid"] is not None:
            raise _policy_error("POLICY_SCHEMA_INVALID", "Unverified commit evidence must be null")
        if evidence["license_state"] == "VERIFIED_DECLARATION":
            if type(evidence["spdx_expression"]) is not str or not _SPDX_RE.fullmatch(evidence["spdx_expression"]):
                raise _policy_error("POLICY_SCHEMA_INVALID", "Frozen license evidence is invalid")
        elif evidence["spdx_expression"] is not None:
            raise _policy_error("POLICY_SCHEMA_INVALID", "Unverified license evidence must be null")
        if evidence["evidence_date"] is not None and (
            type(evidence["evidence_date"]) is not str or not _DATE_RE.fullmatch(evidence["evidence_date"])
        ):
            raise _policy_error("POLICY_SCHEMA_INVALID", "Frozen evidence date is invalid")
        validate_authority(source["authority"])
        source_identity("github", repository)
        result[source_key] = _plain_copy(source)
    return result


def parse_untrusted_source_policy(value: Any) -> dict[str, Any]:
    """Validate policy semantics without creating trusted authority."""
    policy = validate_exact_keys(value, _ROOT_FIELDS, "ecosystem source policy")
    if (
        policy["schema_version"] != POLICY_SCHEMA_VERSION
        or type(policy["policy_id"]) is not str
        or not _POLICY_ID_RE.fullmatch(policy["policy_id"])
        or policy["policy_version"] != "1"
        or policy["mode"] != "quarantine_only"
        or policy["provider_policy"] != PROVIDER_POLICY
        or policy["resource_limits"] != RESOURCE_LIMITS
    ):
        raise _policy_error("POLICY_SCHEMA_INVALID", "Source policy root is invalid")
    validate_exact_keys(policy["provider_policy"], PROVIDER_POLICY, "provider policy")
    validate_exact_keys(policy["resource_limits"], RESOURCE_LIMITS, "resource limits")
    if any(type(policy["resource_limits"][key]) is not int for key in RESOURCE_LIMITS):
        raise _policy_error("POLICY_SCHEMA_INVALID", "Resource limits require exact integers")
    _validate_profile_shapes(policy)
    _validate_sources(policy["sources"])
    canonical_json_bytes(policy, maximum_bytes=MAX_POLICY_BYTES)
    return _plain_copy(policy)


def parse_source_policy_bytes(raw: bytes) -> dict[str, Any]:
    return parse_untrusted_source_policy(
        parse_json_bytes(raw, maximum_bytes=MAX_POLICY_BYTES, label="ecosystem source policy")
    )


class TrustedEcosystemSourcePolicy:
    """Exact final process-local wrapper issued only after manifest verification."""

    __slots__ = (
        "_policy",
        "_seal",
        "policy_semantic_sha256",
        "integrity_manifest_sha256",
        "static_analyzer_config_sha256",
        "component_classifier_config_sha256",
        "evaluation_profile_sha256s",
        "_trust_mode",
        "_repository_root",
        "__weakref__",
    )

    def __init_subclass__(cls, **_kwargs: Any) -> None:
        raise TypeError("TrustedEcosystemSourcePolicy is final")

    def __init__(
        self,
        policy: dict[str, Any],
        *,
        token: object,
        integrity_manifest_sha256: str,
        trust_mode: str,
        repository_root: Path,
    ) -> None:
        if token is not _CONSTRUCTION_TOKEN:
            raise _policy_error("POLICY_UNTRUSTED", "Trusted policy construction is private")
        if trust_mode not in {_PRODUCTION_TRUST_MODE, _HERMETIC_TEST_TRUST_MODE}:
            raise _policy_error("POLICY_UNTRUSTED", "Trusted policy mode is invalid")
        if not isinstance(repository_root, Path) or not repository_root.is_absolute():
            raise _policy_error("POLICY_UNTRUSTED", "Trusted policy root is invalid")
        static_digest, classifier_digest, profile_digests = _validate_profile_shapes(policy)
        self._policy = _plain_copy(policy)
        self._seal = object()
        self.policy_semantic_sha256 = domain_sha256(POLICY_SCHEMA_VERSION, self._policy)
        self.integrity_manifest_sha256 = validate_sha256(integrity_manifest_sha256, "manifest digest")
        self.static_analyzer_config_sha256 = static_digest
        self.component_classifier_config_sha256 = classifier_digest
        self.evaluation_profile_sha256s = dict(profile_digests)
        self._trust_mode = trust_mode
        self._repository_root = str(repository_root)
        # Keep the authority baseline outside the mutable instance.  A test or
        # reflective caller that rewrites both the policy and its public
        # digest attributes must still be unable to manufacture a valid seal.
        _TRUSTED_SEALS[self] = (
            self._seal,
            self.policy_semantic_sha256,
            self.integrity_manifest_sha256,
            self.static_analyzer_config_sha256,
            self.component_classifier_config_sha256,
            tuple(sorted(self.evaluation_profile_sha256s.items())),
            self._trust_mode,
            self._repository_root,
        )

    @property
    def policy_id(self) -> str:
        return self._policy["policy_id"]

    @property
    def policy_version(self) -> str:
        return self._policy["policy_version"]

    @property
    def resource_limits(self) -> dict[str, int]:
        return dict(self._policy["resource_limits"])

    def source(self, source_key: str) -> dict[str, Any]:
        _require_trusted_source_policy(self)
        for source in self._policy["sources"]:
            if source["source_key"] == source_key:
                item = _plain_copy(source)
                item["source_id"] = source_identity(source["provider"], source["canonical_repository"])
                return item
        raise _policy_error("SOURCE_NOT_ALLOWED", "Source is absent from the trusted policy")

    def evaluation_profile(self, profile_id: str) -> tuple[dict[str, Any], str]:
        _require_trusted_source_policy(self)
        for profile in self._policy["evaluation_profiles"]:
            if profile["profile_id"] == profile_id:
                return _plain_copy(profile), self.evaluation_profile_sha256s[profile_id]
        raise _policy_error("POLICY_SCHEMA_INVALID", "Evaluation profile is absent")

    def to_dict(self) -> dict[str, Any]:
        _require_trusted_source_policy(self)
        return _plain_copy(self._policy)


def _require_trusted_source_policy(value: Any) -> TrustedEcosystemSourcePolicy:
    if type(value) is not TrustedEcosystemSourcePolicy:
        raise _policy_error("POLICY_UNTRUSTED", "Trusted source policy is required")
    try:
        baseline = _TRUSTED_SEALS.get(value)
        semantic = domain_sha256(POLICY_SCHEMA_VERSION, value._policy)
        static_digest, classifier_digest, profile_digests = _validate_profile_shapes(value._policy)
    except (AttributeError, TypeError, EcosystemError):
        raise _policy_error("POLICY_UNTRUSTED", "Trusted source policy revalidation failed") from None
    if (
        type(baseline) is not tuple
        or len(baseline) != 8
        or baseline[0] is not value._seal
        or baseline[1] != value.policy_semantic_sha256
        or baseline[2] != value.integrity_manifest_sha256
        or baseline[3] != value.static_analyzer_config_sha256
        or baseline[4] != value.component_classifier_config_sha256
        or baseline[5] != tuple(sorted(value.evaluation_profile_sha256s.items()))
        or baseline[6] != value._trust_mode
        or baseline[7] != value._repository_root
        or value._trust_mode not in {_PRODUCTION_TRUST_MODE, _HERMETIC_TEST_TRUST_MODE}
        or not hmac.compare_digest(semantic, value.policy_semantic_sha256)
        or not hmac.compare_digest(static_digest, value.static_analyzer_config_sha256)
        or not hmac.compare_digest(classifier_digest, value.component_classifier_config_sha256)
        or profile_digests != value.evaluation_profile_sha256s
    ):
        raise _policy_error("POLICY_UNTRUSTED", "Trusted source policy integrity changed")
    return value


def _require_production_source_policy(value: Any) -> TrustedEcosystemSourcePolicy:
    trusted = _require_trusted_source_policy(value)
    repository_root = str(Path(os.path.abspath(__file__)).parents[1])
    if (
        trusted._trust_mode != _PRODUCTION_TRUST_MODE
        or trusted._repository_root != repository_root
        or not hmac.compare_digest(
            trusted.policy_semantic_sha256, EXPECTED_POLICY_SEMANTIC_SHA256
        )
    ):
        raise _policy_error("POLICY_UNTRUSTED", "Production source policy is not approved")
    return trusted


def _load_trusted_source_policy_at(
    *,
    root: Path,
    integrity_manifest_path: Path | None,
    load_token: object,
) -> TrustedEcosystemSourcePolicy:
    """Load one integrity-bound policy in an explicitly selected trust context."""
    if load_token is _PRODUCTION_LOAD_TOKEN:
        trust_mode = _PRODUCTION_TRUST_MODE
        expected_semantic_sha256: str | None = EXPECTED_POLICY_SEMANTIC_SHA256
    elif load_token is _HERMETIC_TEST_LOAD_TOKEN:
        trust_mode = _HERMETIC_TEST_TRUST_MODE
        expected_semantic_sha256 = None
    else:
        raise _policy_error("POLICY_UNTRUSTED", "Trusted policy loader authority is unavailable")
    if not isinstance(root, Path):
        raise _policy_error("POLICY_INTEGRITY_INVALID", "Repository root is invalid")
    if integrity_manifest_path is not None and not isinstance(integrity_manifest_path, Path):
        raise _policy_error("POLICY_INTEGRITY_INVALID", "Integrity manifest path is invalid")
    try:
        # Keep the lexical root until stable_read_bytes has checked every
        # ancestor through no-follow handles. resolve() would hide a junction.
        repository_root = Path(os.path.abspath(root))
    except (OSError, ValueError, TypeError):
        raise _policy_error("POLICY_INTEGRITY_INVALID", "Repository root is invalid") from None
    if not repository_root.is_dir():
        raise _policy_error("POLICY_INTEGRITY_INVALID", "Repository root is invalid")
    policy_path = repository_root / POLICY_RELATIVE_PATH
    release_manifest = repository_root / "release-manifest.json"
    manifest_path = integrity_manifest_path or (
        release_manifest
        if os.path.lexists(release_manifest)
        else repository_root / "MANIFEST.json"
    )
    try:
        # Keep the lexical path for stable_read_bytes. Resolving it first would
        # hide a symlink/reparse point from the no-follow path walk.
        manifest_path = Path(os.path.abspath(manifest_path))
        manifest_path.relative_to(repository_root)
        manifest_raw = stable_read_bytes(
            manifest_path, maximum_bytes=MAX_MANIFEST_BYTES, reason_code="POLICY_INTEGRITY_INVALID"
        )
        try:
            manifest = parse_json_bytes(
                manifest_raw,
                maximum_bytes=MAX_MANIFEST_BYTES,
                label="ecosystem integrity manifest",
            )
        except EcosystemError:
            raise _policy_error(
                "POLICY_INTEGRITY_INVALID", "Integrity manifest is malformed"
            ) from None
        if type(manifest) is not dict:
            raise _policy_error("POLICY_INTEGRITY_INVALID", "Integrity manifest is invalid")
        is_release = Path(manifest_path).name == "release-manifest.json"
        if is_release:
            release_fields = {"schema_version", "product", "distribution", "version", "files"}
            if type(manifest) is not dict or set(manifest) != release_fields:
                raise _policy_error("POLICY_INTEGRITY_INVALID", "Release integrity manifest is invalid")
            release = manifest
            if (
                release["schema_version"] != "nexus.release.manifest.v1"
                or release["product"] != "Nexus"
                or release["distribution"] != "github-release"
                or type(release["version"]) is not str
                or not _RELEASE_VERSION_RE.fullmatch(release["version"])
            ):
                raise _policy_error("POLICY_INTEGRITY_INVALID", "Release integrity manifest is invalid")
            entries = _validate_manifest_entries(release["files"], size_key="size")
            size_key = "size"
        else:
            entries = _validate_manifest_entries(manifest, size_key="bytes")
            size_key = "bytes"
        policy_raw = stable_read_bytes(
            policy_path, maximum_bytes=MAX_POLICY_BYTES, reason_code="POLICY_INTEGRITY_INVALID"
        )
        metadata = entries.get(POLICY_RELATIVE_PATH)
        if type(metadata) is not dict:
            raise _policy_error("POLICY_INTEGRITY_INVALID", "Policy is absent from the integrity manifest")
        if is_release:
            digest_bytes = policy_raw
        else:
            try:
                digest_bytes = policy_raw.decode("utf-8", errors="strict").replace("\r\n", "\n").encode("utf-8")
            except UnicodeDecodeError:
                raise _policy_error("POLICY_INTEGRITY_INVALID", "Policy encoding is invalid") from None
        declared_digest = metadata.get("sha256")
        if (
            type(declared_digest) is not str
            or not re.fullmatch(r"[0-9a-f]{64}", declared_digest)
            or type(metadata.get(size_key)) is not int
            or metadata[size_key] != len(digest_bytes)
            or not hmac.compare_digest(hashlib.sha256(digest_bytes).hexdigest(), declared_digest)
        ):
            raise _policy_error("POLICY_INTEGRITY_INVALID", "Policy integrity verification failed")
        policy = parse_source_policy_bytes(policy_raw)
        semantic = domain_sha256(POLICY_SCHEMA_VERSION, policy)
        if expected_semantic_sha256 is not None and not hmac.compare_digest(
            semantic, expected_semantic_sha256
        ):
            raise _policy_error(
                "POLICY_UNTRUSTED", "Source policy differs from the approved production baseline"
            )
        return TrustedEcosystemSourcePolicy(
            policy,
            token=_CONSTRUCTION_TOKEN,
            integrity_manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
            trust_mode=trust_mode,
            repository_root=repository_root,
        )
    except EcosystemError as exc:
        if exc.reason_code in {"POLICY_SCHEMA_INVALID", "POLICY_INTEGRITY_INVALID", "POLICY_UNTRUSTED"}:
            raise
        raise _policy_error("POLICY_INTEGRITY_INVALID", "Trusted policy loading failed") from None
    except (OSError, ValueError, TypeError):
        raise _policy_error("POLICY_INTEGRITY_INVALID", "Trusted policy loading failed") from None


def load_trusted_source_policy() -> TrustedEcosystemSourcePolicy:
    """Load only the approved policy beside the executing Nexus module."""
    return _load_trusted_source_policy_at(
        root=Path(os.path.abspath(__file__)).parents[1],
        integrity_manifest_path=None,
        load_token=_PRODUCTION_LOAD_TOKEN,
    )


def _load_test_source_policy(
    *, root: Path, integrity_manifest_path: Path | None = None
) -> TrustedEcosystemSourcePolicy:
    """Private hermetic-fixture seam; its seal can never authorize a production store."""
    return _load_trusted_source_policy_at(
        root=root,
        integrity_manifest_path=integrity_manifest_path,
        load_token=_HERMETIC_TEST_LOAD_TOKEN,
    )
