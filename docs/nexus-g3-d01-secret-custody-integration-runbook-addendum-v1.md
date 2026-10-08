# Nexus G3 D01 custody integration runbook addendum v1

2026-10-08. Additive procedure for the
[original custody runbook](nexus-g3-d01-vercel-secret-custody-runbook-v1.md) and
[integration closure](nexus-g3-d01-pre-secret-integration-closure-v1.md).
Historical readiness NO described its earlier unassembled source. This closure
reports technical preparation YES; actual secret entry remains HOLD. No action
below was run. No new account/deployment/live authority is granted by this document.

## Mandatory independent Owner context

Owner must select a separate physical device or independently controlled security
context unavailable to Codex/executor filesystem, browser automation, remote access,
debugging, logs and account credentials. Another browser on this Windows machine
is insufficient. Do not inject, download, open, print, hash, copy or screenshot any
Stytch/Vercel/OIDC secret here. Do not use ChatGPT/Codex messages, shell environment,
CLI args, terminal history or screenshots as a secret channel.

Existing Vercel CLI authentication/OIDC artifacts on the executor machine are
USER_REPORTED, not inspected. Owner must independently identify their effective
rights and invalidate or exclude any executor-accessible account/session/token/
role with deployment, environment, project administration or secret access.
Removing a local file does not prove remote invalidation. Membership descriptions
alone do not prove denial. Retain names/status-only effective-permission evidence
from an independently authorized review; stop before secret entry if ambiguous.
No such credential or permission action is authorized in this offline run.

## Future Owner-only sequence after separate exact authorization

1. Verify the accepted local source checkpoint and fixed 19-file artifact mapping.
   Build/deploy custody must remain Owner-controlled; executor must not upload a
   changed image/config after review, retrieve runtime env, access logs/dumps or
   obtain CLI/account/shell/alternative debug rights. Review deploy permissions
   and current provider tooling from the independent device. No command here
   authenticates a CLI, downloads env or deploys.
2. Independently register the disposable Stytch Consumer Test project, dedicated
   Nexus relying-party boundary, exact native Owner user and delivery address.
   Verify non-Owner account remains distinct. Fill the non-secret registration
   format in the integration closure through a protected reviewed deployment
   revision, never through login TOFU or browser input. Project/user identifiers
   and delivery email may be private; only sanitized aliases enter public evidence.
3. Independently obtain and verify public signing keys for that exact project,
   recording provenance, application generation, review reference and bounded
   validity. Supply the closed project-keyset pin format. There is no prescribed
   guessed JWKS URL. If official/live values fail the candidate issuer/audience/
   subject/signature profile, STOP. Keep mapping CONDITIONAL until qualified;
   changing semantics requires a separately reviewed amendment.
4. Prepare a disabled exact Production deployment with static registration and
   reviewed public keys. The current release has both compile gates false and
   mode FAKE_DISABLED. Do not change them for convenience. Independently verify
   provider build traces include server modules/loader and only the three expected
   public assets, no server credentials/module values. Verify 30-second function
   duration support, headers, single route, no extra endpoint/telemetry/logging or
   Preview activation. Worker affinity is not required; losing a page must deny.
5. Only under separate credential/setup authorization, use the Owner-only Vercel
   Dashboard context to enter STYTCH_PROJECT_ID and STYTCH_SECRET for that exact
   project in Production only. Never Development/Preview or public-prefixed names.
   Never inject from this executor or `vercel env pull` here. No OIDC value belongs
   to the diagnostic input. Variable presence alone cannot activate the service.
6. Treat setting/rotation as requiring a new independently reviewed deployment;
   validate actual dashboard/build/runtime behavior before use. Fixture dry-run
   observations are not evidence of provider env deployment or secret removal.
   A rotated/deleted variable may remain in old deployments. Independently retire
   old deployments and revoke/rotate at the issuer as separately authorized.
7. Live activation is a separate reviewed revision changing both code gates and
   fixed mode, with exact Production registration_generation/application_generation,
   deployment revision, origin and reviewed pin validity. It requires an explicit
   D01 live authorization specifying disposable OTP/TOTP/session effects and
   cleanup. It does not enable Nexus real authority/admission or qualify D04.
8. During future authorized tests, the Owner alone receives/enrolls OTP/TOTP in the
   excluded device. The private seed/recovery channel is a one-use same-origin
   form/HTML flow, not JSON evidence, QR service or screenshot-to-Codex workflow.
   Only sanitized result/error classes are retained. Provider unknown/error means
   retire and reconcile independently; never automatic retry/broader revoke.
9. Cleanup under separate account authority: retire exact test session/factors/
   users, revoke/rotate disposable issuer secret, remove Production variable,
   retire all old deployments with possible custody, then restore reviewed disabled
   source/deployment. Retain generation, deployment IDs, timestamps and verdicts
   without values, hashes of secrets, cookies, JWTs, OTP, raw bodies or dumps.

Stop on missing independent custody/effective denial, unreviewed identity/key/
generation, source/bundle mismatch, unsupported runtime limits, secret exposure,
Preview/unknown tier, unexpected factor/session/provider transformation, missing
authorization or cleanup uncertainty. D01 and D04 remain unqualified until their
exact live/effective evidence gates pass. This addendum releases no actual secret
entry or account mutation; it resolves the offline integration procedure gap only.

```text
READY_FOR_SECRET_CUSTODY_SETUP = YES
OWNER_INDEPENDENT_DEVICE_REQUIRED = YES
CURRENT_EXECUTOR_MACHINE_SECRET_CUSTODY = FORBIDDEN
D04_PRE_SECRET_CUSTODY = CONDITIONAL_OWNER_DEVICE_REQUIRED
D04_EFFECTIVE_EXCLUSION = BLOCKED
SECRET_INJECTION_AUTHORIZED = NO
CREDENTIAL_ACCESS_AUTHORIZED = NO
DEPLOYMENT_AUTHORIZED = NO
LIVE_TESTS_AUTHORIZED = NO
REAL_ADMISSION_ENABLED = NO
```
