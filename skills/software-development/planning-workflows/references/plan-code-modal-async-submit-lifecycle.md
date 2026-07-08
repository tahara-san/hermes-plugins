# Plan-code async-submit lifecycle blocker

Use when a `plan-code` task implements a modal/dialog, wizard, or editor confirmation flow that executes an external confirmation step and/or backend mutation, and reviewers are checking duplicate-submit behavior.

## Failure patterns

### Dialog close/reopen resets the guard

A component can pass same-button duplicate-click tests but still be vulnerable if closing the modal while the mutation is pending runs a reset helper that clears `isSubmitting` or an in-flight ref. The user can then reopen and submit again before the first request settles. A late success can also close/reset the newly reopened modal unexpectedly.

### External confirmation happens before the saving flag

A wizard/editor flow can also be vulnerable even without a modal close path when it awaits an external confirmation before setting the local saving/submitting state. Example: a publish button that calls Stripe `confirmSetup()` and only then sets `isSaving` before `POST /api/question`. React state cannot disable the button until after the first await starts, so rapid repeated clicks can run multiple confirmations and duplicate the publish request. Guard synchronously before the first await.

### Async intent/session preparation uses stale editable input

Payment and pledge flows often prepare a server/Stripe session before Elements mounts (`PaymentIntent`, `SetupIntent`, internal pledge/tip record). If the UI keeps amount controls editable while that preparation request is in flight, the user can change the visible amount after request dispatch but before the response arrives. The late response can then mount a payment element or publish payload for the old amount while the screen shows a new amount. This is a data-integrity/payment-review blocker even when duplicate-submit guards are present.

Fix pattern:
- Capture the prepared amount in a local variable before the await.
- Set a synchronous in-flight ref before dispatching the create/prepare request; ignore duplicate prepare attempts while true.
- Disable or synchronously ignore amount controls while preparation is pending.
- Keep a ref of the currently parsed/selected amount and, after the await, drop the response if it no longer matches the prepared amount.
- Render the payment/review amount from the created session (`paymentSession.amount` / `initialBuffSession.amount`), not from live input state.
- If amount edits are allowed after preparation completes, clear the existing session and confirmation callback so the user must re-prepare.

RED regression pattern: hold the create/prepare promise unresolved, select/enter an amount, click Prepare/Continue, assert all amount controls and the prepare/continue button are disabled, resolve the promise, and assert the mounted Elements provider/session amount matches the original prepared amount. If the preferred product choice is to allow edits while pending, the RED test should instead prove the stale response is dropped and no Elements/session is mounted for the old amount.

## Required review/fix checklist

- Trace all submit paths, not just the final backend request: Stripe/SDK confirmations, setup-intent/payment-intent confirmation, polling, and the save/publish POST.
- For dialogs, trace all close paths (`onOpenChange`, close button, Escape/overlay if applicable), not just the Execute button.
- Keep a synchronous in-flight ref alive until the whole operation settles; do not rely only on React state when the first awaited operation happens before the visible saving flag is set.
- Trace all dialog close paths (`onOpenChange`, close button, Escape/overlay if applicable), not just the Execute button.
- Trace prop/target reuse while an async create/prepare call is pending. If the same component instance can be reused for another target, stale responses must be invalidated by a request sequence/target token, not only by comparing the selected amount/value; the new target may select the same value.
- Trace prop/target reuse while an async post-confirmation poll is pending. A captured old payment/session object can still complete after modal close/reopen/reset or row/target reuse; before applying optimistic success, showing errors, or changing steps, re-check a lifecycle sequence/target token captured before the poll. Add a RED regression that holds the poll promise unresolved, rerenders to a different target, resolves the old poll as success, and asserts the new target's displayed count/weight remain unchanged.
- Trace prop/target reuse while the external Stripe confirmation itself is pending, before polling begins. If the post-confirm callback reads the current lifecycle only after `confirmPayment` / `confirmSetup` resolves, a stale callback can adopt the new target's sequence and start polling the old session. Store the lifecycle/target token on the payment/session object before confirmation, pass that token through the confirmation callback, check it before and after Stripe confirmation, and check it again before setting processing, polling, showing errors, or applying optimistic success. Add a RED regression that holds Stripe confirmation unresolved, rerenders to another target, resolves the old confirmation, and asserts no old-session poll starts and new-target totals stay unchanged.
- Keep any synchronous in-flight/lifecycle ref alive until the mutation settles; do not clear it from a generic modal reset while pending unless stale responses/finally blocks, stale confirmation continuations, and stale poll completions are all invalidated and cannot clear or mutate a newer lifecycle.
- Prefer ignoring open/close attempts while submitting, or prove close/open cannot reset the guard or allow stale completions to mutate a reused component.
- Disable Back/Execute controls while submitting.
- On success, clear the in-flight guard only after the request settles, then close/reset/navigate.
- On failure, show the mapped error and clear the guard to allow a deliberate retry; if an external confirmation already succeeded but the POST failed, consider clearing the session or skipping re-confirmation on retry.
- Add a focused regression for the exact primitive:
  - Modal: pending mutation -> attempt close -> dialog remains open or guard remains active -> second execute does not create a second request -> resolve promise -> success close still works.
  - Wizard/editor: make external confirmation promise unresolved -> click Publish twice -> confirmation and POST are each called at most once -> resolve confirmation -> save continues once.

## Plan-code sequencing note

If a reviewer finds this after another reviewer has approved, save the failed verdict, mark earlier approvals stale, patch narrowly with RED/GREEN, rerun focused and proportional verification, regenerate the implementation bundle, and rerun every mandatory review leg before creating `final-review.json`.
