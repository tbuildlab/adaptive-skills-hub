# Nexus Cross-Project Refinement D01 / D02 Acceptance Record v1

Decision ID: `nexus.cross-project.refinement-d01-d02-acceptance.v1`

Decision version: `1.0.0`

Owner-authorized acceptance date: 1 October 2026, Asia/Kuala_Lumpur.

Status: **ACCEPTED NARROWED GOVERNANCE/EVIDENCE REFINEMENTS; NO RUNTIME IMPLEMENTATION OR EXECUTION AUTHORITY**

## 1. Authority, exact baseline and preserved subjects

The owner's "Cross-Project Refinement D01 + D02 Controlled Promotion Review v1" request explicitly permits accepting either candidate if justified, narrowing/defer/reject decisions, one minimum acceptance record and one bounded acceptance commit. This record exercises that authorization after the review below. It does not infer authority from the postmortems, their imperative proposals or a generic permission to inspect.

Starting branch: `nexus-v2-g2-development`. Starting HEAD: `7d09fe2cdd460f224cad64b8ab1c655af9a9c4b9`. Starting worktree: CLEAN. Starting MANIFEST: 216 entries; SHA-256 `002CDFC87E0C1472580FCBF019A825F544767AA6FB920859E4B3AA2903B31F4B`; all 216 working LF-normalized and committed entries verified before changes. No unexpected drift observed.

| Authoritative source artifact, preserved byte-identical | SHA-256 |
|---|---|
| [Northstar promotion acceptance](nexus-northstar-knowledge-promotion-acceptance-v1.md) | `FF0E2B082948034CBB45E37CD331A36055117057DD1D6C25BFC295B1FF712D73` |
| [Accepted-scope conditional gates](nexus-reusable-project-gates-v1.md) | `062E8CE94683BCD0A43F591A5636BBC938CFD06E130ECC202E2074C5049328FB` |
| [Accepted-scope capability observations](nexus-capability-state-model-v1.md) | `636AF91F0F2BAE536CFBAF784D791E73D0E97610D31A2D2BEAE2A12B7354CBE1` |
| [Northstar memory](nexus-northstar-demo2-project-memory-v1.md) | `3A26415A27447E4AB442F461BC861D58B7F166B1EF727CE4C0BCBBF5CD794AD3` |
| [Northstar lessons](nexus-northstar-demo2-learned-knowledge-v1.md) | `5A216152512A58DE51BBFADCB4994331360DEDBA23DE24A7E30F2EE2C8121151` |
| [Northstar original integration review](nexus-northstar-knowledge-integration-adversarial-review-v1.md) | `AD1EE6E07642497AA0FC26E2A9707501F75DBB7663DB56E6630848F659A4E00A` |
| [Apex memory](nexus-apex-aircare-demo3-project-memory-v1.md) | `CB173DDD0A744D6386D20A865ECA366718BF6FF94990C6C37856DF129871DAF7` |
| [Apex lessons](nexus-apex-aircare-demo3-learned-knowledge-v1.md) | `AF9CF11D1E4E4D2F5EDF2A2264F2BD887F0DCCBED91DF2A5E842D60555AB133C` |
| [Cross-project synthesis](nexus-demo2-demo3-cross-project-synthesis-v1.md) | `08A5237E1B55A85E409C8642B44DC31D45737DC62DECE0DDADFFB9AB75422BF0` |
| [Apex integration adversarial review](nexus-apex-knowledge-integration-adversarial-review-v1.md) | `040577CA1907DFD7ECFCC061C5E7975D65FC6B7C767C651E3E3C8C0A6613DF6B` |

The Northstar acceptance record controls the accepted scope of historical proposal documents. This additive overlay resolves the pending status only for synthesis §6's D01/D02 as narrowed here. Other Apex rules/gates/examples remain the factual checkpoint's classifications. No original evidence grade, prior acceptance disposition or historical text is rewritten.

