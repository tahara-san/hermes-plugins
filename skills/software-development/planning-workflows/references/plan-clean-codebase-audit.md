# Plan-clean codebase audit pattern

Use when a `tasks/<slug>/` directory looks incomplete from stale checkboxes, or complete-but-ambiguous because review artifacts are missing. This is a read-only classification workflow before any cleanup deletion.

## Why

Task docs often drift after implementation. A directory may have unchecked TODO boxes even though the implementation, focused tests, and final review exist; conversely, a fully checked task may conflict with current code or fail current focused tests. Do not classify solely from checkbox counts.

## Audit steps

1. Start from the task docs: `spec.md`, `todo.md`, `progress.md`, phase TODOs, `notes.md`, and `reviews/*` if present.
2. Extract the durable acceptance criteria and expected touched surfaces: routes, components, models, translations, E2E files, backend paths, review gates, and verification commands.
3. Inspect current code/tests for those surfaces. For cross-repo tasks, inspect the referenced repo as read-only evidence before deciding.
4. When the user remembers a task as completed but the current task docs look unstarted, actively check for **same-name / near-name task drift across repos and sessions** before cleanup. Search recent git history/PRs/worktrees plus prior session transcripts for the task slug and distinctive implementation markers. A common false-positive is a completed task in a sibling repo (for example `<repo-A>/tasks/foo-202606`) being confused with an unimplemented task in the active repo (`<repo-B>/tasks/foo`). If the active repo code lacks the expected markers and history only proves a sibling-repo task, classify the active task as not implemented rather than stale-completed; do not delete it.
5. Run proportional focused verification only when it materially improves classification and is safe/read-only. Prefer the commands named in the task docs or the closest focused test files.
6. Classify conservatively:
   - **Complete**: current code matches acceptance criteria; relevant focused tests/review evidence exist or pass; any skipped manual smoke is explicitly documented and non-blocking.
   - **Complete with caveat**: code/test evidence is strong, but task docs have stale checkboxes or missing standalone review artifacts. Report the caveat before cleanup.
   - **Incomplete**: acceptance criteria are not implemented, current focused tests fail, required artifacts are missing for a workflow gate, or the implementation contradicts the spec.
   - **Parked/deferred**: trigger gates are intentionally unmet, e.g. performance follow-ups waiting on production metrics.
6. Never delete ambiguous dirs in the same step as discovery unless the user explicitly asks to remove a named cleanup set.

## Red flags that override checked TODOs

- Current focused tests fail for task-owned surfaces.
- The implementation uses a different API contract than the task spec and the docs were not updated to bless the new contract.
- The current code violates explicit out-of-scope constraints, such as adding navigation/routes the spec forbids.
- Required cross-repo or external review artifacts are absent when the task’s own workflow made them blocking.
- A progress file claims verification passed but current code inspection contradicts it.

## Reporting format

Group results by cleanup recommendation:

- `Cleanup candidates — appear actually complete`
- `Keep — actually incomplete or materially inconsistent`
- Optional `Complete with caveat` notes under the cleanup candidates

For each directory include a one-line reason and the strongest evidence path or command result. Keep the report action-oriented: identify the next removal set separately from dirs that require implementation/doc reconciliation.
