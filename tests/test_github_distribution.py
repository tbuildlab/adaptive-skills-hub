from __future__ import annotations

import hashlib
import json
import os
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
import scripts.build_release as release_build


ROOT = Path(__file__).resolve().parents[1]


def write_test_wheel(directory: Path) -> Path:
    wheel = directory / "example_dependency-1.0.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("example_dependency-1.0.0.dist-info/METADATA", "Metadata-Version: 2.1\nName: example-dependency\nVersion: 1.0.0\n")
    return wheel


def write_test_embed(directory: Path) -> tuple[Path, dict[str, str]]:
    """A structural fixture; real embedded-runtime acceptance is separate."""
    archive = directory / "test-python-embed.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("python.exe", "test executable")
        bundle.writestr("python313._pth", "python313.zip\n.\n")
        bundle.writestr("LICENSE.txt", "PSF test notice")
    return archive, {
        "schema_version": "nexus.windows.embedded-runtime.v1",
        "provider": "Python Software Foundation",
        "python_version": "3.13.15",
        "platform": "win-amd64",
        "filename": archive.name,
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "source_url": "https://example.invalid/python-embed.zip",
        "license": "PSF-2.0",
        "license_notice": "runtime/python/LICENSE.txt",
        "python_pth": "python313._pth",
    }


