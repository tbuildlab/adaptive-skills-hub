# Nexus Pre-G3 / Pre-G4 Contract and Qualification Design v1

**READINESS DESIGN ONLY. Logical obligations derived from accepted architecture, not new wire schemas, trust mechanisms, stage implementation or qualification evidence.**

## 1. Authority, scope and compatibility

The [reconstruction](nexus-pre-g3-pre-g4-roadmap-reconstruction-v1.md) and [matrix](nexus-pre-g3-pre-g4-readiness-matrix-v1.md) identify exact authority, gaps and dependencies. This document completes the useful logical design in W06-W13 and the compatibility/acceptance preparation in W03/W04. Governing sources: [Roadmap](nexus-roadmap-v2.md), G3/G4 fields 4/6-12/15-16 and domain/relationship/policy tables; [A1-A4/A6](nexus-pre-g2-architecture-addendum-v1.md); accepted CP1/CP4/CP5 and ES1-ES6 from the reconstruction. No new mandatory mechanism is accepted by this design.

| Existing mechanism | Reuse obligation and boundary |
|---|---|
| Slice 2 discovery; Slice 3C subjects, intake policy, quarantine and evaluation lineage | Consume exact immutable component/revision/tree and policy/evidence identities. Existing closed states and ZERO_AUTHORITY remain unchanged; separate approval never changes quarantine history. A new revision requires new review. |
| Slice 3A applicability and Slice 3B closed validators | Reuse current subject/reviewed applicability and scoped declared-fact checks. Do not add arbitrary validators or interpret evaluation PASS as approval, runtime execution, current availability or semantic source truth. |
| G1 Host/model profiles, conformance and selection | Keep capability facts separate from authority. Recheck current mandatory eligibility; process-local observation seals cannot authenticate approval origin or be restored as durable trust. |
| G2 domain durability, reservations, native lifecycle and reconciliation | Future G3/G4 consume accepted stable interfaces. Do not supply a substitute ledger, scheduler, Host adapter or crash guarantee while these interfaces are absent. |
| Existing project context, planner and bounded advisory caller | Existing context is not a confirmed-decision/disclosure store. Advice stays non-authoritative. Keep domain logic out of planner core; no changes to frozen routing, result vocabularies, schemas or advisory runtime. |
| Qualified Host analysis, retrieval, authoring, rendering, browser and compaction | Delegate execution and generic understanding. Nexus validates domain evidence, scope and obligations; no parallel memory, graph, retrieval or code-intelligence engine. |

The following catalogs specify minimum logical content already named by the Roadmap. They do not choose serialization, signatures, numeric bounds, timestamps/clock authority, storage format, callable APIs or database technology. Those choices remain W30-W32 or owner decisions. Schema unsupported/malformed/missing mandatory evidence must not produce an eligible/confirmed result; exact parser/result vocabulary belongs to later accepted implementation.

## 2. G3 records and evidence interfaces

| Logical record | Minimum content and binding obligation | Still required before implementation/qualification |
|---|---|---|
| CapabilityApprovalRecord | Exact component/revision/tree; intake-policy identity; review-evidence references; permitted use and constraints; issuer and independently authenticated approval evidence; validity; revocation relationship. Bind evidence to the same reviewed subject, not a catalog, mutable URL or repository name. | Explicitly accepted issuer/security boundary, origin verification/protected delivery, validity semantics and actual G2 durability. Candidate-created JSON and creator-writable storage alone cannot authenticate it. |
| RegistrationRecord | Approval reference, exact capability identity, reviewed applicability and execution-mechanism metadata. Projection must be traceable to current valid approval and may not invent supported capabilities. | Protected projection/readback behavior and stable persistence interface. Mechanism metadata is not installation or execution authority. |
| RevocationRecord | Affected approvals/subjects, effective scope and reason. Bind to authorized revocation evidence and relevant approvals; preserve historical evidence without re-enabling eligibility. | Issuer/origin acceptance, ordering/visibility guarantees and durable replay behavior supplied through accepted G2 infrastructure. |

Logical interface sequence, not an executable API:

