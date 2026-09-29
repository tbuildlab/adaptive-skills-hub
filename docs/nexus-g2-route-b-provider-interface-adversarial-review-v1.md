# Nexus G2 Route B Provider Interface Adversarial Review v1

Document ID: `nexus.g2.route-b.provider-interface-adversarial-review.v1`

Version: `1.0.0`

Date: 28 September 2026

Status: **PROPOSED DOCUMENTARY REVIEW — NOT ACCEPTANCE, HOST QUALIFICATION OR EXECUTION AUTHORITY**

## 1. Review result and exact subjects

**DOCUMENTARY REVIEW: ACCEPTABLE AS WRITTEN FOR OWNER REVIEW.** The finite contract is complete and the fact matrix preserves unresolved candidacy prerequisites. This is a separately performed adversarial pass by the same Codex author/agent, not an independent agent/human audit or experimental result.

| Subject | Raw UTF-8/LF bytes | SHA-256 |
| --- | --- | --- |
| [Provider-Neutral Host Contract v1](nexus-g2-route-b-provider-neutral-host-contract-v1.md) | 18,629 | `E97ECF70BFB1D0082E7DE8E7C8100E321174062E15F9C2EC62CDAC4BB97BEFE0` |
| [Provider Documentation Fact Matrix v1](nexus-g2-route-b-provider-documentation-fact-matrix-v1.md) | 25,881 | `E3FD62C26B0768E831E80D191453ADC2A02D892B31A30541F04E3FB9BD432481` |

Authority is the owner's Route B documentation-only request, attachment `281006f6-2fe2-4759-957c-27194a4f31c1`. Baseline: `nexus-v2-g2-development`, HEAD `ad9f68680ad07b34b0a614108735ccac99059340`, initially clean. These are uncommitted proposals. No acceptance record or MANIFEST addition is made.

## 2. Governing acceptance basis

Reviewed against [A0–A6](nexus-pre-g2-architecture-addendum-v1.md), [Pre-G2 acceptance](nexus-pre-g2-architecture-acceptance-v1.md), [Roadmap V2](nexus-roadmap-v2.md), [G1](nexus-v2-g1.md), [Host Scope & Exit](nexus-g2-host-qualification-scope-and-exit-decision-v1.md)/[acceptance](nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md), and [Next Host Route Decision](nexus-g2-next-host-route-decision-v1.md)/[accepted exit and direction](nexus-pre-g2-current-lpac-host-exit-and-next-route-acceptance-v1.md). Frozen [R2](nexus-runtime-r2-mcp-architecture.md), [R4](nexus-runtime-r4-host-handoff.md) and [R5](nexus-runtime-r5-host-capability-inventory.md) remain unchanged.

The matrix's official-source register is the current public interface basis. Dated E2B/Modal/Daytona feasibility records are used for questions and historical limits only. No account or deployed behavior is promoted from historical observation to current proof.

## 3. Adversarial challenge matrix

“Closed” below means the documentary inference/scope defect is prevented; it never means the runtime property passes.

