# Nexus G3 D01 generation 3 deployment and send evidence v1

Date: 2026-10-10. Source checkpoint: `4f7f619a571081210da5a45fdc8308b08250eb13`. Branch: `nexus-v2-g3-live-qualification`. Additive observed evidence; canonical contracts, historical runtime and public-key windows remain unchanged.

The Owner standing autonomy override closed the same-public-key generation 3 rebind prerequisite without renewal or a new trust source. Exact native Owner/project expectations remain fixed. Delivery is configuration only. The retained pin expires at 2026-10-10 15:35:37 UTC / 23:35:37 Asia/Kuala_Lumpur.

Offline closure passed 574 unique tests: 323 diagnostic, 134 G3, 76 artifact, 30 historical deployment and 11 isolated package tests. Bounded secret/private-key scans, exact historical baseline preservation, client/server boundary, deterministic MANIFEST and git diff --check passed. No existing test guard was weakened.

An initial deployment command failed before CLI startup because npx --no-install could not resolve Vercel CLI. The same failure occurred in the old deployment directory and on a read-only CLI check. The official previously used CLI version 63.1.0 was restored via its fixed npm package. No provider credentials were inspected or output. A read-only deployment metadata check then confirmed the unchanged previous generation 2 artifact. The initial failed command has separate retained evidence; it is not counted as a created deployment.

Two exact 19-file generation 3 artifacts were staged to the existing authorized Vercel project. The disabled deployment `dpl_3UhT8GvpDPVY1EPXaVyLXHasYqoc` matched source/package SHA256 `a04b4957d9e4d043c811970257e27422f5e04d096b2a7dd0178b9ba976192be8`. Its 19 source UIDs and three public asset bytes matched; mode was FAKE_DISABLED, authority NONE, result DENY. The alternate staged origin was rejected.

The live diagnostic deployment `dpl_FLKGY7SiEPygJ9YRo7zgjtLJm8Cx` matched source/package SHA256 `ca868970d5a55a870c4e3be9d618bc6bfe3eae6a00a51cd988a331568b451c88`. Before promotion its 19 source UIDs, three public assets, exact project/generation/checkpoint metadata, Node 24.x and single 30-second function matched. The alternate origin returned REQUEST/DENY. Only this verified deployment was promoted. Stable origin https://nexus-g3-qual.vercel.app was independently rechecked against the same source and public bytes; its initial diagnostic projection remained DENY/NONE with no authority or real admission.

A fresh existing-browser diagnostic context was obtained. Exactly one registered email-send button action was performed. The closed evidence projection returned PASS/NONE. Static request-path inspection plus the observed successful result establishes one native Stytch EMAIL_OTP_SEND exchange for this attempt; no retry was performed. The generic UI source label DIRECT_REMOTE_SESSION_OBSERVATION is not session evidence at this stage: EMAIL_OTP_SEND creates no authenticated session. No signed issuer/audience/subject, OTP authentication, TOTP, session lifecycle or revocation has been observed in this attempt.

The exact next boundary is private Owner email OTP entry in the existing page and clicking Authenticate OTP. The executor does not read inputs, mailbox content, OTP, cookies, bearer material or raw provider responses. The existing context remains non-refreshable and expires at the displayed absolute deadline; late input must deny. Sending succeeded, but Owner receipt/delivery and authentication are not yet proven. Do not automatically resend or revive the context. On Owner completion resume the same safe evidence projection and preserve all exact principal/factor/session checks.

A normal non-force push of the active G3 branch was attempted with interaction disabled. Git returned credential-access-unavailable; no remote success is claimed. The local checkpoint is retained. This independent publication task does not justify provider login, reading credentials, changing Git history or blocking the available D01 flow. The three unrelated Route D documents remain untracked and unstaged.

Evidence is retained under ignored state/g3-d01-autonomous-20261010/generation3-live-qualification, including source/deployment hashes, source-UID and public-byte proofs, closed send JSON and an evidence-only screenshot. No transient secrets or raw provider body is retained. Documentary closure regenerates MANIFEST in a fresh explicit-path isolated snapshot and reruns its 11 package tests; the 574 unique offline tests remain the current regression count.

```text
D01_GENERATION_3_DEPLOYMENT = OBSERVED_EXACT_SOURCE_MATCH
D01_EMAIL_OTP_SEND = OBSERVED_PASS_ONE_EXCHANGE
EMAIL_OTP_AUTHENTICATE = NOT_RUN_OWNER_PRIVATE_INPUT_REQUIRED
TOTP = NOT_RUN
SESSION_AUTHENTICATE = NOT_RUN
SESSION_REVOKE = NOT_RUN
RUNTIME_MAPPING_STATUS = CONDITIONAL_NO_SIGNED_PROVIDER_TOKEN_OBSERVED
LIVE_STYTCH_CALLS_ADDED_THIS_TURN = 1
CUMULATIVE_PROVIDER_EXCHANGES = UNKNOWN_EXACT_TOTAL_BOUNDED_3_TO_4
DEPLOYMENTS_CREATED_THIS_TURN = 2
STYTCH_SECRET_VALUE_ACCESS_BY_EXECUTOR = NONE
VERCEL_SECRET_VALUE_ACCESS_BY_EXECUTOR = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
D01_STATUS = INCOMPLETE_WAITING_PRIVATE_OWNER_EMAIL_OTP
D03_STATUS = CONDITIONAL_D01_ENTRANCE_NOT_SATISFIED
N01_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
N02_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
D04_STATUS = NOT_REQUIRED_UNDER_DELEGATED_EXECUTOR_MODE_NEVER_PASS
COMPLETE_MEDIATION_STATUS = OFFLINE_MODEL_ONLY_NOT_LIVE_QUALIFIED
EXPIRY_STATUS = OFFLINE_PASS_LIVE_NOT_QUALIFIED
REVOCATION_STATUS = OFFLINE_PASS_LIVE_NOT_RUN
ANTI_REPLAY_STATUS = OFFLINE_PASS_LIVE_NOT_QUALIFIED
GENERATION_BINDING_STATUS = OFFLINE_AND_DEPLOYMENT_PASS_IDENTITY_NOT_QUALIFIED
TOTAL_TEST_COUNT = 574
REMOTE_STATUS = PUSH_BLOCKED_CREDENTIAL_ACCESS_UNAVAILABLE
HUMAN_ACTION_REQUIRED = YES_PRIVATE_EMAIL_OTP
```
