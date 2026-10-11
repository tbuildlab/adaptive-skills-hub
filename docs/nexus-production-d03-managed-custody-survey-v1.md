# Production D03 managed custody survey v1

2026-10-11. Accepted baseline: `8f35fabab90bb1a0b51d41f1eb5f55dd79a2ffc5`.
Development branch: `nexus-v2-production-qualification`.

## Authorization and unchanged boundaries

The Owner authorizes a cost-minimized managed/external custody survey and subsequent
Production Final work. Actual spending and irreversible retention require a separate,
concrete bounded approval before the first such operation. This supersedes the prior
zero-paid survey exclusion for research, without approving expenditure. The completed
[zero-cost survey](nexus-g3-d03-zero-cost-survey-v1.md) is retained, not repeated.

[Minimal D03 scope](nexus-g3-d03-minimal-scope-and-autonomy-amendment-v1.md) remains
authoritative: independent custody, exact registration, complete protected history,
conditional append, stale/fork/gap/rollback rejection, quarantine, incarnation retirement
and no automatic redispatch. The accepted two-account requirement is preserved.
D01 remains CLOSED; G3 remains INCOMPLETE; G4 and G6 preparation remain complete.
D04 executor exclusion is not a delegated-mode release gate. REAL_ADMISSION remains NO.
No compatibility amendment, new product feature, production adapter or authority is
created by this survey.

## Managed candidate comparison

These are documentation and access dispositions, not live qualification results.
Lower storage prices alone cannot qualify custody or justify replacing accepted contracts.

| Mechanism | Disposition | Required-property evidence and remaining gap | Cost/integration assessment |
|---|---|---|---|
| AWS S3 Standard, separate recovery account, Versioning and fixed Compliance retention, policy-enforced conditional writes | PREFERRED_CONDITIONAL_CANDIDATE | Documented WORM version retention and conditional create; existing Nexus protocol fits. Actual A/R identities, transitive administrator separation, fixed enrollment, effective policy, complete version-aware history and adversarial recovery remain unverified. | No minimum S3 charge; small metered objects/requests. Existing CLI and accepted AWS contract minimize integration. No N01 compute/database is needed to qualify D03. |
| Azure Blob locked immutability with independently administered recovery subscription/tenant | CONDITIONAL_ALTERNATIVE | Locked retention cannot be shortened/unlocked; writes can still create versions. Exact custody, registration, append preconditions, complete history and live recovery need qualification. It does not automatically satisfy the accepted AWS two-account deployment contract. | Immutability adds no capacity surcharge, but storage, policy transactions and versions are billed. No authenticated Azure custody or thin Nexus adapter is established. A lower storage rate would not establish lower total qualification cost. |
| Backblaze B2 Compliance Object Lock and separately controlled account/application capability | INSUFFICIENT_EVIDENCE_CONDITIONAL | Documented immutable files and irreversible Object Lock enablement. The reviewed S3-compatible guide lists IAM roles as unsupported; equivalent protected role semantics and necessary conditional-write enforcement were not established. No universal claim that B2 cannot support a suitable deployment. | Published pay-as-you-go storage is USD 6/TB-month and Object Lock has no extra fee. Cheaper storage is plausible; no qualified cheaper complete D03 mechanism was demonstrated. No account/key created. |
| Cloudflare R2 bucket locks | NOT_SELECTED_FOR_ACCEPTED_COMPLIANCE_BOUNDARY | Official API/UI documentation permits removal/replacement of lock rules. That is not evidence of the accepted irreversible Compliance retention guarantee. Independent permissions alone do not establish all required recovery semantics. | Standard published storage USD 0.015/GB-month; no egress charge. A new weaker retention contract is not adopted to obtain PASS. |

No candidate is CLOSED or PASS. S3 is preferred as the best-supported reuse path among
the reviewed candidates, not a proof of the globally cheapest possible service.

## Verified public rates and bounded estimate limitations

Read-only public AWS Price List retrieval on 2026-10-11 returned Singapore rates:

| Meter | USD rate | Verified catalog identity |
|---|---|---|
| S3 Standard, first 50 TB | 0.025 / GB-month | AmazonS3, publication 2026-09-28, SKU M6MTARCQFUQBQ2V3 |
| PUT/COPY/POST/LIST | 0.000005 / request | AmazonS3, SKU VHRJWKRHEA6VHEFY |
| GET and other Tier 2 requests | 0.0000004 / request | AmazonS3, SKU T469UNPYX78434EG |
| Ordinary internet outbound beyond global free tier | 0.120 / GB, first 10 TB | AWSDataTransfer, publication 2026-09-16, SKU SDHP4R7WGBVJPQPY |

The S3 catalog also exposes a zero-rated transfer entry and MRAP-specific entries.
Neither is used to infer free ordinary internet egress. The separate AWSDataTransfer
catalog supplies the ordinary outbound rate. Free credits, free allowances, taxes,
currency conversion, billing rounding and existing account usage are not assumed.

