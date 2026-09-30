# Nexus G2 OpenAI-First Compatibility Re-baseline Review v1

Status: **PROPOSED REVIEW — LIMITED CLARIFYING AMENDMENTS JUSTIFIED; NO CONTRACT CHANGE; G2 HOLD**

Review date: 30 September 2026

## 1. Authority, baseline and question

This review asks whether the accepted G2 Host contract confuses minimum end-to-end safety properties with provider-specific proof mechanisms. It applies the accepted Pre-G2 A0–A6 architecture, Host Qualification Scope & Exit, Route B Provider-Neutral Host Contract, Responsibility Re-baseline, UNKNOWN Resolution Matrix and accepted OpenAI-hosted evidence package. It does not alter any of them.

Baseline verification: branch `nexus-v2-g2-development`, HEAD `11f1e8cff470001fdce8dc057cf59ce3a421da2d`, clean working tree, and source `MANIFEST.json` at 187/187 matched with SHA-256 `CF1DB09A1988E7A3CCA9629EFF2D43FAB726B418C994DD84D667E18B3451A7D0`.

The owner direction is OpenAI-first and OpenAI-hosted-compatible without placing OpenAI-specific concepts in the Nexus safety core. This review does not try to make OpenAI pass. It asks what failure each P-property prevents and what minimum trustworthy composition can prevent, bound, detect or reconcile it.

## 2. Decision

**C. ONLY LIMITED CLARIFYING AMENDMENTS ARE JUSTIFIED.**

The accepted contract should not be replaced wholesale. A0–A6 already allow a demonstrated combination of Nexus application controls and qualified Host enforcement. The Responsibility Re-baseline already says internal loaded-module proof, a particular revision API, a dedicated currency-cap API, universal transcript, native idempotency key, monolithic receipt, universal secrets platform and provider push-change feed are not universal requirements.

The genuine defect is narrower: the current provider-evidence advance-gate workflow can be read as requiring the provider to document every component of P1–P6 and P8–P12 before any experiment, even where the accepted end-to-end property can be supplied by Nexus, by a provider/Nexus composition, or by a meaningful fail-closed qualification experiment. That interpretation is stronger than A2 and the accepted Responsibility Re-baseline.

Clarification must not weaken the safety properties. It must identify, per property, which provider fact is indispensable before experimentation, which controller mechanism is independently enforceable, which behavior can be tested, and which residual unknown forces STOP. P5/P6 retain hard provider-dependent boundaries; P7 remains unqualified; a client timeout, budget ledger, prompt or guest statement remains insufficient.

## 3. Non-negotiable G2 safety core

The following invariants remain provider-neutral and unchanged:

1. The workload cannot grant itself, inherit or obtain authority to relax its required restrictions.
2. Controller/API/model credentials are not exposed to untrusted workload inputs, files, environment or evidence.
3. Independently issued authority, admission and reservation complete before the first admitted side effect.
4. Every reachable billable or safety-relevant dimension has a finite enforceable bound; unknown money is never zero.
5. Stop-new-dispatch, cancellation request, acknowledgement, terminal cessation, effect reconciliation and cost settlement remain distinct states.
6. Cancellation, timeout, disconnect, deletion or missing output cannot silently become success or proof of no effect.
7. Potential effects remain UNKNOWN until positively reconciled; unsafe retry is prohibited while UNKNOWN.
8. Qualification evidence is externally sourced or externally corroborated and never rests solely on model/guest self-report.
9. Qualification binds one sufficiently stable public execution/configuration identity, admitted input basis, operation references and observation scope.
10. Material observable drift, expired qualification, changed authority/configuration or missing evidence invalidates the affected binding before dispatch.
11. Default deny remains the default for authority, optional input/effect channels, retries, delegation and fallback.
12. Host qualification precedes G2 execution authorization and never creates task authority.

The refinement in item 9 is deliberate: “sufficiently stable” need not mean internal provider implementation bytes when the qualified product is a managed service. It does require stable customer-visible resource/configuration identity, qualification scope/expiry and revalidation that fails closed. Hidden provider changes remain a provider trust residual; they cannot be mislabeled as observed.

## 4. Minimum end-to-end properties

The detailed origin, threat, responsibility and OpenAI composition mapping is in the companion [contract minimization matrix](nexus-g2-openai-first-contract-minimization-matrix-v1.md). Its principal findings are:

