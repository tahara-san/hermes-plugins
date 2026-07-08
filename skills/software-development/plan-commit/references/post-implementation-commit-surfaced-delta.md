# Post-implementation commit surfaced delta during cleanup

Use this when a `plan-commit` flow has already committed/pushed the implementation, then the cleanup dry-run or status check reveals additional dirty/untracked in-scope source/test files.

## Pattern

1. **Stop the cleanup commit immediately.** Do not delete the task directory or continue with `git rm` while in-scope source/test files are dirty.
2. **Unstage/restore only cleanup deletion state.** If `git rm -r tasks/<slug>` was already applied, run:
   ```bash
   git restore --staged -- tasks/<slug>
   git restore -- tasks/<slug>
   ```
   Then re-run `git status --short --branch`.
3. **Classify the surfaced delta.** Inspect the dirty/untracked source/test files and decide whether they are:
   - intended follow-up implementation for the same task;
   - unrelated local work; or
   - accidental/stale work to discard.
4. **Ask the user when classification changes commit scope.** If the delta is plausibly in-scope but was not part of the reviewed/pushed implementation commit, offer choices: include as follow-up after verification/review, leave uncommitted, discard, or stop.
5. **If including the delta, treat it as a real follow-up implementation commit.** Run proportional verification, create/update a delta bundle, rerun required review legs for the delta or regenerated final bundle, update task docs/final-review/pre-commit consistency, then commit/push the follow-up implementation before task cleanup.
   - If the follow-up is a shared-component extraction/refactor, do not rely only on mocked child/prop-wiring tests. Add or update at least one real-render regression at the integration boundary that proves the external contract still holds (for example, feed mode really hides all controls/actionbars, not just the one prop or child you expected to gate).
   - When a review fails on a follow-up delta, save the failed verdict as superseded historical evidence, patch the source/test gap, regenerate the delta bundle, and rerun both required review legs. A pre-fix passing review is stale after the fix unless it is rerun against the post-fix bundle.
6. **Only resume cleanup after the follow-up implementation commit is pushed and read back.** Re-run `git rm -r --dry-run -- tasks/<slug>` and ensure it lists only the completed task directory.

## Why

A staged cleanup deletion can hide the fact that a task directory was already restored/deleted locally while in-scope source remains dirty. Continuing directly to the cleanup commit would leave reviewed task artifacts removed while unreviewed implementation changes remain local. A pushed implementation commit does not imply the worktree is clean; always read back full status before cleanup.

## Minimal readback checklist after first push

```bash
git status --short --branch
git diff --name-status
git ls-files --others --exclude-standard | sed -n '1,120p'
git rev-list --left-right --count @{u}...HEAD
```

If any in-scope source/test paths appear, pause cleanup and follow the pattern above.