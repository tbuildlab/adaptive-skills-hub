# G3 U1 implementation readiness plan v1

Date: 2026-10-08. Offline preparation authorized; production authority not ready.
Inputs: [consistency review](nexus-g3-u1-architecture-consistency-review-v1.md),
[D01](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md),
[D03](nexus-g3-u1-d03-recovery-fence-qualification-v1.md),
[D04](nexus-g3-u1-d04-executor-exclusion-and-mediated-dispatch-v1.md),
[D05](nexus-g3-u1-d05-production-authority-contracts-v1.md).

## Task classification and stop gates

Categories are prerequisites, not mutually exclusive labels. READY_OFFLINE does
not mean a deployed positive authority can use its output.

| Task | Categories | Permitted next action / stop |
|---|---|---|
| Strict JSON, canonical bytes, domain IDs, seven closed outer envelopes and self-contained nested metadata | READY_OFFLINE | Implement isolated pure helpers; explicitly return untrusted metadata; adversarial tests. |
| Production complete schema/parser joins | READY_OFFLINE for documented structural checks; REQUIRES_OWNER_ACTION for unresolved issuer/row/payload semantics | Record unresolved semantic joins; do not advertise complete qualification. |
| Closed N01 control row schemas and leadership protocol | READY_OFFLINE design preparation | Row inventory/retention/compaction need a separately reviewed concrete storage design before any durable authority implementation. |
| N01 protected positive state machine | BLOCKED_BY_D04; REQUIRES_LIVE_QUALIFICATION | No receipt/grant/intent/claim issuance implementation in this run. Missing D01/D03/D04 keeps it closed. |
| N02 fixed confirmation surface | BLOCKED_BY_D04; REQUIRES_OWNER_ACTION; REQUIRES_LIVE_QUALIFICATION | Future fixed render/origin/CSRF tests and independent Owner browser custody; no UI/login implementation now. |
| Stytch relying-party adapter | REQUIRES_OWNER_ACTION; REQUIRES_CREDENTIALS; REQUIRES_CLOUD_RESOURCE_CREATION; REQUIRES_LIVE_QUALIFICATION; BLOCKED_BY_D04 | First prove issuer/client semantic mapping and factor policy, then separately authorize disposable project/login. No remote calls now. |
| D03 fence adapter | REQUIRES_CREDENTIALS; REQUIRES_CLOUD_RESOURCE_CREATION; REQUIRES_OWNER_ACTION; REQUIRES_LIVE_QUALIFICATION; BLOCKED_BY_D04 | Prove closed row inventory, independent account/policies, retention continuity and crash/recovery; no AWS creation/calls now. |
| Dispatch claim adapter | BLOCKED_BY_D04; REQUIRES_CREDENTIALS; REQUIRES_LIVE_QUALIFICATION; REQUIRES_OWNER_ACTION | Exact payload enforcement and absent alternate effect routes; no provider credentials/dispatch now. |
| Fixture/adversarial/regression tests | READY_OFFLINE | Synthetic untrusted data only; existing fixture seam stays test-only; no production runtime imports tests. |
| Live exclusion/identity/fence qualification | REQUIRES_OWNER_ACTION; REQUIRES_CREDENTIALS; REQUIRES_CLOUD_RESOURCE_CREATION; REQUIRES_LIVE_QUALIFICATION | Separate bounded disposable-account diagnostic authorization required. Never infer success from docs/tests. |
| Real admission activation | BLOCKED_BY_D04; REQUIRES_OWNER_ACTION; REQUIRES_LIVE_QUALIFICATION | Separate explicit authorization after all production dependencies and technical/task/Host/G1/G2 gates qualified; not automatically enabled by test success. |

## Exact implementation and qualification order

1. Pure production metadata schema/parser preparation, strict canonicalization,
   deterministic IDs and closed nested validation. Keep every value UNTRUSTED.
   Test malformed graphs/UTF-8, unknown fields/version/variants, domain confusion,
   duplicate keys, limits and deterministic IDs, plus old fail-closed behavior.
2. Resolve and review D01 semantic issuer/client mapping, enrollment/factor policy,
   D03 closed control rows and inventory/leadership/retention rollover, and fixed
   Subject-specific target/payload contracts. This is a dependency gate, not code.
3. Qualify D04 infrastructure/Owner isolation using separately authorized resources
   and negative access evidence. Code development does not substitute for this gate.
4. Only after those prerequisites are explicitly qualified and implementation is
   separately authorized, implement N01 protected state machine and durable
   transition protocol with fake-only tests first; no live positive deployment yet.
5. Implement the minimal fixed N02 server-rendered surface colocated with N01;
   test full frozen material display, exact Owner and anti-CSRF/origin/session joins.
6. Implement the Stytch relying-party adapter against pinned supported APIs and
   protected custody; isolated live sign-in/revoke/factor/account tests require the
   separate diagnostic authorization. Direct remote claim recheck, no local JWT fallback.
7. Implement D03 ledger/fence adapter and independent recovery administration.
   Qualify conditional writes, complete history, restoration, all crash intervals,
   leader exclusion, clock/retention/size rollover; unresolved fault quarantines.
8. Implement protected dispatch claim adapter against one exact qualified provider
   action; verify complete mediation and no equivalent executor route. Fake effects
   first; real provider qualification requires separate effect authorization.
9. Run full offline adversarial/state-machine tests after every implementation
   slice, followed by authorized integrated live D01/D03/D04/N02 qualification.
   Revoke/claim, CONFIRM/DENY, stale generations, restart, fence uncertainty and
   unknown provider outcomes must preserve consumption and close release.
10. Independently review exact deployed code/config/effective permissions and all
    current technical/task/Host/G1/G2 gates. Obtain separate real-admission activation
    authorization. No auto-activation, fixture seam, copied receipt or bypass flag.

Steps 1 and documentary parts of step 2 are the current authorized implementation
preparation. The remaining steps are an ordered future plan with STOP conditions.
No general IAM/OAuth/approval/policy/vault service, lifecycle broker or custom PKI
is added. N01/N02 remain the two proposed new trusted application components.

## Current closure gaps

Stytch-to-D05 Principal mapping is BLOCKED; exact login/factor and Owner enrollment
are unqualified. D03 root/page encoding is DEFINED but semantic row schemas and
complete durable inventory/leadership/retention rollover are not. D04 has no deployed
proof across the fifteen surfaces. Full production payload contracts/render proof
and independent recovery tests remain outstanding. Public `evaluate_eligibility`
continues to deny `G3_APPROVAL_ORIGIN_UNVERIFIED`; the new metadata module has no
call path from it or any public execution consumer.

```text
OFFLINE_PREPARATION_READY = YES
PRODUCTION_SCHEMA_FULL_SEMANTIC_VALIDATION_READY = NO
N01_IMPLEMENTATION_READY = NO
N02_IMPLEMENTATION_READY = NO
STYTCH_ADAPTER_IMPLEMENTATION_READY = NO
D03_IMPLEMENTATION_READY = NO
D04_IMPLEMENTATION_READY = NO
LIVE_QUALIFICATION_REQUIRED = YES
U1_IMPLEMENTATION_CANDIDATE_READY = NO
REAL_ADMISSION_ENABLED = NO
GRANTS_REVOCATIONS_ISSUED = 0
PROVIDER_EXECUTIONS_ADDED = 0
FAIL_CLOSED_BOUNDARY = PRESERVED
```
