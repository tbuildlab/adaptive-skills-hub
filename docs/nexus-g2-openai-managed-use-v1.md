# G2-OPENAI offline handoff usage v1

This v1 guide describes the checkpointed offline handoff. The separately admitted
[Responses hosted shell adapter](nexus-g2-openai-hosted-adapter-v1.md) supplies the
new direct-provider commands; the handoff commands below remain offline.

This source-only slice prepares real bounded handoffs. It makes no provider API
calls, uploads, account/credential changes or paid requests. Existing `core`
commands remain the reviewed local execution path. Installation is separate.

Run `python scripts/managed_handoff_demo.py <new directory outside a Git repo>`
for a fixed non-secret fixture and real handoff file. It stops at
`HANDOFF_PREPARED`/`NOT_COMPLETE`; it produces no provider receipt. Project scopes
inside a repository must use its root so an exact Git baseline can be bound.

Use an explicit non-secret spec, for example `handoff-spec.json`:

```json
{
  "schema": "nexus.execution.spec.v1",
  "category": "coding",
  "files": ["README.md"],
  "effects": ["output_artifacts"],
  "artifacts": [{
    "path": "report.txt",
    "verification": "owner_review",
    "expected_sha256": null
  }],
  "ttl_seconds": 3600
}
```

```powershell
python scripts/nexus.py managed-plan "Review the selected README and return report.txt." --project "D:\Projects\Example" --request "handoff-spec.json" --task-dir "state\managed-example"
# Review the request in execution.json, input file scope, expiry and budget.
python scripts/nexus.py managed-handoff "state\managed-example" --approve <APPROVAL>
python scripts/nexus.py managed-status "state\managed-example"
```

The resulting `handoff-1.json` includes only approved input text and the bounded
request. It is a real local file, not execution evidence. The Host must independently
review task authority, provider availability, budget and required controls before
using any genuine surface. No Host tools are callable through this CLI.
Do not export a project containing secrets. Hashes do not detect secret content.

Download artifacts separately through an authorized Host/provider mechanism;
then select their local directory and a normalized receipt:

```powershell
python scripts/nexus.py managed-receive "state\managed-example" --receipt "downloaded\receipt.json" --artifacts "downloaded"
```

The closed receipt has these exact fields:

```json
{
  "schema": "nexus.execution.receipt.v1",
  "execution_id": "host-reference-from-actual-execution",
  "backend_id": "openai-host-handoff.v1",
  "task_id": "copy-the-request-task-id",
  "request_digest": "copy-the-request-digest",
  "attempt": 1,
  "start_status": "STARTED",
  "end_status": "completed",
  "artifacts": [{"path": "report.txt", "sha256": "actual-64-character-lowercase-sha256", "bytes": 123}],
  "changed_files": [],
  "checks": [],
  "exit_status": 0,
  "warnings": [],
  "ambiguity": false,
  "continuation_reference": null,
  "provider_metadata": {},
  "usage": null,
  "failure": null,
  "cancel_phase": null,
  "actual_effects": ["output_artifacts"]
}
```

This is a structural example, not a usable provider receipt. Never invent an
execution reference, tests, provider metadata, usage or provenance. Unknown
fields and command-like checks are never executed; checks remain descriptive.
Imported evidence is locally checksum-bound but Host-reported/unauthenticated.

`owner_review` imports preserve `VERIFICATION_REQUIRED`; they cannot complete.
For deterministic artifacts, set `verification` to `sha256` and bind the exact
expected SHA-256 **before approval/export**. Nexus computes downloaded byte hashes
independently and completes only when every artifact satisfies that expectation.
Success certifies that requested artifact contract, not a general code review.
No local code patch is applied and no returned executable is run.

Cancellation records intent only:

```powershell
python scripts/nexus.py managed-cancel "state\managed-example"
```

It does not stop a Host/provider. Bound subsequent evidence can distinguish
`PROVIDER_ACKNOWLEDGED`, `EXECUTION_STOPPED` and `RESULT_RECONCILED`.
Ambiguous/interrupted handoffs require reconciliation; `managed-status` never
replays. Pre-execution transient/provider-unavailable failures alone can prepare
a second attempt using `managed-retry ... --approve <current digest>`; that new
attempt needs its new digest approved for export. The original expiry remains.
Implementation/verification/capability failures require a new reviewed plan.

Current CLI output presents BACKEND, CAPABILITIES, EXPECTED EFFECTS, APPROVAL,
STATUS, ARTIFACTS, VERIFICATION and FINAL RESULT. `NOT_COMPLETE` is intentional
for unsupported, unverified, ambiguous and cancellation outcomes.
