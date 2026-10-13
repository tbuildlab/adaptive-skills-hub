# N01 v6 acceptance and resource HOLD checkpoint

The Owner explicitly approved lifecycle amendment v2 canonical SHA256
`0673285cf0739b1a17cc0fee35f616718246c81cda673a1bb58def452b9793f5`,
including v6 public-pin canonical SHA256
`ae081f017a1036e33e40b06bda6d6a8020526739bafbf75ad40f859c73549df1`
and its conditional existing-environment time adjustments. Separate acceptance
records preserve the pending package bytes. Approval is not authentication readiness.

The fixed v6 public review interval remains 2026-10-13 20:15:00 to 22:15:00
Asia/Kuala_Lumpur, end exclusive. The additional Owner operational cutoff is
21:45:00. If regression, resource/policy verification, artifact/process/R sealing,
or readiness qualification is incomplete at that cutoff, HOLD without PREAUTH.
No shortened human authentication period or old approval migration is permitted.

## Native resource observation

At 2026-10-13T12:01:04.058716Z, the existing A native CloudShell verified caller
account 175880707430 and its exact root principal using protected AWS facilities.
One-attempt `DescribeTable` for `NexusG3AuthorityV1` and `GetSchedule` for
`NexusG3QualificationDeleteTableV1` in group `NexusG3QualificationCleanupV1`, both
in ap-southeast-1, returned `ResourceNotFoundException`. No DynamoDB data-plane
operation, mutation, secret read/output, or new resource was performed.

The observation establishes absence, not the causal attribution or exact time
of deletion. The former cleanup schedule could have completed, but that has not
been proved by these responses. Independent R history has not been rewritten.

## Required disposition

**HOLD_NO_RECREATION.** Exact v2 requires the original table and cleanup schedule
to exist and expressly forbids table recreation and ledger hydration. Date-only
policy amendments cannot restore the missing primary ledger. No policy dates,
cleanup dates, R protected objects, deployment, PREAUTH or OTP/TOTP were changed.
New native process/R binding and live qualification remain NOT_CREATED.

A later v7 public-key interval alone cannot authorize a replacement table,
rehydration, counter reset, or historical operation replay. Any subsequent
resource/lifecycle proposal must first establish an accepted deterministic
continuation contract, exact independent retained-state proof, unchanged budget
accounting and its own explicit Owner scope; otherwise remain HOLD.

## Offline implementation only

Add the exact v6 acceptance/selector and builder namespace to the existing
bounded authentication profile. Historical gen5 behavior is retained. A new
v6 constructor denies at/after the operational cutoff before allocating private
PREAUTH state. The fixed 120-second authentication TTL, cookie, Origin, CSRF,
source, custody, generation/incarnation and retirement checks remain unchanged.

Limits remain: new DDB189, cumulative DDB537 (prior charged348), runtime
S3 attempts15936 plus independent R reserve64, total16000; writes236 plus reserve4,
total240; each backend8MiB including64KiB reserve; existing USD1 inclusive ceiling.
No paid scope was added, and actual invoice reconciliation remains required.

Historical checkpoint7/8/9/10, QUARANTINE evidence, prior pending review documents
and tests are preserved. REAL_ADMISSION remains NO; D01/D03 CLOSED and G4/G6
preparation statuses are unchanged. N01 and G3 remain INCOMPLETE. D04 executor
exclusion is not introduced as a release gate.

## Qualified offline regression and exact seals

All 1,503 unique repository cases were covered in four isolated shards. The first
pass recorded 1,495 PASS, four historical environment SKIP, one FAIL and three
ERROR. These original records remain intact. Exact corrective retests resolved
all four failures: the original cancellation timer race and ZIP deadline case
passed in serial execution; the original Owner persistence module passed 13/13
with its fixed historical review clock and wall clock aligned in the TEST_ONLY
harness; the new v6 test fixture's repeated initialization/clock isolation was
repaired and passed 4/4 after importing the complete 1,503-case discovery context.
No historical test, production deadline, assertion or security gate was weakened.

Qualified unique coverage is **1,499 PASS, four historical SKIP, zero unresolved
FAIL/ERROR**. This is full coverage plus exact corrective retests, not a claim
that the first full run was green. Affected coverage is **244/244 PASS** after the
same exact new-test correction. The 11 historical bounded continuation/expiry
cases passed on the current production bytes in the full regression. The new
v6 CONFIRM/DENY and paired/scalar persistent-byte equivalence model also passed.

Each CONFIRM/DENY model uses 174 DDB calls and 11,940 S3 calls. The unchanged
analytical DDB worst case is 189: commit upper bounds 21+25+47+44+40, plus 12
outside observations. Cumulative conservative accounting is 348+189=537.
Runtime/admin reservations and the USD1 inclusive hard ceiling remain unchanged;
no live data-plane operation or usage-counter reset was performed in this turn.
Actual invoice reconciliation remains unqualified.

The final implementation inventory SHA256 is
`50cc605a6d43415c1d9be1d82a9400e0430cbaf9799a02078a29bdeb079f876c`.
Implementation bytes changed after the approved v2 package only within its
explicit exact-v6 selectors/builders and restrictive cutoff scope, plus the new
TEST_ONLY fixture. All production bytes were identical between full regression
and the final corrective snapshot. Historical tests and canonical pending v2/v6
bytes are unchanged.

The independently reproduced **inactive offline** artifact inventory SHA256 is
`4277d9fe8049f51ab63fa92e37655158eb8ce98d2eaf5e0081d4f2f74913bcbf`.
This does not measure a native process or independently sealed R binding. Both
remain NOT_CREATED because of the resource HOLD. The qualification record is
`research/nexus-production-n01-v6-offline-hold-qualification-v1.json`, canonical
SHA256 `f410b035f0dc51244281aff560f39476eb28c4dca1d8ee8cc16e2d671b815a3b`.
It retains initial failures, corrective provenance, exact budgets and local log
digests. Logs remain local under the excluded output directory.

Syntax, intended-file secret-pattern scanning, production/test import separation,
required-path TODO review, artifact inventory integrity and diff hygiene passed.
No custom agent/orchestration framework, paid resource, production enablement,
G3 bypass, fixture authority or D04 release gate was introduced. This implementer
review is not independent production security certification. Development packaging
and remote identity are recorded in the final checkpoint receipt; no final tag or
Production Final acceptance is claimed.
