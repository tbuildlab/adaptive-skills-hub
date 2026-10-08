# Nexus G3 live qualification setup plan v1

Date: 2026-10-08. **PLANNING ONLY. All live actions below are proposed, not authorized.**
Repository: `D:\chatgpt\安装skills\adaptive-skills-hub`.
Branch: `nexus-v2-g3-live-qualification`.
Source checkpoint: `1316a46804e50984de8a5c1efa5668cfe5863f94`.

Authoritative inputs: [second offline closure](nexus-g3-u1-second-offline-closure-status-v1.md),
[Stytch Principal profile](nexus-g3-u1-stytch-principal-closure-v1.md),
[bounded OwnerContext](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md),
[N01 control state](nexus-g3-u1-n01-protected-control-state-v1.md),
[D03 protocol](nexus-g3-u1-d03-offline-semantic-closure-v1.md),
[D04 fifteen surfaces](nexus-g3-u1-d04-executor-exclusion-and-mediated-dispatch-v1.md),
[N02](nexus-g3-u1-n02-minimal-confirmation-architecture-amendment-v1.md),
[D05](nexus-g3-u1-d05-production-authority-contracts-v1.md) and
[target contracts](nexus-g3-u1-target-dispatch-contracts-v1.md).

## 1. Scope and prerequisite register

Current evidence: D01 candidate mapping CONDITIONAL; D03 deployed enforcement
UNVERIFIED/CONDITIONAL; D04 BLOCKED; real N01/N02 NOT_IMPLEMENTED. Their historical
documents, seven D05 outer bodies and v1 bodies remain unchanged. A DEFINED live
scope is a test specification, not deployment proof, executable readiness or consent.

Use `RUN_ID=g3q-20261008-01` as the proposed disposable run label. It is not an
existing resource or identity. Every case has a pre-registered test-only authority
instance `<RUN_ID>:<case-id>`, workspace `g3q-workspace`, project `g3q-project`,
initial owner_generation=1 and binding_generation=1. No production binding or
Owner identity is enrolled. Never reuse a retired run ID, case prefix or GENESIS.

Owner must complete a restricted **non-secret setup register**, outside production
authority, before the applicable stage. Required exact values: Stytch primary and
negative project IDs; dedicated Nexus application/environment assignment; pinned
native issuer/audience; synthetic native user IDs; selected SDK/version and reviewed
diagnostic image digest; exact HTTPS origin/callback/path allowlist; AWS A/R account
IDs, root/admin custody and role ARNs; region, table/bucket/prefix/backup IDs;
retention acceptance and dates; budget/window; device/browser isolation; and all
candidate target/provider routes. These values are UNSET now. Never infer them from
a checkout name, email, profile label or executor-supplied identity header.

Future diagnostic adapters/harnesses require separate code review and authorization.
This phase neither implements nor deploys them. Existing fake adapters cannot be
promoted into live authority. A live harness may observe managed sessions or exercise
test-only storage, but must expose no real receipt/grant/revocation/admission/dispatch
path. It must preserve fixture classification and log counters proving zero effects.
Storage/identity diagnostics do not qualify an absent real N01/N02 application.

## 2. Future action classification

Labels are cumulative. CODEX_CAN_RUN means *a candidate for a later explicitly
authorized bounded run through protected diagnostic custody*, never current consent
or access to secret values. REQUIRES_CREDENTIAL describes the runtime prerequisite,
not permission to inspect/export it. SAFE_READ_ONLY means a provider read with no
state mutation, and still requires authorization. Authentication/session POSTs are
conservatively classified as mutations; do not call them read-only because duration
extension is omitted. Every matrix case below references these action IDs.

