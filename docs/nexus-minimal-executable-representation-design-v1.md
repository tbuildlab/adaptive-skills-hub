# Nexus Minimal Executable Representation Design v1

**Status: DESIGN CHECKPOINT ONLY — NO IMPLEMENTATION OR NORMATIVE PROMOTION.**

Starting branch: `nexus-v2-g2-development`. Starting HEAD: `bbc13a9d32f7ce0d65cfbe5da8d02b1cd05764e5`. Starting working tree: CLEAN. Starting MANIFEST: 219/219 PASS, SHA-256 `C9DB96A47BE567DDC4E10664E82EC549D4A5CC740CA1D36191253B7606980B77`. These are verified repository facts, not execution evidence for the examples below.

## 1. Purpose, authority and boundaries

Design one small, machine-readable **GovernanceAssessment**: a scoped snapshot of applicability, claims and their evidence. It answers what is assessed, why, under which accepted sources, using which profile facts, with which unresolved obligations. “Executable representation” names a possible later consumer; this document contains no executable contract, schema, parser or evaluator. It issues no grant and schedules no action.

| Inspected source | Authority and design use |
|---|---|
| [Northstar promotion acceptance](nexus-northstar-knowledge-promotion-acceptance-v1.md) §§3-7 | ACCEPTED overlay: CP1-CP5, ES1-ES6, conditional A-F, four applicability classes and exact evidence binding |
| [Reusable project gates](nexus-reusable-project-gates-v1.md) §§1-3 | Catalog governed by that acceptance, not every example universally mandatory; independent source/release/configured-origin/live facts |
| [Capability state model](nexus-capability-state-model-v1.md) §§1-3 | Reporting distinctions accepted through the overlay; independent INSTALLED/CALLABLE/EXECUTED/APPLIED, not replacement runtime enums |
| [D01/D02 acceptance](nexus-cross-project-refinement-d01-d02-acceptance-v1.md) §§3-4 | ACCEPTED WITH NARROWING: relevant boundary assessment, proportionate required tests, six separate documentary diagnostic concerns |
| [Demo2/Demo3 synthesis](nexus-demo2-demo3-cross-project-synthesis-v1.md) | Historical comparison/proposals/learned knowledge. D01/D02 use their later acceptance; other candidates gain no authority here |
| [Applicability validation](nexus-governance-applicability-validation-v1.md) §§2-7 | Documentary validation and stipulated A-E scenarios, not observed execution or new policy |
| [Microsoft reference analysis](nexus-microsoft-ai-agents-gap-analysis-v1.md) §§6,8-10 | External learnings, F01/F02 REPRESENTATION_CONSIDERATION only; no imported framework obligation |
| [Pre-G2 addendum](nexus-pre-g2-architecture-addendum-v1.md) A0-A6 and [acceptance](nexus-pre-g2-architecture-acceptance-v1.md) | Superior accepted architecture: governance data cannot grant authority; no second generic runtime/session/memory engine |
| [G1](nexus-v2-g1.md) scope/evidence contracts and [current P1-P12 mapping](nexus-g2-limited-clarifying-amendment-p1-p12-mapping-v1.md) | Selection has zero dispatch authority; exact conformance, controller/provider responsibilities, unknown effects/cost and qualification remain separate |

All local source references mean the bytes at the starting HEAD above unless an explicitly bound later accepted source is supplied. The existing manifest binds their exact versions. Historical PROPOSED headings do not defeat controlling acceptance overlays. ACCEPTED, PROPOSED, LEARNED KNOWLEDGE, EXTERNAL REFERENCE, DEFERRED and REJECTED remain distinct; this design does not promote the last five to rules.

Non-goals: gate/policy/applicability/workflow engine, generic rules DSL, planner change, finding tracker, database, UI, memory runtime, MCP/A2A, provider abstraction, HostAdapter, OpenAIHostAdapter or G2 runtime. Existing closed schemas and their result vocabularies remain authoritative; this snapshot references them and cannot replace or relabel them.

**A0-A6 and P1-P12 remain unchanged.** D01/D02 accepted semantics remain unchanged. No provider contact, credentials, resources, experiment or LPAC execution is involved. OpenAI human support escalation remains pending and untouched.

Preserved: **Scenario 01-04 = NOT RUN; HQ1-HQ5 = NOT PASS; HQ6 = NOT STARTED; Positive Host Binding = ABSENT; G2 = HOLD.**

## 2. Chosen unit and minimal field model

Choose an assessment rather than a task lifecycle, evidence receipt or isolated applicability row. A lifecycle invites invented transitions; a receipt alone omits applicability; an isolated row loses shared subject/profile/source binding. One assessment contains a small list of checks and shared references. It has no aggregate PASS, readiness flag, execution instructions, action arguments, retry count or next-step command.

This is a proposed serialization boundary for already accepted meanings, not acceptance of new reporting obligations for every Nexus task. Required means necessary *inside a future record of this design*, not that every task must create such a record. Only the declared assessment scope is covered; an incomplete check list never proves complete task acceptance.

### Required top-level fields

| Field / shape | Why it survives minimality review |
|---|---|
| `schema_version`: exact string `1.0` | Identifies this representation contract, independently of governance/artifact version |
| `record_id`: stable scoped string | Distinguishes snapshots; cannot be a grant, resume credential or trusted process seal |
| `basis`: `REAL` or `ILLUSTRATIVE` | Prevents stipulated evidence and conditional PASS from being silently reused as real operation evidence. REAL is a declaration requiring external verification, not a trust certificate |
| `subject`: `id`, `configuration_id`, `criteria_refs` | Exact assessed artifact/task/profile revision and relevant configuration; criteria references bind the acceptance question. IDs must resolve through the profile/references; inventing an ID proves no identity |
| `purpose`: bounded text | Names the question/claim and omissions; no implicit whole-project certification |
| `governance_refs`: reference IDs | Explicit governing accepted sources/sections/versions, independent of ordinary evidence |
| `profile`: fact list, possibly empty with an explained purpose | Only facts used to select checks or bind the subject, not a second TaskProfile/store |
| `checks`: selected check list | Applicability, assessment result and mandatory premises independently represented |
| `references`: shared reference list | Source/evidence identity once, reused without copying transcripts or evidence bodies |

No universal creation timestamp, project/repository field, actor/account field, host/session field or cryptographic hash is added. Put relevant repository/profile/operation/actor identity in the exact referenced subject/evidence. Time/freshness and integrity are required when the governing property needs them, not optional excuses to omit a required binding.

### Nested records and conditional fields

| Object | Fields and limits |
|---|---|
| Profile fact | Required `id`, `claim`, `value`, `basis`, `refs`. `value` is a JSON scalar or null, never an executable expression/object extension bag. `basis` is PROVIDED / OBSERVED / DERIVED / ASSUMED / UNKNOWN. References supply provenance; DERIVED references a bound derivation note identifying its inputs, method and limits, not just an unsupported classification. UNKNOWN has null value and an explicit missing/conflicting basis; absence is not NO |
| Check | Required `id`, `family` (A-F), `governing_refs`, `criterion`, `applicability`, `outcome`. Criterion is a bounded human-readable property, not executable logic; check IDs identify obligations within the snapshot, not globally approved rule registrations |
| Applicability | Required `state`, `reason`, `fact_refs`. State uses the four accepted classes, or null for classification not established. Null is an unresolved slot, not a fifth applicability class. Positive profile support is mandatory for an exclusion; an empty fact list cannot justify absence of a surface |
| Outcome | Required `state`, `reason`, `evidence_refs`. State is null (not assessed), UNKNOWN (assessed, evidence insufficient/stale/conflicting), PASS (scoped criterion supported), FAIL (scoped criterion unmet) or NOT_APPLICABLE (reasoned exclusion). No other universal status enum |
| Check dependencies | Optional `requires`: check IDs, empty/omitted when none. Every listed dependency is a mandatory premise for this check's PASS; same outcome model reused, no separate dependency lifecycle |
| Capability binding | Optional check `capability`: `ref` and `dimension`, only for an applicable capability observation; dimension reuses INSTALLED / CALLABLE / EXECUTED / APPLIED. Exact capability/Host/operation/time and observed YES/NO/UNKNOWN/NOT APPLICABLE remain in the existing referenced record |
| Reference | Required `id`, `kind` (GOVERNANCE or EVIDENCE), `locator`, `source`, `scope`. Optional `selector`, `revision`, `captured_at`, `valid_until`, `integrity_sha256` only where meaningful/required. GOVERNANCE requires a resolved accepted version/section; EVIDENCE does not become authority by using that label |
| Diagnostic context | Optional top-level `diagnostic`, only when a finding is triaged/acted on/claimed resolved: observation, reproduction, cause, disposition, remediation, validation. Each is `{note, refs}`; refs point to evidence. Separate brief answers or references, not a new lifecycle, finding database or closed diagnostic status vocabulary |

