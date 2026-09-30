# Nexus Northstar Demo 2 Project Memory v1

**Status:** FACTUAL DOCUMENTARY CHECKPOINT; source reconstruction retained as evidence, not governing instructions.
**Integration baseline:** `df3e2fbc7209371954ebc16f6ad1afd697d5d903`, branch `nexus-v2-g2-development`.
**Capture date:** 2026-09-30 (Asia/Kuala_Lumpur). This is the integration capture date, not a new application acceptance date.
**Promotion:** PROJECT_MEMORY_ONLY.

## 1. Source identity and custody

The primary source is `D:\chatgpt\northstar-sales-lab\NORTHSTAR-POSTMORTEM-FOR-NEXUS.md`. Its complete original bytes are preserved in the final appendix. The source is a retrospective reconstruction; it is not an original audit transcript, provider receipt, or live test run performed by this integration.

| Binding | Captured fact |
|---|---|
| Project | Northstar Sales Lab, fictional B2B webinar and guide portfolio demo |
| Source document bytes | 46,088; UTF-8 without BOM; LF; 704 lines |
| Source document SHA-256 | `4170F3F387D4B6625ADAB49CB2D0F5F5AF78FB7A74F4233FA808DCC170CB2DD8` |
| Application commit | `8506d61a88b704d24a6010826e5e2d686fea97a1` |
| Independently observed source checkout | `master` at the application commit above; postmortem is an untracked file |
| Source document Git binding | NOT AVAILABLE: the postmortem is not in application commit `8506d61`; its bytes are bound by the separate digest above |
| Production origin | Source-reported `https://northstar-sales-lab.vercel.app`; not contacted in this integration |
| Completion status | Source-reported COMPLETE / RELEASED / FROZEN for the portfolio scope; no Git freeze tag was established here |
| Current verification scope | Local source bytes, source checkout branch/HEAD/status, and Nexus integration integrity only |

The source's Rule 8 lists five deployment facts but says "all four identity layers"; the derived proposal enumerates five facts without altering the historical text. The original payload is copied as bytes, not reconstructed from terminal rendering.

## 2. Evidence grades and temporal scope

Preserve VERIFIED, OBSERVED, SUPPORTED, UNVERIFIED, UNKNOWN, NOT AVAILABLE and NOT APPLICABLE as source grades. Also retain compound source grades such as PARTIALLY VERIFIED and VERIFIED WITH UNKNOWN WARNING DETAIL. A source-reported VERIFIED result remains a historical claim with the coverage the source describes. It does not mean independently reverified today.

| Area / source section | Historical evidence retained | Integration limitation |
|---|---|---|
| Architecture and implementation, §§4, 7, 24 | Source reports VERIFIED App Router boundaries, typed content, validation and provider seams | No Northstar source implementation, dependency or release changes made |
| Design, §§7, 9, 20 | Accepted editorial direction and controlled polish | Gradients, glass, bento and animation exclusions are project preferences |
| Skill/tool use, §§5, 6, 10-13 | Source lists USED; installation and phase briefs support presence/use claims | Original reports and exact invocations are missing; detailed execution and finding-to-diff attribution remain UNVERIFIED |
| Accessibility, forms and responsive behavior, §§14, 19, 24 | Source reports VERIFIED live keyboard/focus/form checks and zero measured horizontal overflow at 375/768/1024/1440 px | Historical route/interaction coverage only; no universal accessibility certification or fresh browser QA |
| API/security, §§15, 19 | Source reports 415/400/403/200 boundary tests, sanitized errors and headers | Tested boundaries do not prove every security property or provider effect |
| Privacy/demo, §§16, 19, 24 | Source reports explicit demo disclosures and no test email in URL/confirmation output | UI and code evidence do not prove absence of platform logging, transport processing or provider retention outside observed scope |
| Release, §§18, 19, 24 | Source reports matching local/remote/application deployment SHA, configured origin and public acceptance | No remote fetch, provider dashboard readback or live revalidation here |
| Performance, §§8.6, 17, 24 | Numeric artifacts absent; §8.6 uses UNVERIFIED and final status uses UNKNOWN | Preserve both original grades; aggregate quantitative-performance result UNKNOWN, no invented score |
| Vercel warnings, §§8.5, 19 | Two warnings; logs NOT AVAILABLE; detail UNKNOWN | No observed release-blocking symptom is not proof warnings are harmless |
| Structured data, §§17, 20 | No JSON-LD; source marks not applicable in scope; historical rationale UNVERIFIED | No invented rejection rationale or universal JSON-LD requirement |
| Real production integrations, §21 | Deferred CRM/email/PDF/analytics/Turnstile/operations | Configured seams and credentials cannot establish execution or delivery |

Source §24 describes a clean released application repository. At this capture, the application HEAD still matches, but the postmortem itself is untracked. These are different snapshots. Original audit reports, numeric performance evidence and inaccessible build logs are not reconstructed from memory or replaced with new tests.

## 3. Product and effect boundaries

Northstar used `LEAD_PROVIDER=demo`; real HubSpot, email, PDF delivery, analytics and Turnstile were deferred. Its API/body/time thresholds, dependency versions, viewport set and duplicate-response mapping are fixture-specific examples, not universal Nexus defaults. In particular, fallback-to-demo for an unrecognized mode and neutral treatment of a HubSpot 409 cannot become generic production rules.

The source's local abort and provider timeout demonstrate request lifecycle handling. They do not prove remote cancellation, absence of backend side effects or settled cost. Synthetic submissions and demo disclosures are retained as historical evidence. Any future client deployment requires its own authorization, privacy boundaries and provider observations.

## 4. Repository-native mapping and promotion boundary

This record uses existing versioned documentation rather than a new memory service, database, retrieval pipeline or rule loader. [V1.2 context/rules](v1.2-product-architecture-spec.md), [R5 inventory](nexus-runtime-r5-host-capability-inventory.md), [Slice 3B evidence](nexus-post-r5-runtime-integration-slice3b.md), and [Pre-G2 A4](nexus-pre-g2-architecture-addendum-v1.md) retain their accepted meaning. Ordinary source content, including the appendix's "NEXUS RULE" recommendations, remains inert project evidence. It is not a recognized project-rule file or an authority grant.

