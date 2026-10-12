# N01 Owner-only composition preparation v1

2026-10-12 UTC. Parent observation checkpoint:
`0e4abfa` on `nexus-v2-production-qualification`.
This is additive implementation preparation, not source qualification, a current
Owner ceremony, N01/N02 closure, independent review or Production Final.

## Reuse and exact deterministic gaps

The accepted N01 control, delegated record, transition, primary reservation and
independent versioned custody contracts remain unchanged. D01 and D03 are not
requalified. Native SDK/TLS/signature/session primitives remain reused; no new
identity provider, cloud resource, paid plan, orchestration or memory engine is
introduced.

[Owner membership persistence](../ash/g3_n01_owner_persistence.py) composes existing
complete membership resolution with PREPARED → independent custody → FINALIZED →
fresh primary/independent equality. Its result remains NONE. The historical
TEST_ONLY SingleCommit is unchanged. The new transport rereads one exact R-only
current source registration; it does not accept a local approval or source-PASS
boolean. Actual protected controller deployment/qualification and native transport
origin are still mandatory. An arbitrary Python object is not qualified origin.

The additional writer is restricted to Owner-only transaction groups T1/T2/T3/T5/T9
and existing context/challenge/view/decision/receipt/registration/source/recovery
families. Grant, admission-intent, claim, result and dispatch are excluded. Source
kinds and Principal must match the independently enrolled Owner-only source.
Complete nested bodies, evidence and assertions must resolve; unreferenced input
payloads cannot enter storage. Every supplied Preparation is semantically rederived
against current independently retained predecessor bytes before primary mutation.
The protected controller must also generate actual observation/origin evidence;
this durability module does not authenticate arbitrary supplied source assertions.

Every put must match one exact private consumed write plan and fixed conditional
JSON/checksum request. Additional retention parameters, approval-prefix writes,
unplanned material and repeated attempts deny. The operation is consumed before
mutation. Unknown outcome retires coordinator and fence and leaves the primary
PREPARED quarantine intact. No automatic redispatch, bearer restore, grant or
positive authority acknowledgment exists.

For a new Owner-controller RECOVER, require a separately protected exact R record
under `qualification/n01/v1/approvals/owner-controller-recovery-v1/<sequence>/`.
Its closed `nexus.g3.n01.owner-recovery-authorization.v1` body binds purpose
`BOUNDED_OWNER_CONTEXT_SOURCE_ONLY`, DELEGATED_EXECUTOR/configuration, exact source
enrollment SHA256, checkpoint/predecessor, epoch/incarnation, app/review generation
1, the unchanged fixed review expiry, NO_AUTOMATIC_REDISPATCH and REAL_ADMISSION=NO.
The incarnation is `n01-owner-` plus the first 32 hexadecimal characters of the
fresh independently enrolled process nonce. Require this authorization before
primary mutation and again before journal append. Sequence 0–2 retain their
original storage-generation/admin semantics. No R authorization or source record
has yet been written for this new controller.

## Current human ingress and exact presentation

[Owner ingress](../ash/g3_n01_owner_ingress.py) is the fixed relying-party seam for
the existing exact Stytch Consumer Test Principal and reviewed public pins. It
requires current R enrollment, a complete OPEN current head, current Owner binding
and the exact Owner-only writer membership before provider interaction. The
protected HTTP controller still needs to be assembled and qualified.

Human email input must match the hash of the previously accepted exact delivery
association. No arbitrary email association, user creation or TOTP enrollment is
introduced. The sequence is fresh email OTP, exact Owner response, current TOTP,
then direct native CurrentSession mapping. Each stage is one attempt; unknown
outcome retires. Session/bearer/code material stays private in runtime memory,
buffers are cleared, and public return values/evidence are NONE. The bounded
pre-authentication window is two minutes, with wall/monotonic regression checks;
the resulting context retains the existing non-refreshable factor/review/provider
deadline. The process-only Secure/HttpOnly/SameSite Strict `__Host-` cookie and CSRF
proof rotate after MFA and cannot be serialized or restored.

[Fixed N02 presentation](../ash/g3_n02_presentation.py) renders all accepted frozen
material, complete targets, scope/operations/effects/dispatch, Principal/binding,
nonce/time, proposal/view and presentation identity. It requires exact canonical
v2 bytes, frozen joins, current expiry and exact template revision. HTML escaping,
visible ASCII JSON, bounded complete output and strict response policy prevent
raw HTML, scripts, frames, remote fetches, hidden material and truncation. Only two
explicit controls exist: CONFIRM and DENY, neither preselected. A closed POST is
compared to exact Origin/Host, CSRF and frozen identities; duplicate/extra/malformed
fields, wrong choice or expiry deny. The result is expressly UntrustedDecision /
NONE. It does not authenticate Owner context, consume durable state, issue a
receipt or execute anything. Those remain N01 integration requirements.

## Adversarial findings and current validation

The complete reader originally rejected a future domain-addressed ledger descriptor
between PREPARED and append. The reader now validates that complete closed
descriptor shape/domain/configuration while excluding it from current checkpoint
membership. A future descriptor cannot advance the current head, and unknown
extra fields still quarantine. The independent journal and complete source/body
joins retain authority over membership; no test or security contract was weakened.

Current new component counts are 13 durability, 11 human-ingress, 10 presentation,
8 complete-reader and 9 bootstrap tests: 51 distinct cases. All passed their focused
runs with zero skips/failures; repeats are not additive. Synthetic transport, code,
source and session values remain under tests. SDK Test-environment warnings stay
visible. These tests do not prove actual Owner authentication, source custody,
durable current context or human CONFIRM/DENY. The existing closed D01 ceremony
and D03/storage/recovery/live-bootstrap observations are not repeated.
The combined affected run contains 85 distinct cases, all PASS with zero skips or
failures, including 34 existing retained-state/delegated-control/transition cases.
Static codec equivalence, import/secret isolation, the 628-entry MANIFEST and a
reproducible 229-member preparation source package pass. This package is not a
Production Final release artifact or independent-review result.

This local preparation adds zero AWS/Stytch operations, new retained versions or
deployments. Current actual live counts remain those in the
[bootstrap observation](nexus-production-n01-native-bootstrap-observation-v1.md).
Existing USD 1.00 scope, review expiry, operation deadline and table cleanup are
unchanged. Full protected controller assembly, source registration, current
Owner/context durable linkage and revoke/consume/replay remain required. Later
G3/G4/G6 live gates, independent review and exact Owner release acceptance remain
separate. D04 exclusion is not reinstated as a delegated release gate.

```text
OWNER_DURABILITY_ADAPTER = COMPLETE_OFFLINE_PREPARATION_NONE
OWNER_HUMAN_INGRESS = COMPLETE_COMPONENT_PREPARATION_NONE
N02_FIXED_PRESENTATION = COMPLETE_COMPONENT_PREPARATION_NONE
COMPLETE_PROTECTED_CONTROLLER = NOT_YET_ASSEMBLED_OR_QUALIFIED
ACTUAL_CURRENT_SOURCE_ENROLLMENT = NOT_PERFORMED
ACTUAL_CURRENT_OWNER_CONTEXT = NOT_CREATED
N01_FULL_LIVE_STATUS = INCOMPLETE
N02_FULL_LIVE_STATUS = INCOMPLETE
D01_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
D03_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
