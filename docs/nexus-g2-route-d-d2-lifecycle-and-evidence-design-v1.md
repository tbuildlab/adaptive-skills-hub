# Nexus G2 Route D D2 Lifecycle and Evidence Design v1

Version: `1.0.0`

Date: **2026-10-03**

Starting baseline: `a0bdfd2b6ea46844d317dff67687e681caacc3c3` / `nexus-v2-g2-development`

Status: **FACTUAL / DESIGN CHECKPOINT ONLY - NOT ACCEPTED; NO IMPLEMENTATION OR EXPERIMENT AUTHORITY**

## 1. Conclusion and design limits

Conceptual state machine and evidence architecture defined; actual supported stack, trustworthy effective release barrier and ultimate fence remain UNKNOWN. [D2](nexus-g2-route-d-d2-architecture-analysis-v1.md) result C controls. This document defines no wire serialization, unit configuration, firewall rule, credential protocol or Host code. [D0](nexus-g2-route-d-d0-requirements-v1.md) numeric values are candidate planning targets only; [D1](nexus-g2-route-d-d1-threat-model-v1.md) fault scope remains unchanged.

## 2. Ordered lifecycle and effect barriers

PREPARE -> ADMISSION -> CREATE UNIT -> BIND LIMITS -> VERIFY LIMITS -> LOAD INPUT -> START -> OBSERVE -> CANCEL if requested -> FORCE TERMINATE if deadline/failure -> VERIFY CESSATION -> VERIFY DESCENDANTS -> RECONCILE EFFECTS -> CLEAN RESOURCES -> VERIFY CLEANUP -> FINALIZE EVIDENCE -> TERMINAL STATE.

Natural completion skips cancel/force initiation, never the verification/reconciliation/cleanup steps. PREPARE here is pure plan/validation; any input staging, upload, helper/resource/fence creation is an effect and must occur only after its admission. CREATE UNIT means bounded trusted setup allocation, **not execution of untrusted code before limits**. Protective containing ancestor, creation-failure limits and autonomous outer lease must already be established before it. The inner leaf/runtime unit's limit binding and effective readback then precede input load/start. If a mature tool cannot provide a protected release barrier, reject that exact composition; 'paused' metadata or post-launch inspection does not create one.

| Transition / gate | Preconditions and admitted effect | Positive evidence needed | Failure/UNKNOWN transition |
| --- | --- | --- | --- |
| PREPARE -> ADMISSION | Fixed closed profile/capability, supported hard semantics/fault/cost/identity; no side effect | Reviewed subject/dependency/config basis and current independent grant scope | Missing mandatory U01-U04 => refuse before effects; no guessed readiness |
| ADMISSION -> CREATE UNIT | Reserve cumulative finite all-in exposure, persist original create intent and single slot; protected custody; safe containing setup envelope and outer fence autonomously armed | Durable PRE_ADMISSION and fence readiness/identity/maximum receipt before allocation | Lost durable ack/arm uncertainty stops create; any possibly accepted arm/allocation retained UNKNOWN |
| CREATE UNIT -> BIND LIMITS | Only trusted bounded setup in protected envelope, actual original returned refs | UNIT_CREATED Host/boot/cgroup/runtime/resource association | Lost create reply => UNKNOWN, slot consumed, query original; no replacement |
| BIND LIMITS -> VERIFY LIMITS | Inner resource/namespace/FS/network/credential controls installed, no workload instruction | LIMITS_BOUND actual properties and enclosing memberships; independent effective readback | Failure cannot fall back rootless/unbounded/default mode; stop/fence original |
| VERIFY LIMITS -> LOAD INPUT | Exact effective controls, actors/no-change custody, observer readiness, outer deadline still valid | Same-unit required restriction and release-barrier observations | Missing/stale/contradiction => no load/start relying on them; preserve UNKNOWN if effects occurred |
| LOAD INPUT -> START | Bounded immutable inputs/executable/dependency custody/FD-env-workdir graph; then-valid authority/config/deadline/headroom revalidated | WORKLOAD_LOADED plus independently observed byte/input basis, effective limits and safe launch/load proof | Unbound input/loaded image check/use gap => block release; never repair post-effect |
| START -> OBSERVE | Single admitted original start; no hooks or output-selected code | EXECUTION_STARTED native start identity/event; barrier proves untrusted code did not run early | Lost start ack => UNKNOWN for execution/effects; existing hard fence remains |
| OBSERVE -> CANCEL | Owner-valid cancellation/admitted native stop, deadline or observed fault; stop-new-dispatch separately | CANCEL_REQUESTED exact original and bounded operation; acknowledgement separate if obtained | Cancel response loss => UNKNOWN, no create/retry; autonomous deadline unaffected |
| CANCEL/deadline -> FORCE TERMINATE | Original grace expired or mandatory failure; no deadline extension | TERMINATION_INITIATED manager/runtime/outer scoped request | Failure/outage escalates to previously armed outer consequence; no ad-hoc authority widening |
| Completion/termination -> VERIFY CESSATION | Query same original native graph; never infer from stream exit | EXECUTION_CEASED scoped main/guest/VMM fact | No source/ambiguous identity => UNKNOWN; timeout alone cannot prove cessation |
| VERIFY CESSATION -> VERIFY DESCENDANTS | Main cessation plus all helper/child/guest scopes independently observable | DESCENDANTS_CEASED recursive zero-live and graph completeness/no resurrection | Outside/missing helper or stale boot => UNKNOWN; contain/fence, no acceptance |
| VERIFY DESCENDANTS -> RECONCILE EFFECTS | Complete observed cessation prevents new local work; prior effects still may exist | Original artifact/effect/no-effect observations and reserved cost status | Missing effect/usage => UNKNOWN retained; do not delete only recovery evidence |
| RECONCILE EFFECTS -> CLEAN RESOURCES | Preserve decisive original evidence first; authorized exact-resource cleanup under finite survivor envelope | Cleanup intent/refs and known-safe deletion effect, unsettled cost retained | Reconciliation unresolved: may perform separately admitted safety cleanup preserving refs/receipts; UNKNOWN persists, no success |
| CLEAN RESOURCES -> VERIFY CLEANUP | Exact units/mounts/backing/tmp/net/helper/log states queried | RESOURCE_CLEANUP actual absence/release inventory, bounded retained owner outputs and retention facts | Not-found alone/partial remove/timeout => cleanup UNKNOWN; block new attempts |
| VERIFY CLEANUP -> FINALIZE EVIDENCE | Required source-bound final facts complete; gaps explicit; no guest writer | Protected bounded durable final record and external acknowledgment | Partial write/source gap => evidence UNKNOWN; no final acceptance |
| FINALIZE EVIDENCE -> TERMINAL STATE | Task outcome/effect/cleanup/cost facts at their accepted scopes | Validated FINAL_STATE with separate status axes | Known task failure can be recorded alongside UNKNOWN effects/cleanup/cost; never flatten to success |