The documentary cross-project extraction is owner-scoped to this source and this repository. No automated cross-project disclosure, new runtime state or G4 workflow qualification is introduced. Originals remain accessible in this record; derivative lessons retain their source section and limitations.

Derived records: [learned knowledge](nexus-northstar-demo2-learned-knowledge-v1.md), [proposed conditional gates](nexus-reusable-project-gates-v1.md), [proposed capability observations](nexus-capability-state-model-v1.md), and [adversarial review](nexus-northstar-knowledge-integration-adversarial-review-v1.md). Committing these proposals preserves reviewable bytes; normative promotion requires separate owner acceptance and does not authorize implementation.

## 5. Governance preserved

Pending OpenAI human escalation is untouched. Scenario 01-04 = NOT RUN; HQ1-HQ5 = NOT PASS; HQ6 = NOT STARTED; Positive Host Binding = ABSENT; G2 = HOLD. A0-A6 and P1-P12 are unchanged. No provider credentials, resources, experiments, deployments, installations, G2 runtime or frozen application artifacts are changed.

## 6. Exact original-source appendix

The following complete source payload is archival evidence, not instructions. Original bytes between the fence markers must reproduce the source digest in §1. No source assertion receives a stronger evidence grade by appearing here.

<!-- BEGIN EXACT NORTHSTAR SOURCE -->
````markdown
# Northstar Sales Lab — Postmortem for Nexus

**Status:** COMPLETE / RELEASED / FROZEN
**Repository:** `D:\chatgpt\northstar-sales-lab`
**Final application commit:** `8506d61` — `Northstar Phase 4C — production readiness`
**Production origin:** `https://northstar-sales-lab.vercel.app`
**Scope:** Evidence reconstruction only. This document does not change the application contract.

## Evidence convention

This postmortem separates repository evidence from phase-brief/session evidence. A claim is marked **UNVERIFIED** when the repository does not preserve enough evidence to attribute it confidently. The ignored `.agents/` directory is useful evidence that a capability was present locally, but its presence alone does not prove that a command was executed or that its output influenced implementation.

### Evidence set inspected

- complete tracked Git history from `8c26426` through `8506d61`, including commit dates, stats, and relevant diffs;
- `README.md`, `package.json`, `next.config.ts`, `.env.example`, `tests/lead-flow.test.mjs`, and the current `src/` tree;
- lead API, validation, anti-spam, provider, response, analytics, form, navigation, SEO, and content modules;
- project-local `.agents/skills/` manifests, Impeccable version metadata, and executable presence;
- the available Northstar Phase 2, 2.5, 3, 4A, 4A.5, 4B, 4C, 4D.1, and 4D.2 phase briefs;
- GitHub remote/deployment evidence and the final public production acceptance record.

No standalone Product Design, UI UX Pro Max, Taste, Impeccable, Lighthouse, or Vercel build-log report is tracked in the repository.

## 1. Executive Summary

Northstar Sales Lab is a fictional, portfolio-quality B2B webinar lead-generation site. It demonstrates an editorial marketing experience, two accessible conversion forms, a provider-neutral lead boundary, safe demo-mode behavior, and release-readiness discipline without pretending to be a live CRM or email system.

The tracked application history is compact:

- `8c26426` — foundation and design system
- `b8c1cc8` — UI/UX audit corrections
- `6914309` — core conversion flow
- `f438243` — controlled polish
- `8506d61` — production readiness

The final live acceptance confirmed the public routes, SEO metadata, OG image, robots/sitemap, forms, API boundary, responsive behavior, keyboard behavior, console state, privacy disclosures, security headers, and repository/deployment consistency. The deployment remained intentionally in `LEAD_PROVIDER=demo` mode. No HubSpot record, email, PDF, analytics vendor, or real personal-data workflow was activated.

The most reusable lesson for Nexus is that a small, explicit product contract plus evidence gates produced a more trustworthy result than broad visual or infrastructure expansion would have done. The main weaknesses were not application defects at release; they were evidence-management weaknesses: audit outputs were not committed, some capability attribution is not reproducible from the repository, Vercel CLI access was unavailable, and two Vercel dashboard warnings could not be classified because their logs were inaccessible.

## 2. Project Scope

### Intended product

Northstar presents a fictional 45-minute sales-coaching webinar for founders, sales managers, and small B2B teams. It also presents a fictional “7 Follow-Up Frameworks” field guide.

### Included routes

- `/` — webinar landing page and webinar registration
- `/follow-up-frameworks` — field-guide landing page and guide request
- `/thank-you?source=webinar|guide|unknown` — source-aware confirmation shell
- `/privacy` — plain-language portfolio-demo privacy notice
- `/robots.txt` and `/sitemap.xml` — crawl controls and public route map
- `/opengraph-image` — generated social image
- branded 404 route

### Explicitly outside scope

- live HubSpot activation
- real email or PDF delivery
- analytics-vendor activation
- production Turnstile configuration
- customer accounts, payments, or dashboards
- fabricated testimonials, customer logos, revenue claims, attendee counts, or certifications
- a custom domain or unrelated Vercel products

The README and the final thank-you screens state the demo limitations directly. This was a portfolio demonstration, not a disguised production business system.

## 3. Development Timeline

The dates below come from Git commit metadata. Phase 1 planning and the audit-only stages did not create tracked application commits; their exact internal artifacts are therefore not reconstructible from Git alone.

