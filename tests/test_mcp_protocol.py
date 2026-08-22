from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
import tempfile
import unittest

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import mcp_types as types
from mcp.shared.message import SessionMessage


class McpProtocolTests(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def _payload(result):
        return json.loads(result.content[0].text)

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
