# Nexus G3 D01 Owner registration and public JWKS pinning v1

2026-10-09, Asia/Kuala_Lumpur. Non-secret, offline integration at exact source
checkpoint `aeb973790211bd76b769ee272690a8adc6e2b70b`, branch
`nexus-v2-g3-live-qualification`. This is an additive review of the
[integration closure](nexus-g3-d01-pre-secret-integration-closure-v1.md) and
[custody runbook addendum](nexus-g3-d01-secret-custody-integration-runbook-addendum-v1.md).
No historical accepted document, v1 body, D05 Principal or production authority
implementation is changed.

## Owner input and its exact storage boundary

The human Owner supplied P_OWNER_PROJECT_ID_REVIEWED, U_OWNER_NATIVE_ID_REVIEWED
and one public JWKS in this request. Exact identifiers and the accepted public
key exist once in the protected **server-side source role**
`diagnostics/g3-d01-rp/lib/server/deployment-input.js`. This role describes the
intended deployment boundary; the current executor can edit repository source,
so it is not a proven D04 custody boundary. No native ID is inferred from a login,
email, display name, External ID, project label, request envelope or browser.
Docs/tests/output use aliases and public-integrity hashes instead of duplicating
the exact supplied IDs. The file is neither client-exported nor authority-bearing.

The registration is STYTCH_CONSUMER, TEST, exact supplied project/native user,
origin `https://nexus-g3-qual.vercel.app`, factors EMAIL_OTP + TOTP, provider
session bound 15 minutes and non-refreshable diagnostic context bound 300,000 ms.
Source is OWNER_REVIEWED, with a static review reference and deployment revision
`g3-d01-owner-pinning-v1`. A source/review label records this human input; it
does not independently authenticate the Owner or prove issuer administration.

The prior checkpoint's deployment has provider/keyset null and
registration_generation 0. This is its **first real static registration**:
registration_generation transitions from unregistered 0 to reviewed 1;
project/application/owner/binding generations are all initialized to 1. Existing
fixture generation 1 records are not production/Owner registrations and never
advance these counters. Registration generation equals application generation,
as required by the existing activation seam; no new counter semantics are invented.
Replacement needs a new separately reviewed source/deployment generation,
retirement of previous contextual state and later qualified custody. These values
are not an N01 durable epoch or a database-issued generation. No real binding,
receipt, grant, revocation or authority state is issued.

The Owner explicitly selected **keep delivery unregistered**. This review adds one
closed, fail-closed registration case: OWNER_REVIEWED may use delivery_email=null.
The field remains required; missing field, wrong type and extra fields still deny.
OFFLINE_SYNTHETIC retains its earlier exact synthetic email rule. Existing string
delivery registrations remain compatible. Null pins native identity without
inventing an address or deriving identity from email. Both the future live selector
and EMAIL_OTP_SEND reject unregistered delivery before credential loading/provider
IO. Filling a future non-secret routing address is a separate reviewed Owner input;
it cannot change native identity or activate the current mode. This explicit
additive diagnostic format clarification does not modify a D05 canonical body.

## Public key review and normalization

The supplied JWKS contains one RSA 2048-bit public key, RS256, use=sig,
key_ops=[verify], public modulus/exponent, a public certificate and thumbprint.
Local crypto parsing confirmed certificate/public-key equality and matching SHA-256
certificate thumbprint. The certificate is not a CA/provider/Owner identity trust
anchor. Its lifetime does not replace the bounded pin review window.

`normalizeReviewedPublicJwks` accepts only the closed public core
`kty/kid/alg/use/n/e`, plus bounded optional key_ops/x5c/thumbprint metadata at
intake. A present key_ops must be exactly [verify]. It checks canonical unsigned
base64url integers, RSA >=2048 bits, algorithm/use, unique bounded kid, 1..8 keys
and a 16-KiB intake bound. Optional x5c allows at most three bounded public DER
certificates, compares leaf public key and any supplied SHA-256 thumbprint, then
discards certificate/operation metadata. The Owner's x5tS256 spelling is an
explicit intake-only alias; standard x5t#S256 is also accepted, and simultaneous
aliases deny. Neither is a verifier trust field. No certificate is persisted.

Every private RSA field d/p/q/dp/dq/qi/oth, unknown key property, jku/x5u/discovery
URL, non-public type/algorithm/use, missing verify operation, ambiguity, malformed
encoding or oversize input denies. Any actual accidentally supplied private/secret
material must stop intake without persistence. This request contained only public
key data and non-secret registration IDs; no actual private field/secret was seen.
Negative tests use field-name placeholders, not real private keys.

Top-level request_id/status_code are response-envelope metadata only. They are
neither identity evidence nor pinned values and are discarded. The resulting pin
contains only the **existing six-field public JWK profile**, project binding,
OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET, application generation, review reference
and fixed review interval. The existing standalone JWT verifier is byte-preserved.
No raw response envelope, URL, token, certificate, bearer or login material is stored
in deployment input. The URL text supplied with the request was not fetched or
used as a trust source.

