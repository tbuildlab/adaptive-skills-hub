# G3 U1 D04 executor exclusion and mediated dispatch v1

Date: 2026-10-08. Offline exclusion specification; no hostile probes or live tests.
Inputs: [minimal architecture](nexus-g3-u1-minimal-authority-architecture-v1.md),
[N02](nexus-g3-u1-n02-minimal-confirmation-architecture-amendment-v1.md),
[D05](nexus-g3-u1-d05-production-authority-contracts-v1.md),
[bounded D01](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md),
[D03](nexus-g3-u1-d03-recovery-fence-qualification-v1.md).

## Qualification decision

D04 remains BLOCKED. No production account, effective policy, protected browser,
runtime, credentials or provider-route inventory has been inspected. The exact
future mediation design is DEFINED; documentation is not isolation evidence.
An executor with filesystem/shell/browser control over the Owner's actual device
cannot be excluded by a same-device confirmation cookie or different web page.
Qualification requires an independently controlled Owner environment or proof of
an equivalent protected browser boundary, not an assumption of good behavior.

Controllers below are *proposed*, not observed. Owner enrollment authority,
deployment administration and recovery custody must be authenticated and excluded
from executor delegation. Admin access is a trusted assumption and must be logged;
Owner approval does not grant unrestricted cloud admin or override technical gates.

## Complete exclusion matrix

| ID | Surface / authoritative controller | Executor allowed permissions | Forbidden permissions | Required evidence | Bypass condition | Fail-closed behavior |
|---|---|---|---|---|---|---|
| X01 | Owner browser/session; human Owner and protected N02 origin | Receive non-secret proposal locator; sanitized status | DOM/cookie/profile/process/extension/remote-control access; driving CONFIRM; browser debugging | Independent device/principal custody, actual browser/process isolation and origin/CSRF tests | Executor can impersonate Owner, edit presentation or click consent | No trusted decision or receipt; D01/D04 fail. |
| X02 | Stytch user/session bearer; protected N01 relying party | None | Read/write/replay bearer, browser cookie, network headers, token export or session replacement | Actual token-flow and memory/log custody, secret-free canonical records, ingress isolation | Bearer visible to executor or supplied as authoritative executor evidence | Reject context; retire compromised lineage; no claim. |
| X03 | Stytch project secret/admin; separate issuer administrator | None | API secret, console, user/session mutation, impersonation, role delegation or secret rotation | Effective issuer roles, secret retrieval scope, admin MFA/custody and impersonation exclusion | Executor can create/authenticate/replace Owner or session | Identity source unqualified; close authority. |
| X04 | N01/N02 runtime; restricted workload role | Proposal submission and sanitized status only | Shell/code/memory/env/filesystem writes, privileged endpoint invocation, origin fabrication | Deployed artifact identity, ingress routes, task identity, effective OS/container isolation | Writable runtime accepts executor-built receipt/context | No positive authority; stop release. |
| X05 | Deployment image/config; independent deployer | Submit reviewable code proposal only | Registry overwrite, image tag repoint, task/config/env/secrets update, build runner modification | Immutable image digest, reviewed source, deployment ownership, config readback and rollback fence | Executor replaces approved code or disables checks | Unregistered generation denies; quarantine on restart mismatch. |
| X06 | DynamoDB/store; N01 writer and separate restore admin | None; sanitized application status | Read sensitive evidence, direct write/delete, export/restore, table alias change, alternate credentials | Resource identity, effective IAM/SCP/resource policy, conditional transaction and consistent reads | Executor edits nonce/grant/revocation/head or restores table | D03/D04 fail; quarantine. |
| X07 | Recovery fence; independent recovery account custodian | None | Journal writes, deletes/versions/markers, retention/policy/key/resource changes | Separate-account effective principals, Compliance per-version metadata, full history and conditional-write tests | Same operator/role can rewrite both ledger and fence | Quarantine; no history reset. |
| X08 | AWS IAM/deployment roles; excluded security administrator | Unprivileged executor role with application proposal permission only | Assume/pass/create role, attach/edit policies, privilege delegation, deploy/restore permission | Transitive assume-role/PassRole/policy simulator plus actual negative access evidence and org/account custody | Indirect IAM path reaches authority/issuer/provider roles | Exclusion not qualified; deny release. |
| X09 | Provider execution credentials; protected dispatch adapter | None | Read/mint/rotate/delegate equivalent credential or use inherited provider login | Exact credential custody and provider account/resource scope; executor-environment inventory | Executor calls equivalent provider API directly | Complete mediation fails; no admission. |
| X10 | Dispatch adapter; N01 in-process protected bounded adapter | Untrusted proposal/cancel/status only | Direct adapter invocation, arbitrary payload/target, claim injection or replay | Endpoint absence/identity proof, closed payload enforcement, one durable claim and single-use handoff | Copied CLAIM or alternate endpoint releases effect | Reject; consumed UNKNOWN stays consumed. |
| X11 | Restore/backup path; independent recovery administrator | None | Restore/repoint/export/import, select earlier head, edit tombstones or backup policy | Versioned recovery registration, full fence reconciliation, crash/restore tests | Old snapshot resumes with old nonce/context/grant | Quarantine; new independently authorized epoch; retire old authority. |
| X12 | DNS/TLS/ingress; excluded infrastructure administrator | Reach proposal/status endpoints | DNS/certificate/listener/proxy/origin/callback changes, request-header forgery | Exact HTTPS origin, certificate custody, routing/config readback, session/CSRF/header tests | Redirect/impersonate login/confirmation or bypass origin middleware | Reject decision; no render/receipt authority. |
| X13 | Direct alternate provider route; provider/account and network controllers | No equivalent effect route | API, console, CLI, browser automation, subprocess, plugin or network route producing same effect | Complete action/credential/host route inventory, scoped account/network controls and actual negative tests | Any executor-accessible equivalent action exists | D04 BLOCKED even if main adapter is protected. |
| X14 | Debug/shell/ECS Exec; deployment/security administrator | None on authority workloads | Exec/SSM/debug attach, proc/memory access, privileged container or host access | Disabled debug paths, effective permissions, actual attach/exec denial and deployment audit | Executor reads tokens or mutates runtime via diagnostics | Stop/quarantine; debug session retires authority until requalification. |
| X15 | Logs/dumps/telemetry; protected runtime and separate operations custodian | Allowlisted sanitized status only | Raw headers/cookies/secrets/session response, crash dump/APM variable capture | Redaction tests across request/error/retry/crash paths, log/export/agent access evidence | Credential or private confirmation material leaks | Revoke/retire under authorized incident process; no positive fallback. |

