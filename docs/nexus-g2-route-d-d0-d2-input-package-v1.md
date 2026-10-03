# Nexus G2 Route D D0 D2 Input Package v1

Version: `1.0.0`

Date / source retrieval: **2026-10-03**

Baseline: `8818b0b674878f016a779197a6f04cb0c5b3a39f` / `nexus-v2-g2-development`

Status: **D-REF FACTUAL / DESIGN CHECKPOINT ONLY - NOT ACCEPTED; NO HOST OR EXPERIMENT AUTHORITY**

## 1. Overall decision and scope

**A. MATURE COMPONENT REUSE APPEARS SUFFICIENT TO PROCEED TO D0-D2.** This justifies separately authorized research/design, not formal phase start or architecture selection. Mature substrate components can plausibly carry most low-level isolation/resource/setup/lifecycle mechanics. No need for a custom isolation runtime has been established. Complete ultimate-fault/cost/provenance/evidence binding is still UNKNOWN, including availability of a suitable existing Host and independent fence. If existing components cannot meet the chosen envelope, stop or seek explicit architecture decision; do not invent a generic runtime. See [survey](nexus-g2-route-d-external-reference-survey-v1.md), [reuse](nexus-g2-route-d-reuse-adapt-reject-matrix-v1.md), [mapping](nexus-g2-route-d-reference-p1-p12-hq-mapping-v1.md), [register](nexus-g2-route-d-reference-source-register-v1.md) and [review](nexus-g2-route-d-reference-adversarial-review-v1.md).

## 2. Small candidate-family set (no ranking)

The rows are design comparisons; isolation strength is a boundary description, not a numerical security score. Startup/performance/burden statements are qualitative inference, no benchmark or price estimate. No family is accepted by decision A.

| Family | Isolation / TCB / privilege | Lifecycle / P5 / P6 / P7 | Operations / compatibility / startup / implementation and evidence burden |
| --- | --- | --- | --- |
| A: mature namespace/cgroup/seccomp tooling | Shared Host kernel; nsjail/runc/bwrap plus fixed policy, manager and optional existing LSM. Setup needs root/delegation or supported userns; no blanket rootless sufficiency. | Independent fixed unit/whole-tree limits and fallback; no monitor-only cutoff. Hard drivers/fixed-host contract may bound cost; native refs plus effective tree/artifact readback. | No separate guest kernel boot, but startup is unmeasured. Native Linux compatibility with exact mount/syscall/UID restrictions; policy escape/kernel and pre-exec evidence burden. Minimal Nexus wrapper cannot become generic command broker. |
| B: gVisor-backed | Sentry/Gofer reduces direct Host syscall surface; Host kernel/platform/manager remain TCB. Choose exact Systrap/KVM and directfs/net mode later. | Bound Sentry/Gofer/helpers and virtual tasks; external lifecycle/fence. Same hard financial obligations; Host and virtual-task terminal states separately observed. | Syscall/IO/device compatibility and platform prerequisites; no performance comparison claimed. runsc integration/virtual task/input/effective source evidence needed. |
| C: Firecracker microVM-backed | KVM/hardware + Host kernel/VMM/jailer + guest kernel/images; restricted API/TAP/backing paths. Privileged setup separated from VMM UID. | Manager owns VMM/helpers independent of guest; total/fault cutoff and survivor quotas; finite infrastructure obligations and external API budget. Guest shutdown not Host cleanup. | Image/kernel/device/patch and virtualization operations; guest boot/image provisioning overhead unmeasured. Reuse VMM/jailer, build only narrow admission/binding/evidence; snapshot/serial/MMDS graph raises burden. |
| D: Kata-style VM/container composition | OCI/shim/VMM/agent/guest kernel plus sharing/network plugins; VM/pod grouping not one-process assumption. | Enforce Host overhead AND guest container limits; independent Host destroy/fence with readback. No storage/egress/guest-agent trust shortcut. | Supported OCI/container workflow if future use warrants extra layers. Larger dependency/configuration/privilege/overhead/evidence graph; no cluster requirement or ranking. |

Kubernetes is a pattern source, not Family E or assumed substrate. containerd is an optional integration layer, not mandatory merely because mature. Existing quota/manager/fence and owner-controlled evidence can combine with more than one family; actual versions/support/permissions decide compatibility. No automatic weaker-family fallback is permitted.

## 3. D0 future requirements inputs

| Input category | Documentary result / future obligation |
| --- | --- |
| Mature primitive capabilities available in source contracts | Namespace/VM/application-kernel isolation, cgroup resources/subtree observations, runtime create/start/kill/query, manager-owned services and quota concepts. COMPONENT EXISTS != PROPERTY PROVEN; no Nexus actual requirement is marked satisfied. |
| Nexus must impose | One accepted fixed capability, default-deny effect/input/actor graph; then-valid independent grant and conserved cumulative resource/money lease; protected bytes/dependencies and pre-effect custody; distinct cancel/effect/cost states; UNKNOWN refusal. |
| Still UNKNOWN | Existing supported dedicated Linux Host, exact kernel/runtime/privileges, actual applied controls/byte observations, ultimate independent manager/kernel/fault cutoff, safe numerical preallocation maximum, all-in contract/rates/headroom and effect visibility. |

Do not convert all F0-F9 into a universal malicious-TCB proof project. Accepted failure scope must be explicit, realistically tested and threat-preserving; expected failures cannot be dropped retrospectively to obtain PASS. Required fault coverage unsupported by a family keeps it ineligible. Financial fixed-cost cases still need finite H/renewal/overage/energy and separate API/effect caps.

