# Nexus G2 Route D Reference P1-P12 HQ Mapping v1

Version: `1.0.0`

Date / source retrieval: **2026-10-03**

Baseline: `8818b0b674878f016a779197a6f04cb0c5b3a39f` / `nexus-v2-g2-development`

Status: **D-REF FACTUAL / DESIGN CHECKPOINT ONLY - NOT ACCEPTED; NO HOST OR EXPERIMENT AUTHORITY**

## 1. Documentary matrix semantics

Columns: Firecracker, Kata, gVisor, nsjail, systemd/cgroup, runc/containerd, bubblewrap, Kubernetes-patterns. These are **DOCUMENTED COMPONENT CONTRIBUTIONS**, never whole-row candidacy/qualification PASS. DIRECT_SUPPORT describes a native mechanism for the scoped subproperty named in this analysis, not complete accepted P/HQ outcome. PARTIAL_SUPPORT has relevant features but missing coverage; COMPOSABLE_SUPPORT requires other reviewed components; PATTERN_ONLY transfers a design idea; NOT_RELEVANT supplies no applicable enforcement; CONTRADICTORY identifies default behavior if copied into Nexus; UNKNOWN lacks adequate examined semantics. Source scope, configuration and open gaps in [survey](nexus-g2-route-d-external-reference-survey-v1.md) and [reuse](nexus-g2-route-d-reuse-adapt-reject-matrix-v1.md) are mandatory qualifiers for every cell; exact bodies in [register](nexus-g2-route-d-reference-source-register-v1.md).

No uniform DIRECT_SUPPORT is awarded to P5/P6/P7 because no entire independent lifetime/financial/failure/physical-state envelope was established. A mature implementation can help HQ1-HQ4; HQ5/HQ6 decisions remain Nexus-owned even when native facts are useful. No matrix cell starts HQ6 or qualifies a Host.

## 2. P1-P12: 96 cells

| Gate | Firecracker | Kata | gVisor | nsjail | systemd/cgroup | runc/containerd | bubblewrap | Kubernetes-patterns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PATTERN_ONLY |
| P2 | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | PATTERN_ONLY |
| P3 | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | PARTIAL_SUPPORT | PATTERN_ONLY |
| P4 | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | PATTERN_ONLY |
| P5 | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | PARTIAL_SUPPORT | PATTERN_ONLY |
| P6 | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | NOT_RELEVANT | NOT_RELEVANT |
| P7 | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | PARTIAL_SUPPORT | PATTERN_ONLY |
| P8 | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PATTERN_ONLY |
| P9 | PATTERN_ONLY | PATTERN_ONLY | PATTERN_ONLY | UNKNOWN | PATTERN_ONLY | PATTERN_ONLY | UNKNOWN | CONTRADICTORY |
| P10 | PATTERN_ONLY | PATTERN_ONLY | PATTERN_ONLY | PATTERN_ONLY | COMPOSABLE_SUPPORT | PATTERN_ONLY | PATTERN_ONLY | PATTERN_ONLY |
| P11 | NOT_RELEVANT | NOT_RELEVANT | NOT_RELEVANT | NOT_RELEVANT | COMPOSABLE_SUPPORT | NOT_RELEVANT | NOT_RELEVANT | PATTERN_ONLY |
| P12 | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PATTERN_ONLY |

