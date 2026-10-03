# Nexus G2 Route D U01-U04 Documentary Closure v1

Version: `1.0.0` | Date: **2026-10-03**

Starting HEAD: `2fb939332c7c20dcbf2a528f296fa1d8a693cc5c` | Branch: `nexus-v2-g2-development`

Status: **DOCUMENTARY CHECKPOINT ONLY / NOT ACCEPTED / NO IMPLEMENTATION AUTHORITY**

Preserved: G2 HOLD; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Scenario 01-04 NOT RUN; Positive Host Binding ABSENT. UNKNOWN != PASS. No architecture selection/acceptance, P1-P12 change, D3, U05 measurement, installation, provisioning, Host execution, credentials, privilege elevation, paid activity, merge, push, tag or freeze.

## 1. Decision and recovered authority

**RESULT C - MATERIAL UNKNOWN STILL PREVENTS ARCHITECTURE SELECTION. SAFE RESUME POINT ESTABLISHED.**

This bounded run completes the documentary adjudication, not the four operational closures. Supported Host classes and an external VM deadline candidate are documented; no exact existing Host, failure-complete outer envelope, effective custody configuration or finite all-in contract has been established. Route D remains FEASIBLE FOR FURTHER DESIGN. No family is selected, newly eligible for selection, accepted or qualified. Lack of sufficient evidence does not prove impossibility.

The starting tree was CLEAN, with 270/270 MANIFEST entries verified and raw MANIFEST SHA-256 `F675B81DD6D55DDC0E04F87CDA27D6FB63C6E178B1D4868AD31780048BC423B8`. The completed 265-entry historical verification and D-REF/D0-D2 reading are reused; no historical research restart occurred. Current baseline verification was explicitly required by this closure request.

The five current design documents below govern interpretation. Their already-read authority chain, including accepted A0-A6, P1-P12/HQ1-HQ6, Limited Clarifying Amendment, Positive Host Binding requirements, P5/P6 safety study and Route D feasibility/D-REF mappings, is retained through D0 section 1. Those 22 authority bindings were checked against the unchanged current MANIFEST. Reuse means prior reading plus current byte consistency; it is not a claim of new acceptance. The safety study remains non-normative. Historical acceptance records outrank older draft labels.

| Current document | Canonical LF SHA-256 |
| --- | --- |
| [nexus-g2-route-d-d0-requirements-v1.md](nexus-g2-route-d-d0-requirements-v1.md) | `BE26E444BFAF23891A7BE34C149BE0FAC9FFE7152EE9ACABAFB473CA336543C3` |
| [nexus-g2-route-d-d1-threat-model-v1.md](nexus-g2-route-d-d1-threat-model-v1.md) | `D3D7E270B545F15CFBC9848B2B048B3939F43C425C7253EA0E42AFF74B03205C` |
| [nexus-g2-route-d-d2-architecture-analysis-v1.md](nexus-g2-route-d-d2-architecture-analysis-v1.md) | `FE3EA6440DDC3563C7C2791E7DAA34166FFA959B3EAEC0847882869422D1FD48` |
| [nexus-g2-route-d-d2-lifecycle-and-evidence-design-v1.md](nexus-g2-route-d-d2-lifecycle-and-evidence-design-v1.md) | `41F82971C417CE41A11BD90E149670A79F8886A106427D7DA1012DFA86F44845` |
| [nexus-g2-route-d-d2-adversarial-review-v1.md](nexus-g2-route-d-d2-adversarial-review-v1.md) | `5516482EB27E5818E6E9B584F5C58DE35FE5F38B86E24D893E592A5D01E88908` |

SUPPORTED HOST != QUALIFIED HOST; DOCUMENTED PRIMITIVE != EFFECTIVE CONTROL; TIMEOUT != ULTIMATE FENCE; PROCESS MANAGER != INDEPENDENT FAULT FENCE; FIXED PRICE != COMPLETE FINITE EXPOSURE; LOG LOCATION != PROTECTED EVIDENCE CUSTODY. Source hashes bind documentary bytes only.

## 2. U01: concrete candidate Host classes

