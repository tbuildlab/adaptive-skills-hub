# Nexus Roadmap V2 — Post-Slice-3C Model-Agnostic Rebaseline

**Status:** OWNER ACCEPTED — PASS

**Owner acceptance date:** 2026-09-13

**Scope:** Architecture and remaining-roadmap documentation freeze only

**Freeze tag:** `nexus-roadmap-v2-final`

**Implementation status:** G1 NOT STARTED; no G1–G6 capability is implemented or qualified by this freeze.

This is the authoritative remaining roadmap after the frozen Post-R5 Slice 3C
foundation. It preserves the owner-accepted Sections A–J and design-stage
utilization report. Formalization changes are limited to acceptance status,
document structure, portable source references and historical-context labels.

The owner accepted the design from the task **Design Nexus Roadmap V2** after
the **Model & Host Capability Allocation Review**. Acceptance of this plan does
not satisfy any future implementation, authority, conformance, security or
release gate. G1 is the only recommended next implementation slice; it requires
a subsequent implementation instruction. G5 remains optional/conditional, and a
sequential Nexus may graduate without G5 when its enforcement/value gates do not
justify delegation or concurrency.

Historical roadmap numbering and proposals remain historical evidence. Frozen
completed milestone contracts and tags retain their existing authority.
Roadmap V2 governs future work; it does not change Slice 3C, its source policy,
quarantine dispositions or zero-authority boundary.

The documentation-freeze tag identifies this accepted plan, not implementation
of G1 or the G6 Production Security Freeze. Its annotated tag object identifies
the exact documentation commit and records the resulting MANIFEST SHA-256.
No prior frozen tag may be moved.

**Recommendation: adopt five required slices and one conditional delegation slice.** Build a small, model-agnostic control plane around capability eligibility, enforceable execution boundaries, evidence, recovery and acceptance. Qualify a limited set of useful workflows before expanding coverage.

This is the owner-accepted design. It grants no implementation, installation, capability-approval or execution authority.

The design review verified the following frozen foundation. These are the pre-roadmap baseline identities, not the later documentation-freeze commit:

| Item | Verified local result |
|---|---|
| HEAD and `main` at the design baseline | `10b802073861fe4991b3a3789609a8161169f499` |
| Frozen tag | `post-r5-runtime-integration-slice3c-final` |
| Tag object | `f24e3538120019cbcef100d233edb24ca9ec383d` |
| Tag target | Same acceptance commit |
| MANIFEST SHA-256 | `a3347b2f8098209bfa31e28df74ab8806950e1ea92689416f281cdf69b1ebee8` |
| Working tree and index | Clean; no tracked or untracked changes reported |

Evidence classifications below describe the design review as of 2026-09-13. Public observations are dated evidence, not continuing certification. `FUTURE PROPOSAL` identifies future implementation and qualification within this accepted plan:

- **VERIFIED CURRENT FACT:** the local checks above, inspected source contracts, the current Meranti postmortem, and specifically cited public documentation.
- **OWNER-SUPPLIED FACT:** remote acceptance/merge status, acceptance of the allocation review, and the completed storage-audit decision. These were not independently re-audited.
- **ARCHITECTURAL INFERENCE:** the proposed allocation of responsibilities and the reasons for retaining or removing work.
- **FUTURE PROPOSAL:** every new slice, schema, integration, experiment, acceptance test and tag below. None has been implemented or qualified.

The primary architectural input was retrieved from **“审查模型与主机能力分配”**. Its recommendations govern this rebaseline; historical research observations remain historical evidence.

## SECTION A — EXECUTIVE ROADMAP

| Slice ID | Name | Main outcome | Complexity | Dependency |
|---|---|---|---|---|
| **G1** | Capability Profiles and Executor Conformance | Determine which capabilities are suitable, permitted and sufficiently enforceable for a task; explain exclusions truthfully. | MEDIUM | Frozen foundation |
| **G2** | Governed Sequential Execution and Recovery | Complete one bounded workflow with trustworthy evidence, budget reservations, interruption recovery and controlled termination. | HIGH | G1; a positively qualified execution binding |
| **G3** | Separate Capability Authorization | Bind owner approval, revocation and registration to exact quarantined components without changing Slice 3C. | HIGH | G1; G2’s durable record infrastructure; frozen Slice 3C |
| **G4** | Evidence-Led Domain Workflows | Qualify Website and Source-backed Report workflows using small context, decision-memory, relationship and change-impact contracts. | MEDIUM | G2; G3 when introducing external capabilities |
| **G5** | Bounded Delegation and Concurrency | Enable limited delegation only where enforceable controls and measured benefit justify it. | HIGH — CONDITIONAL | G2, G4; G3 for external components/personas |
| **G6** | Governance Qualification and Production Security Freeze | Prove supported configurations, value over native Host use, security and release readiness. | HIGH | G3, G4; G5 only if shipped enabled |

**G5 is optional.** A sequential Nexus can graduate. Its release must explicitly state that delegated/concurrent execution is unsupported or disabled.

The required architecture areas are allocated as follows:

| Required areas | Destination |
|---|---|
| A–C: Model profiles, Host profiles, conformance | G1 |
| D–G: Trace, recovery, accounting, termination | G2 |
| H–J: Scoped memory, relationships, change-impact evidence | G4 |
| K–L: Delegation and concurrency governance | G2’s single-executor contract, extended conditionally in G5 |
| M: Post-quarantine authorization | G3 |
| N: Domain Workflow Packs | G4 |
| Substitution, comparative value, accumulated security and release qualification | Introduced in the relevant slices; consolidated in G6 |

The target flow remains:

```text
User Goal
→ Requirements / Constraints
→ Nexus Policy
→ Capability Intelligence
→ Trust / Permission / Privacy / Budget
→ Allowed Capability Pool
→ Execution Strategy
→ Replaceable Execution Engine
→ Evidence
→ Validation
→ Recovery / Replan
→ Acceptance / Stop
```

Models and Hosts perform the substantive execution. Nexus owns the portable decisions and records needed to govern that execution.

## SECTION B — DETAILED SLICE SPECS

All six specifications share these rules:

1. **Extend through separate, versioned boundaries.** Preserve V1.1/V1.2, R1–R5 and Slices 1–3C. New execution contracts must not broaden existing read-only MCP tools, the Presentations mapping or the advisory Agent schema.
2. **Try deterministic execution first.** Models do not calculate authoritative hashes, resolve permission grants, manufacture immutable identities, settle budgets or approve their own evidence.
3. **Filter before optimizing.** Select the lowest expected-total-cost suitable capability only after hard policy, trust, privacy, enforcement and acceptance requirements pass.
4. **Authority comes from an authorized issuer and enforceable boundary.** Profiles, prompts, discovery results, graph edges and validation PASS cannot create it.
5. **Preserve uncertainty.** Unknown mandatory facts make an execution path ineligible. Missing observations are recorded as missing.
6. **Freeze evidence against exact subjects.** Changed inputs, components, relevant configuration or acceptance criteria invalidate affected evidence.
7. **Keep storage portable.** New Nexus-controlled storage should use a configurable, repository-external location, preferring D: on this machine where safely supported. Host-managed storage stays in supported locations. No portable contract hard-codes this machine’s paths. Slice 3C CAS relocation and broad cleanup remain deferred.

The authority distinctions remain explicit:

```text
local presence != trust
discovered != admitted
admitted != approved
approved != routable
routable != executable
loaded != executed
Agent persona != permission
evaluation PASS != execution authority
model recommendation != implementation
implementation != validation
validation != approval
```

