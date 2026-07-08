# Plan-code Stripe Connect/manual gate guidance

Use when a Buffdemy `plan-code` task reaches the final human/browser Stripe gates after automated payment E2E has passed, especially when the user asks for one instruction at a time.

## One-instruction-at-a-time manual gate flow

When the user asks to be guided through Stripe/manual gates, keep each response to one concrete check or browser action. Do not dump the full remaining checklist unless asked. After each user confirmation, record the gate mentally/session-locally and move to the next smallest check.

Recommended sequence after automated real-card E2E is green:

1. Confirm Stripe Dashboard is in **Test mode**.
2. Confirm Connect Express availability through current Dashboard labels:
   - Stripe may not expose a separate toggle named “Stripe Connect Express”.
   - The current Dashboard surface may be `Settings -> Connect -> Express Dashboard` with `Branding` and `Features` tabs plus the description “Customize the Express Dashboard for your connected accounts.”
   - Treat that view as Express Dashboard readiness. Do not ask the user to find a non-existent “enable Express” switch.
3. Confirm webhook endpoint registration in Test mode:
   - target endpoint such as `https://dev-api-grace.buffdemy.com/webhook/stripe`;
   - `account.updated` included on the main endpoint or clearly registered on a separate Connect endpoint.
4. Confirm creator earnings / Connect onboarding browser path:
   - open the frontend earnings page (for Buffdemy2-web this may be `/settings/earnings`);
   - clicking `Set up Stripe Connect` should redirect to a Stripe-hosted URL such as `connect.stripe.com/setup/...`;
   - if the user completes test onboarding, verify the connected account is complete/enabled in Dashboard.
5. Confirm connected-account payment/payout capability:
   - “payment active” and “payout active” are sufficient for the practical test setup gate;
   - other unfinished test accounts with restricted status are not blockers if the tested account is complete/enabled.
6. Confirm answer-tip real-card browser flow:
   - user buffs/tips an answer with a Stripe test card and observes success;
   - if tool access is available, optionally verify `creatorEarning` has `source: answerTip`, `status: available`, and expected gross/fee/net amounts using live container env rather than `.env` files.
7. Confirm broader question-pledge manual browser QA:
   - initial pledge/Buff succeeds;
   - third-party pledge/Buff succeeds;
   - if the user wants reward distribution proof, identify the exact question URL tied to those pledge records before checking settlement state.

## Reward / settlement distinction

Answer-tip rewards and question-pledge settlement are different paths:

- Answer-tip success can immediately create a `creatorEarning` with `source: answerTip` for the answer owner.
- Question-pledge rewards are distributed by the cronWorker `settleQuestionPayouts` path after a question settlement opens, not by a generic browser “reward” button.
- A question that shows `creatorEarnings.source = answerTip` but has no `questionpledges` and no `questionsettlements` is evidence that answer tipping worked, not that pledge settlement ran.
- If testing question-pledge reward distribution, first ask for the URL of the question where initial and third-party pledges were made; do not infer it from an answer-tip URL.

## Pitfalls

- Do not request or store Stripe secrets or single-use onboarding URLs. If the user pastes a `connect.stripe.com/setup/...` URL, acknowledge it only as Stripe-hosted onboarding evidence and avoid persisting it in task docs.
- Do not overclaim manual gates from automated Playwright evidence. Automated accepted/declined real-card question pledge E2E can be green while dashboard/connect/browser gates still need user confirmation or waiver.
- Do not treat restricted status on unrelated/unfinished test connected accounts as a blocker when the test creator account used for QA is complete/enabled and has payment/payout active.
- After updating task docs with manual-gate confirmations, rerun the final artifact-consistency review because those doc edits stale the prior consistency verdict.
