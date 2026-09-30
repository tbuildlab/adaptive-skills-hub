# Nexus G2 Limited Clarifying Amendment P1–P12 Mapping v1

Document ID: `nexus.g2.limited-clarifying-amendment.p1-p12-mapping.v1`

Version: `1.0.0`

Date: 30 September 2026

Status: **PROPOSED NORMATIVE COMPONENT MAPPING — OWNER ACCEPTANCE PENDING; NO PROPERTY PASS; G2 HOLD**

## 1. Reading rule and accepted traceability

This is the normative companion to the proposed [limited amendment](nexus-g2-limited-clarifying-amendment-v1.md) §§3–8. It preserves the [Route B contract](nexus-g2-route-b-provider-neutral-host-contract-v1.md) §4 P1–P12 identifiers and threats, the [Responsibility Re-baseline](nexus-g2-responsibility-rebaseline-review-v1.md) §§3–5 and the accepted [minimization matrix](nexus-g2-openai-first-contract-minimization-matrix-v1.md) §1. No source document or historical finding is changed. Evidence classes are not property scores: a composite row requires every listed mandatory component, not any one convenient class. Experiments have no authority until the amendment §7 safety gate and a separate exact protocol/owner grant are satisfied.

Across all rows, positively observed contradiction/unauthorized effect is **FAIL**; a missing, stale, unavailable, unauthenticated, contradictory-source or unbound mandatory fact is **UNKNOWN/STOP**. Nonapplicability requires demonstrated channel closure, not omitted evidence. PASS is exact-mode/task scoped and never issued by this mapping. Cross-property dependencies are conjunctive; successful P8 or P10 cannot repair a missing P5/P6 bound.

One original attempt means one attempt per admitted logical operation, not one dispatch for the lifetime of G2. Distinct sequential operations require their own then-valid admission and reservation. No ambiguous operation may be disguised as a new operation to evade retry refusal; the current candidate experiment would still need its exact separately authorized creation/dispatch count.

| ID and unchanged contract name | Required component allocation | HQ/property relationship |
| --- | --- | --- |
| P1 Deployment / instance identity | PROVIDER-MANDATORY public unit/operation semantics + NEXUS-OWNED admission/provenance records + COMPOSITE same-operation binding + QUALIFICATION-EXPERIMENT substitution tests | HQ1/HQ5/HQ6 |
| P2 Control/data-plane separation | PROVIDER-MANDATORY denial/actor semantics + NEXUS-OWNED custody/authority + COMPOSITE actor closure + QUALIFICATION-EXPERIMENT escalation negatives | HQ2/HQ3/HQ6 |
| P3 Effective isolation / policy observation | PROVIDER-MANDATORY applied-enforcement/mutation semantics + NEXUS-OWNED config/release controls + COMPOSITE effective binding + QUALIFICATION-EXPERIMENT relevant negatives | HQ2/HQ5/HQ6 |
| P4 Execution input boundary | NEXUS-OWNED admitted channel graph + PROVIDER-MANDATORY reachable-channel enforcement + COMPOSITE closure + QUALIFICATION-EXPERIMENT channel/secret tests | HQ2/HQ3/HQ6 |
| P5 Resource limits | PROVIDER-MANDATORY remote hard limits + NEXUS-OWNED tighter admission + COMPOSITE complete envelope + QUALIFICATION-EXPERIMENT bound/controller-loss tests | HQ4/HQ6 |
| P6 Hard cost boundary | NEXUS-OWNED reservation/admission/accounting + PROVIDER-MANDATORY billing/hard drivers/cutoff + COMPOSITE conservative maximum + QUALIFICATION-EXPERIMENT account/settlement checks | HQ6 |
| P7 Cancellation | PROVIDER-MANDATORY native exact-unit stop/query/ultimate hard termination + NEXUS-OWNED stop-state policy + COMPOSITE reconciliation + QUALIFICATION-EXPERIMENT cessation/fault tests | HQ4/HQ6 |
| P8 Observation | PROVIDER-MANDATORY supported references/observations + NEXUS-OWNED validation/custody + COMPOSITE coverage + QUALIFICATION-EXPERIMENT result/fault tests | HQ5/HQ6 |
| P9 Interruption / unknown effects | NEXUS-OWNED journal/UNKNOWN/retry refusal + COMPOSITE reconciliation using PROVIDER-MANDATORY facts where relied on + QUALIFICATION-EXPERIMENT response-loss tests | HQ4/HQ5/HQ6 |
| P10 Evidence integrity | NEXUS-OWNED protected evidence/adjudication + PROVIDER-MANDATORY source semantics where relied on + COMPOSITE source/scope binding + QUALIFICATION-EXPERIMENT forgery/gap tests | HQ1/HQ5/HQ6 |
| P11 BYOK / credential model | NEXUS-OWNED custody/invalidation + PROVIDER-MANDATORY credential/active-authority semantics where safety depends on them + COMPOSITE account/permission binding + QUALIFICATION-EXPERIMENT non-reachability | HQ2/HQ3/HQ5 |
| P12 Version / capability drift | NEXUS-OWNED expiry/invalidation + PROVIDER-MANDATORY public contract/config identity + COMPOSITE revalidation + QUALIFICATION-EXPERIMENT mismatch tests | HQ1/HQ5/HQ6 |

