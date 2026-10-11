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

The primary AWS storage result is recorded below; it is not production authority.
Initial GitHub run 38146922841 at source
`c9bfebd2312d07b69901bf20d4065931eba5c6d4` failed workflow YAML parsing before
any job existed; protected jobs read returned an empty list. The pip option's
colon was corrected by a block scalar and checked with the installed YAML parser.
There was no federation, data-plane call, partial write or unknown AWS outcome.
The same semantic request is retriggered only after that proven pre-execution
failure; its single 128-attempt reservation remains unchanged. No workflow rerun
of an executed request is used.

## Actual primary storage result

Run [38147046486](https://github.com/TDY0225/adaptive-skills-hub/actions/runs/38147046486),
job 114492492002, source `23b29d92209bb37cfc8b9c36d55fc32a3ce69af4`, completed
successfully. Authenticated connector log read resolved 169 exact SDK operation
events: 52 DDB and 117 S3, including the fresh process. Parent DDB count 50,
child count 2; parent S3 count 95, child 22. Native federation was verified
separately for each process. Sanitized events and receipt are retained in
[observed evidence](../research/nexus-production-n01-storage-observed-evidence-v1.json).

Native refusals: wrong partition and ordinary UpdateItem AccessDeniedException;
duplicate primary put ConditionalCheckFailedException; stale two-item transaction
TransactionCanceledException with a strong read proving no partial put; duplicate
journal PreconditionFailed; approval mutation AccessDenied. Prepare, append and
finalize each received actual service success before injected ACK loss. No
transaction or journal write was repeated; fresh independent read reconciliation
resolved the exact sequence-1 head. A new OS process performed read-only checks,
returning NONE with the semantic root CLOSED.

Parent conservative DDB write payload bound 30988 bytes; new S3 written payload
5421 bytes. Configuration/enrollment plus run S3 attempts total 150. Aggregate
DDB actual is 52; reserve remains 128 including all crash/restart contingencies.
Invoice is UNKNOWN; no resource/permission/cost envelope was expanded.

The explicit N01 recovery integration used two separate requests:
PREPARED (reserve 64 DDB attempts), then independent R registration/approval and
RECOVER append, then FINALIZED (reserve 32). Current protected custody is required;
old generation/incarnation/reference denies. Every root stays CLOSED, all
registration purposes stay TEST_ONLY and no grant/Owner authority is restored.
Total reserved DDB after both phases is 224 of 512; original D03 recovery is not
repeated. The approvals remain outside A write permission. This qualifies the
N01 integration seam only, not production source ingress or consent.

Actual PREPARED run
[38148000136](https://github.com/TDY0225/adaptive-skills-hub/actions/runs/38148000136)
at `05669ce4260e8a4df8a1cdd6785f1ede7a624707`, job 114495304426, succeeded:
17 DDB and 32 S3 attempts. It stopped at a durable reservation without appending
RECOVER or claiming authority. R root independently verified all thirteen exact
retained predecessor/candidate objects and complete version inventories, then
conditionally wrote generation-2 registration, exact recovery authorization and
sequence-2 checkpoint. Three new versions / 2283 payload bytes / 41 S3 attempts;
each exact version/body and Compliance retention was read back. No IAM, table,
retention or resource setting was changed.

Actual FINALIZED run
[38148321004](https://github.com/TDY0225/adaptive-skills-hub/actions/runs/38148321004)
at `94d70757724036c4f4918031dc8854ef4ae038d0`, job 114496259803, succeeded:
11 DDB and 60 S3 attempts. Strong primary read confirmed FINALIZED and exact
independent sequence-2 checkpoint body SHA256
`52dd16d2303656eec0f3c6413e5337f03cb1e64531b7acf8ace920bcaf89ad41`.
Old generation-1 registration could not read the current history; the old
checkpoint could not satisfy primary recovery. A fresh transport still returned
NONE; epoch 2 / `n01-storage-incarnation-2` / CLOSED were verified. No Owner,
bearer or grant was restored and automatic redispatch remained DENY. The native
events and separate R observation are retained in
[recovery evidence](../research/nexus-production-n01-recovery-observed-evidence-v1.json).

Aggregate N01 data-plane count before the Vercel runtime phase was 80 DDB / 283 S3 (including the
earlier configuration/enrollment scope). DDB reserved remains 224 of 512.
The separately bounded Vercel read-only runtime phase reserves another 16,
bringing reserved aggregate to 240 / 512. Existing model remains below USD 1.00;
actual invoice remains UNKNOWN. Source/Owner/revoke/consume provenance is not
qualified by this storage-only recovery result.
The [native Vercel read-only qualification](nexus-production-n01-vercel-runtime-qualification-v1.md)
subsequently passed in its bounded TEST_ONLY/NONE profile: 2 DDB / 38 S3 actual
reads for the observed response, plus two earlier executed responses whose exact
SDK counts were not observed. Verified aggregate is 82 DDB / 321 S3 and conservative
upper bounds are 86 DDB / 521 S3. Reserved aggregate remains 240 / 512. None of
these native reads creates a qualified Owner/source/receipt/grant membership.
Qualified production source ingress, protected runtime revision/current writer,
independent enrollment/recovery, real Owner context/CONFIRM, nonce/revoke/consume
production provenance, N02, mediation and E2E remain separate required gates.
An SDK configuration, TEST_ONLY input or storage PASS cannot satisfy them.

```text
D03_STATUS = CLOSED_BOUNDED_DIAGNOSTIC_PROFILE_UNCHANGED
N01_STORAGE_LIVE_STATUS = QUALIFIED_STORAGE_ONLY_NOT_PRODUCTION_AUTHORITY
N01_RECOVERY_INTEGRATION = QUALIFIED_TEST_ONLY_NONE_NEW_EPOCH_INCARNATION
N01_LIVE_CLOSURE = INCOMPLETE
PRODUCTION_AUTHORITY = NONE
REAL_ADMISSION_ENABLED = NO
```
