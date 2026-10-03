# Nexus G2 Route D Reference Adversarial Review v1

Version: `1.0.0`

Date / source retrieval: **2026-10-03**

Baseline: `8818b0b674878f016a779197a6f04cb0c5b3a39f` / `nexus-v2-g2-development`

Status: **D-REF FACTUAL / DESIGN CHECKPOINT ONLY - NOT ACCEPTED; NO HOST OR EXPERIMENT AUTHORITY**

## 1. Review scope, independence limit and exact subjects

A separate root-assistant adversarial/static pass, not independent human/subagent certification. No subagents were authorized or used. Review tests conclusions against the accepted overlay, exact public source bodies/code paths and common-fault/privilege/input/cost counterexamples. No scenario or source example was run. Hash table binds five reviewed subjects; MANIFEST records this review without a self-referential hash.

| Subject | SHA-256 | Bytes |
| --- | --- | --- |
| [nexus-g2-route-d-external-reference-survey-v1.md](nexus-g2-route-d-external-reference-survey-v1.md) | `808B8A1B262BB30FD2DF5D6E7FC9D6A7209361CC2259DA6FFDF1A7AD796445FF` | 19616 |
| [nexus-g2-route-d-reuse-adapt-reject-matrix-v1.md](nexus-g2-route-d-reuse-adapt-reject-matrix-v1.md) | `69201874C2497B18A5CC00F0920CB9828C9F6FF49F88262E74FF80B9FD5DFD9B` | 14040 |
| [nexus-g2-route-d-reference-p1-p12-hq-mapping-v1.md](nexus-g2-route-d-reference-p1-p12-hq-mapping-v1.md) | `E0468FE483508C3DCA040902CAF202D2FAD3A410E821CB6E3B25B8DE9B25F83D` | 17160 |
| [nexus-g2-route-d-d0-d2-input-package-v1.md](nexus-g2-route-d-d0-d2-input-package-v1.md) | `9BD18A4989A3DB5529A0278CFDC39C2B415885E0E7A13393702E90F6623E877D` | 11498 |
| [nexus-g2-route-d-reference-source-register-v1.md](nexus-g2-route-d-reference-source-register-v1.md) | `76EDCEFF09C42CC02C71EBBA5ED1425E0071A71278CD8D9F3D39C2A38850D541` | 27429 |

## 2. Eighteen reuse decisions challenged

Every challenge attempts to falsify its matching R row. Positive outcome means the documentary recommendation already requires these gaps to close, not runtime PASS.

| ID | Counterexample | Required response / documentary result |
| --- | --- | --- |
| R01 | FC05 parent cgroup absent; jailer continues | Reuse only with protected actual placement/limits before guest start; jailer request/default not sufficient |
| R02 | Snapshot/serial/log/backing survives VMM kill | Separate retained capacity/time/byte/cost envelope; no authority/timer restoration; remain UNKNOWN |
| R03 | Kata agent dead while Host VMM remains | Host-external process/unit/fence observations required; guest Wait/Destroy not decisive |
| R04 | Kata overhead cgroup unlimited / virtiofsd share too broad | Close Host/guest/helper and quota/channel graph in selected release; documented default not whole-unit PASS |
| R05 | gVisor virtual tasks exceed Host pids budget; Gofer/directfs exposes owner file | Virtual plus Host limits and exact input/mode observations; no host-PID-count-only proof |
| R06 | nsjail config allows broad network/mount/capability; rlimits miss aggregate disk | Trusted fixed closed policy and effective cgroup/quota scope; no launch = qualified |
| R07 | nsjail monitor stops or wall clock changes while child lives | PDEATHSIG is supplementary; independent conserved Host deadline/fault control required |
| R08 | Workload migrates cgroup; memory overrun/swap/unsupported scheduler | Deny delegation/migration, pin controller/scheduler and numerical overrun; no knob-name PASS |
| R09 | notify extends timer; restart/hooks/dependencies allocate another process | No guest manager authority; each stage/operation included, no automatic grants/lease reset |
| R10 | IO limit/file-size used as disk quota; crash/log/snapshot grows | Finite bytes/inodes/backing/retention with applied supported filesystem proof |
| R11 | runc rootless/shared-PID fallback kills init only; hook runs before admission | Required delegation/private-PID scope and hook exclusion/authority; downgrade/drift STOP |
| R12 | containerd daemon dies; shim/tasks/content/snapshot remain | Original task/shim/object inventory and independent manager/fence; separate deletions/readbacks |
| R13 | bwrap arguments/FD/TTY/D-Bus pass owner capability; parent guard lacks deadline | Fixed policy, no owner sockets and independent resource/lifecycle/effective evidence |
| R14 | Landlock best-effort omits unsupported mandatory restriction; seccomp broad | Exact ABI/policy must enforce required scope or STOP; optional defense cannot rescue missing hard boundary |
| R15 | K8s retries/replaces at uncertain outcome or resets deadline on suspend | Pattern extraction only; retain original identity, no blind retry/reset; no cluster adoption |
| R16 | Reboot restores expired grant or inventory is lost | Default-deny boot barrier, conserved original refs/exposure/clock; no positive effect evidence => UNKNOWN |
| R17 | Host grant receipt/log or fixed-cost estimate substituted for authority/money | Independently issued authority, actual custody, hard external bounds and protected Nexus adjudication |
| R18 | Watchdog, manager, agent share failing kernel/Host | Independent supported outer failure coverage or family remains ineligible; no new generic runtime implied |

