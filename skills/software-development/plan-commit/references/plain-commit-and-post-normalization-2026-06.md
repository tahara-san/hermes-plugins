# Plain commit/push vs cleanup + post-normalization consistency

Session pattern from a completed plan-code task with unrelated dirty work in the repository.

## Plain `commit and push` means one commit

When the user says only `commit and push` after a plan-code task is complete:

1. Stage only the implementation paths and the completed `tasks/<slug>/` artifacts.
2. Run cached readback/checks.
3. Commit and push.
4. Stop after push/readback.

Do **not** remove `tasks/<slug>/` unless the user explicitly asks for cleanup, says `plan-commit`, or uses two-step wording such as `then remove the task dir and push again`.

In the final report, say whether the task directory was committed and whether it was removed.

## Staged whitespace can appear only after adding untracked task artifacts

A scoped working-tree check can pass before staging, but `git diff --cached --check` may fail after untracked generated task artifacts are added. Common offenders are copied Docker/Compose tables in review bundles or verification logs with trailing spaces.

Safe recovery pattern:

1. Confirm the failures are only inside intended generated task/verification artifacts.
2. Strip trailing whitespace only from those intended artifacts.
3. If the final report is meant to enumerate committed review artifacts, add a line for the new pre-commit/post-normalization consistency verdict before running that verdict.
4. Create a placeholder verdict JSON excluded from its own scope to avoid self-reference.
5. Generate a compact `post-normalization-artifact-consistency-bundle.md` from the exact staged scope, including:
   - `git status --short --branch`
   - `git diff --cached --name-status`
   - `git diff --cached --stat`
   - `git diff --cached --check`
   - canonical task docs/review/verifications
   - explicit exclusions for the future verdict file and the bundle itself
6. Run a read-only delegate consistency review over that bundle.
7. Overwrite the placeholder with the recovered passing JSON verdict.
8. Restage the verdict and rerun `git diff --cached --check` before committing.

Do not edit implementation source after a final review without a proportional delta review. Artifact-only whitespace normalization can be covered by the post-normalization consistency check instead of a full implementation re-review.
