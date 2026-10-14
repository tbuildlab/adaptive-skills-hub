# Nexus G4 final acceptance and freeze v1

Date: 2026-10-14. Decision: **G4 COMPLETED / FROZEN** for the original two-pack,
trusted local Host scope. No production admission or G6 acceptance is implied.

## Standard, subject and Owner authorization

The sole milestone standard is frozen Roadmap V2, tag `nexus-roadmap-v2-final`,
commit `f92b96ea01b8e32dac8bc1d51819bf0c58d55659`,
`docs/nexus-roadmap-v2.md` SHA-256
`e803515ea2342c13b548601e01ba015e6827aa5d6a55c98562533d1ef77d8ba8`.
The current roadmap bytes were compared with that frozen Git blob.

Accepted implementation/evidence checkpoint:
`52d77560fc99d45936e3b253f6131449919bd088`.
Branch: `nexus-core-g4-domain-qualification`.
Final annotated tag: `nexus-v2-g4-final`. Its peeled commit identifies this
documentation-only acceptance commit; its annotation binds the full commit,
MANIFEST and reproducible package digests. A commit cannot include its own hash.

The Owner's current instruction names the exact qualified checkpoint, directs a
final acceptance audit and freeze, and explicitly authorizes acceptance, push and
an annotated final tag if all original mandatory criteria are proven. This is
conditional, scoped Owner acceptance, applied only after this audit passed; it is
not inferred from test PASS. It creates no runtime or production authority.
The earlier qualification record's `owner_milestone_acceptance=NOT_CLAIMED`
remains unchanged as evidence of the stage before this acceptance instruction.

## Original acceptance criteria versus retained evidence

Paths below are repository-relative. All named evidence existed at the accepted
development checkpoint; the audit adds no workflow behavior or test criteria.

| Frozen requirement | Exact retained evidence | Audit result |
| --- | --- | --- |
| G4 field 10: Website completes a real bounded workflow with inspectable evidence | `docs/g4-local-workflows/index.html`, `workflows.html`, shared `assets/catalog.js` / `site.css`; `research/nexus-g4-local-website-packet-v1.json`; `research/nexus-g4-local-website-browser-evidence-v1.json` | SATISFIED. Actual existing Chrome interactions, keyboard/boundary checks, both consumers, four viewport widths and artifact readback; not fixture execution |
| G4 field 10: Source-backed Report completes a real bounded workflow with inspectable evidence | `docs/g4-local-workflows/report.md`, `report.html`, `sources/host-loop-summary.json`, exact `sources/retained-{regression,e2e-proof,receipt}.json`; `research/nexus-g4-local-source_backed_report-{packet,browser-evidence}-v1.json` | SATISFIED. Nine source-mapped rows, recomputed arithmetic, browser rendering and original-source readback; analysis of a real retained run, without replay |
| G4 field 10: relevant shared consumers and unexamined areas are recorded | Both packets' `records.impact` and `scope.excluded_unexamined`; `research/nexus-g4-local-readback-receipts-v1.json` | SATISFIED. Guide/catalogue share JS/CSS; HTML/Markdown report share source, metrics and uncertainty contracts. Empty in-scope `unexamined` does not hide the separately retained excluded areas |
| G4 field 10: small, provenance-bearing, permission-scoped memory | `research/nexus-g4-local-scoped-memory-v1.json`; the two `sources/*-task-memory.json` inputs and corresponding packet decisions/context/relations | SATISFIED. Two finite task/project-scoped advisory entries; exact source bytes, authorized task constraint source, validity, retention, recipients and original/derived provenance; no dispatch grant |
| G4 field 10: changing a pack requires no planner-core domain logic | `scripts/verify_g4_local_evidence.py`, `scripts/qualify_g4_local_browser.cjs`, `tests/test_g4_local_qualification.py`; baseline-to-development diff and `output/g4-local/security-scope-review.json` | SATISFIED. Domain artifacts and bounded Host checks remain outside planner core. Existing G4 contracts, production adapter, planner and Host Loop are unchanged |
| G4 field 10: stop unnecessary polishing | Finite 27-file qualified development change; this acceptance adds only two records and MANIFEST entries | SATISFIED. No feature expansion or further visual polishing |
| G4 field 16: qualify both packs independently with poisoning, impact and evidence-reduction tests | Separate actual packets and browser observations; `research/nexus-g4-local-adversarial-evidence-v1.json`, eight negative cases per pack, 16/16 expected denials; independent expected-oracle tests in `tests/test_g4_local_qualification.py` | SATISFIED. Cross-project poisoning, missing consumers, in-scope unknowns, omitted observations, hidden failure, lost originals and source/artifact corruption deny independently for each pack |
| G4 field 9: all original deterministic negative categories | `tests/test_g4_contracts.py`: `test_poisoned_confirmation_proposal_dispute_and_stale`, `test_cross_namespace_disclosure_and_original_availability`, `test_reduction_loss_unresolved_forgetting_and_conflicts`, `test_supersession_requires_accessible_exact_history`, `test_relation_versions_provenance_conflicts_and_cycles`, `test_dirty_input_shared_consumers_and_unexamined_areas`, `test_pack_restrictions_and_missing_capabilities`, `test_omitted_failure_mixed_artifact_and_forged_source`; additional actual-packet tests above | SATISFIED. Unauthorized confirmation, conflicts/staleness, leakage, supersession/forgetting, reduction, forged edges/cycles, dirty substitution, shared consumers, boundary omissions and permission expansion are covered |
| G4 fields 4, 7 and 8: deterministic records and boundaries | Both packets compose the existing five G4 contracts; `ash/g4_contracts.py`; retained round-trip/schema/binding tests; read-only packet verifier reopens exact files | SATISFIED. Scope/provenance/validity, typed dependency and impact/evidence bindings remain deterministic. Reduced evidence retains accessible originals. Structural validation remains NON_AUTHORITATIVE |
| G4 fields 12 and 15: G2 foundation, conditional G3 dependency, no new authority | Preserved post-G2 Host Loop checkpoint `d9aa1dc3f62a6a7b7a45c7290bc51d3ca7d88c1a`; `research/nexus-g4-local-qualification-result-v1.json`; `tests/test_g4_host_adapter.py` | SATISFIED. Existing Host file/process/browser and installed Skill facilities only; no newly adopted external component. Task permission comes from the explicit Owner task; production adapter remains DENY |
| Website domain evidence table: interaction, shared-consumer regression, accessibility, boundaries and authorized deployment identity | Website browser evidence, existing Core HTML evidence and explicit local-only scope | SATISFIED for this bounded local workflow. No deployment was requested or performed; remote deployment identity is explicitly unexamined, not falsely qualified |
| Report domain evidence table: source-to-claim, calculations, inspection and format-appropriate rendering | Report browser evidence, retained source originals, HTML and Markdown; source-of relationships and source hash table | SATISFIED. Derived summary is labeled DERIVED, originals remain accessible; skips and uncertainty are not removed |
| Roadmap Section B freeze rule: scoped evidence, relevant regression, resolved findings, Owner acceptance and immutable commit/manifest tag | Records above; exact regression reconciliation below; `research/nexus-g4-final-acceptance-audit-v1.json`; current conditional Owner freeze instruction; annotated final tag | SATISFIED upon publication of the tag. No unresolved blocking finding is recorded in this bounded scope. Final tag identity is independently read back after push |