Original Apex source: 48,732 bytes / 916 lines, SHA-256 `DE9ABCE0578E7DD1B9E398CD177E0C9B79D17FDE67ECCAA663EF9487A1E01F2E`; Northstar source: 46,088 bytes / 704 lines, SHA-256 `4170F3F387D4B6625ADAB49CB2D0F5F5AF78FB7A74F4233FA808DCC170CB2DD8`. Both exact archives and current original bytes remain unchanged. These retrospective sources were untracked in their application checkouts; historical behavior is source-reported, not rerun or retrospectively independently verified by this decision.

## 2. Independent decisions and evidence strength

Overall decision: **B. ACCEPT WITH NARROWING / PARTIAL ACCEPTANCE**. Both candidates survive, but only their bounded documentary deltas are accepted. No new gate family, serialized schema, enum or lifecycle is accepted.

| Candidate | Individual decision | Accepted increment and excluded expansion |
|---|---|---|
| D01 | ACCEPT_NARROWED_REFINEMENT | Early boundary/risk/policy/evidence requirement assessment in existing Gate D, linked to A planning and F readiness; proportionate deterministic harness only where justified. Reject every-input/every-task automation and Apex constants |
| D02 | ACCEPT_NARROWED_REFINEMENT | Separate evidence-bound observation, reproduction, cause, disposition, remediation and validation concerns in existing triage/review records. Reject a linear issue state machine, compulsory causal investigation and replacement of trusted analyzer/validator semantics |

**D01 basis:** Apex original §§11, 19-20, 22 and lessons L09/L12 report late boundary hardening/tests and propose an earlier decision. Northstar original §3 reports tests already in Phase 3; §15 and K18 support meaningful boundary checks, not a repeated late-testing failure. The accepted Gate D already selects input/privacy/effect checks, and F already requires scope-bound acceptance. Missing delta: explicitly make the assessment when a relevant boundary is first introduced or materially changed, before asserting readiness, rather than discovering its evidence requirements only at release review.

**D02 basis:** Apex original §§8, 11, 16, 21, 28 and lessons L04/L20 preserve rendered-context false positives, NOT REPRODUCED / ROOT CAUSE UNKNOWN hydration, reproduced overflow and recorded correction/later checks. Northstar §§8.1, 13 and K09/K22 support evidence discipline with UNVERIFIED exact audit details; they do not establish a verified repeat false-positive or hydration event. CP1/CP5, ES1/ES3 and B/F already cover disposition, subject binding and limits. Existing static findings and closed evaluation results already exist; missing delta: explicitly distinguish the six diagnostic concerns when triage or repair claims could otherwise collapse them.

For each specific delta, confidence is **SINGLE_PROJECT_EVIDENCE + ARCHITECTURE_DERIVED**. **TWO_PROJECT_CONVERGENCE** supports broader boundary testing and evidence discipline, not proof of repeated late testing or identical diagnostic outcomes. No new **EXTERNALLY_VERIFIED** experimental evidence is supplied. Shared portfolio/tool/author context limits generalization; two projects are not universal empirical proof. Acceptance is a bounded governance judgment, not measured workflow superiority.

## 3. D01 accepted semantics: early, relevant boundary assessment

### 3.1 Trigger and minimum assessment

When an authorized task first introduces or materially changes an externally influenced or user-controlled input boundary capable of affecting application/workflow state, output, resources, security, privacy or external effects, evaluate its boundary policy and evidence needs at design/introduction time. Do not wait until claiming that boundary readiness-complete. Material change includes a changed parser/format, source trust, privilege/data flow, limits, recipient/effect, or failure/retry behavior that can invalidate existing evidence. Reuse unchanged bound evidence; do not retest unrelated work.

This refines the existing Gate D applicability/subchecks and Gate F closure evidence, with A planning references where useful. It does not create a top-level gate or mandate a named architecture/tool. Not every function parameter, local file, source review, or ordinary task is a newly introduced trust boundary. Classify actual source, interpretation and consequences; local is not automatically trusted, remote is not automatically effectful, and authentication does not make payloads intrinsically safe.

Use the existing assessment/contract record, with references where already documented:

