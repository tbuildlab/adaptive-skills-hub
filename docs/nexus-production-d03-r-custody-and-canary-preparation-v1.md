# Production D03 R custody and canary preparation v1

2026-10-11. Baseline `5a1d2720b9a45ddc10cc099ff7604bb25a5ac646`.
This receipt follows the Owner's renewed Tee login and supersedes the current-state
interpretation of the earlier A-only enrollment receipt. It is not D03 closure.

## Verified deployment and protected setup

R CloudShell STS returned account `862902859484` and root ARN exactly. R plan is
FREE / ACTIVE; approved minimal setup succeeded without any agent plan upgrade.
Complete IAM inventory has zero users, zero groups, zero OIDC providers and four
roles: the two original Support/TrustedAdvisor service-linked roles and the two
approved D03 roles. DescribeOrganization returned AWSOrganizationsNotInUseException.
A is independently authenticated account `175880707430`, PAID / ACTIVE observed
after Owner enrollment, not upgraded by the agent. Neither account is an Organization
management path. Trusted setup uses Owner-authenticated R CloudShell; the ordinary
diagnostic runner has no R root session or root SDK credentials.

The agent created only approved Singapore bucket
`nexus-d03-custody-862902859484-ap-southeast-1-v1`, R `G3QualFenceAppendRead`
and `G3QualRecoveryAdmin`. Versioning Enabled, Object Lock Enabled with default
COMPLIANCE seven days, BucketOwnerEnforced, all four public-access blocks, AES256
SSE-S3 and exact bucket/role policies passed provider readback equality. No managed
role policies or extra inline policies were attached. These observations establish
configuration, not effective ordinary-caller enforcement. The admin role's R-root
principal is account delegation; root cannot assume it. Actual setup administration
was authenticated root, not a falsely claimed assumed RecoveryAdmin session.

The initial bucket read was 404 before creation, and the complete initial version
listing contained zero versions/markers. Setup used 13 S3 attempts. No SDK retries
are enabled. No paid KMS, runtime, logging, replication, acceleration, Organization
or N01/N02 resources were created.

Independent R setup then wrote the exact diagnostic registration, normal GENESIS
and seven isolated fault histories within the two approved prefixes. The registration
version is `PnyOK3mANH6Y5kZQsgQ1VYqACGr1Xb3M`; SHA256
`ac3b890867ded5be576d750b1247021935bf48b9bb45211ef254c969b4d568ec`.
It is TEST_ONLY, fixes the normal origin/generation and exact independent GENESIS/
RECOVER identities, and explicitly states REAL_ADMISSION NO. All 43 initial objects
had actual Compliance retention readback exceeding six days 23 hours. An additional
duplicate fault version and one fault delete marker exercise fork/marker rejection;
normal history was not corrupted. Seed totals: 44 object writes, 22,689 payload bytes,
90 S3 attempts. Cumulative actual S3 attempts at this preparation checkpoint: 103.
No retained version contains a credential, bearer, production grant or site content.
R root then attempted premature deletion and retention shortening of one retained
fault-prefix version. Both actual service calls returned 403 AccessDenied under
Compliance, without relying on the normal-prefix delete deny. The two preceding
version/retention reads and these two refusals add four requests: cumulative 107.

## Minimal integration and evidence taxonomy

The bounded S3 adapter receives an existing scoped SDK client and independently
installed diagnostic registration. It validates canonical unchanged R07 bodies,
complete exact versions, contiguous twenty-digit sequence keys, predecessor IDs/
hashes, retained ledger descriptor/control/page bytes, epoch/incarnation lineage,
registered admin transitions and retention coverage. It rechecks both version
inventories before returning a custody observation. It never returns authority.
The registration's precomputed RECOVER identity is a candidate, not an approval.
RECOVER additionally requires an exact separately retained authorization in the
R-only administration prefix; ordinary append permissions cannot create it.
Absent, duplicated, mismatched or insufficiently retained authorization quarantines
even the previously registered candidate. R must authorize the exact current
predecessor during the independent recovery step.
Missing, duplicated, marked, changed, unsupported, corrupted or partial evidence
quarantines. One conditional append is attempted; acknowledgment loss pins that
exact candidate for read-only reconciliation and prohibits alternative append/retry.
Malformed candidate artifacts are refused before a journal write.

The diagnostic consumer reuses the existing closed snapshot codec. Its records
are synthetic NO_AUTHORITY vectors, not production grants or N01 semantic proof.
Actual S3 responses, injected acknowledgment loss and synthetic consumer predicates
remain separate evidence classes. Production modules do not import the canary.
Independent root setup and ordinary temporary role execution are separate contexts;
account labels alone cannot qualify independence. Actual role and admin-denial
service tests remain required.

