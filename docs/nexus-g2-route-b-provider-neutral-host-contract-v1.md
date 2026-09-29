# Nexus G2 Route B Provider-Neutral Host Contract v1

Document ID: `nexus.g2.route-b.provider-neutral-host-contract.v1`

Version: `1.0.0`

Date: 28 September 2026

Status: **PROPOSED DOCUMENTARY CONTRACT — NO HOST SELECTION, ACCEPTANCE OR EXECUTION AUTHORITY**

## 1. Result, authority and fixed evaluation boundary

**ROUTE B INTERFACE CONTRACT: COMPLETE.** This means the finite contract and its accepted-property traceability are complete, not that a provider implements it or that any runtime criterion passes.

Authority is the owner's Route B Provider Interface Evaluation request, attachment `281006f6-2fe2-4759-957c-27194a4f31c1`. Starting repository: `D:\chatgpt\安装skills\adaptive-skills-hub`, branch `nexus-v2-g2-development`, HEAD `ad9f68680ad07b34b0a614108735ccac99059340`, clean. This contract was derived and fixed before the current provider-documentation check. Provider limitations cannot change its mandatory properties.

The current Windows `26200.9550` LPAC binding remains formally exited as HOST QUALIFICATION BLOCKED for insufficient qualifying evidence, not a finding that Windows/LPAC is insecure. V4 and historical evidence remain unchanged. Scenario 01–04 NOT RUN; HQ1–HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD. Option D remains current and Option A remains HOLD. No previous G0/G1 authority transfers.

## 2. Existing accepted sources

The following source keys make the contract's traceability explicit. Historical proposal headings are read through their acceptance records.

| Key | Accepted property/source |
| --- | --- |
| A1 | [Pre-G2 addendum](nexus-pre-g2-architecture-addendum-v1.md) A1: qualified Host ownership, provider/model independence, distinct visibility/permission/trust/binding/prerequisites/executability, mandatory-unknown ineligibility. |
| A2 | Same addendum A2: complete pre-effect admission; transitive execution; qualified hard resource/money bounds; native lifecycle/observation; authority revalidation; reserve → dispatch → settle/reconcile → release; unsafe-retry prohibition. |
| A3/A6 | Same addendum A3/A6: separate task authority and credential facilities; no new secret platform; drift, observation gaps, revocation, late effects and revised cost. |
| R | [Roadmap V2](nexus-roadmap-v2.md) G1/G2 and recovery/budget rules: exact profiles and enforcing-layer conformance; one accepted capability; correlation IDs are not grants; separate cancellation acknowledgement, settled exposure and acceptance. |
| G1 | [G1](nexus-v2-g1.md), Versioned contracts, Evidence boundary, Policy/suitability/cost and Narrow real pilot: complete relevant path, fresh exact-binding evidence, unknown totals, no shipped actual-spend/whole-Host qualification. |
| HQ | [Host Scope & Exit](nexus-g2-host-qualification-scope-and-exit-decision-v1.md) §§2–4/6–9 through its [acceptance](nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md): HQ1–HQ5 equivalent threats in the actual boundary; separate HQ6 primitives; finite TCB and no recursive assurance project. |
| D | [Next Host Route Decision](nexus-g2-next-host-route-decision-v1.md) §§2–7 through the [current exit/route acceptance](nexus-pre-g2-current-lpac-host-exit-and-next-route-acceptance-v1.md): controller custody, native authority split, complete policy/input graph, hard exposure and remote reconciliation; BYOK model credential distinct from compute credential. |

Frozen [R2](nexus-runtime-r2-mcp-architecture.md), [R4](nexus-runtime-r4-host-handoff.md) and [R5](nexus-runtime-r5-host-capability-inventory.md) remain planning/advisory/handoff surfaces at their accepted scopes. Their existence supplies neither a qualified remote execution unit nor an actual money cap. A0–A6 and all frozen implementation/protocol surfaces remain unchanged.

## 3. Classification and stage rules

**REQUIRED FOR HOST CANDIDACY (C):** a supported interface/mechanism and a finite evidence path must be documented for the proposed bounded operation. A mandatory absent mechanism, documented contradiction, or unknown that prevents a safe first experiment blocks that mode. Documentation establishes feasibility only, never actual enforcement.

