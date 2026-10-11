# Production D03 A enrollment and bounded caller checkpoint v1

2026-10-11. Source checkpoint: `5a1d2720b9a45ddc10cc099ff7604bb25a5ac646`.
This additive receipt preserves prior reports and their historical findings.
It records authenticated setup observations, not D03 closure or production authority.
This is a historical receipt ending before the Owner's renewed Tee login. Its R
login gate, undeployed R configuration, unknown CI allowance and zero S3 counts
describe that earlier interval only. The [R continuation](nexus-production-d03-r-custody-and-canary-preparation-v1.md)
records the subsequent verified state; historical assertions below are preserved.

## Exact enrollment and authorization

The Owner reported completion of the second standalone account login.
AWS Console displayed `NexusD03DiagnosticA (175880707430)` and CloudShell
STS GetCallerIdentity independently returned account `175880707430`, principal
`arn:aws:iam::175880707430:root`. DescribeOrganization returned
`AWSOrganizationsNotInUseException`; GetAccountPlanState returned `PAID` / `ACTIVE`.
The agent did not enroll an account, accept legal terms, inspect account-holder
secrets, or change either account plan at this checkpoint. A's observed Paid Plan
does not establish an independently measured invoice or credit entitlement.

R remains the previously authenticated standalone account `862902859484` (`Tee`).
Signing in to A invalidated the previous R browser session. R's earlier root
identity is historical, not current authenticated custody. No R mutation was
attempted using A's session. Fresh R authentication is required before setup.

The [approved package](nexus-production-d03-custody-authorization-package-v1.md)
and [Owner approval receipt](nexus-production-d03-owner-approval-and-enrollment-checkpoint-v1.md)
remain in force: USD 1.00 maximum incremental D03 expenditure, exact Singapore
bucket and qualification prefixes, seven-day Compliance retention, and necessary
plan upgrade only within qualification scope. No Organization, N01/N02 runtime,
paid compute, production grant or admission is introduced.

The first approved resource operation began at
`T0 = 2026-10-11T05:37:33.570534Z` (A IAM setup). The conservative configured
operation deadline is `2026-11-10T05:36:46Z`, earlier than T0 + 30 days.
No qualification append or extension may outlive the approved operation window;
no retained version may exceed T0 + 37 days. No S3 object or retention exists yet.

## Reused temporary identity and actual A setup

Root setup credentials are not a bounded ordinary diagnostic caller. AWS documents
that root cannot assume an IAM role. Reuse native GitHub OIDC and AWS STS temporary
role credentials instead of creating an IAM login/password, long-lived access key,
custom authentication broker or new runtime. This is diagnostic custody access,
not Owner authentication, a G3 grant, independent review, or production dispatch.

The agent created only the following zero-additional-service-fee IAM resources:

- A provider `arn:aws:iam::175880707430:oidc-provider/token.actions.githubusercontent.com`,
  audience exactly `sts.amazonaws.com`; AWS retrieved its CA thumbprint.
- A role `arn:aws:iam::175880707430:role/G3QualD03DiagnosticCaller`, maximum
  STS session duration 3,600 seconds, with one exact inline policy and no attached
  managed policy. Both trust and identity policy are time-bounded.

The [exact deployed A policy](../research/nexus-production-d03-a-caller-policy-v1.json)
was compared with AWS GetRole, GetRolePolicy, ListRolePolicies,
ListAttachedRolePolicies and GetOpenIDConnectProvider responses. Equality passed.
Trust binds GitHub's issuer, exact STS audience, exact private repository and exact
`nexus-v2-production-qualification` branch subject. The only identity permission
is AssumeRole for R `G3QualFenceAppendRead`, with session name exactly
`nexus-d03-qualification` before the operation deadline. This does not permit
direct S3 mutation, IAM administration, another role or R recovery administration.
Repository/ref trust remains a diagnostic setup binding; it is not immutable
production provenance or automatic execution permission.

Authenticated A inventory returned zero IAM users, zero groups, these two
service-linked roles and the one new caller role, with no truncated role response.
A has no Organization management path. R trust/policy and actual transitive
administration reachability still require independent authenticated inspection.
Two account IDs and a limited role name do not close the custody gate.

The root sessions used for Owner-approved setup remain outside the ordinary
diagnostic permission context. The eventual harness must consume only the bounded
temporary caller/append credentials through supported SDK mechanisms in memory;
it must never export credentials to logs, repository, artifacts or journal.

## Validation taxonomy and unresolved observations

IAM SimulatePrincipalPolicy was requested for the current, expired and wrong
session-name STS cases, each with three exact role resources. It returned an
incomplete one-row generic STS resource result instead of the requested matrix.
All three cases are **INCONCLUSIVE_INCOMPLETE_RESOURCE_MATRIX**. No positive
assumption, expiry enforcement or recovery-administration denial is claimed.
The local diagnostic assertion was corrected to require exact result cardinality
and resource identities before assessing outcomes; an incomplete loop cannot pass.
The initial weak assertion did not modify provider policy, production source or
accepted tests. The separate 16-action IAM/S3/Organizations/AssumeRoot simulation
returned denial, classified **SIMULATOR_ONLY**, not live service enforcement.
Actual scoped SDK calls remain required for D03 qualification.

