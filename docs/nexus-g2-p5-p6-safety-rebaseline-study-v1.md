# Nexus G2 P5/P6 Safety Requirement Re-baseline Study v1

Version: `1.0.0`

Date: **2026-10-03**

Baseline: `57bf2a2df4efa0d93d621e396839f5767bdfa572` / `nexus-v2-g2-development`

Status: **NON-NORMATIVE FACTUAL / DESIGN STUDY ONLY - NOT ACCEPTED; NO EXPERIMENT OR IMPLEMENTATION AUTHORITY**

## 1. Overall decision and authority

**A. CURRENT P5/P6 ARE ALREADY CORRECTLY OUTCOME-BASED; NO AMENDMENT JUSTIFIED.** The current accepted overlay already permits verified composition, task-scoped applicability and an enforced monetary ceiling OR finite hard drivers with conservative all-in pricing. It does not universally require an immutable provider TTL, a native knob for every dimension, a per-dispatch currency API, a monolithic signed receipt, or immediate billing settlement. Removing those purported universal requirements would restate current authority, not resolve a missing safety premise. No amendment proposal or acceptance record is created.

Authority: owner attachment `a6281bf7-52e9-43a0-9bc8-444bc1741ff2`. Before additions, branch/HEAD/clean tree and MANIFEST 256/256 PASS were verified; raw MANIFEST SHA-256 `3DE276D82D6A73FE05543140521225AE76F858C16B549CBD9F69F6810DE8E79F`. Windows archive/checkout CRLF is normalized to canonical LF for entry verification; raw MANIFEST identity is checked separately. The protected sealed V4 manifest anchor remained unchanged. No provider research is reopened; existing eight-candidate evidence is used. Only Linux/upstream service-manager documentation needed for Route D design was read publicly, without executing examples or contacting execution providers.

### Controlling meanings and accepted precedence

- [Roadmap](nexus-roadmap-v2.md) G2 and budget/recovery rules, [Pre-G2 A0-A6](nexus-pre-g2-architecture-addendum-v1.md) through [acceptance](nexus-pre-g2-architecture-acceptance-v1.md), and [G1](nexus-v2-g1.md): complete pre-effect authority, qualified enforcement, native lifecycle, reservation and UNKNOWN-safe recovery. A1 forbids a parallel generic runtime; A2 permits qualified application/Host combination. A3 separates credentials/authority; A4 keeps domain context small; A5 delegation remains optional; A6 requires actual useful/failure/regression evidence. A0 preserves G1 freeze and no inherited G2 authority.
- [P1-P12 contract](nexus-g2-route-b-provider-neutral-host-contract-v1.md) through [acceptance](nexus-g2-route-b-provider-interface-acceptance-v1.md): supported candidacy semantics C, actual applicable-gate evidence Q, optional hardening H. P5 resources, P6 money and P7 cancellation have distinct properties; names/identifiers are unchanged.
- [HQ Scope & Exit](nexus-g2-host-qualification-scope-and-exit-decision-v1.md) through [acceptance](nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md): another route proves equivalent HQ1-HQ5 in its actual boundary; HQ6 requires one accepted capability's enforcing/observable primitives. Complete positive binding precedes separately authorized G2 implementation and useful-workflow acceptance. Windows APIs/Scenarios are not cross-route requirements.
- [Responsibility review](nexus-g2-responsibility-rebaseline-review-v1.md) through [acceptance](nexus-g2-responsibility-rebaseline-acceptance-v1.md): HQ1-HQ4 delegable with Nexus verification/binding; HQ5-HQ6 Nexus-owned. P1-P3/P5/P7-P8 have delegable platform components; P4/P6/P9-P12 retain Nexus governance responsibility.
- [UNKNOWN matrix](nexus-g2-route-b-unknown-resolution-matrix-v1.md) through [acceptance](nexus-g2-route-b-unknown-resolution-acceptance-v1.md) is read under the later [Limited Clarifying Amendment acceptance](nexus-g2-limited-clarifying-amendment-acceptance-v1.md). Its [amendment](nexus-g2-limited-clarifying-amendment-v1.md) sections 3-8 and [mapping](nexus-g2-limited-clarifying-amendment-p1-p12-mapping-v1.md) are the controlling forward-looking overlay. Historical proposed headings and eleven-C-row gates do not undo this accepted supersession.
- Exact current facts: [OpenAI adjudication](nexus-g2-openai-support-reply-adjudication-v1.md), [three-provider fresh assessment](nexus-g2-route-b-fresh-provider-adjudication-v1.md), [expansion matrix](nexus-g2-route-b-expansion-screening-matrix-v1.md), [deep review](nexus-g2-route-b-expansion-p5-p6-p7-review-v1.md), [checkpoint](nexus-g2-route-b-expansion-factual-checkpoint-v1.md). They are dated evidence, not new normative rules. Old and new B findings and human escalation PENDING remain.

