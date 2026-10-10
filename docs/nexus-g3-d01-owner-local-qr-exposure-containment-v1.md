# Nexus G3 D01 local Owner QR and exposure containment v1

Date: 2026-10-10. Starting checkpoint: `d8efff299d71cb349af4c2742510f6712de70a50`. Branch: `nexus-v2-g3-live-qualification`. This additive review does not change historical source, canonical v1/D05 bodies, identity registration, key provenance or the original public-key review interval.

The Owner reported exposure of the current setup/recovery material. No private material was retrieved, captured, logged or retained by the executor during containment. The old five-minute context expired; subsequent requests returned REQUEST_CONTEXT_MISSING. A separately created empty context was explicitly logged out and returned RETIRED with no expiry. The old HTML envelope was already consumed on first display and cannot be redisplayed or rehydrated. These facts establish local retirement, not provider-factor deletion. Actual authenticated private rendering on the preceding parser deployment was observed; two-factor completion was not observed.

## Provider cleanup boundary

The [Stytch Create TOTP contract](https://stytch.com/docs/api/totp-create) documents that an unauthenticated enrollment becomes unusable after its configured expiration window. This transport requests five minutes. However, the exposed enrollment's exact factor reference was destroyed during retirement, and neither its current provider state nor prior authentication is now independently established. Expiry of the local context does not prove revocation of an authenticated provider factor or recovery codes. Fresh creation also does not establish invalidation of previous factors.

The [Delete User TOTP endpoint](https://stytch.com/docs/api/delete-user-totp) requires the exact factor identifier. It is outside the accepted diagnostic transport's six fixed routes. No route was added, no credential was accessed for cleanup, no factor identity was guessed, and no unrelated factor was deleted. Provider cleanup remains UNVERIFIED. This is a genuine contract/access blocker: use the Owner's protected Stytch Test administration to remove the specific exposed factor and confirm cleanup without sharing private material. No new live enrollment or fresh OTP ceremony is initiated before that boundary is resolved.

## Local QR implementation

The versioned `verify_owner_qr.py` builder derives from the accepted parser artifact. Historical 19-file packages remain frozen. The new closed artifact has exactly 20 runtime files: a separate same-origin encoder asset is added, the private renderer/client are changed, the code revision is bound, and the quarantine profile sets both live activation gates false. All Origin, CSRF, request parsing, session checks, expiry, registration generations, signing-key checks, fixed provider routes and security headers retain their accepted bytes.

The local encoder is [Project Nayuki QR Code generator v1.8.0](https://github.com/nayuki/QR-Code-generator/releases/tag/v1.8.0), ES6 release SHA256 `6a1116192ed1dd67fa1bf31e77f5817103d71c23bbac24c382e698b7668bdd01`. The original MIT copyright/license is retained. Exactly five upstream trailing spaces are removed to satisfy diff checks; no executable token changes. Normalized repository vendor SHA256: `5d65f10cbda9bc5f61df20e4dfb716ef3203b19f7daedb6cc7c0ae51193f033f`. The builder additionally appends only the static ESM export. There are no runtime package dependencies, external imports or remote QR calls.

The client constructs the [Google Authenticator key URI format](https://github.com/google/google-authenticator/wiki/Key-Uri-Format) only in private page memory: fixed TOTP type, matching issuer label/parameter, Base32 seed, SHA1, six digits and 30 seconds. The seed is validated against a bounded uppercase Base32 alphabet. Invalid, oversized, unavailable or unrenderable material denies and clears the view. QR error correction is MEDIUM, version range 1–15, with a four-module quiet zone and five pixels per module; the canvas is bounded to 512 pixels. No private URI is placed in an image URL, attribute, browser history, console, log, evidence, clipboard, downloadable image or storage. No provider-supplied QR image is used. Recovery codes are no longer included in private HTML. The temporarily hidden seed node is consumed and removed after local painting.

Cancel, submit, pagehide, beforeunload, hidden-page visibility and expiry clear canvas pixels, input, seed node and private metadata. Secret-bearing references and encoder buffers are cleared on completion where available. JavaScript garbage collection cannot prove physical heap erasure. The one-use server envelope is consumed before the page is returned. Reopening/restoring the old page does not restore an envelope. A best-effort same-origin CSRF-protected CANCEL with keepalive retires the local server context on abandonment; interrupted network delivery is not represented as an acknowledged provider revoke. Independent server expiry remains absolute, non-refreshable, five minutes and non-restorable across workers/restarts. An expired or closed view never starts an automatic replacement enrollment.

The existing private QR itself is sensitive. Live QR screenshots, DOM dumps, barcode decoding, setup-key inspection and recovery-code export are forbidden. The executor may verify only a private-view presence flag and sanitized evidence; the human scans/enters codes directly. The independent decode test uses synthetic data exclusively and adds no deployment dependency.

## Profiles and validation

The default and only currently deployable profile is DISABLED_OWNER_QR_QUARANTINE: mode FAKE_DISABLED, CODE_REVIEWED_LIVE_ENABLED false and DEPLOYMENT_REGISTRATION_ENABLED false. A distinct LIVE_DIAGNOSTIC_OWNER_QR artifact can be prepared structurally, but activation is blocked until exposed-factor cleanup and the remaining live gates are established. Registration/key presence and configured credentials cannot activate the quarantine profile. It reads no credentials and makes no Stytch call. The code revision is `g3-d01-owner-local-qr-v3`; application/registration/keyset generation remains 3, and no public-key review window is extended.

There are 32 additional offline tests: actual encoding/URI parameters, invalid and oversized Base32, canvas/library failure, expiry, origin, CSRF, close/hide/cancel/confirm cleanup, second-action refusal, buffer clearing, authenticated one-use private HTML/replay, exact inventory/import closure, unchanged history/generations/review window and disabled credential/network refusal. A separate jsQR 1.4.0 decoder probe verifies a synthetic QR roundtrip; that decoder lives only in ignored validation state. No real enrollment material is a fixture.

Run unchanged diagnostic, G3, artifact, historical deployment and fresh isolated package regressions; deterministic artifact/source scan; private-key scan; client/server imports; baseline preservation; MANIFEST determinism and git diff --check. Stage the exact quarantine artifact without domain assignment, verify its complete source UIDs and four public assets, then promote the same build and verify stable FAKE_DISABLED / authority NONE / admission DISABLED. No environment/account setting change or provider authentication occurs in these deployment checks. Actual results and hashes are recorded in a separate hosted continuity document after verification.

All 726 unique regressions passed: 323 diagnostic, 134 G3, 228 artifact (including 32 new), 30 historical deployment and 11 fresh isolated package tests. The separate synthetic independent-decoder probe passed. Exact quarantine source/package SHA256: `211191ce2d52591f6b3bab81ea044952852b48f264931dc6cb3ae2341e91ea6b`. Static secret/private-key scans, import closure, historical source preservation, deterministic MANIFEST and diff checks passed. No existing scanner/test guard was weakened. Normalized vendor LF bytes are pinned; only normal Windows CRLF-to-LF source normalization is applied when reading a checkout. Live provider-factor cleanup and human scan remain unverified.

```text
D01_EXPOSED_LOCAL_CONTEXT = RETIRED
D01_EXPOSED_PROVIDER_TOTP_REVOCATION = UNVERIFIED
D01_FRESH_ENROLLMENT = NOT_CREATED_PENDING_PROVIDER_CLEANUP
D01_OWNER_LOCAL_QR = IMPLEMENTED_OFFLINE
D01_QR_GENERATION_LOCATION = CURRENT_PRIVATE_PAGE_ONLY
D01_REMOTE_QR_SERVICE = NONE
D01_RECOVERY_MATERIAL_DISPLAY = REMOVED
D01_LIVE_QR_SCAN = UNVERIFIED
D01_STATUS = BLOCKED_EXPOSED_FACTOR_CLEANUP_AND_TWO_FACTOR_LIFECYCLE
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL_PRIMARY_POSITIVE_OBSERVED
D04_EFFECTIVE_EXCLUSION = UNQUALIFIED
LIVE_ADAPTER_DEFAULT = FAKE_DISABLED
CODE_REVIEWED_LIVE_ENABLED = false
DEPLOYMENT_REGISTRATION_ENABLED = false
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
