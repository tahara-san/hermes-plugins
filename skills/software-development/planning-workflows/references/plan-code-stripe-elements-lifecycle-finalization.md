# Plan-code Stripe Elements lifecycle and finalization reruns

Use this when a frontend payment phase uses Stripe Elements/PaymentElement inside reusable dialogs or editor wizards and mandatory reviewers keep finding stale async lifecycle blockers near final review.

## Lifecycle blocker pattern

A payment flow can pass ordinary duplicate-submit tests and still be wrong if an old target's async work can continue after the component is reused for a new target. The most dangerous windows are:

1. **Create-session response returns late**: old `PaymentIntent`/`SetupIntent` response attaches to a reused component, especially when the new target selected the same amount.
2. **Stripe confirmation resolves late**: old `confirmPayment`/`confirmSetup` resolves after target reuse and then starts polling the old internal record.
3. **Post-confirmation poll resolves late**: old `GET /buff-tip/:id` or `/question-pledge/:id` succeeds after target reuse and applies optimistic totals to the new target.

Fix with a single lifecycle token/sequence model rather than ad-hoc state comparisons:

- Increment a lifecycle sequence on every modal open/reset/close and on target identity changes.
- Store the lifecycle sequence (and amount/target identity as useful debug context) on the created payment/session object.
- Pass that session-bound sequence through the child PaymentElement form callback; do not read the current sequence only after Stripe confirmation resolves.
- Check the sequence before Stripe confirmation, after Stripe confirmation, before entering the processing step, before starting poll, before showing errors, and before applying success/optimistic totals.
- Render payment/review amounts from the immutable session object, not mutable input state.

## RED/GREEN tests reviewers respond to

Add focused regressions that hold each async boundary unresolved, then rerender/reuse the component for a different target:

- create-session promise unresolved -> target reuse with same selected amount -> resolve old session -> no old clientSecret/session attaches to new target;
- Stripe confirmation promise unresolved -> target reuse -> resolve old confirmation -> no old poll starts and new target totals remain unchanged;
- poll promise unresolved after confirmation -> target reuse -> resolve old poll success -> new target totals remain unchanged.

These tests are more persuasive than broad snapshots because they prove the exact stale continuation cannot mutate current UI state.

## Review rerun and final artifact sequence

- Any source/test/i18n change after one review lane passes makes every implementation review lane stale; save the old verdict as superseded, rerun impacted verification, regenerate the final bundle, then rerun both lanes.
- If one lane passes while the interactive Codex TUI is pending, save a pending artifact with its tmux session, raw pane capture, and bundle identity, then stop fail-closed until a parseable attested verdict exists.
- When the interactive Codex verdict is complete, save it as the current verdict, mark the pending artifact `COMPLETED_SUPERSEDED_BY_VERDICT`, then write the aggregate final review.
- Task-doc/TODO updates after implementation review should be followed by a narrow artifact-consistency check that excludes the consistency artifact itself; do not regenerate the implementation bundle after the raw reviewer approvals unless both review lanes rerun.

## Non-blocking suggestions policy

For final payment UX reviews, record non-blocking hardening/UX suggestions without optional churn when they do not affect correctness/security/acceptance criteria. Examples: visible missing publishable-key configuration message, terminal poll-timeout copy, specific terminal failure-code messages, aborting ignored poll traffic, or cleanup of unused legacy i18n keys. Implementing these after final approval would stale the bundle and should be deferred unless the user asks.