| Stage | Evidence | Date | What changed |
|---|---|---:|---|
| Phase 1 | Phase brief/session evidence; no tracked commit | UNVERIFIED | Product, architecture, design, conversion, and release constraints were established. |
| Phase 2 | `8c26426` | 2026-09-16 | Created the Next.js App Router foundation, editorial design tokens, pages, components, content modules, initial form/provider seam, environment example, lint/build setup, and dependencies. |
| Phase 2.5 | `b8c1cc8` | 2026-09-16 | Applied the recorded UI/UX audit corrections: CSS refinement, form copy/semantics adjustments, header changes, and icon treatment. |
| Phase 3 | `6914309` | 2026-09-23 | Added the complete conversion flow, client form lifecycle, API boundary, Zod validation, providers, anti-spam foundation, response guard, analytics contract, thank-you source handling, and tests. |
| Phase 4A | Audit-only phase brief; no application commit | UNVERIFIED | Product, UX, UI, accessibility, responsive, and frontend design advisors were compared before implementation. Detailed report is not stored in the repository. |
| Phase 4A.5 | Audit-only phase brief; no application commit | UNVERIFIED | Impeccable was made available locally for a separate audit. Exact command output is not stored in the repository. |
| Phase 4B | `f438243` | 2026-09-23 | Applied a small, controlled polish slice. The tracked diff is limited to the reusable `MobileNav` client component and header integration. |
| Phase 4C | `8506d61` | 2026-09-23 | Hardened production metadata, canonical origin handling, robots, sitemap, OG image, 404 behavior, security headers, environment documentation, and production-readiness copy. |
| Phase 4D.1 | GitHub/Vercel release evidence; no application commit | 2026-09-29 | Added the intended GitHub remote, pushed existing `master`, verified local/remote SHA equality, and required manual Vercel setup when local Vercel capability was unavailable. |
| Phase 4D.2 | Live acceptance evidence; no application commit | 2026-09-30 | Validated the stable production domain and the final release candidate against the public deployment. |

The repository contains no tag or branch that represents an additional hidden product phase. Phase labels beyond the five application commits are process gates, not invented code checkpoints.

## 4. Architecture

### Application structure

The app uses Next.js App Router with React and TypeScript. Pages remain server-rendered by default. The main client boundary is `src/components/forms/LeadForm.tsx`, where browser state, validation feedback, fetch timeout behavior, and navigation are required. `src/components/layout/MobileNav.tsx` is also a client component because Escape handling and focus restoration require browser interaction.

Content is separated into `src/content/site.ts`, `src/content/webinar.ts`, and `src/content/lead-magnet.ts`. Reusable layout pieces live under `src/components/layout`; marketing primitives live under `src/components/marketing`.

### Conversion boundary

`POST /api/leads` performs the following sequence:

1. enforce JSON content type;
2. enforce an origin allow-list derived from the request and configured site origin;
3. enforce an 8,192-byte body limit;
4. parse JSON with a sanitized 400 response;
5. validate the strict Zod schema;
6. evaluate honeypot, timing, and optional Turnstile controls;
7. call the selected provider;
8. return a stable, narrow success or error shape.

The provider interface is implemented by `DemoLeadProvider` and `HubSpotLeadProvider`. `getLeadProvider()` selects HubSpot only when `LEAD_PROVIDER=hubspot`; every other value falls back to the demo provider. The portfolio deployment intentionally used `LEAD_PROVIDER=demo`.

### Dependency boundary

The production dependency set is deliberately small: Next.js `16.3.5`, React `19.2.8`, React DOM `19.2.8`, and Zod `4.6.5`; TypeScript, ESLint, Tailwind PostCSS, and type packages remain development dependencies. No animation library, CRM SDK, analytics SDK, or email SDK was added.

## 5. Skills and Tools Actually Used

| Capability | Status | Evidence and limitation |
|---|---|---|
| Codex | **USED** | The tracked commits, implementation, tests, release checks, and live acceptance were produced through the Codex workflow. |
| Git | **USED** | Five application commits, clean-state gates, diff checks, remote tracking, and SHA verification are directly reproducible. |
| GitHub | **USED** | The repository `TDY0225/northstar-sales-lab` was created, `master` was pushed, and the remote SHA matched `8506d61`. GitHub’s Vercel deployment record also reported the source SHA and Production success. |
| Vercel | **USED** | The final deployment and environment configuration were performed through the Vercel release path. Local Vercel CLI capability was unavailable in Phase 4D.1, so user intervention was required. |
| Browser/live QA | **USED** | The final public deployment was checked for route behavior, metadata, form states, API outcomes, responsive widths, keyboard behavior, focus, and console state. |
| UI UX Pro Max | **USED** | Phase 2.5/4A briefs explicitly record installation and advisory use. The repository preserves resulting implementation but not the original report or exact command transcript; tool-to-change attribution is therefore partly **UNVERIFIED**. |
| Product Design | **USED** | Phase 4A records Product Design as an advisor. No standalone report is committed, so exact findings are **UNVERIFIED**. |
| Taste | **USED** | Phase 4A records Taste as an advisor. No standalone report is committed, so exact findings and executable output are **UNVERIFIED**. |
| Impeccable | **USED** | Phase 4A.5 records a separate Impeccable-only audit, and a project-local installation exists at `.agents/skills/impeccable` with version `0.1.5`. Exact invocation/output is not tracked, so executable audit details are **UNVERIFIED**. |
| Next.js / React / TypeScript / Zod | **USED** | Directly visible in `package.json` and the source architecture. |
| Automated tests | **USED** | `tests/lead-flow.test.mjs` contains five focused tests; the final release run passed 5/5. |

Tool presence was not treated as tool authority. The approved product/design contract remained authoritative over advisory output.

## 6. Skills Considered / Rejected / Unavailable

- **Impeccable in Phase 4A:** **UNAVAILABLE** according to the Phase 4A brief. This led to the separate Phase 4A.5 availability/audit gate. The later project-local artifact proves installation presence, not every historical invocation.
- **Local Vercel CLI:** **UNAVAILABLE** in Phase 4D.1. A direct availability check found no `vercel` command and no project-local Vercel CLI. The release stopped until the repository and deployment could be handled through the user’s GitHub/Vercel path.
- **Real HubSpot, email delivery, analytics vendor, and Turnstile:** **DEFERRED**, not accidentally omitted. The code contains boundaries, not active credentials or live calls in demo mode.
- **GSAP, screenshot-to-code, Refero, Galaxy, Bencho, and `awesome-design-md`:** **NOT USED / UNVERIFIED**. No package, source import, committed report, or release evidence shows that these capabilities influenced Northstar.
- **New dependencies:** **REJECTED** unless justified by the conversion flow. The final package manifest contains no unnecessary provider, animation, analytics, or UI library additions.
- **Design-advisor authority:** **REJECTED** as a process model. The Phase 4A brief explicitly treated the four review systems as advisors; none could override the accepted Northstar contract.

