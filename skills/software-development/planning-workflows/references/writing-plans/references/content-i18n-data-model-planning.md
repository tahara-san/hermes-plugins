# Content i18n Data-Model Planning Notes

Use this reference when planning future-proof i18n for user-authored post-like content (articles, comments, discussions, activity posts) across frontend and backend models.

## Recommended planning shape

1. Separate metadata from localized content.
   - Keep the parent document for identity, author/ACL/status/stats, publish state, and cheap denormalized language summaries.
   - Put localized display fields in a content document keyed by parent id + language.
   - Name collections by domain content type, e.g. `ArticleContent`, `ArticleCommentContent`, rather than a generic `ContentTranslation` collection when schemas differ.
2. Store both original and translated variants in the content collection.
   - `source: 'author' | 'machine' | 'manual'` or equivalent should distinguish original author rows, automatic translation rows, and manual override rows.
   - Track freshness with `contentVersion`, `sourceContentVersion`, and/or `sourceHash` so stale translations are identifiable after source edits.
3. Add parent-level language metadata, but treat it as cached/derived.
   - `originalContentLanguage`: detected/confirmed BCP-47-ish app language code.
   - `availableContentLanguages`: cheap filter cache derived from ready content rows.
   - Optional detection metadata: provider, confidence, detectedAt, sample length, manual override flag.
   - Add transaction/reconciliation rules so content-row changes cannot permanently drift from the parent caches.
4. Choose rollout mode explicitly before planning API/storage tasks.
   - **Normal incremental rollout:** preserve public API compatibility while moving storage. Resolve requested language server-side and return the existing flat response shape where practical.
   - **Explicit destructive clean-slate reset:** if the user says collections will be nuked/recreated, do not plan migration code, backfill code, legacy dual-read behavior, or tolerance for legacy document shapes. Treat new content collections as canonical from the first implemented version.
   - In both modes, add explicit metadata such as `requestedContentLanguage`, `contentLanguage`, `contentLanguageFallback`, `availableContentLanguages`, and `contentSource`.
   - Do not return all language variants on normal list/detail/feed endpoints.
5. For incremental rollout, prefer phased migration over immediate field removal.
   - Make the content collection canonical first.
   - Keep small original-language denormalized fields on the parent if existing refs, search, outbox events, or feed summaries depend on them.
   - Move heavyweight localized fields first; physically remove legacy parent fields only after all read paths and tiny refs are proven stable.
   - Skip this phased-compatibility guidance only when the plan is explicitly a destructive clean-slate reset.

## Feed/list planning pattern

For existing pre-ranked feeds backed by Redis refs or similar:

1. Overfetch candidate ids from the existing feed.
2. Fetch parent metadata filtered by status and `availableContentLanguages`.
3. Preserve original feed ordering in application code.
4. Fetch requested-language content plus original-language fallback rows in one query.
5. Merge by precedence: requested ready row -> original author row -> explicit missing/fallback behavior.
6. Bound the scan with an overfetch factor and max iterations; document that language-filtered pages may return fewer than `limit`.

## Search and cache cautions

- Decide explicitly whether search is original-language-only for the initial rollout or language-specific. Do not accidentally index every variant without ranking/dedup policy.
- Language summary fields are filters/caches, not authority. Plan a reconciliation job or admin repair path.
- Define edit-time semantics separately from storage `updatedAt`; user-visible `lastEditedAt` should not be bumped by cache-only translation metadata refreshes.

## Language detection direction

- For TypeScript services, plan an adapter interface rather than baking one detector directly into models.
- Persist detector metadata and allow manual correction/override.
- Treat short text and mixed-language text as low-confidence cases that may need fallback to user/profile/site locale or an explicit unknown language state.
- Prefer BCP-47-compatible app codes with a bounded supported-language enum for product behavior.

## Review gate

For cross-repo frontend/backend architecture plans, run an independent review after the draft, revise concrete findings, and re-review if the first review flags architectural gaps. Ask the reviewer specifically about migration blast radius, cache consistency, read-path performance, and public API compatibility.

For huge/high-risk i18n migrations, encode the review gate inside the task docs themselves, not just in chat. If the user asks for Claude Code review, make `/claude-code` mandatory for the initial `/plan-doc`, every implementation-phase review, every `/plan-code` review, and the final holistic review. Do not let Codex/Hermes/delegate review implicitly substitute for the named Claude Code gate unless the user explicitly relaxes it.
