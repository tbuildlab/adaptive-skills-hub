# Nexus G2 Route D D1 Threat Model v1

Version: `1.0.0`

Date: **2026-10-03**

Starting baseline: `a0bdfd2b6ea46844d317dff67687e681caacc3c3` / `nexus-v2-g2-development`

Status: **FACTUAL / DESIGN CHECKPOINT ONLY - NOT ACCEPTED; NO IMPLEMENTATION OR EXPERIMENT AUTHORITY**

## 1. Conclusion and declared threat scope

Threat model documented with material residual UNKNOWNs U01-U05 in [D0](nexus-g2-route-d-d0-requirements-v1.md). Malicious/buggy guest and accidental runtime/Agent/manager/kernel/OS/Host/controller/network/store failures remain relevant. Controller compromise is bounded only by an independently issued fixed grant and Host-enforced conserved slot. Owner/grant issuer, admitted Host root, kernel/hypervisor/hardware and protected infrastructure are named TCB; arbitrary malicious ultimate-TCB compromise is not promised to be contained. Their accidental stall/panic/boot/storage faults are not removed to obtain a favorable result. A TCB change needs owner acceptance. No attack or fault was executed.

## 2. Trust boundaries TB0-TB11

Trusted/untrusted is relative to the stated function; a trusted transport peer cannot authoritatively assert kernel limits. All credentials below are conceptual custody locations, never accessed. Evidence destination holds status and references, no credential values/hashes.

| Boundary | Trusted side / untrusted side | Credentials / authority | Accepted data and validation | Failure consequence / evidence |
| --- | --- | --- | --- | --- |
| TB0 Owner | Independent issuer and infrastructure decision / model or proposed request | Existing issuer facility; finite task/design grant | Scope/subject/expiry/budget and owner decision; verify independent issuance | Forged/ambiguous grant refuses effects; owner grant/decision reference |
| TB1 Nexus Controller | Protected governance/admission / guest/Host-provided claims | Narrow Host control authentication outside guest; validates grant, does not mint it | Original intent/reservation plus scoped observations; identity/source/freshness/order | Controller loss retains exposure; native cutoff must survive; durable intent/checkpoint |
| TB2 HostAdapter | Typed transport mapping / task fields and remote response | Controller transport identity, fixed operations only | Length/schema/operation/profile/native refs; no arbitrary shell/paths/hooks | Confused deputy or hidden retry; request/response/gap evidence, never standalone limit proof |
| TB3 Host admission endpoint | Protected Host verifier / authenticated but possibly compromised requester | Narrow admitted create/status/stop capability; no unlimited root authority | Then-valid independent grant, config, single slot, deadlines, budget reservation binding; reject replay/widening | Unauthorized allocation if bypassed; pre-admission refusal/accepted original-slot record |
| TB4 Host Agent | Fixed integration/collection / workload artifacts/runtime errors | Only fixed allowed manager/runtime operations; none in guest | Closed profile and stable original refs; no workload-selected command/config | Agent loss cannot release/renew; Host journal and missing-observation record |
| TB5 Lifecycle manager | Protected mature supervisor / Agent request and guest processes | Restricted manager authority; guest has no DBus/notify/restart rights | Fixed unit identity, start/stop phase bounds, tree properties; actual readback | Manager loss shares kernel; outer fence needed; manager events/phase identities |
| TB6 Isolation runtime | Pinned supported setup/runtime / bundle and guest syscall traffic | Minimal setup privileges; workload receives dropped rights | Protected input/dependency/mount/device/FD config, no hooks/sockets; external barrier | Escape/helper leak/stall; effective runtime membership/config observations |
| TB7 Kernel | Admitted Linux enforcement / workload/runtime user requests | Kernel and constrained setup capabilities; no guest host-admin privilege | Namespace/cgroup/LSM/seccomp policy and resource operations at exact scope | Common isolation/lifecycle failure; external fence evidence distinct from kernel readback |
| TB8 Execution unit | Protected enclosing allocation / workload and outputs | No control secrets; no persistent grant; no generic privileged MCP/stdio | Bounded staged input; outputs always data, validate bytes/types/paths | Guest forgery/resource attack; GUEST_ASSERTED logs, separate external limit observations |
| TB9 Evidence storage | Protected writer/source validation + Controller copy / guest and partial/replayed bytes | Store write credentials outside guest; write authority scoped to original attempt | Sequence, identity, observation source, hashes, status, durable ack and explicit gaps | Loss/tamper blocks acceptance/retry; no inferred success; source/store acknowledgment |
| TB10 Network boundary | Kernel/qualified external network policy / guest channels | No guest proxy/metadata/control credential | Closed FD/DNS/IPv4/IPv6/helper graph; qualification/config binding | Leak/paid effects; external namespace/policy/flow observation; no-network first |
| TB11 External APIs/services | Supported service receipt/limit semantics / guest request and lost responses | Future broker keeps service secret; task token only if separately accepted | Exact effect/grant/maximum/idempotency/query scope and provider-authenticated refs | Accepted effect can outlive local compute; provider effect/cost observations and UNKNOWN |