1. Receive an exact immutable quarantined subject and bound review references; validate source-policy coverage, revision, policy, license/dependency facts and review freshness. A scanner or model supplies review evidence, never approval.
2. Obtain a separately authorized issuer decision through the future accepted origin mechanism. Independently verify issuer, intended subject, permitted use, constraints and validity. No decision is issued in this preparation.
3. Establish current revocation and durability facts before exposing a bounded registration projection. Readback must refer to authoritative records rather than trusting the projection's own claims. If ordering or storage outcome is unknown, withhold new eligibility until verified; no best-effort optimistic publication.
4. Assess current routability/availability and G1 eligibility independently. Registration is necessary only where applicable and cannot create a callable/installable Host path. Installed, callable, executed and applied facts remain separate.
5. Before a later task dispatch/resume, bind exact effective subject/configuration, current approval/revocation, task authority and G2 resource/budget reservation. No review, capability approval, registration or credential substitutes for those checks.

The eligibility consumer needs verified origin, immutable subject/policy/evidence identity, current permitted scope/validity/revocation, current availability and separately issued task authority. How that consumer obtains a trusted current snapshot is UNKNOWN until W25/W30 are resolved. This design does not silently assume an atomic read, stable network state or a creator-signed object.

## 3. G3 failure, recovery and rollback design

Partial authoritative write, missing readback or corrupt projection must not be interpreted as successful registration. Preserve original operation references and the uncertain outcome; reconcile via actual G2 durability/observation before retrying. Duplicate/replayed input must not mint a second approval, extend validity, renew authority or duplicate an associated external action. Do not invent a new idempotency scheme before G2 contracts exist.

Revocation must block subsequent eligibility. Exact in-flight cancellation/effect handling is governed by the actual qualified G2 binding and task grant; revocation cannot retroactively erase an attempted effect or settled cost. Test the review-to-eligibility race and resumed work after revocation. If required revocation visibility cannot be proven, do not release the next dispatch. After restart, reconstruct a projection only from verified durable subject/origin/revocation facts; serialized G1 seals or a remembered conversation are insufficient.

Disable/rollback stops new registration/eligibility consumption and preserves immutable quarantine, authoritative history, revocations and unresolved operations. A stale projection or older accepted component cannot reinstate revoked or expired approval. Any separately authorized installation/activation, if eventually used, has its own effect/cancellation/reconciliation obligations; G3 does not install it. There is no blanket fallback to an unapproved capability or former permissive policy.

## 4. G4 records, scoped context and impact interfaces

| Logical record | Minimum content and binding obligation | Boundary and unresolved choice |
|---|---|---|
| ProjectDecisionRecord | Decision/constraint; explicit project/task scope; source/evidence; approving authority; validity; proposed/confirmed/superseded/disputed state; supersession; retention class. | A model proposal, remembered text or advice cannot confirm itself. Actual authorized confirmation, retention durations and protected persistence remain required. No new automatic decision state machine. |
| ContextManifest | Included source references, transformations, recipients, omissions and disclosure limits. | Record derived reduction as derived; bind scope/freshness/supersession and accessible originals where required. Do not claim opaque compaction preserved constraints without evidence. |
| CapabilityRelation | One accepted type, exact version-bound endpoints and provenance. | Closed eight-type Roadmap vocabulary; relationships never grant trust, approval or permission. Missing endpoints, cycles or conflicts must remain visible. |
| ChangeImpactRecord | Repository identity; base commit; exact dirty/input snapshot; changed surfaces; dependencies/consumers; shared contracts; validation obligations; unexamined areas. | No import-only completeness claim. Bind the analyzed input to the execution/validation subject; changed input invalidates the old scope. Host supplies analysis; Nexus checks binding/coverage. |
| WorkflowPack | Version, applicability, required capabilities, domain policy, acceptance and evidence requirements. | Pack restrictions intersect superior policy/task grants. No pack expands authority or automatically adopts an external capability. No new engine or universal domain schema. |

