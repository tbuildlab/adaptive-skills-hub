# Nexus G2 Route D Owned Host Feasibility v1

Version: `1.0.0`

Date: **2026-10-03**

Baseline: `57bf2a2df4efa0d93d621e396839f5767bdfa572` / `nexus-v2-g2-development`

Status: **NON-NORMATIVE FACTUAL / DESIGN STUDY ONLY - NOT ACCEPTED; NO EXPERIMENT OR IMPLEMENTATION AUTHORITY**

## 1. Conditional feasibility and architecture boundary

**ROUTE D FEASIBLE FOR FURTHER DESIGN.** This is technical plausibility from mature Linux primitives and an explicit missing-evidence list, not availability, a selected implementation, pre-experiment readiness or positive qualification. No Linux system was discovered/started/configured. No D0-D7 phase is started. [Safety study](nexus-g2-p5-p6-safety-rebaseline-study-v1.md) conclusion A remains independent: no P5/P6 amendment is needed or accepted.

Assume one owner and one dedicated Linux Host/VM, non-public and not multi-tenant; the Nexus Controller is separate, workload units disposable. Hypothetical separation: `Nexus Controller -> narrow HostAdapter -> fixed-profile Host admission/execution agent -> existing Linux kernel/service-manager enforcement -> disposable unit`. This is not an agent/model orchestration runtime. No Docker/Podman/Firecracker/bubblewrap or other engine is chosen. Kernel namespaces/cgroups alone are not a qualified sandbox. Historical F2 and exited LPAC restrictions are not reopened.

Adoption would require a separate versioned Route D architecture/TCB and qualification decision: exact supported distribution/kernel/manager/filesystem and infrastructure, controller versus Host credential/privilege ownership, fixed-capability surface, admission/lease/failure/cost/evidence sources and acceptance scope. The owner of the infrastructure may be Nexus's owner, but the Host enforcer remains a separately qualified component, not portable governance code rebranded as enforcement. A0-A6 are unchanged now. A1/A2 prohibit building a generic runtime to escape a missing binding; if the final Host Agent needs an arbitrary-command privileged broker, general scheduler/model loop or Nexus-implemented generic sandbox engine, this proposal cannot justify it and a material explicit architecture alternative would be required. No Windows privileged-broker/password/NexusTest fallback is authorized.

## 2. Candidate trust and credential boundary

| Layer | Proposed role / rights | Required exclusions |
| --- | --- | --- |
| Owner / grant issuer | Independently establishes exact admitted fixture/capability, scope, expiry, cumulative effects/resources/money | Model, Host and controller cannot mint wider grants; compromised ultimate issuer is not falsely covered |
| Nexus Controller | Eligibility, sequential one-original-attempt admission, reservation and durable domain facts; status/result/effect adjudication | No root/administrator/VM management credential delegated to workload; control credential cannot widen sealed Host profile |
| HostAdapter | Typed fixed operations and exact unit/operation references only; translates supported observations | No arbitrary shell/start-template choice, automatic recreation, unit-reset, model loop or hidden side effects |
| Host admission/enforcer | Independently validates owner-approved profile/finite lease/cumulative slot; creates only approved unit and controls its lifecycle | Workload and restricted controller cannot edit manager/cgroup/lease/policy/issuer/evidence; no broad reusable root endpoint |
| Kernel / service manager / optional outer fence | Known Linux/manager TCB consumes mature primitives; privileged provisioning only in a separately accepted deployment | Privilege minimization is unresolved, not a rootless sufficiency claim; outer fence cannot share every relevant failed layer |
| Disposable workload | Fixed reviewed binary/dependency basis, dropped capabilities/no_new_privs, bounded inputs; isolated user/PID/mount/network/IPC and other applicable namespaces | No Host PID/cgroup/device/sysfs/control socket/evidence mount; no owner credentials or cloud metadata; no privileged mounts or shared-root shortcut |
| Evidence/recovery | Protected Host identity/boot/unit records, external controller custody; bounded retained task outputs | Workload may emit data, not decisive enforcement PASS; append-only label alone does not resist writer/TCB compromise |

