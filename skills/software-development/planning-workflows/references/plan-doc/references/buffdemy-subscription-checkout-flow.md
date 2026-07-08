# Buffdemy Subscription Checkout Flow Planning Notes

Use when planning Buffdemy frontend work for creator/profile subscription checkout, Stripe Checkout redirects, or subscription return pages.

## Backend contract invariants

- New paid subscription creation uses `POST /subscription/checkout-session` only.
- Checkout-session request body is exactly `{ targetUserId, tierId }`; do not plan frontend-sent amount, currency, tax, provider, Stripe customer, or Stripe price fields.
- Old direct `POST /subscription` / `Subscription.subscribe` must not remain in production new-subscribe UI paths. It may exist only as an intentionally unused/deprecated model method or for unrelated non-checkout flows.
- Treat `checkoutSession.stripeSessionUrl` as optional in backend response schemas. The UI/handoff helper should detect absence and show a retryable error before redirect; the proxy/schema should not reject an otherwise backend-valid response just because the URL is missing.
- A Stripe success return is not proof of a local active subscription. Plan pending confirmation UI plus bounded refetch/polling until local subscription state confirms activation.

## Matching and pending context

- Match active subscriptions by normalized relation ids, not raw equality. Existing subscription relations may be populated objects; use the project’s relation-id helper/pattern such as `getRelationId(subscription.target) === targetUserId`.
- Pending checkout context is best-effort and non-authoritative. Include at least `viewerUserId` when available, `targetUserId`, `targetUserName`, `tierId`, `tierDisplayName`, `sourcePath`, and `startedAt`.
- Treat stale pending context, missing context, or `viewerUserId` mismatch after account switching as non-authoritative; show safe generic pending/cancel copy instead of creator/tier-specific claims.

## UI, modal, and guard planning

- Establish the shared checkout modal/handoff/error/guard contract serially before parallelizing profile CTA, public subscription page migration, or return-page work. These features share modal props, helper signatures, error mapping, i18n keys, and selectors.
- If later phases are parallelized, assign explicit file ownership. Do not let multiple workers edit shared checkout helpers, modal/dialog primitives, or i18n keys without a designated owner and reconciliation step.
- Critical checkout-session creation/Stripe handoff state should guard: close button, background click, Escape, secondary actions, `beforeunload`, in-app anchor/form navigation, browser back/forward (`popstate`), and any project router navigation helper that is in play. Bypass guards only for the intended `window.location.assign(stripeSessionUrl)` redirect.
- For stepped modals, the title-as-back-control must be a real accessible button with localized labels; icon-only controls need aria labels; loading/error states should be keyboard-readable.
- Use shared backend checkout error mapping in every entry point. Include already-subscribed, self-subscribe, invalid/missing user, stale tier, tier-not-owned, missing Stripe price, checkout check/create failures, Stripe customer/session failures, and missing checkout URL.

## Return pages and billing boundaries

- Success page: show pending confirmation immediately, poll/refetch with bounded attempts, confirm active state only after normalized active-subscription match, and fall back to manual refresh/navigation if still pending.
- Cancel page: never mark subscribed or mutate subscription state; offer return/retry using non-stale pending context.
- Billing-history display is out of scope unless existing billing UI is touched. If touched, use top-level billing amount fields from backend responses rather than deriving Stripe totals client-side.

## Verification checklist to include in plans

- Schema/proxy tests cover exact request body, unknown-key rejection, backend errors, and optional missing `stripeSessionUrl` behavior.
- Component tests cover profile CTA visibility, modal steps, accessibility, stale async guards, checkout payload, missing URL, and navigation/close guard cleanup.
- Return-page tests cover pending state, normalized active-subscription matching, polling fallback, missing/stale context, viewer mismatch, cancel no-mutation behavior, and retry/return actions.
- E2E/helper updates intercept `/api/subscription/checkout-session`, assert payload shape, and prevent real Stripe navigation while asserting intended redirect.
- Final static audit searches for production new-subscribe UI paths still using old direct subscribe APIs, allowing only intentionally unused/deprecated definitions or unrelated non-checkout change/cancel flows.