The half-open fixed pin interval is:

- valid_from = 1791477725000: 2026-10-09 00:42:05 Asia/Kuala_Lumpur.
- valid_until = 1791564125000: 2026-10-10 00:42:05 Asia/Kuala_Lumpur.

This retains the accepted maximum 24-hour window. Imports, reload, deployment
verification and restart never refresh it. At/after valid_until or before
valid_from runtime pin validation denies. Later use requires a new Owner-reviewed
public-pin revision; long certificate validity does not waive expiry. Source
composition verification tests structural validity at the fixed review point and
does not claim indefinite current validity. All paths remain disabled regardless
of pin age in this release.

Public-core integrity SHA-256:
`5794378f74deee81d960d1860d744a2eed08e6da108789444f04e089efa04dd3`.
Exact registered project/native-user tuple integrity SHA-256:
`1faf53124059cb6967aae8b0fd10f9e5547f249bce6720ae789d0ccd901a58df`.
These hashes bind public/non-secret input bytes, not credentials, provider trust
or authorization. RSA private signing keys in tests are generated transiently
for synthetic signatures and are never exported or persisted.

## Identity semantics and unqualified boundaries

The unchanged candidate Principal is issuer `stytch.com/<P_OWNER_PROJECT_ID_REVIEWED>`,
client_id/audience the exact dedicated project/application candidate and subject
U_OWNER_NATIVE_ID_REVIEWED. Session ID belongs only in protected contextual evidence;
session token belongs only in future protected runtime bearer custody. Neither is
added to registration or public evidence.

[Accepted Stytch Principal closure](nexus-g3-u1-stytch-principal-closure-v1.md) and
[adapter review](nexus-g3-d01-live-stytch-adapter-offline-review-v1.md) support the
candidate profile but leave dedicated project/application semantics and effective
enrollment/lifecycle qualification CONDITIONAL. The supplied IDs/public key do
not close that live gate. No signed provider token, login, factor timestamp,
remote session result, issuer administration or logout/revocation behavior was
observed here. Synthetic test signatures prove local rejection logic only.
STYTCH_PRINCIPAL_RUNTIME_MAPPING therefore remains CONDITIONAL.

D01_JWKS_RUNTIME_SEAM=DEFINED describes the completed closed public-input/
project-generation pin/verifier connection. It does not promote actual issuer key
ownership, provider claims or current-session proof to VERIFIED. Positive future
diagnostic use still needs direct remote SESSION_AUTHENTICATE under a separately
authorized live revision. Local JWT validity alone remains insufficient.

D04 remains unqualified/BLOCKED for effective exclusion. Current Windows/Codex
source access does not qualify as independent Owner custody. Existing reported
Vercel/OIDC state was not read. Owner-only independent device, issuer/deployment/
environment permission exclusion and effective-denial evidence remain necessary;
the earlier custody runbook's prohibition on this executor's secret custody stands.

## Disabled deployment source and artifact

Static deployment input now contains exact server-side registration and public pin,
immutable at all nested key/factor/config arrays. Current mode FAKE_DISABLED and
both false compile gates remain. Pin/registration/credential presence, browser
override, fake adapter, Preview or missing routing cannot activate live operation.
The unchanged public entrypoint, public assets and existing tests preserve their
baseline bytes. No real credential value or environment is inspected during
import, factory creation, validation, source generation or tests.

The existing deterministic verifier still builds exactly **19 diagnostic source
files**. It additionally checks closed Owner registration/keyset/generation matching,
server-only native IDs, non-export of native IDs/provenance in client assets and
sanitized responses, and the registered disabled entrypoint. It does not depend
on repository MANIFEST, install anything or run a provider build/deployment.
The credential loader source remains included only in this separately reviewed
standalone artifact; the repository MANIFEST sensitive-path rule is unchanged.

Exact LF deployment-input source SHA-256:
`67cedb5d52c4f5523252c864c08d48f752f522036e40719eaf6fc8d5addaabeb`.
Exact deterministic 19-file source ZIP SHA-256:
`84796f260303ad64e9982134075a4fadae968c70919d3ffaf17a62be51c78fc3`.
Individual source hashes and secret-free metadata are retained under ignored
`state/g3-d01-owner-pinning-20261009/artifact/`. Repeated ZIP hashes match.
No .env/.vercel/browser state/secret/Route D/Nexus authority module is packaged;
the local deployment directory was not inspected. Public JWKs are public material,
but this source role keeps them and native registration out of client assets.

READY_FOR_DISABLED_PRODUCTION_DEPLOYMENT_REVIEW=YES means this disabled diagnostic
source is ready for an independent Owner build/deployment **review**, not deployment
permission, a provider-built artifact or effective hosted isolation. Review includes
actual Vercel build traces, public/function separation, immutable configuration,
duration support, Preview exclusion and native key review expiry. No provider build
or deployment was performed. Missing OTP routing is explicitly acceptable for the
disabled review; it remains a hard prerequisite before future live activation.