“Independently” in G4 field 16 is implemented as separate pack qualification and
negative expected oracles. It is not a claim of independent production security
review. The latter is explicitly G6 fields 5/10/16 and remains unperformed here.
The earlier preparation-only status is historical; this supplemental acceptance
does not rewrite that checkpoint or its withheld claims.

## Regression and integrity evidence

- New tests: **14/14 PASS**, included in all relevant totals, never counted twice.
- Affected regression: **276 PASS / 1 historical SKIP / 0 FAIL / 0 ERROR**.
- Full discovery: **1,529 unique cases**. Original sweep: **1,511 PASS /
  4 historical SKIP / 7 FAIL / 7 ERROR**. All original logs remain unchanged.
- The exact 14 original failing/error case IDs were matched to 14 successful
  isolated environment retests: existing fixture-clock helper, missing test-only
  Git metadata and existing sibling Skill seed. No source, historical test,
  real deadline, review, binding or authority was changed to pass them.
- Effective unique coverage: **1,525 PASS / 4 historical SKIP / 0 unresolved
  FAIL/ERROR**. This is not one green monolithic run. Three skips lack configured
  embedded-runtime inputs; one requires unavailable Windows symlink privilege.
- This final audit reran the unchanged G4/local/adapter suites: **49/49 PASS**,
  without adding those reruns to unique coverage. No full regression was repeated
  because this freeze changes only acceptance documentation and MANIFEST.
- Both actual packet readbacks match the retained receipts exactly: Website
  artifact `3f0ac451dc35fd9e4a5aef69080164b37cc19405c14b844d1ca3e01de2bb101f`;
  Report artifact `e1ecc3d7b375fb81f528cfc0314b1b57f16cd02d33234eb476bae991d6f2b9da`.
- Qualified development MANIFEST: **746 entries**, SHA-256
  `1e513881e87918efab6efe7aee9fe174473244332566e01ff40d1eed62cd47ac`.
  All 720 prior baseline entries and all 746 qualified entries remain unchanged;
  the freeze MANIFEST adds only the two acceptance/audit records.
- Reproducible portable source package: **260 members**, SHA-256
  `df7f3756baecf0633e6ebdf42fc53d417f72de43ffa0adf25a7a5d6de7573bf5`.
  Rebuilt twice during this audit. Local workflow docs/evidence remain in Git;
  they are excluded from the existing portable-install allowlist.

## Retained limitations and unchanged milestones

Qualification is for the declared trusted local Host, existing Chrome and four
tested widths. Full assistive-technology certification, other browser engines,
backend/authentication and remote deployment are explicitly outside that scope.
Same-user evidence integrity does not authenticate a hostile writer able to
replace every packet and observation. No production authenticity, new value
experiment, billing settlement or independent production review is claimed.
Memory/old task validity and remaining budgets are historical, not renewed.

**Outstanding original mandatory G4 criteria: NONE.** These limitations neither
become PASS claims nor introduce new historical acceptance requirements.

G2 remains accepted/completed/frozen for its managed scope. Host Loop v1 remains
a post-G2 product enhancement. G3/N01 remains **HOLD /
OPTIONAL_HIGH_ASSURANCE_RESEARCH** at its preserved production checkpoint;
no recovery, enrollment, resource, public-pin, PREAUTH or binding work occurred.
G6 remains **COMPLETE_PREPARATION_FAIL_CLOSED**; final qualification was not
started. Production adapter **DENY** and **REAL_ADMISSION=NO** are unchanged.
Stop here: this freeze authorizes no next milestone.