TB11 is unreachable in first fixture except separately admitted Host control transport; no external task API access. A workload token, if ever proposed, must be opaque, one-operation/attempt-bound, fixed endpoint/action/bytes/call/max-cost/deadline constrained, audience/expiry/replay protected, unable to mint infrastructure or model authority. Do not pass an owner/API key. An outside-workload existing broker must independently enforce limits and reconcile the original service effect. Final token/credential protocol is deferred; the prototype uses no token.

## 3. Failure domains F0-F9

KNOWN_SUCCESS means required task/terminal/effect facts positively established, not merely that a protective kill occurred. KNOWN_FAILURE means a positive denied/failed operation with bounded, observed consequences; unresolved cleanup/effect facts can coexist as UNKNOWN. Each domain can yield UNKNOWN if decisive evidence is absent. No failure always has a known outcome.

| Domain | Independence and correlation | Containment / recoverability | Result classification |
| --- | --- | --- | --- |
| F0 Workload | Process-local fault possible; resource pressure propagates to F1-F5/F9 | Native hard limits; terminate original subtree; validate output; no blind retry | KNOWN_SUCCESS only on validated useful result; KNOWN_FAILURE on observed fault with known effects; otherwise UNKNOWN |
| F1 Sandbox runtime | Separate process from Agent in some modes; helpers/guest paths share F4-F6 | External manager/outer fence; query all original helpers/guest tasks; repair only after reconciliation | KNOWN_FAILURE if fault+cessation/effects established; otherwise UNKNOWN |
| F2 Host Agent | Can fail alone; storage/CPU/kernel correlated F3-F6/F9 | Prior manager/fence lease survives; admission closed; later reconcile original refs | UNKNOWN at disconnect, later known failure/success only from external facts |
| F3 Lifecycle manager | Distinct from Agent but common kernel/OS/time/storage F4-F6/F9 | Existing independent outer fence required; no same-manager watchdog proof | UNKNOWN until independent cessation/cleanup evidence; observable violation KNOWN_FAILURE |
| F4 Kernel | All local enforcers/readbacks correlated; no userspace control is independent | Hypervisor/hardware domain fence candidate; no finite SIGKILL latency assumed | UNKNOWN without supported external observation; no post-panic task-success inference |
| F5 OS | Config/boot/clock/storage can affect Agent/manager/runtime/kernel | Default-deny boot, no resurrection, durable external intent and outer control | UNKNOWN for past effects; KNOWN_FAILURE only with original scope reconciled |
| F6 Physical/virtual Host | Guest OS/Host power/device and hypervisor may share physical failure | External power/hypervisor receipt if qualified; retained disks/effects survive | Positive off may prove scoped cessation, not success/cleanup; remaining facts UNKNOWN |
| F7 Controller | Separate machine required; may share infrastructure/storage/time with fence/store unless shown otherwise | Host lease independent of client; persisted original slot/financial reserve | UNKNOWN until lookup/effect validation; no automatic recreate |
| F8 Controller-Host network | Can fail independently; shared switch/DNS/infra affects outer fence and F9 | Native/outer deadline cannot require live connection; reconnect query only | UNKNOWN for request/ack/result loss; positive no-effect can later establish KNOWN_FAILURE |
| F9 Evidence store | Independent copy proposed, actual physical independence UNKNOWN | Hard enforcement continues; stop acceptance/admission; bounded protected original ledger | UNKNOWN for missing mandatory records; surviving reliable records may establish scoped facts |

No F10 is needed: collector is F2/F9; clock is a shared dependency of F3-F7; external service faults are analyzed at TB11 with P6/P9. These are cross-cutting dependencies, not invented independent protective layers.

## 4. Thirty attack/failure cases

Every row inherits: stop new effects; preserve original attempt/unit/exposure; no replacement or retry after UNKNOWN; later retry needs positive original effect/no-effect reconciliation, new then-valid authority, fresh qualification and conserved cumulative budget. 'Refuse' before any effect can be KNOWN_FAILURE only if durable no-effect facts exist. Tests below are future, never run here.

