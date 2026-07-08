# Buffdemy backend search-endpoint readiness plan-doc pattern

Use when planning Elasticsearch-backed API search endpoints in Buffdemy backend, especially after an endpoint inventory or when the user asks which resources are "ready" for ES search.

## Readiness must include write-path coverage, not just ES models

Do not classify a search endpoint as implementation-ready only because an Elasticsearch model exists. For each target resource, explicitly check and report these layers:

1. **ES model/index** — model file under `packages/elasticsearch/src/models/<resource>/`, mapping fields, alias/concrete index, searchable fields, filter/sort fields.
2. **RabbitMQ search message schema and queue profile** — `packages/rabbitmq/src/queues/job/search/messages/schema.ts`, `types.ts`, and `index.ts` queue profiles.
3. **OutboxProcessor fanout** — `apps/outboxProcessor/src/handlers/<resource>/...` must turn Mongo outbox events into search jobs for create/publish, content/metadata update, unpublish/delete, and compensation paths.
4. **UnifiedConsumer search handler** — `apps/unifiedConsumer/src/handlers/search/<resource>/upsert.ts` and delete handler must validate current Mongo source-of-truth before indexing so stale events do not resurrect deleted/unpublished candidates.
5. **API route/query/hydration** — only after the above exist should the API endpoint be treated as mostly route work. The endpoint still must hydrate via Mongo and enforce status/ACL from Mongo before returning results.
6. **Backfill/reset path** — any new field needed for filtering (for example `role` on user search docs) requires a concrete backfill/reset/reindex plan before filters can be trusted for existing documents.

## Report statuses precisely

Use these categories instead of a binary ready/missing label:

- **Route-only / mostly ready** — ES model, search jobs, outbox fanout, and consumer handlers exist; API route/hydration is the main missing piece.
- **Partially ready** — some projection path exists, but important lifecycle coverage is missing (for example create/publish inserts exist but already-published updates do not fan out search changes).
- **Projection not ready** — no ES model/search queue/consumer/fanout exists; plan must include a new search projection before the endpoint.
- **Projection exists but contract-incomplete** — ES docs exist, but they lack fields needed by the endpoint contract (for example role filters for creator search), or write semantics can clobber data.

## Common Buffdemy patterns from Article/User/Question search planning

### Projection audit lessons from article-comment/question/question-answer

When auditing whether a resource is missing Elasticsearch document insertion on create/update, trace the full event chain instead of stopping at route files:

- API route creates an outbox event inside `outboxHelper.withOutboxTransaction`.
- `apps/outboxProcessor/src/handlers/<resource>/...` converts that event into `messageHelper.search.send<Resource>Upsert/Delete` jobs.
- `packages/rabbitmq/src/queues/job/search/messages/{schema,types}.ts` defines the search job payload.
- `apps/unifiedConsumer/src/handlers/search/<resource>/...` consumes the queue.
- `packages/elasticsearch/src/models/<resource>/...` performs the actual upsert/delete.

Concrete Buffdemy backend findings to remember for future search plans/audits:

- **Article comment** currently has publish/unpublish/delete/mention outbox and Neo4j/Mongo stat fanout, but no ES model, search job schema/type, search message helper, unifiedConsumer search handler, or search fanout. Treat create and update search insertion as missing until a new projection is planned.
- **Question** has `Question` ES model/search job/unifiedConsumer support and `QUESTION_PUBLISHED` fanout indexes ready content rows on create-as-published or draft→published. However, ordinary edits to an already-published question update/stale question content rows without emitting a question-content props-changed/search-upsert fanout event. Classify as **partially ready**, not route-only ready.
- **Question answer** currently has publish/delete outbox and Neo4j/Mongo stat fanout, but no ES model, search job schema/type, search message helper, unifiedConsumer search handler, or search fanout. Treat create and update search insertion as missing until a new projection is planned.

Use Article as the comparison pattern for published-content updates: `ARTICLE_CONTENT_PROPS_CHANGED`, `ARTICLE_PROPS_CHANGED`, hashtag/type-change handlers, and current-source validation before sending search upsert/delete jobs. If a new Question or Answer projection is planned, include analogous content-change outbox events and stale-event safeguards; do not rely only on `*_PUBLISHED` events.

### Resource-local route paths

Prefer resource-local search paths, matching existing `/post-tag/search`:

- `/article/search`
- `/user/search`
- `/question/search`
- `/article-comment/search`
- `/question-answer/search`

Avoid central `/search/<resource>` unless the user explicitly chooses a cross-resource search API. Buffdemy route groups are resource-centric, and route files should live under the domain directory.

### Do not count list endpoints as search endpoints when the user needs full-text/fuzzy search

If the user says an existing list/filter endpoint such as `GET /user` is not acceptable because it lacks partial/fuzzy/multi-word full-text semantics, treat that as a contract correction. Plan a dedicated search route (`/user/search`) and keep the old list endpoint unchanged.

### User/creator search readiness pitfalls

For creator search, role filtering must be present in the ES projection and rechecked after Mongo hydration. If `users` ES docs lack `role`, `/user/search` is not route-only work.

When ES upsert uses full-document replacement (`index()`), outbox fanout must not send partial payloads for props-changed events unless the model/client uses merge semantics (`doc_as_upsert`). Plan one of these invariants explicitly:

- every `sendUserUpsert` caller sends a complete replacement document; or
- the User ES write path is changed to update/merge semantics.

Also decide/document stale-write behavior. ArticleContent search docs use external versioning; if User search docs do not, the plan should either add ordering/versioning or state the residual V1 out-of-order overwrite risk.

### Article search route pitfalls

ArticleContent ES projection may be ready while the API route is missing. The route should:

- query the `article-contents` alias;
- support multi-word `q` via `multi_match` over `title` and `body`;
- bounded-overfetch ES candidates before Mongo hydration;
- collapse/dedupe by `articleId` when multiple language rows match;
- hydrate using the existing `/article` list route batching helpers and avoid avoidable N+1 reads;
- enforce Mongo source-of-truth status/ACL before response.

Document that offset pagination applied before Mongo/ACL filtering can under-fill pages and create cross-page gaps/duplicates in V1 unless a later cursor/search-after design fixes it.

## Plan-doc review bundle guidance

For search endpoint plan reviews, include current task docs plus source excerpts for:

- relevant ES model(s), mapping(s), search methods, and low-level ES client write semantics;
- search message schema/types/queue profiles;
- outboxProcessor fanout handlers for create/publish/update/delete paths;
- unifiedConsumer search upsert/delete handlers;
- current route group files and any existing search-route precedent such as `/post-tag/search`;
- route/list handler excerpts that show current hydration/ACL patterns.

If reviewers suggest plan refinements and they are incorporated, regenerate the review bundle and rerun both review legs before claiming the plan-doc gate is complete.