For a REAL record, source and observation coverage must identify what was actually inspected by whom/method and what was merely reported. A source record may carry these details instead of repeated fields. OBSERVED cannot be justified by a declaration, a filename or another unsupported claim. ASSUMED cannot supply a mandatory security/authority/effect premise. PROVIDED can support “source reports X”, but cannot alone support “X independently enforced”. No empty string/null/absent optional property means “not applicable”, “no effect” or “authorized”.

Subject/configuration/criteria unknowns go in explicit UNKNOWN profile facts and applicable checks. An unresolved identity cannot support an exact-subject PASS. Changes create a new snapshot ID/binding, preserving history; no mutable issue lifecycle is designed.

## 3. Applicability, outcomes and dependencies

| Applicability | Outcome discipline |
|---|---|
| REQUIRED | Null if unassessed, UNKNOWN if evidence insufficient, PASS only for the bound property, FAIL when a required criterion is demonstrably unmet |
| OPTIONAL | Same outcome meanings; not performed is null, not PASS. Optional UNKNOWN can coexist with narrowly scoped acceptance only if no mandatory premise depends on it and omission/impact/disposition are explicit |
| NOT_APPLICABLE | Positive scoped reason and profile support; outcome NOT_APPLICABLE, never PASS |
| DEFERRED | Relevant pending work, reason and prerequisite/scope/grant gap explicit; null/UNKNOWN/FAIL as warranted, never satisfied by the word deferred |
| null classification | Preserve unknown applicability; no claimed pass. Security-relevant ambiguity blocks the affected claim/action and requires resolution; do not default to OPTIONAL/NOT_APPLICABLE |

`DEFERRED` applicability describes selected future work; a D02 disposition saying “defer further diagnosis” describes a decision concerning a finding. Neither resolves the finding or weakens a required property. A required obligation remains REQUIRED while its evidence/work is deferred; changing its field to DEFERRED cannot erase governing requiredness. Any source-mandatory or dependency-mandatory unresolved item still blocks the related claim.

`requires` expresses *logical evidence dependence*, not temporal ordering, a runnable DAG or scheduling. A check needing authorization, prerequisite evidence, clarification, qualification or reconciliation names another check representing that obligation. A dependency's PASS must meet the appropriate criterion and scope; a generic “receipt exists” criterion cannot satisfy “restriction enforced”. An irrelevant dependency must be removed with a reviewed reason, not satisfied by NOT_APPLICABLE.

Null, UNKNOWN, FAIL, NOT_APPLICABLE or unresolved applicability in a listed mandatory dependency cannot supply the dependent PASS. A review can record the observed local result separately while keeping dependent closure UNKNOWN. Missing dependency references, contradictory IDs or dependency cycles are rejected as incoherent records; rejection never authorizes retry or execution. No dependency resolution mechanism is implemented.

## 4. Evidence, capability, authority and effect separation

Evidence references identify **what could support a claim**. The outcome's reason explains the association, criteria, exact subject/configuration and coverage. Source existence/hash equality is not conclusion support, current authority, trustworthy issuance or actual execution. Shared references are permitted; shared conclusions are not inferred. Historical observations retain their original time/scope and do not refresh when copied. Required freshness/identity gaps yield UNKNOWN.

A configured-mode claim and an observed/applied-mode claim are separate profile facts/checks; no automatic promotion. When release evidence applies, represent LOCAL SOURCE, REMOTE SOURCE, DEPLOYMENT SOURCE, CONFIGURED ORIGIN and OBSERVED LIVE STATE as separate referenced facts/checks. Their values may match; a source hash never proves the next stage. Non-published local tasks need no fictional release chain.

Capability checks reference the accepted four-dimension model. PASS for `CALLABLE=YES` means supported callability in the stated operation path, not dispatch authority. Failed invocation can still establish EXECUTED=YES. APPLIED needs independent invocation/output-to-artifact/effect correlation and acceptance binding. Never infer INSTALLED -> CALLABLE -> EXECUTED -> APPLIED. An APPLIED claim lacking its own correlation is UNKNOWN; a contradictory same-operation execution claim requires review, not an invented maturity ladder. Existing R4/R5/validator enum terms are retained in their source records.

Authority uses ordinary D/A/F checks and references to the separately issued grant: exact action/subject/configuration/scope, validity, issuer/actor, expiry/revocation where relevant. Represent these separately from capability. A criterion such as “valid grant covers this local write” can PASS only on appropriate evidence; explicit denial/known missing grant can FAIL; absent/unverified validity remains UNKNOWN; owner approval required is an unresolved authorization premise. The snapshot cannot mint/renew a grant. Credential presence, OAuth, installation, accepted document or available API supplies no authority.

External effects need **no seven-state universal enum**. Use separate facts/checks for intended/planned effect, bounded authorization, original attempted operation, observed result, final-state reconciliation and cost where applicable. Scope-bound evidence can establish “no effect”; a missing receipt cannot. An authorization PASS does not imply attempt; an attempt does not imply observed success; local timeout/cancel acknowledgment does not imply cessation, final effect or settled cost. Reconciliation must bind the original operation and remaining uncertainty. Required final effect UNKNOWN blocks related completion/unsafe retry/settlement even while grant validity is supported. No remote query, retry, ledger or provider mechanism is designed here.

## 5. D01 and D02 mapping

D01 uses profile facts and source-bound checks, not a `boundary_trigger` engine. Record actual source/trust/interpretation boundary, risk, selected policy dimensions and evidence obligations. An early new/material boundary selects relevant D checks; the accepted four harness conditions determine whether a deterministic harness is required. A required harness is represented as an ordinary prerequisite check, not code generated by this contract. Evidence selection may be reused, but an absent tool/grant cannot demote mandatory evidence.

A/E unchanged inert local handling does not trigger a new API harness; authority/path/source/result protection remains required. B introduces anonymous public structured input: format/field/resource/error/privacy/repeat-behavior choices and appropriate deterministic verification apply now. L/R/S/W remain contract choices, not universal values. No universal 8 KB, 800 ms, honeypot, same-origin, JSON, technology or test-count parameter is encoded. Material changes to provenance/parser/path/effects require renewed applicability review; no keyword exemption for local/demo/read-only.

D02's six documentary concerns are conditionally present in one snapshot. Their note/reference shapes deliberately do not define status transitions or mandatory root-cause investigation. C can retain NOT_REPRODUCED, cause UNKNOWN and optional diagnostic deferral with no repair claim. D can support a narrow cause/correction/validation claim when each link exists. NOT_REPRODUCED != FALSE_POSITIVE/FIXED; UNKNOWN_CAUSE != NO_DEFECT; PATCH_APPLIED != VALIDATED; DEFERRED/ACCEPTED_LIMITATION != FIXED/RESOLVED. A standalone current-check PASS is possible without a patch, but cannot establish a historical fix. Remediation is artifact change evidence, not capability APPLIED or validation. Existing analyzer findings/required review cannot be relabeled optional by free text.

## 6. F01/F02 decisions: representations, not new requirements

| Consideration | Decision | Minimal treatment / concrete ambiguity avoided |
|---|---|---|
| F01 context source / selected / actually used | REFERENCE_EXISTING_EVIDENCE | Reference existing ContextManifest/selection/invocation observations through different facts/checks only when an attribution claim requires them. Availability/loading does not prove use; summaries remain derived inputs. No mandatory context object, source-body copy or memory system |
| F02 session identity/state | REFERENCE_EXISTING_EVIDENCE | Optional bound native/session reference when relevant; no session required for a local documentary task, no SDK lifecycle copy |
| F02 checkpoint/resume identity | REFERENCE_EXISTING_EVIDENCE | Optional exact existing artifact/domain checkpoint reference. Validated artifact recovery is distinct from restored conversation; no new CheckpointRecord or resume service |
| F02 current authority | INCLUDE_MINIMAL | Independent scoped check and grant evidence when action/claim requires it, using §4. A resumed session cannot renew a grant; this is already accepted authority semantics, not a Microsoft-derived new obligation |
| F02 pending/unreconciled effects | INCLUDE_MINIMAL | Independent original-operation/final-effect/reconciliation checks and required dependencies when effects exist. A checkpoint cannot settle an effect; no new ledger or mandatory effect fields for effect-free tasks |

