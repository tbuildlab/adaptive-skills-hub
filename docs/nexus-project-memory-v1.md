# Project Memory v1 — Nexus 0.3.0 source

Status: C2 source implementation. Not released, installed or accepted as a real
installed workflow. Nexus 0.2.0 remains the installed/released baseline.

## Boundaries

Project continuity and bounded execution learning are local, same-user Host
data, not Codex/ChatGPT global Memory, a production storage service or a G4
persistence interpretation. G4 remains pure historical verification.
REAL_ADMISSION=NO; production adapters, N01/PREAUTH and G1–G6 stay unchanged.

`nexus.plan_task` is read-only. Its new `project_memory` block cannot alter V2
rules, authorization, capability qualification, research classification or
HOLD/fallback semantics. It is untrusted advisory historical context. A failed
Skill on this project never becomes a global exclusion or ranking rule.

## Trusted storage and identity

The primary data store is `D:\NexusData\project-memory`, configurable only by
an explicit Host workflow to another authorized fixed local D: directory.
There is no C: fallback, cache or secondary copy. The small machine-local
`project-memory-config.json` beside the existing trusted `workspaces.json`
contains a root pointer only, not Project Memory. Do not repoint
`NEXUS_DATA_ROOT` or migrate Reference Library v1.

Initialization and persistence reject UNC/device/relative/traversal/alternate
stream/reserved names, reparse ancestors, inappropriate roots, hard-linked
record files and repository/worktree overlap. Roots must be outside source,
release, runtime, plugin and cache locations. Planning never creates a root,
lock, index, revision, timestamp refresh or repair.

Each project has a stable Host-created UUID, canonical approved project locator
and canonical workspace hash. Display names and Git commits are not identities.
The only data file per project is:

```text
<root>/projects/<workspace-binding>.<project-uuid>.json
```

The bundle includes immutable revision snapshots and one current digest. There
are no per-revision files and no mutable global index. Previous digests and
monotonic revision numbers are validated on reads and writes. Changed/removed
decisions require exact supersession links and reasons. Changing an approved or
frozen decision additionally needs verified user-acceptance evidence.

## Closed schemas

See `config/project-memory.schema.json`; runtime validation additionally enforces
UTF-8 byte bounds, privacy, cross-field consistency, evidence and history.

- `nexus.project-memory.config.v1`: trusted enabled/root/required-drive settings.
- `nexus.project-memory.proposal.v1`: identity, state, completion, artifacts,
  evidence, reference usage, capabilities, lessons, environment, supersessions.
- `nexus.project-memory.revision.v1`: proposal snapshot plus sequence, prior and
  current digest, Host authorization reference and write time.
- `nexus.project-memory.bundle.v1`: identity binding and bounded revision chain.
- `nexus.project-memory.write-receipt.v1`: content-free committed digest receipt.
- `nexus.project-memory.context.v1`: bounded read-only MCP projection.
- `nexus.project-validation.v1`: Host execution-validation receipt binding exact
  project/workspace/scope/checks and hashes of named artifacts.

Facts distinguish verified/observed/inferred/unverified. Skill/Agent/workflow
entries distinguish selected, used, role, scope, evidence and effective/partial/
ineffective/fallback outcomes. Lessons preserve symptoms, known/unknown causes,
corrections, rejected approaches, recovery and prevention. No raw instructions,
hidden reasoning or invocation logs are accepted.

`project_completed` requires whole declared scope and actual passing verification;
`validated_checkpoint` means only the named milestone. Incomplete/failed records
cannot claim completed scope. User accepted/rejected/not_obtained is independent
of automated passed/failed/not_run. Rejected delivery is not project completion.

## Host completion handoff

Host executes and validates the project or milestone first. A planner PASS is
not execution evidence. Host then forms a screened bounded proposal. Every
verified evidence pointer must match a guarded local file hash. Completion needs
a typed execution-validation receipt whose scope/checks agree with the proposal
and whose bounded named artifact hashes still match. This validates a same-user
Host assertion, not cryptographic proof against a malicious Host.

The explicit persistence API is:

```python
store.persist(proposal, authorized_workspace,
              authorized=True, privacy_reviewed=True,
              authorization_ref="owner-consent-receipt",
              expected_previous_digest=previous_revision_digest)
```

