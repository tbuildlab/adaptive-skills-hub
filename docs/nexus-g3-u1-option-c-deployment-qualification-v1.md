# Nexus G3 U1 Option C deployment qualification v1

Date: 2026-10-08. Scope: concrete candidate qualification through public primary
documentation and local contract inspection only.

Authoritative design input: the accepted
[minimal authority architecture v1](nexus-g3-u1-minimal-authority-architecture-v1.md),
raw SHA256 `4d0f7b791882fe9618c97c6b744270292a020dbacad6b24863a9896e8e742b9c`.
Source checkpoint: `571bfc872873cb361361ab2c66ed59e591067ac1`,
branch `nexus-v2-g3-development`.

```text
OPTION_C_CONCRETE_STACK = DEFINED
D01_IDENTITY = CONDITIONAL
D02_HOST_CONFIRMATION = BLOCKED
D03_RECOVERY_FENCE = CONDITIONAL
D04_EXECUTOR_EXCLUSION = BLOCKED
D05_PRODUCTION_DECISION_SEAM = BLOCKED
CONCRETE_N01_RUNTIME = AWS_ECS_FARGATE_SINGLE_AUTHORITY_TASK_PROPOSED
CONCRETE_AUTHORITY_STORE = AMAZON_DYNAMODB_SINGLE_REGION_TRANSACTIONAL_TABLE_PROPOSED
CONCRETE_RECOVERY_FENCE = SEPARATE_ACCOUNT_S3_OBJECT_LOCK_COMPLIANCE_CONDITIONAL_CHECKPOINT_JOURNAL_PROPOSED
CONCRETE_N02_HOST_SURFACE = CODEX_NATIVE_COMMAND_APPROVAL_UI_UNQUALIFIED
LIVE_QUALIFICATION_REQUIRED = YES
U1_IMPLEMENTATION_CANDIDATE_READY = NO
```

`DEFINED` identifies a concrete proposed stack, including its unavailable seams;
it does not identify a fully qualified deployment. The AWS combination is a
candidate for later investigation, not permission to provision resources, enroll
an Owner, implement N01/N02, or start an admission service. D02, D04 and D05 prevent
an implementation-ready conclusion. No complete blocker is verified in deployment.

## 1. Evidence rules and unchanged safety boundary

| Classification | Meaning |
|---|---|
| VERIFIED_CANDIDATE | Official documentation establishes the specified primitive and it fits a bounded candidate role. This does not mean an actual resource, permissions, integration or deployment was verified. |
| CONDITIONAL | Concrete primitives are documented, but a required combination, access entitlement, configuration or fault guarantee must be qualified. |
| UNKNOWN | Current evidence cannot establish the claimed property or actual availability; this does not establish absence or impossibility. |
| BLOCKED | A mandatory integration/contract/enforcement prerequisite is missing or unqualified, so dependent work cannot proceed. |
| NOT_SUITABLE | The candidate in the exact stated mode fails the required role or existing contract; a different explicitly reviewed mode may differ. |

For every component, documented capability and verified deployment capability
are separate columns or attributes. Public documentation was read; no customer
cloud console, account APIs, IAM policy, credential store, Host approval request,
issuer registration or provider execution was accessed. All actual account IDs,
user-pool/client IDs, runtime images, table ARNs, bucket owners, domain names,
effective policies and region access remain `UNKNOWN`.

The candidate must retain the architecture's exact Owner/project mapping, complete
effect presentation, five-minute approval challenge, at most ten-minute grant,
exact task/scope/account binding, one intent/claim, current session/context,
protected state, recovery quarantine and all G1/G2/task/Host restrictions.
Positive action must wait for durable ledger and independent fence acknowledgment.

Local facts were inspected in [authorization](../ash/g3_authorization.py) and
[the offline bridge](../ash/g3_host_approval_bridge.py): public eligibility remains
fail-closed; positive decisions are fixture-only; candidate evidence is
`OFFLINE_CONTRACT_ONLY`, `owner_authenticated=false`, with no approval or dispatch
authority; the v1 native request is `item/commandExecution/requestApproval`.
No changes to those facts or canonical bodies are made here.

The accepted [Host qualification report](nexus-g3-u1-host-authority-qualification-v1.md)
is historical evidence of unresolved access and authority, not proof that a
product cannot ever support an integration. Current official OpenAI documentation
was revisited using the OpenAI Docs skill. Other products use their own primary
documentation. Proposed composition rules below are engineering requirements,
not guarantees supplied automatically by their vendors.

## 2. Concrete proposed Option C stack

Use two logical AWS security/custody accounts: **AuthorityAccount** for N01 and
its table, and **RecoveryAccount** for the fence. These are proposed administrative
domains, not existing resources or invented account IDs. A protected Owner/Host
device/context and the untrusted executor are separate from both domains.
No new general IAM, OAuth provider, PKI, approval platform, vault or policy engine
is proposed. Only the accepted N01 and N02 are future new Nexus trusted code.

