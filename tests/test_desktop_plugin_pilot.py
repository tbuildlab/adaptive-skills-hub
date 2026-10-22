from __future__ import annotations

from contextlib import redirect_stderr
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4
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
        self.assertEqual(manifest["version"], "0.4.0")
        self.assertEqual(manifest["interface"]["displayName"], "Nexus")
        self.assertIn("bounded reference research", manifest["description"])
        self.assertIn("server-issued short-lived Host inventory tickets", manifest["description"])
        self.assertIn("ChatGPT Host retains those authorities", manifest["interface"]["longDescription"])
        self.assertEqual(manifest["interface"]["composerIcon"], "./assets/nexus-avatar-500.png")
        self.assertEqual(manifest["interface"]["logo"], "./assets/nexus-avatar-500.png")
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")
        self.assertEqual(mapping["mcpServers"]["nexus_desktop_local"]["cwd"], ".")
        self.assertEqual(mapping["mcpServers"]["nexus_desktop_local"]["args"], ["./scripts/launch_nexus_mcp.py"])
        self.assertEqual(marketplace["plugins"][0]["source"]["path"], "./plugins/nexus-desktop")
        self.assertTrue((ROOT / marketplace["plugins"][0]["source"]["path"]).is_dir())
        self.assertEqual(marketplace["plugins"][0]["policy"]["installation"], "AVAILABLE")
        self.assertIn("nexus.plan_task", skill)
        self.assertIn("nexus.route_capabilities", skill)
        self.assertIn("nexus.scout_candidates", skill)
        self.assertIn("ADMITTED_FOR_REVIEW", skill)
        self.assertIn("not_installed", skill)
        self.assertIn("selection_is_execution_evidence: false", skill)
        self.assertIn("execution: not_executed", skill)
        self.assertIn("nexus.begin_host_capability_assessment", skill)
        self.assertIn("nexus.assess_host_capabilities", skill)
        self.assertIn("nexus.prepare_host_handoff", skill)
        self.assertIn("nexus.prepare_enhancement_handoff", skill)
        self.assertIn("r4_host_capability:presentations", skill)
        self.assertIn("HOST_CAPABILITY_UNAVAILABLE", skill)
        self.assertIn("current_turn_host_visible_subset", skill)
        self.assertIn("not_globally_enumerated", skill)
        self.assertIn("Installed, enabled, selected, and loaded are", skill)
        self.assertIn("mcp_execution_authority: none", skill)
        self.assertIn("nexus.host-capability-snapshot.v3", skill)
        self.assertIn("nexus.host-capability-assessment.v3", skill)
        self.assertIn("nexus.host-capability-receipt.v3", skill)
        self.assertIn("host_skill_workflow", skill)
        self.assertIn("current_turn_execution_substrate", skill)
        self.assertIn("generate or send a timestamp", skill)
        self.assertIn("Do not compare its", skill)
        self.assertIn("runtime-local monotonic clock", skill)
        self.assertIn("Host-local execution-start claim", skill)
        self.assertIn("canonical SHA-256", skill)
        self.assertIn("selected Skill identity/content hash/load state", skill)
        self.assertIn("Freshness is a", skill)
        self.assertIn("pre-execution gate", skill)
        self.assertIn("adaptive_path.status: failed", skill)
        self.assertIn("fallback.kind: native_host_fallback", skill)
        self.assertIn("When no valid assessment", skill)
        self.assertIn("preserve its considered/rejected evidence exactly", skill)
        self.assertIn("stop the Nexus adaptive", skill)
        self.assertIn("Never call", skill)
        self.assertIn("R5 adaptive success", skill)
        self.assertIn("loaded_verified", skill)
        self.assertIn("continue_with_safe_defaults", skill)
        self.assertIn("Do **not** ask the normal presentation", skill)
        self.assertIn("Do not stop after planning or loaded verification", skill)
        self.assertIn("R5 bounded post-execution enhancement", skill)
        self.assertIn("host_copy_on_write", skill)
        self.assertIn("HOST_ENHANCEMENT_HANDOFF_READY", skill)
        self.assertIn("Do not claim an enhancement, an artifact, or validation", skill)
        self.assertIn("nexus-default", skill)
        self.assertIn("substantive", skill)
        self.assertIn("Default Reference Research", skill)
        self.assertIn("NO_SUITABLE_REFERENCE_FOUND", skill)
        self.assertIn("PLAN → BUILD → TEST → VERIFY", skill)
        self.assertIn("unknown or unclear license", skill)
        self.assertIn("REAL_ADMISSION", skill)
        self.assertIn("G5 is disabled", skill)
        self.assertNotIn("nexus executes", skill.casefold())
        source = "\n".join(path.read_text(encoding="utf-8") for path in PLUGIN_ROOT.rglob("*.py"))
        developer_root = "D:" + chr(92) + "chatgpt"
        developer_profile = "C:" + chr(92) + "Users" + chr(92) + "De Yong"
        for forbidden in (developer_root, developer_profile, "shell=True", "http://", "https://"):
            self.assertNotIn(forbidden, source)
        self.assertIn("subprocess.run", source)
        self.assertIn("shell=False", source)

    def test_final_avatar_is_the_packaged_canonical_profile_asset(self) -> None:
        source = ROOT / "assets" / "brand" / "nexus" / "nexus-avatar-500.png"
        packaged = PLUGIN_ROOT / "assets" / "nexus-avatar-500.png"
        self.assertTrue(source.is_file())
        self.assertTrue(packaged.is_file())
        self.assertEqual(hashlib.sha256(source.read_bytes()).digest(), hashlib.sha256(packaged.read_bytes()).digest())
        header = packaged.read_bytes()[:24]
        self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(int.from_bytes(header[16:20], "big"), 500)
        self.assertEqual(int.from_bytes(header[20:24], "big"), 500)

    def test_reference_research_instructions_cover_final_normal_use_policy(self) -> None:
        from ash.reference_research import reference_research_plan

        skill = (PLUGIN_ROOT / "skills" / "nexus" / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(reference_research_plan("Build a new website").status, "required")
        self.assertEqual(reference_research_plan("Build a new website from this complete specification").status, "reduced")
        self.assertEqual(reference_research_plan("Fix a tiny button label typo").status, "skipped")
        self.assertEqual(reference_research_plan("Build a new website; do not search").trigger, "user_opt_out")
        self.assertIn("NO_SUITABLE_REFERENCE_FOUND", skill)
        self.assertIn("synthesize before", skill.casefold())
        self.assertIn("HOLD", skill)

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

    def test_launcher_failure_does_not_expose_configured_private_paths(self) -> None:
        launcher = PLUGIN_ROOT / "scripts" / "launch_nexus_mcp.py"
        with tempfile.TemporaryDirectory() as temporary:
            data_root = Path(temporary) / "Local App Data" / "Nexus"
            data_root.mkdir(parents=True)
            private_marker = Path(temporary) / "Private User Workspace" / "missing"
            payload = {
                "schema_version": "nexus.desktop.local.v1",
                "nexus_root": str(private_marker / "root"),
                "python_executable": str(private_marker / "python.exe"),
                "workspace_config": str(private_marker / "workspaces.json"),
            }
            (data_root / "nexus-desktop-plugin.json").write_text(
                json.dumps(payload), encoding="utf-8",
            )
            environment = os.environ.copy()
            environment["NEXUS_DATA_ROOT"] = str(data_root)
            result = subprocess.run(
                [sys.executable, str(launcher)],
                cwd=str(PLUGIN_ROOT),
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(
                result.stderr.strip(),
                "Nexus Desktop plugin could not start: local launch configuration is invalid or unavailable",
            )
            self.assertNotIn(str(private_marker), result.stderr)
            self.assertNotIn(str(Path(temporary)), result.stderr)

    def test_launcher_exceptions_are_redacted_without_changing_process_contract(self) -> None:
        launcher_path = PLUGIN_ROOT / "scripts" / "launch_nexus_mcp.py"
        spec = importlib.util.spec_from_file_location("nexus_launcher_security_test", launcher_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        secret = "C:\\Users\\SecretOwner\\Private Workspace\\missing.exe"

        config_stderr = io.StringIO()
        with patch.object(
            launcher,
            "load_launch_configuration",
            side_effect=FileNotFoundError(secret),
        ), redirect_stderr(config_stderr):
            self.assertEqual(launcher.main(), 2)
        self.assertEqual(
            config_stderr.getvalue().strip(),
            "Nexus Desktop plugin could not start: local launch configuration is invalid or unavailable",
        )

        runtime_python = Path("C:/Nexus/runtime/python.exe")
        runtime_root = Path("C:/Nexus/release")
        workspace = Path("C:/Nexus/config/workspaces.json")
        launch_stderr = io.StringIO()
        with patch.object(
            launcher,
            "load_launch_configuration",
            return_value=(runtime_python, runtime_root, workspace),
        ), patch.object(
            launcher.subprocess,
            "run",
            side_effect=PermissionError(secret),
        ) as run, redirect_stderr(launch_stderr):
            self.assertEqual(launcher.main(), 2)
        self.assertEqual(
            launch_stderr.getvalue().strip(),
            "Nexus Desktop plugin could not start: runtime process launch failed",
        )
        run.assert_called_once_with(
            [
                str(runtime_python), str(runtime_root / "scripts" / "nexus_mcp.py"),
                "--workspace-config", str(workspace),
            ],
            cwd=str(runtime_root),
            check=False,
            shell=False,
        )
        for output in (config_stderr.getvalue(), launch_stderr.getvalue()):
            self.assertNotIn(secret, output)
            self.assertNotIn("SecretOwner", output)
            self.assertNotIn("Traceback", output)
            self.assertNotIn("FileNotFoundError", output)
            self.assertNotIn("PermissionError", output)

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
                    ticket_result = await session.call_tool("nexus.begin_host_capability_assessment", {
                        "schema_version": "nexus.host-capability-ticket-request.v1",
                        "host_surface": "chatgpt_desktop",
                        "inventory_scope": "current_turn_host_visible_subset",
                        "inventory_completeness": "not_globally_enumerated",
                        "task_category": "presentation",
                        "required_interfaces": ["editable_pptx_create", "pptx_open_render_validate"],
                    })
                    ticket = json.loads(ticket_result.content[0].text)
                    inventory = {
                        "schema_version": "nexus.host-capability-snapshot.v3",
                        "ticket_id": ticket["ticket_id"],
                        "snapshot_id": str(uuid4()),
                        "capabilities": [{
                            "capability_id": "presentations",
                            "provider_id": "openai-primary-runtime",
                            "display_name": "Presentations",
                            "resource_kind": "skill",
                            "availability": "skill_workflow_ready_current_turn",
                            "evidence": ["current_turn_skill_metadata", "current_turn_skill_instructions", "current_turn_tool_catalog", "current_turn_execution_substrate"],
                            "interfaces": ["editable_pptx_create", "pptx_open_render_validate"],
                            "logical_capability": "chatgpt.presentations",
                            "execution_binding_kind": "host_skill_workflow",
                        }],
                    }
                    assessment = await session.call_tool("nexus.assess_host_capabilities", inventory)
                    replay = await session.call_tool("nexus.assess_host_capabilities", inventory)
                    self.assertFalse(health.is_error)
                    self.assertFalse(discover.is_error)
                    self.assertFalse(planned.is_error)
                    self.assertFalse(ticket_result.is_error)
                    self.assertFalse(assessment.is_error)
                    self.assertTrue(replay.is_error)
                    self.assertEqual(json.loads(replay.content[0].text)["error"]["code"], "HOST_INVENTORY_TICKET_REPLAYED")
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
            self.assertIn("plugins/nexus-desktop/assets/nexus-avatar-500.png", names)
            self.assertNotIn("state/installed-skills.json", names)
            developer_root = "D:" + chr(92) + "chatgpt"
            developer_profile = "C:" + chr(92) + "Users" + chr(92) + "De Yong"
            developer_runtime = "D:" + chr(92) + "DevTools"
            self.assertNotIn(developer_root, joined)
            self.assertNotIn(developer_profile, joined)
            self.assertNotIn(developer_runtime, joined)
