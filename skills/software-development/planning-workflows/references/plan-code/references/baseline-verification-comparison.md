# Baseline verification comparison for plan-code

Use this when a repo-wide verification command fails in files or systems that appear unrelated to the current plan.

## Goal
Distinguish a task regression from a pre-existing baseline failure without losing or mixing unrelated worktree changes.

## Safe pattern
1. Capture the current worktree first:
   - `git status --short`
   - `git diff --name-only`
   - if multiple repos are involved, capture each repo separately.
2. Prefer the narrowest passing task-scoped verification first. Baseline comparison is for broad commands such as repo-wide `tsc`, `lint`, `test`, or `build`.
3. If the worktree contains unrelated user/pre-existing changes, call that out in task docs before stashing. A whole-worktree stash may temporarily hide unrelated files too; this is acceptable only for a short baseline probe with guaranteed restoration.
4. Use a guarded stash/pop flow with restoration even on failure. For example:

```bash
set -euo pipefail
before_status=$(git status --short)
stash_output=$(git stash push --include-untracked -m plan-code-baseline-probe)
echo "$stash_output"
if printf '%s' "$stash_output" | grep -q 'No local changes'; then
  npx tsc --noEmit
else
  set +e
  npx tsc --noEmit > /tmp/plan-code-baseline.log 2>&1
  baseline_status=$?
  set -e
  sed -n '1,160p' /tmp/plan-code-baseline.log
  git stash pop --index
  after_status=$(git status --short)
  printf '%s\n' '--- status before baseline probe ---' "$before_status"
  printf '%s\n' '--- status after baseline probe ---' "$after_status"
  exit "$baseline_status"
fi
```

5. Interpret results:
   - Same failure on clean baseline: log/update an out-of-scope issue with the command, failing files, and baseline evidence. Do not block task completion if targeted task verification and other relevant gates pass.
   - Failure disappears on clean baseline: the task or unrelated current work caused it. Restore the stash, isolate the relevant diff, and fix before completion.
   - Stash pop conflict or status mismatch: stop and resolve restoration before doing any more implementation or reporting.

## Pitfalls
- Do not use baseline failure evidence to mark a task-specific failing test as passed. It only de-scopes unrelated broad-command failures.
- Do not leave the stash unapplied while continuing the plan.
- Do not delete task files until the out-of-scope baseline blocker is documented and all remaining executable plan checks are complete or explicitly blocked.
- Do not preserve transient command-output noise; keep the issue focused on durable file locations and the verified baseline comparison.
