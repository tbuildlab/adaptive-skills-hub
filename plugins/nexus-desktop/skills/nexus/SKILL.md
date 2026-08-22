---
name: nexus
description: Use the local Nexus planner for a substantive multi-step task when capability selection, bounded Skill evidence, or a validation plan would materially improve reliability. Do not use for casual chat, simple facts, arithmetic, short rewrites, or task execution.
---

# Nexus local planning workflow

Use this plugin only for a substantive task. It is a planning layer, not an
execution runtime.

1. Call `nexus.plan_task` with a concise `task`, the configured opaque
   `workspace_id` `nexus-default`, and only bounded constraints needed for
   planning. The installer maps that alias to exactly one locally approved
   workspace; never replace it with a filesystem path.
2. Treat the returned plan as advisory. It has no file-write, shell, network, or
   automatic Skill-install authority.
3. Report the selected Skills and validation steps from the redacted result.
   Do not claim a selected Skill was executed merely because it was planned.
4. If Nexus returns an unavailable, unauthorized, or invalid-request result,
   state that it did not run and use the host's native reasoning. Do not retry
   with a filesystem path or expose local configuration, raw instructions, or
   project context.

For simple tasks, bypass Nexus. For execution after planning, use only the
host's separately supported tools and approval flow.