Creation and loaded-byte assurance are distinct: setup can establish allocation identity; actual loaded subject/dependencies require a protected tool-supported launch/observation composition. OCI create/start is a candidate barrier, not proof alone of that byte property. Do not release arbitrary code just to learn which executable was loaded. Exact supported observation/custody method remains U03.

## 3. State axes, UNKNOWN persistence and recovery

Record separate execution, descendants, resource cleanup, effects, result and billing states; known execution failure does not erase unknown cost. Terminal aggregate KNOWN_SUCCESS requires validated task result and all mandatory positive terminal/resource/effect facts; KNOWN_FAILURE requires known task failure with the relevant consequences recorded. Any required unresolved fact keeps that axis and aggregate acceptance UNKNOWN. A positively observed breach is a failure finding even if other axes remain UNKNOWN. Pre-effect refusal is known no-effect only with supported positive nonacceptance facts.

UNKNOWN is entered on lost allocation/start/cancel replies; unavailable native identity; observer/source/sequence/store loss; material config/authority drift; uncertain boot/time; unobserved helpers/cessation/cleanup; external effect/charge ambiguity. It persists with original logical operation/attempt/unit/Host/boot/grant/config/native refs, unresolved effects, conservative reservation and qualified source gaps. Expiry, lease elapsed, API deletion, absent output, reboot, new process or serialized profile does not clear it.

Recovery: close new admission; read durable original intent; query exact original native refs; invoke only previously admitted native stop/outer fence and bounded authorized cleanup; collect external original-effect/no-effect and cost facts; revalidate current grant/config/qualification before any further effect. No retry/replacement/resume while UNKNOWN. A later retry is a distinct authorized attempt only after accepted original reconciliation, renewed admission and conserved cumulative bound; it cannot hide the same logical operation under a new identity. A process-local trust seal is not restored from a durable ID.

Preserve P7's eleven states independently: CANCEL_REQUESTED, CANCEL_ACKNOWLEDGED, EXECUTION_STOPPING, EXECUTION_CEASED, DESCENDANTS_CEASED, SANDBOX_TERMINATED, PERSISTENT_RESOURCE_STATE_KNOWN, RESOURCE_RELEASED, BILLING_CEASED, RESULT_OBSERVED, EFFECTS_RECONCILED. These are scoped observations, not necessarily a total serial order. Additional conceptual records below do not merge/remove them. Cleanup and settlement can lag known result under a bounded envelope, but cannot be labeled complete without evidence.

Reboot: fresh boot ID closes admission before any workload service starts; never auto-restart/resume/restore expired units. Correlate persisted old attempts and native disk/net/VM refs, quarantine survivors, reconcile/fence then clean authorized resources. A true cold/off observation may establish past compute cessation only at its qualified scope; it does not prove artifact/effect success. Warm/live-update preservation, VM snapshot restore and restart paths are excluded until independently analyzed; changed boot ID alone is not zero-live evidence. No reboot is invoked now.