Accepted amendment section 7 already separates required safety semantics/protections BEFORE each effect from later measured qualification. An actual instance ID is bound after safe authorized creation; it cannot be demanded before existence, nor used to excuse unbounded creation. A paper controller design supplies no actual reviewed custody or hard enforcement. This study adds no facts upgrading any provider.

## 2. Threat model and acceptable consequences

Threats include hostile or faulty workloads and ordinary control/transport/infrastructure failures, not a proof against a malicious qualified kernel/provider or fully trusted owner. Controller compromise is analyzed precisely: compromise of a restricted control endpoint must not expand a pre-issued Host-enforced grant/lease/cumulative allowance. Arbitrary compromise of the ultimate trusted grant issuer or Host root/TCB is not covered by a claim of controller independence; adopting a new TCB or shrinking failure coverage requires explicit owner review. No unqualified controller may bootstrap its own trust.

The consequence column defines an acceptance obligation, not a measured numerical allowance. A future protocol must bind actual maxima and failure coverage before its first effect. No owner exposure amount or resource grant is invented here.

### P5 threat register

| Threat | Asset / failure mode | Maximum acceptable consequence | Control owner / enforcing layer | Required evidence |
| --- | --- | --- | --- | --- |
| Hostile workload | Host/owner resources and control state; adversarial inputs | Only admitted resources/channels within finite whole-unit envelope | Platform kernel/VM + Nexus scope | Applied isolation/limits and external adversarial negatives |
| Accidental infinite loop | CPU/time/output exhaustion | Finite active time, aggregate CPU and output under ultimate cutoff | Infrastructure deadline/resource controls | Deadline origin, ceilings, fault-bound cessation |
| Fork/process-tree escape | Children leave tracked unit | Every descendant contained or denied; no orphan beyond bound | Kernel/VM membership and migration denial | Exact descendant/alternate-creation negatives, subtree observations |
| Background descendants | Parent exits while work persists | Parent completion never releases live subtree/exposure | Host lifecycle + Nexus stop states | Whole-unit terminal/zero-live readback, not parent exit alone |
| Controller crash | Lost cancellation and progress | Original unit remains independently bounded; no replacement | Infrastructure + Nexus durable references | Controller-loss test under known fallback |
| Controller disconnect | Remote work survives stream loss | Same bound; effects remain UNKNOWN until observed | Host lease + protected Nexus custody | Original query/retention and disconnect coverage |
| Controller compromise | Stolen endpoint authority tries extension/recreation | Cannot exceed independently issued envelope/cumulative Host allowance | Separate Host admission/enforcer | Actor rights, denied extension/replay/create and issuer boundary |
| Watchdog failure | Advisory timer or kill path disappears | Independent ultimate enforcement remains; no sole-watchdog proof | Separate infrastructure fallback | Common-cause analysis and watchdog-loss test |
| Provider partial failure | Lifecycle service fails while guest runs | Every admitted expected fault has finite containment consequence | Provider/infrastructure TCB | Supported failure scope and absolute fallback semantics |
| Failed delete/kill | Request succeeds/fails but live work persists | No new dispatch; hard fallback still bounds original | Host enforcement + Nexus UNKNOWN | Actual terminal/zero-live evidence and finite cutoff |
| Pause/resume | Clock/exposure resets or unit recreated | Original cumulative deadline/resources unchanged or resume denied | Host actor/lease controls | Timer origin/paused coverage and denied renewal paths |
| Persistent survivors | Disk/snapshot/service outlives compute | No survivor, or separately authorized quantity/lifetime/effect bound | Storage/service infrastructure + Nexus graph | Residual inventory, custody and retention cutoff |
| Workload extends lifetime | Keepalive/notification/management channel | No guest path can enlarge ultimate envelope | Infrastructure authority exclusion | Exact reachable-channel and actor negatives |
| Workload weakens limits | Mutable quota/cgroup/policy/privilege | Required ceilings remain outside guest authority | Kernel/platform permissions | Effective rights/limits, mutation denial and drift binding |
| Setup/cleanup stalls | Work occurs outside main timer | All relevant setup/teardown/retention included or separately bounded | Infrastructure + staged admission | Stage clocks, shutdown allowance and failure coverage |

### P6 threat register