| Challenge | Counterexample / unsafe inference | Review disposition and exact control |
| --- | --- | --- |
| Marketing mistaken for enforcement | An isolated-container description is taken as complete transitive default deny. | Closed in documentation: contract P2–P5/P10 and every provider gap distinguish supported parameters from independently bound applied-state proof. P3/P10 candidacy remains UNKNOWN. |
| Workload changes its own policy | A workload/client receives a broad control key or reachable policy-mutation channel. | Closed in documentation: contract P2/P4/P11 require actor and credential closure. Matrix separates E2B auth domains, Modal port tokens and Daytona organization toolbox scope. No key handoff is authorized. |
| Resource request mistaken for maximum | Reservation, plan entitlement or concurrency quota becomes an operation cap. | Closed in documentation: contract P5 requires enforcing-layer scope; matrix identifies actual hard-limit options versus allocations/shared quotas. Complete bounds remain Q/unresolved C where applicable. |
| Client timeout mistaken for remote lifetime | Local wait expires but remote work persists; idle timeout resets on activity. | Closed in documentation: P5/P7 distinguish maximum lifetime, idle timeout and caller wait. No local timeout is a cancellation receipt or hard charge proof. |
| Background work survives cancellation | Main process exits, a session is deleted or client detaches while another effect continues. | Closed in documentation: P7/P8 require whole admitted unit/effect observation. Each provider's full-tree/failure behavior remains unqualified. |
| Estimated budget masquerades as hard budget | Balance, alert or planned price calculation is used to approve create. | Closed in documentation: P6 permits only verified hard money or all-in hard resource/exposure composition. Matrix credits Modal's documented Workspace hard-cap mechanism without claiming an actual Nexus-bound cap. |
| Delayed billing exceeds authority | Transitions, retained objects, revised usage or shared-account spend consume remaining headroom. | Closed in documentation: P6/P9 and provider cost gaps preserve outstanding exposure. No zero-charge, settled-cost or current-account claim is made. |
| Lost response duplicates effects | Retrying create/exec produces a second live unit or duplicate completed artifact. | Closed in documentation: P9 requires preserved original references, positive effect/no-effect evidence or UNKNOWN/stop. No replacement is created; exactly-once API support is not invented as a universal requirement. |
| Identity insufficient for reconciliation | Reused name/PID, inaccessible ID or missing terminal stream is interpreted as NOT STARTED. | Closed in documentation: P1/P8/P9 bind unit and operation separately. Matrix identifies running lookup and retention gaps; absence is not proof of no effect. |
| Credentials accessible through indirect input | Secret mounts, identity variables, filesystem writes or provider side services expose control/model authority. | Closed in documentation: P4/P11 cover transitive inputs and distinguish compute from optional model keys. No secret retrieval is proposed even as a negative test. |
| Key deletion assumed to stop existing work | A deleted credential is treated as revoking all live data tokens or killing compute. | Corrected in the matrix: all P11 compound rows are PARTIAL; active-authority consequences are unresolved despite documented owner-account/key facilities. Contract requires separate revalidation/cancellation. |
| Provider drift silently preserves binding | `latest`, a documentation version marker or source-main commit is treated as deployed identity. | Closed in documentation: P1/P12 and source register preserve actual deployment UNKNOWN; material changes invalidate affected proof. A mandatory push-change API is not added. |
| Provider telemetry called independent certification | Guest logs or control-side settings establish all applied-policy and trusted-controller claims. | Closed in documentation: P10 separates sources and their trust scope. Provider records are external to the guest, not independent audit of the provider. Workload self-report cannot establish mandatory PASS. |
| UNKNOWN converted to PASS | Partial documentation or an unrun test becomes sufficient candidacy or permission to run. | Closed in documentation: all three candidacy dispositions remain UNKNOWN and no experiment is declared justified. Doc completeness is not complete positive Host binding. |
| Assurance requirements expand without accepted basis | Require recursive system TCB proof, hardware attestation, universal policy receipts, full transcripts or VM snapshots. | Closed in documentation: contract §5 lists H exclusions and permits accepted equivalent mechanisms. Mandatory property traceability remains A1/A2/A3/A6, G1/R/HQ/D, not vendor preference. |
| Unrun formal tests automatically reject providers | Lack of measured account/isolation/failure behavior is treated as provider-wide DOCUMENTED NO. | Closed in documentation: C/Q are distinct; dispositions rely on missing pre-experiment proof paths. Unmeasured Q alone is not rejection. Explicit NO subclaims are narrow and affirmatively sourced. |
| Controller qualification silently waived | A remote guest is used to bypass the exited Windows controller custody/evidence promise. | Closed in documentation: contract §6 and matrix §§1/7 retain the common prerequisite and separate successor governance; no generic broker/runtime or unaccepted trusted bootstrap appears. |
| Research reopens an indefinite rescue loop | More providers, new infrastructure, account login or support engineering is implied by a gap. | Closed in documentation: fixed three-provider scope, finite sources and stop boundary. Any later single-mode clarification/protocol requires new owner authority; no automatic continuation. |