One concrete documentary context is a dedicated x86_64 Ubuntu 24.04 LTS Linux system, physical or a full VM with owner administration, a separate Controller, and supported runtime-specific configuration. N01 documents maintenance through May 2029, GA Linux 6.8 and systemd 255.4, plus AppArmor restrictions on unprivileged user namespaces. These release facts do not identify installed packages or imply every namespace sandbox works without a supported policy. No workaround disabling protections is proposed. An exact patched kernel/runtime profile must be separately matched.

| Host class | Documentary viability | Environment-specific dependencies / present finding |
| --- | --- | --- |
| A Dedicated Linux VPS / full VM | HOST_CLASS_PLAUSIBLE for a full Linux guest and administrative control | Provider image/kernel restrictions, LSM policy, storage/quota, no control secrets in guest; nested KVM only if explicitly exposed. No existing instance identified. |
| B Owner-controlled dedicated Linux VM on existing hypervisor | HOST_CLASS_PLAUSIBLE | Existing physical host, hypervisor, capacity and owner authority are UNKNOWN. Hypervisor lives outside guest OS but may share physical faults; a same-host supervisor is insufficient for every F6 case. |
| C Dedicated physical Linux machine | HOST_CLASS_PLAUSIBLE | Owner hardware, CPU/KVM, disk/filesystem, independent power/fence and Controller placement must be evidenced. No machine inventory supplied. |
| D Hosted dedicated server | HOST_CLASS_PLAUSIBLE | Supported Linux installation and administrative rights, remote control/power semantics, retained disks, product contract and external fence independence are UNKNOWN. |
| E Current Windows workspace / hypothetical WSL or shared container | UNKNOWN as a Route D Host | Windows is the documentary workstation only. No Linux instance was inventoried. A Windows process is INCOMPATIBLE with the Linux-only candidate context; possible Linux environments require their own existing evidence and add no closure here. |

No provider winner or purchase is recommended. Public examples show supported capabilities can exist, not that the owner already has them or can safely use them together.

## 3. U01 capability matrix

Labels concern the specified Linux class, never an actual machine. SUPPORTED means the primitive is authoritatively documented. CONDITIONAL means exact enabled policy/device/storage/privilege is needed. UNKNOWN means actual custody/failure-complete property is absent. These labels are not qualification outcomes.

| ID / required capability | Class label | Documentary basis | Missing read-only evidence for an existing Host |
| --- | --- | --- | --- |
| H01 Supported Linux/kernel lifecycle | SUPPORTED | N01; upstream sources in D-REF | Distribution, kernel build/patch support and update lifecycle; GA facts do not pin actual HWE/vendor kernels. |
| H02 cgroups v2 | CONDITIONAL | CG01; D0 compatibility floor retained | Unified hierarchy, enabled controllers/delegation, enclosing helper/VMM membership. |
| H03 namespaces | CONDITIONAL | NS01; N01 LSM restriction | Enabled namespace features, permitted supported LSM/privilege path and actual namespace topology. |
| H04 seccomp | CONDITIONAL | SC01; runtime-specific sources | Kernel mode/support and exact effective filters; seccomp alone is not full isolation. |
| H05 process subtree management | CONDITIONAL | CG01, SD02/SD07 | Protected enclosing subtree, all helpers, no writable migration/delegation escape; kill interface availability. |
| H06 writable quota mechanism | CONDITIONAL | QT01 | Filesystem hard bytes/inodes accounting across guest image, scratch, logs and metadata; enabled quota/allocation. |
| H07 service manager | SUPPORTED | N01, SD03/SD06/SD08 | Actual version and protected fixed profile; requested properties are not release evidence. |
| H08 reboot recovery | CONDITIONAL | D1 boot model; N13 | Boot default-deny, no workload autostart/resume, preserved original ledger and external fence. Recovery does not retroactively bound outage. |
| H09 monotonic/boot identity | SUPPORTED | N13/N14; D0 existing clock model | Native boot ID and clock source matched to authenticated Host identity; boot-relative time cannot replace cross-boot outer deadline. |
| H10 owner-controlled evidence destination | UNKNOWN | N12/N11 enable storage concepts | Exact protected location/ACL/writer, hard capacity, durability, source identity and independent copy as U03. |
| H11 network isolation | CONDITIONAL | NS01/SD08; D-REF mapping | No interfaces/routes except defined local needs; inherited FDs, UNIX sockets, metadata, proxy, vsock/TAP helpers also denied. |
| H12 deny guest Host credentials | CONDITIONAL | CP01/NS01/SD08 | Mounts, environment, FDs, devices, sockets and attached infrastructure identity expose no authority; full actor policy. |
| H13 virtualization/KVM when needed | CONDITIONAL | FC01/FC03/KA05/GV06; N06 | CPU virtualization, /dev/kvm access, supported exact guest/hypervisor/machine class; provider permission not implied by administrator guest rights. |
| H14 mature substrate without unsupported hacks | CONDITIONAL | NJ01/RC01/GV06/FC03/KA05; N02 | Selected supported release/backend, image/dependency/security compatibility and supported policy; research main-branch pins are not supported deployed releases. |

