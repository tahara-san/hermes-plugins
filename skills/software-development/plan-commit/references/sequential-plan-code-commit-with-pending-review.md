# Sequential plan-code commit with pending review gates

Use this reference when a user asks to execute and plan-commit several task directories in sequence, especially after issue-conversion created many untracked task dirs and source issue deletions.

## Pattern

1. Treat each task directory as its own atomic plan-code + plan-commit cycle.
2. After a task's implementation/review gates pass, commit and push that task's implementation plus task artifacts, then remove only that completed task directory in the cleanup commit.
3. Do not batch sibling untracked task dirs, conversion coverage files, or unrelated source issue deletions into the current task commit. Stage exact source paths, exact task dir, and only the converted issue file(s) owned by that task.
4. If a later task starts while unrelated dirty task dirs exist, keep reporting them as untouched/unrelated rather than absorbing them into the current staged scope.
5. If a mandatory delegate review is dispatched but does not re-enter or become recoverable, stop fail-closed for that task: save a `*-pending.json` artifact naming the delegation id, reviewed bundle, completed companion reviews, verification evidence, and exact resume steps. Do not commit, cleanup, or advance to the next task until the verdict is saved or explicitly waived.

## Staging and generated artifact pitfalls

- Deleted converted issue files may already be staged from an earlier attempt. If `git add`/`git add -u -- <deleted-path>` reports `pathspec ... did not match any files`, inspect `git diff --cached --name-status` before retrying; the deletion may already be staged.
- Generated review bundles often fail `git diff --cached --check` with `new blank line at EOF` or trailing whitespace after staging, even if source files are clean. Normalize only intended generated task artifacts, restage, rerun `git diff --cached --check`, then run or rerun the narrow post-normalization artifact-consistency check before committing.
- Build the post-normalization bundle only after the staged and unstaged scoped whitespace checks are clean; otherwise the verdict can go stale immediately when you normalize the bundle again.

## Handoff wording

When stopping on a pending review gate, say the task is implementation-verified but review-blocked, not complete. Include:

- completed commits for prior tasks;
- current dirty paths for the blocked task;
- pending delegation id and artifact path;
- verification commands/results already obtained;
- exact next step: recover/save the delegate verdict, or rerun/waive it before final review aggregation and commit.
