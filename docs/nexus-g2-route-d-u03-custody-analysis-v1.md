# Nexus G2 Route D U03 Custody Analysis v1

Version: `1.0.0` | Date: **2026-10-03**

Starting HEAD: `2fb939332c7c20dcbf2a528f296fa1d8a693cc5c` | Branch: `nexus-v2-g2-development`

Status: **DOCUMENTARY CHECKPOINT ONLY / NOT ACCEPTED / NO IMPLEMENTATION AUTHORITY**

Preserved: G2 HOLD; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Scenario 01-04 NOT RUN; Positive Host Binding ABSENT. UNKNOWN != PASS. No architecture selection/acceptance, P1-P12 change, D3, U05 measurement, installation, provisioning, Host execution, credentials, privilege elevation, paid activity, merge, push, tag or freeze.

## 1. Decision and existing primitive scope

**U03-B - MODEL IS PLAUSIBLE BUT EXACT HOST STORAGE/PRIVILEGE CONFIGURATION IS REQUIRED / NOT CLOSED.** Existing Linux ownership/permissions, protected namespaces/read-only mounts, dropped capabilities, fixed runtime profiles, quota-backed storage and durable stores can express the inherited boundaries. No new sandbox, trust-boundary invention or production secrets protocol is needed for this model. Exact existing configuration, effective release observations and storage failure semantics remain absent. U03-A's narrower model-definition proposition is plausible, but does not close the full actual custody requirement; B is the operative classification.

