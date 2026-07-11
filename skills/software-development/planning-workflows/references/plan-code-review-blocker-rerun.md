# Plan-code review blocker rerun pattern

Use when a mandatory `plan-code` implementation review leg fails after another leg has already approved, especially for frontend tasks where a reviewer finds a concrete fail-closed or data-integrity gap.

## Pattern

1. Save the failing reviewer verdict as a durable artifact marked initial/superseded; do not overwrite it with the later fix.
2. Treat any companion approval from before the fix as stale. Rename or mark it stale so it is not counted in the aggregate final review.
3. Fix the smallest concrete blocker and add focused regression tests for the exact missed cases.
4. Rerun impacted verification after the fix.
5. Run the simplify gate again after the fix; small cleanup like replacing a type assertion with a type guard is appropriate when it reduces review risk.
6. Regenerate the final implementation bundle from current source/tests/task docs.
7. Rerun every mandatory final review leg against the regenerated bundle.
8. Only after all fresh review legs pass, write the aggregate `final-review.json` and reconcile live `todo.md` / `final-report.md`.

## Common reviewer-found frontend gaps

### In-flight mutation lifecycle guards

For modal/dialog flows that submit a create/payment/reaction request, duplicate-submit guards must survive the whole async lifecycle, not just same-tick double clicks:

- do not let dialog close/open/reset handlers clear an in-flight ref or `isSubmitting` state while the request is pending;
- either ignore close/open transitions while submitting or move the in-flight guard outside modal reset state and clear it only in the request's settle path;
- disable secondary navigation controls such as Back while submitting if they would expose stale state or alternate execution paths;
- preserve the intended success-close path by clearing the guard only after the request settles, then closing the dialog;
- add a focused regression for `execute -> pending -> attempt close/reopen/back -> execute again`, asserting only one create call and that success still closes after resolution;
- if a reviewer finds this after another review leg passed, save the failed verdict, mark the companion approval stale, fix narrowly, rerun verification, regenerate the bundle, and rerun both review legs.

### Partial hydration fail-closed behavior

For UI that hydrates stored IDs into public linked entities, fail closed on partial resolution:

- clear stale rendered entities when a new request starts;
- require every requested ID to resolve to a public entity with the fields needed for display/linking;
- if any item is missing, malformed, or the request rejects, hide the entire row/list instead of rendering a partial set or raw IDs;
- add tests for partial unresolved, request failure, deleted/hidden parents, and stale prop-change clearing.

## Async/deferred review verdicts

Mandatory review legs can return after the parent agent has already saved a pending artifact or even after context compaction. When a late verdict arrives:

1. Save the returned verdict as its own durable artifact first; do not discard it because a pending artifact already exists.
2. If it fails, mark any prior pending artifact as superseded by the returned failure, fix the blocker, rerun impacted verification, regenerate the bundle, and rerun all mandatory review legs.
3. If a fresh rerun does not produce a verdict within a bounded wait, save a new pending artifact with the exact reviewer session, latest raw capture, bundle identity, and resume steps; do not create the aggregate final review.
4. If a rerun remains unrecoverable after context compaction, start a replacement interactive lane against the unchanged current bundle and update task docs/artifacts with the replacement session so the next session can recover. For Codex, keep the bare interactive TUI/tmux contract; never substitute a delegated reviewer.
5. Only create `final-review.json` after a current passing verdict/waiver exists for every mandatory leg; stale approvals from before source/test/task-doc changes do not count.
6. If a replacement review was started because an earlier rerun was missing, but the earlier rerun later returns passing after the aggregate gate is already complete, save the replacement's eventual result as supplemental/historical evidence. Do not reopen a completed gate or start another review loop unless the late replacement reports a blocker or new current-risk finding. Update the replacement pending placeholder, aggregate review JSON (for example `supplemental_reviews`), notes/final report, and run lightweight JSON/marker validation only.

## Pitfalls

- Do not leave a stale final report or TODO saying the old review is pending/approved after a reviewer-driven fix. Review bundles often embed task docs, and Claude/Codex reviewers can correctly flag stale task prose even when source code is fixed.
- Do not use a mocked UI component regression as the only confidence signal when the reviewer-found bug was about the real component's lifecycle/visibility semantics. Either include a real-component unit/E2E assertion or have a read-only reviewer inspect the real wrapper semantics and record why the mock matches production.
- A late supplemental passing replacement review is not a reason to touch source or rerun implementation verification. Treat it as artifact bookkeeping unless it contradicts the active final review.