An illustrative, **unapproved** D03-only envelope is at most 64 MiB retained data,
5,000 Tier 1 requests, 50,000 Tier 2 requests and 0.25 GB ordinary outbound. Charging
an entire 1 GB-month conservatively instead of the smaller storage quantity gives
USD `0.025 + 0.025 + 0.020 + 0.030 = 0.100` before tax. This is a planning calculation,
not an exact invoice, approved limit or service-enforced account-wide cap. It excludes
other production phases. No AWS Budget alert is represented as a hard spending limit.

The actual approval package must bind discovered accounts/resources, finite retention,
request and payload limits, the execution window, cleanup and residual storage treatment.
It must distinguish bounded agent operations from unrelated or hostile account traffic.
If exact billing/access facts or enforceable limits remain unknown, report that uncertainty
instead of promising an exact maximum. Seven-day retention in earlier proposals is not
approved here. A short qualification window does not establish perpetual production
recovery protection; final supported lifetime and custody must separately qualify.

## Minimum selected-path preparation

Reuse the existing closed checkpoint codec and PREPARED/append/readback/finalize protocol.
Discover A/R caller/account/role identity through protected authenticated interfaces.
Verify that ordinary execution/append access cannot administer recovery custody,
including through root/organization/role-assumption paths. Separate account numbers
alone are insufficient. Register an exact lineage and its independently controlled origin.

The candidate resource set is one private R-account S3 Standard general-purpose bucket,
fixed bounded normal/fault prefixes and the minimum A diagnostic / R append-read /
independent recovery-administration roles. Use existing suitable roles where possible.
Enforce TLS, private access, version ownership, conditional create and explicit rejection
of deletion, unauthorized retention/policy mutation and alternate genesis. Bound single
object uploads; do not enable multipart, acceleration, replication, public endpoints,
KMS subscriptions, paid logging or N01/DynamoDB/ECS/ECR by default.

Object Lock protects versions, not the logical current head: new versions/delete markers
remain a concern. Recover only from complete version-aware current history; reject
duplicates, markers, gaps, forks, malformed bytes, incorrect predecessor and inadequate
retention. Unknown append acknowledgments require exact reconciliation and quarantine,
never automatic retry/redispatch. Recovery evidence constrains, never creates authority.

Enabling Object Lock cannot be reversed or versioning suspended on that bucket.
A retained Compliance version cannot be deleted or its retention shortened before expiry.
These effects require the Owner's bounded approval before enabling/writing them.

## Actual access checkpoint and continuation

The installed official AWS CLI returns zero profiles and no usable STS caller identity.
EC2 metadata probing was disabled and timeouts bounded. Only status was reported; no
credential values, configuration contents, caches or cookies were read or retained.
An official AWS Console navigation in Chrome reached the IAM sign-in form, with no
authenticated account context. Existing account login is the next unavoidable human
action. Do not ask the Owner for IDs, ARNs, IAM JSON or secrets.

After protected login, perform only free/reversible metadata and custody discovery first.
Present the exact seven-field cost/retention package and one explicit approval before
the first money-incurring or irreversible operation. Do not infer approval from login.
No resources, paid services, irreversible retention, new D01 ceremony, live production
authority, independent review result, production freeze/tag or admission was created.
The implementing Codex's local survey is not an independent security review.

## Pre-login development verification

All 529 prior MANIFEST entries and all prior tracked non-MANIFEST bytes are preserved
under the repository's LF normalization. The static manifest has 530 entries: only
this advisory survey is added. The private package remains 171 members, reproducible
across two builds, with unchanged SHA256
`9a2e423aa470a4622d73135ebcba20468ab00f42f2d646761743214a99bb13ab`.
The survey is a Git development document outside the private package allowlist.

Existing package/isolation/distribution/desktop and G3/G4/G6/recovery regressions ran
in an isolated static source snapshot: 278 executed, 275 PASS, three existing skips,
zero failures/errors. All three skips require unconfigured real embedded-runtime
inputs; they are not counted as PASS. The prior accepted complete regression is
historical evidence, not a newly executed Production Final regression. No test was
changed or weakened. Bounded secret-pattern and local-link checks passed.
Validation output and package files remain ignored development artifacts.

## Primary sources

- [S3 pricing](https://aws.amazon.com/s3/pricing/),
  [Singapore S3 public catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/ap-southeast-1/index.json),
  [Singapore data-transfer catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/ap-southeast-1/index.json).
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html),
  [irreversible configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-configure.html),
  [conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html),
  [conditional-write enforcement](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes-enforce.html).
- [Azure immutability and billing](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview),
  [locked retention semantics](https://learn.microsoft.com/en-us/rest/api/storageservices/set-blob-immutability-policy).
- [B2 Object Lock](https://www.backblaze.com/docs/cloud-storage-object-lock),
  [B2 S3-compatible limitations](https://www.backblaze.com/docs/cloud-storage-s3-compatible-api),
  [B2 pricing](https://www.backblaze.com/cloud-storage/solutions/backup-and-archive).
- [R2 removable bucket locks](https://developers.cloudflare.com/r2/buckets/bucket-locks/),
  [R2 pricing](https://developers.cloudflare.com/r2/pricing/).

This document is advisory development evidence. It is not a release approval,
independent review, qualified custody registration or production admission signal.