See [D1 TB0-TB11](nexus-g2-route-d-d1-threat-model-v1.md) and [lifecycle design](nexus-g2-route-d-d2-lifecycle-and-evidence-design-v1.md) for the unchanged grant/admission/release/reconciliation contract. This document only resolves how mature primitives could support it. Source IDs are in the [closure register](nexus-g2-route-d-u01-u04-closure-v1.md#7-evidence-register-and-consistency).

## 2. Six custody zones: proposed actor policy, not observed configuration

Read/write here is logical policy for a future exact profile. Privileged admitted Host root remains TCB and may technically bypass local discretionary permissions; no local write-once claim is made against arbitrary malicious root. The Controller and Host do not issue their own wider authority.

| Zone / trust | Read authority | Write authority | Credential presence | Lifetime | Failure handling / tamper implication |
| --- | --- | --- | --- | --- | --- |
| ZONE A Owner / Controller authority store; protected issuer and governance | Owner/issuer; Controller receives verification and fixed grant needed for attempt | Independent issuer for grant; Controller only durable intent/reservation within grant | Existing owner/Controller authority stays here, outside Host/guest; protocol not designed | Original grant/operation reservation through bounded reconciliation, expiry cannot be refreshed by runtime actors | Unavailable verification or original record refuses effect/retry. A compromised Controller cannot enlarge independent grant or mint a replacement slot. |
| ZONE B Host control / admission; trusted verifier and narrow management | Protected admission verifier; Agent minimum attempt/profile/native references | Protected verifier writes admission journal; fixed privileged setup/helper only admitted operations | Narrow existing control authentication, if required, outside execution unit; no general root/sudo secret or broad API for Agent | Fixed attempt; immutable original bounds; revoke or expire rights without reopening slot | Admission/storage loss closes new admission; manager sockets/policy never guest-mounted; source or grant tamper invalidates binding. |
| ZONE C Sealed staged input; provenance trusted, payload untrusted | Host sealing/verifier; execution unit bounded read-only data | Trusted stager before sealing; no workload write; unique staging objects owned outside guest | NO owner/Controller/root/API credentials; input inspection must reject accidental secrets under approved content policy | Fixed byte/inode/file allocation and original input identity until bounded cleanup/retention | Wrong hash, mutable staging alias, writable parent or source change blocks release. Staged data is not a live owner filesystem mount. |
| ZONE D Execution runtime data; untrusted | Workload within fixed profile; bounded collector reads validated output as data | Guest only bounded scratch/output; no other zones | NONE; no authority-bearing environment/FD/device/socket | Same original envelope; cleanup may outlive work only within reserved finite bound | Forged logs, deletion, crash or hostile output never establish limit/terminal facts. Remove only the accounted original resource graph after reconciliation. |
| ZONE E Protected Host evidence; source-relative trusted | Protected collector and bounded transfer reader; owner for review | Restricted outside-guest observer/writer per source/attempt; no workload write or rename; seal final record | Any store/control credential confined here/B, never emitted in evidence | Hard byte/inode allocation and retention bound; mandatory journal reserved ahead of optional guest logs | Collector/Agent death preserves acknowledged prefix and explicit gaps. F4-F6/F9 may still lose local evidence; independent F copy cannot be assumed. Root compromise is outside promised tamper protection. |
| ZONE F Controller durable evidence / reconciliation; trusted governance store | Owner and Controller adjudicator | Protected validated ingest plus conserved original reconciliation state; deny guest overwrite/replay | Controller/store auth remains protected; never in guest artifact | Finite reviewed retention; preserve original UNKNOWN/reservation even if large data expires | Missing/partial/replayed transfer keeps UNKNOWN. No automatic rerun/replacement; reconciled terminal resource/effect facts release reservation only under accepted contract. |

The zoning is allocation of existing D1 responsibilities, not an accepted physical deployment. F and E on the same Host/disk/provider/control plane can fail together; exact placement remains U01/U03. A folder named 'protected' does not supply a privilege boundary.

## 3. Authority and privilege feasibility

PROPOSAL: independently verifiable fixed grant in A, verified by B before any allocation/setup effect; no widening after input/profile/resource IDs are bound. Agent gets only original attempt references and fixed admission/status/stop actions. Runtime setup privilege, if needed, resides in a constrained admitted component outside guest; separate authorization and deployment support are prerequisites, not a claim that rootless defaults satisfy all limits.

Workload must receive no owner credentials, Controller credentials, root/sudo credential, privileged runtime/manager/DBus/libvirt/Firecracker socket, cloud control identity, generic broker, SSH agent, credential mount or arbitrary inherited FD. Deny writable cgroup/namespace control, Host PID/network access, dangerous devices and Host filesystem mounts. Capabilities are per-thread/namespace and broad setup rights are not least privilege (CP01). Namespaces and read-only presentation do not alone close inherited descriptors or privileged parent paths (NS01/SD08). A protected service can enforce a fixed actor policy, but this review does not design a new authorization server or secret exchange.

The Agent may need narrow management rights that unprivileged workload must never inherit. Whether a supported deployment can supply fixed rights without giving the Agent schedule extension, arbitrary unit creation/configuration, store deletion or arbitrary shell is exact profile evidence, not assumed. In particular a 'create-only' infrastructure actor that can create a replacement can still enlarge total logical-operation lifetime; conserved admission slot and independent budget refusal remain necessary.

## 4. Input movement without live filesystem authority

PROPOSAL: A identifies an approved bounded data object and its source/revision; Controller transfers only that object's staged immutable COPY, not its authority store or repository. B verifies byte/file/inode limits and expected provenance, writes into its dedicated protected staging allocation, resolves path/symlink/hardlink hazards within the approved set, checks the complete closed dependency/image set and then seals it. C is presented read-only by a supported fixed mount/image facility; D is distinct quota-backed scratch. No owner home, live Nexus repository, credential directory or arbitrary Host tree is mounted.

| Required input fact | Documentary model | Actual evidence still missing |
| --- | --- | --- |
| Source identity | Approved object identity, revision/source reference, original operation and attempt | Actual approved source object and safe contents/provenance |
| Staging owner | Protected stager UID/service, separate guest identity, protected parent/object ownership | Actual ownership, ACL/LSM policy and closed writer/alias set |
| Write permissions | Stager only before sealing; denied afterward to workload and execution Agent; no inherited writable descriptor | Mount flags, backing permissions, FDs/devices/sockets and runtime effective configuration |
| Hash / provenance binding | Expected content hash independently known before release, readback bound to Host/boot/attempt/profile and staging identity | Byte equality plus trustworthy acquisition/staging observation; hash alone is not source authentication |
| Cleanup owner | Protected Host cleanup of original staged/scratch graph after required receipt/UNKNOWN retention; Controller reconciles | Reserved capacity, supported finite retention and cleanup/cost terms |

Read-only guest mounts still permit external Host writers unless backing authority is sealed. A hash checked only after execution cannot prove what bytes were actually loaded or prevent a race. A guest report of its own input hash is GUEST_ASSERTED. Pre-effect staged and effective release evidence remains mandatory under the inherited lifecycle barrier.

## 5. Protected evidence and bounded failure behavior

| Evidence class | Can establish | Cannot establish merely by appearing in a Host file |
| --- | --- | --- |
| GUEST_ASSERTED | Guest output/log bytes and claims for validation | Effective policy, admission, execution/descendant cessation, cleanup or billing truth |
| HOST_OBSERVED | Scoped observer's Host operation/readback and identities | Independent kernel/hypervisor guarantee or untampered upstream content without provenance |
| KERNEL/RUNTIME_OBSERVED | Native scope/configuration/membership/events as supported by exact runtime | Universal cessation latency, billing/effects or independent Host-failure survival |
| EXTERNAL_OBSERVED | Independently sourced original infrastructure action/state/receipt | Inner policy application, guest correctness or deletion of all separately retained resources |

PROPOSAL: outside-guest bounded observer writes separate source-labelled records into E; preserve original Host ID, boot ID, attempt/operation ID, native resource refs, config/source hashes, sequence, timestamps and gaps. Grant identity is a safe reference, never a credential value or secret hash. A sealed per-attempt record or protected append-only writer is an actor policy; it is not intrinsically immutable against admitted root/storage failure. Distinguish observation time from event time and a complete stream from a durable prefix.

N12 documents persistent/volatile journal modes, size/retention and service-rate controls; rate limits drop records, volatile data is lost on boot, and vacuum removes archived files while active files can leave usage above the nominal limit. Hence journald alone is not a hard per-attempt quota, complete mandatory receipt or tamper-proof store. [Pinned journal source](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/journald.conf.xml).

N11 requires attention to file AND directory sync for durability; synchronization can fail for space/quota/IO reasons and can block waiting on device completion. Therefore a successful file copy or hash is not an independently durable acknowledgment or finite IO latency. [Linux fsync contract](https://man7.org/linux/man-pages/man2/fsync.2.html).

PROPOSAL: hard byte/inode storage partition/quota with separately reserved mandatory metadata, bounded optional guest streams and explicit truncation/drop facts. When mandatory evidence capacity/collector availability cannot be guaranteed, refuse release/new admission; an already running attempt stays under its independent resource/fence envelope, stops acceptance, and retains UNKNOWN for missing facts. Do not let workload log flood consume authority/fence/journal storage or reserves. Exact overhead/reserves are U05 DEFERRED; D0 sample numbers are not accepted effective limits.

Durable transfer to F requires identity/source/schema/sequence/hash validation and protected acknowledgment; retain E until confirmed F durability or the explicitly finite failure policy applies. Controller connection loss cannot make E grow indefinitely; allocation/retention and original reservation remain bounded, and missing mandatory transfer is UNKNOWN. Complete resource release and billing cessation require separate observations. No assumed everlasting retention or magical evidence recovery closes F9.

## 6. Stress outcomes and remaining evidence

| Event | Preserved behavior / result |
| --- | --- |
| Forged guest log | Store as GUEST_ASSERTED data only; do not relabel HOST_OBSERVED after copying. |
| Guest deletes workspace | E/F outside guest writer authority can survive only if actual boundaries hold; original input/operation references remain external. |
| Execution crash | Retain independently recorded prefix; no result/cleanup inference from exit alone. |
| Agent/collector crash | No reliance on crashed writer to arm fence or regenerate evidence; previously durable prefix and gaps, otherwise UNKNOWN. |
| Controller disconnect | No renewal/recreate; bounded E plus conserved F intent; later reconcile original IDs only. |
| Host/storage outage | Local receipt durability and independent copy are exact-store facts; mandatory missing data keeps UNKNOWN. |

Needed packet: actual A-F actor policy and placement; protected staging/read-only effective backing; launch/load byte/profile/Host/boot/attempt barrier; runtime control/mount/FD/device/environment closure; narrowed Agent/helper operations; hard quota and mandatory journal reserve; bounded observer/source semantics; file/directory/transfer acknowledgment behavior; cross-boot original ledger/default-deny/retry refusal; finite retention and U04 costs. Existing runtime/OS primitives make this plausible, but configuration, supported storage guarantees and eventual authorized fault validation remain necessary. No secret protocol, HostAgent code or runtime change was produced.
