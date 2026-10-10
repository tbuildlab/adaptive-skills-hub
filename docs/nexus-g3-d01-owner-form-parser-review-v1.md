# Nexus G3 D01 Owner form parser review v1

Date: 2026-10-10. Starting checkpoint: `5461012d9c49db1b995578d1eb3171c3cfa42f07`. Branch: `nexus-v2-g3-live-qualification`. Additive diagnostic transport correction; historical source, v1/D05 bodies and real admission remain unchanged.

## Observed refusal and reproducible cause

The Owner's authenticated Display navigation reached `/api/diagnostic` and returned DENY / REQUEST, adapter D01_DIAGNOSTIC_LIVE_STYTCH, live diagnostic enabled, authority NONE, admission DISABLED and no context deadline. No private setup view appeared. Only allowlisted response fields were inspected. The request body, headers, cookie, CSRF value, seed and codes were not inspected or retained. The exact live failing member is therefore not directly observed.

The [official Vercel Node helper source](https://github.com/vercel/vercel/blob/main/packages/node/src/serverless-functions/helpers.ts) imports `querystring.parse` and uses it for application/x-www-form-urlencoded bodies. The [Node querystring documentation](https://nodejs.org/api/querystring.html) specifies that parsed objects do not inherit Object.prototype. The frozen handler's `closed` predicate requires Object.prototype. An authenticated synthetic flow reproduces the old REQUEST refusal using Node's actual querystring parser, after primary authentication and TOTP preparation. This is a confirmed compatibility defect and a documented explanation consistent with the live symptom; it does not establish the deployed helper version or inspect the original live request.

The prior unauthenticated form test stopped at the primary-factor guard before examining body shape. Its successful negative did not qualify authenticated parsing. This gap is now covered without replacing or weakening historical tests.

## Exact correction and unchanged boundaries

`verify_owner_form_parser.py` derives the frozen native Owner Origin artifact and changes exactly three of its 19 deployment files: fixed deployment revision, the diagnostic service's dedicated fixed-form decoder, and three closed error enums. The profile is LIVE_DIAGNOSTIC_OWNER_FORM_PARSER and the revision is g3-d01-owner-live-form-parser-v3. Deterministic source/package SHA256: `3b29223459feea42c05a72afc1970e7c286999b67273bd41f42fd934a7341865`.

The decoder accepts bounded raw form strings or framework-parsed ordinary/null-prototype objects. It requires exactly two own enumerable data properties, action and csrf, both strings, with the exact OWNER_TOTP_DISPLAY action. It copies only these two validated values into a new ordinary object. Duplicate parsed values become arrays and deny; duplicate raw fields, extra/symbol fields, custom prototypes, inherited fields, accessors, non-enumerable fields, non-string values and oversized material deny. It never calls getters, trusts prototype data, accepts arbitrary actions or changes the shared closed canonical-body predicate. REQUEST_FORM_SCHEMA, REQUEST_FORM_SIZE and REQUEST_FORM_CSRF identify only fixed guard classes and disclose no request value.

Exact Host/Origin/site, route/method/content type, cookie/page, CSRF, primary Owner authentication, terminal state, remote session recheck, one-use envelope and the original absolute deadline remain mandatory. The public client, private clearing code, fixed form and global/server/private privacy headers are byte-identical. No raw request logging, HTML parsing by the executor, public diagnostic parser-probe endpoint, secret URL, new credential source or reset bypass is introduced. A failure retires the context; it is never revived.

Application, registration and keyset generation remain 3: identity/application inputs are unchanged and the distinct code revision binds this artifact. The same Owner-reviewed keys and original review interval remain unchanged, ending at 2026-10-10 15:35:37 UTC. No review extension or new trust source occurs. No real authority record or provider effect-release path exists.

## Validation and deployment gate

There are 37 additional offline tests, including actual querystring/null-prototype/plain/string authenticated view acceptance, old-artifact reproduction, one-use replay refusal, duplicate fields, field injection, getters, prototypes, arrays, missing/wrong values, size, Origin/site/content-type/expiry guards, exact inventory/delta, unchanged assets/generations/window and unauthorized Owner rejection. Private test material is synthetic only and cannot be activated as real authority. Positive private rendering requires the full synthetic primary and TOTP creation flow plus a fresh remote observation. Invalid forms add zero provider IO. All network is trapped.

Full expected unique regression count: 694 = 323 diagnostic + 134 G3 + 196 artifact + 30 historical deployment + 11 fresh isolated package. Commands: `node --test tests/*.test.js` in the diagnostic directory; `python -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge`; artifact discovery `test_*artifact.py`; historical deployment discovery `test_deployment_prep.py`; fresh isolated `tests.test_ecosystem_isolation_package`; deterministic artifact verification, secret/private-key scan, closed client/server import boundary, unchanged baseline, MANIFEST determinism and `git diff --check`. Actual results are recorded in ignored validation evidence before checkpoint/deployment.

All 694 unique tests passed, including all 37 new tests. G3, artifact and package suites passed in a fresh accepted-source snapshot. The diagnostic and historical handoff suites initially failed there because existing ignored handoff fixtures were absent; both passed unchanged in the actual repository with those fixtures. No test guard was weakened. Static source/secret/private-key checks, historical baseline preservation, deterministic MANIFEST and diff checks passed. Validation did not perform a live Stytch call or inspect a credential value.

Stage only the exact verified artifact in the existing diagnostic Production project, without domain assignment. Verify READY, project, Production tier, Node 24.x, Other framework, checkpoint/profile/generation metadata, all 19 source UIDs, exact public bytes and wrong-host refusal. Promote only that exact verified deployment, then repeat stable-source and no-authority checks. Settings, environment values and credential custody are unchanged; existing platform authentication is used opaquely.

The old context was retired by the REQUEST failure and remains unusable. After the original cookie lifetime elapses, create a fresh independent five-minute context and send the fixed Owner email OTP once. Fresh primary authentication is technically human-only; old successful OTP cannot be copied or restored. Then prepare TOTP once and hand off its private display/enrollment/confirmation. Actual private rendering and two-factor/lifecycle qualification remain pending until observed; offline compatibility is not live D01 closure. D03/N01/N02 entrance remains blocked by incomplete D01.

```text
D01_OWNER_FORM_PARSER_DEFECT = REPRODUCED_OFFLINE
D01_ORIGINAL_LIVE_REQUEST_BODY_INSPECTED = NO
D01_OWNER_FORM_PARSER_FIX = DEFINED_BOUNDED_TRANSPORT_ONLY
D01_OWNER_FORM_PARSER_HOSTED_QUALIFICATION = PENDING
D01_STATUS = INCOMPLETE_TWO_FACTOR_AND_LIFECYCLE_PENDING
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL_PRIMARY_POSITIVE_OBSERVED
OFFLINE_TEST_COUNT_EXPECTED = 694
SECRET_VALUE_ACCESS_BY_EXECUTOR = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