| ID | Exact proposed live action / permitted actor | Classification |
|---|---|---|
| A01 | Owner creates/configures two dedicated Stytch Consumer test projects/application assignments; pins only approved origins | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_ACCOUNT_MUTATION |
| A02 | Owner creates synthetic users, controlled inboxes and TOTP factors; independent administrator records test Owner binding | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_ACCOUNT_MUTATION |
| A03 | Owner manually signs in with email OTP then TOTP on protected device, including deliberate non-Owner sign-in | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_ACCOUNT_MUTATION |
| A04 | Protected diagnostic RP directly calls Stytch session authentication on the retained opaque token | CODEX_CAN_RUN, REQUIRES_CREDENTIAL, REQUIRES_ACCOUNT_MUTATION |
| A05 | Owner/protected issuer operator revokes only an identified disposable session | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_ACCOUNT_MUTATION |
| A06 | Owner performs Nexus-local logout, provider logout/session-end and account/profile switch | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_ACCOUNT_MUTATION |
| A07 | Owner administers disposable binding replacement/user lock/delete and eventual Stytch cleanup | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_ACCOUNT_MUTATION, DESTRUCTIVE_OR_IRREVERSIBLE |
| A08 | Owner/security custodian establishes AWS account separation, roles/trust/boundaries and test-only secret custody | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_ACCOUNT_MUTATION, REQUIRES_CLOUD_RESOURCE |
| A09 | Owner creates approved ledger/bucket/backup/diagnostic runtime/network/audit resources and enables Compliance retention | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE, DESTRUCTIVE_OR_IRREVERSIBLE |
| A10 | Diagnostic observer reads registered account/resource/role/configuration/retention/history metadata | CODEX_CAN_RUN, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE, SAFE_READ_ONLY |
| A11 | Protected test writer performs bounded ledger transactions and independent conditional journal appends/readback | CODEX_CAN_RUN, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE, DESTRUCTIVE_OR_IRREVERSIBLE |
| A12 | Protected harness stops/restarts its own disposable process or discards an acknowledgment at a specified fault point | CODEX_CAN_RUN, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE |
| A13 | Recovery administrator takes one test backup and restores into a new quarantined test table | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE |
| A14 | Recovery custodian seeds bounded fork/gap/extra-version/delete-marker fixtures in a separately registered fault prefix only | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE, DESTRUCTIVE_OR_IRREVERSIBLE |
| A15 | Observer verifies complete independent history and exact snapshot/descriptor joins; no reopen | CODEX_CAN_RUN, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE, SAFE_READ_ONLY |
| A16 | Security observer enumerates registered role/trust/resource/network/image/secret-reference policies and simulates named actions | CODEX_CAN_RUN, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE, SAFE_READ_ONLY |
| A17 | Executor-role harness attempts the exact approved protected read/assume-role requests, expecting service authorization denial | CODEX_CAN_RUN, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE |
| A18 | Executor-role harness attempts bounded write/exec/config mutations on sacrificial canaries, expecting denial | CODEX_CAN_RUN, REQUIRES_CREDENTIAL, REQUIRES_ACCOUNT_MUTATION, REQUIRES_CLOUD_RESOURCE, DESTRUCTIVE_OR_IRREVERSIBLE |
| A19 | Owner independently checks protected browser/device custody and manually drives harmless negative login/presentation cases | OWNER_ACTION, REQUIRES_CREDENTIAL |
| A20 | Harness submits malformed/untrusted proposals, origin/CSRF/replay requests or direct adapter requests to reviewed diagnostic endpoints | CODEX_CAN_RUN, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE |
| A21 | Owner/provider administrator inventories existing provider entitlements and equivalent routes without credential-value disclosure | OWNER_ACTION, REQUIRES_CREDENTIAL, SAFE_READ_ONLY |
| A22 | Operator performs only a documented no-effect provider authorization/dry-run check for the registered exact action | CODEX_CAN_RUN, REQUIRES_CREDENTIAL |
| A23 | Owner stops paid runtimes, revokes diagnostic role sessions and retires diagnostic access after the run | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_ACCOUNT_MUTATION, REQUIRES_CLOUD_RESOURCE |
| A24 | Recovery custodian deletes approved test versions/backups/tables only after retention expiry, evidence export and separate cleanup approval | OWNER_ACTION, REQUIRES_CREDENTIAL, REQUIRES_CLOUD_RESOURCE, DESTRUCTIVE_OR_IRREVERSIBLE |

No action above is performed now. A18 is not harmless just because denial is expected:
unexpected success can mutate a canary and must be preapproved. If an API has no safe
no-effect authorization test, A22 is BLOCKED; never substitute a real provider call.
Read-only observations must not expose credential-bearing API responses. Dangerous
operations that cannot be scoped to sacrificial resources remain untested/BLOCKED.

## 3. D01 Stytch disposable identity environment

### Projects, users and protected relying party

Primary `P_OWNER`: new, dedicated Stytch **Consumer Test** project for one Nexus
qualification application only. Negative `P_OTHER`: separate disposable Consumer
Test project with no shared user/session/application registration. Neither is a
production Stytch project. Pin `https://test.stytch.com`, exact project-bound JWKS,
native issuer `stytch.com/<P_OWNER.project_id>` and audience equal to that exact
project ID under the accepted dedicated-application candidate. Reject the SDK's
alternative base-URL issuer and any other project/audience. If dedicated application
semantics cannot be demonstrated, mapping stays BLOCKED; no Principal relabeling.

Synthetic account inventory, provisioned manually by Owner under A01-A03:

| Alias | Exact role and location | Enrollment rule |
|---|---|---|
| U_OWNER | Native user in P_OWNER; inbox `g3q-owner-<RUN_ID>@<OWNER_CONTROLLED_DOMAIN>` and separate TOTP factor | Sole enrolled diagnostic Owner tuple; real human controls both factors on protected device |
| U_NONOWNER | Different native user in P_OWNER; inbox `g3q-nonowner-<RUN_ID>@<OWNER_CONTROLLED_DOMAIN>` and distinct TOTP | Authenticated but never Owner for the initial binding; may become replacement only in the explicitly authorized replacement case |
| U_FOREIGN | Native user in P_OTHER; inbox `g3q-foreign-<RUN_ID>@<OWNER_CONTROLLED_DOMAIN>` and distinct TOTP | Wrong-project negative; never eligible for P_OWNER binding |

Addresses are naming requirements, not existing mailboxes. Owner fills the real
controlled domain privately; no personal account, production inbox, provider magic
test credential, fixed bypass OTP, impersonation token or admin-created authenticated
session can substitute for actual factor completion. Native user_id, not these
aliases/emails or mutable names, is identity authority. Cross-merge/recreation
continuity is not assumed; changed native ID requires new enrollment.