Every future freeze requires scoped acceptance evidence, relevant frozen regression checks, resolved security findings, owner acceptance and an immutable tag bound to the accepted commit and manifest. Proposed tag names below are placeholders; no tags were created.

### G1 — Capability Profiles and Executor Conformance

| Required field | Specification |
|---|---|
| **1. Name** | Capability Profiles and Executor Conformance |
| **2. Objective** | Produce a bounded allowed-capability pool and auditable selection/refusal decision for a real task class, without introducing product dispatch authority. |
| **3. Why Nexus must own this** | Cross-Host governance needs consistent distinctions between capability claims, current availability, permissions, trust and enforcement. A Host’s self-description cannot substitute for those decisions. |
| **4. Deterministic work** | Validate versioned profiles and evidence; resolve policy intersections/conflicts; check identity, freshness, prerequisites and enforcement coverage; calculate eligibility; compare suitable strategies using explicit cost assumptions. |
| **5. Delegated work** | Hosts report capabilities and expose observations. Models may propose decomposition, identify ambiguity and explain suitability. Existing authorized tools perform bounded conformance probes. Their reports remain evidence inputs. |
| **6. Reused foundation** | V1.2 bounded planning; Slice 1 capability records and minimum-sufficient selection; Slice 3A applicability/integrity gates; Slice 3B exact-subject evaluation; R5’s current-visible-subset semantics. |
| **7. New schemas/contracts** | **ModelCapabilityProfile:** provider/model/deployment identity, configuration and adapter fingerprint, separately sourced claimed/measured/Host-reported/runtime-observed capabilities, limitations, cost/latency distributions, deployment/privacy facts, validity and freshness. **HostCapabilityProfile:** surface identity, observation scope, bindings, prerequisites and separately represented availability/permission/trust facts. **ExecutorConformanceRecord:** each restriction, enforcing layer, covered operations, configuration binding, test evidence, limitations and expiry. **SelectionDecision:** policy/requirement references, eligible/rejected candidates, suitability evidence, cost basis and chosen strategy. Profiles carry no grants. |
| **8. Security/authority boundary** | A successful probe proves only its declared coverage. Prompt instructions do not establish filesystem, network, model-selection, budget or cancellation enforcement. Unverified mandatory controls block the relevant path. No private Host-state scraping. |
| **9. Tests** | Deterministic-only operation; visible-but-forbidden and trusted-but-unavailable cases; forged/stale profiles; model/configuration substitution; alias ambiguity; missing bindings; policy conflicts; false enforcement claims; unknown monetary costs; forbidden fallback; preservation of existing selection limits and routing behavior. |
| **10. Acceptance criteria** | Equivalent facts produce equivalent decisions regardless of model names. Every mandatory restriction has sufficient enforcement evidence or an explicit refusal. At least one narrowly defined pilot binding must pass conformance before G2 can claim governed execution through it. |
| **11. Explicit non-goals** | A model gateway, provider benchmark leaderboard, universal inventory, global Host interception, new executor, execution approval or comprehensive certification of every Host feature. |
| **12. Dependencies** | Frozen foundation and authorized access to bounded test environments. No external ecosystem package is required. |
| **13. Ecosystem candidates** | Codex as a Host/reference candidate; Agent Skills as an interoperability reference. Other sources remain optional evidence or later candidates. |
| **14. Complexity** | MEDIUM. The principal uncertainty is obtaining trustworthy conformance evidence, not storing profile data. |
| **15. Creates runtime authority?** | **No.** It establishes eligibility and conformance decisions. Tests use independently authorized Host facilities. |
| **16. Freeze/tag gate** | Freeze only after profile, substitution, refusal and conformance evidence pass, with the supported pilot scope stated precisely. Proposed tag: `nexus-v2-g1-final`. |

Host capability facts must remain separate:

```text
documented_possible
visible_now
permitted_now
trusted_for_this_use
binding_verified_now
prerequisites_ready_now
executable_now
```

These are independently changing facts, not an installation ladder. Eligibility additionally depends on task suitability, budget and required enforcement.

Use three integration classifications, evaluated **per relevant restriction**:

| Classification | Permitted claim |
|---|---|
| **ADVISORY** | Nexus recommends and evaluates observable results; adherence to unenforced restrictions is not guaranteed. |
| **GOVERNED_HANDOFF** | Scope and evidence are bound to a reviewed Host operation; guarantees cover only that operation and its verified controls. |
| **ENFORCED_INTEGRATION** | Mandatory restrictions are implemented at verified execution boundaries covering the relevant actions. |

