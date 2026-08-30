# Nexus Post-R5 Runtime Integration — Slice 3A

**Status:** implementation candidate ready for independent review on the
dedicated Slice 3A branch. It is not merged, accepted, or frozen.

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
objects. In production it is used only by the existing explicit R4
Presentations Host mapping; JSON/frontmatter/external metadata cannot construct
that object.

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

## Validation evidence

- Semantic/V2/CLI/MCP/R4 focused validation: 105 tests and 19 subtests passed.
- Isolated GitHub-distribution validation: 18 tests passed with three expected
  environment-dependent skips; the packaged release loaded the exact
  manifest-verified 24-rule applicability registry without a development
  repository.
- Full repository regression: 282 tests passed with four expected
  environment-dependent skips and 50 subtests passed.
- The final legacy smoke remains 6/10 in the current Host environment. The four
  failures are `load_failed` for Documents, Spreadsheets, PDF, and the
  research-to-Documents chain. That smoke uses the unchanged legacy V1.1 route
  and reflects the known Host-managed Plugin-cache drift; no Skill file or
  loading evidence is fabricated to obtain 10/10.
- The static manifest, source package, secret/private-path scan, generated-state
  scan, and Git integrity checks are rerun before the candidate is pushed.

## Deferred work

Slice 3B/3C, executable external candidates, automatic Skill
installation/update, Agent Runtime, remote MCP/OAuth, R6, and V1.3 remain
deferred. This candidate must pass an independent acceptance review before any
merge or freeze decision.
