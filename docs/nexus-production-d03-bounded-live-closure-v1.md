# D03 bounded live custody closure v1

2026-10-11. Implementing source: `d09c05dbc92770732a6abacb64b4b7af4d538eea`.
This additive disposition closes the ten gates of the accepted
[minimal D03 amendment](nexus-g3-d03-minimal-scope-and-autonomy-amendment-v1.md)
under the Owner-approved [USD 1.00 diagnostic package](nexus-production-d03-custody-authorization-package-v1.md).
It does not qualify N01/N02, independent review, Production Final or admission.
Historical conditional/failed checkpoints remain unchanged.

## Exact deployed chain and custody

Authenticated A root was `175880707430`, NexusD03DiagnosticA; R root was
`862902859484`, Tee. Both are standalone, without Organizations. Ordinary execution
used GitHub native OIDC, A `G3QualD03DiagnosticCaller`, R `G3QualFenceAppendRead`,
and exact bucket `nexus-d03-custody-862902859484-ap-southeast-1-v1` in Singapore.
No long-lived key, new compute/database/logging service or plan upgrade was performed.
A PAID/ACTIVE was observed following Owner enrollment; R remained FREE/ACTIVE.

The sole A trust correction changed the previous exact subject to
`repo:TDY0225@223441940/adaptive-skills-hub@1341770180:ref:refs/heads/nexus-v2-production-qualification`.
Authenticated repository metadata and GitHub's immutable-subject specification
established the owner/repository IDs. Exact readback preserved issuer, audience,
deadline, principal and all permissions. No wildcard or second subject was added.

