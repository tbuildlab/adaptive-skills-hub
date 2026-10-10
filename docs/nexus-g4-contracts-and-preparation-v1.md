# Nexus G4 Contracts and Preparation Integration v1

Status: implemented offline, PREPARATION_FAIL_CLOSED. No production enable switch.
The [reuse survey](nexus-g4-reuse-survey-v1.md) identifies accepted source contracts.

## Module guarantees

`ash/g4_contracts.py` guarantees closed schemas, bounded canonical encoding,
source/project/task/recipient binding, exact repository/base/input binding,
scoped decision confirmation evidence, explicit supersession history, closed
versioned relationships, dependency-cycle refusal, conservative unknown-impact
handling, permission narrowing and required domain acceptance coverage.
It reuses G1 validators, Slice 3C JSON encoding/parser and public-evidence
redaction patterns. It does not retrieve, reason, confirm, forget or persist.

`ash/g4_host_adapter.py` guarantees request/result binding, typed production G3
input, unconditional production DENY, explicitly non-authoritative structural
fixtures, process-local one-use action/result checks, fixed sanitized audit
projection and an unqualified recovery port. It reuses G2 ExecutionStatus.
It does not dispatch, invoke tools, retry, reconcile external effects or store
an execution ledger. OpenAI/Codex and the Host continue to do that work.

## Common wire rules

JSON input is at most 65536 bytes, with no duplicate keys, NaN, arbitrary objects,
subclasses, cycles, secret/private-path patterns, extra fields or unsupported
versions. G1 structural bounds apply: depth 12, 64 items per collection, 16000
nodes, 512 characters per string, nonnegative signed-64-bit integers. No floats,
raw commands, output prose, bearer data or hidden reasoning are fields. Diagnostics
are fixed codes. Lists representing sets are normalized and reject duplicates.
References are lowercase SHA256; tokens use the frozen G1 grammar. Digests prove
integrity and binding, never source authenticity. Source/confirmation facts are
provided by the trusted caller in this offline test interface and remain
NON_AUTHORITATIVE; copying them cannot turn them into production credentials.

Every domain record has exact `schema_version` and `binding`. Binding contains
workspace_id, project_id, task_id, action_id, execution_id, positive generation,
incarnation and input_sha256. Domain-specific identities use an isolated G4
hash domain and do not change frozen Slice 3C or G3 typed IDs.

| Record / schema suffix | Exact additional fields | Deterministic condition |
| --- | --- | --- |
| ProjectDecisionRecord / project-decision.v1 | decision_key, content_sha256, source_refs, approving_authority_ref, valid_until, state, supersedes, retention, obligations | PROPOSED/CONFIRMED/SUPERSEDED/DISPUTED remain distinct. Active CONFIRMED needs current included sources and separate confirmation reference. One active alternative per decision key; independent keys coexist. Superseded history must be accessible and cannot be simultaneously active. Forgetting unresolved obligations is refused. |
| ContextManifest / context-manifest.v1 | sources, recipients, omissions, disclosure_limits, preserved_obligations | Source has ref, sha256, project_id, task_id, transformation, original_ref, valid_until. ORIGINAL and DERIVED remain distinct; derived evidence needs an accessible distinct original. Expected source digest and recipient scope must match. Omitted mandatory obligations refuse acceptance. |
| CapabilityRelation / capability-relation.v1 | relation, from_endpoint, to_endpoint, provenance_refs | Exact ref/version endpoints; eight Roadmap types only. Dependency cycles, conflicts, wrong versions and unavailable provenance refuse acceptance. No edge confers authority. |
| ChangeImpactRecord / change-impact.v1 | repository_id, base_commit, changed_surfaces, dependencies, consumers, shared_contracts, validation_obligations, unexamined | Exact independent repository/base/input oracle; declared expected shared consumers and validations must be covered. Nonempty unexamined blocks acceptance. No completeness inference from imports or empty lists. |
| WorkflowPack / workflow-pack.v1 | pack, version, applicability, required_capabilities, allowed_operations, required_evidence | website or source_backed_report; current task class applicable, required capabilities supplied, operation set narrows superior permissions. Mandatory evidence cannot be removed by a pack. |

Full wire schema prefixes are `nexus.g4.`. Canonical immutable DomainRecord carries
kind, canonical_body and record_id; every consumption rechecks schema, bytes and
identity, so manually constructed records cannot inherit trust.

## Two packs and independent observation oracle

Website requires interaction, consumer_regression, accessibility, boundary and
artifact_inspection. Source-backed Report requires source_claim, uncertainty,
calculation, artifact_inspection and render. Change-impact obligations add required
observations. Each observation has status, input_sha256, artifact_sha256 and
source_refs. All observations, including optional failures, are retained in the
check and must PASS for acceptance; every observation binds the same input and
artifact and accessible source references. A changed artifact, unsupported claim,
missing calculation/render or failure hidden during reduction cannot inherit PASS.

`validate_domain_bundle` requires independent expected binding, repository/base,
source digest map, task class, scope/recipient restrictions, confirmations,
endpoint versions, expected obligations/consumers/validations and available
capabilities. It returns only PASS_STRUCTURAL_ONLY / NON_AUTHORITATIVE / authority
none. Host analysis and source-to-claim semantics remain external. The tests are
synthetic boundary oracles, not real Owner confirmation, real workflow success,
privacy enforcement, source truth, current capability conformance or G2/G3/D03
qualification. No automatic supersession/forgetting state machine exists.