## 7. What Worked

### 7.1 Observation: the design contract was preserved

**Why it worked:** The project kept a recognizable editorial B2B direction instead of drifting into generic SaaS styling. The palette, type pairing, dividers, spacing, and CTA hierarchy are centralized in `globals.css` and content/layout primitives.

**Evidence:** `8c26426`, `b8c1cc8`, and `6914309` preserve Newsreader, Manrope, `#F6F4EE`, `#112628`, `#1E4B47`, `#A43B2B`, `#596768`, and `#C8D1CA`. Phase 4B explicitly states that no redesign was authorized.

**Nexus lesson:** Freeze a product/design contract before advisory tools run, and require evidence before allowing a review to expand the visual scope.

### 7.2 Observation: the conversion flow used a provider-neutral seam

**Why it worked:** The UI and API do not need to know whether a future provider is demo or HubSpot. This made the portfolio demo honest while keeping a credible path to a separately approved integration.

**Evidence:** `src/lib/leads/provider.ts` defines `LeadProvider`, `DemoLeadProvider`, `HubSpotLeadProvider`, and `getLeadProvider()`.

**Nexus lesson:** Build provider-neutral contracts before adding credentials or vendor-specific UI behavior.

### 7.3 Observation: validation was shared and normalized

**Why it worked:** Client and server use the same schema shape, while the API remains the final trust boundary. Email normalization, strict object parsing, bounded optional fields, and field-error extraction prevent UI-only validation from becoming a security assumption.

**Evidence:** `src/lib/leads/validation.ts` and `src/app/api/leads/route.ts`; the test normalizes `BUYER@EXAMPLE.COM` and rejects malformed input.

**Nexus lesson:** Treat shared schemas as a consistency tool, never as a replacement for server-side validation.

### 7.4 Observation: demo behavior stayed truthful

**Why it worked:** The site demonstrates the interaction without claiming a delivery system that does not exist. Thank-you copy explicitly says that no personal data/email was stored or sent in demo mode.

**Evidence:** README, `ThankYouContent.tsx`, `lead-magnet.ts`, the demo provider response, and final live acceptance.

**Nexus lesson:** A demo-mode boundary should be a first-class product state with visible copy, not a hidden implementation detail.

### 7.5 Observation: accessibility hardening was implemented as behavior

**Why it worked:** Focus management, error summaries, semantic labels, native FAQ disclosure, skip links, and mobile Escape behavior were encoded in components instead of left as audit prose.

**Evidence:** `LeadForm.tsx`, `MobileNav.tsx`, `ThankYouContent.tsx`, `globals.css`, and the live keyboard/focus checks.

**Nexus lesson:** Accessibility gates should assert interaction outcomes, not only inspect static markup.

### 7.6 Observation: production metadata was centralized

**Why it worked:** `getSiteOrigin()` prevents canonical, sitemap, robots, and social URL logic from drifting independently. The final environment made the public domain explicit.

**Evidence:** `src/lib/site-url.ts`, `layout.tsx`, `robots.ts`, `sitemap.ts`, `.env.example`, and Phase 4D.2 live metadata checks.

**Nexus lesson:** Production origin configuration should be an explicit release gate with route-level assertions.

### 7.7 Observation: release checkpoints were preserved

**Why it worked:** Every resume instruction treated the existing checkpoint as valuable. No history rewrite, reset, force-push, or source change was used to conceal unfinished work.

**Evidence:** Git history remains linear from `8c26426` through `8506d61`; final `master` and `origin/master` are equal.

**Nexus lesson:** A release workflow must make “inspect first, preserve valid work, stop on unexpected state” the default behavior.

## 8. What Failed or Was Missed

### 8.1 Problem: audit evidence was not persisted in the repository

**How it was discovered:** Git history contains the application commits but no committed Phase 4A/4A.5 audit reports. The ignored `.agents/` directory contains tool files, not the review outputs.

**Impact:** A later agent cannot reproduce which specific Product Design, UI UX Pro Max, Taste, or Impeccable finding caused each small change. Attribution is partly **UNVERIFIED**.

**Fix:** The application was not changed retroactively. This postmortem records the gap explicitly.

**Validation:** Commit diffs and `git log -- .agents` show no tracked audit artifacts.

**Nexus lesson:** Every advisory audit should emit a small, immutable evidence record containing tool status, command, findings, disposition, and implementation link.

### 8.2 Problem: Impeccable was unavailable at the first audit gate

**How it was discovered:** The Phase 4A brief records `Impeccable: NOT AVAILABLE`; Phase 4A.5 exists solely to make it available and run a separate audit.

**Impact:** The audit sequence needed an additional controlled phase and could not honestly claim four-system coverage at the original gate.

**Fix:** A project-local Impeccable installation was made available before Phase 4A.5. No redesign was authorized.

**Validation:** `.agents/skills/impeccable` exists with executable files and version `0.1.5`; the exact historical command output remains **UNVERIFIED**.

**Nexus lesson:** Capability inventory must happen before promising multi-system coverage. Missing capability should create a bounded hold, not a fabricated PASS.

### 8.3 Problem: mobile navigation needed a real client boundary

**How it was discovered:** The controlled polish phase identified keyboard/focus hardening as a high-confidence slice. `f438243` adds `MobileNav.tsx` and replaces inline header details.

**Impact:** The initial implementation did not provide the final Escape-to-close/focus-return behavior required for a robust mobile menu.

**Fix:** `MobileNav` handles Escape, closes the `<details>`, and restores focus to its summary.

**Validation:** Phase 4B commit diff and final live test confirmed Escape closed the menu and focus returned to the summary.

**Nexus lesson:** Treat mobile navigation as a stateful keyboard component, not only a responsive CSS variant.

### 8.4 Problem: local deployment capability was unavailable

**How it was discovered:** Phase 4D.1 checked for the Vercel CLI and found neither a command nor a project-local CLI.

