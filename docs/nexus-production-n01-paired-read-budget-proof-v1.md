# N01 paired-read budget and exact head-8 continuation

Status: OFFLINE_PREPARATION_ONLY. REAL_ADMISSION=NO; N01/G3 remain INCOMPLETE.
No AWS operation, Owner LOGIN, enrollment, recovery, R binding or deployment is
dispatched by this analysis. Historical checkpoints and tests remain unchanged.

## Exact scalar provenance

The retained SDK lifecycle model makes 272 DynamoDB API attempts: 212 GetItem,
50 conditional PutItem and 10 TransactWriteItems. The original source proposal
uses 2; forward recovery 32; new source retirement 38; PREAUTH bootstrap 2;
the subsequent identity/context/decision/revoke sequence 198. The complete
closed call trace is hashed in the companion evidence. These are TEST_ONLY
simulation observations, not a new execution of FINALIZED checkpoints 7/8.

All eleven current-head observations are required at their original boundaries.
They cannot be cached across an authentication step, storage mutation or request.
Likewise, PREPARED/FINALIZED, immutable pre/post readback, source provenance,
generation/incarnation, retirement, consumption, revocation and replay checks
remain required. No safe cross-boundary deletion is claimed.

## Minimal native reuse

An opt-in paired path uses DynamoDB TransactGetItems with at most two fixed-table,
fixed-instance full-item reads. It keeps response cardinality/order, exact keys,
exact byte equality, existence checks, conditional writes and post-write readback.
An invalid, partial, reordered, corrupt, unavailable or unknown result quarantines;
there is no retry, BatchGetItem fallback, eventual consistency or durable cache.
The default scalar profile and all historical tests remain unchanged.

HEAD and its immutable checkpoint blob are observed atomically at each original
current-head boundary. Blob retention groups only reads belonging to that local
retention operation, and groups finalization material checks only within the same
finalization. No observation crosses a PREPARED/FINALIZED boundary. All 50 writes
and ten mutation transactions in the old model remain; its call count drops to
174. The new head-8 model separately compares every resulting primary item with
the scalar implementation and covers both CONFIRM and DENY, with no grant/effect.

[AWS transaction reads](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactGetItems.html)
provide atomic ordered observations. Transactional Get uses the existing GetItem
IAM permission, as documented in [transaction IAM](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis-iam.html).
No policy, principal, resource, dependency, table or paid plan is added.

## New head-8 qualification and worst-case proof

Both CONFIRM and DENY head-8 models use 174 attempts: 104 TransactGetItems,
10 exact reservation GetItem readbacks, 50 conditional PutItem and 10
TransactWriteItems. Every resulting primary item is byte-equal to the scalar
272-attempt model. Required phases are preserved:

| Phase | Scalar | Paired |
|---|---:|---:|
| Initial exact head/source proposal | 2 | 1 |
| Forward RECOVER 9 | 32 | 21 |
| New source retirement/enrollment 10 | 38 | 25 |
| PREAUTH bootstrap | 2 | 1 |
| Email / OTP / TOTP current-state gates | 6 | 3 |
| Context + challenge 11 | 70 | 46 |
| Display / decision / consume 12 | 68 | 43 |
| Revoke 13 + final independent observation | 54 | 34 |
| Total | 272 | 174 |

The mathematical bound does not assume a retained blob will be reused. For one
immutable material group of n unique bytes, the worst case is ceil(n/2) paired
pre-reads + n conditional puts + ceil(n/2) fresh post-reads. A commit with O new
objects and P snapshot pages therefore costs at most:

`O + 2*ceil(O/2) + (P+3) + 3*ceil((P+3)/2) + 6`

The final six are both current-head observations, both reservation reads and
both mutation transactions. The extra ceil((P+3)/2) rechecks all finalization
material. This bound assumes every blob in each operation needs a write, even
when it was already retained in the preceding operation; no integrity check is
removed to obtain it. For the fixed five-commit head-8 lineage, (P,O) is
(3,0), (3,2), (7,8), (9,4), (9,2), giving 21+25+47+44+40 = 177 attempts.
Twelve separately counted observations outside commits (proposal 1, pre-enroll
1, PREAUTH 1, three authentication gates, pre-challenge 1, display/decision gates
2, pre-decision 1, pre-revoke 1, final recheck 1) give **189 worst-case calls**.
The native hard cap remains 210, with 21 calls unallocated as safety margin.
No additional Owner request, new lifecycle or retry is funded by that margin.

