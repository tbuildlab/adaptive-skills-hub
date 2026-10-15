# G6 exact Owner signing package v1

Approval: **NOT_OBTAINED**. Codex has not signed or executed this package.

Canonical payload SHA256:
`2c60341e61cc652acc26ff4697ecd1ed4ebe0c693901f51bdd03f2fb67579a9a`.
Encoding: sorted compact UTF-8 JSON plus one LF, all covered by the hash/signature.
Signing file: `output/g6-native-owner-signing-v1/decision.json`.
Retained identical copy: `research/nexus-g6-native-owner-decision-v1.json`.

Exact subject:
`nexus.g3.subject.v1:b0a8371112e00c8eaced6ceb3631974d1e765cbf6e4f91d1452ac81097af4b19`.
Component digest: `737180602c473d5dbe981ab920545535e92e088225f7fc0ba69b5a273fb352ff`.
Configuration digest: `e2067e9cfcce8e5d0a43b9da457a06fe9eecb7bb85c233b5d776682bb9b2d58c`.
Independent review digest: `2c9a983aa8c07f74d233142c2ed37a72ee682de4c50aec9bb768c961dee0e2ca`.

Fixed validity: **2026-10-15 10:00 to 2026-10-16 10:00 Asia/Kuala_Lumpur**,
end excluded (02:00 UTC on each date). No silent extension or old decision reuse.

## Exact scope

One real native qualification using the fixed **public** prompt only. After a
fresh authenticated signature, reserve the exact local attempt exclusively;
revalidate the pinned quarantine artifacts; materialize only eight exact native
members plus license data; write the fixed public prompt; run the exact MXC/Job
invocation once; retain bounded local output; then retire the attempt on completion,
failure, cancellation or unknown outcome. Existing/partial reservations deny.

The prompt requests only `PUBLIC_G6_NATIVE_QUALIFICATION_COMPLETE`, with `/no_think`.
This does not authorize private input, capability registration, value experiments,
installation beyond this exact local subset, any other model/backend, cloud
resources, paid services, production release or REAL_ADMISSION.

Runtime ZIP: `8708a7b81842333927f6377ac3f17ff8bba4dbe1ee0cf28dfd5e7a32e3a46b38`.
GGUF: `9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031`.
The payload contains every native member hash, two trusted Host hashes, exact
absolute argv, read-only input/model paths and disabled network/export settings.
Native files total 14,157,312 bytes. Limits: 2 GiB job commit, eight processes,
120-second user-CPU threshold, 180-second guarded wall deadline, 65,536 combined
retained stdout/stderr bytes, two requested threads, 1,024 context and 128 output
tokens. CPU enforcement is periodic; wall-time initiates bounded termination and
cleanup, not zero scheduling overshoot. Inert preparation retains intake bounds.

Independent reviewer `/root/g6_binding_independent_review` returned
`PASS_SIGNING_READINESS`; public composition is 13/13 PASS. Neither result proves
actual model execution, private usefulness or G6 completion. G2/G3/G4 remain
frozen, N01 research remains HOLD, and REAL_ADMISSION remains NO.

## Minimum personal Owner step

Existing issuer: GitHub TDY0225, user ID 223441940, Signing Key ID 1242636.
Fingerprint: `SHA256:5FV4/OvvMPzivK/4YIolW2kPQBGoik/llHbviTDpf98`.
Current public account/key membership was checked. No key generation or GitHub
registration needs repeating. Review this exact scope, then personally run:

```powershell
$g6Payload = 'D:\chatgpt\安装skills\nexus-core-g4-domain-qualification\output\g6-native-owner-signing-v1\decision.json'
if ((Get-FileHash -LiteralPath $g6Payload -Algorithm SHA256).Hash.ToLowerInvariant() -ne '2c60341e61cc652acc26ff4697ecd1ed4ebe0c693901f51bdd03f2fb67579a9a') { throw 'Payload mismatch; do not sign.' }
& "$env:WINDIR\System32\OpenSSH\ssh-keygen.exe" -Y sign -f "$env:USERPROFILE\NexusG3OwnerSigning\nexus_g3_ed25519" -n nexus-g3-approval-v1 $g6Payload
```

Enter the passphrase only in the native prompt, if asked; never send it or the
private key to Codex. The command creates `decision.json.sig` beside the payload
and does not run the candidate. Reply that signing is complete.

Codex will execute this verification-only command after your reply:

```powershell
Set-Location -LiteralPath 'D:\chatgpt\安装skills\nexus-core-g4-domain-qualification'
& 'D:\DevTools\NexusR2Python\Scripts\python.exe' -X utf8 -c "from ash.g6_native_binding import _verify_native_owner; _verify_native_owner(); print('EXACT_OWNER_SIGNATURE_VERIFIED; NO_DISPATCH')"
```

It reuses native OpenSSH `-Y verify`, fixed principal `github-user-223441940`,
namespace `nexus-g3-approval-v1`, binary payload stdin and fresh GitHub membership.
It performs no materialization or dispatch. Plaintext approval, unsigned JSON,
fixture records and this document cannot replace authenticated verification.
