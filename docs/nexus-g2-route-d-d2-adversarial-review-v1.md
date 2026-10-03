# Nexus G2 Route D D2 Adversarial Review v1

Version: `1.0.0`

Date: **2026-10-03**

Starting baseline: `a0bdfd2b6ea46844d317dff67687e681caacc3c3` / `nexus-v2-g2-development`

Status: **FACTUAL / DESIGN CHECKPOINT ONLY - NOT ACCEPTED; NO IMPLEMENTATION OR EXPERIMENT AUTHORITY**

## 1. Separate review pass and verdict

This is a separate root-assistant adversarial/static pass over the four completed design documents and relevant accepted/D-REF source semantics. It is not independent human/subagent certification, runtime validation or a security freeze. No subagents were authorized or used. The prior proposal's conditional preference for A was challenged, not promoted to a decision A merely to enable progress. No prior actual D2 A acceptance exists to downgrade.

Verdict: **SUITABLE FOR FACTUAL / DESIGN CHECKPOINT WITH D2 RESULT C; NOT READY FOR ARCHITECTURE ACCEPTANCE OR D3.** Complete actual independent ultimate-fence coverage is not established. A merely separate process, manager timer or guest VM boundary cannot repair this gap. U01-U04 remain mandatory documentary blockers; U05 needs an actual safe quantified supported profile later. Requirements/threat/lifecycle analysis is useful while decision remains unresolved. Route D stays feasible for further design; P5/P6 wording remains unchanged.