Defer native session/checkpoint payload schemas, automatic context attribution and lifecycle computation. A reference not supplied means the relevant observation remains unknown, not that a session/effect is absent. No F01/F02 source is promoted normatively. Explicitly represented authority/effect obligations come from CP1/CP4/A2/P9-P12, not the external tutorial.

## 7. Format, versioning, determinism and privacy

| Criterion | JSON | YAML |
|---|---|---|
| Deterministic interpretation | Small standard value model; duplicate member names must be rejected by a future reader, not last-wins | YAML versions, implicit scalar typing, tags/aliases/merge keys require a restricted subset |
| Readability/comments | Verbose quoting; comments stay in companion documentation | Convenient annotations/comments, but consumer behavior needs additional choices |
| Schema/diff/canonicalization | Existing Nexus JSON ecosystem; stable UTF-8/LF and member ordering straightforward | Schema/canonicalization possible but more implementation decisions/dependencies |
| Burden/ambiguity | Lower incremental burden for a closed passive record | No current need justifies additional YAML surface |

Preferred **future serialization: JSON**, not an implemented parser or executable JSON Schema. The fenced examples are standard JSON text, inspected for syntax only. Future separately authorized JSON Schema may constrain structure/vocabulary; it cannot prove evidence truth, freshness, authority, completeness or enforcement, and cannot safely evaluate human text as policy.

Version policy: exact supported `schema_version`; a future unsupported version fails closed. A published field/addition requires a versioned design/review and explicit consumer support. A minor version may add reviewed optional fields only without changing prior meanings; unknown fields never gain authority or silently bypass a required check. Until support is explicitly declared, reject unknown versions/members; no permissive “compatible enough” fallback. Incompatible meaning changes require a major version. This is not a plugin mechanism; no metadata/extensions/custom bag.

Future canonical representation: UTF-8 without BOM, LF and terminal newline, stable member ordering, two-space indentation, deterministic ID ordering for profile/check/reference lists, sorted unique reference/dependency ID lists. Unique IDs and duplicate JSON keys checked before use; no silent merge or overwrite. IDs come from stable scoped subject/check identities rather than random time; versions and evidence locators are exact. Retain real observation timestamps where necessary, but add no timestamps merely to make identical records differ. Sorting does not imply execution order. Examples below use compact display formatting, not claimed canonical runtime serialization.

Privacy: store sanitized evidence locators and justified scopes, never keys/passwords/raw credentials/authentication tokens, environment dumps, hidden reasoning or unnecessary PII. A protected evidence reference grants no access and must not include embedded credentials/signed access URLs. Readers lacking permitted access retain UNKNOWN; do not broaden ACLs or fetch evidence automatically. Capture times/digests/identity references are included only for the bound criterion. Hashes prove byte identity, not safety; no universal receipt/signature architecture.

## 8. Expected future handling of incoherent input

These are design expectations for a later authorized static consumer, not implemented validation or new governance waivers. Original evidence is preserved; a rejected snapshot is not a rewritten source record.

| Input/problem | Expected handling and reason |
|---|---|
| Missing required fields, empty source/reason, unresolved structural ref, wrong family, duplicate identity/key, cycle, unsupported version/member | REJECT_RECORD: structure cannot express an unambiguous scoped claim |
| NOT_APPLICABLE because tools/evidence/approval are missing, or exclusion contradicts known profile | REJECT_RECORD: invalid exclusion; preserve underlying unknown/unmet obligation |
| PASS with unresolved mandatory premise, inadequate evidence association or unbound subject | REJECT_RECORD: claimed support is incoherent; factual observation can be preserved separately, not promoted |
| Check not assessed or evidence missing/stale/inaccessible; profile/authority/final effect unresolved | PRESERVE_UNKNOWN (null retains not-assessed distinction): no favorable inference; affected required claims blocked |
| APPLIED asserted without output/invocation attribution while EXECUTED unestablished | REJECT_RECORD for unsupported APPLIED; PRESERVE_UNKNOWN for each unproven observation, no ladder inference |
| FALSE_POSITIVE/FIXED based only on failed reproduction; patch presented as validation; reconciliation asserted with final state UNKNOWN | REJECT_RECORD for contradictory conclusion; separate original facts retained |
| Authority inferred solely from credentials/session/checkpoint/capability | REJECT_RECORD; no grant exists because a record says so |
| Conflicting credible evidence/versions, disputed governing applicability, diagnostic policy conflict | REQUIRE_REVIEW; retain UNKNOWN and block affected mandatory claim/action; review is not permission to waive the property |

PRESERVE_UNKNOWN is not permission to accept a structurally invalid record; REJECT_RECORD and REQUIRE_REVIEW are diagnostic handling categories, not execution dispositions. None marks an HQ/P requirement passed. Selection of checks still requires accepted governing criteria; an omitted required check cannot be made safe by validating only listed fields.

## 9. Field-by-field anti-bloat disposition

| Candidate | Accepted basis / ambiguity | Decision, optionality and coupling |
|---|---|---|
| Version/record ID | Stable subject/source identity and reproducible review | Keep two bounded identifiers; no UUID service or lifecycle |
| Basis qualifier | Demo/stipulated != real evidence | Keep; label does not certify evidence. Avoid a global confidence score |
| Subject/configuration/criteria + purpose | CP5/exact scoped checks; no project-wide PASS | Keep references/short IDs, not copies of repository/session objects |
| Governance refs | Accepted policy != retrieved content | Keep accepted version/section binding; no new authority registry |
| Profile fact id/claim/value/basis/refs | Provenance, configured vs observed, unexplained N/A | Keep only selection/binding facts. No general provenance ontology, arbitrary structured attributes or assumed trust flags |
| Check id/family/criterion/governing refs | Conditional A-F/subcheck/coverage | Keep explicit selected obligation; free text is not an evaluable rule or approved plugin |
| Applicability state/reason/fact refs | Accepted classes; absence != exclusion | Keep positive reasoning and unresolved slot. No new trigger engine/score |
| Outcome state/reason/evidence refs | ES1-ES6; status != support | Keep narrow vocabulary; omit universal success/fix/readiness status |
| requires | Mandatory gaps cannot become PASS | Optional list, reuse check outcomes. No generic graph scheduler, dependency kind enum or auto-resolution |
| Capability ref/dimension | ES5 independent four dimensions | Optional relevant observations, existing model values and source detail. No ladder or new capability registry |
| Diagnostic six notes/refs | D02 independent concerns | Conditional only; no finding ID/owner/deadline/state/history database. Exact findings/actors remain source references |
| Reference id/kind/locator/source/scope | Evidence identity != claim/authority | Shared once; no source payload/custody service. selectors/version/time/digest conditionally required by criterion |
| Dedicated authority/effect/session/checkpoint/context objects | Necessary distinctions already expressible in checks/references | Remove duplicate objects. Authority/effect checks retained when required; F01 and session/checkpoint reuse references |
| Generic metadata/extensions/custom, arbitrary predicates/actions, provider/tool arguments | No accepted need; bypass/coupling/runtime risk | Reject. No code, executable expressions, dynamic remote loaders or opaque extension blobs |
| Timestamp everywhere, universal hashes/signatures, all gates/all diagnostics/all capability dimensions | No task-independent obligation | Reject universal fields; required evidence remains required in applicable scoped references |

Every retained field either binds an accepted distinction or prevents a demonstrated ambiguity. Provider/framework names appear only in referenced subjects if actually relevant; no provider assumptions or new trust boundary are required. Optional fields become required only when their relevant accepted criterion needs them; optional syntax cannot downgrade a substantive requirement.

## 10. Static fixture method

The seven records below are **SYNTHETIC / STIPULATED / NON-EXECUTABLE**. No source/output file, endpoint, defect patch, test harness, detector, provider dispatch or capability invocation is created or executed. ILLUSTRATIVE records cannot supply real acceptance, authorization, execution, effects, capability use, HQ or G2 proof. PASS is solely a conditional logical assessment of the stated fictional criterion. Actual operation/effect validation remains UNKNOWN.