Controller compromise resilience is limited to its independently enforced pre-issued scope: authenticated possession of a control token is not permission to expand deadline, resource class, concurrency or cumulative allocation. Host must refuse extension/resume/new unit beyond that authorization even if controller asks. Owner/root/kernel/provider are named TCB; new trust assumptions need explicit acceptance. Transport authentication, command/data parser, least privilege, revocation and protected owner facilities are design UNKNOWNs; no new secret platform is proposed. No key, password or token value/hash is required in evidence.

## 3. P5 primitive feasibility and caveats

L01-L08 in section 10 are upstream documentation, not installed-system proof. The small facts below are distinguished from this study's proposed acceptance constraints.

| Candidate primitive | Documented fact / design purpose | Qualification gap / false substitute |
| --- | --- | --- |
| cgroups v2 CPU | L01 cpu.max limits applicable scheduler bandwidth; combine finite runtime for aggregate CPU | Fair-class/BPF scope and burst matter; CPU quota is not a wall-clock deadline or universal scheduling-class cap |
| Memory / swap | L01 memory.max is a hard-limit mechanism with documented temporary overrun; swap is separate | Account bound/overshoot and workload capabilities; memory.high alone is not hard memory maximum |
| Process count / descendants | L01 pids.max restricts fork/clone; children inherit cgroup; privileged migration can change membership | All descendants/subgroups, task/thread counting and mutation paths; no workload migration/delegation privilege |
| Whole-unit kill / observation | L01 cgroup.kill targets subtree with concurrent-fork handling; cgroup.events populated records live subtree | Signal request is not a physical-latency guarantee; validate original subtree/boot identity and no resurrection |
| Namespaces | L03 namespace types partition system views; candidate UID/PID/mount/net/IPC/UTS/cgroup scope | Shared kernel remains TCB; inherited FDs, devices, mount propagation and capability paths need independent negatives |
| Seccomp / privilege dropping | L02 filters reduce syscall surface; documentation explicitly does not call seccomp a complete sandbox | Fixed executable/dependency/syscall graph and no_new_privs; no generic invented allowlist or filter-only PASS |
| Filesystem / disk | L04 quota subsystem is available; consider supported hard bytes/inodes or fixed-capacity disposable block workspace | Specific project-quota filesystem/mount/accounting not selected or proved; IO rate/cgroup memory is not a disk-capacity limit |
| Fresh execution inputs | L08 offers environment/root/workdir/temporary-directory controls | Actual launch environment, FD inheritance, runtime-added state, secrets and loaded bytes need external effective observation |
| Service lifecycle | L06 RuntimeMaxSec bounds active service time, not oneshot activation; notify services can extend timers | Separate startup/stop deadlines; no guest notification/extension, random extra time, restart/resume or broad manager access |
| Tree termination | L07 control-group stop targets unit processes and can escalate to SIGKILL | Avoid process/none modes and disabled escalation; bind actual membership, stop configuration and zero-live state |
| Independent watchdog/fence | L05 watchdog APIs describe device/configuration-specific reset behavior | It is not universal finite power-off; availability, feeding/disable/nowayout/latency and failure independence must be established |

P5 is therefore **conditionally feasible, NOT PROVEN**. A finite tuple must cover setup, admitted wall deadline, CPU rate/aggregate, RAM/swap/overshoot, task count, disk/inodes, producer/output/log volume, allowed channels, residual-object lifetime and failure/cleanup. Logs, crash dumps, snapshots, host-root writes, device IO and network-service effects are either proven excluded or separately bounded. Read-only base and ephemeral workspace are proposed restrictions, not current observations. No privileged library/manager/socket escapes through the workspace, environment or descriptors. A private network namespace alone cannot prove closed channels if a trusted proxy/Host service remains reachable.

## 4. Launch, failure, controller-loss and reboot strategy (not executable)

