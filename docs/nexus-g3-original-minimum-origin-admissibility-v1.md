# Original G3 minimum local authorization admissibility v1

Date: 2026-10-14. Status: **BLOCKED_VERIFIED_APPROVAL_ORIGIN_MISSING**.
**G3_NOT_READY_FOR_FREEZE.** This is an inspected and tested development
checkpoint, not a new authority design, approval, registration or milestone freeze.

## Exact task, baseline and historical standard

The current Owner directive requests original Roadmap V2 G3 first, followed by
G6 only after legitimate G3 acceptance. It authorizes ordinary implementation and
qualification but expressly forbids fabricating authority and resuming the frozen
N01/high-assurance path. Its original attachment SHA-256 is retained in the
accompanying evidence record.

Baseline: `a13505729bf719f25aab38ac10440562fdf59220`, accepted G4 tag
`nexus-v2-g4-final`. Qualified G4 implementation remains
`52d77560fc99d45936e3b253f6131449919bd088`. New development branch:
`nexus-v2-g3-original-qualification`.

Sole milestone standard: `docs/nexus-roadmap-v2.md` at
`nexus-roadmap-v2-final`, commit `f92b96ea01b8e32dac8bc1d51819bf0c58d55659`.
G3 fields 4/7/8 require verified issuer and authenticated exact-subject approval
evidence, field 12 requires a verified approval-origin mechanism, and field 15
requires explicit acceptance of its issuer/security boundary. Field 8 explicitly
rejects model-produced approval and creator-writable storage alone as origin.
These requirements predate N01 and do not require its cloud architecture.

## Smallest proposed slice and reuse assessment

The minimum useful slice would observe one repository-owned benign read-only Git
capability, obtain its separately verified exact review decision, project a
registration from that approval, and check current approval/revocation alongside
current eligibility and task authority. It would not add an executor or modify
the production adapter. The selected observed subject is the already accepted
repository-owned `Core Host Git Maintenance v1` Skill; merely observing it does
not approve it through G3 or replay its earlier workflow.

| Existing facility | Reuse | Verified limitation |
| --- | --- | --- |
| `ash/g3_grant_codec.py`, `ash/g3_authorization.py` | EXTEND_EXISTING only after an admissible origin is established; reuse exact bounded identities, scope and validity semantics | Public evaluator intentionally returns `G3_APPROVAL_ORIGIN_UNVERIFIED`; the only positive seam is explicitly TEST_FIXTURE_ONLY |
| `ash/g3_host_approval_bridge.py` | REUSE_WITH_THIN_ADAPTER if a qualified Host origin becomes available | Existing event correlation is `OFFLINE_CONTRACT_ONLY`, `owner_authenticated=false`, `approval_authority=none`; correlation is not authentication |
| `ash/core.py` | REUSE_DIRECT for existing checkpoint, budget, hash, lock and task opt-in mechanics | `--approve <sha>` compares a caller-supplied digest with same-user task data; it is not a verified G3 approval issuer |
| `ash/core_host_loop.py`, planner and Skill discovery/loading | REUSE_DIRECT for accepted bounded execution after its applicable permissions pass | No G3 human-origin or capability-registration service is exposed; existing successful execution does not establish separate approval |
| Existing capability metadata and `updated_revision_state` | REUSE_DIRECT for identity/lifecycle observations | An `approved` label is descriptive metadata, not authenticated approval evidence |
| Frozen Slice 3C subject/policy/quarantine interfaces | REUSE_DIRECT when applicable to the selected subject | Preserve quarantine and zero-authority states; do not edit them to introduce APPROVED |
| Current surfaced Host tools | NOT_QUALIFIED as a G3 issuer from the inspected interfaces | No callable exact-subject human-decision attestation/verifier was exposed. This is a bounded inventory finding, not a claim that every Host facility is incapable |
| Existing code-review tool | NOT_APPLICABLE as an approval source or completed independent review | Its exposed interface reads PR CI diagnostics; no independent G3 review or Owner decision is inferred |

The missing adapter cannot honestly be filled with an `issuer=owner` JSON file,
an implementer-generated signing key, a trusted-looking dataclass, a copied chat
approval or a new boolean supplied by this same implementation. A signature
whose issuer/key binding has not independently been accepted is no improvement
to the origin claim. The current task's general development delegation does not
turn such a new self-declared issuer into an accepted security boundary.

