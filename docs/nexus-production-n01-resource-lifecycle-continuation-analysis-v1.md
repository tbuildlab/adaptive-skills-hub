# N01 resource/lifecycle continuation: retained-evidence disposition v1

Disposition: **HOLD_NO_RECREATION / DETERMINISTIC_CONTINUATION_NOT_PROVEN**.
This is documentary analysis only. It is not an Owner authorization package,
resource provisioning plan, authentication readiness result, or PREAUTH permit.
REAL_ADMISSION remains NO. Implementer review does not constitute independent
production security acceptance.

## Scope and baseline

Baseline branch: `nexus-v2-production-qualification`.
Baseline HEAD: `a7b2ec93c31f19a398f7662fe3ad601d39b73d7c`.
The working tree was clean before this analysis. Existing implementation, tests,
approval packages, checkpoints, and QUARANTINE evidence are not modified.

The prior native A observation at `2026-10-13T12:01:04.058716Z` reported
ResourceNotFoundException for the original table and cleanup schedule. The cause
and exact deletion time are NOT_ESTABLISHED. This analysis does not assert that
the scheduled cleanup executed, or that no unexamined backup exists.

Original identities:

- Table: `arn:aws:dynamodb:ap-southeast-1:175880707430:table/NexusG3AuthorityV1`.
- Schedule: `arn:aws:scheduler:ap-southeast-1:175880707430:schedule/NexusG3QualificationCleanupV1/NexusG3QualificationDeleteTableV1`.
- R bucket: `nexus-d03-custody-862902859484-ap-southeast-1-v1`.
- Audited prefix: `qualification/n01/v1/`.
- Authority instance: `g3-n01-qualification-v1`.

The approved continuation v2 explicitly requires HOLD when the original table is
absent. Its approval cannot authorize a replacement, hydration, or replay.
The v6 public-pin window and 21:45 Malaysia operational cutoff are not used to
authorize activity in this analysis. No new review generation/window is proposed.

## What R independently retains now

Read-only native R CloudShell observation completed at
`2026-10-13T13:13:32.000173Z`. Native STS identified account `862902859484`, root.
No credentials were inspected or exported. SDK authentication remained internal.

The complete version inventory for the exact prefix contained 78 versions:

| Class | Inventory | Current content verification |
| --- | ---: | ---: |
| Sequential normal journal, sequences 0 through 10 | 11 | 11 |
| Normal addressed objects | 46 | 46 |
| Approval/registration objects | 21 | 3 |
| Total | 78 | 60 |

The 46 normal objects comprise 11 commit descriptors, 11 snapshot roots,
16 distinct snapshot pages, four source-enrollment bodies, and four source
observations. Shared pages are counted once. Two complete version inventories
matched; no delete markers or non-latest versions were observed in this prefix.
No other bucket/prefix or unexamined backup is covered by this result.

All 11 journal bodies, domain-separated checkpoint/descriptor identities,
predecessor references, sequence numbers, root/page addresses, page row digests,
and snapshot/checkpoint epoch/incarnation/high-water bindings were checked during
the native read. All 57 normal versions were read. This is structural byte and
lineage verification; it is not a fresh production source/provenance admission
or a reconstruction of the primary transaction outcome.

For each of the 60 read versions, the native GetObject response returned the exact
version identity, content length, COMPLIANCE mode and a future retain-until date.
Observed retain-until range: `2026-10-18T14:20:20.712Z` through
`2026-10-20T06:27:45.251Z`. Each version's exact date is in the readback evidence.
The remaining 18 approvals are INVENTORY_ONLY: their current bodies, digests and
retention headers were not read in this bounded analysis. Historical approval
records remain historical evidence; unread content is not counted as verified.

Bucket Object Lock remains enabled with seven-day Compliance default retention.
The bucket policy was read without mutation; canonical policy SHA256 is
`63987cbec2dad09c2cd756632e4c834eb83b76856794aa949c4a510a93a12ec8`.
This is not a new qualification of all IAM policies or the production reader.
GetObject exposes retention headers, but the accepted production reader's
separate GetObjectRetention verification was not executed here. See
[AWS GetObject response specification](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html).

The selected approvals actually read were storage-registration-v2, the atomic-v1
current-source registration, and recovery-atomic-v1 authorization for sequence 9.
The inventory has no auth-attempt-forward enrollment or sequence-11 recovery
authorization. It does not prove that no such object exists outside this prefix.

Latest R journal member is checkpoint 10, transition INVALIDATE, epoch 6:

- ID: `nexus.g3.production.recovery-checkpoint.v2:1f2b3a821551c19b1d8c98f37ad1ef957366349175d04d7fcb38841f8fa4f4b5`.
- Body SHA256: `cee49468377d9e5068c1bb07bd1faffeaa831554d06e817987899aafd0a2e7d0`.
- Incarnation: `n01-owner-2f71543e6e206736d281aefb62a328af`.
- Control root SHA256: `e7ecbfa847ad0d62673335857379e75a3e5902aeb4c1ea0b657f80541a86ce99`.
- Configuration SHA256: `3632c49345ea111aa992b27a8645e44f479fe7685c98ac04515147891fd0a2d1`.

