# Nexus Post-R5 Slice 3C — Immutable Ecosystem Intake & Security Quarantine

**Document type:** Architecture Decision Record (ADR) and Product Design
Specification (PDS)

**Status:** Implementation-ready; proposed for owner approval; specification
gate only

**Baseline:** `post-r5-runtime-integration-slice3b-final` at
`ae4b37a261c175627b13aceb6c2509cc617c5375`

**Implementation authority:** None. Approval of this document is required
before an implementation branch may be created.

**External-source activity during this gate:** None. The pilot repositories
are identities and frozen local evidence only; they were not downloaded,
cloned, installed, imported, or executed.

## Decision

Nexus will add a trust-decreasing, quarantine-only intake boundary between
Slice 2 candidate discovery and every trust-increasing capability plane. Slice
3C production will accept only explicitly supplied bounded ZIP bytes; hermetic
tests may generate synthetic ZIP bytes through the same validators. It will
normalize them into repository-external content-addressed storage, inspect them
as untrusted data, compare exact revisions, and emit subject-bound evidence. It
may quarantine or reject a candidate. It cannot approve, activate, route,
install, load, or execute one.

The permanent Slice 3C authority ceiling is:

```text
Slice 3C may store, normalize, inspect, compare, quarantine, or reject
an immutable candidate revision.

Slice 3C may NEVER:
  approve it;
  activate it;
  make it routable;
  install it;
  execute it;
  grant Host authority;
  grant MCP authority;
  grant Agent delegation authority.
```

No Slice 3C state, receipt, scanner result, file location, class, or method
may express a stronger outcome.

## 1. Exact scope

Slice 3C includes only:

1. A closed, versioned, manifest-bound source policy for a bounded allowlist
   of source identities.
2. A trusted source-policy loader with an unforgeable process-local integrity
   seal and semantic-digest revalidation at every sensitive use.
3. Immutable source, revision, tree, component, and comparison identities.
4. Repository-external, per-user, content-addressed quarantine storage.
5. Bounded ingestion of explicitly supplied inert ZIP archives only. Network
   acquisition is absent.
6. Safe path, file, link, archive, and resource validation before any
   materialization.
7. Deterministic provenance, license, component-classification, static
   finding, lifecycle, and old/new comparison records.
8. A strict, non-authorizing bridge from validated Slice 2 candidate receipts.
9. Exact-subject validation through the existing Slice 3B evaluation contract.
10. Negative isolation proving that Slice 3C data cannot enter Slice 3A
    routing, Host handoff, MCP connection, installation, execution, or Agent
    delegation.
11. The eight pilot GitHub repositories as source-policy identities only.
12. Hermetic tests using Nexus-owned synthetic fixtures and fake data adapters.

## 2. Explicit non-goals

Slice 3C does not include:

- clone, fetch, pull, `git ls-remote`, browser, API, scheduled watcher, webhook,
  or other network acquisition;
- mutable Git worktrees, checkout filters, hooks, submodule/LFS resolution,
  dependency resolution, build steps, package-manager calls, or commands from
  candidate content;
- automatic update, adoption, approval, promotion, activation, rollback,
  revocation, enablement, installation, loading, routing, or execution;
- a new capability selector, ranking algorithm, Skill loader, Host mapping,
  MCP connection, OAuth flow, Agent Runtime, delegation system, memory system,
  or background service;
- whole-repository instruction loading or treating a README, `SKILL.md`, Agent
  persona, prompt, scanner message, or model output as control instructions;
- production integration of SkillSpector, promptfoo, tree-sitter, Git, an
  archive CLI, an external scanner, or any third-party runtime dependency;
- publisher signing, remote attestation, public distribution approval, or a
  claim that a SHA-256 digest proves publisher authenticity;
- modification of the frozen Slice 2, Slice 3A, Slice 3B, R4, or R5 contracts;
- Slice 3D, Slice 4, update-watch execution, or final red-team execution.

## 3. Trust and authority invariants

The following distinctions are permanent and must appear in code comments,
schemas, tests, and user-visible documentation:

```text
local presence != trust
scanner PASS != approval
review evidence complete != approval
approval != routability
routability != execution
Agent persona != permission
observed update != adopted update
evaluation receipt != Host authority
```

Additional mandatory invariants are:

- A repository is not a capability. A component is not trusted because its
  repository is known, popular, previously reviewed, or already present.
- A commit identifier binds an object name; it does not prove repository
  ownership, maintainer intent, license compatibility, or safety.
- A content digest proves equality to specific bytes, not authenticity or
  fitness.
- A source-policy record authorizes only bounded quarantine intake for that
  identity. It grants no component disposition or runtime authority.
- A trusted policy object means only that the exact Nexus-owned policy bytes
  and semantics passed local integrity validation.
- A clean static scan means only that the declared deterministic rules emitted
  no blocking finding for the exact subject.
- Every revision and every component revision starts quarantined, including a
  new revision of a source whose older component was separately approved.
- Agents remain advisory-only. Agent text cannot grant tools, files, shell,
  network, approval, Host, MCP, execution, or delegation authority.
- All authority fields are closed strings fixed to `none`; Python boolean or
  integer equality substitutions are invalid.
- Errors, missing evidence, unavailable validators, limit exhaustion, schema
  disagreement, or integrity disagreement fail closed without falling back to
  a weaker path.

The complete Slice 3C authority matrix is fixed, not configurable:

| Authority dimension | Only valid value |
|---|---|
| Installation | `none` |
| Execution | `none` |
| Host mapping | `none` |
| MCP connection | `none` |
| Agent delegation | `none` |
| Approval | `none` |
| Promotion | `none` |
| Activation | `none` |
| Routing | `none` |

## 4. Source-policy schema

The only authoritative source-policy format is
`nexus.ecosystem-source-policy.v1`. The implementation file is planned as
`config/ecosystem-source-policy.json`; it does not exist in this specification
gate.

### 4.1 Shared v1 schema primitives

Every Slice 3C JSON schema uses these exact primitives:

| Primitive | Closed rule |
|---|---|
| JSON object | Exact built-in `dict` from the duplicate-key-rejecting parser; exact declared keys only. Mapping subclasses and custom mappings fail closed. |
| JSON array | Exact built-in `list`; list/tuple subclasses and other iterables fail closed. Field-specific maximum; set-like arrays are sorted and duplicate-free. |
| Integer | Exact JSON integer in `0..9223372036854775807`; booleans, floats, exponent notation, non-finite values, and integers with more than 19 digits are invalid. |
| JSON depth | At most 32 containers. Greater depth returns a controlled schema error before recursive validation. |
| `sha256` | Lowercase string matching `^[0-9a-f]{64}$`. |
| Typed ID | One declared prefix (`source`, `tree`, `revision`, `component`, `component-revision`, `comparison`, `evidence`, `finding`, `static-report`, `classification`, `classification-report`, `bridge`, `intake-attempt`, `intake-attempt-result`, `transition`, `state-record`) plus `/` and one `sha256`. |
| Token | Lowercase string matching `^[a-z][a-z0-9._-]{0,63}$`. |
| Short redacted text | NFC UTF-8 string of at most 256 bytes, with no control character, secret, credential, absolute/private path, or raw candidate prose. |
| SPDX claim | `null` or ASCII string of 1–128 characters matching `^[A-Za-z0-9.+() -]+$`; it remains a claim until exact license evidence is complete. |
| Git object ID | Exact lowercase 40 hex for `git_sha1` or 64 hex for `git_sha256`. |
| Authority | The exact fixed object in Section 4.3; no omitted, extra, boolean, or numeric value. |

Every serialized record is at most `max_record_bytes`. The parser rejects a
UTF-8 BOM, invalid UTF-8, excessive nesting, large-integer digit bombs, and
trailing non-whitespace data. Nullable fields are explicitly listed and remain
present as JSON `null`; no other field is nullable.

All public `reason_codes` arrays contain 0–32 unique sorted members from this
closed v1 enum. An empty array is permitted only for a successful complete
record; every blocked, rejected, insufficient, invalid, unavailable, or
internal-error result requires at least one code:

```text
ANALYZER_UNAVAILABLE
ARCHIVE_INTEGRITY_INVALID
ARCHIVE_INVALID
ARCHIVE_UNSAFE_ENTRY
CAS_OBJECT_CONFLICT
CAS_QUOTA_EXCEEDED
CAS_ROOT_INVALID
CLASSIFICATION_CONFLICT
CLASSIFICATION_UNRESOLVED
EVALUATION_RECEIPT_INVALID
EVALUATION_RESULT_BLOCKED
INPUT_DIGEST_MISMATCH
INPUT_UNSTABLE
INTERNAL_FAILURE
LICENSE_AMBIGUOUS
LICENSE_CHANGED
LICENSE_MISMATCH
LICENSE_MISSING
LICENSE_UNSUPPORTED
PATH_COLLISION
PATH_INVALID
POLICY_INTEGRITY_INVALID
POLICY_SCHEMA_INVALID
POLICY_UNTRUSTED
PROVENANCE_CONFLICT
PROVENANCE_INSUFFICIENT
RESOURCE_LIMIT_EXCEEDED
SCOUT_DISPOSITION_BLOCKED
SCOUT_RECEIPT_INVALID
SOURCE_IDENTITY_CONFLICT
SOURCE_NOT_ALLOWED
STATE_TRANSITION_INVALID
STATIC_FINDING_BLOCKING
STATIC_FINDING_REJECTED
STATIC_REVIEW_REQUIRED
SUBJECT_MISMATCH
TIME_LIMIT_EXCEEDED
UNSUPPORTED_INPUT
```

Unexpected internal exceptions map to the redacted `INTERNAL_FAILURE` code and
never expose an exception string or traceback. Adding a primitive, identifier
prefix, reason code, nullable field, or enum member requires a new schema or
policy version.

### 4.2 Policy root and source records

The root object contains exactly these fields:

| Field | Exact type and rule |
|---|---|
| `schema_version` | Literal `nexus.ecosystem-source-policy.v1`. |
| `policy_id` | String matching `^nexus\.ecosystem-source-policy\.[a-z0-9][a-z0-9._-]{0,63}$`. |
| `policy_version` | Canonical positive decimal string, initially `1`; no leading zero. |
| `mode` | Literal `quarantine_only`. |
| `provider_policy` | Closed object defined below. |
| `resource_limits` | Closed object defined below. |
| `analysis_profiles` | Exact closed static-analyzer and component-classifier profiles defined in Sections 10.1 and 11.1. |
| `evaluation_profiles` | Exactly the seven closed profiles in Section 13.1, sorted by `validator_id`. |
| `sources` | Array of 1–32 unique source records, sorted by `source_key`. |

`provider_policy` contains exactly:

```json
{
  "allowed_providers": ["github"],
  "network_acquisition": "disabled",
  "accepted_intake_kinds": ["pre_supplied_zip"],
  "archive_formats": ["zip"]
}
```

`resource_limits` contains exactly these positive integers. These are v1 hard
ceilings, not caller-controlled defaults:

| Field | v1 ceiling |
|---|---:|
| `max_policy_bytes` | 65,536 |
| `max_sources` | 32 |
| `max_input_bytes` | 134,217,728 |
| `max_expanded_bytes` | 536,870,912 |
| `max_entries` | 20,000 |
| `max_directories` | 5,000 |
| `max_file_bytes` | 33,554,432 |
| `max_path_utf8_bytes` | 512 |
| `max_path_segment_utf8_bytes` | 128 |
| `max_path_depth` | 32 |
| `max_components` | 128 |
| `max_component_entries` | 10,000 |
| `max_component_bytes` | 268,435,456 |
| `max_archive_nesting` | 1 |
| `max_entry_compression_ratio` | 100 |
| `max_aggregate_compression_ratio` | 20 |
| `max_findings_per_subject` | 1,024 |
| `max_license_files` | 32 |
| `max_dependency_manifests` | 64 |
| `max_instruction_file_bytes` | 262,144 |
| `max_license_or_dependency_file_bytes` | 1,048,576 |
| `max_record_bytes` | 2,097,152 |
| `max_text_evidence_bytes` | 65,536 |
| `max_ingest_seconds` | 60 |
| `max_cas_bytes` | 2,147,483,648 |
| `max_quarantined_revisions_per_source` | 8 |

`analysis_profiles` contains exactly the keys `static_analyzer_profile` and
`component_classifier_profile`; their complete literal rule arrays are the
normative catalogs in Sections 10.1 and 11.1. `evaluation_profiles` contains
exactly seven closed objects using Section 13.1, with no source-specific
override. All three profile digests are part of the policy semantic digest.
Unknown, missing, duplicated, unsorted profile, or internally inconsistent
profile data makes the entire policy untrusted.

Each source record contains exactly:

| Field | Exact type and rule |
|---|---|
| `source_key` | Lowercase token matching `^github/[a-z0-9](?:[a-z0-9-]{0,38})/[a-z0-9](?:[a-z0-9._-]{0,99})$`; unique after ASCII case-folding. |
| `provider` | Literal `github`. |
| `canonical_repository` | One `Owner/Repository` identifier whose owner/repository components satisfy the corresponding `source_key` lengths and characters; identity comparison is ASCII case-insensitive. |
| `identity_state` | Literal `SOURCE_IDENTITY_ONLY`. |
| `source_classifications` | Sorted, unique non-empty subset of the closed classification enum in Section 11. |
| `whole_repository_disposition` | Literal `QUARANTINE_UNTIL_REVIEW`. |
| `frozen_evidence` | Closed historical-evidence object below. It never becomes live upstream evidence. |
| `authority` | Exact zero-authority object below. |

`frozen_evidence` contains exactly:

```text
evidence_state: VERIFIED_HISTORICAL_SNAPSHOT | UNVERIFIED
commit_object_format: git_sha1 | none
commit_oid: 40 lowercase hex characters | null
license_state: VERIFIED_DECLARATION | UNVERIFIED
spdx_expression: bounded SPDX expression | null
evidence_date: YYYY-MM-DD | null
evidence_scope: historical_local_review_only
```

