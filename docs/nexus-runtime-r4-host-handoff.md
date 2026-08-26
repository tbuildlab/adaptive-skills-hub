# Nexus Runtime R4 — Host Skill Execution Handoff

**Status:** accepted as the Host execution component of the human-validated
`runtime-r5-final` integration baseline. There is no separate
`runtime-r4-final` tag. R4 is a runtime integration layer over frozen Nexus
V1.2, Runtime R1/R2/R3, Desktop Plugin final, and RC6 distribution behavior.
It changes none of their selection, ranking, installation, or execution
authority.

## Scope

R4 closes one observed gap for one capability only:

```text
selected -> loaded_verified -> host execution -> artifact -> validation
```

The only supported handoff is a single selected `Presentations` Skill to the
logical host capability `chatgpt.presentations`.  Documents, Spreadsheets,
Agents, Skill Scout, shell execution, remote MCP, OAuth, and V1.3 Core are out
of scope.

Normal V1.2 planning and ranking are unchanged.  The R4 Desktop Skill uses the
explicit bounded constraint `r4_host_capability:presentations` for the
host-execution path only.  That constraint narrows candidates to the one
supported host capability; it cannot name or select an arbitrary Skill and an
unknown R4 host constraint is rejected.  This prevents a higher-ranked local
presentation workflow from being silently substituted for the host-native
Presentations workflow.

## Authority model

```text
User
  -> @Nexus
  -> nexus.plan_task (Nexus: select and guarded-load verification)
  -> nexus.prepare_host_handoff (Nexus: redacted intent only)
  -> ChatGPT Desktop host (eligibility, Presentations Skill workflow, artifact, validation)
  -> host execution receipt and final response
```

Nexus remains local, stdio, read-only, and stateless.  It does not execute a
Skill, invoke a host tool, start a process, write a file, receive an artifact,
or persist host execution state.  The ChatGPT Desktop host remains the only
owner of host-native tools, artifact creation, approval prompts, validation,
and final response.

