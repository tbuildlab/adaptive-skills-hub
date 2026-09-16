# Nexus Pre-G2 Architecture Acceptance Record v1

Decision ID: `nexus.pre-g2.architecture-acceptance.v1`

Decision version: 1.0.0

Owner acceptance date: 16 September 2026.

Status: **ACCEPTED — ARCHITECTURE ONLY — NO RUNTIME AUTHORITY — G2 NOT STARTED**

## Owner decision and accepted subject

The owner explicitly stated: “I accept the Pre-G2 Architecture Delta Review and the proposed Roadmap V2 companion addendum as the architecture direction for Nexus V2.” The same request restricted this step to architecture acceptance and prohibited starting G2 implementation.

The adopted subject is `docs/nexus-pre-g2-architecture-addendum-v1.md`, document ID `nexus.pre-g2.architecture-addendum.v1`, version 1.0.0. Its UTF-8/LF SHA-256 is `b6680c710dda8fb7808e06cc2569fd1bb6a4aeed47b2223f9626e411e298be14`. Its A0–A6 normative text is identical to the accepted proposal, SHA-256 `0ab3cc5a9031810ab2b0e3bb92edd8325cbe03a4821ccae20a8d38d89ddd9172`.

This record attributes the decision to the owner's explicit request. Its hashes identify bytes; neither this document nor a Git commit is a cryptographic owner credential, executable grant, candidate approval or conformance record.

## Versioning and frozen boundaries

The parent baseline is frozen G1 commit `a8ffe1e743d8106495cb260124b044fa5d8e619f`. The accepted addendum references the frozen Roadmap V2 and Slice 3C commits/tags. Their historical content and status remain unchanged. All existing runtime source, tests, configuration, package rules and R2/R4/R5 interfaces remain unchanged.

The architecture acceptance change is limited to:

1. `docs/nexus-pre-g2-architecture-addendum-v1.md` — the accepted companion.
2. `docs/nexus-pre-g2-architecture-acceptance-v1.md` — this decision, utilization record and handoff.
3. `MANIFEST.json` — generated entries for the two new documents only.

A local Git commit records this versioned acceptance. No push or new tag is part of this acceptance step. Existing local and remote frozen refs must remain unchanged. The post-commit acceptance receipt records the exact commit and final verification; the commit cannot contain its own SHA without a circular dependency.

## Integrity and validation scope

The original review directory, its 21 official-source pages, three source indexes, six-page revalidation record and completed review artifacts are preserved. Acceptance does not rewrite their earlier proposed/review-only status or refresh their claims into current enforcement facts.

Validation records are stored outside the repository in `nexus-pre-g2-architecture-acceptance-2026-09-16`. They include the pre-change refs/input hashes, affected test log, integrity results, final commit/worktree receipt and resolved fresh-session handoff.

The acceptance checks require: exact A0–A6 adoption; no modification/deletion of existing tracked files except the current MANIFEST; deterministic MANIFEST with only two added members; unchanged historical manifest at the G1 tag; passing affected package/isolation tests; deterministic package output matching the accepted G1 package; unchanged local/remote frozen tags; Git integrity and whitespace checks; and a clean final worktree.

The two architecture documents are repository governance records. The existing portable-package document allowlist excludes them; no allowlist or runtime code change is warranted. The current source MANIFEST covers them, while the frozen G1 manifest and portable package remain unchanged. This distinction must be reported explicitly rather than claiming the current MANIFEST is unchanged.

The historical G1 receipt's `manifest_committed_raw_sha256` field records a CRLF reserialization hash. Direct Git blob and checkout bytes use SHA-256 `e9d8fe9ed1fd1854c19508ccfce342f63c439a40e319f1cd62b8d9b6d9fd663e`; CRLF reserialization produces the recorded `007e37a82b698dfbce466cb2bd120f0231c9d187c3d54add5e5f5194a227d54b`. The original receipt remains unchanged. Future raw-byte and normalized-byte measurements are kept separate.

This documentation/manifest-only acceptance does not rerun or recertify the full historical G1 regression. It does not replace any future slice's independent Architecture, Security and Testing reviews, full regression, genuine Critical/High resolution, owner acceptance, release verification or freeze gates.

### Validation outcome and reproducibility

The original direct-checkout attempt is preserved: MANIFEST generation rejected the source root, and the affected suite ran 11 tests with 10 passes and one package-source boundary error. The live checkout contains `state` and `.git/objects`, directory names rejected by the existing release-source boundary. These directories and the enforcement code were not modified.

An external source snapshot copied every tracked file plus the two new documents, with raw source hashes recorded. No fixtures or tests were edited. In that bounded release-source environment, all 11 existing package/isolation tests passed. Controlled probes independently inserted `state` and `.git/objects` into the otherwise identical snapshot: each reproduced both builder rejections; removal of only the newly created empty probe directories restored the identical MANIFEST and package results. This establishes a release-source environment distinction, not a repaired product implementation or a passing live-checkout run.

The source MANIFEST contains 138 entries: the original 136 entries are unchanged and only the two companion documents are added. Repeated generation is deterministic. The portable package contains 114 members and matches frozen G1 byte-for-byte, SHA-256 `15ec05afea2270cea88ce0a57847cc278eca3dd65ac87cd4c72b3f0be4f407fb`. No release package is published or installed. `git diff --check` passes; `git fsck --full` reports no integrity errors, with existing dangling blobs non-blocking. The final post-commit receipt records current MANIFEST/report hashes, refs and worktree state.

