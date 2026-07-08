# Generated artifact normalization and post-check pattern

Use this when committing completed `plan-code` task directories whose review bundles or logs are generated Markdown/JSON artifacts.

## Trigger

- `git diff --cached --check` fails only inside intended generated task artifacts (for example `reviews/*bundle.md`) with trailing whitespace, `space before tab`, or blank EOF lines.
- The staged source/test diff is otherwise correct and reviewed.

## Pattern

1. Normalize only the intended task artifacts, never unrelated dirty files:
   - strip trailing spaces/tabs at line ends;
   - collapse extra blank EOF lines to one final newline;
   - preserve semantic content.
2. Restage only the affected task directory or exact generated artifact paths.
3. Rerun:
   - `git diff --cached --check`
   - `git diff --cached --name-status`
4. Because the staged task artifacts changed after the pre-commit consistency verdict, create a small post-normalization consistency bundle that includes:
   - staged `git diff --cached --name-status`;
   - staged `git diff --cached --check` output;
   - live/staged `todo.md`, `final-report.md`, `final-review.json`, and the pre-commit consistency verdict;
   - a statement that the future post-normalization verdict excludes itself from scope.
5. Run a bounded read-only consistency review and save the verdict under `tasks/<slug>/reviews/post-normalization-artifact-consistency.json`.
6. Stage the verdict and final bundle, rerun `git diff --cached --check`, then commit.

## Commit reporting

In the final user report, list the post-normalization consistency verdict as a commit-prep check. If the task `final-report.md` is meant to enumerate every committed review artifact, update it before the final post-normalization check; otherwise avoid churn and classify the post-normalization verdict as commit-prep evidence rather than implementation-review evidence.

## Pitfalls

- Do not rerun full implementation reviews for whitespace-only normalization of generated artifacts.
- Do not skip the post-normalization check; the staged task docs are commit content.
- Do not use broad `git add -A` in dirty task worktrees. Stage exact implementation paths plus the target `tasks/<slug>/` directory only.
