# Implementation Diff Review for Plan-Code Tasks

Use when the user asks Claude Code to review local diffs after a `plan-code` task is implemented, especially when task docs/review artifacts are untracked.

## Pattern

1. Keep the Claude session read-only. Prompt explicitly: do not edit files; do not run tests/build/lint unless a missing fact blocks the verdict.
2. Build a self-contained bundle before launching Claude:
   - `git status --short`
   - `git diff --stat`
   - tracked `git diff` for the intended implementation/test paths
   - verification commands and real results already run by Hermes
   - static scan result, if used by the gate
   - full contents of relevant untracked task artifacts (`spec.md`, `todo.md`, review JSON/markdown) so Claude does not have to discover them interactively.
   - current snapshots of the key changed source/test files, especially when the diff is large enough that any tool may truncate output.
3. Validate the bundle before review:
   - search the saved bundle for truncation markers such as `[OUTPUT TRUNCATED` or `... omitted ...`;
   - ensure any included source snapshots are from the current working tree, not stale baseline copies;
   - if the bundle is truncated or stale, rebuild it with direct `git`/file reads (not capped tool output) before launching reviewers.
4. Launch Claude Code through tmux with `claude` (not `claude -p`) and paste a prompt pointing at the bundle.
5. If Claude requests to read the prepared `/tmp` bundle, allow that read. Allow narrow read-only source-file inspection if Claude asks to verify a specific hunk in context.
6. Save the complete verdict under the task directory, e.g. `tasks/<slug>/reviews/claude-code-diff-review.md`, including:
   - timestamp
   - Claude Code version/session if known
   - bundle path
   - included verification evidence
   - exact verdict, blocking findings, non-blocking suggestions, and summary
   - disposition of non-blocking suggestions.
7. If Claude returns blocking findings, fix narrowly, rerun affected verification, rebuild the bundle, and rerun Claude review.
8. If Claude returns only non-blocking suggestions, prefer avoiding post-review churn unless the suggestion materially improves correctness. If left unapplied, document why in the review artifact.

## Unimplemented / docs-only task state

If a user asks for a final Claude review but the selected `plan-code` task has no implementation diff yet, still run the read-only gate rather than inventing approval or skipping the request. Build a bundle that makes the absence explicit:

- `git status --short` for the whole repo and the selected task path.
- `git diff --stat` and the scoped tracked diff for the declared implementation/test paths.
- Full untracked task docs (`spec.md`, `todo.md`, existing review artifacts if any).
- Any lightweight verification already possible, such as scoped `git diff --check` and static scan of tracked added lines.
- A scope note saying this is a requested final review and that the current tree appears docs-only / unimplemented.

Ask Claude to judge whether the current tree can be approved as the final implementation. If it returns `CHANGES_REQUIRED` because there is no implementation, save that verdict under the required review path (for example `tasks/<slug>/reviews/final-review.json`) with `passed: false`, model/effort, bundle path, blocking findings, and real timestamp. Report the task as blocked/not complete; do **not** mark TODOs complete or claim the normal `plan-code` sequence passed.

## Pitfalls

- Plain `git diff` omits untracked task docs and review artifacts. Include their contents in the bundle or Claude may approve an incomplete scope.
- A post-review artifact write changes the working tree. Before commit/push, run a final staged-file check and whitespace check; do not silently stage unrelated task directories.
- Do not count an incomplete pane capture as approval. The saved output must include an explicit `VERDICT: APPROVED` or `CHANGES_REQUIRED` section.
- Do not turn a docs-only/unimplemented task into a fake final approval just to satisfy a requested final-review gate; a saved `CHANGES_REQUIRED` artifact is the correct durable outcome.
