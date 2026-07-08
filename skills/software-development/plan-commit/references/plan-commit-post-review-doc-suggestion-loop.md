# Plan-Commit Post-Review Doc Suggestion Loop

Use this during `plan-commit` when commit-readiness checks or reviewers find stale task-doc/review-artifact wording after implementation reviews already passed.

## Pattern

1. Save the reviewer verdict that found the stale wording.
2. If the suggestion is adopted, treat the doc edit as a real post-review artifact change.
3. Regenerate the pre-commit/task artifact bundle from current files.
4. Run a narrow final consistency review over the regenerated bundle before staging.
5. Save both the completed review artifact and a superseded marker for any pending/old artifact.
6. Only after the final consistency review passes, update `todo.md`/`final-report.md` to complete and run final JSON + `git diff --check` checks.
7. If the final consistency reviewer gives another non-blocking doc suggestion, prefer recording it in the aggregate final verdict unless it is a real contradiction. Adopting every cosmetic doc suggestion can create a stale-review loop.

## Why

Plan-code task directories are commit content. A source-correct fix can still be unready to commit if live `notes.md`, `todo.md`, `final-report.md`, or aggregate review JSON contradict the corrected contract. Conversely, adopting every optional wording improvement after approval forces another review round. Distinguish contradictions from optional discoverability improvements.