"""Bounded, data-only creator/reviewer/enhancer workflow contracts.

The functions here describe and validate a future execution sequence.  They do
not call a Skill, Agent, tool, subprocess, network endpoint, or artifact API.
"""
from __future__ import annotations

import json
import re
from typing import Any, Mapping, Sequence

from .evaluation import (
    EVALUATION_CONTRACT_SCHEMA_VERSION,
    EvaluationError,
    TrustedValidatorRegistry,
    canonical_sha256,
    validate_evaluation_receipt,
)


QUALITY_LOOP_SCHEMA_VERSION = "nexus.quality-loop.v1"
QUALITY_RECEIPT_SCHEMA_VERSION = "nexus.quality-receipt.v2"
MAX_REVIEW_CYCLES = 2
MAX_ENHANCEMENT_PASSES = 1
MAX_QUALITY_STAGES = 6
MAX_QUALITY_RECEIPT_BYTES = 64 * 1024
CAPABILITY_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
WORKFLOW_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SECRET_IDENTIFIER_RE = re.compile(
    r"(?i)^(?:sk[-_][A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20,}"
    r"|(?:AKIA|ASIA)[0-9A-Z]{16}"
    r"|xox[A-Za-z]-[A-Za-z0-9-]{8,}|xapp-[A-Za-z0-9-]{8,})$"
)
STEP_TYPES = frozenset(
    {
        "execute_creator",
        "validate_artifact",
        "execute_reviewer",
        "conditional_enhancement",
        "revalidate_artifact",
        "report_result",
    }
)
OUTCOMES = frozenset(
    {
        "artifact_pending",
        "validation_passed",
        "validation_failed",
        "enhancement_eligible",
        "enhancement_skipped",
        "execution_failed",
        "reported",
    }
)

_QUALITY_RECEIPT_FIELDS = {
    "schema_version",
    "workflow_id",
    "selected_capability_ids",
    "subject",
    "stages",
    "evidence_states",
    "budgets",
    "outcome",
    "authority",
}
_QUALITY_SUBJECT_FIELDS = {
    "subject_type",
    "subject_id",
    "original_subject_sha256",
    "current_subject_sha256",
}
_QUALITY_STAGE_FIELDS = {
    "stage",
    "sequence",
    "capability_id",
    "stage_state",
    "input_subject_sha256",
    "output_subject_sha256",
    "evaluation_receipt",
    "mutation_policy",
    "review_cycle",
    "enhancement_pass",
    "reported_validation_state",
    "stage_receipt_sha256",
}
_QUALITY_EVIDENCE_FIELDS = {
    "creation",
    "selection",
    "execution",
    "review",
    "enhancement",
    "validation",
    "reporting",
}
_QUALITY_BUDGET_FIELDS = {"review_cycles_used", "enhancement_passes_used"}
_QUALITY_AUTHORITY = {
    "execution_authority": "host_or_approved_runtime_only",
    "mcp_execution_authority": "none",
    "automatic_execution": False,
    "reviewer_mutation_authority": "none",
}


class QualityLoopError(ValueError):
    """Raised when a bounded quality-loop contract is unsafe or malformed."""


def _ids(values: Sequence[str], name: str) -> list[str]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise QualityLoopError(f"quality loop {name} is invalid")
    result = list(values)
    if any(not isinstance(value, str) or not value for value in result) or len(set(result)) != len(result):
        raise QualityLoopError(f"quality loop {name} is invalid")
    return result


