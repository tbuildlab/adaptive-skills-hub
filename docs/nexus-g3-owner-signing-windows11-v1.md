# Exact Windows 11 Owner signing procedure v1

Prepared 2026-10-14 against checkpoint `9b45a35bb11b490f27deed1e2e745e4faf71a2b6`.
State: **UNSIGNED / NOT REGISTERED / WAITING FOR HUMAN ACTION**.
No private key was created or opened, GitHub key registered, signature produced,
capability registered or production authority enabled by the assistant.

## Exact subject and bytes to review

- Approved origin proposal SHA-256:
  `6a9fb49a874ced10ba0ea6a4aea4cd9c5d48e77c1d6f0f448551d3b7edf4504c`.
- Actual unsigned file to sign:
  `D:\chatgpt\安装skills\nexus-g3-owner-signing-v1-20261014\owner-approval.json`.
  Its exact UTF-8/LF bytes equal
  `research/nexus-g3-owner-signing-decision-v1.json`.
- Payload SHA-256:
  `064f3e9609239cb5f859f13111dde5ed6cfd29c031407712d54aad5514c0f508`.
- Existing capability: `nexus/read-only-git-maintenance`, original read-only
  Core Host Loop v1 at accepted commit
  `a13505729bf719f25aab38ac10440562fdf59220`.
- Exact G3 subject:
  `nexus.g3.subject.v1:2a20b4b3b2d57f35832df83737c3a60896b9c8a2df9dd5fd116828f03ead222e`.
- Component digest:
  `3d86aa2dd7d4a2dae5d9233fa67b08285a2562c4ad11b4ef579df08ab749ef56`.
- Configuration digest:
  `6bf8495ab7c2c150302d4ad4e1f77ec708b2842d55803d48caa6e75790ab28ce`.
- Issuer association: GitHub **TDY0225 / numeric user ID 223441940**.
- Purpose: exact bounded capability approval and acceptance of the proposal's
  issuer boundary. It includes an explicit instruction to revoke this one
  approval after the first completed qualification, or failure/cancellation/
  unknown outcome, before subsequent eligibility. No new revision or unrelated
  task is approved. Registration and execution still require their own gates.
- Finite decision interval: **2026-10-14 13:37:56 through 2026-10-21 13:37:56,
  Asia/Kuala_Lumpur, end exclusive**. This is capability-decision validity,
  not an N01 public-pin review. Expiry denies; no silent extension or resigning
  different bytes. The original signature remains history.

Review the actual payload before signing. Its `component.material_files` pins
five existing code/Skill files, `review_evidence` pins actual retained review/test
records, and its configuration bounds one read-only task to at most eight Host
batches with no replanning. Only evidence output outside the inspected repository
is permitted; source changes, Git mutations, installation, deployment and
production admission are excluded. An unsigned `APPROVE` field grants nothing.

## Human action 1: create the dedicated Ed25519 key

Open a normal **Windows PowerShell** terminal yourself. Paste this block; it does
not change execution policy and refuses to overwrite any existing key pair.
If it reports an existing pair, preserve it and confirm its dedicated purpose
before doing anything further. Do not paste or open the private-key contents.

