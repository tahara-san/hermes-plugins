# Task cleanup and stale-doc reconciliation

Use this when cleaning `tasks/` directories or when the user says a task should be complete but the task docs still show open items.

## Completed task directory cleanup

1. Start with a dry-run classification of every immediate `tasks/<slug>/` directory.
2. Treat `tasks/out-of-scope-issues/` as an issue log, not a normal completion candidate.
3. Disambiguate “docs” before deleting anything. In Buffdemy repos, a user saying stale “docs” often means the top-level `docs/` directory, not documentation files under `tasks/`. If the target could be either `docs/` or task docs/review artifacts, inventory both paths and either choose the explicitly named path or ask one focused clarification before destructive removal.
4. Inspect git state before deletion:
   - tracked deletions are intended cleanup only if the directory is classified complete;
   - modified/untracked files in other task dirs or source paths are unrelated work unless the user explicitly includes them.
5. Delete only the confirmed cleanup set, then verify:
   - remaining directories under `tasks/`;
   - `git status --short -- tasks`;
   - staged/unstaged separation if committing.
5. If asked to commit/push the cleanup, stage with explicit positive pathspecs for the removed task dirs (for example `git add -u -- tasks/foo tasks/bar`), not `git add -A` or broad `tasks/`, and read back `git diff --cached --name-status` before committing.
6. If `git status --short` shows surprising staged deletions in another task directory, stop the commit path and separate index state from worktree state before acting:
   - inspect `git diff --cached --name-status` and `git diff --name-status`;
   - use `git ls-files --stage -- <path>` / `git ls-files --deleted -- <paths>` to determine whether the path is tracked, staged, or only unstaged;
   - unstage unrelated paths when possible, but if a directory-level pathspec does not match tracked files, re-check the exact cached file list instead of forcing broad resets;
   - only then stage the intended cleanup with `git add -u -- <confirmed-task-dir>` and re-run `git diff --cached --check`.
7. For `tasks/out-of-scope-issues/`, cleanup is issue-file based rather than directory based. When the user asks to remove resolved issues, first scan/read the issue files, correlate against the current implementation/commit history or focused verification, then delete only the confirmed resolved issue files. Leave unresolved or merely-overlapping issue files untouched and explicitly report remaining untracked issue files.
8. If the wrong task files were removed and the user asks to restore them, first recover tracked task files with `git restore -- tasks` (or the narrower affected path), then verify `git status --short -- tasks`. Be explicit that untracked task artifacts cannot be restored from Git after deletion unless another backup exists. Only after restoring the mistaken path should you proceed to the intended deletion target.
9. Final report must name:
   - removed task dirs or resolved issue files;
   - kept task dirs/issues and why;
   - updated/untracked task dirs or issue files left alone;
   - whether the removal was tracked deletion or untracked cleanup.

## When the user thinks an incomplete-looking task is finished

Do not rely on checkboxes alone. Task docs often lag behind uncommitted implementation work.

1. Read `progress.md`, `todo*.md`, runtime-fix plans, review artifacts, and current git status for the task and likely implementation paths.
2. Compare open TODOs with current code/test files. Planned files may now exist untracked even while TODOs still say they are missing.
3. Run proportional focused verification before answering when safe:
   - typecheck/build/lint if the task docs list them as blockers;
   - focused unit tests named by the task;
   - test discovery commands (for example Playwright `--list`) when docs claim specs are absent;
   - focused E2E only if the task requires live coverage and the dev stack is available.
4. Classify each open item as one of:
   - **stale doc**: implementation/test exists and verification passes;
   - **real blocker**: focused verification fails or acceptance criteria are unmet;
   - **external/unrelated blocker**: broad-suite failure outside the task scope that should be fixed separately or logged under out-of-scope issues;
   - **unverified**: code may exist but required runtime/browser/review evidence has not run.
5. Do not mark the task complete or remove its directory until the final closure gates are satisfied: focused verification, documented deviations, simplify/review gates where required, and reconciled task docs.

## Reporting pattern

Use a short action-oriented structure:

- `Already resolved / stale in docs` — list verified passing items and command outputs.
- `Actual remaining blockers` — list failing commands and exact failure symptoms.
- `Doc/review reconciliation left` — list task files that need checkbox/progress updates.
- `Bottom line` — say whether the task is complete, complete-with-caveat, incomplete, or parked.