## 2. P1 Deployment / instance identity

- **Minimum property:** Stable supported public execution-unit and original-operation identity associates admitted inputs/configuration, observations, results and effects without relevant substitution or identity reuse confusion.
- **Nexus may establish:** exact admission/request/input hashes, original-attempt journal, controller and Nexus-controlled code/dependency provenance, result validation, qualification epoch/scope and correlation. It cannot claim unobserved remote bytes from a hash sent in a request.
- **Host/provider must establish:** supported stable unit/operation/result references, their association and observation semantics, and public mode/configuration identity sufficient for the exact threat model. Internal implementation-byte/revision identity is additionally mandatory only if safety cannot be preserved without it; managed internals remain an explicit accepted TCB residual, not observed provenance.
- **Experiment may establish:** same-original-operation input/result association, reference mismatch/substitution rejection, tested artifact linkage and coverage under interruption.
- **Cannot count:** API version alone; name/tag alone; prelaunch hash plus path; guest/model assertion; unbound result; reuse of a different unit after lost creation response.
- **PASS:** trusted same-unit/operation/config/input/result association plus applicable controller/code provenance closes the relevant check/use/substitution gaps at the accepted scope.
- **UNKNOWN/FAIL:** unbound original identity/association or mandatory execution-byte basis is UNKNOWN/STOP; mismatched/substituted execution is FAIL. Hidden provider bytes are not silently marked verified.
- **Requalification trigger:** public mode/config/identity-association change, Nexus-controlled executable/dependency change, material drift, expiry or lost required identity evidence.

## 3. P2 Control/data-plane separation

- **Minimum property:** workload and indirect descendants cannot obtain controller authority, change the control plane or relax mandatory restrictions outside admitted authority; relevant customer mutation actors are closed.
- **Nexus may establish:** protected controller/API custody, least-privilege usage, actor exclusion where permissions make that enforceable, one admitted configuration and immediate invalidation on authority changes. No new secret platform or privileged broker is implied.
- **Host/provider must establish:** actual permission/denial/attenuation semantics, workload/control-plane separation, supported customer/project mutation surfaces and managed-harness authority scope. Distinct API products and exhaustive internal personnel enumeration are not universal requirements; a declared managed-provider TCB is not a wildcard guest authority.
- **Experiment may establish:** denied control/mutation calls, secret non-reachability and exact actor/config binding with subject-external observations.
- **Cannot count:** asking the agent to abstain; controller intention without permission enforcement; broad token inside guest; assuming a dedicated project has no other runtime-capable actor.
- **PASS:** every task-reachable elevation/mutation path is denied or independently admitted with a justified no-change interval, actual custody and exact actor scope.
- **UNKNOWN/FAIL:** unclear mutation/control path or actor exclusion is UNKNOWN/STOP; successful workload escalation, credential exposure or unapproved mutation is FAIL.
- **Requalification trigger:** actor/role/token scope, managed-harness authority, mutation API, custody or applicable configuration change.