- **P1/P12:** bind public mode/configuration, admitted inputs, stable unit/turn/item/artifact references and a qualification epoch. Internal image/harness/enforcement bytes are required only if the public contract or tested property depends on them. Expiry and observable drift can trigger fail-closed requalification; API version alone is insufficient.
- **P2/P3/P4:** the provider must enforce the selected hosted boundary and define relevant restriction semantics. Nexus can own credential custody, dedicated-project actor minimization, immutable admitted configuration, channel exclusion and release sequencing. A monolithic applied-policy receipt is optional, but stored request parameters alone cannot establish PASS.
- **P5/P6:** Nexus can choose bounds, limit dispatch count, disable optional tools/delegation, reserve budget and refuse retries. It cannot externally impose a hard maximum on remote active compute, descendants, managed model/tool-loop work or provider billing. Provider-enforced finite bounds or a conservative composition from such bounds remain mandatory.
- **P7:** native cancel/delete interfaces make bounded testing meaningful, but cancellation/descendant/cleanup behavior remains experimental and cannot be replaced by stream close or client timeout.
- **P8/P9:** Nexus owns the operation journal and retry decision. Provider-native stable references and positive terminal/result/effect observations are still required. Native create idempotency and indefinite post-delete history are optional if Nexus admits at most one original attempt, reconciles before deletion and retains UNKNOWN/STOP when provider facts disappear.
- **P10:** Nexus may build a protected receipt bundle from signed/provider API observations, admitted request bytes, local journal facts and experiment results. A single provider-generated security receipt is optional. Missing source, scope, ordering or contradictions remain STOP.
- **P11:** workload non-possession of the application key and controller-side scoped custody are mandatory. Detailed revocation propagation to already running sessions is production hardening when hard lifetime/cancellation containment independently bounds the work; any authority change still invalidates Nexus grants and evidence immediately.

## 5. Responsibility model

The letters below classify necessary components, not whole properties exclusively:

- **A — PROVIDER-MANDATORY:** remote isolation enforcement, relevant network semantics, finite remote resource/lifetime/billing primitives, native unit/turn references and provider-side observations.
- **B — NEXUS-OWNED:** owner authority, admission, credential custody, exact request/input hashing, configuration allowlist, budget reservation, operation journal, receipt protection, qualification expiry and retry refusal.
- **C — COMPOSITE:** actor exclusion, effective policy binding, complete operation identity, cost maximum, observation/evidence bundle and drift invalidation.
- **D — QUALIFICATION-EXPERIMENT:** actual negative isolation behavior, cancellation/descendant behavior, event/result coverage, interruption recovery and configuration mismatch invalidation for the exact bounded mode.
- **E — LEGACY / OVER-SPECIFIED MECHANISM:** internal provider byte identity, universal applied-policy receipt, complete internal actor enumeration, universal native idempotency, monolithic security receipt, indefinite post-delete history and push drift notification when treated as mandatory mechanisms rather than replaceable evidence paths.

E removes no property. Each E mechanism is replaced by the exact minimum property and fail-closed composition in the matrix.

## 6. OpenAI composition test

The accepted OpenAI evidence remains **SUPPORTED 0 / PARTIAL 11**, with P7 experiment-resolvable and NOT PASS. This review does not reclassify those facts.

| Composition area | Existing accepted evidence | Architecture result |
| --- | --- | --- |
| Public identity | Session, environment, turn/item and artifact identities exist. | Potential composite basis for P1/P8/P9; loaded internal revision remains unobserved but is not universally mandatory. |
| Authority/credentials | Application key remains outside hosted sandbox; multi-agent and optional channels can be omitted. | Nexus can own custody/configuration; relevant customer actor/mutation scope still needs qualification/account binding. |
| Network/isolation | `network.access: disabled` has documented request semantics. | Provider enforcement plus exact configuration plus negative experiment can form P3/P4; requested configuration alone is not PASS. |
| Resources/lifetime | Container size and file/artifact limits exist; inactivity may cause deletion. | Insufficient for hard active lifetime/whole-unit bounds. P5 remains a pre-experiment provider-semantic blocker. |
| Cost | Prices and billing categories exist; usage is best effort and not final bill. | Nexus accounting cannot create a finite ceiling without provider-enforced model/loop/lifetime/billing bounds. P6 remains a blocker. |
| Cancellation | Cancel input, terminal events and delete exist; cleanup may be asynchronous. | Meaningful P7 experiment is possible only after other advance gates; no PASS or hard bound exists. |
| Observation/recovery | Saved items, artifacts, signed webhooks and traces exist. | Nexus journal/custody can compose P8–P10 for a fixed task, with missing evidence remaining UNKNOWN. A monolithic provider receipt is unnecessary. |
| Drift | Beta generation and requested configuration are visible. | Short qualification expiry and visible-config mismatch can be Nexus-owned; hidden material drift remains provider trust residual and requires periodic requalification. |