## 4. Evidence record architecture

Every record conceptually binds execution_unit_id (or reserved planned ID pre-create), attempt_id and original operation, Host identity and boot identity when known, runtime/family/version and native refs, config_hash, workload_hash/dependency_hash, independently issued authority_grant_id, qualification scope/expiry, timestamp with clock basis/error, observation source/scope, sequence, status and explicit omissions. Pre-create actual boot/unit/loaded facts may be UNKNOWN; distinguish planned from observed and bind them before release. Never invent actual-instance identity before creation, and never defer creation's safe envelope until afterward. Each observation authenticates its source; a hash protects bytes only. No credentials or their fingerprints are included.

| Record | Required positive source/content | What it does NOT prove |
| --- | --- | --- |
| PRE_ADMISSION | CONTROLLER_OBSERVED durable current grant/eligibility/reservation/one slot/input/config/creation bound; HOST admission and independent fence readiness | Actual created unit/loaded workload or task authority issued by Nexus |
| UNIT_CREATED | HOST_OBSERVED native unit/boot/resource original mapping and bounded trusted setup | Guest execution started or actual limits applied |
| LIMITS_BOUND | KERNEL/RUNTIME_OBSERVED readbacks via qualified Host observer; actual cgroup/ns/policy/quota/FD/actor scope and deadline basis | Entire loaded-byte graph or physical kill-completion bound |
| WORKLOAD_LOADED | HOST/KERNEL/RUNTIME trusted object/byte/custody observation binding staged subject/dependencies/input; effective release barrier | Guest's own inventory or prelaunch hash proves actual load |
| EXECUTION_STARTED | Native actual start/process/guest operation identity tied to admitted release | Successful/accepted result |
| CANCEL_REQUESTED | CONTROLLER/HOST scoped original stop intent and native operation reference | Acknowledgement/cessation/cleanup |
| TERMINATION_INITIATED | Manager/runtime/outer enforcer request source, reason, original deadline and escalation scope | Kill request means stopped |
| EXECUTION_CEASED | Qualified Host/runtime main/guest/VMM cessation at stated scope; external fence if needed | Complete descendants/outside-helper/resource/effect settlement |
| DESCENDANTS_CEASED | Kernel original subtree zero-live plus full helper/virtual/guest coverage and no resurrection | Backing/mount/net/storage released or external API stopped |
| RESOURCE_CLEANUP | HOST native resource inventory, unmount/backing/net/tmp state, bounded retained outputs/evidence | Billing settlement or absence of prior external effects |
| EFFECT_RECONCILIATION | CONTROLLER validated artifact + EXTERNAL_PROVIDER_OBSERVED original effect/no-effect/usage if applicable; closed excluded graph for fixture | Missing response/no output means no effect |
| FINAL_STATE | Nexus validates complete protected record chain, actual task result and separate execution/descendant/resource/effect/cost axes | Qualified capability, new authority or G2 acceptance |

Evidence custody: guest writes only bounded data channels; Host collector writes separately protected bounded domain records; Controller verifies authenticated source, scope, identity, admitted config, sequence/gaps, expiry and durability, then persists an owner-controlled copy outside target Host fault domain. Native kernel facts are delivered through a qualified Host observation mechanism, not independent kernel certification. Protect immutable final artifacts with validated extraction; bounded temporary finalization plus durable prefix/commit marker distinguish partial from complete. Missing store acknowledgment stops new admission/acceptance. Exact storage atomicity/writer privilege/independence/retention remains U03/U04, not an implemented ledger or receipt service.

## 5. Responsibility/evidence reconciliation

HostAdapter translates only typed transport/native identities and explicit failures, no low-level sandbox policy invention. Host Agent verifies its admission inputs, invokes fixed mature tooling, collects scoped original lifecycle facts and coordinates authorized cleanup. Mature manager/runtime/kernel enforce actual controls; outside-domain fence supplies any separately supported final fault envelope. Nexus Controller owns prior authority/budget/dispatch, qualified binding, observation/artifact/effect adjudication, UNKNOWN and retry refusal. Owner independently issues/accepts scope. No component may claim another layer's unobserved state or infer task grants from a qualification receipt.

Expected future reconciliation proof: one PRE_ADMISSION -> one original allocation/release; every record matches Host/boot/unit/input/config/grant/qualification; no hidden side-effect path; no observation gap converted to success; independently qualified ultimate lifetime covers Controller/Agent/manager loss; cleanup/effects/cost remain separate; unknown attempt consumes slot/exposure. Exact next step remains U01-U04 documentary closure, not code.

Preserved state: G2 HOLD; Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT. Route B unresolved / retained; Route D FEASIBLE FOR FURTHER DESIGN. Accepted A0-A6/P1-P12 and all historical accepted bytes remain unchanged. No installation, Linux provisioning, VM/container creation, Host execution, privileged operations, credentials, paid activity, HostAdapter/Host Agent implementation, architecture acceptance, G3/G4 entry, merge, push, tag or freeze.
