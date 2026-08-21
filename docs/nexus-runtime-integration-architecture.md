# Nexus Runtime Integration Architecture

**Product:** Nexus — Adaptive AI Capability Hub
**Status:** Design and feasibility only; not an implementation specification
**Core baseline:** `v1.2-final` at `44458d13a7f4240d34fa58c32e92640e7291a14a`
**Last platform review:** 2026-08-21

## 1. Executive Summary

Nexus V1.2 already makes a bounded, auditable decision: it discovers local
Skills, reads a bounded project context, applies rules, selects the smallest
sufficient set, loads selected `SKILL.md` files, and emits a validation plan.
It deliberately does **not** execute arbitrary natural-language Skill workflows.

The recommended near-term architecture is **Architecture A+**: a lightweight
Nexus activation instruction in a Codex project's `AGENTS.md`, backed by the
existing local `python scripts/nexus.py plan` command. It is the smallest
reliable way to remove the need for the user to type that command on every
substantial task without pretending that Nexus can intercept every Codex turn.

The next optional layer is **R2: a local, read/plan-only MCP adapter** for
Codex. It should be a thin stdio adapter over the existing V1.2 core, not a
second router and not an execution engine. A ChatGPT `@Nexus` experience is a
separate, platform-dependent R3. It must not be promised for this Windows
machine until the account/workspace can use a documented remote custom MCP app.

## 2. Current Nexus V1.2 Interface

The frozen core was inspected directly. Its relevant contracts are:

| Surface | Current behavior | Host responsibility after it returns |
| --- | --- | --- |
| `scripts/nexus.py` | Compatibility alias that delegates to `hub.py`. | Invoke it explicitly or through a future host adapter. |
| `scripts/hub.py plan "<task>"` | Builds a fresh V2 catalog, creates a plan, loads only selected Skills, validates plan loading, and can write a packet. | Execute the selected instructions and validation activities. |
| `ash.v2.plan_task` | Produces `ExecutionPlan` from task, registry, root, bounded context, rules, and sources. | Treat the plan as a decision contract, not an automatic command authority. |
| `ash.v2.load_plan_skills` | Reuses the V1 loader for **selected** Skills only. | Follow loaded instructions with the host's authorized tools. |
| `ash.v2.validate_plan` | Validates coverage, duplicate selection, and selected-Skill loading. | Perform task-result validation; report failures. |
| `write_plan_packet` | Writes serializable evidence with paths/hashes and `product_identity`; project-context content is redacted. | Retain or display only under local policy. |

V1.2 project-context handling is bounded and read-only: it recognizes a small
set of root-level governing files and task-named files, rejects root escapes,
binary/non-UTF-8 and secret-looking files, records soft-budget expansion, and
enforces hard ceilings. Rules are ordered and equal-priority conflicts block
selection. Native Codex fallback is explicit when a required capability is not
covered.

## 3. User Goals

The intended daily interaction is natural language such as “Improve this React
dashboard and verify accessibility,” not a remembered Python command. The
integration must retain these V1.2 truths:

- planning is local and auditable;
- Skill discovery is not automatic execution authority;
- project rules constrain selection;
- selected instructions, not every candidate's full content, are loaded;
- advisory Agents are never delegated by Nexus;
- unavailable Nexus degrades visibly to normal host capability rather than
  blocking an otherwise safe task.

## 4. Codex Daily Usage Architecture

```text
User task in a Codex project
        |
        v
lightweight relevance gate (host instruction; no full scan yet)
        |-- trivial / conversational --> normal Codex handling
        |
        `-- Nexus-relevant --> Nexus planner (local process or R2 tool)
                                  |
                                  v
                   bounded project context + rules + registry
                                  |
                                  v
                     NexusPlanEnvelope, selected Skill loads
                                  |
                                  v
                       Host Codex executes authorized work
                                  |
                                  v
                     task-specific validation + concise report
