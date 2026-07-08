# Buffdemy backend: multilingual Article Elasticsearch data-model planning

Use when planning or reviewing Buffdemy backend Article search/indexing changes after the Mongo split from single-document `Article` to `Article` + `ArticleContent`.

## Current-state pitfall

The legacy ES Article model indexes one flattened document per Article in `articles`, with `title`/`body` resolved from the original ready content row. It is not multilingual-aware.

## Preferred v1 target model

Prefer **one ES document per published-ready ArticleContent language row** rather than one Article doc with nested multilingual `contents[]`.

Recommended identity:

- concrete index: `article-contents-v1`
- write/read alias: `article-contents`
- ES `_id`: `${articleId}:${language}`

Minimal source fields:

- `articleId` keyword
- `articleContentId` keyword
- `language` keyword
- `originalContentLanguage` keyword
- `title` text + keyword subfield
- `body` text
- `ownedById` keyword
- `tags` keyword
- `type` keyword, if article type is needed for filtering/ranking
- `hasMedia` boolean, if media filtering/ranking is needed
- `createdAt` date
- `publishedAt` date, if recency sorting uses publish time

Defer/hydrate from Mongo unless a concrete search/filter requirement needs them:

- `availableContentLanguages` — parent-level cache; denormalizing it makes a new translation require fanout updates to existing language docs.
- `mediaLabels` — add only if search/filter uses labels.
- `searchVisibility` — do not invent an ES-only ACL discriminator; Mongo remains ACL source of truth.
- `status` — usually constant because only published rows are indexed.

## Why not nested `contents[]` under one Article doc?

Nested contents preserve one ES doc per Article, but they move complexity into query/update/scoring:

- normal object arrays lose field pairing unless mapped as `nested`.
- language-specific search needs nested queries and `inner_hits`.
- per-language title/body updates require scripted nested updates or whole-parent rebuilds.
- analyzer strategy becomes harder because all languages share nested field mappings unless you add more subfield complexity.

Per-language docs keep the searchable unit aligned with the source `ArticleContent` row. The API can still return one Article by collapsing/deduping on `articleId` and then hydrating from Mongo.

## Update model

Normal operations should be deterministic by ID where possible:

- ArticleContent title/body row changed: upsert one doc by `${articleId}:${language}`.
- Translation becomes ready: upsert one doc.
- Translation deleted/not-ready: delete one doc by `${articleId}:${language}`.
- Article metadata changed (`tags`, `type`, `hasMedia`, etc.): prefer bulk-by-known-IDs after enumerating ready content languages; reserve `update_by_query` for reconciliation/drift repair.
- Article unpublished/deleted: prefer bulk delete by known language IDs; reserve `delete_by_query` by `articleId` for reconciliation/orphan cleanup.

## Required design gates before creating the index

1. **Analyzer strategy:** do not blindly keep `standard`. Buffdemy is multilingual/Japanese-facing; decide whether to use language-specific analyzers, ICU, Kuromoji, or an explicit v1 compromise. Mapping/analyzer changes require reindex.
2. **Alias support:** code should target alias `article-contents`, not concrete `article-contents-v1`, so future reindex can alias-flip.
3. **Stale event protection:** outbox/retry delivery can be out of order. Plan external versioning or another monotonic stale-write guard using Article/ArticleContent version fields so stale upserts do not clobber newer rows or resurrect unpublished/deleted docs.
4. **ACL safety:** ES is candidate retrieval only. Hydrate through Mongo and enforce canonical ACL before returning results. Avoid pre-ACL snippets/highlights or counts that leak restricted content.
5. **Backfill + drift reconciliation:** include a backfill path and a reconciliation job/query for orphan/missing ES docs.
6. **Collapse semantics:** if querying per-language docs but returning Articles, account for collapse-by-`articleId`, language preference tie-breaks, and article-count pagination/total semantics.

## Versioning pitfalls found during implementation review

When implementing stale-write protection for ArticleContent ES docs, test with **real Buffdemy version scales**, not toy integers. `Article.version` is timestamp-scale (`Date.now()` / monotonic millisecond values), so packed formulas such as `articleVersion * 1_000_000_000 + contentVersion` can overflow JavaScript safe integers and break Elasticsearch external version writes. Prefer a safe monotonic projection revision strategy and add tests using timestamp-scale article/content versions.

Keep the effective ES version source consistent across all fanout paths for the same `{articleId, language}` doc:

- If article-level metadata fanout upserts with the current parent `Article.version`, then ArticleContent lifecycle deletes/stale transitions and compensation deletes must use an equal-or-newer effective article version too (for example `max(payload.articleVersion, currentParentArticle.version)`), not a stale `ArticleContent.articleVersion` copied from the row.
- Ready/non-ready/deleted ArticleContent transitions that affect index inclusion should bump `contentVersion` or otherwise advance the projection version; same-version ready→stale or stale→ready messages can become last-writer-wins under `external_gte`.
- Compensation deletes must use the same effective version as the corresponding upsert payload, not a lower raw content-row version.
- Treat stale lower-version ES conflicts deliberately. In at-least-once/out-of-order consumers, lower-version upsert/delete conflicts are often stale no-op successes, not retryable poison messages; add focused tests for that behavior if chosen.
- Repository helpers such as `softDeleteByArticle` either need lifecycle outbox/version handling for affected content rows or must be explicitly documented/enforced as parent-delete-only convergence paths.

Useful regression tests:

- parent metadata update indexes with current parent version while content row has older `articleVersion`;
- content-row stale/delete after that metadata fanout removes or no-ops correctly under external versioning;
- compensation delete uses the same effective version as the upsert;
- parent delete-by-query skips docs with `articleVersion` greater than the event;
- timestamp-scale versions stay within JS safe integer limits.

## Review lesson

A Claude Code second-opinion review approved the per-language direction with changes: remove speculative `searchVisibility`, defer parent/cache fields, use aliases, decide analyzers up front, add stale-write versioning, and prefer deterministic bulk-by-id fanout over normal `*_by_query` fanout.
