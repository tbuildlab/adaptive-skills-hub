# D01 session continuity refusal phase review

Source checkpoint: `63a65251eda14b7737ade438a25d69105209b6bf`.

## Observed result and limits

After the Owner reported completing both current-factor authentication actions, the retained sanitized diagnostic response showed `DENY / IDENTITY_SESSION_CONTINUITY`, null context expiry, authority NONE, admission DISABLED and qualified_live=false. The operation controls were disabled. The failed context is retired and cannot be reused. Only the closed response projection and a screenshot cropped to the evidence panel were retained in ignored validation state; no input values, raw provider response, session identifiers, bearer tokens, cookies, OTP or TOTP values were inspected.

The exact verified source checks native Owner equality, active/unlocked status, exact factor set and freshness, expiry bounds, pinned JWT signature/issuer/audience/subject, and token shape before the continuity predicate. Both the retained session and the projected response must already identify the fixed registered native Owner. Therefore the source-level inference is a different session_id, rather than acceptance of a different native User. Private IDs were not inspected. The displayed class alone does not establish whether the failure occurred during the precheck, the TOTP response or the postcheck. Token continuity and primary authentication time are checked later and remain unproven. This is a failed qualification observation, not proof that every Stytch integration is unsuitable, that the provider ignored an argument, or that a new session can safely be adopted.

The [official TOTP reference](https://stytch.com/docs/api-reference/consumer/api/totp/authenticate) supports an existing session_token and a duration that extends that session on successful authentication. The [official session reference](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-session) supplies direct session authentication. These documented capabilities do not prove continuity in this observed deployment. The fixed wire body already includes the retained session_token and exact native User; local inspection found no omitted token field, browser-selected session, redirect, retry or alternate endpoint. The accepted same-session requirement in the live setup plan and adapter review remains unchanged.

## Bounded diagnostic change

The additive deterministic builder introduces three closed refusal labels: `IDENTITY_SESSION_TOTP_PRECHECK`, `IDENTITY_SESSION_TOTP_REPLY` and `IDENTITY_SESSION_TOTP_POSTCHECK`. Other session-continuity failures keep the existing generic label. Only the existing failing predicate selects a fixed internal phase label. There is no provider-controlled phase, free text, identifier, token hash, raw claim, request identifier or new public evidence field. No claim of live authority follows a successful diagnostic observation.

The boolean continuity expression, evaluation order and refusal behavior remain identical. No mismatching session/token is adopted. Native wire fields, signature/session/factor validators, HTTP/origin/CSRF/cookie controls, credential custody, local deadlines and generation checks remain unchanged. Four runtime files differ from the preceding artifact: deployment revision, closed server/client error-label allowlists, and internal phase attribution at the same predicate. The default artifact is disabled. Application/registration/keyset generation 3 and the original public key review interval are preserved; this revision does not renew identity review or authorize a new trust source. No production Nexus authority module, receipt, grant, intent or claim is introduced.

Synthetic tests cover failure at all three stages, no TOTP call after precheck failure, no postcheck after reply failure, retirement after postcheck failure, unchanged token/time refusal, unchanged fixed wire keys, normal same-lineage success, later generic refusal, disabled-before-custody behavior, fixed client projection, exact source mutation rejection, and unchanged generations/review interval. Fixtures remain OFFLINE/NO AUTHORITY. Network primitives are forbidden in these tests.

## Qualification disposition

Do not repeat a retired ceremony. After the reviewed phase-label build is independently staged, verified and promoted, one fresh human-entered OTP/TOTP ceremony can distinguish the three failure positions. A repeated mismatch must still deny. If actual provider behavior cannot satisfy the accepted same-session contract, D01 remains BLOCKED; any alternative continuity model requires a separately reviewed compatibility amendment. Token adoption, cross-session factor aggregation and JWT-only current-context validation are not authorized by this diagnostic revision.

The live candidate contains 20 files; deterministic package SHA256 is `58ac4a85ee81093f77fb5f4c023a695ba1b08030a3fee8a5ee0f48f225cc3a47`. Offline validation passed: 366 Node diagnostic tests, 134 G3 Python regressions, 361 artifact tests (including 13 new phase tests), 30 historical deployment tests and 11 isolated package tests: 902 unique tests. Commands: `node --test diagnostics/g3-d01-rp/tests/*.test.js`; `python -B -m unittest discover -s tests -p test_g3*.py`; `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_*artifact.py`; `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_deployment_prep.py`; and `python -B -m unittest tests.test_ecosystem_isolation_package` in a fresh accepted-file snapshot. The new 13 tests also passed independently before the full regression. Bounded secret/private-field scan, server/client boundary, preservation of all historical tracked files and `git diff --check` passed. Inverting the exact internal phase-only transformation reproduced the parent transport byte-for-byte. No offline validation made a provider call.

MANIFEST validation remains deterministic at 485 entries and its bytes are unchanged. The pre-existing sensitive-path rule excludes the three new paths containing session; no rename, rule bypass or scanner relaxation was made. The standalone source verifier independently checks the exact runtime inventory. Only the new builder, its tests and this additive review belong to the checkpoint; ignored evidence and the three unrelated Route D documents are excluded. Deployment verification is recorded separately below. A staged build is not a qualification pass. D03 deployed enforcement, D04 effective exclusion, N01/N02 authority and end-to-end real admission remain unqualified.

The exact staged build `dpl_CMjDbhhZddL3qnnHWbPqKZ5vib1m` was READY with the expected project, Production tier, Node 24.x, generation 3 and source metadata. All 20 deployed source UIDs and all four public asset bytes matched the reviewed artifact. The unaliased hostname denied REQUEST_ORIGIN. The same build was then promoted to the stable domain and independently reverified with the same source/asset checks and an authority-NONE, admission-DISABLED preflight. Verification performed zero Stytch calls. Raw CLI output, credentials, headers, cookies and CSRF values were not retained. The prior failed context remains retired. A fresh human-entered ceremony is still required; this build proves diagnostic attribution and deployment bytes, not provider session continuity or D01 closure.

```text
OBSERVED_DIAGNOSTIC_RESULT = DENY_IDENTITY_SESSION_CONTINUITY
FAILED_EXCHANGE_PHASE = UNKNOWN
SESSION_ID_MISMATCH = SOURCE_INFERENCE_NOT_RAW_ID_OBSERVATION
SESSION_CONTINUITY_PREDICATE = UNCHANGED
SESSION_OR_TOKEN_ADOPTION_ALLOWED = NO
D01 = NOT_QUALIFIED
D04 = UNQUALIFIED
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
RAW_CREDENTIAL_ACCESS = NONE
```
