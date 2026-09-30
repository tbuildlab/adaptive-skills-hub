# Nexus G2 Limited Clarifying Amendment v1

Document ID: `nexus.g2.limited-clarifying-amendment.v1`

Version: `1.0.0`

Date: 30 September 2026

Status: **PROPOSED NORMATIVE CLARIFICATION — OWNER ACCEPTANCE PENDING; NO IMPLEMENTATION OR EXPERIMENT AUTHORITY; G2 HOLD**

## 1. Authority, baseline and proposed effect

The owner authorized four additive draft documents under the accepted [OpenAI-first compatibility acceptance](nexus-g2-openai-first-compatibility-rebaseline-acceptance-v1.md), conclusion **C. ONLY LIMITED CLARIFYING AMENDMENTS ARE JUSTIFIED**. Baseline: branch `nexus-v2-g2-development`, commit `d1de2461ccbcce5b81552c0acc8971f63e0f3ccf`, clean working tree. The unchanged source MANIFEST contains 192 entries, verifies 192/192 against canonical Git blobs and has SHA-256 `B1AD560835A97DE7A34862DAC320129797348069EDFB8D2F92FFA37B483D8D5E`. Windows checkout CRLF and canonical source LF are distinct byte measurements; no accepted source is rewritten.

This proposal is not effective until explicit owner acceptance binds its exact reviewed bytes and named interpretation scope. Proposed normative provisions are §§3–8 and the companion [P1–P12 mapping](nexus-g2-limited-clarifying-amendment-p1-p12-mapping-v1.md). §§2 and 9 are **NON-NORMATIVE RATIONALE / CHANGE TRACEABILITY**. The [OpenAI impact analysis](nexus-g2-limited-clarifying-amendment-openai-impact-v1.md) applies the proposal without adding or upgrading evidence. The [separate adversarial review](nexus-g2-limited-clarifying-amendment-adversarial-review-v1.md) binds these three subjects.

Acceptance would clarify a provider-neutral contract interpretation; it would not pass any property, select a Host, approve a controller, issue a grant, authorize an experiment or authorize G2 implementation. No prior G0/G1, LPAC, provider or implementation authorization transfers.

## 2. NON-NORMATIVE RATIONALE — minimum amendment surface

The [Pre-G2 addendum](nexus-pre-g2-architecture-addendum-v1.md) A2 already permits application/tool controls, qualified Host controls over the complete unit, or a demonstrated combination. Its requirements are non-bypassable admission before effects, qualified hard exposure bounds and reconciliation before unsafe retry. A1–A6 do not require every proof component to originate at the provider.