## 4. D1 future threat inputs

Adopt known threat classes: malicious/buggy guest, runtime/policy bypass, confused deputy, insecure Host sockets/shares/FDs/devices, namespace/cgroup migration, virtual versus Host descendant gaps, controller compromise within granted authority, manager/monitor failure, clock/reset/reboot, retained images/snapshots/logs, price/renewal/egress/API effects, evidence forgery/store loss and interrupted retry duplication. [Mapping](nexus-g2-route-d-reference-p1-p12-hq-mapping-v1.md) F0-F9 records correlated failures.

Separate owner/root/Host/kernel/hypervisor/manager/runtime/guest-agent/collector trust and privilege. A stronger isolation substrate is not a stronger lifecycle guarantee by itself. Define actor ability to mutate bundles, callbacks/hooks, unit properties/notify/reset, runtime paths, cgroup topology, shares/network and log writers. Deny untrusted control credentials; never design a general privileged shell endpoint. Exact privileges remain UNKNOWN pending supported deployment scope; no password transfer or Windows privileged service fallback follows.

## 5. D2 future selection questions and minimum Nexus-specific work

Future selection questions: which single accepted capability and actual existing Host; exact supported release and vendor dependency/license/patch chain; needed guest ABI/network/filesystem/device support; pre-exec actual byte/input/limit barrier; Host-plus-guest/helper membership; numerical conserved lifetime/fault fallback and manager independence; finite storage/output/retention; all-in owner cost; authenticated original effect/query/no-effect scope; least privilege/config/evidence custody; failure/rollback protocol and requalification triggers. No answer is chosen here.

| Component / responsibility | Nexus-specific minimum / reuse boundary |
| --- | --- |
| HostAdapter | Typed fixed create/status/stop/effect mapping, original refs, no arbitrary command/runtime/hooks or hidden recreation |
| Host admission protocol | Verify separately issued current grant/profile/expiry/cumulative slot before every effect; kernel/manager executes hard controls |
| Execution-unit and attempt identity | Bind Host/boot/unit/operation/process start/config/input/reviewed bytes; do not reuse identity after UNKNOWN |
| Configuration/qualification binding | Protected exact mode/version/capability/source scope/expiry; material drift STOP/requalification |
| Credential boundary | Existing owner facility, narrow control authority, no secret/platform broker invention; data-plane gets only accepted input |
| Evidence envelope/collection | External scoped effective observations, protected writer/store, ordered gaps/costs/effects; logs are not decisive receipt by name |
| Budget admission | Conservative all-in finite exposure, current authority/headroom, retained UNKNOWN; native hard drivers/cutoff independent |
| Reconciliation/checkpoint/retry refusal | Positive original effect/no-effect/artifact facts; no blind reissue, restored grant, reset timer or cost release |

Do not rebuild KVM/VMM, guest agent, Sentry, cgroup implementation, namespace plumbing, seccomp compiler, filesystem/image engine, process supervisor, cluster controller, billing service or generic scheduler. A small profile wrapper still needs security review; quantity of custom code is UNKNOWN, not claimed trivial. Existing runtime updates/patches change qualified assumptions. Narrow Host adoption is a separate proposed TCB decision, not an accepted change to A0-A6.

## 6. Future phased gates and rollback

| Phase | Next authorized deliverable would be | Current state |
| --- | --- | --- |
| D0 | Owner-scoped fixed requirement/number/Host availability/effect/cost questions | NOT STARTED |
| D1 | Exact actors/TCB/failure matrix and supported independent protection | NOT STARTED |
| D2 | Reviewed family/config/privilege/custody/license/ultimate-fence architecture proposal, not acceptance | NOT STARTED |
| D3 | Separately authorized minimum secret-free prototype and static package | NOT STARTED |
| D4 | Safely bounded actual identity/input/isolation/descendant negatives | NOT STARTED |
| D5 | Controller/runtime/manager/collector/network/boot fault/recovery validation within independent envelope | NOT STARTED |
| D6 | Equivalent HQ1-HQ6 on one accepted capability, every mandatory fact positive | NOT STARTED |
| D7 | Scoped positive Host binding acceptance; separate G2 authorization still needed | NOT STARTED |

No runnable prototype/unit file/installer/VM/command package is supplied. No current available Host/fence/cost source is invented. Minimum next task is a separately authorized bounded D0-D2 research/design program using this package, with no installation/execution/selection acceptance. OWNER ACTION REQUIRED: YES only to authorize that next phase boundary; no password, account login, shell action or paid resource is requested now.

Future abandon/rollback: stop a family if native mechanisms cannot bound the admitted threat, need broad privileged generic broker/weaker isolation, lack numerical hard fault/cost or actual provenance/evidence. A future separately authorized experiment must halt admission, use qualified native/outer termination, preserve original UNKNOWN/exposure, query/effect reconcile and clean only authorized units; no automatic new unit/Host. D-REF itself changes no system resources requiring rollback. Accepted provider/LPAC/qualification states remain unchanged.

Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD. D0-D7 NOT STARTED. Route B unresolved; OpenAI human escalation PENDING. Accepted architecture/A0-A6/P1-P12 and sealed V4 unchanged. No installation, Host/provider execution, credentials, paid activity, privileged/system changes, G2/G3/G4 implementation, acceptance, merge/push/tag/freeze.