```

The gate belongs to the host integration layer. V1.2 Core remains a planner;
it does not become a global interceptor, daemon, or autonomous executor.

### Integration-option assessment

| Option | Feasibility and reliability | Main risk / limitation | Decision |
| --- | --- | --- | --- |
| A. Explicit Nexus Skill | Codex can discover local Skills, but a Nexus Skill would rely on host selection and can recursively route itself unless it has a dedicated exclusion contract. | Adds a second activation policy and is not a guaranteed per-turn hook. | Defer; do not make Nexus a self-routing Skill in R1. |
| B. Project `AGENTS.md` instruction | Practical, local, and naturally receives the active project context when Codex reads project instructions. | Per-project setup; host instruction following is near-automatic rather than an interceptor. | **Recommend for R1.** |
| C. User-level Codex instruction/bootstrap | A user-level Codex instruction file exists in this environment, so a bootstrap is conceivable. | Global triggering can consult Nexus for trivial tasks; portability and instruction precedence need explicit testing. | Defer until R1 gate metrics justify it. |
| D. Wrapper / launcher | Can prepare environment variables, a root registration, or a health check before Codex starts. | Does not prove influence over every later turn and is platform/startup fragile. | Do not use as the primary integration mechanism. |
| E. Local MCP/tool adapter | The current Codex configuration already has an `mcp_servers` entry, so structured local tools are feasible in principle. | Requires new adapter code, root authorization, tool schemas, and adversarial tests. | **Recommend for R2** after R1 evidence. |

## 5. Activation Policy

The host SHOULD consult Nexus once per user task when any condition below is
true:

- a code feature, refactor, bug diagnosis, test/regression request, or security review;
- document, spreadsheet, PDF, PowerPoint, or other artifact work;
- research requiring current evidence or citations;
- a multi-step task, a task mentioning files/project rules, or one likely to
  need an installed Skill.

The host MAY skip Nexus for a simple factual question, casual conversation,
one-line calculation, trivial explanation, or a request with no project,
artifact, file, or capability-routing relevance.

The R1 instruction must say **consult at most once before planning/execution**;
it must not instruct Codex to call Nexus again because Nexus itself selected a
Skill. This prevents recursive self-routing. An explicit user request such as
“do not use Nexus for this task” is a higher-priority opt-out.

## 6. Nexus ↔ Host Contract

Nexus owns planning; the host owns execution authority.

| Nexus responsibilities | Host Codex responsibilities |
| --- | --- |
| Build/validate `TaskProfile`; inspect bounded context; apply rules. | Decide whether its available tools and authority can execute each step. |
| Discover, deduplicate, rank, select, and load only selected Skills. | Follow selected Skill instructions using normal authorized file/tool operations. |
| Emit steps, validation checks, fallback, provenance, and advisory Agents. | Run applicable validation, summarize result, and report blockers. |
| Refuse invalid roots/conflicting rules and avoid arbitrary command execution. | Never treat the plan or Skill prose as permission to exceed user/project/system authority. |

### NexusPlanEnvelope

The future adapter should expose a versioned envelope, derived from the
existing `ExecutionPlan`, rather than inventing a second decision model.

```json
{
  "schema_version": "nexus.plan-envelope.v1",
  "plan_id": "uuid",
  "product": {"name": "Nexus", "subtitle": "Adaptive AI Capability Hub"},
  "project": {"root_id": "registered-workspace-id", "local_path": "same-user local transport only"},
  "task_profile": {"task_type": "backend", "required_capabilities": ["backend", "testing"]},
  "rules": {"applied": ["..."], "conflicts": []},
  "selected_skills": [{"name": "...", "local_path": "same-user local transport only", "content_hash": "...", "loaded": true}],
  "execution_steps": [{"id": "step-1", "skill": "...", "success_criteria": "..."}],
  "validation_checks": [{"kind": "targeted_test", "reason": "..."}],
  "prohibited_operations": ["automatic_install", "automatic_agent_delegation"],
  "advisory_agents": [{"name": "...", "status": "advisory_only"}],
  "fallback": {"status": "not_needed"}
}
```

`local_path` fields are appropriate only for a same-user local host. A remote
projection receives a root ID, Skill name, hash, and summary, but omits every
local path. The envelope must not include chain-of-thought, full unselected
Skill content, credentials, or raw project context.

## 7. MCP Design

R2 is a **local stdio MCP planning server** launched by the same local Codex
environment that owns the approved workspace. The current user configuration
already contains an `mcp_servers` entry, which verifies local MCP configuration
exists in this environment; it does not prove that a Nexus server is registered
or that every Codex surface will call it automatically.

```text
Codex (same user/session)
  -> local stdio Nexus MCP adapter
       -> existing V1.2 discovery + planner + selected-Skill loader
       -> structured read/plan response
  -> Codex executes separately with its own authority