| Kind | Exact accepted statement / section | Preserved property; proposed clarification |
| --- | --- | --- |
| Actual safety requirement | Pre-G2 A1/A2/A6; [G1 evidence/conformance boundary](nexus-v2-g1.md); [HQ Scope & Exit](nexus-g2-host-qualification-scope-and-exit-decision-v1.md) §§2–3 | Keep complete-boundary enforcement, fresh source-bound evidence, finite exposure, equivalent HQ1–HQ5 and separate HQ6. No A0–A6 amendment is proposed. |
| Evidence mechanism | [Route B contract](nexus-g2-route-b-provider-neutral-host-contract-v1.md) §4 P1/P3/P9/P10/P12 | Identity, applied restrictions, safe retry, custody and drift remain mandatory. Internal managed-service bytes/revisions, a monolithic receipt, native idempotency and push feeds are not universal mechanisms. Relevant Nexus-controlled executable dependencies still require their applicable provenance proof. |
| Provider-specific assumption | Same contract §4 opening: each row's interface obligation is C; §6 finite evidence plan | Interpret interface obligations component by component, including controller and experimental components. Do not require every final component to have provider-only closure before a safe experiment. Mandatory provider hard semantics remain advance gates. |
| Later Route B interpretation | [UNKNOWN Resolution Matrix](nexus-g2-route-b-unknown-resolution-matrix-v1.md) §5: coherent authoritative bundle covering eleven C rows before resource creation | Replace this blanket reading prospectively with §7's experiment safety gate. Preserve all three historical classifications, counts and conclusions. |
| Later evidence workflow | [Authoritative acquisition](nexus-g2-route-b-authoritative-evidence-acquisition-v1.md) §§10–11 and [OpenAI evaluation](nexus-g2-route-b-openai-hosted-authoritative-evaluation-v1.md) §5 opening and §10 final advance rule | Their historical missing facts and no-experiment conclusions remain true. Future eligibility uses allocated safety prerequisites; documentation counts are not runtime scores and cannot automatically change. |
| Historical Windows/LPAC mechanism | Accepted local delivery, owner release, observation, watchdog and CI successors; HQ Scope & Exit §§4–9 | Same-process local loaded-byte evidence, fixed environment, handles, Job and CI gates remain exact local rules. They are not imported as universal remote API requirements. The closed Windows binding stays closed. |
| Controlling clarification direction | [Responsibility Re-baseline](nexus-g2-responsibility-rebaseline-review-v1.md) §§2–5 and [accepted compatibility review](nexus-g2-openai-first-compatibility-rebaseline-review-v1.md) §§2–9 | Preserve HQ1–HQ4 delegable subject to Nexus verification, HQ5–HQ6 Nexus-owned, and component-level composition. This is a limited clarification, not wholesale re-baselining. |

Historical documents are evaluated at their original date, scope and rules. They must not be rewritten to imply this prospective interpretation was already applied or that past unknowns passed.

## 3. NORMATIVE CLARIFICATION — complete safety composition

G2 qualification MUST evaluate the complete trusted execution composition for an exact admitted capability, mode, operation graph, configuration, controller and evidence scope. A candidate's provider brand, managed status or low advertised price is not eligibility. A positive complete Host binding requires equivalent HQ1–HQ5 plus the separate HQ6 capability primitives; the useful G2 workflow, runtime, fault-injection and regression acceptance remain later requirements.

Responsibility and evidence classes apply to **components**, not exclusive labels for compound P-properties:

| Class | Meaning and admissible proof | Boundary |
| --- | --- | --- |
| `PROVIDER-MANDATORY` | Supported authoritative semantics for enforcement/identity/observations controlled by the remote provider, subsequently bound to the actual qualified account/unit/configuration. | A promise without precise scope, request parameter, prompt, local timeout, observation after the effect or accounting entry cannot substitute for hard remote enforcement. Provider telemetry is external to the workload; it is not independent certification against a malicious provider. |
| `NEXUS-OWNED` | Reviewed trusted-controller/application enforcement and protected records for grants, admission, dispatch count, custody, reservation, validation, UNKNOWN persistence and invalidation. | Records prove only facts within the controller's authority and observation coverage. The route-specific controller and custody boundary must themselves be demonstrably suitable; the exited LPAC controller supplies no inherited positive proof. |
| `COMPOSITE` | An explicit conjunction of provider, Nexus and other accepted application components, each with an enforcing layer, source, scope and binding. | Every necessary component must pass. Missing components cannot be averaged, renamed or compensated by stronger unrelated controls. |
| `QUALIFICATION-EXPERIMENT` | Separately authorized, bounded, source-external negatives/faults and observed exact-mode behavior; a test plan predeclares coverage, bounds and PASS/FAIL/STOP. | Finite tests establish only the tested scope. They cannot invent universal semantics, exhaustive pricing, hard remote lifetime or undocumented future behavior. |

A profile MUST enumerate required component classes, enforcement layer, admitted subject/inputs, dependencies, evidence source/scope/freshness, safe observation/release interval and failure consequence. No component may silently migrate classes. A proposed equivalent requires a named threat-preserving evidence path, separate review and acceptance before use; changing a provider-dependent hard property into a controller rule is not equivalence.

