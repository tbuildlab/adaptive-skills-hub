# Nexus G3 D01 generation 3 authorized rebind v1

Date: 2026-10-10. Source checkpoint: `0dcd9b204e8f48966b9566ef542a5caceac42149`. Branch: `nexus-v2-g3-live-qualification`. This additive closure supersedes the generation 3 public-key confirmation dependency; it preserves historical documents, inputs and artifact hashes.

## Authorization and exact binding

The Owner's NEXUS G3 AUTONOMY OVERRIDE explicitly authorizes application generation transitions for accepted bounded registration changes and same-keyset rebinding within the existing valid review window. This is the required explicit review compatibility; no further restatement by the Owner is needed. It does not authorize renewal, discovery or accepting changed keys.

`owner-keyset-generation3.js` binds the existing immutable six-field key array to the separately prepared generation 3 delivery registration. The source remains OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET, project binding is unchanged, and review reference is `owner-public-keys-standing-rebind-20261010-v3`. Every kid/kty/alg/use/e/n field is unchanged. The normalized public key-material SHA256 remains `5794378f74deee81d960d1860d744a2eed08e6da108789444f04e089efa04dd3`. No endpoint is fetched and no new provider provenance is inferred.

The original absolute review interval remains 2026-10-09 16:35:37 UTC to the exclusive end 2026-10-10 15:35:37 UTC / 23:35:37 Asia/Kuala_Lumpur. The first processing clock for this standing authorization was 2026-10-10 02:30:19 UTC; it was within that interval. This timestamp does not reset freshness. The builder and runtime reject expired or future-invalid pins, and retain exact project/application generation checks. Application, registration and keyset generations are all 3; project/Owner/binding generations remain 1. Fixed native Owner identity, issuer/audience expectation, factors, 15-minute session and 300000-ms context limits remain unchanged. The new email is delivery configuration only; its exact value is not duplicated here or exposed in client assets.

## Exact artifacts and checks

`verify_generation3.py` is an additive exact-input builder. It reuses the historical 19-file inventory, scanners, deterministic ZIP encoder and accepted readiness/protocol-status/credential-format transformations. It accepts only the closed reviewed generation 3 export and two fixed profiles. It never accepts executor-selected registration, arbitrary public input, provider routes or production authority profiles. Historical generation 2 builders and tests remain unchanged and reject generation 3 input.

| Profile | Exact 19-file deterministic ZIP/source hash |
| --- | --- |
| DISABLED | `a04b4957d9e4d043c811970257e27422f5e04d096b2a7dd0178b9ba976192be8` |
| LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT | `ca868970d5a55a870c4e3be9d618bc6bfe3eae6a00a51cd988a331568b451c88` |

The disabled profile changes only the serialized server registration/public-pin input. The bounded live diagnostic profile additionally changes only the two diagnostic compile gates, existing closed credential-readiness/format guard, and closed failure projection after mandatory retirement. It never creates Nexus authority or enables admission. The original repository runtime gates stay false. Both generated profiles contain exactly the original runtime file set; public files contain no mailbox/native IDs/server pin provenance. Credentials are absent from source. The protected runtime may use exactly named Production variables opaquely only for an authorized diagnostic request. No environment pull or secret-value inspection is permitted.

Eight new Node tests verify identical public bytes/provenance, unchanged review window, coherent generation, cross-generation denial, wrong project/generation/source rejection, disabled credential exclusion, frozen records and entrypoint exclusion. Twenty new Python tests check deterministic inventory, exact transformations, historical rejection, arbitrary input/profile rejection, extra/missing files, generation/key/window/public/TLS/provider mutations and trapped disabled/live-missing-config requests. An initial new disabled-HTTP test incorrectly expected the live service failure response. Static inspection showed the unchanged disabled factory returns the original request-denying shell's HTTP 400/REQUEST; only that new expectation was corrected. No runtime or existing guard was changed to satisfy the test.

Full closure regression passed: 323 diagnostic, 134 G3, 76 artifact, 30 historical deployment and 11 fresh isolated package tests, totaling 574 unique tests. Baseline preservation, deterministic 435-entry MANIFEST, secret/private-key scans, import closure and `git diff --check` passed before deployment. Test/deployment evidence is retained under ignored `state/g3-d01-autonomous-20261010/`; only accepted additive source/tests/documentation and MANIFEST may be staged. Unrelated Route D files remain excluded.

## Bounded next live steps

After offline verification, use the existing authorized Vercel project only. Stage the disabled source without changing the stable domain, verify all 19 uploaded source UIDs, three public asset bytes, fixed Node/function configuration and sanitized diagnostic denial. Then stage the separately reviewed live diagnostic profile, verify the same source closure and staged-origin rejection, promote only that verified deployment and recheck stable-domain source/projection.

Use one fresh diagnostic context for exactly one registered email-send attempt. Never automatically retry an ambiguous or failed provider operation. Inspect only the closed non-secret evidence projection. If delivery succeeds, the Owner must enter the email OTP privately in the existing page; the executor must not read it. Failed contexts are terminal. The exact provider/native-user, factors and signed issuer/audience/subject checks remain mandatory after authentication. Success sending a message does not prove runtime Principal mapping or qualify D01.

```text
GENERATION_3_REBIND_AUTHORIZATION = EXPLICIT_OWNER_STANDING_INSTRUCTION
PUBLIC_KEY_CORE_COMPARISON = IDENTICAL_ALL_SIX_FIELDS
NEW_TRUST_SOURCE_INTRODUCED = NO
PUBLIC_REVIEW_WINDOW_EXTENDED = NO
D01_APPLICATION_GENERATION = 3
D01_REGISTRATION_GENERATION = 3
D01_PUBLIC_KEYSET_GENERATION_3 = AUTHORIZED_PINNED
D01_GENERATION_3_ARTIFACTS = DEFINED_EXACT_19_FILES
HISTORICAL_GENERATION_1_2_SOURCE = UNCHANGED
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL
D01_LIVE_PROVIDER = NOT_QUALIFIED
D04_STATUS = NOT_REQUIRED_UNDER_DELEGATED_EXECUTOR_MODE_NEVER_PASS
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
