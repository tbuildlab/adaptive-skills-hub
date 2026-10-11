# N01 current Owner context preparation v1

2026-10-11 UTC. Parent checkpoint: `d372ae3fba66b7b75124d72a41fc42e447e4eac3`.
This is bounded adapter preparation, not source enrollment, N01 live closure,
Owner confirmation, independent review or Production Final.

## Reuse and deterministic additions

The closed [D01 bounded profile](nexus-g3-d01-delegated-live-closure-v1.md) is
preserved. Its historic revoked session and expired public-key review are never
restored or renewed by these modules. Its Consumer Test Principal, RS256/public
pin rules, direct remote session observation and exact factor lineage are reused.
The accepted [bounded context](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md)
and [delegated policy](nexus-g3-delegated-executor-authority-policy-v1.md) remain
mandatory; D04 executor exclusion is not reinstated as a release gate.

The maintained [Stytch Python SDK](https://github.com/stytchauth/stytch-python)
owns provider API calls and model parsing; requests owns native HTTPS/TLS.
PyJWT and cryptography own RSA signature verification. Nexus adds only:

- Closed exact registered issuer/project/user and signed-response consistency.
  Missing, duplicated, extra private key fields, unsupported algorithms, bad
  signatures, expired reviews and malformed identity/factors deny.
- Fixed Consumer Test paths and request shapes. Direct `sessions.authenticate`
  omits duration extension, custom claims and JWT-cache fallback. SDK transport
  rebinding, retry adapters, redirect/proxy overrides and unrelated paths deny.
- Bounded response size, unique JSON members, exact HTTP/body status, fixed media
  type, verified TLS, bounded timing and 32 maximum attempts per transport.
  Unknown outcomes retire the transport; no write retry occurs.
- One original opaque bearer in private process memory, fixed exact native
  session/user/factor lineage and a non-refreshable context deadline. Earliest
  factor freshness, provider expiry, review and operation deadlines all constrain
  it. Wall/monotonic regression retires. Nanosecond lineage cannot disappear in
  a millisecond projection. Pickle/deep-copy restoration is rejected.
- Exact-session revoke followed by exact native 404 `session_not_found` is
  distinct from a generic error. SDK buffers are cleared after every operation.

All public projections remain **NONE**. These objects cannot create a binding,
receipt, grant, claim or execution permission. A protected production composition
must still authenticate source origin/enrollment, native runtime/deployment,
current independently retained recovery state, N02 human ingress and every
ledger transition. SDK presence, type checks and matching public hashes do not
supply that composition. The current public fail-closed evaluator is unchanged.

## Dependency and source limits

The optional [qualification dependency lock](../research/nexus-production-n01-identity-sdk-requirements-v1.txt)
pins 23 official PyPI wheels for CPython 3.12 / Linux x86_64, including Stytch
15.3.0, requests 2.34.2, PyJWT 2.13.0 and cryptography 50.0.0. Downloaded wheel
SHA256s matched independent PyPI release metadata. No wheels are committed or
bundled in public assets; the existing read-only Vercel probe is not redeployed.
The local development interpreter installed the maintained SDK and its dependencies.
This does not establish a tested future Linux deployment or production issuer.

The SDK's Test-environment warning is retained: this implementation is restricted
to the already accepted dedicated Consumer Test profile. It does not qualify a
Stytch Live environment. The SDK's unused asynchronous BasicAuth deprecation
warning is visible; the fixed adapter uses the synchronous path. No identity
provider, vault, agent, orchestration platform or memory service was built.

Authenticated native Vercel configuration metadata on 2026-10-11 showed exactly
`STYTCH_PROJECT_ID` and `STYTCH_SECRET` as Production Secret entries, plus enabled
system environment metadata. Values were not opened, pulled, logged or copied.
Configuration presence is not credential validity or native Owner context proof.

## Validation and outstanding live work

**31 distinct new tests passed**: 12 signed projection/clock contracts, 10 fixed
SDK/HTTP contracts and 9 ephemeral context/continuity/revoke contracts. Test keys
are generated only in memory; all provider exchanges are isolated synthetic
responses. These are not D01 ceremonies or N01 live evidence. Imported helper
classes are kept module-qualified so discovery does not inflate test totals.

Current discovery contains 1,295 distinct Python test IDs. The previous exact
full snapshot's 1,243 cases, subsequent 15 custody/budget and six probe cases,
and these 31 additions form separate documented validation snapshots. The retained
366 unchanged Node cases are separate. No combined run is mislabeled as a new
full current-snapshot regression; no test or existing skip was removed or weakened.
An isolated preparation snapshot passed 117 relevant N01/G3 transition and public
boundary cases and 71 package/G4/G6 cases. After tightening validation of unused
public-key entries, the affected 31 adapter cases passed again. Repeats are not
added to distinct totals. Static codec equivalence, secret/import isolation,
deterministic 594-entry MANIFEST and a reproducible 205-member source package pass.

No AWS data-plane call, identity-provider call, paid resource, new retained S3
version or model execution occurred in this preparation. Dependency registry
reads and authenticated Vercel metadata observations are distinct from those
zero provider/service-operation counts. N01's USD 1.00 cap, aggregate reservations,
48-hour window and scheduled cleanup remain unchanged. Invoice cost is UNKNOWN.

N01 still requires native protected controller/source enrollment and real
current-context lineage in the qualified durable state, then revoke/consume/replay
integration. [Existing storage/recovery](nexus-production-n01-storage-qualification-v1.md)
and [native runtime federation](nexus-production-n01-vercel-runtime-qualification-v1.md)
remain qualified only for their explicit TEST_ONLY/read-only profiles. They are
not repeated or relabeled as production authority. N02 and subsequent release
gates remain pending; REAL_ADMISSION remains NO.

```text
N01_CURRENT_CONTEXT_ADAPTER = COMPLETE_OFFLINE_PREPARATION
N01_CURRENT_CONTEXT_LIVE_QUALIFICATION = NOT_PERFORMED
N01_PROTECTED_SOURCE_ENROLLMENT = NOT_IMPLEMENTED
N01_FULL_LIVE_STATUS = INCOMPLETE
D01_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
D03_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
