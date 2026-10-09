# Nexus G3 D01 generation 2 public-key review v1

Source checkpoint: `9615dee7749cffcfab25032fa3019a49cf567246`. Branch: `nexus-v2-g3-live-qualification`. Date: 2026-10-10 Asia/Kuala_Lumpur. This additive review supersedes the pending key-review dependency in the delivery-readiness document; it does not rewrite generation 1 history, deploy an artifact or qualify live identity.

## Input and exact comparison

The Owner supplied fresh JSON reported as obtained from the registered P_OWNER official Stytch Test public JWKS endpoint, and expressly authorized review for application generation 2 whether unchanged or rotated. The executor did not retrieve keys or call Stytch. Endpoint origin/provenance is Owner-reported; public-key structure and equality were verified locally. No signed provider token or provider session was observed.

The existing `normalizeReviewedPublicJwks` accepted one RSA 2048-bit RS256 signature key with `key_ops = [verify]`. The normalized key contains exactly `kty`, `kid`, `alg`, `use`, `n`, `e`. No certificate, key operation metadata, request_id, status_code, URL/discovery field, secret or bearer material enters the pin. Private fields are rejected before a review can succeed.

| Core field | Exact generation 1 comparison |
| --- | --- |
| kid | IDENTICAL |
| kty | IDENTICAL |
| alg | IDENTICAL |
| use | IDENTICAL |
| e | IDENTICAL |
| n | IDENTICAL |

Key count is also identical. No key rotation was detected. SHA256 over the normalized `JSON.stringify(keys)` bytes is `5794378f74deee81d960d1860d744a2eed08e6da108789444f04e089efa04dd3`, exactly matching the historical key-material digest. This digest verifies public data only and supplies no authority.

## New review, generations and time

`owner-keyset-generation2.js` stores a fresh immutable six-field public-key literal from this Owner input, rather than silently promoting the old review. Project binding uses the existing exact server-only registration. Review ID is `owner-public-keys-20261010-v2`; source is `OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET`; application generation is 2. The corresponding disabled input uses the reviewed delivery registration and registration_generation 2. Project, Owner and binding generations remain 1. Native IDs and mailbox are not duplicated in this document.

The first processing clock after this confirmation was 2026-10-09 16:35:37 UTC, corresponding to 2026-10-10 00:35:37 Asia/Kuala_Lumpur. The exact chat-arrival timestamp is unavailable and is not fabricated. The pin begins at this observed processing instant and uses a conservative 23-hour window, shorter than the authorized maximum of 24 hours. It expires at 2026-10-10 15:35:37 UTC / 2026-10-10 23:35:37 local. The checks reject use before the start and at or after the exact end. This window is static, non-refreshing, and never extended by startup, credential presence or a successful login. Any later expired review requires fresh explicit public-key review.

The generation 1 pin, its deadline, original deployment input, accepted 19-file artifact and all historical validators remain unchanged. Both directions of cross-generation keyset use deny. The pending-delivery module's earlier PENDING review marker describes its original preparation checkpoint; this separate review closes that dependency without changing historical preparation bytes.

## Disabled assembly and retained gaps

`DISABLED_GENERATION_2_INPUT` is coherent non-secret configuration only. It does not register a current production service. The deployed diagnostic entrypoint does not import it. It stays FAKE_DISABLED; both compile gates remain false. A public pin, registration and configured mailbox cannot enter the credential loader, read environment credential values, create a native request, or produce Nexus authority.

No new deployment artifact is substituted for the historical reviewed package. A separately reviewed generation 2 artifact must still materialize the new input and receive its own exact source/package hash before deployment or any future bounded diagnostic activation. The historical immutable verifier must not be weakened to accept it. This key-review task authorizes no live Stytch test and enables no real admission.

Stytch Principal runtime mapping remains CONDITIONAL: exact real signed issuer/audience/subject, factors, remote session and lifecycle behavior have not been observed. D04 is NOT_REQUIRED_UNDER_DELEGATED_EXECUTOR_MODE, never PASS or VERIFIED. The accepted delegated mode still requires exact scope, expiry, revocation, replay/generation binding, redaction and fail-closed behavior. N01/N02 real authority remains absent.

## Offline verification

Twelve new tests cover six-field equality and digest, normalized envelope omission, coherent generation binding, exact time bounds, cross-generation denial, project and generation mismatches, duplicate/malformed keys, private/discovery fields, hard-disabled credential getters, trapped credential-loader/network paths, Preview/browser selection, and exclusion from the public/deployed import graph. The child proof uses an empty synthetic environment and traps protected credential names; it never copies the actual environment. An initial overly broad trap caught a Node module-loader environment lookup, before any application credential or network operation. The trap was refined to the existing proof's protected-name semantics, with environment enumeration still denied. No existing test guard was changed.

Final relevant suites: 305 diagnostic tests, 134 G3 regression tests, 30 historical deployment-preparation tests, and 11 package/isolation tests: 480 unique tests PASS. The original 19-file artifact verifier and disabled startup proof pass; deterministic MANIFEST, historical source preservation, bounded secret/private-key scan and git diff --check pass. Validation artifacts are retained only under ignored `state/g3-d01-generation2-review-20261010/`. No local commit, remote push, deployment or provider action was performed by this review.

```text
PUBLIC_KEY_CORE_COMPARISON = IDENTICAL_ALL_SIX_FIELDS
KEY_ROTATION_DETECTED = NO
D01_PUBLIC_KEYSET_GENERATION_2_REVIEW = OWNER_REVIEWED_PINNED
D01_PUBLIC_JWKS = PINNED
D01_KEY_PROVENANCE = OWNER_REVIEWED_PUBLIC_SOURCE
D01_JWKS_RUNTIME_SEAM = CONDITIONAL
D01_APPLICATION_GENERATION = 2
D01_REGISTRATION_GENERATION = 2
D01_CURRENT_DEPLOYED_APPLICATION_GENERATION = 1
D01_GENERATION_2_INPUT = VERIFIED_OFFLINE_DISABLED_CONFIGURATION_ONLY
D01_GENERATION_2_DEPLOYMENT_ARTIFACT = NOT_ASSEMBLED
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL
D04_STATUS = NOT_REQUIRED_UNDER_DELEGATED_EXECUTOR_MODE
LIVE_ADAPTER_DEFAULT = FAKE_DISABLED
CODE_REVIEWED_LIVE_ENABLED = false
DEPLOYMENT_REGISTRATION_ENABLED = false
NETWORK_CALLS_PERFORMED = 0
LIVE_STYTCH_CALLS_PERFORMED = 0
STYTCH_CREDENTIAL_ACCESS = NONE
VERCEL_SECRET_ACCESS = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
