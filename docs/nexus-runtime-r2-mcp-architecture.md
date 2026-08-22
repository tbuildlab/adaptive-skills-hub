# Nexus Runtime R2 — Local MCP Architecture and Security Review

## Status, decision, and scope

**Decision:** approve an additive, local-only, stdio MCP *planning* adapter over
the existing Nexus V1.2/R1 core, subject to the implementation acceptance matrix
in this document. This is an implementation-ready design, not an MCP server.

R2 exists to let a compatible local host ask Nexus for a bounded capability plan.
It does not make Nexus an executor. The host retains all authority to modify files,
run commands, generate artifacts, run tests, and answer the user.

This document is deliberately limited to:

- local stdio MCP;
- read/plan-only capability discovery and planning;
- explicit workspace authorization, redaction, and adversarial tests; and
- coexistence with the accepted R1 CLI handoff.

It does **not** add a network listener, HTTP/SSE transport, a tunnel, a remote
service, OAuth, ChatGPT integration, Skill installation/update, Agent execution,
an embeddings/vector store, a database, a multi-Agent runtime, or a V1.3 core
release. `v1.1-final`, `v1.2-final`, and `runtime-r1-final` remain unchanged.

## Evidence used for this review

### Current Nexus implementation facts

The review is grounded in `b21fe34` rather than earlier design notes:

- `ash.v2.plan_task` composes bounded project context, rule extraction,
  deterministic ranking, minimal selection, validation planning, and an honest
  native fallback. It declares no model client, network access, Agent delegation,
  or automatic command execution.
- `ash.v2.load_plan_skills` uses the V1 loader only after selection; the R1 CLI
  validates coverage, duplicate selection, and selected-Skill loading.
- `scripts/hub.py plan --handoff` is stateless and emits a redacted envelope.
  It fails closed when selected-Skill load evidence is missing, ambiguous, failed,
  or invalid. It excludes instructions, project context, rules, candidates, and
  secrets from the handoff.
- `ash.execution.execute_route` executes a hook only when a caller separately
  supplies `--allow-skill-commands`; it uses an argument vector and `shell=False`.
  A normal R2 request will never invoke this function.
- Discovery records provenance, compatibility, disabled/malformed states, and
  duplicate/shadow decisions. Agents are indexed separately and remain advisory.

The R1 handoff remains a compatible, useful fallback. R2 must call the same
planning model; it must not parse R1 human-readable stdout or duplicate its router.

### Protocol and local-client facts

The current MCP specification requires JSON-RPC lifecycle initialization,
capability/version negotiation, and an `initialized` notification before normal
operations. It recommends bounded request timeouts and uses stream closure for
stdio shutdown. [MCP lifecycle specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)

