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
from .schemas import DISCOVER_INPUT_SCHEMA, HEALTH_INPUT_SCHEMA, PLAN_INPUT_SCHEMA, NexusMcpError
from .telemetry import emit


READ_ONLY_TOOL_ANNOTATIONS = types.ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def _text_for(payload: dict[str, Any]) -> str:
    # TextContent is the baseline MCP result representation supported by current
    # Codex hosts.  Keep the same redacted, versioned envelope as compact JSON
    # instead of relying on optional structuredContent support.
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _result(payload: dict[str, Any], error: bool = False) -> types.CallToolResult:
    return types.CallToolResult(content=[types.TextContent(type="text", text=_text_for(payload))], is_error=error)


def create_server(runtime: NexusMcpRuntime) -> Server[Any]:
    async def list_tools(_ctx: Any, _params: Any) -> types.ListToolsResult:
        return types.ListToolsResult(tools=[
            types.Tool(name="nexus.health", description="Read Nexus R2 local MCP health and safe capability flags.", inputSchema=HEALTH_INPUT_SCHEMA, annotations=READ_ONLY_TOOL_ANNOTATIONS),
            types.Tool(name="nexus.discover_capabilities", description="Read bounded Nexus Skill capability metadata only; no instructions or paths.", inputSchema=DISCOVER_INPUT_SCHEMA, annotations=READ_ONLY_TOOL_ANNOTATIONS),
            types.Tool(name="nexus.plan_task", description="Create a read/plan-only Nexus plan. This never executes the task.", inputSchema=PLAN_INPUT_SCHEMA, annotations=READ_ONLY_TOOL_ANNOTATIONS),
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
            else:
                raise NexusMcpError("INVALID_REQUEST", "tool is not supported")
            emit(request_id, params.name, str(payload.get("status", "ready")), int((time.monotonic() - started) * 1000), [item.get("resource_id", "") for item in payload.get("selected_skills", [])])
            return _result(payload)
        except NexusMcpError as exc:
            payload = safe_error(request_id, exc)
            emit(request_id, params.name, exc.code, int((time.monotonic() - started) * 1000))
            return _result(payload, error=True)
        except Exception:
            payload = safe_error(request_id, NexusMcpError("INTERNAL_ERROR", "Nexus MCP could not safely complete the request"))
            emit(request_id, params.name, "INTERNAL_ERROR", int((time.monotonic() - started) * 1000))
            return _result(payload, error=True)

    return Server("nexus-local-r2", version="2.0-r2", title="Nexus", description="Adaptive AI Capability Hub local read/plan-only MCP server", on_list_tools=list_tools, on_call_tool=call_tool)


async def run_stdio(runtime: NexusMcpRuntime) -> None:
    server = create_server(runtime)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
