# Nexus G3 D01 native Owner navigation qualification v1

Date: 2026-10-10. Evidence starting checkpoint: `ad39b7ee03b955979d1a41a75d3301121698fbe3`. Branch: `nexus-v2-g3-live-qualification`. This additive result resolves the specific independent unauthenticated navigation gate; it does not certify D01, two-factor authentication or authority.

The Owner manually clicked Display transient Owner channel on the fresh public-origin artifact. The browser's actual URL became `https://nexus-g3-qual.vercel.app/api/diagnostic`, with a JSON response and no private owner-transient page. The allowlisted response was diagnostic NEXUS_G3_D01_DIAGNOSTIC_ONLY, authority NONE, real_admission DISABLED, qualified_live false, result DENY, error_class RETIRED, evidence_source FAKE_DISABLED, context_expires_at null. No raw headers, cookies, CSRF value, provider body, OTP or authenticator material was inspected or retained.

Unlike the earlier REQUEST_ORIGIN response and subsequent GET-only retirement observation, this actual manually navigated POST response satisfies the accepted DENY / RETIRED negative gate. It proves the unauthenticated protected view refuses release and the fixed form can navigate to a diagnostic response under the reviewed public-page policy. No authenticated backend existed, so the probe made zero Stytch calls and could not display TOTP material. Automation's failure to display a POST response remains a separate control limitation; no retry or HTTP-response success is inferred from its locked button alone.

The deployed artifact remains LIVE_DIAGNOSTIC_NATIVE_OWNER_ORIGIN, deployment `dpl_DXnJxVudUCQeVytf6zkhe18DaNqT`, source checkpoint `3b9f7ea649c7d32e0bdbeb2eb2ed0f6a345399b8`, exact 19 files, source/package SHA256 `4cce45ae9dd5a11e72a9cdb8c36bd9c93b5dfb4ed2e8057b4059b087b623c626`. No deployment, environment variable, source/runtime, provider account or key generation changed during this confirmation. Historical artifacts and v1/D05 contracts remain unchanged. Application/registration/keyset generation 3 and the original public review interval remain mandatory.

The probe's initial context deadline was 1791605001707 (2026-10-10 04:03:21.707 UTC / 12:03:21.707 Asia/Kuala_Lumpur). Retirement never revives or extends it. The retained five-minute cookie must expire naturally before preparing a fresh independent primary-factor ceremony. After that expiry, one new registered-email send may run under standing delegated authorization; never reuse an old OTP, primary session, pending enrollment or private envelope. The new context remains non-refreshable with at most five minutes, and the Owner alone supplies the latest OTP privately. D01 two-factor, remote lifecycle/negative matrix and subsequent D03/N01/N02 entrance gates remain incomplete.

The source checkpoint previously passed 657 unique offline tests. For this evidence-only slice, rerun the fresh 11-test package suite, bounded secret/private-key scan, exact historical baseline and client/server source closure, deterministic MANIFEST and git diff validation. No implementation or test guard is changed. Stage only this document and MANIFEST; ignore validation evidence and unrelated Route D files.

```text
D01_PUBLIC_ORIGIN_HOSTED_NAVIGATION_GATE = PASS_UNAUTHENTICATED_MANUAL_POST_NEGATIVE
D01_PRIVATE_OWNER_CHANNEL = AUTHENTICATED_DISPLAY_NOT_YET_QUALIFIED
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
NEXT_BOUNDARY = PRIVATE_OWNER_EMAIL_OTP_AFTER_FRESH_SEND
```
