# Nexus Roadmap V2 Companion Architecture Addendum v1

Document ID: `nexus.pre-g2.architecture-addendum.v1`

Version: 1.0.0

Status: **ACCEPTED — ARCHITECTURE ONLY — NO RUNTIME AUTHORITY — G2 NOT STARTED**

Accepted by the owner on 16 September 2026 in the explicit architecture-acceptance request. This separately versioned companion adopts the Pre-G2 Architecture Delta Review direction and the exact A0–A6 clarification text below. It does not authorize implementation in this acceptance step.

## Immutable references and acceptance scope

- Historical Roadmap V2: `docs/nexus-roadmap-v2.md`, frozen tag `nexus-roadmap-v2-final`, commit `f92b96ea01b8e32dac8bc1d51819bf0c58d55659`.
- Frozen G1: `nexus-v2-g1-final`, commit `a8ffe1e743d8106495cb260124b044fa5d8e619f`.
- Frozen Slice 3C: `post-r5-runtime-integration-slice3c-final`, commit `10b802073861fe4991b3a3789609a8161169f499`.
- Frozen R2/R4/R5 surfaces, existing commits and tags remain unchanged. Historical status text is preserved; this companion records the subsequent architecture decision.
- No phase, dependency or authority category is added. All original security, provenance, authorization, evidence, fail-closed, regression, independent-review, owner-acceptance and freeze requirements remain applicable.
- This addendum grants **no execution, installation, activation, approval, delegation or concurrency authority**. Architecture acceptance is not a capability approval, a task grant, executor qualification, G2 implementation acceptance or release authorization.

## Accepted source identity

The original review artifacts remain unchanged in the external review evidence directory `nexus-pre-g2-delta-review-2026-09-15`. They are not runtime inputs or package members. Their original proposed/review-only status records the earlier stage and is not rewritten.

| Accepted input | SHA-256 of original bytes |
|---|---|
| PRE-G2-ARCHITECTURE-DELTA-REVIEW.md | `8f3a60195735f2bf8b261bf98d6f01de7263abb15ccc66df60aca7367beffa35` |
| PROPOSED-ROADMAP-V2-ADDENDUM.md | `77d6b46f97e6325400abdc795d0069f7b8114bf8bd111d3198610e83b57a5410` |
| AGENT-AND-SKILL-UTILIZATION.md | `d2d1d458410a73c67d43c9446cb32a444a2886dfbbdd9dab53e21e5544e103f5` |

The A0–A6 section below is reproduced exactly as UTF-8/LF text from the accepted proposal. Only the surrounding document identity, acceptance metadata and disposition differ. Documentation remains dated capability evidence, never proof of current Host enforcement. The original official-source cache and retrieval indexes remain external and immutable for this acceptance.

## A0. Status companion to Section J

> G1 is frozen at `nexus-v2-g1-final`, commit `a8ffe1e743d8106495cb260124b044fa5d8e619f`. The historical roadmap retains its original freeze-time status. The next proposed activity is bounded G2 design after acceptance of this architecture delta; G2 implementation has not started. Neither this addendum nor G1's read-only pilot authorizes or qualifies a new execution path.

## A1. Clarification of Section B shared rules

> Nexus owns portable governance contracts and their deterministic validation. Qualified Hosts own generic agent loops, tool/Skill execution, native lifecycle and orchestration, environment execution, context compaction, and browser/computer operation. Nexus must not implement parallel generic engines for those responsibilities. A narrow integration adapter and the roadmap's domain records remain in scope. No particular provider or model name becomes a mandatory dependency or a hidden selection rule.
>
> Official documentation and advertised capability establish candidates for investigation, not execution authority or enforcement. Preserve `visible != permitted != trusted != binding_verified != prerequisites_ready != executable`. Profiles, observations, conformance records, selection decisions, prompts, personas and compacted context cannot issue grants. A mandatory unknown or unenforced restriction remains ineligible; hard eligibility precedes cost optimization; unknown money is not zero; forbidden fallback remains forbidden.

## A2. Clarification of G2 fields 4, 7–12 and its recovery/budget/termination rules

