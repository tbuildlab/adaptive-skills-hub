# D03 zero-cost recovery fence survey v1

2026-10-11. Accepted baseline: `21ad1c96220a0f6a4df642143e2851aae583cc8e`.
Branch: `nexus-v2-g3-return-development`. This additive disposition follows the
Owner's zero-paid-infrastructure G3 return directive. It preserves D01 closure,
completed G4/G6 preparation, and all historical findings.

## Recovered scope and precedence

[Minimal D03 scope](nexus-g3-d03-minimal-scope-and-autonomy-amendment-v1.md)
supersedes the older requirement to provision DynamoDB/ECS/ECR/N01/N02 before
qualifying D03. [Offline semantic closure](nexus-g3-u1-d03-offline-semantic-closure-v1.md)
already defines the closed rows, snapshot codec, PREPARED/append/readback/finalize
protocol, quarantine, retirement and terminal consumption. These are reused.
The [delegated policy](nexus-g3-delegated-executor-authority-policy-v1.md) removes
D04 executor exclusion as a release gate. Older D03 text requiring D04 exclusion
is historical for that clause; it does not override delegated mode. Independent
recovery custody and applicable complete mediation remain required.

The latest minimal amendment explicitly retains the two-account requirement and
independently administered recovery registration. Neither delegation nor zero cost
waives it. No single-account replacement, weaker threat model, alternate GENESIS,
new authority schema or compatibility amendment is adopted. Functional alternatives
were evaluated, but none is promoted from a plausible primitive to an accepted fence.

[D01 closure](nexus-g3-d01-delegated-live-closure-v1.md) remains CLOSED for its exact
bounded live profile. This task performs no MFA ceremony, live identity/session
operation, new D01 diagnostic, registration change or diagnostic deployment.

## Current non-secret observations

Fetch and branch history resolved the latest accepted G6 baseline above. The new
worktree excludes the original checkout's three unrelated Route D drafts. Existing
source and historical checkpoint refs are preserved.

Git, GitHub CLI, Node and Docker CLI are present. Go, immudb/immuclient, Rekor CLI,
cosign and an independently registered D03 service are not established by the
bounded PATH/service inspection. Docker CLI presence is not a running protected
backend. Local account names include NexusTest; an account label alone does not
prove authenticated recovery custody, a protected service or an enrollment.
The current process is medium integrity; Administrators is deny-only, not an
elevated administrator token. The worktree ACL grants modification to authenticated
users and sandbox principals. Existing local journal files would therefore share
the executor's ordinary write boundary. No account, ACL, service, TPM or key store
was reconfigured, and no existing private key/credential/profile was read.

Existing Windows Application and PowerShell Operational event logs are enabled,
but both report Circular retention (20 MiB and 15 MiB limits respectively).
Only log configuration metadata was read, never event contents. There is no
registered protected D03 event channel or recovery registration. Bounded TPM
status-only CIM inspection was unavailable through the current interface; TPM
hardware, ownership and registered NV protection remain UNKNOWN. No owner-auth
value, TPM key, NV contents or hardware mutation was requested or accessed.

GitHub CLI has no usable authenticated API context. The existing protected GitHub
connector nevertheless resolves this private repository with `admin`, `maintain`
and `push` permission. These observations describe different interfaces. Git push
authentication does not imply a qualified recovery administrator or an independently
protected checkpoint repository. Current ruleset enforcement and account billing
plan are UNKNOWN; there was no ruleset or remote-history mutation.

One unauthenticated GET of `https://rekor.sigstore.dev/api/v1/log` returned HTTP 200,
tree size `3075995179`, root hash
`4f096909d43a79c17b214fc0ccc5a038b6f6907052ff7b7efc893d4761e8a34e` and response SHA256
`7adf521540cbce93d98e969e34867ab4299fc1914613cbc6edab7d472fd67599`.
These are observed public metadata, **not verified signed/fresh recovery evidence**.
No entry was appended, no OIDC flow was started, and no data was published.
No other registered free service/account with the required custody was found in
the inspected repository/interfaces. This is a bounded negative observation,
not a claim that such facilities cannot exist elsewhere.