| Threat | Asset / failure mode | Maximum acceptable consequence | Control owner / enforcing layer | Required evidence |
| --- | --- | --- | --- | --- |
| Runaway compute billing | Owner funds; infinite allocation/loop | Finite conservative cumulative charge <= remaining authority | Provider hard driver/money controls + Nexus reserve | All-in cap or hard quantities/rates and enforced cutoff |
| Storage survives execution | Retention charge accumulates after stop | Finite retained cost or proven included/unreachable driver; P5 retention still bounded | Storage billing contract/enforcer | Quantity, retention, price scope and residual inventory |
| Egress explosion | Fast paid traffic before cancellation | Finite byte/currency maximum independent of cancellation latency | Infrastructure egress or all-in charge cap | Covered channels/rate/overshoot and guest mutation denial |
| GPU/high-cost escalation | Expensive resource can be allocated indirectly | Denied, or separately granted finite resource/cost | Host/provider permissions + Nexus closed graph | No reachable escalation/auto-create channel |
| Retry duplication | Ambiguous request creates another charged unit | Original attempt/exposure retained; no blind retry or recreation | Nexus + Host creation/replay controls | Durable original references, request/replay semantics |
| Failed cleanup | Resources continue charging | Predetermined finite cutoff/no-charge scope includes cleanup failure | Provider/infrastructure | Failure-tail and survivor terms, not expected cleanup speed |
| Failed deletion | Charged unit remains despite acknowledgement | Hard accrual maximum independently survives failed delete | Provider/infrastructure | Cutoff/failure attribution semantics and observation |
| Delayed settlement | Accurate bill appears later | Amount bounded; reservation not released by absent usage | Provider charge contract + Nexus reconciliation | Accrual vs report vs final bill scope; revised charges |
| Unknown tail charges | Setup/retries/logs add an omitted dimension | Unknown amount blocks admission; no zero-by-omission | Provider facts + Nexus arithmetic | Exhaustive applicable driver and failure inclusion basis |
| Usage overshoot | Cap propagation lag exceeds ceiling | Quantitatively finite overshoot included in reservation | Billing infrastructure | Maximum cutoff lag/excess or exact all-in liability ceiling |
| Controller loss | Cost monitor stops while charges accrue | Same predeclared maximum remains independent of monitor | Infrastructure hard bound | Loss-of-controller cutoff/charge coverage |
| Adversarial cost maximization | Workload selects worst permitted path | All allowed paths fit cumulative cap at worst-case rates | Composite graph + Host controls | Maximum driver quantities, concurrent/indirect path closure |
| External paid effects | Gateway/model/tool triggers upstream charge | Explicit prior grant and separate finite paid-effect allowance | External service hard controls + Nexus admission | Token/call/retry bound, price basis, effect references |
| Price/plan change | Maximum rate rises after calculation | Supported rate/liability ceiling or stop before affected dispatch | Billing contract + Nexus invalidation | Price interval/rate upper bound; no historical-rate assumption |
| Shared usage/renewal | Other actors consume cap; fixed plan renews indefinitely | Headroom/global liability bounded for declared horizon; no auto-topup surprise | Account/contract controls + Nexus scope | Actor set, obligations, renewal/cap applicability |

## 3. Exhaustive atomic current P5/P6 classification

Primary labels are exactly: A INVARIANT; B MECHANISM_SPECIFIC; C COMPOSABLE; D EXPERIMENT_RESOLVABLE; E PROVIDER/INFRASTRUCTURE_MANDATORY; F UNSAFE_TO_RELAX. One primary label per row; component ownership can differ. E identifies the non-controller hard enforcing component; C its end-to-end composition. F identifies the refusal obligation most directly threatened by relaxation. This inventory decomposes contract P5/P6, mapping sections 6-7 and amendment sections 4/7, including adjacent authority/failure requirements; it creates no new P identifiers or normative obligations.

