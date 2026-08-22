from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts.release_common import ReleaseError, safe_extract, verify_release_tree
import scripts.release_install as release_install


ROOT = Path(__file__).resolve().parents[1]


def write_test_wheel(directory: Path) -> Path:
    wheel = directory / "example_dependency-1.0.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("example_dependency-1.0.0.dist-info/METADATA", "Metadata-Version: 2.1\nName: example-dependency\nVersion: 1.0.0\n")
    return wheel


class GitHubDistributionTests(unittest.TestCase):
    def build_candidate(self, temporary: Path) -> tuple[Path, Path]:
        wheelhouse = temporary / "reviewed wheels"
        wheelhouse.mkdir()
        write_test_wheel(wheelhouse)
        output = temporary / "release output"
        result = subprocess.run([
            sys.executable, str(ROOT / "scripts" / "build_release.py"),
            "--output-dir", str(output), "--wheelhouse", str(wheelhouse),
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = output / "Nexus-0.1.0-rc.1-windows.zip"
        self.assertTrue(archive.is_file())
        self.assertTrue(archive.with_suffix(".zip.sha256").is_file())
        self.assertTrue((output / "Install-Nexus-0.1.0-rc.1.ps1").is_file())
        self.assertTrue((output / "Install-Nexus-0.1.0-rc.1.ps1.sha256").is_file())
        return archive, output

    def test_release_artifact_is_allowlisted_hashed_and_location_independent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive, output = self.build_candidate(Path(temporary))
            receipt = archive.with_suffix(".zip.sha256").read_text(encoding="ascii").split()[0]
            self.assertEqual(receipt, hashlib.sha256(archive.read_bytes()).hexdigest())
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
                self.assertTrue(all(name.startswith("Nexus-0.1.0-rc.1/") for name in names))
                text_names = [name for name in names if not name.endswith(".whl")]
                joined = "\n".join(bundle.read(name).decode("utf-8", errors="ignore") for name in text_names)
                self.assertIn("Nexus-0.1.0-rc.1/release-manifest.json", names)
                self.assertIn("Nexus-0.1.0-rc.1/wheelhouse/example_dependency-1.0.0-py3-none-any.whl", names)
                self.assertNotIn("D:" + chr(92) + "chatgpt", joined)
                self.assertNotIn("C:" + chr(92) + "Users" + chr(92) + "De Yong", joined)
                self.assertNotIn("state/installed-skills.json", names)
                self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))
                payload = json.loads(bundle.read("Nexus-0.1.0-rc.1/plugins/nexus-desktop/.codex-plugin/plugin.json"))
                self.assertEqual(payload["version"], "0.1.0-rc.1")
            extracted = safe_extract(archive, output / "clean machine path with spaces")
            manifest = verify_release_tree(extracted)
            self.assertEqual(manifest["version"], "0.1.0-rc.1")
            check = subprocess.run([sys.executable, str(extracted / "scripts" / "release_install.py"), "verify"], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)

    def test_corrupted_artifact_and_traversal_are_rejected_before_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive, output = self.build_candidate(root)
            extracted = safe_extract(archive, output / "extract")
            target = extracted / "scripts" / "nexus_mcp.py"
            target.write_text(target.read_text(encoding="utf-8") + "# tampered\n", encoding="utf-8")
            with self.assertRaises(ReleaseError):
                verify_release_tree(extracted)
            malicious = root / "malicious.zip"
            with zipfile.ZipFile(malicious, "w") as bundle:
                bundle.writestr("Nexus-0.1.0-rc.1/../escape.txt", "no")
            with self.assertRaises(ReleaseError):
                safe_extract(malicious, root / "target")
            symlink = root / "symlink.zip"
            with zipfile.ZipFile(symlink, "w") as bundle:
                entry = zipfile.ZipInfo("Nexus-0.1.0-rc.1/link")
                entry.external_attr = 0o120777 << 16
                bundle.writestr(entry, "target")
            with self.assertRaises(ReleaseError):
                safe_extract(symlink, root / "target-symlink")

    def test_windows_bootstrap_rejects_wrong_checksum_before_extraction(self) -> None:
        if not shutil.which("powershell") and not shutil.which("pwsh"):
            self.skipTest("PowerShell is unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive, output = self.build_candidate(root)
            bad_receipt = output / "wrong.sha256"
            bad_receipt.write_text("0" * 64 + f"  {archive.name}\n", encoding="ascii")
            destination = root / "machine local data"
            bootstrap = output / "Install-Nexus-0.1.0-rc.1.ps1"
            command = shutil.which("powershell") or shutil.which("pwsh")
            result = subprocess.run([
                command, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(bootstrap),
                "-ArchivePath", str(archive), "-ChecksumPath", str(bad_receipt),
                "-WorkspaceRoot", str(root), "-DataRoot", str(destination),
            ], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((destination / "releases").exists())

    def test_release_builder_requires_a_reviewed_wheelhouse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts" / "build_release.py"),
                "--output-dir", str(Path(temporary) / "out"), "--wheelhouse", str(Path(temporary) / "missing"),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("wheelhouse", result.stdout)

    def test_clean_install_reinstall_rollback_and_uninstall_need_no_repository(self) -> None:
        runtime = Path(sys.executable).resolve()
        probe = subprocess.run([str(runtime), "-c", "import mcp"], capture_output=True)
        if probe.returncode:
            self.skipTest("test runtime lacks the existing R2 MCP dependency")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive, output = self.build_candidate(root)
            release = safe_extract(archive, output / "clean machine install")
            project = root / "project with spaces"
            project.mkdir()
            data = root / "machine local state"
            installer = release / "scripts" / "release_install.py"
            base = [sys.executable, str(installer), "--data-root", str(data)]
            command = base + ["install", "--workspace-root", str(project), "--runtime-python", str(runtime), "--mode", "standalone"]
            self.assertEqual(subprocess.run(command, capture_output=True, text=True).returncode, 0)
            self.assertTrue((data / "github-release-state.json").is_file())
            self.assertEqual(subprocess.run(base + ["upgrade", "--workspace-root", str(project), "--runtime-python", str(runtime), "--mode", "standalone"], capture_output=True, text=True).returncode, 0)
            self.assertEqual(subprocess.run(base + ["rollback"], capture_output=True, text=True).returncode, 0)
            self.assertEqual(subprocess.run(base + ["uninstall"], capture_output=True, text=True).returncode, 0)
            self.assertFalse((data / "nexus-desktop-plugin.json").exists())

    def test_plugin_mode_rejects_duplicate_or_restores_migrated_standalone(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data = Path(temporary) / "local"
            project = Path(temporary) / "project"
            project.mkdir()
            args = type("Args", (), {
                "data_root": str(data), "workspace_root": str(project), "workspace_id": "nexus-default",
                "runtime_python": str(Path(sys.executable).resolve()), "mode": "plugin",
                "migrate_standalone": False, "codex_command": "codex",
            })()
            snapshot = {"name": "nexus-r2-local", "transport": {"type": "stdio", "command": str(Path(sys.executable).resolve()), "args": ["server.py"], "cwd": None, "env": None}}
            with patch.object(release_install, "verify_release_tree", return_value={"version": "0.1.0-rc.1"}), patch.object(release_install, "standalone_snapshot", return_value=snapshot), patch.object(release_install, "remove_standalone") as remove, patch.object(release_install, "configure") as configure:
                with self.assertRaises(ReleaseError):
                    release_install.install(args)
                remove.assert_not_called()
                configure.assert_not_called()
            args.migrate_standalone = True
            with patch.object(release_install, "verify_release_tree", return_value={"version": "0.1.0-rc.1"}), patch.object(release_install, "standalone_snapshot", return_value=snapshot), patch.object(release_install, "remove_standalone") as remove, patch.object(release_install, "enable_plugin"), patch.object(release_install, "configure"):
                self.assertEqual(release_install.install(args), 0)
                remove.assert_called_once_with("codex")
            args.migrate_standalone = True
            with patch.object(release_install, "verify_release_tree", return_value={"version": "0.1.0-rc.1"}), patch.object(release_install, "standalone_snapshot", return_value=snapshot), patch.object(release_install, "remove_standalone"), patch.object(release_install, "enable_plugin", side_effect=RuntimeError("host failed")), patch.object(release_install, "remove_plugin"), patch.object(release_install, "restore_standalone") as restore:
                with self.assertRaises(RuntimeError):
                    release_install.install(args)
                restore.assert_called_once_with("codex", snapshot)