1. Bind an owner-approved fixed capability/profile, protected executable/dependencies, immutable deadline/configuration and cumulative one-slot grant. Persist original admission/attempt identity and worst-case exposure BEFORE allocation. Host admission must refuse replay, widening, extra unit, or unsupported state; request IDs alone are not grants.
2. Prepare effective cgroup ceilings, filesystem/namespace/credential/FD/environment denial and independent ultimate-lifecycle protection BEFORE workload instructions execute. Privileged setup and its failure cleanup need their own finite envelope. Bind actual code/object identity across check-to-exec/load, not a prelaunch hash plus later path. No unreviewed executable/dependency is selected by task output.
3. Service manager owns a fixed lifecycle independently of the remote Controller/Host Agent. Watchdog may tighten it. Deny workload notifications/DBus and controller renewal/recreation/reset authority; no automatic restart/restore after expiry or reboot. Finite startup, active and stop phases must form one conserved deadline, rather than restarting the lease at each phase.
4. At cancel/loss/deadline, stop new admission, request whole-unit termination, and independently observe original subtree/process/resource state. If the manager/watchdog/ordinary kill cannot cover an admitted stuck-kernel/device/system fault, a separately qualified outer hypervisor/hardware fence with finite consequence is required OR that profile remains ineligible. No fixed kill latency is inferred from SIGKILL documentation, and faults are not removed from scope merely to pass. Manager/watchdog sharing the same failing kernel does not prove independence against that kernel failure.
5. Power-off/kernel crash stops ordinary active compute, but surviving disk/external effects require reconciliation. Boot recovery begins default-deny before workload starts: enumerate protected persisted attempts/boot identities, quarantine orphan resources, prohibit auto-resume, reconcile/fence originals and cleanup bounded objects. Expired leases are not reissued. Uncertain elapsed time after clock/boot reset is STOP, not a fresh timer. If reboot never happens, boot cleanup alone supplies no runtime bound.
6. Collector loss stops new dispatch and acceptance; independent hard enforcement continues. Incomplete evidence remains UNKNOWN even if the lease has elapsed. Persist attempt/unit/cgroup/object identity, relevant boot ID/clock basis, scope/versions/input/authority refs, event order, limit readback, fallback readiness, externally observed terminal/subtree/resource state, costs/effects/gaps. Keep protected bounded records independent of untrusted output. No infinite logs, universal transcript or recursive verifier project.

Actual manager type/settings, bootstrap race closure, external loaded-byte observations, timer precision/maximum consequence, unavailable-kernel fencing, boot barrier, clock conservation, controller compromise/replay and crash evidence remain UNKNOWN. Ordinary controls are plausible components; this document claims no complete hard wall-clock/failure envelope for an available Host.

## 5. P6 infrastructure, model and effect separation

Use a finite owner-approved obligation horizon H and separately bounded paid effects; never label infrastructure zero-cost. No vendors, prices, accounts or paid resources are selected/used.

| Cost model | Could provide finite Host cost? | Mandatory evidence / exclusions |
| --- | --- | --- |
| Fixed-price dedicated VPS/VM | YES conditionally: committed fee over H can bound covered allocation independent of per-second runtime | Contract covers CPU/RAM/disk/traffic/support/taxes/overage; no autoscale/GPU/snapshots/build/premium service; renewal/topup/extra actors cannot expand authorized obligation. Fixed advertised price is not an all-in contract. No such current contract exists here. |
| Fixed-price physical/local machine | YES conditionally: sunk ownership and hard capacity remove cloud runtime metering | Explicit ownership/allocation basis, finite energy/runtime/power-price upper bound and applicable storage/network/maintenance/repair obligations. Fixed acquisition is not unlimited future electricity/wear and no compute-lifetime bound. No zero-cost or liability guarantee inferred. |
| Metered IaaS with fixed monthly cap | ONLY with genuine enforced all-in liability/cutoff and bounded overshoot/tail | Soft budget, account quota, dashboard alert or credits do not qualify; ongoing VM/storage/egress and internal retries must be covered despite controller loss. Dedicated account narrows actors only. |
| External LLM/API paid effects | Independent of Host pricing; each needs prior finite grant/cap or hard call/token/byte/retry maxima | Provider/model/price/input-output/internal-loop/tool scope, callable actor restriction, reserved cumulative amount, effect identity and authoritative observation/reconciliation. No model is required for the initial deterministic fixture. |

