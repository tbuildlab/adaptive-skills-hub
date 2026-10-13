# N01 bounded authentication continuation / lifecycle amendment Owner review v1

Status: **PROPOSED_NOT_APPROVED**. No production implementation change, deployment,
new R binding, PREAUTH, OTP/TOTP dispatch or Owner decision is performed by preparing
this review. The canonical package and exact digest are recorded in the accompanying
review receipt; the original v4 acceptance is not transferred or extended.

## Exact requested authorization

Authorize exactly one new authentication attempt under
`OWNER_AUTH_ATTEMPT_FORWARD_V1`, using one new measured artifact, one new native
process nonce/incarnation and one independently retained R source/recovery binding.
The current accepted parent is `ba5c53ec09121d680633c2df8247e50ca164a536`.
The old deployed source is `128730fb5de6875df43670c2fb960c9452b92494`;
its runtime inventory is `91c2ecb95f3e42fdd5bc3adab89c5a4dd2ebd7a7bfb6f16fd936c7b1f11ed9cd`.
That artifact/process and its private PREAUTH cannot become the new attempt.

The original failed POST arrived at 14:36:11.495 Asia/Kuala_Lumpur, after PREAUTH
expired no later than 14:35:15.718. Request guard, CSRF and cookie matching passed;
CURRENT_STATE_GATE denied before provider send. Preserve the original closed
native diagnostics and terminal QUARANTINE evidence. The terminal controller is
not restored, reset, reused or copied. Its runtime QUARANTINE is not misrepresented
as a committed quarantine transition in the independent primary ledger.

The new predecessor must be independently re-observed as exact checkpoint 10:

- ID: `nexus.g3.production.recovery-checkpoint.v2:1f2b3a821551c19b1d8c98f37ad1ef957366349175d04d7fcb38841f8fa4f4b5`
- Body SHA256: `cee49468377d9e5068c1bb07bd1faffeaa831554d06e817987899aafd0a2e7d0`

Checkpoints 7/8/9/10 and their original source/recovery records are read-only
historical evidence. **No historical FINALIZED operation may be replayed.** The
only proposed new lifecycle mutations are RECOVER 11 with epoch 7/fresh incarnation,
and source retirement/enrollment 12 with binding generation 5. They retain all old
bytes, retire the generation-4 eligible source/binding through the existing
transaction contracts, and never restore Owner authentication or bearer authority.
Subsequent qualified context/challenge 13, one CONFIRM or DENY consumption 14 and
exact current-session revocation 15 remain non-executing evidence.

New exact IDs:
`n01-owner-binding-auth-attempt-v1`,
`n01-owner-only-source-auth-attempt-v1`,
`n01-owner-enrollment-auth-attempt-v1`.
The new R-only registration prefix is
`qualification/n01/v1/approvals/current-source-controller-auth-attempt-v1/`;
RECOVER 11 authorization uses
`qualification/n01/v1/approvals/owner-controller-recovery-auth-attempt-v1/00000000000000000011/`.
These are bounded subpaths of the already authorized R-only approvals namespace.

The new artifact digest, deployment identity, process nonce, source digest,
checkpoint-11 digest, R version IDs and retention readbacks do not exist yet.
Approval authorizes their deterministic creation only within this recipe, followed
by exact immutable sealing and independent R validation before authentication.
Unknown or mismatched identity must DENY; no placeholder can substitute for binding.

## Public-pin review v5 included in this single review

Use only the separately approved generation-5 public-pin package for this attempt,
even if v4 still happens to be valid at approval time. This avoids crossing the
v4 cutoff and requires no migration or renewal of v4 approval.

- Project: `project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d`
- Issuer: `stytch.com/project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d`
- application_generation: 1; review_generation: 5; source binding_generation: 5
- Review ID: `n01-public-pin-owner-review-auth-continuation-20261013-v5`
- Fixed inclusive start: **2026-10-13 16:00:00 Asia/Kuala_Lumpur**
- Fixed exclusive end: **2026-10-13 18:00:00 Asia/Kuala_Lumpur**
- Canonical public-keyset SHA256: `4e735ee0dd506031013a15c605a6ab08ffbbe1b45d3605b0ee3254872d814480`

The fresh official public JWKS observation found one exact six-field public key
identical to v4 and historical Owner-reviewed keys, with no private material.
The new pending package remains NOT_OBTAINED and no runtime pin is installed.
Approval of the outer canonical review must explicitly include its exact embedded
v5 public-pin package digest. Approval after expiry is unusable; no silent renewal.

## One attempt and handoff

Implement and offline-qualify only the exact head-10 successor seam and local
expiry visibility: closed time-gate diagnostics, an explicit non-secret deadline
on the form, expired-form rejection and PREAUTH cookie lifetime capped by the
existing server deadline. Keep host-only, Path=/, Secure, HttpOnly and SameSite=Strict.
No Origin/CSRF/custody/source/OIDC/schema check or historical test is weakened.

