# Nexus G2 Next Host Route Decision v1

Decision ID: `nexus.g2.next-host-route.v1`

Version: `1.0.0`

Date: 28 September 2026

Status: **PROPOSED DOCUMENTARY ROUTE COMPARISON — NO HOST SELECTED OR QUALIFIED — NO IMPLEMENTATION OR EXPERIMENT AUTHORITY**

## 1. Conclusion and scope

Three route families remain conditional technical candidates: **A**, another supported Windows environment; **B**, a provider-backed isolated Host with an independently controlled execution plane; **C**, an existing supported Linux isolation environment. None currently has sufficient instance-bound evidence for HQ1–HQ6 or eligibility for execution. No particular Windows build, E2B account or Linux runtime is selected. A route family being plausible is not proof that an available deployment can satisfy it.

Use a finite first screen, not a new qualification project by default. If the owner already has a different supported Windows environment, A is the smallest initial evidence screen and offers the most implementation reuse; do not buy, install or downgrade an environment on this basis. If none is identified, B is the strongest recorded interface-level alternative, with E2B one candidate rather than a required vendor. C remains conditional and has the greatest new evidence burden; the blocked F2 mode is not a shortcut. Each screen must close the decisive prerequisite using existing supported evidence or return STOP, without repeated searches or new infrastructure.

The [current LPAC exit](nexus-pre-g2-current-lpac-host-exit-decision-v1.md) and its separate [adversarial review](nexus-pre-g2-current-lpac-host-exit-review-v1.md) precede this comparison. Current binding: Windows `26200.9550`, mask `0xF405`, unresolved `0xC000`, sealed V4 manifest `2B907CD25868124C244E6C350EA13CFFCC041562EA0E9AD479197F6B83D3D3C4`; CI UNKNOWN/STOP. Repository starting HEAD `45407f501d4225e06105f0eafc6b010d516ed66e`, branch `nexus-v2-g2-development`.

This document creates no Host or launcher design. It specifies evidence obligations and bounded future experiments only. No provider/API/support contact, credential use, installation, VM/service/driver creation, Windows security change, package release, HQ6 execution or G2 implementation is authorized. Public Microsoft/Linux documentation supports candidate primitive claims; provider facts below come only from preserved dated evidence, not new provider contact or current account verification.

## 2. Invariant requirements and reuse boundary

The accepted [Scope & Exit](nexus-g2-host-qualification-scope-and-exit-decision-v1.md) §§2–3/9 and [acceptance](nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md) require equivalent HQ1–HQ5 within another Host's actual boundary, not emulation of LPAC-specific APIs or the same four Windows cases. HQ6 then proves one actual accepted capability's pre-effect authority, resource/budget, cancellation, effect observation, checkpoint/recovery references and unknown-effect reconciliation primitives. G2 owns its later ledger and domain recovery; these experiments must not implement them.

Default deny, no implicit authority escalation, no password transfer, no control secrets to untrusted execution, controlled transitive inputs, independent evidence, bounded cancellation and unresolved-effect preservation remain mandatory. Unknown cost is not zero. Timeout, local process termination, idle state and clean exit are not remote cancellation, settled spending or authorization to replay. No runtime, inherited grants, forbidden fallback, parallel delegation or broad command surface follows from a candidate profile.

| Existing asset | Classification and permitted future use |
| --- | --- |
| A0–A6, Roadmap G2, G1 eligibility/conformance and budget/effect vocabulary | **REUSABLE** requirements; profile records grant no execution authority |
| Finite HQ1–HQ6 threat matrix, negative-test objectives and explicit UNKNOWN/STOP | **REUSABLE** security/exit requirements across routes |
| Custody/actual-load/receipt ordering and controller-loss/deadline/cleanup objectives | **REUSABLE** concepts; not transferable test PASS |
| Windows verifier/controller/watchdog/recovery/probe/canary source and four-case logic | **ADAPTABLE** for A after fresh platform review/pins; limited requirements/fixture concepts for B/C, not Windows execution code |
| Same-process observation, process-tree ownership, environment/handle evidence mechanisms | **ADAPTABLE** only where the target OS/Host supplies a supported equivalent |
| Windows PE/PDB/module pins, compiled executables, package/profile SIDs, ACL/file IDs, Job/CI/PSS observations and hard-coded paths | **HOST-SPECIFIC / NOT REUSABLE** as proof on a new binding; repinning or new delivery needs separate authority |
| E2B auth-domain analysis, configuration and account/cost checklists | **ADAPTABLE** for B; all deployed-version/account/actor/cost facts must be fresh |
| F2 workload/seccomp/privilege analyses | **ADAPTABLE** as known blockers and threat questions; not permission or positive Linux proof |
| Sealed V4, prior packages, all blocked attempts and build/diagnostic records | Preserve unchanged; historical evidence, never a new release packet |
| Frozen R2 planning, R4 Presentations handoff and R5 advisory inventory | **REUSABLE** at their frozen scopes; **NOT REUSABLE** as a complete generic G2 Host executor |

