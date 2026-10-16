# Nexus

Nexus is a local planning and capability-routing plugin for ChatGPT Desktop and
Codex. It selects suitable Skills, prepares bounded research and validation
plans, and returns evidence for Host-owned work. The Host executes tools,
creates artifacts, verifies results, and controls permissions.

**Stable private release: 0.1.1.** Nexus Roadmap V2 is completed and frozen at
[`nexus-v2-g6-final`](https://github.com/TDY0225/adaptive-skills-hub/tree/nexus-v2-g6-final).
The distribution version is independent of frozen Core tags. This repository
is private and proprietary: share these links only with authorized repository
users. There is no OpenAI public plugin-directory listing or public license grant.

![Official Nexus avatar](assets/brand/nexus/nexus-avatar-500.png)

## Quick Start: Windows x64

1. Sign in to GitHub with repository access and download the six assets from
   [Nexus 0.1.1](https://github.com/TDY0225/adaptive-skills-hub/releases/tag/nexus-0.1.1)
   into one folder. Use the named Windows ZIP asset, not GitHub's automatic
   **Source code** download.
2. Open PowerShell in that folder and run:

   ```powershell
   $projectRoot = Join-Path $env:USERPROFILE 'NexusProjects\MyProject'
   New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null
   $expectedBootstrap = '37d82101a917030e6441abb8e711c57f6bbaa83779561fa2b4997a080d98608f'
   if ((Get-FileHash .\Install-Nexus-0.1.1.ps1 -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedBootstrap) {
     throw 'Nexus bootstrap checksum mismatch'
   }
   powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-Nexus-0.1.1.ps1 `
     -ArchivePath .\Nexus-0.1.1-windows.zip `
     -ChecksumPath .\Nexus-0.1.1-windows.zip.sha256 `
     -WorkspaceRoot $projectRoot -Mode plugin
   ```

   Replace the example workspace with your existing approved project if desired.
   No administrator access, preinstalled Python, Node/npm, API key, or Codex CLI
   is required by the packaged installer. ExecutionPolicy Bypass applies to this
   PowerShell process only. Do not run this fresh-extraction command over an
   already extracted version; see the maintenance instructions below.
3. The installer prepares the personal marketplace source. In Desktop, open
   **Plugins → Personal → Nexus → Install**, then start a new chat and select Nexus.

[Full installation, checksums, upgrade and rollback](docs/github-release-installation.md)
includes exact assets and an optional Codex CLI registration path. Do not edit
the plugin cache manually. A repository clone alone is not a packaged installation.

## Marketplace paths

The release installer generates `~/.agents/plugins/marketplace.json` with
`source.path: ./.codex/plugins/nexus-desktop`, relative to your user profile.
The managed plugin source is `~/.codex/plugins/nexus-desktop`; Desktop/Codex
owns the installed copy. Its plugin ID is `nexus-desktop@personal-marketplace`.

For source developers, the separate repo catalog
[`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) uses
`./plugins/nexus-desktop`, relative to this checkout, and retains the compatibility
key `nexus-local-pilot`. Use the [developer setup guide](docs/nexus-desktop-plugin-pilot.md)
for that path. Choose one installation path; do not enable two Nexus MCP registrations.

## Basic usage

In a new conversation with Nexus enabled, try:

- `Use Nexus to plan a new editable PowerPoint presentation project.`
- `Use Nexus to plan a backend bug fix and its regression checks.`
- `Use Nexus to plan a new website from this complete specification.`

Nexus returns planning and load evidence; these responses do not claim that a
Host executed or validated an artifact. Task suitability and installed trusted
Skill coverage determine whether planning can proceed. Tiny edits and trivial
questions should normally bypass the planner entirely.

## Default Reference Research and expected fallback

| Situation | Expected behavior |
| --- | --- |
| Substantial new project/change | Bounded research first, preferring official docs and comparing multiple GitHub/public references; synthesize before build. |
| Exact specification/stack | Reduced, targeted research for unresolved implementation, compatibility and risk points. |
| Tiny edit or explicit "do not search" | Skip research. |
| Unknown/unclear license | Learn patterns only; no direct code reuse. |
| No suitable reference within budget | Record `NO_SUITABLE_REFERENCE_FOUND`, design an in-scope Nexus-original solution, then PLAN → BUILD → TEST → VERIFY through the Host. |
| Missing trusted capability coverage | Honest `fallback_needed / CAPABILITY_NOT_COVERED`; this is independent of the research decision. |
| Material security/scope/permission conflict | HOLD / Owner decision; do not expand privilege or bypass selection gates. |

`nexus.plan_task` exposes the existing `reference_research` decision in `0.1.1`.
Covered required/reduced/skipped cases return `planned` with no unexpected
fallback. Vague prompts can still lack supported coverage. HOLD is preserved as
`security_conflict_outcome: HOLD_owner_decision`; a blocked plan may retain the
existing `fallback_needed` envelope. Do not relabel either outcome as success.

## Supported scope

Nexus provides bounded planning/routing/Skill selection, evidence and checkpoint
behavior, qualified scoped Website/Report/project workflows, and the existing
Host-owned presentation handoff. Availability depends on the accepted workflow,
trusted Skills, Host bindings, runtime and permissions; it is not universal coverage.

The release does not promote historical experiments into normal capabilities:
`REAL_ADMISSION=NO`, production adapters are `DENY`, G5 remains disabled, N01
is optional high-assurance research `HOLD`, and remote publication recovery is
not qualified. The Host retains tool, artifact, validation, permission, and
publication authority.

Unsupported scope includes arbitrary production adapters/admission, remote or
external publication recovery, generic confidential-corpus qualification,
universal Host isolation, G5 delegation/concurrency, and retired experiments.
Ordinary technical choices remain autonomous within scope; preserve the first
failure, make the smallest repair, and never lower acceptance criteria to PASS.

## Release and project references

- [Stable release and private downloads](https://github.com/TDY0225/adaptive-skills-hub/releases/tag/nexus-0.1.1)
- [Accepted plugin source commit](https://github.com/TDY0225/adaptive-skills-hub/commit/a8dbcc7c10177f20955ed7cce78b6609e663d1aa)
- [Plugin integration/developer guide](docs/nexus-desktop-plugin-pilot.md)
- [Distribution architecture and versioning](docs/github-distribution-architecture.md)
- [Final visual identity and canonical assets](docs/nexus-visual-identity-v1.md)

`nexus-0.1.1` identifies the accepted, already built release commit. Later
documentation/catalog cleanup on `main` does not reissue its immutable assets.

<details>
<summary>Historical architecture and development notes (not current readiness claims)</summary>

The following sections preserve earlier checkpoints. Their dates, remaining-work
statements and experimental capability descriptions are historical; the stable
scope and installation guidance above control normal plugin use.

## Core internal alpha — 2026-10-07

[Core Alpha 2 project guide](docs/nexus-core-alpha2-local-use-v1.md) adds
`python scripts/nexus.py core "<task>" --project "<project>"` preparation with
reusable fixed Python, static-web and evidence profiles. Review the printed
scope/hash, then explicitly approve `core-run`; preparation does not execute.
Local checkpoints, progress and receipts support bounded trusted project work.

[Core MVP scope and local usage](docs/nexus-core-internal-alpha-v1.md) documents
the opt-in `python scripts/nexus.py core-plan` / `core-run` path for reviewed,
byte-bound local Python Skill hooks. It supports sequential execution, verified
output handoff, bounded repair/re-selection, persisted checkpoints and resume.
The existing planning/advisory/MCP interfaces remain non-executing. This is
internal product-core capability: production G2 remains **HOLD** and Positive
Host Binding remains **ABSENT**. The roadmap text below is a historical baseline.

## Historical remaining roadmap — owner accepted 2026-09-13

[Nexus Roadmap V2](docs/nexus-roadmap-v2.md) records the accepted historical plan
after frozen Post-R5 Slice 3C. It defines five required slices and optional/
conditional G5. G1 — Capability Profiles and Executor Conformance is the only
recommended next implementation slice and has **NOT STARTED**. A sequential
Nexus can graduate without G5 when delegation/concurrency does not pass its
enforcement and value gates.

Roadmap V2 targets a model-agnostic capability control plane. The sections below
describe the existing foundation and its historical contracts; accepting the
roadmap does not implement future capabilities or change frozen authority.

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

## Runtime R4/R5 accepted integration layer

The `runtime-r5-final` baseline is the human-accepted, frozen integration
layer over the frozen Core and Desktop Plugin. It remains separate from Core
versioning and does not begin V1.3. R4 supplies a redacted Host-owned
Presentations execution handoff; R5 adds at
most one Host-owned, copy-on-write post-validation presentation refinement and
a bounded assessment of the capability metadata already surfaced by the Host
in the current conversation. This assessment is explicitly incomplete and is
not a ChatGPT Desktop plugin-enumeration API. Host labels are untrusted and are
not reflected by the MCP result; opaque identities preserve correlation.
R5 distinguishes a direct Host tool from a verified Host Skill workflow; a
Skill workflow uses the tools/runtime required by its loaded instructions and
does not require a fictional same-name callable tool.
Neither layer lets Nexus execute a Host tool, read/write an artifact, select an
arbitrary replacement Skill, spawn an Agent, or claim Host execution without a
real artifact and validation receipt. A Host-local receipt binds the inventory
selection to the R4 mapping without giving Nexus execution authority. See [R4 Host handoff](docs/nexus-runtime-r4-host-handoff.md)
and [R5 adaptive enhancement](docs/nexus-runtime-r5-adaptive-enhancement.md),
plus [R5 Host capability inventory](docs/nexus-runtime-r5-host-capability-inventory.md).

Reviewed third-party provenance is kept in
[`config/upstream-source-registry.json`](config/upstream-source-registry.json).
It records pinned sources as locally usable, advisory-only, reference-only,
license-gated, or rejected; it does not auto-install or auto-execute upstream
content. See [Upstream source registry](docs/upstream-source-registry.md).

## Post-R5 capability foundation and runtime bridge (accepted Slice 1)

The accepted Slice 1 layer introduces a data-only heterogeneous capability
model without changing the frozen R5 runtime. It keeps Skills,
Agents, runtimes, harnesses, frameworks, libraries, reference architectures,
example collections, Skill factories, registries, and design resources as
different types with different trust and execution rules. A bounded exact
selector can choose the minimum sufficient set only from already-approved,
currently available, permission-compatible capabilities and classifies every
considered item as creator, enhancer, reviewer, alternative, advisory,
redundant, unavailable, incompatible, or rejected.

The R5 Host limitation remains `current_turn_host_visible_subset` /
`not_globally_enumerated`; this work does not scan private Desktop state or
turn an installed bundle into a callable Host capability. Upstream commit or
content-hash changes re-enter quarantine instead of inheriting approval.

Slice 1 adds the read-only `nexus.route_capabilities` MCP boundary. It accepts
only normalized requirement tokens, rechecks reviewed provenance and local
content integrity, runs the exact minimum-sufficient selector, and emits a
versioned decision envelope with no execution authority. The existing R5 Host
assessment also uses the selector as an internal fail-closed cross-check while
retaining its frozen response and handoff semantics. See [Capability
foundation](docs/nexus-capability-foundation.md), [Runtime integration Slice
1](docs/nexus-post-r5-runtime-integration-slice1.md), and the [bounded Agent
task contract](docs/nexus-agent-runtime-contract.md).

## Post-R5 read-only Skill/MCP Scout (Slice 2 accepted baseline)

The Slice 2 branch adds `nexus.scout_candidates` only at the bounded
`CAPABILITY_NOT_COVERED` boundary. It independently reruns the trusted Slice 1
decision, then may inspect manifest-approved Gap Scan evidence, the fixed
official MCP Registry endpoint, or an explicitly reviewed Agent Skills
well-known index. Every external description and `SKILL.md` body remains
untrusted data.

The result is a provenance-aware recommendation receipt, not a capability
selection or installation. All candidates remain `not_installed`,
`not_enabled`, `not_loaded`, `not_executed`, and `not_validated`, with no MCP
connection, Host mapping, lifecycle-promotion, or execution authority. Trusted
coverage and the R5 `HOST_EVIDENCE_REQUIRED` path never invoke Scout. See
[Runtime integration Slice 2](docs/nexus-post-r5-runtime-integration-slice2.md).

## Post-R5 routing, evaluation, and immutable quarantine (Slices 3A–3C)

Slice 3A adds bounded semantic routing without expanding execution authority.
Slice 3B adds deterministic evaluation and quality-loop contracts whose
receipts remain evidence rather than Host authority. The frozen Slice 3C
implementation accepts only a validated Slice 2 bridge plus a stable, pre-supplied
ZIP, streams inert bytes into a repository-external immutable quarantine/CAS,
and produces subject-bound provenance, license, static-analysis,
classification, comparison, and lifecycle evidence.

Slice 3C never acquires, installs, activates, routes, loads, or executes a
candidate and grants no Host, MCP, Agent-delegation, approval, or promotion
authority. Its maximum positive state is
`REVIEW_EVIDENCE_COMPLETE + COMPLETE + QUARANTINED`; review completion is not
approval. See [Slice 3A](docs/nexus-post-r5-runtime-integration-slice3a.md),
[Slice 3B](docs/nexus-post-r5-runtime-integration-slice3b.md), and the approved
[Slice 3C ADR/PDS](docs/nexus-post-r5-runtime-integration-slice3c-adr-pds.md).

## Runtime R2 local MCP

Runtime R2 is a separately configured, local stdio-only MCP adapter. Later
development layers add read-only Host handoff and inventory-assessment tools;
none execute a Host capability. The stable planning tools are `nexus.health`,
`nexus.discover_capabilities`, and `nexus.plan_task`; the additive Post-R5
Slice 1 surface also exposes the non-authorizing
`nexus.route_capabilities`. Planning accepts a configured opaque workspace ID rather than a caller
path, uses bounded safe context, returns redacted plan/load evidence, and never
executes a plan. See [docs/nexus-runtime-r2-local-mcp.md](docs/nexus-runtime-r2-local-mcp.md)
for installation, local configuration, security boundaries, and removal.

</details>
