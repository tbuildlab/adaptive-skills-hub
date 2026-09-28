# Nexus Pre-G2 LPAC Verifier/Watchdog Responsibility Amendment v1 — Adversarial Document Review

Review date: 28 September 2026

Subject: `docs/nexus-pre-g2-lpac-verifier-watchdog-responsibility-amendment-v1.md`

Subject SHA-256: `4c49754a1e25db097cbb2d17bec1611a9306b971b75795c17b98b14902d821b3`

Subject bytes: `26,452`

Result: **ACCEPTABLE AS WRITTEN FOR OWNER ACCEPTANCE**

Status: **SEPARATE ADVERSARIAL DOCUMENT PASS — NOT OWNER ACCEPTANCE, IMPLEMENTATION APPROVAL OR QUALIFICATION**

## 1. Review basis and attribution

This is a separate adversarial document pass in the same work session, not an independent human or subagent opinion. It examines the amendment's final bytes against the accepted Owner Release Boundary Amendment/acceptance, Verifier Implementation Spec, Evidence Successor Protocol/acceptance, System-Module Provenance Amendment/acceptance, Scope & Exit Decision/acceptance, Pre-G2 A0–A6 and the preserved `NEW_ARCHITECTURE_REQUIRED` checkpoint. Historical proposal headings are interpreted through their acceptance records. No source, staged executable, V2 package or frozen document was changed; no binary was built or executed, and no qualification or provider action was performed.

The finding is narrow: the proposal specifies a conditional creator/observer topology and falsifiable failure contract sufficiently precisely for owner architecture acceptance. It does not demonstrate that the contract is implementable on the actual Host or satisfied by existing staging. The interrupted detach/attach implementation remains unaccepted, and the original historical rule remains controlling until governed supersession.

## 2. Bounded corrections and final re-review

The first document pass found a cleanup ambiguity in §5.1: debugger-thread exit can terminate its direct debuggees while another surviving verifier thread retains a Job handle. Final-close cleanup cannot then be assumed. The final amendment explicitly requires whole-verifier termination within the fixed abort bound after unexpected debug-thread exit; every authorized Job-handle holder must be inventoried and closed/reconciled. The abort path must not depend on the observer's locks, target operations or receipt flushing. The historical specification heading was also corrected to **Fixed source-level shape** for exact traceability.

A second pass reviewed the complete corrected subject, including A–I and the suspended/create-to-assignment windows, rather than treating either correction as runtime evidence. No unresolved documentary contradiction requiring another correction was found. The stall/fail-safe composition remains an implementation and experimental UNKNOWN, with an explicit STOP/abandon criterion; this review does not quietly assume a responsive debugger.

## 3. Adversarial challenges

