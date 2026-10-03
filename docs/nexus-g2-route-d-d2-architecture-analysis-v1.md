# Nexus G2 Route D D2 Architecture Analysis v1

Version: `1.0.0`

Date: **2026-10-03**

Starting baseline: `a0bdfd2b6ea46844d317dff67687e681caacc3c3` / `nexus-v2-g2-development`

Status: **FACTUAL / DESIGN CHECKPOINT ONLY - NOT ACCEPTED; NO IMPLEMENTATION OR EXPERIMENT AUTHORITY**

## 1. Exact decision and scope

**C. MATERIAL D0/D1 UNKNOWN PREVENTS ARCHITECTURE SELECTION.** No architecture family or component stack is proposed for authorized D3 entry. Route D remains FEASIBLE FOR FURTHER DESIGN; no evidence establishes a need to build an isolation runtime. This is not result D and not factual exclusion of any mature family. Requirements and analysis are complete as documentary deliverables; the architecture selection remains unresolved.

The common blockers are [D0](nexus-g2-route-d-d0-requirements-v1.md) U01 existing supported Host, U02 credible numerical independent ultimate fence, U03 actual narrow custody/admission/release evidence, U04 finite all-in cost/survivor horizon and U05 bounded compatible measured profile. U02 alone prevents A; simply comparing two runtimes would not close a shared missing fence, so B is not justified yet. This preserves the accepted P5/P7 outcomes and the experiment-safety gate.

## 2. Source use and critical new clarification

Reuse the completed [D-REF survey](nexus-g2-route-d-external-reference-survey-v1.md), [reuse matrix](nexus-g2-route-d-reuse-adapt-reject-matrix-v1.md), [mapping](nexus-g2-route-d-reference-p1-p12-hq-mapping-v1.md) and [source register](nexus-g2-route-d-reference-source-register-v1.md). Their exact baseline hashes are in D0. Source IDs below resolve to the register's pinned URLs/hashes. They are component contracts/design/source details, not actual Host evidence. No benchmark, provider contact or broad new survey.

Critical fence clarification: SD06 specifies an active-service runtime limit, no oneshot coverage and notification extension; SD07 specifies tree stop/escalation, not a physical completion deadline. SD03 exposes manager mutation/restart surfaces. The design therefore requires one conserved outer deadline, excludes notification/renewal/restart authority and accounts all start/stop/helper phases. Separate local processes remain in the same Host kernel/OS domain. These facts support requirements, not applied-state claims. [Pinned service semantics](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.service.xml), [pinned kill semantics](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.kill.xml).

