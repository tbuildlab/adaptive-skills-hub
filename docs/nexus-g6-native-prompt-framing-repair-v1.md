# G6 v2 native-output diagnosis and fixed PUBLIC protocol repair v1

The first and second native attempts remain QUARANTINE / RETIRED. All 28 retained
files are byte-identical. No candidate executable/DLL or model runtime was invoked
in this task, and no private input was processed. Integrity hashes read the public
artifact bytes; the separate metadata parser reads the header only, decodes no
tensor values and instantiates no model. REAL_ADMISSION remains NO.

## Evidence and causal limits

V2 stdout has 127 slashes with line endings, no required marker; stderr records
13 input tokens and a 128-token generation cap. Exit code 0 did not qualify it.
Pinned completion source proves `-no-cnv` bypasses chat formatting and tokenizes
raw prompt bytes with special-token parsing. The exact GGUF declares Qwen3
Instruct and its ChatML user/assistant boundary. The previous naked request lacked
that declared framing. This is a demonstrated configuration omission. The precise
numerical cause of the slash loop is **not proven**, and no future model response
is guaranteed by this static/public evidence.

The EOS metadata is 151645 (`<|im_end|>`), with `<|im_start|>` 151644; the logged
128247 `</s>` control-type warning concerns a different token and is not treated
as the root cause or used to change tokenizer/EOS settings. Metadata and provenance
still match the exact pinned 9465e63... artifact; no model replacement is proposed.

The same completion source writes ` [end of text]` to stdout on natural EOG.
That would correctly fail the existing marker-only acceptance. Its fixed reverse
prompt option stops after actual generated marker output and does not force
sampling or enable interaction. Raw-output equality remains unchanged.

## Smallest bounded repair

1. Retain the original PUBLIC user request and `/no_think`; wrap it as the exact
   model template's fixed one-user/no-tools/generation/non-thinking branch.
2. Keep `-no-cnv` and the prior exact ASCII relative file path. Supply literal
   framing bytes, with one extra terminal LF compensating the vendor -f callback.
   No template engine, Jinja execution, generic prompt API or new runtime exists.
3. Add only fixed `-r PUBLIC_G6_NATIVE_QUALIFICATION_COMPLETE`. Public tests show
   prompt-history cannot trigger this stop prematurely. The marker must actually
   appear as the complete raw result; prefixes, missing/wrong/trailing output,
   duplicated markers and EOG labels still reject. No grammar forces the answer.
4. Use fresh v3 subject/packet/review/reservation identity after a new signature.
   The old decisions and directories cannot be reused. No native v3 reservation
   or signing package existed when this qualification record was created.

## Public evidence and first-failure preservation

Fresh public composition: **18/18 PASS_PUBLIC_COMPOSITION_ONLY**, including
28 native C++ path/framing checks and four marker result cases. These are public
fixtures, not model/private usefulness or a successful native attempt. Same MXC,
Job assignment, limits, handle allowlist, filesystem/environment restrictions,
bounded local collection and disabled network/exporters remain shared.

The first v23 suite stays **17/18 HOLD**. Its first foreground startup hit the
unchanged 16-second bound before fixture output; subsequent post-yield Host
identity validation raised a closed failure. The original record did not retain
which component/field changed, and that remains unknown. It is not retrospectively
called harmless, not attributed to framing, and not turned PASS.

The minimal diagnostic correction retains a primary outcome such as TIMEOUT,
plus allowlisted failure/component identifiers and boolean identity differences.
Every original Host identity field and every deadline remains enforced. Unit
negatives independently alter all five identity dimensions and require denial.
A diagnostic-only fresh fixture passed; its numeric-handle reuse observations
cannot establish stable-file mutation. The final uninstrumented full suite is
retained separately at `output/g6-native-binding-public-v24/qualification.json`.

Metadata-observation wording was clarified: full-file hashing reads raw public
artifact bytes, while only the metadata parser avoids tensor data. The original
unclarified observation is retained locally. No model inference occurred.

Focused and affected current-source results are retained under
`output/g6-v3-framing-regression-v2`. A final whole-repository sweep belongs after
remaining actual G6 mandatory qualifications; none is claimed by this repair.
The next signing package may be created only after independent review and exact
signing-readiness audit. G2/G3/G4 remain frozen, G5 remains disabled, N01 remains
optional research HOLD, and production adapters/REAL_ADMISSION remain DENY/NO.

## Sources

- [Pinned completion control and output flow](https://github.com/ggml-org/llama.cpp/blob/fcac19079f3f2985fe74ed845f0880e7e9a8030a/tools/completion/completion.cpp).
- [Pinned -f and reverse-prompt options](https://github.com/ggml-org/llama.cpp/blob/fcac19079f3f2985fe74ed845f0880e7e9a8030a/common/arg.cpp).
- Exact model metadata observation: `output/g6-v2-marker-diagnosis-v1/public-gguf-metadata.json`.
- Closed diagnosis: `research/nexus-g6-native-prompt-diagnosis-v1.json`.
- Fixed prompt contract: `research/nexus-g6-fixed-prompt-contract-v1.json`.
