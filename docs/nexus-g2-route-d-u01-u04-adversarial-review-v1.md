# Nexus G2 Route D U01-U04 Adversarial Review v1

Version: `1.0.0` | Date: **2026-10-03**

Starting HEAD: `2fb939332c7c20dcbf2a528f296fa1d8a693cc5c` | Branch: `nexus-v2-g2-development`

Status: **DOCUMENTARY CHECKPOINT ONLY / NOT ACCEPTED / NO IMPLEMENTATION AUTHORITY**

Preserved: G2 HOLD; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Scenario 01-04 NOT RUN; Positive Host Binding ABSENT. UNKNOWN != PASS. No architecture selection/acceptance, P1-P12 change, D3, U05 measurement, installation, provisioning, Host execution, credentials, privilege elevation, paid activity, merge, push, tag or freeze.

## 1. Separate challenge pass and disposition

This is a separate primary-agent adversarial pass over the four completed analyses, not an external audit or a delegated assessment. No runtime attack/fault was executed. Reviewed byte identities are recorded below. Completion of a documentary review is not a qualification PASS.

Final result: **C - MATERIAL UNKNOWN STILL PREVENTS ARCHITECTURE SELECTION. SAFE RESUME POINT ESTABLISHED.** U01 HOST_SPECIFIC_EVIDENCE_REQUIRED; U02-B, U03-B and U04-B, all NOT CLOSED. Supported-class/model feasibility is retained; actual operational closure is refused. U05 DEFERRED; D3 NO. No family ranking or architecture acceptance follows.

| Reviewed document | Bytes | SHA-256 |
| --- | --- | --- |
| [nexus-g2-route-d-u01-u04-closure-v1.md](nexus-g2-route-d-u01-u04-closure-v1.md) | 28675 | `7D79F700BEC99FAD03542D88F889B6EAC814CBBB79F4F46100240CAA3C7484B5` |
| [nexus-g2-route-d-u02-ultimate-fence-analysis-v1.md](nexus-g2-route-d-u02-ultimate-fence-analysis-v1.md) | 18910 | `DE1232A0C7484AB2C804432B5CCF190FFE787E5568B47E299FF77447765D7FCB` |
| [nexus-g2-route-d-u03-custody-analysis-v1.md](nexus-g2-route-d-u03-custody-analysis-v1.md) | 14746 | `EB5E6A6B8860B02FCDEA1E28F475D47DA647FAF35023394D64A4C0D7E63D13FE` |
| [nexus-g2-route-d-u04-cost-bound-analysis-v1.md](nexus-g2-route-d-u04-cost-bound-analysis-v1.md) | 12539 | `5D921EEF87CABACC9E6F00F8773D4AC06F77A654DC641AAA427C41348F45DCC6` |

## 2. Seventeen mandatory counterexamples

