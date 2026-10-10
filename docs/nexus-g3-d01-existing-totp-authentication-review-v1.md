# D01 current verified factor code-only authentication review

Source checkpoint: `1dfc00d04d1dae1c761b4f1254588f6766249373`.

Two separately dispatched protected Get User observations established an exact registered native Owner with one verified TOTP, no unverified TOTP and identical project/Owner-bound factor hashes. The fixed metadata endpoint was then removed and independently returned HTTP 404. This does not establish the error type or failing operation of the preceding DENY/UNKNOWN. No healthy factor was deleted and no User was deleted.

The existing accepted transport and offline integration suite already authenticate a current native Owner TOTP after a fresh Email OTP without TOTP_CREATE. The [official Authenticate TOTP API](https://stytch.com/docs/api-reference/consumer/api/totp/authenticate) accepts the native user, current dynamic code and existing session. This UI exposes that existing operation; it does not re-enroll, recover or reuse an expired enrollment/context. The original exposed factor remains deleted. The subsequently created factor is verified point-time; only a new dynamic code and a newly authenticated session can establish fresh authentication.

## Bounded source change

Only three runtime files differ from the prior reviewed QR-result artifact: fixed deployment revision, public index and public app. Every server authentication, signature, issuer/audience/subject, fixed native Owner, generation, session lineage, pre/post remote recheck, CSRF, request origin and absolute five-minute deadline check is byte-preserved. No accepted contract body changes. Default artifact profile is DISABLED_EXISTING_TOTP; live profile is separately gated diagnostic-only, authority NONE and admission DISABLED. A client UI cannot enable a disabled service.

The public page has separate Email OTP and current TOTP code inputs, never a seed, recovery code or QR. It removes normal enrollment/display buttons. Client code clears both inputs before submission, on hiding/unload and expiry, suppresses overlapping submissions, rejects local clock rollback and extended/expired response deadlines, and renders a closed sanitized response. Codes occur only in the transient same-origin authentication request; they are never retained as evidence or printed. Browser interaction remains human-only. This does not create durable Owner authority, N01, N02 or a production admission path.

No application or registration generation changes: this is a UI/deployment revision, not a reviewed principal/project/key/factor-policy registration change. The original public review interval is unchanged and must still be valid at runtime. Current native factor metadata is not a grant, principal enrollment source or authority record.

Live candidate artifact: 20 files; SHA256 `78b46dd9e27929f8f21ab8974d9a7778636fd55d497487079fca7afb3540566c`. Staged verification matched all 20 actual source UIDs and all four public assets. The unaliased hostname denied REQUEST_ORIGIN. The same deployment `dpl_DVsaJnFFdFjD6Xg3H3HSXUDBShoK` was promoted to the stable domain; independent stable verification again matched source UIDs/public assets and returned diagnostic DENY/NONE, authority NONE and admission DISABLED without provider calls. Two initial CLI invocations failed before build because only project routing metadata was supplied; obtaining the fixed project non-secret account ID resolved the CLI routing prerequisite. No environment variable, provider setting or protection configuration was changed. No real TOTP authentication or D01 closure is asserted before its successful sanitized result and subsequent lifecycle qualification.

## Offline validation

30 new tests cover code-only input selection/clearing, primary-session dependency, repeated authentication, no enrollment call, stale/extended deadline, clock rollback, wrong origin, duplicate UI submission, authority/admission/mode tampering, malformed/free-text/network responses and exact source delta. Full results: 366 Node diagnostic tests, 134 G3 Python regressions, 325 artifact tests (including 30 new tests), 30 historical deployment tests and 11 isolated package tests passed: 866 unique offline tests. One initial new rollback test exposed uninitialized client time high-water; initialization was corrected and the full suite passed without weakening any guard. Test commands were `node --test diagnostics/g3-d01-rp/tests/*.test.js`, `python -B -m unittest discover -s tests -p test_g3*.py`, `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_*artifact.py`, `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_deployment_prep.py`, and `python -B -m unittest tests.test_ecosystem_isolation_package` in a fresh accepted-file snapshot. Bounded secret/private-field scan, artifact verifier, client/server boundary, baseline preservation, deterministic MANIFEST (482 entries) and `git diff --check` passed. No test makes a real provider call. All historical tracked bytes except MANIFEST are preserved.

```text
CURRENT_FACTOR_METADATA = ONE_VERIFIED_ZERO_UNVERIFIED
CURRENT_FACTOR_AUTHENTICATION = NOT_YET_LIVE_QUALIFIED
NEW_ENROLLMENT_CREATED = NO
FACTOR_MUTATION_BY_THIS_SLICE = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
D01 = NOT_QUALIFIED
D04 = UNQUALIFIED
```
