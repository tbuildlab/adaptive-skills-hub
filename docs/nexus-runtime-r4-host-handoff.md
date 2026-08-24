# Nexus Runtime R4 — Host Skill Execution Handoff

**Status:** development branch only; not merged, frozen, or released.  R4 is a
runtime integration layer over frozen Nexus V1.2, Runtime R1/R2/R3, Desktop
Plugin final, and RC6 distribution behavior.  It changes none of their
selection, ranking, installation, or execution authority.

## Scope

R4 closes one observed gap for one capability only:

```text
selected -> loaded_verified -> host execution -> artifact -> validation
```

The only supported handoff is a single selected `Presentations` Skill to the
logical host capability `chatgpt.presentations`.  Documents, Spreadsheets,
Agents, Skill Scout, shell execution, remote MCP, OAuth, and V1.3 Core are out
of scope.

## Authority model

```text
User
  -> @Nexus
  -> nexus.plan_task (Nexus: select and guarded-load verification)
  -> nexus.prepare_host_handoff (Nexus: redacted intent only)
  -> ChatGPT Desktop host (eligibility, Presentations tool, artifact, validation)
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

## Host contract

The bundled Nexus Skill instructs the host to call the handoff tool only after
an eligible plan, then accept only its current tool result.  It must reject a
copied, expired, malformed, replayed, or substituted handoff.  A fresh planning
pass and fresh handoff are required after every Skill change.

The host must record the following states without collapsing them:

```text
selected
-> loaded_verified
-> host_eligible
-> execution_requested
-> execution_started
-> execution_succeeded | execution_failed
-> validation_passed | validation_failed
-> reported
```

If `chatgpt.presentations` is unavailable, it must return
`HOST_CAPABILITY_UNAVAILABLE` and must not substitute Canva, HTML, another
Skill, or native fallback after execution was requested.  If execution is
refused, fails, returns no artifact, or fails validation, it must return the
corresponding safe failure code and must not report success.

The host obtains a real opaque artifact reference and validates that the output
is an editable `.pptx` and can be opened/rendered before a successful receipt.
The public plugin model supports explicit `@` use after installation; the host
still controls which installed tools it can actually call.
[Using plugins](https://learn.chatgpt.com/docs/plugins)

## Receipt contract

The pure local protocol validator used by tests accepts only a receipt linked
to the current handoff ID, Skill identity, and content SHA-256.  A successful
receipt needs an opaque artifact reference, `artifact_kind: "pptx"`, and both
`execution_succeeded` and `validation_passed`.  It also exercises explicit
failure codes for unavailable capability, execution refusal, artifact failure,
validation failure, substitution, replay, expiry, and malformed input.

The validator is not an MCP tool and is not evidence of a real ChatGPT Desktop
artifact.  Real execution remains a manual Desktop acceptance requirement.

## Automated acceptance

Automated R4 coverage includes:

- selected-but-not-loaded, ambiguous selection, and load hash mismatch;
- malformed/replayed/expired handoffs and attempted Skill substitution;
- raw Skill/context/path leakage;
- unavailable host capability, refusal, artifact absence/generation failure,
  and validation failure;
- MCP stdio protocol registration and read-only annotations;
- existing V1.1/V1.2/R1/R2/R3/plugin/distribution regressions.

## Required human Desktop acceptance

In a fresh ChatGPT Desktop conversation with the R4 plugin installed, submit
exactly:

```text
@Nexus Create an editable PowerPoint presentation about digital transformation in business.
```

Acceptance requires evidence that the trace contains `Presentations` selected,
`loaded_verified`, a valid R4 handoff, host eligibility, a genuine host-native
Presentations tool call, a real editable `.pptx` artifact reference, an
open/render validation, and an execution receipt ending in
`execution_succeeded` plus `validation_passed`.  Planning-only output does not
pass R4 acceptance.