For stdio, the client launches the child process, messages are newline-delimited
JSON-RPC, and stdout must contain only valid MCP messages; diagnostics belong on
stderr. [MCP transport specification](https://modelcontextprotocol.io/specification/2024-11-05/basic/transports)

Tools require a declared `tools` capability and valid JSON Schema inputs. The
specification distinguishes malformed protocol requests from tool execution/input
errors, and requires input validation, access control, output sanitization, rate
limits, and timeouts. [MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)

This machine's installed Codex CLI (`0.146.1`) exposes `codex mcp list|get|add|
remove|login|logout`, and its current config already contains an unrelated local
MCP entry. That proves local MCP configuration exists in this environment; it does
not register Nexus, prove every Codex surface supports the same feature, or grant
R2 any additional authority. No Codex configuration is changed by this review.

### Assumptions fixed by the approved scope

- The server and host run as the same local Windows user.
- R2 is launched by a compatible local host through stdio, not by a network peer.
- The workspace set is configured by the same-user launcher/configuration, not
  supplied dynamically by a task or model.
- Workspace and Skill content are untrusted data. Security policy outranks project
  instructions, Skill instructions, task text, and tool annotations.
- No security-relevant persistent state is required for an initial planning service.

These scope decisions remove the otherwise material questions about remote identity,
multi-tenancy, and write approval. If any changes, a new threat-model review is
required before implementation or deployment.

## Architecture options

| Option | Correctness and maintenance | Security and observability | Decision |
| --- | --- | --- | --- |
| A. Thin MCP adapter over `ash.v2` | Reuses the actual V1.2 plan, selection, fallback, loader, and validation semantics; one decision model to test. | Adapter can add protocol, authorization, redaction, budgets, and safe stderr events at a narrow boundary. | **Select.** |
| B. Separate MCP planner service | Creates a second router/ranking/context implementation and eventual drift from V1.2/R1. | Doubles the attack surface and evidence paths; requires duplicated regression coverage. | Reject. |
| C. MCP wrapper around CLI/stdout handoff | Preserves R1 but requires parsing a human-facing format and loses typed internal data. | Fragile output coupling and confusing error/log separation; weaker schema evolution. | Reject. |

### Advisory governance verdict

Nexus recommended `automation-governance-architect` as an advisory Agent. Its
actual guidance was consulted for this review, but it was not executed or delegated.
Its applicable verdict is **PARTIAL AUTOMATION ONLY**: R2 may automate bounded
planning/discovery, while file changes, commands, tests, artifacts, final validation,
and user communication remain host-controlled with explicit recovery through R1 or
native Codex fallback. This keeps the dependency surface small, supplies failure and
rollback paths, and requires documentation plus adversarial evidence before any
production enablement.

### Selected component model

```text
Compatible local host
  | stdio JSON-RPC only
  v
Nexus R2 MCP server
  | protocol schema + request budget + workspace_id authorization
  | redaction + safe telemetry
  v
Nexus adapter (no execution authority)
  | guarded context reader and guarded selected-Skill loader
  v
Existing Nexus V1.2 Core
  | build_index -> plan_task -> load selected Skills -> validate_plan
  v
Redacted structured MCP result
  |
  `-> host separately decides whether/how to execute and validate
```

The adapter may call `build_index`, `plan_task`, `load_plan_skills`, and
`validate_plan`; it must not call `execute_route`, `subprocess`, a network client,
or any Skill hook. Existing V1.2 public behavior remains unchanged. Optional
limits/guards added to a reusable loader must default to today's behavior so the R1
CLI contract is preserved.

## Final R2 MCP surface

R2 exposes **three** tools, not four. `explain_selection` is rejected as a separate
tool because it either re-plans ambiguously or requires a plan cache that contradicts
the stateless default. `plan_task` already returns the concise selected-skill and
fallback rationale the host needs. There are no prompts or resources: either would
needlessly create a content-exposure surface.

All tool names use the `nexus.` namespace, are unique, and use JSON Schema 2020-12
with `additionalProperties: false`. Server capability advertisement is only
`{"tools": {}}`; it does not advertise `listChanged`, tasks, prompts, resources,
sampling, or elicitation. Tools are synchronous and have `taskSupport: "forbidden"`.

### `nexus.health`

**Purpose:** prove that a server process is available without touching a workspace.

```json
{
  "type": "object",
  "additionalProperties": false
}
```

Result contains `schema_version`, product identity, server version, supported tool
names, protocol version selected during initialization, and an opaque count of
configured workspaces. It contains no absolute path, configuration contents, Skill,
environment, token, or diagnostic data. It writes no state and performs no network
operation. Hard budget: 1 second and 4 KiB result.

### `nexus.discover_capabilities`

**Purpose:** return metadata-only, canonical, currently routable Skill capabilities
for one authorized workspace. It does not load full `SKILL.md` text.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["workspace_id"],
  "properties": {
    "workspace_id": {
      "type": "string",
      "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$"
    },
    "query": {"type": "string", "maxLength": 256},
    "max_results": {"type": "integer", "minimum": 1, "maximum": 25, "default": 20}
  }
}
```

Result contains a `nexus.mcp.v1` envelope and at most `max_results` records with
`resource_id`, `name`, matched capability labels, `source_scope`,
`runtime_compatibility`, `status`, and an integrity metadata fingerprint. It omits
absolute paths, descriptions that may contain untrusted long text, frontmatter,
Skill bodies, duplicate candidates, hidden scoring, and project content. It is
read-only, stateless, offline, and bounded to 10 seconds / 32 KiB.

### `nexus.plan_task`

**Purpose:** create one bounded, redacted plan using existing Nexus V1.2 semantics.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["task", "workspace_id"],
  "properties": {
    "task": {"type": "string", "minLength": 1, "maxLength": 8192},
    "workspace_id": {
      "type": "string",
      "pattern": "^[a-z0-9][a-z0-9_-]{0,63}$"
    },
    "project_context_mode": {
      "type": "string",
      "enum": ["none", "governance"],
      "default": "governance"
    },
    "constraints": {
      "type": "array",
      "maxItems": 16,
      "items": {"type": "string", "minLength": 1, "maxLength": 512}
    }
  }
}
```