| ID | Current atomic obligation | Primary | Reason / enforcing allocation |
| --- | --- | --- | --- |
| S01 | Applicable CPU ceiling and aggregate execution exposure | E | Controller intention cannot throttle hostile remote descendants; qualified application may narrow input but kernel/Host bounds CPU. |
| S02 | Applicable memory ceiling | E | Allocation request and OOM observation alone do not establish maximum/consequence; exact enforcer scope required. |
| S03 | Finite active/ultimate lifetime and termination | E | Independent of controller progress and guest cooperation; a provider TTL is one possible mechanism, not the property. |
| S04 | Whole-unit descendants/background containment | E | Native membership/lifecycle or deny-all descendant creation; root-only observation is insufficient. |
| S05 | Process/concurrency bound where reachable | E | Sequential admission alone cannot prevent guest forks or parallel paid paths. |
| S06 | Storage quantity and retained lifetime | C | Host quota/lifecycle + graph exclusion/independent survivor bound + Nexus inventory/custody. |
| S07 | Output/log/input exposure limits | C | Qualified bounded producer/consumer channels plus infrastructure storage/process/lifetime controls; closed omitted channels explicit. |
| S08 | Workload cannot relax its own envelope | A | No authority/control credential/channel to extend required resources or restrictions. |
| S09 | Controller-loss/failure consequence remains bounded | E | Userspace watchdog-only and controller availability cannot supply ultimate fallback. |
| S10 | Setup/pause/stop/resume/cleanup coverage | C | Compose stage envelopes; deny reset/recreation, bind cumulative deadline and survivors. |
| S11 | Effective actor exclusion or nonrelaxable controls | C | Mutable provider option can be safe only if every relevant actor/path is independently constrained and qualified. |
| S12 | Justified nonapplicability of a dimension | C | Closed admitted graph + actual channel denial + independent evidence; never omitted because inconvenient. |
| S13 | Actual limit/configuration/unit identity and freshness | C | Supported Host facts + protected Nexus receipts + same-unit binding at correct barriers. |
| S14 | Exact observed limit/descendant/failure behavior | D | Test measured Q behavior only after pre-effect safety semantics/enforcement exist; test cannot discover its own safe maximum. |
| S15 | Missing/unbounded mandatory P5 fact STOP | F | Replacing UNKNOWN with an optimistic timer increases worst-case containment risk. |
| S16 | Every applicable financial driver included | A | Setup, models, retries, storage, network, failure/tail and external effects cannot be omitted. |
| S17 | Supported enforceable monetary or driver upper bound | E | Reservation, prompt and rate table cannot bind an external bill. Native currency API itself is optional. |
| S18 | Conservative finite all-in maximum composition | C | Hard quantities + maximum rates/increments/inclusions + finite failure/survivor/paid-effect terms. |
| S19 | Maximum fits current remaining cumulative owner authority | A | A finite but unauthorized amount is still ineligible; no historical RM5/account grant transfers. |
| S20 | Admission/reservation and actual route custody before effects | C | Reviewed Nexus controller/credential/evidence controls + protected Host enforcement; a design plan is insufficient. |
| S21 | Ambiguous create/internal retry/reset costs bounded | C | Original-attempt admission and replay denial plus supported provider internal semantics; client count alone is incomplete. |
| S22 | Billing cutoff/overshoot/failure tail finite | E | Unknown accrual multiplier/currency excess cannot be resolved by one sampled invoice. |
| S23 | Retained/egress/external-service exposure bounded | C | Enforced caps or justified included/unreachable terms + exact actor/channel/rate binding. |
| S24 | No soft quota/alert/balance/accounting substitute | F | Only separately proven hard liability/cutoff semantics can make an account control a valid component. |
| S25 | Accrual bound, effect reconciliation and settlement distinct | A | Unknown final invoice may stay UNKNOWN with maximum reserved; silence never releases exposure. |
| S26 | Actual account/rate/usage and reconciliation measurement | D | Status-only preflight before cost effects; postflight only inside predetermined envelope; no secret values. |
| S27 | Version/rate/plan/actor/material drift invalidation | C | Contract applicability + current protected checks + affected binding STOP/requalification. |
| S28 | Ledger scopes Nexus-managed dispatches; shared interference accounted | A | Do not silently claim control of unrelated native use or double-spend relied-on headroom. |
| S29 | Qualification does not grant paid effects/task authority | A | Separate issuance, experiment, qualification and every later dispatch/resume gate. |
| S30 | Missing current bound/headroom/price STOP before creation | F | Finite observed happy path or subsequent cleanup cannot repair unsafe first effect. |

**No mandatory current row needs primary B.** The following are B-class *illustrative mechanisms*, already optional under accepted authority: immutable native TTL; per-dispatch monetary-cap API; native per-dimension knob; monolithic signed receipt; a particular watchdog/Windows Job/systemd implementation; native snapshots/idempotency as universal recovery. Their optional status does not authorize ignoring literal gates of an existing exact protocol. This study does not manufacture a new restrictive requirement in order to remove it.

## 4. Twelve non-negotiable invariants

| ID | Invariant / unchanged consequence |
| --- | --- |
| I01 | Workload cannot expand its own authority, delegation, parallelism or indirect paid effects. |
| I02 | Controller credentials and applicable owner/model secrets remain unreachable by workload and absent from evidence. |
| I03 | Workload cannot unilaterally remove, extend or reset the required execution/resource envelope. |
| I04 | Ultimate whole-unit execution/resource consequence remains finite under controller loss and every admitted expected failure. |
| I05 | Independently issued then-valid authority, eligibility and conservative reservation precede each side effect. |
| I06 | UNKNOWN persists with original identity/effects/exposure; never silently becomes success or no effect. |
| I07 | Cancellation request/acknowledgement is not cessation, cleanup or settled bill. |
| I08 | Qualification does not grant task authority; binding and G2 acceptance are separate. |
| I09 | Model/guest self-report alone cannot prove enforcement; decisive evidence is external and protected. |
| I10 | Unreconciled external effects cannot be retried/replaced automatically; renewed authority and budget do not erase prior exposure. |
| I11 | Worst-case financial exposure under hostile workload is finite and within cumulative owner authority. |
| I12 | Required enforcement does not rely on workload cooperation, prompts, bookkeeping or sole controller/watchdog survival. |

Accepted amendment section 4 also requires exact identity/freshness, default deny, and material-drift invalidation. These remain mandatory alongside I01-I12; the requested twelve are not a replacement or reduced core. Qualified platform/kernel/provider TCB assumptions must be named, not enlarged to excuse a failure. Finite failure coverage cannot mean whatever happened was excluded retrospectively.