1. Name the exact boundary, subject/configuration, source/trust assumptions and relevant governing criteria.
2. Identify actual correctness, safety, privacy, resource and effect risks, including authority-sensitive interpretations.
3. Declare only applicable policy dimensions and their expected behavior/limits; classify evidence requirements with the accepted REQUIRED / OPTIONAL / NOT_APPLICABLE / DEFERRED meanings.
4. Determine whether deterministic tests are feasible, materially useful and proportionate; declare the minimum relevant cases and evidence method before claiming readiness.
5. Supply and verify the required evidence for the bound boundary before treating it readiness-complete. Keep uncovered, failed, stale or conflicting mandatory properties unresolved; affected closure/activation remains blocked.

Relevant dimensions may include type/format, size/resource limits, encoding/parsing/schema/fields, authentication/authorization, origin/source trust, sensitive data, sanitized errors, side effects, duplicates/retries, timeout/cancellation, abuse or provider handoff. Select from the actual interface/threat model; do not require every dimension for every input. Origin/source checks do not substitute for authorization. Validation of input or a test PASS creates no permission to perform effects.

### 3.2 When a deterministic harness is REQUIRED

Each boundary property required by actual scope, accepted criteria or risk must have evidence proportionate to that property and effect. A minimum deterministic harness becomes REQUIRED for relevant behavior where **all** the following hold:

- The relevant behavior/property has a meaningful machine-testable criterion.
- A regression could materially affect correctness, safety, privacy, resources or effects.
- Deterministic verification is reasonably available for that criterion, including reusable existing contract tests or secret-free fixtures when those prove the applicable property.
- Testing burden is proportionate to the risk and task scope.

Document the judgment and reuse the smallest sufficient harness; do not generate a parallel suite merely for this refinement. These conditions choose an evidence mechanism, not whether a superior mandatory security property still applies. A mandatory test imposed by higher-priority/project criteria remains mandatory. Session tool absence, missing authority, cost avoidance or convenience cannot turn an established REQUIRED test/property into OPTIONAL or NOT_APPLICABLE. Ambiguous security-relevant applicability remains UNKNOWN and blocks the affected claim/action.

Where deterministic verification does not meet the above conditions, a scoped alternative may satisfy the required property only if permitted by the governing criteria and accepted through the existing authorized review path. Record the method, exact coverage, expected criterion, limitations and reason it supplies the necessary evidence. It cannot weaken the property or replace an explicitly required test without the separately authorized criteria change. If the alternative cannot establish a mandatory property, keep UNKNOWN / DEFERRED and stop the related readiness/activation claim. No unavailable method becomes a fabricated PASS.

Harness presence, number of tests or a mock PASS is not safety, live delivery, remote cancellation or settled cost. Safe deterministic fixtures can prove local contract behavior; actual provider security/effect properties retain independent qualified evidence, authorization and reconciliation requirements. This acceptance grants no provider calls, credential collection, installations or live test writes.

### 3.3 Generalization and explicit exclusions

Applicability can include requests/forms, uploads, webhooks, messages/events, imported structured data, callbacks or external tool/model output entering a trusted workflow. It is independent of HTTP/JSON/Node. Model/tool output remains data/evidence rather than an authority issuer; relevant parsing, resource, interpretation and approval boundaries still apply.

No universal promotion of Apex's 8 KB, 800 ms, honeypot, same-origin, JSON, HTTP, particular headers, Node tests, exact count or API architecture. Northstar's thresholds, duplicate mapping and technologies also remain examples. No automatic harness for every external input, all Markdown transformations, every local filename parameter or an unchanged trusted internal value. No blanket exemption for demo/read-only/local tasks when an actual input/privacy/resource/effect risk exists. Neither demo mode nor synthetic data supplies live-effect authorization or proves non-retention outside observed channels.

### 3.4 D01 adversarial semantic cases

These are **static thought cases**, not executed tests or new evidence about a deployed system. Decisions are conditional on the stated scope; no new runtime applicability engine is implied.

