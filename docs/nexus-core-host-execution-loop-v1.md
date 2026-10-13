# Nexus Core Host Execution Loop v1

This is a **post-G2 Nexus Core product enhancement / execution-completion slice**.
Historically accepted G2 remains completed/frozen at its existing accepted
checkpoint. No G2 acceptance evidence, milestone labels or criteria are changed.
G3/N01 remains HOLD / OPTIONAL_HIGH_ASSURANCE_RESEARCH. REAL_ADMISSION=NO.

## Supported workflow

One trusted local Codex Host task: inspect a user-owned Git repository's tracked
status metadata and whitespace checks for explicitly declared non-secret tracked
files; create and verify a local maintenance report outside that repository.
No source edits, stage/commit/push/clean/reset, remote access, deployment, project
test execution, provider request, custody, recovery or production admission.

The existing V2 planner discovers and loads a real task-local narrow Skill copied
from the repository-owned `Core Host Git Maintenance v1` section of the existing
Nexus Skill. Its actual source and loaded-content hashes are bound. Missing or
incompatible coverage blocks; selection is never forced. The old Core hook runner,
approval API, Agent advisory semantics and Presentations mappings are unchanged.

## Host bookkeeping

Use `scripts/nexus.py` with a trusted local Python runtime. The Host performs
these steps; the user need not approve each ordinary read-only operation:

```text
core-host-plan "Inspect this local Git repository changes and whitespace checks, then return a maintenance report." --project <repository> --file README.md --file docs/example.md --task-dir <fresh-outside-directory>
core-host-next <task-directory>
core-host-observe <task-directory>     # bounded normalized JSON on stdin
core-host-status <task-directory>
```

Plan requires an existing parent and a new output directory outside the inspected
worktree. It reads only declared regular non-secret files for scope hashes; raw
project content is not sent into the planner. One bounded local checksum-bound
checkpoint and task-local Skill are created. Nothing is executed during planning.

The output must also be outside an enclosing Skill package: the existing V2
nested-Skill rule remains enforced. For example, use a fresh sibling task folder,
not this Nexus repository's own `output` folder for the task-local Skill.

`next` charges and persists an intent before returning fixed Git argument arrays
or the two exact report bodies. Nexus invokes no Host tools. The Host executes the
arrays through its available native tool; never synthesize shell text from task
input, execute arbitrary response commands, or substitute a missing capability.
The original task is retained. Negative mutation prohibitions already guaranteed
by this fixed profile are separated from its positive planner input; read-scope
restrictions must be resolved explicitly, not silently ignored. V2 is unchanged.
Git optional locks, pager, fsmonitor, untracked-cache mutation, external diff and
textconv are disabled where applicable; pathspecs are literal.

## Observation and verification

Every observation has exactly `task_id`, `action_id`, `stage`, `host_status`,
and `data`. Host statuses are `ok`, `failed`, `unknown`, `approval_required`,
`denied` or `cancelled`. Unknown/failed/approval results never become completion.

Inspection data: `root` (canonical worktree root), `head`, `status_sha256` (SHA256
of exact NUL-separated tracked-only porcelain output), `changed_tracked` entry
count and sorted exact `tracked_files`. Parse rename/copy status entries correctly.
All Git identity/status/ls-files commands must actually succeed; untracked
declared files or a different repository are rejected. Untracked-file discovery
is deliberately excluded, so a clean check is not a claim of a completely clean
repository or a secret scan.

Check data has `unstaged` and `staged`, each with `exit_code` and `findings`.
Findings contain only an allowed `path`, positive `line`, and `kind`:
`trailing_whitespace`, `space_before_tab`, or `blank_line_at_eof`. Exit 0 requires
no findings; recognized Git whitespace exit 2 requires findings. Other failures
stop. Normalize before persistence: discard raw source lines and stderr values.

For report, the Host writes only new `report.json` / `report.md` from the returned
bodies, then observes `{"files":["report.json","report.md"]}`. Unknown existing
files must not be overwritten. For verify, the Host runs all fresh identity/status/
tracked/check arrays and submits `repository` and `checks`. The adapter separately
reopens both actual reports, verifies exact facts/digests, rechecks scope and Skill
hashes, and rejects fresh-state drift. Receipt is then written as `receipt.json`.

`completed_with_findings` is verified inspection with observed whitespace issues;
it is not clean Git. `completed` requires real observations and artifact readback,
not model self-assertion. Local observation files/receipts are same-user evidence,
not authenticated authority or independent production-security certification.

## Bounds and continuation

Defaults: eight Host action batches, 600 seconds overall, 20 seconds per action,
64 KiB observation and 1 MiB artifact ceiling (the reused fixed file reader/writer
also imposes its smaller 256 KiB bound). Counter units are logical Host batches;
they are not provider spend or the count of Git processes inside each batch.
One inspect/check/report/verify completion normally consumes four batches.

Calling `next` while an intent is pending returns no new action. Resume retains
verified steps, charges and original expiry; no blind redispatch or budget reset.
An interrupted report write can be reconciled by observing already existing exact
files while the pending action remains valid, without rewriting them. Expired or
unknown outcomes stop; no automatic replacement task. Completed reports are
reopened when continuing a completed checkpoint; tampering refuses completion.
A task-owned `cancel.request` stops continuation. Dangerous Host actions retain
the Host's existing approval mechanism and remain outside this v1 profile even
after generic approval. No local approval hash impersonates Owner authorization.
