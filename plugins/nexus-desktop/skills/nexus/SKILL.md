---
name: nexus
description: Use the local Nexus planner for a substantive multi-step task when capability selection, bounded Skill evidence, or a validation plan would materially improve reliability. For a single verified Presentations Skill, prepare a host-owned execution handoff and one bounded post-validation enhancement pass when it is clearly useful. Do not use for casual chat, simple facts, arithmetic, or short rewrites.
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

## R5 bounded post-execution enhancement

Run this section only after the current R4 handoff has produced a real editable
`.pptx`, the Host has completed the primary validation requirements, and the
Host holds the current R4 handoff plus its own successful receipt. Nexus must
not receive the artifact reference, a path, the R4 receipt, raw render output,
task text, a selected Skill name, or a hash.

1. Inspect/render the actual Host-owned artifact. If it is already suitable,
   do not enhance it. If a clearly observable, low-risk issue fits exactly one
   supported code, derive a content-free artifact state with only:
   `schema_version: nexus.host-artifact-state.v1`, `artifact_kind: pptx`,
   `base_mapping_id: nexus.host-map.presentations.v1`, successful base
   execution/validation states, the three passed R4 checks, up to three of
   `layout_density_high`, `visual_hierarchy_weak`, `text_legibility_low`, or
   `contrast_needs_review`, and `enhancement_pass: 0`.
2. Call `nexus.prepare_enhancement_handoff` only with that exact bounded
   artifact-state object from the current Host observation. Never send it a
   user-supplied state, an artifact, an artifact URL, a path, an earlier
   handoff, a receipt, a candidate ID, a Skill, an Agent, or any project data.
3. If it returns `NO_ENHANCEMENT_NEEDED`, retain and report the already
   validated primary artifact. If it returns a current
   `nexus.host-enhancement-handoff.v1` with
   `HOST_ENHANCEMENT_HANDOFF_READY`, use only its allowlisted
   `chatgpt.presentations` mapping. It is not authority to invoke another
   Skill, Canva, a shell, an Agent, or an arbitrary tool.
4. Before an enhancement, create the required Host-owned
   `host_copy_on_write` checkpoint. If the Host cannot checkpoint, return
   `HOST_ROLLBACK_UNAVAILABLE` and preserve the
   known-good artifact. Then verify the Host still has Presentations. If not,
   return `HOST_CAPABILITY_UNAVAILABLE`; do not substitute a capability.
5. If eligible, use the Host-native Presentations workflow to apply only the
   allowlisted layout or legibility polish. Do not ask routine style/audience
   clarification questions when the safe R4 defaults already suffice. Make no
   more than one R5 enhancement pass and never rediscover, rerank, reload, or
   substitute a Skill during this flow.
6. Re-open/render and revalidate the edited candidate. Keep it only when it is
   still editable, `presentation_open_render` passes, and the observed issue
   is actually improved. If it is valid but not improved, restore the
   checkpoint and report `NO_IMPROVEMENT_ROLLBACK_RESTORED`. On execution or
   validation failure, restore the checkpoint and report the failure plus
   rollback outcome. Do not claim an enhancement, an artifact, or validation
   merely from a Nexus intent.
7. A truthful enhancement receipt distinguishes:
   `base_execution_verified`, `artifact_state_verified`,
   `enhancement_requested`, `checkpoint_created`, `enhancement_started`,
   `enhancement_succeeded` or `enhancement_failed`,
   `revalidation_passed` or `revalidation_failed`, and the explicit rollback
   result. A successful receipt requires a new real artifact reference and
   passed revalidation. Keep R4 selected/loaded/executed/validated evidence
   separate from R5 enhancement evidence.

For simple tasks, bypass Nexus. All execution remains subject to the host's
separately supported tools and approval flow.