Use provider-supported [email OTP](https://stytch.com/docs/api-reference/consumer/api/otp/authenticate)
and [TOTP authentication](https://stytch.com/docs/api-reference/consumer/api/totp/authenticate)
as the proposed two-factor diagnostic policy. Owner manually completes both;
protected runtime joins the same user/session and verifies factor timestamps from
the remote session. Both required factors must have last_authenticated_at within
300000 ms; missing/ambiguous factors deny. Verify this combined flow against the
pinned SDK before execution; if unsupported, STOP rather than silently use one factor.
Initial provider session duration is 15 minutes, to make the five-minute local
deadline test meaningful; this duration is never the Nexus authority lifetime.
OTP completion creates that diagnostic session; TOTP completion must attach to the
same retained session_token and native user_id, with the explicit 15-minute login
duration only during this initial factor ceremony. Both factors must be visible
in the ensuing direct remote session response. Missing same-session continuity
blocks the factor-policy case. Later rechecks never repeat factor authentication
or extend that duration. If Test Mode only offers fixed/bypass factor responses,
retain service-protocol evidence only; human authentication remains UNVERIFIED.
Do not switch to a production project to conceal that limitation.

HTTPS origin H must be an Owner-controlled disposable hostname with an existing
or separately approved valid certificate. Register exactly `H/auth/callback` if
the selected SDK flow requires a callback; OTP completion remains server-mediated.
No wildcard origins, HTTP callback, open redirect, forwarded-host identity or
executor-controlled reverse proxy. Local session cookies are Secure, HttpOnly,
same-origin with an approved SameSite policy; private server token custody remains
outside executor. Review CSRF and login transaction correlation explicitly; do
not invent an OAuth/OIDC authorization-code ceremony for Consumer OTP Sessions.

Direct rechecks use `POST /v1/sessions/authenticate` with protected session_token
only; omit session_duration_minutes and custom claims on rechecks. Remote user and
session IDs must match pinned Principal and the same protected context evidence.
Returned JWT may prove exact signed issuer/audience/sub, never current-context
validity by itself. See [direct validation](https://stytch.com/docs/consumer-auth/manage-sessions/validate-session)
and [Authenticate Session](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-session).
The diagnostic context is absolute <=300000 ms, non-refreshable, single challenge,
same lineage only, no cross-restart use. This is a test assertion, not a real receipt.

### Exact identity/session matrix

Each case begins with a fresh, manually authenticated disposable session unless
the test explicitly reuses a stale session. Protected results are observations;
there is no real CONFIRM, grant, AdmissionIntent or DispatchAttempt creation.

| ID | Operation and future action IDs | Required observation / stop outcome |
|---|---|---|
| I01 | Owner completes both factors; verify native claims and remote Session/User equality (A03,A04) | Dedicated issuer/audience/user/session and fresh factors match; no email authority; wrong mapping blocks D01 |
| I02 | Sign in U_NONOWNER under same project (A03,A04) | Authentication may succeed, but diagnostic Owner equality must deny |
| I03 | Use U_FOREIGN session and wrong issuer/audience/project registration (A03,A04) | Remote/identity join rejected; no project substitution or default issuer fallback |
| I04 | Recheck same session at page, decision POST, receipt, intent and claim **simulation points** (A04) | Five fresh remote observations and local generation/deadline checks; no real authority records issued |
| I05 | Advance local deadline to exactly authentication_time+300000; try renewal/restart/cross-challenge reuse (A04,A12) | Exclusive expiry denies even if provider session remains valid; no local refresh or restart resurrection |
| I06 | Local Nexus diagnostic logout, then reuse retained provider session (A06,A04) | Local context retired immediately; remote success does not reverse local retirement |
| I07 | Revoke exact known session_id using provider-supported revoke, then direct recheck (A05,A04) | Session rejected; record elapsed time/error class, not assumed propagation SLA |
| I08 | Provider logout/session-end separately from local logout; check retained session (A06,A04) | Measure actual API result; cookie clearing alone is not issuer revocation. Provider logout UI unavailable -> report that subcase UNKNOWN |
| I09 | Switch U_OWNER -> U_NONOWNER in same protected profile (A06,A04) | Locally observed switch retires prior context before new use; new tuple cannot inherit Owner membership |
| I10 | Switch another profile/tab while leaving old session, and inspect old context (A06,A04) | Record unobserved-switch limitation. No claimed global instant invalidation; point-time check plus bounded context remains explicit |
| I11 | Replace diagnostic Owner/rebind project/increase owner or binding generation (A07,A04) | Old context denied; independent ceremony required; no executor TOFU |
| I12 | Restart diagnostic RP/new incarnation while provider session survives (A12,A04) | Old context/session custody cannot resume; state history retains retirement |
| I13 | Lock then delete one disposable user, with explicit per-case approval (A07,A04) | Observe endpoint-specific behavior; unsupported lock operation UNKNOWN, no invented disable primitive; deleted native ID never re-enrolled by alias |
| I14 | Invalid token, timeout, rate limit, malformed/mismatched response and revoke at t1 after successful remote check t0 before simulated claim t2 (A04,A05,A12) | All unknown/negative evidence denies; race is documented residual, not an atomic external guarantee. Fault injection and real provider results are labeled separately |

Revoke uses the documented [session revoke endpoint](https://stytch.com/docs/api-reference/consumer/api/sessions/revoke-session),
with exact session_id retained privately; no broad user-session revoke. No upstream
federation is used. Upstream federated logout and external roles/workspace membership
are NOT_RELIED_ON, not automatically proven. Missing supported logout behavior is
an evidence finding, not permission to create a lifecycle broker.

Evidence: case ID, observer/runtime/image version, native tuple/session aliases
with restricted lookup, sanitized user/session equality and factor-type/timestamps,
request_id, response status/error class, observation start/end UTC+monotonic times,
local generations, exact expiry/retirement and counters showing zero authority
issuance/effects. Retain no complete authenticate/login response. Observe revocation
at most 20 times at >=3-second intervals in a 60-second window; timeouts never pass.
Cap total remote authentication attempts at 200, login sends at 20, and revoke
calls at 20 for the run; rate limits stop retries, not trigger account expansion.

Never put project secret, Basic Authorization header, session_token/session_jwt,
OTP/TOTP seed/code/recovery code, callback bearer, cookie, inbox password, SDK env
dump, TLS private key or HTTP trace into repo, model context, shell arguments,
logs, screenshot or canonical/EvidenceRef records. Owner injects credentials only
into a reviewed isolated runtime through existing protected custody. Codex receives
sanitized results and secret references, not values. Credential leakage stops the
affected stage and requires an independently authorized incident response.

## 4. D03 AWS disposable recovery environment

### Accounts, roles and registered resources

Two distinct AWS accounts are mandatory: A (ordinary authority/restore domain) and
R (independent recovery custody). Different buckets/roles in A do not satisfy this.
Owner provides exact twelve-digit IDs and independently controlled MFA/admin/root
custody. A's deploy/restore/executor principals must not assume R's recovery admin.
Organization management/root/common identity super-admin paths are declared trusted
custody assumptions and checked for executor reachability. Unresolved transitive
control means separation UNKNOWN and the stage stops. No new account is created now.

Planned region: `ap-southeast-1`, same registered region for A/R resources. A
different region needs an updated approved register and cost review before creation.

| Role / account | Minimum future scope | Exclusion |
|---|---|---|
| G3QualObserver / A | Registered non-secret resource/configuration/audit readback | No secret values, data mutation, deploy, role administration or restore |
| G3QualExecutor / A | Diagnostic untrusted proposal/status only; own test workload identity | No authority/table/fence/secret/deploy/admin/Owner permission |
| G3QualRuntime / A | Fixed diagnostic task role; bounded ledger item operations, Stytch custody and narrowly scoped fence role assumption | No IAM, deploy, table/bucket config, backup/restore or issuer administration |
| G3QualTaskExecution / A | Pull only pinned diagnostic ECR image and write sanitized own log stream | No ledger/fence/session authority or broad secret access |
| G3QualDeployAdmin / A | Owner-controlled image/config/task registration, approved PassRole target only | Never delegated to executor/runtime; no R admin trust |
| G3QualRestoreAdmin / A | One test backup and quarantined restore into an approved new table | Cannot write/delete/select recovery history or open dispatch |
| G3QualFenceAppendRead / R | Conditional object creation under registered checkpoint prefix, exact version/history/retention reads | No delete, unconditional replacement, retention shortening/extension, lifecycle/policy/config/admin |
| G3QualRecoveryAdmin / R | Independently authenticated recovery registration and custody/retention administration | Not assumed by A deploy/restore/executor; no shared session/export |
| G3QualFaultInjector / R | Only pre-approved fault prefixes; seed invalid histories with synthetic bytes | No normal journal prefix or ordinary authority/admin delegation |

Cross-account trust pins the exact runtime role and approved run context, not an
account-wide wildcard; temporary STS credentials stay in runtime custody. Observer
in R has a separately approved read-only history scope, not the append credential.
IAM policy drafts must use actual service-supported actions; DynamoDB transaction
APIs depend on underlying item permissions, not an invented IAM transaction action.
Full effective policy/role graph must be reviewed before any workload session.

| Resource | Exact proposed configuration |
|---|---|
| A ledger | `g3q-ledger-<RUN_ID>`, DynamoDB on-demand, PK/SK strings, single Region, no global tables/DAX/GSI authority/streams; TTL disabled; encrypted at rest; test-only rows/pages/bodies; delete protection managed by Owner |
| A backup/restore | One registered on-demand backup of the pre-fault table; restore name `g3q-ledger-<RUN_ID>-restore-r09`; new table stays quarantined and cannot become a live authority endpoint |
| R journal | General-purpose S3 bucket `g3q-r-<R_ACCOUNT_ID>-<RUN_ID>`; Versioning and Object Lock enabled, bucket-owner enforced ownership, public access blocked, HTTPS required, S3 Standard, SSE-S3 selected for this minimum test |
| R normal prefix | `runs/<RUN_ID>/checkpoints/<case-id>/`; immutable sequence keys `00000000000000000000` onward; exact instance/GENESIS registration per case before faults |
| R fault prefix | `runs/<RUN_ID>/faults/<case-id>/`; separate predetermined instances for fork/gap/extra-version/marker tests; parser uses the same verification algorithm |
| Audit/canaries | Dedicated sanitized log group and CloudTrail operation metadata evidence; separate sacrificial table/objects/image/config/secret-canary resources for denied mutation tests; no production data |

No real v1 grant/revocation or trusted receipt is issued. All retained storage
fixtures are pre-reviewed TEST_ONLY data from the closed sixteen-family model,
with purpose/provenance in the diagnostic registry rather than new fields inside
D05/v1 bodies. Copied fixture bytes are never production-issued membership.

Fixed proposed Object Lock policy: **Compliance, 7 days** bucket default; every
new test version must show exact Compliance mode and retain-until in UTC on readback.
The diagnostic append role cannot set longer/shorter retention or legal holds;
Owner's setup fixes defaults and explicit-retention constraints. No Governance
substitution, bypass privilege, event hold, indefinite legal hold, replication or
lifecycle deletion. No account closure or key destruction as cleanup.

Compliance versions cannot be shortened/deleted while protected, but additional
versions/delete markers remain possible without policy exclusions.
[Object Lock semantics](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html).
Bucket Object Lock cannot be disabled after enabling, and versioning cannot then
be suspended; encrypted history also requires readable key custody.
[Object Lock considerations](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html).
Use enforced conditional `PutObject` with `If-None-Match: *`, valid checksum,
version-aware readback and all-version listing; a conditional write is not itself
a monotonic sequence service.
[Conditional write behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html).

Minimum retained case data: registered GENESIS/head, exact before/after control
rows across all thirteen namespaces, their deterministic pages/root, exact ledger
descriptor, checkpoint bytes/version/checksum/retention, preparation/finalization
markers and all consumption/retirement/tombstone history needed for that case.
Retain image/config/registry revisions, backup identity and independent evidence
of both roles. No full real session response or bearer in storage/backups.

Run caps: 16 cases, <=256 checkpoint object versions total (including fault versions),
<=1024 diagnostic ledger items, <=128 MiB retained synthetic payload, <=80 items
and <=3 MiB per diagnostic transaction (stricter than service limits), no deletion
to free a terminal identity. Closed codec page/root bounds still apply. Stop on
capacity rather than truncate. DynamoDB transactions are database atomicity only;
no DynamoDB/S3 cross-service atomic commit is assumed.
[Transaction constraints](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html).

### Crash / rollback / fork / gap matrix

| ID | Exact future exercise / action IDs | Required fail-closed observation |
|---|---|---|
| R01 | Correct prepare -> conditional append -> version/retention readback -> finalize of synthetic state (A10,A11,A15) | Both stores agree before a diagnostic usable-state acknowledgment; no actual admission |
| R02 | Two writers reserve same next sequence and race conditional append (A11) | One payload wins; loser cannot skip sequence or finalize a different after-state |
| R03 | Stop before ledger prepare (A12,A15) | No usable candidate or effect; no phantom sequence |
| R04 | Stop after prepare, before independent append (A11,A12,A15) | Quarantine; pending reservation blocks another writer; no unilateral reopen |
| R05 | Drop/deny append before completion, including unknown success (A11,A12,A15) | Unknown append acknowledgment quarantines; exact version-aware reconciliation only |
| R06 | Stop after independent append, before ledger finalize (A11,A12,A15) | Witnessed exact descriptor recovered; missing candidate bytes block; no alternative payload |
| R07 | Stop after finalize, before caller acknowledgment (A11,A12,A15) | Durable consumption survives; caller UNKNOWN; no duplicate claim or redispatch |
| R08 | Synthetic revoke/intent/claim interleavings, with crashes on both sides (A11,A12,A15) | Same reservation stream; earlier finalized revoke denies claim; finalized consumption survives later revoke |
| R09 | Restore approved old backup into new table while independent journal remains latest (A13,A15) | Latest complete independent head detects rollback; cannot choose older matching prefix |
| R10 | Seed two versions at one sequence in isolated fault prefix (A14,A15) | Extra version/fork detected even if ordinary latest GET looks valid; quarantine |
| R11 | Seed sequence 0 then 2 with missing 1 in isolated prefix (A14,A15) | Gap detected; no gap-fill invented from restored ledger |
| R12 | Missing page/body/checkpoint, denied history read or marker fixture (A12,A14,A15) | Incomplete independent evidence quarantines. Reader fault injection is not proof of an actual S3 outage |
| R13 | Replay old incarnation/pending context and roll clock backward in synthetic state (A11,A12,A15) | New test recovery epoch required; old context/view/grant/intent retired; consumption preserved |
| R14 | Deterministic page rollover, old registry retention and hard-boundary overflow (A11,A15) | Same hashes for same rows; prior pages/revisions retained; bounds deny instead of unsafe truncation |
| R15 | Shorten/delete protected canary version and test append role delete/config/retention exclusion (A10,A18) | Valid authorized-canary attempt obtains service denial; no root/account-deletion experiment |
| R16 | Restart stale writer after reservation/epoch change and attempt finalize; exercise quarantine-only reconciliation (A11,A12,A15) | Head/version checks reject stale writer; lease timeout alone cannot resume authority |

Never corrupt the normal journal to manufacture a PASS. Fault fixture creation
is independently authorized and registered before use; normal append restrictions
stay fixed. Direct S3 responses, harness fault injection and application-model
assertions receive distinct evidence labels. Passing primitive tests cannot stand
in for missing deployed recovery code, trusted time, leadership or D04 exclusion.

### Cost, retention and cleanup gates

Proposed active window: <=24 hours, with up to 7 days retained versions **after the
last object write**, not seven days from bucket creation. Proposal: USD 25 spend
ceiling with alert thresholds USD 5/15/25, subject to Owner-approved regional
estimate. This is a proposed cap, not a quote, spend authorization or automatic
billing cutoff. AWS Budgets alerts are not hard transactional spending limits.
An independent operator stops new work when estimates/counters approach the cap.

Estimate before creation: DynamoDB transactional reads/writes/storage and backup/
restore; S3 storage/all versions/PUT/GET/LIST/retention metadata; plus Fargate, image,
logs/audit, ALB, data transfer and any VPC/NAT/endpoints/secret custody used in D04.
Do not assume free tier or omit continuously billed infrastructure. Refer to
[DynamoDB pricing](https://aws.amazon.com/dynamodb/pricing/),
[S3 pricing](https://aws.amazon.com/s3/pricing/) and
[Fargate pricing](https://aws.amazon.com/fargate/pricing/) for the approved Region;
ALB/NAT/other line items require fresh estimates if selected. No exact total is
claimed without actual account eligibility/configuration.

At run end, close diagnostic access and stop paid compute/load balancers that are
no longer needed under A23, preserving readback/evidence availability. Retire all
test authorities before retention expires; this seven-day disposable profile is
not production-lifetime protection. No retention extension without new approval.
Custodian records the maximum per-version retain-until and funds the waiting period.
After expiry and separate A24 approval, enumerate every version/marker, export the
sanitized audit, delete approved test data/backups/tables, then empty/delete bucket
where permitted. Never try to shorten Compliance retention, force-delete, close
the account, destroy encryption custody or silently abandon retained billable data.

## 5. D04 exclusion and complete-mediation environment

The Owner uses an independently controlled physical device/browser unavailable to
Codex/executor shell, screen, browser profile, extension, sync or remote-control
capabilities. A second profile on the current executor-controlled Windows machine
is insufficient. No hostile local probing or credential discovery is a test.
Owner logs into issuer/admin consoles only on that protected device; deployment
and recovery administrators use separately controlled MFA sessions. Neither
session/credential is handed to the executor or diagnostic agent.

Future N01/N02 diagnostic runtime is one reviewed fixed-image Fargate task with
G3QualRuntime, dedicated task-execution role, private task network, no executor
sidecar/mount, ECS Exec disabled and fixed HTTPS ingress (ALB/ACM only if separately
approved). N02 only displays diagnostic fixed material; it has no release authority.
Image/config/env/secret references, DNS/certificate/listener/origin and task identity
are controlled by excluded administrators. A changed digest/generation retires
affected test context. Actual N01/N02 application qualification remains blocked
until real code is separately reviewed; an imitation page is not that proof.

Executor is G3QualExecutor plus an isolated ordinary test workload/device, never a
cloud admin or RP observer credential. Credentialed diagnostic actions run in
separate named least-privilege harness roles; results are sanitized to Codex. An
operator who can silently impersonate both executor and admin is an unqualified
boundary. Provider credential custody uses existing protected runtime storage,
with executor excluded from value retrieval, minting, delegation and equivalent
console/login paths. No real provider credential is provisioned for this setup
plan or required for the initial canary stage.

### Fifteen surfaces: forbidden permissions and exact denial evidence

For each denial request, retain exact caller role/session alias, registered ARN/
endpoint, operation, non-secret arguments/hash, request_id, service authorization
error, timestamp, policy/config revision and relevant audit-event reference.
Intended-role control must prove the target exists and the valid request is
recognized. 404, bad syntax, validation failure, missing credentials, timeout or
simulator DENY alone is not effective-denial proof. No retry with a stronger role.

| ID | Executor permissions explicitly forbidden | Exact future test / action IDs |
|---|---|---|
| X01 | Owner device/profile/DOM/cookie/process/debug/extension/sync/remote control and driving consent | Owner independently attests device custody and registered login origin; manual harmless cross-origin/replay attempts fail. No scan of Owner filesystem (A19,A20) |
| X02 | Read/export/replay or substitute Stytch session bearer, cookie, network header or callback secret | Canary custody read as executor denied; fake bearer at diagnostic RP rejected; sanitizer drops all bearer fields. Actual token values never sent to Codex (A17,A20) |
| X03 | Stytch project secret/dashboard/admin/user/session impersonation/rotation | Owner checks admin memberships and server-secret scope; executor canary secret access denied. No deliberate real project-secret read or admin mutation (A16,A17,A19) |
| X04 | Runtime code/memory/env/filesystem/shell/privileged endpoint/forged identity-header control | Wrong-role endpoint and forged-header requests reject; task access rules plus safe canary debug denial; no admin exec into token-bearing runtime (A16,A17,A18,A20) |
| X05 | ECR/image tag/digest, build runner, deployment/task/config/env/secret-reference writes | Attempt PutImage/UpdateService/RegisterTaskDefinition only against approved sacrificial clone; valid request must be denied. Actual immutable deployment digest independently read (A16,A18) |
| X06 | Authority DynamoDB Get/Scan/Query/item writes/delete/batch/transaction/export/backup/restore/table repoint | Attempt protected test item GetItem and bounded PutItem/UpdateItem/DeleteItem/transaction on sacrificial resource using actual executor role; authorized controls prove recognition. No actual authority mutation (A17,A18) |
| X07 | Recovery S3 Get/List/Put/Delete/DeleteVersion/marker/retention/legal-hold/bucket policy/lifecycle/config/key custody | Exact registered read denial; bounded write/delete/config canary requests denied. Read back separate-account caller/resource identity and Compliance versions (A10,A17,A18) |
| X08 | Transitive sts:AssumeRole into admin/runtime/fence/restore/issuer/provider custody; iam:PassRole, role/policy/identity delegation | Named AssumeRole requests denied; PassRole tested through a valid sacrificial service operation, plus complete trust/SCP/boundary/session/resource-policy graph. No privilege expansion (A16,A17,A18) |
| X09 | Provider secret Read/mint/rotate/delegate; inherited provider/API/console/browser login capable of same action | Canary secret value retrieval denied; Owner inventories all real entitlement locations without values. Real credential custody stays UNVERIFIED until exact provider integration is qualified (A16,A17,A21) |
| X10 | Direct dispatch invocation, copied claim as bearer, alternate handler, arbitrary target/payload and claim replay | Diagnostic direct-release requests and copied fixture claims rejected; no effect-capable adapter attached. Real adapter proof remains pending (A20) |
| X11 | Backup/export/restore/import/table alias/head selection/tombstone deletion or recovery authority | Executor valid restore/export canary request denied; separately authorized R09 restore remains quarantine. No recovery approval by executor (A13,A17,A18) |
| X12 | DNS/TLS/certificate/listener/ingress/proxy/origin/callback configuration and identity through forwarded headers | Valid sacrificial DNS/ingress update denied, protected config readback; bad Host/Origin/CSRF/callback/replay requests rejected (A16,A18,A20) |
| X13 | Equivalent direct provider API/CLI/console/browser/plugin/subprocess/alternate credential or delegated route | Enumerate action/account/tool/network/credential routes. Use documented no-effect provider check only if available; any allowed equivalent route or unknown route blocks complete mediation (A16,A21,A22) |
| X14 | ecs:ExecuteCommand, SSM/debug attach, privileged/host access, runtime task-role token discovery or proc/memory inspection | Valid ECS Exec request on a credential-free sacrificial task with Exec enabled solely for this test, expected authorization denial; intended-role control proves operation availability. Independently verify protected task Exec=false and no host/mount path. Exec-disabled InvalidParameter is not denial evidence (A16,A18) |
| X15 | Sensitive logs/dumps/APM/telemetry/raw requests/env/session response and export/config control | Sentinel redaction cases across success/error/crash paths; executor log/export canary access denied; no real token dumps generated (A16,A17,A18,A20) |

Canary negatives prove only the tested resource/policy scope. Cross-compare exact
protected resource policies and all condition contexts. Do not infer actual secret,
deployment, restore or provider exclusion solely from a similarly named canary.
If effective testing of a protected surface would expose a secret or mutate it on
unexpected success, do not test it; retain UNKNOWN/BLOCKED until a separately
approved safe diagnostic is available. Policy simulation helps coverage but does
not perform a real service request.
[IAM simulator limitation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_testing-policies.html).

Complete mediation target remains:

```text
executor -> untrusted proposal -> N01 -> durable consumed claim
         -> protected exact-material dispatch adapter -> exact registered action
```

Before X13 can close, the Owner must select one exact provider/account/action,
qualified Subject-specific contract, adapter revision and environment/enforcement
profile. NONE is registered at this checkpoint. A generic list of APIs, unavailable
provider or fake adapter is not proof. Inventory includes this Codex Host's tools,
plugins/browser/session inheritance and any executor credential/egress route,
without inspecting secrets. A no-effect action authorization check is allowed
only under later separate authorization; if provider lacks one, real-effect testing
requires a further scope and remains BLOCKED here. No test manufactures a real
grant/receipt/claim to drive a provider.

## 6. Qualification order and acceptance gates

Required order: **D01 -> D03 -> D04**. All three start NOT_RUN, not VERIFIED.

1. Owner completes global and D01 checklist plus separate scoped authorization.
   Perform only identity/session observations. Pass requires exact candidate
   application/principal/factor/current-context evidence; a fake login cannot pass.
   Basic protected Owner/diagnostic custody is prerequisite safety, not D04 completion.
2. Only after D01's accepted evidence gate, authorize D03 resource/custody setup
   and the bounded storage matrix. Primitive and harness evidence are distinguished;
   do not certify absent N01/D03 implementation. Stop the affected case on uncertainty.
3. Only after D03's accepted evidence gate, run D04 policy/canary/effective exclusion
   tests on the exact candidate deployment. D04 remains BLOCKED wherever actual
   runtime/provider/alternate-route proof is absent. A different harness/image or
   permissions revision invalidates any inference to the eventual application.
4. Produce a bounded qualified/unqualified report per case, with independent Owner
   review. No checklist, test PASS or all-three completion automatically authorizes
   real N01/N02 implementation, receipt acceptance or real admission activation.

Repeated login/resource creation/retry/fault writes beyond the approved counters
need new authorization; do not expand the account, factor or cloud topology to
avoid a blocker. Prior stage BLOCKED stops dependent live work; unrelated future
read-only documentary review may continue.

## 7. Manual Owner preparation checklist

Nothing below is marked complete. Before **any** Codex live diagnostic, O01-O10 and
the applicable stage items must be completed and evidenced, then that stage must
receive separate explicit authorization. D03 resource creation need not occur
before D01 succeeds; avoid spending merely to prepare an unqualified dependency.

- [ ] O01 Confirm disposable run identity, exact source/image scope and no production data, bindings, grants or effect paths.
- [ ] O02 Provide protected Owner device/browser, inbox and authenticator unavailable to executor/Codex control.
- [ ] O03 Identify independent issuer, deploy/security and recovery custodians; confirm none is delegated to executor.
- [ ] O04 Approve exact test IDs/action IDs, permitted callers, request counters, time window, unexpected-success handling and stage order.
- [ ] O05 Approve regional cost estimate, spend cap/alerts/operator stop responsibility, seven-day Compliance risk and funded cleanup custody.
- [ ] O06 Supply non-secret exact setup register; resolve every required UNSET field for the applicable stage, never paste secrets.
- [ ] O07 Prepare existing protected credential injection and result-only access; prohibit raw responses/HTTP traces/env dumps and secret screenshots.
- [ ] O08 Review diagnostic harness source/image digest and disable real receipt/grant/revocation/provider/admission paths; fake adapters cannot be promoted.
- [ ] O09 Prepare restricted evidence export, sanitizer/sentinel checks, retention dates and independently controlled audit readback.
- [ ] O10 Give a later explicit stage-specific authorization naming resources, credential-use scope and mutations; this plan is not that authorization.
- [ ] O11 For D01, manually create/configure P_OWNER and P_OTHER, dedicated application/origin/native issuer/audience registers, and controlled synthetic inboxes.
- [ ] O12 For D01, manually create U_OWNER/U_NONOWNER/U_FOREIGN, enroll distinct TOTP factors and exact test Owner tuple through independent ceremony.
- [ ] O13 For D01, manually sign in on protected device and authorize exact logout/revoke/account-switch/lock/delete cases; never disclose bearer/factor values.
- [ ] O14 For D03 after D01 gate, prepare distinct A/R accounts, exact role/trust graph, independent recovery/root custody and region permissions.
- [ ] O15 For D03, manually create approved table/bucket/default Compliance/audit resources, register all normal/fault prefixes and supply sanitized config evidence.
- [ ] O16 For D03, authorize backup/new-table restore, fault fixtures and bounded immutable writes; schedule retirement and post-expiry separately approved cleanup.
- [ ] O17 For D04 after D03 gate, prepare pinned runtime/ingress/deployment identities and sacrificial canaries with exact policy comparisons and denial-test controls.
- [ ] O18 For D04, enumerate every exact provider/action/credential/Host/plugin/network route; supply a reviewed no-effect diagnostic or leave provider mediation BLOCKED.

## 8. STOP and evidence rules

Current STOP is unconditional before any provider login, credential retrieval/use,
Stytch/AWS resource creation, IAM/account mutation, deployment or live diagnostic.
There is no permission request embedded as an execution directive. Later scoped
runs additionally stop on unresolved setup IDs, wrong account/region/project,
shared Owner/executor custody, absent approved factor support, unexpected privilege
success, secret leakage, unknown provider transformation/route, unproved independent
history/retention, costs beyond the cap, missing reviewed harness or any real
authority/effect request. Remediation, rotation, extension, teardown or activation
is separately authorized; no automatic security/account changes.

Use case labels DOCUMENTED_CAPABILITY, LIVE_SERVICE_OBSERVATION,
HARNESS_FAULT_INJECTION, MODEL_ASSERTION and DEPLOYMENT_UNVERIFIED distinctly.
Keep sanitized case results, exact request/response classes, policy/image revisions,
resource aliases and audit hashes in protected run custody; repo may receive a
reviewed secret-free report only. Request credentials, sessions and factor material
never enter an evidence hash dump or canonical record. A false/simulated denial,
SDK presence or passing offline test cannot be called live qualification.

This deliverable is documentary only. Static validation checks required fields,
24 classified actions, 14 identity cases, 16 recovery cases, all 15 D04 surfaces,
18 Owner preparation items, links, prior bytes and manifest packaging. No N01/N02
or live harness implementation, credential access, account/policy mutation, cloud
creation, deployment, live test, real grant/revocation or provider effect occurs.

Offline validation completed for this deliverable:

- `python -B state/g3-live-setup-plan-20261008/verify_plan.py verify`: PASS;
  required fields, matrix/checklist counts and 362 pre-existing non-manifest paths
  preserved byte-for-byte, including accepted code/contracts and unrelated files.
- `python -B state/g3-live-setup-plan-20261008/verify_plan.py manifest`: PASS;
  unchanged builder, deterministic 359-entry manifest, all 358 previous entries
  preserved and only this plan added. Existing sensitive-path exclusions remain.
- `D:\DevTools\NexusR2Python\Scripts\python.exe -B -m unittest tests.test_ecosystem_isolation_package`:
  11 tests PASS on the isolated manifest-source snapshot, with bytecode disabled.
- `git diff --check`: PASS. HEAD remains the source checkpoint; main and development
  refs remain unchanged. Only this document and MANIFEST.json belong to this change;
  three pre-existing unrelated Route D documents remain untracked. Nothing staged
  or committed. Ignored validation/snapshot artifacts are outside the deliverable.

```text
LIVE_SETUP_PLAN = DEFINED
D01_LIVE_SCOPE = DEFINED
D03_LIVE_SCOPE = DEFINED
D04_LIVE_SCOPE = DEFINED
OWNER_PREPARATION_REQUIRED = YES
LIVE_TESTS_AUTHORIZED = NO
CREDENTIAL_ACCESS_AUTHORIZED = NO
CLOUD_CREATION_AUTHORIZED = NO
REAL_ADMISSION_ENABLED = NO
```
