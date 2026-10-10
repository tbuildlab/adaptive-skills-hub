# Nexus G3 D01 request-stage hosted evidence v1

Date: 2026-10-10. Reviewed source checkpoint: `3eb5c4d2078a96a18dfa8f1091feae7f574e35ed`. Branch: `nexus-v2-g3-live-qualification`. This additive observation preserves all historical evidence and contracts.

The exact LIVE_DIAGNOSTIC_REQUEST_STAGE artifact was staged once to the existing authorized Vercel project, without modifying provider configuration or environment variables. Deployment `dpl_C5B7bbJo6zGfKdf3pE1TtxisNL8i` was READY. Its 19 source UIDs, three public asset bytes, application generation 3, reviewed source checkpoint, framework Other, Node 24.x and one 30-second function matched. Source/package SHA256 is `9c1ff95de2f2c096baac7abfa3e19d4fdeeab39b62c6cdd3b51defc54513540d`.

The alternate generated deployment origin was rejected with REQUEST_ORIGIN / DENY. Only after that exact-source verification was the deployment promoted. The stable origin https://nexus-g3-qual.vercel.app was then independently verified against the same deployment, source UIDs and public bytes. Its initial diagnostic response was DENY / NONE, authority NONE and admission DISABLED. No credential value, raw response, cookie, CSRF or provider log was retained by hosted verification. GET and metadata verification performed zero Stytch calls.

The retained browser was reloaded only after the failed previous context had ended. The fresh page had a bounded deadline. Exactly one existing Local logout button action then returned DENY / RETIRED with null context deadline. The static reviewed handler establishes that this accepted local action passed origin, page, CSRF and closed-body validation, deleted only that diagnostic page, and performed no provider exchange. This proves continuity for that one request. It does not prove subsequent worker continuity, authenticate any Owner, verify any signed token, establish logout at the external issuer or create an authority receipt.

The preceding OTP submissions still have only DENY / REQUEST evidence; their specific cause and provider exchange count remain UNKNOWN. The diagnostic guard split must not be used to retroactively infer which historical guard failed. No OTP value or private input was inspected. The local client now rejects empty/malformed codes before a request and suppresses concurrent clicks. Those guarantees are offline-tested; no actual private OTP authentication result is yet observed in this version.

After this checkpoint, one new independent page/send attempt may proceed under the unchanged authorization. It must retain its closed result in ignored evidence and stop for private Owner input if send succeeds. No old challenge/context may be revived, no five-minute deadline extended, no automatic send/authentication retry performed and no real admission enabled. A later non-NONE failure is recorded before another recovery decision. The Owner must enter the latest delivered code in the same page; the executor cannot access it.

Evidence directory: ignored `state/g3-d01-autonomous-20261010/request-stage-live-qualification`. It contains stage/promotion records, exact source/public-byte proofs, sanitized continuity JSON and an evidence-only screenshot. Historical source/artifacts are unchanged. The reviewed public-key interval still expires at 2026-10-10 15:35:37 UTC. No registration generation, principal expectation, mailbox binding, secret value or provider account state is changed in this correction.

Offline validation passed 610 unique tests: 323 diagnostic, 134 G3, 112 artifact (including 36 new request-stage tests), 30 historical deployment and 11 isolated package tests. This document's closure reruns the isolated 11 package tests in a fresh explicit-path snapshot, static scans, historical baseline comparison, deterministic MANIFEST and git diff --check; repeated tests are not added to the unique count. Only this document and MANIFEST.json are staged for the evidence checkpoint. Three unrelated Route D documents remain untracked. Git publication remains blocked by previously observed unavailable authenticated Git transport; no successful remote push is claimed.

```text
D01_REQUEST_STAGE_DEPLOYMENT = OBSERVED_EXACT_SOURCE_MATCH
D01_LOCAL_CONTEXT_CONTINUITY = OBSERVED_ACCEPTED_ONE_REQUEST_ZERO_PROVIDER
D01_PRIOR_OTP_AUTHENTICATION = OBSERVED_DENY_REQUEST_CAUSE_UNKNOWN
D01_CURRENT_OTP_AUTHENTICATION = NOT_RUN_PRIVATE_OWNER_INPUT_REQUIRED
D01_STATUS = INCOMPLETE
D03_STATUS = CONDITIONAL_D01_ENTRANCE_NOT_SATISFIED
N01_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
N02_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
D04_STATUS = NOT_REQUIRED_UNDER_DELEGATED_EXECUTOR_MODE_NEVER_PASS
COMPLETE_MEDIATION_STATUS = OFFLINE_MODEL_ONLY_NOT_LIVE_QUALIFIED
EXPIRY_STATUS = OFFLINE_PASS_LIVE_NOT_QUALIFIED
REVOCATION_STATUS = OFFLINE_PASS_LIVE_NOT_RUN
ANTI_REPLAY_STATUS = OFFLINE_PASS_LIVE_NOT_QUALIFIED
GENERATION_BINDING_STATUS = OFFLINE_AND_DEPLOYMENT_PASS_IDENTITY_NOT_QUALIFIED
RUNTIME_MAPPING_STATUS = CONDITIONAL_NO_SIGNED_PROVIDER_TOKEN_OBSERVED
STYTCH_CALLS_DURING_REQUEST_STAGE_CORRECTION = 0_AT_THIS_CAPTURE
CUMULATIVE_PROVIDER_EXCHANGES = UNKNOWN_OWNER_SUBMISSIONS_NOT_RECONSTRUCTED
SECRET_VALUE_ACCESS_BY_EXECUTOR = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
TOTAL_TEST_COUNT = 610_UNIQUE_OFFLINE_PASS
HUMAN_ACTION_REQUIRED = YES_PRIVATE_EMAIL_OTP_ON_NEXT_SUCCESSFUL_SEND
```
