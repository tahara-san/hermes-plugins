# Buffdemy User Role Feature-Gate Frontend Planning Notes

Use this reference when planning Buffdemy frontend work for backend `user.role` / feature-gate migrations.

## Contract shape

Backend roles/features:

```ts
export type UserRole = 'user' | 'creator' | 'paidContentCreator';
export type UserFeature =
  | 'article.create'
  | 'article.update'
  | 'paidContent.create'
  | 'subscriptionTier.create'
  | 'subscriptionTier.update'
  | 'subscriptionTier.delete';
```

Role matrix:

- `user`: no features.
- `creator`: `article.create`, `article.update`.
- `paidContentCreator`: creator features plus `paidContent.create` and all `subscriptionTier.*` features.

Planning rules:

- Treat missing/unknown roles as `user`; do not preserve public `admin` compatibility.
- Use the current authenticated user as frontend source of truth; do not use public profile/author role to decide viewer capability.
- Client gating is UX-only; backend remains authoritative.
- `feature_forbidden` is product-feature denial, not auth/session expiration.
- If UI believed the user had a feature but backend returns `feature_forbidden`, plan stale-role recovery by refreshing/revalidating current-user state without showing session-expired UX.
- Do not reintroduce public `/link/purge` dependencies.

## Route/UI planning checklist

- `/article` composer requires `article.create`; denied authenticated users should see product-feature denied/upgrade copy, not signin/session-expiry behavior.
- Article edit affordances require existing owner/write checks plus `article.update`.
- `DELETE /article/:article` has no new role gate; do not accidentally add one while gating edit/update.
- Any Article ACL rule containing `subscribed` in `acl.read`, `acl.write`, or `acl.comment.create` requires `paidContent.create`, including mixed arrays like `['followed', 'subscribed']`.
- Subscription-tier management requires paid-content creator capability. Prefer a named helper/composed check for tier-management capability and individual controls for `subscriptionTier.create/update/delete`.
- Consumer subscription routes under `/subscription` and consumer settings/billing routes are not role-gated by paidContentCreator.
- `POST /media` is not role-gated.

## Parallelization pitfall

For frontend migration plans, Phase 1 role/feature model work is usually sequential. Error/i18n, article UX, and subscription UX can often run in parallel after Phase 1, but define shared contracts up front before parallel dispatch:

- exact feature-forbidden helper signature, e.g. `isFeatureForbiddenError(error: unknown): boolean`;
- exact translation keys in EN/JA;
- whether AuthState/useAuth exposes current-user refresh for stale-role recovery.

Without this mini synchronization point, parallel workstreams may drift on translation keys or helper names.

## E2E fixture/user decision gates

When known E2E users have fixed roles, do not assume another user can be added or promoted. If a paidContentCreator user is needed for subscription-tier dashboard E2E, stop and ask with concrete options.

For Buffdemy’s current known users from the migration session:

- `test01@test.com` / `test01` / `testuser1`: `creator`.
- `test02@test.com` / `test02` / `testuser2`: `user`.

If consumer subscription scenarios use testuser2 as the subscriber, remember Playwright authentication context: specs under `src/tests/e2e/auth/` may default to `USER1_STATE`; subscriber assertions for testuser2 need `chromium-auth-user2` / `USER2_STATE` or an explicit user2-authenticated context, while fixture setup/reset may still require user1 ownership if the test-only route is gated that way.

## Verification planning

Include route-level tests or an explicit no-harness fallback for:

- denied `/article` does not fetch/create drafts before checking `article.create`;
- denied `/creator/subs/` does not render management UI;
- consumer subscription/billing routes remain ungated;
- `feature_forbidden` does not trigger session expiry;
- stale role is refreshed/revalidated after authoritative feature denial;
- final searches for stale `admin`, `/link/purge`, and raw role-string capability checks.
