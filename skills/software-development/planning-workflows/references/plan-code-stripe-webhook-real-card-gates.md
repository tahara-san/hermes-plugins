# Plan-code Stripe webhook / real-card E2E gates

Use when a Buffdemy plan-code task reaches Stripe Elements real-card browser/E2E paths and the remaining blocker is webhook/poll completion rather than deterministic frontend/auth/base-URL coverage.

## Pattern

1. Do not read real `.env` / `.env.*` files when the user forbids it. Verify readiness from live process/container environments instead:
   - API container process env for `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, optional `STRIPE_CONNECT_WEBHOOK_SECRET`, public webhook URL, Linker host/protocol, test-only injection flags.
   - cronWorker process env for matching `STRIPE_SECRET_KEY`, API version, currency, payout/fee flags.
   - compare API/cron secrets by redacted shape and/or hashes, not by printing secret values unless the user explicitly shares/permits a sandbox secret.
2. Verify reachability without secrets:
   - frontend host routes (`/`, fixture profile routes) should return 200 from the agent environment;
   - `POST /webhook/stripe` with no Stripe signature should reject with a signature-missing error. This proves route reachability, not webhook correctness.
3. Run real-card Playwright with explicit gates and save logs under the task review directory:
   - accepted-card full spec (`STRIPE_PAYMENT_E2E_READY=1 ... questionEcoCycle.spec.ts --project=chromium-auth --no-deps`);
   - if the accepted-card case fails before the declined-card case runs, run the declined-card test in isolation with `--grep 'declined card'` so that controlled failure handling can be classified independently.
4. If accepted-card reaches Stripe confirmation/app processing but times out waiting for UI success, inspect API logs around the run before calling it a generic webhook/poll blocker.
   - `stripe_webhook_signature_invalid` means webhook delivery reached the API but the signing secret used to verify the request does not match the endpoint/listener that sent it.
   - If the running API env already equals the Dashboard secret the user provided, do not keep saying the container has the wrong env. The likely issue is a different Stripe endpoint/listener/mode/account sending the event, multiple dashboard endpoints pointing at the same URL, or a Connect endpoint using a separate secret.
5. Update task docs with the concrete classification:
   - deterministic host-base E2E green vs real-card partial;
   - accepted-card reached confirmation but failed webhook/poll success;
   - declined-card passed or remains open;
   - exact backend log error such as `stripe_webhook_signature_invalid`;
   - remaining manual/browser/Connect/cross-border gates.
6. Because task docs/review artifacts changed after the prior verdict, regenerate a narrow active-scope artifact-consistency bundle and rerun the read-only consistency review. Exclude the canonical consistency artifact from its own judged scope.

## Post-renewal diagnostics and evidence hygiene

When the user renews/recreates a Stripe webhook secret and asks for validation diagnostics:

1. Add route-boundary logging that is useful but secret-safe:
   - payload length and parsed event metadata (`eventId`, `eventType`, `livemode`, object type/id);
   - `Stripe-Signature` header length, timestamp presence/age, `v1` count, schemes present;
   - main/connect webhook secret presence, length, and prefix classification only;
   - sanitized Stripe SDK/AppError cause on rejection;
   - accepted secret source (`main` / `connect`) on success.
2. Rebuild/recreate the affected API service before rerunning real-card E2E, then prove route reachability with a safe unsigned POST that returns `stripe_webhook_signature_missing`.
3. Save both the focused Playwright log and an API log excerpt from the exact UTC window. The API excerpt should show the sanitized diagnostics plus the success/failure line, not raw secrets, raw signatures, or raw payloads.
4. Use unique log filenames for reruns. If an earlier filename was reused or overwritten, create a new canonical filename for the current result and patch active task docs so historical failure evidence is either embedded in a markdown artifact or clearly marked non-canonical.
5. After adding diagnostics/log artifacts or changing task docs, regenerate an active-scope artifact-consistency bundle that excludes historical bundles as live-status evidence, run whitespace/truncation/cache-placeholder checks on the bundle, and rerun the consistency review before claiming the plan-code gate is complete.

## Pitfalls

- Do not infer that a present `whsec_...` value is correct merely because the variable exists; correctness depends on the exact Stripe endpoint/listener that sent the event.
- Do not overclaim a GET/HEAD 404 on `/webhook/stripe` as failure; the webhook route may be POST-only. A safe unsigned POST should fail with a signature error.
- Do not mark the whole real-card gate failed if the accepted-card case aborts the suite before declined-card runs; run declined-card in isolation when practical and document the separate result.
- If a transient Playwright preflight timeout occurs but curl/profile routes are reachable immediately afterward, warm the routes and retry once before classifying the run as a base-URL/auth blocker.
- Do not let a historical review bundle's stale snapshots override active docs. Final artifact-consistency reviews for this class should judge live task docs/current verdict artifacts and treat older bundles as reference-only unless the user explicitly asks to audit history.
