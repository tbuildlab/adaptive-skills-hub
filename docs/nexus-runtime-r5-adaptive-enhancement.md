# Nexus Runtime R5 — Adaptive Enhancement Loop

**Status:** development branch only. R5 is not merged, frozen, tagged, or
released. It layers a bounded, Host-owned post-execution enhancement pass over
the accepted R4 Presentations handoff. It does not change V1.1, V1.2 planning,
R1/R2/R3, Desktop Plugin final, RC1–RC6, or any frozen tag.

## Scope and non-goals

R5 addresses only this sequence for an already successful R4 presentation:

```text
primary R4 artifact validated by Host
-> Host render/inspection
-> redacted artifact-state enum
-> one allowlisted enhancement intent
-> Host copy-on-write checkpoint
-> Host-native Presentations refinement
-> re-render/revalidation
-> retain improved artifact or restore checkpoint
```

R5 does **not** create another planner, dynamic Skill executor, Agent runtime,
shell runner, artifact store, remote MCP, OAuth flow, Skill Scout, or V1.3.
It does not route a new Skill after R4 and does not make Nexus read, receive,
write, copy, validate, or retain an artifact.

## Authority and state model

```text
Nexus MCP                         ChatGPT Desktop Host
----------                        --------------------
redacted intent only              holds actual artifact and R4 receipt
no filesystem / tool authority    render/inspect and derive bounded state
no Agent authority                checkpoint before a mutation
no receipt persistence            executes native Presentations if available
                                  re-renders/revalidates and reports truthfully
```

The primary R4 trace remains independent and authoritative:

```text
selected -> loaded_verified -> host_eligible -> execution_requested
-> execution_started -> execution_succeeded|execution_failed
-> validation_passed|validation_failed -> reported
```

R5 adds a distinct trace only after that primary success:

```text
base_execution_verified -> artifact_state_verified -> enhancement_requested
-> checkpoint_created -> enhancement_started
-> enhancement_succeeded|enhancement_failed
-> revalidation_passed|revalidation_failed
-> rollback_retained|rollback_restored|rollback_unavailable -> reported
```

Selection, loading, an intent, and a Host request are never reported as an
executed or validated enhancement.

## Closed artifact-state input

`nexus.prepare_enhancement_handoff` accepts only
`nexus.host-artifact-state.v1`:

```json
{
  "schema_version": "nexus.host-artifact-state.v1",
  "artifact_kind": "pptx",
  "base_mapping_id": "nexus.host-map.presentations.v1",
  "base_execution_state": "execution_succeeded",
  "base_validation_state": "validation_passed",
  "checks": {
    "artifact_created": "passed",
    "artifact_editable": "passed",
    "presentation_open_render": "passed"
  },
  "observations": ["layout_density_high"],
  "enhancement_pass": 0
}
```

The only observations are `layout_density_high`,
`visual_hierarchy_weak`, `text_legibility_low`, and
`contrast_needs_review`. The schema rejects raw artifact references, paths,
URLs, task text, project context, prior handoffs/receipts, Skill names, Skill
hashes, candidate IDs, Agents, and free-form render output. The Host must only
derive the state from its current R4 receipt; a caller-supplied envelope has no
authorization effect.

## Allowlisted enhancement registry

The first registry has two descriptive, non-Skill candidates:

| Candidate | Eligible observation | Host capability | Scope |
| --- | --- | --- | --- |
| `presentation_layout_polish.v1` | `layout_density_high`, `visual_hierarchy_weak` | `chatgpt.presentations` | refine layout and visual hierarchy |
| `presentation_legibility_polish.v1` | `text_legibility_low`, `contrast_needs_review` | `chatgpt.presentations` | improve legibility and contrast |

Nexus chooses at most one by fixed reviewed priority and stable ID tie-break.
It will not choose Canva, `ppt-master`, an Emil UI Skill, a framework, an
Agent, a shell command, or an arbitrary future Skill. A clean artifact,
unsupported observation, unavailable Host, or exhausted budget preserves the
known-good primary artifact.

## Host contract

The MCP result is a short-lived redacted
`nexus.host-enhancement-handoff.v1` with a candidate ID, safe reason codes,
logical Host capability, copy-on-write requirement, validation requirements,
and `HOST_ENHANCEMENT_HANDOFF_READY`. It has no artifact reference or raw
instructions. It is not a command.

The Host must:

1. validate its current R4 handoff and receipt locally;
2. keep the actual artifact private and create a copy-on-write checkpoint;
3. confirm `chatgpt.presentations` is still available;
4. execute only the supplied mapped Presentations refinement;
5. re-open/render the candidate, verify editability, and confirm the observed
   issue actually improved;
6. retain it only after revalidation and improvement assessment, otherwise
   restore the checkpoint; and
7. produce a receipt with the primary and R5 traces kept separate.

If the Host cannot checkpoint, it returns `HOST_ROLLBACK_UNAVAILABLE` before a
mutation. It must return `HOST_CAPABILITY_UNAVAILABLE`, `EXECUTION_REFUSED`,
`ARTIFACT_MISSING`, `ENHANCEMENT_FAILED_ROLLBACK_RESTORED`, or
`VALIDATION_FAILED_ROLLBACK_RESTORED`, or
`NO_IMPROVEMENT_ROLLBACK_RESTORED` rather than claiming success. Handoffs
expire after five minutes and cannot be replayed.

Current official plugin behavior provides model-loaded Skill instructions and
MCP tools, but no documented MCP primitive that can compel the Desktop Host to
invoke a second Host Skill or return a callback. R5 therefore provides a
strict continuation contract; real Desktop execution remains a human
acceptance fact, not an MCP claim. See [OpenAI Skills
documentation](https://developers.openai.com/plugins/concepts/skills).

## R5 automated checks

The branch covers deterministic minimal selection, clean/no-op behavior,
budget exhaustion, malformed or injected state, path/context/Skill/Agent
leakage, host-unavailable and refusal paths, no artifact, mapping/candidate
substitution, primary-receipt mismatch, expired/replayed handoffs, validation
failure, rollback restoration/unavailability, and R4/MCP regressions.

## Required Desktop acceptance

After a future local R5 pilot is installed, use the accepted R4 task:

```text
@Nexus Create an editable PowerPoint presentation about digital transformation in business.
```

Acceptance requires a real primary editable `.pptx` with R4 validation. If a
clearly observable allowlisted issue exists, it additionally requires an R5
copy-on-write checkpoint, actual Host-native Presentations refinement, a new
artifact reference, open/render revalidation, and a truthful R5 receipt. If no
high-value safe enhancement exists, retaining the validated primary artifact is
the correct R5 result.