## 4. Bounded correction and fresh re-review

The draft matrix initially labelled P11 DOCUMENTED YES at the compound level for all three providers. That overstated full coverage: owner-account/authentication facilities do not establish revocation/rotation consequences for already-active authority. The bounded correction changes only those three rows to PARTIAL, retaining the affirmative subfacts and specifying the remaining uncertainty. No accepted invariant, provider-neutral contract, runtime or historical evidence was changed.

Fresh re-review of the corrected pair found no remaining documentary contradiction requiring an edit. The contract remains byte-identical to its pre-browsing basis. The corrected matrix hash above is the review subject; its earlier draft hash is not an accepted or final binding.

Additional checks: no provider rank/winner; no assumed current account/key/credit state; no exact-host inference from broad networking; no silent resumption/timeout extension; no current deployment inference from SDK/documentation version; no cost authority inherited from old RM5/$1 observations; no resurrection of LPAC, NexusTest or Option A. No extra stronger property is required merely because a vendor lacks a familiar Windows API.

## 5. Stable result and residual UNKNOWNs

**ROUTE B INTERFACE CONTRACT: COMPLETE.** **CANDIDACY DOCUMENTATION: UNKNOWN** for E2B, Modal and Daytona, in their declared interface modes. These outcomes are not a preference ordering.

The following remain unresolved, without runtime testing:

- A supported subject-external effective-policy/freshness/actor-exclusion evidence path covering the required input graph.
- The common qualified trusted-controller custody/receipt boundary and exact route successor protocol.
- Complete hard maximum operation exposure, current account/actors/rates/headroom and delayed/revised accounting.
- Actual deployment/image/dependency/input identities and effective credential/resource restrictions.
- Whole-unit/background cancellation, bounded controller-loss behavior, interrupted-operation/effect query and observation retention.
- Revocation/rotation consequences and material runtime/capability-change detection.

Some are measured Q facts for a later qualified experiment; the first three include presently unresolved safe-candidacy/pre-creation prerequisites. No unknown is harmless by default, and no formal experiment is used to discover an unsafe billable boundary after creation.

No current provider has earned a smallest executable experiment proposal. Matrix §7 defines the finite missing-source decision and conditional future outline only. Next owner review can consider these three documents and whether to authorize one exact clarification/successor task. Acceptance would still not supply a key, account access, charge authority, untrusted release, HQ6 or G2 implementation permission.

## 6. Verification boundary and preserved state

Final checks must verify subject byte/hash bindings, UTF-8/LF/no BOM, references, P1–P12 coverage and classification, bounded secret-pattern scan, exact three-document change scope, current branch/HEAD and unchanged tracked repository. Existing source MANIFEST entries can be read-verified; the three proposals are intentionally not added to MANIFEST before owner acceptance.

Protected anchors: source MANIFEST SHA-256 `AB3A28E560AFAB5D7A9CBB7FE579FEB6C8C0CD91D51ADA7CE4F8224BD1C00FD1`; accepted A0–A6 addendum SHA-256 `B6680C710DDA8FB7808E06CC2569FD1BB6A4AEED47B2223F9626E411E298BE14`; sealed V4 manifest SHA-256 `2B907CD25868124C244E6C350EA13CFFCC041562EA0E9AD479197F6B83D3D3C4`. These are documentary integrity anchors, not experimental PASS evidence. No full runtime regression or qualification binary is needed for these documentation-only changes.

**No acceptance record/commit, MANIFEST update, dependency or security change, provider contact beyond public documentation retrieval, credential use, account access, charge, execution, merge, push, tag or freeze.** Current LPAC binding remains exited for insufficient evidence, not insecure. Option D current; Option A HOLD; Scenario 01–04 NOT RUN; HQ1–HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD. A0–A6 and frozen G1/R2/R4/R5 remain unchanged.