def build_quality_loop_plan(
    *,
    creator_id: str,
    reviewer_ids: Sequence[str],
    enhancer_ids: Sequence[str],
    validation_requirements: Sequence[str],
    max_review_cycles: int = MAX_REVIEW_CYCLES,
    max_enhancement_passes: int = MAX_ENHANCEMENT_PASSES,
) -> dict[str, Any]:
    """Build a copy-on-write, bounded workflow plan without executing it."""
    if not isinstance(creator_id, str) or not creator_id:
        raise QualityLoopError("quality loop creator is invalid")
    reviewers = _ids(reviewer_ids, "reviewers")
    enhancers = _ids(enhancer_ids, "enhancers")
    validations = _ids(validation_requirements, "validation requirements")
    if not validations:
        raise QualityLoopError("quality loop requires validation")
    if creator_id in {*reviewers, *enhancers} or set(reviewers) & set(enhancers):
        raise QualityLoopError("quality loop roles must be distinct")
    if not isinstance(max_review_cycles, int) or not 1 <= max_review_cycles <= MAX_REVIEW_CYCLES:
        raise QualityLoopError("quality loop review budget is invalid")
    if not isinstance(max_enhancement_passes, int) or not 0 <= max_enhancement_passes <= MAX_ENHANCEMENT_PASSES:
        raise QualityLoopError("quality loop enhancement budget is invalid")
    steps: list[dict[str, Any]] = [
        {"step": "execute_creator", "capability_id": creator_id},
        {"step": "validate_artifact", "requirements": validations},
    ]
    for reviewer_id in reviewers:
        steps.append({"step": "execute_reviewer", "capability_id": reviewer_id})
    if enhancers and max_enhancement_passes:
        steps.append(
            {
                "step": "conditional_enhancement",
                "capability_ids": enhancers,
                "condition": "validated_defect_and_material_expected_improvement",
                "artifact_policy": "copy_on_write_preserve_original",
            }
        )
        steps.append({"step": "revalidate_artifact", "requirements": validations})
    steps.append({"step": "report_result"})
    return {
        "schema_version": QUALITY_LOOP_SCHEMA_VERSION,
        "execution_authority": "host_or_approved_runtime_only",
        "automatic_execution": False,
        "budgets": {
            "max_review_cycles": max_review_cycles,
            "max_enhancement_passes": max_enhancement_passes,
        },
        "steps": steps,
        "stop_conditions": [
            "validation_passed",
            "review_budget_exhausted",
            "enhancement_budget_exhausted",
            "permission_or_capability_unavailable",
            "execution_failed",
        ],
    }


def validate_quality_loop_plan(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping) or payload.get("schema_version") != QUALITY_LOOP_SCHEMA_VERSION:
        raise QualityLoopError("quality loop schema is invalid")
    if payload.get("execution_authority") != "host_or_approved_runtime_only" or payload.get("automatic_execution") is not False:
        raise QualityLoopError("quality loop execution authority is invalid")
    budgets = payload.get("budgets")
    if not isinstance(budgets, Mapping):
        raise QualityLoopError("quality loop budgets are invalid")
    review_budget = budgets.get("max_review_cycles")
    enhancement_budget = budgets.get("max_enhancement_passes")
    if not isinstance(review_budget, int) or not 1 <= review_budget <= MAX_REVIEW_CYCLES:
        raise QualityLoopError("quality loop review budget is invalid")
    if not isinstance(enhancement_budget, int) or not 0 <= enhancement_budget <= MAX_ENHANCEMENT_PASSES:
        raise QualityLoopError("quality loop enhancement budget is invalid")
    steps = payload.get("steps")
    if not isinstance(steps, list) or len(steps) < 3:
        raise QualityLoopError("quality loop steps are invalid")
    step_names: list[str] = []
    for item in steps:
        if not isinstance(item, Mapping) or item.get("step") not in STEP_TYPES:
            raise QualityLoopError("quality loop step is invalid")
        step_names.append(str(item["step"]))
    if step_names[0] != "execute_creator" or step_names[1] != "validate_artifact" or step_names[-1] != "report_result":
        raise QualityLoopError("quality loop ordering is invalid")
    if "conditional_enhancement" in step_names:
        index = step_names.index("conditional_enhancement")
        enhancement = steps[index]
        if enhancement.get("artifact_policy") != "copy_on_write_preserve_original":
            raise QualityLoopError("quality loop artifact preservation is invalid")
        if index + 1 >= len(steps) or steps[index + 1].get("step") != "revalidate_artifact":
            raise QualityLoopError("enhancement must be followed by revalidation")
    stop_conditions = payload.get("stop_conditions")
    if not isinstance(stop_conditions, list) or "validation_passed" not in stop_conditions:
        raise QualityLoopError("quality loop stop conditions are invalid")
    return json.loads(json.dumps(payload, ensure_ascii=False))


