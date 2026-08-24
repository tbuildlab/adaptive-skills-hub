# Nexus

## Adaptive AI Capability Hub

Nexus is the user-facing name of the Adaptive Skills Hub system. It is a
Codex-first meta-skill for discovering, selecting, loading, chaining, and
executing relevant Skills instead of merely recommending them. V1.1 remains
frozen; V1.2 is an additive, explicit capability-planning layer.

Nexus understands the task, reads project rules, identifies required
capabilities, selects relevant Skills, can recommend advisory Agents, creates
an execution/validation plan, and preserves provenance and evidence. It does
not claim automatic ChatGPT integration. Runtime R2 adds an explicit,
locally configured stdio MCP planning interface; it does not create an automatic
or remote Codex/ChatGPT integration.

## V1.1 capability

Task -> Discover -> Rank -> Load -> Execute -> Validate -> Report

Nexus separately indexes:
- skills
- agents
- reference repositories
- frameworks

## Local use

The source tree is location-independent. In a
Codex session that has loaded this Skill, run the router and then carry out the task:

```powershell
# Compatible Adaptive Skills Hub entry point
python scripts/hub.py rescan
python scripts/hub.py route "Improve this React dashboard UI."
python scripts/hub.py run "Improve this React dashboard UI." --packet state/example-packet.json
```

The Nexus-friendly alias preserves the same commands and behavior:

```powershell
python scripts/nexus.py plan "Fix this API bug and add regression tests."
```

The skill's description is intentionally broad enough that Codex can also select it automatically when capability routing is useful.

For the Windows GitHub Release candidate and a no-clone installation path, see
[GitHub Release installation](docs/github-release-installation.md). It is
separate from the frozen Core tags and does not package local runtime state.
For the private RC6 Desktop flow, the release installer prepares a Personal
marketplace **source** only. The required final host action is
`ChatGPT Desktop → Plugins → Personal → Nexus → + Install`; start a new chat
before expecting `@Nexus`. Nexus never writes Desktop's plugin cache,
enablement state, or `~/.codex/config.toml`.

`route` uses metadata only. `run` then fully reads each selected Skill's `SKILL.md`.
For normal natural-language Skills, Codex follows those loaded instructions to do the
work. Optional local `hub_command` arrays can automate deterministic steps only when
the caller additionally passes `--allow-skill-commands`; execution never uses a shell.

## First commands

Rescan real local Skills and Agents, then rebuild the combined registry:

```bash
python scripts/hub.py rescan
python scripts/rebuild_registry.py
```

Check upstream revisions safely:

```bash
python scripts/check_updates.py
```

The update check is CHECK-ONLY.

## Adding another source

Edit `sources.json`, append the source, then run:

```bash
python scripts/rebuild_registry.py
```

No rewrite of `SKILL.md` is required.

## Important architecture rule

- Skill = executable workflow/instructions
- Agent = specialist role/process
- Reference = patterns/examples
- Framework = orchestration/runtime
- Project rules = highest-priority local requirements

Do not flatten all of these into one giant prompt.

See [docs/architecture.md](docs/architecture.md) for contracts, safety boundaries, and
the exact rescan/route/run flow. Run `python -m unittest discover -s tests -v` for the
acceptance suite.

The frozen V1.1 evidence snapshot is in
[docs/v1.1-final-baseline.md](docs/v1.1-final-baseline.md).

## V1.2 explicit planning

V1.2 does not replace the V1.1 `route` or `run` path. It makes the decision
before handoff explicit and auditable:

```text
TaskProfile -> bounded Project Context -> Rules -> Capability Requirements
-> hard filters -> deterministic ranking -> greedy minimal selection
-> ExecutionPlan -> selected SKILL.md loading -> ValidationPlan -> evidence
```

Run Nexus from the existing Hub root (or pass a project path):

```powershell
python scripts/nexus.py plan "Fix an API HTTP 500 and add regression tests." --project D:\work\my-project
python scripts/hub.py plan "Research evidence and prepare an editable Word report." --project D:\work\my-project
python scripts/hub.py plan "Fix an API HTTP 500 and add regression tests." --project D:\work\my-project --packet state\api-plan.json
python scripts/hub.py plan "Create an editable PowerPoint presentation." --no-state
```

`plan` is the V1.2 MUST-HAVE entry point. It does not execute arbitrary Skill
prose or command hooks. It loads only the full `SKILL.md` files actually
selected by the plan, records their paths and hashes, and emits an honest native
Codex fallback when no installed compatible Skill covers a requirement.

V2 follows `hard filters -> required capability coverage -> deterministic
scoring -> greedy minimal-sufficient selection -> redundancy elimination`.
It deliberately does not use embeddings, vector retrieval, a general optimizer,
automatic Skill installation, or a multi-Agent runtime.

Agents are advisory recommendations only. References and frameworks, including
DeerFlow, remain reference-only and are never promoted to executable Skills.
Project content is bounded evidence; only recognized project-rule files can
contribute project rules, and those rules cannot override system or current-user
constraints.

See [docs/v1.2-usage.md](docs/v1.2-usage.md) for context budgets, evidence
packets, validation, re-planning, safety boundaries, and optional project-level
Codex integration.

## Runtime R4/R5 development layers

R4 and R5 are separate, unmerged development layers over the frozen Core.
R4 supplies a redacted Host-owned Presentations execution handoff; R5 adds at
most one Host-owned, copy-on-write post-validation presentation refinement.
Neither layer lets Nexus execute a Host tool, read/write an artifact, select an
arbitrary replacement Skill, spawn an Agent, or claim Host execution without a
real artifact and validation receipt. See [R4 Host handoff](docs/nexus-runtime-r4-host-handoff.md)
and [R5 adaptive enhancement](docs/nexus-runtime-r5-adaptive-enhancement.md).

Reviewed third-party provenance is kept in
[`config/upstream-source-registry.json`](config/upstream-source-registry.json).
It records pinned sources as locally usable, advisory-only, reference-only,
license-gated, or rejected; it does not auto-install or auto-execute upstream
content. See [Upstream source registry](docs/upstream-source-registry.md).

## Runtime R2 local MCP

Runtime R2 is a separately configured, local stdio-only MCP adapter. Its three
read/plan-only tools are `nexus.health`, `nexus.discover_capabilities`, and
`nexus.plan_task`. It accepts a configured opaque workspace ID rather than a caller
path, uses bounded safe context, returns redacted plan/load evidence, and never
executes a plan. See [docs/nexus-runtime-r2-local-mcp.md](docs/nexus-runtime-r2-local-mcp.md)
for installation, local configuration, security boundaries, and removal.