**Impact:** Codex could not complete repository import, environment configuration, or deployment autonomously. The release stopped for user intervention rather than guessing project IDs or credentials.

**Fix:** The user created/provided the intended GitHub repository and completed Vercel deployment/configuration. Codex then verified the remote SHA and public deployment behavior.

**Validation:** GitHub remote and Vercel deployment records identify `8506d61`; live origin returned the expected route and API behavior.

**Nexus lesson:** Deployment workflows need an explicit capability/credential gate and a human handoff contract.

### 8.5 Problem: Vercel dashboard warnings could not be classified

**How it was discovered:** The final release brief recorded two dashboard warnings, but public output and the available environment did not expose build logs.

**Impact:** The warnings remain `UNKNOWN`; they cannot be truthfully described as harmless.

**Fix:** No source change was made merely to remove unknown warnings. The final report records the evidence gap.

**Validation:** Public deployment was Ready/Production according to release evidence and live behavior passed; warning details remain unavailable.

**Nexus lesson:** Unknown must remain Unknown. Add a release state that separates “live behavior accepted” from “provider diagnostic evidence unavailable.”

### 8.6 Problem: performance evidence is incomplete

**How it was discovered:** The repository preserves build output and responsive/browser checks, but no committed Lighthouse, WebPageTest, bundle-budget, or field-performance artifact exists.

**Impact:** Build correctness is verified, but a numeric performance claim would be unsupported.

**Fix:** No speculative performance optimization was added.

**Validation:** `npm run build` passed and live routes rendered; numeric performance status remains **UNVERIFIED**.

**Nexus lesson:** Do not convert “build passed” or “page rendered” into a performance score.

## 9. Design Lessons

### Direction that was chosen

The final direction is restrained editorial B2B: warm canvas background, dark evergreen ink, muted green surfaces, rust signal color, Newsreader display headings, Manrope body/navigation/forms, crisp dividers, small radii, generous whitespace, and a clear CTA hierarchy.

### Why restraint mattered

The site needed to demonstrate judgment, not a catalog of effects. The source contains no gradient system, glassmorphism layer, bento-grid layout, animation dependency, fake testimonial section, or social-proof metric block. Motion is limited to small CSS transitions and a reduced-motion override. The result keeps the conversion path legible and lets the content carry the page.

### Decisions intentionally preserved

- typography pairing and editorial hierarchy;
- four-color semantic palette;
- section dividers and large whitespace;
- native `<details>` FAQ behavior;
- minimal Client Components;
- no unnecessary fields in forms;
- a simple two-step “webinar / field guide” conversion architecture;
- fictional disclosures instead of simulated proof.

### Advisor conflicts

The phase briefs establish that Product Design, UI UX Pro Max, Taste, and Impeccable were advisors. The exact conflict matrix is not stored, so individual recommendations are **UNVERIFIED**. The verifiable resolution rule was the product contract: only high-confidence, evidence-supported changes entered Phase 4B, and Phase 4B explicitly reported no confirmed P0/P1 findings.

## 10. UI UX Pro Max Findings

The Phase 2.5 brief states that UI UX Pro Max was installed and used as an advisory layer. The repository preserves no standalone UI UX Pro Max report, so the exact finding-to-change mapping is **UNVERIFIED**.

The following resulting concerns are visible in the final code and align with the brief’s named review areas:

- sticky header/anchor structure is explicit through stable section IDs and a visible header;
- decorative SVG icons use `aria-hidden` where they sit beside text;
- buttons and the mobile summary have minimum heights of 44–48 px;
- responsive breakpoints are explicit at 900 px and 640 px;
- form labels, consent semantics, `aria-invalid`, and `aria-describedby` are wired in the component;
- visible `:focus-visible` styling is global;
- reduced-motion behavior is defined.

These are repository outcomes, not proof that every outcome came from one tool. Nexus should preserve the distinction.

## 11. Product Design Findings

The Phase 4A brief records Product Design as one of four requested review perspectives. No Product Design report, generated artifact, or command transcript is committed. Therefore:

- **Availability:** reported available in the phase brief; exact runtime capability **UNVERIFIED**.
- **Role:** product, UX, conversion, accessibility, and frontend-design advisory review.
- **Influence:** the phase briefs and later controlled-polish scope show that the review informed a shortlist rather than authorizing a redesign.
- **Concrete attribution:** **UNVERIFIED** beyond the phase record and final source outcomes.

The durable lesson is to preserve the review’s disposition and authority rules, not to invent missing tool output.

## 12. Taste Findings

The Phase 4A brief records Taste as an audit perspective, and Phase 4B records the four-advisor set as complete. No Taste-generated artifact is tracked.

- **Status:** **USED** according to the phase record; exact executable use is **UNVERIFIED**.
- **Purpose:** anti-slop/visual-quality review of the approved editorial direction.
- **Implementation effect:** no isolated effect can be proven from Git. The final UI’s restrained typography, palette, sparse effects, and rejection of generic SaaS patterns are consistent with the project contract.
- **Nexus lesson:** retain advisor provenance; do not claim a tool changed code unless a disposition record links finding to diff.

## 13. Impeccable Findings

### Availability and installation

Phase 4A explicitly recorded Impeccable as unavailable. Phase 4A.5 was created only to add that missing evidence. The project-local `.agents/skills/impeccable` directory was created on 2026-09-23 at approximately 12:51, before the Phase 4B commit, and contains:

- `SKILL.md`;
- version file `0.1.5`;
- Windows executable and command wrappers;
- references for audit, critique, harden, polish, responsive, hooks, and related commands;
- agent TOML files for documentation/review/edit roles.

### Capability versus installation

Installation is **VERIFIED** by filesystem presence. A complete historical executable transcript is **UNVERIFIED** because `.agents/` is ignored and no audit report is committed. The phase brief records a separate Impeccable-only audit and states that it was not an implementation phase.

### Reported limitations

The phase materials identify two side-tab warnings and limitations around a URL/browser scan when Chromium was unavailable as topics to verify. No committed artifact preserves the exact warning text or final detector output. They are therefore recorded here as **UNVERIFIED historical limitations**, not converted into precise tool claims.

### Source-change boundary

