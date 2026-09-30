# Nexus Reusable Conditional Project Gates v1

**Status:** PROPOSED FOR OWNER ACCEPTANCE; documentary catalog only, no gate engine or automatic activation.
**Source:** [Northstar project memory](nexus-northstar-demo2-project-memory-v1.md) and [lesson register](nexus-northstar-demo2-learned-knowledge-v1.md).
**Authority:** none. No deployment, provider activation, installation, capability approval or execution permission.

## 1. Applicability, evidence and result contract

For a future authorized task, select gates against the objective, delivery surface, risks and accepted project contract. Record required checks before claiming acceptance; changing criteria requires a visible authorized disposition. One evidence record can satisfy multiple overlapping checks. Reuse relevant existing receipts instead of creating parallel logs. Optional advice is not mandatory tooling.

A proposed check record contains: gate/check ID and version; applicable surface or reason for non-applicability; exact subject/input/config identity; governing authority reference; observation source/method/time/coverage; result and evidence references; omissions/UNKNOWNs; required follow-up. References are scoped and sanitized; no credentials, raw PII, cookies or broad environment dumps.

Results below are documentary outcomes, not new runtime enum values:

- **PASS:** the applicable declared property is demonstrated for the bound subject and observation scope.
- **FAIL:** observed evidence contradicts the property. No acceptance of that requirement.
- **UNKNOWN:** missing, stale, conflicting or insufficient evidence. No unsupported PASS. Use the existing validator's INSUFFICIENT_EVIDENCE result where its schema requires that vocabulary.
- **NOT APPLICABLE:** a recorded project/surface reason excludes this requirement; absence of a tool or evidence is not a reason to claim non-applicability.

This proposal does not implement changes to [Slice 3B](nexus-post-r5-runtime-integration-slice3b.md) validators or accepted contracts. Hashes bind content, not truth, approval or authority. A mandatory UNKNOWN blocks the related release/activation claim. Optional diagnostics may remain UNKNOWN with an explicit impact/disposition and narrowly scoped acceptance; they never become harmless or proven by disposition. Superior constraints cannot be waived by this catalog.

## 2. Conditional gate catalog

### A. Pre-build / capability — K01, K03-K04, K16

**Applicability:** new implementation or material change depending on capabilities, packages, environment or providers. Pure documentary work selects only relevant evidence/tooling checks.

**Checks/evidence:** requirements-to-capability inventory; dependency availability and change justification; trusted server/client or analogous execution boundary; public/server-only environment classification without values; required provider/secret categories without collection; [independent capability observations](nexus-capability-state-model-v1.md); missing mandatory invocation path and authorized fallback/handoff.

**PASS:** required paths and permitted scope are evidenced, effects/credentials boundaries declared, and each changed dependency justified. **FAIL:** required tool unavailable with no permitted fallback, prohibited dependency or invalid client trust boundary. **UNKNOWN:** name/listing or installed directory alone; environment/authority/boundary not verified. Do not install automatically to satisfy the gate. **Burden limit:** inspect dependencies touched by the task; no full machine inventory or universal Next.js requirement.

### B. Design / content / truthfulness — K02, K06, K12, K20

**Applicability:** public-facing artifact or changes to a project with an accepted design/content contract.

**Checks/evidence:** exact contract and scoped visual/content diff; advisory finding dispositions; placeholder review; claim-to-source mapping for ratings, reviews, certifications, partners, years, contacts and metrics; fictional/demo labeling; copy accurately states active and deferred integrations. Evidence may be accepted owner-supplied business facts with provenance, not invented proof.

**PASS:** applicable contract and factual/effect claims are supported or explicitly fictional where ambiguity would mislead. **FAIL:** fake proof, unsupported live-effect claim or unauthorized drift. **UNKNOWN:** factual claim lacks source or finding-to-change attribution absent. **Burden limit:** no universal ban on gradients/glass/bento/animation, no obligation to run named design advisors or redesign working content. Project style choices stay project-scoped.

### C. Accessibility — K07, K17

**Applicability:** human-facing UI/interactive content. Non-UI APIs/batch tasks can record NOT APPLICABLE with the actual surface reason.

**Checks/evidence:** relevant keyboard routes, visible focus, skip navigation where navigation density warrants it, heading hierarchy, labels and error associations, mobile disclosure/focus return, reduced-motion behavior when motion exists, and touch-target usability. Observe behavior of the actual changed UI, including error/return states. State device/browser/assistive-tech coverage and untested paths; no compliance certification from a checklist.

**PASS:** declared applicable paths work with recorded observation. **FAIL:** keyboard trap, inaccessible control or focus/error regression in required paths. **UNKNOWN:** markup/screenshot alone for behavioral claims or missing applicable motion/assistive evidence. **Burden limit:** representative risk-based paths; touch-size and viewport criteria come from the project, not Northstar constants. No mobile-menu test for a UI without one.

### D. Security / privacy / provider effects — K05-K06, K11-K12, K14-K16, K18-K19

**Applicability:** untrusted inputs, credentials, personal data, server APIs, external providers or effectful operations. Select subchecks for the real interface and threat model.

**Checks/evidence:** content type; origin handling with correct trust assumptions; declared request size limits; malformed JSON and sanitized errors; public output secret/stack scans; scoped PII data flow, recipients, logging, persistence, retention and disposal; duplicate/idempotency behavior; timeouts, aborts, retries and effect reconciliation; explicit demo/live mode and missing/invalid mode disposition. Origin allowlisting alone is not authentication. A UI non-echo check proves only that observed channel, not universal non-retention.

