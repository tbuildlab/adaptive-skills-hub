"""Slice 2/3B adapters and quarantine-only lifecycle handling for Slice 3C."""
from __future__ import annotations

import copy
import hashlib
import hmac
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from uuid import UUID
import weakref
from typing import Any, Mapping, Sequence

from .ecosystem_models import (
    EcosystemError,
    GENESIS_STATE,
    IMPLICIT_STATE,
    StateVector,
    build_state_record,
    build_transition_receipt,
    canonical_json_bytes,
    canonical_sha256,
    ID_DOMAINS,
    parse_state_vector,
    typed_id,
    validate_authority,
    validate_exact_keys,
    validate_identity_record,
    validate_reason_codes,
    validate_sha256,
    validate_state_record,
    validate_transition_receipt,
    validate_typed_id,
    zero_authority,
)
from .ecosystem_policy import (
    TrustedEcosystemSourcePolicy,
    _require_trusted_source_policy,
)
from .ecosystem_storage import QuarantineStore, _STATE_RECORD_WRITER
from .evaluation import (
    EvaluationError,
    TrustedValidatorRegistry,
    _require_trusted_registry,
    canonical_sha256 as evaluation_canonical_sha256,
    evaluate_contract,
    validate_evaluation_receipt,
)
from .scout import ScoutError, validate_candidate, validate_scout_receipt


BRIDGE_SCHEMA_VERSION = "nexus.ecosystem-intake-bridge.v1"
_BRIDGE_FIELDS = {
    "schema_version",
    "bridge_id",
    "scout_receipt_sha256",
    "scout_id",
    "candidate_id",
    "candidate_immutable_reference_sha256",
    "commit_object_format",
    "commit_oid",
    "candidate_admission_disposition",
    "source_policy_id",
    "source_policy_semantic_sha256",
    "source_key",
    "source_id",
    "requested_input_kind",
    "requested_input_sha256",
    "requested_input_size",
    "bridge_result",
    "reason_codes",
    "authority",
}
_CONSTRUCTION_TOKEN = object()
_BRIDGE_SEALS: "weakref.WeakKeyDictionary[ValidatedIntakeBridge, tuple[object, str]]" = weakref.WeakKeyDictionary()
_PROPOSAL_TOKEN = object()
_PROPOSAL_SEALS: "weakref.WeakKeyDictionary[ValidatedTransitionProposal, tuple[Any, ...]]" = weakref.WeakKeyDictionary()
_REVIEW_PROFILE_ORDER = (
    "nexus.profile.ecosystem-provenance",
    "nexus.profile.ecosystem-static-security",
    "nexus.profile.ecosystem-classification",
    "nexus.profile.ecosystem-validation-bundle",
    "nexus.profile.ecosystem-review-bundle",
)
_NO_STATE_PROFILES = {
    "nexus.profile.ecosystem-comparison-consistency",
    "nexus.profile.ecosystem-intake-bridge-consistency",
}
_WIRE_LIFECYCLE = {
    "creation": "created",
    "selection": "not_selected",
    "execution": "not_executed",
    "review": "not_reviewed",
    "enhancement": "not_enhanced",
    "validation": "not_validated",
    "reporting": "not_reported",
}
_MAX_STATE_RECORDS = 32_768
_MAX_SUBJECT_LINEAGE = 64
_EXPECTED_VALIDATORS = {
    "nexus.validator.ecosystem-provenance": (
        "Nexus Ecosystem Provenance Integrity",
        "digest_integrity",
        ("sha256_matches_subject",),
        ("ecosystem_component_revision", "ecosystem_source_revision"),
    ),
    "nexus.validator.ecosystem-static-security": (
        "Nexus Ecosystem Static Security",
        "bounded_predicate",
        ("equals", "not_equals", "present"),
        ("ecosystem_component_revision", "ecosystem_source_revision"),
    ),
    "nexus.validator.ecosystem-classification": (
        "Nexus Ecosystem Classification",
        "bounded_predicate",
        ("equals", "present"),
        ("ecosystem_component_revision", "ecosystem_source_revision"),
    ),
    "nexus.validator.ecosystem-validation-bundle": (
        "Nexus Ecosystem Validation Bundle",
        "receipt_consistency",
        ("receipt_consistent",),
        ("ecosystem_component_revision", "ecosystem_source_revision"),
    ),
    "nexus.validator.ecosystem-review-bundle": (
        "Nexus Ecosystem Review Bundle",
        "state_consistency",
        ("state_consistent",),
        ("ecosystem_component_revision", "ecosystem_source_revision"),
    ),
    "nexus.validator.ecosystem-comparison-consistency": (
        "Nexus Ecosystem Comparison Consistency",
        "receipt_consistency",
        ("receipt_consistent",),
        ("ecosystem_revision_comparison",),
    ),
    "nexus.validator.ecosystem-intake-bridge-consistency": (
        "Nexus Ecosystem Intake Bridge Consistency",
        "receipt_consistency",
        ("receipt_consistent",),
        ("ecosystem_intake_bridge",),
    ),
}


def _copy(value: Any) -> Any:
    if type(value) is dict:
        return {key: _copy(nested) for key, nested in value.items()}
    if type(value) is list:
        return [_copy(nested) for nested in value]
    return value


def _scout_receipt_sha256(value: Mapping[str, Any]) -> str:
    """Digest the frozen Slice 2 wire value with its own JSON number model."""
    try:
        raw = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Scout receipt cannot be canonically encoded") from None
    return hashlib.sha256(raw).hexdigest()


def _source_repository_from_candidate(candidate: Mapping[str, Any]) -> str:
    try:
        split = urlsplit(candidate["canonical_url"])
    except (TypeError, ValueError):
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Candidate repository identity is invalid") from None
    path = split.path.strip("/")
    pieces = path.split("/")
    if (
        split.scheme != "https"
        or split.hostname is None
        or split.hostname.casefold() != "github.com"
        or split.username is not None
        or split.password is not None
        or split.port not in {None, 443}
        or split.query
        or split.fragment
        or len(pieces) != 2
        or not all(pieces)
    ):
        raise EcosystemError("SOURCE_IDENTITY_CONFLICT", "Candidate does not identify one GitHub repository")
    return f"{pieces[0]}/{pieces[1]}".casefold()


