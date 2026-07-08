# Buffdemy subscription/billing view implementation notes

Use this when executing plans that add or modify Buffdemy subscription tiers, subscriptions, billing records, or related frontend views.

## Model/schema guardrails

- Keep API-source schemas aligned with backend wire shapes, and instance schemas aligned with runtime model shapes.
- For nested date-bearing structures, do not only transform top-level dates. Example: billing record `period.startedAt` / `period.endedAt` arrive as strings from the API, but `BaseBillingRecord` should expose them as `Date` instances and serialize them back to ISO strings from `getInitProps()`.
- Avoid schema defaults that mask backend response drift for required aggregate fields. Example: `SubscriptionTier.stats.subscriberCount` should be required if the backend contract returns it; defaulting to `0` makes missing data look valid and can hide API regressions.
- Add regression tests for both parsed runtime types and `getInitProps()` serialization when transforming nested model fields.

## Creator/subscriber route taxonomy and UI wording

- Preserve the current route separation unless the user explicitly requests a restructure:
  - `/creator/subs/` is the creator-owned subscription tier overview/management surface.
  - `/creator/subs/tier/[tierId]/` is the creator-owned tier detail/members/edit surface.
  - `/settings/subs/` is subscriber-side outgoing subscriptions to other creators.
  - `/settings/billing/` is billing records/history.
  - `/users/[username]/subs/` is the public subscribe/change/cancel page.
- Avoid moving creator-owned tier management into `/settings/subs/`; use explicit links between settings and creator routes when needed.
- When product wording says “disable” but backend disable semantics are deferred, change only the visible UI copy to Disable/Confirm disable and leave existing delete API/internal behavior untouched unless the plan explicitly asks for backend disable logic. Do not add migration/backward-compatibility code for this wording-only change.
- For Japanese-capable subscription UI, keep EN/JA translation parity and remove unused translation keys after deleting visible UI blocks such as overview stats.

## Verification pattern

For schema/model/API proxy phases, run all three after fixes:

1. `npx tsc --noEmit --pretty false`
2. targeted `npx vitest run ...` for new model/route tests
3. targeted `npx eslint ... --max-warnings 0`

Then run the mandatory simplify pass before independent review, and re-review after any review-driven fix.