R2 is planning-only; R4 supports its reviewed Presentations mapping; R5 adds advisory selection and bounded Host handoff evidence. Their successful handoff/receipt behavior does not independently provide mandatory hard resource/money limits, complete transitive admission or ambiguous-effect reconciliation for G2. No materially simpler complete Host binding is established by these integrations. Their interfaces remain unchanged.

## 3. Candidate evidence, not vendor selection

| Candidate | Repository evidence and bounded disposition |
| --- | --- |
| A — another supported Windows environment/build | The accepted LPAC implementation and finite protocol exist, but no alternate environment or its CI/admission state was verified here. **CONDITIONAL TECHNICAL CANDIDATE**, not an assertion that a chosen build omits unknown bits or admits these binaries. |
| B — E2B hosted restricted execution | Preserved 2026-09-24 screen identifies separate envd data-plane token and team/bearer control-plane auth domains. envd is not exec-only; exact deployment permissions, actors, effective policy, complete inputs and budget/cancellation remain unproved. G0 Attempt 04 stopped locally with zero creation attempts and zero untrusted execution across Attempts 01–04. **CONDITIONAL TECHNICAL CANDIDATE**; no account/resource/auth state is refreshed and no former authorization transfers. |
| B — recorded Modal Starter binding | Recorded mutation-authority closure concluded `MODAL_MUTATION_AUTHORITY_NOT_CLOSED`. **INELIGIBLE WITH RECORDED INTERFACE/ARCHITECTURE**; do not restart without a concrete new native authority/evidence capability and review. This is not a rejection of all Modal products. |
| B — recorded Daytona hosted-container binding | Preserved owner-supplied provider reply says no live effective restriction readback or revision-bound command execution. **INELIGIBLE WITH RECORDED EVIDENCE CONTRACT**; mode/source limitations remain in the preserved adjudication. Future materially different interfaces require new evidence, not automatic rejection or admission. |
| B — equivalent isolated VM/container provider | No exact alternative mode or deployed interface was qualified. **UNIDENTIFIED CANDIDATE**, not an invitation to survey indefinitely; one named mode must first supply the proof interfaces below. VM/container marketing and stored configuration are insufficient. |
| C — existing supported Linux isolation stack | Kernel documents expose candidate isolation/resource/lifecycle primitives; no installed environment, privileges, policy application or subject-external observation composition is established here. **CONDITIONAL TECHNICAL CANDIDATE REQUIRING ROUTE-SPECIFIC EVIDENCE REVIEW**. |
| C — preserved F2 seccomp-inspection mode | Recorded effective-stack identity remains UNKNOWN; direct dumping introduces initial-namespace CAP_SYS_ADMIN and ptrace authority with unresolved lifecycle/anti-tamper. **INELIGIBLE AS RECORDED**. Seccomp mode/count or a nested namespace cannot silently satisfy that accepted exact-stack gate. |

These dispositions are dated documentary assessments. Current provider plans, quotas, keys, credits, billing limits and deployments are UNKNOWN. E2B has the strongest concrete recorded auth split among the inspected provider modes, not a proved full Host boundary and not an exclusive Nexus dependency.

## 4. HQ1–HQ6 proof comparison

Every row needs a finite supported source and actual subject/operation binding. Requested settings, a child statement, hashes alone and static tests cannot PASS runtime criteria.

