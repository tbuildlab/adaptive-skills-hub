from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ash.discovery import build_index, discover_skills
from ash.execution import execute_route
from ash.router import route_task


SOURCES = [
    {"id": "awesome-llm-apps", "kind": "reference", "categories": ["llm", "agent", "research", "architecture"], "use_for": ["AI architecture examples"], "avoid_for": []},
    {"id": "deer-flow", "kind": "framework", "categories": ["agent", "workflow", "orchestration", "research"], "use_for": ["complex agent workflows"], "avoid_for": ["simple tasks"]},
    {"id": "liquid-glass-react", "kind": "reference", "categories": ["react", "frontend", "ui", "liquid-glass"], "use_for": ["React Glass"], "avoid_for": ["unrelated backend"]},
]


def skill(root: Path, folder: str, name: str, description: str, extra: str = "") -> Path:
    path = root / folder
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n{extra}---\n\n# {name}\n\nProcedure.\n", encoding="utf-8")
    return path


class AdaptiveSkillsHubTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.hub = self.workspace / "adaptive-skills-hub"
        self.hub.mkdir()
        skill(self.workspace, "requirements", "requirements-analysis", "React dashboard requirements analysis", "hub_after: []\n")
        skill(self.workspace, "dashboard", "dashboard-ui", "React dashboard UI design accessibility", "hub_after: [\"requirements-analysis\"]\n")
        skill(self.workspace, "backend", "backend-api", "Backend API implementation and endpoint debugging")
        skill(self.workspace, "research", "research-architecture", "AI research agent architecture and LLM workflows")
        skill(self.workspace, "presentation", "business-ppt", "Create PowerPoint presentations and PPT slide decks")
        agents = self.workspace / ".codex" / "agents"
        agents.mkdir(parents=True)
        (agents / "engineering-backend-architect.toml").write_text('name = "backend-architect"\ndescription = "Backend API architecture"\n', encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def index(self) -> dict:
        return build_index(self.workspace, self.hub)

    def test_a_frontend_selects_only_complementary_ui_chain(self) -> None:
        route = route_task("Improve this React dashboard UI.", self.index(), SOURCES)
        self.assertEqual(route["capabilities"], ["frontend"])
        self.assertEqual([item["name"] for item in route["selected_skills"]], ["requirements-analysis", "dashboard-ui"])
        self.assertNotIn("backend-api", [item["name"] for item in route["selected_skills"]])
        self.assertIn("liquid-glass-react", {item["id"] for item in route["external_candidates"]})
        self.assertIn("deer-flow", {item["id"] for item in route["skipped_sources"]})

    def test_b_backend_avoids_ui_and_uses_available_backend_capability(self) -> None:
        route = route_task("Fix this backend API bug.", self.index(), SOURCES)
        names = [item["name"] for item in route["selected_skills"]]
        self.assertIn("backend-api", names)
        self.assertNotIn("dashboard-ui", names)
        self.assertFalse(route["no_matching_skill"])

    def test_c_research_considers_reference_and_only_uses_deerflow_when_complex(self) -> None:
        simple = route_task("Design an AI research assistant architecture.", self.index(), SOURCES)
        self.assertIn("research-architecture", [item["name"] for item in simple["selected_skills"]])
        self.assertIn("awesome-llm-apps", {item["id"] for item in simple["external_candidates"]})
        self.assertIn("deer-flow", {item["id"] for item in simple["skipped_sources"]})
        complex_route = route_task("Design a complex multi-agent research orchestration architecture.", self.index(), SOURCES)
        self.assertIn("deer-flow", {item["id"] for item in complex_route["external_candidates"]})

    def test_d_missing_skill_is_truthful(self) -> None:
        route = route_task("Repair a COBOL mainframe batch job.", self.index(), SOURCES)
        self.assertTrue(route["no_matching_skill"])
        self.assertEqual(route["selected_skills"], [])

    def test_e_selected_skill_is_fully_loaded_and_optional_hook_is_validated(self) -> None:
        command = '["{python}", "-c", "from pathlib import Path; Path(\'marker.txt\').write_text(\'ok\')"]'
        validate = '["{python}", "-c", "from pathlib import Path; raise SystemExit(0 if Path(\'marker.txt\').read_text() == \'ok\' else 1)"]'
        skill(self.workspace, "runner", "marker-runner", "Execute a marker workflow", f"hub_command: {command}\nhub_validate: {validate}\n")
        route = route_task("Execute a marker workflow.", self.index(), SOURCES)
        result = execute_route(route, allow_skill_commands=True)
        selected = {item["name"] for item in route["selected_skills"]}
        self.assertIn("marker-runner", selected)
        loaded = next(item for item in result["loaded_skills"] if item["name"] == "marker-runner")
        self.assertGreater(loaded["characters"], 0)
        executed = next(item for item in result["execution"] if item["name"] == "marker-runner")
        self.assertEqual(executed["status"], "command_executed")
        self.assertEqual(result["validation"][0]["returncode"], 0)

    def test_f_equal_authority_duplicates_fail_closed_without_full_content_inspection(self) -> None:
        skill(self.workspace, "duplicate-a", "same-name", "identical duplicate")
        skill(self.workspace, "duplicate-b", "same-name", "identical duplicate")
        bad = self.workspace / "bad"
        bad.mkdir()
        (bad / "SKILL.md").write_text("---\nname: broken\n", encoding="utf-8")
        records = discover_skills([self.workspace], self.workspace, exclude_roots=[self.hub])
        duplicates = [item for item in records if item["name"] == "same-name"]
        self.assertEqual(len(duplicates), 2)
        self.assertTrue(all(item["status"] == "duplicate_conflict" for item in duplicates))
        self.assertTrue(all(item["duplicate_role"] == "conflict" for item in duplicates))
        self.assertTrue(all(item["metadata_fingerprint"] for item in duplicates))
        malformed = next(item for item in records if item["path"].endswith("bad"))
        self.assertEqual(malformed["status"], "malformed")
        self.assertIn("closing delimiter", malformed["scan_error"])

    def test_z_equal_authority_divergent_duplicates_fail_closed(self) -> None:
        skill(self.workspace, "conflict-a", "same-name", "first divergent copy")
        skill(self.workspace, "conflict-b", "same-name", "second divergent copy")
        index = self.index()
        duplicates = [item for item in index["skills"] if item["name"] == "same-name"]
        self.assertTrue(all(item["status"] == "duplicate_conflict" for item in duplicates))
        self.assertTrue(all(item["canonical_skill_id"] is None for item in duplicates))
        resolution = next(item for item in index["duplicate_resolutions"] if item["name"] == "same-name")
        self.assertEqual(resolution["outcome"], "conflict")
        route = route_task("Use same-name duplicate workflow.", index, SOURCES)
        self.assertNotIn("same-name", [item["name"] for item in route["selected_skills"]])

    def test_aa_maintained_project_copy_wins_over_divergent_project_copy(self) -> None:
        maintained = skill(self.workspace, "maintained", "canonical-workflow", "maintained version")
        (maintained / ".git").mkdir()
        skill(self.workspace, "unmanaged", "canonical-workflow", "unmanaged divergent version")
        records = discover_skills([self.workspace], self.workspace, exclude_roots=[self.hub])
        copies = [item for item in records if item["name"] == "canonical-workflow"]
        canonical = next(item for item in copies if item["duplicate_role"] == "canonical")
        self.assertTrue(canonical["provenance"]["maintained_checkout"])
        self.assertEqual(canonical["status"], "available")
        route = route_task("Use maintained version workflow.", {"skills": copies, "agents": []}, SOURCES)
        self.assertEqual([item["name"] for item in route["selected_skills"]], ["canonical-workflow"])
        self.assertEqual(route["selected_skills"][0]["id"], canonical["id"])

    def test_g_presentation_word_inside_api_repair_does_not_select_presentation_skill(self) -> None:
        index = self.index()
        index["skills"] = [item for item in index["skills"] if item["name"] != "backend-api"]
        route = route_task("Fix the backend API endpoint that imports PowerPoint files.", index, SOURCES)
        self.assertTrue(route["no_matching_skill"])
        self.assertEqual(route["selected_skills"], [])
        self.assertEqual(route["rejected_skills"][0]["name"], "business-ppt")

    def test_h_capability_match_selects_ui_skill_with_different_wording(self) -> None:
        route = route_task("Improve the accessibility and layout of a React dashboard.", self.index(), SOURCES)
        self.assertIn("dashboard-ui", [item["name"] for item in route["selected_skills"]])

    def test_i_generic_review_does_not_select_a_security_skill(self) -> None:
        skill(self.workspace, "security", "security-review", "Security vulnerability and threat-model review")
        route = route_task("Review this feature and create a regression test plan.", self.index(), SOURCES)
        self.assertNotIn("security-review", [item["name"] for item in route["selected_skills"]])

    def test_j_generic_presentation_selects_presentation_skill(self) -> None:
        route = route_task("Create an editable presentation.", self.index(), SOURCES)
        self.assertIn("business-ppt", [item["name"] for item in route["selected_skills"]])

    def test_k_frontend_task_does_not_select_a_presentation_skill_for_html_terminology(self) -> None:
        route = route_task("Improve the accessibility and layout of a React dashboard.", self.index(), SOURCES)
        self.assertNotIn("business-ppt", [item["name"] for item in route["selected_skills"]])

    def test_l_generic_research_does_not_select_a_threat_model_skill_for_architecture_terminology(self) -> None:
        skill(self.workspace, "threat", "security-threat-model", "Security threat model and architecture review")
        route = route_task("Research and structure evidence for a business assignment.", self.index(), SOURCES)
        self.assertNotIn("security-threat-model", [item["name"] for item in route["selected_skills"]])

    def test_m_codex_skin_requires_an_explicit_codex_theme_task(self) -> None:
        skill(self.workspace, "skin", "codex-skin", "Apply and verify a Codex desktop skin")
        unrelated = route_task("Diagnose the dependency manifest and explain current pins.", self.index(), SOURCES)
        self.assertNotIn("codex-skin", [item["name"] for item in unrelated["selected_skills"]])
        explicit = route_task("Apply a theme skin to the Codex desktop app.", self.index(), SOURCES)
        self.assertIn("codex-skin", [item["name"] for item in explicit["selected_skills"]])

    def test_n_folded_description_metadata_routes_the_real_skill_trigger(self) -> None:
        path = self.workspace / "history" / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            "---\nname: commit-archaeologist\ndescription: >-\n"
            "  Reconstruct why code exists from local git history.\n"
            "  Use for history and intent questions.\n---\n\n# History\n",
            encoding="utf-8",
        )
        route = route_task("Use git history to explain why this code exists.", self.index(), SOURCES)
        self.assertIn("commit-archaeologist", [item["name"] for item in route["selected_skills"]])

    def test_o_dependency_and_history_form_a_precise_complementary_chain(self) -> None:
        skill(self.workspace, "doctor", "dependency-doctor", "Diagnose a dependency manifest and dependency pins")
        skill(self.workspace, "history", "commit-archaeologist", "Trace git history to explain why code exists")
        skill(self.workspace, "scope", "scope-creep-detector", "Review a git diff against its stated intent")
        route = route_task("Diagnose a dependency manifest, then trace git history to explain its pins.", self.index(), SOURCES)
        names = [item["name"] for item in route["selected_skills"]]
        self.assertEqual(set(names), {"dependency-doctor", "commit-archaeologist"})

    def test_p_scope_review_does_not_select_history_analysis_without_a_history_question(self) -> None:
        skill(self.workspace, "scope", "scope-creep-detector", "Review a git diff against its stated intent")
        skill(self.workspace, "history", "commit-archaeologist", "Trace git history to explain why code exists")
        route = route_task("Review the working-tree diff for scope creep before merging.", self.index(), SOURCES)
        self.assertEqual([item["name"] for item in route["selected_skills"]], ["scope-creep-detector"])

    def test_q_fact_check_routes_to_evidence_research_without_security_false_positive(self) -> None:
        skill(self.workspace, "evidence", "evidence-first-research", "Research and verify factual claims with traceable evidence and citations")
        skill(self.workspace, "security", "security-review", "Security vulnerability and threat-model review")
        route = route_task("Fact check the evidence and citations in this research brief.", self.index(), SOURCES)
        names = [item["name"] for item in route["selected_skills"]]
        self.assertIn("evidence-first-research", names)
        self.assertNotIn("security-review", names)

    def test_r_document_pdf_and_standalone_workbook_gates_reject_incidental_controls(self) -> None:
        skill(self.workspace, "documents", "documents", "Create Word DOCX documents and reports")
        skill(self.workspace, "pdf", "pdf", "Create and inspect PDF files")
        skill(self.workspace, "live-excel", "excel-live-control", "Control an active live Microsoft Excel workbook")
        skill(self.workspace, "books", "Spreadsheets", "Create standalone XLSX workbooks with formulas")
        document = route_task("Create a concise editable Word memo.", self.index(), SOURCES)
        self.assertEqual([item["name"] for item in document["selected_skills"]], ["documents"])
        pdf = route_task("Create a one-page PDF project brief.", self.index(), SOURCES)
        self.assertEqual([item["name"] for item in pdf["selected_skills"]], ["pdf"])
        workbook = route_task("Create an editable Excel workbook with formulas.", self.index(), SOURCES)
        self.assertIn("Spreadsheets", [item["name"] for item in workbook["selected_skills"]])
        self.assertNotIn("excel-live-control", [item["name"] for item in workbook["selected_skills"]])
        pdf_report = route_task("Create and validate a PDF report.", self.index(), SOURCES)
        self.assertEqual([item["name"] for item in pdf_report["selected_skills"]], ["pdf"])

    def test_s_backend_testing_does_not_select_research_or_animation_skills(self) -> None:
        skill(self.workspace, "research", "evidence-first-research", "Research and verify factual claims with evidence")
        skill(self.workspace, "animation", "gsap-core", "Create JavaScript frontend animation and motion")
        route = route_task("Fix a Python backend API validation bug and add regression tests.", self.index(), SOURCES)
        names = [item["name"] for item in route["selected_skills"]]
        self.assertNotIn("evidence-first-research", names)
        self.assertNotIn("gsap-core", names)

    def test_t_specialized_creator_and_review_skills_require_explicit_targets(self) -> None:
        skill(self.workspace, "plugin", "plugin-creator", "Create Codex plugins")
        skill(self.workspace, "review", "review-agent", "Review a code change or diff")
        route = route_task("Fact check the evidence in this research brief.", self.index(), SOURCES)
        names = [item["name"] for item in route["selected_skills"]]
        self.assertNotIn("plugin-creator", names)
        self.assertNotIn("review-agent", names)

    def test_u_file_format_terms_inside_api_repairs_do_not_select_artifact_skills(self) -> None:
        skill(self.workspace, "documents", "documents", "Create Word DOCX documents")
        skill(self.workspace, "pdf", "pdf", "Create and inspect PDF files")
        skill(self.workspace, "books", "Spreadsheets", "Create standalone Excel XLSX workbooks")
        for task in (
            "Fix the API endpoint that uploads Word documents.",
            "Fix the backend endpoint that receives Excel uploads.",
            "Debug the API responsible for storing PDF files.",
        ):
            names = [item["name"] for item in route_task(task, self.index(), SOURCES)["selected_skills"]]
            self.assertNotIn("documents", names)
            self.assertNotIn("pdf", names)
            self.assertNotIn("Spreadsheets", names)

    def test_v_backend_and_regression_skills_chain_only_for_real_code_failure_work(self) -> None:
        skill(self.workspace, "backend-debug", "evidence-driven-backend-debugging", "Diagnose reproducible backend API HTTP failures and apply the smallest verified fix")
        skill(
            self.workspace,
            "regression",
            "regression-first-testing",
            "Turn a confirmed software fix into a focused regression test.",
            "metadata:\n  hub_after: [\"evidence-driven-backend-debugging\"]\n",
        )
        route = route_task("Fix an API HTTP 500 and add a regression test for the failure.", self.index(), SOURCES)
        self.assertEqual(
            [item["name"] for item in route["selected_skills"]],
            ["evidence-driven-backend-debugging", "regression-first-testing"],
        )

    def test_w_backend_and_testing_skills_reject_artifact_and_research_false_positives(self) -> None:
        skill(self.workspace, "backend-debug", "evidence-driven-backend-debugging", "Diagnose reproducible backend API HTTP failures and apply the smallest verified fix")
        skill(self.workspace, "regression", "regression-first-testing", "Turn a confirmed software fix into a focused regression test")
        for task in (
            "Create a PowerPoint explaining backend architecture.",
            "Research software testing trends and cite sources.",
            "Write a Word report about API security.",
            "Create an Excel workbook of test results.",
            "Create a PDF explaining backend architecture.",
            "Test whether this website is reachable.",
        ):
            names = [item["name"] for item in route_task(task, self.index(), SOURCES)["selected_skills"]]
            self.assertNotIn("evidence-driven-backend-debugging", names, task)
            self.assertNotIn("regression-first-testing", names, task)

    def test_x_authorization_remediation_uses_security_fix_guidance_not_threat_modeling(self) -> None:
        skill(self.workspace, "backend-debug", "evidence-driven-backend-debugging", "Diagnose reproducible backend API HTTP failures and apply the smallest verified fix")
        skill(self.workspace, "regression", "regression-first-testing", "Turn a confirmed software fix into a focused regression test")
        skill(self.workspace, "security-best", "security-best-practices", "Perform secure coding reviews and security remediation guidance")
        skill(self.workspace, "threat", "security-threat-model", "Threat model abuse paths and attacker capabilities")
        index = self.index()
        index["skills"] = [item for item in index["skills"] if item["name"] != "backend-api"]
        route = route_task("Fix an authorization defect in a backend API endpoint and add a regression test.", index, SOURCES)
        names = [item["name"] for item in route["selected_skills"]]
        self.assertIn("security-best-practices", names)
        self.assertNotIn("security-threat-model", names)

    def test_y_artifact_terms_and_research_do_not_trigger_code_or_ui_workflows(self) -> None:
        skill(self.workspace, "documents", "documents", "Create Word DOCX documents and reports")
        skill(self.workspace, "evidence", "evidence-first-research", "Research and verify factual claims with traceable evidence")
        skill(self.workspace, "emil", "emil-design-eng", "Implement and review frontend UI design")
        skill(self.workspace, "backend-debug", "evidence-driven-backend-debugging", "Diagnose reproducible backend API HTTP failures and apply the smallest verified fix")
        index = self.index()
        index["skills"] = [item for item in index["skills"] if item["name"] != "backend-api"]
        word = route_task("Write a Word report about API security.", index, SOURCES)
        self.assertIn("documents", [item["name"] for item in word["selected_skills"]])
        security_guidance = route_task("Provide secure coding guidance for a Python API authentication issue.", index, SOURCES)
        self.assertNotIn("evidence-driven-backend-debugging", [item["name"] for item in security_guidance["selected_skills"]])
        research = route_task("Research software testing trends and cite sources.", index, SOURCES)
        self.assertIn("evidence-first-research", [item["name"] for item in research["selected_skills"]])
        self.assertNotIn("emil-design-eng", [item["name"] for item in research["selected_skills"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