## Host adapter use

Production: `pre_execution_gate(request, typed_g3_decision_or_none, now=...)`
returns DENY on every path while G3 is incomplete. Missing/malformed, expired,
fixture-origin and incomplete authority have distinct safe diagnostics. A copied
JSON decision and even a positive typed G3 test decision cannot admit production.
No positive dispatcher or configurable real-admission flag is present.

Offline: create StructuralSession; call its fixture(request, now=...); call check
with that fixture. A successful check is ALLOW_STRUCTURAL_TEST_ONLY and authority
none. For a domain workflow use check_domain(request, fixture, bundle=..., now=...); it validates the complete pack bundle and exact request/time binding before consuming the structural action. Raw check validates only an execution contract and cannot certify pack acceptance. Request schema has binding, operations, expires_at and requires_recovery.
Fixtures are session-bound, NON_AUTHORITATIVE and valid for at most 300 seconds
in the caller's explicitly supplied test clock. Action uniqueness binds workspace,
project, task and action across generations/execution IDs. At most 64 consumed
actions are retained, without eviction; a lock serializes competing checks.
This is a bounded test-consumption set, not a replacement G2 ledger.

Feed a closed `nexus.g4.openai-execution-result.v1` with basis, binding, status,
observed_at and evidence into record_result for the issued request_ref. Evidence
contains type, source, sha256, ref, observed_at and result. Evidence age is bounded
by 300 seconds, cannot be in the future or precede this session's start admission,
and must match the attempted outcome. Raw stdout/stderr, arbitrary metadata,
secrets and reasoning are rejected. Audit includes hashes/enums/evidence references
only, not project names, commands or credentials.

| Host result | Existing G2 status recorded | Interpretation |
| --- | --- | --- |
| COMPLETED | VERIFICATION_REQUIRED | Host success remains unqualified until independent validation. |
| FAILED | FAILED | Failure evidence retained; action is consumed. |
| CANCELLED | CANCEL_REQUESTED | Request/ack evidence is not proof of stopped remote effects. |
| UNKNOWN | OUTCOME_UNKNOWN | Outcome unresolved; no automatic redispatch. |

One valid result consumes the pending reference for every outcome. Late outcomes
may be recorded after the original request expires; this does not extend authority
or permit another action. Invalid result data is refused and pending work remains
unresolved. The session's restart_snapshot serializes evidence only with resume
DENY. New sessions reject old fixtures and cannot import pending references.
No replay/rollback/cross-process durability or hostile same-process resistance is
claimed. Qualified production recovery must come from G2/D03, not this test set.

## Recovery and production dependency boundary

RecoveryFencePort is the future seam. UnqualifiedRecoveryFence reports UNQUALIFIED.
Every current recovery-dependent request DENYs, including a mock returning
QUALIFIED or a port exception. Mocks test seam behavior only. There is no AWS
client, fence service, new database/queue, paid resource or production-positive
restore path. D03 remains DEFERRED; live recovery is BLOCKED_BY_D03.
G3 stays INCOMPLETE and real admission NO. D01 stays CLOSED within its historical
bounded profile. Historical D04 bytes/status are preserved and D04 is not added
as a delegated-mode release gate.

## Compatibility, qualification and stopping

Existing planner, MCP surface, schemas, G1/G2/G3 production code, Core Alpha 2 and Slice 3A-3C are unchanged. The historical G3 test that prohibited every future contract consumer is explicitly extended to permit this deny-only G4 adapter; new production-DENY, no-dispatch and no-test-import assertions preserve its isolation purpose. No test is disabled or made to accept a production positive path. No package dependency is added. Tests live under tests and are not
imported by either production-facing module. No Agent, planner, router, memory,
retrieval/graph engine, workflow scheduler, browser runtime or retry engine is
introduced. No provider Responses execution is added.

Run focused checks with the existing Nexus Python runtime:
`python -m unittest tests.test_g4_contracts tests.test_g4_host_adapter -q`.
Run full regression with `python -m unittest discover -s tests -q`, regenerate
MANIFEST with scripts/build_manifest.py and check package reproducibility and
`git diff --check`. Source identity and secret scan remain separate from tests.

The development checkpoint can mark independent implementation and offline
qualification COMPLETE/PASS. The Roadmap's final G4 release tag remains withheld
until real bounded workflows and the applicable qualified G2/Host evidence pass.
Live authority integration is BLOCKED_BY_G3; real recovery BLOCKED_BY_D03. No
routine Owner action is needed to finish or retain this preparation checkpoint.

G2 historical managed v3 acceptance is preserved; it is not relabeled HOLD. Production Positive Host Binding remains ABSENT. Package qualification uses an isolated LF-normalized source snapshot containing exactly reviewed files; generated local state is excluded without changing or deleting historical evidence.

The release-isolation regression now uses an explicit historical fixture clock for the frozen August research catalog and separately asserts that expired evidence has no recommendations and no authority. The runtime TTL and historical catalog bytes are unchanged. This fixes a date-dependent test expectation rather than renewing stale evidence.