N06 documents Linux KVM nested virtualization for eligible Compute Engine machine types and exclusions such as E2, ARM and memory-optimized VMs. Thus a full VM is not automatically a KVM-capable Route D Host. No nested environment is created. N13 supplies per-running-kernel boot identity; raw machine identity is not a security credential or proof of independent failure domain.

N14 distinguishes CLOCK_MONOTONIC (excludes suspended time) from CLOCK_BOOTTIME (includes it). Neither provides cross-boot identity or an independently enforced external maximum. Actual clock/time-namespace/skew policy remains profile evidence.

## 4. Family compatibility, without ranking

| Current D2 family | Minimum documented prerequisites | Plausible classes / provider-dependent items | Actual disposition / status-only evidence still required |
| --- | --- | --- | --- |
| A namespace/cgroup/seccomp | Supported Linux namespaces, cgroup v2, seccomp; protected fixed nsJail OR runc setup, not both by default; quota and manager | A/B/C/D; permitted setup privilege/LSM and protected delegation/storage | HOST_SPECIFIC_EVIDENCE_REQUIRED. Class plausible; enabled primitives, supported runtime and full mount/FD/helper policy unknown. |
| B gVisor | N02 current minimum: x86_64 or ARM64, Linux 5.6+; backend requirements per GV06, host resource/custody limits | A/B/C/D; systrap and KVM have distinct prerequisites, KVM exposure conditional | HOST_SPECIFIC_EVIDENCE_REQUIRED. No older generic kernel minimum substitutes for the current guide; exact release/backend and permissions unknown. |
| C Firecracker | Supported Linux/KVM/CPU, patched host and guest kernels/microcode; jailer/control socket, image/rootfs and external VMM envelope | C/D or explicitly nested-KVM A/B; provider/hypervisor-dependent | HOST_SPECIFIC_EVIDENCE_REQUIRED. KVM, version/CPU policy, complete host VMM resource graph and no-network storage/log setup unknown. |
| D Kata | Supported selected hypervisor/backend plus shim/runtime/guest-agent, host cgroups and bounded guest storage/sharing | C/D or suitable virtualized A/B; exact backend/nesting support required | HOST_SPECIFIC_EVIDENCE_REQUIRED. No platform-wide infeasibility proved; backend/device/helper compatibility unknown. |

All four remain documentary candidates; none becomes factually infeasible in all classes. A specific VM lacking KVM is INCOMPATIBLE with a KVM-required mode, not with every family. Current D2 carry-forward/reserve dispositions remain unchanged.

**U01: HOST_SPECIFIC_EVIDENCE_REQUIRED / NOT CLOSED.** Exact existing owner-approved Host context and supported configuration are absent. Public compatibility evidence cannot close the word 'existing'.

## 5. Joint re-adjudication after adversarial review

The specialized [fence](nexus-g2-route-d-u02-ultimate-fence-analysis-v1.md), [custody](nexus-g2-route-d-u03-custody-analysis-v1.md), [cost](nexus-g2-route-d-u04-cost-bound-analysis-v1.md) and [review](nexus-g2-route-d-u01-u04-adversarial-review-v1.md) records contain the analysis. Classifications below are final for this documentary checkpoint.