This is a fixed lineage bound, not a claim that arbitrary 64-page ledger input
fits 210. Head 8 is pinned by exact bytes, its prior rows cannot be extended by a
request, source/context identifiers and reference hashes have closed schemas,
and the protocol adds only the fixed rows above. Both decision alternatives
retain identical page/object counts. The largest observed page is 23697 bytes,
well below the unchanged 65536-byte codec bound; fixed-length session IDs,
nonces, hashes and bounded timestamps cannot introduce an extra namespace or
split these pages. Unexpected state, excessive input or exhaustion quarantines;
partial failure never grants a fresh allocation or automatic redispatch.

The larger independent history produces 10312 S3 calls in each full new model.
Those are separately accounted in the unchanged aggregate S3 envelope. All
these observations are TEST_ONLY; no AWS or authentication operation occurred.

## Fresh lifecycle and preserved budgets

OWNER_ATOMIC_FORWARD_V1 accepts only the retained head 8 and old exact generation-3
process/artifact/source. It independently rereads protected RECOVER 3/5/7 history
without treating any old source as the new writer. Explicit forward RECOVER 9
uses epoch 6 and a fresh incarnation. Membership 10 retires old bindings and
creates distinct generation-4 identities. Old bytes and histories are preserved.
Neither the coordinator nor restart restores an Owner bearer or redispatches.

The longer history exceeded the old single writer-reader's 1000-call S3 budget
during the offline revoke model. The new profile uses the existing fresh bounded
gate_reader for the initial observation before beginning the write plan. Both
the observer and writer remain capped at 1000. This is planned separation before
dispatch, not an exhaustion retry. Both use the same native client and aggregate
counter; no counter is reset, no read/check is removed and no result is cached.

The new artifact reserves at most 210 additional DynamoDB attempts. The aggregate
allocation is 98 earlier conservative non-Owner attempts + 134 earlier Owner
attempts + 70 observed SDK-repair attempts + 210 = 512. Unknown/failure paths
consume their dispatched prefix and quarantine; they do not earn a replacement
allocation. No new process may reset the aggregate allocation.

The new native S3 reservation is 16000 reads/total calls, 240 writes and 8 MiB per
backend, inside the existing approved aggregate 50000 Tier-2 / 5000 Tier-1 / 64 MiB
envelope, together with all retained prior usage. Per-reader 1000 limits remain.
Operation/cleanup deadlines and Compliance retention remain unchanged.

At the rechecked Singapore public rates, two 400 KiB transactional reads require
at most 400 read request units per API attempt. Conservatively retaining the
original 1600-write-unit allowance for every one of all 512 attempts, and allowing
302 earlier attempts x 100 + 210 new attempts x 400 read units, increases the
original modeled pre-tax USD 0.712476 by USD 0.0089775. With the existing 20% tax
reserve, the envelope is USD 0.8657442, rounded up to USD 0.87, below the unchanged
USD 1.00 cap. This is an upper-bound model, not an invoice or billing hard cap.
[Public regional catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/ap-southeast-1/index.json).

## Remaining live gate

Review v2 expired at 2026-10-12T22:25:38.065+08:00. Its use in the offline model is
historical-clock fixture alignment only. No live review is extended, auto-approved
or reused outside its fixed interval. A new exact Owner-approved public-pin review
and independent R/artifact/process binding are required before activation.
The earlier TEST_ONLY POST/303/GET transport proof is retained; it does not qualify
the new active Owner controller. No human LOGIN is requested here.

See [budget evidence](../research/nexus-production-n01-paired-read-budget-evidence-v1.json).

## Final development checkpoint verification

The final executable snapshot passes 215/215 affected tests and the complete
1474-test regression: 1470 PASS, four unchanged environment skips, zero failures
or errors. Three real embedded-runtime inputs remain unavailable; one existing
Windows symlink fixture requires unavailable privilege. Neither class is counted
as PASS. Every changed executable source matches the tested snapshot byte for
byte after the repository's accepted LF normalization. Historical tests and
FINALIZED evidence are unchanged. Initial failed offline runs are retained and
not relabeled as successful qualification.

The bounded secret/import scan, historical codec AST-equivalence checks and
reproducible 249-file source package pass. Package SHA256:
`7748ce998375405ab92d2f0576b59b25511cfd563e5737c48dc71d5443ee883a`.
This is a development source package, not a Production Final release artifact.

The exact [pending Owner review v3](nexus-production-n01-paired-read-bounded-public-pin-owner-review-v3.md)
remains NOT_OBTAINED. No acceptance record, live review pin, deployment, new R
binding or human authentication has been created. N01 and G3 remain INCOMPLETE;
independent production review and final Owner release acceptance remain pending.
