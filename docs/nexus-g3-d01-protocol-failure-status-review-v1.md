# Nexus G3 D01 protocol failure status review v1

Date: 2026-10-10. Source checkpoint: `6523136fe6c68c6e44daff3e7de6bdd75d1b4295`. Additive diagnostic-only review under the accepted delegated-executor authorization. This does not change historical runtime files, accepted contracts, identity rules, issuer mapping, custody, TLS, time limits or admission authority.

## Observed failure and limits

After the Owner reported privately correcting the existing Production secret configuration, the unchanged readiness artifact (`05927daf5a5afc718bef392fade66d873856959511c98a4726e34dd3c2a5b527`) was force rebuilt and staged as `dpl_3Az3fMPT38iDzAJqLAGZcJ3KQ2Co`. All 19 deployment source UIDs and three public assets matched; Production metadata and stable routing were verified before one browser email-send action.

The action returned DENY / RETIRED with a null context. No retry occurred. The service replaces any unsuccessful protocol result with RETIRED after deleting the page/backend, hiding the underlying closed failure enum. That observation alone does not prove a valid credential, email delivery, actual provider request, native-user match or successful identity qualification. The request may have failed before or after the sole fixed provider exchange. The number of Stytch exchanges for that action is UNKNOWN, bounded to 0..1 by the reviewed path; do not retain the former run-wide zero-call claim after this ambiguous action. No raw credential, response, cookie, CSRF or OTP was inspected or retained. Earlier zero-call configuration failures remain separate historical evidence.

## Exact additive profile

`LIVE_DIAGNOSTIC_PROTOCOL_STATUS` uses revision `g3-d01-owner-live-protocol-status-v2`, preserving application/registration generation 2, the same key material and absolute review window. It contains exactly 19 source files. Four historical files differ: deployment input, pre-secret policy, credential custody and diagnostic service. The first three use the accepted readiness transformation with the new fixed revision. The fourth changes only the failure response following mandatory retirement: a failed protocol operation preserves its existing error enum through `safeResult`; a nominal PASS whose deadline/page membership failed remains RETIRED. DENY, HTTP 403, authority NONE, real admission DISABLED, null context, null CSRF and irreversible backend retirement are preserved. Unknown enums map to UNKNOWN. No arbitrary provider message or response field is returned.

Deterministic artifact SHA256: `ab9123f949cdd24f8b32fe67451fbd2d664dda76d78b543eb9832e0dedf96774`. The three preceding profiles remain byte-identical to their own accepted compositions. The original repository entrypoint remains FAKE_DISABLED with both compile gates false. The versioned artifact does not add an endpoint, dependency, provider route, authority record, enrollment or positive admission path. It cannot activate fixture authority or refresh a context.

Ten added tests verify the exact four-file inventory, unchanged preceding service compositions, cross-profile rejection, rejection of retirement removal, and end-to-end offline enum retention for AUTH_REJECTED, RATE_LIMITED, PROVIDER_UNAVAILABLE, TIMEOUT, IDENTITY and MALFORMED_RESPONSE. Each failing operation retires the page, rejects a second action, preserves exactly one synthetic IO shape and performs zero real network calls. Evidence must not include synthetic credentials, native IDs, email or provider body text.

## Qualification boundary

Stage only this exact independently validated artifact, verify hosted source UIDs and public assets before promotion, then verify stable routing. Any later send is a bounded new diagnostic revision after resolving the proven observability gap, not an automatic retry of the failed context. Attempt at most one send for the new profile. The fixed enum identifies only a failure category, never a provider error-code detail or credential value. AUTH_REJECTED requires private Owner/provider configuration correction; IDENTITY may indicate an exact native-user mismatch and must never be bypassed by adopting the response user. Other failures require bounded diagnosis without weakening guards. OTP, TOTP, signed identity, session lifecycle and final G3 gates remain unqualified until separately observed.

```text
PROTOCOL_STATUS_PROFILE = DEFINED_DIAGNOSTIC_ONLY
PROTOCOL_FAILURE_PROJECTION = CLOSED_ENUMS_ONLY
FAILED_CONTEXT_RETIREMENT = PRESERVED
AUTOMATIC_SEND_RETRY = NO
PRIOR_READINESS_SEND = DENY_RETIRED_UNDERLYING_CAUSE_UNKNOWN
PRIOR_READINESS_PROVIDER_EXCHANGES = UNKNOWN_0_TO_1
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
