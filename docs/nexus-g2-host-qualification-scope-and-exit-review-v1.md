# Nexus G2 Host Qualification Scope and Exit Decision v1: Adversarial Review

Review date: 27 September 2026

Subject: `docs/nexus-g2-host-qualification-scope-and-exit-decision-v1.md`

Subject SHA-256: `6CF3AB004B66580531185E7E0CE7394AA349ECB3E1E3905F224ED0259BBFCD69`
Disposition: **ACCEPTABLE AS WRITTEN FOR OWNER ARCHITECTURE REVIEW — NOT ACCEPTED ARCHITECTURE OR RUNTIME EVIDENCE**

This is a separate adversarial document review pass in the same work session, not a second human or agent opinion. It challenged the final decision text against the frozen Roadmap/G1/Pre-G2 and accepted LPAC, E2B successor, Package Delivery and Owner Release boundaries; the current local protocol; and the dated negative/UNKNOWN evidence. No executable, profile, scenario, credential, provider or policy was touched. The SHA identifies the exact reviewed proposal; it is not an approval token.

## Under-securing challenges

| Challenge | Review outcome |
| --- | --- |
| Could HQ1–HQ5 let a locally isolated child count as the first G2 Host binding? | No. Section 2 and HQ6 expressly require an actual accepted capability plus full reachable operation graph, pre-effect admission, budget/resource enforcement, effect/cost observation and reconciliation. Local empty-capability LPAC PASS ends only the local gate. Network-capable LPAC, E2B and G2 remain separate. |
| Could classifying PSS as replaceable allow a bare pre-resume handle count to pass? | No. Current exact PSS STOP remains controlling. A successor needs independently observed same-process handle origin/type/access and later state, actual LPAC timing and negative tests, with separate owner acceptance. Existence of a feasible replacement remains UNKNOWN. |
| Could unexplained mapped `fothk` differences be silently blessed as Windows behavior? | No. The proposal refuses both malicious and legitimate inference, keeps the current comparator STOP, and requires a separately accepted bounded system-module provenance/TCB rule. Nexus-owned actual loaded bytes and dependencies retain stronger binding. |
| Could hash-before-launch make the watchdog trustworthy? | No. HQ1/HQ4/HQ5 require actual process provenance, pre-child readiness, independent controller-loss survival and intervention readback. Current staged watchdog remains unbound. |
| Could Windows TCB assumptions hide an attacker-controlled DLL or substituted package? | No. The trust limit excludes a compromised kernel/owner/SYSTEM, but still requires protected physical package objects, actual loaded-module identity, rejection of writable/unexpected paths and negative substitution tests. Signatures, Code Integrity, paths and hashes are not individually accepted as sufficient. |
| Could receipt integrity be established by child status, PID or manifest hash? | No. Owner-only new records, supported process/call identity, creation time, observation source/scope, event order and OS-side cross-check are required. HQ6 uses supported Host/provider references rather than treating local PID as remote authority. |
| Could a local process kill imply remote cancellation or zero cost? | No. HQ4 is local containment; HQ6 separately requires remote effect and usage/cost reconciliation. G2 ledger and checkpoint/retry semantics remain future implementation obligations. Unknown exposure remains UNKNOWN. |
| Could a Host binding omit stable artifact/operation references needed for checkpoint and recovery? | No. HQ6 requires supported session/call, input/artifact and effect references on a bounded enumerated graph; unknown transitive paths remain ineligible. The future G2 ledger still has to implement durable recovery and validate those references. |
| Could the proposed exit itself authorize execution or G2 code? | No. Section 1 and change control preserve current STOP, exact-byte owner release and separate authority. The exit rule applies only after PASS on the exact configuration and then-valid authorization. |

## Overengineering challenges

| Challenge | Review outcome |
| --- | --- |
| Is the PSS API output itself the security objective? | No. It is an accepted current proof method for no unauthorized handles. Fixed-target status 24 challenges its timing; a versioned equivalent proof may be accepted without relaxing HQ3. |
| Must Nexus explain every undocumented Windows loader transformation? | No. It must detect code substitution at the Nexus/Windows boundary and state the Windows TCB assumption. A bounded system-module rule is proposed; unexplained current bytes cannot PASS while that rule is absent. |
| Does each trusted helper need another helper to attest it? | No. The fixed owner/package/process observation chain and Windows TCB terminate recursion. A concrete uncovered threat and architecture review are required to expand the chain. |
| Must Codex-path App Control refusal trigger broad policy administration? | No. It is exact-artifact launch evidence for one path. The authorized owner path remains UNKNOWN; qualification needs an allowed exact launch but cannot bypass or loosen CI. General signing/distribution is deferred unless needed for that exact launch. |
| Does a 247-file candidate inventory prove dependency closure or require infinite expansion? | Neither. Actual loaded security-relevant edges must be bound. Static candidate enumeration is only preparation and further speculative enumeration can be deferred after closure. |
| Do HQ criteria force a new generic Agent runtime or G2 ledger before qualification? | No. HQ6 tests enforceable Host/provider primitives in a separately authorized bounded binding experiment. Nexus runtime records, sequential orchestration and fault-injection acceptance follow after a positive binding. |

## Cross-boundary consistency and residual UNKNOWNs

- A0–A6, G1, R2/R4/R5, the accepted LPAC architecture, no-outer-Job rule, fixed scenarios and package/evidence custody are unchanged. Option D and the trusted-launch Option A HOLD are not reopened. The accepted E2B successor receives no authorization or qualification from this proposal.
- The candidate replacement for pre-resume PSS lacks a proven supported independent actual-LPAC handle inventory at the required timing. The system-module provenance rule lacks an accepted transformation/TCB proof. Watchdog loaded identity and crash survival, verifier lifecycle, exact external-owner-path Code Integrity compatibility, protected V2 package and actual Scenario 01–04 results remain UNKNOWN.
- HQ6 has no positive exact Host/provider binding, enforceable mandatory hard cost limit where required, live effective policy/effect observations or proven remote reconciliation path. The bounded binding experiment itself requires separate authorization. These are genuine blockers to complete G2 Host Qualification, not excuses to broaden the local Windows probe.
- The proposal does not require a replacement mechanism to be accepted merely because the original is inconvenient. If no equally strong bounded mechanism exists, the exact Host stays unsupported/HOLD. If an observed G2 threat falls outside HQ1–HQ6, a new versioned review is required.

## Review result and scope of correction

The first adversarial pass found a local process identity list that appeared to apply to remote HQ6 evidence, wording that could imply LPAC-specific cases were mandatory for every alternative Host, and insufficiently explicit checkpoint/artifact references in HQ6. The decision was corrected in Sections 2–3 to require supported remote and artifact references, a bounded enumerated operation graph and equivalent properties for other Hosts. The classification/disposition tables were also split so each major item has one primary class and each blocker row one primary disposition. The corrected decision was reread against both challenge lists; no further required change was found.

**ACCEPTABLE AS WRITTEN** means this proposed finite boundary is precise enough for owner architecture review. It does not supersede PSS or mapped-byte STOP, approve a successor protocol, authorize exact bytes, qualify LPAC/E2B, establish positive Host binding, authorize G2 runtime or change the HOLD disposition. Local Scenarios 01–04 remain **NOT RUN**. A later acceptance must explicitly name the exact decision bytes and precise evidence mechanisms it supersedes; acceptance alone cannot promote this static review into runtime PASS.