Controller-side evidence and conservative refusal are valid mechanisms only for the properties they actually enforce. Retry refusal can preserve safety with unresolved effects when the original exposure is already hard-bounded. It cannot end remote work, settle a bill or satisfy a useful-success criterion by refusal alone.

## 4. NORMATIVE CLARIFICATION — non-negotiable safety core

1. Independently issued, then-valid authority, capability/policy eligibility, admission and conservative reservation MUST precede every side effect, including resource creation, upload, dispatch, resume and cleanup actions requiring authority.
2. Workload code, model output and transitive/deferred paths MUST NOT expand required authority, restrictions, resources, delegation or parallelism.
3. Controller/API credentials MUST remain outside workload inputs, environment, files, capabilities and evidence; applicable model/third-party secrets must remain unreachable by the untrusted subject.
4. Every reachable safety-relevant resource/lifetime/descendant exposure MUST have a finite, enforceable, non-workload-relaxable bound with a known enforcing layer and controller-loss consequence.
5. Every applicable billable dimension MUST yield a conservative finite all-in maximum before dispatch, within the remaining owner ceiling. Unknown money is not zero; new/unbounded dimensions invalidate admission.
6. Stop-new-dispatch, cancel request, acknowledgement, terminal cessation, physical cleanup, effect reconciliation and billing settlement MUST remain distinct. Local termination, stream closure or API deletion proves none of the other states by itself.
7. UNKNOWN MUST persist with the original identity, unresolved effects and reserved exposure until positive reconciliation. Missing observations, expiry or deletion cannot erase it.
8. Ambiguous operations MUST NOT be retried, replaced or recreated merely for availability. Any later authorized retry requires reconciled effects/no-effect proof, renewed admission and budget, and bounded replay semantics.
9. Qualification MUST NOT rely solely on guest/model self-report. Decisive observations require trustworthy subject-external sources and protected custody; child data may corroborate only within validated coverage.
10. Qualification MUST bind sufficiently stable public execution/configuration identity, admitted input basis, original operation and source/time/coverage, with explicit expiry and revalidation. An API version alone is insufficient.
11. Material security-relevant observable drift, incompatible/unsupported contract change, evidence expiry, relevant authority/configuration change, contradiction or missing mandatory observation MUST invalidate the affected binding before further dispatch/resume. Hidden internal changes remain explicit provider trust residuals, not proven absence of drift.
12. Default deny applies to authority, channels, retries, optional tools, transitive operations, fallback, delegation and concurrency. Nonapplicability requires a justified closed operation graph.
13. Qualification does not grant task authority. Architecture acceptance, experimental authorization, measured qualification, complete positive Host binding and G2 acceptance MUST remain distinct gates.

Any amendment, adapter or qualification protocol that weakens one of these rules MUST fail review.

## 5. NORMATIVE CLARIFICATION — P1–P12 and evidence custody

P1–P12 retain their identifiers, names, threats and required end-to-end outcomes. The companion mapping is the normative component allocation: minimum property, permitted classes, Nexus/provider/test obligations, false substitutes, PASS, FAIL/UNKNOWN and requalification triggers. It does not supply current evidence or authorize a controller design.

Provider internal implementation-byte identity is mandatory only where the exact safety property cannot otherwise be established within an explicitly accepted managed-service TCB/public contract. This rule does not relax actual-loaded identity for Nexus-controlled code or dependencies affecting its trusted boundary, nor supersede a literal existing local protocol. A protected request hash proves admitted bytes, not actual remote execution. Public unit/operation/result association must still rule out relevant substitution.

A protected evidence bundle MAY compose provider API observations, authenticated events/webhooks where used, controller admission/input records, independent effect validation and qualification records. Each decisive fact MUST record source and authenticity basis, actor/account/unit/operation, configuration/input basis, capture/order/time, coverage, omissions and contradictions. No monolithic provider receipt is universally required. A host cannot author its own Nexus grant; the untrusted subject cannot author or replace decisive evidence. Unsigned authenticated API evidence need not be rejected merely for lacking a signature, but its actual source/custody and trust assumptions must be verified. Guest-produced artifacts establish task data only after validation; they do not self-certify isolation or control state.