## Candidate matrix

PASS_CANDIDATE means eligible for actual qualification, not CLOSED. No candidate
reaches that classification here. CONDITIONAL identifies a useful primitive with
unmet deployment/registration/independence conditions. BLOCKED identifies a known
scope or custody failure. NOT_APPLICABLE excludes a different-purpose primitive.

| Candidate | Classification | Independence / mutation | History / current-head gap | Cost, offline viability, complexity / minimal integration |
|---|---|---|---|---|
| Existing Nexus fake fence/control codec | BLOCKED | Test caller can rewrite both Python states; no deployed custodian | Existing protocol catches rollback/fork/gaps **if** independent history survives; joint restore erases the anchor | Already local/zero incremental cost, smallest reuse; retain models/codecs for consumer tests only |
| Local Git repository or same-user bare mirror | BLOCKED | Same principal can change refs, delete sequence refs and replace history | CAS protects an honest expected ref; valid objects/fsck do not establish monotonic current head or D03 sequence completeness | Installed, local/zero cost, small; counterexamples reproduced with actual Git; no adapter selected |
| Existing GitHub repository / protected-history rules | BLOCKED | Connected executor has repository admin; independent recovery administration not established | Rules can block force/delete, but edit/delete/bypass authority and exact recovery register must be separate | Existing account reused for development Git only; public Free rules availability does not prove this private repo plan/controls; no settings changed |
| NTFS read-only / ordinary ACL / same-host service | BLOCKED | Observed shared modification; writer can reverse read-only attribute | Hash journal plus editable anchor can jointly roll back; restart does not create independent custody | Local/zero incremental cost, simple files; separate account/service label insufficient; no ACL change or privileged service installed |
| Existing Windows event-log service | BLOCKED | Service custody differs from ordinary files, but exact D03 channel/admin/register is absent | Inspected channels use Circular retention, which replaces oldest events at capacity; no complete retained D03 history or conditional lineage/current-head proof | Already local, zero incremental cost; converting shared OS diagnostics into a fence would require separately qualified enrollment/retention and consumer semantics; no channel changed or written |
| TPM counter / protected-key primitive alone | NOT_APPLICABLE | Hardware/NV custody unavailable for verification; no registered counter or recovery principal | A counter/key alone is not retained checkpoint bodies, lineage, gap/fork proof or a recovery authorization service | Hardware/access UNKNOWN; no new device purchased, key created, NV modified or custom privileged broker built |
| Signed checkpoint journal without independent head | CONDITIONAL | Signature key custody and independently protected high-water/current-head registration not established | Old genuine signatures remain valid; signatures alone do not prove latest head, fork absence or full sequence | Mature built-in Node Ed25519 reused only for in-memory counterexample; no persisted signing key; thin verification possible only after registration |
| immudb with independent client/auditor state | CONDITIONAL | Separate deployment/admin and protected verifier state required; same-user files do not supply them | SDK verified operations compare against tracked trusted state; rolling back server **and** verifier state loses that anchor | OSS/local possible; no registered deployment or independent auditor now; medium operational footprint; adapter would use SDK verification plus Nexus lineage/retirement checks |
| Public Rekor v1 | CONDITIONAL | External log operator is a promising separate boundary; Nexus recovery enrollment/current-head trust not established | Inclusion/consistency do not by themselves prove complete per-Nexus history/current head; best-effort metadata search may be incomplete | Public GET available at no new infrastructure cost; offline bundles not current-head proof; full-stream discovery, retention of exact referenced bytes and registered recovery semantics unqualified |
| Rekor v2 / transparency-dev witness network | CONDITIONAL | Independent witnesses can counter-sign consistent global checkpoints; exact Nexus custody/trust/freshness registration absent | Countersignature detects inconsistent views relative to retained witness state; an old consistent prefix still needs current-head proof; app sequencing and recovery authorization remain separate | OSS/public primitives; exact hosted terms/cost/coverage UNKNOWN; new local witness would share current custody; no service deployed or public append attempted |
| AWS separate-account S3 Object Lock candidate | BLOCKED | Historical candidate requires actual separate custody and effective controls | Object versions/retention alone do not establish sequence/current-head authority | Billing-backed route excluded by current zero-paid directive; no AWS operation or resource created |

