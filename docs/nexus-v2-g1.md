# Nexus V2 G1 — Capability Profiles and Executor Conformance

Status: IMPLEMENTED / ACCEPTED. Acceptance evidence: 2026-09-15.
Immutable freeze marker: annotated tag `nexus-v2-g1-final` targeting this record's
accepted commit. Publication and local/remote agreement are verified separately;
this document alone does not certify that the tag has been published.
G2: NOT STARTED.

This is the minimal current-status companion to the unchanged historical
[Roadmap V2](nexus-roadmap-v2.md). The Roadmap V2 tag remains bound to
`f92b96ea01b8e32dac8bc1d51819bf0c58d55659`; Slice 3C remains bound to
`10b802073861fe4991b3a3789609a8161169f499`. No later roadmap slice is authorized
by G1 acceptance or its freeze marker.

## Scope and authority

G1 adds bounded data validation, deterministic policy intersection, capability
eligibility, exact-subject conformance evidence and selection/refusal. It adds
no MCP tool, product dispatcher, model gateway, execution loop, checkpoint,
recovery, ledger, budget reservation, Agent runtime, delegation or concurrency.
Frozen R4/R5 mappings and Slices 1–3C remain unchanged.

Profiles, observations, selection, validation PASS and probe success grant no
permission, trust, execution, installation or delegation authority. Actual Host
operations require independent authorization. Prompt instructions are ADVISORY
and cannot satisfy a hard restriction. A GOVERNED_HANDOFF covers only a reviewed
bounded handoff; ENFORCED_INTEGRATION requires an observed technical boundary
for the exact control and operations. Neither classification certifies a whole
Host or an unrelated task.

## Versioned contracts

| Contract | Implementation and meaning |
|---|---|
| ModelCapabilityProfile v1 | `ash/g1_profiles.py`: identity/revision, provider/family/model/deployment/configuration, adapter fingerprint, deployment kind, separately claimed/measured/Host-reported/runtime-observed capabilities and task classes, limits, tools, structured output, delegation facts, cost/latency, privacy/residency/retention, provenance, time/scope/expiry, limitations and uncertainty. |
| HostCapabilityProfile v1 | Seven independent nullable states: documented possibility, current visibility, permission, applicable trust, binding, prerequisites and executable state. Closed facility and lifecycle facts retain unknowns and current-subset inventory semantics. |
| ExecutorConformanceRecord v1 | Exact candidate and binding digests, restriction, enforcing layer, operation coverage, classification, probe result, evidence references, scope, freshness and limitations. |
| SelectionDecision v1 | Requirements and policy digests, required capabilities, effective hard controls, acceptance requirements, considered/rejected/eligible profiles, reason codes, trusted suitability/conformance evidence, cost basis, uncertainty, selected single-executor strategy or UNSUPPORTED. Always zero authority and dispatch not requested. |
| ExecutorCandidate/Requirements/Policy/Observation v1 | Candidate model/Host/path/cost composition; additive requirements reuse the frozen normalized runtime task; policy supports closed field predicates and hard intersections; observations bind exact candidate/configuration/requirements/policy/scope. |

JSON input uses the existing strict Slice 3C parser/canonical bytes with tighter
G1 graph bounds: 512 KiB, depth 12, 16,000 visited nodes, 64 entries per container,
512 characters per string, 16 path nodes, 8 policies and 64 considered candidates.
Aggregate bounds can reject a large combination before the individual limits.
Exact built-in JSON types, canonical lower-case identifiers, unique identities,
NFC, strict digests and a maximum 24-hour observation interval are required.
Duplicate JSON keys, floats, huge integers, cycles, subclasses, control/bidi
characters and unrecognized fields fail closed. Descriptive notes are inert and
are not echoed in decisions. There is no universal intelligence score.

## Evidence boundary

The public selector accepts an in-process `TrustedObservations` handle minted
by a reviewed adapter. Serialized profiles, observation-shaped JSON, copied
handles and altered sealed handles cannot manufacture that provenance. The
internal `_issue_observations` seam is used by the separately authorized pilot
and hermetic tests. It is not exposed through MCP or a deserialization/admission
API. No approval store or capability authorization plane is implemented.

