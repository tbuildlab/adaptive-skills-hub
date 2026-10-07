# G2-OPENAI Responses hosted shell adapter v1

Source implementation, 2026-10-07. Architecture checkpoint:
`bc98d7a33f1ca077243dc14469c989650fdaa078`. Additive to Core Alpha 2 and the
[managed contract](nexus-g2-openai-managed-execution-v1.md). No live execution has
been performed. `SELF_HOSTED_G2 = DEFERRED`; production Positive Host Binding is
ABSENT. This is managed provider trust, not Host qualification or production G2.

## Official contract and boundary

The [shell guide](https://developers.openai.com/api/docs/guides/tools-shell) supports
Responses `shell` with `container_auto`; the adapter explicitly sets a disabled
network policy and 1g memory. It sends bounded non-secret source bytes as base64
in ordinary input text; the model must reconstruct them inside its container.
There is no local filesystem mount, file upload, local shell tool, MCP, browser,
plugin or other provider. Network denial is a documented provider property, not
independent qualification. Input transfer includes only approved files and
instructions. Name/byte/hash checks and limited secret-pattern refusal are not
general DLP; the Owner must approve non-secret content.

[GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) supports
hosted shell and high reasoning. The
[Responses reference](https://developers.openai.com/api/reference/python/resources/responses/methods/create)
documents metadata, output-token and built-in-tool call limits. These are request
controls, not an aggregate hard financial cap. The default standard service tier
is explicit. The adapter does not silently substitute a model.

The [background guide](https://developers.openai.com/api/docs/guides/background)
documents retrieval and cancellation. Background/store are explicit for recovery;
this uses provider retention and is not ZDR. Cancellation acceptance is distinct
from terminal provider state, local result reconciliation, remote effect cessation
and billing settlement. Disconnect/timeout never means remote failure. There is
no claimed hard remote lifetime or cancellation-tail bound.

Artifacts are bound using response file citations and the official
[container file inventory](https://developers.openai.com/api/reference/resources/containers/subresources/files/methods/list)
and [content endpoint](https://developers.openai.com/api/reference/resources/containers/subresources/files/subresources/content/methods/retrieve).
Only an original response-bound container and the exact task-specific output
directory are eligible. Missing citations, pagination, duplicates, unknown tools,
wrong bindings, extra outputs, oversized/binary/private-looking content or
contradictions STOP. Other container files are not downloaded or audited.

## State, custody and verification

`OpenAIHostedExecutionBackend` implements the existing `ExecutionBackend` shape.
Its dataclass request extends the provider-neutral version; exact approval binds
model, backend, implementation byte closure, Nexus/project Git baselines, inputs,
artifact contract, network, deadline, soft budget and verifier. Standard-library
HTTPS uses one fixed API origin, TLS, no inherited proxy, no redirects and no
automatic retries. No dependency is installed. Runtime `OPENAI_API_KEY` is read
only inside an admitted call, never saved, hashed or supplied to a child. Public
errors use local codes; headers are discarded afterward. Python cannot promise
physical memory erasure. Shell commands, output text and raw provider errors are
not retained; bounded call IDs/counts/outcomes and usage are retained.

Intent and the one dispatch slot are persisted before POST. The response ID is
persisted before semantic normalization. A failed POST remains OUTCOME_UNKNOWN,
including HTTP 429/5xx; it never creates a replacement. A known ID resumes bounded
GET retrieval, even for late reconciliation. Poll failures retain ID/counts.
Request expiry is checked before dispatch; it is not a provider TTL. Up to 20
explicit retrievals are possible (the tiny fixture chooses 10), with a 15-second
socket timeout per call. There is no infinite local polling loop. Local clock,
OS/network timing and same-user custody are inherited Core assumptions, not
trusted UTC or all-fault guarantees. Cleanup/status retrieval after expiry is
limited to the original request, not new execution.

API cancel intent and attempt are persisted before POST. No automatic repeated
cancel, dispatch or import occurs. Terminal cancellation retains remote effect
and billing tails UNKNOWN. `RESULT_RECONCILED` here means original provider-status
and local-result disposition only, never remote cessation or settled spend.
Dispatch/import crashes lacking sufficient evidence require manual reconciliation.
An incomplete download cannot silently overwrite or redownload prior artifacts.

Outputs first enter fresh task-owned storage; Nexus builds a normalized
`ExecutionReceipt`, binds its digest and uses the existing importer. Its reported
output effect class describes imported artifacts, not an independently audited
inventory of remote side effects. Provider status alone never completes a task.
Expected-hash outputs require independently computed matching hashes; ordinary
replacement artifacts remain Owner review. A strict text unified-diff parser
returns confined existing-file replacements with exact contexts, no fuzz,
rename/addition/full-file deletion/binary patch. It never applies to a live project.

The first coding verifier is deliberately fixed: two reviewed fixture files,
unchanged tests, and only the AST for `def add(a, b): return a + b` are eligible.
After AST validation, Nexus runs the unchanged tests in a disposable local copy
with fixed argv, isolated Python, minimal environment and closed inherited FDs.
No provider command is executed locally. This is not a general untrusted-code
sandbox; broader code remains review-only. Source/project tests are untouched.

## Preparing the first live review

```powershell
python scripts/openai_live_fixture.py <new-disposable-directory-outside-Git>
```

This creates `spec.json`, a source fixture, `prepared-request.json` and a checksum
ledger; it never dispatches. Review the exact request digest and bytes. With a
separate Owner API/spend grant, the source CLI supports:

```powershell
python scripts/nexus.py managed-openai-dispatch <task-dir> --approve <digest> --allow-live-dispatch
python scripts/nexus.py managed-openai-poll <task-dir> --allow-provider-access
python scripts/nexus.py managed-openai-import <task-dir> --allow-provider-access
python scripts/nexus.py managed-openai-status <task-dir>
python scripts/nexus.py managed-openai-cancel <task-dir> --allow-provider-access
```

Do not run dispatch merely because a credential exists. A subscription is not API
authority. Model/account access remains UNVERIFIED. The future tiny test requests
one response, up to 6 shell calls and 2048 output/reasoning tokens, no network or
installation. The USD 0.10 allowance is a soft declaration only. Current
[pricing](https://developers.openai.com/api/docs/pricing) includes container charges
and model tokens separately; tool contexts, retention and failure tails prevent
claiming a finite worst-case financial maximum. A hard-ceiling requirement must
refuse this dispatch. NEXT-OWNER-DECISION in the external validation packet gives
the exact conditional grant; this sprint does not grant it.

All deterministic transport responses are explicitly FIXTURE / NOT PROVIDER
QUALIFICATION. Only a real provider execution followed by independent Nexus
verification may support `G2_OPENAI_MANAGED_E2E_VERIFIED`.

## Original-result import diagnostics and reconciliation

Every import refusal appends `import-refusal-NNNN.json` with a deterministic code,
bounded reason, stage, subject, expected/observed metadata and ambiguity. Inventory
metadata is preserved before validation in `provider-inventory.json`. These files
omit raw exceptions, HTTP bodies, commands, credentials and headers; suspicious
metadata is redacted. Verification failures retain their existing failed-state
return and receive a separate refusal record. Diagnostic I/O failure is a STOP,
never permission to continue. Metadata snapshots are bounded evidence, not a
complete forensic archive.

The first real calculator execution completed but its original inventory and
import refusal were not persisted by the old importer. The exact historical
refusal remains UNKNOWN. No path rewrite, basename matching, alternate file or
weakening of the artifact contract is authorized to compensate for missing data.
The official [inventory contract](https://developers.openai.com/api/reference/resources/containers/subresources/files/methods/list)
defines container ID, path and size; current supported fields do not by themselves
prove what the lost live inventory contained.

With separate original-result read authority, the fixed command is:

```powershell
python scripts/nexus.py managed-openai-reconcile <original-execution-dir> --allow-provider-access
```

It creates exactly one `original-result-reconciliation-v1` sibling evidence layer.
The original ledger/request/source/test bytes remain unchanged. A snapshot hash,
original response/citation/request/implementation binding and current importer
closure bind the successor layer. Eligibility is limited to the single completed,
once-listed, never-downloaded calculator result. No new task, dispatch, cancellation,
response polling, package installation or real-project apply is performed.

The reconciliation grant admits at most one original-container inventory GET and
one required cited content GET. All historical counters remain; total response,
inventory and content GET attempts must fit within the original ten-retrieval
allowance. The local old one-list replay guard is not reset: the explicit successor
layer permits one separately journaled read under the new reconciliation authority.
Intent/counters precede reads; a fixed existing layer refuses retry/replacement.
Missing credentials refuse before creating a layer. Unknown or failed reads STOP.
The network policy and output-path/citation/size/hash/verifier contract stay intact.

An expired dispatch deadline cannot authorize another execution; original-result
read reconciliation does not renew it. Completion produces a separately bound
`reconciliation-receipt.json` and independently runs the unchanged fixed tests.
Remote effects, retention, cancellation tails and final billing remain UNKNOWN.
If the container is expired/deleted or evidence fails the contract, no new execution
is available as a recovery path. Fixtures cannot qualify the original live result.
