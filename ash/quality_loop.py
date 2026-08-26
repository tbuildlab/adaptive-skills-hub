"""Bounded, data-only creator/reviewer/enhancer workflow contracts.

The functions here describe and validate a future execution sequence.  They do
not call a Skill, Agent, tool, subprocess, network endpoint, or artifact API.
"""
from __future__ import annotations

import json
from typing import Any, Mapping, Sequence


QUALITY_LOOP_SCHEMA_VERSION = "nexus.quality-loop.v1"
MAX_REVIEW_CYCLES = 2
MAX_ENHANCEMENT_PASSES = 1
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


def validate_quality_receipt(payload: Any) -> dict[str, Any]:
    """Validate truthful executed-vs-validated evidence for one loop attempt."""
    if not isinstance(payload, Mapping) or payload.get("schema_version") != QUALITY_LOOP_SCHEMA_VERSION:
        raise QualityLoopError("quality receipt schema is invalid")
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