| Case | Trigger/applicability reasoning | Minimum evidence / over- and under-trigger guard |
|---|---|---|
| T01 Static local Markdown transformation | Fixed trusted text handled only as data, no changed trust/effect boundary: no added D01 harness; existing F integrity remains | Inspect scoped output/source binding. If untrusted imported markup is rendered/interpreted or disclosed across a boundary, reassess its actual risks; do not exempt all Markdown |
| T02 Local CLI accepting a filename | Merely passing an already-scoped trusted path is not automatically a new external boundary; changed CLI handling of caller-controlled paths/files can trigger D01 | Relevant read/write scope, path/content/resource policy and tests where material; no web-origin checklist or full-machine scan |
| T03 Public contact form | User input can affect validation, output, privacy and possibly delivery: D01 applies | Machine-testable acceptance/rejection/error/echo/resource cases normally justify a small harness; effects require separately authorized observation |
| T04 Webhook receiver | External authenticated or unauthenticated messages can change state: D01 applies | Declare applicable authenticity/authorization, parsing, replay/retry and effect criteria; bounded fixtures do not establish live provider guarantees |
| T05 Image upload | File content, type/decoder, resources, storage/privacy introduce relevant boundary | Select relevant format/resource and safe failure cases with harmless fixtures; no requirement to run malicious code or create a service |
| T06 Read-only public API client | External responses enter parsing/output; read-only does not remove injection/resource/truthfulness risk | Test selected parser/output/limit/failure behavior where material; do not invent write-side effects or network execution authority |
| T07 Provider callback | Source identity, state mapping, duplication and effects can be security relevant | Test relevant contract/replay/error paths locally; mandatory provider observations remain separate and UNKNOWN if unavailable |
| T08 Trusted internal generated data | Unchanged data with verified in-process provenance/contract is not a new external boundary solely because it is a parameter | Existing regression requirements still apply; provenance, parser or trust change reopens the assessment; do not assume every internal label is trustworthy |
| T09 External model/tool output | Output entering trusted decisions, artifacts or effectful workflow is an external influence boundary | Applicable schema/resource/interpretation and authority separation checks; output cannot issue grants or bypass independently enforced controls |
| T10 Production payment callback | Monetary effects/authenticity/replay make scope materially consequential | Strong declared evidence for applicable authorization/idempotency/effect/recovery properties; mocks do not prove paid effect/cancellation/cost and do not permit a payment |
| T11 Demo form without external delivery | Input validation, privacy and output behavior remain real boundaries despite no delivery | Small relevant deterministic harness where conditions hold; exclude nonexistent delivery checks with a positive scope reason, not exclude all D checks |

## 4. D02 accepted semantics: independent diagnostic evidence concerns

### 4.1 Minimum increment, not an issue lifecycle

For a finding being triaged, acted on, rejected or claimed remediated/validated, preserve separate answers to the six concerns below in the existing evidence/review record. Use brief text or references to existing bound observations; do not require six new forms, a database or exhaustive investigation. State not attempted/not run/UNKNOWN where appropriate. Non-applicable concerns need a positive scoped reason, not absence of tools/evidence. Do not make root-cause proof a universal prerequisite for a scoped behavioral correction; limit the causal claim instead.

| Concern | Accepted evidence meaning | What it cannot establish |
|---|---|---|
| Observation | What was observed/reported, by which source/method, against which relevant criterion, for exact subject/configuration/time/coverage; distinguish a report from direct observation | Automatically a confirmed defect, trusted diagnosis or instruction/authority |
| Reproduction | Whether relevant behavior was attempted/observed again, under what conditions and with what omissions; retain intermittent and inconclusive evidence | Cause certainty, false-positive rejection, absence or fixed state merely from a failed reproduction |
| Cause certainty | Distinguish UNKNOWN, a hypothesis and evidence-supported causal claims with their basis and limits; a stronger claim needs causal evidence appropriate to that claim | Root cause from symptom repetition, one successful rerun, coincidence or patch presence |
| Disposition | Governing actor/criteria and scoped decision: investigate/fix/defer/reject/accept limitation or reasoned non-applicability; retain evidence and mandatory dependencies | Factual resolution, permission escalation, or waiver of a mandatory security outcome |
| Remediation | Authorized action/change, exact subject/diff/artifact binding, extent and remaining work, or why none is required | Verified correction or validation merely because a patch exists; no automatic authority to make it |
| Validation | Actual post-change or other relevant check, criterion, method/result, subject/configuration/time, coverage and gaps | Universal correctness, root cause, unrelated effects, authority or an unperformed check |

