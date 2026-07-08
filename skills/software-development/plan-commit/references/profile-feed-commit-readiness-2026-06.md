# Profile feed commit-readiness recovery (2026-06)

Use this as a concrete example when a plan-code implementation is complete but commit prep exposes stale artifacts or async review state.

## What happened

- The user invoked `/skill plan-commit` after a large profile Question/Answer feed task.
- Source verification was already green, but task docs still contained stale `pending`/unchecked final-review rows.
- A final implementation review delegate had completed but did not surface in the parent chat.
- Generated review bundles contained Markdown trailing whitespace, causing `git diff --cached --check` to fail during staging.
- An unrelated untracked task directory existed and had to remain unstaged while committing the intended task.

## Recovery pattern

1. Treat preserved session TODOs as potentially stale; reconcile them against live task docs and actual saved review artifacts.
2. For a missing delegate result, recover it from Hermes logs:
   - find the subagent session with `grep -n "<delegation_id>\|<unique prompt phrase>" ~/.hermes/logs/agent.log | tail -80`;
   - confirm completion with `grep -n "<subagent_session_id>" ~/.hermes/logs/agent.log | tail -120`;
   - read the session directly with `session_search(session_id="<subagent_session_id>", profile="default")`;
   - if persisted to `/tmp/hermes-results/...`, parse that JSON and extract the last assistant message with non-empty `content`.
3. Save the recovered verdict as a review artifact before marking TODO/final-report rows complete.
4. Run a narrow artifact-consistency review over `todo.md`, `final-report.md`, and final review artifacts. If it fails, patch the stale docs and rerun; save both the final verdict and any relevant supersession notes.
5. Before committing, run:
   - `grep -RIn '^- \[ \]' tasks/<slug>/todo.md tasks/<slug>/final-report.md || true`
   - a grep for stale pending review phrases used in that task;
   - `git diff --cached --check` after staging.
6. If `git diff --cached --check` fails only inside intended generated task Markdown, strip trailing whitespace in those generated artifacts, restage, and rerun the check.
7. Stage explicit intended paths. Leave unrelated untracked task directories unstaged and report them after commit.

## Durable lesson

Commit readiness is not just `git add && commit`: for plan-code tasks, task artifacts are product artifacts. The commit is not ready until live docs, saved review artifacts, staged paths, and final status all agree.