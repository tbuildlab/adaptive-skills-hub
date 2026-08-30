from __future__ import annotations

import copy
from pathlib import Path
import unittest

from ash.evaluation import canonical_sha256, evaluate_contract, load_trusted_validator_registry
from ash.quality_loop import (
    QUALITY_RECEIPT_SCHEMA_VERSION,
    QualityLoopError,
    build_quality_stage_receipt,
    validate_quality_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
SUBJECT_A = "a" * 64
SUBJECT_B = "b" * 64


def evaluation_subject(digest: str, *, parent: str | None = None) -> dict:
    enhanced = parent is not None
    return {
        "subject_type": "artifact",
        "subject_id": "artifact-1",
        "subject_sha256": digest,
        "parent_subject_sha256": parent,
        "lifecycle": {
            "creation": "created",
            "selection": "selected",
            "execution": "execution_succeeded",
            "review": "not_reviewed",
            "enhancement": "enhancement_succeeded" if enhanced else "not_enhanced",
            "validation": "not_validated",
            "reporting": "not_reported",
        },
        "stage_receipts": {
            "creator": "1" * 64,
            "execution": "2" * 64,
            "reviewer": None,
            "enhancer": "4" * 64 if enhanced else None,
            "reporter": None,
        },
    }


def evaluation_receipt(registry, digest: str, *, passes: bool, parent: str | None = None) -> dict:
    observed = digest if passes else (SUBJECT_B if digest == SUBJECT_A else SUBJECT_A)
    return evaluate_contract(
        {
            "schema_version": "nexus.evaluation-request.v1",
            "validator_id": "nexus.validator.artifact-metadata",
            "validator_version": "1",
            "subject": evaluation_subject(digest, parent=parent),
            "checks": [
                {
                    "check_id": "subject-digest",
                    "operator": "sha256_matches_subject",
                    "required": True,
                    "expected": None,
                    "observed": observed,
                    "evidence": {
                        "evidence_id": "evidence-subject-digest",
                        "content_sha256": canonical_sha256(observed),
                        "summary": "Bounded artifact digest evidence.",
                    },
                }
            ],
        },
        registry=registry,
    )


def creator_stage(*, succeeds: bool = True) -> dict:
    return build_quality_stage_receipt(
        stage="creator",
        sequence=0,
        capability_id="skill/creator",
        stage_state="execution_succeeded" if succeeds else "execution_failed",
        input_subject_sha256=None,
        output_subject_sha256=SUBJECT_A if succeeds else None,
        evaluation_receipt=None,
        mutation_policy="new_candidate",
    )


def reviewer_stage(
    receipt: dict,
    *,
    sequence: int,
    digest: str,
    cycle: int,
    enhancement_pass: int,
    capability_id: str = "nexus.validator.artifact-metadata",
) -> dict:
    return build_quality_stage_receipt(
        stage="reviewer",
        sequence=sequence,
        capability_id=capability_id,
        stage_state="execution_succeeded",
        input_subject_sha256=digest,
        output_subject_sha256=digest,
        evaluation_receipt=receipt,
        mutation_policy="read_only",
        review_cycle=cycle,
        enhancement_pass=enhancement_pass,
    )


def quality_receipt(
    *,
    stages: list[dict],
    selected: list[str],
    original: str | None,
    current: str | None,
    evidence_states: dict,
    review_cycles: int,
    enhancement_passes: int,
    outcome: str,
) -> dict:
    return {
        "schema_version": QUALITY_RECEIPT_SCHEMA_VERSION,
        "workflow_id": "quality-workflow-1",
        "selected_capability_ids": selected,
        "subject": {
            "subject_type": "artifact",
            "subject_id": "artifact-1",
            "original_subject_sha256": original,
            "current_subject_sha256": current,
        },
        "stages": stages,
        "evidence_states": evidence_states,
        "budgets": {
            "review_cycles_used": review_cycles,
            "enhancement_passes_used": enhancement_passes,
        },
        "outcome": outcome,
        "authority": {
            "execution_authority": "host_or_approved_runtime_only",
            "mcp_execution_authority": "none",
            "automatic_execution": False,
            "reviewer_mutation_authority": "none",
        },
    }


class QualityLoopEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_trusted_validator_registry(root=ROOT)

    def test_valid_creator_reviewer_pass_chain(self) -> None:
        evaluation = evaluation_receipt(self.registry, SUBJECT_A, passes=True)
        stages = [creator_stage(), reviewer_stage(evaluation, sequence=1, digest=SUBJECT_A, cycle=1, enhancement_pass=0)]
        receipt = quality_receipt(
            stages=stages,
            selected=["skill/creator", "nexus.validator.artifact-metadata"],
            original=SUBJECT_A,
            current=SUBJECT_A,
            evidence_states={
                "creation": "created",
                "selection": "selected",
                "execution": "execution_succeeded",
                "review": "review_completed",
                "enhancement": "not_enhanced",
                "validation": "validation_passed",
                "reporting": "not_reported",
            },
            review_cycles=1,
            enhancement_passes=0,
            outcome="validation_passed",
        )
        self.assertEqual(
            validate_quality_receipt(receipt, registry=self.registry)["outcome"],
            "validation_passed",
        )

    def test_selected_without_execution_cannot_impersonate_validation(self) -> None:
        receipt = quality_receipt(
            stages=[],
            selected=["nexus.validator.artifact-metadata"],
            original=None,
            current=None,
            evidence_states={
                "creation": "not_created",
                "selection": "selected",
                "execution": "not_executed",
                "review": "not_reviewed",
                "enhancement": "not_enhanced",
                "validation": "validation_passed",
                "reporting": "not_reported",
            },
            review_cycles=0,
            enhancement_passes=0,
            outcome="validation_passed",
        )
        with self.assertRaises(QualityLoopError):
            validate_quality_receipt(receipt, registry=self.registry)

    def test_executed_without_review_remains_not_validated(self) -> None:
        receipt = quality_receipt(
            stages=[creator_stage()],
            selected=["skill/creator"],
            original=SUBJECT_A,
            current=SUBJECT_A,
            evidence_states={
                "creation": "created",
                "selection": "selected",
                "execution": "execution_succeeded",
                "review": "not_reviewed",
                "enhancement": "not_enhanced",
                "validation": "not_validated",
                "reporting": "not_reported",
            },
            review_cycles=0,
            enhancement_passes=0,
            outcome="artifact_pending",
        )
        validated = validate_quality_receipt(receipt, registry=self.registry)
        self.assertEqual(validated["evidence_states"]["validation"], "not_validated")

    def test_reported_without_validation_is_truthful_not_success(self) -> None:
        reporter = build_quality_stage_receipt(
            stage="reporter",
            sequence=1,
            capability_id="skill/reporter",
            stage_state="reported",
            input_subject_sha256=SUBJECT_A,
            output_subject_sha256=SUBJECT_A,
            evaluation_receipt=None,
            mutation_policy="read_only_report",
            reported_validation_state="not_validated",
        )
        receipt = quality_receipt(
            stages=[creator_stage(), reporter],
            selected=["skill/creator", "skill/reporter"],
            original=SUBJECT_A,
            current=SUBJECT_A,
            evidence_states={
                "creation": "created",
                "selection": "selected",
                "execution": "execution_succeeded",
                "review": "not_reviewed",
                "enhancement": "not_enhanced",
                "validation": "not_validated",
                "reporting": "reported",
            },
            review_cycles=0,
            enhancement_passes=0,
            outcome="reported",
        )
        validated = validate_quality_receipt(receipt, registry=self.registry)
        self.assertEqual(validated["evidence_states"]["validation"], "not_validated")

    def test_creator_without_reviewer_cannot_claim_reviewed(self) -> None:
        receipt = quality_receipt(
            stages=[creator_stage()],
            selected=["skill/creator"],
            original=SUBJECT_A,
            current=SUBJECT_A,
            evidence_states={
                "creation": "created",
                "selection": "selected",
                "execution": "execution_succeeded",
                "review": "review_completed",
                "enhancement": "not_enhanced",
                "validation": "not_validated",
                "reporting": "not_reported",
            },
            review_cycles=0,
            enhancement_passes=0,
            outcome="artifact_pending",
        )
        with self.assertRaises(QualityLoopError):
            validate_quality_receipt(receipt, registry=self.registry)

    def test_reviewer_pass_without_enhancer_cannot_claim_enhanced(self) -> None:
        evaluation = evaluation_receipt(self.registry, SUBJECT_A, passes=True)
        stages = [creator_stage(), reviewer_stage(evaluation, sequence=1, digest=SUBJECT_A, cycle=1, enhancement_pass=0)]
        receipt = quality_receipt(
            stages=stages,
            selected=["skill/creator", "nexus.validator.artifact-metadata"],
            original=SUBJECT_A,
            current=SUBJECT_A,
            evidence_states={
                "creation": "created",
                "selection": "selected",
                "execution": "execution_succeeded",
                "review": "review_completed",
                "enhancement": "enhancement_succeeded",
                "validation": "validation_passed",
                "reporting": "not_reported",
            },
            review_cycles=1,
            enhancement_passes=0,
            outcome="validation_passed",
        )
        with self.assertRaises(QualityLoopError):
            validate_quality_receipt(receipt, registry=self.registry)

    def test_reviewer_is_read_only_and_cannot_mutate_creator_output(self) -> None:
        evaluation = evaluation_receipt(self.registry, SUBJECT_A, passes=True)
        with self.assertRaises(QualityLoopError):
            build_quality_stage_receipt(
                stage="reviewer",
                sequence=1,
                capability_id="nexus.validator.artifact-metadata",
                stage_state="execution_succeeded",
                input_subject_sha256=SUBJECT_A,
                output_subject_sha256=SUBJECT_B,
                evaluation_receipt=evaluation,
                mutation_policy="read_only",
                review_cycle=1,
            )

    def test_enhancer_creates_new_candidate_preserves_original_and_requires_revalidation(self) -> None:
        failed = evaluation_receipt(self.registry, SUBJECT_A, passes=False)
        passed = evaluation_receipt(self.registry, SUBJECT_B, passes=True, parent=SUBJECT_A)
        enhancer = build_quality_stage_receipt(
            stage="enhancer",
            sequence=2,
            capability_id="skill/enhancer",
            stage_state="execution_succeeded",
            input_subject_sha256=SUBJECT_A,
            output_subject_sha256=SUBJECT_B,
            evaluation_receipt=None,
            mutation_policy="copy_on_write_preserve_original",
            enhancement_pass=1,
        )
        stages = [
            creator_stage(),
            reviewer_stage(failed, sequence=1, digest=SUBJECT_A, cycle=1, enhancement_pass=0),
            enhancer,
            reviewer_stage(passed, sequence=3, digest=SUBJECT_B, cycle=2, enhancement_pass=1),
        ]
        receipt = quality_receipt(
            stages=stages,
            selected=[
                "skill/creator",
                "nexus.validator.artifact-metadata",
                "skill/enhancer",
            ],
            original=SUBJECT_A,
            current=SUBJECT_B,
            evidence_states={
                "creation": "created",
                "selection": "selected",
                "execution": "execution_succeeded",
                "review": "review_completed",
                "enhancement": "enhancement_succeeded",
                "validation": "validation_passed",
                "reporting": "not_reported",
            },
            review_cycles=2,
            enhancement_passes=1,
            outcome="validation_passed",
        )
        validated = validate_quality_receipt(receipt, registry=self.registry)
        self.assertEqual(validated["subject"]["original_subject_sha256"], SUBJECT_A)
        self.assertEqual(validated["subject"]["current_subject_sha256"], SUBJECT_B)

    def test_enhancer_without_failed_review_fails_closed(self) -> None:
        passed = evaluation_receipt(self.registry, SUBJECT_A, passes=True)
        enhancer = build_quality_stage_receipt(
            stage="enhancer",
            sequence=2,
            capability_id="skill/enhancer",
            stage_state="execution_succeeded",
            input_subject_sha256=SUBJECT_A,
            output_subject_sha256=SUBJECT_B,
            evaluation_receipt=None,
            mutation_policy="copy_on_write_preserve_original",
            enhancement_pass=1,
        )
        receipt = quality_receipt(
            stages=[creator_stage(), reviewer_stage(passed, sequence=1, digest=SUBJECT_A, cycle=1, enhancement_pass=0), enhancer],
            selected=["skill/creator", "nexus.validator.artifact-metadata", "skill/enhancer"],
            original=SUBJECT_A,
            current=SUBJECT_B,
            evidence_states={},
            review_cycles=1,
            enhancement_passes=1,
            outcome="artifact_pending",
        )
        with self.assertRaises(QualityLoopError):
            validate_quality_receipt(receipt, registry=self.registry)

    def test_selected_reviewer_must_match_executed_validator(self) -> None:
        evaluation = evaluation_receipt(self.registry, SUBJECT_A, passes=True)
        bad_reviewer = reviewer_stage(
            evaluation,
            sequence=1,
            digest=SUBJECT_A,
            cycle=1,
            enhancement_pass=0,
            capability_id="skill/fake-reviewer",
        )
        receipt = quality_receipt(
            stages=[creator_stage(), bad_reviewer],
            selected=["skill/creator", "skill/fake-reviewer"],
            original=SUBJECT_A,
            current=SUBJECT_A,
            evidence_states={},
            review_cycles=1,
            enhancement_passes=0,
            outcome="validation_passed",
        )
        with self.assertRaises(QualityLoopError):
            validate_quality_receipt(receipt, registry=self.registry)

    def test_reported_success_without_evaluation_fails_closed(self) -> None:
        reporter = build_quality_stage_receipt(
            stage="reporter",
            sequence=1,
            capability_id="skill/reporter",
            stage_state="reported",
            input_subject_sha256=SUBJECT_A,
            output_subject_sha256=SUBJECT_A,
            evaluation_receipt=None,
            mutation_policy="read_only_report",
            reported_validation_state="validation_passed",
        )
        receipt = quality_receipt(
            stages=[creator_stage(), reporter],
            selected=["skill/creator", "skill/reporter"],
            original=SUBJECT_A,
            current=SUBJECT_A,
            evidence_states={},
            review_cycles=0,
            enhancement_passes=0,
            outcome="reported",
        )
        with self.assertRaises(QualityLoopError):
            validate_quality_receipt(receipt, registry=self.registry)

    def test_stage_digest_tamper_and_review_cycle_overflow_fail_closed(self) -> None:
        evaluation = evaluation_receipt(self.registry, SUBJECT_A, passes=True)
        stage = reviewer_stage(evaluation, sequence=1, digest=SUBJECT_A, cycle=1, enhancement_pass=0)
        tampered = copy.deepcopy(stage)
        tampered["stage_receipt_sha256"] = "f" * 64
        receipt = quality_receipt(
            stages=[creator_stage(), tampered],
            selected=["skill/creator", "nexus.validator.artifact-metadata"],
            original=SUBJECT_A,
            current=SUBJECT_A,
            evidence_states={},
            review_cycles=1,
            enhancement_passes=0,
            outcome="validation_passed",
        )
        with self.assertRaises(QualityLoopError):
            validate_quality_receipt(receipt, registry=self.registry)

        third_review = reviewer_stage(
            evaluation,
            sequence=3,
            digest=SUBJECT_A,
            cycle=2,
            enhancement_pass=0,
        )
        overflow = quality_receipt(
            stages=[
                creator_stage(),
                reviewer_stage(evaluation, sequence=1, digest=SUBJECT_A, cycle=1, enhancement_pass=0),
                reviewer_stage(evaluation, sequence=2, digest=SUBJECT_A, cycle=2, enhancement_pass=0),
                third_review,
            ],
            selected=["skill/creator", "nexus.validator.artifact-metadata"],
            original=SUBJECT_A,
            current=SUBJECT_A,
            evidence_states={},
            review_cycles=2,
            enhancement_passes=0,
            outcome="validation_passed",
        )
        with self.assertRaises(QualityLoopError):
            validate_quality_receipt(overflow, registry=self.registry)

    def test_failed_enhancer_preserves_original_failed_validation_evidence(self) -> None:
        failed = evaluation_receipt(self.registry, SUBJECT_A, passes=False)
        enhancer = build_quality_stage_receipt(
            stage="enhancer",
            sequence=2,
            capability_id="skill/enhancer",
            stage_state="execution_failed",
            input_subject_sha256=SUBJECT_A,
            output_subject_sha256=SUBJECT_A,
            evaluation_receipt=None,
            mutation_policy="copy_on_write_preserve_original",
            enhancement_pass=1,
        )
        receipt = quality_receipt(
            stages=[
                creator_stage(),
                reviewer_stage(failed, sequence=1, digest=SUBJECT_A, cycle=1, enhancement_pass=0),
                enhancer,
            ],
            selected=["skill/creator", "nexus.validator.artifact-metadata", "skill/enhancer"],
            original=SUBJECT_A,
            current=SUBJECT_A,
            evidence_states={
                "creation": "created",
                "selection": "selected",
                "execution": "execution_succeeded",
                "review": "review_completed",
                "enhancement": "enhancement_failed",
                "validation": "validation_failed",
                "reporting": "not_reported",
            },
            review_cycles=1,
            enhancement_passes=1,
            outcome="validation_failed",
        )
        validated = validate_quality_receipt(receipt, registry=self.registry)
        self.assertEqual(validated["subject"]["current_subject_sha256"], SUBJECT_A)

    def test_secret_shaped_stage_identifier_fails_closed(self) -> None:
        with self.assertRaises(QualityLoopError):
            build_quality_stage_receipt(
                stage="creator",
                sequence=0,
                capability_id="sk-" + "A" * 32,
                stage_state="execution_succeeded",
                input_subject_sha256=None,
                output_subject_sha256=SUBJECT_A,
                evaluation_receipt=None,
                mutation_policy="new_candidate",
            )


if __name__ == "__main__":
    unittest.main()