| Gate | Cell-specific source basis / exclusions | Nexus still owns |
| --- | --- | --- |
| P1 | FC process/ID, KA sandbox/VMM, GV container/sandbox, NJ tracked child, SD unit/cgroup, RC OCI/CD task refs and BW status; none proves admitted loaded bytes automatically. K8s UID/generation pattern only. | Exact admitted code/dependencies/unit/operation/source/Host/boot binding; actual check-to-use closure |
| P2 | Every runtime has trusted config/manager/Host input outside workload. That actor/credential/socket split is a component; it is not attenuated Nexus task authority. | Grant/actor closure, denied widening/replay and secure custody |
| P3 | Namespace/cgroup/VM/Sentry state contributes applied restriction observation; runtime desired config requires external effective cross-check. | Source/scope/freshness, mutation exclusion, negative evidence and release barrier |
| P4 | Runtime mount/device/namespace/env/FD channels vary; VM agent/shares and Sentry Gofer count. K8s templates do not close indirect channels. | Finite admitted input/effect graph and independent secret/handle/descriptor observations |
| P5 | Resource/lifecycle components combine; none alone covers all Host/guest/helpers/faults. BW lacks aggregate resource/lifetime manager; K8s deadline depends on control plane/node. | Numerical whole-unit conserved envelope, independent fallback, actual qualified scope |
| P6 | First six columns help hard quantities only with independent lifetime/price/retention bounds; no native cost admission/contract is claimed. BW/K8s patterns do not provide bill cap. | All billable drivers/contract horizon/rates/headroom/reservation and UNKNOWN settlement |
| P7 | Native signal/stop/delete/Destroy/status help; absence of controller/manager-fault cutoff or zero-live scope prevents standalone equivalence. | Ordered states, exact-original observation, late effects, cessation/cleanup/financial separation |
| P8 | Metrics/log/status/task exit are scoped native facts, not artifact acceptance or effect truth. | Validation, retention/coverage, independently observed task effects and source custody |
| P9 | VM/runtime state and query/reconnect support patterns, not exactly-once. NJ/BW have insufficient durable original-effect reconciliation. K8s default replacement conflicts with Nexus no-retry-after-UNKNOWN if copied unchanged. | Durable original attempt/UNKNOWN/no-effect proof; no blind replacement |
| P10 | Native logs/metadata and protected manager interfaces may contribute observations but no project certifies Nexus receipt truth. | Protected writer/storage/source/order/config/unit binding and contradictions |
| P11 | SD exec isolation facilities may help keep a separately qualified secret facility outside guest; no generic credential broker inferred. K8s secret/RBAC concepts pattern only. | Owner facilities/BYOK, current safe custody and revocation invalidation; no developer bundled key |
| P12 | Source pins/version/state support scoped revalidation; no automatic public main -> installed release equivalence. | Material drift/expiry/config/actor/price/dependency invalidation and requalification |

## 3. HQ1-HQ6: 48 cells

| Gate | Firecracker | Kata | gVisor | nsjail | systemd/cgroup | runc/containerd | bubblewrap | Kubernetes-patterns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HQ1 | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PARTIAL_SUPPORT | PATTERN_ONLY |
| HQ2 | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | PATTERN_ONLY |
| HQ3 | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | PATTERN_ONLY |
| HQ4 | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | PARTIAL_SUPPORT | PATTERN_ONLY |
| HQ5 | PATTERN_ONLY | PATTERN_ONLY | PATTERN_ONLY | PATTERN_ONLY | COMPOSABLE_SUPPORT | PATTERN_ONLY | PATTERN_ONLY | PATTERN_ONLY |
| HQ6 | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | COMPOSABLE_SUPPORT | PARTIAL_SUPPORT | PATTERN_ONLY |

HQ1 actual provenance is a separate experiment obligation; no tag/hash/path-only PASS. HQ2/HQ3 configuration/mounts/devices/FDs/sockets/credentials need effective negatives at the true boundary. HQ4 tree/resource/manager/fault/boot exposure needs a finite independent fallback and original-identity observations. HQ5 is Nexus protected adjudication, not child/native-log certification. HQ6 is one accepted capability's pre-effect grants/budget/operation/cancel/effect/recovery primitive binding, not implementing G2 or absorbing responsibility into a runtime. All current statuses remain unchanged.

## 4. P5 dimensions and failure reach

Each row covers CPU/RAM/tasks/disk/network/persistence as applicable, plus lifetime/controller/manager/reboot/ultimate state. Actual quantities and behavior are UNKNOWN everywhere. Source IDs bind the detailed qualifications, not universal project guarantees.

