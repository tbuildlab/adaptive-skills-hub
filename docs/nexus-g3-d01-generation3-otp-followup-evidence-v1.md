# Nexus G3 D01 generation 3 OTP follow-up evidence v1

Date: 2026-10-10. Source checkpoint: `ac0f81a6464beb196819961fffbaa72130d178e7`. Additive evidence on `nexus-v2-g3-live-qualification`; runtime, deployment, principal, keyset and canonical contracts remain unchanged.

The Owner reported completing OTP. The existing browser's closed evidence actually showed DENY / REQUEST, authority NONE, real admission DISABLED and a null context deadline. No authentication PASS was observed. At the first current clock read, 2026-10-10 02:54:23 UTC, the previous context deadline of 02:50:07.465 UTC was already past. The actual submission time and exact failure cause are unknown. This does not prove a wrong OTP, provider rejection, session creation, runtime Principal mapping or the precise number of Owner-initiated provider exchanges. No OTP, input value, bearer, cookie, response body or provider log was inspected.

Static inspection confirms REQUEST can represent missing context, CSRF/body validation, missing first-step backend/method or invalid code shape. Native HTTP errors have other closed classifications. The latest visible result does not reconstruct earlier concurrent or repeated Owner submissions, so cumulative provider exchanges are now UNKNOWN rather than extending the earlier bounded count without evidence. Existing in-memory diagnostic state fails closed on expiry/restart/worker loss; none of those causes is uniquely established by this projection.

Standing authorization permits bounded ordinary recovery. A read-only exact Vercel metadata check confirmed deployment dpl_FLKGY7SiEPygJ9YRo7zgjtLJm8Cx and generation 3 source/package SHA256 ca868970d5a55a870c4e3be9d618bc6bfe3eae6a00a51cd988a331568b451c88 unchanged. The exact artifact composition and current public review window were validated locally. No redeployment, registration change, public-key renewal, account mutation or credential-value inspection occurred.

The failed projection and evidence-only screenshot were preserved. A new GET created a distinct bounded diagnostic context. Exactly one new EMAIL_OTP_SEND button action returned PASS / NONE. This establishes one native send exchange performed by this recovery, not authentication or session qualification. The new absolute context deadline is 1791601313703 ms, 2026-10-10 03:01:53.703 UTC / 11:01:53.703 Asia/Kuala_Lumpur. The old context is not revived, extended or used as positive evidence. No authentication submission was retried by the executor.

The next unavoidable human action is private entry of the latest received email OTP in the same existing page and clicking Authenticate OTP before the new deadline. The executor must inspect only the resulting closed evidence, without reading input or transient secrets. A timeout, DENY or unknown result must not become success. TOTP and later G3 phases remain gated on actual observed identity/session prerequisites.

The prior 574-test offline regression checkpoint is retained: 323 diagnostic, 134 G3, 76 artifact, 30 historical deployment and 11 package tests. Current documentary closure checks tracked baseline preservation, bounded secret/private-key scanning, deterministic 437-entry MANIFEST, a fresh isolated 11-test package run and git diff --check. Only this additive document and MANIFEST belong to the local checkpoint. Ignored evidence and the three unrelated untracked Route D documents are excluded. Remote publication remains blocked by the previously observed Git credential unavailability; no new push or login is attempted.

```text
OWNER_REPORTED_OTP_COMPLETION = YES
OBSERVED_OTP_RESULT = DENY_REQUEST
EXACT_SUBMISSION_FAILURE_CAUSE = UNKNOWN
OWNER_INITIATED_PROVIDER_EXCHANGES = UNKNOWN
AUTOMATIC_AUTHENTICATION_RETRY = NO
NEW_CONTEXT_EMAIL_SEND = OBSERVED_PASS_ONE_EXCHANGE
NEW_CONTEXT_EXPIRY_MS = 1791601313703
LIVE_STYTCH_CALLS_PERFORMED_BY_EXECUTOR_THIS_TURN = 1
CUMULATIVE_PROVIDER_EXCHANGES = UNKNOWN_OWNER_SUBMISSIONS_NOT_RECONSTRUCTED
D01_STATUS = INCOMPLETE_WAITING_NEW_PRIVATE_EMAIL_OTP
RUNTIME_MAPPING_STATUS = CONDITIONAL
D03_STATUS = CONDITIONAL_D01_ENTRANCE_NOT_SATISFIED
N01_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
N02_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
STYTCH_SECRET_VALUE_ACCESS_BY_EXECUTOR = NONE
VERCEL_SECRET_VALUE_ACCESS_BY_EXECUTOR = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
HUMAN_ACTION_REQUIRED = YES_PRIVATE_LATEST_EMAIL_OTP
```