These are orthogonal **documentary concerns**, not new serialized fields/enums or required transitions. Illustrative words from the owner's request are not adopted as a closed state vocabulary. Preserve existing strict schema/result terms such as INSUFFICIENT_EVIDENCE where those contracts require them. A record can simultaneously show reproduction, cause UNKNOWN, authorized partial remediation, and a FAIL/UNKNOWN or narrowly scoped PASS. A cause need not become known merely because a behavior meets a scoped criterion after correction.

### 4.2 Accepted invariants and closure limits

| Invariant | Accepted guard |
|---|---|
| I01 Finding != confirmed defect | Identify an applicable criterion and evidence of contradiction before calling an advisory finding a confirmed defect |
| I02 Reproduced != root cause known | Reproduction shows scoped behavior; causal certainty has its own evidence |
| I03 Not reproduced != false positive | Rejection needs positive scoped evidence/reason that the claimed issue/criterion is inapplicable or incorrectly attributed; not simply no repeat symptom |
| I04 Not reproduced != fixed | Keep attempted conditions/coverage and unresolved issue; do not fabricate repair |
| I05 Root cause unknown != no defect | A failing required criterion still fails even if its cause is unknown |
| I06 Patch applied != validated | Record the actual change separately; corrective closure claims need relevant evidence, not just a diff |
| I07 Validation pass != universal correctness | PASS covers the bound checks/property, not every state/device/security/effect or future configuration |
| I08 False-positive rejection requires evidence/reason | Bind detector/rule/subject/context, positive counter-evidence and review basis; do not rewrite/suppress the original observation |
| I09 Deferred != resolved | Keep reason, dependency, impact and mandatory blockers; no authority for deferred work |
| I10 Accepted limitation != fixed | Authorized limited acceptance names remaining uncertainty/scope, never changes a factual grade or waives a superior mandatory property |
| I11 Insufficient evidence retains UNKNOWN | Missing/stale/conflicting evidence remains unresolved; no silent advancement or causal certainty from status wording |

In this overlay, a corrective closure claim such as "fixed" or "correction validated" needs both a relevant bound authorized remediation and the required verification of the affected criterion. If one is missing, state the narrower fact: change applied, current check passed, symptom not seen, or cause UNKNOWN. A standalone validation PASS for an unchanged subject requires actual bound checks, not invented remediation; it does not establish that an earlier finding was fixed. An unrelated change followed by symptom disappearance is not causal attribution. Evidence can establish a current scoped property without proving the historical root cause; keep those claims separate. Historical source-reported fixes are not retroactively regraded or rewritten.

An optional unresolved diagnostic can coexist with scoped task acceptance only under the already accepted applicability rules: no mandatory premise depends on it, omission/impact/disposition explicit, uncertainty preserved. Required failed/unknown/deferred security, effect, qualification or acceptance conditions still block the related action/claim. "Accepted limitation", "not reproduced" and "false positive" are not alternative authorization or security bypass routes.

### 4.3 Existing findings and capability orthogonality

Actual `ash/ecosystem_evidence.py` `_finding` / `_build_static_report` already bind subject/evidence/analyzer/configuration, category, severity, reasons, disposition and zero authority. `ash/ecosystem_bridge.py` validates closed `_STATIC_RULES` and provenance. `ash/evaluation.py` and [Slice 3B](nexus-post-r5-runtime-integration-slice3b.md) already bind checks/results to exact subjects. [Slice 3C](nexus-post-r5-runtime-integration-slice3c-adr-pds.md) preserves quarantine/approval separation.

D02 cannot replace these schemas, change trusted rule severity/disposition, override deterministic findings or erase required review/STOP outcomes. A diagnostic counter-observation is separate evidence; any legitimate disputed-policy resolution still follows existing governance, never a free-text relabeling. No analyzer result becomes optional because it cannot be reproduced as a UI symptom.