**REQUIRED ONLY DURING FORMAL QUALIFICATION (Q):** current account/configuration, actual applied behavior, independently bound observations, failure tests and reconciliation must be proven at their applicable gate. Their absence in public documentation is not itself an automatic provider rejection if C is satisfied. Pre-creation Q facts must be resolved before creation, and release facts before untrusted execution; neither may be deferred until after their effect.

**FUTURE HARDENING / NOT REQUIRED FOR G2 (H):** extra assurance not implied by the accepted bounded task. It cannot be silently promoted to C or used to rescue a missing C/Q property. Nonapplicable controls require a closed operation-graph justification, not an omitted field.

| Stage | Boundary |
| --- | --- |
| Documentation evaluation | Public official documentation only; no login, keys, API requests to execution endpoints, charges or SDK installation. |
| Future pre-creation review | Separate owner authority; accepted controller custody/evidence and route-specific protocol; fresh identity/account/actor/resource/exposure prerequisites. No creation until every mandatory pre-creation fact passes. |
| Future trusted setup | Separately authorized exact configuration, at most one creation attempt, synthetic bounded observations and cleanup; ambiguous create is reconciled without replacement. No untrusted release follows automatically. |
| Formal qualification / later G2 | Equivalent HQ1–HQ5 and separately authorized HQ6 on one accepted capability; complete positive binding and separate G2 implementation authority. No ledger/runtime implementation in this evaluation. |

Public-source **DOCUMENTED YES**, **DOCUMENTED NO**, **PARTIAL**, and **UNKNOWN** describe documented interface coverage, not account observations or runtime PASS. PARTIAL identifies positive coverage and exact missing facts. UNKNOWN means no sufficient support/absence conclusion in the bounded checked sources; it never means harmless or unsupported everywhere.

## 4. Minimum P1–P12 contract and traceability

Each P row's interface obligation is C. Its measured/account-specific counterpart is Q and is separately specified below. This avoids calling an unrun test a documentation defect or treating a documented parameter as qualified enforcement.

