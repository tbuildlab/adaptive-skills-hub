# Nexus Post-R5 Runtime Integration — Slice 1

**Status:** development checkpoint, ready for review after validation. This is
not a frozen or accepted release and does not change any existing final tag.

## Purpose

Slice 1 adds the first bounded adapter from the Post-R5 Capability Foundation
to a real Nexus MCP decision path. It does not replace V1.1/V1.2 planning and
does not turn Nexus into an executor.

```text
existing planner or Host normalization
  -> nexus.runtime-requirements.v1
  -> reviewed capability catalog and runtime integrity recheck
  -> exact minimum-sufficient selector
  -> lifecycle/trust/permission/compatibility gate
  -> nexus.runtime-capability-decision.v1
  -> existing load/Host/execution boundary, if separately eligible
```

The additive read-only tool is `nexus.route_capabilities`. Its caller supplies
only bounded normalized domain, output, validation, permission, and execution
mechanism tokens. It cannot supply capability IDs, display names, providers,
mappings, paths, prompts, project content, or execution results. Candidate
records come only from the reviewed local foundation catalog.

## Runtime eligibility

Before selection, Nexus validates the complete capability and upstream source
registries. A directly usable local Skill must retain:

- an `available` lifecycle and availability state;
- compatible metadata and an allowed execution mechanism;
- an executable trust tier;
- a reviewed repository and exact commit matching the upstream registry;
- a matching reviewed component SHA-256;
- a regular, non-symlinked file under its configured Nexus source root;
- an unchanged file fingerprint while its bytes are hashed; and
- permissions within the normalized request boundary.

The catalog and upstream registry are parsed from the same stable byte buffers
whose digests were checked against the package manifest. They are not read a
second time after verification, closing the integrity-check-to-use window.

A changed pin or content digest is quarantined. A missing local component is
unavailable. Duplicate IDs, malformed provenance, excessive candidates,
uncovered requirements, and unsupported permissions/mechanisms fail closed.
The adapter neither searches for replacement repositories nor installs an
absent component.

## Decision envelope

`nexus.runtime-capability-decision.v1` records:

- requirement identity and version;
- selector version and bounded candidate IDs;
- considered, selected, and non-selected dispositions with reason codes;
- creator, reviewer, enhancer, advisory, alternative, redundant, unavailable,
  incompatible, and rejected roles where applicable;
- lifecycle, trust, availability, execution mechanism, and Host observation;
- a reviewed Host mapping only when it originated inside the R5 assessment;
- the explicit compatibility/fallback route; and
- fixed evidence states: selection may be present, while execution remains
  `not_executed` and validation remains `not_validated`.

The envelope has `mcp_execution_authority: none`. It contains no raw Skill
instructions, display-name authorization, filesystem path, project context,
credential, artifact reference, or execution receipt. Replaying it grants no
authority, and the R4 handoff validator rejects it as the wrong schema.

## R5 Host compatibility

The accepted R5 boundary remains:

```text
current_turn_host_visible_subset / not_globally_enumerated
```

`nexus.assess_host_capabilities` still parses a fresh, server-ticket-bound Host
snapshot and returns its unchanged `nexus.host-capability-assessment.v3`
schema. Before returning, Slice 1 adapts the already validated internal R5
facts to Capability Foundation records and runs the new selector as a
fail-closed cross-check. Its selected stable identities must exactly equal the
R5 selection. The general decision envelope is not duplicated into the frozen
R5 response, so existing handoff/receipt consumers and response-size limits
remain unchanged.

The only production Host execution mapping remains:

```text
host_skill_workflow
  -> chatgpt.presentations
  -> nexus.host-map.presentations.v1
```

The mapping is never inferred from a display name. If no fresh Host evidence
is available, a presentation decision returns `HOST_EVIDENCE_REQUIRED` and the
explicit R5 assessment compatibility route. Static records for Ppt Master,
DashAI PPT, or `emil-design-eng` are never invented as Host-executable
capabilities. If such names are genuinely surfaced but unmapped, they remain
non-selected.

## Reviewer, enhancer, and Agent boundary

The envelope can represent selected creator/reviewer/enhancer roles and the
existing bounded quality policy: at most two review cycles, one enhancement
pass, copy-on-write original preservation, validated findings before an
enhancement, and revalidation afterward. Actual reviewer/enhancer execution is
deferred to a separately approved Host/runtime mapping.

Agents remain advisory-only. They can appear in `advisory_capabilities`, but
they never enter the executable minimum set and no Agent, subprocess, swarm,
shell, network, install, update, or delegation runtime is added.

## Compatibility and fallback

- Existing V1.1/V1.2 planner behavior is unchanged.
- Existing R1–R5 tools, schemas, Host mappings, TTL/replay gates, artifact
  validation, and receipts remain authoritative.
- `nexus.route_capabilities` is additive and read-only.
- When the foundation cannot cover a non-Host request, it reports
  `CAPABILITY_NOT_COVERED` with the explicit
  `legacy_v1_v2_or_native_codex` compatibility route.
- When a Host-native presentation requires current-turn evidence, it reports
  `HOST_EVIDENCE_REQUIRED` and routes to the existing R5 assessment.
- A selection never proves loading, execution, artifact creation, or
  validation.

## Deferred

No Skill Scout, new upstream, automatic install/update, unrestricted
reviewer/enhancer execution, Agent Runtime, Remote MCP, OAuth, R6, Slice 2, or
V1.3 work is included.
