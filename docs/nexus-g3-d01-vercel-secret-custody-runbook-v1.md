# Nexus G3 D01 Vercel secret custody runbook v1

2026-10-08. Names-only future Owner procedure. OFFLINE preparation; no account,
credential, dashboard, deployment or provider operation has been performed.

**HOLD: do not inject credentials now.** The companion
[readiness closure](nexus-g3-d01-pre-secret-readiness-closure-v1.md) reports
READY_FOR_SECRET_CUSTODY_SETUP = NO. This document is a conditional procedure,
not authorization to execute it. D04 effective exclusion remains BLOCKED.

## Required independent custody before any secret entry

Use an independent Owner-controlled device/security context, outside this Windows
executor's filesystem, browser profile, automation, remote access and credentials.
Owner must independently verify Stytch and Vercel project/account membership,
deployment authority, function environment read/edit rights and log access there.
The executor must have no role/token/session allowing any of those operations.
Do not merely open another browser on the current executor-accessible machine.

The request reports a Vercel CLI-created `.env.local` containing VERCEL_OIDC_TOKEN
at `D:\chatgpt\deploy\nexus-g3-qual`. This is **USER_REPORTED**, not inspected here.
Do not open, print, hash, copy, upload or use it. An artifact on the executor machine
is no isolation proof. From the independent device, Owner must identify and revoke
or otherwise independently invalidate every executor-accessible credential/role
with deployment/environment/account access, including any reported CLI/OIDC grant.
Deleting a local file alone does not establish remote invalidation. These are
future Owner-only actions requiring account authority; no mutation occurred here.

Move project administration, deployment approval, secrets entry, Stytch Test
administration and qualified Owner browser/factor custody to the excluded context.
Establish an Owner-managed deployment workflow which does not give Codex deployment
tokens, environment download rights, shell/debug rights, logs containing secrets,
browser control or equivalent API routes. Ordinary browser labels and policy text
are insufficient; retain status-only effective-permission evidence later.

## Future configuration procedure, after an explicit readiness release

1. Owner verifies the released code/config revision and native Test project/user/
   application registration from the independent device. Check exact origin
   `https://nexus-g3-qual.vercel.app`, generations, public-key provenance and both
   reviewed activation boundaries. Secrets never substitute for registration.
2. Use the Vercel dashboard's selected project's environment-variable settings
   from that device. Configure **Production only** for this stable diagnostic
   origin. Do not select Development or Preview unless separately qualified and
   authorized. Verify the current dashboard UI and permissions before proceeding.
3. The only proposed server-side credential variable names are:

   - `STYTCH_PROJECT_ID`
   - `STYTCH_SECRET`

   Obtain their values directly from the independently administered disposable
   Stytch Test project and enter them privately in the dashboard. Never put their
   values in chat, Codex, Git, source, screenshots, build arguments, repository
   `.env`, shell history or command-line arguments. Never use NEXT_PUBLIC_, VITE_,
   PUBLIC_ or an equivalent client-export name. Do not run `vercel env pull` on
   this executor. No Vercel OIDC/bypass credential is part of this interface.
4. Treat environment changes as requiring a **new independently reviewed deployment**
   before the changed variables can affect a function. Confirm current Vercel
   behavior and environment selection then; this offline run does not verify the
   dashboard. Deployment itself requires separate authorization. Never enable
   code gates merely because a variable exists. Current code remains disabled.
5. Before any separately authorized authentication, Owner independently verifies
   built client assets contain no variable values or server modules; inspect page
   source, JS bundles, network paths and closed error/evidence keys without
   dumping credentials. A source import scan alone does not prove a deployed
   bundle. Verify no debug endpoint, environment endpoint, header/body logging,
   third-party telemetry, preview bypass or alternate executor route exists.
6. Only after separate exact live-action authorization may disposable OTP/TOTP/
   session tests run. Real Nexus authority/admission remains disabled throughout.

## Retained evidence and cleanup

Retain variable **names**, selected environment, project alias, native non-secret
registration review reference, deployment revision, independent reviewer, timestamp,
permission-test verdicts and sanitized diagnostic error/result classes only.
Do not retain secret values or hashes, Authorization, cookies, JWT/session token,
OTP, TOTP seed/QR/recovery material, screenshots exposing values, raw responses,
stack dumps, dashboard exports or environment downloads. Account identifiers
should be independently protected; sanitized evidence uses registered aliases.

After disposable qualification, Owner uses the independent Stytch administration
surface to revoke the exact test session and retire test users/factors as separately
authorized. Rotate/delete the disposable project secret through that surface,
remove the Vercel variable through its dashboard, retire deployments which may
retain old values, and redeploy a disabled reviewed configuration if authorized.
An environment deletion alone does not prove old deployments lost custody; issuer
revocation/rotation and deployment retirement must be verified independently.
Do not ask Codex to retrieve or delete values. Keep cleanup evidence names/statuses
only. Provider failures and unknown outcomes require Owner-led reconciliation,
not automatic retries or broader-user revocation.

Stop if a UI unexpectedly exposes/copies/logs secrets, the device is accessible to
the executor, permissions cannot be established, a native ID is unregistered,
Preview/Development is selected without qualification, a fixture can enter a
live path, an unreviewed deployment is required, or an authorization is missing.

```text
D01_SECRET_CUSTODY_RUNBOOK = DEFINED
OWNER_INDEPENDENT_DEVICE_REQUIRED = YES
SECRET_INJECTION_AUTHORIZED = NO
CREDENTIAL_ACCESS_AUTHORIZED = NO
DEPLOYMENT_AUTHORIZED = NO
LIVE_TESTS_AUTHORIZED = NO
REAL_ADMISSION_ENABLED = NO
```