As with the frozen validator registry, this boundary assumes trusted loaded
Python code and trusted orchestration. It does not resist arbitrary Python
execution in that same process, attest remote issuers, monitor configuration
changes in another process, or authenticate the desktop user. A future real
adapter needs separate review. Callers supply fresh facts and a trusted current
time; changed subjects/configuration, policies, requirements or scope invalidate
existing observations. Evidence hashes prove integrity, not universal identity.

The candidate binds exactly one model node to its complete model profile, or no
model nodes for a deterministic executor. Model/provider/location contradictions
fail validation. The reviewed observer must verify the complete relevant model,
context, validation, tool, storage and forwarding path; caller declarations of
path completeness do not suffice. Unknown mandatory observations are ineligible.

## Policy, suitability and cost

Policy predicates are structured data (`allow_only` and `deny`); provider and
model names appear only in profiles and rules. Policy intersections never weaken
restrictions. Behavior/privacy rules require additional ENFORCED_INTEGRATION
coverage named `policy:<field>` over every requested operation. Observations are
bound to the full policy set, preventing reuse after a policy change. Identity
exclusions are deterministic preselection filters. No forbidden fallback exists.

Task class, capabilities (including normalized domains/outputs/validation),
acceptance, permissions, mechanism, applicable trust, freshness, verified full
path, budget eligibility and all hard controls pass before ranking. Reference,
advisory-only and absent execution mechanisms remain ineligible. Host lifecycle
flags do not substitute for current operational evidence.

Cost is an explicit integer microunit amount in one named currency, composed of
execution, expected retries, validation, context transfer/preparation, tools and
human recovery. Known, estimated and unknown are separate. Unknown totals remain
null. No currency conversion is attempted. Cheapest preference applies only to
comparable eligible totals; otherwise stable candidate identity breaks ties with
`COSTS_NOT_COMPARABLE`. Host-native preference precedes privacy-first preference,
then comparable expected cost, then identity. Monetary ceilings here constrain
expected cost, not actual spending; runtime ceilings require separate technical
conformance and are unsupported by the shipped pilot.

## Narrow real pilot

`scripts/probe_g1_conformance.py` explicitly invokes the existing initialized
`NexusMcpRuntime.route_capabilities` method using the real manifest-verified
RuntimeCapabilityAdapter, an empty external-local-root map and no workspace
authorization. It creates no new product dispatch interface. The report binds
source/configuration hashes and the Python version and rejects changed source.
No model or artifact workflow is executed.

The only positive technical coverage is the existing closed route-input
parser, zero dispatch authority in its decision, and bounded route output.
Read-only audit observations track process/network/write attempts without
blocking effects to manufacture success. A narrow unsupported artifact result
inside the legacy router can still be a valid governance decision. That does not
mean the artifact was completed. Existing legacy fallback metadata has no G1
authority. Whole-Host isolation, cancellation, actual money bounds, remote model
quality, desktop transport identity, R4/R5 artifact execution, and third-party
bindings remain unqualified. The pilot separately requires a refusal for an
uncovered whole-Host network-isolation restriction.

## Interrupted baseline and initial review findings

The initial G1 request failed before doing any work because usage was exhausted.
The next interrupted run wrote the profile and selector modules; a subsequent
run added fixtures and profile tests. All valid work was retained.

The first isolated frozen-baseline full run completed 506 tests with two
failures, one error and four expected skips. The isolated source root lacked its
already-reviewed sibling `adaptive-skills-library/emil-design-eng/SKILL.md`.
Independent A/B/A verification reproduced the exact two failures and one error
when only that copied external fixture was hidden; present/restored fixture
runs passed all 19 affected tests. Its 27,226 bytes and SHA-256
`e71de849347050c2c573c1cf24d742d5a13459557ecffa6e562f08006f46b5b7`
match the frozen registry. No source, assertion, registry, installed Skill or
availability claim was altered. Original failures remain recorded as an
environment defect, not a green full run. The final full regression is a
separate gate.