### 4.3 Fixed zero-authority object

The `authority` object is identical in every source and every Slice 3C public
record:

```json
{
  "approval_authority": "none",
  "promotion_authority": "none",
  "activation_authority": "none",
  "routing_authority": "none",
  "installation_authority": "none",
  "execution_authority": "none",
  "host_mapping_authority": "none",
  "mcp_connection_authority": "none",
  "agent_delegation_authority": "none"
}
```

The canonical URL is derived as
`https://github.com/<canonical_repository>`; it is not a caller-controlled
policy field. Unknown keys, unknown enum values, duplicate keys, duplicate
sources, empty sets, incorrect concrete types, secret-shaped identifiers, and
inconsistent repository/source-key identities are invalid. The parser accepts
no extension/property bag. `source_key` is a policy lookup key; it is not the
digest-based `source_id` defined below.

## 5. Trusted source-policy loading and integrity seal

The trusted loader follows the repaired Slice 3B validator-registry pattern:

1. Resolve the repository root and integrity manifest without following a
   symlink or Windows reparse point.
2. Accept only a regular policy file at the fixed relative path.
3. Enforce `max_policy_bytes` before and during a stable read through a
   no-follow, read-only handle. On Windows, compare volume serial and file ID;
   on POSIX, compare device and inode before and after the read. A string-only
   containment check or `Path.resolve()` is insufficient.
4. Read `release-manifest.json` when present, otherwise `MANIFEST.json`, with
   the existing 2 MiB ceiling, the same no-follow stable-handle checks, and a
   duplicate-key-rejecting parser.
5. Verify the policy against the applicable existing manifest contract before
   parsing semantics: a release manifest binds raw bytes and raw size; the
   repository `MANIFEST.json` binds UTF-8 LF-normalized bytes and normalized
   byte count. Parse only the exact stable raw buffer used for that check; no
   second file read is permitted.
6. Decode strict UTF-8, reject a BOM, duplicate keys, non-finite numbers,
   floats, unknown fields, and non-exact Python types.
7. Validate the complete closed schema, normalize only declared set-like
   arrays, and compute the canonical semantic SHA-256.
8. Construct an immutable `TrustedEcosystemSourcePolicy` only after all prior
   checks pass, then attach a private module-owned process-local seal.

Parsing alone must return untrusted data and must never attach the trusted
seal. Caller-created subclasses, duck-typed mappings, serialized seal values,
copies, or objects returned by the private parser cannot carry policy
authority.

Every authority-sensitive consumer must call one internal guard equivalent to
`_require_trusted_source_policy`. The guard must check the exact final class,
object seal identity, digest syntax, and a freshly recomputed semantic digest
using constant-time comparison. Post-seal mutation, even through test-only
reflection, invalidates the object. The trusted object is never cached across
a manifest or process boundary.

Any manifest, file, schema, seal, or semantic-digest failure raises one bounded
`EcosystemPolicyError` reason code and produces no trusted policy, no intake
record, and no fallback policy. Manifest integrity is a local release-integrity
control; it is not a publisher signature.

## 6. Immutable identity model

All identifiers use strict UTF-8 canonical JSON with sorted keys, no
undeclared metadata fields, no insignificant whitespace, NFC-normalized
strings, exact integer types, and a type-domain prefix. Each identity body has
exactly the fields listed below. Nullable fields in other evidence records do
not enter an identity unless this section explicitly lists them. The digest
input is:

```text
UTF8(<exact-domain-literal>) + 0A + <canonical-json-body-bytes>
```

The core identity domain literals in this section are:

```text
nexus.ecosystem-source-identity.v1
nexus.ecosystem-tree-identity.v1
nexus.ecosystem-revision-identity.v1
nexus.ecosystem-component-identity.v1
nexus.ecosystem-component-revision-identity.v1
nexus.ecosystem-comparison-identity.v1
```

The public identifier is `<kind>/<64-lowercase-hex-sha256>`. A literal, field,
or encoding change requires a new schema version and new golden vectors.

### 6.1 Source identity

`source/<sha256>` uses domain `nexus.ecosystem-source-identity.v1` and hashes
exactly:

```json
{
  "provider": "github",
  "repository": "ascii-casefolded-owner/ascii-casefolded-repository"
}
```

The display URL, branch, stars, timestamps, policy order, and historical
review state do not enter source identity. The resulting `source/<sha256>` is
the `source_id` used by all revision, component, evidence, and comparison
records.

### 6.2 Tree identity

`tree/<sha256>` uses domain `nexus.ecosystem-tree-identity.v1` and hashes the
closed body `{ "entries": [...] }`, where `entries` is a sorted array of closed
entry records. Each record
contains exactly `path`, `kind`, `mode`, `size`, and `sha256`; link-like entries
also contain `link_target_sha256`. The enums are:

```text
kind: regular | symlink | hardlink | gitlink | archive | special
mode: regular_non_executable | regular_executable | link | gitlink | special
```

Paths use `/`, are relative, and obey Section 8. `sha256` binds regular file
bytes or the inert metadata bytes used to describe a non-materialized entry.
Entries are sorted by normalized UTF-8 path bytes. Duplicate normalized or
case-fold-equivalent paths are invalid.

The broader kind/mode enum permits deterministic inventory evidence, but a v1
successful ZIP tree contains only `regular` or inert nested-`archive` entries
with regular modes. A link, gitlink, or special inventory result terminates the
attempt before `tree_id` construction.

### 6.3 Revision identity

`revision/<sha256>` uses domain `nexus.ecosystem-revision-identity.v1` and
hashes exactly:

```json
{
  "source_id": "source/<sha256>",
  "commit_object_format": "git_sha1 | git_sha256",
  "commit_oid": "exact 40- or 64-lowercase-hex value for that format",
  "input_sha256": "sha256 of the raw ZIP bytes",
  "tree_id": "tree/<sha256>"
}
```

An observed mutable ref is evidence only and is excluded. The same commit with
different input or tree bytes is a provenance conflict. Different commits with
identical tree bytes remain different revisions, although immutable blob
storage may be deduplicated.

### 6.4 Component identity

`component/<sha256>` uses domain `nexus.ecosystem-component-identity.v1` and
hashes exactly `source_id` and normalized relative `component_root`. It is a
stable discovered-family identity; classification is deliberately excluded so
an unresolved or later corrected classification cannot manufacture a new
family. Display names and descriptions are also excluded. `component_root` is
either one regular-file path or one directory path selected by the exact
classifier profile in Section 11.1; the repository root itself is forbidden.

`component-revision/<sha256>` uses domain
`nexus.ecosystem-component-revision-identity.v1` and hashes exactly
`revision_id`, `component_id`, and `component_manifest_sha256`. The component
manifest body is `{ "entries": [...] }`; every entry contains exactly its
normalized repository-relative `path`, `mode`, `size`, and `sha256`, uses the
tree-entry rules in Section 6.2, and is sorted by normalized UTF-8 path bytes.
A single-file component therefore contains exactly its own repository-relative
path. Every change to the component closure creates a new component revision.

Slice 2 `candidate/<sha256>` identifiers remain unchanged. They are external
references recorded by the bridge; they are never reused as source, revision,
tree, or component identifiers.

### 6.5 Identity and CAS-object relationship

A CAS blob uses the raw `SHA256(blob_bytes)` as `content_sha256` and storage
locator `objects/sha256/<first-two-hex>/<content_sha256>`. That locator is a
content address, not a public typed semantic identity, so it deliberately has
no schema/domain preimage. Every hash that *is* a semantic identity uses one of
the explicit domains in Sections 6, 8.4, and 9 through 17; a raw content digest must never
be substituted for such an ID.

The relationship is one-way and exact:

```text
source_key --trusted policy lookup--> source_id
content_sha256 + path + size + mode --tree manifest--> tree_id
source_id + commit + raw ZIP digest + tree_id --------> revision_id
source_id + component_root ---------------------------> component_id
revision_id + component_id + component manifest -----> component-revision_id
```

Different sources may deduplicate identical inert blob bytes, but source,
provenance, tree, revision, and component records remain separate. A typed ID
cannot be inferred from local object presence, and deleting or observing a CAS
locator can neither create nor change trust, review, or authority.

## 7. Repository-external CAS and quarantine storage

The production root is a Nexus-owned per-user data directory, never a path
inside the source repository, Host/plugin cache, Skill discovery root, or
`PATH`:

```text
Windows: %LOCALAPPDATA%\Nexus\ecosystem\v1
POSIX:   $XDG_DATA_HOME/nexus/ecosystem/v1
         or ~/.local/share/nexus/ecosystem/v1 when XDG_DATA_HOME is absent
```

Tests inject a newly created repository-external temporary directory. The
production root requires a Nexus-owned v1 marker and user-private permissions.
The root and every parent below it must be opened with no-follow semantics and
verified as real directories, not symlinks, mount aliases, junctions, or other
reparse points. On Windows, stable volume/file identity is checked before and
after every sensitive read; `Path.resolve()` and string containment alone are
insufficient. A root inside the repository, a broad filesystem root, a
network/UNC location, Host/plugin cache, Skill directory, or existing unsafe
directory fails closed. Filesystem ACLs are defense in depth and never a trust
proof.

The v1 layout is:

```text
ecosystem/v1/
  .nexus-ecosystem-root.json         # fixed v1 ownership marker, no authority
  incoming/                         # incomplete, never consumable
  objects/sha256/aa/<digest>        # immutable inert blobs
  intake-attempts/sha256/<attempt-digest>/<result-digest>.json
  trees/sha256/<digest>.json
  revisions/sha256/<digest>.json
  components/sha256/<digest>.json
  evidence/sha256/<digest>.json
  comparisons/sha256/<digest>.json
  quarantine/<revision-digest>.json # metadata view, not an authority label
  locks/                             # bounded writer coordination
  tmp/                               # same-volume atomic staging
```

There is deliberately no `approved`, `active`, `installed`, `routable`,
`executable`, `plugins`, `skills`, or `agents` directory.

Writes must stream to a same-volume exclusive temporary file, enforce the
declared byte ceiling, flush, hash, reopen and rehash, then publish by atomic
create without overwrite. If the digest path already exists, the existing
bytes are rehashed and must match before reuse. Every later read is size-bound,
uses stable metadata checks, and rehashes the bytes before semantic use.
Partial writes remain in `incoming` or `tmp` and are never records. Before a
write begins, the bounded CAS accounting must prove that both the per-operation
limit and `max_cas_bytes` remain available. Slice 3C implements no garbage
collection, eviction, replacement, or destructive cleanup.

## 8. Safe path, file, link, archive, and resource rules

### 8.1 Path rules

A candidate entry path must:

- be valid Unicode normalized to NFC exactly once and encode to at most 512
  UTF-8 bytes;
- contain 1–32 non-empty `/`-separated segments;
- keep every segment at or below 128 UTF-8 bytes and contain no bidirectional
  control character;
- be relative and use `/`; backslash, drive letters, UNC prefixes, URI forms,
  a leading slash, `.` and `..` segments, NUL, control characters, colon,
  alternate-data-stream syntax, and trailing dot/space are rejected;
- avoid Windows reserved device names, case-insensitively and with or without
  an extension: `CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, and `LPT1`–`LPT9`;
- be unique after NFC normalization and Unicode case-folding.

A normalization change that creates a collision is a rejection, not an
automatic rename. No entry may escape its staging directory after a final
parent containment check.

### 8.2 File and link rules

- Only regular files are materialized as inert blobs.
- Executable mode is recorded as a security finding; materialized files are
  created non-executable.
- Symlinks, hardlinks, Git submodules/gitlinks, devices, FIFOs, sockets,
  sparse-file declarations, and other special entries are never followed or
  materialized. In the v1 ZIP path they reject the intake attempt before any
  tree or revision exists; only bounded private attempt evidence may describe
  them.
- Git LFS pointers are stored only as their small pointer bytes. LFS objects
  are never resolved.
- File magic and bounded content inspection, not a filename extension alone,
  determine archive/binary observations.
- Candidate files are never imported as Python, loaded as Skills, parsed as
  Agent instructions, opened with an OS handler, or passed to a shell,
  subprocess, compiler, package manager, Host, MCP server, or model context.

### 8.3 Archive rules

Only an already-open, no-follow, read-only stable ZIP handle is accepted; its
file identity and size are compared before and after inventory/streaming. Only
non-encrypted, non-ZIP64, single-volume ZIP inputs using stored or deflate
compression are supported, through Nexus-owned bounded library code. TAR,
gzip, self-extracting archives, RAR/7z, encrypted members, split archives,
unsupported compression, absolute/link/special members, overlapping member
offsets, and malformed headers fail closed. `ZipFile.extract` and
`ZipFile.extractall` are prohibited.

The raw archive is first stored as an inert CAS object. Entry headers are
validated before content bytes are read. Expanded bytes are streamed directly
to digest-addressed inert blobs and counted independently of declared sizes;
candidate path text never selects a destination. The archive must have exactly
one non-empty common top-level directory. That prefix is removed, recorded,
and collision-checked before any member is committed. Empty or multi-root
archives are rejected. CRC, declared-size, streamed-size, and final digest must
agree. Nested archives are stored as regular inert blobs and reported; they are
never opened recursively because `max_archive_nesting` is one.

An input that cannot be stably read and hashed within `max_input_bytes`
produces a bounded error and no CAS object or intake-attempt result. Deadline
exhaustion likewise produces a retryable bounded error and no result or
revision record. After a raw ZIP is stably CAS-bound, the first breached
expansion, entry-count, per-file, path, depth, component, compression-ratio,
finding-count, or record-size limit stops the operation. Structural escape, collision,
digest, and unsafe-entry failures reject the intake attempt. Capacity
exhaustion or unsupported safe archive content makes the intake attempt
insufficient. Unavailable post-inventory static analysis sets the created
revision's evidence outcome to `INSUFFICIENT_EVIDENCE`. No outcome falls back
to a less strict parser.

### 8.4 Pre-revision intake-attempt record

Unsafe or incomplete ZIP inventory cannot manufacture a `tree_id` or
`revision_id`. Once raw ZIP bytes are stably CAS-bound, Slice 3C writes one
immutable `nexus.ecosystem-intake-attempt.v1` record containing exactly:

```text
schema_version: nexus.ecosystem-intake-attempt.v1
attempt_id
attempt_result_id
bridge_id
source_key
source_id
commit_object_format
commit_oid
input_sha256
input_size
policy_semantic_sha256
intake_algorithm_id: token
intake_algorithm_version: token
result: REVISION_CREATED | REJECTED_BEFORE_REVISION |
        INSUFFICIENT_BEFORE_REVISION
