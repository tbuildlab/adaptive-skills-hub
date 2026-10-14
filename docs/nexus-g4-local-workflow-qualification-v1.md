# G4 local Website and Source-backed Report qualification v1

Date: 2026-10-14. Scope: two explicit trusted local Host workflows. This is not
production admission, a G6 qualification, a release or a milestone freeze.

## Preserved baseline and exact remaining gaps

Host Execution Loop v1 was preserved unchanged at clean product-enhancement
checkpoint `d9aa1dc3f62a6a7b7a45c7290bc51d3ca7d88c1a`, branch
`nexus-core-host-loop-v1-checkpoint`. It is post-G2, not a new milestone. No tag
was created. Work continues on `nexus-core-g4-domain-qualification` in a separate
worktree; the original production checkout remains at `a7b2ec9` with its existing
files intact. G2's accepted managed-v3 completion and all old acceptance records
are unchanged. G3/N01 remains HOLD / OPTIONAL_HIGH_ASSURANCE_RESEARCH.

The accepted [Roadmap G4](nexus-roadmap-v2.md#g4--evidence-led-domain-workflows)
requires real Website and Source-backed Report completion, inspectable evidence,
small provenance-bearing scoped memory, shared-consumer/unknown-area records and
poisoning/impact/reduction negatives. The [preparation checkpoint](nexus-g4-preparation-checkpoint-v1.md)
had only structural examples and denial seams. It explicitly withheld real domain
qualification. It remains historical and is not rewritten.

| Original gap | Smallest delivered evidence |
| --- | --- |
| Website real completion | A usable two-page local Nexus Core guide/catalogue, based on existing accepted usage contracts; shared filtering, keyboard interaction, disclosure and source links |
| Website acceptance coverage | Real existing Chrome execution: interaction, both shared consumers, scoped accessibility, empty/no-result/hostile-text/length boundaries, responsive rendering and artifact readback; existing Core HTML checker reused |
| Report real completion | A factual HTML/Markdown review of the already completed real Host Loop run and retained regression; no replay or fixture promotion |
| Report acceptance coverage | Nine source-mapped rows; independently recomputed totals, utilization and remaining batches; limitations/unknowns, rendered output and local source links |
| Scoped memory and provenance | Two finite task-scoped entries, pinned to the actual current Owner task context and exact file bytes; advisory only, with no grant/dispatch authority |
| Shared impact and unknown areas | Website shared JS/CSS consumers: guide and catalogue; report source/metric/uncertainty consumers: HTML and Markdown; included and excluded-unexamined scope recorded explicitly |
| Actual evidence versus structural PASS | New read-only packet verifier reopens files and original measurements before reusing unchanged G4 contracts; their result remains PASS_STRUCTURAL_ONLY/NON_AUTHORITATIVE |
| Independent negative oracles | Separate tests plus isolated mutations of the exact real packets; poisoning, omitted/shared consumers, in-scope unknowns, hidden failure, evidence loss and changed bytes must deny |

## Artifacts and reproducible local readback

- [Website guide](g4-local-workflows/index.html) and [catalogue](g4-local-workflows/workflows.html).
- [Report HTML](g4-local-workflows/report.html) and [full Markdown](g4-local-workflows/report.md).
- [Actual retained input summary](g4-local-workflows/sources/host-loop-summary.json)
  pins original regression, E2E proof and receipt hashes. This is a derived factual
  projection of real records, not a new provider execution or a credential copy.
  Exact non-secret originals accompany it as `sources/retained-{regression,e2e-proof,receipt}.json`.
  Its ContextManifest marks the summary DERIVED and retains original membership;
  typed source_of relationships record the other contributing originals.
- Per-pack memory, source table, context, decision, impact, relationship, pack,
  observation and independent expected facts are in
  `research/nexus-g4-local-{website,source_backed_report}-packet-v1.json`.
- Original measurements are in the corresponding `*-browser-evidence-v1.json`
  and `nexus-g4-local-core-html-evidence-v1.json`. Readback receipts and exact-packet
  negatives are retained in `research/nexus-g4-local-readback-receipts-v1.json`
  and `research/nexus-g4-local-adversarial-evidence-v1.json`.

```text
python scripts/verify_g4_local_evidence.py . research/nexus-g4-local-website-packet-v1.json
python scripts/verify_g4_local_evidence.py . research/nexus-g4-local-source_backed_report-packet-v1.json
python -m unittest tests.test_g4_local_qualification tests.test_g4_contracts tests.test_g4_host_adapter -q
node scripts/qualify_g4_local_browser.cjs <existing-Host-playwright-module> <existing-browser-executable> <fresh-external-output-directory>
```

Packets bind exact local source/artifact bytes and the original observation time.
Rechecking historical evidence never renews memory validity, task budgets or
authority. Checkout line-ending changes or other byte changes require a newly
bound observation; do not silently rewrite packet hashes to make readback pass.
No packet authorizes execution. This verifier trusts the same-user Host origin
for measurements and the explicit task context; hashes cannot authenticate an
independent writer. An attacker able to rewrite the entire packet and every
underlying measurement is not resisted by this local evidence tool.

## Scope and independent validation

The Website workflow uses existing Host file/process/browser capabilities, the
currently available frontend-ui-engineering Skill and the existing Core HTML
checker. The bundled Playwright and already installed Chrome are Host validation
facilities, not new Nexus components or dependencies. No browser/framework code
is imported into Nexus. Validation used a fresh browser context and an ephemeral
loopback server that served only declared files; page requests outside its exact
origin were denied. No existing user browser profile or credentials were read.

All four declared viewport widths (320, 768, 1024 and 1440) were exercised. Keyboard
checks included skip-link focus, clear-filter activation/focus and native details;
browser semantics and measured normal-text contrast were inspected. Full screen
reader certification, axe scanning, other browser engines, remote deployment and
backend/authentication are explicitly unexamined/outside this local scope, not
PASS. No universal WCAG or hostile-Host claim is made.

Visual inspection found split numeric cells in the initial narrow report. Only
the named, keyboard-focusable table overflow region was corrected. The original
browser records and the subsequent premature keyboard-scroll assertion failure
remain in ignored output. The harness now waits for the observed scroll result
rather than asserting before browser layout/scroll processing. Final numeric
cells, scroll region, source links and artifact bytes were rechecked.

Within-scope unknown impact is still rejected by the original contract. Its
`unexamined=[]` means all declared required consumers were inspected; the packet's
explicit `excluded_unexamined` list records non-target areas. Those areas do not
silently expand the scope or disappear from the receipt. A negative test that
adds a required unexamined consumer denies qualification.

The Report checks use independent arithmetic and browser readback of the actual
source projection. 227 PASS + 1 historical SKIP = 228 tests; 4/8 Host batches =
50% utilization. Twelve Git processes are a different unit. Four batches remained
at the old completion time; no expired task was resumed. No financial savings,
new comparative-value experiment or independent production review is claimed.

## Preserved production boundary and finite change surface

`ash/g4_contracts.py`, `ash/g4_host_adapter.py`, planner/Core/Host Loop source,
historical tests, G2/G3/G4/G6 acceptance documents and production research are
unchanged. The production adapter still returns DENY. No structural fixture is
used to authorize these Host operations. Local actions consume this explicit
Owner task through existing Host capabilities; post-execution evidence creates
no dispatch grant and is not fed into a production admission path.

New code is limited to `scripts/verify_g4_local_evidence.py`, its independent
tests and `scripts/qualify_g4_local_browser.cjs`, the fixed two-workflow Host
qualification harness. The harness receives existing trusted Host facility paths
and refuses existing output directories; it never rewrites accepted measurements.
It is not imported or dispatched by Nexus. The read-only verifier reads declared
files, checks digests/memory/measurement coverage, and
composes the five existing G4 record contracts. It has no tool dispatcher,
planner, retry engine, persistence service, registry, authentication, custody or
ledger recovery. HTML/JS remain workflow artifacts outside planner core.

The Website and Report are qualified only for the declared trusted local Host
scope. Global production qualification, independent approval-origin/security
review, Owner milestone acceptance and any final G4 freeze/tag remain distinct.
The existing G4 preparation label is not retroactively edited. No new external
component was adopted; original G3 external-adoption requirements were not
triggered or waived. REAL_ADMISSION remains NO; G6 final work was not started.

Final regression and source-integrity results are retained in the accompanying
qualification result record and ignored local command logs. No failed or skipped
check is counted as PASS, and reruns are not added to unique test totals.

The full static-source run initially lacked Git metadata required by two unchanged
historical offline builder tests. An external test-only Git directory was added,
pointing at the actual local baseline commit, without rewriting source or adding
production bindings. Other historical mock tests encountered expired fixed
deadlines: real code correctly denied them. Seven affected cases were rechecked
using the already accepted SDK historical-clock fixture helper, applied per case,
and all seven passed. Real deadlines/reviews and product source/tests were not
changed. An initial follow-up applied the helper at suite setup rather than each
case; its cleanup-related failures are also retained. The final result distinguishes
first-run environment failures from recovered unique-case coverage.

Two other retention negatives mixed the fake S3 retention clock with a historical
reader clock; the same existing helper aligned those fixture clocks while keeping
expired retention rejected. Two simulated runtime probes used the expired fixed
deadline, and three runtime-selection cases lacked the existing sibling
`adaptive-skills-library` seed file. Restoring that exact historical file for
tests did not execute it or adopt a new G4 component. All 14 affected unique cases
passed their isolated rechecks.

Final evidence: [qualification result](../research/nexus-g4-local-qualification-result-v1.json).
Affected regression: 276 PASS / one historical SKIP. Full discovery: 1,529 unique
cases; first sweep 1,511 PASS / four historical SKIP / seven FAIL / seven ERROR.
After the 14 classified environment rechecks: 1,525 unique PASS / four SKIP / zero
unresolved FAIL/ERROR. This is complete coverage with environment retests, not a
claim of one green monolithic run. Fourteen new tests are included, not added twice.