No merely nominal separation is counted as independent. Existing OpenAI/Codex/Host
tools performed reasoning, research and local execution; they do not self-assert
recovery authority. Installed skills/connectors provide no evidenced registered
independent D03 fence. No custom planner, orchestration, distributed journal,
consensus system, generic memory engine, paid platform or production adapter is built.

## Primary-source findings and inferences

Git's expected-old update is a conditional ref update; it does not forbid a caller
with ref write authority from deliberately selecting an old object.
[Git update-ref](https://git-scm.com/docs/git-update-ref),
[Git fsck](https://git-scm.com/docs/git-fsck).
The local tests separately reproduce rollback, valid fork, sequence gap and
delete/recreate without changing the real Nexus repository.

GitHub documents rule editing/deletion by administrators and rule-specific bypasses;
free public rules availability is separate from private repository plan eligibility.
With observed admin permission and no independently administered registration,
using this repo as its own D03 fence would lack the accepted boundary. This is a
security inference, not evidence that a protected branch was actually bypassed.
[GitHub rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).

Microsoft documents that Circular event logs replace oldest events at capacity.
The current configuration therefore cannot prove the accepted retained complete
history; changing retention alone would not establish D03 enrollment/current-head
semantics. TPM NV resources are distinct limited hardware resources, not an
automatically registered checkpoint service. Their possible use as one protected
anchor is left conditional on actual hardware/custody qualification.
[Event-log modes](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.eventing.reader.eventlogmode),
[TPM resource virtualization](https://learn.microsoft.com/en-us/windows/win32/tbs/resource-virtualization).

immudb assigns trusted-state tracking to clients and documents external auditors.
The relevant reuse is verified SDK reads/writes with independently protected client
state, not a new Nexus database. No immudb runtime qualification is claimed.
[Client state](https://docs.immudb.io/1.5.0/management/state),
[Auditor](https://docs.immudb.io/master/production/auditor.html).

Rekor documents immutable supply-chain metadata and monitoring for long-term trust.
Its v1 API explicitly marks metadata index search best-effort/incomplete. Therefore
that index cannot be the sole D03 complete-history oracle.
[Rekor overview](https://docs.sigstore.dev/logging/overview/),
[Security model](https://docs.sigstore.dev/about/security/),
[v1 API](https://github.com/sigstore/rekor/blob/main/openapi.yaml).
The v2 client guide requires verifying checkpoints and specifies changed entry,
tile/proof, time and key semantics. A v1 response cannot be treated as qualified v2.
[v2 client specification](https://github.com/sigstore/rekor-tiles/blob/main/CLIENTS.md).

The witness implementation tracks append-only evolution in secure storage and
counter-signs consistent checkpoints; it is not a Nexus recovery authorization
service. Its bootstrap can be TOFU, which does not satisfy Nexus enrollment by itself.
[Witness implementation](https://github.com/transparency-dev/witness).
Inference: these external primitives merit reuse **after** exact independently
protected registration and current-head semantics are demonstrated, but not now.

## Required-property disposition

The prerequisite missing property is **an actually qualified, independently
administered current-head recovery witness for the exact registered Nexus lineage,
outside the ordinary executor/restore write boundary**. This encompasses protection
of registration, retained history and its latest-head anchor; it is one custody/fence
gate, not evidence that any untested primitive is defective. No zero-cost universal
impossibility theorem is claimed. There is no such qualified facility available in
the inspected environment. No weaker boundary is accepted.

| Required property | Reused preparation / adversarial observation | Actual D03 disposition |
|---|---|---|
| Independently protected checkpoint | Same-custody Git/file/joint-restore counterexamples; independent deployment absent | BLOCKED |
| Append-only / tamper-evident history | Existing closed checkpoints/codec; signed modified bytes rejected; Git allows custodian ref rewrite | UNQUALIFIED |
| Stale overwrite / old authority revival | Existing CAS, terminal indexes and context retirement; genuine old head/signature alone insufficient | UNQUALIFIED |
| Rollback / fork / gap | Existing full-chain model tests; actual Git counterexamples establish why fsck is insufficient | UNQUALIFIED |
| Unknown outcome quarantine | Existing crash-before-witness, after-witness and after-finalize tests preserve UNKNOWN/consumption | PASS_OFFLINE_ONLY |
| Restart never restores bearer | Existing RECOVER raises epoch/incarnation, retires context/intents and preserves terminal consumption | PASS_OFFLINE_ONLY |
| Generation / incarnation mismatch | Existing closed metadata/binding tests and G4 request-binding rejection | PASS_OFFLINE_ONLY |
| NO_AUTOMATIC_REDISPATCH | Existing duplicate claim/handoff/UNKNOWN tests; no dispatch code added | PASS_OFFLINE_ONLY |
| Current protected recovery state | Restored local state cannot replace independent history; if both anchors are mutable the assumption is unproved | BLOCKED |
| Recovery cannot promote unqualified authority | Fake promotion refusal and G3/G4/G6 negative composition; no positive production branch | PASS_FAIL_CLOSED_ONLY |
| Missing / ambiguous / corrupted evidence | Existing missing/corrupt page, fork/gap, incomplete index, timeout/crash and malformed-boundary denial | PASS_OFFLINE_ONLY |

R01-R16 consumer semantics stay in `tests/test_g3_offline_control.py`; closed D05
metadata in `tests/test_g3_production_metadata.py`; clock/recovery refusal in
`tests/test_recovery_admission_lab_v1.py`. Accepted bounds, predecessor/version
checks, retention requirements, semantic inventories and trusted clock assumptions
are unchanged. This task adds nine distinct counterexample/boundary tests in
`tests/test_g3_d03_zero_cost.py`, not a replacement fake D03 qualification.
No new unexplained skip or authority-bearing fixture is introduced.

## G3 continuation and Production Final

```text
D03_STATUS = BLOCKED_NO_ZERO_COST_QUALIFIED_FENCE
D03_SELECTED_MECHANISM = NONE_QUALIFIED
D03_REUSED_PREPARATION = EXISTING_CLOSED_PROTOCOL_AND_CONSUMER_HARNESS
D03_DEPLOYED_ENFORCEMENT = UNQUALIFIED
D03_ZERO_COST = YES_NO_NEW_PAID_INFRASTRUCTURE
D03_SECURITY_PROPERTIES_CHANGED = NO
D04_DELEGATED_RELEASE_GATE = NO
D01_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
G3_STATUS = INCOMPLETE
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```

No candidate won actual qualification, so a production adapter is unjustified.
All independent preparation reuses existing contracts; only candidate counterexample
tests and documentation/inventory are new. Protected N01/N02 production transitions,
delegated actor/provenance composition, real route/complete-mediation qualification
and delegated positive E2E remain pending. They are additional G3 work after the D03
fence prerequisite, not D04 blockers and not closed by bounded D01 diagnostics.
Production Final also requires existing G6 live support/value/independent review,
exact release/Owner acceptance gates. G4/G6 completion statuses are preserved;
their negative boundaries are regression-tested with no seam change.

Human action is not requested: there is no identified qualified zero-cost resource
for which a single login would establish the missing custody proof. The blocker is
recorded honestly instead of requesting paid AWS, inventing credentials, handing
over routine software configuration or opening another D01 ceremony.
