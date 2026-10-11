# Nexus Historical Experience Ingestion Audit v1

Audit date: 2026-10-11. Baseline: G4 preparation commit
`befb40f2845c22f77419d19b0bfbb1033e3ee667`, branch `nexus-v2-g4-development`.
Scope: bounded project knowledge and evidence. No application, Host runtime,
G4 architecture, admission, external provider or paid infrastructure change.

## Project conclusions

```text
MERANTI_STATUS = INGESTED_NOW (previously PARTIAL)
NORTHSTAR_STATUS = CONFIRMED_INGESTED
DEMO3_IDENTITY = APEX_AIRCARE (explicit primary-source identity)
DEMO3_STATUS = CONFIRMED_INGESTED
ATELIER_NOMA_STATUS = INGESTED_NOW (bounded local/dirty-checkpoint evidence)
APEX_HOME_SERVICES_STATUS = NOT_FOUND (implementation/rename unproved)
HISTORICAL_MEMORY_STATUS = COMPLETE_BOUNDED_ADVISORY_CHECKPOINT
EXISTING_LESSON_COUNT = 52 source items; 31 unique reusable meanings
NEW_LESSON_COUNT = 10 unique reusable meanings
DEDUPLICATED_COUNT = 27 duplicate/partial source items merged by reference
SUPERSEDED_COUNT = 1 current-source-state summary; 0 reusable lessons erased
TOTAL_REUSABLE_LESSONS = 41
UNRESOLVED_SOURCE_GAPS = PRESERVED; see limitations below
G4_ARCHITECTURE_CHANGED = NO
REAL_ADMISSION_CHANGED = NO
```

Counts are explicit: 26 Northstar K records + 20 Apex L records + six Meranti
Roadmap rows = 52 already represented source items. Ten Meranti issue entries
and eight Noma extraction entries bring the audited inventory to 70. Two
Northstar style/constant records are project-specific, not reusable rules.
The remaining 68 source items consolidate to 41 canonical advisory lessons:
31 existing meanings + ten new meanings, with 27 duplicate/partial items merged.
Northstar's three DEFER dispositions remain attached to missing facts; their
general UNKNOWN/performance/diagnostic practices are usable without upgrading
those historical facts. A rejected promotion does not delete its original record.

## What proves prior ingestion

The entire tracked Nexus source/history was searched for the project identities,
memory/experience/lesson/evidence records, gates and source references. Ignored
state/output artifact-name inspection found duplicate static-source snapshots,
which are not counted as additional ingestions. No credential packets, unrelated
personal chats, environment values or authentication data were inspected/copied.
Project source directories were inspected read-only; their pre-existing dirty
and untracked artifacts remain unchanged.

| Project | Concrete repository proof | Conclusion and temporal limit |
| --- | --- | --- |
| Northstar | Commit `946b73918a01479992d673da2c498b9c29c96d42`; tracked project memory/learned knowledge, MANIFEST entries, promotion acceptance; K01-K26 parse as 26 actual rows | Exact original archive equals the available 46,088-byte original. Prior conversational numbers are confirmed by current bytes/records, not assumed. Live/provider effects are not newly verified. |
| Apex AirCare | Commit `7d09fe2cdd460f224cad64b8ab1c655af9a9c4b9`; tracked project memory/20 L records/synthesis/review and later refinement acceptance, MANIFEST | Exact 48,732-byte original matches the archive. Explicit Demo #3 header is stronger than a proposed name. Historical application/documentation roles remain separate. |
| Meranti | Accepted Roadmap G4's six-row learning case, source attribution and G4 impact/coverage contracts | Partial representation existed, with the postmortem explicitly not bundled. Detailed anchor/image/documentation lessons were missing as reusable records. |
| Atelier Noma | Actual application source, Git local-release history, later dirty Stage 1B report and saved QA JSON; no prior Nexus record found | Meaningful implementation exists; bounded knowledge is ingested now. Latest visual approval remains PENDING. No public release or Demo #3 number is invented. |
| Apex Home Services | Targeted project/repository artifact search produced no implementation or identity-resolution artifact | NOT_FOUND in this search scope; no claim of never implemented, renamed, or accepted elsewhere. |

The existing versioned-document approach is expressly documented in Northstar
project memory section 4 and Pre-G2 A4. No general project-memory runtime schema
or importer exists for these records. Accordingly the new
[canonical experience pack](../research/nexus-website-experience-pack-v1.json)
is inert structured documentation, checked with existing parsers/validators.
Its small closed curation shape does not modify G4's five schemas or create a
runtime loader. OpenAI/Codex can inspect categories and source references;
there is no automatic retrieval, policy application or authority promotion.
The pack is repository-native advisory context; the existing private-package
allowlist is unchanged and does not automatically install these records.

## Source attribution and controlled supersession

