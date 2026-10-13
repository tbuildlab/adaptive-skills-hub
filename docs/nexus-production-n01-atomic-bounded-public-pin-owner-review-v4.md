# N01 atomic continuation bounded public-pin Owner review v4

Approval: **NOT_OBTAINED**. This new pending package is not an Owner acceptance,
runtime pin, authentication, source registration or execution authority.

| Field | Exact pending value |
|---|---|
| Canonical package SHA256 | `01301b7b9652b2d54bb85402b484b9a0f519a5de311b53879e86e803ee9f315e` |
| Project / audience | `project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d` |
| Issuer | `stytch.com/project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d` |
| Application generation / review generation | `1 / 4` |
| New source binding generation | `4; no v3 source was installed` |
| Review ID | `n01-public-pin-owner-review-atomic-20261013-v4` |
| Inclusive start, Asia/Kuala_Lumpur | `2026-10-13T13:45:00+08:00` |
| Exclusive end, Asia/Kuala_Lumpur | `2026-10-13T15:45:00+08:00` |
| Canonical six-field public-keyset SHA256 | `4e735ee0dd506031013a15c605a6ab08ffbbe1b45d3605b0ee3254872d814480` |
| Public-key count | `1` |
| New / aggregate DDB attempt hard limits | `210 / 512; unchanged` |
| Existing cost authorization | `USD 1.00 including tax; unchanged` |
| Authority / REAL_ADMISSION | `NONE / NO` |

The [canonical pending package](../research/nexus-production-n01-pending-public-pin-review-atomic-v4.json) contains only the exact public RSA
key and bounded metadata. Its unauthenticated official JWKS observation at
UNIX_MS 1791869418771 confirms the six alg/e/kid/kty/n/use fields
are identical to the historical Owner-reviewed keyset. Private material is absent;
optional public certificate metadata is not ingested. Project and issuer are exact.

Review v3 ended at 2026-10-13T12:30:00+08:00. Its original pending package and
separate exact Owner acceptance remain historical bytes. This independent two-hour
window does not extend v3, transfer its approval, redo D01/D03, replay checkpoint
7/8 or restore old authority. Approval is required even though the public key is
unchanged. The pending generation 4 is deliberately unavailable to runtime code.

After exact explicit approval, a new measured artifact/process must receive its
own independent R custody binding before use. Existing checkpoint 8 is only the
expected predecessor: it must be independently observed again before the accepted
forward RECOVER 9 / source enrollment 10 contract can execute. Old bindings cannot
serve as current identity. Missing, expired or ambiguous evidence quarantines.

The [paired-read budget proof](nexus-production-n01-paired-read-budget-proof-v1.md)
continues to bound the modeled continuation by 189 DDB attempts, below the existing
210 remainder and 512 aggregate. Current CONFIRM/DENY models each observe 174.
Shared counters, exact checks, all conditional writes and transaction boundaries
are preserved. The conservative cost estimate remains USD 0.8657442 including a
20 percent tax reserve, below USD 1.00; no new billing hard cap is asserted.

No resource, role, account, fee scope, operation deadline, cleanup schedule or
seven-day Compliance retention rule changes. Runtime trust ends at
2026-10-13T18:51:37+08:00; existing table deletion is scheduled for
2026-10-13T19:01:37+08:00. This review ends before those bounds. Scheduling does
not prove deletion. No paid operation, deployment, production binding, LOGIN or
OTP/TOTP dispatch was performed in this preparation.

Owner authentication and an exact one-time decision remain unqualified. Human
LOGIN must wait for the new exact lifecycle binding and form-handoff proof.
Structural/offline regression never becomes current authentication authority.
D01 and D03 remain CLOSED; N01/G3 remain INCOMPLETE; G4/G6 preparation is preserved.
REAL_ADMISSION remains NO. This review is not final Owner release acceptance.

The [accepted Owner keyset-binding contract](nexus-g3-d01-owner-delivery-generation3-preparation-v1.md)
requires a fresh explicit review after expiry and states:
"General delegated execution authorization does not make an executor-generated
review into the required explicit Owner-reviewed keyset binding."
This exact contract, and the latest direct instruction, require one new Owner
approval. Expiry requires DENY, never silent renewal or approval migration.
