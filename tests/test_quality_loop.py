from __future__ import annotations

import copy
import unittest

from ash.quality_loop import (
    QualityLoopError,
    build_quality_loop_plan,
    validate_quality_loop_plan,
    validate_quality_receipt,
)


class QualityLoopTests(unittest.TestCase):
    def test_creator_reviewer_enhancer_plan_is_bounded_and_copy_on_write(self) -> None:
        plan = build_quality_loop_plan(
            creator_id="skill/creator",
            reviewer_ids=["skill/reviewer"],
            enhancer_ids=["skill/enhancer"],
            validation_requirements=["artifact_open", "visual_review"],
        )
        validated = validate_quality_loop_plan(plan)
        self.assertFalse(validated["automatic_execution"])
        self.assertEqual(validated["execution_authority"], "host_or_approved_runtime_only")
        enhancement = next(item for item in validated["steps"] if item["step"] == "conditional_enhancement")
        self.assertEqual(enhancement["artifact_policy"], "copy_on_write_preserve_original")
        self.assertEqual(validated["budgets"]["max_enhancement_passes"], 1)

    def test_role_overlap_and_unbounded_cycles_fail_closed(self) -> None:
        with self.assertRaises(QualityLoopError):
            build_quality_loop_plan(
                creator_id="skill/same",
                reviewer_ids=["skill/same"],
                enhancer_ids=[],
                validation_requirements=["review"],
            )
        with self.assertRaises(QualityLoopError):
            build_quality_loop_plan(
                creator_id="skill/creator",
                reviewer_ids=[],
                enhancer_ids=[],
                validation_requirements=["review"],
                max_review_cycles=99,
            )

    def test_enhancement_must_be_followed_by_revalidation(self) -> None:
        plan = build_quality_loop_plan(
            creator_id="skill/creator",
            reviewer_ids=[],
            enhancer_ids=["skill/enhancer"],
            validation_requirements=["artifact_open"],
        )
        bad = copy.deepcopy(plan)
        bad["steps"] = [item for item in bad["steps"] if item["step"] != "revalidate_artifact"]
        with self.assertRaises(QualityLoopError):
            validate_quality_loop_plan(bad)

    def test_receipt_cannot_claim_success_without_execution_artifact_and_validation(self) -> None:
        receipt = {
            "schema_version": "nexus.quality-loop.v1",
            "outcome": "validation_passed",
            "executed_capability_ids": ["skill/creator"],
            "artifact_reference": "artifact:opaque-123",
            "validation": {"passed": True},
        }
        self.assertEqual(validate_quality_receipt(receipt)["outcome"], "validation_passed")
        bad = copy.deepcopy(receipt)
        bad["executed_capability_ids"] = []
        with self.assertRaises(QualityLoopError):
            validate_quality_receipt(bad)


if __name__ == "__main__":
    unittest.main()
