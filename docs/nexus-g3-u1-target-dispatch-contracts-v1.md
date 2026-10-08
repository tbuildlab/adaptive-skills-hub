# G3 U1 exact target and dispatch contracts v1

2026-10-08. Fixed contract framework, no real provider adapter.
Inputs: [D05 Material](nexus-g3-u1-d05-production-authority-contracts-v1.md),
[N01 state](nexus-g3-u1-n01-protected-control-state-v1.md).

## Protected registry

N01 registers an immutable contract tuple under a new registration ID; changes
retire old registrations and their unclaimed lineages. The tuple comprises
SUBJECT_KIND, TARGET_CONTRACT_REVISION, DISPATCH_CONTRACT_REVISION,
ADAPTER_REVISION, ENVIRONMENT_REGISTRATION and ENFORCEMENT_PROFILE.
The N01 registration row retains their exact identities, contract/config/enforcement
digests, environment generation and N01/N02 deployment revisions. Complete
contract bodies/configuration and deployment evidence must resolve through protected
retained provenance. No executor field chooses a schema, route, registry or resolver.

For every executable existing Subject kind, a separate qualified fixed contract
must specify exact target bytes, operation, ordered arguments, environment/account,
tool/provider route, frozen configuration revision, adapter revision, canonical
payload bytes, enforcement capabilities and expected effect/result class. The
framework does not register any real Subject kind as executable. Unknown kind,
missing contract or provider transformation remains BLOCKED/DENY. Existing
Subject and D05 bodies/IDs/canonicalization remain unchanged.

Each future contract must provide: a closed schema without extensible arbitrary
command fields; a deterministic encoder; a complete bounded plain-text display;
a validator checking Subject/scope/account/effect joins; an independently
qualified adapter that consumes the exact frozen bytes; and a conformance suite
for its exact provider API/version. Runtime credentials are injected solely through
the protected adapter's registered custody, never used as target material or
serialized in canonical records. Credential *account identity* and environment
must already be frozen and shown, without exposing the credential.

## Binding stages and mismatch behavior

| Stage | Required proof | Failure disposition |
|---|---|---|
| Proposal intake | Untrusted existing Subject/body parsed exactly; protected registry selects a compatible fixed kind | DENY unknown/oversize/malformed material; never invent a generic fallback |
| Target qualification | Full target/operation/arguments/account/environment/route/config/revisions and enforceable effect class | DENY unavailable exact material; BLOCKED unknown provider transformation |
| Display freeze | D05 targets/dispatch JsonEvidence contain canonical full bytes and registered schema hashes; display every effect-relevant value through registered fixed template | DENY truncation/hidden defaults; escape as text; no mutable URL/file/config indirection |
| Receipt | Terminal protected view membership binds exact display, Subject/scope/proposal and context | RETIRE stale/mismatched view/context; canonical copied receipt alone cannot authorize |
| AdmissionIntent | Exact grant/receipt/material/registry/current gate joins plus complete revocation generation | DENY negative/unknown gate; RETIRE changed registration |
| Claim exact check | Recompute canonical payload and target digests, verify same protected registration/deployment/environment and unique claim | RETIRE before claim on revision/material mismatch; QUARANTINE authoritative corruption |
| Protected handoff | Claimed immutable dispatch bytes, registry tuple, digest and exclusive deadline; no executor payload replacement | QUARANTINE mismatch; claim remains consumed, no effect release |
| Provider invocation | Fixed compiled/registered adapter invokes only the qualified operation with those arguments and exact account | BLOCKED unqualified behavior; UNKNOWN if invocation may have occurred |
| Result evidence | One protected result tied to consumed attempt, expected result class | UNKNOWN ambiguous/missing outcome; result never authorizes retry |

Equality is byte equality plus the qualified typed interpretation, not digest-only
display or caller assertion. Adapter takes one frozen dispatch material, validates
all joins and its registered revision before handoff; it cannot broaden scope,
add default arguments, reinterpret flags, select another provider route or introduce
environment-variable material after display. Frozen environment values are fully
shown if they affect effects; secrets are not allowed in that material. Post-approval
mutable references are prohibited, including redirects, symlinks and config aliases.
Where a provider necessarily transforms an invocation, a contract must prove the
transformation preserves the exact approved effect. Unproved behavior is BLOCKED.
Unsupported or oversized values DENY, never truncate or split into hidden actions.

## Synthetic reference contract

The only reference registry is `synthetic.echo.v1`, TEST_ONLY. It is not a new
production Subject kind or a provider adapter. Target exact fields are
`{resource, content}`; resource is exactly `test-only:buffer`, content is NFC plain
text <=256 characters. Payload exact fields are `{operation, arguments}`;
operation is exactly `echo`, arguments is a one-element array exactly equal to
target.content. No arbitrary command, URL, file, network or environment lookup
is possible. Canonical JSON uses unchanged D05 canonical bytes and plain SHA256.
Expected class is `TEST_OBSERVATION_ONLY`; fake handoff returns only an untrusted
digest observation. Environment is `test-only`, generation 1, adapter `fake.v1`.
Target and dispatch revisions are fixed to `synthetic.target.v1` and
`synthetic.dispatch.v1`; enforcement identity is `no-effects.v1`.

The test registry has no PRODUCTION lookup or registration/promotion API. Its
validator rejects changes to target bytes, payload arguments, revision, adapter,
environment or operation. Positive test transitions prove only model behavior,
never D05 semantic admission or a production capability. Real Subject-specific
schemas and provider conformance remain individually unqualified.

```text
TARGET_DISPATCH_CONTRACT_FRAMEWORK = DEFINED
SUBJECT_SPECIFIC_CONTRACTS_REQUIRED = YES
GENERIC_ARBITRARY_PAYLOAD_ALLOWED = NO
EXECUTOR_SELECTED_CONTRACT_ALLOWED = NO
OWNER_DISPLAY_TO_DISPATCH_BINDING = DEFINED
TARGET_CONTRACT_REGISTRY = DEFINED
DISPATCH_CONTRACT_REGISTRY = DEFINED
ADAPTER_REVISION_BINDING = DEFINED
REAL_PROVIDER_ADAPTERS_IMPLEMENTED = NO
TARGET_DISPATCH_IMPLEMENTATION_READY = YES
```

YES means framework/synthetic offline validation is ready. Each real executable
Subject contract and adapter still needs qualification; no generic positive path
is authorized by this result.