## 6. NORMATIVE CLARIFICATION — HostAdapter architecture boundary only

```text
G2 Safety Contract
        |
HostAdapter (provider-neutral boundary)
        |
Provider-specific adapter
        |
Provider execution system
```

The current intended primary implementation candidate is `OpenAIHostAdapter -> OpenAI Agents API / managed harness / openai_hosted`. This is direction only; OpenAI is not selected or qualified. Future adapters are possible, not current implementation requirements. OpenAI session/environment/turn/item/artifact names remain adapter-specific.

The minimum conceptual surface is: admitted execution-unit reference; original operation reference; admitted configuration/limits/input description; execution submission; status/result/effect observation; native cancellation; cleanup/lifecycle observation; evidence source/scope/coverage; and exact provider-specific qualification binding/expiry. Unsupported facts and operations MUST be explicit and fail eligibility where mandatory. Creation and submission are themselves governed effects, not convenience side effects hidden in lookup.

Nexus owns independent grant validation, sequential admission, reservations, ordered domain facts, checkpoints/recovery decisions, unresolved exposure, acceptance and invalidation. The adapter translates approved operations and observations; the provider owns its mature loop and native execution/lifecycle. Native continuation does not restore grants, trust seals or settled cost. The adapter MUST NOT add arbitrary command/broker authority, a generic agent loop, scheduler, sandbox, credential platform or simulated remote hard guarantee. No interface or runtime implementation is authorized here.

## 7. NORMATIVE CLARIFICATION — experiment safety gate

A separately authorized bounded qualification experiment MAY be proposed only when all of the following are established **before its first side effect**:

1. All provider-mandatory facts needed to bound the experiment have sufficiently authoritative, supported, exact-mode semantics: isolation/authority and relevant channel restrictions; whole-unit resource/active-lifetime/controller-loss and ultimate termination; every applicable billing driver/cutoff/overshoot/tail; and identity/observations needed for safe conduct and reconciliation. An unresolved hard provider boundary is STOP.
2. Every required pre-dispatch Nexus protection is available and separately reviewed/verified for the actual route: valid finite authority, admitted inputs/configuration, protected controller/credentials/evidence, sequential one-original-attempt admission, conservative reservation, stop/retry rules and qualification invalidation. A paper plan alone does not satisfy these prerequisites.
3. Composite components have enough supported provider semantics and a meaningful externally observed experiment to resolve the remaining **measured** uncertainty. Define each unknown, observable test, safe barrier and falsifier in advance. Never defer an authority or exposure premise until after its effect.
4. All experiment resources, effects and total cumulative financial exposure are finitely bounded, including failed/ambiguous create, retries internal to the provider, controller loss, residual objects, cleanup and delayed charges. External effects are absent or independently admitted, bounded and reconcilable; irreversible/unreconcilable effects cannot be introduced to discover their behavior.
5. Failure stops new dispatch, requests native cancellation where applicable, invokes the independent hard fallback, preserves references/UNKNOWN/exposure and performs bounded authorized cleanup/reconciliation. No automatic replacement, weaker fallback or new unit is allowed.
6. A predeclared protocol, exact profile, test-authority boundary and owner authorization exist. Safe readiness is not execution permission. Production/final-property qualification may remain incomplete; every safety premise needed to conduct this experiment must already hold.

An experiment MUST NOT discover whether an otherwise unbounded experiment is safe. Sampling cancellation does not provide its own hard fallback; sampling charges cannot establish all-in maximum; sampling network denies cannot establish universal egress scope. Full production observation/retention, exact cancellation latency and failure coverage may be measured later only under the already safe envelope. A baseline absent mechanism or contradiction is not reclassified as an experimental unknown merely to permit creation.