Approval is not Owner readiness. First finish regressions, seal the measured
artifact, establish the new current R/process binding and finalize only new 11/12.
Then wait for the Owner's separate readiness message. Only then create one fresh
PREAUTH with independent private nonce/CSRF/session material and immediately hand
its form to the Owner. The server deadline remains min(start+120 seconds, review
end); no refresh, reset, extension, reuse or automatic redispatch is permitted.
Construction is denied unless the full 120 seconds fit before the review end.
The window starts at server construction, not at the first human input. Finish
Git, artifact sealing and evidence preparation before this window; never delay
the immediate form handoff to collect audit logs.

No email OTP or Authenticator call occurs before the human-origin form submission.
Within the sole attempt: at most one email-send request, one email-code verification,
one Authenticator verification, one exact `record-bounded-owner-decision` CONFIRM
or DENY consumption, and one exact current-session revoke. Unknown, expired, failed,
crashed, restarted, mismatched or cancelled attempts quarantine/retire and earn no
replacement allocation. No resend or second authentication attempt is authorized.

## Exact budget amendment

The prior conservative DDB allocation is 302 and the terminal v4 process used 46,
so 348 calls remain charged to the aggregate. Existing cap 512 leaves 164 calls.
Authorize **189 new calls maximum** and an amended cumulative cap of **537**, an
increase of **25** over the old cap. This is an explicit pending amendment, not a
reset or a claim that the old review funded another attempt.

The structural-only proposed lineage has page/object shapes (3,0), (3,2), (7,8),
(9,4), (9,2); maximum page size is 27358 bytes and maximum rows per page is 31.
For each commit, the unchanged worst-case formula is:

`O + 2*ceil(O/2) + (P+3) + 3*ceil((P+3)/2) + 6`

The five commits require at most 21+25+47+44+40=177 DDB calls; twelve required
observations outside commits give 189. Every current-head/generation/incarnation,
reservation, conditional write, PREPARED/FINALIZED, readback, source/custody,
revoke/consume/replay and unknown-outcome check remains. No safety margin funds a
retry. The new profile's complete semantic simulation must independently verify
these exact bounds before any live deployment/binding; this structural sizing is
not implementation qualification. Unexpected history growth or extra work DENY.

New S3 calls are capped at 16000 total including R-admin binding/review work,
with at most 240 writes and 8 MiB new bytes per backend. All original cumulative
limits remain: S3 Tier-1 5000, Tier-2 50000, retained bytes 64 MiB and ordinary
outbound 0.25 GB. Prior usage/reservations must be reconciled before dispatch;
unused reservation is not a reset, and inability to prove remaining capacity
blocks activation. Per-reader 1000 limits and no automatic retry remain.

Rechecked Singapore rates are USD 0.71/million write units and USD 0.1425/million
read units. Reserving 1600 write units per additional API attempt, plus the paired
read allowance, gives a modeled incremental envelope of **USD 0.0357900** including
the existing 20% tax reserve. The cumulative modeled N01 envelope becomes
**USD 0.9015342**, rounded up to **USD 0.91**. The existing monetary authorization
remains **USD 1.00 including applicable tax**. Actual invoice is UNKNOWN; this is
not an AWS billing hard cap. Stop before any action projected to exceed USD 1.00.
[Official regional pricing catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/ap-southeast-1/index.json).
[Transactional capacity accounting](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html).

## Preserved resource and release boundaries

Reuse only A 175880707430's existing Singapore table NexusG3AuthorityV1, fixed
instance g3-n01-qualification-v1; R 862902859484's existing bucket
nexus-d03-custody-862902859484-ap-southeast-1-v1; and existing nexus-g3-qual Hobby
project prj_xH23xMATVChdhX34OS2vjI8dfWN2. No new resource, plan, paid service,
account, subscription or IAM scope expansion. New R-approved S3 versions have
seven-day Compliance retention; those versions cannot be deleted early, while
old versions' retention is unchanged.

Do not extend trust expiry 2026-10-13 18:51:37 Asia/Kuala_Lumpur or table cleanup
2026-10-13 19:01:37. All authentication/decision work must finish inside v5.
D01/D03 remain CLOSED; G4/G6 architecture remains unchanged. D04 executor exclusion
is not a release gate. Public keys, structural fixtures and recovery evidence
never create execution authority. REAL_ADMISSION remains NO before and after
this one authentication/decision; only a separate final accepted release contract
and exact Owner release acceptance may change it.

The regression/budget evidence separates current accepted-code regression from
future-profile qualification. Production source and historical tests are unchanged
while preparing this review. New-profile integration, expiry, terminal-state,
old-source rejection, one-attempt, restart/crash/unknown, scope and budget regressions
must pass after explicit approval and before live activation.