def _validated_candidate(receipt: Mapping[str, Any], candidate_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        validated_receipt = validate_scout_receipt(receipt)
    except (ScoutError, TypeError, ValueError):
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Scout receipt validation failed") from None
    matches = [item for item in validated_receipt["candidates"] if item["candidate_id"] == candidate_id]
    if len(matches) != 1:
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Scout receipt does not bind exactly one candidate")
    try:
        candidate = validate_candidate(matches[0])
    except (ScoutError, TypeError, ValueError):
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Scout candidate validation failed") from None
    return validated_receipt, candidate


def validate_intake_bridge_record(value: Any) -> dict[str, Any]:
    record = validate_exact_keys(value, _BRIDGE_FIELDS, "intake bridge")
    if record["schema_version"] != BRIDGE_SCHEMA_VERSION:
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Intake bridge schema is unsupported")
    validate_typed_id(record["bridge_id"], "bridge")
    for field in (
        "scout_receipt_sha256",
        "candidate_immutable_reference_sha256",
        "source_policy_semantic_sha256",
        "requested_input_sha256",
    ):
        validate_sha256(record[field], field)
    try:
        if str(UUID(record["scout_id"])) != record["scout_id"]:
            raise ValueError
    except (TypeError, ValueError, AttributeError):
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Bridge Scout identity is invalid") from None
    validate_typed_id(record["candidate_id"], "candidate")
    validate_typed_id(record["source_id"], "source")
    if (
        record["commit_object_format"] != "git_sha1"
        or type(record["commit_oid"]) is not str
        or not re.fullmatch(r"[0-9a-f]{40}", record["commit_oid"])
        or record["candidate_admission_disposition"]
        not in {"ADMITTED_FOR_REVIEW", "REFERENCE_ONLY", "QUARANTINED", "REJECTED", "INSUFFICIENT_EVIDENCE"}
        or record["requested_input_kind"] != "pre_supplied_zip"
        or type(record["requested_input_size"]) is not int
        or not 0 <= record["requested_input_size"] <= 134_217_728
        or record["bridge_result"] not in {"QUARANTINE_REQUEST_ACCEPTED", "QUARANTINE_REQUEST_BLOCKED"}
    ):
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Intake bridge fields are invalid")
    accepted = record["candidate_admission_disposition"] in {"ADMITTED_FOR_REVIEW", "REFERENCE_ONLY"}
    if (record["bridge_result"] == "QUARANTINE_REQUEST_ACCEPTED") != accepted:
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Bridge result disagrees with Scout disposition")
    validate_reason_codes(record["reason_codes"], required=not accepted)
    if accepted and record["reason_codes"]:
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Accepted bridge cannot carry failure reasons")
    validate_authority(record["authority"])
    body = {key: _copy(record[key]) for key in record if key not in {"schema_version", "bridge_id"}}
    if record["bridge_id"] != typed_id("bridge", body):
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Bridge identity does not match its semantics")
    canonical_json_bytes(record)
    return _copy(record)


class ValidatedIntakeBridge:
    """Process-local proof that the frozen Scout receipt was revalidated."""

    __slots__ = ("_record", "_seal", "_scout_receipt_sha256", "__weakref__")

    def __init_subclass__(cls, **_kwargs: Any) -> None:
        raise TypeError("ValidatedIntakeBridge is final")

    def __init__(self, record: dict[str, Any], *, token: object) -> None:
        if token is not _CONSTRUCTION_TOKEN:
            raise EcosystemError("SCOUT_RECEIPT_INVALID", "Validated bridge construction is private")
        self._record = validate_intake_bridge_record(record)
        self._scout_receipt_sha256 = self._record["scout_receipt_sha256"]
        self._seal = object()
        _BRIDGE_SEALS[self] = (self._seal, canonical_sha256(self._record))

    @property
    def accepted(self) -> bool:
        _require_validated_bridge(self)
        return self._record["bridge_result"] == "QUARANTINE_REQUEST_ACCEPTED"

    def record(self) -> dict[str, Any]:
        _require_validated_bridge(self)
        return _copy(self._record)


def _require_validated_bridge(value: Any) -> ValidatedIntakeBridge:
    if type(value) is not ValidatedIntakeBridge:
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Validated Slice 2 bridge is required")
    try:
        baseline = _BRIDGE_SEALS.get(value)
        checked = validate_intake_bridge_record(value._record)
    except (AttributeError, EcosystemError, TypeError):
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Validated bridge revalidation failed") from None
    if (
        type(baseline) is not tuple
        or len(baseline) != 2
        or baseline[0] is not value._seal
        or not hmac.compare_digest(baseline[1], canonical_sha256(checked))
    ):
        raise EcosystemError("SCOUT_RECEIPT_INVALID", "Validated bridge integrity changed")
    return value


def bridge_scout_candidate(
    *,
    scout_receipt: Mapping[str, Any],
    candidate_id: str,
    source_key: str,
    requested_input_sha256: str,
    requested_input_size: int,
    policy: TrustedEcosystemSourcePolicy,
) -> ValidatedIntakeBridge:
    """Revalidate one Scout candidate and produce only a quarantine request."""
    trusted = _require_trusted_source_policy(policy)
    validate_sha256(requested_input_sha256, "requested input digest")
    maximum = trusted.resource_limits["max_input_bytes"]
    if type(requested_input_size) is not int or not 0 <= requested_input_size <= maximum:
        raise EcosystemError("RESOURCE_LIMIT_EXCEEDED", "Requested input size is invalid")
    validated_receipt, candidate = _validated_candidate(scout_receipt, candidate_id)
    immutable = candidate["immutable_reference"]
    if (
        type(immutable) is not dict
        or immutable.get("kind") != "git_commit"
        or immutable.get("verification_state") != "verified_at_research_snapshot"
        or type(immutable.get("value")) is not str
        or not re.fullmatch(r"[0-9a-f]{40}", immutable["value"])
    ):
        raise EcosystemError("SCOUT_DISPOSITION_BLOCKED", "Scout candidate lacks a supported immutable commit")
    source = trusted.source(source_key)
    repository = _source_repository_from_candidate(candidate)
    if repository != source["canonical_repository"].casefold() or candidate["identity_key"].casefold() != f"github:{repository}":
        raise EcosystemError("SOURCE_IDENTITY_CONFLICT", "Scout candidate and trusted source policy disagree")
    disposition = candidate["admission_disposition"]
    accepted = disposition in {"ADMITTED_FOR_REVIEW", "REFERENCE_ONLY"}
    body: dict[str, Any] = {
        "scout_receipt_sha256": _scout_receipt_sha256(validated_receipt),
        "scout_id": str(UUID(validated_receipt["scout_id"])),
        "candidate_id": candidate["candidate_id"],
        "candidate_immutable_reference_sha256": canonical_sha256(immutable),
        "commit_object_format": "git_sha1",
        "commit_oid": immutable["value"],
        "candidate_admission_disposition": disposition,
        "source_policy_id": trusted.policy_id,
        "source_policy_semantic_sha256": trusted.policy_semantic_sha256,
        "source_key": source_key,
        "source_id": source["source_id"],
        "requested_input_kind": "pre_supplied_zip",
        "requested_input_sha256": requested_input_sha256,
        "requested_input_size": requested_input_size,
        "bridge_result": "QUARANTINE_REQUEST_ACCEPTED" if accepted else "QUARANTINE_REQUEST_BLOCKED",
        "reason_codes": [] if accepted else ["SCOUT_DISPOSITION_BLOCKED"],
        "authority": zero_authority(),
    }
    record = {
        "schema_version": BRIDGE_SCHEMA_VERSION,
        "bridge_id": typed_id("bridge", body),
        **body,
    }
    return ValidatedIntakeBridge(record, token=_CONSTRUCTION_TOKEN)


def _evaluation_error(code: str, message: str) -> EcosystemError:
    return EcosystemError(code, message)


def _revalidate_revision_subject(
    *,
    subject_record: Mapping[str, Any],
    tree: Mapping[str, Any],
    intake_attempt: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    parent_revision: Mapping[str, Any] | None,
) -> tuple[str, dict[str, Any], dict[str, Any], dict[str, Any], str]:
    """Revalidate a lifecycle subject and every immutable CAS byte it names."""
    from .ecosystem_evidence import (
        _validate_authoritative_component_snapshot,
        _validate_authoritative_revision_snapshot,
    )

    trusted = _require_trusted_source_policy(policy)
    if type(store) is not QuarantineStore:
        raise _evaluation_error("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    if type(subject_record) is not dict:
        raise _evaluation_error("SUBJECT_MISMATCH", "Evaluation subject is malformed")
    if subject_record.get("schema_version") == "nexus.ecosystem-revision.v1":
        checked, checked_tree, checked_attempt = _validate_authoritative_revision_snapshot(
            revision=subject_record,
            tree=tree,
            intake_attempt=intake_attempt,
            store=store,
            policy=trusted,
        )
        parent = checked
        subject_type = "ecosystem_source_revision"
        subject_id = checked["revision_id"]
        creator_sha256 = canonical_sha256(checked_attempt)
    elif subject_record.get("schema_version") == "nexus.ecosystem-component-revision.v1":
        if parent_revision is None:
            raise _evaluation_error("SUBJECT_MISMATCH", "Component evaluation requires its parent")
        checked, parent, checked_tree, _checked_attempt = (
            _validate_authoritative_component_snapshot(
                component=subject_record,
                parent_revision=parent_revision,
                tree=tree,
                intake_attempt=intake_attempt,
                store=store,
                policy=trusted,
            )
        )
        subject_type = "ecosystem_component_revision"
        subject_id = checked["component_revision_id"]
        creator_sha256 = canonical_sha256(checked)
    else:
        raise _evaluation_error("SUBJECT_MISMATCH", "Evaluation subject schema is unsupported")

    return subject_type, dict(checked), dict(checked_tree), dict(parent), creator_sha256


def _revalidate_bridge_subject(
    *,
    subject_record: Mapping[str, Any],
    bridge: ValidatedIntakeBridge,
    scout_receipt: Mapping[str, Any],
    policy: TrustedEcosystemSourcePolicy,
) -> tuple[dict[str, Any], str]:
    trusted = _require_trusted_source_policy(policy)
    current = _require_validated_bridge(bridge).record()
    if type(subject_record) is not dict or dict(subject_record) != current:
        raise _evaluation_error("SUBJECT_MISMATCH", "Bridge subject is not the current sealed bridge")
    validated_scout, _candidate = _validated_candidate(scout_receipt, current["candidate_id"])
    rebuilt = bridge_scout_candidate(
        scout_receipt=validated_scout,
        candidate_id=current["candidate_id"],
        source_key=current["source_key"],
        requested_input_sha256=current["requested_input_sha256"],
        requested_input_size=current["requested_input_size"],
        policy=trusted,
    ).record()
    if rebuilt != current:
        raise _evaluation_error("SCOUT_RECEIPT_INVALID", "Bridge no longer matches its Scout evidence")
    return current, _scout_receipt_sha256(validated_scout)


def _wire_subject(
    *, subject_type: str, subject_id: str, subject_record: Mapping[str, Any], creator_sha256: str
) -> dict[str, Any]:
    prefixes = {
        "ecosystem_source_revision": ("revision", "ecosystem-source-revision"),
        "ecosystem_component_revision": ("component-revision", "ecosystem-component-revision"),
        "ecosystem_revision_comparison": ("comparison", "ecosystem-revision-comparison"),
        "ecosystem_intake_bridge": ("bridge", "ecosystem-intake-bridge"),
    }
    if subject_type not in prefixes:
        raise _evaluation_error("SUBJECT_MISMATCH", "Evaluation subject type is unsupported")
    kind, wire = prefixes[subject_type]
    validate_typed_id(subject_id, kind)
    validate_sha256(creator_sha256, "creator receipt digest")
    digest = subject_id.split("/", 1)[1]
    return {
        "subject_type": subject_type,
        "subject_id": f"{wire}:{digest}",
        "subject_sha256": canonical_sha256(dict(subject_record)),
        "parent_subject_sha256": None,
        "lifecycle": dict(_WIRE_LIFECYCLE),
        "stage_receipts": {
            "creator": creator_sha256,
            "execution": None,
            "reviewer": None,
            "enhancer": None,
            "reporter": None,
        },
    }


def _validate_registry_profile(
    profile: Mapping[str, Any], registry: TrustedValidatorRegistry
) -> None:
    trusted_registry = _require_trusted_registry(registry)
    validator_id = profile["validator_id"]
    expected = _EXPECTED_VALIDATORS.get(validator_id)
    if expected is None:
        raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Evaluation profile is unsupported")
    definition = trusted_registry.resolve(validator_id, profile["validator_version"])
    actual = (
        definition.display_name,
        definition.validator_type,
        definition.operators,
        definition.subject_types,
    )
    if (
        actual != expected
        or list(definition.subject_types) != profile["subject_types"]
        or definition.minimum_checks != 1
        or definition.requires_executed_subject is not False
        or definition.pass_transition != "validation_passed"
        or definition.availability != "available"
        or definition.definition_source != "nexus_core"
    ):
        raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Registry and profile semantics disagree")


def _checked_prior_receipts(
    *,
    supplied: Sequence[Mapping[str, Any]],
    expected_profiles: Sequence[str],
    common: dict[str, Any],
    registry: TrustedValidatorRegistry,
) -> list[dict[str, Any]]:
    if type(supplied) is not list or len(supplied) != len(expected_profiles):
        raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Required evaluation bundle is incomplete")
    checked: list[dict[str, Any]] = []
    for raw, profile_id in zip(supplied, expected_profiles, strict=True):
        try:
            actual = validate_evaluation_receipt(raw, registry=registry)
            expected_request, _evidence_records = _profile_material(
                profile_id=profile_id,
                registry=registry,
                prior_evaluation_receipts=(
                    list(checked)
                    if profile_id == "nexus.profile.ecosystem-validation-bundle"
                    else []
                ),
                prior_transition_receipts=[],
                **common,
            )
            expected = evaluate_contract(expected_request, registry=registry)
        except (EvaluationError, TypeError, ValueError) as exc:
            raise _evaluation_error(
                "EVALUATION_RECEIPT_INVALID", "Required evaluation receipt is invalid"
            ) from None
        if actual != expected:
            raise _evaluation_error(
                "EVALUATION_RECEIPT_INVALID", "Required evaluation receipt is stale or reordered"
            )
        checked.append(actual)
    return checked


def _profile_material(
    *,
    profile_id: str,
    subject_record: Mapping[str, Any],
    policy: TrustedEcosystemSourcePolicy,
    registry: TrustedValidatorRegistry,
    store: QuarantineStore | None = None,
    tree: Mapping[str, Any] | None = None,
    parent_revision: Mapping[str, Any] | None = None,
    intake_attempt: Mapping[str, Any] | None = None,
    provenance_evidence: Mapping[str, Any] | None = None,
    license_evidence: Mapping[str, Any] | None = None,
    static_findings: list[Mapping[str, Any]] | None = None,
    static_report: Mapping[str, Any] | None = None,
    components: list[Mapping[str, Any]] | None = None,
    classifications: list[Mapping[str, Any]] | None = None,
    classification_report: Mapping[str, Any] | None = None,
    prior_evaluation_receipts: Sequence[Mapping[str, Any]] = (),
    prior_transition_receipts: Sequence[Mapping[str, Any]] = (),
    comparison_inputs: Mapping[str, Any] | None = None,
    bridge: ValidatedIntakeBridge | None = None,
    scout_receipt: Mapping[str, Any] | None = None,
    _validated_lineage: Sequence[Mapping[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from .ecosystem_compare import validate_revision_comparison
    from .ecosystem_evidence import (
        validate_component_classification,
        validate_license_evidence,
        validate_provenance_evidence,
        validate_static_evidence,
    )

    trusted = _require_trusted_source_policy(policy)
    trusted_registry = _require_trusted_registry(registry)
    if store is not None:
        if type(store) is not QuarantineStore:
            raise _evaluation_error("CAS_ROOT_INVALID", "Trusted quarantine store is required")
        store._require_policy(trusted)
        store._require_registry(trusted_registry)
    profile, profile_sha256 = trusted.evaluation_profile(profile_id)
    _validate_registry_profile(profile, trusted_registry)
    validator_id = profile["validator_id"]
    evidence_records: list[dict[str, Any]] = []
    common = {
        "subject_record": subject_record,
        "policy": trusted,
        "store": store,
        "tree": tree,
        "parent_revision": parent_revision,
        "intake_attempt": intake_attempt,
        "provenance_evidence": provenance_evidence,
        "license_evidence": license_evidence,
        "static_findings": static_findings,
        "static_report": static_report,
        "components": components,
        "classifications": classifications,
        "classification_report": classification_report,
        "comparison_inputs": comparison_inputs,
        "bridge": bridge,
        "scout_receipt": scout_receipt,
    }

    if profile_id in _NO_STATE_PROFILES:
        if profile_id == "nexus.profile.ecosystem-comparison-consistency":
            if type(comparison_inputs) is not dict:
                raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Comparison inputs are incomplete")
            try:
                checked_subject = validate_revision_comparison(
                    subject_record, **dict(comparison_inputs)
                )
            except (EcosystemError, TypeError):
                raise _evaluation_error("SUBJECT_MISMATCH", "Comparison evidence is not current") from None
            if checked_subject["comparison_result"] == "INSUFFICIENT_EVIDENCE":
                raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Comparison evidence is incomplete")
            subject_type = "ecosystem_revision_comparison"
            subject_id = checked_subject["comparison_id"]
            creator = canonical_sha256(checked_subject)
            projected = canonical_sha256(checked_subject)
        else:
            if bridge is None or scout_receipt is None:
                raise _evaluation_error("SCOUT_RECEIPT_INVALID", "Bridge evidence is incomplete")
            checked_subject, creator = _revalidate_bridge_subject(
                subject_record=subject_record,
                bridge=bridge,
                scout_receipt=scout_receipt,
                policy=trusted,
            )
            subject_type = "ecosystem_intake_bridge"
            subject_id = checked_subject["bridge_id"]
            projected = canonical_sha256(checked_subject)
        values = {profile["required_checks"][0]["check_id"]: (projected, projected)}
    else:
        if store is None or tree is None or intake_attempt is None:
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Evaluation subject inputs are incomplete")
        subject_type, checked_subject, checked_tree, checked_parent, creator = (
            _revalidate_revision_subject(
                subject_record=subject_record,
                tree=tree,
                intake_attempt=intake_attempt,
                store=store,
                policy=trusted,
                parent_revision=parent_revision,
            )
        )
        subject_id = (
            checked_subject["revision_id"]
            if subject_type == "ecosystem_source_revision"
            else checked_subject["component_revision_id"]
        )
        if subject_type not in profile["subject_types"]:
            raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Profile does not apply to subject")
        if provenance_evidence is None:
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Exact provenance evidence is required")
        checked_provenance = validate_provenance_evidence(
            provenance_evidence,
            revision=checked_parent,
            tree=checked_tree,
            intake_attempt=intake_attempt,
            store=store,
            policy=trusted,
        )
        evidence_records.append(checked_provenance)
        if checked_provenance["result"] != "EXACT_SUBJECT_BOUND":
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Provenance is not exact-subject bound")

        values: dict[str, tuple[Any, Any]]
        if validator_id == "nexus.validator.ecosystem-provenance":
            values = {"subject-digest": (None, canonical_sha256(checked_subject))}
        elif validator_id == "nexus.validator.ecosystem-static-security":
            if license_evidence is None or static_findings is None or static_report is None:
                raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Static evidence is incomplete")
            checked_license = validate_license_evidence(
                license_evidence,
                subject_record=checked_subject,
                tree=checked_tree,
                store=store,
                policy=trusted,
                parent_revision=checked_parent if subject_type == "ecosystem_component_revision" else None,
            )
            checked_findings, checked_report = validate_static_evidence(
                static_findings,
                static_report,
                subject_id=subject_id,
                subject_record=checked_subject,
                tree=checked_tree,
                store=store,
                policy=trusted,
                parent_revision=checked_parent if subject_type == "ecosystem_component_revision" else None,
                provenance_evidence=checked_provenance,
                license_evidence=checked_license,
                intake_attempt=intake_attempt,
                analyzer_available=True,
            )
            if (
                checked_report["analysis_status"] != "COMPLETE"
                or checked_report["counts"]["blocking"] != 0
                or checked_report["counts"]["rejecting"] != 0
            ):
                raise _evaluation_error("STATIC_FINDING_BLOCKING", "Static profile is not complete and nonblocking")
            evidence_records.extend([checked_license, checked_report, *checked_findings])
            values = {
                "analysis-status": ("COMPLETE", checked_report["analysis_status"]),
                "analyzer-config": (
                    trusted.static_analyzer_config_sha256,
                    checked_report["analyzer_config_sha256"],
                ),
                "blocking-findings": (0, checked_report["counts"]["blocking"]),
                "rejecting-findings": (0, checked_report["counts"]["rejecting"]),
            }
        elif validator_id == "nexus.validator.ecosystem-classification":
            if components is None or classifications is None or classification_report is None:
                raise _evaluation_error("CLASSIFICATION_UNRESOLVED", "Classification evidence is incomplete")
            checked_components, checked_classifications, checked_report = (
                validate_component_classification(
                    components,
                    classifications,
                    classification_report,
                    revision=checked_parent,
                    tree=checked_tree,
                    store=store,
                    policy=trusted,
                )
            )
            if (
                subject_type == "ecosystem_component_revision"
                and [
                    item
                    for item in checked_components
                    if item["component_revision_id"] == subject_id
                ]
                != [checked_subject]
            ):
                raise _evaluation_error(
                    "CLASSIFICATION_UNRESOLVED", "Component is absent from the current classification"
                )
            if checked_report["report_status"] != "COMPLETE" or checked_report["unresolved_path_sha256s"]:
                raise _evaluation_error("CLASSIFICATION_UNRESOLVED", "Classification profile is incomplete")
            evidence_records.extend([checked_report, *checked_classifications, *checked_components])
            values = {
                "classification-status": ("COMPLETE", checked_report["report_status"]),
                "classifier-config": (
                    trusted.component_classifier_config_sha256,
                    checked_report["classifier_config_sha256"],
                ),
                "unresolved-paths": ([], checked_report["unresolved_path_sha256s"]),
            }
        elif validator_id == "nexus.validator.ecosystem-validation-bundle":
            checked_prior = _checked_prior_receipts(
                supplied=prior_evaluation_receipts,
                expected_profiles=_REVIEW_PROFILE_ORDER[:3],
                common=common,
                registry=trusted_registry,
            )
            bundle = [evaluation_canonical_sha256(item) for item in checked_prior]
            values = {"required-receipts": (bundle, bundle)}
        elif validator_id == "nexus.validator.ecosystem-review-bundle":
            checked_prior = _checked_prior_receipts(
                supplied=prior_evaluation_receipts,
                expected_profiles=_REVIEW_PROFILE_ORDER[:4],
                common=common,
                registry=trusted_registry,
            )
            if type(prior_transition_receipts) is not list or len(prior_transition_receipts) != 4:
                raise _evaluation_error("STATE_TRANSITION_INVALID", "Review transition bundle is incomplete")
            if _validated_lineage is None:
                lineage = load_state_lineage(
                    store=store,
                    subject_id=subject_id,
                    subject_sha256=canonical_sha256(checked_subject),
                    policy=trusted,
                    registry=trusted_registry,
                )
            else:
                if type(_validated_lineage) is not list:
                    raise _evaluation_error(
                        "STATE_TRANSITION_INVALID", "Validated lineage projection is malformed"
                    )
                lineage = [dict(item) for item in _validated_lineage]
            review_transitions = [
                item["transition"]
                for item in lineage
                if item["transition"]["transition_axis"] in {"review", "review_evidence_terminal"}
            ]
            checked_transitions = [validate_transition_receipt(item) for item in prior_transition_receipts]
            if review_transitions != checked_transitions or len(review_transitions) != 4:
                raise _evaluation_error("STATE_TRANSITION_INVALID", "Review transition bundle is stale or reordered")
            for index, (transition, evaluation_receipt) in enumerate(
                zip(checked_transitions, checked_prior, strict=True)
            ):
                if (
                    transition["evaluation_profile_id"] != _REVIEW_PROFILE_ORDER[index]
                    or transition["evaluation_receipt_sha256s"]
                    != [evaluation_canonical_sha256(evaluation_receipt)]
                ):
                    raise _evaluation_error("STATE_TRANSITION_INVALID", "Review lineage evidence is inconsistent")
            evidence_records.extend(checked_transitions)
            values = {"prior-review-state": (None, dict(_WIRE_LIFECYCLE))}
        else:
            raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Evaluation profile is unsupported")

    wire = _wire_subject(
        subject_type=subject_type,
        subject_id=subject_id,
        subject_record=checked_subject,
        creator_sha256=creator,
    )
    if subject_type not in profile["subject_types"]:
        raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Profile subject type is inconsistent")
    checks: list[dict[str, Any]] = []
    if [item["check_id"] for item in profile["required_checks"]] != sorted(values):
        raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Profile check semantics are incomplete")
    for check in profile["required_checks"]:
        expected, observed = values[check["check_id"]]
        checks.append(
            {
                "check_id": check["check_id"],
                "operator": check["operator"],
                "required": True,
                "expected": expected,
                "observed": observed,
                "evidence": {
                    "evidence_id": check["evidence_id"],
                    "content_sha256": evaluation_canonical_sha256(observed),
                    "summary": f"Slice 3C {check['evidence_id']} digest evidence",
                },
            }
        )
    request = {
        "schema_version": "nexus.evaluation-request.v1",
        "validator_id": validator_id,
        "validator_version": profile["validator_version"],
        "subject": wire,
        "checks": checks,
    }
    canonical_json_bytes(request, maximum_bytes=65_536)
    validate_sha256(profile_sha256, "evaluation profile digest")
    return request, evidence_records


def build_ecosystem_evaluation_request(**profile_inputs: Any) -> dict[str, Any]:
    """Build one exact seven-profile Slice 3B request from current evidence."""
    request, _evidence_records = _profile_material(**profile_inputs)
    return _copy(request)


class ValidatedTransitionProposal:
    """Process-local proof of a revalidated, unapplied Slice 3C transition."""

    __slots__ = ("_transition", "_seal", "__weakref__")

    def __init_subclass__(cls, **_kwargs: Any) -> None:
        raise TypeError("ValidatedTransitionProposal is final")

    def __init__(
        self,
        transition: dict[str, Any],
        *,
        predecessor_state_record_id: str | None,
        evidence_records: Sequence[Mapping[str, Any]],
        evaluation_receipts: Sequence[Mapping[str, Any]],
        token: object,
    ) -> None:
        if token is not _PROPOSAL_TOKEN:
            raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition proposal construction is private")
        checked = validate_transition_receipt(transition)
        if predecessor_state_record_id is not None:
            validate_typed_id(predecessor_state_record_id, "state-record")
        evidence_baseline = _evidence_baseline(checked["evidence_ids"], evidence_records)
        evaluation_baseline = _evaluation_baseline(
            checked["evaluation_receipt_sha256s"], evaluation_receipts
        )
        self._transition = checked
        self._seal = object()
        _PROPOSAL_SEALS[self] = (
            self._seal,
            canonical_sha256(checked),
            predecessor_state_record_id,
            evidence_baseline,
            evaluation_baseline,
        )

    def record(self) -> dict[str, Any]:
        _require_transition_proposal(self)
        return _copy(self._transition)


def _evidence_baseline(
    evidence_ids: Sequence[str], evidence_records: Sequence[Mapping[str, Any]]
) -> tuple[tuple[str, str], ...]:
    if type(evidence_records) is not list:
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition evidence records are invalid")
    by_id: dict[str, dict[str, Any]] = {}
    for record in evidence_records:
        if type(record) is not dict:
            raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition evidence record is malformed")
        primary = _record_primary_id(record)
        if primary in by_id:
            raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition evidence identity is duplicated")
        by_id[primary] = dict(record)
    if set(by_id) != set(evidence_ids) or len(evidence_records) != len(evidence_ids):
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition evidence contains undeclared records")
    return tuple((item, canonical_sha256(by_id[item])) for item in evidence_ids)


def _evaluation_baseline(
    receipt_sha256s: Sequence[str], receipts: Sequence[Mapping[str, Any]]
) -> tuple[tuple[str, str], ...]:
    if type(receipts) is not list or len(receipts) != len(receipt_sha256s):
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition evaluation receipts are incomplete")
    result: list[tuple[str, str]] = []
    for expected, receipt in zip(receipt_sha256s, receipts, strict=True):
        if type(receipt) is not dict:
            raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Evaluation receipt is malformed")
        actual = evaluation_canonical_sha256(receipt)
        if actual != expected:
            raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Evaluation receipt digest is inconsistent")
        result.append((expected, actual))
    return tuple(result)


def _require_transition_proposal(value: Any) -> tuple[Any, ...]:
    if type(value) is not ValidatedTransitionProposal:
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Validated transition proposal is required")
    try:
        baseline = _PROPOSAL_SEALS.get(value)
        checked = validate_transition_receipt(value._transition)
    except (AttributeError, EcosystemError, TypeError):
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition proposal revalidation failed") from None
    if (
        type(baseline) is not tuple
        or len(baseline) != 5
        or baseline[0] is not value._seal
        or not hmac.compare_digest(baseline[1], canonical_sha256(checked))
    ):
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition proposal integrity changed")
    return baseline


def _validate_state_evidence_record(
    *,
    expected_id: str,
    record: Mapping[str, Any],
    checked_subject: Mapping[str, Any],
    checked_tree: Mapping[str, Any],
    checked_attempt: Mapping[str, Any],
    parent_revision: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
) -> dict[str, Any]:
    """Validate one state-cited record against the current immutable subject."""
    from .ecosystem_evidence import (
        _STATIC_RULES,
        _validate_component_record,
        _validate_intake_attempt,
        _validate_tree,
        validate_license_evidence,
        validate_provenance_evidence,
    )

    if type(record) is not dict or _record_primary_id(record) != expected_id:
        raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Evidence locator is inconsistent")
    subject_id = (
        checked_subject["revision_id"]
        if checked_subject.get("schema_version") == "nexus.ecosystem-revision.v1"
        else checked_subject["component_revision_id"]
    )
    subject_sha256 = canonical_sha256(dict(checked_subject))
    schema = record.get("schema_version")
    if expected_id.startswith("tree/"):
        if _validate_tree(record) != dict(checked_tree):
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Tree evidence is stale")
        return dict(record)
    if expected_id.startswith("intake-attempt-result/"):
        checked = _validate_intake_attempt(record, revision=parent_revision, policy=policy)
        if checked != dict(checked_attempt):
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Intake evidence is stale")
        return checked
    if expected_id.startswith("component-revision/"):
        checked = _validate_component_record(
            record, revision=parent_revision, tree=checked_tree, policy=policy
        )
        if (
            checked_subject.get("schema_version") == "nexus.ecosystem-component-revision.v1"
            and checked != dict(checked_subject)
        ):
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Component evidence is stale")
        return checked
    if expected_id.startswith("transition/"):
        checked = validate_transition_receipt(record)
        if (
            checked["subject_id"] != subject_id
            or checked["subject_sha256"] != subject_sha256
            or checked["policy_semantic_sha256"] != policy.policy_semantic_sha256
        ):
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Transition evidence is stale")
        return checked
    if schema == "nexus.ecosystem-provenance-evidence.v1":
        return validate_provenance_evidence(
            record,
            revision=parent_revision,
            tree=checked_tree,
            intake_attempt=checked_attempt,
            store=store,
            policy=policy,
        )
    if schema == "nexus.ecosystem-license-evidence.v1":
        evidence_subject = record.get("subject_id")
        if evidence_subject == subject_id:
            target = checked_subject
            parent = (
                parent_revision
                if checked_subject.get("schema_version")
                == "nexus.ecosystem-component-revision.v1"
                else None
            )
        elif evidence_subject == parent_revision.get("revision_id"):
            target = parent_revision
            parent = None
        else:
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "License evidence subject is stale")
        return validate_license_evidence(
            record,
            subject_record=target,
            tree=checked_tree,
            store=store,
            policy=policy,
            parent_revision=parent,
        )
    identity_schemas = {
        "nexus.ecosystem-static-finding.v1": (
            "finding_id",
            "finding",
            ID_DOMAINS["finding"],
        ),
        "nexus.ecosystem-static-report.v1": (
            "report_id",
            "static-report",
            ID_DOMAINS["static-report"],
        ),
        "nexus.ecosystem-component-classification.v1": (
            "classification_id",
            "classification",
            ID_DOMAINS["classification"],
        ),
        "nexus.ecosystem-classification-report.v1": (
            "report_id",
            "classification-report",
            ID_DOMAINS["classification-report"],
        ),
    }
    identity = identity_schemas.get(schema)
    if identity is None:
        raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Evidence schema is unsupported")
    checked = validate_identity_record(
        record, id_field=identity[0], kind=identity[1], domain=identity[2]
    )
    validate_authority(checked.get("authority"))
    if schema in {
        "nexus.ecosystem-static-finding.v1",
        "nexus.ecosystem-static-report.v1",
    }:
        if (
            checked.get("subject_id") != subject_id
            or checked.get("subject_sha256") != subject_sha256
            or checked.get("analyzer_config_sha256") != policy.static_analyzer_config_sha256
        ):
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Static evidence is stale")
        if schema == "nexus.ecosystem-static-finding.v1":
            rule = _STATIC_RULES.get(checked.get("rule_id"))
            if rule is None or tuple(checked.get(key) for key in ("category", "severity", "disposition")) != rule:
                raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Static finding semantics are invalid")
    else:
        if (
            checked.get("revision_id", checked.get("subject_id"))
            != parent_revision["revision_id"]
        ):
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Classification evidence is stale")
        if (
            schema == "nexus.ecosystem-classification-report.v1"
            and checked.get("classifier_config_sha256")
            != policy.component_classifier_config_sha256
        ):
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Classification profile is stale")
    return checked


def _load_lineage_unlocked(
    *,
    store: QuarantineStore,
    subject_id: str,
    subject_sha256: str,
    policy: TrustedEcosystemSourcePolicy,
    registry: TrustedValidatorRegistry | None = None,
    allow_missing: bool = False,
) -> list[dict[str, Any]]:
    trusted = _require_trusted_source_policy(policy)
    if type(store) is not QuarantineStore:
        raise _evaluation_error("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    store._require_policy(trusted)
    trusted_registry = None if registry is None else _require_trusted_registry(registry)
    if trusted_registry is not None:
        store._require_registry(trusted_registry)
    validate_typed_id(subject_id)
    validate_sha256(subject_sha256, "state subject digest")
    try:
        from .ecosystem_evidence import (
            _validate_authoritative_component_snapshot,
            _validate_authoritative_revision_snapshot,
            _validate_component_record,
            _validate_intake_attempt,
            _validate_tree,
        )

        maximum = trusted.resource_limits["max_record_bytes"]
        if subject_id.startswith("revision/"):
            subject_record = store.read_record(
                f"revisions/sha256/{subject_id.split('/', 1)[1]}.json",
                maximum_bytes=maximum,
            )
            tree_id = subject_record.get("tree_id")
            validate_typed_id(tree_id, "tree")
            tree_record = store.read_record(
                f"trees/sha256/{tree_id.split('/', 1)[1]}.json",
                maximum_bytes=maximum,
            )
            checked_subject, checked_tree, checked_attempt = (
                _validate_authoritative_revision_snapshot(
                    revision=subject_record,
                    tree=tree_record,
                    store=store,
                    policy=trusted,
                )
            )
            parent_revision = checked_subject
            component_record = None
            creator_sha256 = canonical_sha256(checked_attempt)
        elif subject_id.startswith("component-revision/"):
            component_record = store.read_record(
                f"components/sha256/{subject_id.split('/', 1)[1]}.json",
                maximum_bytes=maximum,
            )
            revision_id = component_record.get("revision_id")
            validate_typed_id(revision_id, "revision")
            parent_candidate = store.read_record(
                f"revisions/sha256/{revision_id.split('/', 1)[1]}.json",
                maximum_bytes=maximum,
            )
            tree_id = parent_candidate.get("tree_id")
            validate_typed_id(tree_id, "tree")
            tree_candidate = store.read_record(
                f"trees/sha256/{tree_id.split('/', 1)[1]}.json",
                maximum_bytes=maximum,
            )
            checked_subject, parent_revision, checked_tree, checked_attempt = (
                _validate_authoritative_component_snapshot(
                    component=component_record,
                    parent_revision=parent_candidate,
                    tree=tree_candidate,
                    store=store,
                    policy=trusted,
                )
            )
            creator_sha256 = canonical_sha256(checked_subject)
        else:
            raise _evaluation_error(
                "STATE_TRANSITION_INVALID", "State lineage subject type is forbidden"
            )
    except EcosystemError:
        raise _evaluation_error(
            "PROVENANCE_INSUFFICIENT", "Current immutable subject evidence is unavailable"
        ) from None
    if canonical_sha256(checked_subject) != subject_sha256:
        raise _evaluation_error("STATE_TRANSITION_INVALID", "State subject digest is stale")

    names = store.list_record_names("state/sha256", maximum_count=_MAX_STATE_RECORDS)
    records: dict[str, dict[str, Any]] = {}
    transitions: dict[str, dict[str, Any]] = {}
    state_evidence: dict[str, dict[str, dict[str, Any]]] = {}
    state_evaluations: dict[str, list[dict[str, Any]]] = {}
    for name in names:
        raw = store.read_record(f"state/sha256/{name}", maximum_bytes=trusted.resource_limits["max_record_bytes"])
        checked = validate_state_record(raw)
        if name[:-5] != checked["state_record_id"].split("/", 1)[1]:
            raise _evaluation_error("STATE_TRANSITION_INVALID", "State record locator is inconsistent")
        if checked["subject_id"] != subject_id:
            continue
        if checked["state_record_id"] in records:
            raise _evaluation_error("STATE_TRANSITION_INVALID", "State lineage contains a duplicate")
        records[checked["state_record_id"]] = checked
    if not records:
        if allow_missing:
            return []
        raise _evaluation_error("STATE_TRANSITION_INVALID", "State lineage is absent")
    if len(records) > _MAX_SUBJECT_LINEAGE:
        raise _evaluation_error("RESOURCE_LIMIT_EXCEEDED", "State lineage exceeds its bound")

    children: dict[str, list[str]] = {item: [] for item in records}
    genesis: list[str] = []
    for state_id, record in records.items():
        if (
            record["subject_sha256"] != subject_sha256
            or record["policy_semantic_sha256"] != trusted.policy_semantic_sha256
        ):
            raise _evaluation_error("STATE_TRANSITION_INVALID", "State lineage subject or policy is stale")
        transition_id = record["transition_id"]
        transition_digest = transition_id.split("/", 1)[1]
        transition = validate_transition_receipt(
            store.read_record(
                f"evidence/sha256/{transition_digest}.json",
                maximum_bytes=trusted.resource_limits["max_record_bytes"],
            )
        )
        transitions[state_id] = transition
        state_evidence[state_id] = {}
        state_evaluations[state_id] = []
        try:
            for evidence_id in transition["evidence_ids"]:
                evidence_record = store.read_record(
                    f"evidence/sha256/{evidence_id.split('/', 1)[1]}.json",
                    maximum_bytes=trusted.resource_limits["max_record_bytes"],
                )
                state_evidence[state_id][evidence_id] = _validate_state_evidence_record(
                    expected_id=evidence_id,
                    record=evidence_record,
                    checked_subject=checked_subject,
                    checked_tree=checked_tree,
                    checked_attempt=checked_attempt,
                    parent_revision=parent_revision,
                    store=store,
                    policy=trusted,
                )
            for receipt_digest in transition["evaluation_receipt_sha256s"]:
                if trusted_registry is None:
                    raise _evaluation_error(
                        "PROVENANCE_INSUFFICIENT",
                        "Trusted validator registry is required for current review evidence",
                    )
                receipt = store.read_record(
                    f"evidence/sha256/{receipt_digest}.json",
                    maximum_bytes=trusted.resource_limits["max_record_bytes"],
                )
                if evaluation_canonical_sha256(receipt) != receipt_digest:
                    raise _evaluation_error(
                        "PROVENANCE_INSUFFICIENT", "Evaluation evidence digest is stale"
                    )
                checked_receipt = validate_evaluation_receipt(
                    receipt,
                    registry=trusted_registry,
                    expected_subject_id=_wire_subject(
                        subject_type=(
                            "ecosystem_source_revision"
                            if checked_subject.get("schema_version") == "nexus.ecosystem-revision.v1"
                            else "ecosystem_component_revision"
                        ),
                        subject_id=subject_id,
                        subject_record=checked_subject,
                        creator_sha256=creator_sha256,
                    )["subject_id"],
                    expected_subject_sha256=subject_sha256,
                )
                state_evaluations[state_id].append(checked_receipt)
        except (EcosystemError, EvaluationError, TypeError, ValueError):
            raise _evaluation_error(
                "PROVENANCE_INSUFFICIENT", "Current state evidence is unavailable"
            ) from None
        if (
            transition["transition_id"] != transition_id
            or transition["subject_id"] != subject_id
            or transition["subject_sha256"] != subject_sha256
            or transition["policy_semantic_sha256"] != trusted.policy_semantic_sha256
            or transition["to_state"] != record["state"]
            or transition["evidence_ids"] != record["evidence_ids"]
            or build_state_record(
                subject_id=subject_id,
                subject_sha256=subject_sha256,
                previous_state_record_id=record["previous_state_record_id"],
                transition=transition,
            )
            != record
        ):
            raise _evaluation_error("STATE_TRANSITION_INVALID", "State record and transition disagree")
        parent = record["previous_state_record_id"]
        if parent is None:
            genesis.append(state_id)
        elif parent not in records:
            raise _evaluation_error("STATE_TRANSITION_INVALID", "State lineage parent is missing")
        else:
            children[parent].append(state_id)
            if transition["from_state"] != records[parent]["state"]:
                raise _evaluation_error("STATE_TRANSITION_INVALID", "State transition predecessor is stale")
    if len(genesis) != 1 or any(len(items) > 1 for items in children.values()):
        raise _evaluation_error("STATE_TRANSITION_INVALID", "State lineage is branched or lacks one genesis")
    heads = [item for item, nested in children.items() if not nested]
    if len(heads) != 1:
        raise _evaluation_error("STATE_TRANSITION_INVALID", "State lineage has multiple heads")
    ordered_ids: list[str] = []
    cursor: str | None = heads[0]
    visited: set[str] = set()
    while cursor is not None:
        if cursor in visited:
            raise _evaluation_error("STATE_TRANSITION_INVALID", "State lineage contains a cycle")
        visited.add(cursor)
        ordered_ids.append(cursor)
        cursor = records[cursor]["previous_state_record_id"]
    if len(visited) != len(records) or ordered_ids[-1] != genesis[0]:
        raise _evaluation_error("STATE_TRANSITION_INVALID", "State lineage is disconnected")
    ordered_ids.reverse()
    ordered = [
        {"state_record": records[item], "transition": transitions[item]}
        for item in ordered_ids
    ]
    prior_evidence_ids: set[str] = set()
    for state_id in ordered_ids:
        transition = transitions[state_id]
        if transition["transition_axis"] in {"evidence_outcome", "disposition"}:
            _validate_transition_evidence_bundle(
                transition=transition,
                records=[
                    state_evidence[state_id][evidence_id]
                    for evidence_id in transition["evidence_ids"]
                ],
                checked_subject=checked_subject,
                checked_tree=checked_tree,
                checked_attempt=checked_attempt,
                parent_revision=parent_revision,
                store=store,
                policy=trusted,
                prior_evidence_ids=prior_evidence_ids,
            )
        prior_evidence_ids.update(transition["evidence_ids"])
    prior_receipts: list[dict[str, Any]] = []
    prior_transitions: list[dict[str, Any]] = []
    current_provenance: dict[str, Any] | None = None
    for index, state_id in enumerate(ordered_ids):
        transition = transitions[state_id]
        if transition["transition_axis"] not in {"review", "review_evidence_terminal"}:
            continue
        if trusted_registry is None:
            raise _evaluation_error(
                "PROVENANCE_INSUFFICIENT", "Trusted validator registry is required for review lineage"
            )
        review_index = len(prior_receipts)
        if review_index >= len(_REVIEW_PROFILE_ORDER):
            raise _evaluation_error("STATE_TRANSITION_INVALID", "Review lineage has extra edges")
        profile_id = _REVIEW_PROFILE_ORDER[review_index]
        profile, profile_sha256 = trusted.evaluation_profile(profile_id)
        receipts = state_evaluations[state_id]
        if (
            transition["evaluation_profile_id"] != profile_id
            or transition["evaluation_profile_sha256"] != profile_sha256
            or len(receipts) != 1
            or transition["evaluation_receipt_sha256s"]
            != [evaluation_canonical_sha256(receipts[0])]
        ):
            raise _evaluation_error(
                "EVALUATION_RECEIPT_INVALID", "Review transition profile evidence is inconsistent"
            )
        cited = state_evidence[state_id]
        if review_index == 0:
            candidates = [
                item
                for item in cited.values()
                if item.get("schema_version") == "nexus.ecosystem-provenance-evidence.v1"
            ]
            if len(candidates) != 1:
                raise _evaluation_error(
                    "PROVENANCE_INSUFFICIENT", "Review provenance evidence is incomplete"
                )
            current_provenance = candidates[0]
        if current_provenance is None:
            raise _evaluation_error(
                "PROVENANCE_INSUFFICIENT", "Review lineage lacks current provenance evidence"
            )
        from .ecosystem_evidence import (
            analyze_static_evidence,
            classify_components,
            inspect_license_evidence,
        )

        try:
            license_evidence = inspect_license_evidence(
                subject_id=subject_id,
                subject_record=checked_subject,
                tree=checked_tree,
                store=store,
                policy=trusted,
                parent_revision=(
                    parent_revision
                    if checked_subject.get("schema_version")
                    == "nexus.ecosystem-component-revision.v1"
                    else None
                ),
            )
            findings, static_report = analyze_static_evidence(
                subject_id=subject_id,
                subject_record=checked_subject,
                tree=checked_tree,
                store=store,
                policy=trusted,
                parent_revision=(
                    parent_revision
                    if checked_subject.get("schema_version")
                    == "nexus.ecosystem-component-revision.v1"
                    else None
                ),
                provenance_evidence=current_provenance,
                license_evidence=license_evidence,
                intake_attempt=checked_attempt,
            )
            components, classifications, classification_report = classify_components(
                revision=parent_revision,
                tree=checked_tree,
                store=store,
                policy=trusted,
            )
        except Exception:
            # Current-use review validation is a closed trust boundary.  A
            # missing or failed analyzer/classifier cannot demote immutable
            # history, leak an interpreter exception, or make old PASS
            # evidence current; consumption simply becomes insufficient.
            raise _evaluation_error(
                "PROVENANCE_INSUFFICIENT", "Current review analyzer evidence is unavailable"
            ) from None
        expected_evidence_ids = (
            [current_provenance["evidence_id"]]
            if review_index in {0, 3}
            else [static_report["report_id"]]
            if review_index == 1
            else [classification_report["report_id"]]
            if review_index == 2
            else sorted(item["transition_id"] for item in prior_transitions)
        )
        if transition["evidence_ids"] != sorted(expected_evidence_ids):
            raise _evaluation_error(
                "PROVENANCE_INSUFFICIENT", "Review transition cites stale or incomplete evidence"
            )
        request, _records = _profile_material(
            profile_id=profile_id,
            subject_record=checked_subject,
            policy=trusted,
            registry=trusted_registry,
            store=store,
            tree=checked_tree,
            parent_revision=(
                parent_revision
                if checked_subject.get("schema_version")
                == "nexus.ecosystem-component-revision.v1"
                else None
            ),
            intake_attempt=checked_attempt,
            provenance_evidence=current_provenance,
            license_evidence=license_evidence,
            static_findings=findings,
            static_report=static_report,
            components=components,
            classifications=classifications,
            classification_report=classification_report,
            prior_evaluation_receipts=list(prior_receipts),
            prior_transition_receipts=list(prior_transitions),
            _validated_lineage=ordered[:index],
        )
        expected_receipt = evaluate_contract(request, registry=trusted_registry)
        if receipts[0] != expected_receipt or receipts[0]["result"]["state"] != "PASS":
            raise _evaluation_error(
                "EVALUATION_RECEIPT_INVALID", "Review receipt is not the complete current profile"
            )
        prior_receipts.append(receipts[0])
        prior_transitions.append(transition)
    return ordered


def load_state_lineage(
    *,
    store: QuarantineStore,
    subject_id: str,
    subject_sha256: str,
    policy: TrustedEcosystemSourcePolicy,
    registry: TrustedValidatorRegistry | None = None,
) -> list[dict[str, Any]]:
    """Return a fully revalidated, single-head immutable lineage."""
    if type(store) is not QuarantineStore:
        raise _evaluation_error("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    with store._exclusive("state.lock"):
        return _copy(
            _load_lineage_unlocked(
                store=store,
                subject_id=subject_id,
                subject_sha256=subject_sha256,
                policy=policy,
                registry=registry,
            )
        )


def _make_proposal(
    *,
    transition: dict[str, Any],
    predecessor_state_record_id: str | None,
    evidence_records: list[Mapping[str, Any]],
    evaluation_receipts: list[Mapping[str, Any]],
) -> ValidatedTransitionProposal:
    return ValidatedTransitionProposal(
        transition,
        predecessor_state_record_id=predecessor_state_record_id,
        evidence_records=evidence_records,
        evaluation_receipts=evaluation_receipts,
        token=_PROPOSAL_TOKEN,
    )


def adapt_evaluation_receipt(
    *, evaluation_receipt: Mapping[str, Any], **profile_inputs: Any
) -> ValidatedTransitionProposal | None:
    """Rebind a Slice 3B receipt to an exact profile and propose, never apply, an edge."""
    profile_id = profile_inputs.get("profile_id")
    policy = profile_inputs.get("policy")
    registry = profile_inputs.get("registry")
    if type(profile_id) is not str:
        raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Evaluation profile identity is invalid")
    trusted = _require_trusted_source_policy(policy)
    trusted_registry = _require_trusted_registry(registry)
    request, evidence_records = _profile_material(**profile_inputs)
    try:
        checked = validate_evaluation_receipt(
            evaluation_receipt,
            registry=trusted_registry,
            expected_subject_id=request["subject"]["subject_id"],
            expected_subject_sha256=request["subject"]["subject_sha256"],
        )
    except (EvaluationError, TypeError, ValueError):
        raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Evaluation receipt failed revalidation") from None
    if checked["result"]["state"] != "PASS":
        raise _evaluation_error("EVALUATION_RESULT_BLOCKED", "Only an exact PASS can support review")
    expected = evaluate_contract(request, registry=trusted_registry)
    if checked != expected:
        raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Evaluation receipt does not match the complete profile")
    native = checked["state_transition"]
    if native != {
        "from_validation_state": "not_validated",
        "to_validation_state": "validation_passed",
        "permitted": True,
        "applied": False,
    }:
        raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Slice 3B validation transition is invalid")
    if profile_id in _NO_STATE_PROFILES:
        return None

    store = profile_inputs.get("store")
    if type(store) is not QuarantineStore:
        raise _evaluation_error("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    subject_record = profile_inputs["subject_record"]
    subject_id = (
        subject_record["revision_id"]
        if subject_record.get("schema_version") == "nexus.ecosystem-revision.v1"
        else subject_record["component_revision_id"]
    )
    subject_sha256 = canonical_sha256(dict(subject_record))
    lineage = load_state_lineage(
        store=store,
        subject_id=subject_id,
        subject_sha256=subject_sha256,
        policy=trusted,
        registry=trusted_registry,
    )
    head = lineage[-1]["state_record"]
    current = parse_state_vector(head["state"])
    profile, profile_sha256 = trusted.evaluation_profile(profile_id)
    if (
        current.possession_state != "SNAPSHOT_INTEGRITY_VERIFIED"
        or current.disposition != "QUARANTINED"
        or current.evidence_outcome != "IN_PROGRESS"
        or current.review_state != profile["from_review_state"]
    ):
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Evaluation receipt prior state is stale")
    terminal = profile_id == "nexus.profile.ecosystem-review-bundle"
    target = StateVector(
        current.possession_state,
        profile["to_review_state"],
        "COMPLETE" if terminal else current.evidence_outcome,
        current.disposition,
    )
    if profile_id == "nexus.profile.ecosystem-provenance":
        evidence_ids = [profile_inputs["provenance_evidence"]["evidence_id"]]
        proposal_evidence = [profile_inputs["provenance_evidence"]]
    elif profile_id == "nexus.profile.ecosystem-static-security":
        evidence_ids = [profile_inputs["static_report"]["report_id"]]
        proposal_evidence = [profile_inputs["static_report"]]
    elif profile_id == "nexus.profile.ecosystem-classification":
        evidence_ids = [profile_inputs["classification_report"]["report_id"]]
        proposal_evidence = [profile_inputs["classification_report"]]
    elif profile_id == "nexus.profile.ecosystem-validation-bundle":
        evidence_ids = [profile_inputs["provenance_evidence"]["evidence_id"]]
        proposal_evidence = [profile_inputs["provenance_evidence"]]
    else:
        proposal_evidence = [dict(item) for item in profile_inputs["prior_transition_receipts"]]
        evidence_ids = [item["transition_id"] for item in proposal_evidence]
    evidence_ids = sorted(evidence_ids)
    receipt_digest = evaluation_canonical_sha256(checked)
    transition = build_transition_receipt(
        subject_id=subject_id,
        subject_sha256=subject_sha256,
        from_state=current,
        to_state=target,
        transition_axis="review_evidence_terminal" if terminal else "review",
        evidence_ids=evidence_ids,
        evaluation_receipt_sha256s=[receipt_digest],
        evaluation_profile_id=profile_id,
        evaluation_profile_sha256=profile_sha256,
        policy_semantic_sha256=trusted.policy_semantic_sha256,
        reason_codes=[],
    )
    return _make_proposal(
        transition=transition,
        predecessor_state_record_id=head["state_record_id"],
        evidence_records=proposal_evidence,
        evaluation_receipts=[checked],
    )


def propose_snapshot_integrity_verified(
    *,
    subject_record: Mapping[str, Any],
    tree: Mapping[str, Any],
    intake_attempt: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    parent_revision: Mapping[str, Any] | None = None,
) -> ValidatedTransitionProposal:
    """Propose the second possession edge after rehashing the immutable snapshot."""
    trusted = _require_trusted_source_policy(policy)
    subject_type, checked, checked_tree, _parent, _creator = _revalidate_revision_subject(
        subject_record=subject_record,
        tree=tree,
        intake_attempt=intake_attempt,
        store=store,
        policy=trusted,
        parent_revision=parent_revision,
    )
    if subject_type == "ecosystem_source_revision":
        subject_id = checked["revision_id"]
        evidence_ids = sorted([checked_tree["tree_id"], intake_attempt["attempt_result_id"]])
        evidence_records: list[Mapping[str, Any]] = [checked_tree, intake_attempt]
    else:
        subject_id = checked["component_revision_id"]
        evidence_ids = [checked["component_revision_id"]]
        evidence_records = [checked]
    subject_sha256 = canonical_sha256(checked)
    lineage = load_state_lineage(
        store=store,
        subject_id=subject_id,
        subject_sha256=subject_sha256,
        policy=trusted,
    )
    head = lineage[-1]["state_record"]
    current = parse_state_vector(head["state"])
    if current != StateVector(
        "MIRRORED_UNREVIEWED", "NOT_REVIEWED", "IN_PROGRESS", "QUARANTINED"
    ):
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Snapshot integrity edge is stale")
    target = StateVector(
        "SNAPSHOT_INTEGRITY_VERIFIED", "NOT_REVIEWED", "IN_PROGRESS", "QUARANTINED"
    )
    transition = build_transition_receipt(
        subject_id=subject_id,
        subject_sha256=subject_sha256,
        from_state=current,
        to_state=target,
        transition_axis="possession",
        evidence_ids=evidence_ids,
        evaluation_receipt_sha256s=[],
        evaluation_profile_id=None,
        evaluation_profile_sha256=None,
        policy_semantic_sha256=trusted.policy_semantic_sha256,
        reason_codes=[],
    )
    return _make_proposal(
        transition=transition,
        predecessor_state_record_id=head["state_record_id"],
        evidence_records=list(evidence_records),
        evaluation_receipts=[],
    )


def _record_primary_id(record: Mapping[str, Any]) -> str:
    for field in (
        "evidence_id",
        "report_id",
        "classification_id",
        "finding_id",
        "transition_id",
        "component_revision_id",
        "attempt_result_id",
        "tree_id",
    ):
        value = record.get(field)
        if type(value) is str:
            validate_typed_id(value)
            return value
    raise _evaluation_error("STATE_TRANSITION_INVALID", "Evidence record lacks a typed identity")


def _record_map(records: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    if type(records) is not list:
        raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Evidence bundle must be an exact list")
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if type(record) is not dict:
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Evidence bundle record is malformed")
        primary = _record_primary_id(record)
        if primary in result:
            raise _evaluation_error("PROVENANCE_INSUFFICIENT", "Evidence bundle repeats an identity")
        result[primary] = dict(record)
    return result


def _recomputed_bundle_semantics(
    *,
    records: list[dict[str, Any]],
    checked_subject: Mapping[str, Any],
    checked_tree: Mapping[str, Any],
    checked_attempt: Mapping[str, Any],
    parent_revision: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
) -> tuple[str, bool, list[str], list[dict[str, Any]]]:
    """Match an outcome/disposition bundle to one exact current analyzer result."""
    from .ecosystem_evidence import (
        analyze_static_evidence,
        classify_components,
        validate_license_evidence,
        validate_provenance_evidence,
    )

    supplied = _record_map(records)
    schemas = {record.get("schema_version") for record in records}
    subject_is_component = (
        checked_subject.get("schema_version")
        == "nexus.ecosystem-component-revision.v1"
    )
    subject_id = (
        checked_subject["component_revision_id"]
        if subject_is_component
        else checked_subject["revision_id"]
    )
    component_parent = parent_revision if subject_is_component else None

    if schemas <= {"nexus.ecosystem-provenance-evidence.v1"} and len(records) == 1:
        checked = validate_provenance_evidence(
            records[0],
            revision=parent_revision,
            tree=checked_tree,
            intake_attempt=checked_attempt,
            store=store,
            policy=policy,
        )
        return "provenance", checked["result"] == "EXACT_SUBJECT_BOUND", list(
            checked["reason_codes"]
        ), [checked]

    if schemas <= {"nexus.ecosystem-license-evidence.v1"} and len(records) == 1:
        checked = validate_license_evidence(
            records[0],
            subject_record=checked_subject,
            tree=checked_tree,
            store=store,
            policy=policy,
            parent_revision=component_parent,
        )
        return (
            "license",
            checked["license_result"] == "MATCHES_POLICY_DECLARATION",
            list(checked["reason_codes"]),
            [checked],
        )

    static_schemas = {
        "nexus.ecosystem-provenance-evidence.v1",
        "nexus.ecosystem-license-evidence.v1",
        "nexus.ecosystem-static-finding.v1",
        "nexus.ecosystem-static-report.v1",
    }
    if schemas <= static_schemas and "nexus.ecosystem-static-report.v1" in schemas:
        reports = [
            record
            for record in records
            if record.get("schema_version") == "nexus.ecosystem-static-report.v1"
        ]
        provenances = [
            record
            for record in records
            if record.get("schema_version")
            == "nexus.ecosystem-provenance-evidence.v1"
        ]
        licenses = [
            record
            for record in records
            if record.get("schema_version") == "nexus.ecosystem-license-evidence.v1"
        ]
        candidates: list[tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]] = []
        for analyzer_available, use_prerequisites in (
            (False, False),
            (True, False),
            (True, True),
        ):
            if use_prerequisites and (len(provenances) != 1 or len(licenses) != 1):
                continue
            if not use_prerequisites and (provenances or licenses):
                continue
            try:
                findings, report = analyze_static_evidence(
                    subject_id=subject_id,
                    subject_record=checked_subject,
                    tree=checked_tree,
                    store=store,
                    policy=policy,
                    provenance_evidence=(provenances[0] if use_prerequisites else None),
                    license_evidence=(licenses[0] if use_prerequisites else None),
                    intake_attempt=(checked_attempt if use_prerequisites else None),
                    parent_revision=component_parent,
                    analyzer_available=analyzer_available,
                )
            except EcosystemError:
                continue
            expected_records = [
                *(provenances if use_prerequisites else []),
                *(licenses if use_prerequisites else []),
                *findings,
                report,
            ]
            if _record_map(expected_records) == supplied:
                candidates.append((findings, report, expected_records))
        if len(candidates) != 1 or len(reports) != 1:
            raise _evaluation_error(
                "PROVENANCE_INSUFFICIENT",
                "Static evidence bundle is not the exact current analyzer result",
            )
        findings, report, expected_records = candidates[0]
        return (
            "static",
            report["analysis_status"] == "COMPLETE",
            list(report["reason_codes"]),
            [dict(item) for item in expected_records],
        )

    classification_schemas = {
        "nexus.ecosystem-component-revision.v1",
        "nexus.ecosystem-component-classification.v1",
        "nexus.ecosystem-classification-report.v1",
    }
    if (
        schemas <= classification_schemas
        and "nexus.ecosystem-classification-report.v1" in schemas
    ):
        candidates = []
        for classifier_available in (False, True):
            try:
                components, classifications, report = classify_components(
                    revision=parent_revision,
                    tree=checked_tree,
                    store=store,
                    policy=policy,
                    classifier_available=classifier_available,
                )
            except EcosystemError:
                continue
            expected_records = [*components, *classifications, report]
            if _record_map(expected_records) == supplied:
                candidates.append((report, expected_records))
        if len(candidates) != 1:
            raise _evaluation_error(
                "PROVENANCE_INSUFFICIENT",
                "Classification evidence bundle is not the exact current classifier result",
            )
        report, expected_records = candidates[0]
        return (
            "classification",
            report["report_status"] == "COMPLETE",
            list(report["reason_codes"]),
            [dict(item) for item in expected_records],
        )

    raise _evaluation_error(
        "PROVENANCE_INSUFFICIENT", "Evidence bundle has no supported current semantics"
    )


def _validate_transition_evidence_bundle(
    *,
    transition: Mapping[str, Any],
    records: list[Mapping[str, Any]],
    checked_subject: Mapping[str, Any],
    checked_tree: Mapping[str, Any],
    checked_attempt: Mapping[str, Any],
    parent_revision: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    prior_evidence_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Revalidate every state-cited record and its cross-record semantics."""
    supplied = _record_map(records)
    if set(supplied) != set(transition["evidence_ids"]):
        raise _evaluation_error(
            "PROVENANCE_INSUFFICIENT", "Transition evidence bundle is incomplete or extra"
        )
    checked = [
        _validate_state_evidence_record(
            expected_id=evidence_id,
            record=supplied[evidence_id],
            checked_subject=checked_subject,
            checked_tree=checked_tree,
            checked_attempt=checked_attempt,
            parent_revision=parent_revision,
            store=store,
            policy=policy,
        )
        for evidence_id in transition["evidence_ids"]
    ]
    axis = transition["transition_axis"]
    if axis not in {"evidence_outcome", "disposition"}:
        return checked
    kind, complete, evidence_reasons, exact_records = _recomputed_bundle_semantics(
        records=checked,
        checked_subject=checked_subject,
        checked_tree=checked_tree,
        checked_attempt=checked_attempt,
        parent_revision=parent_revision,
        store=store,
        policy=policy,
    )
    if _record_map(exact_records) != _record_map(checked):
        raise _evaluation_error(
            "PROVENANCE_INSUFFICIENT", "Transition evidence is not the exact current bundle"
        )
    if prior_evidence_ids is not None and not (
        set(transition["evidence_ids"]) - prior_evidence_ids
    ):
        raise _evaluation_error(
            "STATE_TRANSITION_INVALID", "Evidence-outcome transition requires new evidence"
        )
    if axis == "evidence_outcome":
        target = transition["to_state"]["evidence_outcome"]
        if target == "INSUFFICIENT_EVIDENCE":
            if complete or not evidence_reasons or transition["reason_codes"] != evidence_reasons:
                raise _evaluation_error(
                    "PROVENANCE_INSUFFICIENT",
                    "Insufficient-evidence transition lacks exact incomplete evidence",
                )
        elif target == "IN_PROGRESS":
            if not complete or transition["reason_codes"]:
                raise _evaluation_error(
                    "PROVENANCE_INSUFFICIENT",
                    "Evidence resumption lacks exact complete new evidence",
                )
        else:
            raise _evaluation_error(
                "STATE_TRANSITION_INVALID", "Evidence outcome target is unsupported"
            )
        return checked

    reports = [
        record
        for record in exact_records
        if record.get("schema_version") == "nexus.ecosystem-static-report.v1"
    ]
    rejecting = [
        record
        for record in exact_records
        if record.get("schema_version") == "nexus.ecosystem-static-finding.v1"
        and record.get("disposition") == "REJECTS_CANDIDATE"
    ]
    fatal_reasons = sorted({record["reason_code"] for record in rejecting})
    if (
        kind != "static"
        or not complete
        or len(reports) != 1
        or reports[0].get("result") != "REJECTED"
        or reports[0].get("counts", {}).get("rejecting") != len(rejecting)
        or not rejecting
        or transition["reason_codes"] != fatal_reasons
    ):
        raise _evaluation_error(
            "STATIC_FINDING_REJECTED",
            "Rejection requires the exact current policy-defined fatal finding bundle",
        )
    return checked


def propose_evidence_outcome(
    *,
    subject_record: Mapping[str, Any],
    tree: Mapping[str, Any],
    intake_attempt: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    registry: TrustedValidatorRegistry | None = None,
    evidence_records: list[Mapping[str, Any]],
    to_outcome: str,
    parent_revision: Mapping[str, Any] | None = None,
    reason_codes: list[str] | None = None,
) -> ValidatedTransitionProposal:
    """Propose only the two nonterminal insufficient-evidence edges."""
    trusted = _require_trusted_source_policy(policy)
    subject_type, checked, _tree, _parent, _creator = _revalidate_revision_subject(
        subject_record=subject_record,
        tree=tree,
        intake_attempt=intake_attempt,
        store=store,
        policy=trusted,
        parent_revision=parent_revision,
    )
    subject_id = (
        checked["revision_id"]
        if subject_type == "ecosystem_source_revision"
        else checked["component_revision_id"]
    )
    subject_sha256 = canonical_sha256(checked)
    lineage = load_state_lineage(
        store=store,
        subject_id=subject_id,
        subject_sha256=subject_sha256,
        policy=trusted,
        registry=registry,
    )
    head = lineage[-1]["state_record"]
    current = parse_state_vector(head["state"])
    if to_outcome not in {"IN_PROGRESS", "INSUFFICIENT_EVIDENCE"}:
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Evidence outcome target is forbidden")
    evidence_ids = sorted(_record_primary_id(item) for item in evidence_records)
    if len(evidence_ids) != len(set(evidence_ids)) or not evidence_ids:
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Evidence outcome requires unique evidence")
    target = StateVector(
        current.possession_state,
        current.review_state,
        to_outcome,
        current.disposition,
    )
    transition = build_transition_receipt(
        subject_id=subject_id,
        subject_sha256=subject_sha256,
        from_state=current,
        to_state=target,
        transition_axis="evidence_outcome",
        evidence_ids=evidence_ids,
        evaluation_receipt_sha256s=[],
        evaluation_profile_id=None,
        evaluation_profile_sha256=None,
        policy_semantic_sha256=trusted.policy_semantic_sha256,
        reason_codes=sorted(set(reason_codes or [])),
    )
    prior_evidence_ids = {
        evidence_id
        for item in lineage
        for evidence_id in item["transition"]["evidence_ids"]
    }
    checked_evidence = _validate_transition_evidence_bundle(
        transition=transition,
        records=evidence_records,
        checked_subject=checked,
        checked_tree=_tree,
        checked_attempt=intake_attempt,
        parent_revision=_parent,
        store=store,
        policy=trusted,
        prior_evidence_ids=prior_evidence_ids,
    )
    return _make_proposal(
        transition=transition,
        predecessor_state_record_id=head["state_record_id"],
        evidence_records=checked_evidence,
        evaluation_receipts=[],
    )


def propose_rejection(
    *,
    subject_record: Mapping[str, Any],
    tree: Mapping[str, Any],
    intake_attempt: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    registry: TrustedValidatorRegistry | None = None,
    evidence_records: list[Mapping[str, Any]],
    reason_codes: list[str],
    parent_revision: Mapping[str, Any] | None = None,
) -> ValidatedTransitionProposal:
    """Propose the sole monotonic disposition edge: QUARANTINED to REJECTED."""
    trusted = _require_trusted_source_policy(policy)
    subject_type, checked, _tree, _parent, _creator = _revalidate_revision_subject(
        subject_record=subject_record,
        tree=tree,
        intake_attempt=intake_attempt,
        store=store,
        policy=trusted,
        parent_revision=parent_revision,
    )
    subject_id = (
        checked["revision_id"]
        if subject_type == "ecosystem_source_revision"
        else checked["component_revision_id"]
    )
    subject_sha256 = canonical_sha256(checked)
    lineage = load_state_lineage(
        store=store,
        subject_id=subject_id,
        subject_sha256=subject_sha256,
        policy=trusted,
        registry=registry,
    )
    head = lineage[-1]["state_record"]
    current = parse_state_vector(head["state"])
    evidence_ids = sorted(_record_primary_id(item) for item in evidence_records)
    if len(evidence_ids) != len(set(evidence_ids)) or not evidence_ids:
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Rejection requires unique evidence")
    target = StateVector(
        current.possession_state,
        current.review_state,
        current.evidence_outcome,
        "REJECTED",
    )
    transition = build_transition_receipt(
        subject_id=subject_id,
        subject_sha256=subject_sha256,
        from_state=current,
        to_state=target,
        transition_axis="disposition",
        evidence_ids=evidence_ids,
        evaluation_receipt_sha256s=[],
        evaluation_profile_id=None,
        evaluation_profile_sha256=None,
        policy_semantic_sha256=trusted.policy_semantic_sha256,
        reason_codes=sorted(set(reason_codes)),
    )
    checked_evidence = _validate_transition_evidence_bundle(
        transition=transition,
        records=evidence_records,
        checked_subject=checked,
        checked_tree=_tree,
        checked_attempt=intake_attempt,
        parent_revision=_parent,
        store=store,
        policy=trusted,
        prior_evidence_ids={
            evidence_id
            for item in lineage
            for evidence_id in item["transition"]["evidence_ids"]
        },
    )
    return _make_proposal(
        transition=transition,
        predecessor_state_record_id=head["state_record_id"],
        evidence_records=checked_evidence,
        evaluation_receipts=[],
    )


def append_state_transition(
    *,
    proposal: ValidatedTransitionProposal,
    subject_record: Mapping[str, Any],
    tree: Mapping[str, Any],
    intake_attempt: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
    evidence_records: list[Mapping[str, Any]],
    evaluation_receipts: list[Mapping[str, Any]],
    registry: TrustedValidatorRegistry | None = None,
    parent_revision: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Append one validated edge under the repository-external state lock."""
    trusted = _require_trusted_source_policy(policy)
    if type(store) is not QuarantineStore:
        raise _evaluation_error("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    store._require_policy(trusted)
    baseline = _require_transition_proposal(proposal)
    transition = validate_transition_receipt(proposal._transition)
    _subject_type, checked, _tree, _parent, _creator = _revalidate_revision_subject(
        subject_record=subject_record,
        tree=tree,
        intake_attempt=intake_attempt,
        store=store,
        policy=trusted,
        parent_revision=parent_revision,
    )
    subject_id = (
        checked["revision_id"]
        if _subject_type == "ecosystem_source_revision"
        else checked["component_revision_id"]
    )
    subject_sha256 = canonical_sha256(checked)
    if (
        transition["subject_id"] != subject_id
        or transition["subject_sha256"] != subject_sha256
        or transition["policy_semantic_sha256"] != trusted.policy_semantic_sha256
    ):
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition proposal subject is stale")
    if _evidence_baseline(transition["evidence_ids"], evidence_records) != baseline[3]:
        raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition evidence changed after proposal")
    if _evaluation_baseline(transition["evaluation_receipt_sha256s"], evaluation_receipts) != baseline[4]:
        raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Evaluation receipt changed after proposal")
    checked_evidence = _validate_transition_evidence_bundle(
        transition=transition,
        records=evidence_records,
        checked_subject=checked,
        checked_tree=_tree,
        checked_attempt=intake_attempt,
        parent_revision=_parent,
        store=store,
        policy=trusted,
    )
    if evaluation_receipts:
        if registry is None:
            raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Trusted registry is required")
        trusted_registry = _require_trusted_registry(registry)
        store._require_registry(trusted_registry)
        wire_id = _wire_subject(
            subject_type=_subject_type,
            subject_id=subject_id,
            subject_record=checked,
            creator_sha256=_creator,
        )["subject_id"]
        for receipt in evaluation_receipts:
            try:
                validated = validate_evaluation_receipt(
                    receipt,
                    registry=trusted_registry,
                    expected_subject_id=wire_id,
                    expected_subject_sha256=subject_sha256,
                )
            except EvaluationError:
                raise _evaluation_error("EVALUATION_RECEIPT_INVALID", "Persisted evaluation receipt is invalid") from None
            if validated["result"]["state"] != "PASS":
                raise _evaluation_error("EVALUATION_RESULT_BLOCKED", "Persisted evaluation did not pass")

    maximum = trusted.resource_limits["max_record_bytes"]
    with store._exclusive("state.lock"):
        lineage = _load_lineage_unlocked(
            store=store,
            subject_id=subject_id,
            subject_sha256=subject_sha256,
            policy=trusted,
            registry=registry,
            allow_missing=baseline[2] is None,
        )
        replay = [
            item for item in lineage if item["transition"]["transition_id"] == transition["transition_id"]
        ]
        if replay:
            if len(replay) != 1 or replay[0] != lineage[-1]:
                raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition replay is not the current head")
            return _copy(replay[0]["state_record"])
        current_id = None if not lineage else lineage[-1]["state_record"]["state_record_id"]
        if current_id != baseline[2]:
            raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition predecessor is stale")
        if lineage and transition["from_state"] != lineage[-1]["state_record"]["state"]:
            raise _evaluation_error("STATE_TRANSITION_INVALID", "Transition prior state is stale")
        if not lineage and transition["from_state"] != IMPLICIT_STATE.as_dict():
            raise _evaluation_error("STATE_TRANSITION_INVALID", "Only genesis may start a lineage")
        if transition["transition_axis"] in {"evidence_outcome", "disposition"}:
            _validate_transition_evidence_bundle(
                transition=transition,
                records=checked_evidence,
                checked_subject=checked,
                checked_tree=_tree,
                checked_attempt=intake_attempt,
                parent_revision=_parent,
                store=store,
                policy=trusted,
                prior_evidence_ids={
                    evidence_id
                    for item in lineage
                    for evidence_id in item["transition"]["evidence_ids"]
                },
            )
        state_record = build_state_record(
            subject_id=subject_id,
            subject_sha256=subject_sha256,
            previous_state_record_id=current_id,
            transition=transition,
        )
        for evidence_id, _digest in baseline[3]:
            record = next(
                item for item in evidence_records if _record_primary_id(item) == evidence_id
            )
            store._publish_record(
                f"evidence/sha256/{evidence_id.split('/', 1)[1]}.json",
                record,
                maximum_bytes=maximum,
                writer_token=_STATE_RECORD_WRITER,
            )
        for digest, _same in baseline[4]:
            receipt = next(
                item for item in evaluation_receipts if evaluation_canonical_sha256(item) == digest
            )
            store._publish_record(
                f"evidence/sha256/{digest}.json",
                receipt,
                maximum_bytes=maximum,
                writer_token=_STATE_RECORD_WRITER,
            )
        store._publish_record(
            f"evidence/sha256/{transition['transition_id'].split('/', 1)[1]}.json",
            transition,
            maximum_bytes=maximum,
            writer_token=_STATE_RECORD_WRITER,
        )
        store._publish_record(
            f"state/sha256/{state_record['state_record_id'].split('/', 1)[1]}.json",
            state_record,
            maximum_bytes=maximum,
            writer_token=_STATE_RECORD_WRITER,
        )
        return _copy(state_record)


def persist_component_revisions(
    *,
    components: list[Mapping[str, Any]],
    classifications: list[Mapping[str, Any]],
    classification_report: Mapping[str, Any],
    revision: Mapping[str, Any],
    tree: Mapping[str, Any],
    intake_attempt: Mapping[str, Any],
    store: QuarantineStore,
    policy: TrustedEcosystemSourcePolicy,
) -> list[dict[str, Any]]:
    """Persist inert component records and their quarantined genesis lineages."""
    from .ecosystem_evidence import validate_component_classification

    trusted = _require_trusted_source_policy(policy)
    if type(store) is not QuarantineStore:
        raise _evaluation_error("CAS_ROOT_INVALID", "Trusted quarantine store is required")
    store._require_policy(trusted)
    checked_components, checked_classifications, checked_report = validate_component_classification(
        components,
        classifications,
        classification_report,
        revision=revision,
        tree=tree,
        store=store,
        policy=trusted,
    )
    maximum = trusted.resource_limits["max_record_bytes"]
    store._publish_record(
        f"evidence/sha256/{checked_report['report_id'].split('/', 1)[1]}.json",
        checked_report,
        maximum_bytes=maximum,
        writer_token=_STATE_RECORD_WRITER,
    )
    for classification in checked_classifications:
        store._publish_record(
            f"evidence/sha256/{classification['classification_id'].split('/', 1)[1]}.json",
            classification,
            maximum_bytes=maximum,
            writer_token=_STATE_RECORD_WRITER,
        )
    states: list[dict[str, Any]] = []
    for component in checked_components:
        digest = component["component_revision_id"].split("/", 1)[1]
        store._publish_record(
            f"components/sha256/{digest}.json",
            component,
            maximum_bytes=maximum,
            writer_token=_STATE_RECORD_WRITER,
        )
        transition = build_transition_receipt(
            subject_id=component["component_revision_id"],
            subject_sha256=canonical_sha256(component),
            from_state=IMPLICIT_STATE,
            to_state=GENESIS_STATE,
            transition_axis="possession",
            evidence_ids=[component["component_revision_id"]],
            evaluation_receipt_sha256s=[],
            evaluation_profile_id=None,
            evaluation_profile_sha256=None,
            policy_semantic_sha256=trusted.policy_semantic_sha256,
            reason_codes=[],
        )
        proposal = _make_proposal(
            transition=transition,
            predecessor_state_record_id=None,
            evidence_records=[component],
            evaluation_receipts=[],
        )
        states.append(
            append_state_transition(
                proposal=proposal,
                subject_record=component,
                tree=tree,
                intake_attempt=intake_attempt,
                store=store,
                policy=trusted,
                evidence_records=[component],
                evaluation_receipts=[],
                parent_revision=revision,
            )
        )
    return states
