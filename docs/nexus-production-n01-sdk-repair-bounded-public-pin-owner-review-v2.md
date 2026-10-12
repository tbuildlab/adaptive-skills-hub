# N01 SDK repair bounded public-pin Owner review v2

Approval: **NOT_OBTAINED**. This is one new fixed four-hour review; no historical
review window is extended and no Owner acceptance record has been created.

| Field | Exact pending value |
|---|---|
| Canonical package SHA256 | `cd2d4a2fa5002d4bd28a0dc3cc789c89fe220060871ed3ee7fa02bd0480feb16` |
| Project / audience | `project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d` |
| Issuer | `stytch.com/project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d` |
| Application generation / review generation | `1 / 2` |
| Review ID | `n01-public-pin-owner-review-sdk-repair-20261012-v2` |
| Inclusive start, Asia/Kuala_Lumpur | `2026-10-12T18:25:38.065+08:00` |
| Exclusive end, Asia/Kuala_Lumpur | `2026-10-12T22:25:38.065+08:00` |
| Inclusive start, UTC | `2026-10-12T10:25:38.065+00:00` |
| Exclusive end, UTC | `2026-10-12T14:25:38.065+00:00` |
| Canonical public-keyset SHA256 | `4e735ee0dd506031013a15c605a6ab08ffbbe1b45d3605b0ee3254872d814480` |
| Key count | `1` |
| Approval / authority / REAL_ADMISSION | `NOT_OBTAINED / NONE / NO` |

The exact [pending canonical package](../research/nexus-production-n01-pending-public-pin-review-sdk-repair-v2.json) preserves the
public six-field RSA key and binds the fixed interval above. The unauthenticated
verified-HTTPS public JWKS read at UNIX_MS 1791800374454 confirmed
structural equality of all public kty/kid/alg/use/n/e fields with the earlier
Owner-reviewed keyset. The maintained parser validated all supplied optional
certificate metadata before projecting that public core. No authentication
header, credential, private key, session or code was requested or copied.

The earlier review ended at 2026-10-12T07:51:51.502Z. Its proposal, Owner
acceptance, independent retained versions, D01/D03 CLOSED statuses and
checkpoints 5/6 remain historical and unchanged. Current production review
checks continue to reject expired review 1. No review-2 runtime pin or acceptance
is installed before exact explicit Owner approval. Equal keys do not renew an
expired interval or create current authority.

After approval, the same existing bounded controller will require an additive
independent R review record, new measured artifact/process binding, fresh
incarnation and explicit forward retirement from retained head 6. These are new
forward operations, never replay of FINALIZED recovery/enrollment 5/6. No old
bearer, Owner context, code, cookie, challenge or execution permission is restored.
No OTP/TOTP request is authorized before the new exact binding and login entry
are verified. Real human authentication and decision remain unqualified.

This review changes no resource, role, account, fee cap, backend operation
window, cleanup schedule or seven-day retention policy. REAL_ADMISSION remains
NO. It neither grants general production execution nor constitutes Production
Final Owner release acceptance.

The [accepted Owner keyset-binding contract](nexus-g3-d01-owner-delivery-generation3-preparation-v1.md)
states: "General delegated execution authorization does not make an
executor-generated review into the required explicit Owner-reviewed keyset
binding." It also requires a fresh current public-key review after expiry.
This is the exact reason one new explicit Owner review is necessary.

If this fixed interval expires before approval or use, fail closed; do not renew
it silently or change NOT_OBTAINED to approved without direct Owner acceptance.
