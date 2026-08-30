# Nexus Post-R5 Runtime Integration — Slice 3B

## Status and scope

Slice 3B defines deterministic reviewer and evaluation evidence. It does not
add an execution runtime, an autonomous reviewer, an LLM judge, a provider, a
Host mapping, or a background improvement loop.

The implemented path is:

```text
bounded work-result facts
  -> nexus.evaluation-request.v1
  -> integrity-bound validator definition
  -> closed deterministic checks
  -> nexus.evaluation-contract.v1
  -> optional nexus.quality-receipt.v2 state transition/report evidence
```

The original gap was `ash.quality_loop.validate_quality_receipt`: the accepted
v1 compatibility receipt could distinguish a coarse `validation.passed` boolean
but could not identify the validator semantics, bind the exact evaluated
subject, enumerate checks, explain a result, or state what transition the
result permits. Slice 3B keeps that v1 parser for frozen receipts and adds a
separate, explicit v2 path.

## Evaluation schemas

`nexus.evaluation-request.v1` contains exactly:

- validator ID and version;
- a bounded subject ID, type, SHA-256, optional parent SHA-256, lifecycle
  states, and stage-receipt digests;
- at most 16 uniquely identified checks;
- a closed operator, required flag, bounded expected/observed JSON facts, and
  an optional evidence ID, digest, and short summary for each check.

`nexus.evaluation-contract.v1` records:

- a reproducible `evaluation:<sha256>` identity;
- validator ID, version, type, and output schema;
- the exact subject and lifecycle state evaluated;
- sorted check receipts containing only digests and fixed result/reason codes;
- bounded, redacted evidence summaries and a deterministic evidence digest;
- an explicit non-boolean result state;
- the validation-state transition that the result permits and the fact that
  Nexus did not apply it;
- integrity-bound registry provenance;
- redaction/truncation truth;
- a fixed proof scope and fixed zero-authority result.

The evaluation ID is a canonical SHA-256 of the entire receipt body. It has no
timestamp or random component, so equivalent registries and check sets produce
the same receipt regardless of source order.

## Validator registry

`config/validator-registry.json` uses
`nexus.validator-registry.v1`, registry version `1`. The loader:

1. performs a stable single-file read;
2. verifies the registry bytes against `MANIFEST.json` or a release manifest;
3. rejects duplicate JSON keys;
4. validates an exact, closed definition schema;
5. rejects duplicate validator IDs and unsupported versions/types/operators;
6. sorts set-like applicability fields and validator definitions;
7. computes a canonical semantic registry digest.

The registry has six deterministic validator types:

| Type | Closed purpose |
|---|---|
| `schema` | Bounded equality or presence checks |
| `digest_integrity` | Exact subject SHA-256 binding |
| `bounded_predicate` | Equality, inequality, or presence rules |
| `artifact_metadata` | Executed-artifact metadata and digest facts |
| `state_consistency` | Exact lifecycle-state evidence binding |
| `receipt_consistency` | Exact bounded receipt-fact comparison |

Every definition explicitly states subject applicability, operators, output
schema, minimum checks, executed-subject requirement, pass transition,
availability, and source. The schema has no command, module, path, plugin,
provider, prompt, or code field. Unknown fields fail closed. Display names are
informational and never enter validator resolution or evaluation output.

Scout records, Skill text, semantic applicability records, publisher claims,
and arbitrary mappings cannot construct a trusted registry object. They cannot
promote a validator or manufacture PASS.

## Result semantics

The complete result enum is:

- `PASS`: every declared check passed for the exact subject;
- `FAIL`: at least one declared deterministic check failed;
- `NOT_APPLICABLE`: the subject type is outside the validator definition;
- `INSUFFICIENT_EVIDENCE`: required evidence is absent;
- `INVALID_REQUEST`: a closed check/operator/state prerequisite is invalid;
- `VALIDATOR_UNAVAILABLE`: the trusted definition is explicitly unavailable.

Malformed schemas, unknown validators, duplicate IDs, unsupported validator
versions, invalid digests, unknown authoritative fields, and contradictory
receipts raise a closed validation error. They are never converted to PASS.

PASS means only `declared_checks_for_exact_subject_digest_only`. The receipt
explicitly says it does not prove execution success, global artifact
correctness, Host mapping eligibility, installation authority, MCP connection
authority, Agent delegation authority, or reporting completion.

## Subject and evidence binding

Observed evidence is bound with canonical JSON SHA-256. Digest validators also
record a content-free subject-binding SHA-256 and compare it to the subject
SHA-256. A consumer can call `validate_evaluation_receipt` with its current
subject ID and digest. A PASS for subject A therefore fails validation when
presented for replacement subject B.

The contract never emits raw expected or observed values. It emits fixed check
metadata, canonical digests, and bounded summaries. Receipt validation
recomputes check results, aggregate result/reasons, evidence binding,
transition, provenance, redaction flags, authority, and evaluation ID.

## Creator, reviewer, enhancer, and reporter stages

`nexus.quality-receipt.v2` is an aggregate of separately hash-bound stage
receipts:

