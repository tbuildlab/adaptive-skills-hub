# G3 U1 D03 offline semantic closure v1

2026-10-08. Additive closure of the explicitly open semantic row gap in
[D03 qualification](nexus-g3-u1-d03-recovery-fence-qualification-v1.md).
Inputs: [closed N01 state](nexus-g3-u1-n01-protected-control-state-v1.md),
[target/dispatch registry](nexus-g3-u1-target-dispatch-contracts-v1.md),
[unchanged D05 R07](nexus-g3-u1-d05-production-authority-contracts-v1.md).
Historical NO/CONDITIONAL findings remain historical; no AWS calls are made.

## Snapshot and protocol closure

The sixteen closed state families populate all thirteen original namespaces.
Root/recovery/registration/source have distinct `provenance` discriminators.
Unknown rows are rejected. Each record/assertion reference resolves retained exact
bytes; inventories must cover every authorizing membership/index, not all arbitrary
orphaned blobs. An omitted required singleton, nonce/claim/tombstone membership or
incomplete revocation index quarantines. Runtime caches and PREPARED transport
markers can only restrict release; they cannot create authoritative state.

Encoding remains `nexus.g3.control-snapshot.v1` / `nexus.g3.control-page.v1`.
Namespace/key ordering is UTF-8 lexicographic, canonical values strict D05 JSON.
Rows/page hashes and full page refs cover exact bytes. Greedy page grouping obeys
64-row/65536-byte bounds; 64-page root and 4096-row total bounds are hard stops.
Empty namespace inventory entries are mandatory. Ordinary database wire format,
dictionary insertion order and unvalidated generic JSON do not enter the hash.

For transition n: root records n and checkpoint predecessor n-1; recovery history
contains checkpoints strictly earlier than n. Snapshot hash -> exact D05 ledger
descriptor hash -> unchanged R07 bytes/ID. Including the current checkpoint ID
inside its own `control_after_sha256` input is forbidden. Current finalized pointer
must be derived from and equal the independently witnessed R07 at n; a conflicting
physical pointer quarantines. The next transition records n as prior recovery
history. This resolves self-reference without changing any R07/ledger body.

Each T1-T9 has one conditional per-authority PREPARED reservation, exact before
head/generations and full candidate after-state. All release stays closed until
append/readback and finalization. Another worker cannot skip, steal or finalize
a different reservation. Every finalize checks the still-current reservation,
predecessor and payload digest. Multi-writer deployment must prove stale leader
exclusion and consistent latest-head reads; lease expiry alone is insufficient.

Independent keys are fixed registered prefix plus 20 decimal digits for global
sequence; epoch never resets it. No fork, gap, duplicate version, delete marker,
missing ancestor, unverified retention or alternate genesis is tolerated. Latest
complete version-aware history is authoritative; a restored ledger may not select
an earlier matching prefix. Object Lock preserves versions, not sequence authority
by itself. The separate account, conditional-create policy, complete listing,
custody and retention/encryption controls remain deployment assumptions.

## Required crash/recovery outcomes

| Observation | Outcome and reconciliation |
|---|---|
| Before ledger prepare | No candidate authority or externally usable record; failed request has no effects. |
| After ledger prepare / before independent append | QUARANTINE. Exact retained reservation only; do not discard consumed after-state and reopen from an earlier head. |
| Before independent append fails definitively | Negative-only close; recovery reconciles the reserved transition under separate authorization, without new payload or sequence reuse. |
| Unknown checkpoint acknowledgment | QUARANTINE; enumerate/read back exact sequence/version/bytes/retention, never assume failure and append an alternative. |
| After append / before ledger finalize | QUARANTINE; reconcile exact witnessed descriptor and after-state, then RECOVER with a new incarnation. Missing prepared bytes cannot be reconstructed from caller claims. |
| After finalize / before caller acknowledgment | Durable consumption remains. Caller UNKNOWN; no second receipt/grant/claim or automatic provider retry. |
| After claim / before handoff or result | Claim remains consumed; UNKNOWN if effect cannot be excluded. No redispatch, including after restart. |
| Old ledger/control snapshot restored | Independent latest history mismatch detects rollback; QUARANTINE, even if hashes of the old prefix are valid. |
| Fork/gap/missing page/body/history/expired retention | QUARANTINE. An unavailable checkpoint cannot be replaced by a fresh GENESIS. |
| Registration revision missing/changed | Unclaimed lineage RETIRED; missing retained registered bytes is corruption and QUARANTINE. |

Revoke and claim occupy the same reservation stream. Revoke finalized before T6
denies intent; after intent but before T7 denies claim. If T7 finalized first, its
consumption survives subsequent revoke, crash and ambiguous acknowledgment.
A later revoke cannot erase an already claimed effect or generate retry authority.
Uncertain revoke finalization cannot acknowledge success or permit a new claim.

Recovery requires independent authenticated recovery authorization, latest complete
checkpoint history and all referenced bytes. RECOVER raises epoch, creates a fresh
incarnation, preserves global sequence and nondecreasing trusted time. Retire all
pre-restart contexts/views/current grants/unclaimed intents; retain decisions,
receipts, nonce/grant/revocation/claim consumption and UNKNOWN outcomes. Restored
pending OwnerContext cannot reuse its former token or refresh itself. D04 must
exclude old deployments and restore principals from dispatch after recovery.

Page rollover is deterministic repacking under the same codec, with old immutable
pages/history retained. It never drops retired identities or terminal tombstones.
At capacity, stop until an independently reviewed versioned migration; no unsafe
truncation or unexplained archive omission. Checkpoint/version retention must
cover the relied-on authority lifetime. Custodian continuity, timely retention
renewal, key readability and account survival are mandatory; if unproved, close
before expiry. No claim of infinite retention or actual effective S3 controls.

## Readiness boundary

The offline protocol and semantic input specification are now defined; isolated
codec/model/fake adapters may be implemented and tested. Real D03 enforcement
remains UNVERIFIED and CONDITIONAL. A deployment later needs two-account effective
permissions, conditional append races, version-aware listing, Object Lock readback,
retention continuity, restoration/crash/leader exclusion and trusted clock tests.
No live adapter or positive authority service is authorized by this closure.

```text
D03_OFFLINE_PROTOCOL = DEFINED
D03_DEPLOYED_ENFORCEMENT = UNVERIFIED
D03_RECOVERY_FENCE = CONDITIONAL
D03_IMPLEMENTATION_READY = YES
CONTROL_SNAPSHOT_SEMANTIC_ROWS = DEFINED
REAL_ADMISSION_ENABLED = NO
```
