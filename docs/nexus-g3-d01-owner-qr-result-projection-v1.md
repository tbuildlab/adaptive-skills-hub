# D01 Owner QR response projection

Source checkpoint: `a97bb31bf3f35effd4eda3d858c3ee1e1c992c9e`.

After the Owner reported scanning and confirming a fresh QR, the diagnostic landing page returned DENY/RETIRED with no current context. This is not evidence of successful TOTP authentication. The earlier private client discarded the confirmation response and redirected to the root page, whose independent GET could only show current context state. The actual confirmation failure cause is UNKNOWN; no provider logs, raw tokens, QR pixels or secrets were inspected to reconstruct it.

This additive revision preserves the historical v3 builder and source. A separate v4 builder replaces only the deployment revision metadata and private QR client in the deterministic 20-file artifact. It clears private DOM, input and QR buffers before submission, then displays a closed projection of the same-origin diagnostic response. Only fixed diagnostic identifiers, PASS/DENY, bounded error enums, bounded expiry, operation and evidence classification are displayed. CSRF, request IDs, provider free text and arbitrary response fields are excluded. HTTP failure, malformed response, unexpected authority/mode, expired response and extended deadline cannot produce PASS. PASS remains diagnostic evidence with authority NONE and qualified_live false; it does not qualify G3 or authorize admission.

The response is retained on the cleared page instead of being silently discarded. A fixed relative link permits return to diagnostics after evidence observation. No automatic authentication retry, dispatch or admission was added. Cancellation, page hiding, unload and expiry still retire the private view. Unknown outcomes require a fresh human ceremony; an expired or retired enrollment is never reused. Local retirement does not prove provider factor deletion or remote session revocation.

Application, registration and public-keyset generation remain 3. Owner identity, delivery registration, review window, CSRF, primary-authentication requirement, backend session proof and all accepted authority/contracts remain unchanged. Diagnostic mode activation uses the previously accepted bounded live profile; canonical source remains disabled. No credential value is read by the executor. D04 remains unqualified.

The live-profile artifact SHA256 is `7f8ec29c02d27fac9f5e35768a76d7a64f4e9fcaab34b4fc69679bed724e46cc`. The old live QR artifact remains `ac38bd9323c2fb5684a432c90a342a610abb1645e5c35fde5abb97796555b8ec`.

Validation passed 804 distinct offline tests: 366 diagnostic, 134 G3, 263 artifact (including 27 new projection/retirement tests), 30 historical deployment and 11 isolated package tests. Initial new test failures came from the fixture clearing its result before inspecting it; the fixture was corrected to inspect the projection first, then verify duplicate-action and pagehide retirement. Existing guards were not weakened. Secret/private-field scans, client/server boundary, historical byte preservation, deterministic MANIFEST and git diff checks passed.

Deployment `dpl_EWZjXmqFNrWZSivAfAvEr7ymCKNE` was staged without domains. Its actual 20 source UIDs, project, Node 24.x, package metadata and four public resource hashes matched. The unregistered hostname denied REQUEST_ORIGIN. Only then was the same deployment promoted; independent stable-origin verification matched the same deployment and hashes, returning DENY/NONE with authority NONE and admission DISABLED. No Stytch calls were made by deployment verification. Sanitized evidence is retained under ignored `state/g3-d01-autonomous-20261010/owner-qr-result-deployment/`.

```text
OWNER_TOTP_CONFIRMATION_OBSERVATION = DENY_RETIRED
ORIGINAL_CONFIRMATION_FAILURE_CAUSE = UNKNOWN
QR_RESPONSE_PROJECTION = DEFINED
QR_RESULT_STAGED_SOURCE = VERIFIED
QR_RESULT_PRODUCTION_SOURCE = VERIFIED
PRIVATE_MATERIAL_CAPTURED = NO
HISTORICAL_QR_SOURCE_CHANGED = NO
PUBLIC_REVIEW_WINDOW_EXTENDED = NO
APPLICATION_GENERATION = 3
D01_TWO_FACTOR_LIVE_QUALIFICATION = NOT_PROVEN
D04 = UNQUALIFIED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
TOTAL_OFFLINE_TEST_COUNT = 804
```