| ID | Classification | Minimum candidacy interface fact | Formal-qualification evidence (Q) | Accepted mapping |
| --- | --- | --- | --- | --- |
| P1 Deployment / instance identity | REQUIRED FOR HOST CANDIDACY | Identify supported execution mode/API/runtime revision, resolved workload/image identity, stable instance and operation references, and observation coverage. There must be a way to correlate one admitted operation with its results. | Bind the actual instance/execution and Nexus-controlled admitted code/dependency basis to independently observed identities; close relevant substitution gaps. A tag, prelaunch hash or guest statement alone is insufficient. | A1/A2, R/G1, HQ1/HQ5/HQ6, D §4. |
| P2 Control/data-plane separation | REQUIRED FOR HOST CANDIDACY | Enumerate creation, mutation, execution/file and termination authority; actors able to change controls; credential custody; available denial/attenuation mechanism. Workload must not receive authority to relax its own required restrictions. Distinct API products are not required if an equivalent supported separation exists. | Verify actual credential reachability, effective permissions, concurrent actors and inability to escalate; preserve the control boundary through indirect/background paths and reconnect. | A1–A3, HQ2/HQ3, D §§4/6B. |
| P3 Effective isolation / policy observation | REQUIRED FOR HOST CANDIDACY | Supported enforcement and subject-external evidence for every required restriction, with exact instance/configuration/freshness binding and safe release after relevant changes. Immutable controlled configuration, verifiable mutation exclusion, or supported drift-safe observation may supply the accepted property. Stored settings alone do not. | Establish applied restrictions, observation source/scope and gaps, actual negatives and a justified no-change interval/revalidation rule. Contradictory or unobservable mandatory state is STOP. | A1/A2/A6, G1, HQ2/HQ5, D §§4/6B. |
| P4 Execution input boundary | REQUIRED FOR HOST CANDIDACY | Describe command/filesystem/env/workdir/mount/IPC/process/network/service inputs and indirect execution channels; support a closed admitted input graph with no reachable control/model secrets. Network requirements are task-specific and cover IPv6/DNS/metadata/side services where reachable. | Observe effective allowed values/paths/handles or descriptors and actual input/secret/escape negatives from a trusted source; classify guest reports separately. Broad Internet capability is not an exact-host allowlist. | A2/A3, G1 complete path, HQ2/HQ3/HQ6, D §4. |
| P5 Resource limits | REQUIRED FOR HOST CANDIDACY | Support non-workload-relaxable bounds for the task's CPU, memory, wall/lifetime, storage, process/concurrency and output/log exposure. State enforcing layer and scope. A client timeout, advertised allocation or maximum plan entitlement alone is not an operation limit. | Bind actual limits and whole-unit descendants, fixed data/output bounds, deadline and controller-loss consequences. Show accepted application/Host combination where native controls alone are incomplete. Sequential Nexus dispatch does not authorize parallel background effects. | A2, R/G1, HQ4/HQ6, D §§4–6. |
| P6 Hard cost boundary | REQUIRED FOR HOST CANDIDACY | Identify every applicable billable dimension and a supported hard bound: an enforced money ceiling or enforced finite resource/lifetime/effect bounds with a verified conservative all-in maximum charge. Prevent unapproved extension, automatic recreation/retry and residual billable objects. | Verify current account/plan/rates/minimums/credits/payment/automatic billing, all-inclusive worst case and remaining owner headroom before creation. Bound ambiguous create/cancel, retention, egress, model/tool calls where applicable. Retain late/revised usage as unresolved until reconciled. | A1/A2, R/G1 cost distinction, HQ6, D §§5/6B. |
| P7 Cancellation | REQUIRED FOR HOST CANDIDACY | Supported exact-unit cancellation/termination, queryable outcome and an independently enforceable lifetime/failure bound covering descendants/background work. Document what request/acknowledgement means and loss-of-controller behavior. | Show stop-new-dispatch versus request/ack versus actual terminal/zero-live state. Lost ack retains ambiguity; reconcile exact original unit/effects/cost and do not blindly recreate. Local death is not remote cancellation. | A2/A6, R, HQ4/HQ6, D §§2/4/6B. |
| P8 Observation | REQUIRED FOR HOST CANDIDACY | Stable operation/unit references and supported status, result/failure and task-relevant effect observation. Explain retention/expiry, which records survive interruption and whether background work is observable. A persistent universal transcript is not required. | Authenticate observation source, exact admitted operation and terminal/error facts; independently validate artifacts/effects and record uncovered channels. An exit code alone is not task acceptance. | A2, R/G1, HQ5/HQ6, D §4. |
| P9 Interruption / unknown effects | REQUIRED FOR HOST CANDIDACY | Supported reconnect/query or equivalent preserved observations can distinguish observed operation states and reconcile potentially completed effects without an unsafe blind retry. Missing/lost identity or expired results must have an explicit UNKNOWN/stop path. | Inject lost create/dispatch/result/cancel/controller responses; preserve original references/exposure, query effect/artifact state and authorize any retry anew. NOT STARTED needs positive evidence or a supported no-effect guarantee. | A2/A6, R recovery/tests, HQ4–HQ6, D §§2/4/6B. |
| P10 Evidence integrity | REQUIRED FOR HOST CANDIDACY | Identify provider, trusted-controller/OS and workload observation sources; bind records to account/unit/operation/config/time and protect the Nexus receipt path against untrusted modification/replay. An independently qualified controller mechanism is a composition prerequisite. | Fresh protected receipts, issuer/source/scope, exact binding, ordered gaps, authenticity and cross-checks; stale/forged/partial/contradictory evidence STOP. Provider telemetry is external to the guest, not independent certification of the provider itself. | A1/A2, R/G1, HQ1/HQ5, D §4. |
| P11 BYOK / credential model | REQUIRED FOR HOST CANDIDACY | Owner-controlled account/credential/quota/billing where the service requires them, no bundled Nexus developer key, credentials outside untrusted inputs; identify revocation/rotation and its effect on active authority. Compute key and optional model BYOK key are distinct. No model call is required for a deterministic local capability. | Current effective custody, safe status-only account binding and revoked/changed authority handling; never retain key/token values or hashes in evidence. Rotation/revocation must invalidate affected grants/evidence; it is not assumed to cancel running compute. | A1/A3/A6, R/G1, HQ2/HQ3/HQ5, D §§4/5. |
| P12 Version / capability drift | REQUIRED FOR HOST CANDIDACY | Supported identity/version/configuration sources and a bounded revalidation/invalidation strategy for material runtime/API/policy/capability changes. No universal provider push-notification feed is required. | Bind qualification scope/expiry; changed dependencies/configuration, authorities, missing observation or incompatible release invalidates the affected binding and stops dispatch pending review. | A1/A2/A6, G1, HQ1/HQ5/HQ6, D §§4/7. |

