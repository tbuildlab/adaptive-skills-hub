# Nexus G2 Host Qualification Evidence Successor Protocol v1 — Adversarial Design Review

Review date: 27 September 2026

Subject: `docs/nexus-g2-host-qualification-evidence-successor-protocol-v1.md`

Subject SHA-256: `e8fa13931355e562a83cfb4c40444a11c1245fc5140440871903a6d4c1e37843`
Result: **ACCEPTABLE AS WRITTEN FOR OWNER ARCHITECTURE/PROTOCOL REVIEW — NOT ACCEPTED, IMPLEMENTED OR QUALIFIED**

This is a separate adversarial **document** pass in the same work session, not an independent human or subagent opinion. It checked the final proposal against the accepted Scope & Exit Decision and acceptance record, current local protocol v3, Owner Release amendment/acceptance/specification, accepted AppContainer and Package Delivery boundaries, Pre-G2 A0–A6, G1/Roadmap and the saved negative/UNKNOWN observations. No qualification binary, profile, process, scenario, credential, network or E2B resource was used. The subject SHA binds the reviewed bytes and is not an owner approval or runtime receipt.

## 1. Under-securing challenge

| Attack or accidental state | Finding on the final text |
| --- | --- |
| `GetProcessHandleCount` zero is mistaken for absence of inherited authority. | §2.1 requires independently recorded `bInheritHandles=FALSE`, no standard streams/handle list, same returned suspended process, a bounded process-DACL/duplication window, a pre-release count **or classified nonzero inventory**, later relevant-handle inventory and negative cases. Count-only cannot PASS. Whether this complete composition works on actual LPAC remains UNKNOWN. |
| An unrelated principal injects/duplicates a handle after the count and before release. | §2.1 explicitly requires independent process security/effective-rights readback and custody across that interval; an unbounded window STOPs. A verified trusted owner or SYSTEM remains in the declared TCB rather than hidden in a claimed universal race-free proof. |
| A harmless Windows-created pre-resume handle is treated as a secret or an impossible zero-table gate is recreated. | The corrected final text permits a nonzero count **only** with complete independent pre-release identity/type/access/origin classification. Unclassified state STOPs; merely nonzero is not declared a security FAIL. This avoids preserving PSS timing as an end in itself. |
| A post-release PSS walk is misrepresented as pre-release provenance, or the loader runs untrusted application code before observation. | §2.1 separates noninheritance from effective later capability state and requires a demonstrated safe barrier before any relevant application operation. No API name or postrun snapshot by itself supplies the ordering proof. If the barrier cannot be shown, STOP/new architecture decision. |
| A hash/path/signature is attached to a different image than the one actually executing. | §2.2 binds held physical object, reviewed bytes, same-process load event/file ID/mapping, process handle/PID/creation time and ordering. Nexus-controlled executable sections retain the accepted stronger PE-normalized mapped comparison. Null/unresolvable event handles STOP. |
| A malicious DLL is labeled “Windows system” to bypass Nexus-controlled byte checks. | §2.2 requires a canonical protected Windows component, physical file ID, exact OS build/inventory and applicable Windows trust basis bound to the actual mapping; writable, unexpected or unresolved physical images STOP. The Windows TCB does not cover attacker-selected code merely because its filename resembles a system module. |
| The unexplained `fothk` differences are silently accepted. | The proposal does not explain or bless them. It changes the proof boundary **only after** a separately accepted bounded Owner Release architecture amendment. Until then the current comparator STOP controls. The declared residual is Windows loader/CI mapping inside the accepted TCB. |
| The watchdog's prehash and self-authored ready line are treated as evidence of independent crash cleanup. | §2.3 requires actual-loaded identity, trusted pre-child readiness and live independence before child creation, plus forced controller-loss/stall observations. Temporary debug-and-detach is explicitly a candidate whose process/order/crash semantics remain UNKNOWN; it cannot relax the verifier's controller attachment. |
| The owner-release verifier accepts a forged child record or becomes a generic executor. | §2.4 fixes the four-case command surface, protected package, own token/no-Job, same-process OS facts, controller/recovery observation, owner-only new records, and continuous cross-check. It has no arbitrary executable, provider or Agent role and cannot attest itself by self-hash. |
| A local process exit is equated with no orphan or with provider settlement. | §2.7 requires Job count, original PID plus creation time, process-tree reconciliation and owner/OS-side zero-live readback. It explicitly excludes remote cancellation/cost inference. |
| The proposed document itself is used as authority to bypass current PSS or mapped-byte STOP. | §§1, 3 and 5 require separately reviewed owner acceptance and an Owner Release bounded architecture amendment for the system comparator; exact bytes and scenario execution need later releases. Historical rules remain in force meanwhile. |