Each fictional `criteria`/`sample` locator names a document-only evidence assumption, not an accessible file or permission. `gov` locators reference real accepted governance at the starting HEAD. A-E exercise the accepted applicability scenarios; F/G add authority/effect and capability distinction controls. These are bounded selected subchecks, not claims that the examples enumerate every gate for a real task. No special-case interpreter/code is supplied.

## 11. Seven documentary JSON illustrations

### A — Inert local Markdown transformation

```json
{
  "schema_version": "1.0",
  "record_id": "illustration.A.1",
  "basis": "ILLUSTRATIVE",
  "subject": {"id": "A.task.v1", "configuration_id": "A.profile.v1", "criteria_refs": ["criteria"]},
  "purpose": "Conditional review of one local output write; no real transformation or task closure.",
  "governance_refs": [
    "gov"
  ],
  "profile": [
    {"id": "local", "claim": "Two LF lines; inert reviewed data; no includes/rendering/PII/network/UI/publication; unchanged interpretation boundary.", "value": "# Draft\nKeep this line.\n", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "grant", "claim": "Separate synthetic grant covers exact input read and separate output write, not source overwrite.", "value": "bounded local grant", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "comparison", "claim": "Fictional complete output and mutation observation; source unchanged; only declared output differs.", "value": "# Reviewed\nKeep this line.\n", "basis": "PROVIDED", "refs": ["sample"]}
  ],
  "checks": [
    {"id": "A01", "family": "A", "governing_refs": ["gov"], "criterion": "Declared input/output identities and usable read/write/comparison paths are bound.", "applicability": {"state": "REQUIRED", "reason": "Exact task path prerequisites matter.", "fact_refs": ["local"]}, "outcome": {"state": "PASS", "reason": "Stipulated note binds the paths/operations; not a real capability invocation.", "evidence_refs": ["sample"]}},
    {"id": "A02", "family": "D", "governing_refs": ["gov"], "criterion": "Bound grant covers the separate local write, inert input and source preservation.", "applicability": {"state": "REQUIRED", "reason": "A local output write is a mutation even without remote effects.", "fact_refs": ["local", "grant"]}, "outcome": {"state": "PASS", "reason": "Only the fictional exact scope is covered.", "evidence_refs": ["sample"]}},
    {"id": "A03", "family": "F", "governing_refs": ["gov"], "criterion": "Complete two-line output matches the declared replacement criterion.", "applicability": {"state": "REQUIRED", "reason": "Actual declared output criterion.", "fact_refs": ["comparison"]}, "outcome": {"state": "PASS", "reason": "Stipulated full comparison supports this conditional criterion.", "evidence_refs": ["sample"]}, "requires": ["A01", "A02"]},
    {"id": "A04", "family": "F", "governing_refs": ["gov"], "criterion": "Input remains unchanged and no undeclared local output changed.", "applicability": {"state": "REQUIRED", "reason": "Output integrity and bounded mutation.", "fact_refs": ["comparison"]}, "outcome": {"state": "PASS", "reason": "Stipulated source/diff coverage only.", "evidence_refs": ["sample"]}, "requires": ["A01", "A02"]},
    {"id": "A.api-harness", "family": "D", "governing_refs": ["gov"], "criterion": "A newly introduced API boundary requires an API harness.", "applicability": {"state": "NOT_APPLICABLE", "reason": "No API or new/material external interpretation boundary exists; local protections remain A01-A04.", "fact_refs": ["local"]}, "outcome": {"state": "NOT_APPLICABLE", "reason": "Positive scope exclusion, not absence of testing tools.", "evidence_refs": []}},
    {"id": "A.release", "family": "E", "governing_refs": ["gov"], "criterion": "Publication/origin/live-stage proof for a published deliverable.", "applicability": {"state": "NOT_APPLICABLE", "reason": "No publication stage is in this task.", "fact_refs": ["local"]}, "outcome": {"state": "NOT_APPLICABLE", "reason": "No deployment claim.", "evidence_refs": []}}
  ],
  "references": [
    {"id": "gov", "kind": "GOVERNANCE", "locator": "docs/nexus-northstar-knowledge-promotion-acceptance-v1.md", "source": "Accepted Nexus source at starting HEAD; not an illustration", "scope": "CP1-CP5, ES1-ES6 and conditional A-F", "revision": "bbc13a9d32f7ce0d65cfbe5da8d02b1cd05764e5"},
    {"id": "criteria", "kind": "EVIDENCE", "locator": "illustration:A:criteria", "source": "STIPULATED fictional note; no real observation", "scope": "Conditional review of one local output write; no real transformation or task closure."},
    {"id": "sample", "kind": "EVIDENCE", "locator": "illustration:A:note", "source": "STIPULATED fictional note; no real observation", "scope": "Fictional A input/output identities, bounded grant, complete two-line comparison and source-only preservation note."}
  ]
}
```

### B — New anonymous public structured-input boundary

```json
{
  "schema_version": "1.0",
  "record_id": "illustration.B.1",
  "basis": "ILLUSTRATIVE",
  "subject": {"id": "B.task.v1", "configuration_id": "B.profile.v1", "criteria_refs": ["criteria"]},
  "purpose": "Select early D01 obligations for a proposed anonymous API; no implementation/readiness/live privacy claim.",
  "governance_refs": [
    "gov"
  ],
  "profile": [
    {"id": "boundary", "claim": "New public caller-controlled structured input; nonpersistent demo response intended; no UI/session/provider/publication yet.", "value": "label and copies input", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "parameters", "claim": "Decoder/format and L/R/S/W choices are not supplied.", "value": null, "basis": "UNKNOWN", "refs": ["sample"]},
    {"id": "testing", "claim": "Machine-testable criteria, material consequences, deterministic secret-free fixtures feasible, small harness proportionate.", "value": "four harness conditions hold", "basis": "PROVIDED", "refs": ["sample"]}
  ],
  "checks": [
    {"id": "B02", "family": "B", "governing_refs": ["gov"], "criterion": "Contract describes computation/demo only and no unsupported delivery promise.", "applicability": {"state": "REQUIRED", "reason": "User-facing API claims must be truthful.", "fact_refs": ["boundary"]}, "outcome": {"state": "PASS", "reason": "Stipulated design description supports only declared intent.", "evidence_refs": ["sample"]}},
    {"id": "B03", "family": "D", "governing_refs": ["gov"], "criterion": "Exact decoder/format, fields/types and source-interpretation policy are bound.", "applicability": {"state": "REQUIRED", "reason": "New external influence boundary applies now.", "fact_refs": ["boundary", "parameters"]}, "outcome": {"state": "UNKNOWN", "reason": "Required choices missing; no universal format selected.", "evidence_refs": []}},
    {"id": "B04", "family": "D", "governing_refs": ["gov"], "criterion": "S/L/R/W and pre-expansion rejection rules have bound evidence.", "applicability": {"state": "REQUIRED", "reason": "Material malformed/resource consequences.", "fact_refs": ["boundary", "parameters"]}, "outcome": {"state": "UNKNOWN", "reason": "No values or implementation evidence.", "evidence_refs": []}},
    {"id": "B05", "family": "D", "governing_refs": ["gov"], "criterion": "Sanitized error/disclosure and actual input/output/logging/retention paths are verified.", "applicability": {"state": "REQUIRED", "reason": "Arbitrary public input could be sensitive; no database does not prove privacy.", "fact_refs": ["boundary"]}, "outcome": {"state": "UNKNOWN", "reason": "Intended nonpersistence is not observed data-flow/retention evidence.", "evidence_refs": []}},
    {"id": "B07", "family": "D", "governing_refs": ["gov"], "criterion": "Actual no-provider/no-persistent-effect and repeat behavior are established at the assessed scope.", "applicability": {"state": "REQUIRED", "reason": "Declared demo mode is separate from effects.", "fact_refs": ["boundary"]}, "outcome": {"state": "UNKNOWN", "reason": "No endpoint or effect observations exist.", "evidence_refs": []}},
    {"id": "B08", "family": "F", "governing_refs": ["gov"], "criterion": "Relevant deterministic valid/invalid/malformed/resource/error/repeat cases are verified for the exact implementation.", "applicability": {"state": "REQUIRED", "reason": "All four accepted harness conditions hold.", "fact_refs": ["testing"]}, "outcome": {"state": "UNKNOWN", "reason": "No harness/implementation was executed.", "evidence_refs": ["sample"]}, "requires": ["B03", "B04", "B05", "B07"]},
    {"id": "B.release", "family": "E", "governing_refs": ["gov"], "criterion": "Later publication has its own release-stage evidence.", "applicability": {"state": "DEFERRED", "reason": "Future delivery scope/configuration/authority must be established separately.", "fact_refs": ["boundary"]}, "outcome": {"state": null, "reason": "Not assessed and no publication readiness claimed.", "evidence_refs": []}}
  ],
  "references": [
    {"id": "gov", "kind": "GOVERNANCE", "locator": "docs/nexus-cross-project-refinement-d01-d02-acceptance-v1.md", "source": "Accepted Nexus source at starting HEAD; not an illustration", "scope": "D01 §§3.1-3.3; accepted conditional evidence semantics", "revision": "bbc13a9d32f7ce0d65cfbe5da8d02b1cd05764e5"},
    {"id": "criteria", "kind": "EVIDENCE", "locator": "illustration:B:criteria", "source": "STIPULATED fictional note; no real observation", "scope": "Select early D01 obligations for a proposed anonymous API; no implementation/readiness/live privacy claim."},
    {"id": "sample", "kind": "EVIDENCE", "locator": "illustration:B:note", "source": "STIPULATED fictional note; no real observation", "scope": "Fictional API design and harness proportionality premises only; no actual policy parameters, harness, privacy or effects."}
  ]
}
```

