# G6 native execution readiness: retained HOLD v1

Date: 2026-10-14. This is a readiness disposition, not a new architecture,
component grant, signing request or change to a completed milestone.

The two exact artifacts passed the successor's inert identity/format checks.
That result does not establish a qualified execution binding. The Owner's latest
instruction explicitly authorizes quarantine-only successor preparation and
withholds executable use, installation, activation and registration. A fresh
authenticated exact-subject decision remains mandatory before any executable use.
No such decision has been obtained, and the retired G3 decision remains retired.

## Exact technical property still missing

**A qualified complete execution unit for these exact Windows native artifacts,
with demonstrable local/private data-path and mandatory restriction enforcement.**

The concrete remaining gap is the complete native-model binding, including its
exact data/loader path and applicable task restrictions. Killing the outer MXC
launcher alone did not stop the public main/child canaries. A separate existing
Windows tree-termination command did establish quiescence in one public probe,
as distinguished below. Neither observation qualifies the complete model unit.

This is an original G6 Section E/F-F/A6 requirement. It is not D04 executor
exclusion, N01 recovery, remote production admission or a reason to reopen G3.
Fresh approval can authenticate a decision; it cannot establish unknown Host
controls or native-loader behavior by assertion.

The static ordinary-import review identifies seven archive modules reachable from
`llama-completion.exe`, plus external Windows/VC runtime import names. Dynamic CPU
backend loading, delayed loads, DLL search path, inherited environment, indirect
process/network effects and full routing are not thereby qualified. The archive
contains server/RPC facilities; no execution subset has been approved. Observed
network-related import names do not prove that network traffic occurred, and do
not prove network isolation either. No module was extracted or loaded to test this.

## Bounded existing-Host observations

- The current command Host exposes unrestricted execution. Visibility of a local
  executable or model file is not evidence of a restricted private execution unit.
- `WindowsSandbox.exe` and `wdagtool.exe` were absent at their standard System32
  locations; neither command was started. Observed Windows registry `EditionID`
  is `CoreSingleLanguage`, with `DisplayVersion=26H2`. Its legacy `ProductName`
  string is not used to infer an OS-major-version change.
- Microsoft's [Windows Sandbox documentation](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/)
  explicitly excludes Windows Home from supported editions. No edition upgrade,
  unsupported Home workaround, feature installation or activation is authorized.
- Existing Docker CLI is available, but the previously observed Linux engine
  binding is unavailable. No usable private execution unit for these Windows
  binaries was established. This does not prove that every possible Host is
  unavailable; it is the limit of the inspected existing facilities.
- Public VC runtime files were present at the inspected System32 paths. Existence
  does not qualify their loader binding or the complete execution environment.

### Existing Codex native MXC: a demonstrated reuse path