## 4. P3 Effective isolation / policy observation

- **Minimum property:** security-relevant restrictions are demonstrably effective and bound to admitted execution/configuration throughout the relevant effect interval.
- **Nexus may establish:** exact immutable admitted request, release sequencing, separately enforced customer-actor exclusion, freshness/revalidation and protected evidence composition.
- **Host/provider must establish:** supported actual enforcement semantics, restriction scope/exceptions and immutability/mutation ordering or equivalent drift-safe release semantics. A direct effective getter/revision or monolithic signed receipt is one mechanism, not mandatory when an equally strong contract/config/external-evidence composition is demonstrated.
- **Experiment may establish:** exact-profile denial behaviors, permitted/forbidden mutation attempts and external observations at justified barriers; finite negatives corroborate scope, not a universal claim about undeclared channels.
- **Cannot count:** requested/stored settings alone; guest firewall/report; stale readback; post-hoc policy observation after an unauthorized effect; network sampling without authoritative scope.
- **PASS:** authoritative enforcement/no-change semantics, actual account/configuration binding and externally observed relevant behavior establish every required restriction over the admitted interval.
- **UNKNOWN/FAIL:** unknown scope, exceptions, freshness or release interval is UNKNOWN/STOP; observed bypass or contradiction of required restriction is FAIL.
- **Requalification trigger:** policy/config/actor/enforcing contract change, missing observation, expiry or violated no-change interval.

## 5. P4 Execution input boundary

- **Minimum property:** all relevant input, secret, transitive-operation and effect channels are explicitly admitted and bounded; no unapproved authority or secret channel remains reachable.
- **Nexus may establish:** finite input/effect graph and exclusions for command/files/env/workdir/mount/IPC/process/network/service/tool/MCP/plugin/model/deferred paths; exact fixtures; validated outputs and capability/authority decisions. Native managed loops remain at the Host, not rebuilt by Nexus.
- **Host/provider must establish:** enforceable restrictions and semantics for customer-reachable channels and applicable provider-internal exceptions. Exact network authorization is task-specific; broad Internet capability is not an exact-host allowlist. Required remote denials cannot be supplied by input omission alone.
- **Experiment may establish:** effective allowed inputs/environment/work paths/relevant handles for that Host, no-secret/escape negatives and controlled task-effect observations from trusted sources.
- **Cannot count:** network-disabled request closing filesystem/IPC/model effects by implication; exhaustive unknown internals replaced with guesses; child-only inventory; tool-disabled prompt instead of supported exclusion.
- **PASS:** justified closed graph, effective restrictions and external negatives cover every task-reachable admitted/prohibited path without owner/control-secret reachability.
- **UNKNOWN/FAIL:** unidentified reachable channel is UNKNOWN/STOP; observed secret/unauthorized-channel reachability or indirect bypass is FAIL.
- **Requalification trigger:** input channel, setup, package, tool/MCP/skill/plugin, model/harness configuration, capability, secret, network or effect graph change.

## 6. P5 Resource limits

- **Minimum property:** every reachable safety/billing-relevant resource and descendant/background exposure has finite non-workload-relaxable bounds, including active lifetime and controller loss.
- **Nexus may establish:** tighter admitted limits, one original creation/dispatch, sequential reservations, bounded admitted input/output handling and refusal of extensions. Qualified application controls may cover only dimensions they actually enforce; controller-loss behavior must be bounded independently.
- **Host/provider must establish:** hard remote CPU/memory/storage/process/concurrency/output and active-lifetime/descendant bounds where the controller cannot enforce the unit. Explicit closed nonapplicable channels or equally strong qualified controls may remove a knob requirement; they do not remove the property. Ultimate remote termination must cover ongoing activity/keep-alives/controller loss.
- **Experiment may establish:** exact-profile limit/failure behavior, descendants, controller-loss cleanup and external terminal/zero-live observation under an already established hard envelope.
- **Cannot count:** size allocation or plan maximum alone; client timeout; controller death; prompt to stop; a cap measured once; financial cutoff that stops charging but permits unbounded dangerous work.
- **PASS:** all applicable dimensions and reset/extension/background paths form an enforceable finite whole-unit envelope with actual binding and tested failure consequences.
- **UNKNOWN/FAIL:** unbounded or undocumented necessary hard dimension/controller-loss consequence is UNKNOWN/STOP; overrun, escape or relaxation beyond admitted bound is FAIL.
- **Requalification trigger:** resources, lifetime/reset rules, descendants/delegation/concurrency, enforcing layer or controller-loss/fallback change.