### C — Unreproduced advisory finding

```json
{
  "schema_version": "1.0",
  "record_id": "illustration.C.1",
  "basis": "ILLUSTRATIVE",
  "subject": {"id": "C.task.v1", "configuration_id": "C.profile.v1", "criteria_refs": ["criteria"]},
  "purpose": "Conditional completeness of triage only; no defect clearance, fix or product-wide acceptance.",
  "governance_refs": [
    "gov"
  ],
  "profile": [
    {"id": "finding", "claim": "Advisory decorative clipping, optional in this contract; no required analyzer/security/accessibility premise is waived.", "value": "separator clipping report", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "attempts", "claim": "Three stipulated attempts do not reproduce; original context incomplete, intermittence not excluded.", "value": "NOT_REPRODUCED", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "cause", "claim": "No independent causal support.", "value": null, "basis": "UNKNOWN", "refs": ["sample"]},
    {"id": "scope", "claim": "Owner decision is limited triage with optional further diagnosis deferred, no UI change/publication.", "value": "triage only", "basis": "PROVIDED", "refs": ["sample"]}
  ],
  "checks": [
    {"id": "C02", "family": "B", "governing_refs": ["gov"], "criterion": "Original advisory source, exact criterion and attempted context omissions are retained.", "applicability": {"state": "REQUIRED", "reason": "Honest report, not a confirmed defect inference.", "fact_refs": ["finding", "attempts"]}, "outcome": {"state": "PASS", "reason": "Fictional report/attempt note retains the specified limits.", "evidence_refs": ["sample"]}},
    {"id": "C03", "family": "B", "governing_refs": ["gov"], "criterion": "Cause uncertainty and scoped optional disposition are separate from fix/false-positive claims.", "applicability": {"state": "REQUIRED", "reason": "D02 prevents semantic collapse.", "fact_refs": ["cause", "scope"]}, "outcome": {"state": "PASS", "reason": "Six concern notes state uncertainty, deferral and no repair.", "evidence_refs": ["sample"]}},
    {"id": "C04", "family": "F", "governing_refs": ["gov"], "criterion": "Triage-only record preserves six concerns, omissions and no dependent mandatory premise.", "applicability": {"state": "REQUIRED", "reason": "Current deliverable is the bounded triage record.", "fact_refs": ["scope"]}, "outcome": {"state": "PASS", "reason": "Conditional triage completeness only.", "evidence_refs": ["sample"]}, "requires": ["C02", "C03"]},
    {"id": "C.access", "family": "C", "governing_refs": ["gov"], "criterion": "Targeted access/meaning impact receives an additional observation.", "applicability": {"state": "OPTIONAL", "reason": "Adds decision value; no mandatory access premise is stipulated affected.", "fact_refs": ["finding"]}, "outcome": {"state": null, "reason": "Not performed; optional coverage remains unassessed.", "evidence_refs": []}},
    {"id": "C.further-diagnosis", "family": "B", "governing_refs": ["gov"], "criterion": "Further contextual reproduction/cause investigation is completed.", "applicability": {"state": "DEFERRED", "reason": "Explicitly optional investigation outside current triage closure.", "fact_refs": ["scope"]}, "outcome": {"state": "UNKNOWN", "reason": "Further evidence absent; deferred is not resolved.", "evidence_refs": []}}
  ],
  "references": [
    {"id": "gov", "kind": "GOVERNANCE", "locator": "docs/nexus-cross-project-refinement-d01-d02-acceptance-v1.md", "source": "Accepted Nexus source at starting HEAD; not an illustration", "scope": "D02 §§4.1-4.3", "revision": "bbc13a9d32f7ce0d65cfbe5da8d02b1cd05764e5"},
    {"id": "criteria", "kind": "EVIDENCE", "locator": "illustration:C:criteria", "source": "STIPULATED fictional note; no real observation", "scope": "Conditional completeness of triage only; no defect clearance, fix or product-wide acceptance."},
    {"id": "sample", "kind": "EVIDENCE", "locator": "illustration:C:note", "source": "STIPULATED fictional note; no real observation", "scope": "Fictional source/rule/report, three failed reproductions, incomplete original context and bounded owner triage disposition."}
  ],
  "diagnostic": {
    "observation": {"note": "Advisory separator clipping report, not a confirmed defect.", "refs": ["sample"]},
    "reproduction": {"note": "NOT_REPRODUCED in three stipulated contexts; original context incomplete.", "refs": ["sample"]},
    "cause": {"note": "UNKNOWN, not proof that no defect exists.", "refs": ["sample"]},
    "disposition": {"note": "Defer optional further diagnosis; finding/omissions retained; no superior required criterion waived.", "refs": ["sample"]},
    "remediation": {"note": "None; no patch or change authority inferred.", "refs": ["sample"]},
    "validation": {"note": "No repair validation; no repair PASS/FAIL or fixed/false-positive claim.", "refs": ["sample"]}
  }
}
```

### D — Reproduced defect, narrow remediation and scoped validation

