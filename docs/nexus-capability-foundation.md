# Nexus Post-R5 Capability Foundation

**Status:** development branch only. This additive foundation does not modify
the frozen `runtime-r5-final` planner, Host inventory, handoff, execution, or
artifact-validation semantics.

## Purpose

Nexus now has a data model for heterogeneous capability evidence without
flattening every upstream resource into an executable Skill. A record can
represent a Skill, Agent, Agent collection, Runtime, Harness, Framework,
Library, Reference Architecture, Example/Application Collection, Skill
Factory, Registry Infrastructure, or Design/Enhancement Resource.

The model records:

- stable capability identity and type;
- source scope, repository, exact commit, relative component path, content
  SHA-256 when available, and import mode;
- trust tier, risk status, lifecycle state, compatibility, and availability;
- execution mechanism and explicit permissions;
- dependencies, inputs, outputs, domains, and validation requirements;
- supported selection roles;
- Host visibility scope and global-enumeration limitation;
- update and re-review strategy.

`config/capability-foundation.json` is data only. Loading it does not install,
load, import, invoke, or update an upstream component.

## Execution authority

Registration never creates execution authority.

- A `Skill` may be executable only when its exact local content/provenance is
  verified, its lifecycle is `available`, its compatibility is `compatible`,
  its permissions fit the caller's boundary, and its execution mechanism is
  explicitly allowed.
- An `Agent` is advisory-only in this phase. It cannot write, use network,
  launch shell/subprocesses, delegate, approve its own output, or execute a
  Host capability.
- Runtime, Harness, Framework, Library, Reference, Example, Skill Factory, and
  Registry records are reference-only or unavailable. Their presence cannot
  turn them into Skills.
- `shell`, `install`, `update`, and `agent_delegation` permissions are rejected
  by the capability validator.

## Host capability boundary

The accepted R5 limitation remains exact:

- inventory scope: `current_turn_host_visible_subset`;
- completeness: `not_globally_enumerated`.

A `host_native` capability record is valid only when the Host surfaced it in
the current turn. A static catalog entry, installed filesystem bundle, display
name, or historical receipt cannot establish current Host eligibility. The
foundation does not scan private ChatGPT Desktop state and does not add a
global Host capability enumeration claim.

## Minimum-sufficient selection

`ash.capabilities.select_minimum_sufficient_capabilities` performs bounded,
exact set-cover selection over already-validated caller-supplied facts. It
matches declared domains, outputs, and validation requirements—not display
names or generic keywords. The caller must provide allowed permissions and
execution mechanisms.

Every considered capability receives one truthful disposition:

- `primary_creator`
- `enhancer`
- `reviewer`
- `alternative`
- `advisory`
- `redundant`
- `unavailable`
- `incompatible`
- `rejected`

The exact search is capped at 18 eligible candidates. Exceeding the cap fails
closed instead of falling into an unbounded optimizer. If the approved set
cannot cover the request, the result is `CAPABILITY_NOT_COVERED`; it does not
invent a Skill or silently authorize a fallback.

## Bounded quality loop

`ash.quality_loop` describes this future execution sequence without executing
it:

```text
creator -> artifact -> validation -> reviewer
        -> optional enhancer -> revalidation -> report
```

The loop has at most two review cycles and one enhancement pass. Enhancement
is conditional on a validated defect and material expected improvement. It is
copy-on-write and must preserve the original artifact. A successful receipt
requires at least one actually executed capability, an opaque artifact
reference, and passed validation. Selected or loaded evidence cannot be
reported as executed.

## Capability lifecycle

The normal lifecycle is monotonic:

```text
discovered -> classified -> provenance_verified -> security_reviewed
-> tested -> approved -> available
```

Any stage may move to `quarantined`, `deprecated`, or `rejected`. These states
cannot jump back to available; a fresh reviewed record is required. If an
approved or available repository commit or content hash changes, the revision
is automatically classified as `quarantined`. No upstream update is installed
or merged automatically.

## Local audit snapshot

The 2026-08-26 read-only scan found:

- 135 local Skill records;
- 106 available records;
- 26 records in `duplicate_conflict`;
- 3 shadowed duplicates;
- 270 unique installed advisory Agent definitions;
- 267 Agent IDs overlapping the Agency Agents sources and 3 local TARUMT-only
  Agents.

This is audit evidence, not a promise of Host executability. Relevant local
Skill evidence included Presentations, Ppt Master, DashAI PPT,
`emil-design-eng`, and the Nexus R5 Plugin Skill. Presentations/Ppt Master/
DashAI availability continues to be governed by the current-turn R5 Host
inventory and existing stable mapping rules; this foundation changes neither.

## Compatibility and non-goals

- V1.1, V1.2 Core, Runtime R1–R5, Desktop Plugin, and RC1–RC6 remain unchanged.
- No Skill Scout, auto-install/update, unrestricted Agent runtime, swarm,
  Remote MCP, OAuth, shell executor, or V1.3 was added.
- The implementation is Python standard-library only.
- Development commands may prefer PowerShell 7. Windows installer behavior
  remains compatible with Windows PowerShell 5.1; no shell configuration is
  changed by this phase.

See [Upstream source registry](upstream-source-registry.md) and
[Agent task contract](nexus-agent-runtime-contract.md).

## Slice 1 runtime integration

The first additive runtime bridge is documented in [Post-R5 Runtime
Integration — Slice 1](nexus-post-r5-runtime-integration-slice1.md). It adds a
strict normalized requirements schema, runtime provenance/content rechecks,
the read-only `nexus.route_capabilities` MCP tool, and an internal R5 Host
selection cross-check. It does not add execution authority or change the
accepted Host handoff, artifact, receipt, TTL, or replay contracts.