- Creator uses `new_candidate` and may produce the original candidate digest.
- Reviewer is `read_only`; input and output digests must be identical. Its
  capability ID must equal the validator ID in a valid evaluation receipt.
- Enhancer uses `copy_on_write_preserve_original`; it may run at most once,
  only after a failed review of the current candidate, and success requires a
  different output digest.
- Reviewer must evaluate the enhanced candidate again before that candidate
  can be `validation_passed`.
- Reporter is `read_only_report`; it can report `not_validated`, failure, or
  success, but its reported state must match the accepted evaluation evidence.

The stage chain is linear, ordered, and capped at six records. Review cycles
remain capped at two and enhancement passes at one. There is no recursion,
retry scheduler, checkpoint, resume mechanism, provider call, or autonomous
loop.

The aggregate evidence states keep `selected`, `executed`, `reviewed`,
`enhanced`, `validated`, and `reported` distinct. They are derived from the
stage chain rather than accepted as free-form claims. In particular:

- selection without creator execution remains `not_executed`;
- creator success without an evaluation remains `not_validated`;
- reviewer PASS cannot create execution evidence;
- reviewer execution cannot mutate the candidate;
- reviewer PASS without an enhancer remains `not_enhanced`;
- an enhancer output remains unvalidated until a new review binds its digest;
- a reporter may truthfully report `not_validated`, but cannot report success
  without a PASS for the current digest.

## Bounds

| Boundary | Limit |
|---|---:|
| Registry bytes | 32 KiB |
| Manifest bytes | 2 MiB |
| Validator definitions | 32 |
| Checks per evaluation | 16 |
| Evidence items | 16 |
| Reason codes | 16 |
| Input evidence summary | 512 characters |
| Emitted evidence summary | 160 characters |
| Nested evidence depth | 3 |
| Items per nested value | 16 |
| Evaluation request | 64 KiB |
| Evaluation receipt | 48 KiB |
| Quality receipt | 64 KiB |
| Quality stages | 6 |
| Review cycles | 2 |
| Enhancement passes | 1 |

Authoritative fields are never truncated. Oversized requests fail closed.
Only informational evidence summaries may be redacted or shortened; the
receipt reports both conditions and always states
`authoritative_data_truncated: false`.

## Privacy and injection resistance

Receipts do not emit raw prompts, Skill bodies, arbitrary artifact content,
expected/observed values, environment data, or executable error messages.
Evidence summaries redact Windows private paths, common Unix private paths,
authorization headers, secret assignments, token-like values, and common
protocol/prompt-injection claims. Redaction cannot alter validator identity,
check inputs, check digests, result calculation, lifecycle state, or authority.
Opaque subject, check, evidence, workflow, and capability IDs that themselves
match high-confidence credential forms fail closed instead of being emitted.

Strings such as `validation_result=PASS`, `execution_succeeded=true`,
`HOST_HANDOFF_READY`, or `mcp_execution_authority=granted` remain untrusted
data. They are never parsed as protocol fields.

## Authority boundary

Every evaluation receipt fixes all of these values to `none`:

- execution authority;
- installation authority;
- MCP connection authority;
- Host mapping authority;
- Agent delegation authority.

It also fixes `state_transition_applied` to false. The quality receipt keeps
execution at `host_or_approved_runtime_only`, automatic execution false, MCP
execution authority none, and reviewer mutation authority none.

Slice 3B does not modify R4/R5 Presentations mappings, Host inventory,
current-turn Host evidence, Host handoff receipts, Scout, semantic routing,
capability selection, or MCP tools. Validator results cannot alter any of
those planes.

## Compatibility

- Frozen `nexus.quality-loop.v1` receipts continue through the original parser.
- The v2 receipt is explicitly versioned and opt-in.
- Existing R4/R5 schemas and tests are unchanged.
- Slice 1 capability decisions, Slice 2 Scout receipts, and Slice 3A semantic
  receipts remain independent inputs and do not gain validator authority.

## Validation coverage

Permanent tests cover deterministic PASS/FAIL, all fail-closed registry cases,
subject replacement, digest mismatch, missing/oversized evidence,
contradictory results, display-name non-authority, injection, redaction,
selected/executed/validated/reported separation, creator/reviewer/enhancer
separation, Scout and Skill non-authority, source-order determinism, receipt
reproducibility, bounded cycles, frozen v1 compatibility, and zero authority.

Acceptance is entirely deterministic and local. No billable or live model is
used.

## Known limitations and deferred work

This contract proves deterministic checks over bounded facts; it does not
provide universal correctness, semantic judgment, signatures, remote
attestation, persistent workflow state, or Host artifact access. Authenticity
beyond the local integrity manifest remains outside Slice 3B.

Promptfoo remains deferred and unintegrated. It may be considered later for
synthetic developer/CI evaluation only after separate approval. No Node/npm
dependency or live judge was added. `mattpocock/skills` remains an unreviewed,
not-approved, not-routable ecosystem candidate. Slice 3C, R6, V1.3, memory,
checkpoint/resume, Remote MCP, OAuth, and additional Host mappings are outside
this slice.