Use separate states for documented semantics, pre-experiment safety readiness, experiment authorization, measured property PASS, final complete binding and G2 acceptance. `UNKNOWN / NOT PASS / fail closed` remains literal until the relevant component has evidence. The revised gate has no current eligible provider as a consequence of this document alone.

The protocol MUST assign gates to effects in order. Before creation, establish creation authority, the exact admitted blueprint, controller custody, supported hard semantics, conservative cumulative maximum and ambiguity/no-replacement plan; an instance ID that does not yet exist is not a creation prerequisite. After the single authorized creation, bind the returned actual unit, applied configuration and trustworthy observations before any release/test whose safety depends on those facts. No later trusted-setup observation may excuse unsafe creation, and no qualification-negative test may excuse a missing release-safety premise. This staging permits measured qualification without requiring final runtime PASS before resource existence.

The exposure proof MUST enumerate all billable drivers and use their hard maximum quantities and conservatively bound rates/minimum increments, plus every failure, retained-object, overshoot and cleanup/tail term. Unsupported pricing or an infinite/unknown quantity leaves the total UNKNOWN. Test grants and reservations apply to the cumulative experiment, not just the happy-path turn. A finite accrual bound does not imply billing settlement, and a financial-only cutoff does not replace resource/effect containment.

## 8. NORMATIVE CLARIFICATION — compatibility, invalidation and limits

A0–A6, frozen Roadmap/G1/R2/R4/R5, HQ1–HQ6 threats/outcomes, the closed Windows 26200.9550 binding, sealed V4 and historical evidence remain unchanged. Option D remains current; the separate-account Option A remains HOLD. No password transfer, privileged broker, generic runtime, Windows security change or LPAC reopening follows.

E2B/Modal/Daytona retain their accepted UNKNOWN/INCOMPLETE conclusions and evidence counts; no route is reopened. OpenAI remains **SUPPORTED 0 / PARTIAL 11**, P7 **EXPERIMENT-RESOLVABLE / NOT PASS**. The six questions stay proposed and unsent. A future fresh evaluation under an accepted amendment must distinguish a changed interpretation from new factual evidence; it must not silently alter historical classifications.

Scenario 01–04 = **NOT RUN**; HQ1–HQ5 = **NOT PASS**; HQ6 = **NOT STARTED**; Positive Host Binding = **ABSENT**; G2 = **HOLD**. Draft acceptance does not authorize HQ6, provider creation, credentials, outreach, costs, HostAdapter, OpenAIHostAdapter or G2 Runtime. MANIFEST stays 192 entries; no commit/merge/push/tag/freeze in this phase.

## 9. NON-NORMATIVE RATIONALE — future integration and finite next step

The minimum future normative change is one owner acceptance record binding this amendment, mapping, impact and review and explicitly naming the prospective interpretation overlay below. Existing accepted history remains byte-identical. No mandatory successor version of A0–A6, Roadmap, G1, HQ outcomes or LPAC protocols is justified.