| Primitive | Lifetime / ultimate cutoff | CPU / RAM / tasks / disk | Descendants / network / persistence | Controller and manager loss / reboot |
| --- | --- | --- | --- | --- |
| Firecracker FC01-05 | Guest shutdown/VMM signal; no checked immutable total lease; Host manager/fence needed | vCPU/RAM/device rates plus Host cgroups; guest tasks, backing bytes/logs/serial separately bound | VM holds guest descendants; Host helpers/taps/API/shares must close; files/snapshots survive process | Remote controller death need not stop VMM; Host manager/kernel fault independent coverage missing; boot inventories originals |
| Kata KA03/05-08 | Agent/runtime/VMM destroy chain plus independent Host unit | Host AND guest ceilings; overhead topology/virtiofsd and disk quotas separate | VM/container/process layers; plugin net and shared storage/control RPC part of graph | Shim/agent/daemon loss not cessation; manager/fence must cover actual VMM/helpers; boot orphan refs conserved |
| gVisor GV01/03-07 | runsc/Sentry/Gofer terminate paths plus external conserved deadline | Host CPU/RAM and virtual task limits differ; backing/Gofer/log disk needs quotas | Virtual tasks need Sentry plus Host-helper observation; net modes/directfs/shares affect boundary | Detached state can outlive caller; manager/kernel/platform fault scope unproved; restore/boot never refresh authority |
| nsjail NJ01-05 | Monitor-loop clock/kill and parent-death guard; external hard lifetime needed | cgroups/rlimits where supported; file-size != aggregate disk | Namespace/PID/cgroup and denied migration; configured network/helper/mount paths; parent cleanup not storage proof | Monitor loss mitigated in some parent paths, not common-kernel fault; finite independent fallback still required |
| systemd/cgroups SD/CG/QT/WD | Manager timer with type/notify/restart/start-stop caveats; cgroups no wall deadline | CPU bandwidth, memory/swap/overrun, Host tasks, IO; quota capacity separate | Protected subtree/all helpers; no delegated mutation; namespace/network/filesystem layer still needed | Manager separate from Host Agent but shares kernel/OS/Host; boot cleanup alone cannot bound never-rebooted work |
| runc/containerd RC/CD/OC | create/start/kill/delete/shim supervise; independent manager deadline | OCI/cgroups actual delegation/controller scope; image/snapshot/log bytes separate | Private PID vs shared/rootless fallback; shim groups, hooks, exec and net outside unreviewed graph forbidden | Runtime command/daemon death not task death; reconnect/state and boot orphan inventory are components, not deadline |
| bubblewrap BW01/02 | Parent-death only where enabled; no aggregate resource/independent lifetime manager | Namespace/rlimit construction insufficient; independently delegated cgroups/quota required | Caller-selected PID/net/mount/FD/TTY/seccomp policy; no retained-file expiry implied | Parent death guard not all-fault fence; kernel/manager/boot/effect behavior needs external composition |
| Kubernetes KW/KJ patterns | activeDeadlineSeconds/grace depend on controller/kubelet; suspend/retry/reset not conserved lease | Scheduler/resource settings eventually applied at node; storage/network/provider charges separate | Pod/Job owner objects not full effect tree; finalizers/GC/PVC/share lifetime independent | Controller/node partition/daemon reboot/object absence cannot establish physical cessation; borrow patterns only |

## 5. P6 and P7 separation

None is a billing platform or a conservative all-in price source. Hard quantity mechanisms can contribute to P6 only with finite lifetime/failure/survivor/overshoot, maximum prices or exact finite fixed-host obligations, current headroom and separately bounded model/API/paid effects. A VM RAM size, byte/sec limiter, quota or fixed monthly advertised fee is not whole-unit money cap. Kernel/systemd/runtimes cannot bound an external paid API by local termination; independent service scope is required. All eight columns therefore need Nexus-owned admission/arithmetic/UNKNOWN reservation and authoritative external cost terms; no actual zero-cost assertion.