All measured Q entries above are **REQUIRED ONLY DURING FORMAL QUALIFICATION**, at the applicable pre-creation/pre-release gate. None is fulfilled by this document. Current hosted deployment and current account state remain UNKNOWN in this documentation-only task.

## 5. Avoiding extra requirements and false substitutes

**FUTURE HARDENING / NOT REQUIRED FOR G2:** universal exactly-once remote effects; VM/process snapshots; total transcripts; cryptographic hardware attestation or signed policy receipts as the only proof model; proof against a malicious provider/kernel/fully trusted owner; enumeration of all enterprise policy internals; a universal identity/billing platform; all-provider feature coverage; mandatory general delegation; mandatory provider/model choice. None may erase an actual accepted threat, required provenance or unknown effect. A supported equivalent evidence mechanism still needs review and testing.

A dedicated currency cap API is not universally mandatory if a qualified hard resource/exposure composition proves the same ceiling. Conversely an estimate, credit balance, budget alert, plan maximum, local reservation or after-the-fact invoice does not supply that composition. Failed/ambiguous calls and effects outside the execution process still consume exposure. Price estimates are not hard bounds.

Native idempotency keys are useful but not universally required: a finite operation can instead use positive effect-query/no-effect proof and refuse retry while UNKNOWN. Likewise a policy revision API is not universally required where equivalent immutability/actor exclusion and freshness are proven. Refusal under uncertainty preserves safety; it does not satisfy the later useful-workflow acceptance requirement by itself.

## 6. Bounded evaluation and experiment eligibility

The fixed documentation set is E2B hosted Sandboxes, Modal Sandboxes and Daytona hosted Sandboxes, because these concrete interfaces already appear in preserved Nexus evidence. No fourth provider, product survey, account access or support contact is needed. Current official documentation is the evidence basis; dated provider replies/source-main analysis identify questions only and cannot certify today's deployed behavior.

For each provider the [fact matrix](nexus-g2-route-b-provider-documentation-fact-matrix-v1.md) assesses every C row, separating its documented positive scope from missing facts. **SUFFICIENT FOR A BOUNDED EXPERIMENT** requires a concrete finite evidence plan for all mandatory pre-experiment controls; it is not provider selection or qualification. **INSUFFICIENT** records a blocking documented limitation or missing mandatory mechanism in this evaluated mode/contract. **UNKNOWN** records insufficient authoritative basis to decide such a prerequisite. Unknown Q behavior alone is expected before a future experiment and is not automatic rejection.

Any proposed experiment still requires separate accepted route-specific protocol, controller custody/evidence, owner account/cost authority and exact subject/input/bounds. The exited Windows controller/LPAC path is not such a control-plane proof. Replacing its ownership, bootstrap or system-TCB promises requires a separately accepted successor; moving the guest remotely does not silently remove them. No unqualified controller, generic runtime, privileged broker, password transfer, weaker fallback or inherited E2B authorization is introduced here.

At most one original identity may be created under any future single-unit authority. On ambiguous create, stop and reconcile the original attempt using supported references; do not create a replacement. Missing required identity/isolation/permission/resource/cost/cancellation/observation proof stops the affected release. The local Scenario 01–04, HQ6 and G2 remain unrun and unauthorized.

## 7. Documentary completion and integrity

The [separate adversarial review](nexus-g2-route-b-provider-interface-adversarial-review-v1.md) must challenge marketing versus controls, workload mutation, timeout scope, background survival, hard versus estimated budget, delayed billing, duplicate effects, identity, credential reachability, drift, observation provenance and UNKNOWN handling. Corrections may refine documentary clarity without altering these accepted properties or inventing a new executor.

Only this contract, its fact matrix and review are deliverables. No acceptance record, MANIFEST integration, acceptance commit, dependency change, experiment, provider selection, merge, push, tag or freeze is authorized. A0–A6 remain unchanged; Positive Host Binding ABSENT; G2 HOLD.
