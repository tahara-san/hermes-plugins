# Multi-task plan-code commit with artifact consistency

Use when `/skill plan-commit` is invoked after a batch session completed multiple `tasks/<slug>/` plan-code directories in one working tree.

## Pattern

1. **Treat `/skill plan-commit` as a two-step cleanup flow** when invoked directly:
   - first commit and push the implementation plus completed task artifacts;
   - then remove the completed task directories, commit, and push that cleanup.
   If the user only says plain "commit and push", stop after the implementation/artifact commit unless cleanup is explicit.

2. **Classify every dirty path before staging.** For each completed task:
   - verify `todo.md`, `spec.md`, `final-report.md`, and `reviews/final-review.json` agree the task is complete;
   - remove or supersede stale pending artifacts such as `codex-implementation-review-pending.json` when a passing recovered Codex verdict exists;
   - ensure final reports mention the canonical final artifact-consistency verdict path.

3. **Review active artifacts, not stale historical bundles.** Pre-commit consistency should judge live `spec.md`, `todo.md`, `final-report.md`, and active review JSONs. Historical bundles/raw transcripts may preserve pre-final unchecked rows and are reference-only unless the final report treats them as active evidence.

4. **Resolved reviewer suggestions belong in active verdicts.** If an active `final-review.json` or Codex review JSON still lists a suggestion that has since been resolved (for example "mark spec checkboxes complete" after the spec was patched), move that item out of active `suggestions` and into `reviewer_suggestions_original` plus `resolved_suggestions`. Otherwise a pre-commit consistency review can correctly fail because active verdicts contradict live docs.

5. **Normalize generated artifacts before committing.** Generated review bundles and raw pane captures often contain trailing whitespace, blank lines at EOF, or tab/space artifacts. If `git diff --cached --check` fails only in intended generated task artifacts:
   - strip line-end whitespace and collapse to exactly one final newline for intended `.md`/`.json` task artifacts;
   - restage the affected task dirs;
   - rerun `git diff --cached --check`.

6. **Run post-normalization consistency over the exact staged set.** After any generated-artifact normalization or artifact membership change:
   - build the consistency bundle from staged contents (`git show :path`), not just the worktree;
   - explicitly exclude the future consistency verdict file from its own scope;
   - save the passing verdict to each completed task's `reviews/final-artifact-consistency-review.json`;
   - restage those verdicts and rerun `git diff --cached --check` before committing.

7. **Stage explicitly across all intended tasks.** Avoid `git add -A`. Stage exact source/test paths plus the completed task directories. Verify:
   - `git diff --cached --name-status` contains only intended source/tests/task artifacts;
   - `git diff --name-status` and `git ls-files --others --exclude-standard` are empty or only contain intentionally unstaged unrelated work.

8. **Cleanup commit dry-run is mandatory.** After the implementation/artifact commit is pushed and branch divergence is `0 0`, run `git rm -r --dry-run -- tasks/<slug> ...` for all completed task dirs. Proceed only when every listed path is under those exact directories.

## Common pitfalls

- A stale pending Codex marker may coexist with a recovered passing Codex review. Do not commit both as active artifacts; remove the pending marker or clearly supersede it.
- Active review JSON suggestions can become stale after doc reconciliation. Treat them as active commit content, not harmless historical notes.
- Running consistency on worktree files before normalization is not enough; run a final staged consistency pass after normalization and after saving any verdict files.
- In multi-task batches, a single combined consistency verdict may be saved into each task directory if the prompt clearly reports per-task results and each task passes.
