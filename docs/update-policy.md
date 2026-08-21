# Update Policy

## Default mode: CHECK-ONLY

The hub may detect new upstream revisions, but it must not automatically merge or overwrite local skills or project files.

## Safe update pipeline

1. Detect remote revision.
2. Compare with stored revision.
3. Identify which registered capability changed.
4. Inspect meaningful changes when the source is relevant to an active task.
5. Classify impact:
   - documentation only
   - additive
   - behavior change
   - breaking
   - security-related
6. Check compatibility with local/project rules.
7. Update adapters or registry only when appropriate.
8. Validate before declaring the update adopted.

## Never

- Blindly `git pull` into an active project.
- Overwrite a local/custom skill from upstream without review.
- Treat an upstream example as a new project requirement.
- Auto-apply breaking changes without compatibility assessment.

## Revision state

`state/source-revisions.json` stores the most recently observed remote commit SHA.
It is an observation record, not proof that the local system adopted that revision.
