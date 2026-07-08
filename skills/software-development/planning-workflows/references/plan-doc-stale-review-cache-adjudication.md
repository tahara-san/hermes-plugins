# Plan-doc stale review cache adjudication

Use when an async plan-doc review result arrives after one or more bundle/doc regenerations, or when a cached delegation summary is discovered out of order.

## Trigger

- A `delegate_task` / Codex-style review returns after newer plan-doc edits.
- Cache/log recovery finds a review summary, but it is unclear which bundle version it reviewed.
- The reviewer reports blockers that quote wording no longer present in the live spec/bundle.
- A companion Claude/CLI review has approved the current bundle while older delegate failures continue surfacing.

## Procedure

1. **Do not count the verdict immediately.** A dispatched review or cached summary is not approval/failure until tied to the current bundle.
2. **Compare chronology and content.** Check the current bundle path, byte size/mtime when available, saved pending artifacts, and whether the review quotes text that still exists in the current bundle/docs.
3. **Adjudicate against live docs/source.** If the finding is already resolved in current docs, save the stale review as `SUPERSEDED_FAILED_ADJUDICATED` with a short current-doc excerpt proving resolution. Do not patch or rerun just to satisfy stale wording.
4. **Patch only valid current risks.** If a stale review exposes a blocker that still applies, patch the active docs narrowly, mark every pre-patch review lane stale, regenerate the bundle, and rerun both required plan-doc lanes.
5. **Keep the current mandatory leg explicit.** If the current delegate for the latest bundle has not returned, save a pending artifact naming the exact delegation id, current bundle path, completed companion review artifacts, stale/adjudicated results, and resume steps. Do not create the aggregate `plan-review.json` yet.
6. **Avoid optional-churn loops.** If a current reviewer approves with non-blocking suggestions, record them rather than adopting them when adoption would stale an otherwise-current pending delegate, unless the suggestion is a concrete implementation footgun worth another full rerun.

## Artifact pattern

For stale failed reviews:

```json
{
  "reviewer": "codex-style delegate_task",
  "delegation_id": "deleg_xxx",
  "status": "SUPERSEDED_FAILED_ADJUDICATED",
  "reviewed_bundle": "older/pre-patch bundle",
  "current_bundle": "tasks/<slug>/reviews/plan-doc-review-bundle.md",
  "raw_output_path": "/home/.../subagent-summary.txt",
  "verdict_from_stale_review": { "passed": false },
  "adjudication": {
    "blocking_finding_applies_to_current_docs": false,
    "reason": "Current spec already pins the safe ordering/error semantics.",
    "current_spec_excerpt": "line-numbered excerpt"
  },
  "saved_at": "ISO timestamp"
}
```

For pending current delegates:

```json
{
  "status": "PENDING_MANDATORY_CODEX_REVIEW",
  "delegation_id": "deleg_current",
  "bundle_path": "tasks/<slug>/reviews/plan-doc-review-bundle.md",
  "completed_review_artifacts": ["claude-plan-doc-review-canonical.json"],
  "stale_delegate_results_adjudicated": ["codex-...-superseded-failed-adjudicated.json"],
  "why_pending": "No parseable current-bundle verdict has re-entered or been recovered.",
  "resume_steps": [
    "Wait for deleg_current to re-enter and save it if it reviewed the current bundle.",
    "If blockers still apply, patch docs, regenerate bundle, and rerun both lanes.",
    "If it passes and docs did not change, create aggregate plan-review.json."
  ]
}
```

## Pitfalls

- Do not treat a cached summary file's existence as proof it reviewed the latest bundle; compare mtime and quoted content.
- Do not rerun or patch when the live spec already contains the requested safety contract; save an adjudication artifact instead.
- Do not let stale failures erase a current companion approval, but also do not aggregate final approval until the current mandatory delegate returns or is explicitly replaced/waived.
- When a tmux Claude review pane disappears before capture and transcript recovery fails, rerun Claude against the unchanged current bundle rather than counting the lost pane.
