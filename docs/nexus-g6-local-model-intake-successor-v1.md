# G6 local model quarantine intake successor v1

This independently versioned successor implements only the Owner-authorized
preparation scope of canonical proposal SHA256
`2cd5dbfa12dccafc693999960a7e7fb70ca4d1638479af1664a7ee715e3b6af3`.
The explicit Owner instruction authorizes implementation, review and qualification
of this quarantine-only boundary. It is **not authenticated component approval**,
model-use permission, installation, activation or registration authority.
G2/G3/G4 remain COMPLETED/FROZEN; optional G3/N01 research remains HOLD.

## Minimum deterministic gap and reuse

The frozen source policy does not cover the two proposed artifacts or the GGUF
size/format. Do not change that policy, its parser, limits, manifest or states.
The new `config/nexus-g6-local-model-intake-successor-v1.json` pins exactly the
approved two artifact identities and 51 exact runtime archive member identities.
The new `ash/g6_local_model_intake.py` reads those files and returns zero-authority
evidence. No source-wide trust or policy activation is added.

Existing `ecosystem_storage.open_stable_input` provides held local handles,
no-follow path checks, file/ancestor identities, hard-link rejection and final
unchanged checks. Existing bounded JSON and cross-platform path validation are
reused. Hashing, ZIP decompression and binary integer decoding use Python's
standard library. No dependency, scanner service, model loader, generic importer,
generic execution loop or replacement identity system is introduced.

The minimum new properties are exact two-artifact binding, streaming large-blob
verification, flat exact-member ZIP checks and a narrow GGUF structural subset.
OpenAI/Host must not self-assert these byte, size and format properties. Reasoning,
selection and all later execution remain Host responsibilities.

## Closed, inert policy

Policy SHA256 over UTF-8/LF bytes:
`16f8d981adfc798dc5baf1c2b84a6c111f3b60af0b557ce804b4afe7b555de65`.
The reader pins this digest before parsing policy data. Changing an artifact,
revision, member, bound, mode or authority field cannot select a more permissive
policy. A changed policy is a new separately reviewed successor, not a runtime
configuration toggle. Normalizing CRLF for this static policy follows the existing
manifest convention and does not normalize candidate binary bytes.

| Constraint | Fixed value |
| --- | --- |
| Aggregate candidate bytes | At most 700,000,000 |
| One model blob | At most 650,000,000; exact accepted size 639,446,688 |
| Runtime input | Exact accepted size 19,518,618 |
| Expanded runtime | At most 200,000,000; fixed member inventory |
| New trusted origins | None globally; only the two proposal URLs/revisions as inert inputs |
| Authority / execution / registration | NONE / DENY / DENY |
| Existing Slice 3C state | Unchanged; no writes or promotion |

`inspect_quarantined(runtime_path, model_path)` accepts only paths, not an approval
dictionary, subject chosen by the caller, serialized result, grant or executable
command. It opens and verifies both stable files, enforces the aggregate bound,
streams their hashes, inspects the immutable ZIP in memory, checks the model's
structure and revalidates held identities. It performs no acquisition or filesystem
write. A forged result JSON has no consumer that could dispatch or register it.

ZIP inspection rejects missing/extra/duplicate/non-flat or unsafe paths, special
files, unsupported compression, encryption, size/hash differences and excessive
expansion. Every decompressed member is hashed in bounded chunks, never written
as an executable file. Archive membership does not approve a future execution
subset; server/RPC tools remain inert even though they occur in the pinned ZIP.

GGUF inspection is deliberately limited to this little-endian v3 Qwen3 model:
bounded typed metadata, unique keys/names, finite scalars, bounded flat arrays,
1–4-dimensional tensor geometry, F32/F16/Q8_0 byte sizes, quantization version,
alignment, non-overlapping complete spans and zero padding. Unsupported layout
causes HOLD. Tensor weights are not decoded, interpreted, imported or loaded.
The source reference is the official [GGUF specification](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md).
This check is not runtime-model compatibility or native-loader safety certification.

## Host acquisition and provenance evidence

Acquisition is a separately authorized Host operation, outside the read-only
module. The already downloaded runtime is reused; do not acquire it again.
The one model is stored as an inert `.blob` in ignored local output, never in
PATH, a model cache, plugin directory, source package or executable working tree.
Public HTTPS reference/license reads use no account or credential material.

Interrupted acquisition is never treated as a complete artifact. Preserve its
HOLD record, actual prefix length/hash and consumed bytes. A known partial public
blob may be continued only by an exact HTTP 206 Content-Range for its remaining
bytes; do not redownload its prefix, reset counters, accept HTTP 200 as a Range
acknowledgement, or promote the prefix. Complete raw size and pinned SHA256 must
still pass the independent stable-input inspection. Unknown outcomes remain HOLD.
The budget refers to acquired candidate bytes, not repeated local verification
reads; no network billing or bandwidth-cost guarantee is inferred.

Provenance evidence binds the public GitHub release/tag/asset and model repository
revision/LFS object to the two approved pins. Source license bytes and their exact
revision identities are retained as public review evidence. This is not a claim
of independent build attestation, exhaustive dependency-license review or complete
upstream supply-chain security. Those limitations remain explicit for any later use.

## Qualification and execution boundary

Tests are `tests/test_g6_local_model_intake.py`. Small generated inert fixtures
exercise the parser and negative properties; they do not substitute for the two
real pinned artifacts. Actual acquisition, stable readback, model geometry and
archive inventory observations are retained separately in the successor
qualification record. First-pass failures and interrupted acquisition records
are preserved, not rewritten into PASS.

`QUARANTINED_EXACT_BYTES` means the stated inert byte/format checks completed.
The returned record always says execution and registration DENY, privacy and
restriction enforcement NOT_QUALIFIED, loader compatibility NOT_QUALIFIED, fresh
authenticated exact-subject decision REQUIRED_NOT_OBTAINED, and REAL_ADMISSION NO.
These are not configurable by passing an approval or receipt.

Before any candidate executable use, a new independently verified decision from
the already accepted GitHub-bound Owner signing issuer is mandatory. The retired
G3 decision cannot be reused. Current task, Host, G1/G2 eligibility, applicable
registration and complete mandatory controls remain separate obligations. Unknown
privacy, routing, indirect effects or restrictions cause HOLD even if a signature
is valid. No new framework or silent permission expansion may resolve that HOLD.

The original G6 value protocol, substitution, independent review, final regression,
exact Owner release acceptance and release freeze remain later gates. Neither this
successor nor its tests grant them PASS. No new paid service, cloud resource,
private input, model run, authentication ceremony or high-assurance research is
authorized by this implementation.
