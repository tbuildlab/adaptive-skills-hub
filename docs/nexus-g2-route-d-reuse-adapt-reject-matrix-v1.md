# Nexus G2 Route D Reuse Adapt Reject Matrix v1

Version: `1.0.0`

Date / source retrieval: **2026-10-03**

Baseline: `8818b0b674878f016a779197a6f04cb0c5b3a39f` / `nexus-v2-g2-development`

Status: **D-REF FACTUAL / DESIGN CHECKPOINT ONLY - NOT ACCEPTED; NO HOST OR EXPERIMENT AUTHORITY**

## 1. Meaning and license screen

REUSE means direct reliance is plausible for the exact component's supported scope, not package installation/selection or qualification. ADAPT means fixed typed integration and configuration/custody, not copying a runtime. REJECT applies to the named mechanism/default/misuse, not a global claim the project is insecure. NEXUS_OWNED identifies nondelegable governance decisions. All rows are proposals; source IDs resolve in the [register](nexus-g2-route-d-reference-source-register-v1.md) and trust boundaries in the [survey](nexus-g2-route-d-external-reference-survey-v1.md).

License screen: not legal advice or a concrete redistributable-product approval. System-call use/external IPC/CLI invocation, linking libraries, modifications and bundling distributions are distinct acts. Every future selected version must receive a dependency/image/kernel/license inventory; no source was copied into Nexus. Prefer supported external components rather than copying security code and assuming responsibility for its patch stream.

| Project / binding | License observed | Reuse class | Direct dependency / modification / attribution / linking / distribution consequence |
| --- | --- | --- | --- |
| Firecracker FC06/FC07 | Apache-2.0 + NOTICE | DIRECT_REUSE_PLAUSIBLE | Use/modification possible under terms; preserve license/applicable NOTICE and mark changed files; binary dependencies/guest assets separately reviewed; executable IPC differs from linking. |
| Kata KA04 | Apache-2.0 | WRAPPER_INTEGRATION_PLAUSIBLE | Same Apache notice/change conditions; VMM, kernel, images, virtiofsd and plugins carry independent licenses; no Apache-only guest-stack claim. |
| gVisor GV02 | Apache-2.0 | WRAPPER_INTEGRATION_PLAUSIBLE | runsc/Sentry reuse plausible; retain terms/notices and dependency inventory, do not copy/rebuild application kernel inside Nexus. |
| nsjail NJ06 | Apache-2.0 | WRAPPER_INTEGRATION_PLAUSIBLE | External fixed CLI/config feasible in principle; Kafel/libraries separately scoped; modification/redistribution require applicable notices/change marking. |
| Linux CG/NS/SC/LK01-LK02 | Kernel GPL-2.0 with Linux-syscall-note; per-file exceptions | DIRECT_REUSE_PLAUSIBLE | OS interfaces do not automatically relicense an independent userspace program; kernel copying/modification/distribution have source/license obligations. Headers/docs have per-file licenses; no kernel source vendoring. |
| systemd SD04/SD05 | Default LGPL-2.1-or-later, explicit exceptions | WRAPPER_INTEGRATION_PLAUSIBLE | External manager/DBus differs from libsystemd linking; modified LGPL/bundled binaries require applicable source/notice duties. Static linking/relinkability and exact library version need LICENSE_REVIEW_REQUIRED; udev GPL exceptions preserved. |
| runc RC04 / OCI OC03 | Apache-2.0 | WRAPPER_INTEGRATION_PLAUSIBLE | External runc/spec use or library linking still needs all dependency terms/notices; avoid copying libcontainer into Nexus. |
| containerd CD03 | Apache-2.0 | WRAPPER_INTEGRATION_PLAUSIBLE | Retain notices and assess shim/plugins/snapshotters/runtime/image licenses; no daemon/plugin vendoring justified. |
| bubblewrap BW02/BW03 | Core SPDX LGPL-2.0-or-later; COPYING contains LGPL-2.1 text | WRAPPER_INTEGRATION_PLAUSIBLE | Keep per-file version distinction; binary/source distribution obligations remain. Linked/copied modifications require LICENSE_REVIEW_REQUIRED; external CLI preferred over source copying. |
| Kubernetes KJ02 / docs KW04 | Code Apache-2.0; website docs CC-BY-4.0 | PATTERN_ONLY | No cluster dependency/code copying proposed; paraphrase with source links. Copied/adapted docs need attribution/change/license compliance; code redistribution separate. |

Apache static versus dynamic linking does not erase license/notice/patent terms; LGPL static linking can require relinkable material where applicable. Vendoring increases license/CVE/change tracking and trust surface even with permissive terms. No final distribution/static-link design is selected. No inspected major project is rejected solely for its license; exact combination clearance remains UNKNOWN.