| Challenge | Final finding and required boundary |
| --- | --- |
| 1. Observing watchdog becomes a generic debugger or arbitrary launcher. | §§2–3 permit only the same existing verifier, one fixed controller and corresponding watchdog per existing case, and existing exact case-03 recovery. Caller paths/PIDs/cases/deadlines/capabilities are prohibited. No arbitrary attach, command interface or target memory/context editing is granted. Closed tables and imports/source must be re-reviewed; no implementation is approved here. |
| 2. Verifier failure strands a suspended/running watchdog in a handoff window. | §3 requires direct debug creation by the verifier and a retained connection through exit. §5 A–D forbids intentional detachment and replacement after ambiguous creation. Default/TRUE kill-on-exit must cover the first creation and suspended window. There is no controller-to-verifier attach gap in this proposal. Actual fault behavior is UNKNOWN, not inferred from synthetic handoff success. |
| 3. Controller failure races with verifier/watchdog cleanup. | §5 E and the cleanup invariant bind actions to the same held process/Job objects, permit only idempotent abort/termination, and require actual outcome evidence. Job name/absence or a raced status line cannot prove zero live processes. An unexpected failure stops later cases; expected case-03/04 outcomes require their original complete criteria. |
| 4. Continuous debugger suspension prevents independent watchdog cleanup. | §5.1 explicitly admits that a watchdog debug event pauses its user-mode cleanup. It requires bounded event service and an independent in-process timer/whole-verifier termination path without observer locks/I/O dependencies. No deadline extension is allowed. Controller-loss independence is conditional on that verified composition; suspension defeating every cleanup path is STOP/new decision, not PASS. The timer is confined to aborting this verifier and issues no evidence or qualification decisions. |
| 5. Debug kill-on-exit kills the watchdog while leaving LPAC or a Job handle alive. | §5.1 distinguishes controller-loss survival from verifier-loss termination. The latter requires combined debugger/last-Job-handle closure evidence and termination of surviving verifier threads. No assertion that watchdog survives verifier exit is made. Job handles cannot enter LPAC or unrelated processes; suspended LPAC between creation and assignment is covered by the retained controller debug connection and must be fault-tested. |
| 6. Watchdog late-loaded cleanup code escapes provenance. | §§3–4 retain creation, initial and every relevant late-load gate until watchdog cleanup and exit, including after controller exit. The verifier cannot stop its loop after only controller completion. Null handles, unbound mappings, byte/identity disagreement or unsafe continuation STOP. The Nexus strong rule and separate bounded Windows TCB rule remain distinct. |
| 7. PID reuse, forged registration or object substitution produces false evidence. | §§3–4 require verifier-created returned process handles, PID plus creation time, image physical identity/byte basis, protected ancestors and fixed owner-only records. A controller request cannot choose a PID/executable. Job identity requires more than a name. Missing same-object/order proof is UNKNOWN/STOP; successful attachment/prehash/path alone cannot establish provenance. |
| 8. Verifier acquires new privileged authority or replaces LPAC/Job enforcement. | §§1–4 keep same-owner non-elevated/no-outer-Job origin and the existing Windows rights boundary. Controller remains LPAC creator/observer and Job owner; verifier never becomes the LPAC executor. §6 rejects any rights expansion, service/broker, elevation, password transfer, Task Scheduler, breakaway or Option A fallback. No broader LPAC access or Windows-policy change is permitted. |
| 9. Missing crash evidence or a child's ready receipt is normalized into PASS. | §§4–7 require independent same-process observations, source/scope and ordered cross-record evidence. Ready/self-report/exit code/Job absence alone cannot PASS. Interrupted receipts remain UNKNOWN pending separate owner/OS reconciliation. STOP forbids later cases and does not excuse abandoned processes. |
| 10. One responsibility fix expands finite HQ1–HQ5 into a runtime or infinite attestation. | §§1–2, 6–7 fix four sequential scenarios and bounded supporting fault assertions, not a fifth scenario, new Host capability or additional observer component. A0–A6, frozen integrations, Windows TCB and finite Scope & Exit remain intact. No HQ6/E2B/G2 or verifier-of-verifier is added. |

## 4. A–I failure coverage cross-check

| Required fault | Contract reviewed | Remaining proof obligation |
| --- | --- | --- |
| A: verifier before controller | §5.2 A; zero new process, no automatic resume | Positive creation/absence readback rather than missing evidence. |
| B: verifier after controller/before watchdog | §3 barrier; §5.2 B; controller debug kill | No LPAC/Job process before watchdog readiness; tracked synthetic-object cleanup. |
| C: verifier while watchdog suspended | Direct creation; §5.2 C | Loss at creation return/main event/pre-release kills both direct debuggees. |
| D: verifier after watchdog release | §5.1; §5.2 D | Controller/LPAC debug termination and last Job handle close across assigned/unassigned/running states. |
| E: controller loss with verifier alive | §5.2 E | Watchdog survives, late loads stay gated, exact Job cleanup works without controller progress. |
| F: verifier loss during watchdog cleanup | §5.2 F and in-process abort | Fault at late load/Job open/termination/wait; bounded complete cleanup, including held Job handles. |
| G: watchdog loss | §5.2 G | Pre-child refusal or full case abort, no replacement, all process/tree exits verified. |
| H: detach failure/lost connection | §5.2 H; all detach forbidden | Any attempted/successful/failed detach invalidates; do not rely on a lost debug connection for termination. |
| I: incomplete/contradictory provenance | §4; §5.2 I | Withhold affected code continuation, abort with trusted paths, classify FAIL/UNKNOWN without executing unverified cleanup. |

