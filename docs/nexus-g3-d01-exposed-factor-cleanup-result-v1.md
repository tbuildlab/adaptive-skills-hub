# D01 exact exposed factor cleanup result

Source checkpoint: `650df2d9caecb1cb1cec7f55fdea9eab02de7c73`.
The fixed scope was approved by the Owner at checkpoint `87014040f612e3ca43aaa23c4f4e54eae5a97fb9`. This result supplements the pre-execution cleanup review; historical findings are preserved.

## Qualified execution

The separate five-file package SHA256 was `ff93ecddf8f62a678a7b7d801a0ab3f729e4593cb0a50d3587faa1c340e6d55d`. The temporary deployment ID was `dpl_J2jznCLNs1BB7KF2Bcbf4dAPvr4R`. Its exact source UIDs, fixed Vercel project, production runtime, artifact metadata, Owner binding and absolute operation window were independently checked before invoking any Stytch call. No stable domain was assigned to this deployment.

Anonymous GET returned a 302 Vercel authentication redirect. Anonymous POST returned 401 from the platform; the reviewed handler does not generate 401. An initial verifier incorrectly expected a redirect for POST and stopped without invoking cleanup. After inspecting the documented platform protection and confirming the source response statuses, the verifier recognized POST rejection. No protection settings were changed. Authenticated CLI preflight returned DENY/PREFLIGHT_ONLY with zero provider calls and no credential loading.

The single cleanup invocation returned PASS/NONE: fixed Owner User existed with the exact Owner-designated factor before deletion; one DELETE was acknowledged for the same native User; post-delete GET proved the factor absent, User retained and all other TOTP IDs unchanged. A separate VERIFY_ABSENCE invocation performed one additional GET and returned PASS/ALREADY_ABSENT. Total: three GET calls, one DELETE call, no retries. The official route was [Delete User TOTP](https://stytch.com/docs/api-reference/consumer/api/users/delete/delete-user-totp); no User deletion route exists in this artifact.

Only existing protected Production runtime read the configured Stytch credential. Credential values were never accessed by the executor, downloaded, inspected, printed or persisted. No OTP, setup key, recovery code, session bearer material, raw User object, cookies, authorization header or credential value was retained in evidence. Evidence contains only closed results, booleans, counts, non-secret hashes and deployment IDs.

## Retirement and limits

After independent provider verification, only the newly created unaliased maintenance deployment was removed. Authenticated HTTP verification returned 404, proving that exact temporary endpoint no longer runs. Anonymous access can still encounter platform authentication before the missing-deployment response; the authenticated 404 is the retirement evidence. Source/artifact bytes and sanitized evidence remain local. Stable Production remained FAKE_DISABLED throughout cleanup and retirement.

This proves exact factor deletion and preservation of the native User and unrelated TOTP factors. It does not prove global revocation of previously issued sessions, D01 two-factor qualification, D04 executor exclusion, or real admission readiness. No old enrollment, secret or recovery material is reused. A later fresh ceremony must use a fresh context and fresh TOTP enrollment.

```text
EXPOSED_TOTP_FACTOR = DELETED_VERIFIED
OWNER_USER = PRESERVED_VERIFIED
OTHER_TOTP_FACTORS = UNCHANGED_VERIFIED
FACTOR_DELETE_CALLS = 1
OWNER_METADATA_GET_CALLS = 3
TEMPORARY_CLEANUP_ENDPOINT = RETIRED_VERIFIED_HTTP_404
STYTCH_CREDENTIAL_VALUE_ACCESS = NONE
SECRET_SETUP_RECOVERY_MATERIAL_ACCESS = NONE
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
D01 = NOT_YET_QUALIFIED
D04 = UNQUALIFIED
```

The prior 777-test review remains current: this result adds documentary evidence only. Ignored evidence is under `state/g3-d01-autonomous-20261010/factor-cleanup-deployment/` and is not part of the checkpoint package.
