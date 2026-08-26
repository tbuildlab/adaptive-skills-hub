# Nexus Upstream Source Registry

`config/upstream-source-registry.json` is the v2 static provenance record for
reviewed upstream material. It is separate from the V1.2 planner, local Skill
catalog, R5 Host inventory, and Host execution mappings. Reading it never
clones, downloads, installs, updates, imports, executes, or delegates upstream
code.

Each concrete source retains its canonical URL, exact commit, classification,
license, purpose, compatibility, integration model, execution disposition,
trust and risk status, maintenance state, import mode, update strategy,
accepted/rejected components, and validation evidence. The validator continues
to accept the v1 schema so historical records remain readable.

## Twelve-source audit

| Source | Exact commit | Classification | License | Integration decision |
| --- | --- | --- | --- | --- |
| `msitarzewski/agency-agents` | `9572c66428bbc8ef475d339b2386eacd8bf540c5` | Agent; Agent collection | MIT | Canonical advisory roles only; no execution authority. |
| `jnMetaCode/agency-agents-zh` | `972452cdedef8d04fed4a8dd1dc10623e33ed412` | Agent; Agent collection | MIT | Localized advisory overlay; canonical duplicates excluded. |
| `Shubhamsaboo/awesome-llm-apps` | `11a4bc330e4b0b1509577db4581c5cfbcf6ea6a0` | Examples; references; selected Skills | Apache-2.0 | Offline static scan and trigger-test patterns adapted; unsafe runtimes rejected. |
| `emilkowalski/skills` | `d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7` | Skill; design resource | MIT | Existing `emil-design-eng` local Skill verified by SHA-256; no automatic install. |
| `rdev/liquid-glass-react` | `ac48eab18d1f7f444ae30002d240cae29c863a21` | Library; design resource | MIT | Relevant React reference only; no Nexus Core use. |
| `bytedance/deer-flow` | `788a890bd022689ef293e6bbfa2c12988173db6c` | Runtime; Harness; Framework; Skills; reference | MIT | Permission, validation, scanner, and bounded-status patterns adapted; runtime excluded. |
| `greensock/GSAP` | `13e2b790546426a1a2e0e9b409f3f8dc6d6611f2` | Library; design resource | GreenSock Standard License | Reference/license gate only; no bundling or redistribution approval. |
| `openai/codex` | `10d5a603aecbd73a38f3a6576cce69a78f8d6f1d` | Runtime; Harness; reference | Apache-2.0 | Official scope, dependency, availability, source, and sandbox concepts adapted. |
| `deepseek-ai/deepseek-harness` | `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` | Runtime; Harness; Framework; reference | MIT | Preview guard/lifecycle patterns adapted; runtime excluded and revisions re-quarantined. |
| `revfactory/harness` | `cceac68ea1d0ad198ef4b7b906cd238375836387` | Skill Factory; Harness; reference | Apache-2.0 | Creator-reviewer and near-miss tests adapted; Claude-specific factory rejected. |
| `cft0808/edict` | `14a207557719c046af0f993a7bff1cc5a5015b33` | Runtime; Harness; Agent collection; reference | MIT | Reviewer gate, permission matrix, and audit-state patterns adapted; runtime rejected. |
| `alchaincyf/nuwa-skill` | `fe0374687037c4cc51a65c1e0c145afe2981dc69` | Skill Factory; Agent collection; reference | MIT | Provenance/checkpoint patterns adapted; swarm, downloads, and auto-writes rejected. |

The historical `https://github.com/green` organization URL remains an
`unresolved` rejected record. It is not counted as one of the twelve audited
repositories and receives no component or authority.

## Component dispositions

| State | Meaning |
| --- | --- |
| `locally_usable_verified` | Existing local Skill matches reviewed pinned content and still requires normal selection/load/Host checks. |
| `advisory_only` | Agent guidance only; no tool, file, approval, artifact, or Host authority. |
| `adapted_pattern` | A small architecture/security concept informed new Nexus-owned validation code; upstream code was not imported. |
| `reference_only` | Read-only engineering evidence, not an executable component. |
| `dependency_only` | May be considered as a project dependency after its own gate; never a Skill. |
| `excluded` | Deliberately outside this phase despite possible technical compatibility. |
| `rejected_incompatible` / `rejected_deprecated` / `rejected_security` | Not permitted under the current architecture or security boundary. |
| `license_decision_required` | No dependency, bundling, or redistribution until owner/license review. |
| `unresolved` | No concrete auditable repository/component was identified. |

## Actually adapted patterns

- OpenAI Codex: separate identity/scope/dependency/availability/source/sandbox
  facts rather than treating registration as execution.
- DeerFlow: explicit permissions, pure validation, blocked scan states, and
  bounded lifecycle/status facts.
- DeepSeek Harness: monotonic gates, frozen outcomes, orthogonal status facts,
  and sanitized execution context.
- Awesome LLM Apps: offline static review plus positive, negative, boundary,
  and near-miss trigger tests.
- RevFactory: creator/reviewer separation, bounded evaluation, and revalidation.
- Edict: mandatory independent review, permission matrices, and auditable state
  transitions.
- Nuwa: source confidence, contradiction preservation, honest limitations, and
  checkpoints.

These are concepts reimplemented in Nexus-owned, standard-library, data-only
validators. No upstream module, executable, dependency, Agent runtime, or
installer was copied or executed.

## Safety and update rules

1. A URL, repository star count, display name, local installation, or metadata
   record never creates execution authority.
2. A concrete source requires an exact commit, license review, component-level
   compatibility/security review, deduplication, and tests.
3. A changed commit or content hash is a new revision and re-enters quarantine;
   approved state is not inherited.
4. Libraries, frameworks, runtimes, examples, factories, and Agent collections
   cannot masquerade as Skills.
5. No source may bypass the R4/R5 Host-owned boundary, scan private ChatGPT
   state, claim global Host enumeration, auto-install/update a Skill, execute
   shell, create a swarm, or introduce Remote MCP/OAuth.
6. Future discovery must use bounded `CANDIDATE_SOURCE` records and receive
   separate approval. This phase did not add further candidates.
