# G3 U1 N01 protected control state v1

2026-10-08. Closed storage specification and offline preparation only.
Inputs: [D05](nexus-g3-u1-d05-production-authority-contracts-v1.md),
[D03 codec](nexus-g3-u1-d03-recovery-fence-qualification-v1.md),
[bounded context](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md).
No production N01, database adapter or authority is implemented here.

## Closed inventory and value types

Sixteen logical families map into the existing thirteen snapshot namespaces.
Root, recovery, registration and source-provenance share `provenance`, each with
a distinct closed discriminator. No namespace or D05 body is redefined.
Each row value has exactly `schema_version, family, revision` plus the fields
listed below; version is `nexus.g3.n01-control.v1`; revision is an integer >=1.
Unknown fields, families, discriminators or schema versions deny decoding.
The key is exactly `family + ':' + identity`, not a caller-selected partition key.

Types reuse D05: token (96-character syntax), NFC nonempty text <=512, SHA256,
unsigned signed-64-range integer, positive generation, exact Principal, RecordRef
and EvidenceRef. References are typed to the named unchanged record body and
must resolve retained canonical bytes with matching ID/body hash. `null` is allowed
only where expressly stated. Lists have at most 64 entries, sorted unique by ID;
no bearer material is a legal value. Deadline comparisons are exclusive UNIX_MS.

| Family / namespace / identity | Exact additional fields and constraints |
|---|---|
| root / provenance / authority_instance | authority_instance, authority_epoch, incarnation, recovery_sequence, previous_checkpoint (RecordRef or null only for GENESIS), time_high_water_ms, quarantine (OPEN/CLOSED), revocation_generation. Root instance/key and snapshot header agree. Epoch/generation >=1. |
| binding / bindings / binding_id | binding_id, principal, owner_generation, workspace_id, project_id, binding_generation, state (CURRENT/RETIRED). One current binding for exact workspace/project; independent enrolled principal only. |
| context / contexts / context_id | context_id, context_generation, binding_id, binding_generation, owner_generation, authority_epoch, incarnation, provider_project, provider_user, provider_session, authenticated_at_ms, expires_at_ms, identity_evidence, session_evidence, state (CURRENT/CONSUMED/RETIRED). Provider identifiers are text, not bearer. Evidence fields are EvidenceRef. Absolute lifespan <=300000 ms, one challenge, no refresh/restart. |
| challenge / challenges / challenge_id | challenge_id, record_ref, context_id, view_id, nonce, expires_at_ms, state (PENDING/CONFIRM/DENY/RETIRED). Nonce is lowercase 64-hex; ID/ref resolve R01. |
| view / views / view_id | view_id, record_ref, context_id, challenge_id, presentation_sha256, template_revision, deployment_revision, state (CURRENT/RETIRED). Resolve R02 and full exact frozen display; one current view per challenge/context. |
| decision / decisions / challenge_id | challenge_id, record_ref, choice (CONFIRM/DENY), context_id, view_id, nonce. Resolve R03; unique terminal decision, immutable. |
| receipt / receipts / challenge_id | challenge_id, record_ref, decision_ref, expires_at_ms. Resolve R04/R03 exact lineage; immutable and never bearer authority. |
| grant / grants / grant_id | grant_id, record_ref, receipt_ref, issuer_registration, state (CURRENT/CONSUMED/RETIRED), use_until_ms. Retain exact v1 body, qualified production issuance provenance and receipt lineage. Fixture grants cannot enter membership. |
| revocation / revocations / index_id | index_id, grant_id (token or null for global index), revocation_refs, generation, completeness (COMPLETE/INCOMPLETE), state (INDEX/CLEAR/REVOKED). One global row `index_id=authority`, grant_id=null, state=INDEX commits complete index generation. Per-grant rows have index_id=grant_id; CLEAR can become REVOKED only. Retained exact v1 revocations and sticky tombstones; no deletion. |
| nonce / nonce_consumption / nonce | nonce, challenge_id, state (PENDING/CONSUMED/RETIRED), decision_ref (RecordRef or null only before terminal decision/retirement). Globally unique per authority lifetime, including old epochs. |
| intent / intent_indexes / intent_id | intent_id, record_ref, task_id, grant_id, target_sha256, payload_sha256, registration_id, context_id, use_until_ms, state (ADMIT_PENDING/DENIED/CONSUMED/RETIRED). Resolve R05; exact frozen material and task/grant joins; one intent lineage cannot be regenerated to evade consumption. |
| claim / claim_indexes / attempt_key | attempt_key, intent_id, record_ref, result_ref (RecordRef or null before RESULT), handoff_deadline_ms, outcome (CLAIMED/SUCCEEDED/FAILED/UNKNOWN). Resolve R06 CLAIM/RESULT; unique intent claim as well as attempt key, consumption irreversible. |
| retirement / retirement / entity_id | entity_kind (one of the sixteen families), entity_id, retired_sequence, reason (EXPIRED/INVALIDATED/RESTART/REVOKED/MISMATCH). Composite identity `entity_kind:entity_id`; never removes the underlying terminal identity. |
| recovery / provenance / sequence as 20 decimal digits | sequence, checkpoint_ref, control_sha256, descriptor_sha256, state (WITNESSED). Immutable **prior** finalized transition history, only sequence < snapshot recovery_sequence. Never include the checkpoint being generated in its own snapshot. |
| registration / provenance / registration_id | registration_id, subject_kind, target_revision, dispatch_revision, adapter_revision, environment_id, environment_generation, target_contract_sha256, dispatch_contract_sha256, config_sha256, enforcement_sha256, runtime_revision, n02_revision, issuer_ref, state (CURRENT/RETIRED), purpose (PRODUCTION/TEST_ONLY). Exact protected deployed revision/environment/issuer identities, not an extensible policy language. |
| source / provenance / source_id | source_id, evidence_ref, assertion_sha256, kind (OWNER_ENROLLMENT/D01/D03/D04/TECHNICAL/TASK/HOST/G1/G2), principal, binding_id, context_id (token or null), registration_id, observed_at_ms, expires_at_ms, conclusion (PASS/FAIL/UNKNOWN), state (CURRENT/RETIRED). Protected sanitized source assertion membership, specific qualified writer per kind. Evidence bytes are retained independently and hash-checked; PASS text alone proves nothing. |

