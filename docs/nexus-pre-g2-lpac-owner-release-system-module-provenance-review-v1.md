# Nexus Pre-G2 LPAC Owner Release System-Module Provenance Amendment v1: Adversarial Review

Review date: 27 September 2026

Subject: `docs/nexus-pre-g2-lpac-owner-release-system-module-provenance-amendment-v1.md`

Subject SHA-256: `49ec2911fb19498a7c797622991eba919b3a52871916371588f59ade23473297`

Disposition: **ACCEPTABLE AS WRITTEN AS A BOUNDED DOCUMENTARY AMENDMENT FOR OWNER ACCEPTANCE**

This is a separate adversarial document pass in the same work session, not an independent human or runtime test. It compares the exact subject bytes against the accepted G2 Host Qualification Scope & Exit Decision/acceptance, Evidence Successor Protocol v1, Owner Release Boundary Amendment/acceptance/Verifier Implementation Spec v1, Package Delivery and LPAC architecture, local protocol v3, and Pre-G2 A0–A6. No executable or qualification scenario was run.

## Under-securing checks

| Challenge | Review finding |
| --- | --- |
| Could a substituted Nexus controller, watchdog, recovery image, probe/canary or dependency evade mapped-byte comparison by calling itself a system module? | No. §2 keeps the strong same-process held-file/mapped-byte rule for every Nexus-controlled executable component and dependency. The Windows exception requires protected canonical Windows component identity and OS trust, not a filename label. |
| Could a signature, path, manifest hash or CI event for one file be presented as proof that another file was actually loaded? | No. §2 binds the physical file identity and mapping base to the same actual process/module load event; a null event handle has no automatic fallback. Any later OS-backed resolution needs its own review. |
| Could the unexplained `fothk` differences be pronounced legitimate and silently allowed? | No. The amendment states that their cause remains unproven. It changes only which proof Nexus demands at the explicitly accepted Windows loader TCB boundary; it does not assert historical runtime PASS. |
| Could Windows system provenance fall through when location, identity, build, applicable trust or CI state is unknown? | No. §3 requires UNKNOWN/STOP for missing, stale, contradictory, untrusted, writable or unbound evidence, and FAIL for positive substitution. |
| Could an old protocol or staging verifier automatically start using the relaxed rule? | No. §§1 and 3 require governed successor activation, exact implementation/package review and separate execution authority. Accepted historical bytes remain unchanged and current STOPs continue meanwhile. |
| Could this acceptance authorize handle implementation, LPAC scenarios, E2B or G2? | No. The amendment expressly excludes these authorities. The separate successor protocol controls the handle evidence mechanism. |

## Over-expansion checks

| Challenge | Review finding |
| --- | --- |
| Does the change require Nexus to reverse-engineer Windows loader rewrites? | No. Windows loader/CI mapping is the stated TCB assumption once Nexus has bound the actual trusted physical system image. |
| Does it add a generic verifier, launcher, signing pipeline, CI-policy change or privileged service? | No. §3 expressly excludes each. Existing fixed verifier/controller/watchdog and package custody remain. |
| Does it rewrite A0–A6, widen HQ1–HQ5 or enter HQ6? | No. It narrows one prior system-module evidence comparison and leaves all other accepted controls and unknowns in place. |
| Does it inadvertently supersede Nexus-controlled mapped-byte requirements in the earlier amendment's main-image, dependency or recovery clauses? | No. §1 expressly limits supersession to verified Windows TCB/system modules; §2 repeats the stronger Nexus rule and covers recovery, watchdog and relevant dependencies. |

## Exact boundary and residual UNKNOWNs

The historical wording superseded is the unconditional application of mapped-versus-file executable-byte comparison to Windows system modules, including its previously reviewed relocation/import normalization, within `nexus-pre-g2-lpac-owner-release-boundary-amendment-v1.md` **Same-process loaded-code binding** and the corresponding main/dependency observation in `nexus-pre-g2-lpac-owner-release-verifier-implementation-spec-v1.md` **Fixed source-level shape**. The old STOP phrase about a weakened mapped-byte standard is narrowed only for that accepted Windows TCB exception. No old file is edited. Nexus-controlled code retains its full mapping check; null or unresolvable load events still STOP.

Actual module/event ordering, physical identity, trust status, Code Integrity compatibility, verifier/debugger lifecycle, watchdog independence, handle inventory, protected successor package, owner-path launch and LPAC Scenario 01–04 are all **UNKNOWN**. Neither this amendment nor its review makes HQ1–HQ5 PASS or qualifies a Host. A positive complete Host binding is ABSENT and G2 remains HOLD.

**Final result: ACCEPTABLE AS WRITTEN.** The amendment is narrow enough for the owner's stated documentary acceptance and preserves the fail-closed boundary. Acceptance should bind the exact subject SHA above; it is not authority to implement, create a qualification package, execute a scenario or freeze G2.