## Protected persistence, replay and recovery contract

N01 is the only authoritative application writer of context/provenance, grants,
revocations, consumption, intents and claims. N02 conveys protected Owner evidence;
it has no effect-release authority or direct store/fence writes. The adapter reads
only the registered live N01 claim and exact frozen invocation, never executor
record copies. Browser/session custody is ephemeral and isolated; authority state
persists in the protected ledger plus independent D03 journal. Tokens are excluded
from canonical records, snapshots, backups and telemetry where not strictly needed
for protected runtime custody. Backup policy must not make them executor-readable.

Every old context is retired across restart; nonce/receipt/grant/claim consumption
and revocation tombstones survive. Restore is quarantined until independent full
history, immutable bodies, descriptor and control rows agree. No backup image or
valid JWT reopens authority. Rebinding, Owner replacement and epoch changes retire
old lineages through the same serialized witnessed transitions.

## Complete mediation and exact release

```text
executor
  -> untrusted proposal only
  -> N01 authority (current D01/D03/D04 and technical/task/Host/G1/G2 gates)
  -> durable claim (complete revocation query + witness + atomic consumption)
  -> protected dispatch adapter
  -> exact provider action
```

The executor cannot issue a positive receipt, claim or provider credential. After
all gates pass in a future qualified deployment, N01 serializes claim against
local invalidation/revoke, fences it, checks deadlines again and gives the adapter
one protected in-memory handoff. Matching record hashes do not substitute for this
capability. Freeze Subject/scope/targets/config/arguments/environment and payload
contract; any substitution denies. A direct equivalent provider route must be
absent for the enrolled execution environment and action. Ordinary task/network
access is not proof of complete mediation.

Before claim, a prior serialized revoke denies. After durable claim, revocation
cannot undo an already released external action; retain consumed attempt. Unknown
handoff/outcome remains UNKNOWN with no retry. Timeout or unavailable witness closes
the gate. D01's accepted external check-to-claim race remains separate from local
revoke serialization. Neither browser click nor ADMIT_PENDING alone dispatches.

## Future qualification and STOP

Later testing must be separately authorized on disposable isolated accounts and
execution environments: positive access for intended roles, negative access for
executor across all 15 surfaces and transitive privilege paths, exact payload
enforcement, revoke/claim races, stale restore and unknown dispatch outcome. Policy
text/simulator success alone is insufficient. Existing cloud/issuer admin, workload
STS and provider credentials will be required; none are accessed here.

The run stops each implementation/live task requiring login, cloud resources,
credential custody, privilege elevation or provider effect. Safe parsers/tests
continue independently, without importing a production-positive path.

```text
D04_EXECUTOR_EXCLUSION = BLOCKED
D04_COMPLETE_MEDIATION_DESIGN = DEFINED
D04_LIVE_QUALIFICATION_REQUIRED = YES
D04_IMPLEMENTATION_READY = NO
D04_DOCUMENTARY_DESIGN_IS_DEPLOYMENT_PROOF = NO
REAL_ADMISSION_ENABLED = NO
GRANTS_REVOCATIONS_ISSUED = 0
PROVIDER_EXECUTIONS_ADDED = 0
FAIL_CLOSED_BOUNDARY = PRESERVED
```
