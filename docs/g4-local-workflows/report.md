# Host Loop v1: evidence-backed completion review

Observation date: 2026-10-14. Scope: one real read-only Git repository maintenance run and its retained regression evidence. This is a local artifact review, not production-security qualification.

## Verified observations

| Claim | Observed value | Source field |
|---|---:|---|
| Related regression tests | 228 | regression.total |
| Passed / historical skipped / failed / errors | 227 / 1 / 0 / 0 | regression.pass / skip / fail / error |
| Logical Host batches used / ceiling | 4 / 8 | execution.commands_used / max_commands |
| Budget utilization | 50% | 100 × commands_used ÷ max_commands |
| Native read-only Git processes | 12 | execution.git_processes |
| Source files preserved in inspected repository | 519 | execution.source_files_preserved |
| Findings in the two declared files | 0 | execution.scoped_whitespace_findings |

## Reconciliation and calculations

227 PASS + 1 historical SKIP + 0 FAIL + 0 ERROR = 228 discovered tests. The skip is not counted as PASS. 4 ÷ 8 × 100 = 50% budget utilization; 4 Host batches remained at completion. Twelve Git processes are not twelve budget units. Budget availability expired on the original task deadline; this report does not restore authority or renew it.

## Evidence and limitations

The retained receipt records status `completed`, verification `passed`, exact inspected HEAD, selected Skill digests and report digests. The baseline/source/index preservation proof covers the actual run. Two preparation-only refusals had zero Host actions; they remain retained and are not counted as successful executions. This report neither repeats that run nor upgrades a fixture.

The two declared files were README.md and docs/nexus-core-alpha2-local-use-v1.md. Untracked-file discovery, secret scanning of the inspected repository, whole-repository cleanliness, production authority, remote effects and financial savings were not qualified. One Windows symlink test was skipped for unavailable privilege. Same-user evidence has no independent production authenticity guarantee. The evidence supports completion of this declared workflow, not universal execution capability.

## Sources

- [Retained source summary](sources/host-loop-summary.json): every table claim maps to a named field. Its original_sha256 object pins the retained regression, E2E proof and receipt; original files remain available in the documented local evidence locations.
- Exact originals: [regression](sources/retained-regression.json), [E2E preservation proof](sources/retained-e2e-proof.json), and [receipt](sources/retained-receipt.json). These are unchanged local evidence bytes, not current authority.
- [Owner task scope](sources/owner-task-scope.json): this new local report's purpose and scope only; not a production grant.
- [Host Loop usage contract](../nexus-core-host-execution-loop-v1.md): batch accounting, fresh readback, resume bounds and same-user limitations.

G2 remains completed/frozen in its accepted managed scope. G3/N01 remains HOLD. REAL_ADMISSION=NO. No G6 final qualification or release decision is made.
