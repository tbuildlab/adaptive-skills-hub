# Bounded authentication continuation / lifecycle amendment v2

Approval: NOT_OBTAINED. REAL_ADMISSION: NO. This proposal neither extends v5
nor moves its approval to v6. The implementation remains frozen at the exact
source seal below. No PREAUTH, provider dispatch, deployment, process binding,
R binding, IAM change, or cleanup reschedule has been performed for this proposal.

## Exact new public review

- Project: `project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d`; issuer: `stytch.com/project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d`.
- Application generation: 1; review generation: 6; planned source generation: 5.
- Review ID: `n01-public-pin-owner-review-auth-continuation-20261013-v6`.
- Fixed interval: **2026-10-13T20:15:00+08:00 to 2026-10-13T22:15:00+08:00, Asia/Kuala_Lumpur**;
  start included, end excluded. No renewal or extension is authorized.
- Embedded public-pin canonical SHA256: `ae081f017a1036e33e40b06bda6d6a8020526739bafbf75ad40f859c73549df1`.
- Six-field public keyset SHA256: `4e735ee0dd506031013a15c605a6ab08ffbbe1b45d3605b0ee3254872d814480`;
  one public key, unchanged from the historical Owner-reviewed keyset. No private material.

## One unspent attempt, exact head-10 forward lifecycle

Exactly one new authentication attempt across the v1/v2 continuation scope, not
one additional attempt per approval. V1 did not create its new process/PREAUTH.
The native terminal QUARANTINE remains history. Never restore or reuse its private
session, nonce, cookie, PREAUTH or controller. Independently re-observe exact
checkpoint 10 `nexus.g3.production.recovery-checkpoint.v2:1f2b3a821551c19b1d8c98f37ad1ef957366349175d04d7fcb38841f8fa4f4b5` and body digest
`cee49468377d9e5068c1bb07bd1faffeaa831554d06e817987899aafd0a2e7d0`. Preserve all historical bytes.
Do not replay FINALIZED 7/8/9/10. Prepare only RECOVER 11 (epoch 7, new incarnation),
retirement/enrollment 12 (source generation 5), context/challenge 13, one
CONFIRM or DENY consume 14, and exact current-session revocation 15. No grant,
product action, release approval, or REAL_ADMISSION enablement.

After exact Owner approval, the only further implementation amendment permitted
is adding exact v6 proposal/acceptance selectors to the existing public-review
and custody/artifact builders and passing the new approved bytes through the
same closed authentication profile. No generic review selector, prior approval
substitution, timer reset, retry framework, or lifecycle redesign. Regress those
selector changes and seal the newly measured artifact/process and R versions
before activation. Current offline source/artifact seals are not current bindings.

Authentication begins only after a separate explicit Owner readiness message.
The full original 120 seconds must fit before review end. Finish Git, sealing
and evidence work first; hand over the form immediately. At most one email-send,
one email-code check, one Authenticator check, one decision and one session revoke.
Expired/missing/ambiguous/unknown state is terminal DENY/QUARANTINE with
NO_AUTOMATIC_REDISPATCH. Failed attempt does not authorize a replacement.

## Budget and regression evidence

- Affected: 240/240, zero skips/failures/errors.
- Full: 1495 PASS + 4 historical environment SKIP
  / 1499 total; zero failures/errors. Historical test bytes unchanged.
- Exact bounded offline qualification: 11/11.
- CONFIRM/DENY paired DDB: 174/174;
  conservative worst case 189. Prior charged allocation 348 + 189 = 537.
  No counter reset or additional DDB allowance.
- Model S3: 11940 calls each; runtime cap 15,936 +
  R-admin reserve 64 = 16,000. Runtime writes 236 + four R writes = 240.
  Runtime bytes 8,323,072 + R reserve 65,536 = 8 MiB per backend.
- Existing aggregate S3 caps stay 5,000 Tier-1 / 50,000 Tier-2 / 64 MiB retained /
  0.25 GB ordinary outbound. Reconcile prior actual/unknown charges before any
  live action; unknown is HOLD, not unused allocation. Preserve seven-day
  Compliance retention for new S3 versions and all old retention bytes.