```json
{
  "schema_version": "1.0",
  "record_id": "illustration.D.1",
  "basis": "ILLUSTRATIVE",
  "subject": {"id": "D.task.v1", "configuration_id": "D.profile.v1", "criteria_refs": ["criteria"]},
  "purpose": "Conditional old/new complete-sum correction chain; not real execution, universal correctness or extra write authority.",
  "governance_refs": [
    "gov"
  ],
  "profile": [
    {"id": "mismatch", "claim": "Trusted [2,3] old result 2, required 5; repeated under same subject/criterion.", "value": "old behavior fails complete sum", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "structure", "claim": "Independent fictional review shows old routine omits final index.", "value": "scoped structural cause", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "grant", "claim": "Separate grant covers only final-index correction old.v1 to new.v1.", "value": "bounded correction", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "regression", "claim": "Stipulated new complete sums: []=0, [7]=7, [2,3]=5; no additional coverage.", "value": "three named cases", "basis": "PROVIDED", "refs": ["sample"]}
  ],
  "checks": [
    {"id": "D.old.correctness", "family": "F", "governing_refs": ["gov"], "criterion": "Old routine sums all elements of [2,3].", "applicability": {"state": "REQUIRED", "reason": "Criterion contradicted in old subject.", "fact_refs": ["mismatch"]}, "outcome": {"state": "FAIL", "reason": "Stipulated old result 2 != expected 5; not hidden by new validation.", "evidence_refs": ["sample"]}},
    {"id": "D.cause", "family": "F", "governing_refs": ["gov"], "criterion": "Final-index omission has causal support within reviewed old behavior.", "applicability": {"state": "REQUIRED", "reason": "This record makes that narrow causal claim.", "fact_refs": ["structure", "mismatch"]}, "outcome": {"state": "PASS", "reason": "Structural review plus mismatch/reproduction, not symptom alone.", "evidence_refs": ["sample"]}},
    {"id": "D04", "family": "D", "governing_refs": ["gov"], "criterion": "Valid bounded grant covers the exact local correction.", "applicability": {"state": "REQUIRED", "reason": "Patch scope is an independent authority premise.", "fact_refs": ["grant"]}, "outcome": {"state": "PASS", "reason": "Separate stipulated grant, no runtime redesign authority.", "evidence_refs": ["sample"]}},
    {"id": "D.change", "family": "F", "governing_refs": ["gov"], "criterion": "Exact old/new correction is bound to the final-index issue.", "applicability": {"state": "REQUIRED", "reason": "Corrective closure needs relevant remediation.", "fact_refs": ["structure", "grant"]}, "outcome": {"state": "PASS", "reason": "Stipulated exact correction link, not validation.", "evidence_refs": ["sample"]}, "requires": ["D04"]},
    {"id": "D05", "family": "F", "governing_refs": ["gov"], "criterion": "New subject satisfies []=0, [7]=7, [2,3]=5.", "applicability": {"state": "REQUIRED", "reason": "Declared post-change regression criterion.", "fact_refs": ["regression"]}, "outcome": {"state": "PASS", "reason": "Conditional three-case evidence, not universal correctness.", "evidence_refs": ["sample"]}, "requires": ["D04", "D.change"]},
    {"id": "D.new-boundary", "family": "D", "governing_refs": ["gov"], "criterion": "New externally influenced interpretation boundary requires a fresh API harness.", "applicability": {"state": "NOT_APPLICABLE", "reason": "Trusted fixed numeric input and unchanged trust/parser boundary.", "fact_refs": ["mismatch", "structure"]}, "outcome": {"state": "NOT_APPLICABLE", "reason": "D05 regression still required.", "evidence_refs": []}}
  ],
  "references": [
    {"id": "gov", "kind": "GOVERNANCE", "locator": "docs/nexus-cross-project-refinement-d01-d02-acceptance-v1.md", "source": "Accepted Nexus source at starting HEAD; not an illustration", "scope": "D01 unchanged-trust case; D02 §§4.1-4.3", "revision": "bbc13a9d32f7ce0d65cfbe5da8d02b1cd05764e5"},
    {"id": "criteria", "kind": "EVIDENCE", "locator": "illustration:D:criteria", "source": "STIPULATED fictional note; no real observation", "scope": "Conditional old/new complete-sum correction chain; not real execution, universal correctness or extra write authority."},
    {"id": "sample", "kind": "EVIDENCE", "locator": "illustration:D:note", "source": "STIPULATED fictional note; no real observation", "scope": "Fictional old/new routine identities, repeated mismatch, independently reviewed omission, narrow grant/diff and listed regression values."}
  ],
  "diagnostic": {
    "observation": {"note": "Old [2,3] produced 2 instead of 5: scoped defect.", "refs": ["sample"]},
    "reproduction": {"note": "Deterministic repeat under old subject/criterion, not all inputs.", "refs": ["sample"]},
    "cause": {"note": "Supported for final-index omission by separate structural review plus mismatch.", "refs": ["sample"]},
    "disposition": {"note": "Only bounded final-index correction and relevant verification.", "refs": ["sample"]},
    "remediation": {"note": "Stipulated exact old.v1 -> new.v1 correction linked to grant and issue.", "refs": ["sample"]},
    "validation": {"note": "Stipulated new []/[7]/[2,3] regression PASS only; no real check ran.", "refs": ["sample"]}
  }
}
```

### E — Owner-selected fixed local input

```json
{
  "schema_version": "1.0",
  "record_id": "illustration.E.1",
  "basis": "ILLUSTRATIVE",
  "subject": {"id": "E.task.v1", "configuration_id": "E.profile.v1", "criteria_refs": ["criteria"]},
  "purpose": "Conditional existing bounded reader assessment; no actual read, scanning or Host qualification.",
  "governance_refs": [
    "gov"
  ],
  "profile": [
    {"id": "contract", "claim": "Unchanged fixed reader/parser and evidenced local contract, read-only/in-memory result; no interpretation/network/PII/publication.", "value": "existing inert reader", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "input", "claim": "One predeclared owner-selected ordinary file; trusted source; no includes/path expansion/symlink/reparse redirection.", "value": "fixed permitted file", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "result", "claim": "Fictional exact summary comparison and scoped no-mutation observation.", "value": "read-only result", "basis": "PROVIDED", "refs": ["sample"]}
  ],
  "checks": [
    {"id": "E01", "family": "A", "governing_refs": ["gov"], "criterion": "Existing reader/operation/configuration and read-only path are bound.", "applicability": {"state": "REQUIRED", "reason": "Prior verification is not inferred from selecting a filename.", "fact_refs": ["contract"]}, "outcome": {"state": "PASS", "reason": "Stipulated bound contract note, not real callability or invocation.", "evidence_refs": ["sample"]}},
    {"id": "E02", "family": "D", "governing_refs": ["gov"], "criterion": "Exact permitted file/provenance and no scope expansion/redirection are established.", "applicability": {"state": "REQUIRED", "reason": "Read-only still requires input/path identity.", "fact_refs": ["input"]}, "outcome": {"state": "PASS", "reason": "Stipulated exact file/path/source support only.", "evidence_refs": ["sample"]}},
    {"id": "E03", "family": "F", "governing_refs": ["gov"], "criterion": "Exact declared summary criterion matches this input/result.", "applicability": {"state": "REQUIRED", "reason": "Bound local result acceptance.", "fact_refs": ["result"]}, "outcome": {"state": "PASS", "reason": "Conditional deterministic comparison only.", "evidence_refs": ["sample"]}, "requires": ["E01", "E02"]},
    {"id": "E04", "family": "F", "governing_refs": ["gov"], "criterion": "Operation is read-only and no extra mutation occurred.", "applicability": {"state": "REQUIRED", "reason": "No-mutation claims need observation.", "fact_refs": ["result"]}, "outcome": {"state": "PASS", "reason": "Scoped fictional observation, not read-only configuration alone.", "evidence_refs": ["sample"]}, "requires": ["E01", "E02"]},
    {"id": "E.api-harness", "family": "D", "governing_refs": ["gov"], "criterion": "A newly introduced API/path parser requires new boundary verification.", "applicability": {"state": "NOT_APPLICABLE", "reason": "Selection within unchanged evidenced local scope; no new parser/trust boundary.", "fact_refs": ["contract", "input"]}, "outcome": {"state": "NOT_APPLICABLE", "reason": "Existing file identity/integrity remains E01-E04.", "evidence_refs": []}}
  ],
  "references": [
    {"id": "gov", "kind": "GOVERNANCE", "locator": "docs/nexus-northstar-knowledge-promotion-acceptance-v1.md", "source": "Accepted Nexus source at starting HEAD; not an illustration", "scope": "CP1-CP5, ES1-ES6 and conditional A-F", "revision": "bbc13a9d32f7ce0d65cfbe5da8d02b1cd05764e5"},
    {"id": "criteria", "kind": "EVIDENCE", "locator": "illustration:E:criteria", "source": "STIPULATED fictional note; no real observation", "scope": "Conditional existing bounded reader assessment; no actual read, scanning or Host qualification."},
    {"id": "sample", "kind": "EVIDENCE", "locator": "illustration:E:note", "source": "STIPULATED fictional note; no real observation", "scope": "Fictional existing reader contract, exact permitted source/file, no redirect/expansion and summary/no-mutation observations."}
  ]
}
```

### F — Authority exists, final external effects UNKNOWN

