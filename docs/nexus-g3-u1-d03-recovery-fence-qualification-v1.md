# G3 U1 D03 recovery fence qualification v1

Date: 2026-10-08. Documentary candidate qualification only.
Prerequisite: Phase 1 documentary validation passed; evidence is retained in
`state/g3-u1-overnight-20261008/phase-1-pass.json`.
Inputs: [Option C](nexus-g3-u1-option-c-deployment-qualification-v1.md),
[D05 R07](nexus-g3-u1-d05-production-authority-contracts-v1.md), and
[bounded OwnerContext](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md).

## Candidate and evidence boundary

Use the proposed protected DynamoDB ledger and a separate recovery-custody AWS
account containing an S3 Object Lock Compliance checkpoint journal. No resource
exists or is tested in this phase. Capability documentation is not effective
permission, configuration, retention or recovery evidence.

S3 retention protects object versions; it does not prevent newer versions or
delete markers. Compliance retention is finite, and the documented account-deletion
exception is outside its protection. Therefore Object Lock alone is not a
monotonic sequence service.
[Object Lock semantics](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html).
Conditional writes support create-if-absent; a delete marker can affect this check.
The candidate must forbid deletes and require conditional creation, then inspect
all versions rather than trusting an ordinary latest-object GET.
[Conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html).
DynamoDB transactional writes provide database atomicity with bounded transaction
size. Its ten-minute client-request-token window is not durable replay protection.
[Transaction APIs](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html).

## Trust and permissions

| Boundary | Writer/controller | Reader | Executor | Persistence and failure |
|---|---|---|---|---|
| N01 ledger and immutable record bodies | Restricted N01 role; independent administrator controls deployment/restore | N01 authoritative consistent read; recovery administrator | No database, backup, role or deployment access | Authority-account DynamoDB; incomplete read/transaction conflict denies; uncertain state quarantines. |
| Independent sequence journal | N01 narrowly scoped append role; recovery account administrator fixes resource/genesis/retention | N01 version-aware reader and recovery custodian | No access, assume-role or policy management | Separate-account S3, fixed bucket/region/prefix; missing permissions/history/retention closes release. |
| Recovery enrollment and epoch transition | Independent authenticated recovery administrator, excluded from executor and ordinary restore principal | N01 reads fixed registration | Cannot select resource, genesis, epoch or restored head | Protected recovery registration outside restored ordinary ledger; unprovable registration quarantines. |
| Retention/encryption/account continuity | Independent recovery custodian | Audited readback | No configuration, key deletion or account closure authority | Verified per-version retention plus readable history; loss of availability is denial, never history reset. |

The future append role may create the next fixed sequence key with a condition;
it may not delete, overwrite, shorten retention, change bucket policy/lifecycle,
change registration, close the recovery account or destroy encryption custody.
Recovery admin privileges remain a trust assumption; "separate account" does not
prove those administrators are excluded from executor control. Required credentials
are workload STS identity and recovery/admin authentication; none are accessed.

## Exact ordering and fencing protocol

Registered instance keys are fixed-width unsigned sequence names under a fixed
registered prefix, sequence 0 GENESIS followed by 1, 2, etc. The encoding uses
20 decimal digits and rejects values above signed 64-bit maximum. Epoch changes
do not reset sequence or create a new unlinked genesis. Checkpoint bytes and IDs
use unchanged D05 R07; S3 version IDs are custody metadata, not new body fields.

1. Close effect release. Under one per-authority serialized transition, compare
   current durable ledger generation/head and independent head; validate local
   deadlines, generations and full revocation/consumption indexes.
2. Durably prepare immutable transition records, transaction descriptor and exact
   after-state snapshot, with a PREPARED marker and conditional sequence reservation.
   Preparation is not authority. Another transition cannot skip or steal it.
3. Conditionally append the one next R07 checkpoint to the independent journal.
   Read back exact bytes, checksum, version and Compliance retain-until metadata.
   Check registered predecessor, resource, sequence and retained complete history.
4. Atomically finalize the ledger/control head to this witnessed transition using
   generation/head checks; retain the descriptor, after-state and tombstones.
   A positive acknowledgment or dispatch is forbidden until both stores agree.
5. Recheck all deadlines/context gates after fence completion. A consumed claim
   whose deadline elapsed cannot dispatch. Preserve consumption without retry.

No cross-service transaction is claimed. Final witnessed ledger/control commit is
the local authority linearization point, while the release gate remains closed
through witness/readback and bounded handoff. Every denial/consumption, invalidation,
revocation, intent, claim and result transition uses the same ordering. No independent
revoke queue can race past it. A crash or ambiguous predecessor interrupts service
instead of inventing a competing sequence. Multi-runtime leadership and fencing
must be proved before a live concurrent writer exists; a lease TTL alone is insufficient.

## Control snapshot encoding amendment

This specifies an additive protected-storage codec, not an eighth issuable D05
record. R07 and its ledger descriptor stay byte-compatible. `control_after_sha256`
is the plain SHA256 of canonical UTF-8 snapshot root bytes under the D05 canonical
rules. DynamoDB wire encoding, attribute order and implementation object repr are
never hashed. All digests are lowercase hex; no secret values enter snapshots.

