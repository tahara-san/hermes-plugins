# Plan-code post-verdict completion edits

Use this when a final artifact-consistency review passes, but the agent then needs to mark task docs or progress docs complete.

## Lesson

A passing artifact-consistency verdict only covers the artifacts as they existed in the reviewed bundle. If `progress.md`, `todo.md`, phase TODOs, final reports, or canonical review JSON are changed after that verdict to convert `pending` / `[~]` / `[ ]` language into complete language, those edits are live task-artifact changes and stale the just-passed verdict for finality.

## Safe sequence

1. Save the passing reviewer verdict and canonical copy.
2. If task docs still need completion edits, patch them narrowly.
3. Generate a new active-scope bundle that includes:
   - the newly edited task/progress docs;
   - the saved passing verdict;
   - the canonical verdict file;
   - manual-gate evidence if the completion claim depends on it;
   - a stale-phrase/status scan over active artifacts.
4. Create a new self-excluded placeholder for this post-completion consistency pass.
5. Dispatch a read-only artifact-consistency review focused only on the post-verdict doc/artifact edits.
6. If it passes, save/canonicalize that final verdict, overwrite/retire the placeholder, validate JSON, run scoped `git diff --check`, and only then report final completion.

## Pitfalls

- Do not update completion checkboxes after a passing consistency verdict and then report completion without another narrow consistency pass.
- Do not let a preserved session TODO that still says an older delegate is in progress override saved canonical verdicts; reconcile saved artifacts first.
- Do not patch historical artifacts after the final pass just because broad string scans find old words inside reference-only files. If cleanup is necessary, treat it as another artifact edit and rerun consistency.
- Keep the rerun narrow: source/test implementation review does not need to rerun when the only changes are task-doc and verdict-persistence artifacts.