`C_owner_max(H) = fixed_infrastructure_obligations_max(H) + bounded_variable_host_terms + bounded_model/API_terms + bounded_external_paid_effects + bounded_setup_failure_retention_cleanup_tail`.

An all-in fixed-price/no-overage contract can make additional compute-charge duration irrelevant for P6 *within its exact covered horizon*, even if cleanup/reporting is delayed. It cannot erase unbounded P5 work, authorize endless renewal, hide storage/network extras or turn an outstanding bill into settlement. Per-task allocation of a monthly fee is internal accounting, not an external financial ceiling. Reserve conservatively without double-counting a shared committed cost; common contract exhaustion/renewal remains scoped and explicit. External paid effects need separate hard enforcement outside a possibly compromised Controller; fixed Host cost cannot cap them. Exact contract/horizon/inclusions, current authority/headroom and variable upper bounds remain UNKNOWN, so no numerical owner ceiling or ready experiment is offered.

## 6. Evidence, cancellation, recovery and reconciliation contract

Route D would need equivalent HQ1-HQ5 security proofs and separate HQ6 primitives on one already accepted capability: actual Nexus-controlled code/dependency provenance; effective isolation/control-actor and input/secret denial; whole-unit finite fault containment; protected source-bound evidence; non-bypassable pre-effect authority/budget and observable operation/effect references. A Host Agent receipt establishes only its authorized observation scope; signed/append-only records do not manufacture truthful enforcement.

Cancellation returns request/ack/status separately; it does not claim zero-live, released resources, erased effects or settled charge. The Host must expose original unit/operation lookup and bounded retained evidence after interruption. Durable checkpoint design retains validated artifacts plus input/current-policy/authority/expiry/unresolved references; reboot or restoration cannot restore grants or reset totals. No universal exactly-once, process snapshot or generic scheduler is required. Ambiguous create/exec/cancel/paid effect remains UNKNOWN; refusal prevents unsafe replay until positive effect/no-effect reconciliation, fresh authority and conserved budget. Actual G2 ledger is not part of this study or Host qualification prototype.

## 7. Engineering / operations difficulty

Estimates are qualitative design judgments, not measured schedule, cost or deployment plan. A small owner scope reduces feature count, not the need to qualify trust and failure boundaries.

| Component | Difficulty | Work / residual responsibility |
| --- | --- | --- |
| Host Agent | HIGH | Fixed parser/profile admission, privileged surface minimization, original-attempt/lease and custody |
| HostAdapter | MEDIUM | Narrow schema/native refs/state translation; no hidden create/retry or generic runtime |
| Execution lifecycle | HIGH | All stages/limits/actors/deadline/revocation; startup race and cleanup |
| cgroups v2 | MEDIUM | Exact delegated topology, scheduler/overshoot/membership accounting and denial |
| Namespaces | HIGH | UID/mount/PID/IPC/net/descriptor/device/kernel attack closure |
| Seccomp | HIGH | Fixed dependency/syscall evidence and supported filter/LSM boundaries |
| Filesystem | HIGH | Immutable byte basis, quota/inodes, path/link/mount and residual capacity |
| Network policy | HIGH | No-network graph first; future egress/service/metadata scope and paid effect gates |
| Process-tree termination | HIGH | Subtree/alternate creation/escape/readback and stuck-task fallback |
| Reboot recovery | HIGH | Boot admission barrier, durable orphan/clock/lease/replay handling |
| Evidence | HIGH | External effective provenance, protected durable bounded records and coverage |
| Reconciliation | HIGH | Original create/effect/artifact/cost query and positive no-effect/UNKNOWN |
| Patching | MEDIUM | Qualified versions/CVE/configuration change, requalification and rollback |
| Secrets | HIGH | Owner facility, least authority, revoked-grant effects, workload exclusion |
| Monitoring | MEDIUM | Bounded diagnostics and actionable loss/drift; monitoring is not hard enforcement |
| Testing | HIGH | Host boundary negatives, finite fault injection and regression |
| Qualification | VERY_HIGH | End-to-end HQ1-HQ6 evidence/finite failure/financial binding and owner review |

