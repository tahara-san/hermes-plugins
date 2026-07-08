# Superseded scaffold verification example — user subscription endpoints

Use this as a model when a `tasks/<name>/` directory contains old endpoint/scaffold docs rather than a normal progress/todo plan.

## Situation

`tasks/user-subscription/` contained only:

- `endpoints.md` — endpoint structure draft for `/subscription-tier`, `/subscription`, and `/billing-record`.
- `subscription-ecosystem.html` — architecture/lifecycle visualization.

There was no active `spec.md`, `progress.md`, or `todo*.md`. The user said to ignore small implementation differences because the docs were likely created for initial scaffolding.

## Verification pattern

1. List tracked files in the task dir and recent commits touching it:
   ```bash
   git ls-files tasks/user-subscription
   git log --oneline --max-count=5 -- tasks/user-subscription
   ```
2. Extract the draft's intended resources/endpoints.
3. Verify route files exist and are mounted from `apps/api/src/routes/index.ts`:
   - `apps/api/src/routes/subscriptionTier/`
   - `apps/api/src/routes/subscription/`
   - `apps/api/src/routes/billingRecord/`
4. Verify OpenAPI tags are wired from `apps/api/src/routes/openApiTags.ts`.
5. Verify repository layer exists and is exported:
   - `packages/mongo/src/repositories/subscriptionTier/`
   - `packages/mongo/src/repositories/userSubscription/`
   - `packages/mongo/src/repositories/billingRecord/`
6. Verify tests exist:
   - `apps/api/src/test/routes/subscriptionTier.test.ts`
   - `apps/api/src/test/routes/subscription.test.ts`
   - `apps/api/src/test/routes/billingRecord.test.ts`
   - repository tests for the three Mongo resources.
7. Verify downstream/outbox/Neo4j pieces when the draft mentions them:
   - `USER_SUBSCRIPTION_CREATED`
   - `USER_SUBSCRIPTION_TIER_CHANGED`
   - `USER_SUBSCRIPTION_DELETED`
   - `apps/outboxProcessor/src/handlers/userSubscription/`
   - `apps/unifiedConsumer/src/handlers/neo4j/userSubscription/`
8. Verify maintained docs supersede the task draft, e.g. `docs/frontend-guides/user-subscription.md` and `docs/api-endpoints.md`.

## Classification

If all of the above are present, classify the old task dir as stale/superseded even if the implementation differs in refined details. Example acceptable drift: an old draft allowed clients to send `currency`, `tax_amount`, and `grand_total_amount`, while current code derives/rejects those fields server-side in subscription-tier helpers.

Do not delete immediately unless the user explicitly approves cleanup; report the evidence and recommended cleanup candidate first.