Preserve eleven independently scoped states: CANCEL_REQUESTED, CANCEL_ACKNOWLEDGED, EXECUTION_STOPPING, EXECUTION_CEASED, DESCENDANTS_CEASED, SANDBOX_TERMINATED, PERSISTENT_RESOURCE_STATE_KNOWN, RESOURCE_RELEASED, BILLING_CEASED, RESULT_OBSERVED, EFFECTS_RECONCILED. Runtime exit/shim event/guest agent response may establish one scoped fact only. Required descendants include Host helpers and relevant virtual/guest tasks; zero Host pids does not release disk/external effects. Billing boundedness does not mean settlement; no bill/log/result means UNKNOWN, not zero. Manager/fence evidence itself must be trustworthy and bound to original unit.

## 6. Failure domains F0-F9

| ID | Domain | What if the protection also fails? / correlated risk |
| --- | --- | --- |
| F0 | Workload | Ignore signals, fork/log/network/IO, mutate inputs; native nonrelaxable envelope must remain |
| F1 | Sandbox runtime | nsjail monitor, Sentry/Gofer, runc/shim, VMM or guest agent stalls; external manager/fence must contain original |
| F2 | Host Agent | No new admission/recreation; independently installed lease and durable refs survive its loss |
| F3 | Host lifecycle manager | PID1/unit/daemon/watchdog path stalls; same-process timer cannot substitute; qualified outer mechanism or STOP |
| F4 | Host kernel | cgroups/namespaces/seccomp/manager/Host watchdog may all share stalled kernel; no universal SIGKILL bound |
| F5 | Host OS | Boot/config/state/policy/clock compromise/failure affects all local userspace; reboot admission barrier and protected state needed |
| F6 | Physical/virtual Host | Hypervisor/device/power failure; ordinary compute may cease but storage/effects survive; outer fence availability/latency/independence unknown |
| F7 | Nexus Controller | Prior finite grant cannot widen; conserved original exposure/UNKNOWN, no blind retry; Host independent cutoff |
| F8 | Controller-Host network | Requests/acks lost while work continues; query original when possible, refuse recreation, hard native lifetime remains |
| F9 | Evidence store | Lost/forged/expired records STOP admission/acceptance/retry; hard containment independent; no recursive invented assurance |

| Architecture | Correlation specific to the family / required future evidence |
| --- | --- |
| Firecracker | VMM threads/jailer process share Host KVM/kernel; VM boundary protects guest escape but not stalled Host manager/kernel; API/log/backing paths and outer cutoff must bind |
| Kata | Guest agent/guest kernel form one side; shim/VMM/virtiofsd/Host manager share Host side; guest kill cannot prove Host helper cessation |
| gVisor | Sentry/Gofer/platform and Host cgroups share Host kernel; virtual task visibility cannot be inferred from Host process inventory |
| nsjail | Monitor/parent-death/resource controllers share Host OS/kernel; a second userspace watcher is not independent of F4-F6 |
| systemd/cgroups | Host Agent + watchdog + PID1 can be separate processes but still one F4-F6 domain; timer extension/delegation changes independence |
| runc/containerd | Runtime command, long-lived shim and daemon are distinct; command/daemon loss may leave live tasks and persistent snapshots |
| bubblewrap | Wrapper/caller/PID1/parent-death paths share kernel; no independent deadline/financial store |
| Kubernetes-patterns | Controller/APIServer/store/node/kubelet/CRI separation adds partitions and replacement ambiguity; not imported as first Route D infrastructure |

Fail-safe order: independent authorized limits/fallback and protected original admission BEFORE allocation; actual identity/input/limit/loaded-byte observations BEFORE instructions; original stop/cancel/zero-live/survivor/effect/cost records retained AFTER failure. If a failure violates a required independent boundary, no averaging or new unit repairs it. All runtime negative tests remain unrun.

Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD. D0-D7 NOT STARTED. Route B unresolved; OpenAI human escalation PENDING. Accepted architecture/A0-A6/P1-P12 and sealed V4 unchanged. No installation, Host/provider execution, credentials, paid activity, privileged/system changes, G2/G3/G4 implementation, acceptance, merge/push/tag/freeze.