| Property | A — different Windows | B — provider-backed isolation | C — supported Linux isolation |
| --- | --- | --- | --- |
| HQ1 identity/provenance | Fresh owner/token/build/CI anchors; protected exact component bytes and actual same-process main/dependency loads; repin the target, preserve check/create stability. | Exact trusted-controller custody plus provider session/Sandbox/image/build identity and actual admitted execution/dependency evidence. Image tags/digests and guest self-report alone do not prove actual loads. | Protected fixed executable/input objects, host/kernel/runtime versions and independent same-process executable/dependency identity before effects; full actual closure rather than container tag alone. |
| HQ2 effective isolation | Real LPAC token/capabilities and owner-resource/CredMan/file/process/no-network negatives on the new host. | Real provider isolation boundary, credentials/control-mutation exclusion, read/mount/network/metadata/service graph and descendants, observed before untrusted release. | Verified namespaces/UID/capabilities/filesystem/network/IPC scope and escape/owner-resource negatives. Seccomp alone is not a sandbox. |
| HQ3 controlled inputs | Independently observed fresh environment, effective TEMP/TMP/workdir, handles and injection window on the same process. | Empty allowed guest secrets/mounts/env, bounded command/filesystem data plane and credential-free untrusted subject; inventory all reachable inputs including network and side services. | Explicit environment/work/TEMP, descriptor and IPC/mount inputs, no inherited authority or writable policy/runner; independently observe effective restrictions. |
| HQ4 cancel/failure/recovery | Reprove no outer Job, before-execution containment, ready watchdog, crash/stall/deadline, recovery and zero-live tree. | Exact-ID lifetime cap, cancellation acknowledgment and eventual live-state/descendant/effect reconciliation; controller loss and uncertain API outcomes remain bounded, not inferred from local timeout. | Existing whole-tree lifecycle/limits under controller custody before release, deadline/failure intervention, descendants and independently verified zero-live cleanup. A process group alone cannot establish escape-resistant containment. |
| HQ5 evidence integrity | Protected current receipts bind case/process/package/time; original forged/stale/partial-record negatives. | Trusted controller/provider evidence with account/instance/call/effect/config/time binding, protected secret-free durable records and explicit source coverage; guest reports corroborate only. | Controller/OS records external to untrusted execution, stable process/namespace/cgroup/object binding, protected receipts and fail-closed stale/partial evidence. |
| HQ6 real capability/effect binding | Still separate: one G1-accepted capability, closed operation graph, hard relevant resources/budgets, native observations/cancel and effect/artifact IDs. LPAC alone supplies none of the remote properties. | Actual supported execution/capability plus native hard resource/exposure boundaries, usage/effect query and ambiguity-safe retry references. Team account, local reservation or kill response alone is insufficient. | One existing accepted local capability within the entire confined unit, finite filesystem effects, kernel-enforced resources and stable artifact/effect references; external/model calls, if any, need their own money/cancel/reconciliation controls. |

For B, a separately controlled trusted launcher/control plane must have its own accepted custody, identity and observation basis. It cannot rely on the stopped V4 LPAC qualification or an unverified local controller. Claiming that current Windows CI ceases to matter for the same already-promised controller guarantees is an architecture change, not relocation of the guest. A concrete control-plane ownership/evidence successor is required wherever existing accepted promises change. No control key is released to the guest or token-only executor.

For C, namespaces, Landlock and cgroups are candidate primitives, not an accepted stack here. Required rights must be fully supported by the actual kernel and enforced before untrusted execution; do not adopt documentation's best-effort degradation for a mandatory Nexus restriction. Landlock is not an exact-host network allowlist. Existing valid cgroup delegation must be available; creating a privileged broker, granting root/CAP_SYS_ADMIN or changing system policy is not an approved way to rescue a failed screen. Exact-seccomp-stack inspection under the old F2 gate remains blocked unless a separate accepted evidence contract resolves it.

## 5. Practical constraints and trade-offs