tree_id: typed ID | null
revision_id: typed ID | null
reason_codes
authority: fixed zero-authority object
```

`attempt_id` is `intake-attempt/<sha256>`, uses domain
`nexus.ecosystem-intake-attempt-identity.v1`, and hashes exactly the bridge,
source, commit, input, policy, and algorithm fields. `attempt_result_id` is
`intake-attempt-result/<sha256>`, uses domain
`nexus.ecosystem-intake-attempt-result.v1`, and hashes the complete canonical
outcome record except itself.
`REVISION_CREATED` requires non-null tree and revision IDs and an empty reason
list. Both failure results require null tree and revision IDs and at least one
reason code. A pre-revision rejection has no possession/review state and cannot
enter the lifecycle in Section 17. Only `REVISION_CREATED` creates the initial
`MIRRORED_UNREVIEWED + QUARANTINED` state record. Repeating the same input tuple
produces the same attempt and result IDs. Because deadline exhaustion produces
no result, a later retry is permitted. A different terminal result at the same
attempt ID and algorithm version is an integrity conflict, never an overwrite.

### 8.5 Production and hermetic-test intake interfaces

The only production entry point accepts one validated Section 12 bridge plus
one already-opened, no-follow, stable local ZIP input. It accepts no directory,
tree manifest, member list, extracted path, Git checkout, URL, repository
object, generic archive, or caller-provided archive iterator. No environment
variable, debug flag, or `test_mode` may widen that interface.

Hermetic tests may inject a Nexus-owned in-memory byte reader, archive-entry
iterator, clock/deadline, and repository-external temporary CAS only through
private constructor arguments unavailable from the production entry point.
Those fakes must emit the same ZIP header/member/byte-stream protocol and pass
the same path, link, size, ratio, digest, and stable-read validators; they may
not inject a prevalidated tree or bypass streaming. Fixtures contain only
synthetically generated ZIP bytes and cannot read a third-party repository.

## 9. Provenance and license evidence model

### 9.1 Provenance evidence

`nexus.ecosystem-provenance-evidence.v1` is a closed immutable record with:

```text
schema_version: nexus.ecosystem-provenance-evidence.v1
evidence_id: evidence/<sha256>
source_key
source_id
revision_id
input_kind: pre_supplied_zip
input_sha256
tree_id
commit_object_format
commit_oid
observed_ref_sha256: sha256 | null             # informational only
provider_repository_id_sha256: sha256 | null   # informational only
signature_state: NOT_EVALUATED | MISSING | PRESENT_UNVERIFIED
signature_evidence_sha256: sha256 | null
source_policy_id
source_policy_version
source_policy_semantic_sha256
integrity_manifest_sha256
result: EXACT_SUBJECT_BOUND | CONFLICT | INSUFFICIENT_EVIDENCE
reason_codes: sorted closed tokens
authority: fixed zero-authority object
```

`evidence_id` uses the domain
`nexus.ecosystem-provenance-evidence.v1` and hashes every following semantic
field in the list. Raw refs and provider identifiers remain only in private
bounded source evidence; the public record contains their digests. No
observation timestamp is a semantic field.
Because v1 performs local intake only, it cannot claim live origin or signature
verification. A future version may add a separately trusted signature-verifier
result, which would remain evidence rather than approval.

### 9.2 License evidence

`nexus.ecosystem-license-evidence.v1` binds one revision or component revision
and contains exactly:

```text
schema_version: nexus.ecosystem-license-evidence.v1
evidence_id: evidence/<sha256>
subject_id
subject_sha256
declared_spdx_expression: SPDX claim | null
license_files: sorted [{path_sha256, content_sha256, size}]
notice_files: sorted [{path_sha256, content_sha256, size}]
license_result: MATCHES_POLICY_DECLARATION | MISSING | CHANGED | AMBIGUOUS |
                MISMATCH | UNSUPPORTED
redistribution_state: NOT_EVALUATED | LOCAL_REFERENCE_ONLY |
                      DISTRIBUTION_ALLOWED_WITH_OBLIGATIONS |
                      DISTRIBUTION_FORBIDDEN
policy_semantic_sha256
reason_codes
authority
```

The two file arrays contain exact three-field objects, are independently sorted
by `path_sha256`, have no duplicate path digest, and contain at most 32 objects
combined. Each referenced file is at most
`max_license_or_dependency_file_bytes`. `evidence_id` uses domain
`nexus.ecosystem-license-evidence.v1` and hashes every following semantic
field. `reason_codes` and `authority` use the shared primitives.

Relative license paths exist only in the private detailed CAS record; public
receipts use `path_sha256`. A license match is evidence, not legal advice,
approval, package permission, or routability. Missing, changed, ambiguous,
mismatched, or unsupported licensing is security-sensitive and cannot produce
complete review evidence.

## 10. Static security finding model

`nexus.ecosystem-static-finding.v1` contains exactly:

```text
schema_version: nexus.ecosystem-static-finding.v1
finding_id: finding/<sha256>
subject_id
subject_sha256
rule_id
rule_version
analyzer_id
analyzer_version
analyzer_config_sha256
category
severity
disposition
path_sha256: sha256 | null
evidence_sha256
reason_code
summary: short redacted text
redaction_applied: boolean
truncation_applied: boolean
authority: fixed zero-authority object
```

`rule_id`, `rule_version`, `analyzer_id`, and `analyzer_version` are shared
tokens. `summary` is shared short redacted text. `finding_id` uses domain
`nexus.ecosystem-static-finding.v1` and is the canonical digest of every field
except itself. At most `max_findings_per_subject` findings may exist, and they
are sorted by `finding_id`. The closed enums are:

```text
severity: INFO | LOW | MEDIUM | HIGH | CRITICAL
disposition: OBSERVED | REQUIRES_REVIEW | BLOCKS_REVIEW_COMPLETION |
             REJECTS_CANDIDATE
category:
  PATH_SAFETY | LINK_OR_SPECIAL_FILE | ARCHIVE_SAFETY |
  EXECUTABLE_OR_BINARY | HOOK_OR_AUTOMATION | DEPENDENCY_OR_INSTALL |
  NETWORK_OR_CREDENTIAL | PERMISSION_DECLARATION | INSTRUCTION_INJECTION |
  OBFUSCATION | LICENSE_CHANGE | PROVENANCE_MISMATCH |
  DUPLICATE_OR_COLLISION | RESOURCE_LIMIT | UNSUPPORTED_CONTENT |
  POLICY_OR_EVIDENCE_TAMPER
```

### 10.1 Fixed v1 analyzer profile and rule catalog

`analysis_profiles.static_analyzer_profile` is a closed object containing
exactly `schema_version=nexus.ecosystem-static-analyzer-profile.v1`,
`analyzer_id=nexus.ecosystem-static`, `analyzer_version=1`, and the following
rules sorted by `rule_id`. Each serialized rule contains exactly `rule_id`,
`rule_version=1`, `predicate_id`, `parameters`, `category`, `severity`, and
`disposition`. Its `analyzer_config_sha256` is the domain-separated canonical
SHA-256 of that complete profile using domain
`nexus.ecosystem-static-analyzer-profile.v1`.

| Rule ID | Exact deterministic predicate | Category / severity / disposition |
|---|---|---|
| `archive.nested` | Regular-file bytes start with ZIP, gzip, 7z, RAR, or POSIX tar magic; the bytes remain inert and are not opened. | `ARCHIVE_SAFETY` / `MEDIUM` / `REQUIRES_REVIEW` |
| `automation.workflow` | Path is `Jenkinsfile`, `.gitlab-ci.yml`, `.circleci/config.yml`, or begins `.github/workflows/`. | `HOOK_OR_AUTOMATION` / `HIGH` / `BLOCKS_REVIEW_COMPLETION` |
| `binary.executable-magic` | First bytes are `MZ`, ELF, any 32/64-bit little/big-endian Mach-O magic, or WebAssembly `00 61 73 6d`. | `EXECUTABLE_OR_BINARY` / `HIGH` / `BLOCKS_REVIEW_COMPLETION` |
| `content.bidi-control` | Any decoded bounded text contains a Unicode bidi-control code point already prohibited for paths in Section 8.1. | `OBFUSCATION` / `HIGH` / `BLOCKS_REVIEW_COMPLETION` |
| `content.invalid-role-text` | A Skill/Agent/reference instruction, license, notice, or dependency manifest is not strict UTF-8, contains NUL, or exceeds its role-specific limit. | `UNSUPPORTED_CONTENT` / `HIGH` / `BLOCKS_REVIEW_COMPLETION` |
| `credential.content` | The complete streamed bytes match the frozen Slice 3B secret detector for environment assignments, quoted JSON/YAML secrets, bearer/API/GitHub/GitLab tokens, private keys, connection strings, or credential-bearing URLs. | `NETWORK_OR_CREDENTIAL` / `CRITICAL` / `BLOCKS_REVIEW_COMPLETION` |
| `credential.filename` | Case-folded basename is `.env`, `.npmrc`, `.pypirc`, `credentials`, `credentials.json`, `id_rsa`, or `id_ed25519`, or ends `.pem`, `.key`, `.p12`, or `.pfx`. | `NETWORK_OR_CREDENTIAL` / `CRITICAL` / `REJECTS_CANDIDATE` |
| `dependency.manifest` | Case-sensitive basename is one of `Cargo.lock`, `Cargo.toml`, `Gemfile`, `Gemfile.lock`, `go.mod`, `go.sum`, `package-lock.json`, `package.json`, `pnpm-lock.yaml`, `poetry.lock`, `pyproject.toml`, `requirements.txt`, `setup.cfg`, `setup.py`, `uv.lock`, or `yarn.lock`. | `DEPENDENCY_OR_INSTALL` / `MEDIUM` / `REQUIRES_REVIEW` |
| `evidence.license-incomplete` | Revalidated license result is not `MATCHES_POLICY_DECLARATION`. | `LICENSE_CHANGE` / `HIGH` / `BLOCKS_REVIEW_COMPLETION` |
| `evidence.provenance-inexact` | Revalidated provenance result is not `EXACT_SUBJECT_BOUND`. | `PROVENANCE_MISMATCH` / `CRITICAL` / `BLOCKS_REVIEW_COMPLETION` |
| `hook.git-control` | Path begins `.git/hooks/`, or is `.gitattributes` or `.gitmodules`. | `HOOK_OR_AUTOMATION` / `HIGH` / `BLOCKS_REVIEW_COMPLETION` |
| `install.declaration` | Strictly parsed `package.json` has any `scripts` key `preinstall`, `install`, `postinstall`, or `prepare`; or `pyproject.toml` contains a top-level `[build-system]`; or basename is `install.py` or `bootstrap.py`. | `DEPENDENCY_OR_INSTALL` / `HIGH` / `BLOCKS_REVIEW_COMPLETION` |
| `instruction.control-claim` | A bounded Skill/Agent/reference instruction contains, under Unicode case-folding with ASCII whitespace collapsed, `ignore previous instructions`, `ignore system instructions`, `grant host authority`, `grant mcp authority`, `grant agent authority`, `execute without approval`, or `install automatically`. | `INSTRUCTION_INJECTION` / `HIGH` / `REQUIRES_REVIEW` |
| `mode.executable` | The tree entry mode is `regular_executable`. | `EXECUTABLE_OR_BINARY` / `HIGH` / `BLOCKS_REVIEW_COMPLETION` |
| `network.declaration` | Bounded role text contains an absolute `http://`, `https://`, `ws://`, or `wss://` URI, or a case-folded whole token `socket`, `requests`, `urllib`, `fetch`, or `webhook`. | `NETWORK_OR_CREDENTIAL` / `MEDIUM` / `REQUIRES_REVIEW` |
| `permission.declaration` | Bounded Skill/Agent/reference text contains a case-folded whole key/token `allowed-tools`, `permissions`, `mcp`, `shell`, `subprocess`, `sudo`, `delegate`, or `spawn-agent`. | `PERMISSION_DECLARATION` / `HIGH` / `REQUIRES_REVIEW` |

`reason_code` is derived, not caller-selected:
`REQUIRES_REVIEW -> STATIC_REVIEW_REQUIRED`,
`BLOCKS_REVIEW_COMPLETION -> STATIC_FINDING_BLOCKING`, and
`REJECTS_CANDIDATE -> STATIC_FINDING_REJECTED`; an `OBSERVED` rule would require
a future version because v1 defines none. The severity/category/disposition
triple must equal the table row for the matched rule.

Magic values, filename sets, phrase/token sets, case rules, and the ordered
source text of the frozen Slice 3B secret patterns are literal profile
parameters and therefore covered by `analyzer_config_sha256`; an implementation
may not silently widen or narrow them. Text matching streams the complete
role-bounded file with a fixed 4,095-byte overlap and a maximum match width of
4,096 bytes. A pattern that cannot honor that bound is invalid policy. Files
outside a declared text role receive only streaming magic, mode, path, and
credential checks. Structural failures that prevent creation of a revision are
represented only by the Section 8.4 intake-attempt result, never by a forged
partial static PASS.

