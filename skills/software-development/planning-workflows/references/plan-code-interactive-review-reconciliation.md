# Plan-code interactive review reconciliation

Use this when a completed `plan-code` task discovers late that the required Claude Code review leg was not actually run through the configured interactive `claude-i`/tmux workflow, or when final task docs/review bundles contain stale unchecked historical content after implementation approval.

## Trigger signals

- The final TODO/spec says Claude Code default Opus/interactive review is required, but the saved artifact came from `claude -p` / print mode.
- Artifact-consistency review fails on stale embedded task-doc copies, old unchecked checklist rows, or review-bundle self-reference.
- Final review artifacts were written after source approval and the task docs need reconciliation before the user-facing completion report.

## Required pattern

1. Treat this as a workflow gate failure, not a harmless wording issue.
2. Load/use `claude-i` and run the missing interactive review in tmux or the PTY fallback. Verify the Claude Code banner/status line before the substantive prompt; for Buffdemy workflows, record the default Fable 5/xhigh banner when shown.
3. Save the interactive pane/verdict as the canonical Claude review artifact. If a previous print-mode artifact exists, overwrite it or clearly supersede it so downstream docs point at one canonical artifact.
4. Patch `spec.md`, `todo.md`, and aggregate review JSON to describe the real review path and verdict. Do not leave wording that claims interactive review if only print-mode ran.
5. Regenerate the final implementation bundle from current file contents. Exclude historical/superseded review bundles and plan-review artifacts unless they are deliberately in scope; otherwise stale embedded checklists can make a current task look incomplete. Generate large `git diff` content with direct filesystem/subprocess capture rather than a Hermes terminal output that may be capped or summarized; if a reviewer observes a literal truncation marker in the saved bundle, regenerate the bundle without changing implementation source/tests and document the artifact-only regeneration in the aggregate verdict.
6. If any source/test file changes after review approval, even a test-only cleanup, rerun the affected verification and both required review legs on the refreshed bundle. Save the rerun verdicts as the canonical artifacts or clearly supersede the old ones.
7. Run a narrow read-only artifact-consistency review over current task docs/review artifacts and the frontend/backend handoff docs. Exclude the consistency artifact itself from scope, then write the PASS/FAIL artifact afterward.
8. Rerun `git diff --check` for all repos that have intended task artifacts before the final response.

## Bundle hygiene

For final consistency bundles, include:

- current `git status --short` / `git diff --stat`;
- tracked implementation diff;
- intended untracked source/test/task docs;
- current canonical review artifacts;
- verification evidence;
- cross-repo handoff docs.

Avoid embedding obsolete review bundles or superseded artifacts in the final bundle unless the reviewer is explicitly checking artifact history. This prevents false failures from old unchecked TODOs and self-referential stale copies.
