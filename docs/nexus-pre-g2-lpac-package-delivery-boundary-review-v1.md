# Nexus Pre-G2 LPAC Package Delivery Boundary: Adversarial Design Review v1

Review date: 27 September 2026
Subject: `docs/nexus-pre-g2-lpac-package-delivery-boundary-decision-v1.md`
Review disposition: **ACCEPTABLE AS WRITTEN as a proposed architecture decision only**

This is a distinct adversarial review pass over the completed proposal and accepted repository contracts, performed in the same work session. It is **not** a second human review, owner acceptance, implementation approval, local qualification result, or proof that the proposed C: boundary works on this Host. The review tested whether the proposal has falsifiable STOP conditions; it did not exercise filesystem creation or an LPAC process.

## Sources and boundaries checked

- Accepted `docs/nexus-pre-g2-architecture-addendum-v1.md` A0–A6 and `docs/nexus-pre-g2-architecture-acceptance-v1.md`.
- Accepted `docs/nexus-pre-g2-appcontainer-architecture-alternative-v1.md`, its acceptance record, and the accepted trusted-launch HOLD record. These files remain unchanged.
- Current external `04-observer-implementation-design-v2.md`, `05-local-qualification-protocol-v2.md`, `06-adversarial-review-round2.md`, 43-entry manifest and fixed controller/watchdog/probe/recovery source. The old package remains preparation-only.
- Read-only ACL chain from `D:\` to the old package: `Authenticated Users` has Modify (mask `0x1301BF`) on every relevant component and all 45 checked package/manifest-sidecar files; `CodexSandboxUsers` or equivalent has Modify under the shared workspace. The `output` component is owned by `CodexSandboxOffline`, not De Yong. Modify includes `DELETE` and write data; the old path therefore fails the delivery-boundary gate. No ACL was changed.
- Read-only candidate chain `C:\`, `C:\Users`, `C:\Users\De Yong`: no reparse point was observed, and the protected profile-root DACL grants De Yong Full Control without broad write. The proposed descendant does not yet exist; its effective ACL remains UNKNOWN.

## Independent adversarial checks

| Attack or contradiction tested | Result and required future evidence |
| --- | --- |
| Treating the mutable D: build tree as trusted | Rejected. The old manifest remains historical; only newly reviewed and rehashed staged bytes can be authorized. |
| Using the new C: root while still running old hard-coded D: paths | Rejected. Controller, watchdog, recovery, offline PDB utility, probe negative target, module/TCB inventory source columns and all generated binaries/manifest must be rebound or explicitly proven unchanged. A zero-stale-literal check is required. |
| Moving a package without rebuilding changed executables | Rejected. Exact source/build/PE/manifest review and staged destination rehash are required. |
| Protecting only files while a parent can rename/delete the package | Rejected. Every path component, target `DELETE`, parent `DELETE_CHILD`, file ID and reparse status must pass; otherwise STOP. |
| Inheriting owner-profile or sandbox ACEs | Rejected. Protected new-root/package/evidence DACLs, effective readback and no unrelated write/delete/read of owner-only material are mandatory. The C: profile snapshot does not prove the descendant DACL. |
| Reparse, junction or alternate-stream substitution | Rejected at staging and release. Exact canonical object/volume IDs and reparse checks are required; no fallback path. |
| Staging from an untrusted source with a passing source hash | Insufficient. The owner must hash the destination after copy and bind it to a separately reviewed new manifest/digest. |
| Replacing an artifact after verification | Protected whole path plus held stable objects, immediate release recheck and actual loaded-image/dependency binding are mandatory. The controller's self-hash alone cannot PASS. |
| Forging or replacing owner receipts | Separate owner-only evidence root, fixed `CREATE_NEW` paths, monotonic/process binding and cross-record OS-side reconciliation are required. A secret-free reviewer copy is nonauthoritative and cannot justify widening original ACLs. Child output remains corroboration. |
| Assuming a Start-menu shell is outside all Jobs | Rejected. Controller and watchdog each query their actual process; any outer Job STOPs before qualification child creation. No breakaway flag. |
| Introducing elevation or a broker through one-time setup | Rejected. De Yong Full Control on the observed profile root suggests non-elevated creation; real setup remains a gate. Elevation, new privilege, password transfer, Task Scheduler or service would require a separate decision. Runtime remains non-elevated. |
| Confusing local LPAC, network LPAC, E2B and G2 | Rejected. The proposal preserves empty capability, no provider use and distinct authorization/qualification gates. Option D and G2 HOLD remain current. |

## Corrections made during this review

The proposal's promotion section was tightened to name the probe's exact old negative-access target and the module/TCB inventory files containing old-root source paths. “Source-hash report” was corrected to “self-binary-hash report.” A nonauthoritative, secret-free reviewer-copy rule was added so a later Codex review cannot be used to widen the owner-only evidence ACL. These were documentary precision corrections only; no accepted invariant, source file, binary or filesystem ACL changed. The corrected proposal was reread against the full checklist above. No further required document change was found.

## Residual UNKNOWNs and disposition

Actual creation of the proposed C: root by the non-elevated owner, descendant DACL/owner readback, ancestor and target effective delete/rename rights at implementation time, same-process loaded controller image proof, staged dependency closure, future Windows/PDB identity, effective LPAC isolation, watchdog/Job behavior and cleanup all remain UNKNOWN. Every such mandatory fact has a STOP gate before it could be promoted. If the owner-controlled path or loaded-image binding cannot be demonstrated without elevation or a new trusted component, the implementer must return for a separate versioned decision; this review does not authorize a workaround.

**ACCEPTABLE AS WRITTEN** means the corrected proposal is sufficiently precise for separate owner architecture acceptance review. It does not authorize root creation, ACL changes, staging, rebuilding, executing any of the four scenarios, E2B or G2 implementation. No positive Host binding exists; G2 remains HOLD.