- Existing N01 hard cost cap remains USD 1.00 including tax. No new paid plan or
  resource. Baseline conservative model USD 0.9015342; additional bounded timing
  reserve USD 0.001; proposed cumulative model USD 0.9025342 (rounded up USD 0.91).
  Actual invoice is UNKNOWN. Stop before an action projected above USD 1.00.

## Explicit proposed environment-time amendment — not applied

The old caller/custody operation deadline is 2026-10-13T10:51:37Z
(18:51:37 local) and old cleanup is 2026-10-13T11:01:37Z (19:01:37 local).
A new public key review alone cannot authorize using expired AWS facilities.
This new outer approval therefore **explicitly requests**, without applying:

- Exact existing caller/custody operation DateLessThan deadline: `2026-10-13T14:20:00Z`.
- Exact existing cleanup schedule: `at(2026-10-13T14:30:00)`, UTC,
  group `NexusG3QualificationCleanupV1`, schedule `NexusG3QualificationDeleteTableV1`,
  target only existing table `NexusG3AuthorityV1` in account `175880707430`, Singapore.
- Exact existing cleanup permission deadline: `2026-10-13T14:45:00Z`.
- Preserve every non-time principal, OIDC subject/audience, action, resource,
  conditional-write and independent-custody constraint. Re-read and compare exact
  current policies before applying; unexplained drift is HOLD. No new role, table,
  bucket, account, Vercel project, or scheduler resource; no deletion or recreation.
- Prove compatibility with the accepted authority configuration and independently
  protected history before changing dates. A required configuration/hash/history
  mutation or weakening is HOLD and is not authorized by this limited amendment.
- **If the original table has already been deleted, its identity changed, the
  cleanup ran, or current history/budget is unknown: HOLD. This approval does not
  authorize table recreation, ledger hydration, replay of old transitions, or a
  new resource budget.** Existence and cleanup disposition are not currently
  verified; no operational readiness is claimed.

The additional table holding allowance is at most 24 hours, inside the same
USD 1.00 cap and 64 MiB maximum. Public AWS regional price-list evidence uses a
conservative USD 0.30/GB-month ceiling, 720 hours/month and 20% tax reserve.
At 24 hours the extra storage bound is USD 0.00075; the USD 0.001 timing reserve
also covers one cleanup invocation. No paid action occurs before approval.
If any existing resource/identity is unavailable, this package remains fail-closed
and cannot itself create a new environment.

## Exact seals and outstanding gates

- Parent HEAD: `ba5c53ec09121d680633c2df8247e50ca164a536`.
- Implementation inventory SHA256: `8ddfc95c445e5d01f97629d49f1d7da783ab8c0ee9f29f17df120d672b9483aa`.
- Inactive reproducible artifact SHA256: `9f4190cf4d26edfd913e0bf894a1a6e7bdf4fa34943a956e2e679f1790e354df`;
  compiled with expired v5, strictly offline only and forbidden for deployment.
- Source-package SHA256: `b86f1df5fb7affcad95c0ad71c08933987800d6de78e4d969ae1203df2ceada6`.
- Qualification evidence canonical SHA256: `658932968ec08479d84c8f57a9623f6aad425204051099b3003def7705cf883d`.
- Implementation bytes changed after approved v1: YES; nine existing executable
  files, one new closed restart module and two new test files. Exact hashes are
  in the evidence source seal. No implementation change after the tested snapshot.
- Current new process/R binding: NOT_CREATED. Digests: NOT_MEASURED, never fake values.
- New v6 runtime pin/acceptance: NOT_INSTALLED / NOT_OBTAINED.
- D01 and D03 remain CLOSED; G3/N01 remain INCOMPLETE; G4/G6 preparation unchanged.
- Independent security review and final Owner release acceptance remain outstanding.

Only an explicit approval of this exact new outer canonical digest, including
the embedded v6 digest and the stated conditional time amendment, can authorize
the proposed bounded work. It is not authentication readiness, execution
authority, or Production Final acceptance.
