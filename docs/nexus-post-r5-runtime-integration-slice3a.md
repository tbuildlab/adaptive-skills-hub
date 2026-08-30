# Nexus Post-R5 Runtime Integration — Slice 3A

**Status:** independently reviewed and accepted for the immutable
`post-r5-runtime-integration-slice3a-final` freeze record. Slice 3B/3C remain
deferred.

## Baseline and scope

Slice 3A starts from the accepted Slice 2 baseline
`b9345e13185050c4d10558f0292cf9ae4813df86`. It changes only semantic Skill
routing precision. It does not add candidate discovery, installation, update,
execution, Agent delegation, Host capability authority, remote MCP, OAuth, or
another Core/runtime version.

The decision path is:

```text
original user task
  -> deterministic semantic task model
  -> trusted Skill applicability gate
  -> compatibility and integrity checks
  -> lexical/provenance ranking among compatible candidates only
  -> deterministic smallest sufficient set
  -> honest native fallback for uncovered domains
```

Raw Skill names, descriptions, tags, instructions, nested metadata, external
candidate claims, and user-supplied protocol-shaped text cannot create trusted
applicability evidence.

## Historical regressions

The implementation includes permanent fixtures for three observed failures:

1. Software ecosystem/architecture research must not select the Product Design
   UX `research` Skill merely because both contain the word `research`.
2. Source-code/security acceptance review must not select Product Design
   `design-qa`; rendered visual comparison remains a valid `design-qa` task.
3. Code documentation such as `README.md`, API documentation, or docstrings
   must not select the editable Word/DOCX `documents` Skill. A request for an
   actual Word/DOCX artifact remains a valid `documents` task.

The routing model represents domains, task kinds, context kinds, explicit
artifact families, and incompatible domains separately. It therefore avoids
making a broad keyword perform several incompatible roles.

## Versioned semantic model

`nexus.semantic-task-domain.v1` includes these bounded domains:

- `product_ux_research`, `software_research`, and `general_research`;
- `architecture_review`, `security_review`, and `code_review`;
- `visual_design_qa`;
- `presentation`, `document`, `spreadsheet`, and `pdf`; and
- the existing `backend_repair`, `software_testing`, and
  `frontend_implementation` engineering roles.

The classifier is deterministic after Unicode NFKC, case, and whitespace
normalization. It requires action/context combinations rather than generic
keywords. Optional structured extraction may populate older planning fields,
but the original user task is always reclassified locally and an extractor
cannot replace the task or manufacture authoritative domains.

Stable public decision codes include `DOMAIN_MATCH`, `DOMAIN_INCOMPATIBLE`,
`DOMAIN_EVIDENCE_MISSING`, `TASK_KIND_INCOMPATIBLE`,
`MINIMAL_SET_REDUNDANT`, and `CAPABILITY_NOT_COVERED`. Skill-integrity failure
is distinguished from semantic incompatibility.

## Trusted Skill applicability

`config/skill-applicability.json` is a bounded, versioned, manifest-protected
Nexus registry. Every reviewed rule binds all of the following:

- exact Skill identity;
- exact frontmatter metadata fingerprint;
- exact full `SKILL.md` SHA-256;
- approved source scope; and
- bounded domains, task kinds, contexts, artifacts, and incompatibilities.

The registry and integrity manifest are parsed from the exact stable byte
buffers whose hashes were verified. Discovery hashes bounded regular
`SKILL.md` files without retaining their instructions. Selection requires a
valid content digest, and loading rechecks the actual loaded bytes against the
digest used for applicability. A change between discovery, selection, and
loading therefore fails closed rather than inheriting an earlier rule.

The one direct in-memory applicability path is reserved for Nexus-owned Python
objects used by internal callers and deterministic fixtures;
JSON/frontmatter/external metadata cannot construct that object. The R4
Presentations constraint only narrows the candidate set and does not create
applicability. Production Presentations routing must independently match the
manifest-bound registry identity before selection.

## Selection and receipts

Compatibility is evaluated before lexical scoring. An allowed candidate must
have positive trusted evidence for at least one required domain, a compatible
task kind, all required contexts, and a compatible artifact family. Explicit
incompatibilities reject the candidate.

Greedy selection covers both coarse capabilities and semantic domains. At each
step it chooses the candidate with the largest uncovered contribution, followed
by stable score/name/path tie-breaks, and then removes any redundant selection.
Compatible alternatives that add no coverage receive
`MINIMAL_SET_REDUNDANT`. Missing domains remain explicit in the native Codex
fallback receipt; Nexus does not invent a Skill match.

