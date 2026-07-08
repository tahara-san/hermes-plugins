# Plan-code stale TODO finalization after saved review

Use when resuming an existing `plan-code` task where implementation, verification, and mandatory review artifacts already exist, but live TODO/progress docs still show finalization items unchecked or no final report exists.

## Pattern

1. **Classify before coding.** Read `spec.md`, `todo.md`, `verification.md`, `simplify.md`, saved review artifacts, current source diff, and git status. Distinguish real missing work from stale checklist bookkeeping.
2. **Verify saved review is real.** A `final-review.json` only counts if it references a parseable passing reviewer artifact and the pending/delegate artifact is completed or superseded. A dispatched/pending review is not approval.
3. **Rerun proportional verification on the current tree.** At minimum rerun the focused regressions and `git diff --check`; rerun broader package-local tests/builds when the task docs list them or the source diff is still dirty.
4. **Handle live-smoke drift truthfully.** If an old live URL no longer returns the original failure but also no longer returns the earlier success (for example `404 target_content_not_found` because fixture data moved), record it as a live-data availability deviation, not as a fresh `200` proof.
5. **Finalize docs narrowly.** Patch TODO checkboxes and add/update `final-report.md` only after verification/review evidence is confirmed. Do not change source just to satisfy stale prose unless source actually violates the spec.
6. **Avoid stale artifact loops.** If final docs/review artifacts change after the implementation review, create a placeholder final artifact-consistency JSON first or explicitly exclude the consistency artifact from judging itself, then overwrite it with the final passed/failed consistency result.
7. **Scope dirty work.** Keep unrelated dirty files/directories out of the task review/finalization bundle and report them separately.

## Consistency checks to run

- Live TODO has no unchecked real task items.
- Final report exists and records verification/review/deviations/no-commit truthfully.
- Aggregate final review passed and references the raw Codex-style reviewer artifact.
- Any pending review artifact is resolved/superseded.
- `git diff --check` still passes after doc edits.
- Historical review bundles are treated as preserved evidence, not live TODO state, if they contain old snapshots.
