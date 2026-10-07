# Nexus Core MVP / Internal Alpha v1

## Scope and authority

Owner commissioning source: `CORE MAINLINE RESUMPTION + DELIVERY SPRINT v1`, received 2026-10-07. Baseline branch: `nexus-v2-g2-development`; baseline HEAD: `114958fa12a1b583e9f571c05c13e1e30cc1e6bd`. This is product-core implementation under that explicit authority, not production G2 implementation or acceptance.

The core extends the existing opt-in V1 `hub_command` abstraction using V2 task profiles, discovery, trusted applicability, ranking, selection and selected-instruction loading. It adds a sequential local command-hook client with checkpoints. It does not add a model loop, agent delegation, generic shell, provider adapter, privileged broker or universal DAG scheduler. Frozen planner/advisory/MCP and presentation Host interfaces retain their semantics. Plain Skill prose still needs Host execution; discovery or loading alone is never completion.

Hooks are reviewed, trusted, same-user Python code. They are **not sandboxed**. Catalog claims are explicit local operator configuration, not global conformance evidence or an untrusted Skill's self-granted authority. The operator must review code, dependencies, project scope, idempotence and verifier coverage before approving. The current alpha supports non-secret local work only; credential, network/provider, payment, privilege, destructive and deployment operations remain outside its supported authority.

## Inspected baseline and implemented target

Labels describe this bounded product milestone; COMPLETE does not mean universal task support or production qualification.

| Area | Before | After | Implementation/evidence |
|---|---|---|---|
| A Task intake | COMPLETE | COMPLETE | Existing natural-language task profile parser |
| B Planner | COMPLETE | COMPLETE | Existing bounded `ash/v2.py` plan, requirements and fallback |
| C Skill discovery | COMPLETE | COMPLETE | Existing local `SKILL.md` discovery; Core limits it to the supplied catalog root |
| D Selection/ranking | COMPLETE | COMPLETE | V2 semantic applicability, ranking and minimal coverage selection |
| E Tool routing | PARTIAL | COMPLETE | Selected Skill maps to byte-bound explicit Python hooks |
| F Execution loop | PARTIAL | COMPLETE | Execute/observe/verify sequentially through approved local hooks |
| G Multi-step continuation | MISSING | COMPLETE | Fixed dependency ordering; structured outputs passed to later steps |
| H Failure detection | PARTIAL | COMPLETE | Command, schema, artifact and independent verifier failures |
| I Retry/replan | PARTIAL | COMPLETE | Explicit retry-safe hooks, approved repair, at most one planning re-selection |
| J Cancellation | PARTIAL | PARTIAL | Persistent cancel request, pre-dispatch check and direct-child termination; escaped trees remain unqualified |
| K Persistence | PARTIAL | COMPLETE | Atomic local JSON state and ordered event records |
| L Resume | MISSING | COMPLETE | Resume only verified checkpoints; unresolved dispatch/running state becomes AMBIGUOUS |
| M Verification | PARTIAL | COMPLETE | Separate bound verifier plus artifact existence/size/digest verification |
| N Budget | PARTIAL | PARTIAL | Command-count/deadline/byte bounds; no provider spend or all-fault lifetime guarantees |
| O Observability | PARTIAL | COMPLETE | CLI status, step observations, attempts, blockers and final receipt |
| P Approval | PARTIAL | COMPLETE | Exact approval digest over the task, project, catalog, interpreter, budget and initial steps |
| Q MCP | COMPLETE | COMPLETE | Existing local stdio read-only planner/advisory integration; no new execution tool exposed |
| R Local project | PARTIAL | COMPLETE | Explicit project path, structured hook context and local artifact readback |
| S Database readiness | DEFERRED | DEFERRED | Core uses local state; external DB is optional and absent |
| T Operator visibility | PARTIAL | COMPLETE | Existing CLI entry gains `core-plan/run/status/cancel`; no new UI |
| U Packaging | PARTIAL | PARTIAL | Repository CLI and isolated manifest-source validation; installed desktop release is unchanged |
| V Regression | PARTIAL | PARTIAL | New focused behavioral coverage plus full existing suite; baseline/environment exceptions recorded separately |
| W Real E2E | PARTIAL | COMPLETE | Three actual local synthetic projects execute code and verify produced artifacts |

The shortest critical path was planner-to-hook binding, persistence, sequential handoff, explicit result validation, bounded repair/re-selection and safe checkpoint continuation. No new framework or database was needed.

## Local usage

Use the existing entry point from the repository root:

```powershell
python -B scripts/nexus.py core-plan "<bounded task>" --project "<project>" --catalog "<catalog.json>" --task-dir "<new task directory>"
python -B scripts/nexus.py core-run "<task directory>" --approve "<approval_sha256 from core-plan>"
python -B scripts/nexus.py core-status "<task directory>"
python -B scripts/nexus.py core-cancel "<task directory>"
```

Preparation does not execute a hook. Review the full `task.json` payload, original catalog and every bound instruction/script/dependency before approval. The digest is an explicit opt-in and a change identifier, not a cryptographic proof of human identity. Local checksums detect corruption; they do not protect against a hostile same-user writer. Do not put a task directory under an untrusted or shared writable location.

`core-run --max-steps 1` pauses after one completed/verified contribution. Running again with the same approval resumes remaining steps and rechecks completed artifact hashes. Budgets and expiry do not reset on resume. If a process was interrupted between persisted intent and final checkpoint, Core refuses automatic replay. Inspect effects and create a separately reviewed task if needed; there is no automatic stale-lock deletion, rollback or ambiguous-effect retry.

## Catalog and hook contract

`catalog.json` has schema `nexus.core.catalog.v1` and 1–32 `skills`. Each entry declares:

