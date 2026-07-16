# Delayed plan-commit cleanup after a plain commit/push

Use when the user first asks for a plain `commit and push`, then later invokes `/plan-commit` or otherwise asks to finish the plan-commit cleanup flow.

## Pattern

1. Treat the previously pushed implementation commit as the first phase if live readback proves:
   - current branch is synced with upstream;
   - the recent implementation commit contains the completed source/test changes and task artifacts;
   - the worktree is clean before cleanup.
2. Do not rerun expensive implementation verification solely for cleanup when the committed task artifacts already record passing tests/reviews and no source/task files are dirty.
3. Verify cleanup scope before deleting:
   - `git status --short --branch`
   - `git ls-files -- tasks/<slug>`
   - `git rm -r --dry-run -- tasks/<slug>`
4. Proceed only if the dry-run lists tracked paths exclusively under the completed task directory.
5. Apply `git rm -r -- tasks/<slug>`, then verify:
   - `git diff --cached --name-status` contains only `D\ttasks/<slug>/...` rows;
   - `git diff --cached --check` passes;
   - `git status --short --branch` has no unrelated staged or dirty files.
6. Commit and push the cleanup deletion, then read back:
   - `git status --short --branch`
   - `git log --oneline --decorate -5`
   - `git rev-list --left-right --count @{u}...HEAD`
   - task directory absence.

## Pitfall

Do not assume `/plan-commit` always starts from an uncommitted implementation. If the user previously said only `commit and push`, the correct behavior is to stop after that first push. A later explicit `/plan-commit` can then resume at cleanup-only phase, but only after readback proves the implementation commit is already pushed and the task directory is tracked.