# HEAD-Committed Implementation with Recreated Task Artifacts

Use this pattern during `plan-commit` when the source/test implementation is already present in `HEAD` (for example a prior commit landed the code and a later cleanup removed task artifacts), but the current session recreates or updates task docs/review artifacts before committing.

## Problem

`git diff` may be empty for the actual implementation files even though the task artifacts still need a review/commit. A final review bundle built only from dirty diffs can falsely omit the implementation being claimed as complete.

## Pattern

1. Verify the implementation commit/history:
   - `git log --oneline --decorate -5`
   - inspect the commit or current source paths that implement the task.
2. Recreate/update task docs truthfully:
   - note that implementation source is already in `HEAD`;
   - record the implementation commit SHA when known;
   - keep current verification/full-suite evidence in task artifacts.
3. Build the final review bundle from:
   - current source snapshots for the relevant implementation/test files;
   - dirty task/issue artifacts;
   - scoped dirty diffs for artifact/issue updates;
   - git status and recent history.
4. Exclude volatile aggregate files such as `reviews/final-review.json` from the reviewed bundle when they only carry the latest delegate id; otherwise every saved delegate id makes the reviewed bundle stale.
5. After dispatching/recovering the final delegate review, save the verdict in the excluded aggregate file and run lightweight consistency checks:
   - no real non-`[x]` TODO rows;
   - final-review approved;
   - final report names the actual full-suite result and remaining issues;
   - `git diff --check` / staged `git diff --cached --check` pass.
6. If generated logs/review bundles fail `git diff --cached --check` only for trailing whitespace, normalize the intended generated artifacts, save a post-normalization consistency artifact, restage, and rerun the staged check before committing.

## Commit flow

- First commit: task artifacts plus related issue updates (even if source implementation was already in an earlier commit).
- Second commit: `git rm -r --dry-run -- tasks/<slug>` and then remove only that task directory.
- Final report should distinguish:
  - implementation commit already in history;
  - artifact/issue commit made now;
  - cleanup commit made now;
  - unrelated dirty work left untouched.