[Source register](nexus-historical-project-source-evidence-v1.md) records exact
original hashes, local commits, evidence scope, M/N locators and unresolved facts.
Existing original archives, accepted governance meanings and historical bytes
are preserved. Northstar promotion acceptance controls original pending headings;
cross-project refinement acceptance controls its narrowed D01/D02 meanings.
Those cross-project refinement IDs are distinct from G3 diagnostic qualification
IDs. Historical G2 HOLD prose is not a current-state override of later G2 v3/G4.

One context-version overlay marks Noma's earlier committed no-animation-framework
configuration SUPERSEDED as a *current* description by the later dirty GSAP
Stage 1B. Both histories remain accessible. This does not reject native controls
or mandate GSAP. Meranti's conditional explicit-anchor controller and Noma's
ordinary native navigation are compatible choices under different requirements.

## Complete bounded lesson inventory

K/L are existing source IDs. R01-R06 are audit aliases for the six Roadmap G4
Meranti learning-table rows, not invented prior record IDs. M/N locators resolve
to the new source register. W labels below are human navigation labels for the
lowercase `wNN` canonical record IDs. DUPLICATE rows preserve provenance while
adding no second rule. M03 enriches an already represented shared-state meaning.

| Item | Source project | Classification | Canonical meaning |
| --- | --- | --- | --- |
| K01 | Northstar | ALREADY_INGESTED | W01 |
| K02 | Northstar | ALREADY_INGESTED | W02 |
| K03 | Northstar | ALREADY_INGESTED | W03 |
| K04 | Northstar | DUPLICATE | W03 |
| K05 | Northstar | ALREADY_INGESTED | W04 |
| K06 | Northstar | ALREADY_INGESTED | W05 |
| K07 | Northstar | ALREADY_INGESTED | W06 |
| K08 | Northstar | ALREADY_INGESTED | W07 |
| K09 | Northstar | ALREADY_INGESTED | W08 |
| K10 | Northstar | DUPLICATE | W01 |
| K11 | Northstar | ALREADY_INGESTED | W09 |
| K12 | Northstar | ALREADY_INGESTED | W10 |
| K13 | Northstar | ALREADY_INGESTED | W11 |
| K14 | Northstar | DUPLICATE | W09 |
| K15 | Northstar | DUPLICATE | W09 |
| K16 | Northstar | ALREADY_INGESTED | W12 |
| K17 | Northstar | ALREADY_INGESTED | W13 |
| K18 | Northstar | ALREADY_INGESTED | W14 |
| K19 | Northstar | ALREADY_INGESTED | W15 |
| K20 | Northstar | NOT_REUSABLE | PROJECT_MEMORY_ONLY |
| K21 | Northstar | NOT_REUSABLE | PROJECT_MEMORY_ONLY |
| K22 | Northstar | DUPLICATE | W08 |
| K23 | Northstar | ALREADY_INGESTED | W16 |
| K24 | Northstar | ALREADY_INGESTED | W23 |
| K25 | Northstar | ALREADY_INGESTED | W17 |
| K26 | Northstar | ALREADY_INGESTED | W18 |
| L01 | Apex AirCare | DUPLICATE | W05 |
| L02 | Apex AirCare | DUPLICATE | W05 |
| L03 | Apex AirCare | DUPLICATE | W02 |
| L04 | Apex AirCare | ALREADY_INGESTED | W19 |
| L05 | Apex AirCare | DUPLICATE | W03 |
| L06 | Apex AirCare | DUPLICATE | W03 |
| L07 | Apex AirCare | DUPLICATE | W03 |
| L08 | Apex AirCare | ALREADY_INGESTED | W21 |
| L09 | Apex AirCare | ALREADY_INGESTED | W20 |
| L10 | Apex AirCare | ALREADY_INGESTED | W22 |
| L11 | Apex AirCare | DUPLICATE | W13 |
| L12 | Apex AirCare | DUPLICATE | W12 |
| L13 | Apex AirCare | DUPLICATE | W09 |
| L14 | Apex AirCare | DUPLICATE | W16 |
| L15 | Apex AirCare | DUPLICATE | W11 |
| L16 | Apex AirCare | DUPLICATE | W01 |
| L17 | Apex AirCare | DUPLICATE | W07 |
| L18 | Apex AirCare | DUPLICATE | W23 |
| L19 | Apex AirCare | ALREADY_INGESTED | W24 |
| L20 | Apex AirCare | ALREADY_INGESTED | W25 |
| R01 | Meranti / Roadmap | ALREADY_INGESTED | W26 |
| R02 | Meranti / Roadmap | ALREADY_INGESTED | W27 |
| R03 | Meranti / Roadmap | ALREADY_INGESTED | W28 |
| R04 | Meranti / Roadmap | ALREADY_INGESTED | W29 |
| R05 | Meranti / Roadmap | ALREADY_INGESTED | W30 |
| R06 | Meranti / Roadmap | ALREADY_INGESTED | W31 |
| M01 | Meranti | MISSING -> INGESTED_NOW | W32 |
| M02 | Meranti | MISSING -> INGESTED_NOW | W33 |
| M03 | Meranti | PARTIALLY_INGESTED -> MERGED | W27 |
| M04 | Meranti | MISSING -> INGESTED_NOW | W34 |
| M05 | Meranti | MISSING -> INGESTED_NOW | W35 |
| M06 | Meranti | MISSING -> INGESTED_NOW | W36 |
| M07 | Meranti | DUPLICATE | W22 |
| M08 | Meranti | MISSING -> INGESTED_NOW | W37 |
| M09 | Meranti | MISSING -> INGESTED_NOW | W38 |
| M10 | Meranti | MISSING -> INGESTED_NOW | W39 |
| N01 | Atelier Noma | DUPLICATE | W05 |
| N02 | Atelier Noma | DUPLICATE | W33 |
| N03 | Atelier Noma | MISSING -> INGESTED_NOW | W40 |
| N04 | Atelier Noma | DUPLICATE | W13 |
| N05 | Atelier Noma | DUPLICATE | W30 |
| N06 | Atelier Noma | MISSING -> INGESTED_NOW | W41 |
| N07 | Atelier Noma | DUPLICATE | W37 |
| N08 | Atelier Noma | DUPLICATE | W23 |

