# Buffdemy frontend: REST/App Route vs Server Action read boundaries

Use this reference when a Buffdemy frontend `/plan-code` task migrates client-triggered pure reads away from Server Actions or enforces REST/App Route boundaries.

## Proven migration pattern

1. Inventory current read call sites before editing:
   - client components/models importing `~/server/actions/**`
   - server-action exports whose only job is a GET/read proxy
   - shared models under `src/models/**` used by client bundles as well as `src/client/models/**`
2. Add/extend App Route GET coverage first for each migrated read:
   - route tests should mock the backend/server API layer and assert path, method, token/auth behavior, query handling, and response schema
   - client tests should assert the new `clientApi.fetch('/api/...', { method: 'GET' })` call shape, not the removed Server Action
3. Migrate callers to REST-backed client/domain APIs:
   - browser/client code should call `clientApi` or a client-safe model method that uses an App Route
   - login/authorization navigations should hit the App Route URL directly when the behavior is a redirect/read orchestration, not a Server Action round trip
4. Add a static boundary test once the first migration lands:
   - fail if client components/models import removed pure-read Server Actions
   - include shared client-used model files, not just `src/client/**`, because shared `src/models/**` can still leak server actions into client bundles
5. Remove stale GET Server Action exports after a full search confirms no valid caller remains.
6. Run targeted route/client/static tests, TypeScript, lint/i18n, and build; rerun affected checks after every post-review tweak.

## Review pitfalls caught in-session

- Backend `api.fetch` wrappers may not accept Next fetch cache hints. Do not pass `cache: 'no-cache'` through server API helpers unless the helper type/implementation explicitly supports it. If a migrated App Route needs no caching, solve it at the App Route/Next layer or by existing helper semantics rather than adding unsupported options.
- When moving autocomplete/tag reads, verify the response schema matches the endpoint. A `/api/tags` route that returns `Tag` data should be parsed through `Tag`/tag schemas, not stale `PostTag` schemas preserved from an older Server Action.
- Removing an exported Server Action/model method is preferable to keeping a broken compatibility shim when searches prove no caller remains. Keeping stale exports can hide schema mismatches and lets future client code reintroduce the forbidden boundary.
- OAuth/auth callback reads can be missed because they are server-side and outside the obvious client migration path. Include auth callback/action files in the stale `cache`/GET Server Action cleanup search.
- Final cleanup is invalidated by even tiny post-review edits such as removing a stale method or cache hint. Re-run the affected targeted tests, TypeScript, simplify/review, and final verification before checking completion or deleting task files.
- When deleting a pure-read Server Action file/export, also audit colocated tests and mocks for that deleted module. A stale test importing `../checkName` (or similar) can be missed by targeted replacement route tests and fail later during broader test discovery. Either delete the stale Server Action test when replacement App Route tests cover the behavior, or rewrite it to target the new route. Strengthen static boundary tests to scan tests/source for imports or method references to removed GET Server Action modules/exports, excluding the static test file itself if it contains sentinel strings.

## Suggested focused verification set

Adjust paths to the current diff, but for this class of task include:

```bash
npx vitest run \
  src/app/api/tags/tests/route.test.ts \
  src/app/api/media/tests/route.test.ts \
  src/app/api/user/check-name/tests/route.test.ts \
  src/tests/static/restServerActionBoundary.test.ts \
  src/client/libs/clientApi/tests/clientApi.test.ts \
  src/components/common/tagListFetcher/tagListFetcher.test.ts

npx tsc --noEmit
npm run lint
npm run build
```

If OAuth callback code changed, add the focused callback suite before final verification.