| # / scenario | Detection | Containment | Terminal state / required recovery | Retry rule | Evidence / unresolved UNKNOWN |
| --- | --- | --- | --- | --- | --- |
| 1 Infinite loop | CPU/time event and native clock | CPU ceiling + conserved manager/outer deadline | KNOWN_FAILURE after zero-live/effect proof; else UNKNOWN; reconcile/cleanup | No timer-reset retry | Kernel membership/usage + outer event; ultimate latency U02 |
| 2 Memory exhaustion | memory events/OOM + helper inventory | Hard ancestor memory/swap/pressure reserve | Observe victim and whole unit; cleanup; UNKNOWN if manager/store harmed | No automatic OOM restart | Kernel events and host reserve; overshoot U05 |
| 3 Fork bomb | pids events/task inventory | Immutable ancestor tasks; virtual-task ceiling if needed | Tree termination/readback; unknown helper stays UNKNOWN | No new unit | Kernel tasks/guest task scope; virtual enforcement U05 |
| 4 Disk fill | quota/capacity/inodes errors | Hard aggregate backing/quota, no root writes | Denied writes plus observed inventory; cleanup may remain UNKNOWN | No relocation to bigger workspace | Host quota/backing/retention; U04/U05 |
| 5 stdout/log flood | Bounded collector counters/truncation | Aggregate capture quota, fixed pipes/buffers, journal denial | Mark truncated result failed/UNKNOWN coverage; cease producer | No implicit rerun to get lost logs | Capture/source/store gaps; helper write scope U03/U05 |
| 6 Ignores SIGTERM | Still populated after grace | Whole-tree forced termination plus fence | Zero-live before final failure; unresolved D-state UNKNOWN | No grace extension | Manager kill request != zero-live; U02 |
| 7 Forks descendants | Recursive subtree + process identities | Inherited protected membership; no migration | Observe all descendants and clean resources | No detached child exemption | Kernel subtree and explicit helper/guest graph |
| 8 Daemonizes | Parent exit with populated subtree | Membership-based containment, no restart/socket activation | Original unit remains stopping until zero-live | No main-PID-only success/retry | Kernel live subtree/runtime refs; no parent-exit shortcut |
| 9 Host mounts | External denied operation/mount inventory | Private nonpropagating mounts, dropped caps, no host devices | Refusal/violation evidence; breach quarantines Host binding | No fallback privileged mode | Effective mount/capability policy; deny coverage U03 |
| 10 Host network probe | Policy/namespace/FD records, synthetic negatives later | NO_NETWORK incl inherited IPC/proxy/metadata | Any unauthorized reach invalidates binding; reconcile effects | No allowlist expansion | Host/network observer; hidden channel U03 |
| 11 Privilege escalation | Effective UID/caps/NNP/seccomp/LSM and later negatives | Fixed privilege drop; no host-admin mapping/socket | Breach is failure and qualification invalidation | No elevated retry | Host/kernel observations; exploit immunity not claimed |
| 12 Runtime/control socket | Mount/FD/service closure | No Docker/containerd/manager/runtime socket, no generic privileged MCP | Deny; any access invalidates scope | No alternate socket route | External input/socket graph; U03 |
| 13 Credential discovery | Synthetic markers only, no real secret probe | No owner/controller/API/credential mount/env/FD | Reachability violation failure; invalidate grant/custody | No same compromised scope retry | Status-only input/mount/FD observations; U03 |
| 14 Alters clock | Wall/elapsed divergence, boot identity | Deny clock/control privilege; independent deadline clock | Uncertain elapsed/expiry UNKNOWN; fence original | No clock-reset lease | Independent origin/time source; U02/U05 |
| 15 Extends deadline | Mutation/notify/restart/replay rejection | No guest/control renewal rights; conserved outer lease | Refusal known only with original unit still contained | No new request-ID workaround | Manager actor/property/lease records; U02/U03 |
| 16 Agent crash | Transport/service death | Previously armed manager/outer bounds survive | External query; missing record UNKNOWN; later cleanup | No automatic create on restart | Original intent/native refs/store; U03 |
| 17 Agent hang | Missing progress vs native timer | Runtime manager and independently armed fence | Timeout not cessation; use native observations after recovery | No availability replacement | Manager/outer records; shared fault U02 |
| 18 Manager crash | Manager outage/external watch observation | Separate outer fence, never same-manager cleanup-only | UNKNOWN until independent fence and original inventory | No service restart of workload | Outer-domain source and boot recovery; U02 |
| 19 Kernel panic | External Host/VM/boot observation | Supported nonrenewable outer fence | Compute cessation separate from disk/effects; past task UNKNOWN | No auto-resume after reboot | Infrastructure observation; actual bound U02 |
| 20 Host reboot | Changed boot ID plus external journal | Default-deny boot/orphan quarantine; original grant expired/conserved | Reconcile old attempt, mounts/backing/effects; not success | No reset origin or old grant restore | Old/new boot/native refs; U03/U04 |
| 21 Controller crashes after dispatch | External durable intent vs Host unit | Host/native/outer lease independent | Original query and output/effect validation; initially UNKNOWN | No redispatch from reconstructed conversation | Controller durable pre-effect record + Host source |
| 22 Controller network loss | Gap/no response | No renewal/new dispatch; prior native/outer bound | Query original once recovered; not no-effect | No reconnect recreate | Intent, Host/fence lease, gap; U02/U03 |
| 23 Evidence collector crash | Missing sequence/ack/writer death | Independent resource/lifetime containment; stop release if not started | UNKNOWN mandatory observation; preserve bounded data | No rerun to fill evidence gap | Durable prefix and source coverage; U03 |
| 24 Partial output/evidence | Length/hash/framing/atomic-finalization checks | Separate bounded temporary and immutable final objects | Never publish partial as final; UNKNOWN if decisive suffix absent | No blind result replay | Output hash/custody and journal prefix/commit marker |
| 25 Termination with incomplete cleanup | Zero-live but mounts/disks/net resources remain | Outer work cutoff plus finite survivor capacity/lifetime | Work failure/success fact may known; cleanup/exposure UNKNOWN | No new unit while survivor unresolved | Resource inventory distinct from cessation; U04 |
| 26 Retry after UNKNOWN | Durable original logical-operation/slot lookup | Reject replay/replacement, retain reservation | UNKNOWN persists until positive reconciliation | Strict refusal | Admission journal/refusal; state availability U03 |
| 27 Persistent state outside workspace | Mount/FD/device/service inventory | Denied writes outside bounded graph; no snapshot/export | Breach invalidates binding; inventory and authorized cleanup | No erase/replace to hide leak | Host-owned resource graph; U03/U04 |
| 28 External effect succeeds, response lost | Original broker/provider reference or gap | First fixture excludes; future service hard bound/idempotency if supported | EFFECT UNKNOWN despite local cessation; query provider | No repeat until original reconciled | EXTERNAL_PROVIDER_OBSERVED fact, not guest log |
| 29 Paid API before Controller state loss | Pre-effect durable intent/reserve + broker/service fact | First fixture denied; future independent API budget | Original reserved maximum stays UNKNOWN until settled | No call repeated using fresh ID | Provider effect/usage/cost and durable grant; external tail unknown |
| 30 Qualification/execution config drift | Compare current exact versions/profile/actors/source | Refuse before relying effect; invalidate if detected mid-run, native stop/fence | Record stale binding and UNKNOWN effects; requalify scope | No old-binding retry | Actual config and qualified identity; U01/U03/U05 |