Real provider activation requires separate owner authority and task-specific security/privacy evidence for the exact adapter/configuration. Credentials remain in approved secret handling; presence is not integration success. Where practical, authorized provider-side observation binds effect IDs/status to the attempted operation using sanitized evidence. Mocks test contracts; they cannot prove live writes, delivery, cancellation or cost. If a promised effect cannot be independently established, report UNKNOWN and stop the relevant claim/unsafe retry.

**PASS:** all applicable preconditions and declared observed boundaries are demonstrated; effect claims separately supported. **FAIL:** secret disclosure, unauthorized PII/effect, contradictory retention claim or unsafe blind retry. **UNKNOWN:** external effect/cancellation/persistence unobserved, conflicting duplicates or accounting lag. Local timeout/abort is not remote termination or cost settlement. **Burden limit:** no credentials/provider calls merely to fill evidence gaps; observation remains within current authorization. No universal 409-as-success, body limit or timer.

### E. SEO / release / handoff — K08, K10, K13, K25-K26

**Applicability:** SEO to indexable/public web surfaces; release identity to any published deliverable; local-only work excludes nonexistent remote/deployment stages with reason.

**Checks/evidence:** declared metadata/canonical/social outputs; robots and sitemap inclusion/exclusion where applicable; missing-route status; content-appropriate structured data only when required; source/config identity; change scope and clean/declared-dirty release snapshot; deployment identity model in §3; deployment capability and authorized human/tool handoff. Northstar's five source commits and public alias are historical examples.

**PASS:** required stages have matching or explicitly explained identities and scoped live evidence; handoff actor/actions and returned evidence are bound. **FAIL:** deployed source/config mismatch, unauthorized publication or incorrect public-origin metadata. **UNKNOWN:** build/push alone, inaccessible deployment records or unexplained live binding. A dirty tree cannot support an unqualified clean-commit release claim; intentionally delivered dirty snapshots require explicit acceptance and complete binding. **Burden limit:** no compulsory deploy/tag/push, CLI installation, JSON-LD or indexing for every project.

### F. Acceptance — K07, K09, K13, K15, K17, K24

**Applicability:** closure of an authorized task against its declared deliverable and acceptance criteria.

**Checks/evidence:** relevant route/output matrix, responsive contexts, API smoke cases, console observations, form success/invalid states, deployment behavior if publication is in scope, required evidence coverage, unresolved diagnostics and exclusions. Synthetic reserved data is used only in authorized operations; a synthetic public submission can still cause provider effects and requires permission. Record exact tested subject, configuration, environment and time.

**PASS:** all mandatory applicable criteria are evidenced and the conclusion is limited to that coverage. **FAIL:** observed failure in a mandatory criterion. **UNKNOWN:** unobserved production/provider/performance requirement, missing mandatory proof or conflicting receipts. **Burden limit:** build correctness can be sufficient for a build-only task; no invented browser/live requirement. Live portfolio QA does not qualify a Host or establish security/budget/cancellation guarantees for G2.

## 3. Five-fact deployment identity proposal

No stage implies the next. This is a small reporting record, not a deployment runtime or guarantee that a dashboard label is trusted attestation.

| Fact | Sufficient scoped evidence | Insufficient substitute / limitations |
|---|---|---|
| LOCAL SOURCE | Local repository identity, full commit and status/diff; if dirty, complete accepted snapshot identity | Short SHA or clean claim without status; not remote evidence |
| REMOTE SOURCE | Authorized remote ref readback with repository/ref/full commit and capture time | Local tracking ref can be stale; local commit or successful push alone |
| DEPLOYMENT SOURCE | Authorized deployment record binding deployment ID/environment to full source commit and relevant build/config revision; inspect available provenance | Remote commit alone; unbound successful dashboard label; provider record assurance must be stated |
| CONFIGURED ORIGIN | Authorized config readback for exact deployment/environment and intended origin, sanitized | Environment value alone does not show the public alias reaches this deployment |
| OBSERVED LIVE STATE | Authorized responses/browser observations at intended origin, routes/behavior/metadata, deployment linkage and time | A live URL or UI alone cannot prove which SHA or backend effect it serves |

Missing linkage remains UNKNOWN; release conclusion names tested facts and missing assurance. Aliases and immutable deployment URLs are distinct. Numeric performance and provider-side effects require their own evidence. Historical Northstar reported matching facts; this integration has not rechecked the live chain.

## 4. Promotion, invalidation and cost of checks

Every candidate check maps to K IDs and source sections. Owner acceptance may adopt only justified applicable checks; acceptance does not authorize providers, publication or execution. Changes to subject, relevant configuration, governing criteria or evidence provenance invalidate affected results. Prefer existing receipts and bounded representative checks. Discard proposed gates that add bureaucracy without a concrete safety, truthfulness or quality obligation; never discard a superior mandatory invariant.

This is neither G4 implementation/qualification nor a new [V1.2 Rules Engine](v1.2-product-architecture-spec.md). A later implementation requires its own accepted scope and schemas. Pending OpenAI escalation and G2 governance remain unchanged: Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD; A0-A6/P1-P12 unchanged.
