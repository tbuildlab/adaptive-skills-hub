# Nexus G3 D01 closed request-stage diagnostic review v1

Date: 2026-10-10. Source checkpoint: `c4c2583605d16ba72b1fc0fe2867070ac6cd266a`. Branch: `nexus-v2-g3-live-qualification`. Additive diagnostic-only correction under standing delegated authorization. Existing v1/D05 bodies, authority gates, accepted generation 1/2/3 builders and historical runtime files remain unchanged.

The Owner reported pressing Authenticate OTP after the fresh send. The retained page again showed DENY / REQUEST with no context deadline, authority NONE and admission DISABLED. This is not authentication success. The submitted value, request body, cookie, CSRF, provider raw response and signed token were not read. Cumulative provider exchanges remain UNKNOWN because Owner submissions cannot be reconstructed from that projection. No additional send/authenticate was retried during investigation.

Static review establishes that REQUEST collapsed several different guards: origin/route, missing page, CSRF, content type, body size/schema, missing/extra code, request order, method state and busy transport. A worker restart with a retained cookie yields RETIRED; a missing cookie can yield REQUEST. These are distinct candidates, not a proven cause of the observed failure. An in-memory page map does not establish cross-worker continuity. No deadline extension, state resurrection, cookie extraction or token relocation is permitted as a repair.

## Bounded additive artifact

`verify_request_stage.py` derives exactly 19 files from the unchanged reviewed generation 3 credential-format artifact. Its fixed profile is LIVE_DIAGNOSTIC_REQUEST_STAGE and revision is g3-d01-owner-live-request-stage-v3. It changes only the fixed input revision, closed error enum, request-guard classification, two transport guard classifications, and client submission guard. The six differing runtime files relative to the original disabled generation 1 source are deployment-input.js, pre-secret-policy.js, credential-custody.js, diagnostic-service.js, stytch-transport.js and public/app.js. Relative to the generation 3 live artifact, five files differ: deployment-input.js, pre-secret-policy.js, diagnostic-service.js, stytch-transport.js and public/app.js. Credential custody bytes remain identical to the accepted generation 3 credential-format artifact.

Source/package SHA256: `9c1ff95de2f2c096baac7abfa3e19d4fdeeab39b62c6cdd3b51defc54513540d`. Previous live generation 3 source/package remains exactly `ca868970d5a55a870c4e3be9d618bc6bfe3eae6a00a51cd988a331568b451c88`. Owner/project/application generation, exact public keys and review interval are unchanged. The review still expires at 2026-10-10 15:35:37 UTC. A code revision alone does not renew a registration or public-key review.

Only fixed REQUEST_* enums are added. They never include a value, identifier, length, digest, submitted code, header, body or provider message. All previous guard predicates and mandatory identified-context retirement remain. Early failures before cookie/key identification cannot retire an unrelated unidentified page; repeating such a malformed request still denies before provider IO. New tests initially asserted otherwise, then were corrected against the unchanged guard order. No historical test or guard was modified.

The client rejects a non-six-digit input locally with DENY / REQUEST_CODE_SHAPE and LOCAL_INPUT_VALIDATION_ONLY. This is never session, identity or authority evidence. Its in-flight guard permits one request, disables controls while that request is pending and ignores concurrent clicks. It does not retry. Server-side shape checks remain mandatory; the browser cannot select registration, mode, provider route or keys. No OTP value is inspected by the executor.

## Qualification order and retained boundary

Before any further email send, deploy the exact versioned diagnostic artifact, verify all 19 source UIDs and all three public asset bytes, then obtain a fresh page and exercise the existing LOCAL_LOGOUT action once. A successful RETIRED result with no provider calls establishes only that this request's page/cookie/CSRF continuity was accepted. It is DENY, authority NONE and admission DISABLED. A fixed failure class identifies the blocked guard without reading secret values. A failed continuity test stops email sends; it cannot be replaced by a weaker cookie or CSRF rule. A successful check does not prove future worker continuity or authenticate the Owner.

Only after that zero-provider check passes may an independent fresh context perform one registered send. Private human OTP input remains required. Old contexts are not restored. No authentication or factor qualification is inferred from send success. If a browser/runtime architecture incompatibility is established, record it before selecting a separately reviewed compatible runtime. No production storage, bearer-client state or authentication bypass is introduced by this diagnostic version.

## Offline validation

The 36 new artifact tests cover precise reject classification; no IO for malformed/foreign/expired/stale requests; full retirement for identified invalid contexts; zero-provider local logout; no restart restoration; no public identities or raw error leakage; missing project/secret fail closed; no expiry extension or retirement removal; and local empty/invalid/double-click behavior. Synthetic IO cannot promote into a real service. All relevant existing tests remain required: 323 diagnostic, 134 G3, 76 historical artifact, 30 historical deployment and 11 isolated package tests. With the 36 new tests this is 610 unique offline tests, without double-counting reruns.

Commands use the established Python runtime and explicit-path fresh package snapshots:

```text
node --test tests/*.test.js
python -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge
python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_*artifact.py
python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_deployment_prep.py
python -B -m unittest tests.test_ecosystem_isolation_package
python -B diagnostics/g3-d01-rp/scripts/verify_request_stage.py --output state/g3-d01-autonomous-20261010/request-stage-artifact
git diff --check
```

Static secret/private-field scan, exact historical baseline preservation, import/client boundary and deterministic MANIFEST must pass before checkpoint/deployment. No credential-bearing local file is read. Artifacts and live evidence remain ignored. Only MANIFEST.json, this document, the new builder and new artifact test are eligible for the source checkpoint; unrelated Route D files remain unstaged. Actual hosted observations belong in a separate additive evidence document after verification.

```text
D01_REQUEST_STAGE_DESIGN = DEFINED_DIAGNOSTIC_ONLY
D01_REPEATED_OTP_AUTHENTICATION = OBSERVED_DENY_REQUEST_CAUSE_UNKNOWN
D01_REQUEST_STAGE_LIVE_QUALIFICATION = PENDING_EXACT_DEPLOYMENT_AND_CONTINUITY_CHECK
D01_STATUS = INCOMPLETE_NO_AUTHENTICATED_OWNER_OBSERVED
APPLICATION_GENERATION = 3_UNCHANGED
KEY_REVIEW_WINDOW = UNCHANGED_NO_RENEWAL
RUNTIME_MAPPING_STATUS = CONDITIONAL
D03_STATUS = CONDITIONAL_D01_ENTRANCE_NOT_SATISFIED
N01_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
N02_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
LIVE_STYTCH_CALLS_BY_OFFLINE_VALIDATION = 0
SECRET_VALUE_ACCESS_BY_EXECUTOR = NONE
```
