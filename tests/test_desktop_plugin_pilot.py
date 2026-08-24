from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "nexus-desktop"


class NexusDesktopPluginPilotTests(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def _runtime_python() -> Path:
        # CI or a clean machine can supply a normal R2 runtime through this
        # explicit hook. The repository itself contains no developer path.
        configured = __import__("os").environ.get("NEXUS_R2_TEST_PYTHON")
        return Path(configured) if configured else Path(sys.executable)

    def test_plugin_manifest_marketplace_and_skill_are_portable(self) -> None:
        manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        mapping = json.loads((PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
        skill = (PLUGIN_ROOT / "skills" / "nexus" / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(manifest["name"], "nexus-desktop")
        self.assertEqual(manifest["interface"]["displayName"], "Nexus")
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")
        self.assertEqual(mapping["mcpServers"]["nexus_desktop_local"]["cwd"], ".")
        self.assertEqual(mapping["mcpServers"]["nexus_desktop_local"]["args"], ["./scripts/launch_nexus_mcp.py"])
        self.assertEqual(marketplace["plugins"][0]["source"]["path"], "./.codex/plugins/nexus-desktop")
        self.assertEqual(marketplace["plugins"][0]["policy"]["installation"], "AVAILABLE")
        self.assertIn("nexus.plan_task", skill)
        self.assertIn("nexus.prepare_host_handoff", skill)
        self.assertIn("r4_host_capability:presentations", skill)
        self.assertIn("HOST_CAPABILITY_UNAVAILABLE", skill)
        self.assertIn("loaded_verified", skill)
        self.assertIn("nexus-default", skill)
        self.assertIn("substantive", skill)
        self.assertNotIn("nexus executes", skill.casefold())
        source = "\n".join(path.read_text(encoding="utf-8") for path in PLUGIN_ROOT.rglob("*.py"))
        developer_root = "D:" + chr(92) + "chatgpt"
        developer_profile = "C:" + chr(92) + "Users" + chr(92) + "De Yong"
        for forbidden in (developer_root, developer_profile, "shell=True", "http://", "https://"):
            self.assertNotIn(forbidden, source)
        self.assertIn("subprocess.run", source)
        self.assertIn("shell=False", source)

    def test_plugin_lifecycle_delegates_only_to_official_codex_commands(self) -> None:
        import scripts.setup_nexus as setup

        with patch.object(setup, "require_codex_cli", return_value="codex"), patch.object(setup.subprocess, "run") as run:
            run.return_value.returncode = 1
            run.return_value.stdout = ""
            setup.run_plugin_install("codex")
        self.assertEqual(run.call_args_list[0].args[0], ["codex", "mcp", "get", "nexus-r2-local"])
        self.assertEqual(run.call_args_list[1].args[0], ["codex", "plugin", "marketplace", "list"])
        self.assertEqual(run.call_args_list[2].args[0], ["codex", "plugin", "marketplace", "add", str(ROOT)])
        self.assertEqual(run.call_args_list[3].args[0], ["codex", "plugin", "add", "nexus-desktop@nexus-local-pilot"])
        with patch.object(setup, "require_codex_cli", return_value="codex"), patch.object(setup.subprocess, "run") as run:
            run.return_value.returncode = 1
            run.return_value.stdout = "nexus-local-pilot"
            setup.run_plugin_install("codex")
        self.assertEqual(len(run.call_args_list), 3)
        self.assertEqual(run.call_args_list[2].args[0], ["codex", "plugin", "add", "nexus-desktop@nexus-local-pilot"])
        with patch.object(setup, "require_codex_cli", return_value="codex"), patch.object(setup.subprocess, "run") as run:
            run.return_value.returncode = 0
            with self.assertRaises(setup.SetupError):
                setup.run_plugin_install("codex")
        self.assertEqual(run.call_args_list[0].args[0], ["codex", "mcp", "get", "nexus-r2-local"])
        with patch.object(setup, "require_codex_cli", return_value="codex"), patch.object(setup.subprocess, "run") as run:
            setup.run_plugin_uninstall("codex")
        self.assertEqual(run.call_args_list[0].args[0], ["codex", "plugin", "remove", "nexus-desktop@nexus-local-pilot"])
        self.assertEqual(run.call_args_list[1].args[0], ["codex", "plugin", "marketplace", "remove", "nexus-local-pilot"])

    def test_windows_default_prefers_a_spawnable_codex_executable(self) -> None:
        import scripts.setup_nexus as setup

        with patch.object(setup.shutil, "which", side_effect=["C:/npm/codex.cmd", "C:/Codex/codex.exe"]):
            self.assertEqual(setup.default_codex_command(), "C:/npm/codex.cmd")

    async def test_isolated_install_health_discover_plan_and_uninstall(self) -> None:
        runtime_python = self._runtime_python()
        try:
            probe = subprocess.run([str(runtime_python), "-c", "import mcp"], check=False, capture_output=True)
        except OSError as exc:
            self.skipTest(f"no R2 test runtime: {exc}")
        if probe.returncode:
            self.skipTest("NEXUS_R2_TEST_PYTHON must reference a Python with mcp installed")
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            release = temporary_root / "release with spaces"
            shutil.copytree(ROOT, release, ignore=shutil.ignore_patterns(".git", "state", "output", "__pycache__", ".venv", "venv"))
            project = temporary_root / "project with spaces"
            project.mkdir()
            data = temporary_root / "local data"
            setup = release / "scripts" / "setup_nexus.py"
            install = [
                sys.executable, str(setup), "--data-root", str(data), "install",
                "--workspace-id", "portable-project", "--workspace-root", str(project),
                "--runtime-python", str(runtime_python.resolve()),
            ]
            self.assertEqual(subprocess.run(install, capture_output=True, text=True).returncode, 0)
            self.assertEqual(subprocess.run([sys.executable, str(setup), "--data-root", str(data), "check"], capture_output=True, text=True).returncode, 0)
            config = json.loads((data / "nexus-desktop-plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(Path(config["nexus_root"]), release.resolve())
            self.assertNotIn(str(ROOT), config["nexus_root"])
            workspace_config = data / "workspaces.json"
            script = release / "scripts" / "nexus_mcp.py"
            params = StdioServerParameters(command=str(runtime_python), args=[str(script), "--workspace-config", str(workspace_config)], cwd=str(release))
            async with stdio_client(params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    health = await session.call_tool("nexus.health", {})
                    discover = await session.call_tool("nexus.discover_capabilities", {})
                    planned = await session.call_tool("nexus.plan_task", {"task": "Create an editable PowerPoint presentation.", "workspace_id": "portable-project", "project_context_mode": "none"})
                    self.assertFalse(health.is_error)
                    self.assertFalse(discover.is_error)
                    self.assertFalse(planned.is_error)
                    payload = json.loads(planned.content[0].text)
                    self.assertNotIn("path", json.dumps(payload).casefold())
            launcher = release / "plugins" / "nexus-desktop" / "scripts" / "launch_nexus_mcp.py"
            local_app_data = temporary_root / "local app data"
            shutil.copytree(data, local_app_data / "Nexus")
            launch_params = StdioServerParameters(
                command=str(runtime_python),
                args=[str(launcher)],
                cwd=str(launcher.parents[1]),
                env={"LOCALAPPDATA": str(local_app_data)},
            )
            async with stdio_client(launch_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    health = await session.call_tool("nexus.health", {})
                    self.assertFalse(health.is_error)
            uninstall = [sys.executable, str(setup), "--data-root", str(data), "uninstall"]
            self.assertEqual(subprocess.run(uninstall, capture_output=True, text=True).returncode, 0)
            self.assertFalse((data / "nexus-desktop-plugin.json").exists())
            self.assertFalse((data / "workspaces.json").exists())
            self.assertTrue(any((data / "backups").iterdir()))

    def test_private_archive_excludes_runtime_state_and_developer_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "nexus-desktop-pilot.zip"
            package = ROOT / "scripts" / "package_nexus.py"
            result = subprocess.run([sys.executable, str(package), "--output", str(archive)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(archive.with_suffix(".zip.sha256").is_file())
            with zipfile.ZipFile(archive) as contents:
                names = contents.namelist()
                joined = "\n".join(contents.read(name).decode("utf-8", errors="ignore") for name in names)
            self.assertIn("plugins/nexus-desktop/.codex-plugin/plugin.json", names)
            self.assertNotIn("state/installed-skills.json", names)
            developer_root = "D:" + chr(92) + "chatgpt"
            developer_profile = "C:" + chr(92) + "Users" + chr(92) + "De Yong"
            developer_runtime = "D:" + chr(92) + "DevTools"
            self.assertNotIn(developer_root, joined)
            self.assertNotIn(developer_profile, joined)
            self.assertNotIn(developer_runtime, joined)
