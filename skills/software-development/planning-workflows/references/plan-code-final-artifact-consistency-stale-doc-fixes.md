# Plan-code final artifact-consistency stale-doc fixes

Use when a completed `/plan-code` task has passed implementation verification and mandatory reviewers, but the final artifact-consistency pass flags stale planning prose rather than source-code blockers.

## Pattern

1. Treat artifact-consistency warnings as real final-state issues even when implementation reviewers approved the code.
2. Fix stale task-doc prose narrowly:
   - update old pseudocode to the implemented contract;
   - label missing historical/source issue links as historical and absent in the current checkout instead of leaving broken Markdown links;
   - preserve immutable review bundles as historical inputs rather than regenerating them just because final docs changed.
3. Rerun a narrow artifact-consistency review after the doc-only fixes.
4. Overwrite the placeholder consistency artifact only after the rerun returns a clean verdict.
5. Do not rerun full implementation reviews for docs-only consistency fixes unless the docs change the implementation contract, verification claims, or reviewed scope.

## Example warning classes

- `spec.md` still shows `deleteAvatar({ id: ... })` even though the final backend contract is idless `deleteAvatar()`.
- A task source issue link points to a file that no longer exists in the current checkout; convert it to a historical source reference and state the file was absent during final review.
- Progress docs still say "review pending" after final-review artifacts have passed.

## Verification

- Run `git diff --check` after doc artifact edits.
- Run a read-only artifact-consistency review scoped to current task docs and review artifacts, explicitly excluding only the consistency artifact's own content when using the placeholder pattern.
