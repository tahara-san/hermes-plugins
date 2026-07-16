# Plan-doc pending interactive Codex review blocker

Use when an explicit `/plan-doc` flow has created task docs and a saved review bundle, but the mandatory interactive Codex TUI plan review has not produced a parseable attested verdict.

## Pattern

1. Do not treat a started tmux session as approval. A companion Claude/other reviewer approval does not satisfy the missing Codex leg.
2. Bound the recovery attempt: confirm the managed tmux session exists, capture a wide pane window, and verify any final verdict against the bundle identity and model/effort attestation. Do not keep polling indefinitely.
3. Save a blocker artifact under the task's `reviews/` directory, for example `plan-review-blocked.json`, with:
   - `passed: false`;
   - status such as `BLOCKED_PENDING_CODEX_TUI_REVIEW`;
   - review bundle path;
   - tmux session and latest raw pane capture;
   - completed review artifacts/verdicts;
   - exact resume steps.
4. Update `todo.md` / notes truthfully: task docs exist, Claude/other review may be approved, but aggregate plan review is not complete until the missing Codex verdict is saved or explicitly waived.
5. Final response must say "stuck" or "blocked" on the review gate and must not present the plan-doc flow as fully complete.
6. On resume, either save the recovered raw pane plus normalized JSON verdict or rerun a narrower uniquely named interactive Codex TUI review against the same bundle. Never substitute `delegate_task`, `codex exec`, or `codex review`. If docs change after any review finding, regenerate the bundle and rerun all required review legs.

## Artifact skeleton

```json
{
  "passed": false,
  "status": "BLOCKED_PENDING_CODEX_TUI_REVIEW",
  "bundle_path": "tasks/<slug>/reviews/plan-doc-review-bundle.md",
  "codex_tui": {
    "tmux_session": "codex-plan-doc-...",
    "raw_pane_path": "tasks/<slug>/reviews/codex-plan-doc-raw.txt",
    "artifact_path": null,
    "status": "started but no parseable attested verdict was recoverable after bounded capture",
    "resume_steps": [
      "Capture the managed tmux pane and check for a final verdict.",
      "If available, save it as tasks/<slug>/reviews/codex-plan-doc-review.json.",
      "If unavailable, rerun the pinned interactive Codex TUI review against the saved bundle.",
      "If docs change after review feedback, regenerate the bundle and rerun all required review legs."
    ]
  },
  "aggregate_verdict": "not approved because required interactive Codex TUI verdict is missing"
}
```