- `skill`: relative path to a real `SKILL.md` under the catalog root.
- `bindings`: SHA-256 values for `SKILL.md`, command/verifier/repair scripts, and all owner-reviewed local dependencies. This is the operator's declaration; Python stdlib/interpreter remain part of the unqualified local TCB.
- `applicability`: supported semantic domains/task kinds using the existing V2 model. Core builds a catalog-local trusted applicability record; it does not edit the frozen global registry.
- `authority`: exactly `owner_local` for supported effects; missing or different authority blocks execution.
- `retry_safe`: true only when repeating the failed fixed hook/repair is acceptable under its reviewed contract. Ordinary failure does not itself prove that no effects occurred.

Skill frontmatter supplies `hub_command`, `hub_validate`, optional `hub_repair`, and optional `hub_after`. Hooks use arrays such as `["{python}", "hook.py", "analyze"]`. Only a bound Python script is supported: no shell, executable search, command synthesis or arbitrary arguments from task text. An unresolved dependency or cycle is refused. Dependencies only order the already-selected resources; they do not install or select extra tools implicitly.

Core launches Python with `-I -X utf8 -B`, a fresh minimal environment, explicit project cwd, task-local TEMP/TMP, fixed stdin/stdout/stderr and `close_fds=True`. These are ordinary local process controls, **not LPAC/Host isolation evidence**. UTF-8 mode is explicit because Windows isolated Python ignores encoding environment variables.

Stdin JSON (`nexus.core.input.v1`) contains task/project/task ID, attempt number, previous completed results in `inputs`, and, for verification/repair, the current result/failure. Bound input size is 256 KiB. Successful execution stdout must be one JSON object:

```json
{"status":"ok","data":{"useful":"structured output"},"artifacts":["relative-output.json"]}
```

The separate verifier receives that result and must return `{"status":"ok","verified":true}` after observing actual outputs. Core independently checks artifact paths, nonempty size and SHA-256; the verifier must not alter them. Artifacts from completed steps are immutable checkpoints. Verifier quality remains the operator's responsibility; a trivial verifier is not meaningful task validation.

Failure may return `{"status":"error","failure_kind":"implementation_defect","retryable":true}`. Only retry-safe entries can repeat; an optional bound repair hook runs first. A planning failure (`wrong_resource`, `missing_capability`, `bad_plan`) can trigger one re-selection only before any completed step and with explicit `no_effect:true` from the trusted hook. It stays within the same approved catalog and rejects unsupported authority. Boundary results stop, never supply authority. Raw malformed stdout and stderr are not persisted. Duplicate fields, nonfinite JSON values and malformed results are rejected.

## Bounds, effects and recovery

Defaults: 12 dispatches, 120 seconds from preparation, 20 seconds per dispatch, two attempts per step, one re-selection, 64 KiB combined output per hook, 1 MiB per artifact. Alpha ceilings cap configurable values. Verification and repair consume dispatches too. Commands are charged and intent is fsynced **before** launch; interrupted charges are never refunded. Persistent UTC expiry and in-run monotonic deadline checks prevent ordinary resume-based renewal; clock reversal stops the task. This is not a hostile-clock/all-fault budget proof or provider hard financial cap.

Cancellation/deadline termination applies to the direct hook process. Reviewed hooks must not launch detached children, arbitrary unbounded work or external effects. Core cannot prove cessation of escaped descendants, cancel remote work, settle provider cost or roll back partial local writes. Timeout/output overflow/interrupted intent is AMBIGUOUS; operator cancellation records possible partial effects. OS run locks prevent concurrent Core runners for the same task and release on process death.

Local state (`task.json`) is versioned JSON: task ID, plan, loaded-instruction evidence, steps/results, attempts, completed steps, artifacts, commands used, blockers, ordered events, in-flight intent and final receipt. It is replace-atomically written with a canonical payload checksum. `read_task` is the current local read interface; a future DB adapter must preserve the same intent-before-dispatch, concurrency and unknown-effect rules rather than becoming a mandatory dependency.

## Acceptance and safe demonstrations

Required core acceptance: real plan/selection/loading, multiple sequential hooks, output handoff, observed failure and bounded repair/replan, verified completion, persistent useful checkpoints, no blind replay, explicit approval and hard-boundary handling. Unit tests include cancellation, timeout, malformed output, verifier rejection, integrity drift, budget exhaustion, concurrency and interrupted intents. Unit fault injection is not Host qualification.

Create a **new** directory containing only synthetic fixtures:

```powershell
python -B scripts/core_local_demo.py "<new demo directory>" --run
```

`--run` explicitly approves only these reviewed synthetic examples. Without it the command prepares plans only. A analyzes local notes and produces `analysis.json`; B runs two actual regression assertions against a faulty addition module, repairs the fixed defect, reruns and produces `test-results.json`; C selects research and architecture-review Skills, passes verified data between them and produces `review.md`. These examples operate real files/processes; no mocks stand in for execution. No network, credential, VM or provider effect is used.

## Deferred hardening and unchanged boundaries

Route D, Root R, SD01 backend exclusion, production Positive Host Binding, U02 independent fence, G01–G06, Trusted UTC/N07 and hostile-host guarantees remain preserved/deferred. No historical evidence, counter, UNKNOWN or violation is changed. The three existing untracked custody-domain proposals remain untouched. A0–A6 and accepted production P/HQ rules are not amended. This opt-in internal alpha does not claim any production G2 acceptance, HQ PASS or Positive Host Binding. **Production G2 = HOLD; Positive Host Binding = ABSENT.**

No new provider/MCP execution surface, network service, credential, Windows account/service, VM operation, installation or system security change is part of this implementation. Core fixtures execute only approved local code; unrestricted model reasoning/tool generation and production provider costs are unsupported.