| Criterion | A | B | C |
| --- | --- | --- | --- |
| Authoritative evidence | Mature Windows interfaces; exact CI semantics, source coverage and normal-path admission still must be obtainable | Recorded official interface analysis offers concrete auth split; current deployed behavior and live restriction evidence still missing | Published kernel contracts; exact ABI, policy-install/release observation and delegated controller availability are environment-specific |
| Privilege/admin requirement | Preserve non-elevated qualification; no elevation or policy changes to achieve admission | Guest must lack control authority; administrative account setup is not implied; provider TCB and controller ownership require review | Existing unprivileged-supported restrictions/delegation preferred; root-only setup or observation is a separate trust decision, not assumed |
| Credentials | Synthetic local qualification needs none; later remote/BYOK work separate | Protected account control credential required later; scoped data-plane token remains secret; no chat/evidence transfer | Local synthetic qualification needs none; remote access or model/provider keys remain separate |
| Owner interaction | Identify an existing environment; review new pins/package and separately authorize ordinary launch | Select an exact mode, approve account/cost preflight and separately authorize bounded setup; no inherited payment authority | Identify existing host/runner/delegation; review successor protocol and separately authorize a fixed experiment |
| Implementation complexity | Lowest adaptation if existing code/observers work unchanged semantically; new version-specific problems may stop it | Narrow adapter may be small, but controller trust and policy/effect/cost interfaces dominate; no generic runtime | Greatest adaptation: Windows observers/binaries cannot be carried over; use mature primitives without building an isolation platform |
| Qualification complexity | Existing finite local cases plus separate HQ6; no automatic reuse of runtime claims | Provider/version-specific controls and actors, real remote negatives, lifetime/cost and late-effect checks | New equivalent HQ1–HQ5 cases plus capability binding; avoid inheriting F2's unclosed privileged-inspection problem |
| Portability | Windows-specific implementation; governance contracts portable | Provider-specific adapter with portable admission/evidence vocabulary; optional provider, not architectural lock-in | Linux/version/delegation-specific implementation; governance contracts portable |
| BYOK compatibility | Model credentials remain owner-controlled and outside LPAC; compute boundary is distinct from model choice | Provider compute credential is distinct from BYOK model credential; no mandatory vendor/model coupling or guest key injection | Same separation; local capability does not require a model call to demonstrate a binding |
| Cost | No live compute charge in this task; alternate hardware/maintenance/acquisition cost unverified | Current prices, credits, hard stop, all billable dimensions and cumulative headroom UNKNOWN; RM5 historical cumulative ceiling is no new spending authority | Existing hardware may avoid a new compute invoice, but provisioning/maintenance and any external calls are unpriced and unauthorized |
| Checkpoint/recovery | Process/artifact references may support G2; durable domain ledger still later | Native instance/call/effect references and retained late effects are essential; provider reconnect is not task recovery | Stable artifacts/effect observation and contained process references needed; PID alone cannot restore grants or accept artifacts |
| Reconciliation | Local cleanup and separately bounded effects; no remote-cost inference | Termination, TTL, resource state, usage lag and remote side effects require distinct evidence | Local filesystem/process effects can be finite; external effects do not disappear because the local tree died |
| Open-ended loop risk | High if the same CI issue recurs; stop at first unresolvable mandatory preflight fact | High if live policy/cost/actor proof is unavailable; reject that exact mode rather than build a broker | Highest if workload/filter identity or privileged observer closure is missing; do not extend Linux internals research to rescue it |

Cost must include compute, storage/snapshot/egress and model/API charges where applicable, including ambiguous create/termination and accounting lag. Before any future paid effect verify actual terms and enforceable worst-case exposure against the remaining owner-approved cumulative ceiling. No credit balance, exchange rate, account hard cap or zero total exposure is asserted now.

## 6. Smallest future experiment for each conditional route

These are proposed experiments, **not executable instructions or present authorization**. Stop after the named decisive screen; advance only with separately accepted protocol/package and owner authority. No credentials are read or resources created during this decision.

### A — one existing alternate Windows binding

**First screen:** on one owner-identified supported environment, obtain read-only non-elevated identity/elevation/outer-Job/OS and effective CI evidence through an approved status-only collector. Do not transfer sealed V4, use old pins, install an OS or downgrade security. Bind exact source/build/time; recheck every known required/prohibited state and unresolved relevant flags. Screen result is evidence eligibility only, not local qualification.