There is no Impeccable-only application commit. The next tracked implementation commit, `f438243`, is a two-file controlled polish change. This supports the conclusion that the audit was advisory and manually applied, but does not prove every manual operation.

### Nexus lesson

Nexus must record four separate states: package installed, command callable, audit executed, and finding applied. A directory listing is evidence for only the first state.

## 14. Accessibility Lessons

### Early and structural protections

- semantic headings and `<main id="main-content">` support document structure;
- the skip link is present and targets the main content;
- form labels are explicitly associated with inputs;
- FAQ uses native `<details>`/`<summary>`;
- decorative icons use `aria-hidden`;
- `:focus-visible` uses a high-contrast outline;
- reduced-motion CSS disables smooth scrolling and shortens transitions/animations;
- buttons and mobile navigation meet the project’s minimum touch sizing.

### Late hardening that became implementation

- `MobileNav.tsx` closes on Escape and returns focus to the summary;
- `LeadForm.tsx` focuses a `role="alert"` error summary after client or server validation failures;
- field errors set `aria-invalid` and `aria-describedby`;
- the honeypot is outside the keyboard path using `aria-hidden`, `inert`, and `tabIndex={-1}`;
- the thank-you heading is `tabIndex={-1}` and receives focus on navigation.

### Validation evidence

Final live acceptance verified skip link presence, mobile Escape/focus return, FAQ expansion, form focus sequence, error-summary behavior, and thank-you heading focus. Responsive live checks covered 375, 768, 1024, and 1440 px with no measured horizontal overflow.

### Nexus gates

Automate a keyboard path that includes form fields, consent, submit, error summary, mobile menu, Escape, FAQ, and route-change focus. A static “has labels” check would not have caught the mobile focus-return requirement.

## 15. Form / API / Security Lessons

### Validation and normalization

The strict Zod schema accepts only `webinar` or `guide`, lowercases/trims email, bounds first name, requires literal `true` consent, bounds honeypot/form timing/Turnstile fields, and rejects unknown keys. `getLeadFieldErrors()` exposes only approved user-facing fields.

### API boundary

The API returns:

- 415 for unsupported content types;
- 403 for invalid origins;
- 413 for oversized bodies;
- 400 for malformed JSON or schema failure;
- 400 for spam rejection;
- 503 for unconfigured/recoverable provider errors;
- a narrow success object for accepted requests.

Error messages do not include stack traces, provider payloads, credentials, or field values.

### Anti-spam

The baseline uses a honeypot and rejects implausibly fast submissions under 700 ms. Turnstile is an optional server-side boundary: if a secret is configured, a token is required and verification has a bounded timeout; if no secret is configured, the optional control is inactive. The portfolio deployment did not activate Turnstile.

### Providers and duplicates

`DemoLeadProvider` waits briefly to model provider work, returns deterministic demo outcomes, and does not persist input. `HubSpotLeadProvider` keeps its token server-side, times out after five seconds, converts HubSpot 409 duplicate responses to neutral success, and returns a generic provider error for other failures. The automated test covers duplicate neutrality without making a live HubSpot call.

### Client lifecycle

The form prevents duplicate submits while `submitting` or `success`, aborts the browser fetch after eight seconds, uses a response-shape guard, displays recoverable errors, and routes to a source-specific thank-you page only after accepted demo success.

### Why this fit a portfolio demo

The architecture demonstrates production judgment without creating a false production system. It proves the boundary, validation, error, and integration seams while keeping credentials, storage, delivery, and vendor side effects inactive.

## 16. Truthfulness and Demo Safety

Northstar intentionally avoids misleading portfolio behavior:

- the footer calls the site a fictional portfolio demonstration;
- the event date and instructor profile are marked fictional;
- the privacy page says it is not legal advice or a compliance certification;
- the forms explain that demo submissions do not send/store email or personal data;
- the guide copy says live delivery would require activation;
- no customer logos, testimonials, attendee totals, revenue outcomes, or certification claims are present;
- analytics is a contract-only `track()` function with no vendor or form-value transmission;
- the production demo API returns `provider: "demo"` and delivery state rather than pretending that a CRM/email side effect occurred;
- public URLs do not contain submitted email addresses.

This matters because a portfolio demo is still a public claim. Nexus-generated demos should have a truthfulness scan before release, not after a reviewer discovers fabricated proof.

## 17. SEO / Production Readiness

### Verified production work

- `metadataBase` comes from `NEXT_PUBLIC_SITE_URL` through `getSiteOrigin()`;
- route-specific titles, descriptions, canonicals, OG metadata, and Twitter metadata are generated;
- thank-you pages use `noindex, follow` and canonicalize query variants to `/thank-you`;
- the 404 page is branded and non-indexable;
- `robots.txt` disallows `/thank-you` and `/api/` and points to the configured sitemap;
- the sitemap contains the public homepage, guide, and privacy routes only;
- `opengraph-image.tsx` returns a 1200×630 PNG and labels itself as a portfolio demonstration;
- security headers are applied globally: `nosniff`, `DENY`, strict-origin referrer policy, and restricted camera/microphone/geolocation permissions;
- `.env.example` and README distinguish public site configuration from server-only secrets;
- the final build generated the expected App Router route set.

### Status distinctions

| Area | Status | Evidence/limitation |
|---|---|---|
| Metadata/canonical | **VERIFIED** | Local build and live HTML inspection. |
| robots/sitemap/OG | **VERIFIED** | Live HTTP responses and image response. |
| Accessibility/responsive | **VERIFIED** | Automated tests plus live browser checks. |
| Security boundary | **VERIFIED** | Source review, API boundary checks, and live security headers. |
| Privacy/demo disclosure | **VERIFIED** | Source and live route/form behavior. |
| Structured data | **N/A / UNVERIFIED rationale** | No JSON-LD is present; the repository does not preserve a written decision explaining why additional structured data was rejected. Do not invent one. |
| Numeric performance score | **UNKNOWN** | Build passed and pages rendered, but no committed Lighthouse/field-performance artifact exists. |
| Dependency audit | **PASS WITH DEFERRED PRODUCTION CONDITION** | Small dependency set and no active provider credentials; a future real integration still needs its own review. |