```

The adapter MUST be thin: it calls Nexus Core and returns its normal evidence.
It must not maintain a duplicate index, add an embeddings/vector store, install
Skills, spawn Agents, or expose arbitrary shell execution.

## 8. Proposed MCP Tools

| Tool | Purpose and input | Output / side effects | Raw Skill content / host execution |
| --- | --- | --- | --- |
| `nexus.plan_task` | `task`, `workspace_id`, optional bounded planning options. | `NexusPlanEnvelope`; local read-only planning and selected-Skill load only. | No full content by default; host executes. |
| `nexus.discover_capabilities` | `workspace_id`, optional query. | Metadata-only available/canonical capabilities and provenance. | Never loads all `SKILL.md`; host executes nothing. |
| `nexus.explain_selection` | `plan_id` from a short-lived local cache. | Selected/rejected rationale, applied rules, fallback. | No raw context/Skill content; no execution. |
| `nexus.get_project_rules` | `workspace_id`. | Rule identifiers, provenance, conflict state, hashes. | Redact rule body by default; no execution. |
| `nexus.get_loaded_skill` | `plan_id`, selected Skill ID, `include_content=false`. | Path, hash, size and load status. | R2 MUST reject `include_content=true`; host already has local Skill access. |
| `nexus.validate_result` | `plan_id`, host-provided validation observations. | Deterministic coverage/step-status summary. | Cannot run commands; host remains executor. |
| `nexus.health` | No project input. | Version, core tag, supported tools, allowed workspace IDs. | No execution or content disclosure. |

All tools are read/plan focused. `validate_result` validates declared evidence;
it does not convert user-supplied text into a claim that tests were run.

## 9. ChatGPT / @Nexus Feasibility

### Verified platform facts

- The OpenAI developer site presents plugins as a way to extend ChatGPT and
  Codex with Skills, MCP servers, and optional UI. [OpenAI Developers](https://developers.openai.com/)
- OpenAI's current ChatGPT developer-mode documentation says custom MCP apps
  are configured with a server endpoint and that ChatGPT does **not** connect
  directly to a local MCP server; private/on-premises/developer-machine servers
  require Secure MCP Tunnel. [Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt)
- The same documentation makes availability role- and plan-dependent; custom
  app publishing is an administrator/owner-controlled workspace capability.
  [Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt)
- The Apps SDK is an MCP-based preview surface for building ChatGPT apps.
  [Build with the Apps SDK](https://help.openai.com/en/articles/12515353-build-with-the-apps-sdk)

### Consequences

`@Nexus` is **unsupported/unknown for this account and desktop surface** until
the user verifies an eligible ChatGPT plan, workspace role, Developer Mode, and
custom-app availability. The documented closest UX is to enable/select a custom
app and refer to it in a ChatGPT conversation where the workspace permits it;
the exact `@Nexus` affordance must not be promised for a custom Nexus app.

ChatGPT cannot directly read `D:\chatgpt\安装skills\adaptive-skills-hub` merely
because it exists on this machine. A local Nexus MCP is useful for local Codex,
but does not by itself make Nexus reachable from ChatGPT.

## 10. Local vs Remote MCP

| Dimension | Local MCP for Codex | Remote/hosted MCP for ChatGPT |
| --- | --- | --- |
| Local project and Skill access | Strong, with same-user workspace restrictions. | None by default; requires explicitly supplied/synchronized data. |
| Privacy | Best default; no network bridge. | Requires auth, service hardening, data policy, and remote retention decisions. |
| Reliability | Works offline with local Codex/Python. | Depends on network, endpoint availability, account/workspace configuration. |
| ChatGPT reachability | Not direct. | Potentially supported through documented custom MCP/app configuration. |
| Attack surface | Local process/user boundary. | Internet or tunnel boundary plus OAuth/authz and tenant isolation. |

**Recommendation:** local MCP is sufficient for R2 and should precede any
remote service. Do not build a tunnel merely to mimic `@Nexus`. Reconsider a
remote adapter only when an eligible ChatGPT workspace has a concrete use case
and can accept the required remote authorization and data boundary.

## 11. Security Model

### Assets and boundaries

```text
Untrusted user task / repository text
        |  (content, never authority)
        v