Context flow: select only permitted project/task sources and recipients; retain provenance and omissions; independently validate any confirmation against its authorized source; surface conflicts/staleness/disputed or superseded facts before planning. Proposed/disputed/expired facts cannot silently replace confirmed constraints. Supersession must refer to the exact replaced source/decision and retain the relevant history. Forgetting/deletion under an authorized retention rule must not erase unresolved obligations or misrepresent history; exact retention/recovery behavior requires later acceptance for real data. No cross-project retrieval by name similarity or default recipient inheritance.

Relations support a bounded dependency/impact record, not a graph runtime: `requires`, `uses`, `depends_on`, `conflicts_with`, `produces`, `validated_by`, `available_through`, `source_of`. Validate typed endpoints and provenance, expose cycles/conflicts, and sequence conservatively when write/resource relationships are unknown. An edge stating available_through does not prove present availability; validated_by does not prove an actual validation ran.

Impact flow: bind repository/base and dirty byte basis before analysis; identify changed interfaces and relevant consumers, including shared interactions, event scopes, DOM/layout assumptions and non-import consumers where applicable; record validation obligations and unexamined areas; bind test/artifact observations to that same scope. A changed tree requires new/revalidated analysis. Unknown consumer coverage is an explicit gap, not empty impact. No universal static detector or imported Meranti framework/timing constants are implied.

## 5. Two minimum pack contracts

| Requirement | Website | Source-backed Report |
|---|---|---|
| Applicability and inputs | Exact task/repository/base/dirty subject, relevant site surfaces and current source facts; domain scope agreed before execution. | Exact question, permitted sources/data and their identity/date/scope, artifact format and claim/calculation requirements. |
| Capability dependency | Current qualified analysis/coding/browser/rendering facilities. Already accepted capabilities avoid G3; new external code/Skills need actual G3 outputs and any intake extension first. | Current qualified retrieval/analysis/authoring/rendering facilities. Same conditional G3 rule; existing tools do not become current-qualified merely by being installed. |
| Required evidence | Shared interaction ownership/state assumptions; affected consumers; relevant regressions; accessibility and boundary/transition checks; source/implementation/test/visual approval distinguished. | Source-to-claim mapping, contradictions/uncertainties, reproducible calculations, actual artifact inspection and format-appropriate rendering; source evidence distinct from prose/derived summary. |
| Conditional effects | Deployment only if explicitly authorized: bind local source, actual deployment source, configured origin and live observations separately; resolve attempted/unconfirmed remote effects before unsafe retry. | Retrieval/disclosure/publication/persistent external writes only within explicit grants; provenance or a rendered local artifact cannot prove remote delivery. |
| Useful acceptance | Real bounded workflow meeting the predeclared task/domain rubric with inspectable evidence. No fabricated contacts/metrics or approval of unobserved states. | Real bounded workflow answering the defined task with supported claims/calculations and inspected artifact. No invented source, result or historical evidence. |
| Stopping/reopening | Stop polishing the accepted artifact; reopen for an authorized requirement change, bound regression, material contradiction or new security/evidence defect. | Same stop/reopen rule; retain source/date limits and distinguish later corrections from original acceptance. |

The rubric must be locked before real qualification: exact subject, scope, source quality/coverage, relevant validation obligations, justified comparison/benefit metrics and thresholds, review/owner authority and stopping rules. Numbers, framework choices, real datasets and deployment targets are not invented here. A missing mandatory criterion blocks acceptance; a genuinely irrelevant optional check may be excluded only with an explicit reason under the task/domain scope, never to turn a failed mandatory test into PASS.

## 6. G4 interruption, reduction, disable and recovery

Resume from actual G2 domain facts, not Host-idle/completed status, summary text or restored conversation. Revalidate current grants/budget, source/decision scope and freshness, supersession/revocation, exact input/artifact identity and changed impact obligations. Preserve accepted artifacts; altered bytes require their own validation and cannot inherit visual/owner approval.

Compaction/reduction must preserve the binding to original sources, constraints, omissions, failures, unresolved effects and unexamined areas. A brief may guide continuation without confirming a decision or settling an operation. If originals needed for a claim are unavailable, retain UNKNOWN and do not accept the dependent claim. Native context facilities are reused rather than replaced.

