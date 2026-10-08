# Nexus G3 D01 disabled Production deployment Owner runbook v1

2026-10-09, Asia/Kuala_Lumpur. Future Owner-only handoff, not authorization to deploy.
Use the independent Owner phone/device. Do not restore Windows Vercel CLI,
Windows Vercel Dashboard or Windows Stytch Dashboard access. Do not supply any
credential, OTP, TOTP material, cookie or session token to Codex/ChatGPT.

## Before any secrets exist

The exact reviewed source checkpoint is
`3ccdb3d414ac75895361aa1274d560996c6ccd1b`.
The frozen deterministic deployment-source ZIP SHA-256 is
`84796f260303ad64e9982134075a4fadae968c70919d3ffaf17a62be51c78fc3`.
It contains exactly 19 runtime source files. The enclosing Owner handoff has 27
members including source copies, source ZIP, SHA-256 list, manifest and checklists.
**Only the source directory's 19 files form the deployment root.** Do not deploy
the whole handoff, repository, validation directory or an existing local CLI tree.
No .git/.vercel/.env/tests/docs/validation/Route D file belongs in that root.

Owner reports Windows CLI and Dashboard authorization revoked, Stytch logged out,
phone still independent, and STYTCH_SECRET not injected. These are OWNER_REPORTED;
offline preparation has not tested remote invalidation or effective permissions.
Verify from the independent device that the executor has no account/deployment/
environment/debug/log/backup route capable of reading secrets or changing a later
reviewed deployment. If uncertain, retain HOLD and use separate authorized Owner
account review; do not reauthenticate Windows to perform that review.

1. Confirm the available Owner-only deployment mechanism before acting. This run
   does not prove an existing Git-connected project, dashboard upload/redeploy,
   mobile CLI or Git integration. A phone must not be assumed capable of CLI
   deployment or ZIP import. If no exact mechanism is available, stop at that step;
   request a separately reviewed Owner-controlled source transfer/deployment path.
   No executor login, remote push or upload is authorized as a workaround.
2. Obtain the secret-free handoff through an independently approved transfer path.
   Verify the source ZIP hash above and every path/hash in source-manifest.json
   and SHA256SUMS.txt. Keep native Owner identifiers and public pin server-side.
   No secret/private material or account metadata may accompany it.
3. Use a separately authorized Owner-only workflow that deploys those exact bytes
   to **Production only**, with stable origin https://nexus-g3-qual.vercel.app.
   Do not deploy this live-capable source to Preview/Development. Do not use an
   older remote branch or press Redeploy unless source provenance establishes
   that it refers to the exact reviewed 19 files. The local checkpoint was not
   pushed; an existing remote Git integration cannot be assumed up to date.
4. Review deployment input: one function api/diagnostic.js, one application API
   route /api/diagnostic; public assets index.html, app.js, owner-transient.js;
   dependency-free private ESM package, requested Node 24.x; maxDuration 30 seconds;
   no rewrites, redirects or added endpoint. Verify actual runtime/version, account
   duration support and build/function trace independently. All are currently
   OWNER_LIVE_REVIEW_REQUIRED; package.json is a request, not runtime evidence.
5. Ensure **no STYTCH_SECRET is entered, downloaded or injected**. Do not retrieve
   environment values or local OIDC artifacts. Any existing environment/build
   configuration must be reviewed by the Owner without exporting its values to
   Codex. If unexpected secret-bearing state exists, stop. The diagnostic remains
   FAKE_DISABLED with both compile gates false and unregistered OTP routing.
6. Preserve exact headers: no-store, no-referrer, nosniff, frame denial and CSP
   self-only public script/connect/form sources. Application request checks accept
   only the exact stable Host/origin. Global header matching is not wildcard Host
   acceptance. Confirm actual merged platform/function headers and unknown-route
   denial. Do not broaden Host/origin or add redirects to make a Preview URL work.

## Evidence after a separately authorized disabled deployment

Retain only deployment IDs/revisions, source hashes, aliases, runtime/configuration
verdicts and sanitized labels. Do not return dashboards/environment exports,
Authorization headers, cookies, CSRF values, raw browser traffic, credentials,
factor material, session JWT/token, secret hashes or screenshots containing them.

