# Stale task reset reconciliation pattern

Use when a task directory looks incomplete because phase TODOs/progress files are stale, but current code may already implement a newer or stricter contract.

## Trigger

- User says a task is "not fully complete" or asks to resume an old `tasks/<slug>/` directory.
- Phase checkboxes remain unchecked, but git history/current source suggests a reset/replacement implementation landed.
- The task spec describes an older hybrid/migration path while source/tests implement a clean-slate or superseding contract.

## Procedure

1. **Audit before coding.** Read `spec.md`, `progress.md`, all phase TODOs, notes, git history for the task, and current source/tests for the named surfaces. Do not blindly resume the first unchecked checkbox.
2. **Classify contract drift.** Separate:
   - implemented reset/new-contract behavior;
   - old-contract items that are truly missing;
   - old-contract items that are superseded/deferred and should not be implemented without a new decision.
3. **Verify proportionally.** Run focused tests/builds that prove the current contract, including cross-repo model/schema tests when the task spans repos. Record exact commands/results in task docs.
4. **Reconcile docs, not code, when source is correct.** Patch `progress.md` and phase TODOs to mark each old item as completed, superseded, or deferred. Add a status notice to the historical spec so future agents do not resurrect obsolete instructions.
5. **Be explicit about deferred follow-ups.** Route-level features, production backfills, cron jobs, rollback flags, or feed/index work that are outside the reset contract should be named as deferred/out of scope and require a fresh task to reopen.
6. **Review the reconciliation.** Build a self-contained review bundle containing git status/diff, updated task docs, relevant source excerpts, and verification output. Run the normal independent review + Claude Code review when the task workflow requires review artifacts. Save an aggregate `reviews/final-review.json`.
7. **Avoid false incomplete signals.** If the review bundle embeds historical diffs with old `[ ]` checkboxes, narrow final unchecked-item searches to active task docs (e.g. `file_glob="todo-phase-*.md"`) rather than counting the bundle's archived diff text.

## Pitfalls

- Treating unchecked boxes as authoritative when source/tests prove a superseding contract.
- Marking superseded hybrid items as simply "done" without explaining they were intentionally not implemented.
- Claiming old per-phase review gates happened when only fresh final reconciliation reviews exist. Say they are final reconciliation reviews, not reconstructed history.
- Letting a review artifact itself make a prior approval stale. Update final task docs to point to saved artifacts, then run a final whitespace/status check.
