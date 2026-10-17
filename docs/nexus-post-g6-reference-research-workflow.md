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

## Phase B: reusable-reference discovery (0.2.0 source, not released)

One shared `classify_substantial_work` boundary now feeds Reference Research
and reusable-reference eligibility. It covers creation, redesign, refactor,
substantial fixes and meaningful extensions in English and Chinese. The 0.1.2
website cases, tiny/focused-repair skips, explicit opt-out and exact-spec
reduction remain regression controls. Equal-priority security/scope conflicts
produce HOLD before the library is read; reference matches never satisfy a
missing execution capability.

The local-data file is `<Nexus data root>/references/library.json`, normally
`%LOCALAPPDATA%/Nexus/references/library.json`, respecting the existing trusted
`NEXUS_DATA_ROOT` deployment override. No directory/file is created by planning.
The library has exactly `schema_version: nexus.reusable-reference-library.v1`
and `records`. Limits: 256 records, 1 MiB/file, 4 KiB/record; match payloads are
bounded to 8 KiB plus the fixed decision envelope, within existing MCP limits.

Each closed record contains `id`, `name`, public HTTPS `url`, `revision`, `tags`
(categories included as tags), `use_for`, `patterns`, `avoid_for`, `roles`,
`workspace`, `acceptance`, `approval_evidence`, `license`, `license_evidence`,
`reuse`, `last_checked_at`, `compatibility`, and `provenance`. Fields are bounded
plain data. Local paths, secret-like assignments and unknown fields are rejected.
URLs reject credentials, query strings, encoded paths, local hostnames and
non-global literal IPs. No DNS lookup occurs during planning: the Host must
recheck public destinations and redirects with its supported research tools.

`workspace` is a SHA-256 binding to the canonical workspace root, calculated
with `workspace_binding`, not a rebindable workspace alias. `shared` requires
explicit approval evidence. `accepted` denotes Host-accepted reference data,
not explicit user preference; `preferred` requires an explicit approval receipt.
Receipts are same-user provenance, not cryptographic authentication or authority.

`license` is `unknown|compatible|restricted|incompatible`; the evidence URL
identifies the license text/version to check. `reuse` is
`patterns_only|conditional_code_reuse|no_reuse`. Conditional code reuse requires
compatible-license evidence; stale/unknown compatibility downgrades matches
to patterns-only. An unknown check time or a check older than 30 days requires
revalidation; selecting a record never refreshes it. License evidence still
requires Host review for the actual intended use, attribution and restrictions.

Retrieval filters scope, rejected/incompatible/no-reuse records and conflicting
duplicate restrictions before relevance scoring. Ranking uses deterministic
task/tag/use-for overlap (including bounded Chinese aliases), then a small
explicit preference and freshness bonus, with stable URL/ID tie-breaks.
Known conflicting frontend/backend framework tags are excluded before scoring;
unmodeled compatibility restrictions still require Host review. Patterns
and names do not independently establish applicability. Duplicate canonical
URLs use one slot; conflicting revision/license/reuse metadata is excluded.
Each independent URL can fill only one comparison role: multiple labels on
one reference cannot impersonate the required multi-source comparison.
Exact-spec matches address official documentation or matched implementation,
compatibility, security/risk/API questions only.

Known and fresh references share the existing six slots. Retrieval reserves
space for missing official/mature-project/alternative roles and required
revalidation. The Host can supplement only unresolved gaps, at most three
queries and 120 seconds, within existing permissions. Role coverage is an
advisory sufficiency hint, not evidence of completed research. Empty, missing,
oversized or invalid libraries expose a bounded status and safely retain the
existing Host research/original-design fallback. No stored reference is
mandatory; no default reference is seeded or imported from historical evidence.

### Explicit Host enrollment/update

Only a separately authorized Host action calls `host_upsert(record,
authorized=True, expected_sha256=<prior snapshot digest>, data_root=<trusted
local root>)`. Initial creation uses `expected_sha256=None`; it cannot overwrite
an existing library. The data root must already exist. The helper validates
the complete record/library, checks the prior digest, serializes cooperating
writers with an exclusive lock, and atomically replaces a flushed same-directory
temporary file. It refuses invalid/oversized libraries, conflicting updates and
unsafe filesystem targets rather than repairing them. A failed/crashed writer's
remaining lock is HOLD for explicit review, never automatically removed.

This API has no MCP write endpoint, CLI auto-enrollment, completion hook,
background crawler, embedding/vector dependency, or Project Memory integration.
The same-user guard is not universal Host isolation or a new security boundary.
Distribution 0.2.0 is an additive feature release; accepted 0.1.2 artifacts/tags
and frozen G1–G6/N01/PREAUTH records remain unchanged.