### 10.2 Static report

One `nexus.ecosystem-static-report.v1` record aggregates a complete analyzer
run and contains exactly:

```text
schema_version: nexus.ecosystem-static-report.v1
report_id: static-report/<sha256>
subject_id
subject_sha256
analyzer_id
analyzer_version
analyzer_config_sha256
finding_ids: sorted finding/<sha256> list
counts: {observed, requires_review, blocking, rejecting}
analysis_status: COMPLETE | INSUFFICIENT_EVIDENCE
result: DECLARED_STATIC_RULES_PASSED | BLOCKED | REJECTED |
        INSUFFICIENT_EVIDENCE
reason_codes
authority: fixed zero-authority object
```

The four count values are exact non-negative integers whose sum equals the
finding-list length. `COMPLETE` requires every applicable rule to have examined
the complete exact subject. It yields `REJECTED` when any finding rejects,
`BLOCKED` when none rejects and any finding blocks, and
`DECLARED_STATIC_RULES_PASSED` otherwise. Analyzer error, deadline, truncated
coverage, finding overflow, unknown rule/profile, or unavailable evidence must
yield `INSUFFICIENT_EVIDENCE`, never a pass. `report_id` hashes every following
field under domain `nexus.ecosystem-static-report.v1`.

Detailed evidence bytes remain in the private CAS object referenced by
`evidence_sha256`; they do not enter receipts. Findings are sorted by
`finding_id`. Analyzer exception or unavailability produces only an
`INSUFFICIENT_EVIDENCE` static report with a closed reason code; it must not
invent a synthetic finding. External scanner output, if supported in a future
slice, must enter through this schema as untrusted evidence and cannot seal
itself.

Zero blocking/rejecting findings in one complete profile means only
`DECLARED_STATIC_RULES_PASSED` for the exact subject. No field named `safe`,
`trusted`, `approved`, `active`, `routable`, or `executable` is permitted.

## 11. Component-level classification

Source classifications and component kinds are separate. The source-policy
semantic classification enum is:

```text
GRANULAR_SKILL_SOURCE
ADVISORY_AGENT_SOURCE
REFERENCE_ARCHITECTURE
MEMORY_PATTERN_SOURCE
WORKFLOW_PATTERN_SOURCE
LIBRARY_DEPENDENCY_REFERENCE
```

`LIBRARY_DEPENDENCY_REFERENCE` is the wire token for the human label
`LIBRARY/DEPENDENCY_REFERENCE`.

The component-kind enum is:

```text
GRANULAR_SKILL
ADVISORY_AGENT
REFERENCE_ARCHITECTURE
MEMORY_PATTERN
WORKFLOW_PATTERN
LIBRARY_DEPENDENCY_REFERENCE
```

### 11.1 Fixed v1 classifier profile

`analysis_profiles.component_classifier_profile` contains exactly
`schema_version=nexus.ecosystem-component-classifier-profile.v1`,
`classifier_id=nexus.ecosystem-component-classifier`,
`classifier_version=1`, and the following ordered discovery rules. Its
`classifier_config_sha256` is the domain-separated canonical SHA-256 of the
complete profile under domain
`nexus.ecosystem-component-classifier-profile.v1`.

1. Discover every non-root directory containing an exact-case regular file
   named `SKILL.md` as a `GRANULAR_SKILL` candidate. Its closure contains all
   regular files below that directory except a nested discovered Skill root and
   that nested root's subtree. A repository-root `SKILL.md` produces an
   unresolved source-level classification; the whole repository is never a
   Skill component.
2. Outside every Skill closure, discover each regular `.md` file beneath an
   exact first segment `agents` or `.agents` as a single-file
   `ADVISORY_AGENT` candidate.
3. Outside prior closures, a regular file with a case-folded path segment
   `memory`, `memories`, `wiki`, `codegraph`, or `code-graph` and extension
   `.json`, `.md`, `.py`, `.txt`, `.yaml`, or `.yml` is a single-file
   `MEMORY_PATTERN` candidate.
4. Outside prior closures, a regular file with a case-folded path segment
   `example`, `examples`, `pattern`, `patterns`, `workflow`, or `workflows` and
   extension `.json`, `.md`, `.py`, `.rst`, `.ts`, `.tsx`, `.txt`, `.yaml`, or
   `.yml` is a single-file `WORKFLOW_PATTERN` candidate. Paths beneath
   `.github/workflows` are automation findings, never components.
5. Outside prior closures, each exact dependency-manifest basename in rule
   `dependency.manifest` is a single-file
   `LIBRARY_DEPENDENCY_REFERENCE` candidate.
6. Outside prior closures, `README.md` or a regular `.md`, `.rst`, or `.txt`
   file beneath an exact first segment `docs` is a single-file
   `REFERENCE_ARCHITECTURE` candidate.

Rules 3 through 6 are evaluated as a set, not as precedence. Exactly one matching kind
is required; multiple matches produce `CONFLICTING`, and a discovered kind not
listed by that source's `source_classifications` produces `UNRESOLVED`. Source
classifications are therefore an allow-list/suggestion, never a positive
classification. Paths that match no discovery rule remain part of source-level
static analysis but do not become components. Identical bytes, translated
names, or self-claims never merge or override components; identity remains the
source/root pair in Section 6.4.

Every directory closure and single-file manifest is assembled only from the
already verified tree, with the exact Section 6.4 manifest algorithm. Candidate
roots and manifests are sorted by normalized UTF-8 path bytes. Component,
entry, byte, instruction-file, and record limits are enforced before a complete
classification report can be produced. Invalid UTF-8 in a file whose rule
requires text, classifier error, limit exhaustion, or unknown profile produces
insufficient evidence, never an inferred kind.

`nexus.ecosystem-component-classification.v1` contains exactly:

```text
schema_version: nexus.ecosystem-component-classification.v1
classification_id: classification/<sha256>
source_id
revision_id
component_id
component_revision_id
component_manifest_sha256
component_kind: closed component kind | null
classification_status: OBSERVED | UNRESOLVED | CONFLICTING
evidence_ids: sorted typed-ID list, maximum 16
reason_codes
disposition: QUARANTINED | REJECTED
authority: fixed zero-authority object
```

`classification_id` uses domain
`nexus.ecosystem-component-classification.v1` and hashes every field after
itself. `OBSERVED` requires exactly one non-null kind and no classification
reason. `UNRESOLVED` and `CONFLICTING` require a null kind and the corresponding
non-empty reason code. `REJECTED` disposition always requires a non-empty fatal
reason; otherwise disposition is `QUARANTINED`. No free-form description enters
the record.

The complete classifier run produces one
`nexus.ecosystem-classification-report.v1` containing exactly:

```text
schema_version: nexus.ecosystem-classification-report.v1
report_id: classification-report/<sha256>
subject_id
subject_sha256
classifier_id
classifier_version
classifier_config_sha256
classification_ids: sorted classification/<sha256> list
unresolved_path_sha256s: sorted sha256 list, maximum 128
report_status: COMPLETE | UNRESOLVED | CONFLICTING |
               INSUFFICIENT_EVIDENCE
reason_codes
authority: fixed zero-authority object
```

`COMPLETE` requires every discovered candidate to have one `OBSERVED`,
`QUARANTINED` classification, no unresolved path, and an exact valid manifest.
Any unresolved/conflicting classification selects the matching report status;
resource, parser, or classifier incompleteness selects
`INSUFFICIENT_EVIDENCE`. `report_id` hashes every following field under domain
`nexus.ecosystem-classification-report.v1`.

Every non-rejected classification has disposition
`QUARANTINED` and zero authority. The source policy separately fixes
`whole_repository_disposition=QUARANTINE_UNTIL_REVIEW`; neither disposition is
a semantic classification. A source may suggest allowed component kinds but
never pre-classifies a discovered component. Whole repositories cannot be
`GRANULAR_SKILL` or become routable. Each Skill root is
independent and binds its entire declared file closure. Each Agent component is
advisory text only. Reference/library classifications grant no dependency,
import, build, installation, or execution authority.

Candidate prose is parsed only as inert bounded data for classification.
Neither headings nor self-claims such as `trusted`, `official`, `system`,
`approved`, `Host`, `MCP`, or `execute` can change classification or authority.

## 12. Slice 2 candidate-to-quarantine bridge

The bridge schema is `nexus.ecosystem-intake-bridge.v1`. It contains exactly:

```text
schema_version: nexus.ecosystem-intake-bridge.v1
bridge_id: bridge/<sha256>
scout_receipt_sha256
scout_id: canonical UUID string
candidate_id: candidate/<sha256>
candidate_immutable_reference_sha256
commit_object_format: git_sha1
commit_oid: 40 lowercase hex
candidate_admission_disposition: ADMITTED_FOR_REVIEW | REFERENCE_ONLY |
                                 QUARANTINED | REJECTED |
                                 INSUFFICIENT_EVIDENCE
source_policy_id
source_policy_semantic_sha256
source_key
source_id
requested_input_kind: pre_supplied_zip
requested_input_sha256
requested_input_size
bridge_result: QUARANTINE_REQUEST_ACCEPTED | QUARANTINE_REQUEST_BLOCKED
reason_codes
authority: fixed zero-authority object
```

The bridge must call the frozen `validate_scout_receipt` implementation, locate
exactly one candidate, and recompute candidate identity/immutable-reference
consistency. `scout_receipt_sha256` is the SHA-256 of the canonical JSON bytes
of the built-in mapping returned by that validator; it is independent of the
caller's original serialization. The bridge then requires a trusted
source-policy `source_key` match and recomputes the corresponding `source_id`.
`candidate_immutable_reference_sha256` is the digest of the validated
candidate's canonical immutable-reference object. An accepted bridge requires
that object to contain exactly the current Slice 2 values
`kind=git_commit`, a 40-lowercase-hex `value`, and
`verification_state=verified_at_research_snapshot`. The bridge derives
`commit_object_format=git_sha1` and `commit_oid=<value>`; callers cannot supply
or override either value. A mutable/missing, non-Git, differently verified, or
future object format fails closed until a new bridge schema is approved.
`bridge_id` uses domain `nexus.ecosystem-intake-bridge.v1` and hashes every
field after itself.

Only Slice 2 dispositions `ADMITTED_FOR_REVIEW` and `REFERENCE_ONLY` may
produce `QUARANTINE_REQUEST_ACCEPTED`; they authorize only the bounded intake
attempt in Section 8.4. They do not create a tree, revision, or lifecycle
state. `QUARANTINED`, `REJECTED`, or `INSUFFICIENT_EVIDENCE` produces
`QUARANTINE_REQUEST_BLOCKED`. A Scout recommendation rank is informational and
cannot alter the result. Slice 3C v1 has no manual or bridge-bypass intake.

The bridge never downloads bytes. The supplied ZIP must already be local; its
bounded stable-read digest and size must equal the request before the CAS
pipeline begins. An accepted bridge with an unstable or mismatched ZIP creates
no intake attempt.

## 13. Slice 3B evaluation-contract integration

Slice 3C adds no second PASS mechanism and does not change the frozen Slice 3B
operators, result states, or validation-state semantics. It adds exactly these
manifest-bound validator definitions, all version `1`, output schema
`nexus.evaluation-contract.v1`, `requires_executed_subject=false`,
`availability=available`, `definition_source=nexus_core`, minimum one check,
and `pass_transition=validation_passed`:

| Validator ID | Exact display name | Existing type | Exact operators | Exact subject types | Slice 3C adapter result after validated PASS |
|---|---|---|---|---|---|
| `nexus.validator.ecosystem-provenance` | `Nexus Ecosystem Provenance Integrity` | `digest_integrity` | `sha256_matches_subject` | `ecosystem_component_revision`, `ecosystem_source_revision` | Propose `PROVENANCE_EVIDENCE_COMPLETE`. |
| `nexus.validator.ecosystem-static-security` | `Nexus Ecosystem Static Security` | `bounded_predicate` | `equals`, `not_equals`, `present` | `ecosystem_component_revision`, `ecosystem_source_revision` | Propose `STATIC_SECURITY_EVIDENCE_COMPLETE`. |
| `nexus.validator.ecosystem-classification` | `Nexus Ecosystem Classification` | `bounded_predicate` | `equals`, `present` | `ecosystem_component_revision`, `ecosystem_source_revision` | Propose `SEMANTIC_CLASSIFICATION_COMPLETE`. |
| `nexus.validator.ecosystem-validation-bundle` | `Nexus Ecosystem Validation Bundle` | `receipt_consistency` | `receipt_consistent` | `ecosystem_component_revision`, `ecosystem_source_revision` | Propose `VALIDATION_EVIDENCE_COMPLETE`. |
| `nexus.validator.ecosystem-review-bundle` | `Nexus Ecosystem Review Bundle` | `state_consistency` | `state_consistent` | `ecosystem_component_revision`, `ecosystem_source_revision` | Propose `REVIEW_EVIDENCE_COMPLETE`. |
| `nexus.validator.ecosystem-comparison-consistency` | `Nexus Ecosystem Comparison Consistency` | `receipt_consistency` | `receipt_consistent` | `ecosystem_revision_comparison` | Validate comparison evidence; no review-state proposal. |
| `nexus.validator.ecosystem-intake-bridge-consistency` | `Nexus Ecosystem Intake Bridge Consistency` | `receipt_consistency` | `receipt_consistent` | `ecosystem_intake_bridge` | Validate bridge evidence; no review-state proposal. |

The registry wire subject tokens are exactly
`ecosystem_source_revision`, `ecosystem_component_revision`,
`ecosystem_revision_comparison`, and `ecosystem_intake_bridge`. Each definition
uses only operators already permitted by its frozen Slice 3B validator type.
Operator and subject-type arrays are serialized in lexicographic order.
Display names are fixed registry bytes but remain non-authoritative.

