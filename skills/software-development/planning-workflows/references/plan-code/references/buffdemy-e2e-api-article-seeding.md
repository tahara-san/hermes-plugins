# Buffdemy E2E API Article Seeding Pattern

Use this when migrating slow/flaky article/comment Playwright suites away from editor-driven article creation while preserving UI-driven behavior under test.

## Durable pattern

- Add a narrow `src/app/api/test-only/<fixture>/route.ts` endpoint only for E2E fixture setup/cleanup.
- Gate the route behind the same test-only hardening flag used by the E2E suite (for this project, `TEST_E2E_AUTH_HARDENING=1`). Fail closed when the flag is absent.
- Keep the fixture endpoint scoped to data setup and guarded cleanup; do not move the user-facing behavior under test out of the UI unless the plan explicitly says so.
- For article/comment flows, API-seed the article, then continue creating comments/reactions/permalinks through the UI so the real user path remains covered.
- Cleanup must verify ownership. Prefer stable email-based identity checks; if historical fixture data lacks email, only then fall back to username.
- Add route unit tests for disabled gate, validation, create, cleanup, ownership-denied cleanup, and idempotent/not-found cleanup behavior.
- Add Playwright helpers such as `seedArticle(...)` and `cleanupSeededArticle(...)` rather than duplicating fixture calls in specs.

## Verification shape observed useful

- Run the fixture route's focused Vitest suite first.
- Run lint/build after the API/helper changes.
- Run the migrated Playwright specs under the required E2E hardening env and target project.
- Finish with `git diff --check` before reporting completion.

## Pitfalls

- Do not replace UI-driven comment creation with API seeding when the spec is intended to cover comment UI behavior.
- Do not allow cleanup by username alone when email is available; this weakens fixture ownership boundaries.
- Keep this as test-only fixture infrastructure, not migration/backward-compatibility production code.