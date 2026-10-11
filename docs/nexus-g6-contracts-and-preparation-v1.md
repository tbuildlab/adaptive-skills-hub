# Nexus G6 Contracts and Preparation v1

Status: preparation only; NON_AUTHORITATIVE. Accepted scope and reuse decisions:
[scope reconstruction](nexus-g6-scope-and-reuse-v1.md). G4 is preserved.

## Closed contracts

The five Roadmap names map to `ash/g6_contracts.py` kinds as follows:

| Accepted contract | Kind | Deterministic property |
|---|---|---|
| AcceptanceSuiteManifest | acceptance-suite | Eight A-H scenarios, ten native cases, explicit profiles/restrictions, materially different substitution and local/private requirement |
| ValueExperimentProtocol | value-protocol | Fair native/Nexus arms, nine required metrics, pilot/threshold preregistration, stopping/retention rules |
| QualificationRecord | qualification | Distinct capability/governance/effect results, exact attempt identity, observations, measurements and unknown cost |
| ReleaseEvidenceManifest | release-evidence | Exact artifact, Git source and components, seven integrity/release checks, non-authorizing approval references |
| SecurityFreezeRecord | security-freeze | Findings/fixes/retests/review references, reopening triggers, PREPARATION_ONLY |

Each record uses `nexus.g6.<kind>.v1`, `basis=NON_AUTHORITATIVE`, and
`dispatch_authority=none`. The common fields are binding, subject_id, observed_at,
expires_at and state. State is CURRENT or RETIRED. The validity window is at most
86,400 seconds; consumption checks the caller's clock. Generation, incarnation,
workspace/project/task/action/execution and input are reused from G4 binding.
No historical hash, fixture or manually constructed dataclass is trusted.

`record` validates bounded closed data, creates canonical bytes and a domain-separated
SHA-256 identity. `checked` reparses/revalidates those bytes, checks the identity,
binding, retirement and expiry. G1/G4 encoding limits and secret/path rejection are
reused without changing their implementation. Unsupported versions, cycles, extra
keys, malformed types and authority labels fail closed with fixed diagnostics.

## Structural bundle consumption

`validate_bundle` takes the five records, bounded qualification attempts, explicit
caller-owned expected binding/artifact/source/components/configuration profiles,
the independent attempt inventory, a content-addressed observation map and `now`.
It rechecks every record and exact cross-record link. Profiles are compared in full,
including restrictions, policy and Host/model identity; an unchanged digest alone
does not hide policy drift. Missing or duplicate attempts are rejected; repeated
non-idempotent attempt identities do not become distinct receipts.

Observation map keys equal the SHA-256 of their canonical metadata. This proves
metadata integrity and consistency, **not authenticity or execution**. Host identity,
raw source files, reviewers and measurements must be independently authenticated by
the qualified path before any live use. This module supplies no such path.

Observation shapes are closed:

* qualification: kind, evidence_type, binding_sha256, configuration_id, scenario_id,
  attempt_id, artifact_sha256, capability_result, governance_result, effect_outcome,
  observed_at, evidence_basis, measurements, monetary_cost_microunits;
* release_check: kind, binding_sha256, check_id, result, artifact_sha256, observed_at;
* document: kind, binding_sha256, purpose, subject_id, artifact_sha256, observed_at,
  source_ref. Purposes are pilot, finding, fix, retest, regression, independent_review,
  approval, publication or owner_acceptance. Finding/fix/retest subjects match the
  exact finding. Source references are pointers; their presence is no attestation.

All declared scenario/profile cells and all native-case/profile cells must have
attempts. Required evidence types must be covered. Useful-success cells require
an artifact-backed capability PASS; refusal-only cannot qualify a useful product.
Governance FAIL/UNKNOWN and unresolved UNKNOWN/CANCEL_REQUESTED effects refuse the
candidate. Failed capability attempts remain representable and retained alongside
successful ones; failure-free filtering violates the independent attempt inventory.
An effect NONE/SETTLED is an observation claim and not proof of cancellation safety.

Release checks require exact purpose, artifact and PASS. High/critical findings need
FIXED with fix/retest references, or FALSE_POSITIVE, plus an independent-review
reference. Missing referenced evidence is rejected. Lower unresolved findings may
remain recorded in preparation; they grant no production freeze. Optional absent
pilot/review/owner/publication evidence never defaults to satisfied live gates.

## Value and capability limits

The two protocol arms conserve Host/model, inputs, policy/permissions, criteria and
native features; only the Nexus treatment/configuration differs. G5 is disabled.
Metrics cover policy violations, evidence completeness, recovery accuracy, acceptance,
retries, cost, latency, human intervention and transparency. Numeric data use bounded
integers and explicit units; score scales belong to the referenced criteria.
Unknown measurements/cost remain unknown. No monetary savings are inferred.

DRAFT permits absent pilot and unknown thresholds. PREREGISTERED requires a pilot,
locked thresholds for every metric and explicit per-arm repetitions within the
attempt budget, registration before evaluation and no earlier
qualification attempt. It remains a **structural claim**, never verified historical
registration. Attempt and duration/cost limits are a protocol contract; this module
does not run experiments, automatically stop/retry work or compute benefit. The
qualified Host must enforce real budgets and retain the actual full attempt ledger.
Value qualification always remains UNMEASURED in this preparation API.

## Thin integration and fail-closed status

`ash/g6_host_adapter.py` composes optional accepted G4 Website/Report evidence checks
with the same task/clock/artifact. It emits bounded sanitized results and fixed
refusal codes; no raw exception, transcript, credential or tool output is returned.
`release_gate` calls G4's typed G3 boundary and always DENY. There is no enable flag,
dispatcher, callback, transport, model client, storage, retry, or production promotion.
Pure repeated structural checks are idempotent, not replayable execution authority.
Restart/copied records cannot restore positive admission. Existing G3/G2 own real
authority, lifecycle/replay/recovery; G6 does not replace them.

PASS_STRUCTURAL_ONLY reports consistency; capability NOT_LIVE_QUALIFIED, governance
STRUCTURAL_ONLY, value UNMEASURED, production_freeze DENY, real_admission_enabled false.
G3 remains INCOMPLETE, D01 CLOSED, D03 DEFERRED. Recovery-dependent requests retain
BLOCKED_BY_D03. Mock QUALIFIED metadata cannot qualify recovery. D04 is unchanged.

Synthetic examples live only in `tests/g6_fixtures.py`. Production imports neither
that module nor any tests. They prove contract behavior, not positive live support,
comparative value, independent review, owner acceptance or publication permission.

## Preparation inventory and release boundary

`research/nexus-g6-preparation-inventory-v1.json` links accepted source identities,
the support/test matrix and outstanding live evidence. It contains no runtime
qualification or external page content. Historical advisory experience is reused
by reference; no memory architecture or ingestion is added.

The existing manifest/package/release tooling checks real source/package bytes.
G6 metadata validation does not replace that tooling or claim to verify artifact
bytes supplied only as a digest. Development push is authorized by the owner;
it is distinct from production publication.

Preparation can close after contracts, integration, adversarial/full regression,
security/scope review, source/package verification, docs/MANIFEST, commit and verified
normal push. Production requires actual G3/D03 where applicable, two qualified
material configurations including useful local/private success, fair pilot-locked
value evidence, independent review, owner acceptance and exact authorized release.
The accepted production freeze sequence is not satisfied by this checkpoint.