## 18. Release and Deployment

### Repository sequence

Phase 4D.1 began with a clean `master` at `8506d61` and no remote. The user supplied the intended repository, `https://github.com/TDY0225/northstar-sales-lab.git`. Codex added that exact `origin`, verified it had no conflicting branch, and pushed the existing history without creating a setup commit.

The final remote check showed:

```text
local  = 8506d61a88b704d24a6010826e5e2d686fea97a1
remote = 8506d61a88b704d24a6010826e5e2d686fea97a1
```

### Capability limitation and manual handoff

The local `vercel` command was unavailable. Codex did not install a plugin, guess credentials, create a different project, or force a deployment. The user completed the Vercel setup and configured:

- `LEAD_PROVIDER=demo`
- `NEXT_PUBLIC_SITE_URL=https://northstar-sales-lab.vercel.app`

GitHub’s Vercel deployment record then reported source SHA `8506d61`, Production, completed successfully. The stable alias was checked separately from immutable deployment URLs.

### Release lesson

Repository publication, provider configuration, and public-origin verification are different gates. A successful Git push is not evidence of a successful deployment, and a live URL is not evidence that it points to the intended SHA unless the deployment source identity is checked.

## 19. Final Live Acceptance

The final public acceptance used `https://northstar-sales-lab.vercel.app`, not localhost.

### Route and content checks

- `/`, `/follow-up-frameworks`, `/privacy`, and all three thank-you query variants returned HTTP 200.
- The missing route returned HTTP 404 with the branded message.
- Canonicals, titles, descriptions, `noindex`, OG/Twitter metadata, robots, sitemap, and image response matched the production origin.

### Form and API checks

- Both forms rendered labels, consent, validation, and safe helper copy.
- Invalid email/missing consent produced an error summary and field state without navigation.
- Synthetic `.invalid` submissions reached the correct webinar and guide thank-you sources.
- No submitted address appeared in the URL or confirmation copy.
- API checks returned 415, 400, 403, and 200 for the specified boundary cases.

### Browser matrix

At 375, 768, 1024, and 1440 px, all required routes had zero measured horizontal overflow and visible key headings. Keyboard checks covered skip links, anchor navigation, mobile menu Escape/focus return, FAQ disclosure, form tab order, error-summary focus, and thank-you heading focus.

### Runtime and security

No application console errors/warnings were observed while exercising the route set and interactions. Public output contained no server secrets, stack traces, fallback origin, or synthetic test PII. Security headers were present on HTML and API responses.

### Unresolved item

The Vercel UI reported two build warnings, but the available environment could not access their build logs. Both remain **UNKNOWN**. This was documented rather than guessed away. No live release-blocking symptom was observed.

## 20. Rejected Ideas

The following were intentionally not adopted where the source or phase contract provides evidence:

- fabricated metrics, testimonials, customer logos, or revenue claims — rejected to preserve truthfulness;
- real HubSpot/email/analytics activation — rejected for a demo-only release boundary;
- gradients, glassmorphism, bento layouts, and excessive animation — excluded by the editorial design contract and phase scope;
- an animation library — no interaction requirement justified the dependency;
- unnecessary form fields — rejected in favor of email, optional first name, consent, and hidden anti-spam fields;
- PII in query strings — rejected by source-specific routing that passes only `kind`;
- public provider credentials — rejected by server-only environment boundaries;
- `overflow-x-hidden` as a layout mask — no such rule exists in the final CSS; defects were checked through responsive evidence instead;
- unsupported structured data — no JSON-LD was added; the exact historical rationale is **UNVERIFIED**, so Nexus must not invent one;
- a broad visual redesign during Phase 4B — rejected because no confirmed P0/P1 finding justified it.

## 21. Deferred Real-Production Work

### Portfolio demo complete

The fictional marketing experience, forms, API contract, demo provider, source-aware confirmation, accessibility behavior, responsive layouts, SEO metadata, security headers, repository release, and public live acceptance are complete.

### Real business integrations not activated

- HubSpot credentials, portal mapping, consent/retention policy, and live CRM writes;
- transactional email and printable PDF delivery;
- analytics vendor, consent management, and event governance;
- production Turnstile keys and operational anti-spam policy;
- approved legal/business contact details and jurisdiction-specific privacy copy;
- monitoring, alerting, provider dashboards, and incident response;
- numeric field-performance budgets and ongoing production observability.

These are not release defects for this portfolio scope. They are explicit prerequisites for a real client deployment.

## 22. Nexus-Reusable Rules

### Rule 1 — Capability availability detection

**EVENT:** Phase 4A reported Impeccable unavailable; Phase 4A.5 was added.
**SIGNAL:** The requested audit capability did not exist at the original gate.
**DECISION:** Pause the missing audit and make it available locally instead of claiming coverage.
**RESULT:** A separate audit phase existed, but its detailed output was not persisted.
**NEXUS RULE:** Gate multi-tool workflows on callable capability, and require an evidence artifact for every completed advisory pass.

### Rule 2 — Installed is not executable

**EVENT:** `.agents/skills/impeccable` exists with an executable and version file.
**SIGNAL:** The directory is ignored and no command transcript is tracked.
**DECISION:** Treat installation as verified, execution as separately classified.
**RESULT:** The postmortem avoids false tool attribution.
**NEXUS RULE:** Track `installed`, `callable`, `executed`, and `applied` as four independent states.

### Rule 3 — Advisory tools do not override the product contract

**EVENT:** Four independent design perspectives were requested.
**SIGNAL:** The project brief explicitly made them advisors and prohibited redesign.
**DECISION:** Preserve the editorial contract and implement only high-confidence findings.
**RESULT:** Phase 4B remained a two-file polish change.
**NEXUS RULE:** Require an authority map and disposition for every advisory recommendation.

### Rule 4 — Accessibility is behavioral

**EVENT:** Mobile menu, form errors, and thank-you navigation needed focus behavior.
**SIGNAL:** Static markup alone could not prove Escape closure, summary focus, or heading focus.
**DECISION:** Add stateful handlers and test real keyboard paths.
**RESULT:** Live checks passed menu, form, FAQ, and thank-you focus behavior.
**NEXUS RULE:** Make keyboard paths part of the acceptance matrix, not an optional visual review.