## 5. Outcome-based P5/P6 restatement and composition rules

These are **NON-NORMATIVE RESTATEMENTS of already accepted outcomes**, not proposed successor clauses:

**P5:** An admitted execution unit has a finite, enforceable, non-workload-relaxable whole-unit resource/active-lifetime/ultimate-termination envelope for every reachable safety-relevant dimension, bound to the exact configuration and known enforcing layer, including controller loss and declared expected failure consequences. CPU rate plus finite runtime bounds aggregate CPU; memory, process count, disk/inodes, output/logs, channels and descendants require their applicable hard coverage. Paused/stopped/resumed states and retained objects cannot reset or leave that envelope. Final-state observations are distinct from the enforcement that makes tests safe.

**P6:** Before each effect, Nexus establishes and reserves a conservative finite maximum financial consequence of that admitted unit and every separately authorized paid effect, including all applicable failed/ambiguous/internal-retry/retention/overshoot/cleanup/tail terms, within current cumulative owner headroom. An enforced all-in monetary/liability ceiling OR enforced finite charge-driver maxima with maximum applicable prices/increments can supply the hard financial half; Nexus supplies verified admission/arithmetic/custody/UNKNOWN accounting. Fixed pricing may bound a cost dimension without duration-metered billing, but neither proves P5 nor creates a zero-cost claim.

`SAFE_COMPOSITION(U) = ALL(required independent hard enforcers applicable to U) AND reviewed pre-effect authority/custody/admission/reservation AND protected exact-unit evidence/invalidation/reconciliation AND qualified measured coverage AND separate current task/experiment authority`

For financial arithmetic use `C_max = fixed_committed_obligations(H) + sum(ceil(Q_i_max / increment_i) * rate_i_max) + bounded_setup_failure_retry_retention_overshoot_cleanup_tail + bounded_external_paid_effects`. Do not double-count included terms; zero requires justified no-charge/unreachability scope. An enforceable all-in liability cap may bound a grouped sum if its complete coverage, lag and excess are proven. Reporting latency alone need not raise charge or be instant, but any unknown accrual/cutoff amount leaves the maximum UNKNOWN. P5 still requires bounded relevant retained-resource lifetime even when its price is included.

### P6 candidate control assessment

These are conditional component tests, not current provider findings or newly accepted mechanisms. Every YES below needs supported exact-scope evidence; otherwise STOP. No control can replace an unrelated missing P5 dimension.

| Candidate control | Enforceability / workload bypass | Controller-loss consequence | Overshoot / billing tail | Pre-effect computability |
| --- | --- | --- | --- | --- |
| Fixed infrastructure cost | Contractual all-in liability for finite H; guest cannot buy upgrades/renewals or access infrastructure control | Covered obligation remains bounded without online accounting; no uncontrolled renewal | All applicable overage, taxes, retained services and failure charges included or independently bounded | YES only with exact contract/horizon/exclusions and remaining owner authority |
| Hard resource limits | Actual infrastructure CPU/RAM/tasks/storage/channel ceilings; guest cannot mutate, migrate or allocate outside unit | Ceilings survive controller loss; separate ultimate lifetime still required | Quantified overrun and every charge driver/failure phase; quantity cap alone does not bound duration-priced charge | YES only when finite quantities/lifetime and maximum rates/increments close all terms |
| Immutable maximum lifetime | Whole-unit infrastructure deadline includes stages/descendants; no extension/reset/pause/recreate bypass | Independent cutoff survives loss and admitted faults | Numerical failure/termination tail and survivors must be covered separately | Only finite time term; not total money without hard quantities/prices |
| Network disabled | Effective closure of every guest/indirect billable channel, including trusted proxies; no inherited bypass | Applied denial remains independent of controller | Zero egress charge only for proven closed scope; unrelated model/storage/service tails remain | Removes a term only with justified no-charge/unreachability evidence |
| Egress ceiling | Enforced byte or all-in charge cap on all reachable paths; guest cannot select excluded channel | Native bound remains without monitor/cancel | Quantified bursts, cutoff excess, minimums and retained traffic charges | YES for this driver with maximum charged bytes/rate or complete liability ceiling |
| No persistent resources | Creation/retention paths denied or guaranteed whole-unit destruction; guest cannot export/create survivors | Denial/destruction does not require controller cleanup | Cleanup failure and outside logs/snapshots/artifacts cannot be assumed absent | Removes retention only with supported failure/inclusion scope; otherwise add bounded term |
| Dedicated project/account | Narrows actors only; guest lacks account credential, but dedication itself imposes no financial ceiling | Independent hard controls still needed | Shared interference and every account driver/tail remain in scope | NO alone; only improves binding of a separately proven cap/headroom |
| Provider hard spend ceiling | Genuine scope-complete liability/cutoff control; no guest/controller ability to raise cap or move charges | Provider limit applies without Nexus progress | Maximum overshoot/residual accrual must be finite and reserved | YES only when cap plus maximum excess covers every applicable charge |
| Prepaid finite balance | Balance alone is not enforcement; separately prove no debt, topup, credit, uncovered service or bypass | Hard liability terms, if any, must survive loss | Maximum post-balance excess/tail cannot be inferred from current balance | NO alone; YES only through separately supported finite liability semantics |
| Finite API token budget | External service hard cumulative call/token/tool/retry bound; guest cannot use other credential/model or reset it | Bound survives caller loss; client request counting does not constrain internal loops | Internal retries, cached/input/output units, rounding and failure tails included | YES only with finite all-in driver graph and maximum applicable rates |
| Explicit paid-effect grants | Nexus enforces prior scope/admission; grant does not impose external charge cap by itself | Independent service/Host bounds still needed; unresolved effects retain reservation | Each admitted service's hard overshoot/tail maximum remains necessary | YES only with actual custody plus separately enforced maximum and conserved headroom |
| Conservative cost formula | Arithmetic over independently enforced premises; cannot prevent a guest or provider exceeding unproven premises | Reserved maximum persists, but ledger does not stop accrual | Includes all quantitative failure/tail/overshoot terms without double-counting | YES only if every input maximum and price scope is proven; missing input is UNKNOWN |