| Accepted document requiring prospective amendment or cross-reference | Exact scope if this package is accepted |
| --- | --- |
| [Route B Provider-Neutral Host Contract v1](nexus-g2-route-b-provider-neutral-host-contract-v1.md) §§3–4/6 | Normative additive overlay: retain C/Q/H and P1–P12; apply component classes and §7 rather than provider-only closure of all final components. The overlay covers P1/P3/P9/P10/P11/P12 optional mechanisms and keeps P5/P6 hard premises. |
| [Responsibility Re-baseline review](nexus-g2-responsibility-rebaseline-review-v1.md) §§3–5 and [acceptance](nexus-g2-responsibility-rebaseline-acceptance-v1.md) | Additive cross-reference in the new acceptance/interpretation index; retain conclusion A, delegable HQ1–HQ4, Nexus-owned HQ5–HQ6 and P allocation. Do not amend its historical no-change conclusion. |
| [UNKNOWN Resolution Matrix](nexus-g2-route-b-unknown-resolution-matrix-v1.md) §5 and [acceptance](nexus-g2-route-b-unknown-resolution-acceptance-v1.md) | Prospectively qualify the eleven-row authoritative-bundle advance reading through §7. Historical A/B/C/D classifications and no-experiment finding remain. |
| [Authoritative acquisition](nexus-g2-route-b-authoritative-evidence-acquisition-v1.md) §§10–11 and [acceptance](nexus-g2-route-b-authoritative-evidence-acceptance-v1.md) | Cross-reference future gate interpretation; preserve exact dated evidence, provider counts, unresolved facts and no experiment authority. |
| [OpenAI evaluation](nexus-g2-route-b-openai-hosted-authoritative-evaluation-v1.md) §§5/10; [review](nexus-g2-route-b-openai-hosted-adversarial-review-v1.md); [24-question pack](nexus-g2-route-b-openai-hosted-support-question-pack-v1.md); [acceptance](nexus-g2-route-b-openai-hosted-authoritative-evaluation-acceptance-v1.md) | Prospective gate overlay, not evidence upgrade. If outreach is later authorized, version its derivative questions separately; the 24-question historical artifact remains unsent and unchanged. |
| [Compatibility review](nexus-g2-openai-first-compatibility-rebaseline-review-v1.md); [minimization matrix](nexus-g2-openai-first-contract-minimization-matrix-v1.md); [review](nexus-g2-openai-first-compatibility-adversarial-review-v1.md); [six-question pack](nexus-g2-openai-first-proposed-clarification-pack-v1.md); [acceptance](nexus-g2-openai-first-compatibility-rebaseline-acceptance-v1.md) | Cross-reference completion of the proposed clarification phase. Preserve conclusion C and question dispositions; attach the §7 interpretation and explicit Q6 safety/measurement split without silently editing questions. |

The Pre-G2 addendum/acceptance and HQ Scope & Exit decision/acceptance need only source citations, not normative amendment or changed rules. Frozen R2/R4/R5 and every local LPAC amendment/protocol need no changes. The future source MANIFEST would follow existing acceptance rules only after owner acceptance; it is unchanged now.

The next action is owner review/acceptance of exact draft bytes. That action would establish the interpretation only; further controller preparation, provider clarification submission and experiment proposals require their own authority. No experiment is ready from the present evidence.


## 10. Accepted-source byte binding

This register binds canonical UTF-8/LF Git bytes at baseline `d1de2461ccbcce5b81552c0acc8971f63e0f3ccf`. Historical proposed/review headings are read through the named acceptance records, not treated as newly effective decisions. The local acceptance chain is consulted only to preserve exact local rules and the closed binding; none is imported as a universal remote proof mechanism.

