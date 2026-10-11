# Production N01 bounded service qualification authorization package v1

2026-10-11. Accepted D03 closure parent:
`5aea47b962113ae67821c1406766e15a78539287`.
PROPOSED_NOT_APPROVED. No resource or spending approval is inferred from this file.

## Why this separate approval is required

The accepted [D03 approval package](nexus-production-d03-custody-authorization-package-v1.md)
expressly excludes DynamoDB, N01/N02 services and any prefix outside
`qualification/v1/normal/` and `qualification/v1/faults/`. Its bounded ten-gate
qualification is now [closed and retired](nexus-production-d03-bounded-live-closure-v1.md).
Do not reopen its roles, registration, ceremonies or fault journals. A real N01
atomic primary ledger and separately registered current-head lineage are distinct
remaining production gates. Source hashes and synthetic storage cannot satisfy
them. Only the new bounded scope below is proposed; REAL_ADMISSION remains NO.

## Exact proposed service envelope

- A `175880707430`: one DynamoDB Standard ON_DEMAND table
  `NexusG3AuthorityV1`, `ap-southeast-1`, string keys `pk` and `sk`, no indexes,
  streams, PITR, backups, global replicas, TTL or customer-managed KMS key.
  Only fixed instance `g3-n01-qualification-v1` may be used by the runtime role.
- R `862902859484`: reuse existing bucket
  `nexus-d03-custody-862902859484-ap-southeast-1-v1`, with new exact namespaces
  `qualification/n01/v1/normal/`, `qualification/n01/v1/faults/` and
  `qualification/n01/v1/approvals/`. The approvals prefix is R-admin-only;
  A cannot write, delete or administer it. Existing D03 objects are untouched.
- New A `NexusG3QualificationCaller` and R `NexusG3N01AppendRead` roles, one
  A `NexusG3QualificationCleanup` role and one one-time native Scheduler job
  `NexusG3QualificationDeleteTableV1` in the sole new group
  `NexusG3QualificationCleanupV1`. Exact principals, subjects, resources,
  session name, registration/instance and deadline; no managed policies or
  long-lived keys. R root remains independent setup/recovery custody.
- Existing GitHub OIDC issuer and exact immutable-ID branch subject may be reused
  for bounded service qualification. Existing Vercel `nexus-g3-qual` Hobby runtime
  is a conditional later ingress candidate; only after exact native OIDC namespace,
  project, revision and token origin verification. No Vercel upgrade or paid
  add-on, new project, new model API charge or commercial Hobby usage is approved.
- No ECS/ECR/ALB/EC2/Lambda, Secrets Manager, paid logs, Organizations, new generic
  orchestration service or unrelated AWS resource. New OIDC provider registration
  is limited to the exact verified Vercel issuer if necessary, with no static secret.

Reviewable resource/IAM templates are
[`research/nexus-production-n01-resource-proposal-v1.json`](../research/nexus-production-n01-resource-proposal-v1.json).
Only `_BOUND_DEADLINE_UTC_` is substituted: actual T0 plus 48 hours, recorded before
the first operation. Its time limit is not permission to widen any resource or
identity. If an exact name collides with unrelated state, fail closed; no adoption
or destructive replacement. Native DynamoDB transactions use underlying
PutItem/UpdateItem permissions, not an invented TransactWriteItems IAM action.
[AWS transaction IAM](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis-iam.html).

## Cost and operation bounds

Proposed **additional maximum USD 1.00 including applicable taxes**, separate from
the original D03 ceiling. This is an authorization cap, not an AWS account-wide
hard billing cap. No free tier or credit is required by the calculation.

Across all qualification runs, failures, restarts and cleanup: at most **512
DynamoDB data-plane attempts**, at most two affected items per transaction,
each service item at most 400 KiB, and at most **64 MiB of all retained table
items**. Strong reads use at most 100 units per 400 KiB item. Reserve 1,600 write
units per attempt to cover two 400 KiB transactional writes, including failed
conditions. Do not reset the aggregate attempt ledger on process restart.
Unknown writes quarantine and reconcile read-only, never retry or redispatch.
If a meaningful complete run cannot fit, stop the affected paid operation for a
new bounded approval; do not weaken qualification or make extra uncounted calls.

New S3 scope separately permits at most 64 MiB including every version, 5,000
Tier 1 / 50,000 Tier 2 attempts, and 0.25 GB ordinary outbound. Count configuration,
negative calls, pagination and cleanup. The new lineage cannot be promoted from
TEST_ONLY evidence and cannot restore earlier D03 authority. No user content,
secret, bearer, raw provider session or OTP is persisted in custody evidence.

