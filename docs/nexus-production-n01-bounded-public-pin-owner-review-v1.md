# N01 bounded public-pin Owner review v1

2026-10-12 Asia/Kuala_Lumpur. Parent development checkpoint:
`a0f053da3e310079c75fbedebd46392af0273b85`.

## Exact pending package

Approval is **NOT_OBTAINED**. The complete machine-readable input is
[pending-public-pin-review-v1.json](../research/nexus-production-n01-pending-public-pin-review-v1.json).

| Field | Exact proposed value |
|---|---|
| Canonical review-package SHA256 | `be22798028d218c2ec83816e0d78407f0b30eab82295db217c673318d58fdbc3` |
| JSON file SHA256, including final LF | `0a5d657153b455511f479eaa8f0cdbabe601759736dd1146ad21920388acf90d` |
| project_id / audience | `project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d` |
| issuer | `stytch.com/project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d` |
| Dedicated profile | Existing bounded Stytch Consumer Test profile; no Stytch Live qualification |
| N01 service revision | `nexus-g3-n01-controller-v1` |
| N01 application / review generation | `1 / 1`; separate from historical D01 application generation 3 |
| Review ID | `n01-public-pin-owner-review-20261011-v1` |
| Inclusive start, UNIX_MS | `1791762711502` |
| Exclusive end, UNIX_MS | `1791791511502` |
| Malaysia window | **2026-10-12 07:51:51.502 to 15:51:51.502, UTC+08:00** |
| UTC window | 2026-10-11 23:51:51.502 to 2026-10-12 07:51:51.502 |
| Maximum review lifespan | Exactly 28,800,000 ms / 8 hours |
| Canonical public-keyset SHA256 | `4e735ee0dd506031013a15c605a6ab08ffbbe1b45d3605b0ee3254872d814480` |
| Historical six-field public-material SHA256 | `5794378f74deee81d960d1860d744a2eed08e6da108789444f04e089efa04dd3` |
| Current vs historical keys | Exactly equal, including every kty/kid/alg/use/n/e field |
| New credential/private material | NONE |
| D01 status change / old review extension | NO / NO |
| REAL_ADMISSION | NO |

The two keyset digests use different documented JSON representations, not different
keys: the canonical sorted-key codec versus the historical ordered six-field
serialization. Structural equality was checked before either comparison was
reported. This pending proposal does not authenticate a session, register a
production writer, issue consent or prove N01 live closure.

## Verified source and parsing

The [exact public JWKS endpoint](https://test.stytch.com/v1/sessions/jwks/project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d)
returned HTTP 200 with 1,579 bytes and one RSA/RS256/signature key. The native
request used verified HTTPS, disabled environment proxies and redirects, bounded
response size and timing, and no authentication header or credential. It is a
public metadata read, not a D01 ceremony or repeated AWS qualification.

[Public-pin normalization](../ash/g3_n01_public_pin.py) validates every supplied
field before projecting the closed six-field public core. Private/unknown fields,
signing operations, duplicate IDs/members, malformed key/certificate bytes,
mismatched certificate RSA key and incorrect/ambiguous SHA256 thumbprints deny.
Certificate parsing proves byte/key consistency only; it does not claim CA trust.
The native optional metadata is not silently discarded as unvalidated input.

The native correlation ID uses `request-id-test-<UUID>`. The initially proposed
parser incorrectly assumed a bare UUID and denied the response. The fixed parser
accepts only the native Test prefix and UUID syntax; a Live-prefixed response still
denies. The retained original public response was reprocessed after this repair,
without another HTTP request. The parser has no fetch, discovery, renewal or key
rotation path. Public certificate bytes remain in ignored evidence; no raw
authenticated provider response or bearer is retained.

## Owner gate and accepted security property

[Owner delivery generation 3 preparation](nexus-g3-d01-owner-delivery-generation3-preparation-v1.md)
explicitly states: "General delegated execution authorization does not make an
executor-generated review into the required explicit Owner-reviewed keyset binding."
The [accepted runbook](nexus-g3-d01-disabled-production-deployment-owner-runbook-v1.md)
requires a fresh current public-key review after the old window expires. The latest
Owner instruction separately authorizes presentation of this exact bounded review
package and one pause for its explicit acceptance.

Acceptance must identify the exact canonical package SHA256, new N01 generation
and fixed interval above. An additive Owner acceptance/provenance record must bind
those bytes; the pending input remains historical NOT_OBTAINED evidence. No
receipt may be invented before actual acceptance. If acceptance arrives after the
exclusive end, this input remains expired; neither timestamp is silently renewed.
The old D01 review, artifacts, revoked session and CLOSED disposition stay intact.

After acceptance, independently protected R enrollment and actual current N01
source/context persistence remain necessary. Matching keys, a review receipt,
retained hashes or an implementer review cannot replace those live gates, explicit
N02 human decisions, qualified production sources or independent final review.

## Remaining engineering and validation

Three narrow deterministic additions were prepared while this gate was resolved:

- Public JWKS normalization reuses maintained cryptography/RSA primitives.
- [Retained-state resolution](../ash/g3_n01_retained_state.py) joins complete
  canonical bodies, source evidence and assertions, including nested v2 references
  and unchanged v1 grant/revocation bodies. Missing/corrupt bytes quarantine;
  retained TEST_ONLY memberships cannot be promoted into PRODUCTION.
- [Single commit ordering](../ash/g3_n01_commit.py) composes the already qualified
  transports with fresh custody observation, semantic transition recomputation,
  primary PREPARED, conditional retained objects/journal, FINALIZED, then another
  current-head read. A forged public Preparation dataclass cannot bypass transition
  checks. Unknown outcomes retire the coordinator without retry or redispatch.
  This adapter explicitly admits only the existing empty TEST_ONLY storage profile;
  a future live writer needs its separately registered provenance path.

All three return NONE and expose no production admission or credential loader.
They are preparation, not a repeated live storage/recovery run or N01 closure.
**24 distinct new tests passed**: 7 public metadata, 8 commit ordering and 9 complete
retained-state cases. The full terminal/consumed/unknown fixtures remain synthetic,
isolated under tests, and are never imported by production modules. Historical
full regressions and qualified AWS/Vercel observations are preserved rather than
rerun. The new inputs/source, deterministic MANIFEST, reproducible package,
secret/import isolation and diff hygiene are verified before this checkpoint.

No additional AWS resource, retention write, SDK identity-provider operation,
credential inspection, Vercel deployment, account configuration or paid operation
was performed here. Public metadata retrieval does not consume the bounded AWS
operation reservations. The approved USD 1.00 envelope and T0+48-hour cleanup
remain unchanged. Exact invoice cost remains UNKNOWN. Any later retained public
review uses only the already approved N01 R prefix and seven-day policy.

```text
PUBLIC_PIN_REVIEW_APPROVAL = NOT_OBTAINED
PUBLIC_PROJECT_ISSUER_KEYSET_COMPARISON = EXACT_UNCHANGED
NEW_REVIEW_WINDOW = BOUNDED_EIGHT_HOURS
OLD_REVIEW_WINDOW_CHANGED = NO
D01_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
D03_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
N01_FULL_LIVE_STATUS = INCOMPLETE
N01_CURRENT_SOURCE_ENROLLMENT = PENDING_OWNER_PIN_REVIEW_AND_LIVE_INTEGRATION
N02_STATUS = PENDING
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
