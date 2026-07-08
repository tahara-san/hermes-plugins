# Buffdemy Main Content Feed Frontend Planning Notes

Use this reference when planning frontend work for the Buffdemy authenticated main content feed.

## Backend Contract

Source of truth: `~/dev/buffdemy-backend/docs/frontend-guides/v1-feed-system.md`.

V1 boundaries:

- Backend-owned `GET /feed` is the source of truth.
- Strict authenticated feed for the current viewer.
- V1 supports only `type=main`.
- V1 content is Article-only.
- The response is normal public Article data plus `feed: { type: 'main', contentType: 'article', score: number }`.
- `feed.score` is an epoch-millisecond cursor; use it for both older and newer requests.
- The endpoint does not return pagination metadata.
- Feed population is eventually consistent through backend materialization; do not treat immediate absence after follow/subscribe/publish as a frontend failure.

## Frontend Rules to Capture in Specs

- Do not use WebSocket, SSE, or push invalidation for V1 unless a later backend contract explicitly adds it.
- Do not compose a feed client-side from follow/subscription lists.
- Do not call Redis, RabbitMQ, outbox, unifiedConsumer, or feed materialization internals from the frontend.
- Do not sort feed items client-side by `publishedAt`, `createdAt`, creator, `_id`, or any other field; preserve backend order.
- Dedupe merged pages by Article `_id`.
- Keep `feed` metadata intact after schema/model parsing. Do not round-trip feed entries through Article/BaseArticle init helpers in a way that drops `feed`, because the UI needs it for cursors.
- Render scoped/gated Article state from the returned Article shape and existing `privileges.read` behavior.

## Pagination / Refresh Shape

Recommended page size: `FEED_PAGE_SIZE = 50`.

- Initial load: `GET /feed?limit=50`.
- Older page: `GET /feed?olderThan=<lastVisibleItem.feed.score>&limit=50`.
- Newer refresh: `GET /feed?newerThan=<firstVisibleItem.feed.score>&limit=50`.
- Initial retry after SSR feed failure and no visible items should call the frontend proxy with `limit=50` and no cursor.
- Only use `olderThan` / `newerThan` after at least one visible feed item exists.
- Stop/disable older pagination when an older response returns fewer than `FEED_PAGE_SIZE` items or zero unique items after dedupe.
- Do not invent a compound cursor; V1 supports score-only cursors.

## Proxy / Adapter Planning Notes

- Plan a frontend `/api/feed` proxy for client pagination/refresh so browser code uses the app session/cookie flow instead of calling the backend directly.
- Client adapter path wording should account for helper conventions: if an existing client API helper already prefixes `/api`, the adapter may need to pass `/feed/` rather than `/api/feed/` to avoid `/api/api/feed/`.
- Proxy query policy should be explicit:
  - accept `limit`, `olderThan`, and `newerThan`;
  - reject unsupported query keys unless implementation intentionally tolerates `type=main` for compatibility;
  - if `type` is tolerated, accept only `type=main` and reject every unsupported value;
  - reject simultaneous `olderThan` and `newerThan`.

## UI / Verification Planning Notes

- Keep the root page thin and server-first: load session, render signed-out CTA without feed call, server-fetch initial feed for active users, and pass errors to a client leaf for retry.
- Include signed-out, loading, empty, retryable error, refresh, and older-loading states.
- Tests should prove order preservation, score-cursor construction, `_id` dedupe, initial-error retry with no cursor, and older-pagination stop behavior.
- If parallelizing implementation, assign `hooks/useMainFeed.ts` to one owner (usually signed-in UI) and keep hook tests as a separate non-mutating test workstream to avoid file conflicts.