All unqualified actual subjects/contracts, registrations, source assertions and
production membership remain unavailable. This schema defines their closed
envelopes, not their live authenticity. Immutable D05/v1 body storage is a separate
content-addressed collection; its *complete provenance membership and hash* is
represented here. Unreferenced blobs never authorize. Operational caches are
derived only and must match a consistent authoritative revision before use.

## Boundary and transition rules for every family

All authoritative writers/readers below are future protected components, not this
offline model. Persistence is the N01 transactional ledger plus immutable body/
assertion/page storage, fenced by D03. Executor permissions are NONE for every
row, index, keyspace, backup and mutation; sanitized decision readback grants no
authoritative membership. D04 must prove this exclusion before positive use.

| Family | Writer; readers | Mutability / allowed transition | Generation, recovery, tombstone and replay |
|---|---|---|---|
| root | N01 coordinator; N01/recovery custodian | Conditional next sequence; quarantine only restricts until authorized RECOVER | Expected head/revision CAS; time never decreases; epoch rises only on recovery; old incarnation cannot reopen. |
| binding | N01 after independent Owner/admin ceremony; N01 | CURRENT -> RETIRED, replacement is new ID | Owner/binding generation increases; retired identity retained; no executor TOFU. |
| context | N01 relying-party adapter; N01 | CURRENT -> CONSUMED/RETIRED | Single challenge; generation exact; expired/old incarnation never refreshes. Retain retirement and sanitized evidence, never bearer. |
| challenge | N01; N01/N02 sanitized view | PENDING -> CONFIRM/DENY/RETIRED | Exact context/view generation; terminal nonce identity retained across restart. No duplicate terminal decision. |
| view | N01 fixed N02 registration; N01/N02 | CURRENT -> RETIRED | Replacement retires challenge/context and allocates fresh lineage; no second confirmable tab. |
| decision | N01 decision transaction; N01 | Create once, immutable | Same challenge/nonce has one choice forever; conflicting choice is corruption, not overwrite. |
| receipt | N01 same decision transaction; N01 | Create once, immutable | Exact decision provenance survives; expired or retired lineage is unusable even with copied body. |
| grant | N01 qualified issuer path; N01 | CURRENT -> CONSUMED/RETIRED | Unique production provenance, qualified issuer/receipt; restart retires current grants, retains body/consumption. |
| revocation | N01 revoke transaction; N01/recovery | CLEAR -> REVOKED; monotonically next global generation | Complete index verified at intent and claim; immutable retained refs/tombstones; no generation reset at epoch. |
| nonce | N01 decision/invalidation transaction; N01 | PENDING -> CONSUMED/RETIRED | No reallocation or terminal reversal; retired nonces remain unavailable. |
| intent | N01 evaluation/claim; N01/adapter sanitized claim | ADMIT_PENDING -> CONSUMED/RETIRED; DENIED terminal | All task/grant/material/deadline joins exact; recovery retires pending, never resurrects denied/consumed. |
| claim | N01 protected claim/result path; N01/adapter | CLAIMED -> SUCCEEDED/FAILED/UNKNOWN once | Attempt and intent uniqueness; missing result is UNKNOWN after interruption; NO_AUTOMATIC_REDISPATCH. |
| retirement | N01 invalidation/recovery; N01 | Append immutable identity tombstone | Retired sequence <= current; cannot be omitted by compaction or restore. |
| recovery | N01 after prior witnessed finalize; N01/recovery custodian | Append immutable earlier checkpoint | Exact predecessor and gap-free global sequence; restore cannot choose a convenient earlier head. |
| registration | Independently authorized deploy/admin through N01; N01/adapter | CURRENT -> RETIRED; replacement new registered revision | No caller schema/provider/env selection. Preserve all revisions and exact target/dispatch contracts; change retires affected lineage. |
| source | Qualified source adapters through N01; N01 | Immutable assertion, CURRENT -> RETIRED | Bound issuer/principal/context/registration; observed/expiry deadlines; caller-provided PASS never promoted. |

