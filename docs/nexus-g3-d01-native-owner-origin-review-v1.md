# Nexus G3 D01 native Owner Origin review v1

Date: 2026-10-10. Source checkpoint: `07ef93906f83935afd080196a117c521c86e1619`. Branch: `nexus-v2-g3-live-qualification`. Additive diagnostic-only correction; no historical source or canonical authority contract changes.

## Newly observed navigation

The Owner manually clicked Display transient Owner channel in the independent unauthenticated context. The actual browser URL became `/api/diagnostic`, with a JSON response and no private Owner page. The closed projection was DENY / REQUEST_ORIGIN, authority NONE, admission DISABLED, no context deadline. This proves actual navigation reached a diagnostic refusal. It does not satisfy the intended DENY / RETIRED gate, identify which composite Origin guard failed, or establish a two-factor session. This probe had no authenticated backend and made zero provider calls. Only allowlisted response fields were retained; no headers, cookies or hidden values were inspected.

The [WHATWG Fetch Standard, append a request Origin header](https://fetch.spec.whatwg.org/#append-a-request-origin-header) specifies that a non-CORS, non-GET/HEAD request under no-referrer serializes Origin as null. The existing public page's no-referrer metadata is therefore incompatible with the server's mandatory exact Origin for ordinary POST navigation. The [Referrer Policy standard](https://w3c.github.io/webappsec-referrer-policy/#referrer-policy-strict-origin) defines strict-origin as origin-only disclosure and suppresses HTTPS-to-HTTP downgrade disclosure. This is a standards-backed explanation of the observed refusal, not a claim that raw live headers were read. Scripted CORS-mode fetch and ordinary form navigation have different Origin semantics; prior mocked forms did not verify browser header generation.

## Exact bounded correction

The new versioned builder `verify_owner_origin.py` derives the frozen native-form artifact. It changes exactly two deployment files: the fixed code revision in server registration and the public index's referrer metadata from no-referrer to strict-origin. Profile LIVE_DIAGNOSTIC_NATIVE_OWNER_ORIGIN; revision g3-d01-owner-live-native-origin-v3. The deterministic 19-file source/package SHA256 is `4cce45ae9dd5a11e72a9cdb8c36bd9c93b5dfb4ed2e8057b4059b087b623c626`.

The public root page can disclose only its origin, never URL path/query, under this policy. Global Vercel no-referrer headers, server response no-referrer, private Owner HTML and one-use clearing logic remain byte-identical. HTML referrer metadata updates the public document policy; hosted behavior still requires qualification. The fixed same-origin POST, form-action self, exact host/Origin, site exclusion, current cookie/page, CSRF, primary authentication, remote recheck, one-use envelope and absolute expiry gates remain unchanged. Null, absent or wrong Origin is not accepted. No Referer fallback, Origin rewriting, CSRF bypass, arbitrary URL or browser bearer storage is added.

Application/registration/keyset generation remains 3 because registered identity/application inputs are unchanged. The distinct code revision binds this artifact. The exact reviewed public keys and original review interval remain unchanged, expiring at 2026-10-10 15:35:37 UTC. No provider account, environment-variable setting, credential source, authority endpoint or effect-release path is introduced. The public real-admission entrypoint remains fail closed.

## Gates and validation

The 18 new offline tests cover exact two-file delta, historical hash preservation, exact public policy, retained private/global no-referrer, unchanged interval, deterministic packaging, registered identity rejection, unsafe policy/GET/external route rejection, Origin bypass rejection, and null/missing/same-site/valid-but-unauthenticated form refusal with zero provider IO. They do not simulate a browser's header generation or certify hosted navigation. Existing tests are unchanged.

Full regression commands: `node --test tests/*.test.js` from the diagnostic directory; `python -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge`; artifact discovery with `test_*artifact.py`; historical deployment discovery with `test_deployment_prep.py`; fresh isolated `tests.test_ecosystem_isolation_package`; deterministic builder; static secret/private-key scan; client/server closure; historical baseline preservation; MANIFEST verification; `git diff --check`. Expected unique count is 657: 323 + 134 + 159 + 30 + 11. All must pass before checkpoint and deployment.

Stage this exact diagnostic artifact only, verify all 19 source UIDs and three public assets, and promote only the verified version. Then repeat the independent unauthenticated navigation negative. A real DENY / RETIRED response is required before any new OTP send. If automation cannot navigate but actual human navigation does, hand off only that exact zero-provider interaction; never substitute a generic DENY or a locked button for the gate. After it passes, a fresh bounded OTP ceremony may resume. No old context may be extended or revived. D01 full qualification, D03/N01/N02 entrance and all release gates remain incomplete.

```text
D01_NATIVE_OWNER_FORM_NAVIGATION = OBSERVED_MANUAL
D01_NATIVE_OWNER_FORM_RESULT = DENY_REQUEST_ORIGIN
D01_PUBLIC_ORIGIN_POLICY_DESIGN = DEFINED_BOUNDED_CANDIDATE
D01_PUBLIC_ORIGIN_HOSTED_QUALIFICATION = PENDING
D01_STATUS = INCOMPLETE_TWO_FACTOR_AND_LIFECYCLE_PENDING
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL_PRIMARY_POSITIVE_OBSERVED
OFFLINE_TEST_COUNT_EXPECTED = 657
NEW_NAVIGATION_PROBE_PROVIDER_CALLS = 0
CUMULATIVE_PROVIDER_EXCHANGES = UNKNOWN
SECRET_VALUE_ACCESS_BY_EXECUTOR = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