Exact subjects reviewed (review's own identity belongs to MANIFEST; no self-referential commit/hash claim):

| Reviewed subject | Exact UTF-8/LF bytes | SHA-256 |
| --- | --- | --- |
| [nexus-g2-route-d-d0-requirements-v1.md](nexus-g2-route-d-d0-requirements-v1.md) | 30115 | `BE26E444BFAF23891A7BE34C149BE0FAC9FFE7152EE9ACABAFB473CA336543C3` |
| [nexus-g2-route-d-d1-threat-model-v1.md](nexus-g2-route-d-d1-threat-model-v1.md) | 24001 | `D3D7E270B545F15CFBC9848B2B048B3939F43C425C7253EA0E42AFF74B03205C` |
| [nexus-g2-route-d-d2-architecture-analysis-v1.md](nexus-g2-route-d-d2-architecture-analysis-v1.md) | 31716 | `FE3EA6440DDC3563C7C2791E7DAA34166FFA959B3EAEC0847882869422D1FD48` |
| [nexus-g2-route-d-d2-lifecycle-and-evidence-design-v1.md](nexus-g2-route-d-d2-lifecycle-and-evidence-design-v1.md) | 15610 | `41F82971C417CE41A11BD90E149670A79F8886A106427D7DA1012DFA86F44845` |


## 2. Twenty required adversarial challenges

| # / challenge | Counterexample applied to the proposed composition | Design response and disposition |
| --- | --- | --- |
| 1 Workload escape | A syscall/mount/device/FD or VM/share path reaches Host beyond declared policy | D0 H03-H08/R04-R06 and D1 cases 9-13 require actual effective boundary; no runtime maturity proof. U01/U03; unqualified. |
| 2 Cgroup escape | Workload writes migration/delegation or gains Host namespace/scheduler rights | Protected nondelegated ancestor, denied topology/control authority and actual membership; D0 R07/D2 section 6. U03/U05; no rootless sufficiency. |
| 3 Helper outside cgroup | Setup, Sentry/Gofer, shim/VMM/share daemon logs/allocates outside guest leaf | D0 U defines entire graph; bounded companion leaves under envelope or separately qualified finite envelope. Unknown helper blocks release, not exempt from P5/P6. |
| 4 Runtime daemon privilege | Broad task-selected bundle/hooks/runtime path asks privileged daemon to act as deputy | Fixed profile/operation; no general runtime command/API and no custom scheduler. D2 components/responsibilities; exact narrow privilege U03. |
| 5 Host socket exposure | Passed FD/bind mount gives Docker/containerd/systemd/API access despite private netns | Closed input/FD/socket/service graph; first fixture denies all. D1 TB2-TB8/case 12; no network-only inference. Actual custody U03. |
| 6 Deadline extension | notify extension, randomized extra time, manager mutation, restart/pause/recreate resets runtime | Conserved original allocation origin; no notification/renewal/restart scope; external nonrenewable bound. D2 section 5. Actual ultimate fence U02 remains blocking. |
| 7 Controller loss | Lost response after creation/start leaves active work and financially reserved effect | Native lease independent of client; durable one slot; no hidden recreation; original query/UNKNOWN. U02/U03/U04, not client timer. |
| 8 Manager loss | Agent/watchdog/PID1 remain different processes but share kernel/storage/time failure | D1 correlated review requires supported outside-domain autonomous bound. Local timers cannot declare ultimate cessation. U02; result C. |
| 9 Reboot | New boot ID/live update/snapshot resumes old resources or reset lease | Default-deny boot, no auto-resume/old grant restore; cold/off evidence and original resource inventory needed. Lifecycle section 3 excludes warm/live-update preservation until analyzed. U02/U03/U04. |
| 10 Stale workspace | Old files/metadata reuse unit name to hide a prior unresolved attempt | Never reuse original identity for new effect; protected references, immutable stage, quarantine and no replacement. U03/U04; no wipe-before-reconcile. |
| 11 Leaked mount | Process exit leaves mount/backing/virtio-fs/open helpers | Separate RESOURCE_CLEANUP with explicit inventory/absence/readback. Zero-live and path deletion insufficient. Residual lifetime U04 prevents ready prototype. |
| 12 Network leak | Inherited socket/Host proxy/DNS/IPv6/metadata helper bypasses disabled interface | NO_NETWORK covers full channel graph, helper network and FD passing; future modes separately qualified. D0 R17/D2 section 6. U03; no applied-denial claim. |
| 13 Secret leak | Environment omitted key but image/home mount/FD/log/evidence holds it | No real secret access/probes; synthetic markers only later; broad directories/sockets/evidence denied. Credential protocol deferred. U03; no actual secrets read. |
| 14 Evidence forgery | Guest prints signed-looking PASS; Host copies partial/stale log to protected store | Observation classes/source/identity/sequence/coverage validated; protected false data stays false. Separate guest data and decisive evidence. U03; current static documents are not HQ proof. |
| 15 Config drift | Effective mounts/cgroups/profile actors differ from cached qualified request | Compare actual supported state/byte/custody/config before effect; material change stops invalidates. D0 R05/R15, D1 case 30. U01/U03/U05. |
| 16 Runtime upgrade | Supported new runsc/jailer/nsjail/runc changes helper/policy/load behavior | Version/dependency/source/qualification scope invalidation and new qualified review; no upstream-main release recommendation. D2 sections 2/4/9. U01. |
| 17 Host upgrade | Kernel/manager/FS/backport changes cgroup/quota/timer/storage/source semantics | Invalidate affected supported binding; feature floor alone never means security/support/current applied proof. D0 H01/H09/H20/R20; U01/U05. |
| 18 Unknown termination | SIGKILL request succeeds but task stuck or outside helper/guest graph unobserved | Request/ack/zero-live/resource/effect axes separate; outer physical consequence absent => UNKNOWN. U02/U03, no false finite 2-second completion guarantee. |
| 19 UNKNOWN retry | Fresh request ID or restored conversation obtains another slot to rerun uncertain effect | Durable logical-operation/attempt slot and reserved exposure; replay/replacement forbidden until positive reconciliation and renewed admission. D0 R13/lifecycle section 3. U03. |
| 20 Cleanup failure | Deadline/zero-live proven but disk/network/metering/effects survive | Separate bounded survivor envelope and authenticated resource/effect/cost facts; retain UNKNOWN, stop further admission. Capacity does not bound retention lifetime. U04; no cleanup assumed. |

All twenty counterexamples have explicit controls/UNKNOWN consequences. This is a completeness check of the design challenge list, not twenty passed runtime tests. D1 separately contains the thirty requested attacks/failures.

## 3. Cross-cutting review findings

1. **Critical selection blocker U02 retained.** systemd timer semantics are narrower than whole-unit/fault lifetime. Its local manager/kernel failure domain remains shared. Hardware watchdog API describes variable reset/feed/disable behavior; a healthy feed loop can mask continued work. An on-demand Controller poweroff cannot survive that Controller/network loss. Only an actual autonomously pre-armed separately enforced finite lease could close the chosen envelope; none is currently evidenced. No invented numeric outer maximum.
2. **Pre-creation safety is explicit.** Lifecycle PREPARE is pure validation; all resource/fence/upload/staging effects require prior authority/reservation. Actual inner unit creation is bounded trusted setup under already-protected limits/fence, never a guest-running-before-limits window. Outer-arm operation itself needs supported bounded effect/cost/no-replacement semantics; if uncertain, no create. Actual tooling/release method U03 is not repaired by an attractive diagram.
3. **Numeric target is not total maximum.** Inner 5/10/1/2/10-second targets, CPU/memory/tasks/disk/output limits are owner-review proposals. Overshoot/control reserves/image overhead/finite survivor retention/outer-fault latency remain unknown. Nominal t0+28 s is a cleanup-observation target, not a claimed hard maximum. D3 max exposure stays UNKNOWN / NOT ADMISSIBLE.
4. **Common gap makes decision C appropriate.** A/C are conditional carried-forward candidates; B/D reserved with concrete capability-fit criteria. No family is excluded for complexity or insufficient evidence; no unfixable incompatibility documented. A small comparative design cannot substitute for missing common Host/fence/custody/cost inputs. Decision B/A would currently hide the shared critical premise.
5. **No architecture drift.** Requirements are candidate Route D design, not modifications of A0-A6/P1-P12. HQ1-HQ4 supply/verification and Nexus-owned HQ5-HQ6 adjudication remain intact. No generic runtime, supervisor, model loop, arbitrary root broker, new identity/secret platform or deployment machinery is built or justified.
6. **Evidence/cost states are honest.** Guest/native/Host/Controller/provider observations are scoped. Qualification is not authority, hash is not enforcement, all eleven P7 states persist. Actual cost contract/horizon/rates/headroom are absent. Fixed pricing is a conditional cost-model preference, not zero money or a purchased/selected Host.
7. **Finite scope maintained.** One owner/Host/original unit; no public endpoint, tenants, cloud service, production secret/API/network/workload, or uncontrolled fault tests. First future mechanics fixture is not an accepted capability/HQ6 experiment and has no generic task authority.

## 4. Architecture, Security and Testing reconciliation

Architecture: D0 requirements/HQ matrix and D2 families/components/lifecycle/responsibility design agree on result C, no exact proposed stack and no acceptance. Security: D1 scenarios/correlations/credential/evidence graph and this challenge pass preserve U01-U05 and no safe prototype. Testing: only documentary/source-byte/reference/manifest and existing focused offline repository tests are in this checkpoint's authorized scope; no Host/tool/VM/qualification execution. Existing governance baseline 52 PASS / 3 SKIP / 1 FAIL / 1 ERROR remains inherited known evidence unless explicitly rerun and shown changed; it must not be rewritten as green. Actual checkpoint validation and commit facts are saved outside these self-bound review subjects.

Checkpoint gates: inspect exact documentation-only diff; verify four review-subject hashes and all internal references/source bindings; UTF-8/LF/control/trailing whitespace and secret-pattern scan; canonical MANIFEST twice, preserve all 265 historical entries/bytes; git diff --check; focused tests in an isolated source export; final clean local commit with no push/tag/merge/freeze. No new persistent test code is needed for reversible document changes. The external validation helper is not Host Agent/HostAdapter code and does not become a package entry.

Agent and Skill Utilization: root assistant plus separate root review pass; no delegation/subagents. nexus-g2-documentary-review skill USED for manifest-first resume, bounded source use, evidence/UNKNOWN discipline and reconciliation. No Nexus planner/runtime, provider SDK or managed Host execution. Source-fetch and document/validation helpers remain external to repository; no credential/environment inspection.

## 5. Exact STOP and safe resume

The authorized D0-D2 factual/design deliverable can be checkpointed. **STOP before architecture acceptance, D3 proposal entry/implementation or any experiment because U01-U04 lack actual supported Host/fence/custody/cost evidence; U02 leaves the mandatory ultimate lifetime boundary unresolved.** This is insufficient evidence, not a finding that Route D or any mature runtime is insecure/impossible. Do not invent work to consume time.

SAFE RESUME POINT ESTABLISHED. Resolve only stated U01-U04 with read-only supported status-only records for an existing owner-controlled Host and actual independent fence, exact narrow authority/evidence custody and finite all-in cost/survivor horizon. Then scope U05's measurements inside the already-safe envelope. Owner decision: whether such existing records are available and whether to authorize only that documentary closure. No D3 experiment, provisioning, purchase or credential use follows.

Preserved state: G2 HOLD; Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT. Route B unresolved / retained; Route D FEASIBLE FOR FURTHER DESIGN. Accepted A0-A6/P1-P12 unchanged. No installation, Host execution, privileged operations, credentials, paid activity, HostAdapter/Host Agent code, architecture acceptance, merge, push, tag or freeze.
