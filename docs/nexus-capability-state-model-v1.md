# Nexus Capability Observation Model v1

**Status:** PROPOSED DOCUMENTARY REPORTING SEMANTICS FOR OWNER ACCEPTANCE; no runtime schema/enum or state-machine change.
**Basis:** [Northstar memory](nexus-northstar-demo2-project-memory-v1.md) §§5-6, 8.1-8.4, 10-13 and 22; [lesson register](nexus-northstar-demo2-learned-knowledge-v1.md) K01-K04, K14.

## 1. Four independent observations

The words below are dimensions, not a linear progression. For each, record an observed YES, observed NO, UNKNOWN or NOT APPLICABLE with reason. Absence of evidence yields UNKNOWN, not NO. Evidence strength is separate: source-reported, independently observed, or UNVERIFIED/UNKNOWN. These documentary labels do not replace accepted validator/lifecycle enum values.

| Dimension | Precise meaning | Evidence needed for YES | What YES does not establish |
|---|---|---|---|
| installed | Exact capability/package/tool exists in the declared environment and installation scope at observation time | Scoped filesystem/package/runtime presence and identity/version evidence | Reachable invocation, successful invocation, approval or output influence |
| callable | A valid reachable invocation path for the exact capability exists in the declared Host/session with prerequisites and permitted operation scope | Host/path/tool availability evidence bound to operation, session/environment and time; safe availability check when authorized | Future availability, execution grant, invocation or success; global discovery listing alone is insufficient |
| executed | Evidence establishes an invocation for the relevant operation | Bound invocation/receipt/trace including attempt, actor, input/artifact references, time and outcome; failure is still an executed attempt | Successful effect, application to artifact, acceptance or validated quality |
| applied | Evidence establishes that the operation's output/effect influenced the accepted artifact/state | Trace from identified invocation/output to artifact diff or external effect, subject/config identity and acceptance reference; failed/rejected suggestions do not qualify | General capability quality, authority, complete validation or unrelated backend effects |

No installed -> applied, callable -> applied or configured -> executed inference. Dependencies, secrets and provider mode are separate prerequisites; credentials must not appear in observation records. A native/remote callable capability may have installed NOT APPLICABLE locally, with remote installation UNKNOWN. An executed but failed operation can have applied NO if rejection/non-application is observed, otherwise UNKNOWN. An installation seen later cannot prove a historical invocation.

## 2. Minimum evidence binding and stale records

A documentary observation carries: capability canonical identity and version/digest where available; environment/Host identity and scope; operation and attempt where applicable; capture time and source; dimension and observed value; evidence grade; sanitized evidence references; outcome and limitations; artifact/state digest and acceptance reference for applied. No private environment dumps, passwords, API keys or submitted PII.

Each dimension can have a different observation time and source. Values are not silently advanced. A changed capability, environment, invocation path, artifact or governing acceptance invalidates affected observations; historic facts remain historic. Hash equality proves content identity, not use or trustworthy receipt issuance. If invocation/output attribution cannot be established, applied remains UNKNOWN even when similar code exists.

## 3. Crosswalk to accepted Nexus structures

| Existing structure | Preserved meaning | This proposal's use |
|---|---|---|
| [R5 capability inventory](nexus-runtime-r5-host-capability-inventory.md) | Installed/enabled/visible/loadable/workflow-ready/tool-callable/selected/loaded/executed/validated are distinct; snapshot not authenticated authority | Summarize applicable presence/callability facts without compressing the detailed trace or claiming execution from assessment |
| [R4/R5 execution trace](nexus-runtime-r5-adaptive-enhancement.md) | Selected, loaded_verified, execution_started/outcomes and validation remain separate Host-owned receipts | Reference actual trace for executed, and output/artifact binding plus acceptance for applied; preserve failure/validation states |
| [Slice 3B evaluation](nexus-post-r5-runtime-integration-slice3b.md) | PASS covers declared checks for exact subject digest only; review does not create execution evidence | Record validation independently; no validator PASS -> executed/applied/Host authority |
| [Slice 3C quarantine](nexus-post-r5-runtime-integration-slice3c-adr-pds.md) | Presence, review, approval, routability and execution are separate | Four observations grant none of approval/promotion/activation/routing/installation/execution/delegation authority |
| `ash/capabilities.py` | Existing lifecycle and availability vocabularies remain unchanged | No new runtime enums, automatic transitions or registration |
| [V1.2 context/rules](v1.2-product-architecture-spec.md) and [Pre-G2 A4](nexus-pre-g2-architecture-addendum-v1.md) | Ordinary content is evidence; scoped memory is not an authority or universal memory platform | Small versioned reporting proposal; no persistent observation service or G4 implementation |

Approval, eligibility, loaded instructions, success, validation and permission remain distinct in existing records. No additional new dimension is necessary for this documentary integration. The proposed four dimensions supplement existing detail when useful, not replace it.

## 4. Northstar examples without upgraded evidence

All examples are historical source-reported observations. The integration independently verified source-file identity only; it did not inspect installed Skill directories or rerun the original operations.

| Subject and time scope | installed | callable | executed | applied / limitation |
|---|---|---|---|---|
| Impeccable, Phase 4A | Source reports UNAVAILABLE at planned audit; exact presence observation limited to brief | Source path unavailable | Audit at this gate not established | No application attribution from this gate |
| Impeccable, later Phase 4A.5 / reconstruction | Source reports installation presence/version 0.1.5 | Exact historical executable path/reachability UNVERIFIED | Source says USED; exact invocation/output UNVERIFIED | UNKNOWN for exact finding-to-diff; installation is insufficient |
| UI UX Pro Max / Product Design / Taste | Presence varies by source brief; no universal installed YES | Historic path details UNVERIFIED | Source says USED/advisory; original reports not retained | Detailed contribution UNVERIFIED; resulting CSS is not proof of exact tool use |
| Vercel CLI, Phase 4D.1 | Source reports command and project CLI unavailable | Source reports unavailable path | No CLI deployment established | Human GitHub/Vercel handoff is a separate operation, not CLI applied |
| Demo provider vs HubSpot seam | Adapter code source-reported present | Configured demo route historically exercised; HubSpot live prerequisites deferred | Demo synthetic requests source-reported executed; HubSpot live execution not established | Demo UI/API outcome reported; no CRM/email/PDF effect or production applied claim |

Use the same caution for local builds, a configured public origin and deployment receipts: none alone establishes live backend effects. [Conditional gates](nexus-reusable-project-gates-v1.md) define applicability and five deployment facts separately.

## 5. Acceptance and authority boundary

The conceptual separation is consistent with existing architecture. Adoption of these precise new reporting obligations still awaits owner acceptance. The checkpoint authorizes no engine, installation, provider effect or memory automation. A0-A6/P1-P12 unchanged; pending OpenAI escalation untouched; Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD.
