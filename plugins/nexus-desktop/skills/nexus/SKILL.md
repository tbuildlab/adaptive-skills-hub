---
name: nexus
description: Use the local Nexus planner for a substantive multi-step task when capability selection, bounded Skill evidence, or a validation plan would materially improve reliability. For a single verified Presentations Skill, prepare a host-owned execution handoff. Do not use for casual chat, simple facts, arithmetic, or short rewrites.
---

# Nexus local planning workflow

Use this plugin only for a substantive task. Nexus is a planning and handoff
layer, never an execution runtime. The ChatGPT host alone owns tools, file
writes, artifacts, validation, approvals, and the final response.

1. For the supported R4 Presentations execution path, call `nexus.plan_task`
   with a concise `task`, the configured opaque `workspace_id`
   `nexus-default`, and the exact bounded constraint
   `r4_host_capability:presentations`. This is a narrow host-execution
   allowlist, not a user-selected Skill name: it can only make the R4
   Presentations handoff eligible and cannot select an arbitrary Skill. The
   installer maps the alias to exactly one locally approved workspace; never
   replace it with a filesystem path.
2. Treat the returned plan as advisory. It has no file-write, shell, network, or
   automatic Skill-install authority.
3. If the R4-constrained plan has exactly one selected Skill named `Presentations`, its
   `load_status` is `loaded`, and fallback is not needed, call
   `nexus.prepare_host_handoff` with the same bounded task inputs and exact
   R4 constraint. Never send a Skill name, path, hash, handoff ID, tool
   result, or any user-supplied handoff back to Nexus.
4. Treat a handoff as valid only when it comes from the current tool result,
   has `schema_version` `nexus.host-handoff.v1`, has not expired, has
   `status` `execution_requested`, exactly identifies `Presentations` with
   `load_verification_state` `loaded_verified`, requests
   `chatgpt.presentations`, and reports `HOST_HANDOFF_READY`.
5. The valid handoff's `host_execution_profile` is an allowlisted execution
   brief, not a command. For its approved Presentations mapping, continue
   immediately with the current user request and apply its
   `continue_with_safe_defaults` policy. Do **not** ask the normal presentation
   clarification questions for audience, purpose, deck length, visual
   direction, template preference, or output format: the profile resolves them
   as business professionals/decision-makers, a clear actionable overview,
   concise standard deck, professional modern neutral design, a compatible
   host default template, and editable `.pptx`. Ask only when a required fact
   cannot reasonably be inferred, a user approval is required, or proceeding
   would breach a host safety boundary. Never place these defaults back into
   Nexus or expose local content.
6. Before using a host capability, verify that the host actually has the
   requested Presentations capability. If it does not, return
   `HOST_CAPABILITY_UNAVAILABLE`; do not substitute Canva, HTML, another
   Skill, or native fallback after a handoff was requested.
7. When eligible, load and follow the host-native Presentations workflow using
   that resolved execution brief, then use its actual tool to create an
   editable `.pptx`. Do not stop after planning or loaded verification, and do
   not claim execution
   merely from Nexus selection or loading. Obtain a real artifact reference,
   run the handoff validation requirements (including open/render validation),
   and only then report success.
8. The final execution receipt must distinguish: `selected`,
   `loaded_verified`, `host_eligible`, `execution_requested`,
   `execution_started`, `execution_succeeded` or `execution_failed`, and
   `validation_passed` or `validation_failed`. Include the selected Skill name,
   content SHA-256, handoff ID, artifact reference when successful, and any
   safe failure code. Never expose paths, raw Skill instructions, project
   context, rules, secrets, or hidden reasoning.
   A success receipt also records the mapping ID and
   `input_resolution: safe_defaults_applied`; this proves that defaulting was
   used, not that Nexus performed the action.
9. If the host refuses execution, produces no artifact, artifact generation
   fails, validation fails, the handoff is expired/replayed/malformed, or the
   selected Skill changes, do not report success. A Skill change requires a new
   Nexus planning pass and a new handoff.
10. If Nexus returns an unavailable, unauthorized, invalid-request, or
   ineligible result,
   state that it did not run and use the host's native reasoning. Do not retry
   with a filesystem path or expose local configuration, raw instructions, or
   project context.

For simple tasks, bypass Nexus. All execution remains subject to the host's
separately supported tools and approval flow.