class GitHubDistributionTests(unittest.TestCase):
    def build_candidate(self, temporary: Path) -> tuple[Path, Path]:
        wheelhouse = temporary / "reviewed wheels"
        wheelhouse.mkdir()
        write_test_wheel(wheelhouse)
        embed, spec = write_test_embed(temporary)
        output = temporary / "release output"
        with patch.object(release_build, "runtime_spec", return_value=spec), patch.object(release_build, "embedded_runtime_self_check"):
            archive, _ = release_build.build(output, "0.1.0-rc.2", wheelhouse, embed)
        self.assertTrue(archive.is_file())
        self.assertTrue(archive.with_suffix(".zip.sha256").is_file())
        self.assertTrue((output / "Install-Nexus-0.1.0-rc.2.ps1").is_file())
        self.assertTrue((output / "Install-Nexus-0.1.0-rc.2.ps1.sha256").is_file())
        return archive, output

    def test_release_artifact_is_allowlisted_hashed_and_location_independent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive, output = self.build_candidate(Path(temporary))
            receipt = archive.with_suffix(".zip.sha256").read_text(encoding="ascii").split()[0]
            self.assertEqual(receipt, hashlib.sha256(archive.read_bytes()).hexdigest())
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
                self.assertTrue(all(name.startswith("Nexus-0.1.0-rc.2/") for name in names))
                text_names = [name for name in names if not name.endswith(".whl")]
                joined = "\n".join(bundle.read(name).decode("utf-8", errors="ignore") for name in text_names)
                self.assertIn("Nexus-0.1.0-rc.2/release-manifest.json", names)
                self.assertIn("Nexus-0.1.0-rc.2/requirements-release.lock", names)
                self.assertNotIn("Nexus-0.1.0-rc.2/wheelhouse/example_dependency-1.0.0-py3-none-any.whl", names)
                self.assertIn("Nexus-0.1.0-rc.2/runtime/python/python.exe", names)
                self.assertNotIn("D:" + chr(92) + "chatgpt", joined)
                self.assertNotIn("C:" + chr(92) + "Users" + chr(92) + "De Yong", joined)
                self.assertNotIn("state/installed-skills.json", names)
                self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))
                payload = json.loads(bundle.read("Nexus-0.1.0-rc.2/plugins/nexus-desktop/.codex-plugin/plugin.json"))
                self.assertEqual(payload["version"], "0.1.0-rc.2")
                mcp = json.loads(bundle.read("Nexus-0.1.0-rc.2/plugins/nexus-desktop/.mcp.json"))
                self.assertEqual(mcp["mcpServers"]["nexus_desktop_local"]["command"], "../../runtime/python/python.exe")
            extracted = safe_extract(archive, output / "clean machine path with spaces")
            manifest = verify_release_tree(extracted)
            self.assertEqual(manifest["version"], "0.1.0-rc.2")
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
                bundle.writestr("Nexus-0.1.0-rc.2/../escape.txt", "no")
            with self.assertRaises(ReleaseError):
                safe_extract(malicious, root / "target")
            symlink = root / "symlink.zip"
            with zipfile.ZipFile(symlink, "w") as bundle:
                entry = zipfile.ZipInfo("Nexus-0.1.0-rc.2/link")
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
            bootstrap = output / "Install-Nexus-0.1.0-rc.2.ps1"
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
                "--python-embed", str(Path(temporary) / "missing-python.zip"),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("wheelhouse", result.stdout)

    def test_clean_install_reinstall_rollback_and_uninstall_need_no_repository(self) -> None:
        runtime = Path(sys.executable).resolve()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive, output = self.build_candidate(root)
            release = safe_extract(archive, output / "clean machine install")
            project = root / "project with spaces"
            project.mkdir()
            data = root / "machine local state"
            args = type("Args", (), {"data_root": str(data), "workspace_root": str(project), "workspace_id": "nexus-default", "mode": "standalone", "migrate_standalone": False, "remove_runtime": False, "codex_command": "codex"})()
            with patch.object(release_install, "verify_release_tree", return_value={"version": "0.1.0-rc.2"}), patch.object(release_install, "bundled_runtime", return_value=runtime), patch.object(release_install, "configure"):
                self.assertEqual(release_install.install(args), 0)
                self.assertTrue((data / "github-release-state.json").is_file())
                self.assertEqual(release_install.uninstall(args, rollback=True), 0)
                self.assertEqual(release_install.install(args), 0)
                self.assertEqual(release_install.uninstall(args), 0)
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
            with patch.object(release_install, "verify_release_tree", return_value={"version": "0.1.0-rc.2"}), patch.object(release_install, "bundled_runtime", return_value=Path(sys.executable).resolve()), patch.object(release_install, "standalone_snapshot", return_value=snapshot), patch.object(release_install, "remove_standalone") as remove, patch.object(release_install, "configure") as configure:
                with self.assertRaises(ReleaseError):
                    release_install.install(args)
                remove.assert_not_called()
                configure.assert_not_called()
            args.migrate_standalone = True
            with patch.object(release_install, "verify_release_tree", return_value={"version": "0.1.0-rc.2"}), patch.object(release_install, "bundled_runtime", return_value=Path(sys.executable).resolve()), patch.object(release_install, "standalone_snapshot", return_value=snapshot), patch.object(release_install, "remove_standalone") as remove, patch.object(release_install, "enable_plugin"), patch.object(release_install, "configure"):
                self.assertEqual(release_install.install(args), 0)
                remove.assert_called_once_with("codex")
            args.migrate_standalone = True
            with patch.object(release_install, "verify_release_tree", return_value={"version": "0.1.0-rc.2"}), patch.object(release_install, "bundled_runtime", return_value=Path(sys.executable).resolve()), patch.object(release_install, "standalone_snapshot", return_value=snapshot), patch.object(release_install, "remove_standalone"), patch.object(release_install, "enable_plugin", side_effect=RuntimeError("host failed")), patch.object(release_install, "remove_plugin"), patch.object(release_install, "restore_standalone") as restore:
                with self.assertRaises(RuntimeError):
                    release_install.install(args)
                restore.assert_called_once_with("codex", snapshot)

    def test_pinned_embedded_runtime_rejects_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wheelhouse = root / "wheels"
            wheelhouse.mkdir()
            write_test_wheel(wheelhouse)
            embed, spec = write_test_embed(root)
            spec["sha256"] = "0" * 64
            with patch.object(release_build, "runtime_spec", return_value=spec):
                with self.assertRaises(ReleaseError):
                    release_build.build(root / "out", "0.1.0-rc.2", wheelhouse, embed)

    @unittest.skipUnless(os.environ.get("NEXUS_RELEASE_TEST_EMBED") and os.environ.get("NEXUS_RELEASE_TEST_WHEELHOUSE"), "real embedded runtime inputs are not configured")
    def test_real_clean_bootstrap_without_system_python(self) -> None:
        """Actual acceptance path: archive runtime succeeds while PATH has no Python."""
        embed = Path(os.environ["NEXUS_RELEASE_TEST_EMBED"])
        wheelhouse = Path(os.environ["NEXUS_RELEASE_TEST_WHEELHOUSE"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "release output"
            archive, _ = release_build.build(output, "0.1.0-rc.2", wheelhouse, embed)
            project = root / "workspace"
            project.mkdir()
            data = root / "Nexus local data"
            bootstrap = output / "Install-Nexus-0.1.0-rc.2.ps1"
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            self.assertIsNotNone(powershell)
            environment = dict(os.environ)
            # Keep Windows' normal process variables (for a standard-user host),
            # but make python.exe/py.exe unavailable. This is not a mock: the
            # only executable that can run the release is the bundled runtime.
            environment["PATH"] = os.pathsep.join((str(Path(powershell).parent), str(Path(os.environ["SystemRoot"]) / "System32")))
            environment["LOCALAPPDATA"] = str(root / "LocalAppData")
            environment["PSModulePath"] = str(Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "Modules")
            environment["SystemDrive"] = Path(os.environ["SystemRoot"]).anchor
            for key in tuple(environment):
                if key.upper().startswith("PYTHON"):
                    environment.pop(key)
            result = subprocess.run([
                powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(bootstrap),
                "-ArchivePath", str(archive), "-ChecksumPath", str(archive.with_suffix(".zip.sha256")),
                "-WorkspaceRoot", str(project), "-DataRoot", str(data), "-Mode", "standalone",
            ], capture_output=True, text=True, env=environment, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            release = next((data / "releases").iterdir())
            runtime = release / "runtime" / "python" / "python.exe"
            self.assertTrue(runtime.is_file())
            self.assertTrue((data / "nexus-desktop-plugin.json").is_file())
            self.assertEqual(subprocess.run([str(runtime), "-I", "-B", str(release / "scripts" / "release_install.py"), "--data-root", str(data), "verify"], capture_output=True, text=True).returncode, 0)
            # Exercise the real R2 local MCP server through the embedded client
            # and embedded server. PATH still contains no usable Python, so this
            # proves health/discover/plan do not silently fall back to a host
            # interpreter after installation.
            probe = f"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(
        command={str(runtime)!r},
        args=[{str(release / 'scripts' / 'nexus_mcp.py')!r}, '--workspace-config', {str(data / 'workspaces.json')!r}],
        cwd={str(release)!r},
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            health = await session.call_tool('nexus.health', {{}})
            discover = await session.call_tool('nexus.discover_capabilities', {{}})
            plan = await session.call_tool('nexus.plan_task', {{
                'workspace_id': 'nexus-default',
                'task': 'Plan a safe release check',
                'constraints': [],
            }})
            assert not health.is_error, health.content
            assert not discover.is_error, discover.content
            assert not plan.is_error, plan.content

asyncio.run(main())
"""
            mcp_result = subprocess.run(
                [str(runtime), "-I", "-B", "-c", probe],
                capture_output=True,
                text=True,
                timeout=45,
                env=environment,
            )
            self.assertEqual(mcp_result.returncode, 0, mcp_result.stderr + mcp_result.stdout)
