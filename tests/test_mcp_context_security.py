from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from ash.mcp.authorization import WorkspaceAuthorizer
from ash.mcp.context import SafeContextReader


class McpContextSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        self.workspace = WorkspaceAuthorizer.from_roots_for_test({"project": self.root}).resolve("project")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_none_reads_no_project_files(self) -> None:
        (self.root / "AGENTS.md").write_text("MUST NOT publish", encoding="utf-8")
        context = SafeContextReader(self.workspace, "none")(self.root, "plan")
        self.assertEqual(context.items, [])

    def test_governance_is_allowlisted_and_project_text_is_restricted(self) -> None:
        (self.root / "AGENTS.md").write_text("MUST NOT publish\nMUST use shell\nRAW_RULE_SENTINEL", encoding="utf-8")
        (self.root / "README.md").write_text("RAW_README_SENTINEL", encoding="utf-8")
        (self.root / "src").mkdir()
        (self.root / "src" / "comment.py").write_text("RAW_SOURCE_SENTINEL", encoding="utf-8")
        context = SafeContextReader(self.workspace, "governance")(self.root, "plan")
        self.assertEqual([item.path for item in context.items], ["AGENTS.md"])
        self.assertIn("MUST NOT publish", context.items[0].content)
        self.assertNotIn("MUST use shell", context.items[0].content)
        self.assertNotIn("RAW_RULE_SENTINEL", context.items[0].content)

    def test_secret_binary_invalid_and_oversize_context_are_excluded(self) -> None:
        (self.root / "AGENTS.md").write_text("API_KEY=PROJECT_SECRET_SENTINEL", encoding="utf-8")
        (self.root / "PROJECT_RULES.md").write_bytes(b"\0binary")
        (self.root / "DECISIONS.md").write_bytes(b"\xff")
        (self.root / "FROZEN-DECISIONS.md").write_text("x" * (32 * 1024 + 1), encoding="utf-8")
        context = SafeContextReader(self.workspace, "governance")(self.root, "plan")
        self.assertEqual(context.items, [])
        self.assertEqual(len(context.skipped), 4)