`constraints` are caller-provided requirements, not executable instructions. Their
aggregate UTF-8 length is limited to 8 KiB. There is no `path`, `file`, `root`,
`command`, `environment`, `skill`, or `agent` argument.

The successful `structuredContent` is a versioned `nexus.mcp.v1` envelope:

```json
{
  "schema_version": "nexus.mcp.v1",
  "request_id": "uuid",
  "product": {"name": "Nexus", "subtitle": "Adaptive AI Capability Hub"},
  "status": "planned|fallback_needed|blocked",
  "task_summary": {"task_type": "...", "required_capabilities": ["..."]},
  "selected_skills": [{
    "resource_id": "skill:...",
    "name": "...",
    "source_scope": "...",
    "runtime_compatibility": "directly_usable_by_codex",
    "content_sha256": "...",
    "characters": 123,
    "load_status": "loaded"
  }],
  "execution_steps": [{"capability": "...", "summary": "...", "validation": ["..."]}],
  "validation_plan": [{"kind": "...", "summary": "..."}],
  "advisory_agents": ["..."],
  "fallback": {"kind": "native_codex_fallback", "status": "...", "reason_code": "..."},
  "warnings": ["..."]
}
```

`request_id` is correlation-only and expires when the response is emitted; it is not
a retrieval token. A Skill identity is exact through resource ID, provenance,
content hash, character count, and load status, but R2 intentionally omits the local
file path and raw instructions. The same information is serialized into a concise
`TextContent` block for clients that do not expose `structuredContent`.

The tool has no write or network behavior. It never auto-installs/updates a Skill,
executes Skill metadata, starts an Agent, invokes a shell, or asks a model to execute
the plan. Hard budget: 15 seconds planning, absolute 30 seconds, 64 KiB response.

## Error, lifecycle, and fallback contract

1. The process accepts only newline-delimited JSON-RPC on stdin and emits only MCP
   JSON-RPC on stdout. Safe event logs go to stderr.
2. `initialize` must be first; server and client negotiate a supported protocol
   version. The server waits for `notifications/initialized` before serving tools.
3. Unknown methods, invalid JSON-RPC, protocol-version mismatch, and schema-invalid
   envelopes receive JSON-RPC errors. Unknown tool / malformed request uses the
   protocol error path; no traceback or path is disclosed.
4. Valid protocol requests that fail a policy or data check return a tool result with
   `isError: true` and only a stable code plus safe message, for example
   `WORKSPACE_NOT_AUTHORIZED`, `CONTEXT_REJECTED`, `REQUEST_LIMIT`,
   `SKILL_LOAD_UNVERIFIED`, `PLAN_BLOCKED`, or `INTERNAL_FAILURE`.
5. Timeouts fail closed: cancel internal work, return a safe `TIMEOUT` result, and
   never continue in the background. Closing stdin starts graceful shutdown; server
   releases in-memory data and exits.
6. If initialization, planning, or selected-Skill verification fails, the host gets
   an explicit unavailable/blocked result and may use native Codex capability. R2
   never pretends a Skill was loaded or substitutes an unrelated Skill.

## Workspace authorization and bounded project context

### Authorization model

Use **both** a trusted server configuration allowlist and host-supplied
`workspace_id` validation:

- Startup configuration maps a small opaque ID to one canonical local root. The
  mapping is supplied by the same-user launcher/configuration, outside tool input.
- A request can name only one preconfigured ID. It cannot register, enumerate,
  replace, or provide a root. Client `roots` capability, if advertised, is not an
  authority grant and is ignored for R2 authorization.
- R2 supports local fixed-drive roots only. UNC paths, device paths, home roots,
  filesystem roots, and a root equal to a configured ancestor that covers unrelated
  repositories are rejected. No whole-drive allowlist is permitted.

On Windows, implementation canonicalizes the configured root with strict resolution
at startup, normalizes drive/case identity, and checks every candidate before and
after opening. It rejects `..`, alternate roots, non-regular files, symlinks,
junctions, mount points, and any reparse point in the candidate chain. A race or
resolution failure is `CONTEXT_REJECTED`; it never falls back to lexical comparison.

This is stricter than present V1.2 context discovery, which is suitable for its fixed
CLI project root but is not by itself an R2 authorization layer. R2 must introduce a
guarded context reader before it hands content to the core. It must not weaken the
existing V1.2 scanner or change ordinary R1 behavior.

