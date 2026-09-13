from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
import unittest
import zipfile

from scripts.build_manifest import (
    ECOSYSTEM_ROOT_MARKER,
    ManifestBoundaryError,
    build_manifest_bytes,
    write_manifest,
)
from scripts.package_nexus import (
    ECOSYSTEM_DATA_PARTS,
    PackageBoundaryError,
    build_package,
)


ROOT = Path(__file__).resolve().parents[1]
ECOSYSTEM_MODULES = tuple(sorted((ROOT / "ash").glob("ecosystem_*.py")))


class EcosystemIsolationTests(unittest.TestCase):
    def test_runtime_modules_have_no_acquisition_execution_or_authority_imports(self) -> None:
        forbidden_imports = {
            "httpx",
            "importlib",
            "requests",
            "runpy",
            "socket",
            "subprocess",
            "urllib.request",
        }
        forbidden_relative = {
            "activation",
            "agent_runtime",
            "approval",
            "capabilities",
            "checkpoint",
            "host",
            "mcp",
            "memory",
            "promotion",
            "routing",
            "runtime_decision",
            "scheduler",
            "selection",
        }
        forbidden_calls = {"compile", "eval", "exec"}
        observed: list[str] = []
        for path in ECOSYSTEM_MODULES:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(
                            alias.name == item or alias.name.startswith(item + ".")
                            for item in forbidden_imports
                        ):
                            observed.append(f"{path.name}:import:{alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if any(
                        module == item or module.startswith(item + ".")
                        for item in forbidden_imports
                    ):
                        observed.append(f"{path.name}:from:{module}")
                    if node.level and module.split(".", 1)[0] in forbidden_relative:
                        observed.append(f"{path.name}:relative:{module}")
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in forbidden_calls:
                        observed.append(f"{path.name}:call:{node.func.id}")
                    if (
                        isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name)
                        and (node.func.value.id, node.func.attr)
                        in {("os", "system"), ("os", "popen")}
                    ):
                        observed.append(
                            f"{path.name}:call:{node.func.value.id}.{node.func.attr}"
                        )
        self.assertEqual(observed, [])

    def test_legacy_update_checker_remains_check_only_and_unimported(self) -> None:
        legacy_path = ROOT / "scripts" / "check_updates.py"
        legacy_source = legacy_path.read_text(encoding="utf-8")
        self.assertIn("CHECK-ONLY upstream revision checker", legacy_source)
        self.assertIn("CHECK-ONLY: no repositories were pulled or modified.", legacy_source)
        for module_path in ECOSYSTEM_MODULES:
            tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module or "")
            with self.subTest(module=module_path.name):
                self.assertNotIn("scripts.check_updates", imports)

    def test_manifest_builder_is_deterministic_and_rejects_embedded_data_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            (root / "ash").mkdir(parents=True)
            (root / "ash" / "module.py").write_bytes(b"first\r\nsecond\r\n")
            first, first_entries = build_manifest_bytes(root=root)
            second, second_entries = build_manifest_bytes(root=root)
            self.assertEqual(first, second)
            self.assertEqual(first_entries, second_entries)
            self.assertEqual(
                list(first_entries),
                sorted(first_entries, key=lambda item: item.encode("utf-8")),
            )
            self.assertEqual(
                first_entries["ash/module.py"]["sha256"],
                hashlib.sha256(b"first\nsecond\n").hexdigest(),
            )
            data_root = root / "state"
            data_root.mkdir()
            (data_root / ECOSYSTEM_ROOT_MARKER).write_text("{}", encoding="utf-8")
            with self.assertRaises(ManifestBoundaryError):
                build_manifest_bytes(root=root)

    def test_manifest_and_package_reject_unmarked_repository_storage_directories(self) -> None:
        for directory in (
            "ecosystem",
            "quarantine",
            "incoming",
            "intake-attempts",
            "trees",
            "revisions",
            "components",
            "decisions",
            "evidence",
            "comparisons",
            "locks",
            "objects",
            "observations",
            "receipts",
            "staging",
            "state",
            "tmp",
        ):
            with self.subTest(directory=directory), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "source"
                (root / "ash").mkdir(parents=True)
                (root / "ash" / "module.py").write_text("value = 1\n", encoding="utf-8")
                storage = root / "ash" / directory
                storage.mkdir()
                (storage / "record.json").write_text("{}\n", encoding="utf-8")
                with self.assertRaises(ManifestBoundaryError):
                    build_manifest_bytes(root=root)
                with self.assertRaises(PackageBoundaryError):
                    build_package(Path(temporary) / "blocked.zip", root=root)

        for namespace in (
            "objects",
            "intake-attempts",
            "trees",
            "revisions",
            "components",
            "evidence",
            "comparisons",
            "decisions",
            "locks",
            "observations",
            "receipts",
            "staging",
            "state",
            "tmp",
        ):
            with self.subTest(digest_namespace=namespace), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "source"
                (root / "ash").mkdir(parents=True)
                (root / "ash" / "module.py").write_text("value = 1\n", encoding="utf-8")
                storage = root / "ash" / namespace / "sha256"
                storage.mkdir(parents=True)
                (storage / (("a" * 64) + ".json")).write_text("{}\n", encoding="utf-8")
                with self.assertRaises(ManifestBoundaryError):
                    build_manifest_bytes(root=root)
                with self.assertRaises(PackageBoundaryError):
                    build_package(Path(temporary) / "blocked.zip", root=root)

    def test_private_package_is_byte_reproducible_and_excludes_mutable_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first_path = base / "first.zip"
            second_path = base / "second.zip"
            first_digest, first_names = build_package(first_path, root=ROOT)
            second_digest, second_names = build_package(second_path, root=ROOT)
            self.assertEqual(first_names, second_names)
            self.assertEqual(first_digest, second_digest)
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
            self.assertEqual(first_digest, hashlib.sha256(first_path.read_bytes()).hexdigest())
            with zipfile.ZipFile(first_path) as archive:
                self.assertEqual(archive.namelist(), first_names)
                joined = b"\n".join(archive.read(name) for name in first_names)
                for info in archive.infolist():
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                    parts = {part.casefold() for part in PurePosixPath(info.filename).parts[:-1]}
                    self.assertTrue(parts.isdisjoint(ECOSYSTEM_DATA_PARTS))
            required = {
                "ash/ecosystem_bridge.py",
                "ash/ecosystem_compare.py",
                "ash/ecosystem_evidence.py",
                "ash/ecosystem_intake.py",
                "ash/ecosystem_models.py",
                "ash/ecosystem_policy.py",
                "ash/ecosystem_storage.py",
                "config/ecosystem-source-policy.json",
                "docs/nexus-post-r5-runtime-integration-slice3c-adr-pds.md",
                "tests/test_ecosystem_isolation_package.py",
            }
            self.assertTrue(required <= set(first_names))
            self.assertFalse(any(PurePosixPath(name).name == ECOSYSTEM_ROOT_MARKER for name in first_names))
            developer_root = ("D:" + chr(92) + "chatgpt").encode("utf-8")
            developer_profile = (
                "C:" + chr(92) + "Users" + chr(92) + "De Yong"
            ).encode("utf-8")
            self.assertFalse(developer_root in joined, "private developer root entered package bytes")
            self.assertFalse(developer_profile in joined, "private user profile entered package bytes")

    def test_package_bytes_are_independent_of_source_mtimes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "source"
            (root / "ash").mkdir(parents=True)
            (root / "SKILL.md").write_text("synthetic\n", encoding="utf-8")
            (root / "ash" / "module.py").write_bytes(b"value = 1\r\n")
            write_manifest(root=root)
            first_path = base / "first.zip"
            second_path = base / "second.zip"
            first_digest, first_names = build_package(first_path, root=root)
            for path in (root / "SKILL.md", root / "ash" / "module.py"):
                current = path.stat().st_mtime_ns
                os.utime(path, ns=(current + 5_000_000_000, current + 5_000_000_000))
            second_digest, second_names = build_package(second_path, root=root)
            self.assertEqual(first_names, second_names)
            self.assertEqual(first_digest, second_digest)
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
            with zipfile.ZipFile(first_path) as archive:
                self.assertEqual(archive.read("ash/module.py"), b"value = 1\n")

    def test_manifest_and_package_exclusions_are_case_insensitive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "source"
            (root / "ash").mkdir(parents=True)
            (root / "ash" / "module.py").write_text("value = 1\n", encoding="utf-8")
            excluded = {
                "ash/.GIT/config": b"git metadata\n",
                "ash/__PYCACHE__/module.pyc": b"generated cache\n",
                "ash/.ENV": b"SECRET=synthetic\n",
                "ash/.Env.Local": b"SECRET=synthetic\n",
                "ash/secret.PEM": b"synthetic key material\n",
            }
            for relative, contents in excluded.items():
                location = root / Path(relative)
                location.parent.mkdir(parents=True, exist_ok=True)
                location.write_bytes(contents)

            _manifest_bytes, manifest = build_manifest_bytes(root=root)
            self.assertNotIn("ash/.GIT/config", manifest)
            self.assertNotIn("ash/__PYCACHE__/module.pyc", manifest)
            self.assertNotIn("ash/.ENV", manifest)
            self.assertNotIn("ash/.Env.Local", manifest)
            self.assertNotIn("ash/secret.PEM", manifest)
            write_manifest(root=root)
            _digest, names = build_package(base / "package.zip", root=root)
            self.assertEqual(names, ["ash/module.py"])
            self.assertTrue(set(excluded).isdisjoint(names))

    def test_package_rejects_unmanifested_or_manifest_drift_without_partial_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "source"
            (root / "ash").mkdir(parents=True)
            module = root / "ash" / "module.py"
            module.write_text("value = 1\n", encoding="utf-8")
            write_manifest(root=root)

            injected = root / "ash" / "pilot.bin"
            injected.write_bytes(b"unreviewed upstream payload")
            output = base / "unmanifested.zip"
            with self.assertRaisesRegex(PackageBoundaryError, "MANIFEST set"):
                build_package(output, root=root)
            self.assertFalse(output.exists())

            injected.unlink()
            module.write_text("value = 2\n", encoding="utf-8")
            output = base / "drifted.zip"
            with self.assertRaisesRegex(PackageBoundaryError, "differs"):
                build_package(output, root=root)
            self.assertFalse(output.exists())

            module.write_text("value = 1\n", encoding="utf-8")
            output = base / "reviewed.zip"
            _digest, names = build_package(output, root=root)
            self.assertEqual(names, ["ash/module.py"])
            self.assertTrue(output.is_file())

    def test_package_manifest_schema_and_paths_are_strictly_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "source"
            (root / "ash").mkdir(parents=True)
            (root / "ash" / "module.py").write_text("value = 1\n", encoding="utf-8")
            write_manifest(root=root)
            manifest_path = root / "MANIFEST.json"
            valid = json.loads(manifest_path.read_text(encoding="utf-8"))

            def rejected(candidate: object, index: int) -> None:
                manifest_path.write_text(json.dumps(candidate), encoding="utf-8")
                output = base / f"invalid-{index}.zip"
                with self.assertRaises(PackageBoundaryError):
                    build_package(output, root=root)
                self.assertFalse(output.exists())

            mutations = (
                lambda value: value["ash/module.py"].update(unexpected=True),
                lambda value: value["ash/module.py"].update(bytes=True),
                lambda value: value["ash/module.py"].update(sha256="A" * 64),
                lambda value: value.update(
                    {"ASH/module.py": {"bytes": 1, "sha256": "a" * 64}}
                ),
                lambda value: value.update(
                    {"ash\\escape.py": {"bytes": 1, "sha256": "a" * 64}}
                ),
                lambda value: value.update(
                    {"ash/evil\u202etxt.py": {"bytes": 1, "sha256": "a" * 64}}
                ),
                lambda value: value.update(
                    {"ash/CON.txt": {"bytes": 1, "sha256": "a" * 64}}
                ),
                lambda value: value.update(
                    {"ash/.GIT/config": {"bytes": 1, "sha256": "a" * 64}}
                ),
                lambda value: value.update(
                    {"ash/__PYCACHE__/module.pyc": {"bytes": 1, "sha256": "a" * 64}}
                ),
                lambda value: value.update(
                    {"ash/.Env.Production": {"bytes": 1, "sha256": "a" * 64}}
                ),
                lambda value: value.update(
                    {"ash/secret.PEM": {"bytes": 1, "sha256": "a" * 64}}
                ),
            )
            for index, mutate in enumerate(mutations):
                candidate = json.loads(json.dumps(valid))
                mutate(candidate)
                rejected(candidate, index)

            metadata = valid["ash/module.py"]
            manifest_path.write_text(
                '{"ash/module.py":'
                + json.dumps(metadata)
                + ',"ash/module.py":'
                + json.dumps(metadata)
                + "}",
                encoding="utf-8",
            )
            output = base / "duplicate-key.zip"
            with self.assertRaisesRegex(PackageBoundaryError, "duplicate JSON key"):
                build_package(output, root=root)
            self.assertFalse(output.exists())

    def test_manifest_builder_rejects_nonportable_paths(self) -> None:
        for relative in ("ash/evil\u202etxt.py", "ash/CON.txt"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "source"
                location = root / Path(relative)
                location.parent.mkdir(parents=True)
                location.write_text("synthetic\n", encoding="utf-8")
                with self.assertRaises(ManifestBoundaryError):
                    build_manifest_bytes(root=root)

    def test_package_builder_rejects_marker_even_beneath_excluded_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            (root / "ash").mkdir(parents=True)
            (root / "ash" / "module.py").write_text("value = 1\n", encoding="utf-8")
            embedded = root / "state"
            embedded.mkdir()
            (embedded / ECOSYSTEM_ROOT_MARKER).write_text(
                json.dumps({"schema_version": "nexus.ecosystem-root-marker.v1"}),
                encoding="utf-8",
            )
            with self.assertRaises(PackageBoundaryError):
                build_package(Path(temporary) / "blocked.zip", root=root)


if __name__ == "__main__":
    unittest.main()