```powershell
$G3KeyDir = Join-Path $env:USERPROFILE 'NexusG3OwnerSigning'
$G3Key = Join-Path $G3KeyDir 'nexus_g3_ed25519'
if ((Test-Path -LiteralPath $G3Key) -or (Test-Path -LiteralPath ($G3Key + '.pub'))) { throw 'Existing key preserved; do not overwrite.' }
[void][System.IO.Directory]::CreateDirectory($G3KeyDir)
& "$env:WINDIR\System32\OpenSSH\ssh-keygen.exe" -t ed25519 -a 100 -C 'nexus-g3-owner-223441940-signing-only' -f $G3Key
if ($LASTEXITCODE -ne 0) { throw 'Key generation did not complete.' }
$G3Public = (Get-Content -Raw -LiteralPath ($G3Key + '.pub')).Trim()
if (-not $G3Public.StartsWith('ssh-ed25519 ')) { throw 'Expected Ed25519 public key.' }
[System.IO.File]::WriteAllText('D:\chatgpt\安装skills\nexus-g3-owner-signing-v1-20261014\github-signing-key.pub', $G3Public + "`n", [System.Text.Encoding]::ASCII)
$G3Public
& "$env:WINDIR\System32\OpenSSH\ssh-keygen.exe" -l -E sha256 -f ($G3Key + '.pub')
Set-Clipboard -Value $G3Public
```

Choose a **nonempty passphrase** in the two native key-generation prompts. The
assistant never receives it. Do not use `-N ""`, put a passphrase on the command
line, or add this dedicated key to `ssh-agent`. Only native `ssh-keygen` handles
the private key during your personal generation/signing actions. Public-key and
signature files are shareable verification material; private keys are not.

The actual public key cannot be known before you generate it. The block produces
the exact public registration text, prints its public fingerprint, copies only
the public text to the clipboard, and saves the public registration material as
`D:\chatgpt\安装skills\nexus-g3-owner-signing-v1-20261014\github-signing-key.pub`.
It does not substitute a fake public key or an implementer-controlled signer.
The passphrase and no-agent restriction protect access to signing; no whole-Host
or same-user OS isolation guarantee is claimed.

## Human action 2: register only the public Signing Key

In your **TDY0225** GitHub account open
[New SSH key](https://github.com/settings/ssh/new):

- Title: **Nexus G3 Owner signing v1 — 223441940**.
- Key type: **Signing Key**, not Authentication Key.
- Key: the complete single `ssh-ed25519 ...` public line copied above.

Finish GitHub's own confirmation if requested. No credentials or confirmation
codes are sent to the assistant. GitHub documents the separate signing-key type
in [its official registration procedure](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

## Human action 3: sign the exact reviewed payload once

Use the same terminal or paste this complete block into a fresh PowerShell
terminal. Native OpenSSH prompts for the key passphrase; enter it only there.

```powershell
$G3Payload = 'D:\chatgpt\安装skills\nexus-g3-owner-signing-v1-20261014\owner-approval.json'
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $G3Payload).Hash.ToLowerInvariant() -ne '064f3e9609239cb5f859f13111dde5ed6cfd29c031407712d54aad5514c0f508') { throw 'Payload changed; do not sign.' }
if (Test-Path -LiteralPath ($G3Payload + '.sig')) { throw 'Existing signature preserved; do not replay signing.' }
& "$env:WINDIR\System32\OpenSSH\ssh-keygen.exe" -Y sign -f "$env:USERPROFILE\NexusG3OwnerSigning\nexus_g3_ed25519" -n nexus-g3-approval-v1 $G3Payload
if ($LASTEXITCODE -ne 0) { throw 'Signing did not complete; no approval inferred.' }
```

Exact signature output:
`D:\chatgpt\安装skills\nexus-g3-owner-signing-v1-20261014\owner-approval.json.sig`.
Never edit/reformat the payload, pipe it through a text pipeline, change its line
endings or overwrite an earlier signature. Retain the original key registration,
payload and signature. Reply that these three actions are complete; no private
key/passphrase needs to be uploaded or pasted. The public file and signature are
already at known local paths for subsequent verification.

## Exact post-signature verification command

The assistant will execute this after the three human actions; you may also run
it yourself for inspection. It is not a fourth non-delegable human requirement.

```powershell
& 'D:\DevTools\NexusR2Python\Scripts\python.exe' -X utf8 'D:\chatgpt\安装skills\nexus-core-g4-domain-qualification\scripts\verify_g3_owner_signature.py' --payload 'D:\chatgpt\安装skills\nexus-g3-owner-signing-v1-20261014\owner-approval.json' --signature 'D:\chatgpt\安装skills\nexus-g3-owner-signing-v1-20261014\owner-approval.json.sig' --public-key "$env:USERPROFILE\NexusG3OwnerSigning\nexus_g3_ed25519.pub"
```

This fixed-packet helper checks the proposal/payload/subject digests, validity,
actual current material/review bytes, live GitHub login **and numeric ID**, and
the exact Ed25519 key's membership in GitHub's **SSH signing-key** registry.
It does not trust a caller-created allowed-signers file. It builds a temporary
public allowed-signers file from that independently read association, then calls:

```text
C:\Windows\System32\OpenSSH\ssh-keygen.exe -Y verify -f <fresh-derived-allowed-signers> -I github-user-223441940 -n nexus-g3-approval-v1 -s <byte-exact-copy-of-owner-approval.json.sig>
```

The exact payload bytes are passed directly to the subprocess's binary stdin;
no PowerShell text conversion is involved. [OpenSSH verification](https://man.openbsd.org/ssh-keygen)
checks both the signer and namespace. The helper accepts only current successful
GitHub reads, no redirects/pagination/cached Age, and a fresh HTTP Date; the whole
source observation and verification must finish within 30 seconds. Network,
clock, key, signature, subject or scope uncertainty returns DENY_OR_UNKNOWN.
It never signs, reads a private key, calls an agent, registers a capability or
enables admission. A success is explicitly READBACK_ONLY_NOT_BEARER_AUTHORITY.

Only after genuine identity/key/signature verification may the previously
authorized G3 qualification continue. This does not pre-certify registration,
revocation, independent review, G3 freeze or G6. Plain-text “approved,” the
unsigned payload and mocked test success cannot substitute for the signature.
Historical N01/security research remains HOLD. **REAL_ADMISSION=NO**.
