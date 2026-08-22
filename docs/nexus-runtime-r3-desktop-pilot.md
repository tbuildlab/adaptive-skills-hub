# Nexus Runtime R3 Desktop Integration Pilot

**Scope:** bounded local feasibility pilot for the existing Nexus Runtime R2 stdio
MCP server. This is not Remote MCP, a tunnel, OAuth, Skill Scout, or Core V1.3.

## Outcome

The local Nexus R2 integration is healthy and registered with Codex as
`nexus-r2-local`, but this pilot cannot truthfully confirm that the currently
running ChatGPT Desktop instance has consumed that registration. The required
Desktop MCP surface was not accessible to this text-only agent session through
an approved UI-observation channel. No Desktop-originated MCP call was made.

This is a **Desktop UI verification gap**, not evidence that ChatGPT Desktop
does not support local stdio MCP. The current OpenAI documentation states that
Codex Desktop shares `~/.codex/config.toml`, that Desktop servers can be added
in **Settings -> MCP servers**, and that `/mcp` displays connected servers after
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
| Desktop visibility | **Not verified**: no approved normal-text Desktop UI control surface was available to this session |

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
| Server visible in `/mcp` or MCP server settings | NOT VERIFIED | The Desktop UI was not observable through an approved tool in this text session. |
| `nexus.health` from Desktop | NOT RUN | Must originate from the visible Desktop tool surface. |
| `nexus.discover_capabilities` from Desktop | NOT RUN | Same boundary. |
| `nexus.plan_task` from Desktop | NOT RUN | Same boundary; use opaque `nexus-r2-validation`, never a path. |
| Natural explicit selection | NOT RUN | Record the actual UI mechanism, not an assumed `@Nexus` syntax. |
| Automatic positive/negative selection | NOT RUN | Only test if the Desktop product exposes autonomous MCP tool selection. |
| Literal `@Nexus` | NOT EXPOSED | Do not claim support unless the UI visibly offers custom App/tool references. |
| Local D: file execution after planning | NOT GRANTED | A plan does not authorize file access. Do not broaden MCP to make this work. |

## Required single user interaction to resume

In **ChatGPT Desktop**, restart the app if it was already open, open a new
conversation, type `/mcp`, and confirm whether `nexus-r2-local` appears as
connected. If the command is unavailable, open **Settings -> MCP servers** and
confirm the visible status of `nexus-r2-local`. Provide the visible result (a
screenshot or exact status text). This is the only user interaction required to
resume the Desktop-originated health, discovery, plan, natural UX, and optional
auto-selection tests.

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

Do not represent Nexus as available in ChatGPT Desktop until the Desktop
surface and Desktop-originated calls are observed. The R2 implementation is
safe to leave installed for Codex; daily ChatGPT Desktop use remains pending
the single UI confirmation above.