| Blocker | Previous state | Current evidence / classification | Exact missing fact | Evidence owner | Missing category | Still blocks D2? |
| --- | --- | --- | --- | --- | --- | --- |
| U01 | Exact supported existing Host UNKNOWN | Concrete supported Linux classes; HOST_SPECIFIC_EVIDENCE_REQUIRED / NOT CLOSED | Existing Host identity, owner authority, kernel/runtime/hypervisor support and effective prerequisite status | Owner and existing infrastructure administrator | OWNER_DECISION + STATUS_ONLY; release compatibility DOCUMENTARY; later effective qualification FUTURE_EXPERIMENT | YES |
| U02 | Independent ultimate finite envelope UNKNOWN | External absolute VM cutoff is a plausible candidate; U02-B / NOT CLOSED | Immutable original-slot maximum, prearm binding, F0-F9 correlation/outer-domain failure coverage and finite cessation/survivor tail; actual no-reset/no-renew rights | Infrastructure/fence authority plus owner; Host cannot attest external coverage alone | DOCUMENTARY + STATUS_ONLY + OWNER_DECISION; later bounded validation FUTURE_EXPERIMENT | YES |
| U03 | Protected authority/input/evidence custody UNKNOWN | Mature primitive model; U03-B / NOT CLOSED | Existing protected stores/writers/permissions/mounts/FDs/source provenance, durable original ledger and pre-effect release barrier | Owner, Host administrator, existing evidence-store operator | STATUS_ONLY + OWNER_DECISION; exact storage semantics DOCUMENTARY; eventual release/custody fault validation FUTURE_EXPERIMENT | YES |
| U04 | Complete finite cost/retention boundary UNKNOWN | Fixed and metered profiles conditionally feasible; U04-B / NOT CLOSED | Exact all-in terms/rates, finite horizon and cancellation/renewal/tail, enforceable metered maxima, residue inventory and funded headroom | Owner and applicable product/utility/network contract issuer | DOCUMENTARY + OWNER_DECISION + STATUS_ONLY resource/account-policy facts; later cleanup validation FUTURE_EXPERIMENT | YES |

U02-B records a plausible external mechanism, not a finding that only machine configuration is missing. Its indispensable documentary failure/consequence gap is retained. Likewise U03/U04 are models, not proven effective profiles.

## 6. D2 reopening test and bounded resume point

**RESULT C.** Four remaining irreducible blockers are: an identified existing supported Host; a supported prearmed immutable outer maximum covering declared common faults with finite execution and survivor consequences; protected effective custody including release evidence and durable original identity; and an all-in finite infrastructure/retention profile enforceable through outage/cleanup/renewal. No new blocker or P1-P12 redesign is introduced.

RESULT A is unjustified because these facts are not closed. RESULT B is unjustified because U02 needs authoritative failure/termination semantics and U04 needs contractual/cost decisions in addition to status. RESULT D is unjustified because absence of sufficient evidence is not a universal impossibility result. No family is currently eligible for renewed selection on the strength of this run.

The next owner decision is whether to nominate one ALREADY EXISTING dedicated Linux Host with an existing external fence and provide redacted, independently sourced Host/fence/custody/cost records for bounded review. This is not a request to buy/provision/configure one. If no such context is available, retain C/HOLD. If available, first resolve the documentary U02/U04 gaps; then compare the following read-only status packet, without automatic qualification or privileged changes:

| Packet | Bounded status/evidence contents | Scope restrictions |
| --- | --- | --- |
| Host | Redacted distribution/kernel/runtime support records, cgroup controllers/delegation, namespace/seccomp/LSM status, filesystem/quota, manager, hardware/hypervisor and KVM if needed, Host/boot identity and dedicated capacity | Existing records only; no installation, privilege, container/VM or fault execution. |
| Fence | Original independent armer/maximum, exact immutable resource/slot ID, arm-before-create acknowledgment, schedule/clock/reboot/resume policy, no renew/change/start/recreate rights, external failure dependencies and consequence terms | Configuration values and actor-role names only; never credentials or live control requests. |
| Custody | Redacted actor permission matrix, mount/FD/socket/device graph, staging sealing/provenance, protected bounded writer/storage, durability/ack/reconciliation policy | No secret contents, credential directory reads or production data. |
| Cost | Applicable published/redacted terms, finite period and inclusions, caps, rates/taxes/fees, cancellation effective time, no renewal/autoscale/snapshot, protected evidence retention and residual resource list | No login/API-key/account access or paid action in this run. |