## 7. P6 Hard cost boundary

- **Minimum property:** a conservative finite pre-dispatch maximum for all billable dimensions fits the remaining cumulative owner ceiling, including ambiguous calls, internal retries, retained objects, overshoot and tail.
- **Nexus may establish:** then-valid authority, rates/account/headroom binding, worst-case arithmetic, reservation/admission, one-attempt/no-retry policy, durable uncertain exposure and later settlement/release. Unrelated native Host use remains outside the Nexus ledger but shared account actors must be accounted for where they can consume or defeat relied-on headroom/caps.
- **Host/provider must establish:** complete applicable billing dimensions/minimums/current rate basis and enforced finite drivers or hard monetary cutoff with bounded lag/overshoot/residual accrual. Remote managed-loop/model/token/tool/retry and active/idle/cleanup bounds are mandatory where billed. A dedicated per-operation money API is optional; finite conservative composition is not.
- **Experiment may establish:** fresh status-only account/plan/rate/cap/actor evidence and pre/post usage/settlement behavior within the predetermined maximum. Accounting lag stays UNKNOWN, not zero.
- **Cannot count:** ledger reservation bounding provider charges; price example/rate table alone; balance/credit/soft alert; finite sampled invoice; controller request count bounding provider-internal retries or loop steps.
- **PASS:** every admitted billable driver is hard-bounded and conservatively priced, including worst-case failure/tail, within actual remaining authority; outstanding versus settled cost remains explicit. Delayed usage cannot release reservation without accepted settlement evidence.
- **UNKNOWN/FAIL:** missing dimension, unbounded multiplier/tail or current headroom is UNKNOWN/STOP before creation; charges beyond admitted bound or unauthorized extension is FAIL. Reconciliation state may remain UNKNOWN under safe refusal; it is not settled cost PASS.
- **Requalification trigger:** price/plan/account/shared-actor/billing/cutoff/overshoot, model/tool/runtime bounds, retained resource or settlement rules change.

## 8. P7 Cancellation

- **Minimum property:** stop-new-dispatch and native exact-unit cancellation are supported; a provider-enforced ultimate termination boundary contains work even if cancellation/controller communication fails; actual cessation and cleanup are observable to the required scope.
- **Nexus may establish:** ordered request/ack/terminal/cleanup/reconciliation/settlement states, exact original references, stopping new dispatch, protected unresolved effects/exposure and bounded cancel attempts without recreating the unit.
- **Host/provider must establish:** native cancel/terminate and query semantics plus non-workload-relaxable whole-unit/descendant ultimate termination independent of client progress. A cancellation API alone cannot make an experiment safe.
- **Experiment may establish:** exact-mode latency/cessation/descendant and controller-loss behavior, lost-ack/delayed-result cases, cleanup/effect observations and whether the predeclared acceptance bound is met.
- **Cannot count:** cancel acknowledgement, terminal turn label alone where work may persist, stream close, local deadline, session deletion, no logs or API not-found as proof of physical cleanup.
- **PASS:** each predeclared failure case reaches externally bound terminal/required zero-live/cleanup outcomes within accepted bounds; late effects and cost are reconciled separately.
- **UNKNOWN/FAIL:** missing fallback or decisive cessation/cleanup observation is UNKNOWN/STOP; live prohibited work beyond bound, escape or false terminal claim is FAIL. If physical cleanup is unobservable, retain UNKNOWN even when accrual is bounded.
- **Requalification trigger:** cancellation/termination/query/lifetime semantics, descendant graph, cleanup coverage or failure envelope changes.

## 9. P8 Observation

