# D01 Pre-context MFA Transition Amendment v1

Status: Owner-accepted, bounded diagnostic implementation amendment; not D01 PASS. Source checkpoint: `a56cd306f476b3755d30ee9aebcbe4d1f3480706`, branch `nexus-v2-g3-live-qualification`. The Owner explicitly accepted this exception on 2026-10-10 after the recorded TOTP reply continuity denial. Historical documents and canonical v1/D05 bodies remain unchanged.

## Scope and authority

The initial Email OTP session may transition once at TOTP completion, before establishment of an OwnerContext. This does not permit replacement of an established context's session, Principal, native User, generations, or binding. The diagnostic page and its initial factor bootstrap are not a production OwnerContext. This slice creates no production OwnerContext, receipt, grant, admission intent or dispatch authority.

The fixed registered Stytch TEST project and native Owner User are authoritative enrollment inputs. Email remains delivery-only. Display names and external IDs are ignored. The existing pinned RS256 signature checks require the exact registered issuer, audience and native subject; direct authenticated remote responses additionally require the exact active, unlocked User/project and fresh factors. A token signature alone is never a positive remote lifecycle check.

## Candidate protocol

1. Authenticate Email OTP using the fixed server-retained method. Require its response method and factor `email_factor.email_id` to match. Freeze the exact primary factor authentication time and its native factor reference privately. The original page/ceremony deadline is not extended.
2. Immediately before TOTP authentication, authenticate the retained primary session remotely. Existing exact session/token/User/expiry/time checks apply. The OTP factor reference and lossless time must still match. Require one unambiguous verified TOTP on the exact Owner User. This bounded implementation supports the already verified Owner TOTP; a missing, unverified or ambiguous enrollment denies. It does not recreate or reuse retired setup material.
3. Send exactly one fixed TOTP authentication request with the primary session token, fixed native Owner User and human-entered current code. No browser-selected session or identity is accepted.
4. Treat the direct response as a pending candidate. Require valid pinned signature, exact project/native Owner/Principal, fresh exact OTP+TOTP factor set, original OTP factor identity/time, exact expected TOTP identity and verified ownership. Do not aggregate independent sessions' factors. Missing primary lineage denies, even if the replacement otherwise looks valid.
5. Directly authenticate the candidate opaque token without a duration/refresh request. Require exact candidate session/User/token, expiry, both factor references and lossless times. Recheck local deadline, current generations, registration, key review window and monotonic time before and after remote validation.
6. Only after all checks succeed, bind the final session under the existing private busy-operation guard. Contract the original deadline with final expiry/factor freshness; never extend it. Clear primary runtime token/lineage references by replacing them with the final private binding. No second TOTP ceremony is allowed in that context.
7. Every later recheck retains the existing strict session/token/native User/Principal/generation checks and additionally validates frozen native factor references and lossless times. Replacement/mismatch denies and retires. Revocation targets only the final bound disposable diagnostic session. Result evidence cannot refresh or retry an authority operation.

Timestamp lineage comparison normalizes UTC fractional seconds to nine digits, preserving provider precision and permitting equivalent zero padding. Freshness/expiry calculations retain the existing conservative millisecond floor. No deadline, generation or public-key review is reset. Native references and bearer values remain private runtime state; evidence emits only closed classifications. No raw provider response, token, OTP/TOTP, seed, recovery code or authentication header is logged or persisted.