U05 remains DEFERRED: all four preconditions are unproven and later owner authorization is absent. D3 authorized? **NO**. Future experiments cannot be used to discover an unbounded outer consequence by first executing untrusted work. D2 reopening, architecture acceptance and any subsequent experiment are separate gates.

## 7. Evidence register and consistency

Public sources only; no account session, credentials, paid service, target Host inspection or installation was used. New bodies were acquired on 2026-10-03; exact UTC retrieval timestamps and redirect URLs are in the external source register. N01-N11 and N14 are public page snapshots, not immutable release pins; N12-N13 use the existing systemd research commit `0794ba0045d11d4227f61ebacf7d75983ba884f1`. N11 identifies Linux man-pages 6.19. N14 is the public clock_gettime(3) compatibility page; its historical rendering is not presented as a current man-pages release. Cloud pages N05/N06 displayed update date 2026-09-30; N10 displayed 2026-08-06; N08 displayed 2020-07-07 despite current content, so its displayed date is not treated as an account-term version or fresh contract. A body hash proves the retrieved snapshot, not future stability or applicability.

The freedesktop rendered journal/identity URLs returned 403 through the browser fetch; first-party pinned systemd source N12/N13 was used instead. The cancellation page was successfully cached directly when a browser find returned an internal error. No failed retrieval is positive evidence. New source bodies are outside the repository at `D:\chatgpt\安装skills\output\route-d-u01-u04-2026-10-03`; reused bodies remain in the D-REF cache. No external code is vendored or executed. Primary facts are distinguished from model PROPOSAL and failure-domain INFERENCE in the specialized records.

