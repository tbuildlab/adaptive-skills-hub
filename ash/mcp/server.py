"""Official MCP SDK stdio wiring. No HTTP transport is created by R2."""
from __future__ import annotations

import time
import json
from typing import Any
from uuid import uuid4

import mcp_types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .adapter import NexusMcpRuntime
from .redaction import safe_error
from .schemas import (
    ASSESS_HOST_CAPABILITIES_INPUT_SCHEMA,
    BEGIN_HOST_CAPABILITY_ASSESSMENT_INPUT_SCHEMA,
    DISCOVER_INPUT_SCHEMA,
    HEALTH_INPUT_SCHEMA,
    PLAN_INPUT_SCHEMA,
    PREPARE_ENHANCEMENT_HANDOFF_INPUT_SCHEMA,
    PREPARE_HOST_HANDOFF_INPUT_SCHEMA,
    NexusMcpError,
)
from .telemetry import emit


READ_ONLY_TOOL_ANNOTATIONS = types.ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)

# Tool descriptions are the host's primary semantic routing signal.  Keep each
# description concise, explicit, and mutually exclusive: routine task routing
# belongs only to ``nexus.plan_task``; diagnostics and catalog inspection do
# not compete for ordinary conversations.
HEALTH_TOOL_DESCRIPTION = (
    "Check Nexus local MCP availability and safe capability flags. Use only for "
    "diagnostics or connection status, not for task planning, execution, or ordinary chat."
)
DISCOVER_TOOL_DESCRIPTION = (
    "Inspect the bounded Nexus capability catalog when the user explicitly asks "
    "which Skills or capabilities are available. Returns metadata only; do not use "
    "for ordinary task planning, execution, or casual conversation."
)
PLAN_TOOL_DESCRIPTION = (
    "Plan a substantive multi-step task and select the smallest suitable Nexus Skills "
    "before the host executes. Use for professional artifacts (presentations, documents, "
    "spreadsheets, PDFs), engineering/debugging/testing/security, evidence-based research, "
    "coursework, or work where choosing capabilities improves reliability. Do not use for "
    "greetings, simple calculations or facts, simple translation, short rewrites, or execution."
)
ONE_USE_READ_ONLY_TOOL_ANNOTATIONS = types.ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=False,
)
ASSESS_HOST_CAPABILITIES_DESCRIPTION = (
    "Classify a bounded, current-turn subset of capability metadata already "
    "surfaced by the ChatGPT Desktop host. This tool cannot enumerate installed "
    "plugins, inspect private host state, load or execute a Skill, or grant an "
    "execution mapping. Use only before the approved host handoff workflow."
)
BEGIN_HOST_CAPABILITY_ASSESSMENT_DESCRIPTION = (
    "Issue a short-lived, single-use ticket for one bounded current-turn Host "
    "capability metadata submission. The ticket is scoped to this local stdio "
    "runtime and grants no execution or private Host-state access. Call this "
    "immediately before nexus.assess_host_capabilities."
)
PREPARE_HOST_HANDOFF_DESCRIPTION = (
    "Create a short-lived, read-only host execution handoff only after planning a "
    "single verified Presentations Skill. The ChatGPT host, not Nexus, decides "
    "eligibility and performs any artifact action. Never use this tool to execute, "
    "write files, invoke commands, or substitute a Skill."
)
PREPARE_ENHANCEMENT_HANDOFF_DESCRIPTION = (
    "Create a short-lived, read-only Host enhancement handoff only from a "
    "current, redacted, validated Presentations artifact state. Nexus cannot "
    "read or modify the artifact. The ChatGPT host must prove primary receipt "
    "provenance, checkpoint the artifact, and revalidate any enhancement. Never "
    "use this tool to execute, write files, invoke commands, or substitute a Skill."
)


def _text_for(payload: dict[str, Any]) -> str:
    # TextContent is the baseline MCP result representation supported by current
    # Codex hosts.  Keep the same redacted, versioned envelope as compact JSON
    # instead of relying on optional structuredContent support.
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _result(payload: dict[str, Any], error: bool = False) -> types.CallToolResult:
    return types.CallToolResult(content=[types.TextContent(type="text", text=_text_for(payload))], is_error=error)


def _safe_selected_ids(payload: dict[str, Any]) -> list[str]:
    """Extract only safe selected IDs from either plan or R4 handoff output."""
    ids = [str(item.get("resource_id", "")) for item in payload.get("selected_skills", []) if isinstance(item, dict)]
    selected = payload.get("selected_skill")
    if not ids and isinstance(selected, dict):
        ids = [str(selected.get("resource_id", ""))]
    return [item for item in ids if item]