Its 24 control rows include the old atomic source/binding/registration generation
4, three retired predecessor bindings, recovery witnesses, root revision 11 and
revocation generation 1. There is no Owner context, pending challenge, decision,
grant or consume row in this snapshot. Historical CURRENT does not mean a current
live controller or permission to restore authority. The associated public-pin
review generation 4 is expired. The cached metadata appendix records all 11
checkpoint bodies, exact record references/high-water values, and lifecycle
generations without modifying remote history or creating a ledger.

## Why the retained bytes are insufficient for authority-ledger continuation

The accepted commit order in `ash/g3_n01_owner_persistence.py:185` is:
primary prepare; independent object/journal append; primary finalize; separate
fresh current-head observation. The primary implementation in
`ash/g3_primary_ledger.py:127` writes reservation PREPARED and HEAD.pending in a
DynamoDB transaction. Its separate `finalize` transaction at line 190 writes
reservation FINALIZED and HEAD.READY, removing pending. The R append does not
contain a receipt of that later primary transaction. DynamoDB transaction
atomicity covers its transaction items, not a separately executed S3 append;
see [AWS transaction API documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html).

Two protocol-compatible histories have the same independently retained R bytes:

| History | R journal/object bytes | Lost primary outcome |
| --- | --- | --- |
| Prepare -> append checkpoint 10 -> crash before finalize | Exact checkpoint 10 and associated snapshot | HEAD still PREPARED, reservation 10 PREPARED |
| Prepare -> append checkpoint 10 -> finalize | Same exact checkpoint 10 and associated snapshot | HEAD READY, reservation 10 FINALIZED |

Furthermore, after a finalized checkpoint 10, a primary-only preparation for the
next sequence could occur before its first R write. The observed R inventory
cannot exclude that pending/unknown primary outcome. These are counterexamples
to uniqueness, not assertions that either crash actually occurred.

Existing local native evidence reports checkpoint 9/10 FINALIZED. That historical
report is preserved. It does not provide an independently retained full primary
image or a protected no-pending witness at the later table-loss boundary. The
retained recovery row state WITNESSED refers to recovery evidence, not the primary
reservation phase FINALIZED. Inventing a FINALIZED reservation, deleting an
unknown pending reservation, or replacing HEAD.phase from journal membership is
therefore prohibited. A quarantined archival copy could preserve R history, but
would not satisfy the accepted current-primary authority contract.

The native aggregate budget is also process-local (`_BUDGET` in
`ash/g3_n01_native_transport.py:21`). Its leases, DDB/S3 attempts, writes and byte
charges are not in the retained checkpoint, descriptor or control-row schemas.
R bytes cannot recover exact historical attempt totals, including failed reads,
unknown outcomes and non-journal operations. Unknown totals are not zero.

Required missing evidence is a protected, complete primary terminal-state witness
(exact HEAD, every reservation phase/pending state, retained material and a
no-later-preparation boundary), plus authoritative cumulative usage accounting.
No qualified witness/backup meeting those requirements was established in the
audited evidence. This analysis does not claim that all possible backups were
searched or that safe recovery can never be designed under a separate contract.

## Preservation and decision algorithm

This is a documentary decision procedure, not an executable migration:

1. Bind the exact existing resource identities and baseline commit. If either
   original resource is absent, enter HOLD before changing policy or state.
2. Inventory exact R versions; check complete contiguous lineage, identities,
   snapshot material and retained dates. Any ambiguity, gap, fork, mismatch or
   expired required evidence is HOLD.
3. Require independent terminal primary and cumulative accounting witnesses.
   Require their exact consistency with the R head and all historical outcomes.
   Missing, partial, contradictory or unknown evidence is HOLD.
4. Only if uniqueness is proven could a separate resource-only Owner review define
   exact replacement identity, immutable migration inventory, generation/epoch
   mapping, transaction preconditions, counters, retention and costs. That
   precondition fails here. No mapping, replacement or hydration is authorized.

Replacement account/region/table ARN, creation identity, schedule, role, resource
generation and migration ID: **NOT_SELECTED / NOT_QUALIFIED**. Reusing the old
table name/ARN would not prove the same table incarnation. The current adapters
pin the original identity and have no accepted deleted-primary migration method.
The existing head-10 forward-retirement seam requires qualified current primary
state; it is not an empty-table bootstrap. `enroll_genesis` only accepts genuine
GENESIS/sequence 0, not checkpoint 10. There is no admissible shortcut.

Rollback behavior is HOLD without writes: retain all R versions and local history;
do not lower the head, reset sequence/generation/epoch or budgets, overwrite the
terminal controller, promote old bindings, recreate genesis, or redispatch an
unknown outcome. Since no migration starts, there is no rollback transaction.
Any future authorized migration would have to quarantine partial results rather
than erase them or undo independently retained history; this document does not
define or authorize that future transaction.