- **Minimum property:** trustworthy stable terminal/result/failure/task-effect observations bind the admitted original operation sufficiently for acceptance or explicit bounded UNKNOWN handling.
- **Nexus may establish:** protected observation collection, artifact/effect validation, ordered gaps, task-specific coverage and reconciliation-before-delete. Universal transcripts and indefinite retention are not required.
- **Host/provider must establish:** supported external unit/operation/result references and observations, authenticity/retention/expiry and relevant failure/cleanup meanings where relied on. Safety-critical observations needed to conduct a test cannot be deferred to post-test discovery.
- **Experiment may establish:** exact task event/result/artifact/failure/retention coverage, disconnect/reconnect/late observation behavior and known gaps under the safe envelope.
- **Cannot count:** exit/completed status as task acceptance; guest output as control-state proof; missing item/artifact/log as no effect; unbound trace or webhook.
- **PASS:** all task acceptance/required terminal facts have validated positive source-bound observations; gaps are explicit and cannot yield false success or unsafe retry. Tested refusal under missing facts is not a useful positive workflow by itself.
- **UNKNOWN/FAIL:** missing mandatory result/effect/terminal fact is UNKNOWN/STOP; false attribution or uncovered unauthorized effect is FAIL.
- **Requalification trigger:** record format/source, identity linkage, coverage/retention, observable channels, task or terminal semantics change.

## 10. P9 Interruption / unknown effects

- **Minimum property:** durable original-attempt identity/exposure and UNKNOWN persistence prevent duplicate/unsafe effects during recovery; safe loss of availability is permitted.
- **Nexus may establish:** protected pre-effect intent/admission, one original create/input attempt, checkpointed ordered domain facts, positive reconciliation-before-retry/delete where needed and permanent retry refusal when facts disappear. Recovery revalidates current authority/configuration/budget; serialized IDs/profiles do not restore process-local trust seals.
- **Host/provider must establish:** supported observations/reconnect facts where relied on for positive reconciliation; meanings of not-found/expired/deleted where used. No universal idempotency API or permanent post-delete history is mandatory when ambiguous operations are never retried and their effects/exposure are already bounded.
- **Experiment may establish:** lost create/dispatch/result/cancel/controller-response behavior, original-only query, validation of completed/no-effect facts and durable UNKNOWN/no-replacement paths.
- **Cannot count:** Nexus journal proving remote exactly-once/no effect; API absence interpreted as NOT STARTED; replay to discover whether the first attempt ran; cleanup deleting outstanding accounting facts.
- **PASS:** every tested interruption produces source-bound reconciliation or durable bounded UNKNOWN/STOP with no unsafe retry/replacement and preserved reservation; this qualifies safety handling, not success of an unresolved task.
- **UNKNOWN/FAIL:** original effects may remain UNKNOWN indefinitely and further dispatch stays stopped; unbounded/unreconcilable external effects disqualify the experiment. Erasure, replacement or blind retry is FAIL.
- **Requalification trigger:** submission/retry/query semantics, effect graph, journal/custody/retention, recovery or identity handling change.

## 11. P10 Evidence integrity

- **Minimum property:** provenance, scope, time/config/unit/operation binding and workload-resistant custody protect decisive evidence against forgery, replay, omissions and false PASS.
- **Nexus may establish:** protected controller bundle, admitted request/input identity, original references, source-authenticated collection, ordering/gap/coverage records, cross-check and deterministic adjudication. One monolithic provider security receipt is not mandatory.
- **Host/provider must establish:** authenticity/source/schema/scope of observations relied on, their identity association and freshness/retention. External provider telemetry is not independent certification of provider internals; the declared provider TCB remains explicit.
- **Experiment may establish:** forged/replayed/stale/partial/conflicting records are rejected, workload cannot modify custody, and actual observation coverage matches the protocol.
- **Cannot count:** receipt bytes/hashes as owner grant or runtime enforcement; guest/model-signed self-certification; a protected copy making untrusted content true; trace completeness inferred from export availability.
- **PASS:** every decisive property has trustworthy scoped observations protected and bound to the same admitted attempt; missing/contradictory facts are deterministically rejected.
- **UNKNOWN/FAIL:** unauthenticated or incomplete decisive coverage is UNKNOWN/STOP; writable/forged accepted evidence or mismatch is FAIL.
- **Requalification trigger:** controller/evidence writer/ACL/custody, authentication/source/schema, replay/ordering/time basis or mandatory coverage change.

