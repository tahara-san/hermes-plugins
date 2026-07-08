# Buffdemy Backend Search Endpoint Inventory Pattern

Use this when a Buffdemy backend plan-doc asks which search endpoints already exist versus which need implementation.

## Key distinction

Do not classify internal Elasticsearch models, aliases, or unifiedConsumer projection handlers as user-facing API endpoints. Report three separate layers when relevant:

1. **API route exposed** — an Elysia route mounted under `apps/api/src/routes/**` that accepts search query params and returns API payloads.
2. **Collection/list filtering only** — a `GET /resource` handler that filters by id/tag/status/owner/pagination but does not perform text search.
3. **Search infrastructure exists** — `packages/elasticsearch/src/models/**` and/or `apps/unifiedConsumer/src/handlers/search/**` projection upsert/delete handlers exist, but no API route queries them.

## Source inspection checklist

- Inspect `apps/api/src/routes/index.ts` for mounted route groups.
- Inspect each resource `index.ts` and `get.ts` under `apps/api/src/routes/<resource>/`.
- Search for explicit `search` route folders such as `apps/api/src/routes/postTag/search/`.
- Inspect `packages/elasticsearch/src/models/index.ts` and per-model files to identify indexed documents.
- Inspect `apps/unifiedConsumer/src/handlers/search/` to identify projection/indexing coverage.
- Search for actual API imports/usages of ES models before claiming a route is implemented.

## Classification wording

Use statuses like:

- **Implemented** — user-facing API route exists and performs search.
- **Partially implemented** — a route supports bounded prefix/filter lookup that may satisfy autocomplete, but not full-text search.
- **Missing as API endpoint; indexing exists** — ES model/projection exists but no API route queries it.
- **Missing** — neither API route nor search projection/model exists.

## Buffdemy V1 search inventory example

As of the 2026-06-19 inventory:

- Creator search: partially implemented via `GET /user?q=...&role=creator|paidContentCreator`; Mongo prefix/filter lookup, not exposed ES user full-text search.
- Article Post Search: missing as API endpoint; ArticleContent ES projection/indexing exists.
- Article Comment Search: missing; no article-comment ES search model/projection found.
- Question Post Search: missing as API endpoint; QuestionContent ES projection/indexing exists.
- Question Answer Search: missing; no question-answer ES search model/projection found.
- Related existing explicit search route: `GET /post-tag/search` using Elasticsearch `PostTag` search.

## Plan-doc output guidance

For inventory-only requests, create task docs with:

- A table covering each requested service.
- Evidence paths for route handlers, ES models, and projection handlers.
- Open implementation decisions: endpoint shape, auth policy, response shape, missing projection/index coverage, analyzer/language strategy.
- A clear deviation note if the full plan-doc parallel review gate was not run, so the artifact is not mistaken for a fully reviewed implementation plan.