To reproduce: export the accepted commit's tracked tree into a fresh external directory without Git metadata or local runtime state; run the unchanged `scripts.build_manifest.build_manifest_bytes` twice and compare its bytes with the exported MANIFEST; run `py -3.12 -B -m unittest tests.test_ecosystem_isolation_package -v` from that export; build the portable package twice with the unchanged `scripts.package_nexus.build_package`, placing both archives outside the export; verify their hashes and the original 136 manifest entries against `nexus-v2-g1-final`. Do not relax the source-boundary checks to run a release build against the live checkout.

## Agent & Skill Utilization Report

| Resource | Use in this acceptance step | Limits |
|---|---|---|
| Root assistant | Verified the accepted inputs and repository; adopted the exact normative text; recorded acceptance; ran affected integrity checks and committed the architecture-only change. | No G2 design implementation, executor qualification, installation, activation or product dispatch. |
| New subagents | None. | No independent review is claimed for this acceptance step. Historical G1 reviews and the prior delta review retain their own scope. |
| Nexus Skill | Instructions inspected to preserve the advisory/no-authority boundary; no new planner or handoff call. | The two advisory planner calls reported by the earlier review are historical, not repeated or counted as executor evidence. |
| OpenAI Docs Skill | No new use in this step; the accepted review's dated official-source evidence was retained. | Architecture acceptance is not renewed Host capability verification. |
| Other Skills / Plugins | None invoked for execution or installation. | Markdown and Git operations needed no artifact-generation or runtime plugin. |
| Native Host tools | Local file editing, Git/Python inspection, affected tests and package verification; remote Git ref reads. | These ordinary authorized development operations do not grant Nexus runtime authority. No live paid API or child-agent workload. |

## Exact recommended handoff for a fresh G2 session

The following is a recommended future request, not an instruction to execute during this acceptance step. The external post-commit handoff supplies the exact architecture commit SHA.

> Implement Nexus V2 G2 only: Governed Sequential Execution and Recovery. Start from the recorded Pre-G2 architecture acceptance commit in adaptive-skills-hub. First inspect the actual repository/worktree and preserve any valid subsequent work. Verify the accepted companion docs/nexus-pre-g2-architecture-addendum-v1.md and acceptance record docs/nexus-pre-g2-architecture-acceptance-v1.md, frozen docs/nexus-roadmap-v2.md, frozen docs/nexus-v2-g1.md, and the Slice 3C boundary. Do not restart, reopen or mutate frozen G1, Roadmap V2, Slice 3C or R2/R4/R5 surfaces or existing tags.
>
> Complete the bounded G2 design and binding feasibility checks before implementation. Select one actual Host binding and already accepted useful capability. Establish the exact independently authorized task scope, effective configuration, enforceable operations/resources, supported observations, budget bounds, cancellation and effect-reconciliation semantics. Documentation, tool visibility, prompts, native intelligence, profiles, selection records and the G1 read-only route pilot are not qualification or authority. Mandatory unknown or unenforced restrictions remain ineligible. If no suitable binding exists, report the precise unmet boundary; do not fabricate evidence, broaden permissions, introduce forbidden fallback or build a generic runtime as a workaround.
>
> Implement the existing GovernedExecutionContract, TraceEvent, BudgetRecord, CheckpointRecord and StopRecord around qualified Host-native sequential execution. Preserve policy intersection, hard eligibility before cost, model/config neutrality, unknown monetary cost, bounded retries, accepted artifacts and unresolved effects. Cover deferred/programmatic/transitive tool paths. Durable IDs and compacted context cannot restore grants or process-local seals. Reserve before dispatch; reconcile effects and cost separately; distinguish stop requests, stopped dispatch, cancellation acknowledgement and settlement/unknown outcomes. No unsafe retry or reservation release merely because of timeout or disconnect.
>
> Do not implement a generic agent/Skill runtime, context compressor, browser/computer engine, scheduler or multi-agent orchestration platform. Do not start G3–G6 or create installation, activation, candidate-approval, delegation or concurrency authority. Preserve No-Agent behavior and whole-path privacy. Use native mechanisms only where the actual binding proves the required controls.
>
> Continue through focused tests, adversarial/fault-injection tests, genuine defect fixes and retests, then independent Architecture, Security and Testing reviews. Resolve every genuine Critical/High finding and blocking defect. Run affected/full regression and required model/config/Host substitution checks; demonstrate an actual useful bounded success and recovery from injected interruption, not refusal-only acceptance. Preserve original failures and distinguish implementation defects, environment defects, Host limitations and expected skips. Complete truthful evidence and the Agent & Skill Utilization Report.
>
> Only when every original G2 and accepted-addendum acceptance gate passes, commit and push the accepted G2 state, create and verify the annotated nexus-v2-g2-final tag, verify local/main/origin/remote/tag agreement, MANIFEST/package integrity, unchanged prior frozen refs and a clean worktree, and freeze G2. If a necessary owner/auth/platform/license/security/destructive decision cannot be resolved within existing authorization, stop at that precise boundary. Do not weaken tests or controls to obtain PASS. Do not start G3 after G2. If interrupted, preserve all valid work and record the exact safe continuation point.

## Acceptance boundary

The architecture direction is accepted. This step grants no execution, installation, activation, approval, delegation or concurrency authority. G2 remains **NOT STARTED**. The future handoff requires a new owner instruction to begin that work.