### 13.1 Manifest-bound evaluation profiles

The validator registry limits validator mechanics; it does not by itself prove
that a domain-complete set of checks was requested. Therefore the trusted
source policy carries exactly seven `evaluation_profiles`. Each profile is a
closed object containing exactly:

```text
profile_id: token
profile_version: "1"
validator_id: token
validator_version: "1"
subject_types: sorted non-empty registry subject-token list
from_review_state: review-state token | null
to_review_state: review-state token | null
precondition_set: token
required_checks: sorted non-empty CheckProfile list
```

Each `CheckProfile` contains exactly `check_id`, `operator`, `required=true`,
`expected_source`, `observed_source`, and `evidence_id`; all except the boolean
are bounded tokens. `profile_sha256` is computed over the complete canonical
profile under domain `nexus.ecosystem-evaluation-profile.v1`. For each row,
`profile_id` is exactly its validator ID with the leading `nexus.validator.`
replaced by `nexus.profile.`, and `subject_types` exactly equal the sorted
registry values in Section 13. The seven exact profiles are:

| Validator | Required checks encoded as `check_id / operator / expected_source / observed_source / evidence_id` | Precondition and review edge |
|---|---|---|
| `nexus.validator.ecosystem-provenance` | `subject-digest / sha256_matches_subject / none / subject-sha256 / provenance-subject` | `provenance-exact`; `NOT_REVIEWED -> PROVENANCE_EVIDENCE_COMPLETE`. |
| `nexus.validator.ecosystem-static-security` | `analysis-status / equals / literal-complete / static-report-analysis-status / static-analysis-status`; `analyzer-config / equals / policy-analyzer-config / static-report-analyzer-config / static-analyzer-config`; `blocking-findings / equals / literal-zero / static-report-blocking-count / static-blocking-count`; `rejecting-findings / equals / literal-zero / static-report-rejecting-count / static-rejecting-count` | `static-report-complete-nonblocking`; `PROVENANCE_EVIDENCE_COMPLETE -> STATIC_SECURITY_EVIDENCE_COMPLETE`. |
| `nexus.validator.ecosystem-classification` | `classification-status / equals / literal-complete / classification-report-status / classification-status`; `classifier-config / equals / policy-classifier-config / classification-report-classifier-config / classification-config`; `unresolved-paths / equals / literal-empty-list / classification-report-unresolved-paths / classification-unresolved-paths` | `classification-report-complete`; `STATIC_SECURITY_EVIDENCE_COMPLETE -> SEMANTIC_CLASSIFICATION_COMPLETE`. |
| `nexus.validator.ecosystem-validation-bundle` | `required-receipts / receipt_consistent / recomputed-required-validation-bundle / supplied-required-validation-bundle / validation-bundle` | `validation-bundle-exact`; `SEMANTIC_CLASSIFICATION_COMPLETE -> VALIDATION_EVIDENCE_COMPLETE`. |
| `nexus.validator.ecosystem-review-bundle` | `prior-review-state / state_consistent / none / subject-lifecycle / review-prior-state` | `review-bundle-exact`; `VALIDATION_EVIDENCE_COMPLETE -> REVIEW_EVIDENCE_COMPLETE`. |
| `nexus.validator.ecosystem-comparison-consistency` | `comparison-record / receipt_consistent / revalidated-current-comparison / supplied-comparison-projection / comparison-record` | `comparison-exact`; both review-state fields are null. |
| `nexus.validator.ecosystem-intake-bridge-consistency` | `bridge-record / receipt_consistent / revalidated-current-bridge / supplied-bridge-projection / bridge-record` | `bridge-exact`; both review-state fields are null. |

The symbolic `expected_source` and `observed_source` tokens above have one
closed meaning: the Slice 3C adapter constructs the corresponding value from
the current integrity-revalidated record, fixed literal, or submitted value,
then compares the receipt's stored canonical digests with freshly recomputed
digests. The profile field value `none` is the literal token string `none`; it
directs the adapter to construct JSON null as the evaluation check's expected
value. `literal-complete` constructs the exact string `COMPLETE`, `literal-zero`
constructs the exact JSON integer `0`, and
`literal-empty-list` is the exact JSON array `[]`; all other source tokens name
the exact field or canonical projection stated in the table. For every check,
the evidence content digest must equal the canonical digest of the observed
value, as required by Slice 3B. Evidence IDs in the table are exact fixed Slice
3B token values; summaries remain non-authoritative and redacted.

The precondition sets are also closed: `provenance-exact` requires one current
provenance record with `EXACT_SUBJECT_BOUND` and exact source/revision/input/
tree/policy/manifest binding; `static-report-complete-nonblocking` requires the
current manifest-bound analyzer profile, `COMPLETE`, and zero blocking or
rejecting findings; `classification-report-complete` requires the current
classifier profile, `COMPLETE`, and every component classification revalidated;
`validation-bundle-exact` requires the exact current provenance, static, and
classification evaluation receipts with no omission or duplicate;
`review-bundle-exact` requires the exact four prior review edges and current
`VALIDATION_EVIDENCE_COMPLETE` lineage; and the comparison/bridge sets require
the complete current record and every referenced parent to revalidate.

The adapter requires an exact profile-digest match, exact check count and
lexicographic order, every declared check with `required=true`, no extra check,
and the complete precondition set. A trivial, partial, caller-invented, stale,
or self-consistently rewritten PASS therefore cannot propose any Slice 3C
transition. Parser-created or post-seal-mutated profiles fail through the same
trusted-policy guard as the source records.

### 13.2 Exact Slice 3B wire-subject projection

Slice 3C typed IDs contain `/`, while the frozen Slice 3B `subject_id` grammar
does not. The adapter therefore uses these non-authority wire IDs and verifies
their suffix against the current typed ID:

```text
ecosystem_source_revision     -> ecosystem-source-revision:<revision digest>
ecosystem_component_revision  -> ecosystem-component-revision:<component-revision digest>
ecosystem_revision_comparison -> ecosystem-revision-comparison:<comparison digest>
ecosystem_intake_bridge       -> ecosystem-intake-bridge:<bridge digest>
```

The wire `subject_sha256` is the canonical SHA-256 of the complete current
Slice 3C public record, not merely the typed-ID suffix. Its frozen Slice 3B
lifecycle is exactly `created`, `not_selected`, `not_executed`, `not_reviewed`,
`not_enhanced`, `not_validated`, and `not_reported`; `parent_subject_sha256` is
null. Only `stage_receipts.creator` is non-null, and the adapter recomputes it
from the exact intake-attempt result (source revision), component manifest
(component revision), comparison record (comparison), or validated Scout
receipt (bridge). All other stage receipts are null. This wire lifecycle does
not encode Slice 3C review state; the separately revalidated StateVector and
profile preconditions do.

The subject SHA-256 binds the complete canonical Slice 3C record. A consumer
must use the existing trusted-registry guard and
`validate_evaluation_receipt`, then verify the current subject ID, subject
SHA-256, validator ID/version, registry semantic digest, checks, result, and
Slice 3B validation-state transition. For a prerequisite PASS, that transition
must be exactly `not_validated -> validation_passed`, `permitted=true`, and
`applied=false`.

Slice 3B does not name or apply a Slice 3C review transition. A separate pure
Slice 3C adapter uses the fixed table above, requires the exact current prior
review state and trusted source-policy digest, and may emit only an unapplied
`nexus.ecosystem-state-transition-receipt.v1` proposal. The bounded Slice 3C
state writer is the only component that may apply an allowed quarantine/review
transition.

`PASS` is therefore an evidence prerequisite only. The evaluation receipt
keeps `state_transition_applied=false`, Slice 3C disposition remains
`QUARANTINED`, and all authority fields remain `none`. `FAIL`,
`NOT_APPLICABLE`, `INSUFFICIENT_EVIDENCE`, `INVALID_REQUEST`, and
`VALIDATOR_UNAVAILABLE` block the adapter. Stale, forged, self-consistently
rewritten, wrong-subject, wrong-parent, wrong-registry, wrong-prior-state, or
post-evaluation-mutated evidence fails closed.

Evaluation summaries use only redacted reason codes and digests. An evaluation
receipt cannot authorize approval, activation, routing, installation,
execution, Host mapping, MCP connection, Agent delegation, reporting
completion, or memory insertion.

## 14. Strict isolation from Slice 3A routing

Slice 3A must not import a Slice 3C module, inspect the ecosystem data root,
read quarantine records, enumerate CAS objects, or consider source/component
classifications during capability selection.

No Slice 3C path is a Skill root. No Slice 3C record may be written into the
capability registry or semantic-applicability registry. No component is
selected, loaded, or revalidated through Slice 3A. A later separately approved
promotion slice must copy or construct an exact Nexus-owned component under a
new manifest-bound release decision before Slice 3A can see it.

Dependency direction is one-way:

```text
Slice 2 validated receipt ---->
                               Slice 3C quarantine evidence
Slice 3B validator service --->

Slice 3A routing     X<-------- no import, data, path, or receipt edge
Host/MCP/execution   X<-------- no authority edge
```

Negative tests must monkeypatch every known routing, Host, MCP, install,
subprocess, Skill-loading, and Agent-delegation entry point to fail if called.

## 15. Deterministic old/new revision comparison

`nexus.ecosystem-revision-comparison.v1` accepts two integrity-revalidated
revision records for the same `source_id`. It contains exactly:

```text
schema_version: nexus.ecosystem-revision-comparison.v1
comparison_id: comparison/<sha256>
source_id
old_revision_id
new_revision_id
old_tree_id
new_tree_id
comparison_policy_semantic_sha256
ancestry_state: SAME | FAST_FORWARD | REWIND | DIVERGED | UNKNOWN
added_path_sha256s: sorted sha256 list
removed_path_sha256s: sorted sha256 list
modified_path_sha256s: sorted sha256 list
type_changed_path_sha256s: sorted sha256 list
mode_changed_path_sha256s: sorted sha256 list
component_changes: sorted ComponentChange list
license_changes: sorted FileEvidenceChange list
dependency_changes: sorted FileEvidenceChange list
security_change_codes: sorted SecurityChangeCode list
comparison_result: NO_TREE_CHANGE | CHANGED | SECURITY_SENSITIVE_CHANGE |
                   INCOMPARABLE | INSUFFICIENT_EVIDENCE
algorithm_id: token
algorithm_version: token
reason_codes: shared reason-code list
authority: fixed zero-authority object
```

The five path lists contain only `sha256` values and contain at most 8,192
members combined. `ComponentChange` contains exactly
`component_id`, nullable `old_component_revision_id`, nullable
`new_component_revision_id`, and `change_kind`. `FileEvidenceChange` contains
exactly `path_sha256`, nullable `old_sha256`, nullable `new_sha256`, and
`change_kind`. `change_kind` is `ADDED`, `REMOVED`, or `MODIFIED`; `ADDED`
requires only the new value, `REMOVED` only the old value, and `MODIFIED` both
different values. Component, license, and dependency changes are sorted by
their complete canonical object bytes and are limited to 256, 64, and 128
items respectively.

`SecurityChangeCode` is one of:

```text
BINARY_ADDED
COMPONENT_ADDED
COMPONENT_CHANGED
COMPONENT_REMOVED
COMPONENT_ROOT_CHANGED
DEPENDENCY_ADDED
DEPENDENCY_CHANGED
DEPENDENCY_REMOVED
EXECUTABLE_ADDED
FILE_ADDED
FILE_CONTENT_CHANGED
FILE_MODE_CHANGED
FILE_REMOVED
FILE_TYPE_CHANGED
HOOK_OR_INSTALLER_CHANGED
LICENSE_ADDED
LICENSE_CHANGED
LICENSE_REMOVED
LINK_OR_SPECIAL_FILE_CHANGED
LOCKFILE_CHANGED
NETWORK_OR_CREDENTIAL_CHANGED
PERMISSION_CHANGED
POLICY_RELEVANT_FILE_CHANGED
PROVENANCE_CHANGED
SIGNATURE_OR_ATTESTATION_CHANGED
SKILL_OR_AGENT_INSTRUCTION_CHANGED
UNSUPPORTED_CONTENT_CHANGED
WORKFLOW_CHANGED
```

At most 32 unique security-change codes are permitted. All collections are
sorted and duplicate-free. `comparison_id` uses domain
`nexus.ecosystem-comparison-identity.v1` and hashes every semantic field after
itself, including the fixed authority object. Renames are not guessed in v1;
they appear as remove/add unless exact component identity provides a stable
mapping. `ancestry_state` is evidence supplied by a separately bounded
provider and never inferred from timestamps or branch labels.

Any change to policy, license, dependency/lockfile, installer/hook/workflow,
binary/executable, link/special file, Skill/Agent instruction, permission,
network/credential behavior, component root, provenance, signature, or
attestation adds a closed security-change code. A new revision is always
quarantined even when the comparison is `NO_TREE_CHANGE`. Comparison output
never inherits an old review, approval, routing, or execution state.

## 16. Eight pilot GitHub source identities

These are policy identities, not acquisition instructions, approval records,
or statements about current upstream state. Historical commit/license evidence
comes only from the frozen local Nexus review and must be labeled accordingly.
Every future supplied revision and component starts
`QUARANTINE_UNTIL_REVIEW`.

