# Plan-code manual Stripe gate finalization

Use when a Buffdemy backend/frontend `plan-code` task is blocked only on manual Stripe/browser gates after automated real-card and deterministic E2E are already green.

## Pattern

1. Guide the user one gate at a time. Avoid a wall of questions. Record each confirmed gate as evidence only after the user confirms it or the agent verifies it from live state.
2. Interpret Stripe Connect Express correctly:
   - There may be no standalone "Enable Stripe Connect Express" toggle.
   - Current dashboard evidence can be `Settings → Connect → Express Dashboard` with copy such as `Customize the Express Dashboard for your connected accounts`.
   - Treat this as Express Dashboard/readiness evidence, not as a requirement to find a nonexistent separate switch.
3. For webhook scope, ask the user to confirm the Dashboard endpoint for the public API URL includes `account.updated`. Do not ask them to paste signing secrets.
4. For Connect onboarding, use the app's creator earnings page and verify that clicking setup redirects to a Stripe-hosted `connect.stripe.com` onboarding URL. Do not preserve one-time onboarding URLs in durable docs.
5. For connected-account readiness, have the user check the completed test connected account status in Dashboard. `payment active` and `payout active` are sufficient practical readiness evidence for the test setup; incomplete/restricted accounts for other test users are expected and non-blocking.
6. For answer-tip reward proof, after the user confirms a real-card browser tip succeeded, verify live DB state from running containers only (no `.env` reads): an available `creatorEarning` with `source: answerTip`, gross/fee/net amounts, and target answer reference proves the reward path.
7. For question-pledge reward distribution, distinguish secured pledges from settlement:
   - A live question can show `pledges.status: secured` and no `questionsettlement` until the question closes/expires/all requested answerers answer.
   - If the user explicitly approves a test-only force close, use the existing repository close/expiry path, not ad-hoc document mutation, then run the existing `settleQuestionPayouts` job.
   - Verify post-state: question closed, pledges charged, settlement settled, charged pool equals pledge total, and available `questionReward` creator earnings exist.
8. Save a concise manual-gate confirmation artifact under the task review dir. Include evidence summaries, not secrets or one-time Stripe URLs.
9. Any manual-gate doc update stales the current final artifact-consistency verdict. Mark older passing consistency verdicts as superseded, regenerate a current-only bundle, create a self-excluded pending marker, rerun the final consistency review, then canonicalize only after it passes.

## Pitfalls

- Do not overclaim Phase completion before the post-doc-update final consistency review passes. Use wording like "functional/manual gates complete; final artifact consistency pending".
- Do not treat `deleg_e60d5589`-style pre-async or pre-manual-gate review approvals as current final approval after new evidence artifacts are written.
- Do not preserve raw Stripe secrets, raw signatures, raw webhook payloads, or one-time onboarding links in task docs.
- Do not ask the user to finish Stripe-hosted onboarding details unless the gate needs full onboarding; reaching hosted onboarding proves redirect wiring, while completed test onboarding proves readiness.
