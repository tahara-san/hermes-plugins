# Small UI plan-code commit with generated bundle normalization

Use this reference when a small frontend/UI `plan-code` task has completed implementation reviews, has an untracked task directory of review artifacts, and the user invokes `/skill plan-commit`.

## Pattern captured

1. Treat `/skill plan-commit` as the two-step flow for this user's completed plan-code tasks:
   - commit + push implementation/source/tests plus the completed task artifacts;
   - then remove the now-tracked task directory and commit + push that cleanup.
2. Before staging, prove the task is commit-ready:
   - `todo.md` has no unchecked/pending rows;
   - final aggregate review and final artifact consistency artifacts exist and say passed;
   - the active Codex-style review artifact is saved, and any earlier async delegate reviews that became stale after reviewer-driven changes are marked superseded rather than counted.
3. Stage only the implementation/test files and the intended task directory. Do not use broad `git add -A` while other work could exist.
4. Generated Markdown review bundles can fail `git diff --cached --check` on blank lines with trailing spaces created by embedded diffs/snapshots. Normalize only the intended generated bundle by stripping line-end whitespace.
5. After normalization, write a narrow post-normalization consistency artifact that self-excludes and states source/test content was unchanged; stage it with the normalized bundle.
6. Rerun `git diff --cached --check` and staged name-status before the implementation commit.
7. After pushing the implementation commit, verify branch sync and a clean worktree before cleanup. Run `git rm -r --dry-run -- tasks/<slug>` and ensure every listed path is under that exact task directory before applying deletion.

## Pitfalls

- A returned async review can be stale if a non-blocking suggestion was adopted after dispatch; save it as superseded and rerun the final reviewer instead of aggregating it.
- Late async review results may keep arriving after the final accepted gate. Do not re-open the task for old handles automatically; compare the delegation id/bundle wording against the active final bundle and artifact set. If the finding was already fixed in a later accepted review, state it is superseded; if it names a live current-risk blocker, fix and rerun.
- Do not treat post-review artifact edits (TODO closure, final-review JSON, bundle normalization) as invisible. They need a final consistency artifact or an explicit self-exclusion pattern.
- Before staging an untracked completed task directory, remove or rename stale active-looking `*pending*` / `*blocked*` review markers only when their JSON body says they are superseded and current aggregate reviews pass. Otherwise leave them and fail closed.
- Generated Markdown review bundles can contain trailing whitespace from embedded source snapshots; normalize only the intended generated bundles, then save a post-normalization consistency artifact that says source/test content was unchanged.
- If the task directory was untracked before the first commit, include it in the implementation commit so the cleanup commit has real tracked deletions.
- When the cleanup commit deletes handoff docs such as `backend-contract.md`, mention the implementation commit SHA so the user can retrieve them with `git show <sha>:tasks/<slug>/<file>`.
