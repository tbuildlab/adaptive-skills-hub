# Nexus Runtime R2 local MCP

Runtime R2 is an **explicit local stdio integration layer** over the frozen Nexus
V1.2 Core and accepted Runtime R1 handoff. It is not a network service, ChatGPT
integration, plugin, OAuth flow, GUI, remote endpoint, or execution runtime.

## SDK and environment

R2 uses the official [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk):

- Package: `mcp==2.0.0` (MIT; Python 3.10–3.14 supported)
- Direct wheel SHA-256:
  `1cb4c75d2d2c7b8c1d756355e5d82a39f2822cc7f13e22a2051d7ca3592349d6`
- Direct dependency and full resolved environment: `requirements-r2-mcp.txt` and
  `requirements-r2-mcp.lock`
- Validated isolated local environment: `D:\DevTools\NexusR2Python`
- Download cache: `D:\DevCache\nexus-r2-mcp-download`

The SDK contains optional HTTP/ASGI packages, but R2 imports only `mcp.server` and
`mcp.server.stdio`. It creates no HTTP application, socket, listener, client,
background daemon, or network request.

## Tool surface and lifecycle

The only tools are:

1. `nexus.health`
2. `nexus.discover_capabilities`
3. `nexus.plan_task`

The official SDK owns JSON-RPC initialization, `notifications/initialized` gating,
tool negotiation, malformed-frame handling, and stdio shutdown. stdin/stdout carry
newline-delimited MCP JSON-RPC only. The R2 implementation never writes diagnostics
to stdout; opt-in safe diagnostics are disabled by default and use stderr only.

`nexus.plan_task` returns an advisory plan, never authorization to execute it. The
safe, versioned result envelope is compact JSON in standard MCP `TextContent` for
compatibility with the current Codex local host; it is not a raw packet. It
does not expose commands, raw rules, raw project files, raw `SKILL.md` contents,
absolute paths, environment values, credentials, tracebacks, candidates, scores, or
hidden reasoning.

## Workspace authorization

Tool callers supply an opaque `workspace_id`, never a filesystem path. The local
launcher supplies a separate, trusted JSON allowlist. Start from
`config/nexus-mcp-workspaces.example.json`, copy it to a private local location, and
replace the example root with one specific project root. Do not commit the copy.

```json
{
  "schema_version": "nexus.mcp.workspace.v1",
  "workspaces": {
    "my-project": { "root": "D:\\work\\my-project" }
  }
}
```

At startup R2 validates every configured root and rejects drive roots, the user home
root, UNC/device paths, missing roots, symlinks, junctions, mount/reparse points,
and unsafe resolution. During a request it accepts only exact configured IDs and
performs guarded before/after reads. Governance context is a fixed allowlist of
small, UTF-8, non-secret files; `README.md`, source comments, recursive discovery,
and caller-named files are not context inputs.

## Run locally

```powershell
D:\DevTools\NexusR2Python\Scripts\python.exe scripts\nexus_mcp.py `
  --workspace-config D:\DevTools\NexusR2\workspaces.json
```

For an explicit, reversible Codex local registration, after all tests pass:

```powershell
codex mcp add nexus-r2-local -- D:\DevTools\NexusR2Python\Scripts\python.exe `
  D:\chatgpt\安装skills\adaptive-skills-hub\scripts\nexus_mcp.py `
  --workspace-config D:\DevTools\NexusR2\workspaces.json
codex mcp get nexus-r2-local
```

For a non-interactive Codex host, set the following **on the same
`[mcp_servers.nexus-r2-local]` table** in `~/.codex/config.toml` (or an
equivalent trusted project configuration):

```toml
startup_timeout_sec = 15
tool_timeout_sec = 60
default_tools_approval_mode = "writes"
```

R2 advertises all three tools as read-only, non-destructive, idempotent, and
closed-world. The `writes` policy therefore permits these bounded calls while
continuing to require approval for any future tool that is not explicitly
read-only. Do not replace it with an unrestricted policy.

Release validation exercised this registration with the real local Codex host:
`nexus.health`, `nexus.discover_capabilities`, and one bounded
`nexus.plan_task` call completed without execution authority. This is local
Codex-host evidence only; it is not ChatGPT App integration or remote MCP.

Remove it without touching Nexus source, branches, or tags:

```powershell
codex mcp remove nexus-r2-local
```

The registration is local user configuration only. It does not alter AI Coordinator
or replace the R1 `python scripts/nexus.py plan ... --handoff` path.

## Limits and failure model

- Task: 8 KiB UTF-8; constraints: 16 / 8 KiB aggregate
- Context: 12 files / 128 KiB aggregate / 32 KiB per file
- Skill read: 3 selected / 128 KiB each / 256 KiB aggregate
- Catalog: 1,024 metadata records; MCP response: 64 KiB
- Soft synchronous planning budget: 15 seconds

Structured tool errors use stable, non-sensitive codes including
`INVALID_REQUEST`, `UNAUTHORIZED_WORKSPACE`, `CONTEXT_REJECTED`,
`SKILL_LOAD_FAILED`, `NEXUS_UNAVAILABLE`, `TIMEOUT`, and `INTERNAL_ERROR`.
R2 fails closed and leaves host Codex free to use its native fallback.

Large metadata discovery responses are truncated to a conservative TextContent
envelope budget before the 64 KiB MCP wire ceiling. The response reports both
returned and available safe-metadata counts plus `truncated: true`; it never turns
a large catalog into an unbounded response or an internal error.

## R1 coexistence and scope

R1 remains independent and usable. R2 reuses existing V1.2 discovery, planning,
selection, validation, and selected-Skill loader interfaces but adds a guarded R2
context reader and selected-file read guard. It does not add embeddings, a vector
database, Skill install/update, subprocess/shell execution, network fetches, Agent
execution/delegation, persistence, R3 ChatGPT integration, or V1.3 work.