## 3. Cross-cutting acceptance challenges

- Isolation is not lifecycle. None alone receives P5/P6/P7 or complete HQ PASS. Native mechanisms are scoped and composable, not declared equivalent merely by project maturity.
- Rootless is not least-privilege/resource proof. Current bwrap removed setuid support; runc source fallback and delegated cgroups require exact mode. No userns/kernel enablement/elevation is performed.
- Kata cgroup/storage defaults, FC absent-cgroup path, nsjail realtime monitor, systemd notify/oneshot/restart/scope attachment, gVisor virtual tasks and K8s duplicate/reset behavior are concrete downgrade reasons, not invisible favorable assumptions.
- Source/document discrepancies stay explicit: old Kata architecture.md 404 resolved via design index; host-cgroups document is a dated design not automatically current runtime default; bwrap README historical comparisons cannot overwrite per-file current source/license; pinned upstream main not selected supported release.
- Licenses permit plausible use only under actual terms. bwrap core LGPL-2.0-or-later differs from supplied LGPL-2.1 COPYING; systemd exceptions and kernel syscall-note scope preserved. External command versus linking/modification/bundling remains separate; no source vendoring or legal approval.
- Lifecycle request, runtime status, zero-live, retained-resource absence, effects and billing settlement remain separate. Safe refusal/UNKNOWN is not useful success or G2 acceptance. All eleven P7 states retained.
- A virtual machine/kernel/container is not a default security proof. AppArmor/SELinux/Podman/nspawn are not silently selected or claimed qualified. No broad provider search/support interaction or new account facts.
- A conclusion A justifies future D0-D2 documentary work, not immediate architecture/execution. Missing actual Host/outer fence/cost/custody can stop a future family; it does not prove Route D globally impossible or authorize a material custom isolation runtime.
- All proposed privileges/trust additions remain future design obligations. HQ5/HQ6 remain Nexus-owned; a narrow adapter cannot become arbitrary shell/runtime/socket broker or own a generic scheduling loop.
- Complete diff must be exactly six new documents plus MANIFEST. All 259 historical entries, accepted architecture/code/frozen refs/V4 must remain unchanged. No acceptance record/commit or D0 phase entry occurs.

## 4. Verdict and deterministic gate

**ACCEPTABLE AS WRITTEN FOR A FACTUAL / DESIGN CHECKPOINT.** Overall **A** remains supported; mature substrates appear sufficient for further design of most low-level mechanics. It is NOT a complete qualifying hard envelope, selected family, installed Host, experiment authority or architecture acceptance. Route D remains feasible for further design; qualified fixed custody/failure/cost/provenance/effect sources remain UNKNOWN.

Verify: 64 exact source-body hashes/URLs/commit pins with tier/scope/exclusions; ten major systems plus justified kernel concepts; ten license rows with bwrap/systemd/kernel/docs distinctions; eighteen R and eighteen X rows; P1-P12 96 cells plus HQ1-HQ6 48 cells using only declared vocabulary; eight P5 primitive/failure rows; F0-F9 and eight architecture correlations; eleven P7 states; four family rows and eight Nexus-owned component rows; D0-D7 NOT STARTED; five exact review subject hashes; UTF-8/LF/reference/control/trailing/secret checks; canonical double MANIFEST 259 -> 265 preserving historical entries; focused tests and bounded known governance 52 PASS / 3 SKIP / 1 FAIL / 1 ERROR. Actual test/manifest/commit results saved externally/final report, not self-referential committed claims.

No runtime experiment or exhaustive security/maintenance audit occurred. UNKNOWNs: selected supported release/dependency/privilege/actual Host; same-unit actual loaded byte and effective state proof; numerical whole-unit fault/cost/fence; protected controller/evidence/original-effect recovery and qualification. Component existence and public code do not close them.

Agent & Skill Utilization: root assistant source review, synthesis and separate adversarial pass only; no subagents, Nexus planner/runtime or provider SDK. Documentary-review skill USED for manifest-first scope/evidence/reconciliation discipline. Public-source collector/validation helpers remain external to repository and do not implement HostAgent/HostAdapter. No secret/credential environment inspection.

Exact next task: request separate owner authorization for bounded D0-D2 research/design, fixing capability, existing Host availability, supported substrate/fault/cost/custody and qualification questions without installing/executing or accepting a family. OWNER ACTION REQUIRED: YES for that future authorization; none for credentials/system action in D-REF.

Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD. D0-D7 NOT STARTED. Route B unresolved; OpenAI human escalation PENDING. Accepted architecture/A0-A6/P1-P12 and sealed V4 unchanged. No installation, Host/provider execution, credentials, paid activity, privileged/system changes, G2/G3/G4 implementation, acceptance, merge/push/tag/freeze.
