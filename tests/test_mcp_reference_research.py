from __future__ import annotations

from contextlib import asynccontextmanager
import json
from pathlib import Path
import sys
import tempfile
import unittest

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from ash.reference_research import reference_research_plan
from tests.test_reference_research import WEBSITE_CASES, WEBSITE_TASK


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TASK = "Create a new editable PowerPoint presentation project"
CASES = (
    (REQUIRED_TASK, "required"),
    (REQUIRED_TASK + " from this complete specification", "reduced"),
    ("Edit an editable PowerPoint presentation; tiny label typo", "skipped"),
    (REQUIRED_TASK + "; do not search", "skipped"),
)

# Exercise the actual MCP server, adapter, planner, guarded loader and serializer.
# Only the trusted catalog is a controlled fixture; no plan/result is mocked.
SERVER = """
import asyncio, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from tests.test_mcp_redaction import make_skill
from ash.mcp.adapter import NexusMcpRuntime
from ash.mcp.authorization import WorkspaceAuthorizer
from ash.mcp.server import run_stdio
root = Path(sys.argv[2])
skills = root / 'skills'
skill = make_skill(skills, 'ppt-safe', 'Create and edit editable PowerPoint presentation decks', 'RAW_SKILL_SENTINEL')
catalog = {'skills': [skill] if sys.argv[3] == 'covered' else [], 'agents': []}
runtime = NexusMcpRuntime(WorkspaceAuthorizer.from_roots_for_test({'project': root}),
    catalog_builder=lambda: catalog, skill_roots=[skills])
asyncio.run(run_stdio(runtime))
"""


class McpReferenceResearchTests(unittest.IsolatedAsyncioTestCase):
    @asynccontextmanager
    async def session(self, *, covered=True, conflict=False):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            if conflict:
                (root / "AGENTS.md").write_text("MUST NOT use ppt-safe\n", encoding="utf-8")
            params = StdioServerParameters(command=sys.executable,
                args=["-B", "-c", SERVER, str(ROOT), str(root), "covered" if covered else "uncovered"],
                cwd=str(ROOT))
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield session

    async def plan(self, session, task, *, context="none", constraints=()):
        result = await session.call_tool("nexus.plan_task", {
            "task": task, "workspace_id": "project", "project_context_mode": context,
            "constraints": list(constraints),
        })
        self.assertFalse(result.is_error)
        return json.loads(result.content[0].text)

    async def test_actual_mcp_serializes_existing_policy_for_covered_tasks(self):
        async with self.session() as session:
            for task, expected in CASES:
                with self.subTest(task=task):
                    payload = await self.plan(session, task)
                    research = payload["reference_research"]
                    policy = json.loads(json.dumps(reference_research_plan(task).to_dict()))
                    self.assertEqual({k: v for k, v in research.items() if k != "reusable_references"},
                                     {k: v for k, v in policy.items() if k != "reusable_references"})
                    self.assertEqual(research["status"], expected)
                    self.assertEqual(payload["status"], "planned")
                    self.assertEqual(payload["fallback"]["status"], "not_needed")
                    self.assertTrue(payload["selected_skills"])
                    self.assertTrue(all(item["load_status"] == "loaded" for item in payload["selected_skills"]))
                    self.assertNotIn("RAW_SKILL_SENTINEL", json.dumps(payload))

    async def test_actual_mcp_retains_bounded_original_design_and_hold_policy(self):
        async with self.session() as session:
            research = (await self.plan(session, REQUIRED_TASK))["reference_research"]
            self.assertLessEqual(research["candidate_limit"], 6)
            self.assertEqual(research["sources"][0], "official_documentation")
            self.assertIn("patterns_only_no_code_reuse", research["license_policy"])
            self.assertIn("record_no_suitable_reference", research["no_suitable_reference_fallback"])
            self.assertIn("reference_derived_vs_nexus_designed", research["no_suitable_reference_fallback"])
            self.assertIn("continue_plan_build_test_verify", research["no_suitable_reference_fallback"])
            self.assertIn("no_permission_expansion", research["security_policy"])
            self.assertEqual(research["security_conflict_outcome"], "HOLD_owner_decision")

    async def test_real_coverage_gap_still_requires_fallback_with_research_visible(self):
        async with self.session(covered=False) as session:
            payload = await self.plan(session, REQUIRED_TASK)
            self.assertEqual(payload["reference_research"]["status"], "required")
            self.assertEqual(payload["status"], "fallback_needed")
            self.assertEqual(payload["fallback"]["reason_code"], "CAPABILITY_NOT_COVERED")
            self.assertEqual(payload["selected_skills"], [])

    async def test_website_creation_research_does_not_force_missing_coverage(self):
        async with self.session(covered=False) as session:
            for task, expected in WEBSITE_CASES:
                with self.subTest(task=task):
                    payload = await self.plan(session, task)
                    self.assertEqual(payload["reference_research"]["status"], expected)
                    self.assertEqual(payload["status"], "fallback_needed")
                    self.assertEqual(payload["fallback"]["reason_code"], "CAPABILITY_NOT_COVERED")
                    self.assertEqual(payload["selected_skills"], [])

    async def test_website_creation_security_scope_conflict_retains_hold(self):
        async with self.session(covered=False) as session:
            payload = await self.plan(session, WEBSITE_TASK, constraints=("network", "no_network"))
            self.assertEqual(payload["reference_research"]["status"], "required")
            self.assertEqual(payload["reference_research"]["security_conflict_outcome"], "HOLD_owner_decision")
            self.assertEqual(payload["status"], "fallback_needed")
            self.assertEqual(payload["selected_skills"], [])

    async def test_project_prohibition_is_not_promoted_to_planned(self):
        async with self.session(conflict=True) as session:
            payload = await self.plan(session, REQUIRED_TASK, context="governance")
            self.assertEqual(payload["reference_research"]["security_conflict_outcome"], "HOLD_owner_decision")
            self.assertEqual(payload["status"], "fallback_needed")
            self.assertEqual(payload["selected_skills"], [])

    async def test_security_scope_conflict_retains_owner_hold_and_no_selection(self):
        async with self.session() as session:
            payload = await self.plan(session, REQUIRED_TASK, constraints=("network", "no_network"))
            self.assertEqual(payload["reference_research"]["security_conflict_outcome"], "HOLD_owner_decision")
            self.assertEqual(payload["status"], "fallback_needed")
            self.assertEqual(payload["selected_skills"], [])


if __name__ == "__main__":
    unittest.main()
