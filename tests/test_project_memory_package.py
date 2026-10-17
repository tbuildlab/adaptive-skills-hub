from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from ash import project_memory as model
from scripts.build_manifest import build_manifest_bytes, ManifestBoundaryError
from scripts.package_nexus import reviewed_members, PackageBoundaryError, _stable_source_bytes
from scripts.release_common import safe_member_name, ReleaseError, is_private_memory_payload
from scripts.build_release import source_payloads
from tests.test_project_memory import temporary

ROOT = Path(__file__).resolve().parents[1]


class MemoryPackageTests(unittest.TestCase):
    def test_private_names_namespaces_and_renamed_payloads_fail_closed(self):
        cases = [model.CONFIG_NAME, model.ROOT_MARKER, "project-memory/renamed.json", "config/renamed.json", "config/renamed.txt"]
        for relative in cases:
            with self.subTest(relative=relative), temporary() as directory:
                root = Path(directory)
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"schema_version":"nexus.project-memory.bundle.v1"}', encoding="utf-8")
                with self.assertRaises(ManifestBoundaryError):
                    build_manifest_bytes(root=root)
                with self.assertRaises(PackageBoundaryError):
                    reviewed_members(root=root)
        for name in ("config/project-memory-config.json", "project-memory/project.json", "config/.nexus-project-memory-root.json"):
            with self.assertRaises(ReleaseError):
                safe_member_name(name)
        self.assertTrue(is_private_memory_payload(b'{"schema_\\u0076ersion":"nexus.project-memory.config.v1"}'))

    def test_public_schema_matches_runtime_closed_schemas(self):
        path = ROOT / "config/project-memory.schema.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload, model.public_schema())
        self.assertFalse(is_private_memory_payload(path.read_bytes()))
        for schema in payload["$defs"].values():
            self.assertFalse(schema["additionalProperties"])

    def test_source_members_are_deterministic_and_memory_free_without_building(self):
        # In-memory review only: no archive, release build or install.
        first, entries = build_manifest_bytes(root=ROOT)
        second, _ = build_manifest_bytes(root=ROOT)
        self.assertEqual(first, second)
        members = reviewed_members(root=ROOT)
        self.assertIn(ROOT / "ash/project_memory.py", members)
        for path in members:
            if path.suffix == ".json":
                self.assertFalse(is_private_memory_payload(_stable_source_bytes(path)))
        payloads = source_payloads()
        names = {p.relative_to(ROOT).as_posix() for p, _ in payloads}
        self.assertIn("scripts/project_memory.py", names)
        self.assertIn("config/project-memory.schema.json", names)
        self.assertFalse(any("project-memory/" in name or model.CONFIG_NAME in name for name in names))


if __name__ == "__main__":
    unittest.main()