### Rule 5 — Truthfulness is a release gate

**EVENT:** The site needed to look production-quality while remaining a fictional demo.
**SIGNAL:** A normal landing-page pattern could easily imply CRM capture or delivery that did not exist.
**DECISION:** Use explicit demo provider responses and visible thank-you disclosures.
**RESULT:** No public copy claims active CRM, email, PDF, customer proof, or stored PII.
**NEXUS RULE:** Run a truthfulness scan for claims, side effects, metrics, and credentials before release.

### Rule 6 — PII boundaries must be observable

**EVENT:** Forms accept email addresses.
**SIGNAL:** Demo behavior must not silently retain or leak test data.
**DECISION:** Keep provider demo-only, avoid URL propagation, and return stable responses without input echoing.
**RESULT:** Live synthetic submissions contained no email in URLs/pages/logs.
**NEXUS RULE:** Test PII non-echo and non-persistence explicitly; do not infer it from code intent.

### Rule 7 — Unknown remains Unknown

**EVENT:** Two Vercel dashboard warnings were visible without accessible logs.
**SIGNAL:** Public deployment behavior cannot identify a build warning’s cause.
**DECISION:** Preserve `UNKNOWN` and document the evidence gap.
**RESULT:** Release acceptance did not invent a harmless explanation.
**NEXUS RULE:** Unknown diagnostics require a visible follow-up state and must not be silently downgraded to PASS.

### Rule 8 — Git and deployment identity are separate

**EVENT:** GitHub push succeeded before stable Vercel origin configuration.
**SIGNAL:** A remote SHA does not prove which source a public deployment serves.
**DECISION:** Verify local SHA, remote SHA, deployment source SHA, configured origin, and live routes separately.
**RESULT:** All four identity layers matched the accepted candidate.
**NEXUS RULE:** Add a release gate that refuses “deployed” without source identity and public-origin evidence.

## 23. Proposed Nexus Automation Gates

These automations follow directly from Northstar evidence:

### Pre-build

- capability inventory with installed/callable/executed states;
- dependency diff and justification check;
- Server Component/client-boundary review;
- environment-variable classification scan for public versus server-only values.

### Design and content

- approved design-contract snapshot and visual-drift review;
- generic-pattern scan for gradients, glassmorphism, bento overuse, fake proof, and unexplained animation dependencies;
- copy truthfulness scan for metrics, testimonials, certifications, and active-integration claims.

### Accessibility

- keyboard route matrix;
- mobile menu Escape/focus-return check;
- skip-link and heading-structure check;
- form label/`aria-invalid`/`aria-describedby`/error-summary focus check;
- hidden-honeypot semantics check;
- reduced-motion and minimum touch-target check.

### Security and privacy

- content-type, origin, body-size, JSON, and sanitized-error smoke tests;
- secret and stack-trace scan of rendered HTML/API responses;
- PII non-echo check for URL, response, logs, and demo storage;
- duplicate/timeout/abort behavior test for every provider adapter.

### SEO and release

- canonical/metadata/OG/Twitter route matrix;
- robots/sitemap inclusion and exclusion assertions;
- 404 status/content assertion;
- local/remote/deployed SHA equality;
- clean-tree and diff-check gate;
- explicit deployment-capability and human-handoff gate.

### Acceptance

- required route matrix at 375/768/1024/1440 px;
- production API boundary smoke tests;
- console error/warning capture;
- live form success and invalid-state checks using synthetic reserved data;
- unknown-state report that prevents unsupported PASS claims.

## 24. Final Factual Status

| Area | Status | Evidence |
|---|---|---|
| Architecture | **VERIFIED** | App Router source, component boundaries, provider seam, and five commit history. |
| Design | **VERIFIED** | Final CSS/content contract and controlled polish diff. |
| Responsive | **VERIFIED** | Live 375/768/1024/1440 checks with zero measured overflow. |
| Accessibility | **VERIFIED** | Source semantics plus keyboard/focus live acceptance. |
| Forms | **VERIFIED** | Client lifecycle, invalid state, synthetic success, and thank-you routing. |
| API | **VERIFIED** | Source boundary and production 415/400/403/200 checks. |
| Security | **VERIFIED** | Origin/content/body guards, sanitized errors, headers, and secret scan. |
| Privacy | **VERIFIED** | Demo disclosure, no PII echo, inactive storage/delivery. |
| SEO | **VERIFIED** | Canonical, metadata, OG, robots, sitemap, and 404 checks. |
| Performance | **UNKNOWN** | No committed numeric performance artifact. Build correctness passed. |
| Deployment | **VERIFIED** | GitHub remote, matching SHA, Vercel deployment record, and stable live origin. |
| Production acceptance | **VERIFIED WITH UNKNOWN WARNING DETAIL** | Public route/API/browser matrix passed; two Vercel warnings could not be inspected. |
| Git/repository hygiene | **VERIFIED** | Clean `master`, matching `origin/master`, no rewrite/force-push, no source changes after release. |
| Audit provenance | **PARTIALLY VERIFIED** | Phase briefs and local skill artifacts exist; detailed advisor reports are not committed. |

## 25. Key Takeaways

1. A fictional portfolio product can demonstrate serious engineering without pretending to have live business integrations.
2. Provider abstraction, strict server validation, anti-spam boundaries, sanitized responses, and truthful demo copy are more valuable than a fake “complete” integration.
3. Small controlled diffs protected the accepted visual direction and reduced regression risk.
4. Accessibility acceptance must test focus and keyboard behavior, not only markup.
5. Git SHA, deployment source SHA, configured origin, and public behavior must be verified as separate facts.
6. Tool installation, tool execution, and tool influence are different evidence states.
7. Missing evidence and inaccessible diagnostics must remain explicitly `UNVERIFIED` or `UNKNOWN`.
8. Northstar is complete as a portfolio demo; the deferred real-production work is a separate, approval-gated project.
````
<!-- END EXACT NORTHSTAR SOURCE -->
