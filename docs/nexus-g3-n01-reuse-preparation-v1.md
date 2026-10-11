# G3 N01 reuse preparation v1

2026-10-11. Accepted parent: `5aea47b962113ae67821c1406766e15a78539287`.
This checkpoint is deterministic preparation, not a production authority service,
authenticated source, qualified primary ledger, live admission or independent review.

## Reused contracts and remaining gaps

The accepted N01 contract specifies sixteen closed state families and nine fixed
transaction groups. OpenAI/Codex retains reasoning, planning, tool selection and
execution. Nexus checks exact persisted state, references and transition ordering.
No planner, agent framework, model router, workflow engine, generic memory service
or automatic redispatch was introduced.

The unchanged subject/grant/revocation and Host proposal shape routines are now
shared pure codecs. The original public modules re-export the same objects;
their disabled real-admission and explicitly synthetic evaluation/correlation
behavior remains unchanged. D05 metadata and control snapshot encoding similarly
move into shared pure codecs with compatibility facades. Canonical v1 bodies,
domain-separated IDs, field sets, bounds and gate layout remain unchanged.
The production preparation modules do not import the old fixture evaluator or
Host correlation module. This addresses the original isolation test failure;
that test was retained unchanged. No test-only issuer or simulation is imported
by the new modules.

`ash/g3_control_semantics.py` checks complete retained-body/evidence consistency,
history, source-reference joins, exact Owner/context/material joins, revocation
index completeness, nonce/claim consumption, retirement and typed record stamps.
A successful consistency check returns authority NONE. Matching hashes cannot
authenticate a source writer, session, presentation or deployment.

`ash/g3_transition_protocol.py` encodes only the accepted nine transaction groups.
It checks exact predecessor/state binding, monotonic sequence/time, irreversible
consumption and retirement, retained history and recovery epoch/incarnation changes.
It produces PREPARED bytes only; it does not persist, append custody, finalize an
authority operation, dispatch an effect or acknowledge an Owner decision.

`ash/g3_primary_ledger.py` is an injected SDK transport for one exact proposed
DynamoDB table. Strong reads, immutable retained blobs, conditional head updates
and reservation/finalization transactions replace a custom database or journal.
Unknown writes are never retried. Startup and every ambiguous outcome quarantine;
prepared or finalized acknowledgments do not create authority. Stored pages are
bounded immutable hash references in the reservation, avoiding DynamoDB's 400 KiB
item limit while retaining the accepted 64-page codec. Native client-request-token
idempotency lasts only ten minutes and is not a permanent replay guarantee.

The transport's `independent_checkpoint` argument is unqualified bytes. Equality
alone is not independent current-head proof. A later protected controller must
authenticate the actual registered fence, history, source writers, current session,
configuration and deployment before any authoritative operation. There is no
public positive endpoint or dispatcher in this checkpoint. A `CheckedControl`
dataclass or `Preparation` value supplied by a caller is likewise not provenance.

## Exact compatibility issue retained for production composition

The historical D05 v1 structural layout contains eight gate facts, including D04,
and requires all eight to PASS on its positive shape. The accepted
[delegated policy](nexus-g3-delegated-executor-authority-policy-v1.md) explicitly
excludes D04 from release gates while preserving its historical unqualified status.
Neither a fabricated D04 PASS nor changing the historical v1 all-PASS parser is
acceptable. Current v1 helpers remain untrusted preparation. Before a delegated
positive transition, implement and qualify an explicit additive versioned seam
binding the delegated mode and exact protected configuration, preserving all seven
remaining mandatory gates and truthful historical D04 evidence. That seam is
implemented as the separate untrusted v2 record codec documented in the
[additive compatibility contract](nexus-g3-delegated-record-compatibility-v2.md).
Its structural validation is complete; control-state semantic integration,
protected runtime membership and live qualification remain open. An executor
identity cannot replace the Owner Principal;
delegation cannot fabricate a human CONFIRM or trusted receipt.

## Host and service reuse evidence

Authenticated Vercel project discovery found the existing `nexus-g3-qual` project
`prj_xH23xMATVChdhX34OS2vjI8dfWN2`; authenticated user metadata reports Hobby.
The team endpoint returned 403, while user and project reads succeeded; it does
not prove absent project access or justify credential-cache extraction. Existing
D01 source, closed ceremony and deployment are preserved. Hobby permits personal
non-commercial use and pauses most features after included usage exhaustion;
remaining usage and suitability for commercial production are not established.
No upgrade, deployment, credential retrieval or new D01 ceremony was performed.
[Hobby rules](https://vercel.com/docs/plans/hobby).

Native Vercel OIDC is a candidate for temporary AWS credentials without new static
keys. Exact owner/project/environment issuer, subject, audience, deployed revision
and runtime token origin require actual verification. The proposed `tdy0225`
namespace is not silently qualified from a user name. Tokens remain memory-only,
never evidence or logs. Existing GitHub OIDC immutable-ID binding is already
qualified for the bounded D03 run; a different runtime scope needs exact new roles
and qualification. [Native AWS federation](https://vercel.com/docs/oidc/aws).

N01/N02 remain incomplete: actual protected source membership, current session
mapping, fixed confirmation ingress, authenticated receipt issuance, delegated
composition, qualified recovery integration, mediation and E2E are open. G4/G6
live value/governance qualification, independent review and final exact Owner
acceptance remain open. Preparation cannot promote any of those gates.

## Validation taxonomy

Sixty-four new unique simulation/contract tests cover consistency, invalid joins,
generation/incarnation, corrupted history, fixed transitions, restart quarantine,
conditional reservations, dropped acknowledgments and bounded SDK input shapes.
The official installed botocore model validates actual GetItem/PutItem/
TransactWriteItems parameter shapes without network or credential access. The
test-only MemoryClient is not real DynamoDB enforcement. Existing pinned
`research/nexus-production-d03-sdk-requirements-v1.txt` supplies this development
SDK dependency; no new library or infrastructure is installed by the transport.

The retained D03 regression baseline is 1,533 unique cases / 1,529 PASS / four
existing environment skips / zero FAIL. Current full Python regression on the
LF-normalized preparation snapshot completed 1,219 cases / 1,215 PASS / four
existing environment skips / zero FAIL in 1,014.692 seconds. The twelve additive
v2 record cases were added after that snapshot and passed separately. The 366
unchanged Node cases retain the prior exact-source successful regression; no D01
ceremony was repeated. Combined distinct coverage is 1,597 / 1,593 PASS / four
SKIP / zero FAIL across these explicitly separate snapshots. Repeated focused
cases are not added to totals; this is not live qualification.
Current relevant focused regression: **282 PASS / zero SKIP / zero FAIL** after
repairing both production-preparation imports of the legacy test-capable modules.
The original failing logs remain retained as failed attempts, not counted as PASS.
G4/G6 architecture and D01 source are unchanged. No required path is marked PASS
from a simulation or source hash.

```text
D03_STATUS = CLOSED_BOUNDED_DIAGNOSTIC_TEN_GATE
D01_STATUS = CLOSED
G3_STATUS = INCOMPLETE
N01_IMPLEMENTATION_STATUS = PARTIAL_DETERMINISTIC_PREPARATION
N01_PRIMARY_SERVICE_QUALIFICATION = NOT_PERFORMED
N01_SOURCE_PROVENANCE_QUALIFICATION = NOT_PERFORMED
N02_PRODUCTION_INGRESS = NOT_IMPLEMENTED
DELEGATED_POSITIVE_COMPATIBILITY_SEAM = STRUCTURAL_V2_CODEC_ONLY_UNTRUSTED
G4_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
G6_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