| Source-policy key | Frozen local evidence | Source classifications | Permanent automatic prohibitions |
|---|---|---|---|
| `github/tencentcloud/tencentdb-agent-memory` | Commit `5299c00aaf65481703c180fd69df066d11254eb7`; MIT; historical review only | `MEMORY_PATTERN_SOURCE`, `REFERENCE_ARCHITECTURE`, `WORKFLOW_PATTERN_SOURCE` | Never import/start its proxy, services, databases, retrieval runtime, dependencies, credentials, or user memory. |
| `github/mattpocock/skills` | Commit and license unverified | `GRANULAR_SKILL_SOURCE` | Never import, install, load, or route the repository wholesale; review each component independently. |
| `github/jnmetacode/agency-agents-zh` | Commit `972452cdedef8d04fed4a8dd1dc10623e33ed412`; MIT; historical review only | `ADVISORY_AGENT_SOURCE` | Never grant tools/delegation; never let a localization duplicate override canonical identity. |
| `github/msitarzewski/agency-agents` | Commit `9572c66428bbc8ef475d339b2386eacd8bf540c5`; MIT; historical review only | `ADVISORY_AGENT_SOURCE` | Never treat persona text or installer/conversion scripts as permission, Skill authority, or execution. |
| `github/shubhamsaboo/awesome-llm-apps` | Commit `11a4bc330e4b0b1509577db4581c5cfbcf6ea6a0`; Apache-2.0; historical review only | `GRANULAR_SKILL_SOURCE`, `REFERENCE_ARCHITECTURE`, `WORKFLOW_PATTERN_SOURCE` | Never run examples, resolve dependencies, consume credentials, unsafe flags, or route the collection wholesale. |
| `github/bytedance/deer-flow` | Commit `788a890bd022689ef293e6bbfa2c12988173db6c`; MIT; historical review only | `GRANULAR_SKILL_SOURCE`, `LIBRARY_DEPENDENCY_REFERENCE`, `REFERENCE_ARCHITECTURE`, `WORKFLOW_PATTERN_SOURCE` | Never start its runtime/gateway/subagents, install dependencies, or inherit permissions. |
| `github/cft0808/edict` | Commit `14a207557719c046af0f993a7bff1cc5a5015b33`; MIT; historical review only | `ADVISORY_AGENT_SOURCE`, `REFERENCE_ARCHITECTURE`, `WORKFLOW_PATTERN_SOURCE` | Never start its runtime/swarm, spawn/delegate Agents, or disclose hidden reasoning. |
| `github/openai/codex` | Commit `10d5a603aecbd73a38f3a6576cce69a78f8d6f1d`; Apache-2.0; historical review only | `LIBRARY_DEPENDENCY_REFERENCE`, `REFERENCE_ARCHITECTURE`, `WORKFLOW_PATTERN_SOURCE` | Never vendor/build/install/execute Codex, replace the Host, inspect private Host state, or infer current Host availability. |

Repository spelling and URL case are display metadata; the identity comparison
is ASCII case-insensitive. Redirects, forks, renamed repositories, transferred
owners, aliases, and typo-similar names are different or conflicting sources
until a new manifest-bound policy revision explicitly resolves them.

## 17. Lifecycle and state-transition rules

Slice 3C uses orthogonal facts; it has no generic `trusted` flag.

### 17.1 Possession axis

```text
NOT_PRESENT -> MIRRORED_UNREVIEWED -> SNAPSHOT_INTEGRITY_VERIFIED
```

Only exact supplied-byte and tree-manifest verification permits the second
transition. Local presence alone permits neither.

### 17.2 Review axis

```text
NOT_REVIEWED
  -> PROVENANCE_EVIDENCE_COMPLETE
  -> STATIC_SECURITY_EVIDENCE_COMPLETE
  -> SEMANTIC_CLASSIFICATION_COMPLETE
  -> VALIDATION_EVIDENCE_COMPLETE
  -> REVIEW_EVIDENCE_COMPLETE
```

Each edge requires exact-subject evidence and any required Slice 3B PASS. No
edge may be skipped. `REVIEW_EVIDENCE_COMPLETE` is not approval readiness or
approval; it means only that this slice's evidence set is complete.

### 17.3 Evidence outcome, disposition, and authority axes

```text
evidence_outcome: IN_PROGRESS | COMPLETE | INSUFFICIENT_EVIDENCE
disposition:      QUARANTINED | REJECTED
authority:        fixed zero-authority object
```

Every mirrored revision begins `QUARANTINED`. A policy-defined fatal condition
may create an immutable `REJECTED` record. Missing or unavailable evidence sets
`evidence_outcome=INSUFFICIENT_EVIDENCE` while disposition remains
`QUARANTINED`; before terminal completion, the last completed review state is
preserved. `REJECTED` does not transition back. Additional evidence creates a
new evidence record, and remediated bytes create a new revision.

After the terminal complete pair is recorded, later missing, unreadable,
tampered, or unavailable referenced evidence does not rewrite history and
there is no `COMPLETE -> INSUFFICIENT_EVIDENCE` edge. Every consumer must
revalidate all evidence on use; such a failure returns a bounded current-use
`INSUFFICIENT_EVIDENCE` error, applies no transition, grants no authority, and
leaves the immutable state lineage unchanged. Restoring the exact bytes permits
revalidation; changed bytes require a new revision and new lineage.

Quarantine is monotonic within Slice 3C: `QUARANTINED -> REJECTED` is the only
disposition change, and neither value has an edge to any positive runtime or
promotion state. Review progress, evidence completion, comparison with an old
revision, repeated local presence, or a Slice 3B PASS never removes quarantine.
A changed byte set is a new revision whose genesis disposition is again
`QUARANTINED`; it cannot inherit an older review outcome.

The only positive terminal pair in Slice 3C is therefore:

```text
review_state = REVIEW_EVIDENCE_COMPLETE
evidence_outcome = COMPLETE
disposition = QUARANTINED
```

`REVIEW_EVIDENCE_COMPLETE` means that the declared evidence set is complete;
it does not mean approval, approval readiness, promotion eligibility, or
routability.

All unlisted transitions fail closed. Slice 3C contains no `APPROVAL_READY`,
`APPROVED`, `AVAILABLE`, `ACTIVE`, `SUPERSEDED`, `REVOKED`, `ROUTABLE`,
`INSTALLED`, `LOADED`, `EXECUTABLE`, `HOST_ELIGIBLE`, or delegation state.

### 17.4 Versioned transition and state records

A `StateVector` contains exactly:

```text
possession_state
review_state
evidence_outcome
disposition
```

The null-parent genesis record created after a successful intake attempt has
exactly:

```text
possession_state = MIRRORED_UNREVIEWED
review_state = NOT_REVIEWED
evidence_outcome = IN_PROGRESS
disposition = QUARANTINED
```

Its required genesis transition changes only possession from the implicit
pre-record vector `NOT_PRESENT + NOT_REVIEWED + IN_PROGRESS + QUARANTINED` to
that exact vector. A source revision cites exactly its successful
`intake-attempt-result`; a component revision cites exactly its own
`component-revision` ID and requires the writer to revalidate its manifest and
parent revision. The transition has empty evaluation receipts and null
evaluation-profile fields and is the only transition that may back a
null-parent state record. No public state record is written for the implicit
vector. State lineages exist only for source and component revisions;
comparison and bridge records never receive lifecycle state.

The state validator enforces these cross-axis invariants on both sides of every
edge: any review or evidence-outcome progress requires
`possession_state=SNAPSHOT_INTEGRITY_VERIFIED` and
`disposition=QUARANTINED`; `evidence_outcome=COMPLETE` if and only if
`review_state=REVIEW_EVIDENCE_COMPLETE`; `REJECTED` cannot coexist with that
complete pair and has no outgoing edge; and every non-rejected vector has
`disposition=QUARANTINED`. Thus review cannot begin from local presence alone,
and no independently valid axis token can be combined into an invalid state.

`nexus.ecosystem-state-transition-receipt.v1` contains exactly:

```text
schema_version: nexus.ecosystem-state-transition-receipt.v1
transition_id: transition/<sha256>
subject_id
subject_sha256
from_state: StateVector
to_state: StateVector
transition_axis: possession | review | review_evidence_terminal |
                 evidence_outcome | disposition
evidence_ids: sorted typed-ID list, maximum 32
evaluation_receipt_sha256s: sorted sha256 list, maximum 16
evaluation_profile_id: token | null
evaluation_profile_sha256: sha256 | null
policy_semantic_sha256
reason_codes
permitted: true
applied: false
authority: fixed zero-authority object
```

`transition_id` uses domain
`nexus.ecosystem-state-transition-receipt.v1` and hashes every semantic field
after itself. Except for the one fixed terminal compound edge below, a receipt
changes exactly one axis. Invalid or skipped edges raise a bounded error and
produce no permitted receipt. The first four review edges in Section 17.2 each
carry exactly one mapped Slice 3B receipt and its exact trusted profile ID and
digest from Section 13.1. The fifth edge is
`review_evidence_terminal`: it atomically changes
`VALIDATION_EVIDENCE_COMPLETE + IN_PROGRESS` to
`REVIEW_EVIDENCE_COMPLETE + COMPLETE`, and changes no other axis. It likewise
carries exactly the review-bundle receipt/profile. This sole compound edge
prevents an observable contradictory intermediate vector.

Possession edges are the two consecutive edges in Section 17.1.
`QUARANTINED -> REJECTED` is the only disposition edge and requires a non-empty
reason-code list. Standalone evidence-outcome edges are only
`IN_PROGRESS -> INSUFFICIENT_EVIDENCE` and
`INSUFFICIENT_EVIDENCE -> IN_PROGRESS` when a new evidence ID is supplied;
there is no standalone `COMPLETE` edge. Review and terminal receipts have
exactly one evaluation receipt and non-null profile fields. All other axes have
an empty evaluation-receipt list and null profile fields. A rejected state has
no outgoing edge.

The writer never mutates the proposal. After revalidating the proposal,
subject, policy, evidence, and current lineage, it atomically appends one
`nexus.ecosystem-state-record.v1` containing exactly:

```text
schema_version: nexus.ecosystem-state-record.v1
state_record_id: state-record/<sha256>
subject_id
subject_sha256
previous_state_record_id: state-record/<sha256> | null
transition_id: transition/<sha256>
state: StateVector
evidence_ids
policy_semantic_sha256
authority
```

`state_record_id` uses domain `nexus.ecosystem-state-record.v1` and hashes all
following fields. The initial state record has a null previous ID; every later
record has exactly one previous ID. Records are append-only. Missing parents,
cycles, multiple heads, stale prior state, or digest disagreement fail closed.
An exact replay of byte-identical transition and resulting state-record IDs
returns the already existing record without a write. Reuse of the same prior
head with any different transition bytes/ID, or replay whose expected result
bytes differ, is a stale/conflicting transition and fails closed. This is the
only idempotence rule.
This versioned state record is the applied state receipt; Slice 3C defines no
separate unversioned or mutable state-receipt format.
This is a bounded quarantine-state lineage, not the future approval/activation
ledger. The writer can write only beneath the quarantine data root.

## 18. Privacy and redaction requirements

Public receipts, errors, logs, and evaluation summaries must never contain:

- absolute local paths, drive roots, UNC shares, usernames, home/profile
  directories, environment values, temporary-directory names, or CAS roots;
- credentials, tokens, cookies, authorization headers, connection strings,
  private keys, secret-shaped values, or credential-bearing URLs;
- raw candidate instructions, prompts, README/Skill/Agent bodies, arbitrary
  scanner output, stack traces, hidden reasoning, or exception representations;
- unbounded filenames, repository prose, provider responses, or archive
  metadata.

Public records use source/component IDs, content digests, path digests, closed
reason codes, safe file-category/extension tokens, and bounded redacted
summaries. Private detailed records may contain normalized repository-relative
paths but never host-absolute paths. Candidate text remains private inert CAS
evidence and is not copied into memory or Agent context.

Redaction uses the proven Slice 3B behavior for environment assignments,
quoted JSON/YAML secrets, credential-shaped tokens, private Windows/UNC paths,
and comma/semicolon-containing values. `redaction_applied` and
`truncation_applied` must remain truthful during generation and revalidation.
Redaction occurs before receipt-size calculation and before any error crosses
the public boundary.

Identifiers reject secret-shaped or path-shaped input rather than relying on
output redaction. Informational timestamps, when present, are UTC RFC 3339 and
are excluded from deterministic identities.

## 19. Deterministic and cross-platform requirements

- Strict JSON semantics are identical on supported Python 3.12 and 3.13.
- Canonical JSON uses UTF-8, NFC strings, sorted keys, compact separators, no
  floats/non-finite values, and exact booleans/integers.
- Set-like arrays are sorted explicitly; input, source, archive, finding, and
  filesystem enumeration order cannot change identities or outcomes.
- Repository paths are modeled with POSIX `/` semantics on every platform.
  Local storage containment requires no-follow handles plus stable file
  identity; `Path.resolve()` may be an informational precheck but is never the
  security decision.
- Case-fold and Windows portability collisions are detected on every host, not
  only on Windows.
- Line endings and archive timestamps do not alter file-byte digests. No text
  newline normalization occurs for source blobs.
- File permission metadata is normalized to the closed mode enum. UID, GID,
  owner name, archive timestamp, filesystem timestamp, and host ACL do not
  enter identity.
- Repeating the same operation 100 times and permuting all set-like inputs must
  produce byte-identical canonical records and equal digests.
- The 60-second ingestion deadline is a fail-safe resource fuse, not an
  identity input. Deadline exhaustion yields bounded insufficient evidence and
  commits no revision record.
- Controlled errors use stable codes, not platform exception text.

## 20. Package and MANIFEST exclusion rules

The main repository may eventually contain only Nexus-owned Slice 3C policy,
schemas, implementation, tests, synthetic fixtures, and approved documentation.
It must never contain raw pilot bytes, cloned repositories, archives, expanded
trees, CAS objects, quarantine/evidence/observation state, generated receipts,
credentials, private paths, or third-party build outputs.

The ecosystem data root is categorically outside `MANIFEST.json`, the release
manifest, source-package membership, release archives, and portable-install
assets. Package code must use an explicit Nexus-owned allowlist; it must not
recursively include a data root even when a caller points one inside the
repository. `.gitignore` is not a security boundary.

On implementation acceptance:

1. Nexus-owned new source/config/test/doc files are added to `MANIFEST.json` by
   the existing deterministic builder.