## 2. Concrete reuse decisions and required wrapper

Each row states component, trust, wrapper/configuration, residual UNKNOWN and requalification trigger. Required configurations are design obligations, not runnable config files or accepted mechanisms. A manager/fence is not independently qualified merely because it is mature.

| ID | Component / sources | Class | Trust and fixed wrapper / required configuration | Remaining UNKNOWN | Invalidation trigger |
| --- | --- | --- | --- | --- | --- |
| R01 | Firecracker VMM + matching jailer FC01/02/05 | REUSE | Patched Host KVM/hardware and protected matching binaries; fixed image/UID/device/API/netns/cgroup inputs, placement readback before guest start | Actual release/support, loaded bytes, fault/deadline, broad socket denial and numerical limits | VMM/jailer/kernel/image/device/cgroup/socket actor change |
| R02 | Firecracker snapshot/device/log plumbing FC03/04 | ADAPT | Disable nonrequired snapshot/MMDS/device features; finite Host backing/output; independent lifecycle unit | Orphan/stalled VMM/survivor/serial/tail handling | Snapshot/resume/log/device/profile or price graph change |
| R03 | Kata supported shim/VMM/guest stack KA03/05 | REUSE | Pin complete Host/guest chain; one fixed unit rather than arbitrary pod/multicontainer/API selection | Guest-independent Host cessation, exact support and TCB size | Hypervisor/shim/agent/image/container grouping change |
| R04 | Kata resource/network/filesystem integration KA06/07/08 | ADAPT | Bound guest plus VMM/shim/virtiofsd/IO overhead, finite quota/store, minimal shares and no network first | Effective overhead topology, resource propagation, quota/channel closure | sandbox_cgroup_only, sharing/backend/plugin/controller change |
| R05 | gVisor runsc/Sentry/Gofer GV01/03-07 | REUSE | Fixed platform and filesystem mode, no Host-network bypass, no workload control socket; bound all Host helpers and virtual task count | Actual compatibility/resource/byte/cancel behavior and Gofer/directfs coverage | Platform/directfs/network/helper/guest task semantics change |
| R06 | nsjail namespace/mount/seccomp/rlimit/cgroup setup NJ01/03-05 | REUSE | Frozen fixed config and inputs; no listen/general command service; independent protected cgroup/manager | Userns/privilege/delegation, aggregate limits, default policy and negatives | Config/mode/Kafel/kernel/library/network-helper change |
| R07 | nsjail parent-race/PDEATHSIG containment NJ02/03 | ADAPT | Supplementary parent-loss guard only; independent conserved deadline and Host fallback | Clock/monitor/kernel loss and full subtree cleanup | Parent/clock/identity/namespace or monitor behavior change |
| R08 | cgroups v2 kernel resource/subtree interfaces CG01 | REUSE | Protected nondelegated workload subtree, enabled controllers, finite CPU/RAM/swap/tasks/IO scope and readback | Installed kernel/topology/overrun/task accounting/termination latency | Kernel/controller/scheduler/delegation/migration change |
| R09 | systemd service/transient lifecycle SD01-03/06-08 | REUSE | Narrow typed fixed operations; pre-exec attachment, bounded start/run/stop, no notify extension/restart/random extra/DBus access | Actual applied ordering, effective inputs, manager/kernel failure fence | Unit type/hooks/dependency/restart/property/manager version change |
| R10 | Supported quota/finite backing workspace QT01 | REUSE | Independent bytes/inodes/log/snapshot coverage and expiry, not IO-throttle substitution | Chosen filesystem/quotas/support/retained-object scope | Filesystem/mount/project-ID/logging/persistence change |
| R11 | runc/OCI create-start-query barrier OC01/02 RC01-03 | REUSE | Fixed trusted bundle/runtime root, hooks excluded or separately admitted; denied update/exec/recreate surface; actual effective pre-start checks | Byte/provenance and whole-unit rootless/delegation failure behavior | Runtime/hook/bundle/capability/rootless/cgroup/PID mode change |
| R12 | containerd runtime-v2 shim and references CD01/02 | ADAPT | Only if daemon/state/plugins needed; fixed runtime path/options, protected socket, single original unit and explicit task/snapshot/content cleanup | Shim grouping/reconnect/orphan/cleanup tail/evidence coverage | Daemon/shim/plugin/runtime/snapshotter/API actor change |
| R13 | bubblewrap construction BW01/02 | REUSE | Fixed reviewed argument policy; no owner sockets/broad mounts; close FDs/TTY, apply external limits/deadline | Actual userns/privileges, applied inputs, parent-death and resources | bwrap/policy/kernel/FD/terminal/mount change |
| R14 | Existing namespaces/seccomp/capability/optional Landlock NS/SC/CP/LL/LK03 | REUSE | Supported exact ABI and least privilege; omit no mandatory restriction through best-effort compatibility | Actual kernel/LSM support, policy closure and escape negatives | Kernel/ABI/profile/capability/device/share change |
| R15 | Kubernetes identity/conditions/cleanup patterns KW01-03 KJ01 | ADAPT | Extract original UID and desired/observed divergence into Nexus records; no automatic availability retries | Exact task effect/no-effect query and durable evidence | Identity/replacement/retention/effect schema change |
| R16 | Boot orphan inventory/protected owner state | NEXUS_OWNED | Default-deny admission, original grant/lease/budget refs; native query before cleanup; no new grant after reboot | Actual boot barrier/store/fence semantics and reconciliation | Boot/clock/storage/policy/authority binding change |
| R17 | Authority/budget/evidence/retry/qualification decisions | NEXUS_OWNED | Owner-issued then-valid grant, pre-effect admission/reserve, exact graph, protected receipts, refusal while UNKNOWN | Actual controller custody/financial source/operation observations | Any accepted policy/credential/rate/actor/capability/material drift |
| R18 | Independent outer lifecycle fence WD01 + future existing infrastructure | ADAPT | Reuse a supported separately controlled mechanism with predeclared numerical consequence; no invented custom isolation engine | Availability/privilege, clock and common-fault coverage | Device/hypervisor/manager/failure-mode/timer change |

