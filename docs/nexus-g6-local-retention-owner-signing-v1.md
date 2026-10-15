# G6 exact Owner signing package: one local-retention workflow v1

Approval: **NOT_OBTAINED**. This new packet is unsigned. The new reservation is
absent. V1/v2/v3 decisions remain consumed and all 42 historical native attempt
files remain unchanged. This package creates no execution or release authority
until the Owner supplies the detached signature and exact verification succeeds.

Canonical payload SHA256: `0635da1837e8793f314080cbdc803fa78556be2a93a78a3d64ae68d239a9f9f5`.
Encoding: sorted compact UTF-8 JSON plus one LF; sign these exact bytes.
Signing file: `output/g6-local-retention-owner-signing-v1/decision.json`.
Identical retained copy: `research/nexus-g6-local-retention-owner-decision-v1.json`.

Exact subject: `nexus.g3.subject.v1:ce780c9ee36284c39f3a28f4eaddfd4225b3796abb0a020b4fe58ad8e4005c9d`.
Component SHA256: `796557c6e924b586d1c99e50aa13b7a3465e1cddd9db77a6acf159f8e8a5b1ff`.
Configuration SHA256: `35bdd9b8df87f951fcca647a501ba20ff77c12ccf9ab4b2f531c5993b58f716a`.
Independent review SHA256: `378dcd458109c114041f3496386210523361f0d1f9d8dfb14a11e0fe40aa0ba2`.
Independent review scope SHA256: `7d68df2e9428525294f09464d9f3a45364627442c5eec9c0bd1ece474e2d7233`.

Fixed window: **2026-10-15 15:16 to 2026-10-16 15:16 Asia/Kuala_Lumpur, end excluded**.
Duration 24 hours. No renewal, old approval migration or replay is permitted.

## Exact authorized-if-signed scope

Exactly **one** fixed local-only model qualification creating an inspectable
retention-index CSV from the three real, hash-pinned v1/v2/v3 dispositions.
The model must classify quarantines versus PUBLIC_ONLY_PASS, copy measured byte
counts and KEEP every retired record. A marker alone is insufficient. The
controller must verify the complete source-derived CSV, write the local artifact
exclusively and reopen it; failed/unknown/late output remains quarantine.

Input classification: **PUBLIC_PROJECT_EVIDENCE_WITH_LOCAL_ONLY_ROUTING**.
These are real project records, not new confidential input or synthetic
replacements for failed runs. The private/local claim concerns the enforced
execution and routing policy. This does not authorize arbitrary private files,
credentials or new source discovery, and does not prove confidential-data handling.
Actual useful completion is not established until this real model run succeeds.

Only four selected fields from each fixed source enter the sealed 811-byte task
file. The full payload binds all source hashes, selected task/configuration,
actual prompt hash, executable/DLL membership, Host hashes and permissions.
The candidate can read only its exact task file/model and pinned loader paths,
not the original source directories. No raw input/output/report is sent to the
conversation, feedback, OTel or remote exporters. Post-run verification must use
local checks returning bounded metadata/hashes, without printing model output.

Same eight CPU members; no model/backend/runtime replacement. ZIP SHA256:
`8708a7b81842333927f6377ac3f17ff8bba4dbe1ee0cf28dfd5e7a32e3a46b38`.
GGUF SHA256:
`9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031`.
Prompt SHA256: `7c3c836c4738cf937af710894f067b3a0d67bee109c27028b5492d143e91fbf5`.
Effective prompt SHA256 after vendor -f trim:
`058ddc78ede23bd31423637b8a8d1f73cdc0284fbc71fe6aa69f9dc059637f03`.

Fresh exclusive reservation: `output/g6-local-retention-once-v1` (currently absent).
Exact input: `D:\chatgpt\安装skills\nexus-core-g4-domain-qualification\output\g6-local-retention-once-v1\input\task.txt`.
Raw local output: `D:\chatgpt\安装skills\nexus-core-g4-domain-qualification\output\g6-local-retention-once-v1\result` stdout.bin/stderr.bin.
Accepted artifact: `output/g6-local-retention-once-v1/result/retention-index.csv`.
Only bounded receipt metadata is returned. No registration, installation outside
the exact ephemeral subset, activation, automatic retry or production use.