### Four candidate compositions

| Composition | Equivalent only when | Failure / non-equivalence |
| --- | --- | --- |
| Immutable provider TTL | Hard resources/channels, exact origin/stages/tree/controller-loss/fault destruction, survivor and cost coverage also close | TTL name/default or unchanged field alone misses setup, tail, outside objects and charge drivers. |
| Provider max runtime + nonpersistent unit + hard ceilings + forced destruction | No resume/extensions/recreation; actual actor graph, fault/survivor scope and all charges independently bounded | Nonpersistent flag without proof; max per-session resets; delete can fail; quantity/price omitted. |
| Provider hard maximum + Nexus watchdog + independent provider ultimate timeout | Watchdog only tightens deadline; independent ultimate bound survives its loss; original total exposure conserved | Two watchdogs sharing controller/API/kernel failure are not independent ultimate enforcement. |
| Owned Host + cgroups/namespaces + manager/watchdog + boot cleanup | Separate accepted infrastructure TCB, protected launch, full dimension coverage, actual controller-loss/manager/fault fallback and no resurrection | Kernel quota has no wall deadline; reboot-only cleanup requires reboot; manager timer has mutable/extension/type semantics; new Host unqualified. |

### Order, invalidation and forbidden substitutions

1. Define exact capability, subject/code/dependencies, unit identity scheme, reachable actors/channels/effects, threat/TCB scope and numerical cumulative bounds. Establish supported hard semantics and a separate owner-approved route; no circular trust or assumed absent channels.
2. BEFORE creation: actual reviewed controller/custody, current independent grant/account/financial facts, safe allocation/ambiguity plan and hard creation/failure envelope. BEFORE release: bind actual unit/configuration/limits, loaded Nexus-controlled provenance, effective input/credential/isolation state and fallback readiness. Verification barriers must prevent execution before enforcement.
3. Test only measured uncertainty within those bounds; all claimed independent controls identify shared failure domains. On failure stop new dispatch, use admitted native cancellation/ultimate fallback, preserve original refs/UNKNOWN/reservation and bounded authorized cleanup. No blind retry/new unit.
4. Bind versions/configuration/actors/rates/clock/expiry/source/scope. Material drift, missing/contradictory observations, new channels, unbounded survivor/charge, altered fallback or control reachability invalidate before further effects. Require requalification at the affected scope, not universal TCB reimplementation.

Forbidden substitutes: prompts, voluntary SIGTERM, client wait/deadline, userspace-watchdog-only, ledger/reservation, post-hoc logs, guest self-report, one successful stress run, ordinary retry, expected usage, soft monthly budget/alert, prepaid balance, unquantified spend overshoot, or an assumption that the controller is always online. A dedicated account narrows actors but is not a cap. A prepaid balance counts only if separate authoritative liability/cutoff/overshoot/no-auto-topup terms make it a genuine hard bound. A finite model input/output parameter does not automatically bound all internal calls/retries/tools.

## 6. Eight-provider hypothetical compatibility (no new research or PASS)

Every row evaluates the hypothetical outcome wording WITHOUT changing accepted semantics. A missing universal mechanism that is already optional cannot improve readiness. No provider is ranked or selected.

