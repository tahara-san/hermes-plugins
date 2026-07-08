# Plan-code after context compaction or stale preserved state

Use when a `/plan-code` session resumes after context compaction, preserved task-list replay, delayed background-process notifications, or other stale in-chat state while the working tree may already contain implementation work.

## Pattern

1. **Treat preserved task lists and delayed notifications as hints, not truth.** Reconcile against live repo/task state before continuing:
   - `git status --short` / `git diff --stat`
   - current `tasks/<slug>/spec.md`, `todo.md`, verification/review artifacts
   - relevant source/test reads for newly touched or untracked files
   - the newest verification logs for the same command class, not just the latest chat notification.
2. **Order evidence chronologically.** A background process completion can surface after a newer foreground rerun has already fixed and verified the issue. Label the older result `superseded` in notes/artifacts instead of re-opening completed work from the stale notification.
3. **Update the live todo list to match the working tree** after that reconciliation. Do not blindly re-enter stale `in_progress` items when RED tests, implementation, or verification already happened.
4. **If finalization artifacts change after an implementation review bundle is created, regenerate the bundle.** This includes:
   - task TODO/checklist updates
   - `verification.md` or final-report additions
   - extra tests added after an initial full-suite pass
   - review/pending-review artifacts that are intended commit artifacts.
5. **Include untracked intended files explicitly in bundles.** Standard `git diff` omits new task/source/test files; use full source snapshots or `git diff --no-index /dev/null <file>` for every in-scope untracked file so reviewers can judge the actual implementation.
6. **Do not count an async delegate dispatch as approval.** Until a parseable verdict artifact is saved, leave the review gate open or write a pending/blocker artifact with the delegation id, reviewed bundle path, completed verification, companion review artifacts, and resume steps.
7. **When a final bundle is refreshed after a reviewer was dispatched, dispatch a fresh review on the refreshed bundle** or explicitly mark the older pending result stale/superseded when it returns.
8. **Record verification evidence in a task artifact** when the task is large or context-heavy, so the gate can be audited outside chat. Keep it terse: command, result counts, known deviations, and whether any failures were superseded by later reruns.
9. **For frontend E2E blockers, separate base-URL/auth environment failures from product assertions.** If Playwright fails in global setup before app assertions, document that as an environment blocker with the exact URL/error. If local ports are owned by a shared dev proxy or other harness, do not kill it or claim a Next server is running; record that the listener is not a usable app endpoint and leave the E2E gate partial.
10. **Run a final diff hygiene check** such as `git diff --check -- . ':(exclude)tasks/<slug>/reviews/**'` after final artifact changes.

## Pitfalls

- A context-preserved todo list may show discovery/RED/implementation as pending even though the working tree already contains the code and passing tests. Verify before doing duplicate work.
- Delayed background-process output can report an old failure after a newer rerun is green. Do not overwrite current state from the delayed notice; attach it to the evidence timeline as the original RED or superseded failure.
- Writing `verification.md`, changing `todo.md`, or adding a final regression test after bundle creation makes the prior bundle stale for plan-code review purposes.
- Background delegate reviews can return after they are superseded by a newer bundle. Save/disposition them as stale; do not use them as current approval.
- Do not mark the task complete while the required Codex-style review is merely running. Report “implementation verified, review pending/blocking” instead.
- Do not rely on `git diff` alone for dirty plan-code repos with untracked files; reviewers may otherwise approve a bundle that omitted the new implementation.
