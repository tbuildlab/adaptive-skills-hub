# D01 exposed TOTP factor cleanup

Source checkpoint: `87014040f612e3ca43aaa23c4f4e54eae5a97fb9`.

The Owner authorized deletion of exactly `EXPOSED_FACTOR_OWNER_REPORTED`, supplied its non-secret native TOTP ID, and expressly prohibited deleting the User. Exact IDs exist only in the closed server-side reviewed scope. No setup key, recovery code, OTP, bearer token or credential value is an input to this operation.

The official Consumer [Delete User TOTP](https://stytch.com/docs/api-reference/consumer/api/users/delete/delete-user-totp) operation is `DELETE /v1/users/totps/{totp_id}`. [Get User](https://stytch.com/docs/api-reference/consumer/api/users/get-user) supplies native User and factor metadata. Before deletion, the fixed registered Owner must exist and contain this exact factor. After one DELETE, one independent GET must prove the same User survives, the exact factor is absent and unrelated TOTP IDs are unchanged. Unknown acknowledgments never trigger another DELETE. No deletion of a User, session or other factor is implemented. Factor absence does not prove existing sessions were revoked.

## Execution boundary

This is a separate, five-file, fixed administrative maintenance artifact. It is not imported into the diagnostic service, N01, N02 or real admission. Default assembly is disabled. An explicitly enabled artifact has a maximum 30-minute absolute window, exact Owner/project/factor binding, production-only runtime, same fixed Vercel project, unaliased deployment hostname only, no browser interface, no CORS and no Origin/browser request acceptance. GET is a non-provider preflight. POST accepts only the fixed action and public scope digest; IDs, URLs and credential fields are forbidden.

The existing diagnostic six-route provider transport is unchanged. The maintenance native transport allows only GET of the fixed User and DELETE of the fixed exposed factor at `test.stytch.com:443`, with TLS certificate verification, four-second timeout, bounded JSON, duplicate-key rejection, no redirects, no retries and no logging. Existing Production credentials are read only inside the protected server runtime after all request/deployment/time gates. Credentials are not downloaded or inspected by the executor. Raw User responses and authorization headers are never emitted. JavaScript reference clearing is not a claim of guaranteed heap erasure.

Before any provider call, independently verify the exact deployed source UIDs, project and metadata; prove anonymous GET and POST are intercepted by Vercel Authentication; then use the existing opaque authenticated Vercel CLI. Do not weaken deployment protection or create a bypass secret. The stable Production diagnostic domain remains `FAKE_DISABLED`. Do not alias or promote this maintenance deployment. If any gate is unverified, do not invoke cleanup.

The in-process DELETE latch is not durable cross-worker serialization. A cold worker cannot delete a different factor because the target is compiled and never reused; precheck absence prevents repeat deletion after successful cleanup. Concurrent Owner/provider changes can cause postcondition mismatch; that is DENY and preserves quarantine. This limited cleanup is not D04 qualification or production authority.

## Status before live execution

```text
FACTOR_CLEANUP_SCOPE = EXACT_OWNER_AUTHORIZED_SINGLE_FACTOR
FACTOR_DELETE_DEPLOYED = NOT_YET_VERIFIED
FACTOR_DELETE_PERFORMED = NO
FACTOR_ABSENCE_VERIFIED = NO
USER_DELETE_ALLOWED = NO
STYTCH_CREDENTIAL_VALUE_ACCESS = NONE
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
D04 = UNQUALIFIED
```

Sanitized deployment and cleanup results will be recorded in an additive completion document. Do not infer successful provider cleanup from local context retirement, scanner PASS or deployment success.

## Offline review

777 unique tests passed: 366 Node diagnostic tests (43 new fixed-factor tests), 134 G3 regressions, 236 artifact tests (8 new cleanup artifact tests), 30 historical deployment tests and 11 isolated package tests. The exact commands were:

```text
node --test tests/*.test.js (diagnostics/g3-d01-rp)
python -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge
python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_*artifact.py
python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_deployment_prep.py
python -B -m unittest tests.test_ecosystem_isolation_package (fresh accepted-source snapshot)
```

Static source/private-key scan, closed server import graph, exact artifact reconstruction, historical baseline preservation, deterministic 467-entry MANIFEST and `git diff --check` passed. All previously tracked files except MANIFEST retain their accepted bytes after LF normalization. No live provider calls occurred during this review. Ignored validation state and the three unrelated Route D documents are excluded.
