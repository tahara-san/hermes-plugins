# Buffdemy test-only subscription/billing fixture routes

Use this reference when implementing or verifying backend support for deterministic subscription, tier, and billing UI/E2E fixtures.

## Durable route shape

- Keep the backend route outside production and fail closed:
  - register only when `NODE_ENV !== 'production'`
  - require explicit E2E hardening opt-in such as `TEST_E2E_AUTH_HARDENING=1`
  - disabled/production behavior should be route absence/404 before auth, not a handler-level 403 after route registration
- Put routes under a clearly test-only namespace such as `/test-only/<feature>` and keep public production route groups separate.
- Use `strictAuthPreset` for authenticated fixture routes, but set `logBody: false` when the body could include fixture controls or future sensitive identifiers.
- Authorize a stable test actor explicitly. For Buffdemy Playwright-style default users, allow only the default E2E `user1` to run global fixture reset/setup.
- Keep the standard API response contract: `{ success: true, content }`.

## Fixture data boundary

For subscription/billing E2E support, distinguish user identity/profile data from subscription/billing surface data:

- Preserve default E2E `user1`/`user2` user documents and profile fields.
- Under the explicit hardening gate, their subscription tiers, user-subscriptions, and billing records may be considered fixture-controlled state so reset scenarios can make empty pages actually empty.
- Preserve unrelated non-E2E users and rows with no default-E2E/synthetic fixture involvement.
- Add a short inline ADR-style comment at the broad cleanup filters explaining this boundary; otherwise reviewers may reasonably flag user1/user2-owned-row deletion as over-broad.

## Reset/setup implementation notes

- Reuse existing Mongo repositories/schemas for creation where possible, so domain validation and normalization still run.
- Respect unique indexes:
  - subscription tiers commonly need deterministic but unique display names per owner
  - billing records need deterministic `paymentRef` values with a fixture prefix, and reset should remove them first
- Reset filters should remove all fixture-generated surface rows before setup, including rows referenced by fixture tier IDs, subscription IDs, paymentRef prefixes, or synthetic/default-E2E participants.
- Recalculate affected subscription stats after deleting or creating subscriptions; tests should assert stat repair, not just returned payloads.
- Preserve deterministic response ordering for billing lists and subscription lists. Tests should assert first/selected item fields, not only counts.

## Verification pattern

- Add route tests for:
  - disabled gate 404 before auth
  - production 404 even when the opt-in env var is set
  - unauthenticated 401 when enabled
  - authenticated non-user1 403
  - idempotent reset
  - empty scenarios with exact paths and empty arrays
  - populated public tiers, active subscription, creator dashboard, settings subscription list, and billing scenarios
  - unrelated non-E2E data preservation plus stats repair
- Run targeted route tests and per-app build in the Docker API container:
  - `docker compose exec -w /app/apps/api api bun test src/test/routes/<fixture>.test.ts`
  - `docker compose exec -w /app/apps/api api bun run build`
- If the full API suite fails in an unrelated area, isolate the failing test file. If that file fails alone with the same error, document it as an external/baseline blocker and rely on targeted passing tests plus build for this task.