Use `MemoryStore.initialize` only in an explicitly authorized initialization.
No initializer runs during planning. The packaged thin Host CLI supports
`new-id`, `initialize`, `validate`, and `persist`:

```text
python -B scripts/project_memory.py initialize --workspace-config <trusted-config> --workspace-id <alias> --authorize --authorization-ref <consent-id>
python -B scripts/project_memory.py persist --workspace-config <trusted-config> --workspace-id <alias> --authorize --privacy-reviewed --authorization-ref <consent-id> [--expected-previous-digest <digest>]
```

Persistence/validation read one bounded proposal from stdin; do not put user
memory in repository files or command-line arguments. Schema-only `validate`
does not promise that persistence/evidence checks will pass. The CLI does not
execute validators, read unrelated files or connect to MCP/network services.
Initialize configuration only after source/install approval; these are usage
instructions, not an automatic installation step.

Writes take a fixed exclusive cooperating-writer lock, compare the prior digest,
validate history/capacity, flush/fsync a same-directory temporary bundle and
atomically replace the target. A failed replace preserves the previous valid
bundle. Do not remove another writer's lock. No automatic pruning/compaction:
capacity exhaustion refuses the memory write without failing project execution.

## Automatic next-session retrieval

The existing installed stdio entrypoint loads memory configuration beside its
trusted workspace configuration. For a normal `nexus.plan_task` call it resolves
the authorized workspace and automatically reads the unique matching bundle.
No memory JSON paste or manual D: browsing is required. Optional opaque
`project_id` resolves a known ambiguity; it is never a path or display name.

Multiple matches return `project_memory_ambiguous`; missing/corrupt/unavailable
data returns a visible non-blocking state. `project_context_mode=none` skips
memory entirely. Research opt-out alone does not disable local project context.
Foreign workspace contents are not opened for matching.

Retrieval returns the latest valid bundle state plus deterministic task-relevant
project-local lessons, including relevant earlier-revision lessons. Source
revision digests identify lesson provenance. Unrelated lessons are excluded;
omissions are reported. A corrupt chain is not silently rolled back.

No network, storage writes or changes to mtime/hash are required. The current
safe MCP envelope remains 24 KiB. Memory is at most 8 KiB; essential state is
never silently truncated. Optional sections may be omitted; envelope pressure
returns an overflow warning rather than forcing capability coverage or HOLD.

## Bounds and privacy

128 projects; 32 revisions/project; 32 KiB/revision; 1,152 KiB/bundle; 160 MiB
committed store. Text fields: 1,024 UTF-8 bytes maximum, names 128, IDs 64,
locators 512. Aggregate state facts/decisions: 64. Supersessions: 32. Artifacts:
16; evidence pointers: 32; Skills/Agents/workflows: 8/4/8; lessons: 16/revision;
reference usages: 16. Continuation core: 4 KiB. Retrieved lessons: four, each
at most 768 bytes. Aggregate limits override individual field allowances.

Reject secrets, credentials, key/token material, transcript/code/debug dumps,
control/bidi content, unsafe paths and credential-bearing URLs before any
temporary write. Absolute private paths are permitted only in the approved
identity locator and never exposed in the MCP projection. Screening does not
prove arbitrary prose is secret-free: explicit Host privacy review is required.

Reference usage stores IDs and project-specific influence only. Validate accepted
IDs against the read-only scoped Reference Library; unknown IDs fail the memory
write. Never enroll, prefer, duplicate records or change license/scope metadata.

## Packaging and acceptance

Actual user bundles, machine-local configuration and local receipts never belong
in Git or releases. Ignore their names and reject embedded store directories,
markers and renamed JSON carrying Project Memory schemas at MANIFEST/source/
release validation boundaries. Only source/schema/docs and sanitized tests ship.

C2 uses disposable controlled test stores, not the real D: primary. It does not
build/install/release or claim full Phase C acceptance. C3 still requires an
explicit real verified milestone write, installed MCP smoke, terminated session,
fresh installed-process automatic retrieval, workspace isolation and privacy
checks before any publication. Preserve every prior release and frozen tag.
