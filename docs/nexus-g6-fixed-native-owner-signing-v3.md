# G6 exact Owner signing package v3: fixed PUBLIC framing and output protocol

Approval: **NOT_OBTAINED**. This new packet is unsigned. No v3 native attempt
has been reserved or executed. Both v1/v2 attempts remain QUARANTINE / RETIRED;
all 28 original files and their consumed decisions/signatures remain unchanged.

Canonical payload SHA256: `1f819d4d3a7f1508b2dd681b8b35fd4c51415619981a82f925f785101dd6fcd6`.
Encoding: sorted compact UTF-8 JSON plus one LF; sign these exact file bytes.
Signing file: `output/g6-native-owner-signing-v3/decision.json`.
Identical retained copy: `research/nexus-g6-native-owner-decision-v3.json`.

Exact subject: `nexus.g3.subject.v1:49fd2291573105ec5b07a6430febd4ea4797356c67eb0813296fc0ac7c963cd9`.
Component digest: `b1fddf3f419b489cd13a99089e3d62aba997104eeee89786dda61a7b14eab780`.
Configuration digest: `1da9e84fcaf0d1a4dc2b217330bea5617d91ac5b7108d840a5cd28f582a55b64`.
Independent review digest: `8cd65f91a47a88ab57976f78ca649d4f1f30e1a30b7e66f9acf3f364570b6c01`.
Independent review scope: `86aefbc431d93dbe6b72d2831df78104724abad822deaa6583b122c1549debc5`.

Fixed window: **2026-10-15 14:40 to 2026-10-16 14:40 Asia/Kuala_Lumpur, end excluded**.
No silent extension, approval migration or reuse of retired decisions is allowed.

## Exact authorized-if-signed scope

Exactly one future qualification of the same pinned eight-file llama.cpp CPU set
and Qwen3-0.6B Q8_0 GGUF, under the existing MXC / Windows Job binding, using only
the fixed PUBLIC request. The complete executable/DLL membership and hashes,
Host hashes/profile, absolute paths, permissions and exact argv are in the payload.
There is no private input, additional model/backend/runtime, capability
registration, value experiment, remote model/provider call, cloud resource,
paid service, production release or REAL_ADMISSION authorization.

Runtime ZIP SHA256:
`8708a7b81842333927f6377ac3f17ff8bba4dbe1ee0cf28dfd5e7a32e3a46b38`.
GGUF SHA256:
`9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031`.
Prompt file SHA256: `5914939520ed74f16ae23222c1d9b9cdf0c35fc9d1dbee093fe616626dc46f22`.
Effective prompt SHA256 after vendor -f trim:
`307805ac096c27917a711c67211e4ae1eb2f8fb5af9f085a73817a41ad19936a`.

The minimal configuration repair supplies literal framing from the exact GGUF's
one-user/no-tools/non-thinking template branch, retaining the original PUBLIC
request and /no_think. One additional terminal LF compensates the vendor -f trim.
The same ASCII relative path and pinned bin CWD remain. A fixed reverse prompt
`PUBLIC_G6_NATIVE_QUALIFICATION_COMPLETE` stops after actual generated marker
content, without grammar forcing or interaction. The unchanged raw-output rule
still requires stdout.strip() to equal the entire marker exactly. Noise, missing,
wrong, duplicate, prefix/trailing and natural EOG-label output fail.

The previous prompt's omitted declared framing and natural-EOG output protocol
mismatch are source-supported findings. The precise numerical cause of v2 slash
repetition is **not proven**. This new experiment may fail; there is no promised
native PASS or inferred private usefulness.

Exclusive fresh reservation: `output/g6-native-public-once-v3` (absent at preparation).
Its existence or partial state denies reuse. It must never be reset or deleted.
Only verification after the Owner signs may permit this single dispatch.
Completion, failure, cancellation, partial/late output or unknown outcome all
permanently retire the attempt. No automatic retry or authority restoration.

Limits remain unchanged: 2 GiB Job commit, eight processes, 120-second user-CPU
threshold with periodic enforcement, 180-second guarded wall deadline with
bounded termination/drain, 65,536 aggregate retained stdout/stderr bytes, two
requested threads, 1,024 context and 128 output tokens. No zero-overshoot claim.
The exact input/model are read-only; native writes are denied. Output is confined
to bounded local pipes, with network and exporters disabled. No new permission
or input-directory allowance is introduced.

Independent review: **PASS_SIGNING_READINESS**, no remaining material finding.
Public composition: **18/18 PASS_PUBLIC_COMPOSITION_ONLY**, **28/28** C++ checks.
Focused regression: **42/42 PASS**. Affected regression: **147/147 PASS**,
zero SKIP/FAIL/ERROR; focused tests overlap affected tests, not 189 unique tests.
The earlier v23 **17/18 HOLD** is retained; its unknown Host field/component is
not relabeled. No new full repository sweep or real model success is claimed.
G2/G3/G4 remain frozen; N01 remains HOLD; REAL_ADMISSION=NO.

## One personal signing step

The existing GitHub-bound Owner issuer was freshly read back: TDY0225,
user ID 223441940, SSH Signing Key ID 1242636, fingerprint
`SHA256:5FV4/OvvMPzivK/4YIolW2kPQBGoik/llHbviTDpf98`.
Reuse that dedicated key. Do not create/register a new key.
Review the exact scope, then run locally:

```powershell
$g6Payload = 'D:\chatgpt\安装skills\nexus-core-g4-domain-qualification\output\g6-native-owner-signing-v3\decision.json'
if ((Get-FileHash -LiteralPath $g6Payload -Algorithm SHA256).Hash.ToLowerInvariant() -ne '1f819d4d3a7f1508b2dd681b8b35fd4c51415619981a82f925f785101dd6fcd6') { throw 'Payload mismatch; do not sign.' }
& "$env:WINDIR\System32\OpenSSH\ssh-keygen.exe" -Y sign -f "$env:USERPROFILE\NexusG3OwnerSigning\nexus_g3_ed25519" -n nexus-g3-approval-v1 $g6Payload
```

Enter any passphrase only in the native prompt; do not send it or the private key
to Codex. This creates decision.json.sig and does not dispatch anything.
A plaintext approval cannot replace the detached signature. Reply when signed.

Codex must first execute verification only after your reply:

```powershell
Set-Location -LiteralPath 'D:\chatgpt\安装skills\nexus-core-g4-domain-qualification'
& 'D:\DevTools\NexusR2Python\Scripts\python.exe' -X utf8 -c "from ash.g6_native_binding import _verify_native_owner; _verify_native_owner(); print('EXACT_OWNER_SIGNATURE_VERIFIED; NO_DISPATCH')"
```

That existing verifier checks fresh public GitHub identity/key membership,
OpenSSH namespace nexus-g3-approval-v1, principal github-user-223441940, current
material/configuration/review hashes and the fixed window. Only then may the
native guard reserve one fresh attempt and revalidate immediately before resume.
No signed execution material may change under this seal.
