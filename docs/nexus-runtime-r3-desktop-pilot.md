# Nexus Runtime R3 Desktop Integration Pilot

**Scope:** bounded local feasibility pilot for the existing Nexus Runtime R2 stdio
MCP server. This is not Remote MCP, a tunnel, OAuth, Skill Scout, or Core V1.3.

## Outcome

The local Nexus R2 integration is healthy and registered as `nexus-r2-local`.
Subsequent real ChatGPT Desktop acceptance established that the server is
visible and enabled, and that explicit Desktop calls to `nexus.health`,
`nexus.discover_capabilities`, and `nexus.plan_task` succeed. An explicit
editable PowerPoint planning request selected `ppt-master`, preserving native
editable PPTX routing.

The remaining R3 gap is **automatic** selection: a fresh, unqualified
presentation-planning conversation received a useful native response without
observed `nexus.plan_task` use. That observation is not evidence that Desktop
lacks local stdio MCP support. Current OpenAI documentation states that Codex
Desktop shares `~/.codex/config.toml`, that Desktop servers can be added in
**Settings -> MCP servers**, and that `/mcp` displays connected servers after
restart. See [Extending Codex with MCP](https://learn.chatgpt.com/docs/extend/mcp).

## Environment and supported configuration evidence

| Check | Result |
| --- | --- |
| Operating system | Windows local development machine |
| Desktop executable observed | `OpenAI.Codex` package `26.818.5229.0` running `ChatGPT.exe` |
| Local registration | `nexus-r2-local`, enabled, stdio transport |
| Server command | Existing dedicated Nexus R2 Python environment and `scripts/nexus_mcp.py`; no environment values configured |
| R2 tool surface | `nexus.health`, `nexus.discover_capabilities`, `nexus.plan_task` only |
| Authority | Read/plan-only; no shell, file-write, network, or arbitrary-path input authority |
| Desktop visibility | PASS: `nexus-r2-local` visible and enabled in real ChatGPT Desktop acceptance |

The registration is user-level machine configuration. It is not committed to
this repository and this pilot did not modify it.

## Local and Codex-host evidence

The following tests originate from the local Nexus/Codex environment; they are
not substituted for ChatGPT Desktop evidence.

| Scenario | Evidence | Result |
| --- | --- | --- |
| R2 health from a real Codex host | `codex exec --ephemeral` called `nexus.health` through `nexus-r2-local` | PASS; only the three safe tool names returned |
| R2 discover and plan from a real Codex host | `codex exec --ephemeral` called `nexus.discover_capabilities` then `nexus.plan_task` with configured opaque workspace ID `nexus-r2-validation` | Calls completed; no execution authority was granted |
| Protocol | MCP initialize, tool list, health, plan, invalid workspace | PASS in `tests/test_mcp_protocol.py` |
| Workspace authorization | Exact opaque workspace ID required; unknown IDs, UNC/device roots, reparse points and escapes reject | PASS in `tests/test_mcp_authorization.py` |
| Projection/redaction | Discover is metadata-only; plan has safe load evidence but no raw instructions or paths; failed loads are not success | PASS in `tests/test_mcp_redaction.py` |
| Context and server boundaries | No arbitrary request path/command/environment/Skill/Agent inputs; no execution or network-client imports | PASS in `tests/test_mcp_context_security.py` and `tests/test_mcp_boundaries.py` |

## Desktop test matrix

| Required Desktop test | Result | Reason / next evidence required |
| --- | --- | --- |
| Server visible in `/mcp` or MCP server settings | PASS | `nexus-r2-local` was visible and enabled in real Desktop acceptance. |
| `nexus.health` from Desktop | PASS | Explicit Desktop request completed successfully. |
| `nexus.discover_capabilities` from Desktop | PASS | Explicit Desktop request completed successfully. |
| `nexus.plan_task` from Desktop | PASS | Explicit Desktop request completed successfully; editable PowerPoint selected `ppt-master`. |
| Natural explicit selection | PASS | An explicit request can use Nexus. |
| Automatic positive/negative selection | NOT YET ACCEPTED | One unqualified presentation-planning prompt did not show a Nexus call. |
| Literal `@Nexus` | NOT EXPOSED | Do not claim support unless the UI visibly offers custom App/tool references. |
| Local D: file execution after planning | NOT GRANTED | A plan does not authorize file access. Do not broaden MCP to make this work. |

## Remaining Desktop acceptance

Automatic selection remains a host/model heuristic, not a server guarantee.
Use the four fresh-chat prompts in
[`nexus-runtime-r3-auto-invocation.md`](nexus-runtime-r3-auto-invocation.md)
to record the post-optimization Desktop result. Do not infer literal `@Nexus`
support unless that UI surface is visible.

## Privacy, authorization, and fallback contract

Only the R2 redacted projection may cross the MCP boundary:

- `discover_capabilities` returns bounded canonical metadata, never raw
  `SKILL.md` content or absolute local paths.
- `plan_task` returns an advisory plan and selected-Skill load evidence, not
  raw Skill/project/rule content, credentials, tracebacks, hidden reasoning, or
  execution authority.
- Callers supply only a configured opaque workspace ID. Unknown IDs reject
  safely; callers cannot select arbitrary local paths.
- If the local server is unavailable or a request is invalid, the host must
  report that Nexus was unavailable/rejected and use no remote fallback.

## Disable and removal

No disable/remove action was performed during this pilot. The existing local
registration can be removed safely with:

```powershell
codex mcp remove nexus-r2-local
```

Alternatively, disable the same server from the supported Desktop MCP settings
surface if it is shown there. Neither operation changes Nexus source code.

## Regression evidence

- Nexus: `python -m unittest discover -s tests -v` — **86 passed, 1 skipped**
  (Windows symlink fixture lacks the required privilege).
- Nexus V1.1 smoke: `python scripts/final_smoke.py` — **10/10 passed**.
- AI Coordinator R1 integration: `pytest tests/test_nexus_r1_integration.py -q`
  — **10 passed** (one pre-existing non-fatal pytest cache permission warning).

## Pilot decision

Nexus is available for explicit ChatGPT Desktop use. Automatic invocation is
not yet accepted and must be judged only from the fresh-conversation retest
packet after the metadata optimization.