GitHub native OIDC/STS reuses the existing private repository and exact development
branch, with time-bounded Aâ†’R trust. GitHub's authenticated Actions billing panel
shows zero of 2,000 included minutes and zero of 0.5GB included storage consumed.
The diagnostic job is bounded to eight minutes, contains no artifact/cache upload,
uses the verified official checkout v4.2.2 commit and pinned SDK, and aborts workflow
reruns before credential acquisition. Only the explicit run-request path triggers
it; documentation pushes do not launch a new diagnostic. No long-lived keys or
new agent/workflow platform are introduced. Runner cost is within verified free
allowance; S3 remains metered and all requests count against the approved limits.

Owner USD1.00 inclusive maximum and the exact approved retention/resource window
remain unchanged. Current small payload/request counts fit the conservative package
bound; no AWS invoice total or account-wide hard spending cap is claimed. Retention
is irreversible for each actual protected version. Diagnostic access is to be retired
after qualification; sustained production custody is not automatically authorized
by this diagnostic package.

## Preparation regression and next gate

New adapter adversarial regression: 27 passed, 0 skipped, 0 failed. Initial combined adapter,
existing offline control and zero-cost boundary regressions: 90 passed, 0 skipped,
0 failed, before the additional independent-recovery-authorization refusal test.
These are offline tests. The earlier package and full regression totals
remain historical until rerun for the exact new checkpoint.

```text
D03_R_CONFIGURATION = DEPLOYED_EXACT_READBACK_VERIFIED
D03_R_CURRENT_AUTHENTICATION = VERIFIED_ROOT_SETUP_CONTEXT
D03_SELECTED_MECHANISM = S3_COMPLIANCE_VERSION_HISTORY_WITH_INDEPENDENT_R_CUSTODY
D03_PROTECTED_DIAGNOSTIC_REGISTRATION = RETAINED_EXACT_VERSION_VERIFIED
D03_GITHUB_COST = VERIFIED_EXISTING_FREE_ALLOWANCE
D03_A_TO_R_LIVE_ASSUMPTION = NOT_RUN_AT_THIS_RECEIPT
D03_BILLABLE_S3_ATTEMPTS = 107
D03_DIAGNOSTIC_PAYLOAD_BYTES = 22689
D03_QUALIFICATION_STATUS = NOT_YET_QUALIFIED
N01_PRODUCTION_LEDGER_QUALIFICATION = NOT_PERFORMED
D01_STATUS = CLOSED
G3_STATUS = INCOMPLETE
G4_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
G6_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
HUMAN_ACTION_REQUIRED = NONE_AT_THIS_CHECKPOINT
```

Primary technical references: [S3 conditional-write and racing-writer semantics](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html),
[GitHub native AWS OIDC](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).

## First source publication and pre-runner syntax failure

Diagnostic source checkpoint `692210cc555b42b7c87f94eea0f3906719f0d6a2` was normally
pushed and remote identity verified. Focused G3/G4/G6 regression passed 230 tests;
isolated package regression passed 11. Full repository regression is still pending,
not PASS. The 175-member diagnostic preparation package has SHA256
`d4746563b39e3a64f8b54b4b68b7e6fac1adbbef9203d08a3be4719fd288a05f`.

