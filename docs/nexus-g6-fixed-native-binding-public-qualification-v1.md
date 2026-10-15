# G6 fixed native binding: public composition qualification v1

This additive G6 work does not reopen G2/G3/G4 or resume N01/high-assurance
research. It creates no registration, production grant or release authority.
REAL_ADMISSION remains NO. The existing Core Python hook contract is unchanged.

## Scope and reuse

`ash/g6_native_binding.py` contains one internal guarded runner with two closed
roles. The public role uses a finite repository-owned Python fixture. The native
role consumes the exact eight-member llama.cpp subset and the already pinned
GGUF through a fixed plan, and refuses before materialization without a fresh
exact-subject signature from the existing GitHub-bound Owner issuer. It is not
an arbitrary-command runner or an agent/process-control framework.

Existing MXC performs isolation. Windows Job Objects provide native resource and
process-tree lifecycle controls. Existing intake supplies pinned format/identity
validation; stable file handles, Core atomic writes, hash and safe-path helpers
are reused. No saved Host configuration, account, service, VM or sandbox was
created. The old G3 decision remains retired and is not accepted by this gate.

The native role is not executed by the qualification harness. Its preparation
code, reachable only after fresh signature verification and exclusive attempt
reservation, selects exactly eight archive members plus license data. Current
held inputs are rehashed, unknown loader files are rejected, and the exact model
blob and fixed public qualification prompt are read-only. No inference occurs
while inspecting the inert archive/GGUF.

## Fixed boundaries

- Exact Codex CLI and command-runner hashes; explicitly selected MXC, managed
  requirements included, no legacy fallback.
- Root-deny; read-only System32 runtime exception, exact bin, model and prompt.
  The Python installation allowance belongs only to the public role.
- CWD equals the sealed bin. PATH is fixed both in the launcher environment and
  `shell_environment_policy.set.PATH`; setting only the parent PATH was observed
  insufficient and is retained as a first-pass failure. GGML/HF/LLAMA/proxy and
  credential variables are excluded by an explicit environment-name allowlist.
  OMP threads are fixed at two. No environment values are logged.
- Exactly stdin NUL and two stdout/stderr write handles are in the inherited
  handle list. An intentionally inheritable public sentinel is excluded. The
  sole anonymous Job handle is noninheritable, with no breakaway flags.
- CreateProcess starts suspended; Job assignment and limit readback precede
  ResumeThread. Both roles use this same code path and collector.
- Native plan: 2 GiB job commit limit, eight processes, 120-second user-CPU
  threshold, 180-second wall deadline, 65,536 combined retained stdout/stderr
  bytes, two requested model threads, 1,024 context and 128 output tokens.
- Windows user-CPU enforcement is periodic. The observed one-second test
  threshold overshot before OS termination; it is not an exact zero-overshoot
  CPU promise. Wall deadlines initiate Job termination, followed by bounded
  quiescence/drain cleanup. These are distinct limits.
- The local collector retains at most 65,536 bytes combined, in 4 KiB reads;
  excess output triggers quarantine and tree termination. No unbounded
  communicate(), raw stderr logging, generic JSON passthrough or raw output
  return to the conversation is used.
- Analytics, feedback, OTel log/trace/metrics exporters, prompt export, hooks
  and notification commands are disabled per invocation. Native command network
  access is disabled. This is command isolation, not a new global policy over
  every Codex service surface.
- Missing authority, startup/guard error, unknown/partial/trailing output,
  timeout, cancellation and nonzero results quarantine. The exclusive attempt
  directory prevents automatic retry/restart; audit records never restore
  authority. Partial audit bytes are preserved on reconciliation.

## Public evidence and first-pass preservation

The retained suites distinguish public composition from actual native/model
qualification. The current full composition contains thirteen cases: exact
file/backend/environment/network/handle checks; stdout and stderr overflow;
nonzero and partial output; timeout; cancellation; CPU, memory and process limits;
trailing bytes after a completion declaration; and controller failure. Successful
public results are not native execution evidence or production authority.

The loader probe copies the trusted public Windows `version.dll` as fixture data,
loads only its declared exact path, and rejects an unlisted copy. No candidate DLL
is loaded. The cancellation/timeout cases wait for a main/child readiness record;
the earlier startup-only observations are preserved separately. Controller death
is tested by terminating only the owned controller and observing both previously
live fixture processes become signalled.

First-pass failures under `output/g6-native-binding-public-v1` through `v14` are
retained. These include a legitimate installed-Host hardlink, unrequested Job
readback fields, output creation under stable parent locks, invalid-handle canary
diagnostics, child PATH rewriting, a non-exercising late-output fixture and a
too-small public DLL read bound. None becomes a retrospective PASS. Installed
trusted Host hardlinks are held against mutation with existing Windows handle
primitives; the candidate/input hardlink policy is unchanged.

Initial independent review by `/root/g6_binding_independent_review` returned HOLD:
the native plan was disconnected from the public guard, and cancellation evidence
covered startup only. Initial scope digest:
`793fe94ff1191b302139c3f377eea9a432d5884320bea1deee0fee3406ba8ff4`.
Initial reviewed public v14 record SHA256:
`7fa2769c8721c8683e377a9ff48b7398bb5311595ac50c568e7e8c408bc7335d`.
The corrected revision must receive a separate independent readback; the first
review cannot be silently migrated to later bytes.

Final independent readback is retained in
`research/nexus-g6-fixed-native-independent-review-v1.json` with decision
`PASS_SIGNING_READINESS`, scope SHA256
`fe403b77fd50b518af346c7030effd75acd425e7542c976a0d6f4e6489d9dd0f`.
Current public evidence is retained in
`research/nexus-g6-fixed-native-public-qualification-v1.json`, SHA256
`29d2ed9965b4d5e3d88b2fac05997dfcd1f36ea7884a6eaefb564b5b5e1eafa2`.
Source-revision overlap in v17/v18 caused controller-probe HOLD; those records
remain retained. The final runner rejects changed already-loaded source, and v19
source stayed fixed during its complete suite. No native/Owner attempt was replayed.

No Owner signing payload is justified until the corrected mandatory controls and
independent review pass. Any resulting payload authorizes at most one real native
qualification, conditional on current exact bindings. It is not a full G6 pass,
useful private completion, value experiment, capability registration or release.

## Primary references

- [Official OpenAI Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox).
- [Official OpenAI permissions](https://learn.chatgpt.com/docs/permissions).
- [Official OpenAI shell environment and telemetry configuration](https://learn.chatgpt.com/docs/config-file/config-advanced).
- [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).
- [CPython inherited handle list](https://docs.python.org/3.12/library/subprocess.html).
