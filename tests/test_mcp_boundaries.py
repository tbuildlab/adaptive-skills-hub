from __future__ import annotations

from pathlib import Path
import unittest

from ash.mcp.schemas import NexusMcpError, parse_plan_request, parse_prepare_enhancement_handoff_request


class McpBoundaryTests(unittest.TestCase):
    def test_request_schema_has_no_path_command_environment_skill_or_agent_inputs(self) -> None:
        for forbidden in ("path", "file", "root", "command", "environment", "skill", "agent"):
            with self.assertRaises(NexusMcpError):
                parse_plan_request({"task": "x", "workspace_id": "project", forbidden: "x"})

    def test_task_and_constraint_limits_fail_closed(self) -> None:
        with self.assertRaises(NexusMcpError) as task:
            parse_plan_request({"task": "x" * (8 * 1024 + 1), "workspace_id": "project"})
        self.assertEqual(task.exception.code, "REQUEST_LIMIT")
        with self.assertRaises(NexusMcpError):
            parse_plan_request({"task": "x", "workspace_id": "project", "constraints": ["x"] * 17})

    def test_r5_enhancement_schema_accepts_no_artifact_or_execution_inputs(self) -> None:
        base = {
            "schema_version": "nexus.host-artifact-state.v1",
            "artifact_kind": "pptx",
            "base_mapping_id": "nexus.host-map.presentations.v1",
            "base_execution_state": "execution_succeeded",
            "base_validation_state": "validation_passed",
            "checks": {"artifact_created": "passed", "artifact_editable": "passed", "presentation_open_render": "passed"},
            "observations": [],
            "enhancement_pass": 0,
        }
        for forbidden in ("path", "artifact_ref", "task", "workspace_id", "command", "skill", "agent", "handoff_id", "receipt", "content_sha256"):
            with self.assertRaises(NexusMcpError):
                parse_prepare_enhancement_handoff_request({**base, forbidden: "attacker-controlled"})

    def test_r2_server_modules_have_no_execution_or_network_client_imports(self) -> None:
        root = Path(__file__).resolve().parents[1] / "ash" / "mcp"
        source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))
        for forbidden in ("import subprocess", "execute_route", "socket.", "requests.", "urllib.", "pip install", "agent spawn", "os.system", "shell=True"):
            self.assertNotIn(forbidden, source)