Use POST-DEPLOYMENT-EVIDENCE.json as an **unverified checklist**, not a receipt:

1. Record Production deployment revision/id and independent reviewer/time.
2. Verify stable Production domain and its mapping to that revision.
3. Bind actual uploaded/build source trace to the frozen ZIP and per-file hashes.
4. Confirm exactly one function and its server dependency trace, including protected
   assembly, fixed HTTPS transport, credential loader and pinned input source.
5. Confirm exact application route /api/diagnostic; no extra application endpoint.
6. Confirm three public source assets and actual output trace; no bundled server
   modules, native Owner/project IDs, key provenance or unnecessary public key data.
7. Confirm actual Node runtime/profile is compatible with requested Node 24.x.
8. Confirm actual 30-second function-duration support; stop on unsupported limits.
9. Verify actual security headers, including function JSON overrides.
10. Verify Preview deployments cannot activate live mode.
11. Verify Development deployments cannot activate live mode.
12. Verify unknown/admin/debug/environment routes do not expose a function/secret.
13. Verify no unexpected analytics, telemetry or debug endpoint. Platform-managed
    routes and settings require separate live review; they were not inspected here.
14. Verify public/client output omits server registration and native identifiers.
15. Verify actual public/build output contains no secret-bearing values.
16. Correlate source/trace with hard-disabled credential-loading behavior; dashboard
    variable absence alone does not prove zero credential reads.
17. Verify page/API labels AUTHORITY=NONE, REAL_ADMISSION=DISABLED,
    adapter_mode=FAKE_DISABLED, live_diagnostic_enabled=false and result=DENY.
18. Retain independently supported no-provider-call evidence while disabled.
    An API DENY response or absence of a log entry alone does not prove all these
    build/runtime/permission/side-effect conditions.

Any future page/API inspection is a separately authorized hosted read-only review;
none was performed by Codex in this run. Use only the independent device. Do not
press OTP/TOTP controls, perform session tests or capture factor material. If the
actual build/source/runtime cannot be tied to the reviewed bytes, keep deployment
verification NO and stop before secrets/live operation. Do not mark every checklist
row PASS merely because the disabled page loads.

The browser may receive diagnostic enums/aliases, booleans, bounded diagnostic
timestamps and nullable generation/factor observation fields. The current disabled
API also uses a random Secure/HttpOnly/SameSite Strict page cookie and CSRF transport
field for local page protection; those are not Owner identity or diagnostic evidence.
Keep them out of retained evidence. The static Owner-transient script contains no
TOTP material, and the current disabled API cannot return the future private
Owner enrollment HTML. Its source presence is not an enrollment/authority path.

## Review deadline and prohibited actions

The fixed public-pin review window ends **2026-10-10 00:42:05 Malaysia time**.
Complete disabled deployment/review before that deadline if the pin is intended
to remain current. No reload/restart/redeploy/checklist operation renews it.
If the deadline passes, historical offline hashes/results remain valid, but stop
before secret injection or live activation. Owner must independently re-review
current public JWKS, compare exact keyset/generation and create a new reviewed
provenance record/checkpoint if required. Do not silently extend the timestamp.

This runbook prohibits: STYTCH_SECRET injection, restoring Windows account access,
enabling either compile gate/live mode, OTP/TOTP, live session authenticate/revoke,
provider execution, real receipts/grants/intents/dispatch/admission, remote push
or cloud/account mutation without separate authorization. A disabled deployment
review does not qualify D01/D04 or release secret/live authority.

```text
OWNER_DEPLOYMENT_MECHANISM = OWNER_CONFIRMATION_REQUIRED
ACTUAL_BUILD_RUNTIME_PERMISSION_EVIDENCE = OWNER_LIVE_REVIEW_REQUIRED
SECRET_INJECTION_AUTHORIZED = NO
LIVE_TESTS_AUTHORIZED = NO
CURRENT_EXECUTOR_PROVIDER_AUTHENTICATION = FORBIDDEN
REAL_ADMISSION_ENABLED = NO
```
