# Nexus Upstream Source Registry

`config/upstream-source-registry.json` is Nexus's static provenance record for
reviewed upstream material. It is deliberately separate from the V1.2 planner,
local Skill catalog, and Host execution mappings. Reading it never clones,
downloads, installs, updates, imports, executes, or delegates upstream code.

Each entry records the requested review facts: source ID, exact repository and
commit (when a concrete repository exists), category, license, trust tier,
discovery source, review date, accepted/rejected components, and risk state.
Every component has a final non-escalating disposition:

| State | Meaning |
| --- | --- |
| `locally_usable_verified` | Existing local Skill matches a pinned upstream component hash and remains subject to normal Nexus selection/load checks. |
| `advisory_only` | An Agent role may inform a review; it cannot receive tool, shell, file-write, approval, artifact, or Host-execution authority. |
| `reference_only` | A pattern/library/framework is available for bounded human engineering reference, not execution. |
| `rejected_incompatible` / `rejected_deprecated` | Not permitted in the current architecture. |
| `license_decision_required` | No use, bundle, or redistribution until the owner reviews the license. |
| `unresolved` | A supplied URL was not a concrete repository and has no accepted component. |

## Reviewed sources

- `msitarzewski/agency-agents` is the canonical Agent catalog. Its reviewed
  architecture, code-review, and reality-checker roles are advisory only.
- `jnMetaCode/agency-agents-zh` is a localized overlay. Equivalent canonical
  roles are deduplicated semantically; China-specific roles remain advisory
  candidates only.
- `emilkowalski/skills` provides native Skill bundles. The pre-existing local
  `emil-design-eng` content hash matches the pinned source commit and can be
  selected for a genuinely relevant frontend/UI task. It has no R4/R5 Host
  mapping and is not relevant to Presentations enhancement.
- `Shubhamsaboo/awesome-llm-apps` is a reference library. Examples that need
  shell access, external models, credentials, or agent runtimes are rejected
  for Nexus runtime use.
- `rdev/liquid-glass-react` is a React library reference, not a Skill.
- `bytedance/deer-flow` is a multi-agent framework and Skill-review reference,
  not a Nexus dependency. Its runtime and install/update flows are rejected in
  R4/R5.
- `greensock/GSAP` is a frontend library under a license gate; it is not a
  Skill and cannot be bundled or imported until an owner license decision.
- `https://github.com/green` identifies an organization, not a repository. It
  is recorded as unresolved; no repository or component was accepted.

## Safety rules

1. A source URL does not create execution authority.
2. New components require a pinned commit, license review, per-component
   compatibility and risk assessment, semantic deduplication, and tests.
3. No upstream source may bypass the R4/R5 Host-owned artifact boundary or
   create an Agent runtime, arbitrary shell execution, automatic Skill
   installation/update, Remote MCP, or OAuth flow.
4. Future bounded candidate discovery must add `CANDIDATE_SOURCE` records
   first. It may not recursively crawl or automatically execute/install a
   discovered component.