def _legacy_quality_receipt(payload: Any) -> dict[str, Any]:
    """Preserve the accepted v1 receipt without changing frozen semantics."""
    outcome = payload.get("outcome")
    if outcome not in OUTCOMES:
        raise QualityLoopError("quality receipt outcome is invalid")
    executed = payload.get("executed_capability_ids")
    _ids(executed, "receipt execution list")
    artifact = payload.get("artifact_reference")
    validation = payload.get("validation")
    if not isinstance(validation, Mapping) or not isinstance(validation.get("passed"), bool):
        raise QualityLoopError("quality receipt validation is invalid")
    if outcome == "validation_passed":
        if not executed or not isinstance(artifact, str) or not artifact or not validation["passed"]:
            raise QualityLoopError("quality receipt cannot claim validation success")
    if outcome in {"execution_failed", "artifact_pending"} and validation["passed"]:
        raise QualityLoopError("quality receipt contradicts execution state")
    return json.loads(json.dumps(payload, ensure_ascii=False))


def _nullable_digest(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise QualityLoopError(f"quality {label} digest is invalid")
    return value


def _quality_json_size(value: Any) -> int:
    try:
        encoder = json.JSONEncoder(
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        size = 0
        for chunk in encoder.iterencode(value):
            size += len(chunk.encode("utf-8"))
            if size > MAX_QUALITY_RECEIPT_BYTES:
                return size
        return size
    except (TypeError, ValueError, RecursionError) as exc:
        raise QualityLoopError("quality receipt is not canonical JSON") from exc


def _bounded_quality_copy(value: Any) -> Any:
    if _quality_json_size(value) > MAX_QUALITY_RECEIPT_BYTES:
        raise QualityLoopError("quality receipt exceeds its bounded size")
    try:
        return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))
    except (TypeError, ValueError, RecursionError) as exc:
        raise QualityLoopError("quality receipt is not canonical JSON") from exc


def build_quality_stage_receipt(
    *,
    stage: str,
    sequence: int,
    capability_id: str,
    stage_state: str,
    input_subject_sha256: str | None,
    output_subject_sha256: str | None,
    evaluation_receipt: Mapping[str, Any] | None,
    mutation_policy: str,
    review_cycle: int = 0,
    enhancement_pass: int = 0,
    reported_validation_state: str | None = None,
) -> dict[str, Any]:
    """Build one hash-bound stage record; sequence validity is checked later."""
    base = {
        "stage": stage,
        "sequence": sequence,
        "capability_id": capability_id,
        "stage_state": stage_state,
        "input_subject_sha256": input_subject_sha256,
        "output_subject_sha256": output_subject_sha256,
        "evaluation_receipt": (
            _bounded_quality_copy(evaluation_receipt)
            if evaluation_receipt is not None
            else None
        ),
        "mutation_policy": mutation_policy,
        "review_cycle": review_cycle,
        "enhancement_pass": enhancement_pass,
        "reported_validation_state": reported_validation_state,
    }
    result = {**base, "stage_receipt_sha256": canonical_sha256(base)}
    # This validates the record's local shape without pretending that the
    # surrounding creator/reviewer/enhancer sequence has already been proven.
    _validate_quality_stage(result, registry=None, validate_evaluation=False)
    return result


