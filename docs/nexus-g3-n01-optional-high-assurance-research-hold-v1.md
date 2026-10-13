# G3/N01 optional high-assurance research HOLD checkpoint v1

Owner direction: 2026-10-13, freeze production qualification and return development
focus to the Nexus core product. This is a research freeze, not a production release
or a successful security qualification.

| Field | Frozen disposition |
| --- | --- |
| Preserved production-qualification HEAD | `a7b2ec93c31f19a398f7662fe3ad601d39b73d7c` |
| Preserved branch | `nexus-v2-production-qualification` |
| G3 production qualification | HOLD / OPTIONAL_HIGH_ASSURANCE_RESEARCH |
| N01 production qualification | HOLD / OPTIONAL_HIGH_ASSURANCE_RESEARCH |
| G3/N01 live closure | NOT_ACHIEVED |
| Resource disposition | HOLD_NO_RECREATION |
| Deterministic ledger continuation | NOT_PROVEN |
| D01 | CLOSED, historical accepted scope preserved |
| D03 | CLOSED, historical bounded qualification preserved |
| G4 / G6 | COMPLETE_PREPARATION_FAIL_CLOSED, unchanged |
| REAL_ADMISSION | NO |
| Active development focus | NEXUS_CORE_PRODUCT |

The research snapshot is a separate descendant commit on
`nexus-g3-n01-research-hold`, with research-only tag
`nexus-g3-n01-research-hold-v1`. Neither moves the preserved production branch,
changes its checked-out HEAD, updates main, nor overwrites a historical tag.
The final Git receipt identifies the new snapshot commit; this record avoids a
circular self-commit hash. This tag does not qualify a release or enable admission.

## Preservation

Preserve every existing tracked evidence/checkpoint/review/test byte and its Git
history. Include the completed resource/lifecycle HOLD analysis and four associated
evidence files in the separate research snapshot. The exact pre-freeze 713-entry
working-tree MANIFEST is copied to
`research/nexus-g3-n01-hold-preserved-manifest-v1.json`; the accepted HEAD's
708-entry MANIFEST remains available at its original Git revision. The new static
manifest adds documentary files without changing existing source/evidence entries.

Existing ignored output, native records, regression logs, artifacts and diagnostic
results remain in place. They are not cleaned, rewritten, replayed or promoted to
authority. The freeze is a Git source/evidence checkpoint, not a claim that ignored
local output has been copied into Git or that external retention lasts forever.
Existing R Compliance retention remains on its original terms; no AWS operation
or retention change is part of this freeze.

The analysis records contiguous R checkpoint 0-10, the exact IDs/digests of
7/8/9/10, epoch 6, old incarnation/source bindings, historical QUARANTINE, and
the unresolved primary FINALIZED/pending and cumulative accounting gaps.
Historical live and offline results retain their original classifications.
No unknown result becomes PASS. No authority, budget, counter, sequence, epoch,
incarnation or lifecycle generation is reset.

## Execution stop boundary

No DynamoDB or other AWS creation/recreation; no ledger hydration; no checkpoint
7/8/9/10 replay; no v7 public-pin review; no new artifact/process/source/R binding;
no PREAUTH, LOGIN, OTP/TOTP, provider send, real admission, or production release.
Expired review windows remain expired. No automatic continuation, renewal,
retry, research scheduling or resource cleanup is commissioned by this freeze.

Production qualification can resume only after a new explicit Owner instruction.
Distributed custody, immutable-ledger recovery, remote production admission,
enterprise zero-trust and new production-security architecture are outside active
core work. Historical D04 executor exclusion is not added as a release gate.

## Core product direction

Use the [core resumption plan](nexus-core-product-resumption-plan-v1.md).
Product flow: user task -> Nexus planner -> select Skill/Agent role -> Host/local
execution -> verify actual result -> return finished result and concise evidence.

Reuse OpenAI/Codex/Host for intelligence, tools and execution. Keep existing
Nexus selection, scope checks and result validation. Ordinary authorized safe
work should not require repeated human approval; dangerous or genuinely missing
authority remains subject to Host approval. This direction does not modify the
old local-hook approval contract or bypass a production G3/G4/G6 gate.
No core implementation or large redesign is started by this documentary freeze.
