# Plan-code secret-safe Stripe/manual readiness checks

Use this when a `plan-code` task is blocked on Stripe/manual/browser gates and the user asks you to verify setup without reading `.env` / `.env.*` files.

## Pattern

1. Treat the user's no-`.env` constraint literally: do not read real `.env`, `.env.local`, `.env.*`, or deployment secret files. `.env_sample` / `.env_template` remain allowed only if the user already allowed sample/template docs.
2. Inspect **running process/container environments** instead, and redact values by shape:
   - Stripe secret key: report `sk_test`, `sk_live`, missing, or unexpected prefix.
   - Publishable key: report `pk_test`, `pk_live`, missing, or unexpected prefix.
   - Webhook secret: report `whsec`, missing, or unexpected prefix.
   - Test-only injection secret: report present + length only.
   - Non-secret config such as currency, API version, paths, public URLs, booleans, fee rates can be reported directly.
3. Compare shared backend/worker secrets by short hash/equality, not value. For example, API and cronWorker `STRIPE_SECRET_KEY`, `STRIPE_API_VERSION`, `STRIPE_DEFAULT_CURRENCY`, `PAYMENT_PLATFORM_FEE_RATE`, and `PAYOUT_TRANSFERS_ENABLED` should match where expected.
4. Verify service reachability separately from env readiness:
   - Compose services running/healthy.
   - Frontend host-base URL returns HTTP 200.
   - Public webhook route is reachable. A safe unsigned `POST /webhook/stripe` should return a signature-missing/rejected response; that proves route reachability and signature enforcement, not Dashboard delivery.
5. Do not overclaim what cannot be observed:
   - If the actual Next dev server process is not visible from WSL/proc inspection, say the frontend `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` could not be verified even if the host URL is reachable.
   - If `stripe-listener` is not running, classify it as OK only when the Dashboard/public endpoint is the intended delivery path.
   - Missing `STRIPE_CONNECT_WEBHOOK_SECRET` is OK only if `account.updated` is registered on the same main endpoint and the backend intentionally falls back to `STRIPE_WEBHOOK_SECRET`.
   - Stripe Connect Express might not appear as a standalone “enable Express” Dashboard toggle. Current Dashboard evidence such as `Settings → Connect → Express Dashboard` with Branding/Features tabs and “Customize the Express Dashboard for your connected accounts” is enough to classify Express Dashboard as available/configurable; then verify the app’s creator earnings flow redirects to a Stripe-hosted `connect.stripe.com` onboarding URL.
6. Before running real-card gates, ask for the smallest necessary confirmation, not secrets:
   - frontend `pk_test` is loaded in the server currently serving the target host;
   - Dashboard webhook points to the public API endpoint;
   - Dashboard webhook signing secret matches the API process env;
   - `account.updated` delivery path is known (main endpoint vs separate Connect endpoint);
   - Express Dashboard readiness is visible under Connect settings, or the app’s creator earnings flow reaches Stripe-hosted Express onboarding.

## Reporting shape

Keep the result as a pass/blocker matrix:

- Backend/API env: ready / missing / uncertain.
- cronWorker env: ready / mismatch / uncertain.
- Webhook route reachability: reachable + unsigned rejection code, or blocker.
- Frontend host reachability: reachable / blocker.
- Frontend publishable-key readiness: verified / not observable / blocker.
- Stripe listener/Dashboard delivery: running / not running but Dashboard expected / unknown.

Never paste or request real secret values in chat.