## 12. P11 BYOK / credential model

- **Minimum property:** owner-controlled account/authority/billing, no bundled Nexus developer key, least-privilege controller custody and no control/API credential in workload; affected authority changes invalidate grants/evidence immediately.
- **Nexus may establish:** safe status-only account/actor binding, protected credential use, no secret/token values or hashes in evidence, compute versus optional model-key separation, current grant checks and no new dispatch after revocation/rotation.
- **Host/provider must establish:** credential/permission and active-authority semantics to the extent they affect safe admitted work. If revocation is relied on to attenuate an active path, that behavior must be established before use. Detailed propagation may be deferred only when no security premise relies on it and independent P5/P7 bounds contain existing work; revocation is never assumed to terminate compute.
- **Experiment may establish:** actual custody/non-reachability and changed-authority invalidation using a separately authorized safe method. No credential disclosure or destructive control-plane test follows from this document.
- **Cannot count:** secret omission from one env field as whole-path isolation; revoked key as cessation; dashboard identity alone as SDK/control binding; opaque token fingerprint as proof of safe custody.
- **PASS:** actual required account/scopes/custody bind the controller, workload cannot reach control secrets and all relied-on active authority semantics plus immediate Nexus invalidation are proven.
- **UNKNOWN/FAIL:** mandatory credential reachability/scope/active permission unknown is UNKNOWN/STOP; exposed secret or surviving forbidden authority is FAIL.
- **Requalification trigger:** credential actor/scope/custody/role/rotation/revocation or account/model-provider authority change.

## 13. P12 Version / capability drift

- **Minimum property:** qualification binds sufficiently stable supported public mode/config/operation/evidence identity with limited reuse; observable material drift/expiry/authority or contract change invalidates before dispatch.
- **Nexus may establish:** exact qualification record, short explicit expiry, public config/version comparison, mandatory observation checks and periodic requalification; required current authority is separately revalidated on resume.
- **Host/provider must establish:** supported public contract/config identity and relevant change semantics sufficient to preserve the actual property. Inaccessible internal revision or push notification is not universally mandatory; it becomes mandatory if no accepted public-contract/composite path can preserve safety without it.
- **Experiment may establish:** mismatch/expiry/missing-fact/changed-authority rejection and supported configuration revalidation for the same exact mode.
- **Cannot count:** API generation proving unchanged implementation; short expiry proving invisible drift absent; `latest`/dashboard label proving exact identity; periodic tests guaranteeing continuous undocumented behavior.
- **PASS:** current exact public identity/config, fresh accepted component evidence, bounded qualification reuse and deterministic invalidation satisfy the explicit managed-service trust model. Hidden drift remains recorded residual provider trust, not semantic knowledge.
- **UNKNOWN/FAIL:** unsupported or incompatible public contract, missing mandatory identity/change evidence or expired binding is UNKNOWN/STOP; ignored known material drift or falsely claimed stability is FAIL.
- **Requalification trigger:** any material public contract/API/mode/model/Host/capability/config change, current authority change, expiry, contradictory/missing observation or later authoritative evidence invalidating a relied-on premise.

## 14. Preserved status

No row is deleted, renumbered or passed. HQ1–HQ4 remain delegable only with Nexus verification/binding; HQ5–HQ6 remain Nexus-owned. A0–A6 and frozen G1/R2/R4/R5 remain unchanged. The local Windows/LPAC binding stays exited; E2B/Modal/Daytona findings stay historical. OpenAI **SUPPORTED 0 / PARTIAL 11**, P7 **NOT PASS**; Scenario 01–04 **NOT RUN**; HQ1–HQ5 **NOT PASS**; HQ6 **NOT STARTED**; Positive Host Binding **ABSENT**; G2 **HOLD**. No implementation, outreach, credential, provider effect or experiment authority is granted.
