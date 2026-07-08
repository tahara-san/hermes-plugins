# Plan-doc pending delegate review blocker

Use when an explicit `/skill plan-doc` flow has created task docs and a saved review bundle, but the mandatory Codex-style Hermes `delegate_task` plan review does not return or cannot be recovered in the current turn.

## Pattern

1. Do not treat a dispatched delegation as approval. A companion Claude/other reviewer approval does not satisfy the missing Codex leg.
2. Bound the wait/recovery attempt: check whether the delegation surfaced in chat/logs/session history using the normal review-recovery path, but do not keep polling indefinitely.
3. Save a blocker artifact under the task's `reviews/` directory, for example `plan-review-blocked.json`, with:
   - `passed: false`;
   - status such as `BLOCKED_PENDING_CODEX_DELEGATE_REVIEW`;
   - review bundle path;
   - delegation id;
   - completed review artifacts/verdicts;
   - exact resume steps.
4. Update `todo.md` / notes truthfully: task docs exist, Claude/other review may be approved, but aggregate plan review is not complete until the missing Codex verdict is saved or explicitly waived.
5. Final response must say "stuck" or "blocked" on the review gate and must not present the plan-doc flow as fully complete.
6. On resume, either save the returned JSON verdict or rerun a narrower uniquely named `delegate_task` review against the same bundle. If docs change after any review finding, regenerate the bundle and rerun all required review legs.

## Artifact skeleton

```json
{
  "passed": false,
  "status": "BLOCKED_PENDING_CODEX_DELEGATE_REVIEW",
  "bundle_path": "tasks/<slug>/reviews/plan-doc-review-bundle.md",
  "codex_delegate": {
    "delegation_id": "deleg_...",
    "artifact_path": null,
    "status": "dispatched but no completed verdict surfaced after bounded wait",
    "resume_steps": [
      "Check whether the delegation verdict surfaced in chat/logs/session history.",
      "If available, save it as tasks/<slug>/reviews/codex-plan-doc-review.json.",
      "If unavailable, rerun a narrower Hermes delegate_task plan-doc review against the saved bundle.",
      "If docs change after review feedback, regenerate the bundle and rerun all required review legs."
    ]
  },
  "aggregate_verdict": "not approved because required Codex delegate review is missing"
}
```