[Run 38118190214](https://github.com/TDY0225/adaptive-skills-hub/actions/runs/38118190214)
failed workflow compilation at YAML line 22. GitHub returned zero jobs and the UI
reported the syntax annotation: the unquoted `--only-binary=:all:` shell command
contained a colon followed by whitespace. No runner, OIDC request, STS assumption
or S3 call executed. This failed source validation remains historical FAIL and is
not a qualified live test. Use a YAML block scalar and independently parse it.
The unchanged first diagnostic request is reformatted to publish corrected source
through the exact path trigger; this is not redispatch of an unknown operation.
No qualification effect existed to retry, and the actual append still requires the
protected GENESIS head before its first write. Do not rerun an old workflow attempt.
## Authentication diagnostic follow-up

Run `38118539116` at `fbed5376f3501d749bc1e4e2e93095b88a3f9c79`
completed checkout and hash-pinned SDK installation, then quarantined before
the verified native A-to-R session marker. Its complete sanitized log contains
no S3 call. It is not a successful qualification. A source repair adds only
fixed authentication phase, bounded provider error code and HTTP status; no
provider message, response body, token, credential or header is recorded.
Reformatting the unchanged first request triggers the repaired diagnostic;
the prior job is not rerun, and no unknown S3 write is redispatched.

Run `38118972153` at `58f3def80a647ee30607ff5ad1211d3691d7d5bf`
then established `A_WEB_IDENTITY_ASSUME_ROLE / AccessDenied / HTTP 403`.
It performed no S3 call and did not establish an A or R session.
Authenticated GitHub metadata confirmed repository `1341770180`, Owner
`223441940`, creation `2026-08-21T12:08:28Z`, and default OIDC subject policy.
[GitHub's current official AWS guidance](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
requires immutable Owner/Repository IDs for repositories created after
July 15, 2026. The prepared trust correction replaces the obsolete subject
with `repo:TDY0225@223441940/adaptive-skills-hub@1341770180:ref:refs/heads/nexus-v2-production-qualification`.
It retains exact equality, STS audience, issuer, branch, deadline and all
existing permissions. No wildcard or alternative subject is added.
At this checkpoint the correction is prepared but not applied: A's protected
console session was logged out, while R/Tee remains available. Owner A login
is required; no R paid-plan upgrade is justified by this failure.

After renewed A login, actual STS verified A root `175880707430`. The guarded
repair required exact original trust and unchanged inline permissions before
its single update; exact immutable subject trust readback and unchanged
permissions then passed. No alternative subject, wildcard, audience, principal,
deadline or permission was added. R configuration and retained versions were
not rebuilt. A new bounded first-stage request follows only the known prior
authentication failures with zero S3 calls; no prior job rerun is used.

## Completed offline compatibility regression

Full Python discovery in the repaired-core static snapshot: 1167 tests,
1163 PASS, four existing environment SKIP, zero failure/error. The wrapper's
Windows stdout encoding failed while printing the completed UTF-8 log; its
recorded unittest `OK (skipped=4)` was recovered without rerunning the suite.
The four skips are the three unconfigured embedded runtime inputs and the
Windows symlink fixture without privilege. They are not counted as PASS.

Existing offline Node compatibility: 366 PASS, zero skip/fail. Two earlier
validation snapshots failed because the static manifest omits the credential
loader source by its existing name policy, and the standalone diagnostic
snapshot initially lacked its generated disabled source artifact. The final
check used 99 exact tracked diagnostic files and the existing offline artifact
builder with network traps. No D01 source, test, ceremony, deployment or closed
qualification was changed. The failed snapshot attempts remain recorded.

Unique Python plus Node result: **1533 total / 1529 PASS / 4 SKIP / 0 FAIL**.
Focused repetitions (27 D03, 230 G3/G4/G6, 11 package tests) are not added.
The later live canary change only adds sanitized authentication phase/status
diagnostics; it passed compilation, current-source package isolation and exact
package reproduction. The full run's snapshot is retained separately from
these current-source checks; no exact final release qualification is claimed.

## Actual append stage and independent recovery

[Run 38127720218](https://github.com/TDY0225/adaptive-skills-hub/actions/runs/38127720218)
at `914513b526e8bb9c4549dd5b230e96a88430a190` passed its first attempt.
Native GitHub OIDC, exact A temporary caller and exact R AppendRead identities
were verified. All 298 S3 calls have sanitized provider records: 288 HTTP 200,
seven HTTP 403 and three HTTP 412. Thirteen object creates succeeded. The exact
retained registration matched its original protected version and digest.
Conditional duplicate/conflicting writes returned PreconditionFailed; overwrite,
deletion, retention shortening, fault/admin-authorization writes and bucket
administration returned AccessDenied. R recovery-admin assumption was denied.
Unknown acknowledgment after an actual committed append quarantined without
retry, then reconciled only its exact version. Concurrent contenders produced
one 200, one 412 and one version. All seven isolated fault histories quarantined;
stale head, generation/incarnation and inadequate retention coverage quarantined.

Independent R root then verified all exact journal/object bytes at current
sequence 3, rechecked complete inventories and original protected registration,
and created root-only retained recovery authorization plus sequence 4 RECOVER.
This used 70 S3 calls, six writes and 4045 payload bytes. Exact readback yielded
RECOVER version `.HLyIDG2CtYV7V7pe7r3PTcTd7rCjd3W` and authorization version
`QfYTlVH0dMa0UrGM1zI8flinsMTPw_Ic`. No primary history was overwritten and no
authority was created. Total S3 attempts before restart-read qualification: 475.

The pending fresh restart-read stage also tests actual IAM trust/permission
mutation rejection and bucket-policy mutation rejection using the unchanged
exact existing policy bodies. Unexpected acceptance fails qualification and
cannot widen access. This is custody qualification, not a D04 release gate.
D03 remains NOT_YET_QUALIFIED until that stage and retirement checks complete.
