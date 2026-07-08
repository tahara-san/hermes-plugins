# Buffdemy backend search-projection plan-doc pattern

Use when writing or reviewing a Buffdemy backend `plan-doc` for Elasticsearch/search projections derived from Mongo source documents, especially when a source model splits into child/content rows.

## Defaults for pre-service projection rewrites

When the user says the product is pre-service and data can be nuked:

- Do **not** plan backward compatibility, dual-read/write, or old-index migration/backfill unless explicitly requested.
- State the no-compat/no-migration constraint in `spec.md`, `todo.md`, acceptance criteria, and kickoff prompt.
- Treat new by-query cleanup for the new projection as runtime convergence, not legacy migration; name that distinction explicitly.

## Endpoint readiness gate

When the user asks whether an Elasticsearch-backed search endpoint can be implemented, do not stop at projection/model existence. Use `references/buffdemy-backend-search-endpoint-readiness-plan-doc.md` to classify each resource across ES model/index, RabbitMQ search schema/queue, outboxProcessor fanout, unifiedConsumer search handlers, API route/hydration, and backfill/reset needs. In particular, distinguish "ES docs exist" from "create/update/delete write paths actually keep the index current" and from "the API contract has all required indexed fields."

## Projection design checklist

- Choose the projection cardinality explicitly: e.g. one ES document per content-language row vs one parent doc with nested content.
- Define deterministic `_id` and every identity field stored in `_source`.
- Keep the v1 field set minimal. Do not invent visibility/ACL fields without a Mongo source of truth; hydrate/enforce ACL from Mongo.
- If using an alias, distinguish runtime alias from concrete index in the plan:
  1. Create concrete index, e.g. `article-contents-v1`.
  2. Ensure alias, e.g. `article-contents`, points to it.
  3. Runtime upsert/delete/search targets the alias.
  4. Tests assert setup uses concrete index and operations use alias.
- Decide analyzer strategy before index creation. If plugins (kuromoji/ICU) are not installed, it is acceptable to choose `standard` for v1 only if the plan documents the CJK/Japanese quality limitation and alias-backed reindex path.

## Endpoint readiness audit checklist

Before planning an Elasticsearch-backed search endpoint, do **not** equate an existing collection/list route or a Mongo prefix filter with a real search endpoint. For Buffdemy V1 search, a route like `GET /user?q=...` is not search-ready when the product needs partial/fuzzy/multi-word ES matching.

For each target element, classify readiness across all of these layers and report the matrix before writing implementation phases:

1. **ES model/index:** model exists under `packages/elasticsearch/src/models`, has a mapping for all required query/filter fields, and stores discriminator fields such as `role` when the endpoint is semantically narrower than the model (for example creator search via user docs).
2. **Search message schema/types:** `packages/rabbitmq/src/queues/job/search/messages/*` supports upsert/delete payloads for the element.
3. **Search queue profile/helper:** queue profiles and outboxProcessor `messageHelper.search.*` helpers can publish the element's search jobs.
4. **OutboxProcessor fanout:** publish/create, props/content changed, unpublish/delete handlers send search jobs for the element.
5. **UnifiedConsumer handler:** `apps/unifiedConsumer/src/handlers/search/<element>/` actually upserts/deletes ES docs.
6. **Write-path event emission:** API/repository write paths create the outbox events on create/publish, update, unpublish, and delete. Watch for a publish-only path with no props/content-changed event for already-published updates.
7. **Write semantics:** if the ES client uses full-document `index()` replacement, partial update fanout is unsafe unless the handler fetches/builds a full canonical search document or switches deliberately to merge/update semantics.
8. **API hydration/ACL:** the endpoint must treat ES as candidate retrieval only; hydrate from Mongo and enforce canonical status/ACL before returning data.

Call out each element as one of: `route-only ready`, `projection exists but lifecycle incomplete`, `projection missing`, or `projection unsafe until fixed`.

## Lifecycle and convergence checklist

Do not plan only parent-level publish/update/delete events when the projection unit is a child/content row. Require normal write-path events for:

- content row becomes ready -> upsert one row doc;
- ready content row changes -> upsert one row doc;
- content row becomes non-ready/error/deleted -> delete one row doc;
- parent metadata changes -> enumerate current ready rows and bulk upsert deterministic docs;
- parent unpublish/delete -> by-parent deletion that does not depend on enumerating ready rows after they may be gone.

If the current repository only has batch lookup by known languages/ids, require a method like `findReadyByArticle(article, session?)` that lists ready child rows without a pre-known language list.

### Child projections under a root source

For projections whose searchable child is also governed by a separate root resource (for example article-comment content under a root article, or question-answer content under a root question), plan both child lifecycle and root lifecycle explicitly:

- Child publish/content-change upserts must fetch and validate both the child parent and root source before indexing.
- Every child upsert path must stamp the current root version in the ES document, not only root visible-again/rebuild paths.
- Root no-longer-visible events (root unpublish/delete/etc.) must enqueue version-guarded by-root deletes for child projection docs.
- Root visible-again events (root publish/republish/etc.) must enumerate currently published children and ready child content rows, then enqueue upserts to restore child projection docs that may have been removed by a prior root delete.
- Child delete events must define a real version source before claiming version-guarded deletes. If existing child unpublish/delete payloads lack the child version, require extending the payload producers/schemas or re-fetching a current/last-known child version in the fanout handler. Do not use `Number.MAX_SAFE_INTEGER` or other unbounded shortcuts for new child projection cleanup.
- Keep the child projection version based on child-parent version + content version unless the ordering model is deliberately redesigned and tested. Treat root version as source-state metadata for guarded root deletes and visible-again convergence, not something to casually fold into the external version.

Plan tests for stale root delete after newer root republish, root republish restoring child docs, version-sourced child deletes, and root-version-stamped child upserts.

### Implementation pitfalls observed in search-projection lifecycle work

When moving from plan-doc to plan-code for these projections, encode the following as explicit tasks/tests rather than relying on broad build failures to reveal them:

- Existing delete/unpublish outbox payloads may be missing the child/root version needed by new guarded cleanup. Patch payload schemas, all API/repository producers, and stale test fixtures together; otherwise handlers will compile against required fields that some producers never send.
- Preserve repository-level lifecycle guards while allowing route-level lifecycle operations deliberately. If a route already owns a transition such as published -> draft and emits deletion fanout, add a narrowly named internal option to that repository call rather than weakening the default repository contract.
- Content-row repositories are often tested directly with synthetic parent IDs. If new content-change outbox emission fetches parent/root documents, treat a missing parent/root as “skip outbox emission” for direct orphan/synthetic writes while still throwing on actual fetch errors.
- For Bun test suites with module-level mocks, verify touched handlers with focused tests in addition to package builds. Cross-file mock contamination can make broad search-handler batches fail even when the individual handler test passes; capture the focused command/result separately and do not mask real production import errors.
- When adding new message-helper methods, extend central test mocks/preloads in the same change (`messageHelper.search.*`, repository mocks, ready-row schema mocks), or unrelated handler tests can fail because the fanout path now calls an undefined mock.

## Version and race checklist

Search projections fed by outbox/RabbitMQ are at-least-once and can arrive out of order. Plans should require:

- a concrete projection version helper based on existing monotonic source fields;
- safe-integer/bounds assertions for any combined version number;
- ES client/model support for `version` / `version_type` on single and bulk operations;
- tests that stale lower-version events cannot clobber newer docs.

For parent delete-by-query, avoid unguarded deletes when stale parent events are possible. Store queryable version fields in `_source` and guard deletes, for example:

```text
term articleId = event.articleId
range articleVersion <= event.articleVersion
```

Also handle the opposite race: a stale content-row upsert after parent delete can recreate a candidate because delete-by-query leaves no per-id tombstone. Require consumer-side current-parent validation before upsert; if the parent is not currently published, skip upsert and converge/delete instead. Future search hydration still enforces source-of-truth status/ACL, but the indexer should not knowingly resurrect unpublished/deleted candidates.

## Route shape for search endpoints

Prefer resource-local search routes in this backend unless the user explicitly asks for a central search router:

- `GET /article/search`
- `GET /article-comment/search`
- `GET /question/search`
- `GET /question-answer/search`
- `GET /user/search`

This matches the existing resource-centric route tree and the precedent `GET /post-tag/search`. A central `/search/<element>` group is usually less consistent with this repo because route files, OpenAPI tags, auth presets, and hydration logic already live under each resource domain.

For new V1 search APIs, prefer a consistent multi-word-compatible text parameter such as `q` plus standard pagination (`limit`, `skip`) unless an existing route contract forces `key`. The ES query should handle multiple words via `multi_match`/equivalent rather than anchored prefix-only Mongo filters.

## Review-bundle pitfalls

- Include current task docs plus source excerpts for current search model, ES client/init, RabbitMQ schemas, outbox handlers, consumer handlers, repository schemas, and child-row repository methods.
- Initial review blockers often identify missing child-row lifecycle events, unsafe enumeration after delete, or missing alias/version client support. Patch docs and rerun both plan-doc review legs until final artifacts reference the latest bundle.
- If a reviewer approves with non-blocking suggestions that clarify plan semantics, patch them and rerun; save earlier approvals as superseded rather than final.
