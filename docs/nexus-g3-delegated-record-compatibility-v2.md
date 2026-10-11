# G3 delegated record compatibility v2

2026-10-11. Additive implementation of the accepted
[Delegated Executor policy](nexus-g3-delegated-executor-authority-policy-v1.md).
Historical [D05 v1](nexus-g3-u1-d05-production-authority-contracts-v1.md) bodies,
IDs, tests, eight-gate structural layout and dispositions remain unchanged.

## Exact versioned difference

The seven production record domains use `.v2`. Each body adds exactly
`authority_mode=DELEGATED_EXECUTOR`, the protected configuration reference
`authority_config_sha256`, and
`d04_historical_status=UNQUALIFIED_NOT_A_RELEASE_GATE`. All production record
references in that lineage are v2; mixed v1 anchors are rejected. Unchanged
Subject, grant, revocation, proposal and full effect material remain v1 where
their accepted contracts are unchanged. An executor never replaces Owner Principal.

An ADMIT_PENDING intent or CLAIM has exactly seven mandatory PASS facts, in the
original order excluding only historical D04: D01, D03, TECHNICAL, TASK, HOST,
G1 and G2. Missing, reordered, duplicate, extra, UNKNOWN, FAIL or CONDITIONAL
facts deny that positive *shape*. No D04 PASS is inserted, asserted or inferred.
Expiry, exact revocation-read/grant binding and closed field sets are retained.

The codec reuses pure v1 validators through a throwaway shape lens for unchanged
fields of non-positive records. This lens changes only production reference
domain suffixes and schema version; it never changes hashes, Principal or material.
It is never returned, stored, hashed as evidence, used to authorize, or passed to
the historical eight-gate positive validator. Actual IDs hash the actual canonical
v2 bytes in the actual v2 domain. It does not migrate existing retained v1 history.

## Qualification limit

`ash/g3_delegated_record_codec.py` returns UNTRUSTED metadata with authority NONE
and semantic validation NOT_PERFORMED. A supplied mode/config digest is not
protected registration. The v1 control snapshot reader, transition protocol,
primary transport and diagnostic fence do not silently accept v2. Their explicit
versioned integration and actual independent source/custody qualification remain
required before any authoritative positive operation.

Twelve unique structural/adversarial test methods pass. Their examples are test
fixtures, including shape-valid positive bodies; none is production authority,
source qualification, Owner CONFIRM, independent review or real admission.
The original v1 tests and fail-closed G4/G6 boundary remain required.

```text
V1_CONTRACT_CHANGED = NO
D04_HISTORICAL_STATUS_CHANGED = NO
DELEGATED_V2_SHAPE_VALIDATION = PASS
DELEGATED_V2_PROTECTED_RUNTIME_QUALIFICATION = NOT_PERFORMED
REAL_ADMISSION_ENABLED = NO
```