Singapore DynamoDB public catalog published 2026-09-11 returns USD 0.71/million
write units, USD 0.1425/million read units, USD 0.285/GB-month storage. Recheck
rates before spending. Conservative envelope:

| Component | Calculation | USD before tax |
| --- | --- | ---: |
| DynamoDB writes | 512 x 1,600 x 0.000000710 | 0.581632 |
| DynamoDB reads | 512 x 100 x 0.0000001425 | 0.007296 |
| DynamoDB storage allowance | 0.0625 GB x 37/28 months x 0.285 | 0.023538 |
| S3 retained bytes/requests/outbound | Original conservative D03 rate envelope | 0.100000 |
| One native cleanup invocation | Reserve, without assuming free tier | 0.000010 |
| Total | Conservative modeled envelope | 0.712476 |

Reserve 20% for taxes, producing **USD 0.854972**, rounded up to **USD 0.86**.
The 20% reserve is not a claim about the account's actual tax rate. The exact
invoice remains UNKNOWN before metered use. Check any applicable charge/plan
requirement before execution; if the forecast exceeds USD 1.00, pause again.
The 37-day storage allowance is contingency, not permission to operate that long.
[DynamoDB public catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/ap-southeast-1/index.json),
[pricing](https://aws.amazon.com/dynamodb/pricing/),
[native transaction capacity](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html),
[Scheduler pricing](https://aws.amazon.com/eventbridge/pricing/).

## Lifetime, irreversible effects and cleanup

All runtime and qualification access expires at **T0 + 48 hours**. Every context,
grant, claim-use window and registration must end at or before that deadline; no
production activation or persistent authority beyond it. At completion revoke
the temporary append/runtime permissions and independently witness retirement.
No active authority may depend on state deleted by cleanup.

Every newly retained S3 version uses **Compliance seven days** from creation.
Before expiry, neither root nor this approval can remove it or shorten retention.
Retirement and native lifecycle rules affect only the three new fixed prefixes:
current expiration at eight days, noncurrent expiration at one day, and expired
marker cleanup, subject to Object Lock. Existing D03 lifecycle remains unchanged.
Scheduled expiration is not observed deletion; verify actual versions later.

Native Scheduler performs one exact DeleteTable on the new table only, after
the operation deadline plus ten minutes. This irreversibly removes the disposable
primary qualification state after every possible authority use window is closed.
The cleanup role has only DeleteTable on that exact table and is outside normal
runtime. No automatic retry, queue, Lambda or event bus is added. Missing/ambiguous
head after deletion continues to deny; retained independent history cannot revive
old authority. Scheduling is not successful deletion and cleanup failure can leave
residual storage cost; verify and remediate inside the same ceiling.
[Native universal targets](https://docs.aws.amazon.com/scheduler/latest/UserGuide/managing-targets-universal.html).

No already-existing table or unrelated object may be deleted. No account upgrade
is approved here. A/R plan state must remain usable under the already approved
D03 enrollment; if a new subscription fee is required, pause before accepting it.
Long-term production custody and final activation are outside this disposable
qualification budget and must be explicit in the eventual exact release package.

## Alternatives and decision

Free local/Git alternatives already failed to establish independent current-head
custody. A provisioned 4-write/4-read table for 48 hours appears cheaper at idle
but cannot demonstrate the accepted large atomic reservation envelope without
additional throughput qualification; free credits and burst availability are not
assumed. A custom database/consensus system adds implementation and operational
risk. On-demand DynamoDB reuses the accepted managed primary candidate with native
conditional transactions and no idle throughput charge; S3 custody and existing
Host authentication remain reused. No cheaper **fully qualified complete** path
has been demonstrated. This proposal is conditional until actual runtime/service
qualification and independent review pass.

```text
N01_OPTION = DYNAMODB_ON_DEMAND_PLUS_EXISTING_R_S3_AND_EXISTING_HOST
MODELED_COST_ENVELOPE = USD_0.86_WITH_20_PERCENT_TAX_RESERVE
EXACT_INVOICE_COST = UNKNOWN_UNTIL_METERED
ADDITIONAL_MAXIMUM_BOUNDED_COST = USD_1.00_INCLUDING_TAX
IRREVERSIBLE_EFFECTS = SEVEN_DAY_S3_COMPLIANCE_AND_EXACT_DISPOSABLE_TABLE_CLEANUP
OPERATION_WINDOW = T0_PLUS_48_HOURS
RETENTION_PERIOD = SEVEN_DAYS_PER_NEW_S3_VERSION
APPROVAL = PENDING_OWNER
NEW_PAID_RESOURCES_CREATED = NO
REAL_ADMISSION_ENABLED = NO
```