INSTALLED / CALLABLE / EXECUTED / APPLIED remain the four independent capability dimensions. D02's remediation concern is about an artifact/change, not the capability model's APPLIED dimension. Validation of an artifact/criterion is separate from tool presence, invocation, output attribution, approval and effect authority. INSPECTED is an observation, CONCEPT ADOPTED design provenance, IMPLEMENTED artifact state and VALIDATED scoped check evidence; none becomes a new capability lifecycle state. No linear issue or capability state machine is introduced.

### 4.4 D02 adversarial semantic cases

These are static review cases, not executed reproductions, fixes or validation receipts. Reproduction is never mandated by this decision where it would be unsafe or unauthorized.

| Case | Separate concerns and accurate conclusion | Invalid inference blocked |
|---|---|---|
| F01 Analyzer warning reproduced manually | Keep original warning, actual observed behavior and applicable criterion; confirm defect only with criterion contradiction; cause may remain UNKNOWN | Repeated symptom automatically means known root cause or all analyzer rules can be reclassified |
| F02 Analyzer warning rejected after inspection | For an advisory finding, record positive scoped context/criterion counter-evidence and governing disposition; inspection may suffice without executing risky behavior | Inspection alone or lack of repro declares any security blocker false; mandatory analyzer contracts remain intact |
| F03 Intermittent hydration not reproduced | Retain historical report, attempted subject/conditions, lack of observed repeat and ROOT CAUSE UNKNOWN; remediation/validation not invented | NOT_REPRODUCED means no bug, fixed, failure of every validation, or cleared mandatory property |
| F04 Overflow reproduced at one viewport | Reproduction + applicable criterion establishes scoped defect; cause separately evidenced; authorized fix and later measured matrix qualify only those contexts | One viewport proves all layouts/devices or a source report becomes a new experiment |
| F05 Patch applied; regression not run | Remediation observed/bound; required validation missing -> UNKNOWN/NOT_RUN, affected closure blocked | Patch presence advances to validated/resolved |
| F06 Failing test; cause unknown | Actual bound FAIL retained, cause UNKNOWN; further action separately authorized | Unknown cause invalidates the observed failure or no defect exists |
| F07 Symptom disappears after unrelated change | Record changed subject and current scoped observations; causal link and original-resolution claim remain unsupported unless evidence establishes them | Coincidence proves the change fixed the historical root cause |
| F08 Performance advisory without measurements | Observation/advice exists; applicable measured-impact evidence missing, recommendation deferred as scoped; no measurement invented | Static build/detector becomes CWV or a mandatory performance requirement is waived |
| F09 Provider failure with incomplete observation | Local failure/stream evidence recorded; remote effect/cancellation/cost may remain UNKNOWN; reconciliation before unsafe retry | Local error or no reproduced failure proves remote absence, settled cost or permission to retry |
| F10 User complaint without reproducible case | Retain report/source, known conditions and missing information; reproduction/cause UNKNOWN or not attempted, scoped disposition | Complaint automatically confirms a defect, or no repro justifies dismissing it as false positive |

## 5. Narrowing, rejected expansion and bureaucracy review

| Candidate | Value of the accepted delta | Burden and false-positive control | Excluded/deferred portion |
|---|---|---|---|
| D01 | Earlier requirements decision can reduce late boundary/test gaps and ambiguous readiness claims; preserves input/privacy/resource/effect safety | One existing-record applicability decision; reuse sufficient tests/evidence; relevant cases only; no new top-level gate. Static/local/unchanged tasks do not automatically acquire a harness | Reject universal automation, full dimension checklist and Apex constants; future tooling/automatic classification/test generation NOT AUTHORIZED |
| D02 | Distinct observations prevent unsupported diagnostic, causal and repair claims; preserve original findings and regression evidence | Existing triage record/references; brief UNKNOWN/not attempted is valid; causal investigation only if required for actual claim/property. No six separate forms or mandatory unsafe reproduction | Reject giant enum/lifecycle/tracker and mandatory root-cause proof for every fix; implementations and new schema fields NOT AUTHORIZED |

No empirical reduction in defects or reporting cost has been measured. Benefits are supported governance judgments, not a benchmark. Burden can narrow optional observations or select an allowed evidence method; it cannot erase a mandatory security/property requirement. Existing receipts can satisfy overlapping A/D/F or B/F concerns without duplication. Short task summaries remain sufficient when the required facts are already bound elsewhere.