Every family is included in `control_after_sha256`; corrupt, omitted, extra,
overlapping, ambiguous or mismatched rows/refs **QUARANTINE**, while malformed
untrusted intake **DENY**. No fallback to a weaker partial index. Cross-family
semantic validation requires all joins, global index completeness, unique active
binding/view/context memberships, and typed body/provenance equality. Structural
row encoding alone does not perform these checks.

Index completeness is a semantic obligation: exactly one global revocation row,
with empty header `revocation_refs`, generation equal to root.revocation_generation,
plus exactly one per-grant CLEAR/REVOKED row for every retained grant membership.
Every per-grant generation is <= the global generation; every retained v1 revoke
belongs to the exact grant and appears in its retained sorted refs. No orphan
revocation, missing grant row, missing provenance or omitted sticky tombstone is
allowed. COMPLETE is accepted only after this full consistent validation, never
because the header claims it. All unique grant IDs equal their exact v1 reference
IDs; other control IDs are tokens linked uniquely to their typed record references.

## Transaction groups and serialization

Each group conditionally reads the same authority head, all affected generations,
trusted nondecreasing time, current deployment registrations and complete revocation
index. A per-instance durable PREPARED reservation serializes *all* nine groups.
No group executes around an outstanding reservation. Finalized consistent head
is the linearization point. N01 cannot authorize direct provider release.

| Group | Atomic after-state membership / preconditions | R07 transition |
|---|---|---|
| T1 challenge | Registered Owner/binding/source, new non-refreshable context, unique authority nonce, pending challenge; expiry bounded by context | CHALLENGE |
| T2 view | Fixed registered N02/template, exact material; register view, or retire old view/challenge/context before a fresh T1 | INVALIDATE for replacement; CHALLENGE for initial view |
| T3 terminal decision | Exact pending challenge/current view/context, fresh source proof; consume nonce/context, unique decision+receipt, CONFIRM/DENY terminal index together | CONFIRM / DENY |
| T4 grant provenance | CONFIRM receipt lineage, exact v1 body and registered issuer, finite use-until, no fixture membership, unique grant | EVALUATE with grant ref; no new R07 enum |
| T5 revoke/invalidate | Append immutable revocation/tombstones, advance complete revocation generation; retire affected binding/context/view/grant/intent memberships; independently authorized Owner/deployment registration changes are INVALIDATE | REVOKE / INVALIDATE |
| T6 intent evaluation | Qualified gates and exact registered target/payload, current Owner context, grant provenance, complete revocation index; unique ADMIT_PENDING or terminal DENIED | EVALUATE |
| T7 claim | Expected intent, same principal/session lineage and fresh remote recheck, current gates/deadlines/materials; consume intent/grant and insert unique attempt together | CLAIM |
| T8 result | Exact existing claim, protected adapter provenance; append one result, UNKNOWN permanent on ambiguity; never produce a new claim | RESULT |
| T9 recovery | Independent latest-history proof and separate recovery authorization; increase epoch, new incarnation, retire all pending pre-restart memberships, retain consumption | RECOVER |