The same contract includes unexpected debugger-thread exit and an alive but stalled observation thread. It does not presume that documented default kill-on-exit proves bounded wall-clock intervention or a complete LPAC tree. A compound loss requires demonstrated kernel/Job fail-safe and owner readback, not just process-level status. If the composition cannot satisfy the accepted bounds, the proposal itself requires rejection/HOLD rather than a weakened proof.

## 5. Minimality, security invariants and API basis

The proposed change is a bounded formal supersession of the controller-only observer/creator allocation, not an amendment to A0–A6. The fixed pre-watchdog barrier, internal abort timer and finite metadata are necessary consequences of moving creation/continuous observation into the existing verifier. They may not become a generic health service, debugger or command broker. Watchdog independence from controller is preserved as a tested property; independence from verifier failure is supplied by termination/Job cleanup instead of claiming watcher survival. Neither a new executable nor a privileged trust boundary is introduced by the document.

Strong actual-loaded Nexus byte proof, bounded Windows TCB provenance, PID/creation-time and held-object binding, protected package custody, observed effective environment/TEMP/workdir, HQ3 relevant-handle evidence, Job containment/negative descendants, fixed timers, cancellation/recovery, flushed owner-only evidence and fail-closed UNKNOWN handling remain mandatory. The one inherited ready-event allowance is for the trusted watchdog only; the LPAC child still permits zero inherited handles. A network-capable LPAC, provider cancellation/cost controls and complete Host binding remain separately qualified.

Microsoft's [DebugSetProcessKillOnExit](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-debugsetprocesskillonexit), [WaitForDebugEvent](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-waitfordebugevent), [debugger main loop](https://learn.microsoft.com/en-us/windows/win32/debug/writing-the-debugger-s-main-loop), and [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) support the document's API distinctions. They do not prove the combined candidate's actual event ordering, liveness, nested debugging, last-handle closure or cleanup. No API availability is scored as feasibility PASS.

## 6. Final disposition and remaining UNKNOWNs

**ACCEPTABLE AS WRITTEN FOR OWNER ACCEPTANCE.** This is a review of a conditional architecture document, not approval of code, a package or execution. No deeper architecture conflict is established by this document review; runtime feasibility may still falsify the candidate.

Remain UNKNOWN: exact multi-debuggee startup/late-load ordering and controller LPAC-debugger interaction; full actual dependency/byte closure; effective input/handle observations; observation-thread abort reliability and bounds; controller/watchdog/verifier combined crash/stall/Job cleanup; original isolation/descendant/cancellation/recovery outcomes; owner-path active CI/enforcement identity and launch of the final reviewed bytes. These UNKNOWNs are deliberately not resolved by documentary acceptance.

Only explicit owner acceptance of these exact reviewed documents and supersession scope can establish the successor architecture. Separately valid bounded implementation authority would then be needed for implementation/static preparation. Exact package review and separate exact-byte execution authorization remain later gates. No old release/implementation instruction silently activates the amendment. The sole next step is **owner accept/reject review of this document pair**.

**Scenario 01–04 NOT RUN; HQ1–HQ5 NOT PASS; Positive Host Binding ABSENT; G2 HOLD.** No acceptance record/MANIFEST change, commit, merge, push, tag or freeze is made by this review.

## 7. Documentary validation performed

Strict UTF-8/no-BOM decoding, final newline, trailing-whitespace, heading separation, table-column consistency and repository document-reference checks passed for both new files. The review's subject digest/byte count binds the final amendment. A bounded known-secret-pattern scan found zero hits in these two documents; this is not a universal secret-absence proof. Tracked and staged diffs are empty; inspection of the untracked additions and `git diff --check`/new-file whitespace checks found no unrelated changes or whitespace errors. Git's normal LF/CRLF conversion notice is not an integrity PASS or a reason to change repository settings.

Repository `MANIFEST.json` remains at SHA-256 `c6d15c45b4acea5205cc52ec0b03534c1c919ad8137331b833cfc4d218c60558`; the immutable V2 manifest digest remains the value recorded in the amendment. The protected V3 root does not exist. No build, regression suite, synthetic runtime test or LPAC scenario was run in this documentation-only phase. Baseline branch/HEAD remain those in the subject; the only working-tree additions are this review and its amendment, both untracked and uncommitted.