def _validate_quality_stage(
    value: Any,
    *,
    registry: TrustedValidatorRegistry | None,
    validate_evaluation: bool = True,
) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _QUALITY_STAGE_FIELDS:
        raise QualityLoopError("quality stage receipt schema is malformed")
    stage = value.get("stage")
    sequence = value.get("sequence")
    capability_id = value.get("capability_id")
    if stage not in {"creator", "reviewer", "enhancer", "reporter"}:
        raise QualityLoopError("quality stage identity is invalid")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or not 0 <= sequence < MAX_QUALITY_STAGES:
        raise QualityLoopError("quality stage sequence is invalid")
    if not isinstance(capability_id, str) or not CAPABILITY_ID_RE.fullmatch(capability_id):
        raise QualityLoopError("quality stage capability identity is invalid")
    if SECRET_IDENTIFIER_RE.fullmatch(capability_id):
        raise QualityLoopError("quality stage capability identity resembles secret material")
    input_digest = _nullable_digest(value.get("input_subject_sha256"), "stage input")
    output_digest = _nullable_digest(value.get("output_subject_sha256"), "stage output")
    review_cycle = value.get("review_cycle")
    enhancement_pass = value.get("enhancement_pass")
    if not isinstance(review_cycle, int) or isinstance(review_cycle, bool) or not 0 <= review_cycle <= MAX_REVIEW_CYCLES:
        raise QualityLoopError("quality stage review cycle is invalid")
    if not isinstance(enhancement_pass, int) or isinstance(enhancement_pass, bool) or not 0 <= enhancement_pass <= MAX_ENHANCEMENT_PASSES:
        raise QualityLoopError("quality stage enhancement pass is invalid")
    reported_state = value.get("reported_validation_state")
    evaluation = value.get("evaluation_receipt")

    if stage == "creator":
        if (
            value.get("stage_state") not in {"execution_succeeded", "execution_failed"}
            or value.get("mutation_policy") != "new_candidate"
            or input_digest is not None
            or evaluation is not None
            or review_cycle != 0
            or enhancement_pass != 0
            or reported_state is not None
            or (value["stage_state"] == "execution_succeeded") != (output_digest is not None)
        ):
            raise QualityLoopError("creator stage receipt is contradictory")
    elif stage == "reviewer":
        if (
            value.get("stage_state") not in {"execution_succeeded", "execution_failed"}
            or value.get("mutation_policy") != "read_only"
            or input_digest is None
            or output_digest != input_digest
            or not 1 <= review_cycle <= MAX_REVIEW_CYCLES
            or reported_state is not None
            or (value["stage_state"] == "execution_succeeded") != isinstance(evaluation, Mapping)
        ):
            raise QualityLoopError("reviewer stage receipt is contradictory")
        if validate_evaluation and isinstance(evaluation, Mapping):
            try:
                validated = validate_evaluation_receipt(
                    evaluation,
                    registry=registry,
                    expected_subject_sha256=input_digest,
                )
            except EvaluationError as exc:
                raise QualityLoopError("reviewer evaluation receipt is invalid") from exc
            if validated["validator"]["validator_id"] != capability_id:
                raise QualityLoopError("selected reviewer and executed validator disagree")
    elif stage == "enhancer":
        if (
            value.get("stage_state") not in {"execution_succeeded", "execution_failed"}
            or value.get("mutation_policy") != "copy_on_write_preserve_original"
            or input_digest is None
            or evaluation is not None
            or review_cycle != 0
            or enhancement_pass != 1
            or reported_state is not None
            or output_digest is None
        ):
            raise QualityLoopError("enhancer stage receipt is contradictory")
        if value["stage_state"] == "execution_succeeded" and output_digest == input_digest:
            raise QualityLoopError("enhancer must create a new candidate digest")
        if value["stage_state"] == "execution_failed" and output_digest != input_digest:
            raise QualityLoopError("failed enhancer cannot replace the original candidate")
    else:
        if (
            value.get("stage_state") != "reported"
            or value.get("mutation_policy") != "read_only_report"
            or input_digest is None
            or output_digest != input_digest
            or evaluation is not None
            or review_cycle != 0
            or enhancement_pass != 0
            or reported_state not in {"not_validated", "validation_passed", "validation_failed"}
        ):
            raise QualityLoopError("reporter stage receipt is contradictory")
    base = {key: value[key] for key in value if key != "stage_receipt_sha256"}
    if value.get("stage_receipt_sha256") != canonical_sha256(base):
        raise QualityLoopError("quality stage receipt digest is inconsistent")
    return json.loads(json.dumps(value, ensure_ascii=False))


