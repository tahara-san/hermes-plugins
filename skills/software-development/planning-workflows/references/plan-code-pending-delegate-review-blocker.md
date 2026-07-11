# Plan-code pending interactive Codex review blocker handoff

Use this when a required `plan-code` implementation is coded and verified, one review leg (often Claude Code via `claude-i`) has passed, but the mandatory interactive Codex TUI session has not produced a parseable final verdict.

## Principle

A started TUI session is not approval. If the interactive Codex review is mandatory and no parseable attested verdict is saved, the task is **blocked**, not complete, even when implementation tests/build and the companion reviewer pass. A user saying to proceed in autonomous/YOLO mode is not, by itself, a waiver of a mandatory `plan-code` review lane; attempt bounded tmux recovery, then stop fail-closed unless the user explicitly waives that lane.

## Sequence

1. Keep the final implementation bundle immutable while the Codex TUI is running.
2. Follow `codex-cli-review-lane.md`: confirm the managed tmux session exists, capture a wide pane window, and compare the pane's explicit verdict and bundle identity with the saved raw-pane artifact. A session name, startup banner, or partial response is not approval.
3. If a completed verdict is visible, save the raw pane capture, normalize it to the required parseable schema, verify the CLI/model/effort/bundle attestation, and proceed with the normal aggregate/final consistency path.
4. If no verdict is recoverable after bounded waits, save a blocker artifact under `tasks/<slug>/reviews/`, for example `codex-implementation-review-blocked.json`, containing:
   - `passed: false`
   - status such as `BLOCKED_PENDING_CODEX_REVIEW`
   - tmux session name and state
   - final bundle path and hash
   - latest raw pane capture path
   - CLI/model/effort attestation state
   - completed verification gates and companion review artifact
   - exact resume steps
5. Update `todo.md` truthfully:
   - mark implementation/test/build/simplify/companion-review rows complete when backed by real output;
   - mark the Codex review and aggregate final-review rows `[!]` blocked/deviation;
   - leave final-report/completion rows unchecked unless actually produced.
6. Add a short `notes.md` handoff with implemented scope, verification evidence, companion review verdict, and the pending tmux session/artifact state.
7. Run `git diff --check` after artifact updates.
8. Final response must state clearly: implementation is done and verified, but `plan-code` completion is blocked on the mandatory review leg. Do not commit/push or claim completion unless the user explicitly waives the missing review leg or it later returns and is saved.

## Resume path

On resume, first try to recover the original managed tmux session and capture its final pane. If no parseable attested verdict is recoverable, start a fresh pinned interactive Codex TUI session against the current final implementation bundle. Never substitute `delegate_task`, `codex exec`, or `codex review`. If any task docs or source files changed since the prior companion review, regenerate the bundle and rerun all mandatory review legs before finalizing.