Cancellation stops further dispatch and separately records cancellation request/acknowledgment, late effects, reconciliation and unsettled exposure. Interrupted or attempted-but-unconfirmed deployment/publication is not absent; reconcile before unsafe replay. Local timeout/termination cannot settle remote billing/effects. Resource/budget exhaustion preserves unresolved work without expanding grants. Disable the affected pack/new work while keeping mandatory policy checks, original evidence, accepted artifacts and unresolved obligations; rollback is a separately authorized, observed operation where it has effects. No fallback to a more permissive pack, unqualified Host or previous task authority.

## 7. Future acceptance gates and independent oracles

| Gate | Future acceptance criterion / required observation | What this preparation establishes |
|---|---|---|
| DESIGN ACCEPTANCE | Contracts preserve Roadmap/A0-A6 and distinguish origin/approval/registration/eligibility/task authority; owner accepts any real new issuer/security boundary. | Logical design and separate adversarial static review only. No new origin/boundary accepted. |
| STATIC/OFFLINE VALIDATION | After wire contracts are separately specified, test exact identities/policy/scope/versions, malformed/missing fields, deterministic serialization and bounded projections with explicit synthetic labels. Existing regression must preserve frozen behavior. | Inert scenario/oracle specification and existing foundation regression. No future wire parser/fixture validation claimed. |
| RUNTIME VALIDATION | G3 independently authenticated benign approval/registration plus drift/revocation/restart negatives; G4 each initial pack completes a useful real bounded workflow and relevant poisoning/impact/reduction negatives. | NOT RUN, BLOCKED_BY_G2; new external adoption additionally BLOCKED_BY_G3. Refusal-only tests do not establish useful success. |
| PROVIDER/HOST EVIDENCE | Exact positively qualified complete binding for task operations, environment/authority/resources/budget/cancellation/observation; provider facts only if that binding uses one. | ABSENT. Old profiles, docs, mocks, child self-report and historic demos do not satisfy it. |
| EXTERNAL-EFFECT VALIDATION | For each actual authorized effect, bind operation/attempt/final observation and gaps; reconcile ambiguous outcomes/exposure before unsafe retry. | NOT RUN and conditional on effect scope, not a universal deployment/cloud requirement. |
| OWNER ACCEPTANCE | Exact artifact/subject, applicable independent review and regression, supported gates, accepted issuer/data/rubric decisions and separately authorized release/freeze workflow. | Readiness checkpoint only. No stage acceptance, execution, merge, tag or freeze authority. |

The following fixed documentary cases are future experiment specifications, not executable fixtures or executed results. Unrelated optional effects/capabilities are not required merely to exercise a case. Future harnesses must supply exact authorized subject/versions, source-external origin or effect observations, applicable scope and a useful success control. No proposed result names below extend any frozen enum.