```json
{
  "schema_version": "1.0",
  "record_id": "illustration.F.1",
  "basis": "ILLUSTRATIVE",
  "subject": {"id": "F.task.v1", "configuration_id": "F.profile.v1", "criteria_refs": ["criteria"]},
  "purpose": "Document one original ambiguous external attempt; no provider contacted, retry or settlement authorized.",
  "governance_refs": [
    "gov"
  ],
  "profile": [
    {"id": "grant", "claim": "Independent fictional authorization is valid for one original bounded operation only.", "value": "one attempt scope", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "attempt", "claim": "Stipulated original operation op.original.1 dispatched; response/stream lost.", "value": "original attempt reported", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "final", "claim": "No authoritative final-state record for op.original.1.", "value": null, "basis": "UNKNOWN", "refs": ["sample"]},
    {"id": "cost", "claim": "Applicable final cost/exposure remains unsettled; no settlement evidence supplied.", "value": null, "basis": "UNKNOWN", "refs": ["sample"]}
  ],
  "checks": [
    {"id": "F.authority", "family": "D", "governing_refs": ["gov"], "criterion": "Grant validity covers the original exact action, not a replacement/retry.", "applicability": {"state": "REQUIRED", "reason": "Authority independent of technical availability.", "fact_refs": ["grant"]}, "outcome": {"state": "PASS", "reason": "Stipulated independent bounded grant only.", "evidence_refs": ["sample"]}},
    {"id": "F.attempt", "family": "D", "governing_refs": ["gov"], "criterion": "Original attempted-operation identity is associated with the scope named by the grant.", "applicability": {"state": "REQUIRED", "reason": "Reconciliation needs original identity.", "fact_refs": ["attempt"]}, "outcome": {"state": "PASS", "reason": "Stipulated original-attempt association only; not proof of complete safe admission or effect success.", "evidence_refs": ["sample"]}, "requires": ["F.authority"]},
    {"id": "F.final", "family": "D", "governing_refs": ["gov"], "criterion": "Authoritative final state of original operation is bound.", "applicability": {"state": "REQUIRED", "reason": "Stream loss/local timeout cannot settle effects.", "fact_refs": ["final"]}, "outcome": {"state": "UNKNOWN", "reason": "No authoritative final observation.", "evidence_refs": []}},
    {"id": "F.reconcile", "family": "D", "governing_refs": ["gov"], "criterion": "Original effect uncertainty is reconciled before unsafe retry/completion.", "applicability": {"state": "REQUIRED", "reason": "CP4/A2 unresolved effects retained.", "fact_refs": ["final"]}, "outcome": {"state": "UNKNOWN", "reason": "Original final state unresolved.", "evidence_refs": []}, "requires": ["F.attempt", "F.final"]},
    {"id": "F.cost", "family": "D", "governing_refs": ["gov"], "criterion": "Applicable final cost/exposure can be settled without treating unknown as zero.", "applicability": {"state": "REQUIRED", "reason": "Financial uncertainty separate from effect state.", "fact_refs": ["cost"]}, "outcome": {"state": "UNKNOWN", "reason": "Required final settlement evidence missing; no zero-cost inference.", "evidence_refs": []}},
    {"id": "F.retry-closure", "family": "F", "governing_refs": ["gov"], "criterion": "Any related retry/completion/settlement claim has resolved required premises.", "applicability": {"state": "REQUIRED", "reason": "No unsafe repeat or fabricated closure.", "fact_refs": ["final", "cost"]}, "outcome": {"state": null, "reason": "Not assessed favorably; mandatory gaps block this claim.", "evidence_refs": []}, "requires": ["F.authority", "F.reconcile", "F.cost"]}
  ],
  "references": [
    {"id": "gov", "kind": "GOVERNANCE", "locator": "docs/nexus-northstar-knowledge-promotion-acceptance-v1.md", "source": "Accepted Nexus source at starting HEAD; not an illustration", "scope": "CP1-CP5, ES1-ES6 and conditional A-F", "revision": "bbc13a9d32f7ce0d65cfbe5da8d02b1cd05764e5"},
    {"id": "criteria", "kind": "EVIDENCE", "locator": "illustration:F:criteria", "source": "STIPULATED fictional note; no real observation", "scope": "Document one original ambiguous external attempt; no provider contacted, retry or settlement authorized."},
    {"id": "sample", "kind": "EVIDENCE", "locator": "illustration:F:note", "source": "STIPULATED fictional note; no real observation", "scope": "Fictional independent grant and original-attempt identity only; no authoritative remote-final-state/cost evidence."}
  ]
}
```

### G — Callable capability, invocation not established

```json
{
  "schema_version": "1.0",
  "record_id": "illustration.G.1",
  "basis": "ILLUSTRATIVE",
  "subject": {"id": "G.task.v1", "configuration_id": "G.profile.v1", "criteria_refs": ["criteria"]},
  "purpose": "Observe capability dimensions independently; no invocation or artifact influence inferred.",
  "governance_refs": [
    "gov"
  ],
  "profile": [
    {"id": "available", "claim": "Fictional availability observation binds exact native renderer/version/environment/operation path.", "value": "CALLABLE=YES", "basis": "PROVIDED", "refs": ["sample"]},
    {"id": "invoke", "claim": "No invocation/receipt/attempt association supplied for this operation.", "value": null, "basis": "UNKNOWN", "refs": ["sample"]},
    {"id": "applied", "claim": "No invocation-output-to-artifact/acceptance association supplied.", "value": null, "basis": "UNKNOWN", "refs": ["sample"]}
  ],
  "checks": [
    {"id": "G.callable", "family": "A", "governing_refs": ["gov"], "criterion": "CALLABLE=YES for the exact bound renderer operation.", "applicability": {"state": "REQUIRED", "reason": "The scoped capability availability claim is assessed.", "fact_refs": ["available"]}, "outcome": {"state": "PASS", "reason": "Conditional availability evidence only.", "evidence_refs": ["sample"]}, "capability": {"ref": "sample", "dimension": "CALLABLE"}},
    {"id": "G.executed", "family": "A", "governing_refs": ["gov"], "criterion": "EXECUTED=YES for this particular operation.", "applicability": {"state": "REQUIRED", "reason": "An execution claim would need an independent trace.", "fact_refs": ["invoke"]}, "outcome": {"state": "UNKNOWN", "reason": "Availability is not invocation evidence.", "evidence_refs": []}, "capability": {"ref": "sample", "dimension": "EXECUTED"}},
    {"id": "G.applied", "family": "F", "governing_refs": ["gov"], "criterion": "APPLIED=YES to the named accepted artifact/state.", "applicability": {"state": "REQUIRED", "reason": "Attribution needs independent invocation/output/acceptance linkage.", "fact_refs": ["applied"]}, "outcome": {"state": "UNKNOWN", "reason": "Neither similarity nor availability proves application.", "evidence_refs": []}, "capability": {"ref": "sample", "dimension": "APPLIED"}}
  ],
  "references": [
    {"id": "gov", "kind": "GOVERNANCE", "locator": "docs/nexus-northstar-knowledge-promotion-acceptance-v1.md", "source": "Accepted Nexus source at starting HEAD; not an illustration", "scope": "ES5 / capability state model acceptance", "revision": "bbc13a9d32f7ce0d65cfbe5da8d02b1cd05764e5"},
    {"id": "criteria", "kind": "EVIDENCE", "locator": "illustration:G:criteria", "source": "STIPULATED fictional note; no real observation", "scope": "Observe capability dimensions independently; no invocation or artifact influence inferred."},
    {"id": "sample", "kind": "EVIDENCE", "locator": "illustration:G:note", "source": "STIPULATED fictional note; no real observation", "scope": "Fictional exact renderer/Host/operation/time availability record; invocation and application observations missing."}
  ]
}
```

## 12. Static design-test results and changed-profile controls

| Case | Static result / precise limit |
|---|---|
| A | Applicable local grant/integrity/comparison obligations represented; new API harness and release chain excluded for positive profile reasons. Conditional comparison support, actual transformation UNKNOWN |
| B | D01 applies at introduction; relevant choices/privacy/effects/harness remain UNKNOWN. Future publication DEFERRED, not readiness PASS. No fixed Apex constants or live endpoint inferred |
| C | Six concerns separated; limited triage completeness can be supported while cause/additional coverage remain unknown. Deferral is not resolution; no patch/repair validation claim |
| D | Old criterion FAIL retained; independent structural support, bounded grant, exact correction and listed new regressions conditionally support a narrow correction claim. No automatic status advancement or universal correctness |
| E | No new boundary solely from fixed owner-selected filename; original reader/path/source/no-mutation requirements retained. Actual reader/Host execution not established |
| F | Valid bounded authority coexists with final-effect/reconciliation/cost UNKNOWN. Original identity retained; required dependencies prevent a favorable retry/completion/settlement conclusion |
| G | Callability support cannot advance EXECUTED/APPLIED. Missing operation traces remain UNKNOWN, not NO. No installed/callable maturity ladder or inferred grant |

Manual counterfactual checks: removing A's source-preservation evidence makes A04 UNKNOWN; allowing E arbitrary paths/reparse/parser changes invalidates its old exclusion and requires D01 review; adding a mandatory accessibility criterion to C prevents optional-deferral closure; removing D's cause evidence leaves cause UNKNOWN even if new behavior passes; removing D's correction/authorization link prevents a fixed claim; giving F only a cancel acknowledgment leaves final effects/cost UNKNOWN; adding an installation observation to G leaves invocation/application UNKNOWN. These are documentary consistency checks, not executed scenarios, automated assertions or security experiments. F describes an ambiguous original attempt, not qualification of its pre-dispatch admission: all applicable pre-effect authority, financial/resource and Host controls would still require their separate evidence before any real dispatch.