All earlier Northstar exclusions/deferred items, Apex project-specific choices, 22-rule/10-gate deduplication and original evidence grades remain unchanged. The accepted increment does not impose retrospective testing/triage on either frozen demo, resolve hydration/performance/unknown logs, or alter any other candidate.

## 6. Architecture consistency and authority boundary

This follows the existing additive acceptance pattern used by [Northstar acceptance](nexus-northstar-knowledge-promotion-acceptance-v1.md) and [Pre-G2 acceptance](nexus-pre-g2-architecture-acceptance-v1.md): exact reviewed subjects/hashes, scoped owner authorization, minimum overlay, unchanged originals, canonical manifest addition and one focused commit. No extra catalog or separate canonical architecture document is needed.

- [V1.2 context/rules](v1.2-product-architecture-spec.md), §§10-11: source/trust/authority distinctions and superior rules remain; external model/tool content cannot issue permissions.
- Existing A-F/applicability remain authoritative. D01 refines D planning/evidence timing and F readiness; D02 refines CP1/CP5, ES1/ES3 and relevant existing review/acceptance records. No new rule issuer, seventh gate, applicability engine or general policy language.
- The [capability model](nexus-capability-state-model-v1.md), R4/R5 trace meanings and five-fact deployment identity are unchanged. Artifact remediation/validation does not supply capability execution/application, deployment or live effects.
- [G1](nexus-v2-g1.md), [R2](nexus-runtime-r2-mcp-architecture.md), [R4](nexus-runtime-r4-host-handoff.md), [R5 inventory](nexus-runtime-r5-host-capability-inventory.md), [R5 enhancement](nexus-runtime-r5-adaptive-enhancement.md), Slice 3B/3C and their frozen implementation/schema surfaces are unchanged.
- [Pre-G2 A0-A6](nexus-pre-g2-architecture-addendum-v1.md), P1-P12, HQ1-HQ6, qualification/LPAC STOP conditions and [roadmap](nexus-roadmap-v2.md) remain intact. Alternative diagnostic/input evidence cannot replace mandatory qualified Host enforcement, native budget/cancellation bounds, independent authority or effect reconciliation. This is not G2 or G4 implementation/qualification.

Governance acceptance is not an execution grant. No authority to implement a boundary detector, automatic test generator/harness runtime, finding tracker/database, state machine/applicability/policy engine, UI, HostAdapter/OpenAIHostAdapter or G2 Runtime. No installation, providers, credentials, network experiment, payments, resources, deployment or security-policy change. No OpenAI contact/comment/adjudication or escalation change. No amendments to prior commits, merge, push, tag or freeze.

## 7. Separate static adversarial acceptance review

Review result: **ACCEPTABLE AS WRITTEN FOR THE NARROWED GOVERNANCE/EVIDENCE PROMOTION**. The review is a separate static pass after drafting by the same assistant; no independent human or separately attested reviewer is claimed. Cases in §§3.4/4.4 are semantic thought cases only. The record is integrity-bound by the final MANIFEST, not a circular self-hash.