Nexus context and rule boundary
        |  (bounded, schema-checked plan)
        v
Local selected Skill files ----> Host Codex execution boundary
        |                               |
        `---- hashes/provenance --------'-- authorized tools and validation
```

Assets are workspace files, project rules, local Skill content, selected-Skill
hashes/provenance, host credentials, and execution authority. The initial
attacker model includes a malicious repository/README, a path-traversal caller,
a local untrusted process, a compromised remote MCP caller, and a prompt trying
to turn planning output into shell authority.

| Abuse path | Initial control |
| --- | --- |
| Prompt injection in project/Skill/reference text | Keep content separate from rules; accept only recognized rule files; schema validate tool input/output; do not execute prose. |
| Arbitrary filesystem root | Resolve/canonicalize root, reject traversal/reparse escapes, use registered workspace IDs and per-root allowlists. |
| Skill exfiltration | Return metadata/hashes by default; never offer bulk or arbitrary raw `SKILL.md` retrieval. |
| Remote caller controls local machine | R2 has no remote listener; any R3 endpoint needs authenticated identity, explicit root authorization, read-only tools first, rate limits, audit logs, and user approval for writes. |
| Command injection / auto-install | No execute-shell MCP tool; retain V1.2 prohibitions on automatic installation and arbitrary command execution. |
| Cross-project leakage | Bind plan ID and cache to workspace ID; never accept a path from one project to read another. |
| Credential leakage | Do not read config secrets, environment variables, caches, or application credentials into plan/diagnostic payloads. |

The security threat-model guidance materially changes the recommendation: R2
starts read/plan-only, remote access is deferred, and untrusted content never
becomes instruction authority.

## 12. Project Root / Permissions

R1 passes the Codex current workspace root to the existing CLI. R2 should
prefer a `workspace_id` registered at MCP startup over an arbitrary `path`.

1. The local launcher/config registers one or more approved canonical roots.
2. The tool accepts only those IDs; an optional path is accepted only when it
   resolves beneath the corresponding approved root.
3. Junctions/symlinks/reparse points escaping the root are rejected.
4. Nexus retains its existing bounded file policy; the adapter cannot widen it.
5. A request for another root returns `project_root_not_allowed`, not a scan.

For a future remote R3, the client must not pass `D:` paths at all. It either
uses an explicitly authorized secure bridge session or submits a deliberately
scoped, user-approved project bundle; both are separate designs requiring
privacy review.

## 13. Installation Model

Future installation is a separate, explicit operation—not background behavior.

| Stage | Future installer responsibility | Explicit non-goal |
| --- | --- | --- |
| R1 | Verify Python/Nexus path; offer a project `AGENTS.md` snippet; run health check; remove only what it created. | Global interception or overwrite of project instructions. |
| R2 | Register a local stdio MCP config with approved workspace roots; verify `health`; uninstall cleanly. | Remote exposure, shell execution, or automatic Skill updates. |
| R3 | Configure documented remote MCP/app endpoint, identity, workspace approval, and privacy notice. | Direct D: access or silent tunneling. |

## 14. Daily Usage UX

| UX | Availability | User experience |
| --- | --- | --- |
| Codex explicit | Available now. | “Use Nexus and fix this bug.” |
| Codex implicit via R1 project instruction | Practical now after deliberate project setup. | “Fix this bug.” The host consults Nexus only when the gate applies. |
| CLI | Available now. | `python scripts/nexus.py plan "Fix this bug."` |
| Local MCP | R2 design only. | Host calls `nexus.plan_task` with the active registered workspace. |
| ChatGPT custom app | R3, account/workspace dependent. | Select/refer to an enabled Nexus app; exact `@Nexus` is unknown. |

## 15. Failure and Fallback

| Failure | Required behavior |
| --- | --- |
| Nexus Core/CLI unavailable | Host continues with native capability and reports `Nexus unavailable`; no silent claim that Nexus was consulted. |
| MCP unavailable | R1 command fallback if authorized; otherwise native host capability. |
| Planner error or invalid envelope | Return structured error/plan ID; do not execute inferred Skills. |
| Root not allowed | Refuse context access and ask for an approved workspace; do not widen permissions. |
| Skill missing/malformed | Preserve Nexus's current rejected-candidate evidence and explicit native fallback. |
| Host cannot execute a selected Skill | Report the affected step and use only a compatible host fallback; do not invent tool access. |
| ChatGPT cannot reach Nexus | State remote integration unavailable; do not tunnel or expose local files automatically. |
| R1 instruction absent | Normal Codex behavior; no claim of automatic Nexus coverage. |

