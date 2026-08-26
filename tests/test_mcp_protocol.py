from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import mcp_types as types
from mcp.shared.message import SessionMessage
import ash.mcp.adapter as adapter
from ash.mcp.server import _safe_selected_ids


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

    def test_r4_handoff_audit_uses_only_the_safe_selected_identity(self) -> None:
        payload = {"selected_skill": {"resource_id": "skill:presentations", "path": "C:/must-not-log"}}
        self.assertEqual(_safe_selected_ids(payload), ["skill:presentations"])

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
                    self.assertEqual([item.name for item in tools.tools], ["nexus.health", "nexus.discover_capabilities", "nexus.plan_task", "nexus.begin_host_capability_assessment", "nexus.assess_host_capabilities", "nexus.prepare_host_handoff", "nexus.prepare_enhancement_handoff"])
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
                    self.assertEqual(metadata["nexus.begin_host_capability_assessment"].title, "Nexus Host inventory ticket")
                    self.assertIn("single-use ticket", metadata["nexus.begin_host_capability_assessment"].description)
                    self.assertEqual(metadata["nexus.assess_host_capabilities"].title, "Nexus Host capability assessment")
                    self.assertIn("cannot enumerate installed plugins", metadata["nexus.assess_host_capabilities"].description)
                    self.assertEqual(metadata["nexus.prepare_host_handoff"].title, "Nexus Presentations host handoff")
                    self.assertIn("single verified Presentations", metadata["nexus.prepare_host_handoff"].description)
                    self.assertEqual(metadata["nexus.prepare_enhancement_handoff"].title, "Nexus Presentations enhancement handoff")
                    self.assertIn("cannot read or modify the artifact", metadata["nexus.prepare_enhancement_handoff"].description)
                    for tool in tools.tools:
                        self.assertIsNotNone(tool.annotations)
                        self.assertTrue(tool.annotations.read_only_hint)
                        self.assertFalse(tool.annotations.destructive_hint)
                        self.assertEqual(
                            tool.annotations.idempotent_hint,
                            tool.name not in {
                                "nexus.begin_host_capability_assessment",
                                "nexus.assess_host_capabilities",
                            },
                        )
                        self.assertFalse(tool.annotations.open_world_hint)
                    health = await session.call_tool("nexus.health", {})
                    self.assertFalse(health.is_error)
                    health_payload = self._payload(health)
                    self.assertEqual(health_payload["transport"], "stdio")
                    self.assertIn("nexus.begin_host_capability_assessment", health_payload["supported_tools"])
                    self.assertFalse(health_payload["capabilities"]["persistent_state"])
                    self.assertEqual(
                        health_payload["capabilities"]["ephemeral_security_state"],
                        "bounded_runtime_local",
                    )
                    planned = await session.call_tool("nexus.plan_task", {"task": "Translate this text into Klingon", "workspace_id": "project", "project_context_mode": "none"})
                    self.assertFalse(planned.is_error)
                    self.assertEqual(self._payload(planned)["fallback"]["kind"], "native_codex_fallback")
                    ticket_result = await session.call_tool("nexus.begin_host_capability_assessment", {
                        "schema_version": "nexus.host-capability-ticket-request.v1",
                        "host_surface": "chatgpt_desktop",
                        "inventory_scope": "current_turn_host_visible_subset",
                        "inventory_completeness": "not_globally_enumerated",
                        "task_category": "presentation",
                        "required_interfaces": ["editable_pptx_create", "pptx_open_render_validate"],
                    })
                    self.assertFalse(ticket_result.is_error)
                    ticket = self._payload(ticket_result)
                    self.assertEqual(ticket["security_result"]["code"], "HOST_INVENTORY_TICKET_READY")
                    snapshot = {
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
                    assessment = await session.call_tool("nexus.assess_host_capabilities", snapshot)
                    self.assertFalse(assessment.is_error)
                    self.assertEqual(self._payload(assessment)["security_result"]["code"], "HOST_CAPABILITY_SELECTION_READY")
                    replay = await session.call_tool("nexus.assess_host_capabilities", snapshot)
                    self.assertTrue(replay.is_error)
                    self.assertEqual(self._payload(replay)["error"]["code"], "HOST_INVENTORY_TICKET_REPLAYED")
                    handoff = await session.call_tool("nexus.prepare_host_handoff", {"task": "Create an editable PowerPoint presentation.", "workspace_id": "project", "project_context_mode": "none"})
                    self.assertTrue(handoff.is_error)
                    self.assertEqual(self._payload(handoff)["error"]["code"], "HANDOFF_NOT_ELIGIBLE")
                    enhancement = await session.call_tool("nexus.prepare_enhancement_handoff", {
                        "schema_version": "nexus.host-artifact-state.v1",
                        "artifact_kind": "pptx",
                        "base_mapping_id": "nexus.host-map.presentations.v1",
                        "base_execution_state": "execution_succeeded",
                        "base_validation_state": "validation_passed",
                        "checks": {"artifact_created": "passed", "artifact_editable": "passed", "presentation_open_render": "passed"},
                        "observations": ["layout_density_high"],
                        "enhancement_pass": 0,
                    })
                    self.assertFalse(enhancement.is_error)
                    self.assertEqual(self._payload(enhancement)["security_result"]["code"], "HOST_ENHANCEMENT_HANDOFF_READY")
                    invalid = await session.call_tool("nexus.plan_task", {"task": "x", "workspace_id": "unknown"})
                    self.assertTrue(invalid.is_error)
                    self.assertEqual(self._payload(invalid)["error"]["code"], "UNAUTHORIZED_WORKSPACE")
