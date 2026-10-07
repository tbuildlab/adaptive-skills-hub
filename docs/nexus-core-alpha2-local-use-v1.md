# Nexus Core Alpha 2 — local project use

Status: source implementation for trusted, non-secret local projects. Production
G2 remains HOLD; Positive Host Binding remains ABSENT. The installed Desktop
release is unchanged. No provider, VM, Route D or Root R operation is added.

## Quick workflow

Use Python from a trusted local runtime and the repository's `scripts/nexus.py`.
Preparation never executes tests or edits project source. It creates only the
task package, copied reviewed bundle, plan and approval summary.

```powershell
python scripts/nexus.py core "Fix the failing backend regression tests." --project "D:\Projects\Example"
# Review the printed exact edits, inputs, hooks, hashes, output and budget.
python scripts/nexus.py core-run "<printed task directory>" --approve <printed SHA-256> --progress
python scripts/nexus.py core-status "<printed task directory>"
python scripts/nexus.py core-cancel "<printed task directory>"
```

`core --json` emits a machine-readable view including `task_directory` and
`approval_summary`. Existing `core-plan/run/status/cancel` options and JSON fields
remain supported. New fields are additive. `--progress` sends concise lifecycle
metadata to stderr and leaves final JSON on stdout. Raw hook stderr is not shown.

Use `core-run ... --max-steps 1` for a verified checkpoint pause. Resume with the
same directory and approval hash. Completed steps are not re-executed. A status
of `SAFE TO RESUME` describes a non-ambiguous checkpoint within the remaining
deadline, subject to fresh binding checks at dispatch. `TASK COMPLETE` requires
verified artifacts. `MANUAL REVIEW REQUIRED` includes blocked, failed, cancelled,
expired and ambiguous outcomes. An unresolved intent is never blindly replayed.
Pending cancellation is reported explicitly; it cannot be cleared by resume.

Alpha 2 defaults: 12 calls, 600 seconds from preparation, 30 seconds per hook,
two attempts, one replan, 64 KiB hook output, 1 MiB per artifact. Verification
and repair consume calls. Pausing does not renew time or counters. Use explicit
smaller `core --total-seconds` and `--step-seconds` values if needed. If review
takes longer than the deadline, prepare a new task; do not reset the old ledger.

## One small reusable project configuration

Place `.nexus.json` in a supported, trusted project. There are no executable or
command fields. Task prose only selects capabilities through the existing V2
planner; it never supplies executable commands or replacement code.

Python example, using an existing `unittest` directory:

```json
{
  "schema": "nexus.core.project.v1",
  "profile": "python",
  "files": ["shipping.py", "tests/test_shipping.py"],
  "tests": "tests",
  "patches": [{
    "path": "shipping.py",
    "old": "return amount - discount",
    "new": "return max(0, amount - discount)"
  }]
}
```

This runs the existing tests, applies only this reviewed patch after a failure,
retries once, and independently runs the tests again to verify the report.
Omit `patches` for test-only work. A passing first run does not apply a patch.
Zero tests, entirely skipped tests or test execution/load errors stop without
repair. Only a concrete assertion failure can trigger the approved patch.
Test discovery is fixed to `test_*.py`. Every `.py` input under the ordinary
project tree is hash-bound (up to 64 files, 1 MiB total); excluded runtime/cache
directories are not imported by this bundle. All project tests and imports must
be owner-reviewed trusted code. Tests execute as the current user; they can have
side effects outside this contract. Core provides no sandbox for unknown tests.
Use only standard-library projects or dependencies already in the exact approved
runtime. There is no dependency installation or automatic virtualenv discovery.

Static web example:

```json
{
  "schema": "nexus.core.project.v1",
  "profile": "static-web",
  "files": ["index.html"],
  "patches": [{"path": "index.html", "old": "Book a consultation", "new": "Request a service quote"}],
  "checks": [{"path": "index.html", "contains": "Request a service quote"}]
}
```

Prepare with `core "Improve HTML UI content and run regression tests."`. The
fixed checker verifies expected text, a title and no duplicate IDs. It does not
claim browser rendering, accessibility certification, JavaScript behavior or a
Node build. Node/TypeScript execution remains unsupported in this milestone.

Multi-file evidence example:

```json
{
  "schema": "nexus.core.project.v1",
  "profile": "evidence",
  "files": ["README.md", "architecture.md", "notes.txt"]
}
```