The direct provider interface documents native factor references and Session/User metadata: [Stytch TOTP authentication](https://stytch.com/docs/api-reference/consumer/api/totp/authenticate) and [remote session authentication](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-session). Those schemas support candidate validation; they do not prove that this deployment will return the required lineage or explain the previously observed session change. Actual positive behavior remains a live qualification prerequisite.

## Failure and cleanup

Any missing, stale, ambiguous, malformed or mismatched evidence retires the entire local bootstrap/context. Failed remote postcheck cannot install a candidate. Concurrent requests fail closed; no fallback to the old session, silent retry or cross-restart recovery is allowed. The provider may still retain a primary or rejected candidate session until provider expiry: local retirement is not claimed to revoke that external session. Broad User logout is not performed. Exact-session external cleanup requires known retained lineage and a bounded separately specified operation; no cleanup success is inferred from local clearing.

The remote-check-to-local-bind race remains accepted and visible. Remote validation at t0 cannot establish that no logout/revocation occurs at t1 before local use t2. This amendment does not replace subsequent remote rechecks, expiry, revocation, anti-replay, claim-time validation or complete mediation.

## Artifact and qualification

`verify_mfa_transition.py` deterministically extends the accepted v7 artifact. It changes only server transport and deployment revision input, preserving the 20-file inventory, client/service/custody/identity/projection code and public admission boundary. Default profile `DISABLED_MFA_TRANSITION` stays FAKE_DISABLED before credential loading. The explicit live diagnostic profile enables only the existing bounded diagnostic provider operations; it cannot enable Nexus authority. Registration/key review generations and review upper bound remain unchanged.

The added no-network tests exercise same-session success, one initial replacement, precise factor lineage, missing/foreign/ambiguous identity evidence, candidate recheck failures, subsequent replacement, expiry, clock rollback, exact final-session revoke, closed browser input, fixture isolation, unchanged generations/review and disabled defaults. Historical regression guards are not edited. Source hashes, staged deployment file UIDs, public asset hashes and independent stable verification are retained in ignored validation evidence. Deployment follows stage -> verify exact source and wrong-origin denial -> promote the same deployment -> independently verify stable source and initial DENY.

Acceptance and offline tests do not qualify real factors, lifecycle or D01. A fresh human OTP/current-TOTP ceremony and direct remote lifecycle observations are still required. No expired context or prior dynamic code is reused.

Offline validation passed 951 unique tests: 366 Node diagnostic, 134 G3 regressions, 410 artifact tests (including 49 new transition cases), 30 deployment tests and 11 isolated package tests. The 49 new cases were also rerun after correcting a deliberately malformed synthetic token's placeholder naming; this repeat is not added to the total. Commands: `node --test diagnostics/g3-d01-rp/tests/*.test.js`; `python -B -m unittest discover -s tests -p test_g3*.py`; `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_*artifact.py`; `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_deployment_prep.py`; `python -B -m unittest tests.test_ecosystem_isolation_package` in the accepted-file snapshot. Underlying Node tests passed; the local evidence collector's Unicode summary-marker parsing was corrected without changing tests.

The deterministic live-diagnostic ZIP SHA256 is `6d98549bbbccfdf904e8f7e8032cedcd2be01d374bfe567e39cf363523777571`; the default-disabled ZIP SHA256 is `35f61f51d1ada1734c75af9f01560155182248c181b55b2eb2c46518be0e0416`. Both contain exactly 20 reviewed files. Bounded secret/private-key scans, frozen client/server boundaries, all historical tracked-byte comparisons, deterministic MANIFEST (488 entries) and `git diff --check` passed. No credential values were inspected and offline provider/network calls remained zero. Only this amendment, the additive builder/tests and MANIFEST belong to this implementation checkpoint; ignored validation/deployment evidence and unrelated Route D files are excluded. Live qualification/deployment outcomes are separate evidence and cannot be inferred from these offline results.

## Delegated release-gate clarification

The accepted `nexus-g3-delegated-executor-authority-policy-v1.md` remains effective. Historical D04 executor exclusion stays unqualified; no claim of malicious-executor resistance or D04 PASS is made. It is not a release gate in DELEGATED_EXECUTOR mode. Complete mediation is evaluated independently: production frozen target/payload enforcement, durable claim-to-dispatch handoff and provider route qualification are not implemented/qualified. That is a concrete production implementation/evidence gap, not a mechanical BLOCKED_D04 classification. D03 recovery enforcement and production N01/N02 remain separately pending. No other mandatory delegated-mode gate is waived.

```text
PRECONTEXT_MFA_COMPATIBILITY = OWNER_ACCEPTED
INITIAL_SESSION_TRANSITIONS_ALLOWED = 1
TRANSITION_SCOPE = INITIAL_MFA_BEFORE_OWNER_CONTEXT_ONLY
FINAL_SESSION_REMOTE_RECHECK = REQUIRED
PRIMARY_FACTOR_LINEAGE = EXACT_NATIVE_REFERENCE_AND_LOSSLESS_TIME
POST_CONTEXT_SESSION_REPLACEMENT = DENY_AND_RETIRE
ORIGINAL_CONTEXT_DEADLINE = PRESERVED_OR_CONTRACTED
GENERATION_REVIEW_WINDOW_REFRESH = FORBIDDEN
D05_BODY_CHANGED = NO
G3_AUTHORITY_MODE = DELEGATED_EXECUTOR
D04_HISTORICAL_EXCLUSION = UNQUALIFIED_UNCHANGED
D04_RELEASE_GATE = NOT_REQUIRED
COMPLETE_MEDIATION = NOT_IMPLEMENTED_NOT_LIVE_QUALIFIED
D01 = PENDING_FRESH_LIVE_QUALIFICATION
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
