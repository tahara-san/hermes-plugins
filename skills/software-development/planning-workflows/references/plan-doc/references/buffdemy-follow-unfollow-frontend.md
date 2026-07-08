# Buffdemy Follow / Unfollow Frontend Planning Notes

Use this reference when planning `buffdemy2-web` work around user follow/unfollow API routes, profile UI, or Feed relationship setup.

## Known Frontend Surfaces

- Frontend app route: `src/app/api/user-follow/route.ts`.
- Route tests: `src/app/api/user-follow/tests/route.test.ts`.
- Existing profile follow affordance has been observed in `src/components/users/profile/sidebar/profileSidebar.tsx` as a static Follow button; wire this before inventing a new broad UI.
- Existing local CTA/auth/owner handling patterns can be inspected in `src/components/users/profile/sidebar/profileSubscriptionCta.tsx`.
- Client/server userFollow model helpers have historically supported GET/fetch only:
  - `src/client/models/userFollow/userFollow.ts`
  - `src/server/models/userFollow/userFollow.ts`
- Dedicated profile follow E2E may exist at `src/tests/e2e/auth-user2/followUnfollow.spec.ts`; watch for skip-tolerant smoke tests that pass without a functional UI.
- Feed membership/backfill E2E may exist at `src/tests/e2e/auth-user2/feedFollowUnfollow.spec.ts`; keep it real backend-backed and distinct from profile follow/unfollow product coverage.

## Backend Contract to Recheck

Backend route source has been observed under:

- `/home/tahara/dev/buffdemy-backend/apps/api/src/routes/userFollow/get.ts`
- `/home/tahara/dev/buffdemy-backend/apps/api/src/routes/userFollow/post.ts`
- `/home/tahara/dev/buffdemy-backend/apps/api/src/routes/userFollow/delete.ts`

Planning assumptions to verify against live code:

- `GET /user-follow` accepts one of `id` or `self` plus pagination/populate options. Preserve existing frontend GET behavior unless a concrete app contract requires tightening.
- `POST /user-follow` body is exactly `{ id: string }`; frontend proxy should reject unknown keys before proxying.
- `DELETE /user-follow?id=<targetUserId>` accepts exactly the `id` query key; frontend proxy should reject missing/unknown query shape before proxying.
- Mutations require authenticated backend forwarding (`requireToken: true`).
- Keep backend authoritative for permission/data rules: self-follow, target existence, deleted targets, idempotency, stats, and authorization.
- Preserve structured backend errors when route proxy helpers support it (for example via `_subscriptionProxyUtils.proxyFetch` / `mapApiError`).

## Planning Checklist

- Preserve existing `GET /api/user-follow` behavior and route coverage.
- Add/confirm strict `POST /api/user-follow` and `DELETE /api/user-follow?id=...` mutation proxy behavior.
- Include route/unit tests for exact forwarding, invalid/missing inputs, unknown keys, auth forwarding, and structured backend errors.
- Prefer typed client/model helpers for UI calls unless a tiny local app-route fetch is materially simpler and still follows local conventions.
- Keep profile sidebar server-first; use a small client leaf only for interactive follow/unfollow mutation state.
- Decide whether visible follower count updates after a successful mutation or remains stale until refresh; document the decision.
- Add English/Japanese i18n parity and plan `npm run check:i18n` when translation files change.
- Dedicated profile follow/unfollow E2E should be deterministic: authenticated happy path, unfollow path, unauthenticated behavior if exposed, and failure UI if practical.
- Feed E2E should remain a real follow/backfill membership test: seed fresh article, assert absent before follow, follow via app API, poll `/api/feed`, assert present, unfollow, assert removal. Do not mock `/api/feed` for this scenario.

## Common Pitfalls

- Treating Feed backfill E2E as the only follow/unfollow product coverage.
- Letting Zod strip unknown POST keys by default instead of rejecting stale/misspelled payloads.
- Changing/tightening GET semantics while implementing mutation strictness.
- Adding a client component around the whole sidebar instead of a small leaf button.
- Leaving skip-tolerant E2E that can pass when the Follow button is still static.
- Forgetting that task docs are untracked: independent review bundles must include untracked planning files explicitly, not only `git diff`.