## 5. Correlated-control review

| Apparent controls | Shared failure domain | Required separate protection / residual |
| --- | --- | --- |
| Agent deadline + Agent child watchdog | Event loop/process if colocated; even separate process shares kernel/OS/Host | Mature manager supplies process-fault separation only; outer domain for manager/kernel faults |
| Agent + watchdog + systemd/runtime manager | Kernel, OS, Host pressure/time/storage; OOM or block IO may impair all | Reserve control resources plus supported arm-before-create outer fence; reserves alone do not eliminate F4-F6 |
| systemd RuntimeMaxSec + watchdog service/timer | PID1/time/cgroup/DBus/OS | Not two independent final fences; no notification/restart/renewal and actual outer deadline |
| nsjail monitor + PDEATHSIG + cgroup.kill | Linux clock/kernel/process state | Useful local layers; none proves finite physical kill completion after kernel stall |
| gVisor Sentry/Gofer + Host cgroups | Host kernel/OS/platform; virtual tasks differ from physical tasks | Bound both graphs and outer Host cutoff |
| Firecracker/Kata guest watchdog + VMM kill | Guest can fail independently, Host VMM/KVM/manager share Host kernel | Host process ceiling plus outside-Host/OS fence; guest agent is not final Host evidence |
| Hardware watchdog + manager feed | Device independent clock may exist; healthy feeding process can keep it alive indefinitely while unit leaks | Lease-aware feed cutoff cannot depend solely on the failing Agent; immutable independent arm/cutoff and qualified device semantics needed |
| Controller fence command + Controller timer | Same Controller, network, credential and stored state | Pre-arm autonomous finite lease before allocation; emergency request alone is not ultimate fence |
| Host evidence + external store | Shared backing/network/controller may defeat supposed independence | Actual failure-domain/custody map and bounded persistent original intent; source compromise remains TCB residual |