| # | Required layer | Proposed technology / mode | Candidate classification | Verified deployment capability |
|---|---|---|---|---|
| 1 | External identity issuer | Amazon Cognito user pool, managed login, registered OIDC authorization-code/PKCE client; fixed issuer/client/`sub` binding. OpenAI Sign in with ChatGPT remains a reuse alternative if entitlement is established. | CONDITIONAL | UNKNOWN: no pool, app client, Owner principal or OpenAI entitlement inspected. |
| 2 | Protected Owner confirmation surface | Existing Codex native command-approval UI with a future protected N02 integration that captures explicit Owner confirmation before releasing the native action. Cognito managed login supplies identity only. | BLOCKED | UNKNOWN: no qualified native UI callback, exact presentation, session/context binding or delayed-dispatch hook. |
| 3 | N01 runtime | AWS ECS on Fargate; one protected authority task, fixed reviewed image/dependency digest, private task network, no executor code or executor sidecar. | VERIFIED_CANDIDATE for task isolation / role primitives | UNKNOWN: no task, image, role, network or restart behavior inspected. |
| 4 | Transactional authority store | Amazon DynamoDB, one Region and one authoritative table; `TransactWriteItems`/`TransactGetItems`, conditional control/generation item; no global tables, DAX, positive decisions from GSIs or TTL deletion of authority history. | VERIFIED_CANDIDATE for bounded transaction primitives | UNKNOWN: no table, configuration, effective permissions or recovery evidence inspected. |
| 5 | Independent rollback/recovery fence | RecoveryAccount S3 general-purpose bucket: Versioning, Object Lock **Compliance** retention, create-only sequence checkpoint objects using enforced `If-None-Match: *`, version-aware reads and fixed protected bucket/root registration. | CONDITIONAL | UNKNOWN: the complete append/freshness/recovery protocol and independent administrative boundary need live qualification. |
| 6 | Protected dispatch adapter | Bounded function inside N01 using the existing reviewed OpenAI managed route only after durable claim; fixed payload/environment; application authentication outside executor; uncertain outcomes consume the attempt. | BLOCKED | UNKNOWN: current G2 acceptance does not qualify remote N01 custody, every equivalent route or exact-effect enforcement. |
| 7 | TLS / service authentication | Public HTTPS via Application Load Balancer and ACM-managed certificate; private ALB-to-task network is explicitly within the trusted VPC boundary; AWS service calls use HTTPS and restricted IAM task-role credentials/SigV4. N01 validates Owner/session authentication, not caller-supplied identity headers. | CONDITIONAL | UNKNOWN: no certificate, hostname, ingress, network or token validation deployment inspected. |
| 8 | Deployment identity and executor exclusion | Separate ECS task role and task execution role; separate deployment and recovery roles; executor gets none of them, no cloud console profile, no store/secret access and no `iam:PassRole`/ECS Exec/deployment route. | CONDITIONAL primitive; complete D04 BLOCKED | UNKNOWN: no actual principals, permissions, Owner-device isolation or direct-route exclusions verified. |
| 9 | Backup/recovery administration | DynamoDB recovery/export mechanism as backup only; RecoveryAccount retains independent checkpoints; separately authorized recovery administrator restores only into quarantine and compares full authoritative history. AWS Backup Vault Lock is an optional backup-retention alternative, never the generation fence. | CONDITIONAL | UNKNOWN: no backup schedule, retained checkpoint chain, recovery account or restore procedure verified. |

A proposed initial Region is AWS Singapore (`ap-southeast-1`), subject to a later
check of account-enabled Regions, service support, residency and concrete resource
settings. No Region/resource availability, price, SLA or existing customer
subscription is claimed. Region and account selection must not be supplied by
an executor-controlled project file.

Fargate documentation identifies a task isolation boundary and distinguishes
task roles from the role used to launch/pull images. A task role is readable by
code within its task; therefore the executor must never share N01's task, including
as a sidecar. [ECS task roles and isolation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html).

DynamoDB documents all-or-nothing transactional operations. The selected mode
must fit its transaction limits and preserve conditional joins; choosing its name
does not implement revoke/admit ordering. [DynamoDB transactions](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html).

ACM integrates certificates with ALB. This candidate does not claim TLS termination
authenticates the actual Owner or attests N02, nor does it claim encryption of
the private HTTP hop. If the approved threat model requires authenticated TLS
through that hop, the transport choice must be requalified before readiness;
do not quietly introduce a private CA. [ALB certificates](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/https-listener-certificates.html).

## 3. Blocker qualification register

### D01. Qualified identity access

| Attribute | Qualification |
|---|---|
| Candidate technologies | OpenAI Sign in with ChatGPT; Amazon Cognito user pool / managed login as the mainstream managed alternative. |
| Classification | **CONDITIONAL** overall. Cognito's issuer primitive is a VERIFIED_CANDIDATE; OpenAI access for Nexus is UNKNOWN, so OpenAI-only deployment is BLOCKED without entitlement. |
| Documented capability | OpenAI documents verified issuer/client/`sub`; Cognito documents a signed ID token, issuer/audience, `sub`, authentication time and nonce, plus managed login. Neither issuer assigns ownership of this Nexus project or signs an exact capability approval. |
| Verified deployment capability | UNKNOWN. No registered client, pool, authenticated Owner, approved callback, MFA setting, federation, sign-in or active session was inspected or tested. |
| Exact trust boundary | Issuer authenticates an account; protected N02/Owner context holds its identity transaction; N01 verifies issuer/JWKS/algorithm/audience/token-use/time/nonce and resolves a protected exact Owner/project mapping. Email, Host profile labels and JWT content supplied without verification are not authority. |
| Executor permissions | No Owner credentials, identity tokens, session cookies, PKCE verifier, callback control, user-pool admin role or Owner process/browser control. Public issuer metadata and an untrusted proposal may be readable. |
| Owner permissions | Sign in through the issuer's existing UI, complete issuer authentication/MFA, and later explicitly confirm the exact binding/approval through qualified N02. No table, fence or deployment-write permission follows from login. |
| Admin permissions | Registered-client/issuer configuration and approved enrollment/recovery administration only through separately trusted existing admin identities. No automatic Nexus Owner promotion from being an AWS administrator or matching an email. |
| Recovery semantics | Restore neither tokens nor authority from a browser backup. Reauthenticate and validate the current binding against independent protected history; changed issuer/client/subject or pool replacement requires explicit reenrollment. |
| Failure semantics | Invalid/stale tokens, unknown entitlement, issuer outage, context change, missing lifecycle proof or shared executor/Owner context deny. JWT signature/expiry alone cannot prove immediate logout, account-disable or relevant role-removal invalidation. |
| Required credentials/secrets | Owner's issuer login/MFA stays with the existing issuer/Owner. Registered client ID is metadata; a public PKCE client needs no client secret. Authorization code, PKCE verifier, identity/access tokens and Nexus session are protected transient secrets. A confidential-client secret, if selected later, stays in protected custody. None accessed. |
| Later live qualification | YES: availability, real principal and binding, callback origin, nonce reuse, account switch, sign-out/disable and lifecycle enforcement must be tested in a separately authorized isolated context. No grants/provider actions are needed for the initial identity test. |