Preliminary independent reviews found blocking G1 defects: advisory records
could satisfy a hard control; model/path descriptions could contradict; behavior
policy did not imply enforcement obligations; advisory-only mechanisms could
be marked executable. Targeted fixes and permanent regressions address these
findings. All three independent final reviews accepted these fixes. Unresolved
Critical, High, Medium and Low findings: zero; other blocking defects: zero.

## Final acceptance evidence

| Gate | Verified result |
|---|---|
| Dependency-complete isolated full regression, CPython 3.12.10 | 556 total tests: 552 passed, four existing skips, zero failures or errors. The run includes all 50 G1 and all 19 previously affected runtime-decision tests. |
| Focused G1 compatibility | 50/50 passed independently on CPython 3.12.10 and 3.13.15, with no skips. |
| Adversarial G1 coverage | Passing permanent profile, selection and pilot regressions; independent Security review also passed 30 additional synthetic boundary checks. |
| Cross-Python G1 determinism | 18 synthetic decision/error vectors produced the same 44,116 bytes on both runtimes. SHA-256: `341612ef9785415203893b45fa3105fb1d009d59d424fa5d776b411b1dc9cb41`. |
| Frozen Slice 3C identity/canonicalization checks | Four golden/boundary/100-repeat determinism checks passed on each Python version. |
| Architecture final | PASS; independently reran all 50 G1 tests; zero unresolved findings or blocking defects. |
| Security final | PASS; independently reran all 50 G1 tests and 30 additional security checks; zero unresolved findings or blocking defects. |
| Testing final | PASS; independently verified full-run provenance, source identity, cross-version vectors/goldens and smoke comparison; zero unresolved findings or blocking defects. |
| Final separately authorized real pilot | PASS against the existing initialized direct `route_capabilities` method. Observed network, process, file-write and filesystem-mutation counts were all zero. |
| Pilot refusal and truthfulness | Legacy route result remains `CAPABILITY_NOT_COVERED`; the G1 governance selection is not an artifact success. Mandatory whole-Host isolation remains `UNSUPPORTED`. |
| Frozen route/load smoke | 6/10, identical to baseline, with zero Skill command calls. The same four Host-cache failures and all three input-index hashes remain unchanged. |
| Source and release integrity | Executable source and tests match the reviewed full-test snapshot. Only this factual acceptance record and its MANIFEST entry change after review. Final freeze requires the deterministic manifest/package rebuild and remote-ref checks below. |

The four full-suite skips are three existing embedded-bootstrap tests lacking
their explicitly configured integration inputs, plus the existing Windows
symlink fixture requiring an unavailable privilege. They do not count as passing
executions. The four smoke failures are `document`, `spreadsheet`, `pdf`, and
`research_document_chain`, caused by missing historical Host-managed Skill cache
paths. They remain Host/environment limitations; they were not repaired by
changing availability claims, installed indexes, fixtures or frozen assertions.
There is no unresolved implementation defect or lower-severity review backlog.

Model/config substitution uses four synthetic profile configurations and a
deterministic non-model executor. Changing provider/model/configuration is data
substitution; a relevant identity change invalidates old observations. These
checks establish routing neutrality and evidence binding, not measured quality
of any named commercial model. The 18-vector comparison also covers candidate
ordering, hard-filter-before-cost behavior, unknown cost, policy denial/conflict,
ADVISORY rejection, operation mismatch, expiry and stale policy/configuration.

The retained validation directory contains the original failed baseline log,
A/B/A logs and fixture hashes, full/focused logs, canonical output files, pilot
receipts, source identity records, and the independent reports. Report raw-byte
SHA-256 values bind the conclusions summarized here:

| Independent report | SHA-256 |
|---|---|
| `ARCHITECTURE-REVIEW.md` | `c8e8ab6f67f96562c6953945e6e575f07c673fe838d15b0d0680e4dbb27d1cf2` |
| `SECURITY-REVIEW.md` | `d86fa9a5b1e0d2b141746a19cfdbc7894fea0e7913745a626c9aee95208a25ab` |
| `TESTING-REVIEW.md` | `539d5b6071c7cc90751bb1d6c4e3c4b41d9e7d7febdae907de275c3f2128ac17` |