Use `core "Research local project evidence and review the software architecture."`.
Inspection produces an inventory. The next selected capability consumes that
structured inventory and produces a source-bound factual Markdown summary.
Independent verification recomputes both. This is deterministic synthesis, not
an LLM analysis or arbitrary architectural judgment. A research-only task may
select only inspection; planner steps are not silently extended.

Without config, bounded read-only evidence discovery selects existing
`README.md`, `pyproject.toml`, `package.json`, or `index.html`. Editing/testing
requires config. `--profile` may confirm a profile; it cannot override a conflict.

Each task creates a fresh `nexus-results/<task-id>` artifact directory. Optional
`output` changes only the simple output-root name. Prior results are preserved.
The same config can be reused without hand-building catalogs/hashes; already
applied exact patches are recognized. New desired edits still require explicit
configuration and a new approval. No repair is generated from task text.

## Reviewed capability and scope contract

The fixed `nexus.core.bundles.v1` implementation lives in
`ash/core_capabilities.py`. Preparation copies its exact bytes and bounded
settings into a per-task catalog with generated `SKILL.md` frontmatter. All
instructions, hook/settings bytes, current interpreter bytes, task, project,
input hashes, allowed before/after patch hashes and budgets enter approval.
The controller checks config/input/source membership before each phase. Hooks
also enforce declared paths, fixed phases and independent artifact verification.

Inputs: 1–32 distinct UTF-8 non-secret files, 256 KiB per file. Up to eight exact
one-match patches, one per declared supported text file. HTML checks: 1–16.
Absolute/parent/ADS/private/reserved paths, symlinks, reparse paths and hard-linked
inputs are refused. Unknown config keys, raw commands, executable paths,
credentials and privilege requests are unsupported. Artifacts cannot replace
unrelated prior files. Repairs are idempotent within the approved before/after
hash set; file changes outside that set stop before dispatch. Concurrent same-user
tampering is outside the alpha trust model; this is not ACL custody or attestation.

Failure categories remain separate: test failures may use a declared safe repair;
verifier failure remains failure; unsupported capabilities, scope/config drift
or environment errors refuse progress; timeout/overflow or interrupted intent
may have partial effects and require reconciliation. No ambiguous task retries.
Cancellation terminates the direct hook child only, not an independently
qualified process tree. Checkpoints and receipts are local checksum-bound JSON,
not authenticated same-user tamper-resistant records. External databases remain
optional and are not a Core dependency.

## Skill prose and Host boundary

Alpha 2 bridges only reviewed, hash-bound Skill frontmatter to fixed capability
IDs. Prose alone does not execute. Unsupported tasks produce a blocker and
`NEXT-OWNER-DECISION.md`; there is no fabricated Host receipt. Reuse the existing
`plan "<task>" --project "<project>" --handoff` for a non-executing Host plan.
Existing R4/R5 MCP handoff/receipt validation remains on its accepted interface;
Core does not call Desktop tools, enumerate private capabilities or import a
returned Host artifact as a completed local step. Host execution requires its own
current authority and supported capability. This bridge is DEFERRED independently
of the three supported local profiles.

## Validation and future installation

`python scripts/core_project_demo.py <new directory> --run` explicitly approves
only three fixed, non-secret fixture projects: a three-test Python repair,
static HTML edit/check, and three-file inventory/report with checkpoint resume.
The fixture files are ordinary projects with config, not custom per-project hooks.
Focused tests also cover backward CLI compatibility, drift, scope refusal,
config shape, capability resolution, profile reuse and interrupted-effect rules.

Private source packages now include both Core user documents, all Core code and
demo/test scripts. The strict existing package guards remain unchanged. Package
validation uses an isolated static source snapshot because the real repository
contains legitimate excluded/mutable storage; it does not delete those objects.

The installed `0.1.0-r5.pilot.4` Desktop release is unchanged. A future separately
authorized release needs an additive release allowlist for `scripts/hub.py`,
`scripts/nexus.py`, Core demo entry points and Core docs; `ash` is already included.
It must verify relocated CLI/profile execution, package/release manifest hashes,
offline runtime/dependency inventory and a reversible install. No Core tools
are added to MCP by this sprint. Installation, publishing and provider/production
Host qualification require separate authorization; they are distinct milestones.
