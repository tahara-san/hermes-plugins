# Buffdemy Tag List / Tag Feed Frontend Planning Notes

Use this reference when planning frontend work for Tag discovery, popular tags, tag search, tag-combination feeds, or tag/tag-combination follow UX in `buffdemy2-web`.

## Known Current Frontend Surface

- Root authenticated feed lives at `src/app/page.tsx` and delegates UI to `src/components/top/mainFeed`.
- Root mixed-content feed proxy is `src/app/api/feed/route.ts`; historically it accepted only `limit`, `olderThan`, and `newerThan` and rejected unsupported keys. Do not assume tag Article feeds should extend this path.
- Client/server mixed-feed adapters live under `src/client/models/feed` and `src/server/models/feed`; Article list adapters live under `src/client/models/article` and `src/server/models/article`.
- Main mixed-feed hook (`src/components/top/mainFeed/hooks/useMainFeed.ts`) preserves backend order, dedupes by Article `_id`, uses `feed.score` cursors, and has stale async response guards.
- Backend Article tag-feed support may be documented in the backend checkout at `docs/frontend-guides/tag-article-feed.md`: use `GET /article` with repeated `tags`, normal Article array responses, AND tag membership, `sortBy=publishedAt&sortDirection=desc`, and `olderThan`/`newerThan` epoch-millisecond cursors derived from Article `publishedAt`.
- Legacy tag search/autocomplete used `PostTag.search` via `src/server/actions/postTag/postTag.ts` (`/post-tag/search`) and `src/components/common/tagListFetcher/tagListFetcher.ts`.
- Article tag chips used `linker.postFeed.getPath({ tags: name })`; the legacy `PostFeedLinkHandler` pointed to `/posts/?tags=...`, but there may be no App Router `/posts` page. Verify before retaining that link shape.
- Follow mutation proxy conventions are available in `src/app/api/user-follow/route.ts`: strict POST body validation, strict DELETE query validation, `requireToken: true`, and structured backend-error preservation.
- App shell search/navigation surfaces include `CompactSearchField`, `MobileTopbar`, `NavRail`, `MobileBottomMenu`, and `SearchSidebar`; navigation copy usually lives in `topbar`.

## Planning Decisions to Capture

When backend Tag model/search is expected ready but exact frontend contract is not fully known, gate implementation on contract confirmation rather than inventing client-side approximations.

Recommended frontend route shape unless product/backend requires otherwise:

- `/tags` — Tag List discovery/search page.
- `/tags/feed?tags=<tag>&tags=<tag>` — filtered content feed for one or more tags.
- `/api/tags` — canonical frontend proxy for tag search/popular tags.
- `/api/tag-follow` — canonical frontend proxy for exact tag/tag-combination follow state and mutations.

Recommended semantics to document:

- Public tag URLs/API calls should use the backend-confirmed canonical public identifier, expected to be slug-like `name` unless the backend exposes `slug`. Do not use `displayName` or database `_id` in public URLs unless explicitly required.
- Treat tag combinations as order-insensitive exact sets. `VALORANT + ASCENT` and `ASCENT + VALORANT` should normalize to the same identity.
- Serialize selected tags in stable sorted canonical order for URLs/API identity; preserve user/backend display order for UI only.
- Plan filtered-feed semantics as AND (`VALORANT + ASCENT` means content with both tags) but confirm with backend; if backend semantics differ, stop for a product/backend decision.
- Do not fetch the main feed and filter client-side. Use backend-owned filtered feed results.
- Popular tags should display backend ranking as returned; do not derive/sort popularity from local articles.

## Backend Contract Gate

Before coding, confirm and record which backend contract applies. Prefer a current backend frontend guide over older assumptions; if the user references a sibling backend doc with a missing `~/dev/...` path, try the workspace sibling path (for example `/workspace/dev/buffdemy-backend/docs/...`) before asking.

For **Article-only tag feeds**, if `docs/frontend-guides/tag-article-feed.md` exists in the backend checkout, treat it as the source of truth:

- Use `GET /article`; do not add a new tag-feed endpoint and do not extend mixed-content `/feed` unless a newer contract explicitly says so.
- Response content is the normal Article array; there is no feed metadata object and no `feed.score` cursor.
- Send repeated `tags` query params for multi-tag AND membership (`tags=valorant&tags=ascent` returns Articles containing both tags; extra tags may still be present).
- Use `sortBy=publishedAt&sortDirection=desc` for default latest-first display feeds.
- Use `olderThan` / `newerThan` as exclusive epoch-millisecond filters derived from Article `publishedAt`; note this is not a lossless total-order cursor for identical timestamps.
- Render backend order unchanged and display returned normalized Article tags in returned order.
## Backend Contract Gate

Before coding, confirm and record:

- Tag search/popular endpoint path, method, auth requirement, accepted query keys, duplicate-key policy, result envelope, result schema, canonical identifier (`name` vs `slug` vs `_id`), Unicode handling, and case normalization.
- Whether popular tags are a separate endpoint or a query mode on search.
- Filtered feed endpoint/query shape; do not assume it reuses `GET /feed`. Check current backend/frontend-guide docs first. As of the backend guide `docs/frontend-guides/tag-article-feed.md`, Article-only tag feeds use `GET /article` with repeated `tags`, normal Article arrays, no Feed metadata, AND membership semantics, `sortBy=publishedAt&sortDirection=desc`, and exclusive `olderThan`/`newerThan` epoch-ms cursors from Article `publishedAt`.
- Tag/tag-combination follow endpoint path, methods, payload/query identity shape, returned follow state/counts, GET auth behavior, POST/DELETE auth requirement, idempotency, and structured error shape.
- Cache policy: popular tags may be cacheable only if public/cacheable; filtered feeds and follow state must be auth-aware/no-store when personalized. Never cache user-specific follow state across users.

If filtered feed or tag-combination follow backend support is missing, stop and report the backend blocker instead of implementing a client-side approximation. If a backend guide says the support exists on a different existing endpoint (for example `GET /article` rather than `GET /feed`), refresh the plan in place and remove stale backend-blocker language.

## Frontend Planning Checklist

- Create new Tag schemas/models rather than extending legacy `PostTag` if the backend has moved to Tag as the product model.
- Add shared tag-combination normalization helpers for trim, canonical identifier normalization, dedupe, stable identity, repeated-query serialization, Unicode/case behavior, and display labels.
- Add strict `/api/tags` and `/api/tag-follow` route tests: accepted params, duplicate/unknown rejection, schema parsing, structured backend errors, auth forwarding for mutations, and cache/auth policy.
- Choose the data endpoint from the confirmed backend guide before planning proxy/model changes. Use `/api/feed` + Feed models only for mixed-content Feed-backed responses; use `/api/article` + Article models for Article-only tag feeds. Preserve root main-feed behavior either way.
- Filtered feed hook/page must include selected tags in initial load, retry, refresh, older pagination, stale async guards, and dependency arrays so old tag responses cannot update a newer selection.
- Preserve backend order and the backend-confirmed cursor contract. For Feed responses this may be `feed.score`; for Article-only tag feeds this is Article `publishedAt` epoch milliseconds. Add tests proving the frontend does not sort or convert cursor types incorrectly.
- Use a dedicated `tags` i18n namespace for `/tags` and `/tags/feed`; keep app-shell search/navigation copy under `topbar`.
- Use a dedicated `tags` i18n namespace for `/tags` and `/tags/feed`; keep app-shell search/navigation copy under `topbar`.
- For navigation, prefer wiring existing search affordances to `/tags` before adding another primary nav item: desktop `CompactSearchField` can submit to `/tags?q=...`, mobile topbar search can link to `/tags`, and article chips should link directly to `/tags/feed?tags=...`.
- Add tests that article tag chip hrefs no longer contain legacy `/posts/` when the new tag-feed route is intended.

## E2E Notes

- Deterministic UI/navigation E2E can mock `/api/tags` and filtered `/api/feed` for popular tags, search/select combination, canonical reordered URL, repeated `tags` params, cursor params, and empty/error states.
- Backend-backed follow/tag-feed E2E should be gated on confirmed backend readiness and should not mock the follow/feed membership behavior it is meant to prove.
- Scope app-shell assertions to stable shell test IDs (`app-shell-content`, `app-shell-nav-rail`, `app-shell-search-sidebar`, `app-shell-mobile-topbar`, `app-shell-mobile-bottom-menu`) to avoid duplicate semantic controls after shell migrations.
