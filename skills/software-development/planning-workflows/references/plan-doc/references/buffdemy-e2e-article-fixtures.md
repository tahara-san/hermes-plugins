# Buffdemy E2E Article Fixture/Seeding Planning Notes

Use this when `/plan-doc` is creating a plan for fast Playwright Article fixtures, gated test-only routes, or migrating UI-driven Article setup to API setup.

## Existing Patterns to Inspect

- `src/app/api/test-only/_lib/isEnabled.ts` — test-only route gate. Plans should require `NODE_ENV !== 'production'` and `TEST_E2E_AUTH_HARDENING=1`, returning 404 when disabled.
- `src/app/api/test-only/bootstrap-session/route.ts` — test-only session bootstrap pattern and known E2E users.
- `src/app/api/test-only/article-acl-fixture/route.ts` — proven Article creation via `api.fetch({ path: '/article', method: 'POST', requireToken: true, data }, undefined, ArticleApiSourcePropsSchema)` and cleanup safety patterns.
- `src/tests/e2e/helpers/article.ts` — current UI-driven `createAndPublishArticle`/`deleteArticle` helpers.
- `playwright.config.ts` and `src/tests/e2e/helpers/constants.ts` — storage-state names and authenticated projects.
- `src/models/base/article/schema/common.ts` — valid Article types/statuses; do not invent enum values in plans.

## Planning Checklist

1. Keep the route test-only: plan a hard gate and a 404 response when disabled. Cover both `TEST_E2E_AUTH_HARDENING` missing/disabled and `NODE_ENV=production` even when the flag is set.
2. Require authenticated known E2E fixture ownership; if specs create manual `browser.newContext(...)`, explicitly plan `storageState: USER1_STATE` or use the authenticated project page fixture.
3. Use the real backend Article pipeline rather than production UI/Tiptap interaction when the test only needs a fixture Article.
4. Force the minimum needed fixture shape. For published Article setup, force `status: 'published'` unless the task explicitly needs draft/deleted state.
5. Use valid backend Article type enum values (`gameplay_review`, `device_review`, `tips`, `data`, `news`, `fluff`) or a single helper mapping UI labels such as `Tips` to backend values.
6. If adding mutation or cleanup actions, plan them as carefully as setup:
   - cleanup request should be narrow, usually `{ action: 'cleanup', articleId }`;
   - fetch before PUT/DELETE;
   - require known fixture owner AND deterministic route-controlled seed markers (for example title prefix plus tags `e2e` + `seed`/scenario tag);
   - positively verify fixture scope before every mutation or cleanup, not just before delete;
   - include refusal tests for wrong owner, missing markers, and mutation of non-fixture Articles;
   - explicitly migrate each target spec's `afterAll` cleanup, not only setup.
7. If planning stale-permission or status-mutation E2E flows, name the initially allowed scenario and exact narrow helper action (`setCommentCreateAudiences`, `setArticleStatus`, etc.) in the TODO, and require route/unit coverage for those mutation actions plus fixture-scope refusal.
8. Preserve editor-specific tests on the UI path; do not migrate tests whose purpose is Article editor publishing, media uploads, or TipTap behavior.
9. Verification should include route unit tests, lint, proportional build verification, and targeted Playwright specs. If local E2E services/credentials are unavailable, require documenting the exact blocker and commands. For test-only routes, state that the app/dev server itself must run with the gate env vars; setting them only for the Playwright runner is insufficient.

## Common Pitfalls

- Planning a fast setup path but leaving slow/flaky UI cleanup in migrated specs.
- Relying on a user-provided title prefix alone for destructive cleanup; route-controlled markers are safer.
- Accepting arbitrary owner/ACL/status fields in a generic seed endpoint and accidentally creating a broad test-only mutation surface.
- Mentioning invalid Article types in the plan because the schema was not inspected.
- Saying `pageOrRequestContext` without specifying how the helper branches; prefer a clear `Page` helper unless the plan truly needs both.
