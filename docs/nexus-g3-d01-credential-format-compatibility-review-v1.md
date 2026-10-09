# Nexus G3 D01 credential format compatibility review v1

Date: 2026-10-10. Source checkpoint: `79042b2b4e03907e4244bc9e866a37dad838a686`. Additive diagnostic-only compatibility correction. Historical runtime and all v1/D05 canonical bodies remain unchanged.

## Evidence and scope

The exact protocol-status artifact was staged and promoted as `dpl_GPVJZ5VuPUhHtBbERFiN98B8xBGY`. All 19 source UIDs, three public assets, Production metadata and stable domain matched the reviewed artifact (`ab9123f949cdd24f8b32fe67451fbd2d664dda76d78b543eb9832e0dedf96774`). Exactly one browser email-send action returned DENY / AUTH_REJECTED with a null context. This class can arise only from HTTP 401/403 in the fixed native response parser. It proves one failed native exchange, not successful credential validation, email delivery or principal authentication. No retry occurred. The earlier readiness-profile send remains UNKNOWN 0..1 exchanges; the two sends together therefore have a total range of 1..2, not a fabricated exact count.

The [official Consumer email-send reference](https://stytch.com/docs/api-reference/consumer/api/otp/via-email/send) documents the Test endpoint and Basic authentication using project ID and secret. The existing host, route, POST method, Basic encoding and bounded five-minute email request match that reference. The retained response is only a closed failure category; the particular provider error type/message and whether the status was 401 or 403 were not retained or inferred.

The [official Stytch SDK documentation](https://stytch.com/docs/api-reference/b2b/api/sessions/authenticate-jwt) includes Test secret examples with trailing `=` padding. This establishes a concrete incompatibility in the local unpadded-only grammar for that documented key representation. That reference is a B2B example; it does not prove the actual Consumer-project secret representation or that padding caused this run's rejection. It justifies a minimal opaque Test-key grammar correction, without any identity-model or authority-contract change. No sample credential is copied into source or used. No actual Owner secret is read, normalized, hashed, guessed or tested by the executor.

## Versioned correction

`LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT` has revision `g3-d01-owner-live-credential-format-v2`. It preserves the reviewed generation 2 project/native Owner registration, public keyset, exact absolute review window, factors, session/context limits, Test-only host/paths, TLS verification, closed status-only failure projection and mandatory retirement.

The generated credential guard accepts the existing Test prefix and bounded URL-safe body plus zero to two trailing padding characters. Total length remains at most 268 characters, including the 12-character prefix. All whitespace, control characters, embedded padding, excess padding, wrong environment and overlength inputs are denied. Values are passed unchanged to Basic encoding; the adapter never strips or appends padding. JavaScript end-anchor behavior cannot accidentally allow a final newline because whitespace is rejected separately. This is a structural compatibility guard, never proof that a credential is valid or permissioned. The exact-project check still occurs before the single named secret read. No environment enumeration, disk source, fallback, alternate credential, logging or retry is introduced.

The artifact still contains exactly 19 files; four differ from the original historical source: input, pre-secret policy, credential custody and diagnostic service. The previous four profile compositions remain unchanged. The repository's original gates and entrypoint remain false/FAKE_DISABLED. Deterministic artifact SHA256 is `8de2147e6edb1489c4089524f3159159c552d60de8dedba17ed478b49c58ce29`.

Fifteen additional offline tests cover exact inventory, historical grammar preservation, profile substitution denial, unpadded/one-pad/two-pad opaque handling, excess/embedded padding, space/newline/carriage return, wrong environment, short/oversize values and header injection. Synthetic credentials alone enter the harness. Accepted strings are asserted to reach protected Basic construction unchanged, never serialized, and become unusable after custody disposal. No real HTTP request is made.

## Private-input boundary

The AUTH_REJECTED context is permanently retired. Do not send again using unchanged provider configuration or guess a correction to the secret. The smallest necessary Owner action is to privately verify/copy the complete current Consumer P_OWNER Test API secret verbatim into the existing nexus-g3-qual Production STYTCH_SECRET variable, retaining any padding present in the official value. Do not generate a new key, change project/Owner registration, expand policy or expose the value in chat. If provider permission or account availability prevents that preparation, stop and classify the actual boundary rather than bypassing it. After Owner confirmation, rebuild the same corrected artifact to ingest the server setting, verify hosted source/stable routing and attempt one fresh diagnostic send. Successful email send alone must not qualify D01 or enable admission.

```text
CREDENTIAL_FORMAT_COMPATIBILITY = DEFINED_VERSIONED_DIAGNOSTIC_CORRECTION
ACTUAL_OWNER_SECRET_REPRESENTATION = UNOBSERVED
ACTUAL_AUTH_REJECTION_CAUSE = UNKNOWN
CREDENTIAL_NORMALIZATION_OR_GUESSING = FORBIDDEN
RAW_CREDENTIAL_VALUES_ACCESSED_BY_EXECUTOR = NO
LATEST_PROVIDER_SEND = DENY_AUTH_REJECTED_HTTP_401_OR_403
LATEST_PROVIDER_EXCHANGES = 1
RUN_PROVIDER_EXCHANGES = UNKNOWN_1_TO_2
EMAIL_DELIVERY_CONFIRMED = NO
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
