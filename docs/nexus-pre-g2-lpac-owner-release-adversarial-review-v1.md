# Nexus LPAC Owner Release Amendment: Final Static Acceptance Review v5

Status: **INDEPENDENT STATIC DESIGN REVIEW; OWNER ACCEPTANCE PENDING**
Disposition: **ACCEPTABLE AS WRITTEN AS A PROPOSED BOUNDED AMENDMENT**

This review incorporates rounds v2–v4 and the final recovery-byte correction. The proposal and specification now require the case-03 recovery image, if launched by the verifier to preserve one owner action, to meet the same pre-instruction mapped-main-image, dependency, token, Job and receipt gates as each controller. A path, manifest membership or prelaunch digest alone cannot qualify recovery. The controller-created watchdog remains subject to the existing watchdog checks and exact reviewed bytes; if their observed load evidence fails any accepted requirement, STOP rather than treating the verifier's manifest check as independent mapping proof.

The proposal explicitly changes the direct owner-to-controller launch rule and adds one same-owner, non-elevated, fixed-purpose trusted component. A separate owner-accepted versioned amendment is therefore mandatory. Its v2 destination root is only proposed and does not exist as an authorized package. No accepted A0–A6 text, frozen runtime integration, LPAC scenario semantics or E2B protocol changes. The earlier v1 package and evidence remain historical.

Adversarial threats remain addressed by exact STOP conditions: wrong/stale/replaced bytes, manifest or path substitution, parent DELETE/DELETE_CHILD, reparse/hardlink/ADS, mapped-file mismatch, PID reuse, null debugger handles, unexpected or late DLLs, loader timing, controller/debugger interference, wrong token/elevation/outer Job, inherited environment/handles, verifier/controller/watchdog crash, forged receipt and premature release. Microsoft API contracts identify candidate primitives but do not demonstrate actual Host behavior. Each listed runtime property is **UNKNOWN** pending separately authorized tests; any missing or contradictory mandatory fact stops the sequence.

The only decision this review supports is that the proposed conditional amendment is precise enough for owner architecture acceptance. It does not authorize its implementation, package creation, a verifier or controller launch, any LPAC scenario, credential access, network/E2B or G2. Positive Host binding remains absent and G2 remains HOLD.