| Candidate | Classification | Mechanism assumption already optional | True remaining safety gap / experiment consequence |
| --- | --- | --- | --- |
| OpenAI hosted | STILL_PROVIDER_CLARIFICATION_REQUIRED | Native session budget or currency API is not sole proof; no monolithic receipt needed | Active whole-unit/model-loop/internal retry and financial/cancel tail remain unbounded in current evidence; human escalation PENDING. No safe experiment. |
| Daytona | STILL_PROVIDER_CLARIFICATION_REQUIRED | Resettable TTL can form a verified actor-excluded composition; SDK must expose/use actual supported mode | TTL existence positive, but reset/actor/custody, all-in retained/failure charges and exact applied graph remain open. No safe experiment. |
| Modal | STILL_PROVIDER_CLARIFICATION_REQUIRED | CPU allocation request need not be native hard knob if explicit limit is set; workspace cap only a possible component | Maximum lifetime/hard CPU/RAM positives preserved; setup/fault tail, all drivers/gross-net/shared scope and controller/policy custody incomplete. No safe experiment. |
| E2B | STILL_PROVIDER_CLARIFICATION_REQUIRED | A protected kill-only/no-resume composition may exclude mutable timeout/pause paths; no generic loop needed | Narrow compute half remains positive; hard failure/whole-unit/remaining-cost/actor and template-generation proof incomplete. No safe experiment. |
| Blaxel | STILL_PROVIDER_CLARIFICATION_REQUIRED | Immutable TTL itself not mandatory if no-update/clear actor closure verified | Creation-age expiry positive; hard allocations/fault termination, retained charges and actual non-root/control custody unresolved. No safe experiment. |
| Runloop | STILL_PROVIDER_CLARIFICATION_REQUIRED | Fixed lifetime need not be idle timeout; gateway secrecy is not task authority | <=48h parameter positive; clock phases, suspend/resume/fault and disk cutoff/billing discrepancy plus custody open. No safe experiment. |
| Vercel | STILL_PROVIDER_CLARIFICATION_REQUIRED | Total persistent-object immutability not necessary for one proven nonpersistent/no-resume session | Session cap and Hobby no-extra-Sandbox-charge positives retained; fault tree/tail and actual single-session/charge-scope/custody still open. No safe experiment. |
| Cloudflare | STILL_PROVIDER_CLARIFICATION_REQUIRED | A provider native total-TTL knob need not be the only ultimate enforcer | Inactivity/keepAlive is not a whole-unit bound; supported independent total/failure cutoff and multi-product charge/custody proof missing. No safe experiment. |

Status-change effect for all eight: **NO_CHANGE in current eligibility**. Primary hypothesis classification above identifies why; none earns POTENTIALLY_ADVANCES_IF_AMENDMENT_ACCEPTED because composition is already accepted and missing factual/actual control premises persist. None is provider-wide INCOMPATIBLE_WITH_INVARIANT from absent evidence. More favorable pricing cannot compensate for P5/P2/P3/P10. Assuming a local timer, all-zero extras, safe silent SDK recreation, indefinite free compute as containment, or untested actor denial would be unsafe improvement and is rejected.

## 7. P7 preservation and finite conclusion

Preserve all eleven states: `CANCEL_REQUESTED`, `CANCEL_ACKNOWLEDGED`, `EXECUTION_STOPPING`, `EXECUTION_CEASED`, `DESCENDANTS_CEASED`, `SANDBOX_TERMINATED`, `PERSISTENT_RESOURCE_STATE_KNOWN`, `RESOURCE_RELEASED`, `BILLING_CEASED`, `RESULT_OBSERVED`, `EFFECTS_RECONCILED`. A positive source may establish one state only at its scope. Price-fixed/no-charge evidence does not establish cessation; kernel kill request does not establish zero-live; boot cleanup does not establish past effect absence. Bounded UNKNOWN can safely prohibit retry but is not task success, settled finance or useful G2 acceptance. No P7 requirement or exact local STOP is relaxed.

Study conclusion A concerns P5/P6 wording, not adequacy of present provider evidence. No normative amendment is justified. Removing independently enforced finite failure/financial bounds to make a provider experiment-ready would be a **rejected safety weakening (D-type alternative)**, not a hidden B clarification. Changing the accepted threat model/TCB or permitting larger owner risk would require a separate explicit architecture decision; this study does not make one.

[Route D feasibility](nexus-g2-route-d-owned-host-feasibility-v1.md) is a conditional design-only fallback, not the historical trusted-launch **Option D** or a NexusTest/Option A fallback. It does not start D0-D7, select infrastructure, install or qualify a Host. [Adversarial review](nexus-g2-p5-p6-safety-rebaseline-adversarial-review-v1.md) binds both subject documents and all eighteen required counterexamples.

Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD. OpenAI human escalation PENDING; all eight candidates remain below experiment readiness. A0-A6/P1-P12, frozen Roadmap/G1/R2/R4/R5 and sealed V4 are unchanged. Public documentary reads only; no credentials, accounts, provider resources, paid activity, HostAgent/HostAdapter/G2/G3/G4 or execution. A factual/design checkpoint commit plus canonical MANIFEST is authorized; acceptance/merge/push/tag/freeze is not.

## 8. Exact accepted/evidence source binding

Hashes below identify baseline canonical LF bytes, not runtime enforcement. Historical draft headings are read through the acceptance chain above; newer factual checkpoints preserve rather than amend normative rules.