| Attack | Final accepted guard |
|---|---|
| Every input creates heavy tests | §3 requires relevant newly introduced/materially changed boundary and four harness conditions; references and reusable sufficient evidence minimize burden |
| Trusted/local data always hostile or always exempt | Classify actual source/provenance/interpretation/consequence; unchanged trusted internal data not auto-triggered, local path/parser changes can matter |
| Model output ignored as a boundary | T09 and §3.3 explicitly include relevant model/tool outputs; no output-derived authority |
| Callback or demo under-tested | T07/T10/T11 retain authenticity/effect/privacy/validation requirements where applicable; no mode-based exemption |
| Testing unavailable becomes non-applicable | §3.2 preserves established REQUIRED status; alternative only allowed by governing criteria with sufficient evidence; missing mandatory evidence stops affected readiness |
| Burden/cost weakens qualified security evidence | §§3.2/6 preserve superior mandatory properties, P1-P12/HQ and Host evidence mechanisms; no generic equivalence waiver |
| Input validation grants effect authorization | §§3.1-3.2 preserve separate actor/task authority and independent provider effects |
| Exact Apex values/technology become universal | Explicit exclusions in §3.3; decisions are criterion/risk-based, not HTTP-only |
| Six diagnostic concerns form a giant state machine | §4 says orthogonal documentary concerns, reference reuse, no closed vocabulary/schema/transitions |
| False positive from no repro or inspection alone | I03/I08 and F02 require positive counter-evidence and governing context; mandatory analyzer rules untouched |
| Non-reproduction or unknown cause means no bug | I04/I05 and F03/F06/F10 retain missing causal/reproduction evidence and actual failures |
| Patch implies validated or coincidence implies cause | I06/I07 and F05/F07 require bound change and actual relevant verification; causal claim separate |
| Root-cause work forced for every fix | §4.1 allows causal UNKNOWN with a demonstrated scoped correction; no unsupported causal claim |
| UNKNOWN eliminated by status/disposition | I11 and existing required applicability preserve insufficiency and limits; deferred/accepted limitation not fixed |
| New fields override trusted static/validator records | §4.3 forbids rewriting schemas, rule severity/disposition or zero-authority/mandatory results |
| Capability remediation and APPLIED collapse | §4.3 separates artifact/change concern from invocation/output attribution and keeps four dimensions |
| Historical proposals/reports rewritten as accepted facts | §1 and §5 keep all ten documents/archives byte-identical; only D01/D02 pending governance status resolved |
| New engine, provider task, Host qualification or G2 starts | §§6/8 prohibit implementation and effects; exact scope is one overlay plus MANIFEST |

No architectural conflict identified. Bounded final clarifications: reasonably available/proportionate testing governs method selection, not downgrade of an existing required property; alternative evidence must meet the same property under actual governing criteria. Correction validation needs relevant remediation and verification, while standalone validation of an unchanged subject does not require an invented fix. Diagnostic concerns never allow reinterpretation of mandatory analyzer or Host outcomes. These restrictions are included in the final accepted wording, not deferred to a future implementation.

## 8. Integration, verification, preserved state and next independent work

Add only this acceptance record to the existing canonical manifest: 216 unchanged entries + one = 217. Validate ten source hashes/archives, local references, decisions/invariants/case coverage, UTF-8/LF/no-BOM/terminal-newline/whitespace/control hygiene and bounded secret-pattern scan. Hashes prove bytes, not truth or authority; scan non-matches do not certify arbitrary secret absence.

Use the existing builder on an isolated Git export, rebuild twice with exact byte equality, verify working/staged/committed entries and original-entry identity, inspect exact two-file staged scope and `git diff --check`, preserve frozen local refs, verify clean post-commit state and unchanged application source checkouts. Final record/manifest/commit hashes belong to the external acceptance receipt; this document cannot predeclare full regression PASS or embed its own final hash.

Run relevant package/isolation, distribution and quality/evaluation checks plus existing R5 inventory loading. Known baseline limitations remain: Scout expected `recommendation_ready` vs observed `evidence_only`, missing `mcp_types`, and embedded-runtime skips without configured inputs. Report actual outcomes; do not repair tests/source, install dependencies or claim full green. An unexplained new failure or scope/hash drift stops integration.

**Runtime enforcement is NOT implemented or authorized.** Accepted semantics add no new permission, provider experiment, model call or Host binding. Pending OpenAI human escalation remains untouched. Scenario 01-04 = NOT RUN; HQ1-HQ5 = NOT PASS; HQ6 = NOT STARTED; Positive Host Binding = ABSENT; G2 = HOLD. A0-A6/P1-P12 unchanged.

Recommended next independent work item, under a separate scoped task: a secret-free documentary applicability exercise using a local Markdown transformation, an externally influenced input contract and an unreproduced advisory finding. Predeclare expected D01 selection and D02 evidence distinctions, compare reporting burden/false positives, and reuse existing records. No engine, application/provider run, new mandatory test framework or G2 implementation follows. Stop after this acceptance checkpoint; that exercise is not begun here.