Fixture references are intentionally stipulated, without fabricated hashes/measurements. Their version/criteria names distinguish fictional subjects. No real grant or evidence is minted. Real use would need independently bound sources appropriate to each property; illustrative PASS cannot cross the basis boundary. No material accepted-governance ambiguity is exposed by these examples.

## 13. SEPARATE STATIC ADVERSARIAL REVIEW

Method: a separate challenge pass by the same assistant after drafting, not an independent staffed reviewer, external expert or runtime qualification. Criterion: retain accepted semantics in a small passive record without imported authority. Manual attacks below were considered against the final text/examples; source authority remains external to the record. No evaluator was implemented to make these conclusions.

| Attack | Review finding / final guard |
|---|---|
| Applicability/outcome collapse; deferred status treated satisfied | Independent objects; NOT_APPLICABLE never PASS; required work cannot be erased by a DEFERRED label, §3 |
| UNKNOWN disappears through omission/null/NO defaults | UNKNOWN explicit; null separates unassessed classification/result; absent conditional metadata supplies no favorable premise, §§2-3 |
| N/A hides unavailable tools, evidence or authority | Positive supported profile reason required; E retains actual local protections; §§3,8,11 |
| Check PASS despite unmet dependency | Requires binds mandatory premises, source scope and exact criterion; F remains unresolved, §§3,8,11 |
| Evidence/claim collapse or self-labeled GOVERNANCE/source | Source existence/hash/type declaration cannot establish acceptance/trust/support. Accepted versions must be independently resolved; ordinary tool/model/context text cannot issue policy, §§1,4 |
| Incomplete check list becomes whole-task acceptance | No aggregate PASS/readiness; purpose/criteria/coverage explicit; structural validation alone cannot prove omission-free selection, §§2,8 |
| Configured state becomes observed enforcement/live output | Separate fact basis, scoped evidence and five independent release facts; B's intent does not satisfy effect/privacy checks, §4 |
| Credential/capability availability becomes grant | Separate authority check bound to valid issuer/action; snapshot creates none, §§4,8 |
| Invocation becomes effect, local cancellation becomes remote cessation/settlement | Original attempt, final/reconciliation and cost are separate; F blocks unsafe closure, §4 |
| Remediation becomes validation or NOT_REPRODUCED becomes FALSE_POSITIVE | D02 orthogonal concerns; C no repair; D old FAIL/new scoped evidence separate, §§5,11 |
| Diagnostic free text overrules trusted analyzer or required security result | Superior source contracts/closed results retain force; REQUIRE_REVIEW preserves UNKNOWN, not relabeling, §§1,5,8 |
| Session restoration/checkpoint renews grant or settles effect | F02 separate references and authority/effect checks, no session-state shorthand, §6 |
| Context selected/loaded reported as actually used | F01 existing selection/use observations distinct; missing actual-use linkage remains unknown, §6 |
| APPLIED forced from EXECUTED; failure cannot be executed | Independent dimension references and original values; failed invocation can be executed, §4/G |
| Excessive required fields/enums/metadata make a DSL | Only scope/version/provenance/check/reference minimum; conditional diagnostics/capability; no expressions/commands/extension bags. Literal text is never policy code, §§2,9 |
| Dependency references create workflow/scheduler | Logical support only, no ordering/actions/transitions. Cycles incoherent, not interpreted, §3 |
| Finding database or persistent memory emerges | One snapshot, no history/assignment/deadline/store; existing evidence references, §§2,5-6 |
| Microsoft concepts silently promoted; provider/framework assumptions | F01/F02 reuse accepted obligations/references only; no new universal SDK/session/context requirement, §§1,6 |
| G2/HQ proof inferred from general assessment | Architecture/qualification bindings remain separate and absent; no provider facts established or A0-A6/P1-P12 edits, §§1,4 |
| Future unknown member/version used as bypass | Explicit support/versioned review required; default refusal, not permissive field ignoring, §7 |
| Stipulated fixture support reused as real evidence | Mandatory basis distinction plus source/coverage binding; ILLUSTRATIVE never real execution/acceptance, §§2,10-12 |
| Generic privacy reference leaks keys or forces access | Sanitized locator only; no embedded secrets/access capabilities; inaccessible evidence UNKNOWN, §7 |

**Review result: ACCEPTABLE AS WRITTEN FOR DESIGN CHECKPOINT ONLY.** No material architecture/governance conflict found. This is a documentary judgment, not independent security certification or approval to build/execute a consumer.

## 14. Deferred dimensions and unresolved evidence

Deferred: executable schema/reader/evaluator, programmatic source trust/freshness validation, concrete accepted-check selection/completeness validation, static prototype semantics tests, integrations with closed Nexus records, session/checkpoint payloads, automatic context use attribution, persistence and any runtime enforcement. These need separately scoped design/authorization when needed; no engine is justified merely by this snapshot.

No new governance clarification is required for this scoped passive design. A future consumer cannot decide arbitrary human criteria, evidence truth or source authority from JSON structure alone; that limitation is explicit, not resolved by this document. Future conflicting accepted sources or unavailable mandatory evidence still require review/STOP. Profile/evidence facts for the seven illustrations remain stipulated; real execution, grants/effects, installed/callable/executed/applied observations and Host qualification are not established. Provider hard-bound gaps and pending OpenAI escalation are untouched.

## 15. Validation and checkpoint boundary

Authorized validation: manual source/field/fixture/anti-bloat/adversarial review; UTF-8/LF/no-BOM/newline/whitespace/control-character checks; local reference checks; standard JSON syntax inspection of seven fenced examples only; bounded secret-pattern scan; git diff --check; existing relevant repository governance tests. No custom parser, semantic contract/schema validator or proposed evaluator is implemented, including in external tooling. Checkpoint verification helpers only check repository bytes, document hygiene and existing manifest/test behavior.

The canonical MANIFEST integration is isolated from mutable local ecosystem state: export the accepted tracked source snapshot, add this document, use the existing builder twice, require exact byte equality and unchanged original 219 entries, and verify all entries against working/index/committed bytes as applicable. Commit scope is only this design and required MANIFEST update. Existing source documents, architecture, code, frozen refs and sealed V4 remain unchanged.

Relevant tests are existing ecosystem isolation/package, GitHub distribution, quality-loop evaluation and R5 capability inventory. Known baseline/environment limitations remain the Scout recommendation_ready versus evidence_only mismatch and missing mcp_types import; neither is repaired nor relabeled here. Actual run counts/results and manifest/commit hashes are emitted in the final checkpoint report; this document claims no full-green regression. No full runtime/provider qualification is performed.

Observed bounded run for this checkpoint: 57 tests, 52 PASS, three SKIP, one FAIL (release-artifact Scout expectation), one ERROR (R5 test module cannot import missing mcp_types), exit 1. The run used an isolated tracked-source/package snapshot; no new representation consumer or qualification fixture ran. These are the predeclared baseline/environment limitations, not resolved tests. Source code is unchanged, and no dependency installation or baseline repair is attempted.

## 16. Decision and exact next independent task

**B. MINIMAL REPRESENTATION DESIGN COHERENT WITH DEFERRED DIMENSIONS — READY FOR CONTROLLED STATIC PROTOTYPE REVIEW**

Rationale: one scoped snapshot preserves applicable accepted meanings with shared source/evidence references, independent applicability/outcomes and required-premise gaps. Concrete sessions/checkpoints/context attribution and executable consumer behavior are deliberately deferred; this is sufficient for documentary/static prototype review, not operational enforcement.

Recommended next independent task: separately authorize a controlled static-prototype design/review using this version's inert A-G records and contradictory-input examples, with explicit scope for any syntax/structural consumer and selected accepted semantics. Do not assume this checkpoint authorizes writing such a consumer. Its acceptance criteria must retain source/claim separation, all mandatory UNKNOWNs and no execution/effect/grant/qualification inference; no runtime/provider integration, architecture change or blanket gate engine.

A/B design conclusions do not grant implementation authority. Representation checkpoint acceptance is not capability approval, Host qualification, P1-P12/HQ PASS, G2 readiness or a release. Scenario 01-04 remain NOT RUN; HQ1-HQ5 remain NOT PASS; HQ6 remains NOT STARTED; Positive Host Binding remains ABSENT; G2 remains HOLD; OpenAI human support escalation remains pending and untouched.
