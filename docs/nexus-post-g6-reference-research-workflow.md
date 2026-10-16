# Post-G6 Default Reference Research Workflow

This additive workflow extends the existing V1.2 `ash.v2` planner after the
frozen `nexus-v2-g6-final` baseline. It is not a new roadmap milestone, planner,
research platform, or execution/security architecture. G2, G3, G4, G6 and
their tags and evidence remain unchanged.

## Planning and routing

For a new project or substantial project change, `ash.reference_research`
classifies the task as `required`, `reduced`, or `skipped`. The V2 planner
serializes the result in `ExecutionPlan.reference_research` and the existing
stateless plan handoff. When research is active, the execution plan places a
`reference-research` step before project contribution steps. It reuses the
existing trusted applicability and selected-Skill loader to attach at most one
compatible research Skill. If none is available, the stage stays in the plan
for native Host research; selection failure does not block the project.

The R2 Nexus MCP remains a local planning/handoff interface. The new record is
data-only: it does not browse, access GitHub, download code, install resources,
or execute a Skill. The Host carrying out the existing handoff performs the
research with its separately available public-source tools before implementation.
The V1.1 router/run path and unrelated tasks are unchanged.

## Trigger and skip rules

- `required`: an explicit new project or substantial build, architecture,
  refactor, redesign, rebuild, or expansion request.
- `reduced`: an active project trigger accompanied by a complete/exact spec,
  acceptance criteria, a provided architecture/design, or an exact technology
  choice. Research addresses unresolved compatibility, implementation, and risk
  points only.
- `skipped`: explicit external-research opt-out, a simple non-project task,
  focused bug repair, or small copy/color/button/typo change.

The trigger and opt-out vocabulary also recognizes common Simplified Chinese
project and scope phrases.

Classification is conservative and lexical; it is a planning default, not a
permission grant. Users can always explicitly opt out or provide the complete
specification.

## Research policy

The brief prefers official documentation for implementation facts, followed by
GitHub repositories, relevant public products/projects, and community evidence
when useful. The default comparison covers one mature relevant project, one
alternative implementation, and one official or otherwise authoritative source.
The candidate limit is six. Stop when the brief can answer mature patterns,
best-fit direction, material pitfalls, and reuse/license constraints.

Compare relevance, maintenance, documentation, releases/tests, license,
compatibility, security posture, and operating cost. Unknown or unclear licenses
permit learning patterns only; they prohibit direct code reuse. Do not clone or
rebrand one reference. Extract patterns, compare tradeoffs, then synthesize an
approach fitted to the current user, repository, environment, scope, and budget.

The reference intelligence brief records the problem, references and tradeoffs,
reusable patterns, approaches to avoid, license constraints, technical risks,
recommended direction, fit to scope, and what Nexus will design differently.
It must distinguish reference-derived ideas from Nexus-designed decisions.

Research never expands permissions. A pattern requiring elevated privileges,
production credentials, a new trust model, or a frozen milestone boundary is
out of scope, is marked `HOLD`, and requires an owner decision before that
approach is used. Ordinary project implementation continues within existing
authority when a safe in-scope direction remains available.

## No suitable reference fallback

If the bounded search finds no sufficiently relevant, trustworthy, compatible,
or license-suitable reference, retain that conclusion. Prefer official sources,
standards, and currently verified capabilities; design the remaining solution
from the user's goal, existing architecture, stack, security boundary, and
budget. Label reference-derived and Nexus-designed choices separately. Then
continue through PLAN, BUILD, TEST, and VERIFY. Missing references never block
project startup and never justify an unlimited search loop.

## Evidence and known limitation

The plan proves that the stage, source policy, synthesis fields, selected
research Skill (if any), and ordering dependency were prepared. It does not prove
that a Host actually searched, that a reference is current, or that synthesis
was completed. Such completion requires Host-side source observations and a
brief in the normal execution evidence. The Nexus planner itself performs no
network requests.
