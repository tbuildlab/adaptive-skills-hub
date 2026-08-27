# Nexus Post-R5 Runtime Integration — Slice 1

**Status:** independently reviewed, accepted, and frozen as
`post-r5-runtime-integration-slice1-final`. This additive integration baseline
does not move or replace `runtime-r5-final` or any earlier final/RC tag.

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

## Final independent acceptance

The final review rechecked all previously identified blockers and the complete
diff from the accepted R5 baseline. One additional blocker was reproduced:
persisted catalog metadata could claim `host_native` and
`observed_current_turn=true`, causing a non-authorizing but misleading selected
state without fresh Host evidence. The accepted repair makes every static
`host_native` record unavailable and requires an internal R5 mapping before a
Host-native record can enter a selected state. A regression now covers both
the static-catalog path and a direct unmapped selection attempt.

The first post-merge validation pass also exposed a Windows-only test-fixture
error: its temporary manifest hashed raw CRLF bytes while the production
manifest contract normalizes UTF-8 text to LF. The fixture now uses the
production normalization rule; no runtime integrity check was weakened.

Final validation on 2026-08-27 recorded:

- 230/230 full unit/protocol tests successful, with four intentional
  environment skips;
- 29/29 focused Capability Foundation/runtime-decision tests successful;
- 73/73 targeted R4/R5/Desktop Plugin tests successful;
- 53/53 security/protocol tests successful, with one Windows symlink-privilege
  skip included in that suite;
- 21/21 distribution tests successful, with three intentional environment
  skips;
- stable single reads of the integrity manifest, catalog, and upstream
  registry, with the decision parsed from those verified byte buffers;
- static manifest reproducibility and per-entry integrity successful;
- no execution/network authority, secret/private-path leakage, generated
  runtime state, or packaging regression in the Slice 1 diff; and
- unchanged R5 v3 response fields, Presentations mapping, current-turn Host
  evidence requirement, TTL/replay gates, handoff, artifact, and receipt
  contracts.

The legacy final smoke remains 6/10 in the current Host-managed environment.
The identical failures (`document`, `spreadsheet`, `pdf`, and the dependent
`research_document_chain`) reproduce from the unchanged pre-Slice-1 checkpoint
`65304b7cd2d787f06b8054ac8e54dc05981e5cda`. Its persisted index references
Host Plugin cache version `26.819.11345`, while the Host currently exposes a
newer cache version and the indexed Skill files no longer exist. Nexus does not
fabricate or rewrite those Host-managed files; this environmental cache drift
is a recorded non-blocking limitation, not a Slice 1 regression.