### Context modes and caps

`none` reads no project files. `governance` reads only an allowlisted root-level
governing set (`AGENTS.md`, `PROJECT_RULES.md`, `DECISIONS.md`,
`FROZEN-DECISIONS.md`) and a fixed, explicit architecture manifest set when present.
There is no arbitrary filename argument, recursive scan, glob, source-code crawl, or
README-by-default input.

| Limit | R2 hard cap |
| --- | ---: |
| Files | 12 |
| Aggregate decoded bytes | 128 KiB |
| One file | 32 KiB |
| Relative depth | 2, allowlist only |
| Task | 8 KiB UTF-8 |
| Constraints | 16 / 8 KiB aggregate |
| Candidate metadata records | 1,024 |
| Selected Skills | 3 |
| One selected Skill | 128 KiB |
| Aggregate selected Skill text | 256 KiB |
| MCP response | 64 KiB |

NUL-containing, non-UTF-8, binary/polyglot-suspect, unreadable, secret-named, and
over-limit files are excluded and represented only by a safe reason code. Secret
patterns in otherwise eligible content are not returned; implementation should reject
the entire context item before planner use rather than redact it line by line. Project
content is data, not policy: only the R2 fixed security policy and a narrowly parsed,
recognized governance-rule subset can affect planning. No project text may grant a
root, tool, command, network, persistence, or disclosure permission.

## Data, provenance, redaction, and state

Discovery remains metadata-first. Selection causes at most the selected Skills to be
loaded under the above guarded path/size checks. A selected record preserves
`resource_id`, source scope, canonical/duplicate status, compatibility, hash, and
load evidence. Duplicate or shadowed copies remain non-routable unless the existing
core resolves them deterministically; equal-authority conflicts remain fail-closed.

Never expose through MCP:

- raw `SKILL.md`, project files, project-rule bodies, source comments, or README text;
- absolute file paths, directory listings, registry internals, candidate score detail,
  rejected-candidate internals, or hidden reasoning;
- environment values, credentials, tokens, cookies, caches, error tracebacks, or
  external reference contents.

R2 is stateless. It stores no task, project, Skill, plan, request, or raw log content
after a response. A process-local request object is discarded at completion. This is
why there is no `explain_selection(plan_id)`, cached `get_loaded_skill`, or
`validate_result` tool. An optional persistent evidence/audit store is deferred to a
separately approved release with data retention, ACL, deletion, and threat-model
requirements.

Safe observability is stderr-only and disabled by default. When enabled for a local
debug session, it emits timestamp, generated request ID, tool name, status code,
duration bucket, selected Skill IDs/hashes, and fallback flag; it never emits task,
path, context, Skill body, environment, or credential data. No default log retention
exists. stdout logging is forbidden.

## Threat model

### Assets and boundaries

| Asset | Why it matters | Boundary |
| --- | --- | --- |
| Workspace identity and files | Project privacy/integrity | MCP caller -> workspace authorization -> guarded reader |
| Project governance text | Can influence planning if misclassified | untrusted content -> fixed parser/policy |
| Local Skill instructions/provenance | Confidential workflow and selection integrity | discovery -> guarded selected loader -> redactor |
| Host execution authority | Could alter files/run commands | plan result -> host-only execution decision |
| Process availability | Local work can be blocked by resource abuse | caller -> JSON-RPC budgets/timeouts |
| Safe telemetry | Needed for diagnosis but may leak content | server -> stderr sink |

The attacker may control task text, tool arguments, a repository's files, a Skill in a
lower-trust source, and a local process able to send stdio requests to its own child.
The attacker cannot obtain a network endpoint because R2 creates none, cannot alter
the trusted launch configuration, and has no privileged OS or same-user credential
access beyond the host's normal local authority. Those non-capabilities lower, but do
not eliminate, local prompt-injection and boundary-bypass risk.

