from __future__ import annotations

import json
import hashlib
from pathlib import Path
import tempfile
import unittest

from ash.mcp.adapter import NexusMcpRuntime
from ash.mcp.authorization import WorkspaceAuthorizer
from ash.semantic_domains import make_trusted_applicability


def make_skill(root: Path, name: str, description: str, body: str) -> dict:
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(f"---\nname: {name}\ndescription: {description}\n---\n{body}", encoding="utf-8")
    return {
        "id": f"skill:{name}", "kind": "skill", "name": name,
        "description": description, "path": str(path.parent),
        "skill_md_path": str(path), "scope": "project", "source": "local",
        "tags": ["presentation"], "status": "available", "metadata": {},
        "provenance": {"source_scope": "project-specific", "precedence": 40},
        "content_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "content_bytes": path.stat().st_size,
        "_nexus_trusted_applicability": make_trusted_applicability(
            supported_domains=("presentation",),
            supported_task_kinds=("create_artifact", "edit_artifact", "read_artifact"),
            required_context=("office_artifact",),
            artifact_families=("presentation",),
            provenance="unit_test_fixture",
        ),
    }


class McpRedactionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        self.skills = Path(self.temp.name) / "skills"
        self.skill = make_skill(self.skills, "ppt-safe", "Create editable PowerPoint presentation decks", "RAW_SKILL_SENTINEL\nSECRET_VALUE_SENTINEL")
        (self.root / "AGENTS.md").write_text("RAW_PROJECT_SENTINEL\nMUST NOT publish RAW_RULE_SENTINEL", encoding="utf-8")
        authorizer = WorkspaceAuthorizer.from_roots_for_test({"project": self.root})
        self.runtime = NexusMcpRuntime(authorizer, catalog_builder=lambda: {"skills": [self.skill], "agents": []}, skill_roots=[self.skills])

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_plan_returns_load_evidence_but_never_raw_content_or_paths(self) -> None:
        payload = self.runtime.plan({"task": "Create an editable PowerPoint presentation", "workspace_id": "project"})
        encoded = json.dumps(payload)
        for forbidden in ("RAW_SKILL_SENTINEL", "SECRET_VALUE_SENTINEL", "RAW_PROJECT_SENTINEL", "RAW_RULE_SENTINEL", str(self.root), str(self.skills), "instructions", "project_context", "candidates", "rejected"):
            self.assertNotIn(forbidden, encoded)
        self.assertEqual(payload["selected_skills"][0]["load_status"], "loaded")
        self.assertTrue(payload["selected_skills"][0]["content_sha256"])

    def test_load_failure_is_not_reported_as_a_success(self) -> None:
        self.skill["skill_md_path"] = str(self.skills / "missing" / "SKILL.md")
        with self.assertRaisesRegex(Exception, "selected Skill load evidence"):
            self.runtime.plan({"task": "Create an editable PowerPoint presentation", "workspace_id": "project"})

    def test_discover_is_metadata_only_and_bounded(self) -> None:
        payload = self.runtime.discover_capabilities({"capability_tags": ["presentation"]})
        self.assertEqual(payload["capability_count"], 1)
        self.assertEqual(payload["catalog_scope"], "nexus_local_skill_metadata")
        self.assertEqual(payload["host_inventory_authority"], "none")
        encoded = json.dumps(payload)
        self.assertNotIn("skill_md_path", encoded)
        self.assertNotIn(str(self.skills), encoded)

    def test_discover_truncates_500_safe_metadata_records_instead_of_failing(self) -> None:
        records = [dict(self.skill, id=f"skill:{number}", name=f"presentation-{number:03d}") for number in range(500)]
        runtime = NexusMcpRuntime(
            WorkspaceAuthorizer.from_roots_for_test({"project": self.root}),
            catalog_builder=lambda: {"skills": records, "agents": []}, skill_roots=[self.skills],
        )
        payload = runtime.discover_capabilities({"capability_tags": ["presentation"]})
        self.assertEqual(payload["available_capability_count"], 500)
        self.assertLessEqual(payload["capability_count"], 500)
        self.assertTrue(payload["truncated"])
