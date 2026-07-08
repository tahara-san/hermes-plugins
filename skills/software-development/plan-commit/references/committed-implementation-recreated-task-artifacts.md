# Committed Implementation With Missing/Removed Task Artifacts

Use during `plan-commit` when the implementation source is already committed in `HEAD` (or another recent local commit), but the task directory artifacts were deleted, never tracked, or removed by a prior cleanup commit before the user asks for the two-step plan-commit flow.

## Pattern

1. **Do not assume a clean diff means the implementation is missing.** Inspect recent commits and current source snapshots:
   - `git log --oneline --decorate -10`
   - `git show --name-status <suspected-implementation-commit>`
   - targeted reads/searches of the source/test files named by the task.
2. **If source is already in `HEAD`, build the review/commit bundle from current files, not only `git diff`.** A diff-only bundle will falsely omit the implementation.
3. **Recreate the task directory only from durable evidence:** current source snapshots, saved logs, final reports, recovered review verdicts, and out-of-scope issue files. Mark any reconstructed artifacts as reconstructed/current evidence rather than pretending old raw artifacts still exist.
4. **Recover async review verdicts before declaring the gate pending:** search Hermes logs for the delegation id and subagent session, read the subagent transcript, and save the parseable verdict artifact.
5. **Avoid self-referential review loops:** keep volatile delegate ids out of reviewed docs, or exclude the aggregate file that records the id from the reviewed bundle.
6. **Generated artifacts often need whitespace normalization.** Strip line-end whitespace from committed logs/bundles, rerun `git diff --cached --check`, then save a narrow post-normalization consistency artifact if task docs/review artifacts changed during commit readiness.
7. **Commit sequence:**
   - Commit the reconstructed task artifacts and any associated issue-file updates as the implementation/artifact commit.
   - Push and read back branch sync.
   - Then remove only the task directory with `git rm -r --dry-run` / `git rm -r`, commit, push, and read back that the task directory is no longer tracked.

## Pitfalls

- Do not stage unrelated task directories while recreating the missing one.
- Do not regenerate a review bundle from dirty diff only when implementation source is already committed.
- Do not keep a stale source comment pointing at a task/issue file that the cleanup commit will delete.
- Do not count a delegation dispatch id as a review pass; save the actual verdict recovered from logs/session history.