**Advance criterion:** required state is positively established with no relevant unclassified/contradictory status, supported observation APIs and no new privilege/trust dependency. Review new exact code/dependency/delivery pins and normal-path admissibility before separately authorizing the finite local experiment. Admission and all runtime outcomes remain UNKNOWN until that experiment.

**Stop criterion:** unavailable environment, same unresolved CI problem, refused mandatory observation, unaccepted elevation/policy/signing/broker change, or unavailable code/containment evidence. Do not search successive Windows builds or procure a machine to force PASS. Even local HQ1–HQ5 success would require a separate finite HQ6 binding experiment.

### B — one named provider mode with a native authority split

**First screen:** bind one exact supported mode and its proposed trusted-controller environment. Map control/data-plane operations, all mutation actors, instance/image/configuration identity, effective restriction observation, hard lifetime/resource/money bounds and effect/usage/cancel query interfaces. Start with preserved released-interface evidence; a current authenticated account readback would require new owner authority. No guest, account charge or control token is assumed at this stage.

**Advance criterion:** every required proof has an available supported source and the subject cannot mutate control policy or receive broad credentials. Then propose one separately authorized temporary trusted setup, with at most one creation attempt, fixed synthetic input, exact-ID binding, bounded operations, hard exposure headroom and cleanup/reconciliation. E2B token-only usability, deployed auth denials and complete guest input/network state must be demonstrated, not inferred from source main. Future negative tests must avoid destructive control-plane effects and secret retrieval.

**Stop criterion:** missing current deployed-source binding, unresolved concurrent policy actors, only stored configuration/guest-only firewall evidence, incomplete credential separation, unsupported effect/usage query, unknown mandatory hard limit or ambiguous create. Reconcile the original identity; never create a replacement. Local timeout is not proof of remote cancellation or settled cost. No provider-wide engineering/support loop or custom control broker is proposed.

This route may qualify equivalent HQ1–HQ5 directly at its actual execution boundary under a separately accepted protocol; it need not earn Windows LPAC PASS first. That flexibility does not erase trusted-controller proof obligations or allow reuse of old NexusTest/LPAC G0/G1 authority.

### C — one existing Linux host and mature fixed execution boundary

**First screen:** identify one already available supported OS/kernel/runner, actual supported isolation rights, observer coverage and valid cgroup/resource-controller delegation. Define the fixed workload/dependency identity and enumerate filesystem/network/IPC/descriptor/transitive inputs. Check whether the existing supported mechanisms can independently bind applied policy and complete-tree ownership before release, without a privileged dumper or new service. This is a proposed finite readiness inventory, not permission to run a workload or modify delegation.

**Advance criterion:** every mandatory restriction and observation has a concrete supported source; the controller can impose unmodifiable bounds and independently reconcile tree/artifact effects. A separately reviewed Linux evidence protocol must preserve HQ1–HQ6 and explicitly resolve any changed F2/Windows evidence promises. Only then propose one secret-free fixed-subject isolation/containment/failure experiment with bounded outputs and cleanup. Do not port the Windows C++ qualification harness or implement a generic Linux executor.

**Stop criterion:** optional/best-effort security feature, incomplete applied-policy evidence, no delegated hard resources/tree termination, uncontrolled read/descriptor/mount path, workload identity still unfrozen, or a need for root/CAP_SYS_ADMIN/ptrace broker expansion. Current F2 evidence triggers STOP already; merely using Landlock or cgroup terminology cannot resolve it.

## 7. Route-selection and architecture consequence

There is **no unconditional recommendation to abandon Windows or choose E2B**. Prefer A's first screen only if an alternate supported environment already exists and can expose all prerequisites. Otherwise review B's single concrete mode and control-plane proof first; E2B merits that documentary comparison because of its recorded native auth-domain split, not because of sunk work. C is a legitimate fallback only if an existing mature environment supplies the decisive policy/resource/observation primitive; it is not permission to resume F2 or create custom infrastructure.

Before selecting a concrete route, require: an actual available environment; named authoritative/runtime proof sources for every HQ row; a bounded owner/privilege/credential/cost model; one falsifiable first screen and explicit STOP; and a reviewed successor for any changed Host-specific promise. A missing primitive is reported once as the exact unavailable binding, not converted into a plan to recreate the Host. No numeric scoring or speculative time/cost estimate is used.