> Keep G2 as governed sequential execution around an existing qualified Host executor. Reuse GovernedExecutionContract, TraceEvent, BudgetRecord, CheckpointRecord and StopRecord. Where relevant, those records must bind the effective model/Host/tool configuration, policy and independently issued authority to supported Host session/turn/call references, input/artifact identities, observation coverage and unresolved effects. Store no credentials or hidden chain-of-thought in these records. Native identifiers are correlation data, not grants.
>
> Before dispatch or resume, establish a non-bypassable boundary for the admitted operations and resources. That boundary may be application/tool enforcement, qualified Host enforcement over the complete execution unit, or their demonstrated combination; Nexus need not intercept every internal primitive when equivalent controls are proven. Qualification must include deferred tool discovery, programmatic calls, scripts, MCP paths and any transitive execution. A root-only check, post-hoc trace or instruction to comply is insufficient. Prohibited delegation and parallelism must remain prohibited on indirect paths. If mandatory controls cannot be established, reject that binding for the task; do not broaden permissions, silently switch executors or build a generic runtime as a workaround.
>
> Reuse native continuation, cancellation and supported observation APIs. Persist only the ordered domain facts necessary for authority, reservations, accepted artifacts, validation and unresolved work/effects; do not mirror entire Host transcripts or implement another session scheduler. Reconcile event gaps and external effects before unsafe retries. Host idle/completed state, a restored conversation or a compacted context item does not establish task acceptance, renewed authority or artifact recovery. Process-local trust seals cannot be restored from a durable identifier or serialized profile.
>
> Preserve the existing reserve → dispatch → settle/reconcile → release lifecycle and distinct stop states. Native usage may be incomplete or revised; treat cost uncertainty explicitly. A Nexus ledger records exposure and cannot by itself enforce an external spending ceiling. Mandatory hard limits require a qualified bound; otherwise apply the existing ineligibility rule. Stop further dispatch separately from requesting/acknowledging cancellation, resolving effects and settling cost. Timeout, disconnect or cancellation must not erase unresolved exposure. The global Nexus budget remains limited to Nexus-managed dispatches.
>
> The first G2 acceptance must use one positively qualified binding and already accepted capabilities, demonstrate a useful bounded workflow, and exercise interruption/reconciliation and containment failures. G1 route-pilot success is not that qualification. G2 does not depend on future G3 approvals for existing accepted capabilities and valid task authorization. Its separately accepted dispatch integration must not modify the frozen R2/R4/R5 or Slice 3C surfaces or acquire installation, activation, candidate-approval, delegation or concurrency authority.

## A3. Clarification of G3 fields 4, 5 and 8

> Retain the separate authorization plane after immutable quarantine and review. Host OAuth, connection consent, installation, discovery or enablement does not approve a capability revision and does not replace task authority. Use existing qualified identity, credential and installation facilities where appropriate, while Nexus retains approved-subject identity, independent issuance, scope, expiry and revocation. Any installation or activation action requires separately valid authorization; this addendum grants none. Do not build a universal identity, secret-management, marketplace or installation platform.

## A4. Clarification of G4 fields 4, 5, 8 and 11

> Keep small project decision/constraint records, ContextManifest, change-impact evidence and workflow acceptance. Delegate generic retrieval, analysis, authoring, rendering, browser execution and compaction to qualified Host facilities. Treat conversational summaries and opaque compacted context as derived inputs, not authoritative policy or project decisions. A continuation brief must preserve source references, scope, omissions, freshness and supersession; changed constraints require their existing authorized confirmation. Do not build a universal memory store, vector database, transcript archive, context compressor or code-intelligence platform.

## A5. Clarification of G5 fields 4, 5, 8–12 and 16

> G5 is optional governance over native delegation, not a second orchestration runtime. Keep the existing delegation contracts, bounded dependency/resource representation, conserved grants/budgets and merge/cancellation evidence; delegate lifecycle, scheduling, messaging and execution. A BoundedDAG is a bounded validation contract, not authorization to implement a general DAG scheduler.
>
> Enable G5 only if the chosen binding demonstrates the required child-specific attenuation, resource ownership, cancellation and observable accounting, including indirect descendants. Shared filesystems, inherited credentials, parent-level controls, concurrency limits and persona instructions do not independently prove those properties. No-Agent mode must prevent delegated dispatch, not merely request abstention. A pre-registered experiment must demonstrate worthwhile value over both sequential Nexus and a contemporary native Host baseline with relevant native subagent capabilities enabled under comparable constraints. If enforcement or value is insufficient, omit/disable G5; G6 may qualify the sequential product without it.

## A6. Clarification of G6 tests and the existing value experiment

> Preserve the full original qualification and freeze gates. Add native-boundary cases for deferred/indirect tool admission, transitive delegation, effective-configuration drift, observation gaps, compaction-related constraint loss, resume after revocation, cancellation/late effects, unknown or revised cost, and whole-path privacy. Bind results to exact supported configurations. A refusal-only matrix does not satisfy declared useful success, including the existing local/private requirement. Distinguish capability performance from governance correctness.
>
> Compare against a contemporary native Host using relevant available features with equivalent inputs, permissions, constraints and acceptance criteria; do not weaken the comparator to manufacture Nexus value. Register metrics, thresholds and stopping rules before the experiment. Retain functionality only where value and governance evidence support it. Existing requirements for genuine Critical/High resolution, independent review, affected/full regression, exact-artifact approval, release integrity and authorized freeze remain unchanged.

## Accepted disposition

The owner has accepted this companion as the Nexus V2 architecture direction. It is effective only as an architecture constraint on separately authorized future work. G2 implementation remains NOT STARTED. The acceptance record, validation scope and exact recommended fresh-session handoff are in `docs/nexus-pre-g2-architecture-acceptance-v1.md`.