| Abuse path | Risk | Required mitigation | Residual risk |
| --- | --- | --- | --- |
| Malicious `AGENTS.md`, README, or comments tell Nexus to broaden permissions | High | Fixed policy outranks content; allowlisted governance files only; no execution tools; redact output. | Planning quality may be degraded, not authority. |
| Caller supplies traversal, sibling root, UNC, or device path | High | No root/path input; opaque allowlist IDs; strict canonical checks. | Misconfigured trusted allowlist. |
| Junction/symlink race escapes a registered root | High | Reject every reparse point; verify parent/target before and after open; fail closed. | Platform-specific race bugs require adversarial tests. |
| Poisoned/duplicate Skill becomes selected | High | Existing provenance/duplicate controls plus guarded path/hash/size verification; fail closed on ambiguous load evidence. | Trusted upstream/local checkout compromise. |
| Skill or request causes shell/Agent/install/network action | Critical | No such tool or code path; prohibit `execute_route`; dependency allowlist; no network listener/client. | Host may separately choose actions outside R2. |
| Raw Skill/context/secret leaks in result or log | High | Central redactor; fixed output schema; response-size cap; stderr allowlist. | Metadata can reveal limited capability names. |
| Oversized request/context/index exhausts process | Medium | Input/file/count/result caps, deadline, no background task, rate limit per process. | Local host can restart server. |
| Malformed JSON/MCP state confusion | Medium | SDK lifecycle handling; JSON Schema; no requests before initialized; protocol/tool error split. | Client incompatibility returns fail-closed error. |
| Host treats plan as authorization to execute | High | Documentation, tool description, schema and test prove advisory plan only; no command fields. | A malicious/unmodified host remains outside R2 trust boundary. |

### Testable security invariants

1. The process binds no socket and makes no network request for any R2 tool.
2. stdout contains only MCP JSON-RPC; diagnostics never appear there.
3. No tool accepts an arbitrary filesystem root, file, command, environment, Skill,
   or Agent name.
4. Every accepted workspace ID resolves to exactly one configured local root.
5. Traversal, sibling escape, UNC/device path, symlink, junction, and reparse-point
   candidates fail closed.
6. `none` reads zero project files; `governance` never reads outside the allowlist.
7. Binary, invalid encoding, secret-named, secret-pattern, and over-budget files
   cannot reach planning input or output.
8. Only selected canonical Skills are loaded; their hash/length/path guard evidence
   must validate exactly once.
9. A failed or ambiguous Skill load produces no success claim.
10. Responses and stderr never contain raw Skills, raw context, secrets, absolute
    paths, hidden reasoning, tracebacks, or environment values.
11. No `subprocess`, Skill hook, install/update, Agent spawn, or host-execution API
    is reachable from request-controlled data.
12. R2 creates no persistent plan/cache/log state by default.
13. A timeout cancels/returns error and does not continue work in the background.
14. Existing V1.1/V1.2/R1 tests and R1 `--handoff` contract remain unchanged.
15. AI Coordinator remains untouched and continues native/R1 fallback behavior.

## Dependency and future code organization

Use the official **`mcp` Python SDK** from the Model Context Protocol Python SDK as
the sole new runtime dependency. Its exact release must be selected and hash-pinned
in the implementation change after verifying the then-current supported API and
license; this design intentionally does not invent an unverified version number.
The SDK is preferable to a handwritten protocol implementation because lifecycle,
JSON-RPC, schema exposure, cancellation, and stdio correctness are protocol-sensitive.
No web framework, HTTP client, database, vector store, DeerFlow dependency, or
Agent-runtime dependency is justified.

Proposed additive layout:

```text
ash/
  mcp/
    __init__.py              # bounded public server factory
    server.py                # stdio SDK wiring; tools only
    schemas.py               # strict input/output models and error codes
    adapter.py               # calls existing V1.2 plan/load/validate interfaces
    authorization.py         # immutable workspace allowlist and Windows guards
    context.py               # guarded, bounded governance-context reader
    redaction.py             # one outbound allowlist/redactor
    telemetry.py             # disabled-by-default safe stderr events
scripts/
  nexus_mcp.py               # explicit local stdio entry point
tests/
  test_mcp_protocol.py
  test_mcp_authorization.py
  test_mcp_context_security.py
  test_mcp_redaction.py
  test_mcp_boundaries.py
```

`ash.v2`, `ash.discovery`, `ash.execution`, and `scripts/hub.py` remain the source of
truth for planning/discovery/loader behavior. R2 must not copy ranking, selection,
fallback, or validation code. A narrowly extended guarded selected-loader option may
be added with default-compatible behavior only after direct regression tests prove
that R1 remains byte/semantic compatible.

## Implementation acceptance matrix