READY_FOR_SECRET_CUSTODY_SETUP=YES retains the prior technical-preparation meaning:
no secret access is needed to finish local code/source composition. Actual secret
entry remains HOLD pending separate Owner authority and independent custody.
Pinning does not authorize credentials, deployment, provider actions or admission.

## Exact scope and validation

Modified:

```text
MANIFEST.json
diagnostics/g3-d01-rp/lib/server/deployment-input.js
diagnostics/g3-d01-rp/lib/server/pinned-identity.js
diagnostics/g3-d01-rp/lib/server/provider-registration.js
diagnostics/g3-d01-rp/lib/server/pre-secret-policy.js
diagnostics/g3-d01-rp/lib/server/stytch-transport.js
diagnostics/g3-d01-rp/scripts/verify_deployment.py
```

Added:

```text
diagnostics/g3-d01-rp/tests/owner-pinning.test.js
docs/nexus-g3-d01-owner-registration-jwks-pinning-v1.md
```

Nine files comprise this reviewed slice. Ignored validation evidence and the three
preexisting untracked Route D documents are excluded. Baseline checks preserve
402 other paths, all 214 old tests, old public/current deployment graph, D05/v1
contracts, credential loader and MANIFEST rules. Main/development refs do not change.
Deterministic repository MANIFEST has 405 entries with only six explicitly modified
old source hashes and two new entries; credential-custody.js remains excluded.

| Offline command | Result |
|---|---|
| `node --test tests/owner-pinning.test.js` in diagnostic directory | 53 PASS |
| Existing seven diagnostic files before adding the new test file | 214 PASS |
| `node --test tests/*.test.js` in diagnostic directory | 267 PASS |
| `D:\DevTools\NexusR2Python\Scripts\python.exe -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge` | 134 PASS |
| Same Python `-B -m unittest tests.test_ecosystem_isolation_package` in fresh accepted source snapshot | 11 PASS |
| Same Python `-B diagnostics/g3-d01-rp/scripts/verify_deployment.py --output state/g3-d01-owner-pinning-20261009/artifact` | 19-file deterministic closure PASS; disabled entrypoint; network 0 |
| Same Python `-B state/g3-d01-owner-pinning-20261009/verify_pinning.py` | Scope/baseline/secret/private-JWK/import/JS-syntax/MANIFEST checks PASS |
| `git diff --check` and staged equivalent | PASS |

New coverage is 19 registration, 22 key/pin and 12 disabled assembly tests. No old
test is edited or weakened. A small ad hoc digest command initially used invalid
ESM import alias syntax; it was corrected and rerun without provider IO or changes
to validation guards. Source/staged scans inspect only accepted source material,
not real credentials or ignored account state. Network traps require zero calls.

## Remaining Owner-only work

1. Establish independent device and effective issuer/Vercel/deployment/admin/log/
   environment exclusion, including independently invalidating any executor-accessible
   credentials/rights. This requires separate account authority; no such action ran.
2. Independently review the disabled Production build/source/config trace and runtime
   constraints. Confirm the exact native project is a dedicated Nexus application
   and independently renew public pins before their fixed expiry as needed.
3. Supply a separately reviewed non-secret OTP delivery address before any future
   live activation. It is routing only and cannot replace the native Owner tuple.
4. Under separate exact authorization, privately prepare Production-only secret
   custody on the excluded device; never provide values to Codex/current machine.
5. Obtain a separately reviewed activation revision and explicit disposable D01
   live-effect/cleanup authorization. Qualify actual issuer/audience/subject/factors/
   session lifecycle and D04 effective denial. Public admission remains disabled.

No current secret entry, dashboard action, sign-in, resource mutation, deployment
or provider test is authorized. Stop at missing independent custody, provenance,
expired pin, routing, deployment proof or live authorization rather than weakening
a guard. No remaining independent authorized offline task requires such actions.

## Final fields

```text
D01_OWNER_NATIVE_REGISTRATION = PINNED
D01_OWNER_PROJECT_REGISTRATION = PINNED
D01_PUBLIC_JWKS = PINNED
D01_KEY_PROVENANCE = OWNER_REVIEWED_PUBLIC_SOURCE
D01_JWKS_RUNTIME_SEAM = DEFINED
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL
D01_DISABLED_DEPLOYMENT_SOURCE = VERIFIED_OFFLINE
LIVE_ADAPTER_DEFAULT = FAKE_DISABLED
CODE_REVIEWED_LIVE_ENABLED = false
DEPLOYMENT_REGISTRATION_ENABLED = false
NETWORK_CALLS_PERFORMED = 0
LIVE_STYTCH_CALLS_PERFORMED = 0
STYTCH_CREDENTIAL_ACCESS = NONE
VERCEL_SECRET_ACCESS = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
READY_FOR_DISABLED_PRODUCTION_DEPLOYMENT_REVIEW = YES
READY_FOR_SECRET_CUSTODY_SETUP = YES
READY_FOR_D01_LIVE_AUTHORIZATION = NO
```