def _validate_quality_receipt_v2(
    payload: Any, *, registry: TrustedValidatorRegistry | None,
) -> dict[str, Any]:
    if _quality_json_size(payload) > MAX_QUALITY_RECEIPT_BYTES:
        raise QualityLoopError("quality receipt exceeds its bounded size")
    if not isinstance(payload, Mapping) or set(payload) != _QUALITY_RECEIPT_FIELDS:
        raise QualityLoopError("quality receipt v2 schema is malformed")
    workflow_id = payload.get("workflow_id")
    if not isinstance(workflow_id, str) or not WORKFLOW_ID_RE.fullmatch(workflow_id):
        raise QualityLoopError("quality workflow identity is invalid")
    if SECRET_IDENTIFIER_RE.fullmatch(workflow_id):
        raise QualityLoopError("quality workflow identity resembles secret material")
    selected = payload.get("selected_capability_ids")
    if (
        not isinstance(selected, list)
        or len(selected) > 8
        or any(not isinstance(item, str) or not CAPABILITY_ID_RE.fullmatch(item) for item in selected)
        or len(selected) != len(set(selected))
        or any(SECRET_IDENTIFIER_RE.fullmatch(item) for item in selected)
    ):
        raise QualityLoopError("quality selected capability list is invalid or unbounded")
    subject = payload.get("subject")
    if not isinstance(subject, Mapping) or set(subject) != _QUALITY_SUBJECT_FIELDS:
        raise QualityLoopError("quality subject schema is malformed")
    subject_type = subject.get("subject_type")
    subject_id = subject.get("subject_id")
    if not isinstance(subject_type, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._:-]{0,127}", subject_type):
        raise QualityLoopError("quality subject type is invalid")
    if not isinstance(subject_id, str) or not WORKFLOW_ID_RE.fullmatch(subject_id):
        raise QualityLoopError("quality subject identity is invalid")
    if SECRET_IDENTIFIER_RE.fullmatch(subject_type) or SECRET_IDENTIFIER_RE.fullmatch(subject_id):
        raise QualityLoopError("quality subject identity resembles secret material")
    original_digest = _nullable_digest(subject.get("original_subject_sha256"), "original subject")
    declared_current = _nullable_digest(subject.get("current_subject_sha256"), "current subject")

    raw_stages = payload.get("stages")
    if not isinstance(raw_stages, list) or len(raw_stages) > MAX_QUALITY_STAGES:
        raise QualityLoopError("quality stages are invalid or unbounded")
    stages = [_validate_quality_stage(item, registry=registry) for item in raw_stages]
    if [item["sequence"] for item in stages] != list(range(len(stages))):
        raise QualityLoopError("quality stage ordering is not deterministic")
    if any(item["capability_id"] not in selected for item in stages):
        raise QualityLoopError("executed quality stage was not selected")
    if stages and stages[0]["stage"] != "creator":
        raise QualityLoopError("quality stages must begin with creator execution")

    current: str | None = None
    creator_state = "not_executed"
    latest_review_state = "not_reviewed"
    latest_evaluation: Mapping[str, Any] | None = None
    latest_evaluated_digest: str | None = None
    enhancement_state = "not_enhanced"
    review_count = 0
    enhancement_count = 0
    reporter_seen = False
    creator_seen = False
    enhancer_seen = False
    for index, stage in enumerate(stages):
        name = stage["stage"]
        if reporter_seen:
            raise QualityLoopError("quality stages cannot continue after reporting")
        if name == "creator":
            if creator_seen or index != 0:
                raise QualityLoopError("quality receipt contains duplicate creator execution")
            creator_seen = True
            creator_state = stage["stage_state"]
            current = stage["output_subject_sha256"]
            if creator_state == "execution_failed" and len(stages) != 1:
                raise QualityLoopError("failed creator cannot be followed by later stages")
        elif name == "reviewer":
            if current is None or stage["input_subject_sha256"] != current:
                raise QualityLoopError("reviewer did not evaluate the current candidate")
            review_count += 1
            if review_count > MAX_REVIEW_CYCLES or stage["review_cycle"] != review_count:
                raise QualityLoopError("quality review cycle is invalid or unbounded")
            if stage["enhancement_pass"] != enhancement_count:
                raise QualityLoopError("reviewer enhancement-pass evidence is inconsistent")
            if stage["stage_state"] == "execution_succeeded":
                evaluation = stage["evaluation_receipt"]
                assert isinstance(evaluation, Mapping)
                if evaluation["subject"]["subject_type"] != subject_type or evaluation["subject"]["subject_id"] != subject_id:
                    raise QualityLoopError("reviewer evaluated a different subject identity")
                latest_evaluation = evaluation
                latest_evaluated_digest = current
                latest_review_state = "review_completed"
            else:
                latest_evaluation = None
                latest_evaluated_digest = None
                latest_review_state = "review_failed"
        elif name == "enhancer":
            if enhancer_seen or current is None or stage["input_subject_sha256"] != current:
                raise QualityLoopError("quality enhancer sequence is invalid")
            if (
                latest_evaluation is None
                or latest_evaluated_digest != current
                or latest_evaluation["result"]["state"] != "FAIL"
            ):
                raise QualityLoopError("enhancer lacks a failed review of the current candidate")
            enhancer_seen = True
            enhancement_count = 1
            current = stage["output_subject_sha256"]
            enhancement_state = (
                "enhancement_succeeded"
                if stage["stage_state"] == "execution_succeeded"
                else "enhancement_failed"
            )
            if stage["stage_state"] == "execution_succeeded":
                latest_evaluation = None
                latest_evaluated_digest = None
        else:
            if current is None or stage["input_subject_sha256"] != current:
                raise QualityLoopError("reporter did not report the current candidate")
            current_validation = "not_validated"
            if latest_evaluation is not None and latest_evaluated_digest == current:
                if latest_evaluation["result"]["state"] == "PASS":
                    current_validation = "validation_passed"
                elif latest_evaluation["result"]["state"] == "FAIL":
                    current_validation = "validation_failed"
            if stage["reported_validation_state"] != current_validation:
                raise QualityLoopError("reported validation state is not supported by evaluation evidence")
            reporter_seen = True

    if creator_state == "execution_succeeded":
        if original_digest != stages[0]["output_subject_sha256"]:
            raise QualityLoopError("quality original subject digest does not match creator output")
    elif original_digest is not None:
        raise QualityLoopError("quality receipt claims an original subject without creator success")
    if current != declared_current:
        raise QualityLoopError("quality current subject digest does not match the stage chain")

    validation_state = "not_validated"
    if latest_evaluation is not None and latest_evaluated_digest == current:
        if latest_evaluation["result"]["state"] == "PASS":
            validation_state = "validation_passed"
        elif latest_evaluation["result"]["state"] == "FAIL":
            validation_state = "validation_failed"
    derived_states = {
        "creation": "created" if creator_state == "execution_succeeded" else "not_created",
        "selection": "selected" if selected else "not_selected",
        "execution": creator_state,
        "review": latest_review_state,
        "enhancement": enhancement_state,
        "validation": validation_state,
        "reporting": "reported" if reporter_seen else "not_reported",
    }
    evidence_states = payload.get("evidence_states")
    if not isinstance(evidence_states, Mapping) or set(evidence_states) != _QUALITY_EVIDENCE_FIELDS:
        raise QualityLoopError("quality evidence-state schema is malformed")
    if dict(evidence_states) != derived_states:
        raise QualityLoopError("quality evidence states contradict the stage receipts")
    budgets = payload.get("budgets")
    expected_budgets = {
        "review_cycles_used": review_count,
        "enhancement_passes_used": enhancement_count,
    }
    if (
        not isinstance(budgets, Mapping)
        or set(budgets) != _QUALITY_BUDGET_FIELDS
        or any(type(budgets.get(field)) is not int for field in _QUALITY_BUDGET_FIELDS)
        or dict(budgets) != expected_budgets
    ):
        raise QualityLoopError("quality receipt budgets are inconsistent")
    if creator_state == "execution_failed":
        expected_outcome = "execution_failed"
    elif reporter_seen:
        expected_outcome = "reported"
    elif validation_state == "validation_passed":
        expected_outcome = "validation_passed"
    elif validation_state == "validation_failed":
        expected_outcome = "validation_failed"
    else:
        expected_outcome = "artifact_pending"
    if payload.get("outcome") != expected_outcome:
        raise QualityLoopError("quality receipt outcome contradicts its evidence")
    authority = payload.get("authority")
    if (
        not isinstance(authority, Mapping)
        or set(authority) != set(_QUALITY_AUTHORITY)
        or type(authority.get("automatic_execution")) is not bool
        or dict(authority) != _QUALITY_AUTHORITY
    ):
        raise QualityLoopError("quality receipt authority boundary is invalid")
    return json.loads(json.dumps(payload, ensure_ascii=False))


def validate_quality_receipt(
    payload: Any, *, registry: TrustedValidatorRegistry | None = None,
) -> dict[str, Any]:
    """Validate either a frozen v1 receipt or an explicit Slice 3B v2 receipt."""
    if not isinstance(payload, Mapping):
        raise QualityLoopError("quality receipt schema is invalid")
    if payload.get("schema_version") == QUALITY_LOOP_SCHEMA_VERSION:
        return _legacy_quality_receipt(payload)
    if payload.get("schema_version") == QUALITY_RECEIPT_SCHEMA_VERSION:
        return _validate_quality_receipt_v2(payload, registry=registry)
    raise QualityLoopError("quality receipt schema is unsupported")
