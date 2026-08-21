---
name: adaptive-skills-hub
description: Route a task to the smallest sufficient set of locally accessible Codex
  Skills, load their full instructions only after selection, and complete the task with
  validation. Use for multi-capability work; do not use as a generic recommendation list.
---

# Adaptive Skills Hub

## Purpose

Act as the capability router for the current task.

The deterministic helper is `scripts/hub.py`. Its default workspace is this Hub's
parent directory. Start a task with:

```powershell
python scripts/hub.py route "<user task>"
```

Then read each selected `SKILL.md` in full and execute the user's task with its
instructions. For an auditable packet that proves the load step, use:

```powershell
python scripts/hub.py run "<user task>" --packet state/task-packet.json
```

`run` loads instructions; it does not pretend prose instructions are a shell program.
Codex is the executor for normal Skills. A trusted local Skill may optionally declare
JSON-array `hub_command` and `hub_validate` frontmatter hooks; only run them with the
explicit `--allow-skill-commands` flag, never through a shell.

The goal is not to recommend skills and stop. The goal is to:
1. understand the task,
2. discover relevant capabilities,
3. select the smallest sufficient set,
4. load accessible skills,
5. execute the task using their instructions,
6. validate the result,
7. report what was actually used.

## Core rule: execute, do not merely recommend

When a relevant installed skill is available and accessible:

- Open/read that skill's `SKILL.md`.
- Follow its instructions.
- Use its supporting resources when relevant.
- Continue executing the user's task.

Do NOT stop after saying "use X skill".

Only stop at a recommendation when:
- the skill is not installed or cannot be accessed,
- a required external capability is unavailable,
- execution requires an explicit permission that has not been granted,
- the requested operation is unsafe or disallowed,
- or the user explicitly requested recommendations only.

## Source classes

Treat registered sources according to their class:

### skill
Reusable procedural instructions. These may be directly loaded and executed.

### agent
Specialist role/process guidance. Use it to improve task decomposition or expert review.
An agent reference does not automatically become an executable skill.

### reference
Example implementations, patterns, architectures, or design references.
Use selectively. Do not copy a whole repository by default.

### framework
Execution/orchestration software. Use only when the task actually requires the framework.

### project-rule
Local requirements, specifications, rubrics, architecture decisions, or explicit user instructions.
These have higher priority than external references.

## Routing workflow

### Phase 1 — Understand
Identify:
- primary task,
- domain,
- deliverable,
- constraints,
- required tools,
- whether code/files/web/research are involved.

Do not over-classify. Keep only materially useful signals.

### Phase 2 — Discover
Search in this order when accessible:
1. explicit user/project requirements,
2. installed local skills,
3. project-specific skills,
4. registered specialist skills,
5. registered agents,
6. registered reference repositories,
7. registered frameworks.

Use the indexed `state/installed-skills.json`, `state/installed-agents.json`, and
`sources.json`. Rebuild the local index with `python scripts/hub.py rescan`; do not
manually maintain normal local Skill entries. `registry.json` is a generated overview.

If the runtime provides a native skill discovery mechanism, use it as well.
The registry supplements native discovery; it does not replace it.

### Phase 3 — Rank
Rank candidates by:
- task relevance,
- specificity,
- authority,
- compatibility with current project,
- execution cost,
- overlap with already selected capabilities.

Prefer the smallest sufficient set.

Do not load every possible skill.

### Phase 4 — Resolve conflicts
Priority order:

1. system/safety/tool constraints
2. explicit user instructions
3. project requirements/specifications/rubrics
4. project-specific skills
5. installed specialist skills
6. official framework/project documentation
7. agent guidance
8. external examples/reference repositories

When a lower-priority source conflicts with a higher-priority source:
- preserve the higher-priority rule,
- use only the non-conflicting part of the lower-priority source.

### Phase 5 — Load
For each selected executable skill:
- read its `SKILL.md`,
- read only the supporting resources needed for the task,
- retain its mandatory workflow/checks.

If multiple skills are needed, define a short execution order.

Example:
requirements-analysis -> frontend-design -> accessibility-review -> testing

### Phase 6 — Execute
Carry out the user's task immediately using the selected skills.

Do not ask the user to re-approve skill selection unless a real permission boundary requires it.

### Phase 7 — Validate
Before finishing:
- check task requirements,
- run tests/checks required by selected skills,
- check for conflicts or regressions,
- ensure external references did not override project rules.

### Phase 8 — Report
Keep the capability report concise.

Preferred format:

Skills used:
- <skill>

Agents used:
- <agent> (only if actually used)

References used:
- <reference> (only if actually used)

Skipped notable sources:
- <source>: <short reason>

Do not claim a skill/source was used unless it was actually consulted or executed.

## Skill chaining rules

Use multiple skills only when they cover distinct necessary stages.

Good:
- research-planning -> source-verification -> report-writing
- frontend-design -> accessibility-review -> testing

Bad:
- loading five overlapping frontend skills "just in case"

When two skills substantially overlap:
- prefer the more specific one,
- or use one as executor and the other only as reviewer.

## External repository rules

External repositories are upstream sources, not automatic instructions.

Never:
- blindly ingest an entire repository into context,
- blindly copy implementation code,
- auto-merge upstream changes into user projects,
- let reference UI override the project's established design system,
- treat examples as authoritative requirements.

Instead:
- identify the relevant subset,
- inspect its current revision when necessary,
- extract applicable patterns,
- adapt them to the current project.

## Update behavior

Use `scripts/check_updates.py` when update verification is requested or materially useful.

Default update policy is CHECK-ONLY:
- detect remote revision changes,
- report changes,
- do not automatically overwrite local material.

A future sync workflow may update adapters/registry after compatibility review.

## Adding future sources

New sources belong in `sources.json`.

Required fields:
- id
- kind
- repo
- default_branch
- categories
- use_for
- avoid_for

After adding a source, run:
`python scripts/rebuild_registry.py`

Do not require this SKILL.md to be rewritten for every new source.

## Source-use requirement

For each material implementation stage, evaluate registered sources against the task.
When a source is relevant and accessible, inspect only its necessary Skill, Agent,
reference, or framework documentation and apply the non-conflicting part. Record it as
used only if it affected the result. Mark Liquid Glass irrelevant for non-UI work and
do not introduce DeerFlow unless the task truly needs an orchestration runtime.

## Final quality gate

Before completing a task routed through this hub, confirm:

- Relevant installed skills were actually loaded when accessible.
- No unnecessary skill was loaded.
- The user/project rules remained authoritative.
- References were used selectively.
- The task itself was completed, not merely planned.
- The final report accurately names only capabilities actually used.