Receipts expose bounded model/applicability versions, trusted provenance,
registry digest, matched domains/task kinds, and reason codes. They do not
expose raw Skill instructions. Agents remain advisory-only and are not included
in executable Skill selection.

## Compatibility and security boundaries

- The frozen R5 v3 response schema and current-turn Host evidence requirement
  are unchanged.
- The existing Presentations Host mapping and explicit R4 constraint remain
  unchanged in meaning.
- Non-Presentation Host-native tasks cannot enter the Presentations-only R5
  execution path.
- Slice 1 decision envelopes and Slice 2 candidate-admission receipts retain no
  execution authority.
- The semantic router performs no network request, subprocess, file write,
  installation, update, Skill execution, or Agent invocation.
- Unknown or unreviewed Skills fail closed to honest native capability rather
  than receiving applicability from descriptive prose.

## Independent acceptance review

The review started from candidate
`08af81854a54c7fe81ac2d6e0dac40e874caf71e` and independently reproduced the
historical UX-research, design-QA, and DOCX/documentation mismatches before
attacking the new trust and integrity paths. Three blocking defects were found
and closed without adding authority:

1. the explicit R4 constraint was narrowing by the `Presentations` display name
   and then manufacturing an in-memory trusted applicability object; it now
   narrows only, while the normal manifest-bound registry remains mandatory;
2. a task containing more than six genuine domains was silently truncated, and
   the first fail-closed repair exposed a CLI traceback with a local path; domain,
   task-kind, and context bounds now reject overflow and the CLI reports a
   bounded error without a traceback; and
3. protocol-shaped fields other than `supported_domains` (for example
   `primary_domain`, `required_capabilities`, and `artifact_type`) could inject
   routing tokens, including through a long scalar tail; bounded control-plane
   assignments are now treated as inert data after Unicode normalization.

The review also verified registry schema strictness, duplicate/contradictory
rule rejection, stable single-read manifest/registry parsing, source-order
determinism, prompt/body inertness, minimal complementary selection, exact
select-to-load digest revalidation (byte change, replacement, truncation,
newline change, missing file, and malformed digest), receipt redaction, Agent
advisory-only behavior, and unchanged R4/R5 Host-mediated execution authority.
No Critical or High finding remains open.

Final validation evidence:

- Semantic/V2/CLI/R4 focused validation: **77 tests passed**, including **19
  subtests**.
- Independent adversarial matrix: **20/20 checks passed**, plus stable
  manifest/registry single-read and strict-registry mutation checks.
- Capability Foundation, Slice 2, MCP, R4/R5, Desktop Plugin, and distribution
  regression group: **238 tests passed**, **4 expected environment skips**, and
  **50 subtests passed**.
- The remaining repository test modules: **42 tests passed**.
- Authoritative full repository regression: **285 tests passed**, **4 expected
  environment skips**, and **50 subtests passed**.
- Isolated distribution regression: **18 tests passed** with **3 expected
  environment skips**. Two source-package builds were byte-identical; the
  85-member archive included the Slice 3A router, registry, and documentation,
  while traversal, runtime-state, private-path, and credential-pattern checks
  passed.
- The 106-file static manifest rebuilt identically twice and an independent
  per-entry verifier found **0 mismatches**. The exact verified registry byte
  buffer loaded **24 rules**.
- Candidate and unchanged Slice 2 baseline both reproduce the same legacy smoke
  result: **6/10**. The four failures are `document`, `spreadsheet`, `pdf`, and
  `research_document_chain`, all `load_failed` because the persisted V1.1 index
  points at Host-managed Plugin-cache files that no longer exist. No Skill file,
  index, or loading evidence was fabricated to obtain 10/10.

The semantic classifier remains a bounded deterministic ruleset, not general
semantic intelligence. Tasks with more semantic domains than the v1 model can
represent fail closed rather than silently discarding requirements. The
registry uses a portable content-addressed identity (name, frontmatter digest,
full content digest, and approved source scope); volatile absolute-path-derived
catalog IDs are not authorization evidence.

## Deferred work

Slice 3B/3C, executable external candidates, automatic Skill
installation/update, Agent Runtime, remote MCP/OAuth, R6, and V1.3 remain
deferred. The independent Slice 3A acceptance review is complete; no deferred
roadmap item was started as part of this merge and freeze.