- [Append run 38127720218](https://github.com/TDY0225/adaptive-skills-hub/actions/runs/38127720218):
  first attempt, source `914513b526e8bb9c4549dd5b230e96a88430a190`, SUCCESS.
- [Fresh restart-read run 38128221559](https://github.com/TDY0225/adaptive-skills-hub/actions/runs/38128221559):
  first attempt, source `d09c05dbc92770732a6abacb64b4b7af4d538eea`, SUCCESS.

Sanitized projections preserve service, operation, HTTP status, request ID,
fixed error code and contract outcome; raw logs and credentials are not persisted.
Earlier YAML/authentication failures remain failures, with zero S3 effect; they
were not rerun or relabeled. UNKNOWN writes were never automatically retried.

## Ten gate dispositions

| Gate | Actual evidence and limit | Disposition |
|---|---|---|
| Independent protected state | Exact A/R accounts and native temporary chain; no Organization or alternative A administrator path. Ordinary R role's IAM trust/policy and bucket-policy mutations returned actual 403 AccessDenied. Owner R root is independent setup/recovery custody, outside that role. | PASS |
| Immutable / append-only history | Actual Compliance seven-day versions, exact retained reads, conditional create; duplicate/conflict returned 412. Root attempted locked fault-version deletion and retention shortening: actual 403. Versioning/Object Lock and bucket controls read back unchanged. | PASS |
| Stale overwrite / revival | Unconditional overwrite denied by AWS; current full history and exact versions checked before consumer use. Stale expected head quarantined. | PASS |
| Rollback / fork / gap | Real independently seeded isolated fault histories read from S3; stale snapshot/head, duplicate version, missing sequence, delete marker, corrupt body and wrong predecessor rejected by the deterministic consumer. Normal history remains intact. | PASS |
| Unknown outcome | Actual RESULT sequence 2 committed; acknowledgment deliberately dropped after commit. QUARANTINE, no second write; exact pending candidate reconciled read-only. | PASS |
| Restart retirement | Independent R verified complete current sequence 0..3, committed immutable RECOVER authorization and sequence 4; fresh native OIDC process read current 0..4, observed epoch 2/incarnation 2 and rejected incarnation 1. No bearer was present or restored. | PASS |
| Generation / incarnation | Original exact retained registration pinned; mismatched generation/incarnation and insufficient remaining retention quarantined. Caller cannot replace R registration. | PASS |
| No automatic redispatch | UNKNOWN consumed reference and context retirement survive RECOVER; synthetic consumer attempts remain DENY. No real provider dispatch was performed. | PASS |
| Current protected recovery state | All versions, markers, contiguous lineage, referenced bodies and Compliance coverage checked; repeated inventory matches. RECOVER candidate without independently retained authorization quarantined. Missing/corrupt evidence never creates new GENESIS. | PASS |
| Independent recovery administrator | Actual STS attempt to assume R recovery administrator denied. Fault/admin-authorization mutation, deletion, retention, IAM trust, role permission and bucket-policy mutation denied to ordinary execution. R root alone verified/approved RECOVER. | PASS |

There are two evidence classes: REAL_AWS_SERVICE_RESPONSES and
SYNTHETIC_CANARY_CONSUMER_ASSERTIONS. AWS enforcement is real; synthetic references
are TEST_ONLY and never production authority. Backend unavailability and malformed
transport are existing focused offline fault tests, not an induced AWS outage.
Concurrent explicit contenders produced exactly one successful append and one
412, not a retry engine. This is not complete N01 cross-family membership,
transaction/fence crash serialization, live grant issuance or real effect proof.
D04 historical executor exclusion is unchanged and is not a release gate.

## Exact independent references

Original retained registration version: `PnyOK3mANH6Y5kZQsgQ1VYqACGr1Xb3M`;
SHA256 `ac3b890867ded5be576d750b1247021935bf48b9bb45211ef254c969b4d568ec`.
Independent RECOVER sequence 4 version: `.HLyIDG2CtYV7V7pe7r3PTcTd7rCjd3W`.
Root-only authorization version: `QfYTlVH0dMa0UrGM1zI8flinsMTPw_Ic`.
No previous registration or canonical D05 body was changed.

## Retirement, costs and cleanup

After successful restart qualification, independent R changed the exact append
role trust to explicit DENY of the same A role and deleted its sole inline policy.
Readback confirmed that trust, zero inline policies and zero attached policies.
Existing temporary sessions therefore have no role permissions; future role
assumption is denied. No new permission or principal was introduced.

R retained and read back a TEST_ONLY diagnostic retirement record under
`qualification/v1/faults/custody-retirement-v1/retirement.json`:
version `CVwjs.AvI3W8.Dl20wVmCpVD7RTDCapp`, SHA256
`0a3aebd86d61ce1a87e3a2e12b6029b03f9c1d52545ef4c3cce75d28e5eaae48`.
The lineage is retired before its retained ancestors expire. It cannot be reused
as production membership or automatically redispatched.

Four native Lifecycle rules were applied and read back, confined to the two
approved prefixes: current expiration after eight days, noncurrent expiration
after one day, and expired-delete-marker cleanup. Active Object Lock continues
to prevent deleting retained versions; no retention was shortened. No unrelated
prefix, transition/storage class, replication, queue or compute was added.
**Cleanup is SCHEDULED, NOT COMPLETED.** Actual expired-object deletion and removal
of the emptied bucket must be verified later; small residual storage charges are
possible. Lifecycle scheduling is not proof of deletion or an AWS billing hard cap.

Recorded S3 attempts: setup 13 + seed 90 + root negative 4 + append 298 + independent
RECOVER 70 + restart-read 56 + retirement/configuration 12 = **543**. These include
negative requests and exact reads. Final retained inventory: **64 versions,
35,606 payload bytes**, plus the intentional fault delete marker. No large object,
unbounded retry or out-of-scope service was used. These quantities remain far below
the approved 5,000/50,000 request and 64 MiB envelope and its conservative USD 0.108
indicative taxed bound. Exact AWS invoice is UNKNOWN; USD 1.00 remains the ceiling.
New production custody/lifetime/services require a separate bounded approval.

References: [Object Lock and Lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html),
[expiration rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intro-lifecycle-rules.html),
[asynchronous expiration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html).

## Regression and subsequent gates

Already completed distinct regression baseline: **1,533 / 1,529 PASS / four existing
environment-dependent SKIP / zero FAIL**: 1,167 Python cases and 366 Node cases.
The original UTF-8 Python log says OK(skipped=4); wrapper printing failed afterward
on cp1252 Unicode output and is not counted as a test failure or hidden success.
Full regression source snapshot predates the small safe OIDC/IAM canary additions;
those were compiled and actually exercised by the referenced live runs. Completed
offline regressions and D01 ceremonies were not repeated for this closure.
Package reproduction, MANIFEST, secret/import/scope and diff hygiene are retained
as separate checkpoint validation, not additional live gates or inflated tests.

Continue directly with N01/N02 deterministic implementation and actual composition,
mediation and E2E qualification. The bounded diagnostic fence cannot be promoted
to PRODUCTION. G4/G6 design remains complete; live qualification and independent
security review remain open. Only exact Owner acceptance can authorize final freeze.

```text
D03_STATUS = CLOSED
D03_QUALIFICATION_PROFILE = BOUNDED_DIAGNOSTIC_TEN_GATE
D03_ZERO_COST = NO_APPROVED_METERED_BUDGET
D03_PRODUCTION_LINEAGE = NOT_REGISTERED
D03_DIAGNOSTIC_APPEND = REVOKED
D03_DIAGNOSTIC_REGISTRATION = RETIRED
D03_CLEANUP = SCHEDULED_NOT_COMPLETED
D01_STATUS = CLOSED
G3_STATUS = INCOMPLETE
N01_PRODUCTION_LEDGER_QUALIFICATION = NOT_PERFORMED
N02_PRODUCTION_INGRESS_QUALIFICATION = NOT_PERFORMED
G4_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
G6_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
INDEPENDENT_SECURITY_REVIEW = NOT_PERFORMED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