A0–A6 and G2 security properties do not change. A can reuse the current architecture only where its exact owner/path/OS/package evidence contract is respected; changed pins or paths require existing versioned governance. B/C need their own versioned Host evidence protocol and explicit bounded amendments to any superseded LPAC-specific ownership, observer, system-TCB or credential rules. This document does not supersede those rules. The current trusted-launch Option D and Option A HOLD remain unchanged; no NexusTest/password/service fallback is reopened.

No route qualifies a generic agent runtime. Qualification needs one existing accepted capability and a closed effect graph; if none is available with the necessary supported primitives, report an unsupported binding and retain G2 HOLD. Qualification completion, later G2 implementation authority and G2 acceptance remain separate decisions.

## 8. Sources, freshness and documentary review

Repository references: [Roadmap](nexus-roadmap-v2.md) G2, [G1](nexus-v2-g1.md), [A0–A6](nexus-pre-g2-architecture-addendum-v1.md), [Scope & Exit](nexus-g2-host-qualification-scope-and-exit-decision-v1.md)/[acceptance](nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md), [CI evidence amendment](nexus-pre-g2-lpac-code-integrity-evidence-amendment-v1.md)/[acceptance](nexus-pre-g2-lpac-code-integrity-evidence-acceptance-v1.md), [R2](nexus-runtime-r2-mcp-architecture.md), [R4](nexus-runtime-r4-host-handoff.md), [R5](nexus-runtime-r5-host-capability-inventory.md), and the accepted [LPAC architecture alternative](nexus-pre-g2-appcontainer-architecture-alternative-v1.md) and [E2B protocol successor](nexus-e2b-appcontainer-protocol-successor-proposal-v1.md) through their [acceptance record](nexus-pre-g2-appcontainer-architecture-acceptance-v1.md).

External evidence root: `D:\chatgpt\安装skills\output\nexus-g2-feasibility-2026-09-16`. Sources inspected within it:

- `E2B-MUTATION-AUTHORITY-SCREEN-2026-09-24\09-decision.md`.
- `E2B-RESTRICTED-EXECUTOR-QUALIFICATION-PROTOCOL-2026-09-24\04-capability-matrix.md`, `06-configuration-binding.md`, `11-resource-cost-bounds.md`.
- `E2B-G0-TRUSTED-SANDBOX-QUALIFICATION-2026-09-24\ATTEMPT-04-HOST-ISOLATION-2026-09-24\01-host-isolation.md`, `03-lifecycle-disposition.md`.
- `MODAL-MUTATION-AUTHORITY-CLOSURE-DECISION-2026-09-24\11-decision.md`.
- `DAYTONA-PROVIDER-RESPONSE-ADJUDICATION-2026-09-23\05-provider-classification.md`.
- `B-F2-SECCOMP-EFFECTIVE-PROOF-REVIEW-2026-09-23\10-final-disposition.md`.

They retain their dated scope and unresolved outcomes. Attempt 04's next action was historical and does not instruct another NexusTest check; subsequent trusted-launch/LPAC decisions remain controlling. No current provider or alternate-host state is claimed from these records.

Public primary references read on 28 September 2026: [Microsoft AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation), [Linux Landlock](https://docs.kernel.org/userspace-api/landlock.html), [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html), [seccomp filtering](https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html). They establish candidate primitives and limitations, not installed support or qualification. In particular, cgroup delegation/whole-tree kill and Landlock ABI coverage must be demonstrated on the actual candidate; seccomp is not a complete isolation system. No provider public/API/support contact is performed in this task.

Internal documentary consistency/adversarial pass: route families versus actual instances, stored versus effective configuration, guest versus independent observation, old versus current account facts, local versus remote cancellation/cost, source reuse versus runtime proof, and changed evidence contracts versus unchanged A0–A6 were checked. No required documentary correction remains. This is a separate pass by the same author/agent, not an independent reviewer or experimental finding.

**Scenario 01–04 NOT RUN; HQ1–HQ5 NOT PASS; HQ6 not begun; Positive Host Binding ABSENT; G2 HOLD.** All three new documents remain uncommitted proposals; MANIFEST and final acceptance records are unchanged.
