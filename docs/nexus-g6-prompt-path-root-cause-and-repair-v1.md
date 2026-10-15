# G6 public prompt file-open diagnosis and minimal repair v1

The retired first native attempt is unchanged. All fourteen files, including its
original audit, candidate subset, public prompt and raw output, match the retained
pre-diagnosis SHA256 inventory. No candidate program/DLL or model was executed
or loaded in this diagnostic task; no private input or consumed Owner decision
was used. REAL_ADMISSION remains NO. G2/G3/G4 remain frozen and N01 remains HOLD.

## Proven root cause

The pinned vendor revision converts Windows argv to UTF-8, then the `-f` / `--file`
handler passes that narrow filename to `std::ifstream`. With the observed Windows
ACP 1252, the Chinese directory component in the absolute path is interpreted
using an incompatible code page. Opening fails before prompt content is read.
The original error identifies this exact argument/file-open stage.

A finite repo-owned C++ executable reproduces the same narrow filename operation
inside the existing MXC and preassigned Windows Job. It can read the **original
exact retired prompt path** through CreateFileW, while narrow UTF-8 std::ifstream
returns ENOENT (2) for that same path. An identical public copy gives the same
crossover. The path is only 102 characters, so MAX_PATH is not the explanation.
The successful wide read of identical bytes under the same exact-file allowance
rules out a missing file or missing read permission as this failure's cause.

The public probe is compiled with the installed MSVC x64 compiler, static CRT,
and no candidate/runtime/model dependency. Its only direct PE import is KERNEL32.
Its source and binary are pinned and inputs rehashed under held stable handles.
This is a surrogate for the source-proven filename operation, not an execution
of the vendor parser, candidate binary, model or full inference path.

## Seven requested checks

| Boundary | Retained public evidence |
|---|---|
| Exact absolute input | Wide API reads the original exact approved file; UTF-8 narrow open reports ENOENT |
| Relative path / CWD | ASCII relative paths read the identical prompt from pinned bin CWD; incorrect CWD denies; absolute wide read still works after CWD change |
| Quoting / separators | A quoted argument containing spaces arrives intact and reads; relative slash/backslash/dot forms read; changing absolute separators does not cure the encoding mismatch |
| Encoding / BOM / newline | LF and text-mode CRLF read identically; UTF-8 BOM remains content and does not prevent opening; original PUBLIC bytes are unchanged |
| Handles / ACL / MXC | Exactly three inherited stdio handles, pipe output, excluded sentinel, exact-file read, unlisted/outside read denial and write denial; no Python or model allowance for the C++ probe |
| Actual -f semantics | Pinned source: UTF-8 argv -> narrow file reader -> prompt bytes -> remove one terminal LF; -f and --file share the same callback |
| Equivalent bounded fix | Actual repaired plan's `-f ../input/task.txt` is passed into the C++ probe and reads the expected fixed public prompt |

The sentinel inspection handles only STATUS_INVALID_HANDLE, matching the prior
public Python fixture's narrow negative handling. Other exceptions still fail.
No file/network/loader/authority check was removed or weakened.

## Minimal repair

Keep the same fixed CWD, held prompt bytes, exact absolute-file read allowance,
argv structure and budgets. Change only the prompt filename passed to `-f` to
ASCII `../input/task.txt`. Before launch, require that resolving it from the
pinned bin CWD equals the exact held input. No parent-directory allowance is
added. A literal `-p` is supported by the vendor but is not selected: the relative
filename retains existing file delivery and newline semantics.

Versioning the future reservation/packet/review to v2 prevents old-decision or
retired-directory reuse. The v2 native directory does not yet exist. This is
not permission for a second attempt. A new packet may be prepared only after
independent signing-readiness review and relevant regression; actual dispatch
still needs a new authenticated exact-subject Owner signature.

## Qualification and preservation

Current public suite: **14/14 PASS_PUBLIC_COMPOSITION_ONLY**, including all
24 path checks and the prior lifecycle/resource/negative cases. Current focused
binding/intake regression: **36/36 PASS**. The affected regression is recorded
separately when complete. No new full repository sweep or G6 acceptance is
claimed here.

Original outputs remain under `output/g6-native-binding-public-v22`;
LF-normalized retained metadata is
`research/nexus-g6-fixed-native-public-qualification-v2.json`.
The full root-cause inventory is
`research/nexus-g6-prompt-path-root-cause-v1.json`.

First-pass v20's partial CWD-restore result and v21's invalid-handle fixture
exception remain HOLD with their raw bytes and source snapshots retained.
They are not retrospectively relabelled PASS. The first real native attempt
remains QUARANTINE / RETIRED, with no replay, reset or replacement execution.
Public success does not establish model loading, inference, private usefulness,
capability registration, release authority or G6 completion.

## Primary references

- [Pinned llama.cpp argument reader and Windows argv conversion](https://github.com/ggml-org/llama.cpp/blob/fcac19079f3f2985fe74ed845f0880e7e9a8030a/common/arg.cpp).
- [Microsoft narrow and wide file opening semantics](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/fopen-wfopen?view=msvc-170).
- [Official OpenAI Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox).
