# G2 OpenAI structured delivery v3

Owner direction: 2026-10-08. Baseline: `7fe05589bcf6b54db4f8275f02289c5d009a146f`.

## Reuse assessment before implementation

1. Nexus already provides one-dispatch intent custody, original-response retrieval,
   request approval/digests, confined artifact receipt import, strict unified diff
   parsing and a fixed AST plus unchanged local unittest verifier. Reuse all of them.
   The existing response normalizer discards final text; its importer depends on
   container files. That is the remaining gap.
2. OpenAI Responses, GPT-6.1 Sol, Hosted Shell and strict Structured Outputs provide
   execution and bounded JSON delivery. Reuse them. Codex/Work/Host execution alone
   does not supply the exact Nexus request-bound local acceptance receipt required
   by this declared workflow. Do not build another executor.
3. Available Plugins/Connectors expose no approved Responses execution bridge for
   this exact one-slot API task. The installed Nexus plugin is a planner/handoff,
   not a managed provider result acceptance service.
4. Available MCP capabilities do not supply this specific response-to-approved-
   patch acceptance operation. No new MCP runtime is needed.
5. The existing standard-library HTTPS adapter already implements the documented
   provider operations without installation, redirects, proxy inheritance or
   retries. An SDK would duplicate its transport for this small change.
6. Implement only an adapter branch for strict result extraction/validation and
   existing patch/staging/verifier integration. An adapter solves the gap; no
   custom execution infrastructure or additional container transport is justified.

## Official capability references checked on 2026-10-08

- [Model and reasoning](https://developers.openai.com/api/docs/models/gpt-6.1-sol):
  Responses tools, Hosted Shell, Structured Outputs and `reasoning.effort=high`.
- [Hosted Shell](https://developers.openai.com/api/docs/guides/tools-shell): shell
  environment `container_auto` and managed container memory configuration.
- [Responses schema](https://developers.openai.com/api/reference/resources/responses/methods/create):
  container network policy `type=disabled` disables outbound access.
- [Strict Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses):
  `text.format` with `type=json_schema`, `name`, `strict=true`, required fields and
  `additionalProperties=false`. Base-model string/array bounds are supported;
  Nexus independently enforces UTF-8 byte limits and semantic constraints.
- [Original-response retrieval](https://developers.openai.com/api/docs/guides/background):
  stored background response GET, terminal states and cancellation distinctions.
- [Usage](https://developers.openai.com/api/reference/python/resources/responses/methods/retrieve):
  input/output totals, cached/cache-write input and reasoning output details.
- [Pricing](https://developers.openai.com/api/docs/pricing): standard short-context
  input $2/M, cached input $0.10/M, cache writes $2.50/M, output $10/M;
  1 GB container $0.03 per 20-minute session. Estimate is not billing settlement.

The bridge preserves provider trust limitations. Network policy is a documented
managed configuration, not hostile-host qualification. Provider shell outcomes
and test claims are evidence; only local independent verification accepts work.

## Declared contract

Fresh non-secret two-file addition fixture; calculator.py is the only patch
subject. Strict JSON fields: status, changed_files, patch, provider_test_status.
Patch limit 4096 UTF-8 bytes; result limit 8192 bytes. Existing files and exact
unified-diff context only. No test edits, deletion, rename, binary, Git metadata,
absolute/traversal paths, unsupported control/encoding content or local commands.
Final text is transported in the original response. No container GET is required.

One fresh v3 POST at most, bounded original GETs, no replacement dispatch. Intent
is saved before POST; an original ID is saved before normalization. A malformed
structured result cannot trigger another provider task. An interrupted local
import fails closed with stage evidence and never grants dispatch authority.

Use existing CLI plan/dispatch/poll/import/status commands with verification
contract `python_add_structured_v3`. Import applies a proposed patch in isolated
staging and uses the unchanged `python_add_fixture_v1` verifier. Fixtures are
contract tests, not provider infrastructure qualification.

## Controlling future direction

REUSE FIRST. BUILD ONLY THE GAP. NO ROUTINE OWNER INTERRUPTIONS.
Autonomy does not create authority. Record genuine credential/payment/privilege/
destructive/production/legal/product-direction boundaries in NEXT-OWNER-DECISION.md;
stop only dependent work. No commit, push, merge, tag, freeze or release is granted.

G3 reuses Host/OpenAI OAuth, connection, credentials and installation; Nexus owns
exact capability subject, approval, scope, expiry, revocation and task eligibility.
No universal OAuth, identity provider, vault, marketplace or generic installer.

G4 reuses retrieval, analysis, coding, authoring, browser, rendering and compaction;
Nexus owns bounded decisions, constraints, evidence references, freshness,
supersession, change impact and workflow acceptance. No search/browser engine,
vector database, context compressor or generic code intelligence platform.

G5 is optional. Reuse native agents/lifecycle/scheduling/messaging/execution/
cancellation. Add only delegation policy, child authority, budget conservation,
resource ownership and merge/acceptance validation. Skip/disable without measurable
value and enforceability. No generic multi-agent runtime or DAG scheduler.

G6 reuses CI, tests, scanners, security/red-team tools and specialist review; Nexus
owns support matrix, qualification evidence, exact build identity, known limits,
release gate and freeze decision. No universal benchmark/security platform.

SELF_HOSTED_G2 = DEFERRED. PRODUCTION_POSITIVE_HOST_BINDING = ABSENT.
Historical v1/v2 records remain unchanged. The declared v3 managed configuration is verified.


## Real v3 acceptance and mainline closure

G2_OPENAI_MANAGED_E2E_VERIFIED

G2_OPENAI_MAINLINE = COMPLETE_FOR_DECLARED_MANAGED_CONFIGURATION

SELF_HOSTED_G2 = DEFERRED

PRODUCTION_POSITIVE_HOST_BINDING = ABSENT

NEXT = G3_REUSE_FIRST

Exactly one v3 provider dispatch completed; historical executions increased from
2 to 3. Original response: `resp_003e45ddf36a115d006ac68048d45887d09a27da8eadec23dc`.
Four bounded original-response GETs occurred: three terminal polling reads and
one diagnostic read. Container inventories and downloads: zero.

The strict structured patch passed original request/baseline/path/scope checks.
It was applied only in a new isolated staging directory. The original unchanged
AST plus local unittest verifier passed; original tests and baseline remained
byte-identical. Only calculator.py changed. No provider-returned command ran
locally and no replacement execution occurred.

The first local import refused outer shell exit codes 0/0. The original response
proved that initial unittest exit 1 was captured by a successful expected-failure
wrapper; repair/retest exit was 0 and the test hash was unchanged. The minimal
local parser repair preserves the initial refusal and original execution ledger
in a separate reconciliation layer. It accepts bounded paired wrapper evidence
without weakening patch, AST, scope, hash or independent verification checks.

Provider usage: input 3125, output 1188 (reasoning 1108), cached input 0,
cache-write input 1409, total 4313 tokens. Estimated tokens $0.0188345 plus an
assumed full 1 GB container session $0.03 = $0.0488345. Actual settled cost is
UNKNOWN. The $0.10 allowance was soft; no hard financial ceiling is claimed.

Final validation: 416 relevant regression tests, 2 isolated package tests and
324 static MANIFEST subjects passed. Machine-local evidence is retained under
state/g2-openai-structured-v3-20261008 and the separate disposable v3 fixture.
No commit, push, merge, tag, freeze, publication, Desktop release or VM operation
occurred. G3 is the next separately authorized product slice; it was not started.
No additional G2 infrastructure is authorized by this closure.