## 16. Observability

The host should show concise, user-facing status without exposing hidden
reasoning:

```text
Nexus consulted: yes
Plan ID: <uuid>
Skills: evidence-driven-backend-debugging, regression-first-testing
Advisory Agents: none
Validation: targeted regression tests
Fallback: not needed
```

R2 diagnostics may expose `health`, core/tag version, allowed workspace IDs,
tool version, plan ID, selected Skill names/hashes, validation status, and
structured error code. They must not log raw context, credentials, or
chain-of-thought. A future remote service additionally needs request identity,
workspace authorization decision, audit event ID, rate-limit result, and an
opaque trace ID.

## 17. Architecture Comparison

| Architecture | Ease / reliability | Local access and privacy | `@Nexus` feasibility | Complexity / maintenance | Verdict |
| --- | --- | --- | --- | --- | --- |
| A. Codex Skill + project instructions | High after one project setup; instruction adherence is host-mediated, not an interceptor. | Strong local access; no network. | None. | Lowest. | Recommended R1, but start with instructions rather than a self-routing Skill. |
| B. Codex integration + local Nexus MCP | Structured and auditable; requires supported local MCP registration. | Strong with workspace allowlists. | None by itself. | Moderate. | Recommended R2 after R1 evidence. |
| C. Local Nexus + remote/plugin bridge | Variable; platform/plan/network dependent. | Weakest unless heavily constrained. | Possible only through supported custom app/plugin mechanics; exact mention UX unknown. | Highest. | Defer to R3; do not build preemptively. |

## 18. Recommended Architecture

Adopt **A+ then B**:

1. R1: project-local activation instruction with a strict relevance gate and
   the existing Nexus CLI.
2. Measure missed/over-triggered tasks, user friction, and plan usefulness.
3. R2: a thin local stdio MCP planning adapter only if structured tool calls
   materially improve daily usage.
4. R3: evaluate remote ChatGPT app/MCP only after account/workspace eligibility
   and a justified remote use case are verified.

This is intentionally sequential, not a multi-Agent mesh. The architecture
Agent guidance was applied by using explicit contracts, least privilege,
bounded fallback, and observable state rather than adding autonomous agents.

## 19. Runtime Integration R1

**Goal:** Make normal, substantial Codex project tasks near-automatic without a
global launcher.

- Install an opt-in project instruction that applies the activation policy.
- It invokes `nexus.py plan` at most once when relevant and passes the current
  project root.
- Host reads the returned concise plan/evidence, follows selected Skills, and
  runs validation.
- User can explicitly opt out per task.

R1 requires no MCP server, remote hosting, plugin, or new Nexus Core behavior.

## 20. Runtime Integration R2

**Goal:** Replace the host shell invocation with a structured local tool call.

- Local stdio server, same user/session, registered approved workspace IDs.
- Implement `health`, `plan_task`, `discover_capabilities`, and
  `explain_selection` first.
- Keep `get_loaded_skill` metadata-only and omit `validate_result` until there
  is a clear host evidence schema.
- Test failure modes, injection, root isolation, and no-execute guarantees
  before enabling it for everyday work.

## 21. Runtime Integration R3

**Goal:** Offer a supported ChatGPT app/plugin experience if the target account
and workspace genuinely support it.

- First verify Developer Mode/custom app eligibility and the exact ChatGPT
  surface, role, plan, and app invocation UX.
- Use a remote MCP endpoint or officially supported secure tunnel; never assume
  direct local D: access.
- Begin with metadata/plan tools and explicit user confirmation for any future
  write capability.
- Perform separate remote authentication, privacy, audit, and abuse testing.

## 22. Testing Strategy

R1 tests should cover the activation gate: substantial code/artifact/research
tasks consult Nexus once; trivial tasks do not; explicit opt-out wins; project
rules are honored; unavailable CLI visibly degrades.

R2 requires at least 20 representative cases before general use, including
allowed/disallowed roots, symlink escapes, malformed request schema, prompt
injection in README/Skill text, duplicate Skills, missing/malformed selected
Skill, rule conflict, unsupported capability, no raw Skill-content leak, no
shell/action tool, and plan/result observability. Run V1.1 and V1.2 regression
suites unchanged against every adapter release.