This follows the official plugin boundary: Skills supply reusable workflow
instructions while MCP servers supply controlled actions; they are not a
mechanism for an MCP server to invoke an arbitrary host Skill directly.
[Skills](https://developers.openai.com/plugins/concepts/skills)

## `nexus.prepare_host_handoff`

The new R4 tool uses exactly the bounded planning inputs of `nexus.plan_task`:
`task`, opaque `workspace_id`, optional `project_context_mode`, and bounded
`constraints`.  It accepts no Skill name, path, hash, prior handoff, artifact,
or host result.

For every invocation it independently replans, guarded-loads the selected
Skill, reads it again, and compares internal load fingerprints.  Any change,
missing evidence, ambiguous selection, fallback, or non-Presentations Skill
fails closed.  The result is a short-lived redacted envelope:

```json
{
  "schema_version": "nexus.host-handoff.v1",
  "handoff_id": "opaque UUID",
  "issued_at": "UTC timestamp",
  "expires_at": "UTC timestamp within five minutes",
  "plan_version": "nexus.v2.plan.v1",
  "status": "execution_requested",
  "task_category": "presentation",
  "selected_skill": {
    "resource_id": "skill:presentations",
    "name": "Presentations",
    "content_sha256": "64-character digest",
    "load_verification_state": "loaded_verified"
  },
  "logical_host_capability": "chatgpt.presentations",
  "requested_execution_mode": "host_native_presentations",
  "host_execution_profile": {
    "mapping_id": "nexus.host-map.presentations.v1",
    "continuation_policy": "continue_with_safe_defaults",
    "clarification_policy": "ask_only_for_required_noninferable_input",
    "default_profile": "business_presentation.v1"
  },
  "validation_requirements": [
    "artifact_created",
    "artifact_editable",
    "presentation_open_render"
  ],
  "fallback": {"kind": "native_codex_fallback", "status": "not_needed"},
  "security_result": {"code": "HOST_HANDOFF_READY", "mcp_execution_authority": "none"}
}
```

The envelope never contains raw `SKILL.md` text, absolute paths, project
context/rules, candidates, scores, environment values, secrets, artifact paths,
or hidden reasoning.

`host_execution_profile` is a registry-based, content-free mapping designed to
extend safely: each future host-native capability needs its own reviewed
mapping and tests; it cannot be selected through an arbitrary user Skill name.
For the R4 Presentations mapping only, ordinary authoring defaults are resolved
before Host execution: business professional audience, actionable overview,
concise standard deck, professional neutral design, host-compatible default
template, and editable `.pptx`. The Host must continue without asking about
those defaultable values. It may still stop for an approval boundary, a truly
non-inferable required value, integrity failure, unavailable capability, or a
safety conflict.

## Host contract

The bundled Nexus Skill instructs the host to call the handoff tool only after
an eligible plan, then accept only its current tool result.  It must reject a
copied, expired, malformed, replayed, or substituted handoff.  A fresh planning
pass and fresh handoff are required after every Skill change.

The current documented plugin model does not expose an MCP operation that can
force ChatGPT Desktop to invoke a second Host Skill/tool or accept a receipt
callback. Skills are model-loaded workflow instructions and MCP provides its
own controlled actions; Nexus therefore supplies an explicit continuation
instruction and the Host retains tool selection and artifact authority.
[Skills](https://developers.openai.com/plugins/concepts/skills) This is the
sole platform-controlled limitation: successful R4 execution remains subject
to real Desktop Host evidence, never an MCP claim.

The host must record the following states without collapsing them:

```text
selected
-> loaded_verified
-> host_eligible
-> execution_requested
-> execution_started
-> execution_succeeded | execution_failed
-> validation_passed | validation_failed
```

`reported` may be used by the Host as an outer conversational lifecycle label,
but it is not a normative R4 receipt field, is not required to be serialized,
and is not an acceptance gate.

If `chatgpt.presentations` is unavailable, it must return
`HOST_CAPABILITY_UNAVAILABLE` and must not substitute Canva, HTML, another
Skill, or native fallback after execution was requested.  If execution is
refused, fails, returns no artifact, or fails validation, it must return the
corresponding safe failure code and must not report success.

The host obtains a real opaque artifact reference in the bounded
`host-artifact:<opaque-token>` namespace and validates that the output is an
editable `.pptx` and can be opened/rendered before a successful receipt. Paths,
URLs, URI-like values, and unapproved namespaces are rejected.
The public plugin model supports explicit `@` use after installation; the host
still controls which installed tools it can actually call.
[Using plugins](https://learn.chatgpt.com/docs/plugins)

## Receipt contract

The pure local protocol validator used by tests accepts only a receipt linked
to the current handoff ID, Skill identity, and content SHA-256.  A successful
receipt needs a `host-artifact:<opaque-token>` reference, `artifact_kind:
"pptx"`, and both `execution_succeeded` and `validation_passed`.  It also
exercises explicit
failure codes for unavailable capability, execution refusal, artifact failure,
validation failure, substitution, replay, expiry, and malformed input.

The validator is not an MCP tool and is not evidence of a real ChatGPT Desktop
artifact.  Real execution remains a manual Desktop acceptance requirement.
It also requires the approved mapping ID and `input_resolution:
safe_defaults_applied` for a success receipt, so the trace cannot silently
convert selection/loading into a claimed artifact result.

## Automated acceptance

Automated R4 coverage includes:

- selected-but-not-loaded, ambiguous selection, and load hash mismatch;
- malformed/replayed/expired handoffs and attempted Skill substitution;
- raw Skill/context/path leakage;
- unavailable host capability, refusal, artifact absence/generation failure,
  and validation failure;
- MCP stdio protocol registration and read-only annotations;
- existing V1.1/V1.2/R1/R2/R3/plugin/distribution regressions.

## Human Desktop acceptance

In a fresh ChatGPT Desktop conversation with the R5 pilot.4 plugin installed,
the user submitted exactly:

```text
@Nexus Create an editable PowerPoint presentation about digital transformation in business.
```

The accepted trace recorded `Presentations` selected and `loaded_verified`;
the binding `host_skill_workflow -> chatgpt.presentations ->
nexus.host-map.presentations.v1`; `HOST_HANDOFF_READY`; actual Host workflow
execution; and a real editable `.pptx` that passed artifact creation,
editability, and open/render validation.

Acceptance requires evidence that the trace contains `Presentations` selected,
`loaded_verified`, a valid R4 handoff, host eligibility, a genuine host-native
execution of the loaded Presentations workflow through its required Host tools,
a real editable `.pptx` artifact reference, an
open/render validation, and an execution receipt ending in
`execution_succeeded` plus `validation_passed`.  Planning-only output does not
pass R4 acceptance.