OpenAI-hosted is therefore compatible with the proposed composition model, but it is still not ready for experiment. The remaining hard blockers are the provider-enforced whole-unit lifetime/resource boundary and a conservative finite all-in financial exposure, including managed agent/model-loop behavior and cleanup/billing tail. Clarification or another authoritative supported control is still required for those facts.

## 7. HostAdapter architecture recommendation

G2 should formally preserve this separation:

```text
G2 Safety Contract
        ↓
HostAdapter interface
        ↓
OpenAIHostAdapter (primary implementation candidate)
        ↓
OpenAI Agents API / managed harness / openai_hosted environment
```

The **G2 Safety Contract** owns authority-before-effect, finite exposure, sequential admission, checkpoint/recovery facts, UNKNOWN/retry rules, cancellation state distinctions, evidence requirements and qualification invalidation.

The **HostAdapter** exposes provider-neutral primitives: create/admit one execution unit; return stable unit/operation references; bind admitted configuration/input identities; query status/results/effects/usage; request cancellation; query terminal/cleanup state; report relevant hard limits and observation coverage. Unsupported primitives are explicit and make the binding ineligible; adapters do not emulate missing hard guarantees.

The **OpenAIHostAdapter** maps session/environment/turn/item/artifact/event semantics, exact OpenAI configuration and billing categories. OpenAI-specific beta headers, resource types and event names stay outside the core contract. Future adapters may implement equivalent properties without imitating OpenAI.

Nexus governance remains provider-independent: grants, admission, reservations, evidence custody, qualification records, stop states, reconciliation and requalification. The adapter is narrow translation and observation code, not a generic agent runtime, scheduler, secret manager or substitute sandbox.

No adapter implementation is authorized by this review.

## 8. Classification of the accepted 24-question pack

The exact per-question decision and replacement wording are in the matrix. Totals:

| Classification | Questions | Count |
| --- | --- | ---: |
| KEEP | 5, 7, 9, 11, 13, 14 | 6 |
| REFRAME | 1, 2, 3, 4, 6, 8, 10, 15, 16, 19, 20, 21, 23 | 13 |
| MOVE-TO-NEXUS | 18 | 1 |
| MOVE-TO-EXPERIMENT | 12, 17 | 2 |
| DEFER | 22, 24 | 2 |

No question is discarded as irrelevant to security. MOVE-TO-NEXUS means a controller invariant removes the need for the requested provider mechanism. MOVE-TO-EXPERIMENT means accepted provider interfaces already make a bounded negative/fault test meaningful; it does not predict PASS. DEFER means useful production hardening that is not a prerequisite to the first secret-free bounded qualification experiment when the hard safety core is otherwise satisfied.

The companion [proposed clarification pack](nexus-g2-openai-first-proposed-clarification-pack-v1.md) reduces the pre-experiment provider questions to the unresolved semantics that Nexus and bounded experiments cannot safely manufacture.

## 9. Precise proposed amendment plan

If the owner later accepts this direction, create a versioned successor/clarification record rather than editing accepted history:

1. Preserve P1–P12 names, threats and PASS/STOP criteria.
2. Add a normative “minimum end-to-end property and evidence allocation” column using the companion matrix.
3. Define the pre-experiment gate as: provider documentation is mandatory only for remote facts that Nexus cannot enforce and an experiment cannot meaningfully establish; controller and experiment components must have separately reviewed designs before resource creation.
4. State that internal provider bytes/revisions, monolithic applied-policy receipts, universal native idempotency, monolithic security receipts and push drift feeds are optional mechanisms unless the exact mode depends on them.
5. Require an exact adapter-specific qualification profile, short expiry and fail-closed invalidation for visible drift, missing observations or authority/configuration changes.
6. Retain hard provider-dependent P5/P6 requirements and P7 measured cancellation. Explicitly prohibit substituting client timeouts, instructions, ledger entries, account alerts or post-hoc usage.
7. Version the OpenAI clarification pack separately; do not rewrite the accepted 24-question historical artifact.
8. Require independent adversarial review and explicit owner re-acceptance before any experiment proposal.

This is a limited clarification, not an OpenAI exception or a relaxation of default deny.

## 10. Preserved boundary

The separate [adversarial review](nexus-g2-openai-first-compatibility-adversarial-review-v1.md) binds and challenges this review and its matrix. No accepted file, MANIFEST entry, adapter, credential, provider account, sandbox, experiment or runtime code is changed here.

Scenario 01–04 remain **NOT RUN**; HQ1–HQ5 **NOT PASS**; HQ6 **NOT STARTED**; Positive Host Binding **ABSENT**; G2 **HOLD**. OpenAI-hosted remains an unqualified candidate. No provider outreach, implementation, commit, merge, push, tag or freeze is authorized.

**Decision: C. ONLY LIMITED CLARIFYING AMENDMENTS ARE JUSTIFIED.**