The root's exact keys are `codec_version, authority_instance, authority_epoch,
incarnation, recovery_sequence, time_high_water_ms, inventory, pages`.
`codec_version` is `nexus.g3.control-snapshot.v1`. Epoch >=1, sequence/time >=0;
instance/incarnation use D05 token syntax. `inventory` is the sorted exact list
of these required namespaces, including empty namespaces:
`bindings, contexts, challenges, views, decisions, receipts, grants, revocations,
nonce_consumption, intent_indexes, claim_indexes, retirement, provenance`.
`pages` is a sorted array of page references with exact keys
`namespace, first_key, last_key, row_count, page_sha256`; each nonempty page has
1..64 rows, exact NFC keys <=512 characters and contiguous nonoverlapping key
ranges within its namespace. Empty namespaces have no pages. Root exceeds 64
pages or 65536 canonical bytes: close and require a separately versioned codec;
do not silently truncate or reinterpret the bounds.

A page's exact keys are `codec_version, namespace, rows`, with version
`nexus.g3.control-page.v1`; row exact keys are `key, value_canonical_utf8,
value_sha256`. Keys sorted/unique; value text is strict canonical JSON <=16384
UTF-8 bytes; digest hashes its exact UTF-8 bytes. Page hashes cover canonical page
bytes. Root membership commits to every page and every row; namespace omission,
duplicate/overlap, absent page or mismatched row/hash quarantines. Preserve all
historical revocation/nonce/claim tombstones; no compaction silently drops them.

The root/page byte encoding is DEFINED, but the *semantic row schemas* and proof
that the inventory covers every future authoritative storage surface are not yet
qualified. Each namespace needs a closed versioned row schema tied to the N01
store design; generic arbitrary values are not accepted for reopening. This is an
explicit implementation-preparation gap, not permission to use a caller-defined
snapshot. Size growth/compaction and leadership recovery also remain open. The
composition is therefore not yet sufficiently qualified for a production adapter.

## Crash, restore and replay dispositions

| Interval / fault | Required disposition |
|---|---|
| Before durable prepare | No authority; later retry requires an unconsumed, current lineage and a new qualified operation. |
| After prepare, before S3 append | QUARANTINE; inspect independent history and prepared transition. No effect or unilateral rollback to release-open. |
| S3 timeout/unknown write | QUARANTINE; exact version-aware reconciliation only. No different payload at that sequence. |
| After witness, before ledger finalize | QUARANTINE; independent recovery may reconcile exact retained descriptor/after-state, then retire pre-restart authority. |
| After final commit, before acknowledgment | Existing consumed state persists; caller outcome UNKNOWN. No second grant/claim/effect. |
| After claim, before/after provider call with uncertain result | Consumed UNKNOWN attempt; never automatic redispatch. |
| Restored older table, missing page/body/descriptor or divergent hash | QUARANTINE. Never select an older matching journal prefix or advance journal from restored data. |
| Fork, extra object version, delete marker, sequence gap, inconsistent listing | QUARANTINE; complete version-aware paginated enumeration required, not a single cached list. |
| Retention expiry/lifecycle removal, unavailable key/account or history | QUARANTINE; retention continuity must cover the entire relied-on history. No automatic fresh genesis. |

A recovery ceremony verifies the latest complete independent history and exact
ledger/control state, then independently authorizes RECOVER with increasing epoch
and a fresh incarnation, continuous sequence and nondecreasing trusted time.
Retire pre-restart contexts/views/grants/intents; preserve all terminal consumption
and results. A restored executable cannot resume merely by presenting the old
incarnation string. D04 must exclude old runtime/deploy/restore roles and alternate
dispatch routes. R07 alone cannot prove a trusted clock or current executable.

## Qualification remaining

Future isolated tests need actual two-account permissions, retention readback,
conditional-write races, paginated version history, crash points, stale restoration,
clock regression, leader exclusion and retention rollover/size limits. These require
Owner authorization, resources and credentials and are not run. Root/page codec
test vectors may be prepared offline; semantic inventory proof cannot be substituted
with a hash-only test. No claim of VERIFIED enforcement is made.

```text
D03_RECOVERY_FENCE = CONDITIONAL
RECOVERY_CHECKPOINT_STORAGE = SEPARATE_ACCOUNT_S3_OBJECT_LOCK_COMPLIANCE_JOURNAL_CANDIDATE
CONTROL_SNAPSHOT_ENCODING = DEFINED
CONTROL_SNAPSHOT_SEMANTIC_ROWS = BLOCKED_PENDING_CLOSED_N01_STORAGE_SCHEMAS
ROLLBACK_DETECTION = DEFINED_CONDITIONAL_ON_COMPLETE_INDEPENDENT_HISTORY
FORK_GAP_DETECTION = DEFINED_VERSION_AWARE_FULL_CHAIN_CHECK
RECOVERY_QUARANTINE = REQUIRED_DEFAULT_CLOSED
D03_IMPLEMENTATION_READY = NO
D03_LIVE_QUALIFICATION_REQUIRED = YES
EFFECTIVE_OBJECT_LOCK_ENFORCEMENT = UNKNOWN
REAL_ADMISSION_ENABLED = NO
GRANTS_REVOCATIONS_ISSUED = 0
PROVIDER_EXECUTIONS_ADDED = 0
FAIL_CLOSED_BOUNDARY = PRESERVED
```