Owner operations also cover inventory/backups, protected logs/retention, storage sanitization, patch/incident response, availability/fencing, renewal and external API accounting. Long-term Linux/version and infrastructure changes invalidate affected qualification. None of these responsibilities is assumed solved by open-source availability.

## 8. Proposed D0-D7 roadmap (none started)

| Phase | Future deliverable / falsifiable exit | Present state |
| --- | --- | --- |
| D0 Requirements | One accepted capability and finite numerical effect/resource/money/failure envelope; no generic execution service | NOT STARTED |
| D1 Threat Model | Exact TCB/actors/controller-compromise and admitted failure matrix; no convenient exclusions | NOT STARTED |
| D2 Architecture | Owner-reviewed versioned route/privilege/cost/custody/outer-fallback decision; A1/A2 compatibility established | NOT STARTED |
| D3 Minimal Prototype | Separately authorized fixed secret-free facility; static review and safe package before execution | NOT STARTED |
| D4 Isolation Validation | Actual bytes/inputs/secret/control/migration/network/device negatives externally bound | NOT STARTED |
| D5 Failure/Recovery Validation | Controller/agent/watchdog loss, deadline/tree/manager failure, reboot/orphans and UNKNOWN replay tests within independently safe outer envelope | NOT STARTED |
| D6 HQ1-HQ6 Qualification | One accepted capability with all equivalent security and pre-effect/effect/cost/cancel/recovery primitives; every mandatory fact positive | NOT STARTED |
| D7 Positive Host Binding | Exact scoped expiry-bound owner qualification record; separate G2 authorization still required | NOT STARTED |

Minimum future design experiment, NOT authorized here: first static/contract review of a supported exact existing dedicated Host, isolation/lifecycle/outer-fence capability and all-in cost basis. Only after those hard safety premises and separate owner authority may one secret-free deterministic unit test be designed for pre-exec containment, controller/watchdog loss, descendants, denial, fixed deadline and original-identity reconciliation. It must not create resources or run hostile code to discover whether the fallback is safe. No commands/unit files/agent code/VM provisioner are supplied.

Abandon/rollback criteria: inability to minimize privileged surface or close actual byte/input/actor evidence; absent finite lifecycle/fault or monetary consequence; workload influence on deadline/manager/credentials/evidence; need for generic runtime, password transfer, Windows Option A, relaxed default deny or unaccepted privilege expansion. During any separately authorized future test, stop admission, use qualified native/outer termination, quarantine originals/UNKNOWN, reconcile and clean only approved resources; no automatic new Host/unit. This study creates nothing requiring system rollback.

## 9. Route B versus Route D (no ranking or selection)

| Dimension | Route B | Route D |
| --- | --- | --- |
| P5 evidence | Provider owns native hard limits/failure semantics; Nexus needs exact-mode authoritative and applied evidence | Owner can inspect chosen kernel/manager state; complete actual fault/TCB evidence still required |
| P6 predictability | Metering/caps/inclusions/tails are contractual provider dependencies | Fixed covered obligations may simplify charge proof; energy/overage/paid APIs/renewal remain |
| Trust boundary | Provider runtime + separate qualified Nexus control/custody | Owner Linux/manager/provisioning/agent/possible fence + separate controller; new TCB requires acceptance |
| Implementation burden | Narrow adapter/governance plus qualification; no infrastructure engine | Fixed Host boundary/provisioning/admission/evidence/failure facility in addition to adapter; generic engine still prohibited |
| Operating burden | Provider patches infrastructure; Nexus tracks supported mode/actors/contracts/drift | Owner patches/hardens/monitors/recovers/fences and requalifies |
| Failure ownership | Provider contract/telemetry vs Nexus uncertainty/retry decisions | Owner manages Host failures; independent fallback/physical limits cannot be assumed |
| Credential surface | Compute control and optional model/service credentials | Remote control + infrastructure/admin/possible fence + model/service credentials; guest gets none |
| Qualification burden | Equivalent HQ1-HQ5 + HQ6; no marketing/SDK PASS | Same properties, independent actual Linux evidence; no source-code availability PASS |
| Portability | Adapter isolates provider APIs; contract/version drift | Linux/manager/fs/hardware coupling; portable Nexus governance remains separate |