AWS IAM Access Analyzer ValidatePolicy completed all five bounded policy inputs
(A trust/identity; proposed R trust/identity/bucket). No ERROR or SECURITY_WARNING
was returned. A trust has `CONFIRM_AUDIENCE_CLAIM_TYPE` SUGGESTION; its audience
already uses the single-valued StringEquals operator without a set qualifier.
The R identity and bucket policies each have `WILDCARD_WITHOUT_LIKE_OPERATOR`
WARNING for the deliberately literal `s3:if-none-match = "*"`. Preserve exact
StringEquals/StringNotEquals matching: interpreting this HTTP precondition as a
wildcard would admit arbitrary header values and weaken the required boundary.
These findings are reviewed static provider diagnostics, not proof of enforcement.

The [proposed R append/bucket policy](../research/nexus-production-d03-r-append-policy-v1.json)
remains **UNDEPLOYED**. It confines append to the normal prefix, requires the exact
conditional-create header, reads version-aware history and exact-version retention
from normal/fault prefixes, denies normal deletion/markers and denies diagnostic
mutation outside normal history. It specifies seven-day Compliance default,
BucketOwnerEnforced ownership, all four public-access blocks and SSE-S3 encryption;
no paid KMS key. Independent R administration, bucket/version/configuration readback,
fault isolation and all accepted adversarial consumer cases remain unqualified.

Authenticated GitHub metadata established private repository ID `1341770180`,
Owner administration permission and enabled Actions with zero existing workflows.
The normal protected Git Credential Manager was used only in process memory for
bounded API authentication; no credential values were emitted or persisted.
The Actions billing usage endpoint was unavailable with current access (HTTP 404).
Free quota and additional execution cost are **UNKNOWN**. No Actions workflow,
runner, cache, artifact upload or job was created or started. Do not infer that
Actions are free merely because they are enabled. Verify an existing free allowance
or resolve an exact material cost/scope change before starting a runner.

AWS native multi-session support was enabled and A retained in its own session.
An official Add session / root sign-in page is open for R. No credential store,
cookie, auth header, user-entered password/OTP or private billing record was read.
The remaining immediate human gate is R login/MFA, not manual IAM/configuration.

## Repository and preparation checks

No application, contract, accepted test or G4/G6 architecture changed. The changes
are this receipt, two exact non-secret setup policy records, and MANIFEST.
The prior 532 manifest entries remain byte-equivalent; current count is 535.
Ignored local setup/validation scripts, temporary snapshots and screenshots are
excluded from both Git and the package.

This continuation ran the existing D03 counterexample/boundary regression:
9 tests passed, zero skipped or failed. The isolated static package regression
ran 11 tests, all passed. Total newly executed tests: 20 passed, 0 skip, 0 fail.
These are preparation regressions; none is live recovery custody qualification.
Full historical repository totals are not rerun or promoted to current live proof.
The unchanged 171-member package reproduces SHA256
`9a2e423aa470a4622d73135ebcba20468ab00f42f2d646761743214a99bb13ab`.
MANIFEST, unchanged historical bytes, local references, bounded secret scanning,
explicit staging and git diff --check are required before checkpoint publication.

No billable S3 request, bucket, retained object, new compute service, paid CI job,
account-plan upgrade or irreversible retention operation was performed by the
agent. IAM/standard CloudShell have no additional service charge; this observation
is not an invoice measurement or an account-wide spending cap. Diagnostic access
must be revoked at qualification completion, even if its time limit has not expired.

```text
D03_A_ENROLLMENT = VERIFIED_175880707430_STANDALONE
D03_A_ACCOUNT_PLAN = PAID_ACTIVE_OBSERVED_NO_AGENT_UPGRADE
D03_A_CALLER_CONFIGURATION = CREATED_EXACT_READBACK_VERIFIED
D03_A_CALLER_LIVE_ASSUMPTION = NOT_RUN
D03_STS_IDENTITY_SIMULATION = INCONCLUSIVE_INCOMPLETE_RESOURCE_MATRIX
D03_SENSITIVE_ACTION_SIMULATION = SIMULATOR_ONLY_ALL_16_DENY
D03_R_CONFIGURATION = UNDEPLOYED
D03_R_CURRENT_AUTHENTICATION = HUMAN_LOGIN_REQUIRED
D03_GITHUB_EXECUTION_COST = UNKNOWN_NO_JOB_STARTED
D03_BILLABLE_S3_OPERATIONS = 0
D03_IRREVERSIBLE_RETENTION_OPERATIONS = 0
D03_RESOURCE_WINDOW_T0 = 2026-10-11T05:37:33.570534Z
D03_OPERATION_DEADLINE = 2026-11-10T05:36:46Z
D03_QUALIFICATION_STATUS = NOT_QUALIFIED
D03_STATUS = NOT_CLOSED
G3_STATUS = INCOMPLETE
D01_STATUS = CLOSED
G4_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
G6_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
HUMAN_ACTION_REQUIRED = R_ACCOUNT_LOGIN_AND_REQUIRED_MFA
```

## Primary documentation

- [AWS root cannot assume a role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-cli.html).
- [AWS OIDC provider creation and retrieved thumbprints](https://docs.aws.amazon.com/cli/latest/reference/iam/create-open-id-connect-provider.html).
- [GitHub OIDC audience and subject binding for AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).
- [GitHub Actions included allowance and metered excess](https://docs.github.com/en/billing/concepts/product-billing/github-actions).
- [GitHub billing usage API access requirements](https://docs.github.com/en/rest/billing/usage).
- [AWS native multi-session support](https://docs.aws.amazon.com/awsconsolehelpdocs/latest/gsg/multisession.html).
- [S3 exact conditional-write enforcement](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes-enforce.html).
- [IAM pricing](https://aws.amazon.com/iam/faqs/) and [CloudShell pricing](https://aws.amazon.com/cloudshell/pricing/).