Checkpoint 0-10 IDs, digests, epochs, incarnation identities, timestamps and source
references are preserved. In particular 7/8/9/10 are not replayed. Existing
QUARANTINE evidence remains at
`research/nexus-production-n01-preauth-timeout-closed-evidence-v1.json`:
closed-log SHA256 `d76aaa8d2ced12b7060fdc2f7f0173c76619f96056425a43cd1538a29260ecb9`;
diagnosis-record SHA256 `dc05cc8880f28be643d5165c774d6dbb37393d08f0ef3b83c40aafc1c944cd76`.
That runtime terminal state is not replaced by the older snapshot's CURRENT labels.
No counter, budget, generation or authority state is reset by this analysis.
Exact lost runtime totals remain UNKNOWN, never manufactured as an initializer.

## Calls, cost and retention consequences

Exact native analysis operations:

| Operation | Calls |
| --- | ---: |
| S3 ListObjectVersions | 2 |
| S3 GetObject | 60 |
| S3 GetBucketPolicy | 1 |
| S3 GetObjectLockConfiguration | 1 |
| S3 total | 64 |
| STS GetCallerIdentity | 1 |
| DDB data-plane | 0 |
| Cloud writes / provisioning / replay | 0 |

Retrieved S3 payload bytes: 128,363. SDK retries were disabled (one total attempt).
Cached metadata analysis/download did not reread S3 or reset any native counter.
Charge these 64 calls against the existing reserved R-admin 64: this reserve is
now exhausted, not renewed. Existing runtime S3 allocation 15,936 and total 16,000
stay unchanged; neither is a new allocation. The aggregate historical envelopes
5,000 Tier-1 / 50,000 Tier-2 / 64 MiB / 0.25 GB stay unchanged.

Approved conservative prior DDB charge 348, proposed continuation cap 189 and
cumulative cap 537 remain recorded. New DDB charge is zero. The arithmetic
`537 - 348 = 189` is an approved allocation, not proof of reconciled live remaining
usage and not permission to initialize a replacement counter. No live attempt is
eligible until historical known/unknown costs and counters are reconciled.

Public Singapore AWS price catalogs were read without credentials or resource
operations. Tier-1 is USD 0.000005/request; Tier-2 USD 0.0000004/request.
Using all 64 calls at the higher Tier-1 price, 128,363 bytes at the conservative
USD 0.12/decimal GB outbound rate and a 20% tax reserve gives
USD **0.000402484272**, rounded upward to **USD 0.001** for this request/payload
model. This is inside the existing reserve, not added to the authorization.
It is not the exact account invoice or a bound on unrelated account costs;
actual invoice remains UNKNOWN. No credits or free-tier qualification are assumed.
Selected prices, catalog digests and model scope are in the cost evidence.
Sources: [regional S3 catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/ap-southeast-1/index.json),
[regional AWS transfer catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/ap-southeast-1/index.json).

New resource storage/write/retention impact is exactly zero. Existing S3 retention
and ongoing storage billing continue on their previous terms; no deletion,
extension, new version or irreversible retention was applied. Compliance expiry
does not itself prove automatic deletion. New-resource DDB/S3 operation counts,
cost and retention for a future migration are **UNDETERMINED_NOT_AUTHORIZABLE**,
not a zero-cost estimate: no valid reconstruction algorithm passed the prerequisite.
The N01 cumulative USD 1.00 inclusive ceiling is not enlarged.

## Evidence and stop boundary

Native readback: `research/nexus-n01-resource-continuation-r-readback-v1.json`.
Canonical SHA256 (excluding its `report_sha256` field):
`6d9b3196d992f7d9f85eb2a4ad96c549283965d87708c16a4aae8bfea6a0b1c7`.
Inventory SHA256: `2d00fb14d4a1d099584aecc3f2883eab1355278c2213c0b9d292a3ee8f16ddc7`.
Cached schema/checkpoint appendix: `research/nexus-n01-cached-retained-schema-analysis-v1.json`.
Canonical SHA256 (excluding its `canonical_sha256` field):
`dce612f12e4ae4167b0599e3fe6e4a1241eda8ae948d8f5093edd66dbe3fafdd`.
These metadata seals establish evidence identity, not Owner approval or authority.

No source/test bytes changed; no new implementation regression is claimed.
Previously recorded regressions remain historical offline results, not live
continuation qualification. Local validation here checks metadata digests,
lineage/cached checkpoint identities, historical-byte preservation and MANIFEST.

**Stop here.** No Owner review package is offered for approval because deterministic
continuation has not been proved. No new resource, ledger, lifecycle binding,
PREAUTH, LOGIN, OTP/TOTP, or authentication readiness authorization is included.
D01/D03 closure and G4/G6 preparation statuses remain unchanged; N01/G3 remain
incomplete, REAL_ADMISSION=NO, and fail-closed behavior is preserved.