Different process != independent kernel/OS/storage/time source. A lower-level hardware or higher-level hypervisor/power controller may be suitable only if its actual numerical semantics and no-extension/auto-start boundary are supported. External reachability alone is not autonomous fence enforcement. No credible complete fence is established in current evidence.

## 6. Evidence attack surface

| Field / attack | Decisive source and validation | Rejection/UNKNOWN rule |
| --- | --- | --- |
| Execution identity / reused PID/path/unit name | HOST_OBSERVED + KERNEL/RUNTIME_OBSERVED; boot/native generation, PID start identity, protected original attempt | Unbound/reused identity cannot close provenance/cessation |
| Timestamps / wall jump, reboot, fabricated time | HOST/CONTROLLER observations with clock basis/error; outer independent observation | No wall-only duration; uncertain interval cannot extend lease |
| Status / forged completed/not-found | Scoped runtime state plus zero-live and independent output/effect validation | Runtime completed/deleted is not task/cleanup success |
| Logs / injection, truncation, replay | GUEST_ASSERTED data plus bounded HOST capture/source sequence | Logs never prove effective policy; missing capture yields explicit gap |
| Output / symlink traversal, partial final, fake receipt | HOST extraction of fixed allowed regular files; validate identity/size/hash/type | Reject links/paths/devices and unbound artifacts; never execute output |
| config/workload/dependency hash / pre-check substitution | Protected admitted bytes plus actual loaded/object/custody observation at safe barriers | Requested hash alone cannot prove applied/loaded state |
| Lifecycle / kill request called cleanup | HOST/KERNEL/RUNTIME scoped query plus outer cessation source when Host unavailable | Each state independent; inaccessible required fact UNKNOWN |
| Descendants / hidden helper or virtual tasks | Protected enclosing subtree plus explicit runtime/helper/guest graph | cgroup-zero-live insufficient for escaped/outside helpers or retained resources |
| Cleanup / deletion hides survivors | HOST resource inventory, mount/net/backing refs; provider facts if needed | Path absence alone not release; reserve unresolved tail |
| External effect receipt / forged or response lost | EXTERNAL_PROVIDER_OBSERVED authenticated original-operation scope, Controller/broker durable intent | Guest-only or lost response leaves effects UNKNOWN; no retry |

Observation classes: GUEST_ASSERTED (untrusted claim); HOST_OBSERVED (trusted Host collector at stated scope); KERNEL/RUNTIME_OBSERVED (enforcer-origin fact delivered through a qualified observer); CONTROLLER_OBSERVED (admission/reservation/reception/artifact validation); EXTERNAL_PROVIDER_OBSERVED (qualified service/fence/effect fact). These do not form a universal truth ranking. Source authenticity does not prove its claim beyond coverage; a Host/root compromise can undermine kernel observations delivered by Host. Guest-only evidence never closes a required Host property; guest kata-agent claims do not prove Host VMM cessation.

## 7. Residual risks and disposition

U02 is the critical correlated-failure/lifetime premise; U03 controls authority/provenance/evidence; U01/U04/U05 determine supported deployment and complete cost/quantities. No arbitrary TCB assurance project is required, but mandatory declared failures cannot be dropped or hidden inside 'trusted kernel'. D1 status: THREAT MODEL DOCUMENTED / PARTIAL. Consult [D2](nexus-g2-route-d-d2-architecture-analysis-v1.md) and the separate [adversarial pass](nexus-g2-route-d-d2-adversarial-review-v1.md). No acceptance or D3 authority follows.

Preserved state: G2 HOLD; Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT. Route B unresolved / retained; Route D FEASIBLE FOR FURTHER DESIGN. Accepted A0-A6/P1-P12 and all historical accepted bytes remain unchanged. No installation, Linux provisioning, VM/container creation, Host execution, privileged operations, credentials, paid activity, HostAdapter/Host Agent implementation, architecture acceptance, G3/G4 entry, merge, push, tag or freeze.
