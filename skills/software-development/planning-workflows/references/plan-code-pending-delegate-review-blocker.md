# Plan-code pending delegate review blocker handoff

Use this when a required `plan-code` implementation is coded and verified, one review leg (often Claude Code via `claude-i`) has passed, but the mandatory Codex-style `delegate_task` review was dispatched and does not return to the parent chat after bounded waits.

## Principle

A dispatched delegate is not approval. If the Codex-style review is mandatory and no parseable verdict is saved, the task is **blocked**, not complete, even when implementation tests/build and the companion reviewer pass. A user saying to proceed in autonomous/YOLO mode is not, by itself, a waiver of a mandatory `plan-code` review lane; keep driving bounded recovery/fallback attempts, then stop fail-closed unless the user explicitly waives that lane.

## Sequence

1. Keep the final implementation bundle immutable while waiting for the delegate review.
2. Use `requesting-code-review` → `references/delegate-review-status-recovery.md` to check logs/session search for the delegation id or unique bundle phrase.
   - When rerunning with a compact bundle, keep it comfortably below the Hermes `read_file` guard or instruct the reviewer to read paginated ranges from the start. A file can be under ~100 KB on disk but still exceed the read limit once line-number/serialization overhead is added, so aim closer to ~80–85 KB or provide explicit `offset`/`limit` guidance.
3. If a completed verdict is recovered, save it as the Codex implementation review artifact and proceed with the normal aggregate/final consistency path.
4. If no verdict is recoverable after bounded waits, save a blocker artifact under `tasks/<slug>/reviews/`, for example `codex-implementation-review-blocked.json`, containing:
   - `passed: false`
   - status such as `BLOCKED_PENDING_CODEX_REVIEW`
   - delegation id
   - final bundle path
   - completed verification gates and companion review artifact
   - exact resume steps
5. Update `todo.md` truthfully:
   - mark implementation/test/build/simplify/companion-review rows complete when backed by real output;
   - mark the Codex review and aggregate final-review rows `[!]` blocked/deviation;
   - leave final-report/completion rows unchecked unless actually produced.
6. Add a short `notes.md` handoff with implemented scope, verification evidence, companion review verdict, and the pending delegation id.
7. Run `git diff --check` after artifact updates.
8. Final response must state clearly: implementation is done and verified, but `plan-code` completion is blocked on the mandatory review leg. Do not commit/push or claim completion unless the user explicitly waives the missing review leg or it later returns and is saved.

## Resume path

On resume, first try to recover the original delegate verdict. If still unavailable, rerun a new Codex-style delegate review against the current final implementation bundle. If any task docs or source files changed since the prior companion review, regenerate the bundle and rerun all mandatory review legs before finalizing.