| Accepted source / acceptance chain | SHA-256 |
| --- | --- |
| [nexus-pre-g2-architecture-addendum-v1.md](nexus-pre-g2-architecture-addendum-v1.md) | `B6680C710DDA8FB7808E06CC2569FD1BB6A4AEED47B2223F9626E411E298BE14` |
| [nexus-pre-g2-architecture-acceptance-v1.md](nexus-pre-g2-architecture-acceptance-v1.md) | `C8B2FE28F9E2B6250288B736B8741824CD1FC750299AADCE07AB72C9479E782B` |
| [nexus-g2-host-qualification-scope-and-exit-decision-v1.md](nexus-g2-host-qualification-scope-and-exit-decision-v1.md) | `6CF3AB004B66580531185E7E0CE7394AA349ECB3E1E3905F224ED0259BBFCD69` |
| [nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md](nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md) | `A3B47DB405B30896A92F50B7E6EF018813980461FA3FEF315EC7AF3CF85F53F1` |
| [nexus-g2-route-b-provider-neutral-host-contract-v1.md](nexus-g2-route-b-provider-neutral-host-contract-v1.md) | `E97ECF70BFB1D0082E7DE8E7C8100E321174062E15F9C2EC62CDAC4BB97BEFE0` |
| [nexus-g2-route-b-provider-interface-acceptance-v1.md](nexus-g2-route-b-provider-interface-acceptance-v1.md) | `BA45C5223212DF59A287A51FB0966C18D6C1D7C004C6E86ACAA68D878B3936DF` |
| [nexus-g2-responsibility-rebaseline-review-v1.md](nexus-g2-responsibility-rebaseline-review-v1.md) | `8220287EDDC1DFE653394E29D53A53B7413168598336907F61493DD65E751B93` |
| [nexus-g2-responsibility-rebaseline-acceptance-v1.md](nexus-g2-responsibility-rebaseline-acceptance-v1.md) | `F2CD2FE306F065D1A97E4EDAD50098ED73EC82C5EF4E93E378511B318948A942` |
| [nexus-g2-route-b-unknown-resolution-matrix-v1.md](nexus-g2-route-b-unknown-resolution-matrix-v1.md) | `6FD8BDE5D2ACA64301D280BED050C957EC40F8C767EA41B9CF60B8877CD7197E` |
| [nexus-g2-route-b-unknown-resolution-acceptance-v1.md](nexus-g2-route-b-unknown-resolution-acceptance-v1.md) | `69CF5D6A2AA3E49C339A9BAC1981E449F27452A9A6E6A5D966BC567ABA014A61` |
| [nexus-g2-route-b-authoritative-evidence-acquisition-v1.md](nexus-g2-route-b-authoritative-evidence-acquisition-v1.md) | `C7A9C60F1BDFDD3AD5E13DBCD347A51F82C4B0BEE1BD8C18EC6D4308F28528AE` |
| [nexus-g2-route-b-authoritative-evidence-acceptance-v1.md](nexus-g2-route-b-authoritative-evidence-acceptance-v1.md) | `1210577F16299C400A05D5F18EF102EBCDE3C66132BB5B2E78C3248A9DC0E568` |
| [nexus-g2-route-b-openai-hosted-authoritative-evaluation-v1.md](nexus-g2-route-b-openai-hosted-authoritative-evaluation-v1.md) | `B6F6AB0933CFFF3E88B84788374FFF22442AD565A430E81F79E9D1A330BA8284` |
| [nexus-g2-route-b-openai-hosted-adversarial-review-v1.md](nexus-g2-route-b-openai-hosted-adversarial-review-v1.md) | `7384FC571C81BFAE8A681B1BB442DBEED356E286BA2CCEAC9AF3675D2FA2F239` |
| [nexus-g2-route-b-openai-hosted-support-question-pack-v1.md](nexus-g2-route-b-openai-hosted-support-question-pack-v1.md) | `8A6491572F23598702C78D77E9E90C73B4E2B16B954E42F4993190EF1BEFE88B` |
| [nexus-g2-route-b-openai-hosted-authoritative-evaluation-acceptance-v1.md](nexus-g2-route-b-openai-hosted-authoritative-evaluation-acceptance-v1.md) | `B73BC2E9F4C73D81968DA227757F1CF517C93BA82E4D5A696852A91CDFDCE9EF` |
| [nexus-g2-openai-first-compatibility-rebaseline-review-v1.md](nexus-g2-openai-first-compatibility-rebaseline-review-v1.md) | `CCA9C25D833A1423B026F72C7EE459218D79151A9F23DDA86E078BDF192D6471` |
| [nexus-g2-openai-first-contract-minimization-matrix-v1.md](nexus-g2-openai-first-contract-minimization-matrix-v1.md) | `8A291A4A8AFB1644F473368813C13F443AF1650680E1F6C5DFADA014956D2A5E` |
| [nexus-g2-openai-first-compatibility-adversarial-review-v1.md](nexus-g2-openai-first-compatibility-adversarial-review-v1.md) | `06BB4F52F56D71D3B3C1C1AEFE17C3D400686D4F04F0192D79E901BD6819BDEA` |
| [nexus-g2-openai-first-proposed-clarification-pack-v1.md](nexus-g2-openai-first-proposed-clarification-pack-v1.md) | `82DA60966F590448CE887519A6819D9577730B13BC7114FDC87E27762B3A5190` |
| [nexus-g2-openai-first-compatibility-rebaseline-acceptance-v1.md](nexus-g2-openai-first-compatibility-rebaseline-acceptance-v1.md) | `873BB2135002CF975FCD58AA839469B73F1D10F4538548B3EA682A85A0A580E7` |
| [nexus-g2-host-qualification-evidence-successor-acceptance-v1.md](nexus-g2-host-qualification-evidence-successor-acceptance-v1.md) | `0AFF074A4097D66286E0EC126CF18EC21DE712F1F5397F0ECDF578EE0D614EC6` |
| [nexus-pre-g2-appcontainer-architecture-acceptance-v1.md](nexus-pre-g2-appcontainer-architecture-acceptance-v1.md) | `6D5C96FE917C09F3123D9024E24866FBD5F65373E1F826E9A45015536AAD6357` |
| [nexus-pre-g2-lpac-package-delivery-boundary-acceptance-v1.md](nexus-pre-g2-lpac-package-delivery-boundary-acceptance-v1.md) | `1D460A49BC3DF6A01326078F761B9E514843CB25B05FFA5F7D45A0B6108B0B1D` |
| [nexus-pre-g2-lpac-owner-release-acceptance-v1.md](nexus-pre-g2-lpac-owner-release-acceptance-v1.md) | `C50062E63BA01152C34127FDC0A656ED17D0F95FFB56133E4BBB9C709119790B` |
| [nexus-pre-g2-lpac-owner-release-system-module-provenance-acceptance-v1.md](nexus-pre-g2-lpac-owner-release-system-module-provenance-acceptance-v1.md) | `E8E1F7C848D0134707967EA020A2E0139DE17F47B50838A073622F5986F63E18` |
| [nexus-pre-g2-lpac-verifier-watchdog-responsibility-acceptance-v1.md](nexus-pre-g2-lpac-verifier-watchdog-responsibility-acceptance-v1.md) | `D214DADBF6F6048B70244F88855AE04FF0240B9B36A3D6C345DF3A9F51797B5C` |
| [nexus-pre-g2-lpac-code-integrity-evidence-acceptance-v1.md](nexus-pre-g2-lpac-code-integrity-evidence-acceptance-v1.md) | `259C3F67A4115FE83B68828ED7E8A8BD08D8A179EA7429A46C8E529E454CBCFB` |
| [nexus-pre-g2-current-lpac-host-exit-and-next-route-acceptance-v1.md](nexus-pre-g2-current-lpac-host-exit-and-next-route-acceptance-v1.md) | `C2B912A316114B0AC1797DB07F45B54FBC0A2D57AD2B16DB1515F80A5EEEF8BD` |
| [nexus-v2-g1.md](nexus-v2-g1.md) | `FA51F6D36AE7AFB9431D092F5D3FE4F1D1EE378F7B5ADEA8EBF10FE72495CEDE` |
| [nexus-runtime-r2-mcp-architecture.md](nexus-runtime-r2-mcp-architecture.md) | `C322C9FA95CEF310DAD80339A9EC706613959C54F92350A6FF0DE82A92DFEABC` |
| [nexus-runtime-r4-host-handoff.md](nexus-runtime-r4-host-handoff.md) | `2AB9E9322904176EB6ED70B64D33CEDE39729885CF95AFDA3EC3914342AAB1A2` |
| [nexus-runtime-r5-host-capability-inventory.md](nexus-runtime-r5-host-capability-inventory.md) | `FFEF98D9E4AFB678912152B536AAE7B6251B60F6DB8D82BAE30C918556F3135A` |
