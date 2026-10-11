# Production D03 custody authorization package v1

2026-10-11. Source checkpoint: `0703f45c33f748920b847010cc8c22970e74aa78`.
This is a proposed bounded authorization package, not Owner approval, custody
qualification, independent review or production admission.

## Authenticated discovery

Protected AWS Console CloudShell successfully returned free read-only metadata:
account `862902859484`, principal `arn:aws:iam::862902859484:root`.
Organizations `DescribeOrganization` returned `AWSOrganizationsNotInUseException`.
IAM role enumeration returned only `AWSServiceRoleForSupport` and
`AWSServiceRoleForTrustedAdvisor`. No existing A/R pair or D03-specific role was
established. These observations supersede only the earlier survey's unavailable
browser-access observation; its historical bytes remain unchanged.
Free Tier `GetAccountPlanState` returned `FREE` / `ACTIVE`. Remaining credit amounts
and private billing/contact data were not queried. Login does not approve a plan
upgrade, Organization creation, spending or retention.

No credentials, payment details, contact records, cookies or authentication caches
were copied into repository evidence. No Organization, account, role, bucket,
billable S3 request or irreversible retention configuration was created.

## Selected conditional mechanism and exact scope

Reuse AWS S3 Standard in `ap-southeast-1`, Versioning, fixed Compliance retention,
policy-enforced conditional creation, complete version-aware history and the
existing Nexus checkpoint/recovery consumer protocol. The managed survey remains
[conditional](nexus-production-d03-managed-custody-survey-v1.md), not PASS.

The proposed exact bucket is
`nexus-d03-custody-862902859484-ap-southeast-1-v1`, in the current Owner recovery
account R. Only fixed `qualification/v1/normal/` and `qualification/v1/faults/`
prefixes are authorized here; no production bearer, personal material or secrets.
If this bucket name is unavailable, do not alter or adopt an unrelated existing
bucket. Resolve scope before any replacement incurs money or irreversible effects.

Preserve the accepted two-account requirement. Use the current Owner account as
trusted standalone R custody and enroll/reuse at most one separate standalone A
account named `NexusD03DiagnosticA`, if supported by actual AWS permission, account
enrollment and legal boundaries. **No AWS Organization is proposed.** No account
has been created or qualified. A new standalone account
requires a unique Owner-controlled email; do not invent a deliverable address or
inspect private credential stores. Ordinary authenticated discovery/configuration
is autonomous; genuinely unavailable account-holder input remains a human gate.

At most one A `G3QualD03DiagnosticCaller`, one R `G3QualFenceAppendRead`, and one R
`G3QualRecoveryAdmin` role are proposed; a distinct fault role is permitted only
if an accepted adversarial case requires it, limited to the fixed fault prefix.
No long-lived access key, unrelated cross-account access or public access is
authorized. The append role may write/read only the registered journal and cannot
delete versions, create markers, alter retention, change bucket/IAM controls or
assume recovery administration. Fault permissions cannot touch the normal prefix.

The required separation is that ordinary A execution cannot administer R,
including transitive role/root/organization paths. Owner R root/setup access
must remain outside the ordinary diagnostic/runtime permission context. Possession
of the present root session is trusted setup access, not production executor
authority or demonstrated administrator separation. Verify A's actual enrollment
and administrator paths; two account numbers alone are insufficient.
Failure to establish effective
separation blocks D03; D04 is not reintroduced as a delegated-mode release gate.

No DynamoDB, ECS, ECR, EC2, paid logging, KMS key, replication, acceleration,
multipart runtime, new planner, orchestration framework or N01/N02 service is in
this D03 package. IAM, Organizations and standard CloudShell have no additional
service charge; creating other resources from CloudShell is not free by implication.

Creating/joining Organizations can change Free Plan eligibility and credit activity
eligibility. Historical public billing guidance and the newly updated October 2026
FAQ differ on details of remaining credit expiry; do not silently choose the more
favorable statement or promise retained credits. Avoid Organizations in this package.
Standalone accounts preserve the accepted A/R requirement without adding management
account reachability. A second Free Plan/credit grant is not assumed for an existing
customer. Basic Support only; no paid support subscription.

This proposed approval also covers an explicit metered Paid Plan upgrade of current
R if needed for full IAM/S3 qualification or sustained account availability, inside
the same operation budget. Such an upgrade has no asserted fixed fee but enables
pay-as-you-go billing beyond credits and **cannot revert to Free Plan**. No upgrade
has occurred. Do not activate unrelated advanced features or promise credit expiry
dates; actual account terms must be observed before any change. A legal agreement
or unavailable Owner account-holder action remains a distinct human gate.

## Bounded expenditure and irreversible effects

Proposed Owner-authorized incremental expenditure: **at most USD 1.00**, including
applicable tax, for the controlled D03 operations below. This is an authorization
ceiling, not an AWS-enforced account-wide hard cap. Do not spend beyond it or enable
unbounded workloads. An AWS Budget alert would not enforce this ceiling.

- One exact private S3 Standard bucket; at most 64 MiB total retained bytes,
  counting every version and diagnostic fault object.
- At most 5,000 Tier 1 and 50,000 Tier 2 requests, counting negative tests,
  SDK attempts, enumeration pages, configuration/readback and cleanup. No
  unlimited retries; unknown outcomes quarantine and reconcile exactly.
- At most 0.25 GB ordinary internet outbound; do not assume free credits/egress.
- Qualification operations stop no later than T0 + 30 days, where T0 is the first
  approved resource operation. No new appends or retention extensions after that
  deadline. Every retained version has at most seven days of retention measured
  from its approved append/extension; no retention date exceeds T0 + 37 days.