Official documentation distinguishes sandbox enforcement from approval policy. That distinction supports this design; it does not certify this session, whose supplied permissions expose unrestricted access. [Sandbox documentation](https://learn.chatgpt.com/docs/sandboxing)

Cost comparison uses:

```text
expected execution cost
+ expected retries
+ validation
+ context preparation/transfer
+ tools/infrastructure
+ expected human recovery
```

Unknown cost is never zero. Comparisons need a dated basis, uncertainty and a defined suitability threshold. A strict ceiling requires an enforceable bound; estimate-based operation is eligible only when policy permits it.

### G2 — Governed Sequential Execution and Recovery

| Required field | Specification |
|---|---|
| **1. Name** | Governed Sequential Execution and Recovery |
| **2. Objective** | Complete and recover one bounded, sequential workflow using already accepted capabilities. Preserve sufficient state to explain success, failure, interruption and unresolved effects. |
| **3. Why Nexus must own this** | Cross-engine acceptance, accounting and recovery must survive a conversation or executor replacement. Native session continuation alone does not establish artifact integrity, remaining authority or external-effect outcome. |
| **4. Deterministic work** | Validate dispatch scope; reserve and settle budgets; maintain ordered state/events; bind results to subjects; enforce retry/replan limits; select recoverable steps; preserve accepted artifacts; stop further dispatch when required. |
| **5. Delegated work** | Host/model reasoning, repository work, artifact generation, Skill execution, browser/tool actions, native cancellation and checkpoint operations. Hosts or external systems provide execution/effect observations. |
| **6. Reused foundation** | G1; existing accepted capabilities; Slice 3B evaluation; R4/R5 handoff and receipt distinctions; existing quality-loop bounds and copy-on-write principles where applicable. Existing protocols remain unchanged. |
| **7. New schemas/contracts** | **GovernedExecutionContract:** task/objective, input scope, allowed operations/resources, capability/profile references, independently issued grant reference, acceptance version, budget, cancellation and effects. **TraceEvent:** task/plan/attempt/parent IDs, event sequence, policy and profile references, operation, source, result, evidence binding and observation gaps. **BudgetRecord:** allocation, reservation, dispatch, usage, reconciliation and release. **CheckpointRecord:** input/artifact identities, completed validation, pending work, current policy references and unresolved effects. **StopRecord:** best artifact, validation state, remaining work, consumed/reserved budget, effects and stop reason. |
| **8. Security/authority boundary** | Validate existing user/Host authorization before dispatch, resume and consequential effects. Durable identifiers correlate work; they cannot restore expired grants or process-local seals. Missing effect evidence blocks unsafe retry. This new integration remains separate from frozen R2/R4/R5 surfaces. |
| **9. Tests** | Crash before/after reservation, dispatch, effect completion, receipt and settlement; quota interruption; duplicate receipts; replay; cancellation races; late results; changed inputs; permission revocation; forged observations; budget exhaustion; unknown spend; exhausted recovery allowance; no-progress repair loops. |
| **10. Acceptance criteria** | A bounded real workflow completes with subject-bound validation. Injected interruption preserves validated work. Unknown effects remain unresolved until reconciled. Retries cannot reset limits. Cancellation stops new dispatch and records acknowledgement separately. No pending exposure is released merely because a timeout occurred. |
| **11. Explicit non-goals** | Universal exactly-once effects, process/VM snapshots, a general Agent Runtime, distributed workflow services, arbitrary external capabilities, concurrent execution, universal rollback or an account-wide billing system. |
| **12. Dependencies** | G1 and a positively qualified binding. Initial workflows use existing accepted capabilities, so G2 does not depend on future candidate approval in G3. |
| **13. Ecosystem candidates** | Codex as an optional execution Host; DeerFlow and Edict as reference patterns. No imported runtime is required. |
| **14. Complexity** | HIGH, concentrated in durable ordering, receipt provenance, cancellation and uncertain-effect reconciliation. |
| **15. Creates runtime authority?** | **Yes, a narrowly scoped dispatch integration after separate implementation/boundary acceptance.** It consumes valid task authority; it cannot invent permission or approve capabilities. Nothing is activated by this roadmap. |
| **16. Freeze/tag gate** | Require an actual bounded success, fault-injection evidence, budget/recovery invariants and unchanged frozen boundaries. Proposed tag: `nexus-v2-g2-final`. |

Use one local transactional ledger initially; a standard-library SQLite implementation is the recommended starting proposal. Keep artifact bytes in approved Host/local storage and reference them from the ledger. Validate durability and access boundaries before acceptance. Avoid a new database service, transcript mirror or observability platform.

Record observable events:

```text
Task → Plan → Capability Selection → Policy Decision
→ Delegation/Handoff → Tool Call → Result → Validation
→ Retry/Replan → Completion/Stop
```

Policy filtering occurs before ranking; the dispatch policy decision rechecks current authority. Record concise decision explanations and evidence, never hidden chain-of-thought.

Execution claims must distinguish model-reported, Host-observed and externally confirmed results. Hashes bind bytes; they do not prove that an operation happened or authenticate the issuer. Current MCP diagnostics are explicitly non-retained, so this ledger is an additive contract, not a relabelling of existing telemetry. [Telemetry source](../ash/mcp/telemetry.py#L1)

Recovery distinguishes:

| Recovery concern | Required behavior |
|---|---|
| Conversation continuation | Reconstruct a bounded continuation brief from valid records. |
| Artifact rollback | Restore a known artifact only through a qualified checkpoint mechanism. |
| Durable task recovery | Reconcile completed, pending and invalidated work against current inputs and authority. |
| External-effect reconciliation | Determine whether an action happened before deciding whether repetition is safe and authorized. |

Budget lifecycle:

```text
Reserve → Dispatch → Settle/Reconcile → Release
```

Support global Nexus-managed, task and future delegation budgets across tokens, knowable money, time/compute, iterations, retries and fan-out. The global pool covers Nexus-managed dispatches; it cannot silently account for unrelated native Host usage.

Retain a bounded validation/shutdown allowance. Effect reconciliation and budget settlement are separate: knowing that an effect happened does not establish its final cost. Timeout, disconnect or lease expiry does not automatically release a reservation.

Termination includes acceptance satisfaction, user cancellation, revocation, exhausted limits, infeasibility, missing mandatory evidence and unresolved effects. Distinguish:

```text
STOP_REQUESTED
DISPATCH_STOPPED
CANCEL_ACKNOWLEDGED
SETTLED or OUTCOME_UNKNOWN
```

Late results cannot automatically overwrite the retained artifact. Budget exhaustion is a stop reason, not task completion.

### G3 — Separate Capability Authorization

| Required field | Specification |
|---|---|
| **1. Name** | Separate Capability Authorization |
| **2. Objective** | Support explicit, revocable approval and registration of an exact reviewed component while preserving Slice 3C’s permanent quarantine-only boundary. |
| **3. Why Nexus must own this** | Nexus must prevent discovery, review results and registration from being mistaken for approval or execution permission across different Hosts. |
| **4. Deterministic work** | Revalidate immutable subject/evidence bindings; verify the approval issuer; enforce approval scope and validity; process revocation; produce bounded registration projections; check current routability independently. |
| **5. Delegated work** | The owner or explicitly authorized reviewer decides approval. Specialists may analyze license/security uncertainty. Optional scanners run only through separately approved, isolated validation facilities. |
| **6. Reused foundation** | Slice 2 provenance-aware discovery; Slice 3C immutable subjects and quarantine evidence; Slice 3B evaluation; Slice 3A applicability; G1 eligibility; G2 durable records. |
| **7. New schemas/contracts** | **CapabilityApprovalRecord:** exact component/revision/tree identity, intake-policy identity, review-evidence references, permitted use, constraints, issuer, authenticated approval evidence, validity and revocation relationship. **RegistrationRecord:** approval reference, exact capability identity, reviewed applicability and execution-mechanism metadata. **RevocationRecord:** affected approvals/subjects, effective scope and reason. These records live outside Slice 3C. |
| **8. Security/authority boundary** | Slice 3C never gains `APPROVED`. Approval cannot be manufactured from candidate JSON, scanner PASS or model output. Registration grants no tool, install, MCP, Host or delegation authority. Creator-writable storage alone cannot authenticate an approval. |
| **9. Tests** | Wrong subject/revision; stale evidence; forged issuer; modified approval records; expired/revoked approval; changed license/dependencies; registry projection tampering; review-to-dispatch substitution; source-policy mismatch; approved-but-unavailable capability; malicious candidate attempts to enter routing. |
| **10. Acceptance criteria** | A benign controlled fixture can be separately approved and registered; execution still requires current eligibility and task authorization. A changed revision cannot inherit approval. Revocation blocks subsequent eligibility. Negative tests prove that Slice 3C remains non-authorizing. |
| **11. Explicit non-goals** | Editing Slice 3C states or manifests, blanket repository trust, automatic installation, auto-approval, automatic update adoption, runtime execution, organizational PKI or approving the roadmap’s candidate list. |
| **12. Dependencies** | G1, G2 record durability, accepted Slice 3C validation interfaces and a verified approval-origin mechanism. |
| **13. Ecosystem candidates** | All candidates may eventually supply review subjects or references. Actual intake remains limited by accepted source-policy coverage. SkillSpector is an optional isolated signal, never a trust authority. |
| **14. Complexity** | HIGH because it introduces a trust-increasing boundary and must resist forged approvals and subject substitution. |
| **15. Creates runtime authority?** | **Creates separate capability-approval/registration authority, but no dispatch or execution grant.** Implementing this plane requires explicit acceptance of its issuer and security boundary. |
| **16. Freeze/tag gate** | Require independent review of approval origin, subject binding, revocation and quarantine isolation. Proposed tag: `nexus-v2-g3-final`. |

The lifecycle remains:

```text
Capability Gap
→ Discovery
→ Immutable Observation
→ Provenance / License / Security
→ Slice 3C Quarantine
→ Review Evidence
→ Separate Approval
→ Registration
→ Routability
→ Execution Eligibility
```

The quarantine record remains a quarantine record after separate approval. A new revision creates new review obligations.

The current source policy contains the first eight named repositories in the user’s candidate list. It does not cover every future source. [Frozen source policy](../config/ecosystem-source-policy.json#L657)

Sources outside that coverage remain reference/WATCH candidates for executable adoption. They require a separately accepted, versioned intake extension or successor boundary. This is deferred work, not permission to modify frozen Slice 3C.

### G4 — Evidence-Led Domain Workflows

| Required field | Specification |
|---|---|
| **1. Name** | Evidence-Led Domain Workflows |
| **2. Objective** | Qualify two useful workflows—Website and Source-backed Report—while adding only the context, memory, relationship and impact records those workflows require. |
| **3. Why Nexus must own this** | Portable acceptance needs explicit decisions, source references, affected consumers and validation obligations. Repository understanding and artifact creation can remain with the executor. |
| **4. Deterministic work** | Compose policy restrictions; validate record scope/provenance/validity; filter retrieval; resolve supersession; validate typed relationships and dependencies; bind change-impact evidence to input snapshots; check acceptance coverage. |
| **5. Delegated work** | Repository analysis, coding, research retrieval, report writing, rendering, browser checks and semantic review. Hosts manage native context and compaction where suitable. Models may propose memory entries, relationships and validation cases. |
| **6. Reused foundation** | G1 profiles; G2 ledger and execution; G3 for newly adopted external capabilities; Slice 3A applicability; Slice 3B validation; existing Host Skills; Meranti evidence. |
| **7. New schemas/contracts** | **ProjectDecisionRecord:** confirmed decision/constraint, scope, source/evidence, approving authority, validity, proposed/confirmed/superseded/disputed state, supersession and retention class. **ContextManifest:** included sources, transformations, recipients, omissions and disclosure limits. **CapabilityRelation:** typed, version-bound endpoints with provenance. **ChangeImpactRecord:** repository identity, base commit, dirty/input snapshot, changed surfaces, dependencies/consumers, shared contracts, validation obligations and unexamined areas. **WorkflowPack:** version, applicability, required capabilities, domain policy and acceptance/evidence requirements. |
| **8. Security/authority boundary** | Retrieved memory and generated summaries do not become grants. Confirmation requires its authorized source. Cross-project retrieval is explicitly scoped. Domain packs may narrow superior permissions. Reduced observations remain derivative evidence, with originals accessible where required. |
| **9. Tests** | Memory poisoning/conflicts/staleness; unauthorized confirmation; namespace leakage; supersession and forgetting; omitted failures during reduction; forged graph edges; dependency cycles; dirty-tree substitution; missed shared consumers; boundary-state omissions; pack attempts to expand permissions. |
| **10. Acceptance criteria** | Both initial packs complete real bounded workflows with inspectable evidence. Relevant shared consumers and unexamined areas are recorded. Memory remains small, provenance-bearing and permission-scoped. Changing a pack does not require domain logic in planner core. Acceptance stops unnecessary further polishing. |
| **11. Explicit non-goals** | Universal memory, default embeddings/vector database, universal ontology, an LSP/IDE platform, generic code intelligence, eight fully implemented domain products, automatic memory confirmation or copying Meranti’s implementation choices into core. |
| **12. Dependencies** | G2. G3 is required only when adopting a new external component. The initial packs can use already accepted Host capabilities. |
| **13. Ecosystem candidates** | TencentDB memory patterns; granular Matt Pocock Skills; Tree-sitter if justified; UI UX Pro Max advice; Galaxy components; SoL-Pi observation/context patterns. All are optional. |
| **14. Complexity** | MEDIUM for the bounded two-pack scope. Broader domain coverage would be additional work requiring its own demonstrated need. |
| **15. Creates runtime authority?** | **No new authority category.** Work consumes existing qualified execution paths and explicit task permissions. |
| **16. Freeze/tag gate** | Qualify Website and Source-backed Report independently, including poisoning, impact and evidence-reduction tests. Proposed tag: `nexus-v2-g4-final`. |

The capability relationship vocabulary is deliberately closed:

```text
requires
uses
depends_on
conflicts_with
produces
validated_by
available_through
source_of
```

Relationships support planning; they cannot establish trust or permission. Unknown write/resource relationships require conservative sequencing.

Policy composition remains:

```text
General Nexus Policy
+ Domain Policy
+ Project Policy
+ Task Requirements
```

Hard restrictions compose by intersection. Soft preferences use explicit precedence. Contradictions must be surfaced rather than resolved by arbitrary overwriting.

Domain placement:

| Domain | Roadmap treatment | Principal evidence |
|---|---|---|
| Websites | **Initial qualified pack** | Shared interactions, consumer regression, accessibility, boundary states and authorized deployment identity |
| Reports/documents | **Initial qualified pack** | Source-to-claim mapping, calculations, artifact inspection and format-appropriate rendering |
| Presentations | Optional later pack using existing Host workflows | Real artifact, editability, rendering and layout checks |
| Spreadsheets | Optional later pack | Recalculation, formulas, data reconciliation and output inspection |
| Research | Shared source/evidence contract initially; independent pack if useful | Source quality, scope, contradictions and uncertainty |
| Data analysis | Optional later pack | Data grain, quality, methodology and reproducible calculations |
| Code projects | General impact contract initially; broader pack if useful | Input-state binding, affected interfaces/consumers and relevant regression |
| File organization | Deferred optional pack | Explicit source/destination plan, collisions, permissions and recovery; no current migration |

Meranti provides the first learning case:

| Transferable lesson | Placement |
|---|---|
| Dependencies include event scopes, DOM contracts, layout measurements and consumers beyond imports | General change-impact contract |
| Shared interactions need explicit ownership and state assumptions | General contract; Website-specific scenarios |
| Shared changes require consumer-aware regression | General validation obligations |
| Endpoint checks can miss transition failures | General coverage rule; domain chooses relevant boundaries |
| Recommendation, implementation, validation and visual approval establish different claims | General evidence semantics |
| Accepted artifacts need clear completion and reopening conditions | General termination contract |

The postmortem distinguishes inspectable source from historical execution accounts and unavailable intermediate implementations. Those limitations remain attached to its lessons. External evidence: `MERANTI-POSTMORTEM-FOR-NEXUS.md`, line 25, from the Meranti Coffee House project. This project-specific source is not bundled with Nexus.

Its exact animation duration, easing, breakpoints, frameworks, structure and visual identity remain project parameters.

### G5 — Bounded Delegation and Concurrency

| Required field | Specification |
|---|---|
| **1. Name** | Bounded Delegation and Concurrency |
| **2. Objective** | Add limited delegated execution only when measured benefit exceeds coordination cost and the Host can enforce the required boundaries. |
| **3. Why Nexus must own this** | Nexus must preserve parent policy, budget, input/output scope and acceptance across child work. Native scheduling alone does not establish those guarantees. |
| **4. Deterministic work** | Validate parent-child contracts; attenuate permissions and budgets; check delegation depth, dependencies and resource conflicts; reserve child allocations; validate cancellation and merge evidence. |
| **5. Delegated work** | Native Agent lifecycle, scheduling, reasoning, implementation and cancellation. Hosts provide isolation/ownership mechanisms and observable child results. |
| **6. Reused foundation** | G1 conformance; G2 contracts, accounting and recovery; G4 impact/resource evidence; the frozen advisory Agent contract as a preserved boundary. Executable delegation uses a separate schema. |
| **7. New schemas/contracts** | **DelegationContract:** parent/child/task identity, executor profile, optional persona revision, objective, input/output scope, read/write resources, capabilities, attenuated grant/budget, maximum depth, acceptance binding and cancellation. **BoundedDAG:** dependencies, node states, resource ownership and fan-out. **DelegationReceipt/MergeEvidence:** result identity, usage, validation, base state, conflict disposition and cancellation outcome. |
| **8. Security/authority boundary** | Child permission is a subset of parent grant ∩ user policy ∩ Host enforcement. Children cannot approve themselves, expand scope or multiply budgets. Missing ownership enforcement disables conflicting parallelism. Persona text grants no authority. |
| **9. Tests** | Hidden/transitive delegation; depth/fan-out bypass; overlapping writes; unknown resource sets; stale base state; late child output; parent cancellation/revocation; orphaned work; budget multiplication; forged child receipts; merge conflicts; resource exhaustion. |
| **10. Acceptance criteria** | A pre-registered experiment demonstrates worthwhile benefit. Permissions and budget exposure remain conserved. One-writer rules hold. Failed/cancelled children cannot overwrite accepted output. No-Agent mode causes zero delegated dispatches. |
| **11. Explicit non-goals** | Mandatory swarm, distributed scheduler, unrestricted dynamic DAGs, autonomous Agent marketplaces, custom process supervision or requiring independent Agents for every review. |
| **12. Dependencies** | G2 and G4; qualified Host ownership/cancellation controls; G3 for external capabilities/personas. |
| **13. Ecosystem candidates** | Agency Agents collections as optional advisory personas; Edict/DeerFlow as patterns; Codex as an optional native scheduling Host. |
| **14. Complexity** | HIGH. Concurrency amplifies accounting, resource and cancellation failure modes. |
| **15. Creates runtime authority?** | **Yes, conditional delegated execution authority through a separately accepted contract.** Disabled until its entry and value gates pass. |
| **16. Freeze/tag gate** | Require positive controlled-concurrency evidence and negative containment tests, plus comparative value. Otherwise omit/disable G5. Proposed tag if qualified: `nexus-v2-g5-final`. |

Start with a sequential child workflow. The first parallel experiment should be a small, fixed DAG with a shallow delegation limit and bounded fan-out.

Use one writer per resource. Disjoint workspaces help only where they actually isolate the resources involved; external systems and shared stores still need coordination.

Current documentation describes Host-owned subagent lifecycle and inherited controls. It does not establish that a particular task has enforceable child-specific attenuation or suitable result receipts. [Subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)

### G6 — Governance Qualification and Production Security Freeze

| Required field | Specification |
|---|---|
| **1. Name** | Governance Qualification and Production Security Freeze |
| **2. Objective** | Qualify the supported Nexus product against real workflows, substitution, comparative value, defensive security testing and release requirements. |
| **3. Why Nexus must own this** | Nexus’s product claims concern governance across engines. Individual tool successes cannot establish that the integrated control plane provides those guarantees or adds sufficient value. |
| **4. Deterministic work** | Assemble acceptance evidence; verify artifact/configuration identities, required coverage and unresolved findings; validate release manifests; enforce qualification and freeze gates. |
| **5. Delegated work** | Real workflow execution, specialist security testing, independent review, subjective acceptance and authorized release operations. |
| **6. Reused foundation** | All accepted foundation and new slices; accumulated adversarial fixtures; existing distribution/installation mechanisms; Meranti-derived scenarios. |
| **7. New schemas/contracts** | **AcceptanceSuiteManifest:** scenarios, supported configuration matrix, criteria and evidence requirements. **ValueExperimentProtocol:** comparable arms, metrics, thresholds and stopping rules. **QualificationRecord:** capability results separately from governance results. **ReleaseEvidenceManifest:** exact build/components, approvals, checks, known limitations and release identity. **SecurityFreezeRecord:** findings, fixes, retests, independent review and accepted scope. |
| **8. Security/authority boundary** | Red Team runs only in owner-authorized environments. Test fixtures and receipts cannot become production grants. Release requires concrete artifact approval and a qualified execution path. Passing tests does not authorize publication. |
| **9. Tests** | All scenarios in Section F; cumulative boundary/security tests; model/Host substitution; installer/package integrity; secret/private-data exclusion; update/revocation behavior; portable-path checks; authorized release and post-release verification. |
| **10. Acceptance criteria** | Supported configurations complete their declared useful tasks; restrictions and refusal behavior hold; comparative value is demonstrated for retained functionality; genuine Critical/High findings are resolved; independent review and full regression pass; release evidence binds the approved artifact. |
| **11. Explicit non-goals** | Universal Host support, approval of every candidate, mandatory Web OS, claims of being “unhackable,” forced G5 adoption or public deployment without authorization. |
| **12. Dependencies** | G3 and G4, their prerequisites, and G5 only if enabled in the release. Test development begins earlier. |
| **13. Ecosystem candidates** | Optional qualified evaluation/security tools. No named external repository is a graduation dependency. |
| **14. Complexity** | HIGH, with scope bounded by the declared support matrix. |
| **15. Creates runtime authority?** | **No new category.** Tests and release operations consume separately valid authority through accepted boundaries. |
| **16. Freeze/tag gate** | Final Red Team → Blue Team fixes → retest → independent review → full regression → owner acceptance → Production Security Freeze. Proposed tag: `nexus-v2-production-final`. |

## SECTION C — OLD → NEW ROADMAP MAP

The repository’s historical roadmap lists Slice 5 as one context/memory phase. The accepted allocation review provides the later **5A/5B** split used below; it is not presented as a separate verified repository milestone. [Historical roadmap](nexus-ecosystem-gap-scan.md#32-longer-term-slice-roadmap)

| Old item | Decision | Roadmap V2 destination |
|---|---|---|
| **Slice 4 — Durable Local Checkpoint and Resume Ledger** | KEEP evidence; ADAPT recovery; MERGE | G2 combines trace, checkpoints, accounting, reconciliation and stopping around one workflow. |
| **Slice 5A — Working context** | ADAPT; DELEGATE | G4 owns disclosure/source contracts; Host owns suitable retrieval and compaction. |
| **Slice 5A — Persistent project memory** | ADAPT | G4’s small decision ledger; no universal memory platform. |
| **Slice 5A — User policy/personalization** | KEEP policy; ADAPT preferences | G1 explicit policy; G4 provenance-bearing decisions/preferences. No inferred grants. |
| **Slice 5A — Capability graph/ontology** | ADAPT; MERGE | G4’s small typed relationship set. |
| **Slice 5B — Code intelligence** | ADAPT; DELEGATE | G4 change-impact evidence; Host/model repository understanding and coding. |
| **Slice 6 — Generic single-Agent Runtime** | DROP | Replace with G2’s narrow executor contract and existing Host execution. |
| **Slice 6 — Delegation contracts/profiles** | KEEP; ADAPT | G1 executor facts; G2 single-executor contract; G5 conditional delegation. |
| **Slice 6 — Universal/progressive Skill runtime** | DELEGATE | Host Skill loading/execution; Nexus verifies applicability, identity and evidence. |
| **Slice 7 — Multi-Agent DAG** | ADAPT; conditional | G5, only after ownership, accounting and value gates. |
| **Slice 7 — Cost/resource/evidence governance** | KEEP; MERGE | G1 selection economics; G2 accounting/evidence; G4 impact; G5 concurrency extensions. |
| Later discovery/ecosystem knowledge | ADAPT | Reuse Slice 2 and Slice 3C; G3 closes the separate approval/registration boundary. |
| Later browser/web research | DELEGATE | Qualified Host/tools under G2 and domain evidence requirements. |
| Later Domain Workflow Packs/Integrity Policies | ADAPT | G4 common contract and two initial packs. |
| Later long-running improvement loops | ADAPT; MERGE | G2 bounded repair/replan with best-artifact preservation and termination. |
| Later global budgets/controlled termination | KEEP; MERGE | G2. |
| Later Final Red Team | KEEP; ADAPT | Continuous slice testing plus G6 cumulative review. |
| Later Grand Acceptance/Web OS | DROP mandatory Web OS; ADAPT acceptance | G6 governance suite. Technology-brand website remains a major optional scenario. |
| Later ecosystem auto-updates, broad cleanup, CAS relocation | DEFER | Separate future decisions; outside the minimal production path. |

## SECTION D — ECOSYSTEM INTEGRATION TIMELINE

**Every named candidate is optional.** No candidate receives approval through this table.

Three gates apply:

- **Reference use:** bounded source reading with attribution and evidence dates; no execution of source instructions.
- **Granular adoption:** exact source/revision/component, dependency scope, provenance/license/security review, valid quarantine coverage, separate approval and registration.
- **Execution:** independently qualified binding, current task authority, privacy/budget controls and required evidence.

For sources outside the frozen eight-source policy, executable adoption remains blocked pending separately accepted intake coverage. Reading a specification or adapting an idea does not require importing its runtime.

| Candidate | Earliest eligible stage and role | Quarantine/review requirements | Required? / What not to import |
|---|---|---|---|
| **1. TencentCloud/TencentDB-Agent-Memory** | G4 — `PATTERN_SOURCE`, `REFERENCE_ARCHITECTURE` | Review relevant scoped-memory, provenance and retrieval patterns; exact-component review if copying code. Current source-policy identity is covered. | Optional. No default proxy, remote memory service, database platform or full runtime. |
| **2. mattpocock/skills** | G3 review; G4 use — `GRANULAR_SKILL_SOURCE` | Select one relevant Skill; pin its content and referenced resources; review permissions and applicability. | Optional. No wholesale activation or inherited authority for scripts. |
| **3. jnMetaCode/agency-agents-zh** | G4 advisory use; G5 optional executor association — `ADVISORY_CAPABILITY` | Review exact persona revision, instruction content and duplication. Bind persona separately from executor. | Optional. Persona never grants tools, approval or delegation. |
| **4. msitarzewski/agency-agents** | G4/G5 — `ADVISORY_CAPABILITY` | Same granular persona review; preserve canonical identity and avoid duplicate roles. | Optional. No entire-catalog activation or mandatory Agent organization. |
| **5. Shubhamsaboo/awesome-llm-apps** | G2 — `REFERENCE_ARCHITECTURE`, `PATTERN_SOURCE` | Treat examples as references; separately review any copied component and dependencies. | Optional. No bundled examples, credentials, provider choices or application runtime. |
| **6. bytedance/deer-flow** | G2; G5 for delegation patterns — `REFERENCE_ARCHITECTURE`, `PATTERN_SOURCE` | Evaluate individual harness/workflow mechanisms against Nexus boundaries. | Optional. No automatic runtime, infrastructure or provider stack import. |
| **7. cft0808/edict** | G2/G3; G5 — `PATTERN_SOURCE`, `REFERENCE_ARCHITECTURE` | Review reviewer, governance and delegation ideas independently from implementation. | Optional. No authority derived from role hierarchy or imported runtime. |
| **8. openai/codex** | G1 reference/conformance; G2 execution — `REFERENCE_ARCHITECTURE`, `FUTURE_EXECUTOR_ADAPTER` | Qualify the actual Host/version/configuration/binding. Source-code copying, if ever proposed, follows separate granular review. | Optional as a particular Host. Do not vendor, replace or scrape Host Codex. |
| **9. agentskills/agentskills** | G1/G4 — `REFERENCE_ARCHITECTURE`, `PATTERN_SOURCE` | Pin the relevant specification for interoperability. Executable components need separate intake coverage and review. | Optional. No universal Skill interpreter; format validity is not trust. |
| **10. cloudflare/agent-skills-discovery-rfc** | G3 — `REFERENCE_ARCHITECTURE`, `PATTERN_SOURCE` | Reuse accepted Slice 2 scope; review protocol revisions before new adoption. | Optional. No assumption that a proposal is universally implemented; no automatic installation. |
| **11. modelcontextprotocol/registry** | G3 — `DISCOVERY_SOURCE` | Reuse bounded accepted metadata discovery. Review the exact linked project/package, not merely its registry entry. | Optional. No package launch, remote connection, OAuth or trust from metadata membership. |
| **12. NVIDIA/SkillSpector** | G3 — `OPTIONAL_VALIDATOR`, `WATCH` | Exact-version review and qualified isolated execution outside Slice 3C; separately resolve intake coverage. | Optional. No trust-authority role, mandatory scanner dependency or modification of frozen analysis. |
| **13. promptfoo/promptfoo** | G1 evaluation-design reference; G3+ for newly adopted tooling — `OPTIONAL_DEV_TOOL`, `OPTIONAL_VALIDATOR` | Review exact harness/configuration/dependencies; synthetic/offline fixtures first. Live providers require separate authorization. | Optional. No runtime authority, unrestricted provider calls or model-judge approval. |
| **14. tree-sitter/tree-sitter** | G4 — `OPTIONAL_DEV_TOOL`, `GRANULAR_COMPONENT_SOURCE` | Review exact parser and grammars through accepted intake coverage; measure narrow impact-extraction value. | Optional. No universal code graph or claim that syntax proves all consumers. |
| **15. nextlevelbuilder/ui-ux-pro-max-skill** | G4 — `ADVISORY_CAPABILITY`, `GRANULAR_SKILL_SOURCE` | Exact Skill/resource review and intake coverage. Classify as `EXTERNAL_DESIGN_INTELLIGENCE_CAPABILITY`, `ADVISORY_ONLY_BY_DEFAULT`. | Optional. No global installer or automatic code-modification authority. |
| **16. uiverse-io/galaxy** | G4 — `GRANULAR_COMPONENT_SOURCE` | Search/select exact component → quarantine/review → separate approval → use; verify component-specific licensing and dependencies. | Optional. Treat as `LARGE_EXTERNAL_UI_COMPONENT_CATALOG`; no wholesale catalog trust. |
| **17. awesome-selfhosted/awesome-selfhosted** | G3 — `DISCOVERY_SOURCE`, `REFERENCE_ARCHITECTURE` | Catalog entry → specific project → exact revision/artifact → accepted intake and review. | Optional; `REFERENCE_ONLY`. No mass deployment, container execution or trust inherited from listing. |
| **18. NVlabs/SoL-Pi** | G4 — `REFERENCE_ARCHITECTURE`, `PATTERN_SOURCE`; integration remains `WATCH` | Evaluate ObservationPack, evidence-preserving reduction and compaction against omission, privacy and recovery tests. Code adoption requires intake coverage. | Optional. No Pi runtime, provider routing, installer, continuation hooks or default remote reducer. |

The MCP Registry describes metadata pointing to packages; this supports retaining the discovery/trust distinction. [MCP Registry documentation](https://modelcontextprotocol.io/registry/about)

SoL-Pi documents stable observation handles, source-checked reductions and native compaction integration. It also warns that reduction may transmit logs to the configured model. Nexus should adapt the relevant ideas under its own evidence/privacy contracts. Matching retained quotations does not prove that omitted failures were preserved. [SoL-Pi repository](https://github.com/NVlabs/SoL-Pi)

## SECTION E — MODEL/HOST SUBSTITUTION PLAN

The labels below define test configurations, not planner branches or current performance certifications.

| Configuration | Nexus behavior | Required evidence and fallback |
|---|---|---|
| **Strong frontier model** | Supply bounded objective, allowed pool, policy, privacy constraints, budget, acceptance and evidence requirements. Allow internal semantic judgment within that scope. | Task-specific competence and qualified Host controls. More reasoning freedom grants no additional authority. |
| **GPT-5.6-class general model** | Use the same contracts. Adjust objective size and validation checkpoints from measured task results. | Profile/configuration binding and actual acceptance evidence. Do not assume it needs more scaffolding solely from its name. |
| **Cheaper cloud model** | Use smaller decisions or explicit context only where experiments show benefit. Include extra turns and validation in total cost. | Measured suitability, cost uncertainty and retry behavior. Escalation only to another permitted profile. |
| **Local/private model** | Keep required inference, reducers, embeddings, judges, tools, memory retrieval, logs and storage within the permitted deployment boundary. | Verify the full data path, including proxies and telemetry. Unsupported strict privacy requirements cause refusal before dispatch. |
| **No-Agent mode** | Use one executor and deterministic tools; sequentially perform required steps. | No child dispatch or hidden delegated fallback. A Host that cannot establish this restriction is ineligible for the strict mode. |
| **No-remote-MCP mode** | Use permitted local tools/Host workflows; exclude remote MCP and forwarding proxies to prohibited endpoints. | Verify actual routing. This restriction alone does not prohibit all cloud inference or web research; those follow their own policies. |
| **Deterministic-only mode** | Perform policy, identity, comparison, budget and evidence checks without a model. | Zero model invocation for declared deterministic operations; semantic work remains explicitly unsupported if no suitable engine is allowed. |

Qualification includes combined restrictions, particularly:

```text
No frontier model
+ local/private model only
+ no Agents
+ no remote MCP
```

Require a useful bounded success in the local/private configuration. More demanding tasks may return unsupported.

For substitution, keep task inputs, hard policy and acceptance requirements stable while changing profile/adapter data. Recheck only affected bindings and evidence. Never silently transfer private context to a replacement destination.

A refusal may pass a **governance behavior test** while leaving the requested artifact **not completed**. Report both outcomes.

## SECTION F — ACCEPTANCE SUITE

All scenarios below are proposed and unexecuted.

| Scenario | Test | What it proves |
|---|---|---|
| **A. Deterministic governance** | Run schema, identity, policy, state, budget and evidence checks with models unavailable. Include conflicts and forged inputs. | Nexus’s authoritative decisions do not depend on a particular model. |
| **B. Existing repository modification** | Perform an authorized bounded change with base commit, dirty/input snapshot, shared contracts, consumer impact and regression evidence. Use Meranti-derived interaction cases. | Scope control and change-impact evidence extend beyond “tests passed.” |
| **C. Source-backed artifact workflow** | Produce a real report from approved sources; verify claims, calculations and format-appropriate output. Exercise source or artifact substitution. | Evidence remains traceable through authoring and validation. |
| **D. Interrupted/recovered workflow** | Inject interruption before/after dispatch, effect, receipt and settlement; include usage exhaustion and ambiguous publication outcome. | Recovery preserves valid work and does not invent authority, release uncertain exposure or blindly replay effects. |
| **E. Capability gap and malicious/quarantined candidate** | Introduce malicious metadata/persona/Skill content, changed revisions and a benign controlled fixture. | Discovery and review cannot bypass separate approval, registration and current eligibility. |
| **F. Model/Host substitution** | Run common tasks across at least two materially different qualified execution configurations, including useful local/private execution and restricted combinations. | Portable policy and evidence semantics survive substitution; capability limitations remain truthful. |
| **G. Bounded concurrency** | If G5 is enabled, test disjoint work, conflicting writes, cancellation and pooled budgets. If disabled, test rejection of delegated/concurrent requests. | Enabled concurrency preserves ownership and allocations. Disabled-mode tests do not certify positive concurrency capability. |
| **H. Public release** | Verify a concrete release artifact, manifest, source/dependency provenance, data exclusion and authorized publishing operation; check the released identity afterward. | Production claims and release effects are bound to approved artifacts and valid authority. |

Graduation requires actual useful completion for the declared supported workflows. An all-refusal result cannot qualify the product as a working artifact orchestrator.

The technology-brand website may remain a major real-world scenario. Web OS features—window manager, Files, Browser, Notes, Calendar, Photos, Settings, App Store, safe Terminal simulation, Notifications, Search, AI Assistant and interoperability—remain optional scenario content.

**Value-over-native-Host experiments**

Compare:

| Arm | Configuration |
|---|---|
| **A** | Native Host with equivalent task instructions and hard constraints |
| **B** | Same Host with Nexus governance |
| **C** | Host + Nexus + bounded delegation, only where justified |

Measure policy violations, evidence completeness, recovery, acceptance quality, retries, cost, latency, human intervention and failure transparency.

Before each experiment:

1. Define the task population, fixtures, inputs, permitted capabilities and acceptance rubric.
2. Choose the primary outcome, minimum worthwhile benefit and tolerable cost/latency/intervention overhead.
3. Define failures, unsupported outcomes, intervention events and missing measurements.
4. Use a separate pilot to estimate variability; then lock thresholds, repetition strategy and stopping rules before evaluating the comparison set.
5. Record Host/model/configuration versions, observation coverage and measurement uncertainty.
6. Keep all failed and interrupted attempts in the results.

Do not invent universal success percentages. Unknown money remains unknown; token or time measurements must not be relabelled as monetary savings.

Security acceptance and comparative value are separate gates. If native Host use provides equivalent outcomes with less complexity, remove or delegate the unnecessary Nexus responsibility. G5 must additionally demonstrate benefit over the qualified sequential Nexus path.

## SECTION G — FINAL RED TEAM PLAN

Security tests begin in the slice that introduces each boundary. G6 consolidates coverage and tests interactions across those boundaries.

| Test area | Coverage |
|---|---|
| **Untrusted capabilities and supply chain** | Malicious Skills, Agent/persona text, ecosystem revisions, dependencies, update substitutions and misleading catalog provenance |
| **Policy and execution boundaries** | Prompt/protocol injection, permission escalation, secret exposure, arbitrary filesystem effects, shell/network failures and MCP/Host authority confusion |
| **Evidence and identity** | Forged validation, forged execution receipts, stale evidence, substituted model/profile/configuration, subject mismatch and replayed authority |
| **Memory and context** | Poisoned decisions, unauthorized confirmation, cross-project retrieval, sensitive reduction, omitted contradictions and false source attribution |
| **Lifecycle and resources** | Budget bypass, cancellation failure, unresolved effects, concurrency conflicts, orphaned work and resource exhaustion |
| **Release/update safety** | Package contamination, private-state leakage, unauthorized publishing, stale approvals, revocation failures and unsafe rollback to disallowed components |

Use owner-controlled fixtures, test accounts and authorized Nexus/test environments. Define an independent expected result and collect observable evidence for each case.

The final sequence is:

```text
Final Red Team
→ Blue Team fixes
→ retest
→ independent review
→ full regression
→ Production Security Freeze
```

Production freeze requires:

- Zero unresolved genuine **Critical/High** findings in the supported release scope.
- Explicit disposition of remaining lower-severity findings.
- Reproducible evidence for fixes and relevant cross-boundary regression.
- A documented support matrix and truthful unsupported behavior.
- Verified release identity, package contents and approved publication scope.
- Defined reopening triggers: material code, dependency, policy, binding or threat-model changes.

A genuine defect in frozen foundation blocks the affected release and requires separately authorized remediation through a versioned change. It never justifies moving an old tag or silently changing Slice 3C.

## SECTION H — REMAINING OPEN DECISIONS

Only these decisions need evidence or owner-specific information unavailable now:

| Open decision | Why unresolved | Resolution gate |
|---|---|---|
| **Which initial Host binding provides sufficient enforcement and receipt provenance?** | Product documentation and current tool visibility do not establish all required controls. | G1 conformance; prerequisite to G2 dispatch qualification |
| **How is owner approval authenticated and protected from executor/candidate forgery?** | Single-owner approval is recommended, but the concrete trusted channel/storage mechanism needs verification. | G3 security design |
| **Which concrete model/deployment configurations qualify for each task class?** | No task-specific comparative measurements were run, including local-model configuration measurements. | G1 profile evidence and G6 qualification |
| **Which budget dimensions have trustworthy enforceable bounds?** | Subscription attribution, late usage and provider/Host control visibility may differ. | G1/G2; strict requests remain unsupported where bounds are absent |
| **What retention periods and disclosure rules apply to new project/evidence records?** | These depend on the owner’s data classes and obligations. Retention classes alone do not determine durations. | Before persistent real-data operation in G2/G4 |
| **What thresholds and reviewer evidence define worthwhile quality/value for each experiment?** | Subjective acceptance and material benefit are task-specific. | Lock before each comparative experiment |

The default first domains, sequential execution, small local ledger and absence of a universal memory/runtime are recommendations resolved by this roadmap. They do not need to remain open merely because alternatives exist.

Additional source intake, other domain packs and CAS relocation remain deferred proposals rather than blockers for the minimum product.

## SECTION I — TOTAL COMPLEXITY / CRITICAL PATH

**Total remaining complexity: HIGH, but bounded.** Reducing the roadmap to six slices reduces duplicated infrastructure; it does not make authority, durability and cross-Host evidence easy. No calendar estimate is justified by current evidence.

Critical path:

```text
Frozen baseline
      ↓
     G1
      ↓
     G2
   ↙    ↘
 G3      G4
   ↘    ↙
     G6
```

If G5 is enabled, its qualification becomes an additional prerequisite to the final release.

| Work category | Placement |
|---|---|
| **Parallelizable** | G3 authorization and G4 workflow work after G2’s stable contracts; independent domain qualification; test/Red Team fixture development throughout |
| **Optional** | G5, external tooling, additional model/Host adapters, later domain packs, technology-brand website expansion and Web OS |
| **Deferred** | CAS relocation, broad cleanup/migration, automatic ecosystem updates, new source-intake coverage, distributed services, remote Agent protocols and universal memory/code graphs |
| **Highest-risk engineering** | Trustworthy Host/approval receipts; actual restriction coverage; uncertain-effect reconciliation; atomic budget exposure; cancellation and concurrent ownership |
| **Biggest unknowns** | Suitable Host integration surface, real local-model competence, usable cost controls and measurable value over native Host behavior |

Each slice survives the minimization challenge for a specific reason:

| Slice | Remove/merge/Host-delegation assessment |
|---|---|
| **G1** | Retain. Its eligibility/conformance decision must exist before expanded execution. Keep it to profiles and evidence, while Hosts provide observations. |
| **G2** | Retain and combine the formerly separate trace, budget, checkpoint and termination ambitions around one workflow. Delegate actual execution and native lifecycle. |
| **G3** | Retain for a product that adopts external capabilities. It cannot merge into Slice 3C because approval is a different authority boundary. Keep it to exact-subject authorization and registration. |
| **G4** | Retain the smallest evidence/pack layer that proves useful workflows. Merge small context, decisions, relationships and impact records; delegate reasoning, coding and authoring. |
| **G5** | Remove if its value or enforcement gate fails. Its optional status prevents delegation infrastructure from becoming a prerequisite for ordinary Nexus usefulness. |
| **G6** | Retain the final qualification/release decision. Perform most test development earlier; reserve this stage for cumulative evidence and independent judgment. |

The production claim should cover a small, tested configuration matrix. Support expands only when a new configuration or workflow passes its own gates.

## SECTION J — RECOMMENDED NEXT SLICE

**Choose exactly one: G1 — Capability Profiles and Executor Conformance.**

It should come first because it resolves the most consequential uncertainty: **which execution paths Nexus can govern truthfully**.

Its first implementation deliverable should establish versioned model/Host facts, deterministic eligibility and a constraint-by-constraint conformance result for one bounded pilot. That evidence determines whether G2 can proceed through an existing Host or must return a narrower unsupported result.

G1 introduces no product dispatch authority and provides immediate value through accurate selection and refusal. Implementation has not started.

## Appendix — Design-stage Agent & Skill Utilization Report

This appendix records the completed design task only. Its statements about changes, tests and Agent usage are historical and do not describe the subsequent documentation-freeze task.

| Category | Considered / applicable | Actually used and outcome |
|---|---|---|
| **Advisory Agents** | Architecture mapping, Meranti evidence analysis and governance/security critique were applicable. | Two Host-native advisory subtasks were dispatched. `meranti_evidence` completed evidence analysis and a bounded governance critique. `foundation_map` failed because usage was exhausted and returned no usable analysis; the parent completed that mapping. |
| **External specialist personas** | Software/security architecture perspectives were relevant; named ecosystem personas were not needed to provide them. | No external persona bundle was loaded, activated or granted authority. |
| **Nexus Skill** | Applicable to planning and boundary discipline. | Read and applied; one `nexus_plan_task` call before interruption. It was not repeated unnecessarily. |
| **OpenAI Docs Skill** | Applicable to current Host enforcement/subagent facts. | Read and applied; bounded official documentation was fetched. |
| **Deep Research** | Suggested by the Nexus planner; not appropriate as an executed workflow for this bounded architecture task. | Nexus reported `selected` and `load_status: loaded` for `deep-research`. The Host did not execute the Deep Research workflow or independently certify its mapping. |
| **Browser-control / product-design Skills** | Interactive UI inspection and design implementation were unnecessary. | Not loaded or executed. |
| **Document, presentation, spreadsheet and report-generation Skills** | Artifact production was outside this conversation-first design scope. | Not executed. |
| **Installation/integration Skills and candidate tools** | Prohibited by the task scope. | No installation, connection, scanner execution or candidate integration. |
| **Native Host work** | Appropriate for bounded inspection and synthesis. | Read repository/task evidence, compared Git/hash identities, performed limited public research, completed mapping and authored this roadmap. |

The advisory Agents did not exercise a Nexus Agent Runtime or constitute production-independent review. Their read-only task instructions were not represented as technically enforced sandbox restrictions.

Historical memory helped locate Meranti evidence; the current document and relevant source were inspected. No historical test result was presented as a new test run. The serving Nexus MCP process was not independently attested to the inspected Git commit.

No source, configuration, repository document, tag, candidate installation or storage migration was changed. No implementation or acceptance suite was run.

End of the accepted design record.