def create_server(runtime: NexusMcpRuntime) -> Server[Any]:
    async def list_tools(_ctx: Any, _params: Any) -> types.ListToolsResult:
        return types.ListToolsResult(tools=[
            types.Tool(name="nexus.health", title="Nexus status", description=HEALTH_TOOL_DESCRIPTION, inputSchema=HEALTH_INPUT_SCHEMA, annotations=READ_ONLY_TOOL_ANNOTATIONS),
            types.Tool(name="nexus.discover_capabilities", title="Nexus capability catalog", description=DISCOVER_TOOL_DESCRIPTION, inputSchema=DISCOVER_INPUT_SCHEMA, annotations=READ_ONLY_TOOL_ANNOTATIONS),
            types.Tool(name="nexus.plan_task", title="Nexus substantive-task planner", description=PLAN_TOOL_DESCRIPTION, inputSchema=PLAN_INPUT_SCHEMA, annotations=READ_ONLY_TOOL_ANNOTATIONS),
            types.Tool(name="nexus.begin_host_capability_assessment", title="Nexus Host inventory ticket", description=BEGIN_HOST_CAPABILITY_ASSESSMENT_DESCRIPTION, inputSchema=BEGIN_HOST_CAPABILITY_ASSESSMENT_INPUT_SCHEMA, annotations=ONE_USE_READ_ONLY_TOOL_ANNOTATIONS),
            types.Tool(name="nexus.assess_host_capabilities", title="Nexus Host capability assessment", description=ASSESS_HOST_CAPABILITIES_DESCRIPTION, inputSchema=ASSESS_HOST_CAPABILITIES_INPUT_SCHEMA, annotations=ONE_USE_READ_ONLY_TOOL_ANNOTATIONS),
            types.Tool(name="nexus.prepare_host_handoff", title="Nexus Presentations host handoff", description=PREPARE_HOST_HANDOFF_DESCRIPTION, inputSchema=PREPARE_HOST_HANDOFF_INPUT_SCHEMA, annotations=READ_ONLY_TOOL_ANNOTATIONS),
            types.Tool(name="nexus.prepare_enhancement_handoff", title="Nexus Presentations enhancement handoff", description=PREPARE_ENHANCEMENT_HANDOFF_DESCRIPTION, inputSchema=PREPARE_ENHANCEMENT_HANDOFF_INPUT_SCHEMA, annotations=READ_ONLY_TOOL_ANNOTATIONS),
        ])

    async def call_tool(_ctx: Any, params: types.CallToolRequestParams) -> types.CallToolResult:
        request_id = str(uuid4())
        started = time.monotonic()
        try:
            if params.name == "nexus.health":
                payload = runtime.health()
            elif params.name == "nexus.discover_capabilities":
                payload = runtime.discover_capabilities(params.arguments)
            elif params.name == "nexus.plan_task":
                payload = runtime.plan(params.arguments)
            elif params.name == "nexus.begin_host_capability_assessment":
                payload = runtime.begin_host_capability_assessment(params.arguments)
            elif params.name == "nexus.assess_host_capabilities":
                payload = runtime.assess_host_capabilities(params.arguments)
            elif params.name == "nexus.prepare_host_handoff":
                payload = runtime.prepare_host_handoff(params.arguments)
            elif params.name == "nexus.prepare_enhancement_handoff":
                payload = runtime.prepare_enhancement_handoff(params.arguments)
            else:
                raise NexusMcpError("INVALID_REQUEST", "tool is not supported")
            emit(request_id, params.name, str(payload.get("status", "ready")), int((time.monotonic() - started) * 1000), _safe_selected_ids(payload))
            return _result(payload)
        except NexusMcpError as exc:
            payload = safe_error(request_id, exc)
            emit(request_id, params.name, exc.code, int((time.monotonic() - started) * 1000))
            return _result(payload, error=True)
        except Exception:
            payload = safe_error(request_id, NexusMcpError("INTERNAL_ERROR", "Nexus MCP could not safely complete the request"))
            emit(request_id, params.name, "INTERNAL_ERROR", int((time.monotonic() - started) * 1000))
            return _result(payload, error=True)

    return Server("nexus-local-r5", version="2.0-r5.2", title="Nexus", description="Adaptive AI Capability Hub local read/plan-and-handoff-only MCP server", on_list_tools=list_tools, on_call_tool=call_tool)


async def run_stdio(runtime: NexusMcpRuntime) -> None:
    server = create_server(runtime)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
