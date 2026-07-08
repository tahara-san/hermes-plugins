# Plan-code Stripe PaymentIntent outcome review reruns

Use when a Buffdemy backend `plan-code` phase involving Stripe PaymentIntents, pledge charges, webhooks, settlement, or payout cron passes focused tests but independent review finds money-state/data-integrity gaps.

## Trigger signals

- Reviewer flags that code records `charged`/billing state from a PaymentIntent without checking `status`.
- Fresh `create*PaymentIntent` return path and stale/webhook reconciliation path classify PaymentIntent outcomes differently.
- Terminal Stripe failures without a determinate `last_payment_error.code` can leave rows stuck in an in-flight state.
- Retry/reconciliation code must avoid duplicate Stripe actions while still progressing terminal rows.

## Pattern

1. Save the failed reviewer verdict as a superseded/fixed artifact before editing, including delegation id, bundle path, findings, and intended verification.
2. Add RED regressions for every distinct outcome path before patching production code:
   - fresh-created `processing`/`requires_action`/other nonterminal PI stays in in-flight state, does not bill, and does not consume attempts unless the product contract says otherwise;
   - fresh-created terminal failed PI records a failed attempt with `paymentIntentId`;
   - stale/retrieved/searched terminal failed PI with missing decline code progresses with a safe fallback code rather than waiting forever;
   - succeeded PI is the only path that creates paid billing/settlement state.
3. Verify RED fails for product reasons (old code bills/distributes too early, omits PI id, or leaves row stuck), not setup noise.
4. Patch with one shared outcome classifier used by fresh create, stale reconciliation, and webhook-equivalent logic where possible:
   - `succeeded` -> full success write set;
   - terminal failed statuses -> failed-attempt write set with PI id and fallback error code if needed;
   - nonterminal/in-flight statuses -> no billing, no duplicate charge, wait for webhook or stale reconciliation.
5. Rerun focused suite, impacted combined suite, build/typecheck, scoped scan (`console`, `any`, TODO/FIXME, `originalError`), and `git diff --check`.
6. Rerun `/simplify` after the source/test fix. Keep payment-state tests explicit even if fixture factories could reduce lines; readability can be more important than abstraction for money invariants.
7. Regenerate the final review bundle from the current tree, supersede older pending review artifacts, and rerun every mandatory review lane. Do not count any approval that predates the post-review source/test/doc changes.

## Notes

- Treat reviewer-found money-state issues as data-integrity blockers, not optional hardening.
- Do not ask the user before fixing valid reviewer blockers unless the fix requires a product decision, destructive action, or scope change.
- If the companion Claude Code Opus 4.8 @ xhigh effort lane is blocked by login/limits, save current-bundle blocked artifacts and leave the phase incomplete; do not let the blocked lane stop the RED/GREEN fix for a valid Codex finding.