## 3. Rejected mechanisms and anti-patterns

These are Nexus design exclusions; a source warning/example identifies risk, not proof of a deployed vulnerability. No named project is declared insecure wholesale.

| ID | Pattern / example | Why REJECT for the candidate Nexus boundary |
| --- | --- | --- |
| X01 | Fail-open policy/optional cgroup errors, FC05 absent parent path; RC02 shared-PID rootless fallback | Required actual limits must be independently positive before release; requested settings/warnings are not PASS |
| X02 | approval=never or capability possession alone | No independently issued task authority; interface access cannot mint grants |
| X03 | Workload notify/keepalive/deadline/restart/resume control SD06 KW01 | Guest can extend/reset exposure; deny or independently conserve original lease |
| X04 | Client-only timer / monitor-only nsjail deadline NJ02 | Controller/monitor loss and clock change defeat sole enforcement |
| X05 | Generic privileged daemon exposing shell or arbitrary runtime/hooks SD03 CD01 OC01 | Confused deputy / broad privilege; fixed typed profile only |
| X06 | Docker/containerd/runtime socket in workload | Broad Host control channel; no Docker dependency proposed |
| X07 | Broad writable Host mount/share BW01 KA07 GV04 | Files/services/devices/authority escape and substituted bytes |
| X08 | Controller credentials in env/image/guest/snapshot | Workload gains mutation/paid-effect authority; evidence must contain no secret values |
| X09 | Blanket Host CAP_SYS_ADMIN / privileged container CP01 | Broad Host TCB expansion; not justified by a fixed capability |
| X10 | Host PID namespace / unbounded rootless resource fallback RC02 | Descendant control/observer/credential separation weakened |
| X11 | Host network or broad Internet mode GV07 FC01 | No exact channel/effect graph; VM/net stack alone not policy |
| X12 | Retry/replacement after UNKNOWN KW01 KJ01 | May duplicate side effects and cumulative cost; original refs retained |
| X13 | Guest agent/log/self-report as final PASS | Subject cannot certify isolation/provenance/cleanup; protected external evidence required |
| X14 | kill/delete/not-found = successful cleanup | Request/API state differs from zero-live, storage, late effects and bill settlement |
| X15 | Broad stdio MCP/general helper execution on Host | New indirect ungoverned effects/credentials; no MCP route authorized |
| X16 | Automatic fallback to weaker runtime / unqualified rootless mode | Material boundary change requires invalidation/review, not availability fallback |
| X17 | Snapshots restoring grants/deadlines; unlimited log/serial/image retention FC03/04 | Persistence and resumed exposure bypass original envelope |
| X18 | Shared-kernel watchdog/agent/manager advertised as independent of kernel failure | Different processes are not separate F4-F6 failure domains |

No anti-pattern is repaired through installation, new daemon, policy change or implementation here. [Review](nexus-g2-route-d-reference-adversarial-review-v1.md) challenges each reuse row.

Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD. D0-D7 NOT STARTED. Route B unresolved; OpenAI human escalation PENDING. Accepted architecture/A0-A6/P1-P12 and sealed V4 unchanged. No installation, Host/provider execution, credentials, paid activity, privileged/system changes, G2/G3/G4 implementation, acceptance, merge/push/tag/freeze.
