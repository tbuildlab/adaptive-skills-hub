# N01 native public-review bootstrap observation v1

2026-10-12 UTC. Exact successful source checkpoint:
`1dc3cf754615113fa3a53b93885fe28a7d9ef90b`.
This additive observation supersedes only the pending bootstrap observation in
the [earlier custody checkpoint](nexus-production-n01-public-review-live-custody-v1.md).
It preserves all historical bytes, qualifications and review deadlines.

## Actual protected native execution

Deployment `dpl_5sxMuPgfNyt8kAX1xqQbRi8i7Nwn` was READY in the existing
`prj_xH23xMATVChdhX34OS2vjI8dfWN2` project. All 29 submitted platform source
identities matched. Native protection remained `all_except_custom_domains`.
The protected generated host was
`nexus-g3-qual-2t17w2lbo-tdy0225.vercel.app`.

The one successful explicit invocation logged the closed sanitized result
`NATIVE_PUBLIC_REVIEW_BOOTSTRAP_VERIFIED`. It performed six S3 reads through
native Vercel OIDC → exact A temporary role → exact R AppendRead role → the
independently retained public review. It verified the fixed public pins in the
actual Linux runtime. There were zero DynamoDB attempts, Stytch operations,
Stytch credential reads, source writes, Owner contexts or execution permissions.
Browser response blocking did not prevent server execution; protected native
runtime logs supplied the observed result. No blocked response was redispatched.

The submitted complete inventory SHA256 was
`81b3bfa9a399628e90cd57c771f7d085a888066a79513f7334c02075644194e7`.
The measured actual runtime inventory SHA256 was
`9573abc3f60aff92499a282f5ee17308f730534b4d69082e03c5962f41a48d9b`.
These identify different byte inventories, not an unexplained equality. Native
build serialization changed `vercel.json` bytes while preserving its exact JSON
meaning. The adapter checks duplicate-free canonical equality against the bound
configuration and measures actual bytes; all other files require exact bytes.
No semantic configuration change is accepted. Native project `name` and the
exact function's 60-second limit are explicit build inputs.

The [official Python runtime](https://vercel.com/docs/functions/runtimes/python)
uses file-based handlers. The [native Python builder source](https://github.com/vercel/vercel/blob/main/packages/python/src/index.ts)
excludes `public/**` from the function bundle. The static non-authorizing page
therefore resides at the artifact root, and the loader declares the handler
class explicitly. These are narrow deployment compatibility repairs.

## Preserved failures, bounds and qualification limits

Eight deployments and seven explicit runtime invocations occurred. The first
deployment failed before runtime; six later invocations quarantined. One early
quarantine lacked exact service-attempt visibility, so its full 12-read bound
remains reserved. Five diagnosed artifact failures preceded AWS access. The
successful invocation used six reads. The eight-invocation allowance has one
unused invocation; it is not automatic retry permission.

Known cumulative observations are 82 DynamoDB / 335 S3 attempts. Conservative
upper accounting, including earlier unobserved responses, is 86 / 547. Invoice
cost is UNKNOWN. The approved USD 1.00 N01 cap, 48-hour operation deadline,
seven-day retention, aggregate request ceilings and scheduled cleanup remain
unchanged. No paid plan, new resource, account or permission expansion occurred.

Nine current bootstrap contract tests pass. They include the added exact native
configuration semantic-equality test; repeated earlier runs are not added to
distinct totals. Seven new complete-membership reader tests pass. That reader
reuses the immutable version/retention/lineage transport and resolves nested
grant, revocation, source and checkpoint references. It is read-only, returns
NONE, and does not promote the historical TEST_ONLY storage registration.
Fixtures remain under tests and are not live observations.

Bootstrap does not qualify a complete controller. Its process nonce and artifact
must not be registered as an Owner writer. Actual current source registration,
Owner/context persistence, revoke/consume/replay, N02 and release remain pending.
The original public-pin review expires at 2026-10-12 15:51:51.502
Asia/Kuala_Lumpur, exclusive. No expiry extension is inferred.

```text
N01_NATIVE_PUBLIC_REVIEW_BOOTSTRAP = PASS_EXACT_BOUNDED_READ_ONLY
CURRENT_SOURCE_ENROLLMENT = NOT_PERFORMED
CURRENT_OWNER_CONTEXT = NOT_CREATED
N01_FULL_LIVE_STATUS = INCOMPLETE
D01_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
D03_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
G3_STATUS = INCOMPLETE
G4_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
G6_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