OpenAI identity documentation supports stable external identity and verification
checks. Its plugin identity flow is limited to selected partners and contains
separate identity and connector authorization transactions. Do not build a custom
connector OAuth provider to obtain that flow.
[OpenAI website identity](https://developers.openai.com/siwc/website),
[OpenAI plugin identity availability](https://developers.openai.com/siwc/chatgpt-plugin).

Cognito is a managed issuer with an existing login surface; the proposed Nexus
code is only a relying party, not an identity provider. User-pool `sub` is the
documented account identifier; include the issuer and app client and verify the
token. A short token expiry does not force a fresh human login when a managed
login cookie remains valid. [Cognito authentication modes](https://docs.aws.amazon.com/cognito/latest/developerguide/authentication-flows-public-server-side.html),
[Cognito ID token](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-id-token.html).

Revoked Cognito tokens can still pass offline JWT signature/expiry validation.
The managed logout endpoint does not sign out external OIDC/social issuers.
Consequently, short TTL or `/logout` alone does not satisfy the architecture.
[Token revocation](https://docs.aws.amazon.com/cognito/latest/developerguide/token-revocation.html),
[managed logout](https://docs.aws.amazon.com/cognito/latest/developerguide/logout-endpoint.html).

An online `GetUser` check is a concrete candidate for detecting invalid token use;
it requires the user's access token and `aws.cognito.signin.user.admin` scope and
does not use IAM authorization. That scope also serves user self-service, so it
must remain outside the executor. This check is not proof of every Host account
switch or group-removal event, nor an atomic check with later dispatch. Protected
Host lifecycle observation and serialized context invalidation are still required;
their ordering is part of D02/D04 qualification.
[GetUser](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_GetUser.html).

### D02. Trusted Host approval confirmation integration

| Attribute | Qualification |
|---|---|
| Candidate technologies | Existing Codex native command approval UI / app-server command approval transport; MCP `openai/form` elicitation as an alternative interaction primitive only. |
| Classification | **BLOCKED**. Native command UI is the proposed surface; exact protected integration is UNKNOWN. Form elicitation is NOT_SUITABLE as a drop-in replacement for the current v1 command bridge. |
| Documented capability | Host can present command approvals and accept client responses. MCP form/URL elicitation is documented. These docs do not establish a Nexus-verifiable, actual-human callback bound to full canonical proposal/effects, current Owner identity and delayed dispatch. |
| Verified deployment capability | UNKNOWN. No prompt opened, Host/app-server started, UI configuration changed or protected callback/display/hold behavior tested. Current task permits no such live actions. |
| Exact trust boundary | N01 freezes proposal/target bytes and nonce; N02 must show those exact effects in the existing trusted Owner UI, bind the verified identity/context, capture explicit acceptance and obtain N01's durable disposition before the pending native action can run. A transport client under executor control cannot be this writer. |
| Executor permissions | Submit untrusted proposal/event/candidate material only. No native response write, Owner UI automation/injection, session/callback access, effect substitution or native-action release. |
| Owner permissions | Inspect full workspace/project, Subject, scope, targets and effects; explicitly accept/deny that one challenge through qualified existing Host UI. Cognito login or chat text is not that acceptance. |
| Admin permissions | Install/pin/protect N02 and the existing Host integration; restrict prompt/response/lifecycle transport and automatic-review policy through separately authorized existing controls. Admin deployment is not Owner consent. |
| Recovery semantics | Retire pending UI requests after restart/recovery/context switch; new challenge and explicit confirmation required. No replay from saved transcripts or copied responses. |
| Failure semantics | Missing origin/display/identity join/hold hook, automatic review, timeout, clearing, session approval or policy amendment denies. If native approval releases an effect before N01 claim/fence completion, the integration is unsuitable. |
| Required credentials/secrets | Protected Owner identity/session material from D01; protected Host account session and transport access, held only in the Owner/Host context. No new receipt-signing key or PKI is proposed. Actual credential/profile access is NONE. |
| Later live qualification | YES, only after a documented integration route is identified: forged caller, hidden/substituted effects, auto/timeout/clear handling, lifecycle invalidation and prevention of action release before the gate. Use a non-effectful diagnostic route; creating a dummy approval never creates a real grant. |

The app-server approval flow normally resumes work after the client answers.
It also documents clearing and form elicitation. That interaction is insufficient
to assert a separate Nexus admission barrier. A protected pre-response hook,
exact display and gate-controlled release must be demonstrated, not inferred.
[App-server approvals and elicitation](https://learn.chatgpt.com/docs/app-server).

Local bridge v1 accepts only the command method and a closed native body. Do not
insert `mcpServer/elicitation/request`, `tool/requestUserInput`, additional identity
claims or permissions into it. An alternative would need a separately reviewed
bridge version or independently defined outer evidence, preserving v1 bytes;
it is not silently accepted by this qualification. No new approval UI is proposed.

### D03. Independent recovery checkpoint/fence

| Attribute | Qualification |
|---|---|
| Candidate technologies | Separate-account S3 Object Lock Compliance + enforced conditional sequence writes; compare ordinary second-account DynamoDB counter and AWS Backup Vault Lock. |
| Classification | **CONDITIONAL** for the S3 composition. Ordinary mutable counters and backup retention alone are NOT_SUITABLE as the required complete freshness fence. |
| Documented capability | S3 supplies retained immutable object versions, conditional create, policy enforcement and version enumeration. These are ingredients for a checkpoint journal, not a managed Nexus monotonic-counter API or an atomic database-plus-fence transaction. |
| Verified deployment capability | UNKNOWN. No bucket/account identity, Compliance retention, policy, conditional operation, checkpoint chain, version listing, cross-account trust or restore domain was inspected. |
| Exact trust boundary | AuthorityAccount's database can be restored without restoring RecoveryAccount's immutable checkpoint history. N01 has bounded append/read credentials; an independent recovery administrator controls custody. Protected registration fixes account, bucket, prefix and genesis identity. |
| Executor permissions | None: no S3/fence role, credential, write, delete, version/retention/policy/lifecycle change or recovery capability. Public technology documentation may be read. |
| Owner permissions | Scoped checkpoint/audit readback through N01; no direct journal write/reset/delete follows from Nexus ownership. Reopening requires separately authenticated current Owner participation. |
| Admin permissions | Recovery administrator creates/manages the managed primitive outside ordinary table-restore administration. Retention/policy changes cannot be routine recovery shortcuts; changes trigger closure and requalification. Account-closing/organization-root authorities are explicitly trusted/excluded from executor access. |
| Recovery semantics | Compare all required versions/sequence/digests with database state before reopening. Gaps, forks, duplicates, delete markers, expired protection or partial two-system commit quarantine. Never select an older checkpoint merely because it matches a restored table. |
| Failure semantics | Fence denial/outage, unknown PUT result, incomplete pagination, wrong owner/prefix, retention expiry, extra same-key version or co-restoration closes authority. Hash chains alone cannot detect a jointly restored history. |
| Required credentials/secrets | N01 task-role credentials and a narrow cross-account STS role/session or equivalent resource-policy access; recovery-admin credentials kept outside both executor and ordinary deployment automation. No custom signing/PKI key. Protected resource IDs/genesis are metadata, not secrets. None accessed. |
| Later live qualification | YES: effective append-only permissions, conditional races, retention/deletion behavior, version pagination/markers, account separation, old-table restore, fence unavailability and crash windows must be tested on isolated non-authority records. |

Compliance mode protects retained versions from deletion/overwrite and shortening
of their retention, including against account root; it is time-bounded and does
not survive account deletion. It does not prevent a new version at the same key.
[Object Lock modes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html).

Delete markers can hide a retained version, and `If-None-Match` tests only the
current version; a marker can allow another write. Therefore neither Object Lock
nor conditional writes alone qualifies the fence. Selected mode requires deny
delete/marker creation and disallowed write paths, plus version-aware detection.
[Object Lock considerations](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html),
[conditional-write semantics](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html),
[conditional-write enforcement](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes-enforce.html).

### D04. Complete executor exclusion and mediated dispatch

| Attribute | Qualification |
|---|---|
| Candidate technologies | Fargate task isolation/IAM, ECR-pinned authority image, separate account/roles, restricted private network, ALB/ACM ingress, narrowly used existing managed secret custody, existing OpenAI managed execution behind N01. |
| Classification | **BLOCKED** for complete exclusion/mediation. Runtime IAM/isolation ingredients are VERIFIED_CANDIDATE; effective deployment and exact effect mediation are UNKNOWN. |
| Documented capability | Fargate separates tasks; AWS roles scope access; standard TLS protects public transport. OpenAI documents separation of application credentials from executor-readable environment authentication. These do not prove every Nexus route is mediated. |
| Verified deployment capability | UNKNOWN. No runtime/Owner/executor separation, IAM policy, role assumption, network, secret permission, protected image or bypass route tested. The current full-access local shell is not qualified as the protected Owner context. |
| Exact trust boundary | N01 task/code/store/fence/provider custody and N02 Owner device/transport are outside executor control. Only N01's one-time durable intent claim permits the fixed provider handoff; every equivalent privileged route is denied. |
| Executor permissions | No N01 task/metadata access, application credential, AWS deployment/recovery/store/fence role, `iam:PassRole`, ECS Exec, image/config/dependency write or direct privileged provider/target API. Only untrusted proposal/status request and separately qualified admitted workload permissions. |
| Owner permissions | Confirm/revoke through protected N02 and read scoped evidence; no automatic cloud-administration or privileged dispatch endpoint access. Owner browser/Host processes must be inaccessible to executor automation. |
| Admin permissions | Separate deployment operator installs reviewed closure; identity admin operates issuer; recovery admin controls recovery domain. Runtime principal cannot deploy, change IAM/bucket/table configuration, restore resources or administer identity. |
| Recovery semantics | Restore deployment only closed, pin verified closure/current registration, revalidate effective permissions and fence, retire old authority and reconcile reserved attempts. Old overlapping tasks must never claim work after incarnation change. |
| Failure semantics | Writable dependency, shared task/Owner principal, exposed secret, stale worker, direct-route bypass, missing scope-to-enforcement mapping or uncertain provider outcome closes dispatch. A status/reference or copied decision is never a bearer authorization. |
| Required credentials/secrets | AWS short-lived task and fence-access credentials; separate image-pull execution role; existing OpenAI application authentication in protected custody; any executor environment-only key remains distinct. ACM manages server certificate material. Named-secret custody is optional existing infrastructure, not a new vault API. None accessed. |
| Later live qualification | YES: effective denial from actual executor, Owner/Host isolation, dependency/config custody, duplicate/stale worker denial, exact-scope enforcement and protected diagnostic handoff. Real provider execution remains separately gated and unauthorized here. |

Existing managed G2 acceptance is evidence only for its declared configuration;
it cannot qualify N01's future deployment or complete G3 admission. OpenAI states
that generated code can access available files/credentials/network and that
executor environment credentials are readable by the executor; application keys
must stay outside it. [OpenAI sandbox security](https://developers.openai.com/api/docs/guides/agents-api/environments/security).

An existing AWS Secrets Manager secret may narrowly hold the selected provider
authentication. Runtime access must be limited to the specific secret; Owner and
executor get no secret read API. This is metadata-only selection and does not
access or invent a generic vault. [Secrets Manager identity policies](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_iam-policies.html).

### D05. Separately versioned production decision seam

| Attribute | Qualification |
|---|---|
| Candidate technologies | Existing strict G3 parsers/canonicalization plus future separately versioned Nexus authority receipt, production decision, intent/attempt and fence metadata contracts. Standard maintained validation/SDK libraries only; no new policy engine. |
| Classification | **BLOCKED**. The architecture defines the needed seam, but approved bounded production schemas, provenance rules and gate interface do not yet exist. This is not a cloud-service selection problem. |
| Documented capability | Local v1 explicitly forbids real-positive eligibility/dispatch and trusted candidate promotion. Existing Subject/grant/revocation/proposal/event/candidate bodies can be retained as immutable inputs/references. |
| Verified deployment capability | No production seam implemented or qualified. Static source confirms v1 remains disabled; this is verification of the negative boundary, not a VERIFIED_CANDIDATE positive decision. |
| Exact trust boundary | Only N01 may derive a future positive decision from protected verified identity, confirmation, state, current context and independently qualified G1/G2/task/Host evidence; only its protected gate consumes it. The executor never supplies trusted booleans or positive JSON. |
| Executor permissions | Construct untrusted existing inputs and receive non-authoritative readbacks. No production decision, receipt, provenance, intent, schema selector or fixture basis write. |
| Owner permissions | Review and confirm exact effects through N02; participate in explicit contract acceptance. Owner conversation authorization does not itself mint the future machine receipt. |
| Admin permissions | Install only separately reviewed versions; no reinterpretation of old records, migration-to-positive, unsigned downgrade or fixture-based production path. |
| Recovery semantics | Unknown schema/version, lost authoritative provenance, failed migration or obsolete epoch denies. Restore preserves negative/fixture meanings and immutable canonical bytes. |
| Failure semantics | Reject unknown keys/versions, substituted hashes, incomplete joins, unproven gate facts or fixture-to-production conversion. D01-D04 failure dominates the future decision. |
| Required credentials/secrets | None for documentary schema review. Future trusted records use N01's protected storage provenance; no custom receipt-signing key or transferable bearer grant is required. |
| Later live qualification | Offline schema/adversarial contract qualification first; YES for later integrated provenance/claim/revoke/recovery enforcement after separate authorization. No positive production records or N01/N02 implementation in this phase. |

Preserve all seven accepted bodies: `Subject`, `ApprovalGrant`, `Revocation`,
`EligibilityDecision`, `HostApprovalProposal`, `HostApprovalEvent`, and
`HostDecisionEvidenceCandidate`. Version names for new outer metadata are not
allocated here. An explicit later specification must define domain separation,
limits, canonical bytes, identity/project/Subject/scope/effect joins, issuer
provenance, generations, timestamps, evidence references and dispatch consumption.
Do not add `owner_authenticated=true` or a production basis to existing v1.

## 4. Explicit managed-primitive comparisons

### 4.1 Identity and confirmation

| Candidate / exact mode | Assessment | Disposition |
|---|---|---|
| OpenAI Sign in with ChatGPT verified ID token | Reuses OpenAI identity; no Nexus entitlement/client verified and no full approval/lifecycle guarantee established. | CONDITIONAL primitive; access UNKNOWN. Prefer reuse if those prerequisites can later be proved. |
| OpenAI plugin identity transaction | Depends on trial access and a distinct connector-authorization flow. Building an OAuth provider to obtain it would expand scope. | BLOCKED as the current deployment route. |
| Amazon Cognito managed login / OIDC | Mainstream managed fallback with existing login and account authentication; separate exact Nexus binding and trusted Host confirmation remain necessary. | Selected CONDITIONAL issuer. No custom login/identity platform. |
| Native Codex command approval | Fits current bridge method, but trusted origin, complete effects and gate-controlled release are unqualified. | Selected named Host surface, BLOCKED integration. |
| MCP form/URL elicitation | Useful interaction, but not a trusted callback by itself and not the closed v1 command proposal. | NOT_SUITABLE as a v1 replacement; separate explicit contract review would be needed. |
| Cognito consent/login page used as proposal approval | Authenticates/login-consents; does not display and confirm the complete Nexus Subject/scope/effects. | NOT_SUITABLE for D02. |

The issuer choice does not resolve D02. Do not silently convert a Cognito
authenticated session, MCP response, platform approval log or upstream Host
attestation into a Nexus Owner receipt.

### 4.2 Managed transactional stores

| Candidate / exact mode | Documented primitive and qualification limit | Selection |
|---|---|---|
| DynamoDB single-Region transactions | Atomic item operations and conditional checks fit bounded records without a DB server or SQL credential. Restore and independent fence still need qualification. | Selected VERIFIED_CANDIDATE primitive; deployment UNKNOWN. |
| Amazon Aurora PostgreSQL / Serverless v2 | Managed SQL runtime; PostgreSQL documents SERIALIZABLE transactions, including serialization failures that applications must handle. Engine/version/permissions/durability and independent recovery remain unqualified. | CONDITIONAL alternative; more connection/schema/database administration for this minimum. |
| DynamoDB ordinary batch writes, GSIs or stream consumer as authority | Not the selected atomic snapshot/transition route; index/stream propagation cannot be treated as one committed decision view. | NOT_SUITABLE for positive authority in that mode. |
| SQLite file in the remote container | Familiar local engine, but adds durable-volume and backup/restore custody work; container-local storage is not the selected durable managed ledger. | NOT_SUITABLE in ephemeral-container mode; a different deployment would require review. |

SQL is viable, but familiar coding is not a sufficient reason to choose it.
The selected bounded DynamoDB mode reduces database administration and long-lived
database-password custody. This is an engineering judgment about this design,
not a verified cost/performance comparison.
[Aurora managed runtime](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html),
[PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html).

The transaction API has a 100-action / 4-MB limit and a ten-minute client-token
idempotency window. Permanent nonce/attempt consumption must therefore be explicit
ledger state. Use generation/tombstone checks rather than an unbounded fan-out
update to every pending intent. Conditions belong on their associated writes;
one transaction cannot independently check and update the same item twice.
[TransactWriteItems API](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html).

Backup/index/stream propagation may not preserve a recent transaction as a complete
snapshot. A recovered table must be checked against the independent checkpoint;
PITR success cannot reactivate authority by itself.
[Transaction recovery caveats](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html),
[DynamoDB recovery configuration](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery_Howitworks.html).

### 4.3 Independent generation/checkpoint options

| Candidate / exact mode | Strength / missing property | Disposition |
|---|---|---|
| Separate-account S3 Compliance checkpoint objects plus enforced conditional create | Retained immutable versions and create-only sequence slots; independent from ordinary ledger restore. Nexus must still validate predecessor/current history, duplicates, retention, permissions and the two-system crash protocol. | Selected CONDITIONAL composition; no native monotonic-service claim. |
| Second-account DynamoDB conditional counter | Conditional updates can record a high-water value, but an ordinary mutable/restorable table alone is not immutable recovery history. Separate account placement does not prove protection from counter restoration/reset. | NOT_SUITABLE as a standalone complete fence; potentially CONDITIONAL only with separately proved non-reset custody. |
| AWS Backup Vault Lock Compliance | Protects retained recovery points after its grace period. Backup retention is not synchronous generation advancement for each authority transition. | VERIFIED_CANDIDATE backup-retention primitive; NOT_SUITABLE as the sole admission fence. |
| Object Lock Governance or versioning alone | Privileged bypass or new versions/current-pointer changes leave required exclusions unproven. | NOT_SUITABLE as the sole rollback guarantee. |
| Cloud audit log/hash chain alone | Evidence of some events is not a live conditional current-generation gate. Restorable local chains cannot detect complete co-rollback. | NOT_SUITABLE alone. |

Vault Lock's Compliance protection applies to retained backup recovery points;
it does not acknowledge arbitrary Nexus commits. No vault is provisioned or
locked in this phase. [AWS Backup Vault Lock](https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html).

### 4.4 Small runtime options

| Candidate | Primitive / integration cost | Disposition |
|---|---|---|
| ECS Fargate, one N01 task | Managed container/task identity with one serialized authority loop and bounded provider handoff; no VM administration. Restart and accidental task overlap still require state/fence enforcement. | Selected VERIFIED_CANDIDATE primitive; deployment UNKNOWN. |
| AWS Lambda | Managed functions scale execution environments with concurrency. Serialization, crash ambiguity and incarnation/claim ordering must remain in durable state; reserved concurrency does not make a process lock a recovery proof. | CONDITIONAL alternative; not selected for the initial long-lived ordering/hold model. |
| Google Cloud Run | Managed containers with automatic scaling/revisions; plausible runtime, but cross-cloud identity/store/fence custody expands this candidate's operational configuration. Scaling limits are not an authority lock. | CONDITIONAL alternative; not selected. |

Fargate is selected for explicit task custody and a bounded serialized handoff,
not because containers are intrinsically trusted. Do not implement active-active
leaders, a queue platform or an extra broker to accommodate the alternatives.
[Lambda concurrency](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html),
[Cloud Run scaling](https://docs.cloud.google.com/run/docs/about-instance-autoscaling).

## 5. Exact proposed custody and recovery protocol

### 5.1 Permission and administrative separation

The following are **future required effective permissions**, not generated IAM
policies or existing role assignments. Every actual assignment remains UNKNOWN.

| Principal/domain | Allowed minimum | Excluded authority |
|---|---|---|
| Owner / protected N02 context | Existing issuer authentication; exact explicit confirmation/deny; scoped audit; current-binding recovery participation. | No direct table/fence writes, AWS role credentials, image/config/policy administration or bearer dispatch credential. |
| N01 application task role | Exact table transactional access, read current protected registration, bounded fence append/read, and selected provider credential/use. | No IAM administration, user-pool admin, restore/table/bucket control, image/deployment update, ECS Exec or arbitrary role assumption. |
| Fence-access role / RecoveryAccount resource policy | Required prefix `PutObject` with mandatory conditional header; exact object/version/retention reads and complete version listing. | No delete, marker creation, copy/multipart alternative route, bucket/retention/lifecycle/policy changes or prior-version replacement. |
| ECS task execution role | Reviewed image pull and narrowly scoped operational launch/log permissions. | No authority state access or provider operation. Do not expose it as Owner approval authority. |
| Deployment operator | Install/pin approved N01/N02 release and fixed resource registration; perform separately approved closed maintenance. | No Owner-consent inference or ordinary fence-history reset. |
| Recovery administrator | Read retained checkpoint history and backups; perform explicit closed restoration/reconciliation with current binding proof. | No restore-and-resume, checkpoint rewind, stale Owner reinstatement or deletion of deny/consumption history. |
| Executor / admitted workload | Submit bounded untrusted proposals/status queries; perform only separately admitted workload effects. | No Owner device/session/transport, authority task/metadata, store/fence/secret, deployment/recovery identities or equivalent privileged provider routes. |

Trusted cloud/platform administrators and issuer administrators can influence
the system and are part of its trusted computing base. This candidate does not
claim safety against collusion of all administrators, account closure or compromise
of the identity issuer/platform. It requires independent recovery custody from
the ordinary restore operation and exclusion of those privileges from the
executor. A hidden shared recovery/deployment credential defeats that claim.

N01's full image/interpreter/library/config closure must be pinned and protected;
do not mount an executor-writable repository or import runtime code from it.
N02's Host/browser/session/transport closure must have equivalent protection on
the Owner device. A remote service alone does not solve local Owner impersonation.

### 5.2 Concrete S3 fence composition

The fence is an immutable checkpoint journal using existing managed primitives,
not a new witness service. The following algorithm is a proposed composition
for later proof; it is not code, resource configuration or an issued record.

1. Protected deployment/recovery registration fixes RecoveryAccount owner, bucket,
   authority instance and genesis/prefix. Executor-supplied endpoints, restored
   local files or a different apparently empty prefix cannot change that root.
2. Each sequence slot is a fixed-width key under that authority instance. Its
   separately versioned checkpoint metadata binds epoch/incarnation, sequence,
   predecessor/commit digest and transition/evidence references. Existing G3
   bodies remain byte-for-byte unchanged. Never maintain authority in a rewritable
   `latest` object alone.
3. Prepare one transition in DynamoDB with conditions on current control generation
   and expected sequence; mark it unavailable for dispatch. All relevant binding,
   consumption, revocation, evidence and intent joins are in that transition.
4. Read/validate the registered fence history and predecessor under the single
   authority ordering rule. Append the next checkpoint with SigV4 `PutObject`,
   `If-None-Match: *`, checksum and qualified Compliance retention. Bucket policy
   must require conditional create. Select no multipart/copy shortcut.
5. Verify successful durable append and exact checkpoint version/body; finalize
   the same prepared transition conditionally in DynamoDB. Only then acknowledge
   authority or release a claimed dispatch. A duplicate slot is not blindly accepted:
   compare its exact immutable body; any different body is a fork and closes the
   instance. Unknown result, conflict or mismatch quarantines rather than retries
   an external effect.
6. Startup/recovery obtains the complete registered version history, including
   delete markers and pagination. It validates the chain, latest unambiguous slot,
   exact protected owner and retained-version protection before comparing ledger
   generation/digest. Incomplete/ambiguous enumeration is a failure, not proof that
   no newer checkpoint exists. Unexpected same-key versions/markers close authority.
7. New incarnation retires pending approvals, grants and unclaimed intents, as the
   accepted architecture requires. Retain latest binding removal, revocation and
   consumption history. Reserved/uncertain attempts remain consumed. A restored
   ledger behind the fence cannot be advanced using stale local content.

S3 documents strong GET/LIST behavior after a successful object write, but does
not provide atomic changes across keys. Complete version listing requires
`s3:ListBucketVersions`, continuation markers and correct parsing; `200` is not
itself complete valid evidence. A paginated enumeration is not assumed to be an
atomic snapshot during concurrent writes. Proving single current writer and
absence of unobserved newer slots remains mandatory.
[S3 consistency](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html),
[ListObjectVersions](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectVersions.html).

Conditional create protects one slot; it does not check the predecessor key,
enforce the complete sequence protocol, or atomically commit with DynamoDB.
Those are N01 responsibilities within the already accepted scope. This explicit
composition gap is why D03 is CONDITIONAL rather than VERIFIED_CANDIDATE as a
complete fence. No external authority is released during the prepared/fenced/
finalized ambiguity window; the minimum chooses quarantine over automatic repair.

Compliance retention duration and recovery-history horizon are **NOT SELECTED**
and must be separately reviewed before any resource setup. Protection must cover
every checkpoint used to validate any admissible restoration, including binding
and deny history. Minimum mode has no automatic deletion/lifecycle expiry and
performs no purge. If required retained protection is expired, shortened, missing
or no longer independently readable, readiness/admission closes. A digest-only
checkpoint detects loss; it cannot reconstruct lost records. Missing recent
state/evidence/deny history requires quarantine, not invention or reset-to-empty.

### 5.3 Dispatch and task replacement

The protected N01 claim transition is the only authorization to start the fixed
attempt. Revoke before claim blocks it; revoke after claim cannot promise to undo
an already handed-off effect. Keep the architecture's bounded serialization
through the handoff, priority for pending revocation and permanent consumption of
unknown outcomes. Do not treat a DB idempotency token as provider exactly-once.

One configured Fargate task is not proof that only one old/new process can act.
Planned replacement must close the gate and record a current incarnation; every
claim is conditional on it and current fence state. Overlap, takeover ambiguity
or an unresolved old handoff keeps the deployment closed. No automatic rollback
to an older image/table/prefix reopens it, and no active-active design is proposed.

A concrete scope-to-existing-enforcement mapping is needed for each admitted
operation/target. The bounded N01 adapter must own privileged provider access,
while the workload uses only its separately constrained environment authentication.
Starting unrestricted executor code behind one check does not enforce exact
effects. No uncovered local/cloud/tool/network bypass can be declared safe from
a container name or a previous managed G2 result.

## 6. Required later evidence and credential-safe qualification plan

All tests below are **planned only**. No resources, services, users, certificates,
secrets, policies, checkpoints, grants, revocations or provider runs are created
here. Live resource mutation, identity sign-in/disable, irreversible retention
settings and any actual provider execution require separate authorization for
the exact isolated test scope. No permission question is needed to finish this
documentary phase.

| Test group | Minimum evidence / pass condition | Required prerequisites |
|---|---|---|
| Q01 Identity availability | Concrete issuer/client/entitlement metadata, actual verified principal and protected exact project enrollment route; wrong issuer/client/sub/nonce denied. | Named issuer access and isolated Owner context; no credential contents in evidence. |
| Q02 Lifecycle | Sign-out, disable, account/workspace switch and relevant role/context removal invalidate use before subsequent claim; no stale-token or managed-cookie shortcut. | Trusted lifecycle integration; explicit authorization for identity/account-state tests. |
| Q03 Host approval | Existing surface shows complete frozen effects; explicit actual Owner callback; auto/clear/timeout/substitution forged-origin denied; native action cannot run before gate. | Identify a documented supported N02 integration first. No fake/dummy prompt promoted into a real grant. |
| Q04 Primitive transactions | Bounded diagnostic items commit atomically under condition conflicts; duplicate requests remain consumed beyond SDK/API idempotency window; negative history survives restart. | Isolated managed test resources; diagnostic records are not `ApprovalGrant`/`Revocation` and confer no authority. |
| Q05 Independent fence | Effective separate custody, current-generation discovery, denied overwrite/delete/policy/retention routes, conflict/fork/marker/pagination handling and retention checks. | Authorized disposable prefix/account and retention plan; no production authority records. |
| Q06 Crash and rollback | At every prepare/append/finalize interval: either proven current finalized state or closed quarantine; old backup/prefix/table/image cannot restore authority; missing history stays closed. | Closed diagnostic recovery environment; no destructive change to current Nexus state. |
| Q07 Executor exclusion | Actual executor denied Owner session/transport/process access, task credentials, store/fence/secrets/admin/deployment and equivalent privileged dispatch; effective permission evidence retained. | Named isolated executor/Host/runtime deployment; planned configuration alone is insufficient. |
| Q08 Ordering and handoff | Revoke-before-admit/claim outcomes, duplicate/stale task denial, one claim and uncertain-outcome consumption; diagnostic dispatcher never retries an ambiguous effect. | Reviewed future seam, then separately authorized N01/N02 implementation and isolated non-effectful diagnostic target. |
| Q09 Production seam | Separately versioned bounded schemas and provenance interface accepted; old v1 fixture/offline records never become positive; current G1/G2/task/Host failures dominate. | Documentary/contract review first; integrated live proof only after implementation authorization. |

Mock/diagnostic handoff evidence cannot qualify a real provider's enforcement,
credential custody or scope restrictions. A later actual provider test, if needed,
has its own authorization and execution-count boundary; none is authorized here.
Initial managed-primitive tests need not issue grants or implement admission.

Required metadata, without retrieving its contents:

| Material | Future custodian / requirement |
|---|---|
| Issuer/client registration, JWKS/discovery URL, callback and actual stable Owner identity | Public/protected configuration metadata, plus independently verified binding; currently UNKNOWN. No email-based substitution. |
| Owner login/MFA and Host account session | Existing issuer/Owner context only. Never accessible to executor or stored in grant/evidence exports. |
| Code, PKCE verifier, identity/access tokens, Nexus session | Short-lived protected D01/N02 transaction/session material. No raw tokens in documentary/runtime evidence. |
| AWS task/fence STS credentials | Short-lived machine credentials in protected N01 task only; no shared operator profile or static key in workspace. |
| Deployment and recovery admin authentication | Separately operated existing admin identities; executor possesses none. Actual separation/effective permissions currently UNKNOWN. |
| OpenAI application authentication | Existing selected managed route, held outside executor; exact authentication mode/access entitlement UNKNOWN until separately qualified. |
| Executor environment-only authentication | Distinct workload credential if the chosen existing route requires it; not Owner identity and not permission to create sessions/authority. |
| TLS hostname/certificate and store/fence resource identities | ACM/service-managed certificate material; protected exact resource registration. No custom CA, receipt-signing key or generated PKI. |
| Retention/recovery horizon, root/genesis and complete backup/deny history | Protected administrative facts, not secret values. Actual choices/evidence currently UNKNOWN; cannot be invented from local state. |

## 7. Documentary validation and final disposition

The proposed stack has nine named layers and two future Nexus trusted components.
It converts Option C into a specific candidate and identifies the exact required
managed primitives, permissions, credentials and tests. It does not close the
trusted Host seam or prove an actual deployment. The remaining blockers must not
be hidden by a VERIFIED_CANDIDATE label on an individual cloud primitive.

This phase adds only this distributable document and its static manifest entry.
Validation checks twelve attributes for each of D01-D05, nine stack layers,
classification vocabulary, required output fields, local links, unchanged source
and preserved accepted/historical documents. The manifest extends from 336 to
337 entries through an isolated static snapshot; all prior 336 entries remain
unchanged. Ignored documentary evidence is in
`state/g3-u1-option-c-qualification-20261008/`.

No production trust test has been performed. No N01/N02 implementation or public
admission change is included. Existing public denial and offline/fixture semantics
remain unchanged. No credential/account discovery or state change, grant/revocation
issuance, authenticated cloud call, Host-process start, provider execution, commit,
push or deployment occurs.

```text
OPTION_C_CONCRETE_STACK = DEFINED
D01_IDENTITY = CONDITIONAL
D02_HOST_CONFIRMATION = BLOCKED
D03_RECOVERY_FENCE = CONDITIONAL
D04_EXECUTOR_EXCLUSION = BLOCKED
D05_PRODUCTION_DECISION_SEAM = BLOCKED
CONCRETE_N01_RUNTIME = AWS_ECS_FARGATE_SINGLE_AUTHORITY_TASK_PROPOSED
CONCRETE_AUTHORITY_STORE = AMAZON_DYNAMODB_SINGLE_REGION_TRANSACTIONAL_TABLE_PROPOSED
CONCRETE_RECOVERY_FENCE = SEPARATE_ACCOUNT_S3_OBJECT_LOCK_COMPLIANCE_CONDITIONAL_CHECKPOINT_JOURNAL_PROPOSED
CONCRETE_N02_HOST_SURFACE = CODEX_NATIVE_COMMAND_APPROVAL_UI_UNQUALIFIED
LIVE_QUALIFICATION_REQUIRED = YES
U1_IMPLEMENTATION_CANDIDATE_READY = NO
N01_N02_IMPLEMENTED = NO
REAL_ADMISSION_ENABLED = NO
GRANTS_REVOCATIONS_ISSUED = 0
PROVIDER_EXECUTIONS_ADDED = 0
LIVE_QUALIFICATION_TESTS_PERFORMED = 0
CREDENTIAL_ACCESS = NONE
ACCOUNT_POLICY_CHANGES = NONE
FAIL_CLOSED_BOUNDARY = PRESERVED
```