No new module is implemented: at this checkpoint the NEW_REQUIRED authority
boundary cannot be justified or qualified using the available accepted local
facilities. Building a registration API on top of unverified origin would not
complete original G3. A future thin adapter remains possible if an existing
Host/operator source can supply an independently verifiable decision for the
exact subject/scope and an explicitly accepted issuer boundary. This finding is
not a proof that every local solution is impossible and does not prescribe N01,
organizational PKI, a new service or any paid infrastructure.

## Executed evidence and original acceptance disposition

`research/nexus-g3-original-minimum-origin-evidence-v1.json` retains the exact
observed subject identity, reopened source-file hashes, negative observations,
test command/results and original mandate hash. The original verbose test log
is preserved at `output/g3-original-qualification-v1/focused-regression.log`;
its digest is included in the retained record.

- Existing G3 authorization/Host correlation, Core Host Loop and G4 suites:
  **107 PASS / 0 SKIP / 0 FAIL / 0 ERROR**, no new tests or changed assertions.
- Three fresh direct public-evaluator probes used ordinary candidate records
  claiming `owner`, `reviewer` and `test-fixture`, with all supplied eligibility
  flags true. Each returned **NOT_ELIGIBLE / G3_APPROVAL_ORIGIN_UNVERIFIED /
  dispatch_authority=none**. They are intentional untrusted negative probes,
  never issued approvals; the supplied flags are not runtime observations.
- A changed actual Skill-byte digest produced a different subject identity.
  Existing tests separately cover no inherited fixture approval, expiry,
  revocation, forged issuer, scope, wrong subject, source/evidence mismatch,
  replay, quarantine preservation and metadata that cannot become authority.
  Their positive fixture controls remain TEST_FIXTURE_ONLY.

| Original G3 acceptance requirement | Current disposition |
| --- | --- |
| Benign controlled component separately approved and registered | **NOT PROVEN / BLOCKED** before real approval: no qualified approval-origin interface; no real registration is claimed |
| Execution still requires current eligibility and task authority | Existing contracts and Core/Host guards retained; no new G3-positive execution is qualified |
| Changed revision cannot inherit approval | Exact identity and existing deterministic fixture negatives PASS; not promoted to a real approved lifecycle |
| Revocation blocks subsequent eligibility | Existing deterministic fixture tests PASS; real approval-to-revocation linkage remains unqualified without a real approved record |
| Slice 3C stays non-authorizing on negative paths | Existing isolation/candidate negatives PASS; source and frozen history untouched |
| Independent review of origin, binding, revocation and isolation before freeze | **NOT COMPLETED**; unit tests and implementer inspection are not independent final review |

The earliest blocker is the original verified approval origin and accepted
issuer boundary. Positive approval/registration, real revocation linkage and
independent final review remain dependent unproven gates; they are not silently
counted as PASS. No full repository regression is newly claimed or rerun for
this documentary-only checkpoint. Prior G4 full coverage remains historical.

## Rejected expansion and stop boundary

No N01, PREAUTH, OTP/TOTP, Owner login, public-pin review, DynamoDB, S3 custody,
distributed recovery, production binding, admission, new AWS resource or IAM
change was resumed or created. D04 executor exclusion is not reintroduced as
a release gate. The original origin requirement is assessed on its own terms,
not by importing the later U1/N01 requirement matrix wholesale.

G2 and G4 remain **COMPLETED / FROZEN** in their accepted scopes. Historical
G3/N01 research remains **HOLD / OPTIONAL_HIGH_ASSURANCE_RESEARCH**, with its
production checkout and all prior evidence unchanged. Original G3 remains
**INCOMPLETE / NOT READY FOR FREEZE**. G6 preparation is unchanged and its final
qualification is **NOT STARTED**, because this instruction requires G3 freeze
first. **Production adapter DENY; REAL_ADMISSION=NO.**

Stop at this actual mandatory boundary. Do not create `nexus-v2-g3-final`, start
G6, turn fixture authority into real approval, or begin another architecture
program to manufacture completion.
