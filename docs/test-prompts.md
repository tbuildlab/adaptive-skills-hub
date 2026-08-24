# V1 Test Prompts

Use these after installing Nexus.

## Test 1 — UI task

Use Nexus (Adaptive AI Capability Hub). Review this React page and improve its UI. Automatically find and execute relevant installed skills. Use external references only when they add value. Do not stop at skill recommendations.

Expected behavior:
- frontend/design-related skills selected when present
- emilkowalski skills may be relevant
- liquid-glass-react only if the design actually calls for it
- DeerFlow normally skipped
- task is executed

## Test 2 — LLM architecture

Use Nexus (Adaptive AI Capability Hub). Design the architecture for an AI research assistant and implement the next actionable project step. Automatically load relevant skills and references.

Expected behavior:
- LLM/agent architecture references may be used
- agency agent roles may support decomposition/review
- DeerFlow considered only if orchestration complexity warrants it
- UI references not loaded without need

## Test 3 — simple backend bug

Use Nexus (Adaptive AI Capability Hub) and fix this backend bug. Select the smallest sufficient set of skills and execute them.

Expected behavior:
- unrelated UI/reference sources are skipped
- no "load everything" behavior

## R5 Desktop pilot — Host capability inventory and presentation execution

Start a new ChatGPT Desktop conversation after installing/updating the R5
pilot, then use:

```text
@Nexus Create an editable PowerPoint presentation about digital transformation in business.
```

Expected behavior:

- Nexus distinguishes its local Skill catalog from the current Host-visible
  capability subset;
- `nexus.assess_host_capabilities` is called before the R4 handoff;
- every genuinely Host-visible relevant presentation capability is considered,
  without assuming a memorized name is installed or executable;
- installed/visible/loadable candidates without a reviewed callable Host
  mapping are rejected truthfully;
- the smallest complete mapped set is selected;
- the existing R4 plan/load/hash handoff and Host-owned execution remain
  unchanged;
- a real editable `.pptx` is created and open/render validated before success;
- the final receipt separates considered, selected, loaded, executed, rejected,
  and validated states and reports the inventory as
  `current_turn_host_visible_subset`, `not_globally_enumerated`;
- Host-visible labels are reported from the Host's own trace, while the Nexus
  assessment uses opaque identities and never reflects an untrusted label;
- the Host-local inventory receipt binds the fresh assessment selection to the
  exact R4 mapping and execution receipt; a mismatch or replay fails closed;
- capabilities absent from the current Host-visible subset are reported as
  `not observed`, not `unavailable`.
