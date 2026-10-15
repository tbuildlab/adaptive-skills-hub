# G6 local-retention one-shot v1: retained QUARANTINE / RETIRED

The separately requested verification-only signature command passed before any
candidate materialization. Exact subject/configuration/review, fixed window,
ZIP/model/member integrity and current Host/runner pins were checked inertly.
The existing guard independently reverified immediately before dispatch/resume.
Authenticated payload SHA256:
`0635da1837e8793f314080cbdc803fa78556be2a93a78a3d64ae68d239a9f9f5`.

Exactly one fresh `output/g6-local-retention-once-v1` invocation occurred. Its
exclusive reservation, original disposition, task, raw output and quarantine
receipt remain retained. No v1/v2/v3 native attempt was replayed/reset or reused.
No raw task, model output or report content was printed to the conversation or
review messages; local predicates returned closed booleans and hashes only.

## Observed failure and independent review

- Return code 0; elapsed **28.453 seconds**; stdout **146 bytes**, stderr **2,153
  bytes**, aggregate **2,299 bytes**. Zero active Job processes after termination.
- Earliest failure: **UNVERIFIED_PRIVATE_RESULT**. Model output has an opening CSV
  fence and field whitespace, contrary to the exact signed CSV protocol. Local
  diagnostic parsing finds the expected header and all three rows/fields. This is
  **FORMAT_NONCONFORMANT_WITH_SEMANTIC_CONTENT_MATCH**, never an accepted result.
  No CSV artifact was created and no parser repair was applied to this attempt.
- Independent secondary failure: **HOST_CHANGED**, `codex` **link_count only**.
  Volume, file ID, size and last-write comparisons did not change. Current Host
  and runner hashes still match. The reason for the link-count change is unknown;
  it is not evidence of executable-byte modification or a justified benign waiver.
- Original guard result remains **QUARANTINE / BINDING_OR_HOST_FAILURE**, retaining
  pre-failure reason UNVERIFIED_PRIVATE_RESULT. Receipt remains QUARANTINE.
- Authorization and attempt are permanently **RETIRED**; no automatic retry,
  replacement, restoration or post-hoc promotion is allowed.

Independent read-only reviewer `/root/g6_binding_independent_review` confirms
**HOLD** and both findings. The reviewer performed no authentication, candidate or
model execution, tests, replay, edits or raw-content printing. A zero exit code,
semantic match or end delimiter cannot overrule the signed output/Host boundary.

## Exact retained evidence

Closed record: `research/nexus-g6-local-retention-once-result-v1.json`.
Originals: `output/g6-local-retention-once-v1`; additional closed observations:
`output/g6-local-retention-execution-audit-v1`. Raw output stays local.

Stdout SHA256:
`348c66707ae3425fdfb4526fc0d062e736024c4ec2a2fb304c4183465c62d540`.
Stderr SHA256:
`10b522314ba8a4c6dc5ddeda421446f543379c7d89307c78cbe9660cf0465a13`.

All 42 earlier native-attempt files were checked unchanged before dispatch;
post-run preservation is rechecked at checkpoint. No source/test bytes changed
under the signed decision. Prior 56 focused / 161 affected and 18+4 public
readiness results remain their original evidence, not successful model completion.
No new full repository sweep is claimed for this evidence-only checkpoint.

## Next boundary

The five-field Host stability check remains intact. Any future reuse repair must
first establish bounded handle-bound PUBLIC lifecycle evidence; documentation or
matching executable hashes alone cannot waive a link-count failure. A narrow
prompt correction may address generation format, keeping exact CSV acceptance.
Both corrections require fresh public qualification/regression and independent
review before a different exact signing package. No second native attempt or
signing package is created by this result record.

Official [Windows sandbox guidance](https://learn.chatgpt.com/docs/windows/windows-sandbox)
and [CLI reference](https://learn.chatgpt.com/docs/cli/reference) were inspected
for existing MXC/profile reuse. They do not establish why this observed Host link
count changed, nor qualify a replacement path. No new sandbox or generic security
framework follows from this observation.

G2/G3/G4 remain frozen, N01 remains optional research HOLD, and G6 remains
**INCOMPLETE / HOLD**. Useful local-only completion and subsequent substitution,
value, final review/regression and Owner release acceptance remain outstanding.
REAL_ADMISSION=NO. No cloud resource, paid service or production release occurred.