2. The private package allowlist adds only explicitly reviewed Nexus-owned
   files; a policy file may be packaged, but pilot payloads and mutable state
   may not.
3. Two manifest builds must have identical entry count and bytes with zero
   missing, extra, size, or digest mismatches.
4. Two packages must have the same member set and be byte-for-byte identical.
5. Package inspection must explicitly reject `ecosystem`, `objects`,
   `quarantine`, `incoming`, `evidence`, `comparisons`, `state`, cache, private
   root, upstream payload, and generated receipt members.

This proposed ADR/PDS is intentionally not added to the frozen Slice 3B
`MANIFEST.json` or package allowlist during the specification gate. Approval
must precede its documentation-freeze change.

## 21. Security and supply-chain threat model

### 21.1 Assets and trust boundaries

Protected assets are the frozen Nexus code/manifest, trusted policy seal,
trusted Slice 3B registry, capability/applicability registries, Host/MCP/Agent
authority boundaries, user secrets/private paths, repository integrity, and
future approval/active/checkpoint state.

Trust boundaries are:

```text
untrusted supplied bytes
  -> safe bounded parser
  -> immutable CAS
  -> deterministic static evidence
  -> Slice 3B exact-subject evaluation
  -> quarantined review record

No direct edge reaches capability routing, Host/MCP, install, execution,
Agent delegation, memory, approval, activation, or distribution.
```

### 21.2 Threats and mandatory controls

| Threat | Required control and fail-closed outcome |
|---|---|
| Typosquat, fork, redirect, repository transfer, or alias substitution | Fixed manifest-bound source identity and exact derived origin; mismatch is rejected or policy-conflicting. |
| Mutable branch/tag, force-push, rewind, or observation spoofing | Mutable refs are informational; exact commit/input/tree identities create a new quarantined revision. |
| Compromised upstream or malicious maintainer | No inherited trust; every revision/component is independently quarantined and reviewed. |
| Archive traversal, absolute/UNC/ADS path, collision, link, device, or decompression bomb | Validate before materialization, stream bounds, never follow links, reject structural hazards. |
| Git hook/filter, submodule, LFS, build, package, or dependency execution | No Git checkout, external command, package manager, dependency resolution, or hook execution. |
| Dependency confusion or install-script introduction | Deterministic dependency/hook findings and security-sensitive comparison; quarantine persists. |
| Prompt/control injection in README, Skill, Agent, metadata, or scanner text | Treat as inert data, closed schemas/reason codes, no raw text in control context or receipts. |
| Forged policy, parser-created trust, or post-seal mutation | Manifest-first loader, private seal, exact class, semantic digest recomputed at every use. |
| Forged scanner PASS or evaluation receipt | Scanner cannot approve; Slice 3B receipt is revalidated and rebound to current subject/registry. |
| CAS tampering or TOCTOU | Stable reads, immutable digest paths, rehash before every semantic use, atomic create/no overwrite. |
| Cross-source overwrite or digest collision claim | Namespace by canonical digest, bind provenance separately, verify existing bytes, quarantine conflicts. |
| Resource exhaustion | Hard policy ceilings, streamed accounting, bounded records/findings, explicit no-background-GC. |
| Privacy/secret disclosure | Reject secret-shaped identifiers; redact before output; use path/evidence digests and closed errors. |
| Local cache mistaken for trusted install | Repository-external inert CAS; no Skill root, PATH, import, routing, or loader adapter. |
| Legacy update script mistaken for adoption authority | Treat output as untrusted observation only; no import from `scripts/check_updates.py` into control code. |
| License drift or redistribution leakage | Exact license evidence/diff, incomplete state on ambiguity, no pilot payload in packages. |
| Agent persona or memory poisoning | Advisory-only classification; raw candidate instructions never become permission, memory, or system context. |

Residual risks must be stated honestly: static analysis can miss malicious
behavior; SHA-256 does not establish publisher authenticity; a compromised
local OS can alter process/storage; legal interpretation is outside Nexus; and
future acquisition/promotion adds new trust boundaries requiring separate
approval and red-team review.

## 22. Future update-watch compatibility

Slice 3C records reserve no scheduler or network fields. A future update-watch
adapter may emit a closed `upstream_observation` containing source ID, observed
ref, exact commit, provider evidence digest, and bounded error code. Its
observation ID excludes timestamps and popularity. It must then supply bytes
through the same intake boundary and create a new quarantined revision.

The existing `scripts/check_updates.py` remains a legacy CHECK-ONLY developer
utility. Its `{repository, branch, sha, checked_at}` output is an untrusted
observation, not a snapshot, pin, adoption decision, or trusted policy input.
Slice 3C must not import that script because it has ambient Git/subprocess,
network, and repository-local state behavior.

Future cadence, credentials, retries, API quotas, webhooks, redirects, remote
signatures, and network policy belong to a separately approved watch/acquisition
slice. An unavailable watch reports `UPDATE_STATUS_UNKNOWN`; it never mutates a
quarantined or future active revision.

## 23. Future rollback and checkpoint compatibility

Slice 3C creates immutable IDs and evidence references that a future Slice 4
ledger may cite. It does not create promotion plans, active pointers, rollback
pointers, or checkpoints.

A future activation event must bind the exact approved component revision,
approval receipt, expected prior active pointer, policy/evaluation digests,
idempotency key, and append-only journal position. Application must use
compare-and-swap semantics. A future rollback is a new auditable event to a
still-approved, non-revoked immutable component; it never rewrites history or
trusts upstream availability.

Slice 3C CAS records are therefore immutable and digest-addressed, but their
presence does not reserve them for rollback. Reference-aware retention and
checkpoint durability are future ledger responsibilities. Slice 3C must not
introduce a partial ledger under another name.

## 24. Future Agent Runtime and Memory compatibility

Future Agent Runtime records may reference only an independently approved
Agent component revision plus a separate permission/authority grant. The
Slice 3C `ADVISORY_AGENT` classification remains persona metadata and cannot
be interpreted as a delegation, tool, or execution grant.

Future Memory may store only typed, redacted identifiers, digests, reason
codes, review outcomes, and provenance references. It must not ingest raw
candidate instructions, secrets, absolute paths, scanner prose, or hidden
reasoning from Slice 3C. A memory reference cannot change the referenced
record, confer approval, or bypass retention/privacy policy.

Both future systems must revalidate the exact immutable subject and their own
separate authority policy. No Slice 3C schema includes a permission field,
delegation target, memory-load directive, prompt-injection surface, or runtime
entry point.

## 25. Future Final Red-Team test seams

Implementation must expose pure dependency-injection seams for Nexus-owned
tests, not new runtime authority:

- supplied-byte reader and bounded archive-entry iterator;
- clock-free canonicalizer and identity builder;
- trusted policy loader/guard;
- CAS reader/writer with injectable mutation points;
- provenance, license, and static analyzer adapters returning typed evidence;
- Slice 2 receipt validator adapter;
- Slice 3B evaluator/receipt validator adapter;
- pure state-transition validator and deterministic comparison engine;
- forbidden network, subprocess, package-manager, Host, MCP, Skill-loader,
  router, Agent-delegation, and memory sentinels.

The final red team must be able to exercise malicious provider metadata,
source substitution, poisoned archives, path/link/special-file attacks,
decompression/resource exhaustion, cache mutation, forged policy seals,
scanner compromise, forged/stale receipts, duplicate conflicts, license and
dependency substitution, instruction injection, cross-source writes,
privacy leaks, router/Host escalation, future pointer races, rollback
poisoning, and memory/context poisoning without using real third-party systems.

## 26. Exact test matrix

Every row below is a mandatory parameterized family, not a claimed case count.
Each semicolon-delimited clause and each slash-separated variant is a required
named parameter within that family and must appear separately in the test
evidence. None may be collapsed into a weaker happy-path assertion. All tests
use only Nexus-owned synthetic ZIP bytes in repository-external temporary
directories.

| ID | Required cases and expected result |
|---|---|
| `S3C-POL` | Valid manifest-bound policy; parser-only object rejected; manifest missing/extra/size/digest mismatch; duplicate JSON key; unknown root/source/nested key; bool-for-int; float/non-finite; excessive nesting/large-integer digit bomb; mapping/list subclass input; duplicate/case-duplicate source; repository/source mismatch; secret identifier; exact static/classifier/evaluation profile count, ordering, fields, rules, and semantic digests; missing/extra/duplicated/mutated profile; symlink/reparse policy; unstable read; post-seal mutation; recomputed policy/profile semantic-digest mismatch; legitimate sealed reuse. All invalid cases create no trusted policy and leak no raw interpreter exception. |
| `S3C-ID` | Source case normalization; display metadata non-authority; canonical ordering; 100-run repeatability; every typed prefix and schema domain (`source`, `tree`, `revision`, `component`, `component-revision`, both provenance/license `evidence` domains, `finding`, `static-report`, `classification`, `classification-report`, `comparison`, `bridge`, `intake-attempt`, `intake-attempt-result`, `transition`, `state-record`) has a golden vector and cross-schema non-collision case; raw CAS content digest cannot substitute for a typed ID; same commit/different tree conflict; different commit/same tree distinct; component root change; classification correction preserves component identity; file byte/mode/type change; candidate ID separation; same intake tuple/result replay returns identical IDs; same attempt ID with a different terminal result conflicts without overwrite; timestamp/ref/popularity exclusion; NFC equivalence; normalization collision; case-fold collision; Python 3.12/3.13 equality; malformed digest/object format rejection. |
| `S3C-CAS` | External temp root accepted; repository root, child path, filesystem root, UNC/network, Host/plugin/Skill, symlink/reparse root rejected; valid/forged ownership marker; Windows volume/file-ID and POSIX device/inode mutation; exclusive temp write; input/CAS-quota limit; 60-second deadline; eight/nine quarantined revisions per source; partial-write isolation; flush/rehash; atomic no-overwrite; existing matching object reuse; existing mismatched object rejection; read-time size/digest/metadata mutation; cross-source write; concurrent writers/stale lock; no executable bit; no Skill/PATH/import exposure; no GC/eviction call. |
| `S3C-PATH` | Normal file; empty/absolute/drive/UNC/backslash/URI/NUL/control/bidirectional-control/colon/ADS/dot/dot-dot/empty segment; trailing dot/space; every reserved-name family; excessive path/segment UTF-8 length/depth; NFC collision; case collision; symlink; hardlink; gitlink/submodule; device/FIFO/socket/sparse; executable; LFS pointer; binary; containment race. Structural hazards reject or remain non-materialized exactly as Section 8 requires. |
| `S3C-ARC` | Valid stored/deflated ZIP; TAR/gzip/ZIP64/magic-extension mismatch; encrypted/split/unsupported/self-extracting; malformed header/overlapping offsets; one common-prefix strip; empty/multi-root rejection; traversal header; CRC/declared-size lie; streamed expansion/per-file/entry overflow; per-entry/aggregate compression-ratio overflow; nested archive inert/no recursion; duplicate/colliding member; link/special member; deterministic order and timestamp exclusion; rejected/insufficient pre-revision attempt has null tree/revision; successful attempt creates them. |
| `S3C-INTAKE-IFACE` | Production accepts only a validated bridge plus one stable local ZIP handle; separately reject directory, caller tree manifest, member list, extracted path, Git checkout/worktree, URL, repository object, generic archive, and caller-provided iterator; environment/debug/`test_mode` cannot widen production; private synthetic reader/iterator/CAS/deadline seams are not production-callable; every fake still traverses ZIP headers and the same streaming validators; fake cannot inject a prevalidated tree or external bytes. |
| `S3C-PROV` | Exact binding; wrong source/commit/input/tree/policy/manifest/signature digest; mutable ref non-authority; not-evaluated/missing/present-unverified signature states; rejection of a v1 verified-signature claim; same commit conflicting snapshot; observation timestamp exclusion; provider ID informational; malformed reason/authority; receipt mutation. Conflicts never complete provenance evidence. |
| `S3C-LIC` | Matching SPDX/file; missing; removed; changed; ambiguous multiple; declaration/file mismatch; unsupported expression; notice addition/removal; component/source license conflict; 32/33 license-file boundary; 1 MiB/+1 byte license-file boundary; ordering; path privacy; stale evidence; forged redistribution claim; exact-subject revalidation. Non-matching states block completion. |
| `S3C-FIND` | Every fixed v1 rule and exact predicate boundary; every finding category reachable by v1 plus rejection of unsupported categories; exact category/severity/disposition/reason mapping; deterministic finding/report ID and order; complete/pass, requires-review/pass, blocked, rejected, and insufficient report derivation; duplicate finding conflict; finding limit; analyzer exception/unavailable yields report-only insufficient evidence with no synthetic finding; config/version/digest/rule mutation; streamed 4,095/4,096 overlap boundary; raw scanner text exclusion; path digest; truthful redaction/truncation; secret/UNC/private path/comma/semicolon redaction; PASS-with-hidden-blocker forgery; external scanner self-seal rejection. |
| `S3C-CLS` | Every fixed discovery rule and each six component kinds; exact Skill nested-root closure; source suggestion does not pre-classify; whole repo cannot be Skill; single-file manifest binding; path matching no rule stays source-only; multi-rule conflict; detected kind outside source allow-list; complete/unresolved/conflicting/insufficient report derivation; classification correction preserves component ID; Agent advisory-only; reference no dependency authority; duplicate canonical/localized Agent; display/prose/injection non-authority; component-count/size bounds; 256 KiB/+1 instruction-file boundary; invalid instruction UTF-8; new revision re-quarantine; rejected component terminal; config mutation; order determinism. |
| `S3C-BRG` | Valid `ADMITTED_FOR_REVIEW`; valid `REFERENCE_ONLY`; each three blocked Slice 2 dispositions; malformed/stale/forged Scout receipt; canonical validated-receipt digest; wrong candidate ID/immutable reference/source; `mutable_or_missing`, non-`git_commit`, non-40-hex value, and wrong verification state blocked; derived `git_sha1` commit cannot be caller-overridden; wrong supplied digest/size; unsealed/mutated source policy; ranking non-authority; manual/bypass intake rejected; bridge mutation; zero authority; no network call. |
| `S3C-EVAL` | Each four exact wire-ID/lifecycle/creator-receipt projections; exact seven-validator registry bytes/operators/display names; exact seven manifest-bound profile digests and complete required-check sets; missing/extra/optional/reordered/wrong-source/wrong-evidence/trivial-one-check PASS blocked; for the otherwise valid one-check review-bundle PASS, independently omit, duplicate, reorder, or mutate each of the four prior review-edge receipts and prove no terminal proposal plus unchanged lineage; native PASS transition is only `not_validated -> validation_passed`, permitted and unapplied; five fixed review-edge adapter mappings; two no-review-transition mappings; each five non-PASS states block; stale/wrong subject/parent/registry/profile/check/transition/prior-review-state; forged/self-rewritten receipt; raw-summary mismatch; post-seal validator/policy/profile mutation; redaction truth on generation/revalidation; zero authority; evaluator never applies a Slice 3C state. |
| `S3C-STATE` | Exact null-parent genesis vector; every allowed possession/review/evidence-outcome/disposition edge; exact terminal compound review/evidence edge; every skip/back-edge; review/evidence progress before snapshot integrity; complete/review-complete disagreement; non-rejected/non-quarantined combination; rejected/complete combination; rejection terminal behavior; pre-terminal insufficient outcome and evidence-backed resumption; post-terminal evidence missing/tampered/unavailable produces current-use insufficient error, no demotion, no write, and no authority; new revision for changed bytes; prior-state mismatch; missing evidence/profile; missing/wrong/unknown `schema_version`, missing/extra/null/wrong-concrete-type field for both transition and state record; transition/state-record mutation; missing parent/cycle/multiple head; order determinism; exact replay returns the existing record without write; same-head different replay conflicts; fixed concrete authority types; explicit rejection of `APPROVAL_READY`, `APPROVED`, `ACTIVE`, `ROUTABLE`, `INSTALLED`, `EXECUTABLE`, and every other forbidden lifecycle/authority token; writer containment; failed write leaves lineage unchanged. |
| `S3C-DIFF` | Same revision; same tree/new commit; add/remove/modify/type/mode; component add/remove/change; license; dependency/lockfile; 64/65 dependency-manifest boundary; 1 MiB/+1 manifest boundary; hook/workflow; binary/executable; link/special; Skill/Agent instruction; provenance/signature; same-source requirement; unknown ancestry; force-push/rewind/diverged evidence; every closed security-change code; aggregate/nested list bounds; ordering; old/new swap distinct; comparison mutation; no inherited trust. |
| `S3C-PRIV` | Drive/home/profile/temp/CAS/UNC paths; environment assignment; quoted JSON/YAML secret with comma; semicolon value; bearer/API/GitHub/GitLab/token/private-key/connection-string shapes; credential URL; raw prompt/README/Skill/Agent/scanner/traceback; path digests; short-redacted-text bound; redaction/truncation truth after revalidation; identifier rejection. No private value crosses the public boundary. |
| `S3C-ISO` | Forbidden sentinels for network, Git/subprocess, package manager, candidate import, Skill loader, capability registry, Slice 3A router, Host handoff, MCP connect, execution, Agent delegation, memory, scheduler, checkpoint, approval, promotion, activation, and package mutation. Every sentinel remains untouched in success and failure paths. |
| `S3C-COMPAT` | Frozen Slice 2 receipt/parser behavior; Slice 3A selection/receipts; Slice 3B evaluation/quality and native validation-state semantics; R4/R5 Host boundaries; legacy `{repo,branch,sha}` imports as observation only; branch/order/timestamp identity exclusion; force-push new quarantine; malformed legacy SHA/source; legacy tamper non-authority; network failure leaves facts unchanged; CHECK-ONLY messages; no direct import of update script; unknown future schema fails closed. |
| `S3C-PKG` | Two identical MANIFEST builds; zero missing/extra/size/digest mismatch; two byte-identical packages; exact member set; no CAS/quarantine/incoming/intake-attempt/evidence/comparison/state/receipt; no pilot bytes; no secret/private path; no `.git`/cache/generated data; policy included only after the approved implementation release gate; compile/syntax; `git diff --check`; clean final worktree at freeze. |
| `S3C-RED` | Malicious metadata provider; source alias/transfer; poisoned archive; cache mutation at each read boundary; forged policy seal; forged scanner result; forged evaluation receipt; duplicate/conflicting evidence; dependency substitution; instruction injection; cross-source CAS write; resource exhaustion; privacy exfiltration; router/Host/MCP/Agent escalation; future pointer race; future rollback/memory poisoning seam. All fail closed without new authority. |