| Baseline source | SHA-256 |
| --- | --- |
| [nexus-pre-g2-architecture-addendum-v1.md](nexus-pre-g2-architecture-addendum-v1.md) | `B6680C710DDA8FB7808E06CC2569FD1BB6A4AEED47B2223F9626E411E298BE14` |
| [nexus-pre-g2-architecture-acceptance-v1.md](nexus-pre-g2-architecture-acceptance-v1.md) | `C8B2FE28F9E2B6250288B736B8741824CD1FC750299AADCE07AB72C9479E782B` |
| [nexus-roadmap-v2.md](nexus-roadmap-v2.md) | `E803515EA2342C13B548601E01BA015E6827AA5D6A55C98562533D1EF77D8BA8` |
| [nexus-v2-g1.md](nexus-v2-g1.md) | `FA51F6D36AE7AFB9431D092F5D3FE4F1D1EE378F7B5ADEA8EBF10FE72495CEDE` |
| [nexus-g2-route-b-provider-neutral-host-contract-v1.md](nexus-g2-route-b-provider-neutral-host-contract-v1.md) | `E97ECF70BFB1D0082E7DE8E7C8100E321174062E15F9C2EC62CDAC4BB97BEFE0` |
| [nexus-g2-route-b-provider-interface-acceptance-v1.md](nexus-g2-route-b-provider-interface-acceptance-v1.md) | `BA45C5223212DF59A287A51FB0966C18D6C1D7C004C6E86ACAA68D878B3936DF` |
| [nexus-g2-host-qualification-scope-and-exit-decision-v1.md](nexus-g2-host-qualification-scope-and-exit-decision-v1.md) | `6CF3AB004B66580531185E7E0CE7394AA349ECB3E1E3905F224ED0259BBFCD69` |
| [nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md](nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md) | `A3B47DB405B30896A92F50B7E6EF018813980461FA3FEF315EC7AF3CF85F53F1` |
| [nexus-g2-responsibility-rebaseline-review-v1.md](nexus-g2-responsibility-rebaseline-review-v1.md) | `8220287EDDC1DFE653394E29D53A53B7413168598336907F61493DD65E751B93` |
| [nexus-g2-responsibility-rebaseline-acceptance-v1.md](nexus-g2-responsibility-rebaseline-acceptance-v1.md) | `F2CD2FE306F065D1A97E4EDAD50098ED73EC82C5EF4E93E378511B318948A942` |
| [nexus-g2-route-b-unknown-resolution-matrix-v1.md](nexus-g2-route-b-unknown-resolution-matrix-v1.md) | `6FD8BDE5D2ACA64301D280BED050C957EC40F8C767EA41B9CF60B8877CD7197E` |
| [nexus-g2-route-b-unknown-resolution-acceptance-v1.md](nexus-g2-route-b-unknown-resolution-acceptance-v1.md) | `69CF5D6A2AA3E49C339A9BAC1981E449F27452A9A6E6A5D966BC567ABA014A61` |
| [nexus-g2-limited-clarifying-amendment-v1.md](nexus-g2-limited-clarifying-amendment-v1.md) | `0760F2D37BF87F8F6042FA87787ACFDA7EB5899DB61E0F5C1517C048F19D1320` |
| [nexus-g2-limited-clarifying-amendment-p1-p12-mapping-v1.md](nexus-g2-limited-clarifying-amendment-p1-p12-mapping-v1.md) | `49A00E43C253939C0733B8A84A83B22846A21914EEE02DF3FECBE66A8F2A9CCA` |
| [nexus-g2-limited-clarifying-amendment-acceptance-v1.md](nexus-g2-limited-clarifying-amendment-acceptance-v1.md) | `0AE283239132F08C5AB851D7E0DC3BEBDFEE1AE2C9F92538DB2AE1C7D9A0A280` |
| [nexus-g2-openai-support-reply-adjudication-v1.md](nexus-g2-openai-support-reply-adjudication-v1.md) | `ABCFAC35985E174768E8D50995B61684EF3AB309D8591869D73C4109B1D81041` |
| [nexus-g2-route-b-fresh-provider-adjudication-v1.md](nexus-g2-route-b-fresh-provider-adjudication-v1.md) | `29B45A6BFFAD7F9DD50ACC7BBC0181F694BE0B42880A6F2ED828C2E5B7E5F022` |
| [nexus-g2-route-b-expansion-p5-p6-p7-review-v1.md](nexus-g2-route-b-expansion-p5-p6-p7-review-v1.md) | `E7EABF71C81B71AE5774E9DD154EBFE84B79835994F594962865E326AF73153C` |
| [nexus-g2-route-b-expansion-factual-checkpoint-v1.md](nexus-g2-route-b-expansion-factual-checkpoint-v1.md) | `C1377CBA16D7F0AEC81A3873377D7618565012B3DFD08341A00911A39714BB44` |