R3 additionally requires authentication/authorization, cross-project isolation,
remote outage, replay/rate-limit, tunnel exposure, data-retention, consent, and
workspace role tests. No write action is in the initial R3 acceptance set.

## 23. Acceptance Criteria

An integration layer is acceptable only when it proves:

- `v1.2-final` Core selection, rule, loading, and fallback behavior remains unchanged;
- the activation gate is observable and avoids repeated/re-entrant planning;
- every request has an approved workspace root and bounded context;
- planning works with Nexus unavailable/malformed-Skill/fallback states;
- tools disclose selected Skill metadata and validation honestly;
- no tool offers arbitrary shell execution, installation, update, or Agent delegation;
- V1.1/V1.2 regression and integration-specific adversarial tests pass;
- remote use, if proposed, has documented platform support and explicit authz/privacy controls.

## 24. Deployment / Rollback

R1 deploys as an opt-in project instruction. Rollback is removing the exact
Nexus block the installer added; normal Codex behavior resumes.

R2 deploys disabled by default, then to one approved workspace root. Rollback
is unregistering the MCP server/config entry and clearing only its own
short-lived plan cache. It must not remove Skills or modify Nexus Core.

R3 needs a separate change approval. Rollback disables the remote app/action in
the workspace before endpoint retirement, preserving audit evidence according
to the approved retention policy.

## 25. Platform Limitations

- Codex instruction following is not a guaranteed all-turn interception hook;
  R1 is near-automatic, not invisible middleware.
- This environment proves an existing local MCP configuration, not that Nexus
  is registered or that every Codex client/surface exposes the same tools.
- Official ChatGPT documentation supports custom remote MCP/apps only subject
  to product plan, workspace role, and rollout; this account's eligibility was
  not established.
- Official documentation does not establish that a custom app will have an
  exact `@Nexus` mention affordance in this desktop session.
- ChatGPT does not directly access a local Windows D: project or local MCP
  server; remote/tunnel designs require separate authorization and security work.

## 26. Open Questions

1. Which Codex project-instruction mechanism is preferred for R1 in the user's
   normal workspaces, and what wording has acceptable false-positive rate?
2. Should R2 cache plans in memory only, or retain redacted local evidence with
   a defined retention policy?
3. Which roots may be registered for R2, and should each need user confirmation?
4. Does the target ChatGPT account/workspace expose Developer Mode/custom MCP
   apps, and which plan/role governs publication?
5. Is a future ChatGPT use case worth a remote privacy boundary, or is local
   Codex sufficient?

## 27. Final Recommendation

1. **Can Nexus be automatic in Codex?** Near-automatically, yes: an opt-in
   project instruction can make Codex consult Nexus for gated substantial tasks;
   it is not a guaranteed global interceptor.
2. **Safest approach?** R1 project instructions first, then a local read/plan
   MCP adapter only after measuring friction and false triggers.
3. **ChatGPT plugin/MCP app today?** Platform support exists conditionally for
   custom remote MCP/apps, but eligibility and exact UX for this account are
   unverified; do not claim it is available now.
4. **`@Nexus`?** Unsupported/unknown as an exact custom-app affordance. The
   closest documented UX is selecting or referring to an enabled custom app.
5. **Can ChatGPT access local D: directly?** No supported direct local-MCP/D:
   assumption; remote endpoint or officially supported secure bridge is needed.
6. **Is local MCP sufficient?** Yes for local Codex R2; it is the preferred
   path for private project access.
7. **Is a tunnel/remote service required?** Only for a justified ChatGPT R3;
   not for R1/R2 and not recommended yet.
8. **Implement first?** R1 activation policy and project instruction prototype.
9. **Defer?** Remote bridge, ChatGPT app/plugin, write tools, global launcher,
   automatic activation hooks, and any multi-Agent runtime.
10. **Major risks?** Prompt injection, root escape/cross-project reads, raw
    Skill exfiltration, remote caller control of local files, credential leakage,
    command injection, and unobservable over-triggering.

Nexus V1.2 remains a frozen Core. Runtime Integration is a thin, separately
versioned host layer around it, not a rewrite of it.
