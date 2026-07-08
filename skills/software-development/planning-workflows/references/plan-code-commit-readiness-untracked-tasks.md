# Plan-code commit readiness with untracked task directories

Use when a plan-code implementation is complete but task docs/directories may be stale, untracked, or unrelated.

## Checklist

1. Reconcile task docs against actual implementation and verification before deleting anything.
2. If the task directory is untracked and complete/stale, `rm -rf tasks/<slug>` removes it from the working tree but does **not** create a tracked deletion. Report that explicitly.
   - If the user explicitly asks for two commits — first implementation, then removal of the implemented task directory — and the completed task directory is currently untracked but is an intended task artifact, include that task directory in the first implementation commit. Only after that commit is pushed should `git rm -r --dry-run -- tasks/<slug>` / `git rm -r -- tasks/<slug>` be used for the second cleanup commit. Otherwise the cleanup commit is a no-op.
3. Before staging, list task status separately:
   - `git status --short tasks`
   - `git ls-files --others --exclude-standard tasks`
4. Stage intended implementation paths explicitly (for example `git add apps packages`) instead of `git add -A` when unrelated task dirs are present.
5. Verify staged contents:
   - `git diff --cached --name-only`
   - `git diff --cached --stat`
   - `git diff --cached --check`
   - `git status --short tasks`
6. Commit only after confirming unrelated task dirs remain untracked/unstaged.

## Final report

Include:
- whether the completed task dir was tracked or untracked,
- whether it was removed or simply excluded,
- exact unrelated untracked task paths left behind,
- commit SHA and push target if pushed.