| ID / challenge | Adversarial counterexample | Evidence and correction | Final classification effect |
| --- | --- | --- | --- |
| R01 Supported docs != machine state | Owner has only a restricted shared guest or unsupported kernel although an Ubuntu page lists features | Closure H01-H14 requires existing identity/status/LSM/runtime/storage; no install or inferred availability | U01 stays NOT CLOSED; no qualified Host |
| R02 systemd common kernel | Agent, watchdog and PID1 lose progress under Host kernel/IO/OS failure | Fence M1/M2 same F4-F6; SD06/SD07/CG01 are inner tools, not an outer independent guarantee | U02 closure refused; external dependency still required |
| R03 Hypervisor TTL renews | Restart/resume gets a new duration or Controller creates a replacement | Fence section 3 interruption semantics; require fixed original absolute maximum AND conserved slot/no change/recreate authority | U02-B candidate only; renewable normal lease rejected as ultimate |
| R04 Reboot clears deadline | Local timer/unit lost at boot, prior grant restored from snapshot | Fence M7 and original boot ledger; distinguish reboot/reset from stop/resume; prohibit resurrection; independent old maximum must survive | U02/U03 unresolved; no blanket 'reboot always clears external cutoff' claim |
| R05 Agent alters cutoff | Agent has broad manager/provider schedule or start/recreate permission | Custody B and fence prearm actor require no extension/replacement rights; read-only calculated timestamp is not immutable scheduling authority | U02/U03 configuration proof still needed |
| R06 Guest reaches control socket | Read-only rootfs still contains runtime/DBus/libvirt/Firecracker socket or inherited FD | Custody section 3 requires complete mounts/FDs/socket/device/actor closure; namespaces alone insufficient | U03 NOT CLOSED; no NO_NETWORK inference from public route absence |
| R07 Evidence guest-writable | Host collector copies mutable guest 'receipt' into protected folder | Custody section 5 keeps source labels; protected destination does not authenticate past source or prevent pre-copy tamper | GUEST_ASSERTED remains data; U03 not promoted |
| R08 Log storage fills | Guest floods serial/journal and blocks mandatory control ledger, IO or quota | FC03 existing bounded-log warning; custody hard storage/reserved mandatory metadata; N12 rate/drop/vacuum not strict attempt cap | U03/U05 reserves unmeasured; release/evidence acceptance refused on missing prerequisites |
| R09 Fixed price excludes traffic | Monthly server cap with metered outgoing traffic/IP/storage extras | Cost C1/C2 and N08/N09 require exact inclusion and hard cap or conservative maxima | U04-B NOT CLOSED; no fixed-price PASS |
| R10 Fees/overage/renewal tail | Taxes or extra resource charges plus repeated periods exceed declared one-month budget | Cost section 3 requires every rate/term/max and finite effective endpoint independent of Controller loss | U04 NOT CLOSED; no arbitrary planning-horizon truncation |
| R11 NO_NETWORK exposes metadata/control | Guest inherits proxy/metadata identity/UNIX/vsock or Host helper | Custody and cost require full channel graph, no infrastructure identity/control socket and bounded Host transport | U03/U04 unresolved; no workload egress/effect qualification |
| R12 Owned hardware hides expense | Unlimited uptime on owned PC incurs electricity/network/storage/fence costs | Cost C3 requires conservative power/rate/time bounds and retention/control services; no assumed zero incremental cost | U04-B; owning machine not complete cost profile |
| R13 Period automatically recurs | Owner disappears; service renews beyond supposedly fixed month | N10 conditional cancellation; cost requires supported no-renew finite period/tail, not an owner reminder | U04 retains horizon gap; stop/idle does not cancel bill |
| R14 Late evidence copy | Workload modifies staged input/logs before collector hash/copy | Custody C sealing/backing-authority closure and pre-effect independently sourced binding; post-copy hash proves only captured bytes | U03 retains release/byte/provenance gap |
| R15 Cleanup cost survives | Work stops but provider disk/IP/Host storage remains indefinitely under failed control plane | Fence finite survivor tail + cost graph/horizon needed; cessation, resource release and billing are separate facts | U02/U04 still block; DELETE intent is not complete release |
| R16 Snapshot persists | Boot disk backup or snapshot survives guest/VM deletion or resumes old authority | No snapshot/restore provision; full native resource inventory/cancellation terms; any existing survivor counted | U03/U04 not closed; no unseen persistent resource assumed absent |
| R17 Blind retry after outage | Controller loses acknowledgment and creates new unit, doubling lifetime/budget | Existing D1 original conserved slot/UNKNOWN; custody F intent and refusal; reconnect status/reconcile original only | No retry/replacement or new authority; U02/U03/U04 exposure remains reserved |

## 3. Three additional evidence-consistency challenges

| ID / challenge | Check and disposition |
| --- | --- |
| R18 External completion mistaken for initiation | N03 initiation delay and N04 normal guest shutdown interval do not prove numerical end-to-end bound during L0/control-plane/common faults. Reject universal summed bound; U02 documentary gap remains. |
| R19 Contradictory shutdown modes | N05 disallows enabled graceful shutdown on limited-runtime VMs. Avoid assuming an additional PENDING_STOP allowance coexists; verify compatible exact fields later. This narrows configuration analysis, not the ultimate fault guarantee. |
| R20 Research pin mistaken for supported deployed release | D-REF main/source commits bind texts; N01 release GA kernel/systemd differ from exact patched/HWE/vendor state; N02 current platform minimum must not be replaced by stale generic recollection. No install/qualification inference. |

## 4. Reconciled architecture/security/testing outcome

Architecture: supported class candidates and mature primitive models are plausible; family compatibility is conditional, ranking unchanged and acceptance NO. Security: F0-F9 accidental/common faults retained, no malicious ultimate-TCB/hardware-destruction escalation, no same-kernel independence claim, no actor renewal/recreate loophole or guest-authored evidence promotion. Testing: no target Host/fault/qualification run; existing offline package tests may pass without proving any of those runtime properties. Cost: every retention/control/renewal tail must be financially bounded before use.

Downgrades apply to proposed optimistic closures: public supported Host becomes class-only; a provider absolute cutoff becomes candidate-only until immutable original-slot/failure-tail evidence; protected-looking logs become source-relative and exact-store-dependent; a monthly price becomes contract-profile-dependent. No fully supported closure was reversed by arbitrary skepticism, and no unknown was declared impossible.

## 5. Scope, STOP and next decision

The prior local documentary baseline and accepted A0-A6/P1-P12/HQ requirements remain unchanged. U01-U04 material evidence is not closed, so D2 stays at result C and the evidence gate STOP applies to architecture selection/execution. The authorized documentary mission can complete with its factual checkpoint; it does not require an unsafe experiment or account access to force a favorable result.

Next owner decision: nominate ONE existing dedicated supported Linux context plus existing independently armed outer-fence, redacted custody and applicable finite cost records, or retain Route D HOLD. Resolve U02 consequence/immutability and U04 contract/horizon gaps before treating status verification as sufficient. No purchase, new Host, weakening of the accepted fault scope, architecture choice or D3 authorization is requested or inferred.