- No automatic production use or perpetual custody subscription is authorized.
  Bound and stop operations before any aggregate quantity or authorization limit.

The verified Singapore public rates are USD 0.025/GB-month, 0.000005/Tier 1
request, 0.0000004/Tier 2 request and 0.120/GB ordinary outbound. Conservatively
charging a full 1 GB-month for the much smaller 64 MiB/37-day storage envelope
gives `0.025 + 0.025 + 0.020 + 0.030 = USD 0.100` before tax.
AWS's published Malaysia service tax is 8%; the indicative amount with that rate
is **USD 0.108**. Exact invoice cost is not knowable before actual metered use,
tax treatment, billing rounding and currency conversion. The proposed USD 1.00
ceiling leaves margin; it is not an exact bill, account-wide cap or promise to
cover hostile/unrelated traffic or future price changes. Unexpected pricing or
metering that cannot fit the ceiling blocks further billable operations.

Enabling Object Lock permanently prevents disabling Object Lock or suspending
Versioning on this bucket. Each Compliance-retained version cannot be deleted or
have retention shortened before its exact expiry; administrative account closure
is not an accepted escape. The proposed default is **seven days per version**.
Seven days is a bounded qualification choice, not perpetual production protection.
The consumer must require all relied-on ancestors to remain protected throughout
its claimed lifetime, or deny/quarantine. Extensions may only occur inside the
same approved cost/window limits; they cannot silently enlarge this authorization.

Revoke diagnostic append access when qualification ends. Retire the diagnostic
registration before expiry or cleanup; never omit needed history to reduce costs.
The proposed scope includes expiry-based disposal of only these synthetic diagnostic
versions after their exact retention expires, with local sanitized evidence kept
and the emptied qualification bucket removed. Record and verify cleanup scheduling
and its actual completion separately; scheduling does not prove deletion happened.
No production lineage or unrelated account data may be deleted. Do not close either
AWS account. Failure or delay of cleanup may leave small residual storage charges;
report it honestly and remediate, rather than claiming an absolute service cap.

Sustained production custody, a different retention lifetime, new services or an
expanded resource budget are material changes outside this package. They must be
specified in a later exact release/cost package before use. Qualified short-lived
diagnostics do not authorize long-term production or REAL_ADMISSION.

## Qualification obligations after approval

Reuse the accepted [minimal D03 gates](nexus-g3-d03-minimal-scope-and-autonomy-amendment-v1.md)
and [closed offline semantics](nexus-g3-u1-d03-offline-semantic-closure-v1.md).
Verify exact A/R identities, trust and effective policy, protected origin/current
head, conditional append, version retention and all-version complete history.
Run isolated stale/duplicate/rollback/fork/gap/delete-marker/corruption/unknown
acknowledgment/restart/generation/incarnation/unavailable-backend/unauthorized
mutation cases. Independent history must constrain recovery without creating
authority; NO_AUTOMATIC_REDISPATCH remains mandatory. Real AWS responses and
synthetic consumer references have separate evidence classifications.

Approval authorizes bounded setup and qualification, not a result. Close D03 only
after actual required properties are demonstrated. G3 implementation/E2E, G4/G6
live qualification, accepted independent review and exact Owner release acceptance
remain subsequent gates. D01 is not repeated; completed G4/G6 design is preserved.
REAL_ADMISSION remains NO throughout this preparation and qualification package.

No cheaper **qualified** complete alternative was established by the retained
managed survey. B2's lower storage rate alone does not prove equivalent conditional
append/custody; Azure requires a different accepted deployment and actual protection
qualification. Do not weaken security for a lower nominal storage price.

## Sources and status

- [AWS member-account creation and management access](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_create.html).
- [Current Free/Paid Plan, eligibility and downgrade limitations](https://aws.amazon.com/free/free-tier-faqs/),
  [account-plan metadata API](https://docs.aws.amazon.com/cli/latest/reference/freetier/get-account-plan-state.html).
- [IAM pricing](https://aws.amazon.com/iam/faqs/),
  [Organizations pricing](https://aws.amazon.com/organizations/faqs/),
  [CloudShell pricing](https://aws.amazon.com/cloudshell/pricing/).
- [S3 irreversible Object Lock configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-configure.html),
  [conditional-write enforcement](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes-enforce.html).
- [Singapore S3 price catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/ap-southeast-1/index.json),
  [ordinary outbound catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/ap-southeast-1/index.json),
  [AWS Malaysia tax](https://aws.amazon.com/tax-help/malaysia/).

```text
D03_SELECTED_OPTION = AWS_S3_COMPLIANCE_TWO_ACCOUNT_CONDITIONAL
D03_ACCOUNT_TOPOLOGY = TWO_STANDALONE_ACCOUNTS_NO_ORGANIZATION
D03_CURRENT_ACCOUNT_PLAN = FREE_ACTIVE
D03_BOUNDED_COST_APPROVAL = PENDING
D03_RETENTION_APPROVAL = PENDING
D03_PAID_OPERATIONS = 0
D03_IRREVERSIBLE_RETENTION_OPERATIONS = 0
D03_EFFECTIVE_CUSTODY_QUALIFICATION = NOT_PERFORMED
D01_STATUS = CLOSED
D03_STATUS = BLOCKED_NO_ZERO_COST_QUALIFIED_FENCE
G3_STATUS = INCOMPLETE
G4_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
G6_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```

This document grants no permissions. Only the Owner's subsequent explicit approval
of this exact bounded package can authorize its proposed spending/retention scope.
