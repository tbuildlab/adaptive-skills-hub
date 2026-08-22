from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from ash.mcp.authorization import WorkspaceAuthorizer, _assert_no_reparse_chain, guard_regular_file, verify_unchanged
from ash.mcp.schemas import NexusMcpError


class McpAuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "approved-project"
        self.root.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _config(self, workspaces: dict) -> Path:
        path = self.root.parent / "config.json"
        path.write_text(json.dumps({"schema_version": "nexus.mcp.workspace.v1", "workspaces": workspaces}), encoding="utf-8")
        return path

    def test_only_exact_configured_workspace_id_is_authorized(self) -> None:
        authorizer = WorkspaceAuthorizer.from_file(self._config({"approved": {"root": str(self.root)}}))
        self.assertEqual(authorizer.resolve("approved").root, self.root.resolve())
        for value in ("approved/../sibling", "approved\\..\\sibling", "unknown", ".."):
            with self.assertRaises(NexusMcpError) as raised:
                authorizer.resolve(value)
            self.assertEqual(raised.exception.code, "UNAUTHORIZED_WORKSPACE")

    def test_unc_and_device_workspace_roots_are_rejected(self) -> None:
        for root in (r"\\server\share\project", r"\\?\C:\project", r"\\.\PhysicalDrive0"):
            with self.assertRaises(NexusMcpError):
                WorkspaceAuthorizer.from_file(self._config({"approved": {"root": root}}))

    def test_guard_rejects_sibling_escape_and_non_regular_file(self) -> None:
        inside = self.root / "SKILL.md"
        inside.write_text("safe", encoding="utf-8")
        outside = self.root.parent / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        guarded, before = guard_regular_file(inside, [self.root])
        self.assertEqual(guarded, inside.resolve())
        verify_unchanged(guarded, before)
        with self.assertRaises(NexusMcpError):
            guard_regular_file(outside, [self.root])
        with self.assertRaises(NexusMcpError):
            guard_regular_file(self.root, [self.root])

    def test_race_like_replacement_fails_closed(self) -> None:
        target = self.root / "SKILL.md"
        target.write_text("one", encoding="utf-8")
        guarded, before = guard_regular_file(target, [self.root])
        target.write_text("two changed", encoding="utf-8")
        with self.assertRaises(NexusMcpError) as raised:
            verify_unchanged(guarded, before)
        self.assertEqual(raised.exception.code, "CONTEXT_REJECTED")

    def test_reparse_detection_is_fail_closed_when_reported(self) -> None:
        child = self.root / "child"
        child.mkdir()
        with patch("ash.mcp.authorization._is_reparse_point", side_effect=lambda value: value == child):
            with self.assertRaises(NexusMcpError):
                _assert_no_reparse_chain(child)

    @unittest.skipUnless(os.name == "nt", "Windows-specific junction/symlink behaviour")
    def test_symlink_if_privilege_is_available_is_rejected(self) -> None:
        target = self.root / "target"
        target.mkdir()
        link = self.root / "linked"
        try:
            os.symlink(target, link, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlink fixture unavailable: {exc}")
        with self.assertRaises(NexusMcpError):
            guard_regular_file(link / "SKILL.md", [self.root])

    @unittest.skipUnless(os.name == "nt", "Windows-specific junction behaviour")
    def test_real_junction_is_rejected_when_the_platform_can_create_one(self) -> None:
        target = self.root / "junction-target"
        target.mkdir()
        (target / "SKILL.md").write_text("safe", encoding="utf-8")
        junction = self.root / "junction-link"
        created = subprocess.run(["cmd.exe", "/d", "/s", "/c", "mklink", "/J", str(junction), str(target)], capture_output=True, text=True, check=False)
        if created.returncode != 0:
            self.skipTest("junction fixture unavailable")
        try:
            with self.assertRaises(NexusMcpError):
                guard_regular_file(junction / "SKILL.md", [self.root])
        finally:
            junction.rmdir()