| Case | Fixed logical input/mutation | Expected result and independent evidence oracle | Deferred gate |
|---|---|---|---|
| G3-N01 | Candidate JSON/scanner PASS/model claims approval; or correct subject but no authorized issuer | No approval/current eligibility; authoritative origin verification fails/missing. Scan/child declaration is insufficient. | Origin/owner plus G2 |
| G3-N02 | Approval bound to A; present B or a changed revision/tree/license/dependency | No inherited approval. Independently re-read exact immutable subject/policy/review identity and changed facts. | G2/current subject |
| G3-N03 | Stale/expired/modified approval or unsupported schema; missing mandatory dependency/policy mismatch | No eligibility; trusted readback and validity/review/schema checks expose exact deficiency. No UNKNOWN coercion. | Wire/origin/G2 |
| G3-N04 | Revocation arrives before subsequent eligibility, including resumed work | Subsequent eligibility denied; actual durable revocation/current readback and release ordering verified. In-flight effects retained separately. | G2/revocation |
| G3-N05 | Tampered registration projection or approved-but-unavailable capability | No new routability/dispatch grant. Compare authoritative approval/review facts and current G1 availability. | G2/projection |
| G3-N06 | Interrupt write/projection; duplicate/replay input; restart with serialized trust seal | Withhold uncertain eligibility, reconcile authoritative outcome before unsafe replay; no duplicate/renewed authority. Observe actual durable operations/recovery, not mock calls. | G2/durability/origin |
| G3-N07 | Roll back to stale pre-revocation projection; malicious candidate tries frozen routing | Revocation remains effective and Slice 3C authority remains none; independent current record/routing boundary observation. | G2/quarantine isolation |
| G3-N08 | Capability approved/present but no task grant, invalid transition or insufficient reservation | No side effect; actual admission/resource/budget boundary denies before dispatch. No installation/activation inferred. | Qualified G2 |
| G4-N01 | Retrieved/model entry requests confirmation, broadens grant or leaks across namespace | No confirmation/grant/disclosure; compare authorized source and observed recipient/project scope. | G2/owner data |
| G4-N02 | Conflicting/stale/disputed/superseded decision; forget source while obligation unresolved | Conflict/UNKNOWN preserved; no silent replacement or lost obligation. Trusted source/validity/supersession readback. | G2/context |
| G4-N03 | Reduction omits failed validation, mandatory constraint or unresolved effect | No dependent acceptance; source-to-brief omissions comparison exposes missing facts; originals retained where required. | G2/reduction |
| G4-N04 | Forged/wrong-version relation, missing endpoint, cycle or unknown writer | No authority from edge; invalid evidence exposed, unresolved resources conservatively sequenced. Bound endpoint/source check. | Wire/G2 |
| G4-N05 | Analyze base A, execute dirty B; omit shared event/DOM consumer or transition state | Revalidate subject; do not declare affected coverage complete. Bind actual tree/artifacts and affected consumer/boundary observations. | G2/Website |
| G4-N06 | Report unsupported claim, mismatched source/date/calculation or uninspected render | No accepted claim/artifact until required mapping/calculation/inspection evidence exists. Independently reproduce relevant calculation/inspect actual output. | G2/Report |
| G4-N07 | Pack proposes permissions beyond superior intersection or uses missing/revoked new external component | Deny conflicting work; no implicit authority/capability substitution. Verify grant intersection/current G3 evidence only for new adoption. | G2; G3 if adopted |
| G4-N08 | Interrupt/cancel workflow after authorized but unconfirmed effect; lose stream/controller; replay | Stop new dispatch, retain attempted/UNKNOWN effect/cost, reconcile before unsafe retry. Bind original operation and actual final/gap observations; no success from local timeout. | G2; effect evidence if applicable |
| G4-N09 | Exhaust budget/resources; resume under revoked task grant or stale evidence | No expanded grant/dispatch; preserve exposure and incomplete work. Qualified enforcement and current resume records required. | Qualified G2 |
| G4-N10 | Accepted artifact altered or advice relabeled implementation/validation/visual approval | Old acceptance cannot bind new bytes; evidence states remain distinct. Observe exact subject and actual validation/approval source. | G2/owner acceptance |

Positive controls remain mandatory: one exact benign separately approved/registered G3 fixture with unchanged Slice 3C; real bounded Website and Report successes. A controlled static mutation can later check a parser's refusal but cannot prove authenticated issuance, durable recovery, denial before effects, cancellation or privacy enforcement. Every case above is NOT RUN in this readiness program.

## 8. Finite readiness exit and resumption

Useful logical contracts, compatibility, rollback/failure design, both minimum pack rubrics and gate-separated scenario oracles are now prepared. No prototype answers a remaining origin/durability/Host/wire question without preselecting unaccepted mechanisms; none is warranted. Numeric limits and real fixtures await their actual interfaces/authority, not a speculative engine.

Remaining execution work stays C/D; issuer, real-data/rubric and execution choices stay E; actual interfaces/credential mechanisms stay F in the matrix. Resume only when relevant accepted G2 evidence/contracts or explicitly authorized decisions exist. No immediate owner action is required merely to retain these preparation artifacts. Human OpenAI support evidence, if received, must be adjudicated separately at a safe checkpoint.

A0-A6/P1-P12 and frozen artifacts remain unchanged. Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 Runtime HOLD; OpenAI human escalation PENDING. G3/G4 NOT ENTERED. No provider, network, credentials, runtime/authorization/memory implementation or release activity.