## 2. Over-engineering challenge

| Proposed or tempting work | Finite result |
| --- | --- |
| Require zero physical handles at every time or complete arbitrary Windows kernel-handle instrumentation. | Rejected. HQ3 requires no unauthorized inherited/security-relevant authority. A supported bounded pre-release composition plus relevant later classification is enough; if it cannot be observed, STOP rather than add a driver or broker. |
| Reverse-engineer every Windows loader rewrite, or demand raw mapped==disk for system DLLs. | Rejected inside the explicitly accepted Windows TCB, while maintaining actual physical system-image identity and OS trust. Because accepted Owner Release text presently promises stronger raw comparison, only an express amendment can change it. |
| Turn the 247-file/694-name static candidate list into an ever-expanding qualification inventory. | Rejected. It guides review, while actually loaded executable edges must be closed. Unknown actual edge STOPs; speculative unused candidates are diagnostic. |
| Add a verifier of the watchdog verifier, signing infrastructure, generic launcher or privileged service. | Rejected. Existing owner/package/Windows trust roots and fixed actors close the intended chain. A concrete uncovered threat would require another owner-reviewed architecture decision. |
| Treat Codex-path CI refusal as a machine-wide policy mandate. | Rejected. §2.5 requires an actual final-byte owner-path result under unchanged policy. Owner-path behavior remains UNKNOWN; broad policy management is not a local qualification criterion. |
| Extend this local successor to HQ6 or G2 orchestration. | Rejected. Local HQ1–HQ5 evidence cannot prove remote authority, hard budget/cost enforcement, checkpoint references or reconciliation. Positive Host binding remains separate and absent. |

## 3. Corrections during the design/review loop

The first pass found two bounded drafting risks. First, an unconditional zero pre-resume handle count would recreate an overstrict timing gate and reject harmless OS-opened state; §2.1 and its traceability row now permit only a **completely classified** nonzero state, with STOP if classification is unavailable. Second, generic “configured CI observation” might be read as a required per-module success event, which Windows need not emit; §2.2 now calls for measured policy/enforcement state and the applicable system-image trust basis, and makes a null load-event file handle STOP until a separately reviewed OS-backed same-mapping resolution exists. The final subject SHA above was computed after these corrections. A second pass found no remaining document-level requirement that silently weakens HQ1–HQ5 or expands them beyond the accepted finite boundary.

## 4. Residual UNKNOWNs and exact acceptance boundary

- A supported **actual LPAC** pre-release count/inventory, safe first loader barrier, full relevant post-release handle classification and negative detection have not been demonstrated. PSS returned status 24 at the old fixed-target timing; this is not proof of LPAC outcome.
- Same-process loaded-image event ordering, null-handle resolution, mapped Nexus code comparison and dynamic dependency closure are not qualified on the final Host. The system-module alternative still needs an **explicit Owner Release architecture amendment** and independent acceptance; `fothk` provenance is historically unexplained.
- A temporary controller debug observation of the watchdog, explicit watchdog-only detach, pre-child readiness and survival across controller/verifier loss are technically UNKNOWN. If its lifecycle cannot satisfy the accepted fail-safe, STOP rather than add another verifier.
- Final exact binaries' CI behavior in an ordinary non-elevated owner shell, no-outer-Job facts there, protected successor package bytes, all four scenario results and zero-live cleanup are UNKNOWN. The observed Codex-path CI block and outer Job are not owner-path PASS or FAIL.
- Network-capable LPAC, E2B/provider controls, HQ6, positive complete Host binding and G2 remain outside this proposal. Local qualification is not an inherited authorization for any of them.

**Disposition: ACCEPTABLE AS WRITTEN FOR OWNER REVIEW.** This is a falsifiable bounded design with explicit STOP branches, not a claim that the mechanisms will work on this Windows Host. Owner acceptance would have to identify this exact protocol SHA, accept a bounded successor to the Owner Release mapped-byte promise, and preserve the historical protocol until governed supersession. Implementation and exact-byte package authorization would still be separate. If the finite handle or watchdog observation cannot be implemented under the accepted TCB, the precise affected blocker requires a new architecture decision. Scenario 01–04 remain **NOT RUN**; positive Host binding is **ABSENT**; G2 remains **HOLD**.