The separate Windows Sandbox feature is not the only available Host mechanism.
The existing Codex CLI `0.162.0-alpha.17.2`, binary SHA256
`e98c516f1c8935789aabe9122ee7e05ec4c3efd1ba6acf179242e031c495b99e`,
successfully launched its native MXC backend. No installation, OS upgrade,
administrator action, service, account or persistent configuration change was
needed. The backend was explicitly selected with `windows.sandbox="mxc"`, with
managed requirements included and no legacy fallback. This follows the official
[Windows sandbox guidance](https://learn.chatgpt.com/docs/windows/windows-sandbox)
and [permission configuration](https://learn.chatgpt.com/docs/permissions).

The retained third synthetic canary used root-deny, Windows/Python read-only,
one public input directory read-only, one exact standalone public file read-only,
one output directory writable, and network disabled. Both its deterministic
main process and child successfully read declared inputs and wrote declared
outputs, failed to read/write the public out-of-scope fixture, and failed to
connect to a local endpoint whose reachability had a successful positive control.
The listener observed no sandbox connection. No secret path was probed. The
second successful canary used the additional `:minimal` read allowance; the third
removed it and still passed. Neither profile is installed globally.

Initial command-selection/quoting errors and a launcher error 203 with an overly
restricted startup environment are retained. The later working startup passes
only an explicit allowlist of ordinary Windows environment names plus fixed
PATH/TEMP/TMP, without copying provider credentials or proxy configuration.
These first-pass failures are not silently converted to PASS.

This is **Host synthetic-control preflight**, not candidate execution, a model
benchmark, full network-protocol coverage, private-input qualification or
independent security review. It removes the claim that a paid Windows edition
upgrade or a new sandbox framework is necessary. Actual native-loader
compatibility and task-level integration remain unperformed; the next bounded
public qualification requires a fresh exact-subject Owner decision first.

### Lifecycle negative: launcher termination is not process-tree cancellation

The separate public cancellation canary started a deterministic parent and child,
each writing only its own public heartbeat file in the declared output directory.
Both had a fixed 12-second self-lifetime. Both were observed active before the
owned launcher was terminated; no unrelated process was touched. Main/child sizes
were 50/25 bytes before termination, 300/275 bytes after one second, and
1,050/1,025 bytes after four seconds. Thus the ongoing writes were observed late
effects, not a guessed cancellation outcome. The finite fixture later stopped
writing; no candidate/model or private input was involved.

First result: **HOLD_CANCELLATION_NOT_ESTABLISHED**. This proves only that abrupt
launcher termination is insufficient for this inspected invocation. A bounded
search found no process-tree termination implementation in `ash`, `scripts` or
`plugins`. Existing `ash/core_host.py:invoke` admits only current Python script
hooks and terminates its direct child. Do not force a native program into that
incompatible hook contract or rewrite it as part of this successor.

An existing mature OS alternative was then inspected: System32 `taskkill.exe`
with `/PID <owned-launcher-PID> /T /F`, exclusively targeting the probe's owned
process tree. The second probe retained HOLD because its overly strict observation
compared bytes before the termination call with bytes after it: that alone cannot
distinguish legitimate in-flight writes during termination from post-return
effects. It did observe equal sizes one and four seconds later; that result is
retained without silently relabelling it PASS.

A third fresh finite public fixture measured the actual native-call return
boundary. The command returned 0; both files were 150/100 bytes at that return
and stayed exactly 150/100 bytes one and four seconds later. Result:
**PASS_ONE_NATIVE_HOST_CANCELLATION_OBSERVATION**. This is a concrete reuse lead,
not a new process-control framework, universal kill guarantee, complete unknown-
effect reconciliation or candidate execution qualification. Late results during
termination still cannot become accepted output or authorize redispatch.

This finding is confined to the proposed, unqualified native-model binding. It
does not reopen G2, invalidate accepted Core hooks, reintroduce D04 executor
exclusion, or require N01 infrastructure. Unknown/late outcomes must remain
quarantined with no automatic retry. A signature cannot substitute for the still
unqualified complete native/private integration. Do not prepare an allegedly
execution-ready packet or begin a value pilot by promoting public canary results
to candidate qualification.

No other model, runtime build, compatibility layer, image, VM or remote executor
may silently replace the approved artifacts. A Linux runtime build would have a
different artifact identity/format and require a separate exact scope amendment;
the current approval cannot cover it. No such amendment is implemented here.

## Consequence and next admissible step

```text
SUCCESSOR_INERT_BYTE_AND_FORMAT_CHECKS = QUALIFIED_FOR_QUARANTINE_ONLY
EXECUTABLE_ELIGIBILITY = HOLD
COMPLETE_PRIVATE_PATH = NOT_QUALIFIED
MANDATORY_RESTRICTION_ENFORCEMENT = NOT_QUALIFIED
FRESH_AUTHENTICATED_EXACT_SUBJECT_DECISION = NOT_OBTAINED
REGISTRATION = DENY
REAL_ADMISSION = NO
G6_FINAL_FREEZE = NOT_READY
```

Preserve this HOLD. Reuse the demonstrated native Host rather than introduce a
new execution platform. Any proposed next review must pin the actual artifact,
minimal DLL set, Host/profile, public input and resource bounds, and must state
that it authorizes only the specified qualification attempt, conditional on
current mandatory checks. Do not claim unknown loader or private-path properties
already passed. Use the existing GitHub-bound signing issuer; never use plain
text, this report, hashes or old approvals as the authenticated decision. No
unsigned review packet or successful signature alone creates a registration,
dispatch grant or production authority.

The remaining G6 pilot/protocol/comparison, material configuration substitution,
independent security review and exact Owner release acceptance remain outstanding.
No refusal or deterministic-only success substitutes for useful private-model
completion. This disposition changes no frozen G2/G3/G4 evidence and resumes no
G3/N01 research or production-security infrastructure.
