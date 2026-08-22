from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import mcp_types as types
from mcp.shared.message import SessionMessage
import ash.mcp.adapter as adapter


class McpProtocolTests(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def _payload(result):
        return json.loads(result.content[0].text)

    def test_catalog_builder_scans_workspace_only_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            skill = workspace / "backend" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(
                "---\nname: evidence-driven-backend-debugging\n"
                "description: Diagnose reproducible backend API failures.\n---\n",
                encoding="utf-8",
            )
            fake_home = Path(temporary) / "home"
            fake_root = workspace / "hub"
            with patch.object(adapter, "ROOT", fake_root), patch.object(adapter.Path, "home", return_value=fake_home):
                catalog = adapter.NexusMcpRuntime._build_catalog()
            records = [item for item in catalog["skills"] if item["name"] == "evidence-driven-backend-debugging"]
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["status"], "available")

    async def test_tools_are_gated_before_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            root.mkdir()
            config = Path(temporary) / "workspaces.json"
            config.write_text(json.dumps({"schema_version": "nexus.mcp.workspace.v1", "workspaces": {"project": {"root": str(root)}}}), encoding="utf-8")
            script = Path(__file__).resolve().parents[1] / "scripts" / "nexus_mcp.py"
            params = StdioServerParameters(command=sys.executable, args=[str(script), "--workspace-config", str(config)], cwd=str(script.parents[1]))
            async with stdio_client(params) as (read_stream, write_stream):
                await write_stream.send(SessionMessage(types.JSONRPCRequest(jsonrpc="2.0", id=1, method="tools/list", params={})))
                response = await asyncio.wait_for(read_stream.receive(), timeout=5)
                self.assertIsInstance(response.message, types.JSONRPCError)

    async def test_stdio_initialize_tools_and_safe_calls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            root.mkdir()
            config = Path(temporary) / "workspaces.json"
            config.write_text(json.dumps({"schema_version": "nexus.mcp.workspace.v1", "workspaces": {"project": {"root": str(root)}}}), encoding="utf-8")
            script = Path(__file__).resolve().parents[1] / "scripts" / "nexus_mcp.py"
            params = StdioServerParameters(command=sys.executable, args=[str(script), "--workspace-config", str(config)], cwd=str(script.parents[1]))
            async with stdio_client(params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    initialized = await session.initialize()
                    self.assertTrue(initialized.server_info.name.startswith("nexus"))
                    tools = await session.list_tools()
                    self.assertEqual([item.name for item in tools.tools], ["nexus.health", "nexus.discover_capabilities", "nexus.plan_task"])
                    metadata = {item.name: item for item in tools.tools}
                    self.assertEqual(metadata["nexus.health"].title, "Nexus status")
                    self.assertIn("diagnostics", metadata["nexus.health"].description)
                    self.assertIn("not for task planning", metadata["nexus.health"].description)
                    self.assertEqual(metadata["nexus.discover_capabilities"].title, "Nexus capability catalog")
                    self.assertIn("explicitly asks", metadata["nexus.discover_capabilities"].description)
                    self.assertIn("not use for ordinary task planning", metadata["nexus.discover_capabilities"].description)
                    self.assertEqual(metadata["nexus.plan_task"].title, "Nexus substantive-task planner")
                    self.assertIn("substantive multi-step task", metadata["nexus.plan_task"].description)
                    self.assertIn("presentations", metadata["nexus.plan_task"].description)
                    self.assertIn("Do not use for greetings", metadata["nexus.plan_task"].description)
                    self.assertIn("or execution", metadata["nexus.plan_task"].description)
                    for tool in tools.tools:
                        self.assertIsNotNone(tool.annotations)
                        self.assertTrue(tool.annotations.read_only_hint)
                        self.assertFalse(tool.annotations.destructive_hint)
                        self.assertTrue(tool.annotations.idempotent_hint)
                        self.assertFalse(tool.annotations.open_world_hint)
                    health = await session.call_tool("nexus.health", {})
                    self.assertFalse(health.is_error)
                    self.assertEqual(self._payload(health)["transport"], "stdio")
                    planned = await session.call_tool("nexus.plan_task", {"task": "Translate this text into Klingon", "workspace_id": "project", "project_context_mode": "none"})
                    self.assertFalse(planned.is_error)
                    self.assertEqual(self._payload(planned)["fallback"]["kind"], "native_codex_fallback")
                    invalid = await session.call_tool("nexus.plan_task", {"task": "x", "workspace_id": "unknown"})
                    self.assertTrue(invalid.is_error)
                    self.assertEqual(self._payload(invalid)["error"]["code"], "UNAUTHORIZED_WORKSPACE")