Required regression execution after implementation is:

1. the affected Slice 3C focused suites;
2. Slice 2 Scout, Slice 3A semantic routing, Slice 3B evaluation/quality loop,
   authority-boundary, package, and backward-compatibility suites;
3. the full repository suite with no new skip, failure, or error beyond the
   four frozen environment skips;
4. compile/syntax checks, `git diff --check`, MANIFEST rebuild/verification,
   package reproducibility, repository/security/privacy checks, and final
   smoke;
5. smoke may reproduce only the already documented **6/10** result: the four
   Host-managed `document`, `spreadsheet`, `pdf`, and
   `research_document_chain` plugin-cache checks may fail identically. It must
   describe that limitation truthfully rather than modifying Host state.

Live GitHub tests are prohibited for deterministic acceptance. Any future live
smoke is separately authorized, non-blocking evidence and cannot replace the
hermetic matrix.

## 27. Exact acceptance criteria

Slice 3C implementation is acceptable only when all statements below are
proven with recorded evidence:

1. The implementation diff is limited to the files and order in Section 28;
   no Slice 3D/4, watcher, approval, activation, routing, install, execution,
   Host, MCP, Agent Runtime, Memory, or rollback behavior exists.
2. Every schema is closed, versioned, bounded, duplicate-key rejecting,
   exact-type checked, canonical, and unknown-version fail-closed.
3. Parsing cannot manufacture a trusted source policy; MANIFEST failure cannot
    return one; post-seal mutation and semantic-digest mismatch fail at every
    sensitive use; the exact analyzer, classifier, and seven evaluation
    profiles are policy-bound; legitimate integrity-loaded behavior passes.
4. Every supplied byte, tree entry, revision, component, evidence object, and
   comparison is cryptographically bound to the exact subject consumed.
5. All path/archive/resource attacks in the exact matrix fail before unsafe
    materialization, with no fallback parser or external command. Production
    accepts only the bridged stable ZIP interface; synthetic test readers
    cannot inject a tree or bypass the same streaming validators.
6. CAS is repository-external, immutable, rehashed on use, atomic on publish,
   never a Skill/PATH/import root, and exposes no private root in receipts.
7. Provenance, license, static finding, and component classification records
   are deterministic evidence only and cannot express approval or authority.
8. The exact genesis and cross-axis invariants hold, and every new
    revision/component begins and remains quarantined unless rejected;
    no Slice 3C path produces an approved, active, routable, installed, loaded,
    executable, Host-eligible, MCP-authorized, or delegated state.
   Installation, execution, Host mapping, MCP connection, Agent delegation,
   approval, promotion, activation, and routing authority remain exactly
   `none` in every success and failure record.
9. Slice 2 bridge cases revalidate the exact frozen receipt, accept only a
    representable verified 40-hex `git_commit`, and never convert
    recommendation/ranking into trust or permit manual bypass.
10. Slice 3B receipt cases revalidate exact current subject and trusted
     registry/policy/profile semantics; only a PASS containing the exact full
     mandatory check profile supports a review-axis proposal and never applies
     it or grants authority. Partial or trivial PASS is blocked.
11. Slice 3A and every execution/Host/MCP/Agent boundary remain isolated under
    positive, negative, and failure-path sentinels.
12. Old/new comparison is order-independent and reports every declared
    security-sensitive change without inheriting old trust.
13. All eight pilot policy records are source identities only; no third-party
    bytes or live evidence enter the repository, tests, MANIFEST, or package.
14. Public outputs contain no secret, credential, private path, raw candidate
    instruction, scanner prose, traceback, hidden reasoning, or unbounded data;
    redaction/truncation truth survives revalidation.
15. Golden identities and receipts match across 100 runs and supported Python
    3.12/3.13 environments; portable path cases match on Windows and POSIX.
16. The entire Section 26 matrix passes with no ignored or weakened case and no
    third-party/network/subprocess/package-manager/Host activity.
17. Focused, affected legacy, and full regression suites pass with no new skip,
    failure, or error beyond the four frozen environment skips.
18. Compile/syntax, `git diff --check`, MANIFEST zero-mismatch, two-build
    MANIFEST identity, package member review, byte-for-byte package
    reproducibility, repository integrity, secret/private-path/generated-state
    checks, and final smoke meet the frozen procedure.
19. Independent Architecture, Security, Code Review, and Testing Evidence
    Agents report no unresolved Critical/High blocker; Agents remain advisory.
20. The acceptance report records Nexus Skill routing truth, including
    `CAPABILITY_NOT_COVERED` when reproduced, without claiming a Skill ran.
21. Freeze uses a separately approved implementation branch and tag; this
    specification itself creates neither.
22. Documentation confirms that no Slice 3C content was downloaded, installed,
    or executed during the specification gate and no Slice 3D work began.

Any unmet criterion is a blocker. The implementation must stop without merge,
freeze, tag, promotion, or Host-state modification.

## 28. Implementation order

After this specification receives explicit approval, implementation proceeds
in this exact order, with affected tests after each step:

1. Create the separately approved Slice 3C implementation branch from the
   frozen Slice 3B commit; record the clean baseline and no-Slice-3D boundary.
2. Add `config/ecosystem-source-policy.json` containing exactly the v1 policy
    with its fixed analyzer/classifier/evaluation profiles and eight source
    identities, plus closed schema constants and synthetic fixtures. Do not
    acquire source bytes.
3. Add `ash/ecosystem_policy.py`: bounded parser, manifest-first trusted loader,
   private seal, semantic digest, and revalidation guard.
4. Add `ash/ecosystem_models.py`: strict JSON primitives, canonicalization,
   identity models, records, enums, errors, and zero-authority constants.
5. Add `ash/ecosystem_storage.py`: repository-external root validation,
   no-follow handle identity checks, bounded streaming CAS,
   atomic/no-overwrite writes, quota enforcement, revalidation, locks, and
   quarantine metadata views; no GC or eviction.
6. Add `ash/ecosystem_intake.py`: supplied-ZIP validation,
   ZIP-only per-member streaming, path/file/link/archive/resource enforcement,
   tree/revision manifests, and no-execution sentinels.
7. Add `ash/ecosystem_evidence.py`: provenance, license, fixed-profile static
    findings/report, fixed-profile component inventory/classification/report,
    privacy projection, and redaction.
8. Add `ash/ecosystem_compare.py`: deterministic exact old/new comparison and
   security-sensitive change classification.
9. Add `ash/ecosystem_bridge.py`: validated Slice 2 quarantine requests only,
    pure lifecycle transition validation, and Slice 3B subject/receipt binding;
    no manual or bridge-bypass intake exists in v1.
10. Extend `config/validator-registry.json` only with the four closed Slice 3C
    subject types and deterministic validators; preserve the trusted loader and
    zero-authority result.
11. Add the Section 26 synthetic unit, adversarial, integration, compatibility,
    isolation, package, and golden-vector tests. No external repository fixture
    is permitted.
12. Add approved documentation links, update `MANIFEST.json`, and extend the
    private package allowlist only for reviewed Nexus-owned files.
13. Run focused and legacy suites; fix only confirmed Slice 3C blockers with
    permanent regressions; then run the full acceptance procedure in Section
    27.
14. Obtain independent Architecture, Security, Code Review, and Testing
    Evidence acceptance. Stop on any unresolved blocker.
15. Only under a separate explicit freeze authorization: commit, push,
    fast-forward, tag, and verify the clean frozen state. Do not begin update
    watch, promotion/rollback, Agent Runtime, Memory, Slice 3D, or Slice 4.

The planned modules are intentionally dependency-light and use the Python
standard library plus existing Nexus primitives. New project dependencies are
not permitted merely to simplify parsing, scanning, or testing.

## Agent and Skill Utilization Report

- **Nexus Skill:** Invoked for the specification task under governance mode.
  It returned `fallback_needed` with reason `CAPABILITY_NOT_COVERED`, selected
  no Skill, executed nothing, and granted no authority. Native Codex therefore
  covered the documentation work.
- **Architecture Agent:** Advisory-only review of state, identity, storage,
  integration, future compatibility, and implementation order. No edits or
  external access were authorized.
- **Security Agent:** Advisory-only review of integrity seals, quarantine/CAS,
  path/archive/resource safety, privacy, supply-chain threats, and red-team
  seams. No edits or external access were authorized.
- **Testing Evidence Agent:** Advisory-only review of the exact test matrix,
  acceptance evidence, compatibility, MANIFEST/package, and smoke gates. No
  edits or external access were authorized.
- **Native Codex:** Reconciled the approved decision with the frozen local
  Slice 2/3A/3B and distribution contracts and authored this ADR/PDS. Native
  work did not implement Slice 3C or contact a third party.

## Approval gate

Approval of this ADR/PDS authorizes only a later, separately initiated Slice
3C implementation gate with the frozen scope above. Until then:

- the document remains a proposed specification;
- no implementation branch exists;
- runtime, tests, policy, MANIFEST, package, and Host-managed state remain
  unchanged;
- none of the eight source repositories may be downloaded, cloned, installed,
  imported, or executed; and
- Slice 3D and all later roadmap work remain prohibited.
