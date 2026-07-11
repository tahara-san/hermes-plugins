# Plan-doc stale review cache adjudication

Use when a review result appears after one or more plan-doc bundle regenerations, or when cached historical review evidence is discovered out of order.

## Trigger

- A historical delegated review or older interactive review returns after newer plan-doc edits.
- Cache/log recovery finds a review summary, but its reviewed bundle identity is unclear.
- The reviewer quotes wording no longer present in the live spec/bundle.
- One current interactive lane has approved while stale failures continue surfacing.

## Procedure

1. **Do not count the verdict immediately.** A result is not current approval/failure until tied to the finalized bundle path/hash.
2. **Compare chronology and content.** Check current bundle identity, saved pending artifacts, reviewer session identity, and whether quoted text still exists.
3. **Adjudicate against live docs/source.** Save already-resolved findings as `SUPERSEDED_FAILED_ADJUDICATED` with a short current-doc excerpt; do not patch or rerun solely to satisfy stale wording.
4. **Patch only valid current risks.** If a stale review exposes a blocker that still applies, patch narrowly, mark every pre-patch review stale, regenerate the immutable bundle, and launch both required interactive lanes before waiting on either.
5. **Keep the current mandatory Codex leg explicit.** If the current interactive Codex TUI has no parseable attested verdict, save a pending artifact naming its tmux session, latest raw pane capture, current bundle path/hash, companion artifacts, stale adjudications, and exact resume steps. Do not create `plan-review.json` yet.
6. **Avoid optional-churn loops.** Record non-blocking polish unless it is a concrete implementation footgun worth staling and rerunning the full review pair.

## Artifact pattern

For stale historical reviews:

```json
{
  "reviewer": "historical delegated reviewer",
  "review_session": "legacy-session-or-delegation-id",
  "status": "SUPERSEDED_FAILED_ADJUDICATED",
  "reviewed_bundle": "older/pre-patch bundle",
  "current_bundle": "tasks/<slug>/reviews/plan-doc-review-bundle.md",
  "raw_output_path": "/home/.../historical-review.txt",
  "verdict_from_stale_review": { "passed": false },
  "adjudication": {
    "blocking_finding_applies_to_current_docs": false,
    "reason": "Current spec already pins the safe ordering/error semantics.",
    "current_spec_excerpt": "line-numbered excerpt"
  }
}
```

For the current interactive Codex lane:

```json
{
  "status": "PENDING_MANDATORY_CODEX_REVIEW",
  "tmux_session": "plan-doc-codex-<slug>-vN",
  "raw_pane_capture": "reviews/codex-plan-doc-vN.raw.txt",
  "bundle_path": "tasks/<slug>/reviews/plan-doc-review-bundle.md",
  "bundle_sha256": "<sha256>",
  "completed_review_artifacts": ["claude-plan-doc-review-canonical.json"],
  "stale_results_adjudicated": ["review-...-superseded-failed-adjudicated.json"],
  "why_pending": "No parseable current-bundle attested verdict is saved.",
  "resume_steps": [
    "Recover and capture the managed tmux pane.",
    "If no parseable verdict exists, rerun bare codex against the same current bundle.",
    "If docs change, regenerate the bundle and rerun both independent lanes."
  ]
}
```

## Pitfalls

- A cached summary is not proof of the latest bundle; compare bundle identity and quoted content.
- Do not let stale failures erase a current companion approval, but do not aggregate final approval until the current interactive Codex verdict exists or is explicitly waived.
- A lost tmux pane is not approval; rerun the unchanged lane if the raw evidence and normalized verdict cannot be recovered.
- Never substitute a Hermes `delegate_task` reviewer, `codex exec`, or `codex review` for the mandatory interactive Codex lane.