CG01 supplies subtree membership/kill concepts; these are not outside-kernel fences. WD01 varies by device/driver and feed/disable semantics, so generic watchdog availability cannot establish a nonrenewable lease. [Kernel cgroups](https://docs.kernel.org/admin-guide/cgroup-v2.html), [watchdog API](https://docs.kernel.org/watchdog/watchdog-api.html). New feature-floor check L514: [Linux v5.14 cgroup source](https://raw.githubusercontent.com/torvalds/linux/v5.14/kernel/cgroup/cgroup.c) includes cgroup.kill; this justifies D0's candidate functional floor without selecting an outdated kernel or guaranteeing distribution support. Additional source bytes/hash/retrieval are bound in section 11; URLs initially failing web extraction are not treated as positive evidence.

## 3. Four-family comparison against D0/D1

Qualitative startup/compatibility/operational statements are design inferences, not measurements/security rankings. Every family requires the same independent authority/cost/evidence/fault envelope. No family survives merely by having a stronger guest boundary.

| Criterion | A Namespaces+cgroups+seccomp tooling | B gVisor | C Firecracker microVM | D Kata |
| --- | --- | --- | --- | --- |
| Host prerequisites | Supported Linux, cgroups/controllers, namespaces/seccomp, bounded FS, service manager | Same + exact supported runsc platform/fs/network mode | Same + KVM/CPU support and matching jailer/VMM, guest image/kernel | Same + supported shim/VMM/guest-agent/backend and share/network stack |
| Privilege | Constrained setup or supported userns/delegation; not blanket rootless | Supported platform/setup rights; protected runtime roots/sockets | Privileged jailer/KVM/setup separated from VMM UID; root setup is not guest root | Runtime/backend/KVM/net/storage setup plus protected daemon/shim surfaces |
| Trust boundary | Guest syscalls enter shared Host kernel through policy | Sentry mediation plus Gofer/directfs and Host kernel/platform | Guest kernel separated by KVM/VMM/jailer; Host KVM still trusted | VM boundary plus shim/VMM/agent/sharing/OCI chain |
| Isolation strength | Fixed namespace/UID/mount/seccomp controls; kernel remains exposed | Reduces direct syscall exposure with added app-kernel TCB | Hardware-assisted guest boundary, restricted device/API graph | Hardware-assisted VM/container composition; exact backend matters |
| Kernel exposure | Shared Host kernel; syscall policy/caps are crucial | Host interface narrowed but not removed | Host KVM/VMM paths plus guest kernel | Host hypervisor/runtime/IO paths plus guest kernel/agent |
| Resources | Native whole-unit CPU/RAM/tasks; separate disk/output/log quota | Bound Sentry/Gofer/helpers and virtual task graph | Bound VMM/helpers and guest resource capacities separately | Bound Host overhead/virtiofsd/shim plus guest container tasks/resources |
| Process tree | Native descendants/cgroup recursive membership | Host process inventory != virtual task count | Host VMM/helper inventory != guest PIDs | Shim/VMM/share daemons + guest agent/task graph |
| Filesystem | Fixed immutable base/private mounts; quota workspace | Exact Gofer/directfs and FD/mount mode; bounded Host backing | Read-only base block, finite writable backing; no broad shares/MMDS/snapshot | Exact block/virtio-fs/shared path policy; no default Host-share trust |
| Network | Private netns with denied interfaces/FDs/helpers | Disabled mode and Host-helper channel closure; no Host-network | No guest NIC/TAP first; Host API/control graph denied | No guest connectivity/CNI broad reach; all plugin helpers accounted |
| Lifecycle | Manager owns fixed unit, runtime adds primitives only | Host manager encloses sandbox/helpers; no Sentry-only deadline | Host manager encloses VMM; guest shutdown not final stop | External manager/outer destroys full sandbox graph independent of guest agent |
| Controller loss | Prior manager+outer lease, no re-creation | Same common lease; protected original runsc refs | Same common lease; original VMM/API/backing refs | Same common lease; original shim/VM/container/share refs |
| Evidence visibility | Native cgroup/ns/mount/byte custody; seccomp attachment scope still qualification work | Host+virtual task/fs observations, no guest-only closure | Host VMM/jailer/KVM/config/backing plus scoped guest observations | Multi-layer source/identity/resource visibility; guest reply insufficient |
| Startup | No required guest-kernel boot; actual overhead UNKNOWN | Sandbox/platform start overhead UNKNOWN | Guest kernel/image boot overhead UNKNOWN | Shim/VMM/guest-agent initialization overhead UNKNOWN |
| Compatibility | Fixed harmless Linux command likely plausible; exact syscalls/libs UNKNOWN | Syscall/filesystem support must match fixture; UNKNOWN | Guest binary/kernel/image must match minimal device ABI; UNKNOWN | OCI-style fixed container path plausible; exact release/backend UNKNOWN |
| Patching | Host kernel/manager/runtime/policy/dependencies | Same + runsc/Sentry/Gofer/platform | Host KVM/manager + VMM/jailer + guest kernel/image | Host/shim/hypervisor/guest-agent/kernel/share/plugin versions |
| Operational burden | Fixed bundle/profile plus manager/quota/outer fence | Adds runtime platform and virtual-resource evidence | Adds image/guest lifecycle/KVM/device/fence custody | Adds VM/container/share/plugin coordination; no cluster necessary |
| Custom Nexus work | Narrow admission/identity/evidence/reconciliation bindings | Same with Host/virtual task scope mapping | Same with VMM/backing/guest references | Same with shim/guest/share reference mapping |
| Qualification complexity | Escape/input/migration/quota/manager-fault and loaded-byte tests | Same + Sentry/Gofer/virtual tasks/platform tests | Same + KVM/jailer/guest/Host cleanup and image tests | Same + multi-layer grouping/overhead/share/agent-loss tests |
| Current disposition | CARRY_FORWARD, conditional documentary candidate | RESERVE, conditional alternative | CARRY_FORWARD, conditional VM alternative | RESERVE, conditional OCI/VM alternative |

A is a plausible simplest mechanics candidate IF exact Host, privileged launch, complete fence/custody and fixed fixture compatibility close. That conditional engineering preference is not result A. C is carried forward because a VM boundary may be preferable under the eventual accepted threat/capability; KVM availability is unknown, not absent. B is reserved pending a concrete need for its syscall mediation/compatibility and virtual-task enforcement. D is reserved pending a concrete OCI/VM capability need. Reserve means maintained as an alternative, not removed for complexity; no adverse security fact is asserted. Active future D3 eligibility for all four is BLOCKED by common U01-U04. No family receives FACTUALLY_EXCLUDE; no specific unfixable incompatibility is established. No family-wide DEFER merely for burden. KVM-dependent modes become factually incompatible with a specifically evidenced non-KVM Host only if no supported composition fits that Host; no such evidence is present.

## 4. Concrete mature component decisions

REUSE = reuse supported external component at its bounded contract; WRAP = narrow fixed-profile integration/custody/evidence; PATTERN_ONLY = concept, no dependency; REJECT = named misuse only; UNKNOWN = cannot name a supported actual deployment. Every selection below is conditional; no exact supported package release is selected from upstream research main pins. Full dependencies/licenses/NOTICE/support/patch stream must be bound before adoption; D-REF's LGPL/kernel/Apache distinctions remain intact, no source vendoring/linking/runtime rebuild.

| Component / family / source | Class | What Nexus may do / required qualification |
| --- | --- | --- |
| Linux cgroups v2, namespaces, seccomp/capabilities / all / CG01 NS01 SC01 CP01 | REUSE | Consume native interfaces through supported tooling; verify immutable whole-unit scope, actual policy, controller support and no migration |
| systemd fixed transient service / all / SD02 SD03 SD06-SD08 | WRAP | Fixed create/status/stop with independently admitted profile; no arbitrary DBus broker; start/run/stop/helper readback |
| systemd externally attached scope / all / SD01 | REJECT | Reject for first release design if processes can execute before containment; supported protected alternative requires separately proven creation barrier |
| nsjail confinement / A / NJ01 NJ03-NJ05 | WRAP | Fixed non-listening configuration and protected inputs; reuse setup, no arbitrary user-supplied config or syscall compiler |
| nsjail own timer/PDEATHSIG / A / NJ02 NJ03 | REUSE | Supplementary local defense only; REJECT as sole ultimate fence |
| OCI/runc create/start/state/kill / A / OC01 OC02 RC01-RC03 | WRAP | Conditional alternative to nsjail where its separate create/start barrier is suitable; trusted fixed bundle, no hooks/update/exec/recreate |
| bubblewrap / A / BW01 BW02 | PATTERN_ONLY | Fixed construction remains possible, but no reason to add a third A implementation now; no family-wide exclusion |
| runsc/Sentry/Gofer / B / GV01 GV03-GV07 | WRAP | Exact platform/filesystem mode; all Host helpers and virtual tasks; denied broad directfs/Host-network/control |
| Firecracker + matching jailer / C / FC01-FC05 | WRAP | Reuse VMM/jailer; fixed guest/kernel/images/API/netns/UID/cgroup placement; no MMDS/snapshot/restore paths |
| Kata shim/VMM/guest-agent / D / KA03 KA05-KA08 | WRAP | Reuse supported complete stack, bind Host+guest/share overhead; no agent rewrite or group-as-one-PID assumption |
| containerd runtime-v2 / B/D or OCI integration / CD01 CD02 | PATTERN_ONLY | Optional future daemon/shim need, not first required dependency; broad daemon/API/snapshot/plugin graph needs separate justification |
| Filesystem project quota/finite backing / all / QT01 | WRAP | Reuse selected supported mechanism; whole writable bytes/inodes/logs/tmp/retention scope and host-helper writes |
| Hardware watchdog / all / WD01 | UNKNOWN | Existing device contract may help; feed/reset/disable/clock semantics and correlated-failure bound not established |
| Hypervisor/power-controller nonrenewable lease / all | UNKNOWN | Reuse existing supported infrastructure if available; exact enforcer/arm/fault/latency/cost unknown; no new generic supervisor |
| Boot recovery facility / all | WRAP | Reuse native default-deny service ordering/inventory; Nexus builds original-state reconciliation only; no auto-start/resume |
| MAC/Landlock supplementary layer / all / LL01 LK03 | REUSE | Exact supported policy only; mandatory missing ABI is STOP, not best-effort waiver |
| Kubernetes UID/desired-observed state patterns / KW01-KW03 KJ01 | PATTERN_ONLY | Original identity and observation concepts; no cluster, automatic retry or TTL-after-finished lifetime substitute |
| Host/runtime control sockets or generic root shell/MCP / all | REJECT | No workload or task-selected privileged management surface |

The candidate A alternatives are mutually exclusive future design choices, not a combined nsjail+runc/bwrap stack. UNKNOWN supported quota/outer-stack choice prevents an exact D3 stack recommendation. REJECT concerns the unsafe attachment pattern, not all systemd scopes.

Nexus-specific work still needed, only after separate implementation authorization: typed original-request mapping; admission checks over current independent grant/slot/budget; exact attempt/Host/boot/config/input/qualification binding; minimal domain journal/evidence validation; UNKNOWN and effect/cost reconciliation; retry refusal and requalification invalidation. Reuse existing qualified identity/credential and lifecycle facilities. Do not build a cgroup implementation, seccomp compiler, process supervisor, VMM, Sentry, guest agent, image filesystem engine, daemon scheduler, general model loop, billing platform or secret broker. Code size/ease is UNKNOWN.

## 5. Ultimate lifetime-fence candidate assessment

The required deadline starts before first allocation and conserves exposure through all phases. Workload refusal, lost Controller, lost Agent and failed inner watcher cannot renew it. Mechanism remains incomplete until a supported finite independent consequence covers every declared mandatory fault. See D1 F0-F9/correlation matrix.

| Candidate combination | Survives what / remaining failure | Decision |
| --- | --- | --- |
| Runtime timer alone (nsjail/watchdog/client wait) | May stop normal guest; fails monitor/client/clock loss and common kernel | REJECT as ultimate fence |
| Fixed manager service + runtime timer + cgroup kill | Plausible F0/F1/F2/F7/F8 process containment when manager/kernel healthy; F3-F6 shared dependencies remain | REUSE local layers; incomplete ultimate envelope |
| Above + separate local supervisor | Can cover one userspace process failure if not same manager; shares OS/kernel/time/storage | Conditional supplementary layer; no independence claim for F4-F6 |
| VM process bound + guest timer | Host manager contains VMM independent of guest refusal; same Host kernel/KVM/manager fault remains | Conditional C/D local envelope; stronger guest isolation is not final-fault fence |
| Boot-time orphan cleanup | Can prevent resurrection/reconcile AFTER a boot; never-rebooted work may persist | REUSE recovery, REJECT as sole lifetime bound |
| Host manager + hardware watchdog | Device may reset independently; feeding/disable/nowayout and deadline arm/reset provenance unknown; healthy feeder can conceal a leaking unit | UNKNOWN until device-specific lease/fault contract; not selected |
| Host local layers + outer hypervisor finite lease | Can survive target Agent/manager/kernel failure IF separately controlled, autonomously armed before creation, immutable/nonrenewable and finite-stop proven | Conditional credible design family, actual component/maximum UNKNOWN |
| Host local layers + independent physical power fence | Can remove target power IF independent clock/control/power path, known finite cutoff and no automatic reboot/resume | Conditional credible design family; actual facility/scope/cost UNKNOWN |
| Controller emergency API poweroff request | May assist cleanup; client/network/credential outage can prevent request | REJECT as autonomous ultimate fence |

Mutability audit requirements for any systemd candidate: no notify/notify-reload workload, no notification socket inherited or forwarded; no RuntimeRandomizedExtraSec; no automatic Restart/restart-forcing exits/socket or dependency activation; no unadmitted hooks/actions; bound activation/start/stop separately; deny Manager Start/Restart/SetUnitProperties/Reload update channels to workload and restricted requesters; do not assume RuntimeMaxSec immutable. Manager reset/reexec/reboot and activation timestamp behavior require exact-version source/test binding. Even if those paths close, PID1/kernel starvation or uninterruptible process state is not assigned a physical maximum from timer/SIGKILL documentation. A nonrenewable external lease constrains cumulative lifetime across restart/pause/boot; neither client progress nor a failure-prone event loop is its final enforcer.

Outer readiness must produce a protected receipt bound to exact Host/VM generation, absolute deadline/origin, clock/error, enforcer identity/version/policy, actors unable to extend/reset/restart, numerical failure/stop tail and independently observable cessation. It must cover privileged setup too; arm-before-release is insufficient if unbounded setup already occurred. The fence must be independent of the Controller for expiry and of the target Host kernel/OS for enforcement; shared physical/hypervisor dependencies require explicit coverage. Ordinary fixed watchdog feeding is not automatically such a lease. No supported actual instance of this composition is currently evidenced: **ultimate fence unresolved**.

## 6. Filesystem, network and process/resource design

Filesystem: protected immutable/read-only staged base and dependencies; private nonpropagating mounts; owner home, actual repository, credential directories, control/evidence sockets and host devices absent. Explicit owner-admitted input copy only; no live bind of owner repository. One bounded writable synthetic workspace plus separately accounted tmp/log/output/runtime metadata, project-byte/inode quota or finite backing. No unaccounted cache/dump/snapshot/shared paths. Extract only allowed regular files, reject links/devices/traversal, enforce aggregate size, copy to protected staging and validate hashes before acceptance. Native FS quota limits capacity; IO controller limits rate, neither substitutes for the other. Unmount/remove objects only with exact original refs and authorization, then independently inventory. Cleanup timeout retains UNKNOWN/exposure; finite residual retention remains U04.

Network modes are conceptual: NO_NETWORK first = no guest interfaces/routes/DNS/IPv4/IPv6/metadata/proxy/Host service or inherited socket channel, no runtime helper creating unadmitted network on its behalf. ALLOWLISTED_NETWORK future = exact endpoint/protocol/name-resolution/redirect/byte/rate/cost scopes and failure behavior through a qualified policy boundary. TASK_BOUND_NETWORK future = operation-specific independently attenuated capability to a qualified outside-workload broker, with effect query/reconciliation and no raw secret. These two future modes require separate authority/qualification; no firewall rules designed or applied. Hash effective mode/resolver/proxy/helper/socket/allowlist basis into config and qualification; changes invalidate before use.

Process/resource: assign protected unit ancestor BEFORE any workload instruction; kernel descendants inherit membership but cannot migrate/delegate/change ancestor ceilings, alter namespaces or acquire Host rights. Native runtime setup/helper processes must be enclosed or explicitly qualified companion units. Daemonization/setsid/reparenting/parent exit does not remove membership. Native domain-subtree cgroup.events populated plus original cgroup object/path/boot identity and cross-checked task-start refs is authoritative for that subtree's live membership, not all escaped processes. Retain allowed actor graph and runtime/helper inventory to justify completeness. For B/C/D separately bound virtual/guest tasks and verify Host VMM/Sentry/Gofer/shim/share process closure. Do not infer guest PID count from Host pids.max. Hard CPU/RAM/swap/tasks and aggregate writable capture limits account all helpers; control-plane resources remain separately bounded/reserved. Attempts to access topology/control/sockets or unexplained outside helpers invalidate binding and invoke admitted stop/fence. No network/device/scheduler escape.

## 7. Conceptual responsibility split

| Layer | Owns | Must not acquire |
| --- | --- | --- |
| HostAdapter | Transport, bounded request/response validation, supported original native-reference mapping and identity/source errors | Policy invention, arbitrary shell/config/hooks/runtime choice, opaque retries/recreation, grant issuance |
| Host admission endpoint | Verify independent grant/profile/expiry/cumulative slot/current supported config and safe create/fence readiness before each effect | Widen authority or infer grant from qualification/credential possession |
| Host Agent | Fixed invocation, original lifecycle facts, effective observation collection and bounded authorized cleanup coordination | Generic agent/model loop/scheduler, workload-renewable deadline, arbitrary root endpoint, self-certification of unseen state |
| Runtime/substrate | Actual isolation, cgroup/namespace/seccomp/FS/network mechanics, supported process start/stop/query and enforced limits | Nexus task authority, budget arithmetic, useful task acceptance |
| Lifecycle/outer manager | Preinstalled finite whole-unit and failure cutoff, no resurrection, independent source observations | Depend solely on Controller/Agent/guest cooperation or restore an expired grant |
| Nexus Controller | Authority validation, eligibility, conservative budget/admission, dispatch, exact qualification binding, minimal records, UNKNOWN/reconciliation/retry/invalidation | Mint independent grants, enforce remote hard limits by ledger, replace missing runtime with generic engine |
| Owner | Explicit architecture/TCB/profile/custody/cost acceptance and separate later experiment authority | Acceptance implicitly authorizing installation or G2 |

## 8. Conditional minimum future D3 boundary (not proposed for entry)

No standalone D3 proposal document is created because decision C is unresolved. The following defines the smallest *conditional* mechanics scope for later re-review once U01-U04 close, not an execution protocol or permission.

One existing approved Host; one fixed harmless reviewed executable that reads <=1 MiB synthetic staged fixture, produces a fixed small deterministic output and exits; no arbitrary command, shell strings, internet, owner files, model, API, credentials, devices, snapshots or background service. One grant/one attempt/one original unit; NO_NETWORK; D0 small envelope; fixed start barrier; external owner-visible protected evidence; whole-unit cessation and explicit mount/net/backing cleanup. No generic task authority. No adversarial test or fault injection before its own safe envelope/protocol/owner authorization. D3 measures identity/create-bind-start-observe-cleanup mechanics only; later D4/D5 qualification uses separately bounded adversarial/fault tests.

Success criteria: externally verified pre-effect admission/original slot/fence; protected byte/input/config/effective-limit association before release; one deterministic result independently validated; scoped whole-unit/helpers/guest zero-live; resource cleanup/effects positive; conserved cost/exposure and source-bound final evidence. Failure criteria: any bypass/widening/hidden helper/late execution, stale identity/config, false terminal/evidence, overrun, network/secret access or unsafe retry. Missing facts produce UNKNOWN, admission stays closed and original exposure remains. A refusal-only result is not useful HQ6/G2 success. **Max exposure UNKNOWN now; D3 not admissible**. Tiny nominal limits do not cap outer-fault or retained-object exposure. No chosen component stack or accepted capability exists yet.

## 9. Future HQ qualification plan

The plan applies to any subsequently proposed family; family-specific supplements follow below. STATIC_EVIDENCE and CONFIG_EVIDENCE do not replace RUNTIME_EXPERIMENT/FAILURE_INJECTION where actual proof is required. OWNER_DECISION does not manufacture enforcement, and EXTERNAL_EVIDENCE must have qualified source/scope. No HQ scenario run.

| HQ / future required proof | STATIC_EVIDENCE | CONFIG_EVIDENCE | RUNTIME_EXPERIMENT | FAILURE_INJECTION | OWNER_DECISION | EXTERNAL_EVIDENCE |
| --- | --- | --- | --- | --- | --- | --- |
| HQ1 Fixed execution provenance | Supported reviewed binaries/dependencies and custody design | Exact Host/boot/profile/byte/transformation basis | Same-unit actual loaded/object identity; substitution refusal | Interrupted staging/load and boot/recovery identity | Exact TCB/code/dependency scope | Qualified OS/runtime observations, supported release/support identities |
| HQ2 Effective isolation | Namespace/VM/UID/FD/socket/threat graph | Actual policy, actors, mounts/network/caps/seccomp | Safe negative escape/credential/control tests at exact barrier | Runtime/helper loss and no weaker fallback | Accepted isolation/TCB residual | Subject-external applied-state and denied-access facts |
| HQ3 Controlled inputs | Closed command/files/env/mount/IPC/FD graph | Actual staged inputs and inherited descriptors | Same-unit input/secret-marker/stream/source observations | Interrupted input staging, config substitution | Exact fixed fixture and allowed outputs | Protected launch and effective-state observations |
| HQ4 Containment/recovery | Numeric full-phase/whole-tree/outer-fault design | Effective bounds, fence arm/origin and no renew/restart | Descendant/resource/deadline/zero-live/cleanup tests | Controller/Agent/runtime/manager/Host/boot/network loss only inside already-safe outer envelope | Exact numeric fault coverage and separately authorized protocol | Independent outer-fence and subtree/resource observations |
| HQ5 Evidence integrity | Source/custody/ordering/gap/UNKNOWN rules | Actual writer/storage/identity/expiry protection | Forgery/replay/partial/guest-only refusal and valid positive record chain | Collector/store loss/crash durability | Scoped evidence acceptance and retained UNKNOWN policy | Source authentication, durable external copy/corroboration |
| HQ6 Execution/effect binding | One accepted capability complete P1-P12 graph | Current independent authority, resources/costs/config/qualification | Pre-effect admission; original result/effect/usage/cancel primitives | Ambiguous create/dispatch/result/cancel/external effect; no blind retry | Separate accepted capability, binding and later G2 gates | Contract/hard-price/fence/native-effect observations and settlement |

Family supplements: A native namespace/seccomp/cgroup/UID/mount/actual loaded byte coverage plus setup outside leaf; B Sentry/Gofer/directfs/platform and virtual-task limits; C KVM/VMM/jailer/guest-image/API/Host backing and guest-independent stop; D shim/VM/agent/share/plugin grouping and overhead. Qualify exact releases/configuration; kernel/runtime/Host/custody/fence/price/input upgrade or material drift invalidates affected binding. HQ6 is not a demand to implement G2 ledger during qualification. Windows Scenario 01-04 remain untouched, no Linux scenario relabeled as their completion.

## 10. Decision, adversarial dependency and next owner action

D2 selection status: **UNRESOLVED / RESULT C**. Proposed family: NONE. Proposed exact stack: NONE. Accepted: NO. Route D remains feasible: YES, conditional further design. A/C carried forward and B/D reserved as above; no factual exclusion. Neither supported runtime maturity nor optional outer-fence idea closes actual U02. See [lifecycle/evidence](nexus-g2-route-d-d2-lifecycle-and-evidence-design-v1.md) and [separate adversarial review](nexus-g2-route-d-d2-adversarial-review-v1.md).

SAFE RESUME POINT ESTABLISHED. Resolve only U01-U04 with supported status-only existing Host/fence/custody/cost records, then bind U05's safe measurement scope. Exact owner decision now: identify whether such existing evidence is available and authorize only its bounded documentary closure if desired; no password, login, purchase or shell action. If unavailable, keep C/HOLD rather than invent an implementation task. A future family recommendation must receive separate architecture review/decision and only then any bounded D3 authorization. No pre-D3 comparison/installation is authorized here.

## 11. Additional source-byte bindings

| ID / exact source URL | Retrieved / bytes | SHA-256 / scope |
| --- | --- | --- |
| [L514](https://raw.githubusercontent.com/torvalds/linux/v5.14/kernel/cgroup/cgroup.c) | 2026-10-03 / 178886 | `A903277BF500A868E813F71EF0D635909FAEB7AF1F7D289D42AF6294F1F2930E` - cgroup.kill present in v5.14; not supported Host selection |
| [SD03](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/org.freedesktop.systemd1.xml) | 2026-10-03 / 603472 | `59CFEEA5144E169369EE81F2B797FE9EB63EC18CB6AA918C2E66A7D5218117CA` - D-REF cache reused and byte-verified for critical fence/source consistency |
| [SD06](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.service.xml) | 2026-10-03 / 120642 | `12770F86A26DCDF32873225669F5AA9421283C303BBC72BDDB04530850F66D44` - D-REF cache reused and byte-verified for critical fence/source consistency |
| [SD07](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.kill.xml) | 2026-10-03 / 11224 | `448322830DBBD02C64CCA99941BA92705AFE9648241FC917DB7A8D6AE7910E72` - D-REF cache reused and byte-verified for critical fence/source consistency |
| [CG01](https://docs.kernel.org/admin-guide/cgroup-v2.html) | 2026-10-03 / 172971 | `6EFABE7ED748F1D863859A0E5C50E770E47255C9A071BF878F6460E7E01C0563` - D-REF cache reused and byte-verified for critical fence/source consistency |
| [WD01](https://docs.kernel.org/watchdog/watchdog-api.html) | 2026-10-03 / 24828 | `0E0D19BBCE5CCCA8D22DC8CBF754CF626E9D723B144C029477235326C69882D0` - D-REF cache reused and byte-verified for critical fence/source consistency |

Preserved state: G2 HOLD; Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT. Route B unresolved / retained; Route D FEASIBLE FOR FURTHER DESIGN. Accepted A0-A6/P1-P12 and all historical accepted bytes remain unchanged. No installation, Linux provisioning, VM/container creation, Host execution, privileged operations, credentials, paid activity, HostAdapter/Host Agent implementation, architecture acceptance, G3/G4 entry, merge, push, tag or freeze.
