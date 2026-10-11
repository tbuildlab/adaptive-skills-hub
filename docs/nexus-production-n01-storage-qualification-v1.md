# N01 bounded primary/custody storage qualification v1

2026-10-11. This is a separate real storage protocol qualification under the
[explicit N01 budget receipt](nexus-production-n01-owner-budget-receipt-v1.md).
It does not repeat D03 or claim full N01, Owner consent, delegated E2E or release.

## Reuse and exact compatibility change

Native DynamoDB conditional immutable puts, strongly consistent reads and
two-item transactions implement the prepared/finalized primary transport.
Existing D03 S3 conditional append, complete version inventories, retained body
reads, predecessor/sequence and integrity checks are reused. The only existing
D03 implementation amendment is fixed instance codec/registration hooks with
unchanged v1 defaults; its 27 focused adversarial tests remain passing. The
versioned N01 adapter additionally validates complete v2 control rows and bound
configuration. It does not upgrade the old diagnostic registration or grants.

The storage-only enrollment contains exactly a CLOSED root and complete empty
revocation index. It has no Owner binding, context, source assertion, receipt,
grant, intent, claim or target. Every result is NONE; production membership is
rejected. The isolated input builder is imported only by qualification harnesses
and tests, never by the authority implementation.

Independent R root owns the exact new approvals registration and genesis.
The runtime is only the approved A Caller to R AppendRead chain. It cannot write
approval/fault namespaces, delete history, change retention or mutate IAM.
Normal objects are conditional immutable additions. Default Compliance retention
must be read back for every version relied on; no snapshot fallback exists.

## One bounded request

The new GitHub workflow triggers only on its exact request file and branch,
run_attempt=1, concurrency=1, eight-minute timeout and pinned official checkout.
It reuses the existing hashed SDK requirements. Native OIDC/STS credentials remain
only in SDK memory; no token/session/credential field is logged or retained.

`n01-storage-append-1` reserves **128 of the approved aggregate 512 DDB attempts**,
including crashes and its explicit fresh read-only OS process. The parent may
attempt at most 108 and child at most 20. This reservation is consumed in full
even if actual attempts are fewer or outcome unknown. Parent/child S3 caps are
650/250; actual configuration and R enrollment are counted separately. New
mutations retain each written version's payload, attempt and digest metadata;
there is no blind workflow rerun or write retry. No additional resource or cost
scope is introduced. The total model remains inside the approved USD 1.00 cap.

Actual service conditions to prove: exact partition access; ordinary UpdateItem
refusal; immutable duplicate put refusal; two-item PREPARED/finalized transitions;
stale head transaction refusal with no partial put; journal duplicate refusal;
independent approval mutation refusal. The harness injects acknowledgement loss
**after real service commit** for prepare, append and finalize. Injected loss is
labelled separately from native service behavior. Quarantine prevents resubmission;
reconciliation uses only reads. A fresh process federates anew and reads current
independent custody and primary; it restores no bearer authority and the semantic
root remains CLOSED. This does not claim forced machine power-loss qualification.

## Honest remaining gates

The v2 full Python snapshot regression completed with 1243 tests: 1239 PASS,
four retained environment-dependent skips, zero failures. Snapshot
`nexus-n01-preparation-cjjyi3_l`; retained log
`output/production-final/n01-v2-cjjyi3_l-full-regression.log`.
The later custody compatibility has eight new tests and 62 affected focused tests
passing; the live budget wrapper adds four meaningful bounds/redaction tests.
Repeated focused runs do not increase distinct test totals. The unchanged Node
D01 source retains the previously verified 366 PASS; no D01 ceremony is repeated.

Authenticated R root enrollment completed with six new versions, 3816 payload
bytes and 21 S3 attempts, including empty-prefix preflight, conditional put,
exact version/body and Compliance retention readback. The registration's body
SHA-256 is `7d4dbf19620c38e2e3633800f7b47243c801313dce63f292fcd20782a73911ba`.
The closed genesis body SHA-256 is
`7fe0fb527ce2c8bb519a0f837124bfce22ce8e964008f2aa0fc7b4f1c9b036db`.
The initial interrupted browser command had not begun: its durable own-operation
receipt was absent after terminal restoration; exact empty-prefix preflight
preceded the first actual writes. No ambiguous mutation was resubmitted.
Configuration plus enrollment S3 count is 33; DDB data-plane count is still zero
before the first native GitHub storage run. No production source was registered.

Live primary AWS storage status is PENDING until exact current run responses are read.
Initial GitHub run 38146922841 at source
`c9bfebd2312d07b69901bf20d4065931eba5c6d4` failed workflow YAML parsing before
any job existed; protected jobs read returned an empty list. The pip option's
colon was corrected by a block scalar and checked with the installed YAML parser.
There was no federation, data-plane call, partial write or unknown AWS outcome.
The same semantic request is retriggered only after that proven pre-execution
failure; its single 128-attempt reservation remains unchanged. No workflow rerun
of an executed request is used.
Qualified production source ingress, protected runtime revision/current writer,
independent enrollment/recovery, real Owner context/CONFIRM, nonce/revoke/consume
production provenance, N02, mediation and E2E remain separate required gates.
An SDK configuration, TEST_ONLY input or storage PASS cannot satisfy them.

```text
D03_STATUS = CLOSED_BOUNDED_DIAGNOSTIC_PROFILE_UNCHANGED
N01_STORAGE_LIVE_STATUS = PENDING_REAL_RUN
N01_LIVE_CLOSURE = INCOMPLETE
PRODUCTION_AUTHORITY = NONE
REAL_ADMISSION_ENABLED = NO
```