### Other source aliases and coverage

Meranti sections 5, 9 and 10 repeat these meanings as practices/playbook/gates:
evidence/boundaries -> W05/W17/W38; planning -> W01/W02/W18/W30;
architecture -> W21/W32-W37; build -> W12/W13/W37;
interaction QA -> W13/W27-W29/W33-W36; visual/responsive -> W06/W22/W30;
release -> W07/W11/W18/W23/W24/W31. They are aliases, not additional lessons.
Northstar sections 22-23's rules/gates and Apex's 22 operational rules are already
mapped by the preserved acceptance/synthesis documents; they are not counted
again. Project colors, typography, durations, viewport/body/time constants,
specific status codes and framework versions remain examples, not Nexus defaults.

## G4 compatibility and authority

The experience file can be a derivative source in the existing ContextManifest,
with exact digest, project/task scope, recipient limits and accessible source
references. Tests compose that reference with the existing Website bundle;
only ALLOW_STRUCTURAL_TEST_ONLY / authority none results. Missing derivative
original references fail closed. Neither the knowledge object nor a structural
fixture admits the production gate: every production check remains DENY.

Knowledge is contextual. Accepted permissions, G3 authority, G4 evidence/impact
coverage and G2/D03 recovery remain separate. No new production module, planner,
agent, database, RAG service, policy loader or execution path was added. G4 remains
COMPLETE_PREPARATION_FAIL_CLOSED; G3 INCOMPLETE; D01 CLOSED; D03 DEFERRED;
REAL_ADMISSION_ENABLED NO.

## Verification and remaining gaps

Regression result: 599 relevant tests executed; 595 passed, four existing
environment/privilege skips, zero failures/errors. The clean LF snapshot includes
the unchanged G3/G4, governance, managed execution, package/distribution and
Host/plugin boundaries, plus seven new knowledge checks. This documentary audit
does not replace the earlier complete G4 regression (1,462 checks, zero failures).
Seven meaningful knowledge tests cover closed parsing/category lookup, exact
archive/provenance binding, semantic duplicates, supersession, malformed/sensitive
inputs, evidence grades/counting and G4 derivative-source/production-DENY behavior.
These are static documentary checks, not a production ingestion service or a
universal personal-data classifier. Curated content receives a separate bounded
secret/contact-pattern scan and manual scope review.
Repository hygiene: all 511 baseline MANIFEST entries and production files are
unchanged; the project checkpoint contains 515 entries. The existing private
allowlist builds reproducibly with 166 members (the additional member is the
test module). Source-project HEADs, dirty status and inspected byte digests match
the read-only baseline. Curated secret/contact-pattern checks and scope review
pass. No freeze/tag is justified for this advisory knowledge checkpoint.

Missing Meranti old code, Northstar original advisor reports/performance/warning
details, Apex hydration root cause/performance and Noma approval/reduced-motion/
public delivery remain UNKNOWN, UNVERIFIED or DEFERRED as applicable. Meranti and
Noma originals remain external; no source access/semantics claim is manufactured
from hashes. No historical application test, browser run or live deployment was
replayed by this audit. Current remote/deployment identities of the portfolio
projects were not queried. These gaps safely remain unresolved.

## Reference-source addendum

The separately authorized reference audit follows the completed project checkpoint.
It will classify source usage from repository/project evidence, link metadata
instead of copying external content, and merge duplicate lessons into this same
canonical experience pack. Its counts will be appended without rewriting the
project audit or its original source inventory.