| Area | Required proof |
| --- | --- |
| Protocol | initialize/version negotiation, initialized gate, `tools/list`, all tool schemas, unknown method/tool, malformed JSON, graceful stdin close, stdout purity. |
| Functional | health; metadata-only discovery; backend plan; document plan; no-Skill native fallback; exact selected load evidence; capability count/result caps. |
| Authorization | unknown ID, traversal attempt, sibling root, UNC/device path, root ancestor, symlink/junction/reparse-point escape, canonical/case equivalence, TOCTOU failure. |
| Context | none mode; governance allowlist; file/depth/byte caps; binary/polyglot; invalid UTF-8; secret-name/pattern rejection; malicious governance instruction remains data. |
| Skill integrity | duplicate/shadowed canonical selection; equal-authority conflict; missing/unreadable/oversized selected Skill; hash/size mismatch; malicious Skill text cannot grant authority. |
| Boundary | monkeypatch/prove no subprocess, no shell, no network listener/client, no Skill install/update, no Agent spawning, no persistent state, no arbitrary file read. |
| Redaction | sentinels in task/context/rule/Skill/environment never appear in `structuredContent`, text content, error, or stderr; no absolute paths/hidden reasoning. |
| Performance | task/context/registry/response caps; timeout/cancellation; repeated malformed requests; bounded safe rate policy. |
| Compatibility | full existing Nexus test suite, final smoke, manifest integrity, R1 handoff regression, V1.1 compatibility checks; AI Coordinator R1 tests unchanged. |
| Local host | one explicit configured local Codex MCP test with a disposable approved root; no network port; host observes structured result and native fallback. |

## Bounded implementation sequence

1. **R2.1 Protocol skeleton:** add pinned `mcp`, stdio factory, lifecycle and
   `health`; prove stdout purity and no port.
2. **R2.2 Adapter:** add `discover_capabilities` and `plan_task` over existing core;
   establish schemas, stateless results, core/R1 regressions.
3. **R2.3 Authorization/context:** add immutable workspace configuration and
   Windows reparse-safe context reader; pass adversarial filesystem cases.
4. **R2.4 Redaction/bounds:** centralize outbound allowlist, telemetry, limits,
   timeout/cancellation, and Skill-load guard.
5. **R2.5 Adversarial acceptance:** complete the matrix, manifest/integrity scan,
   and dependency review.
6. **R2.6 Local Codex integration test:** add one explicit local config only after
   server acceptance. Prove a host invocation; do not change AI Coordinator.
7. **R2.7 Freeze:** separate review/merge/tag decision after all evidence passes.

Each stage is additive, independently testable, and reversible by removing the R2
server configuration and code branch. No stage authorizes R3 work.

## R1 coexistence and R3 boundary

R1 `python scripts/nexus.py plan ... --handoff` remains supported and stateless.
R2 neither migrates nor modifies AI Coordinator; a future host may choose R1, a
configured R2 tool, or native Codex fallback according to a separately approved
integration policy. A failed/unavailable R2 server must not break R1 or native use.

R2 is not ChatGPT integration. It creates no remote endpoint, tunnel, OAuth flow,
ChatGPT App, plugin UI, custom `@Nexus` behavior, remote credential exchange, or
network listener. Those belong to a separately scoped R3 architecture/security review.

## Defect-first review and revisions

This design review found and corrected five risks in the earlier integration concept:

1. **Cached `explain_selection` and `get_loaded_skill` were unnecessary state and
   disclosure surfaces.** R2 omits them; `plan_task` has a safe summary.
2. **Host-provided path authorization was too broad.** R2 accepts only configured
   opaque workspace IDs and never returns absolute paths.
3. **Existing V1.2 fixed-root context handling is not an MCP authorization control.**
   R2 adds a reparse-safe guard/context reader before core invocation.
4. **A plan envelope could accidentally resemble execution authority.** The schema
   has no command/artifact/approval fields, and boundary tests prohibit execution.
5. **Tool output/logs could leak untrusted content.** Central output allowlisting,
   sentinel tests, stderr-only telemetry, and no default retention are mandatory.

The resulting design is simpler: three tools, no cache, no path parameter, no raw
content capability, no network, and no second planner.

## Implementation readiness

**Ready for implementation review, not implementation.** The main remaining
implementation-time checks are the exact compatible `mcp` SDK release/hash, Windows
reparse-point behavior in the target Python runtime, and a disposable local Codex
MCP integration test. None requires an architecture change if the invariants and
acceptance matrix pass. A failure in any of those areas blocks R2 release rather than
weakening a boundary.