No winner is ranked. Route D offers more observable control at the cost of new owner operations and trust responsibility. There is no claim it is available, cheaper, easier or already qualified.

## 10. Narrow upstream documentary sources and byte binding

Retrieved publicly on 2026-10-03 solely for primitive feasibility. No broad provider survey, credentials or executing documentation examples. Web-rendered freedesktop pages were inaccessible; upstream systemd documentation was read instead, then pinned to the public commit below. Kernel docs/man-pages are upstream primary references. Moving docs are dated cache bindings, not the version of an installed Host. No source establishes a numerical qualification/fault or financial bound for this absent environment.

| ID | Source / owner / relevant scope | Bytes | SHA-256 |
| --- | --- | --- | --- |
| L01 | [Linux kernel cgroup v2: resource/membership/kill interfaces](https://docs.kernel.org/admin-guide/cgroup-v2.html) | 172971 | `6EFABE7ED748F1D863859A0E5C50E770E47255C9A071BF878F6460E7E01C0563` |
| L02 | [Linux kernel seccomp BPF: filtering, not complete sandbox](https://docs.kernel.org/userspace-api/seccomp_filter.html) | 38437 | `419DE4141B38BCE8754DE25A28902CFB8F7BC98FC6F1C9C9640983CC5BC8065D` |
| L03 | [Upstream Linux man-pages namespaces(7): partitioned views](https://man7.org/linux/man-pages/man7/namespaces.7.html) | 25329 | `F8E08716DF1F4AFDF05B22E11B010E14F47311EB92F0A948FEDBB95099C36AA7` |
| L04 | [Linux kernel quota subsystem: filesystem quota facility](https://docs.kernel.org/filesystems/quota.html) | 13430 | `D9D456E70A7465DFCDFEA1ADDFFCCFEDBBB0124DEF8A05630432140F46EAB140` |
| L05 | [Linux kernel watchdog API: device-dependent reset behavior](https://docs.kernel.org/watchdog/watchdog-api.html) | 24828 | `0E0D19BBCE5CCCA8D22DC8CBF754CF626E9D723B144C029477235326C69882D0` |
| L06 | [Upstream systemd.service: timer/type/notification lifecycle](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.service.xml) | 120642 | `12770F86A26DCDF32873225669F5AA9421283C303BBC72BDDB04530850F66D44` |
| L07 | [Upstream systemd.kill: control-group termination and escalation](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.kill.xml) | 11224 | `448322830DBBD02C64CCA99941BA92705AFE9648241FC917DB7A8D6AE7910E72` |
| L08 | [Upstream systemd.exec: execution environment/root/input facilities](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.exec.xml) | 343315 | `44B89BFFCE737AFF803966C207329E9FE2D28AD07709A4BB8E0EDF6A4EC0D844` |

Systemd documentation commit: `0794ba0045d11d4227f61ebacf7d75983ba884f1` (2026-10-02T22:09:19Z); not an installed package or supported Host selection. Cached public bytes and retrieval metadata: `D:\chatgpt\安装skills\output\p5-p6-safety-rebaseline-2026-10-03`. No source was imported/run.

The controller-loss/finite-envelope composition, component difficulties, fixed-cost cases and roadmap above are **PROPOSAL / DESIGN INFERENCE**, not platform promises. Present Route D hard-bound completeness, installed capabilities, privileges, runtime negatives, cost basis and evidence collector are UNKNOWN. Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD. Sealed V4, accepted A0-A6/P1-P12 and historical routes unchanged. This study touches no Host, paid resource or secret.