Machine-specific logs remain external evidence, outside the portable package.
The full-regression raw log SHA-256 is
`f573238b4da0157829149afb44c0a330c4a2df00c67781b8095275bf10dfb01b`.
The original failing baseline log remains
`dfb59d215e02acd38e4a8abf9a217338116d8e3a35dcfcc66d8185a4b6c5f59b`.

The release gate rebuilds MANIFEST twice in a fresh source-only snapshot,
verifies every member using the existing newline normalization, builds two
byte-identical packages, and checks members, CRC, traversal, symlinks, generated
state, private paths and secrets. Exact unchanged historical example/redaction
fixtures retain their existing semantics. The freeze receipt records final
manifest/package hashes, commit, annotated tag object and target, all prior tag
identities, private-origin agreement and clean worktree. Those values are kept
outside the manifest-owned document to avoid self-referential hashes.

## Changed files

| Files | Purpose |
|---|---|
| `ash/g1_profiles.py`, `ash/g1_selection.py` | Additive versioned contracts, observations, policy intersection, eligibility and deterministic selection/refusal. |
| `scripts/probe_g1_conformance.py` | Separately invoked diagnostic of the existing read-only route boundary. |
| `tests/g1_fixtures.py`, `tests/test_g1_profiles.py`, `tests/test_g1_selection.py`, `tests/test_g1_pilot.py` | Bounded synthetic fixtures and the 50 permanent focused/adversarial/pilot tests. |
| `docs/nexus-v2-g1.md` | Implemented semantics, acceptance evidence, scope limitations, current Roadmap status and utilization report. |
| `scripts/package_nexus.py`, `MANIFEST.json` | Add this document to the existing package allowlist and bind the G1 additions. No other existing implementation, test or historical document is changed. |

## Agent & Skill Utilization Report

The Nexus Skill was read and applied. Its planner returned
`CAPABILITY_NOT_COVERED`, selected no Skill/Agent and granted no authority. Native
Codex performed authorized implementation and testing. Applicable Host-native
Software Architect, Security Engineer and Testing Evidence Collector advisors
performed bounded independent checks; interruptions and incomplete reviews are
not treated as acceptance. These personas remain advisory, with no Nexus Agent
runtime. Their read-only instructions are not technical sandbox enforcement.

| Considered capability | Applicability and actual use |
|---|---|
| Installed trusted Nexus Skill and bounded planner | Applicable and used once to assess the task. Result: `fallback_needed` / `CAPABILITY_NOT_COVERED`; no selected Skill or Agent, no execution grant. |
| Host-native Software Architect advisor | Applicable and used for independent initial/final architecture review. Final reviewer: `g1_architecture_final`; actual code inspection and 50-test rerun. |
| Host-native Security Engineer advisor | Applicable and used for independent initial/final security review. Final reviewer: `g1_security_final`; actual 50-test rerun and 30 additional boundary checks. |
| Host-native Testing Evidence Collector advisor | Applicable and used for independent fixture diagnosis and final evidence review. Final reviewer: `g1_testing_final`; independent compatibility/determinism/smoke verification and completed final report after interruption. |
| Native Codex | Implemented and fixed the authorized additive code, maintained test snapshots and exact hashed dependencies, ran focused/full regression, integrated findings, and performed documentation, release and freeze checks. These are the owner's authorized engineering tasks; no specialist sign-off was substituted by self-review. |
| Artifact, presentation, design, browser and document-production Skills | Non-applicable to this Python contract/release task; not used as specialist review. Existing smoke loading is bounded validation, not artifact execution. |
| Installation, external research, provider-execution Skills and new third-party Plugins | Non-applicable and not used. No new capability was installed, activated or executed. |
| Unavailable or untrusted external capabilities | None selected or promoted. Missing historical Host-cache bindings remain explicit smoke limitations; no authority or availability was inferred. |

Advisors use existing Host-native facilities only for this separately authorized
engineering review. Their personas and read-only instructions are advisory;
neither those instructions nor their PASS conclusions enforce runtime controls.
Profiles, observations, conformance records and selection decisions retain no
approval, installation, activation, routing or execution authority. G1 adds no
G2 dispatch, execution/recovery/checkpoint loop, runtime-budget reservation,
delegated child execution or concurrency. G2 remains NOT STARTED.
