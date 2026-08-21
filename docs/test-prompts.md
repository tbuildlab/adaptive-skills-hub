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
