# Buffdemy Subscription/Billing Views Plan Notes

Use this reference when planning frontend views for backend subscription and billing features in Buffdemy.

## Backend contract shape recovered during planning

The relevant backend contract may be supplied as an out-of-workspace document (for example `/home/tahara/user-subscription.md`) even when the chat context warns that a relative `@file` path is outside the allowed workspace. For `/plan-doc`, first try to recover the intended absolute/sibling file before asking the user to paste it.

Core domain objects planned around:

- `MoneyAmount`
- `SubscriptionTier`
- `Subscription`
- `BillingRecord`
- compact relation payloads such as `UserTinyData`

Frontend proxy/API areas:

- `/subscription-tier`
- `/subscription`
- `/billing-record`

Primary view routes chosen in the session:

- Public creator tiers: `/@username/subs`
- Creator tier/subscriber management: `/creator/subs`
- Subscriber settings / outgoing subscriptions: `/settings/subs`
- Billing history: `/settings/billing`

## Planning decisions that were useful

- Full v1 scope can include models, API proxies, public profile views, creator management, subscriber settings, billing history, navigation, i18n, tests, and manual QA.
- Keep payment UX v1-only for internal provider flows: no checkout, payment-method, refund, or invoice UI unless product explicitly asks for it.
- Default tier currency: JPY. Treat prices as integer yen. Older plans allowed editable `tax_amount`, but newer backend subscription-tier write schemas removed tax/total from create requests; re-check `buffdemy-backend/apps/api/src/routes/subscription-tier` before planning any tier write payload.
- Subscribe/change/cancel flows should use confirmation dialogs, not a checkout page, when no real payment provider is in scope.
- Any authenticated user may access `/creator/subs` if creator capability is represented by creating/managing tiers rather than a separate role.
- Preserve backend auth/ownership as authoritative; frontend write proxies should fail closed.

## Creator tier management split-view pattern

When planning a creator subscription management refactor, prefer this route split unless the user asks otherwise:

- `/creator/subs`: overview page with a top summary panel, existing tier list rendered as card-list items, and a create-new-tier form/card.
- Each tier card links to `/creator/subs/tier/:tierId` or the Next route `src/app/creator/subs/tier/[tierId]/page.tsx`.
- `/creator/subs/tier/:tierId`: tier-specific summary card on top plus a paginated subscriber/member list below.
- The detail summary card may have an edit link/action, but detail editing should be limited to tier `name` and `description` when backend pricing fields are not intended to be mutable from that view.
- For member pagination, the existing list endpoint shape can be planned as `GET /subscription?id=<creatorId>&tier=<tierId>&populate=true&limit&skip` when confirmed in the current backend/frontend proxy code.
- If an overview summary is derived from the loaded tier cards only, say so explicitly in `spec.md`; do not imply an all-tier aggregate unless a backend aggregate endpoint is planned.

## Pitfalls to plan around

- Do not infer public subscribe state from only the first page of outgoing subscriptions. Plan deterministic lookup/pagination handling.
- Do not accidentally add payment-provider UI (checkout/payment method/refunds/invoices) when backend only exposes internal/manual billing records.
- For create-tier UI/payloads, do not include `tax`, `tax_amount`, `total`, or derived total fields after the backend schema has removed them. Prefer a strict write schema such as `{ price: { base_amount } }` if that matches the inspected backend route typing.
- For tier-detail edit payloads, do not send `price` or other non-editable fields when the scoped UX only permits `name` and `description` updates.
- Detail routes for creator-owned tiers should fail closed for invalid, nonexistent, fetch-failed, or non-owned `tierId` values.
- Explicitly include manual visual QA for all new route areas.
- Record backend fixture/live mutation needs separately from frontend implementation tasks.