| Source ID / primary page | Snapshot bytes | SHA-256 | Scope |
| --- | --- | --- | --- |
| [N01](https://documentation.ubuntu.com/release-notes/24.04/) | 177808 | `51DDED78C86CFE041D17246E10880D582B5DD5C0CA5F7E103B6D2155C0CCFDA5` | Ubuntu 24.04 LTS release notes; GA kernel/systemd are release facts, not actual installed versions |
| [N02](https://gvisor.dev/docs/user_guide/install/) | 32666 | `83C4D53A506DC9A5B2A04FA2863F32D96168C038F027C4974D795424D748E087` | Current documented Linux/architecture prerequisites only; installation instructions not executed |
| [N03](https://docs.cloud.google.com/compute/docs/instances/limit-vm-runtime) | 412590 | `8C466167CE7914F978A63C845578C8DA13B5C83ACB5EF67A4E32B3F3ABE12376` | VM deadline interruption/update/initial termination semantics |
| [N04](https://docs.cloud.google.com/compute/docs/instances/suspend-stop-reset-instances-overview) | 378566 | `E91F3B8E9A8BE0DE8E6B77CE543D9FD844445626FE5B68EC22F96C2BCE4F66E9` | Guest shutdown and mechanical-off normal operation; not fault SLA |
| [N05](https://docs.cloud.google.com/compute/docs/instances/graceful-shutdown-overview) | 370142 | `9A35B6A5D9DDB798D0060F69B7FE2BC6C03EC059B80395E0E82DFB14B7667BA6` | Graceful shutdown incompatible with limited-runtime instances |
| [N06](https://docs.cloud.google.com/compute/docs/instances/nested-virtualization/overview) | 364259 | `2DC7F14CB06A626837C81297F3C94FA9F500ACC40085C631E608D2B9C227F8A2` | KVM nested virtualization support restrictions |
| [N07](https://libvirt.org/formatdomain.html) | 635537 | `0B5D479ADC7948819FCD8723211B7E39FD96C441FE55FBD8835EF19B2FED551F` | Virtual watchdog, restart and poweroff semantics; not independent absolute lease |
| [N08](https://docs.hetzner.com/cloud/billing/faq/) | 369331 | `355B1A18ED1D3EA7033C2C025A064B36613F6CC9AFEB81431ECBBDB8EC1D9E9D` | Monthly cap versus continuing base/IP/storage/traffic bills and alerts |
| [N09](https://docs.hetzner.com/robot/general/traffic/) | 351250 | `A08088D632447E11687844848338ADDC3B163D4F93D6DA93B88FD1962D1C3BCD` | Product-specific included traffic versus overage |
| [N10](https://docs.hetzner.com/general/billing-and-account-management/cancellation/cancellations-overview/) | 356021 | `D2011257CFE1A6AE5FD4443BEC8C8D7088E0A0E09ED60671FF16B66CCA9FF004` | Renewal and cancellation conditions; no account/contract accessed |
| [N11](https://man7.org/linux/man-pages/man2/fsync.2.html) | 15152 | `F0A986D21500222ECB69580FC7A910F346C6B1FF1005CA515501FB05BB5D91F5` | File/directory durability, failure and blocking semantics |
| [N12](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/journald.conf.xml) | 32708 | `ED71E38DF308227A94ACA77B0840742B2C6EC49C1E43C2376D4AA135908F87F2` | Storage, retention, rate/drop semantics; not per-attempt tamper-proof custody |
| [N13](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/sd_id128_get_machine.xml) | 14415 | `A7154A4C39D61816EEF2C3B44712643D913C322376E29700B146EF842F928120` | Machine/boot identity and privacy; not unique qualified Host authentication |
| [N14](https://man7.org/linux/man-pages/man3/clock_gettime.3.html) | 25289 | `8FD256ACE6DDCC4E379F006B1FB0CD2467A28C14B920D5A06F053C32CF47C062` | Linux CLOCK_MONOTONIC versus CLOCK_BOOTTIME suspend semantics; public snapshot, not deployed clock state |
| [CG01](https://docs.kernel.org/admin-guide/cgroup-v2.html) | 172971 | `6EFABE7ED748F1D863859A0E5C50E770E47255C9A071BF878F6460E7E01C0563` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [CP01](https://man7.org/linux/man-pages/man7/capabilities.7.html) | 83601 | `79CA88F6D8984CA2858860E7267D7C4660F6555151CC1F570305A9C6DFCCF714` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [FC01](https://raw.githubusercontent.com/firecracker-microvm/firecracker/f23a2136011e89e7953923d0efcf67f72d18fc87/docs/design.md) | 9988 | `58CDE9CFA1E9CF7A87B687EAD69BED5FD7542B331AC45DE18E91059D29B6ACE6` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [FC02](https://raw.githubusercontent.com/firecracker-microvm/firecracker/f23a2136011e89e7953923d0efcf67f72d18fc87/docs/jailer.md) | 17751 | `E71C8647C46F5FEE16A2E72B0FE68D0BE130BC84987FF0EF37C55504267927F9` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [FC03](https://raw.githubusercontent.com/firecracker-microvm/firecracker/f23a2136011e89e7953923d0efcf67f72d18fc87/docs/prod-host-setup.md) | 21548 | `19CF9CF9965FB4FDD36C0F55CEB7165E06EFD8601629E956827069D9F1A3DE16` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [GV06](https://gvisor.dev/docs/architecture_guide/platforms/) | 24848 | `79F81D3E2B05E0244073CFB497DCD5F78B4B952C39587163CF5B8DF80CDEF9F9` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [KA05](https://raw.githubusercontent.com/kata-containers/kata-containers/fdff4bb12d2a0292724681e2ca8b47e3e8828100/docs/design/architecture/README.md) | 19776 | `5A48C237FB00F97D4A1DBD327C9FCAC4D6D350CED41C19D3C1072A105DCE657B` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [KA07](https://raw.githubusercontent.com/kata-containers/kata-containers/fdff4bb12d2a0292724681e2ca8b47e3e8828100/docs/design/architecture/storage.md) | 2509 | `AEF5B2F48D01B46090C29E284063D9760B508A490AE07407127849F768DB12FE` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [KA08](https://raw.githubusercontent.com/kata-containers/kata-containers/fdff4bb12d2a0292724681e2ca8b47e3e8828100/docs/design/host-cgroups.md) | 20405 | `F00E39435587F92AA60E21E1FC849584E98EBB028382166183EE58DC7E7E99E3` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [NJ01](https://raw.githubusercontent.com/google/nsjail/4ff54a6e0d5b65a0e1633d6e2fd1425ba6c882ce/README.md) | 8237 | `D2D919E9CF5CF0267F11A124678AA0459B3A822610D2EA75AFA55B385CFFCE84` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [NS01](https://man7.org/linux/man-pages/man7/namespaces.7.html) | 25329 | `F8E08716DF1F4AFDF05B22E11B010E14F47311EB92F0A948FEDBB95099C36AA7` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [QT01](https://docs.kernel.org/filesystems/quota.html) | 13430 | `D9D456E70A7465DFCDFEA1ADDFFCCFEDBBB0124DEF8A05630432140F46EAB140` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [RC01](https://raw.githubusercontent.com/opencontainers/runc/a945133d52eb87415b3a9004f68e11b8b6e0cc2e/README.md) | 14953 | `90C9050F1D5BFF14E28CE2BDF8CD6A6DE8EB71ABD13A732B6DDF5A90D3572D95` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [SC01](https://docs.kernel.org/userspace-api/seccomp_filter.html) | 38437 | `419DE4141B38BCE8754DE25A28902CFB8F7BC98FC6F1C9C9640983CC5BC8065D` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [SD02](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.resource-control.xml) | 110159 | `D57641DF40E45811403DE91E55059B6A8F7506C6812A85CBE9C6BA22900587D8` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [SD03](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/org.freedesktop.systemd1.xml) | 603472 | `59CFEEA5144E169369EE81F2B797FE9EB63EC18CB6AA918C2E66A7D5218117CA` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [SD06](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.service.xml) | 120642 | `12770F86A26DCDF32873225669F5AA9421283C303BBC72BDDB04530850F66D44` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [SD07](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.kill.xml) | 11224 | `448322830DBBD02C64CCA99941BA92705AFE9648241FC917DB7A8D6AE7910E72` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [SD08](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.exec.xml) | 343315 | `44B89BFFCE737AFF803966C207329E9FE2D28AD07709A4BB8E0EDF6A4EC0D844` | Previously read D-REF source reused after byte verification; no redundant fetch |
| [WD01](https://docs.kernel.org/watchdog/watchdog-api.html) | 24828 | `0E0D19BBCE5CCCA8D22DC8CBF754CF626E9D723B144C029477235326C69882D0` | Previously read D-REF source reused after byte verification; no redundant fetch |


## 8. Validation and checkpoint boundary

Validation covers source-byte bindings, inherited authority identity, complete additive document scope, references and internal adjudication consistency, UTF-8/LF, secret-pattern scan, complete diff review, git diff --check, deterministic canonical MANIFEST double rebuild and existing focused offline package tests. Canonical rebuild uses an isolated export plus these five documents; ignored live ecosystem/state is preserved. The external validation receipt records actual outcomes and the checkpoint identity; this document is not its own passing receipt.

The governance baseline remains **52 PASS / 3 SKIP / 1 FAIL / 1 ERROR - INHERITED / NOT RERUN**: known scout_status evidence_only/recommendation_ready failure and missing mcp_types import error. Do not conceal them as PASS or install dependencies to repair unrelated work. Focused tests do not qualify a Linux Host or prove P1-P12 effective enforcement.

The authorized work ends at a local documentary commit and SAFE RESUME POINT. Hard STOP on unexplained baseline drift, unsupported mandatory evidence being promoted to PASS, or any need for installation, Host execution, VM/container creation, privilege, credentials, payment or widened authority. No such action was taken. The evidence gate prevents architecture selection; it does not interrupt completion of these documentary deliverables.