Existing MXC, suspended pre-resume Job assignment/readback, strict three-stdio
handle allowlist and root-deny filesystem remain enforced. Network/exporters
are disabled; no frontier model, semantic Agents, remote MCP or fallback is
permitted in this fixed execution path. Limits remain 2 GiB Job memory, eight
processes, 120-second periodic user-CPU threshold, 180-second guarded wall
with bounded cleanup, 65,536 aggregate output bytes, two threads, 1,024 context,
and 128 output tokens. No zero-overshoot claim is made.

Completion, failure, cancellation, crash, partial/late output or unknown outcome
permanently retires the attempt. Its directory must not be reset/deleted. Missing
artifact or controller failure never authorizes redispatch. V1/v2/v3 cannot be
replayed, rehydrated or reused. This decision cannot authorize value/comparison,
material substitution, another native attempt, new private sources, capabilities,
cloud/paid services, N01, production release or REAL_ADMISSION.

## Readiness and remaining original G6 gates

Independent review: **PASS_SIGNING_READINESS**, no remaining material finding.
Current shared public composition **18/18 PASS**; public CSV transport **4/4 PASS**.
Focused regression **56/56 PASS**; affected **161/161 PASS**, zero SKIP/FAIL/ERROR.
Focused tests overlap affected tests. These are readiness evidence, not actual
model completion. Earlier unit/export failures and intermediate revisions remain
retained. No new full final repository sweep is claimed at this stage.

Material configuration substitution/common tasks, remaining A-H/A6 coverage,
separate pilot and locked fair value comparison, final independent G6 review,
final regression and exact Owner release acceptance remain separate gates. A
correct CSV alone proves no advantage over a capable native Host or deterministic
implementation; the comparator must not be weakened.

No new cloud resource or paid service. Existing local hardware/energy cost is
unmeasured, not a claim of monetary savings. G2/G3/G4 remain frozen, G5 disabled,
N01 optional research HOLD, and REAL_ADMISSION=NO. The approved baseline/module
history is preserved; this is a new exact source/configuration subject.

## One Owner signing step

Existing issuer freshly verified: GitHub TDY0225, user ID 223441940, Signing Key
ID 1242636, fingerprint SHA256:5FV4/OvvMPzivK/4YIolW2kPQBGoik/llHbviTDpf98.
Use the existing dedicated key; do not generate/register a new key.

```powershell
$g6Payload = 'D:\chatgpt\安装skills\nexus-core-g4-domain-qualification\output\g6-local-retention-owner-signing-v1\decision.json'
if ((Get-FileHash -LiteralPath $g6Payload -Algorithm SHA256).Hash.ToLowerInvariant() -ne '0635da1837e8793f314080cbdc803fa78556be2a93a78a3d64ae68d239a9f9f5') { throw 'Payload mismatch; do not sign.' }
& "$env:WINDIR\System32\OpenSSH\ssh-keygen.exe" -Y sign -f "$env:USERPROFILE\NexusG3OwnerSigning\nexus_g3_ed25519" -n nexus-g3-approval-v1 $g6Payload
```

Any passphrase stays in the native prompt; never send it or the private key to
Codex. This creates decision.json.sig only. Plaintext approval is insufficient.
After the Owner reports signing, Codex must first perform verification only:

```powershell
Set-Location -LiteralPath 'D:\chatgpt\安装skills\nexus-core-g4-domain-qualification'
& 'D:\DevTools\NexusR2Python\Scripts\python.exe' -X utf8 -c "from ash.g6_native_binding import _verify_native_owner; _verify_native_owner('private'); print('EXACT_OWNER_SIGNATURE_VERIFIED; NO_DISPATCH')"
```

Only after successful exact verification may `ash.g6_private_completion.attempt()`
create this single fresh reservation. The guard rechecks current issuer/key,
material/configuration, review, source identity and time before resuming the
bound process. No signed execution material may change under this seal.
