from __future__ import annotations

import unittest

from ash.reference_research import reference_research_plan


class ReferenceResearchPolicyTests(unittest.TestCase):
    def test_new_substantial_project_defaults_to_bounded_research(self) -> None:
        plan = reference_research_plan("Build a new web app")
        self.assertEqual(plan.status, "required")
        self.assertEqual(plan.trigger, "substantial_project_work")

    def test_major_refactor_triggers_and_new_project_types_are_broad(self) -> None:
        for task in (
            "Refactor the architecture of our existing desktop app",
            "Create a new MCP plugin",
            "Build a client-ready data workflow",
            "Develop a portfolio project from scratch",
        ):
            with self.subTest(task=task):
                self.assertEqual(reference_research_plan(task).status, "required")

    def test_tiny_edit_and_focused_bug_fix_skip_research(self) -> None:
        for task in ("Fix a typo in the website button label", "Fix a simple CLI bug"):
            with self.subTest(task=task):
                self.assertEqual(reference_research_plan(task).status, "skipped")

    def test_user_opt_out_skips_research(self) -> None:
        plan = reference_research_plan("Build a new app; do not search GitHub")
        self.assertEqual(plan.status, "skipped")
        self.assertEqual(plan.trigger, "user_opt_out")
        self.assertEqual(reference_research_plan("创建一个新网站，但不要搜索 GitHub").trigger, "user_opt_out")

    def test_exact_spec_reduces_research_to_missing_points(self) -> None:
        plan = reference_research_plan("Build a new app from this complete specification and acceptance criteria")
        self.assertEqual(plan.status, "reduced")
        self.assertEqual(plan.trigger, "complete_spec_missing_points")
        self.assertEqual(reference_research_plan("根据完整规范构建新工具").status, "reduced")
        self.assertEqual(reference_research_plan("Create a new app using React").status, "reduced")

    def test_simplified_chinese_project_request_triggers(self) -> None:
        plan = reference_research_plan("创建一个新网站")
        self.assertEqual(plan.status, "required")

    def test_multiple_sources_comparison_and_license_guard_are_explicit(self) -> None:
        plan = reference_research_plan("Create a new API service")
        self.assertEqual(len(plan.minimum_reference_set), 3)
        self.assertEqual(plan.sources[0], "official_documentation")
        self.assertIn("compare_multiple_sources", plan.single_repository_policy)
        self.assertIn("unknown_or_unclear_license", plan.license_policy)
        self.assertIn("reference_derived_vs_nexus_designed", plan.synthesis_fields)

    def test_research_is_bounded_and_no_reference_never_blocks_build(self) -> None:
        plan = reference_research_plan("Build a new developer tool")
        self.assertLessEqual(plan.candidate_limit, 6)
        self.assertIn("continue_plan_build_test_verify", plan.no_suitable_reference_fallback)
        self.assertIn("record_no_suitable_reference", plan.no_suitable_reference_fallback)

    def test_security_conflict_stays_inside_existing_authority(self) -> None:
        plan = reference_research_plan("Design a new security-sensitive API service")
        self.assertIn("no_permission_expansion", plan.security_policy)
        self.assertIn("owner_decision", plan.security_policy)
        self.assertEqual(plan.security_conflict_outcome, "HOLD_owner_decision")

    def test_simple_non_project_question_has_no_research_overhead(self) -> None:
        self.assertEqual(reference_research_plan("What is an API?").status, "skipped")


if __name__ == "__main__":
    unittest.main()