T1-T9 all require durable ledger PREPARED + exact independent D03 append/readback +
ledger FINALIZED **before any authoritative external usability or positive ack**.
Negative-only runtime quarantine may close immediately without a witness, but
can never reopen or acknowledge a successful revoke on uncertain persistence.
Initial instance/genesis enrollment is separately authorized under T9's recovery
custody, using the existing GENESIS transition at sequence zero only once. Owner
enrollment and registration changes use T5 with independent verified ceremony
evidence, never executor TOFU. New Owner generations retire old authority; any
affected pending lineages are retired in the same candidate after-state.
T3 DENY is persisted terminal, not an issued grant. Test labels never issue any
real record. Revocation wins if finalized before claim; a finalized claim is already
consumed if revoke follows. No atomic cross-service transaction is claimed.
Recheck local invalidation/deadlines and bounded remote source evidence after
fence, before adapter handoff. Source proof does not cover continuous provider
logout between remote check and claim; that accepted race remains explicit.

## Exact snapshot coverage, head relationship and retention

Use unchanged D03 root/page v1 encoding, all thirteen namespaces sorted by UTF-8
namespace/key bytes, including empty namespaces. Values are the closed schemas
above in exact D05 canonical JSON. Greedily pack sorted rows into pages, starting
a new page before 64 rows or 65536 canonical bytes would be exceeded. A row
value is <=16384 UTF-8 bytes; no representation truncates it. Page refs are ordered
by namespace/first_key, with exact first/last/count/hash. No page may be omitted.

The proposed after-state for sequence n contains root sequence n and predecessor
checkpoint n-1; its recovery rows contain only finalized checkpoints <n. Root
headers and root row agree. Hash snapshot first, hash the exact D05 ledger descriptor
second, construct unchanged R07 third. The checkpoint **n** is not inside its own
hash input. After finalize, the physical current checkpoint pointer is derived
from that exact witnessed R07 and verified against its sequence/descriptor/snapshot.
It is a consistency pointer, never independently writable authority. The next
transition includes n in recovery history. PREPARED/FINALIZED transport metadata
is outside the semantic snapshot; it can only close release until verified and
cannot supply omitted authority. A corrupt transport pointer quarantines.

Maximum pending challenges per binding: 8; maximum current contexts per binding:
8, with one challenge per context. Maximum total rows: 4096 subject to the stricter
64-page/65536-root-byte limit. Every singleton/global key and uniqueness index
must be complete. Exceeding any limit denies creation; retirement does not free
terminal identities. No TTL deletion on authoritative rows. Pending expiry only
permits a witnessed retirement transition; it never deletes nonce/claim history.
Immutable old page generations and checkpoint versions remain reachable through
retained transition history. Rollover repacks pages deterministically, retaining
the previous generation; never reset sequence, drop tombstones or truncate pages.
Capacity exhaustion closes service until a separately versioned, independently
reviewed larger codec/migration. This bounded design does not claim unlimited
operation. Retention/encryption custody must cover the entire relied-on authority
lifetime; unproved renewal or unavailable old history quarantines before expiry.

```text
N01_CONTROL_STATE_SCHEMA = DEFINED
N01_CONTROL_STATE_FAMILIES = 16
N01_TRANSACTION_GROUPS = 9
NONCE_CONSUMPTION_STATE = DEFINED
REVOCATION_INDEX_STATE = DEFINED
INTENT_CLAIM_STATE = DEFINED
RECOVERY_STATE = DEFINED
CONTROL_AFTER_SHA256_SEMANTICS = DEFINED
CONTROL_SNAPSHOT_SEMANTIC_ROWS = DEFINED
N01_STORAGE_SCHEMA_IMPLEMENTATION_READY = YES
REAL_ADMISSION_ENABLED = NO
```

Implementation-ready here means the closed storage specification can be encoded
and tested offline. It does not qualify production writers, authenticate actual
source assertions or authorize positive service implementation/activation.
