# Nexus G3 D01 native Owner Origin hosted continuity v1

Date: 2026-10-10. Source checkpoint: `3b9f7ea649c7d32e0bdbeb2eb2ed0f6a345399b8`. Branch: `nexus-v2-g3-live-qualification`. Additive diagnostic evidence; no historical finding is rewritten.

The LIVE_DIAGNOSTIC_NATIVE_OWNER_ORIGIN artifact was staged once as deployment `dpl_DXnJxVudUCQeVytf6zkhe18DaNqT`, verified and promoted. Staged and stable checks both passed: exact project and Production target, READY, Node 24.x, Other framework, fixed diagnostic function, all 19 source UIDs and all three public asset byte hashes. Source/package SHA256 is `4cce45ae9dd5a11e72a9cdb8c36bd9c93b5dfb4ed2e8057b4059b087b623c626`. Stable routing is `https://nexus-g3-qual.vercel.app`. No account setting, environment variable or secret source changed. The verifier made zero Stytch calls and retained no secret, cookie or CSRF value.

The browser's fresh public root exposed strict-origin metadata and an unauthenticated DENY / NONE context expiring at 1791604679418 (2026-10-10 03:57:59.418 UTC). A single documented native Return action on the Display control locked the controls. The URL remained the root and no private or JSON response page was observed. A subsequent safe GET returned DENY / RETIRED with no context deadline. This proves retirement was observed, but not that the intended form POST received the required DENY / RETIRED response: a process-instance change could also retire an in-memory context. Therefore the actual navigation response gate stays NOT_PROVEN. No authenticated backend existed, no provider call was made, no private view was observed, and no OTP was sent.

The earlier actual human form navigation returned REQUEST_ORIGIN. The versioned public-origin correction and its standards rationale are recorded in the separate review. Raw request headers were never inspected, so the live composite guard's exact failing member remains unobserved. Hosted source consistency and metadata alone do not prove browser request semantics.

A retired context is not revived or extended. Its existing five-minute cookie lifetime must elapse before a fresh independent context is prepared. Do not recover browser cookie values or introduce a reset bypass. The remaining bounded action is one actual human Display click on that fresh unauthenticated page, with no OTP entry or send. An actual diagnostic response showing DENY / RETIRED is required before a new primary-factor ceremony. If it fails, retain the exact closed error and continue safe transport investigation; do not relax Origin or CSRF requirements. No secret page should be read or captured by the executor.

All 657 unique offline regressions passed for the source checkpoint: 323 diagnostic, 134 G3, 159 artifact, 30 historical deployment and 11 fresh isolated package tests. For this evidence-only slice, fresh package validation, secret/private-key scan, unchanged historical baseline, closed client/server imports, deterministic MANIFEST and diff checks are required. Ignored evidence and the three unrelated Route D files are excluded. No production authority, receipt, grant, revocation or dispatch is created by any observation.

```text
D01_PUBLIC_ORIGIN_HOSTED_SOURCE = VERIFIED_EXACT_19_FILES
D01_PUBLIC_ORIGIN_HOSTED_NAVIGATION_GATE = NOT_PROVEN
D01_CONTEXT_RETIREMENT = OBSERVED_SUBSEQUENT_SAFE_GET
D01_PRIMARY_OWNER_IDENTITY = OBSERVED_ACCEPTED_PROTECTED_GUARDS_EARLIER_CONTEXT
D01_TOTP_AUTHENTICATION = NOT_OBSERVED
D01_STATUS = INCOMPLETE_TWO_FACTOR_AND_LIFECYCLE_PENDING
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL_PRIMARY_POSITIVE_OBSERVED
D03_STATUS = CONDITIONAL_D01_ENTRANCE_NOT_SATISFIED
N01_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
N02_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
NAVIGATION_PROBE_PROVIDER_CALLS = 0
CUMULATIVE_PROVIDER_EXCHANGES = UNKNOWN
SECRET_VALUE_ACCESS_BY_EXECUTOR = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
HUMAN_ACTION_REQUIRED = FRESH_UNAUTHENTICATED_DISPLAY_CLICK
```
