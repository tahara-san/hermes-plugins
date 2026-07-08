# Buffdemy content-row route migration checklist

Use this when a Buffdemy backend plan moves canonical parent content fields (`title`, `body`, `papers`, etc.) out of parent documents and into content-row collections such as `articlecontents` or `articlecommentcontents`.

## Route/test migration pattern

1. Keep parent repository schemas fail-closed: parent `Article`/`ArticleComment` documents must reject/omit legacy canonical content fields.
2. Route tests that need to build PUT bodies should not read `title`/`papers` back from raw parent repository results. Instead, use either:
   - the test factory input/return value that carries resolved content for request construction, or
   - the content-row repository/collection for DB assertions.
3. It is acceptable for test factories to return a test-only object that combines the persisted parent document with the input/resolved content fields, as long as the factory does **not** write those content fields back onto the parent collection.
4. Update stale DB assertions from `doc.title` / `doc.body` / `doc.papers` to explicit checks such as:
   - parent document does not contain the removed field, and
   - the `{ parent, language/status/sourceKind }` content row contains the expected canonical content.
5. For route response media references, populate media only after resolving/merging content rows into the public response shape. If outbox/media-change detection reads pre-populated input rows, count both resolved `media` and raw `mediaId` references without using `any`.
6. For delete/soft-delete routes, verify the response uses the post-delete content contract. Do not accidentally resolve and return stale pre-delete content rows after parent status becomes `deleted`; tests should make this distinction explicit. A safe pattern is: perform the soft-delete/content-row status transition first, then build the deleted response from parent metadata plus an explicit empty resolved-content view (`title: ''`, `body: ''`, `papers: []`, no public available languages) rather than calling the normal ready-row resolver after rows have been marked deleted.
7. Delete tests should assert both sides of the split: parent metadata fields such as `status`/`tags` reflect deletion, and all matching content rows are marked `status: 'deleted'`; they should not expect removed canonical content fields to be cleared on the parent document.

## Feed/search/outbox cross-reference pattern

When the content-row split reaches feed/search/outbox callers, treat parent docs as metadata-only even if old payload names still contain `articleTitle`/`articleBody`:

1. Feed display-language filtering should use Strategy A unless the plan says otherwise: validate the requested content language, bounded-overfetch Redis refs, apply parent metadata filtering such as `availableContentLanguages`, preserve Redis order, and resolve display content through `resolveArticleContentView(s)` with `missingContent: 'skip'`.
2. Feed tests should deliberately make parent legacy fields absent or different from content-row fields so assertions prove responses are built from resolved content rows, not from parent `title`/`body`/`papers`.
3. Outbox processor search payload handlers (`published`, `propsChanged`, etc.) should fetch the parent article for status/metadata, then resolve ArticleContent rows before producing `articleTitle`, `articleBody`, `articleMediaLabels`, and `articleHasMedia`. Tests should use mismatched legacy parent content to guard against accidental parent reads.
4. Queue message schemas for generic "props changed" graph/search jobs should not derive partial payload schemas from transformed Mongo document schemas. If the runtime payload contract is arbitrary changed props, use an explicit `z.record(z.string(), z.unknown())`-style schema and keep canonical content fields out of parent-derived contracts.
5. Isolated API route tests that `mock.module('@buffdemy-backend/mongo/repositories', ...)` must include inert exports used by route dependencies imported transitively (for example outbox constants/repositories and ACL subscription/follow repositories). Missing export errors in such tests are mock-surface issues, not proof that production exports are absent.

## Pitfalls

- A build can pass while route tests are still stale because helper return types include content but raw repository reads do not. Search failing tests for `doc!.title`, `doc!.papers`, `currentArticle!.title`, and similar parent-content assertions.
- Do not “fix” stale tests by reintroducing legacy parent fields or legacy dual-read behavior. The clean-slate contract is parent metadata plus content rows.
- When a test needs the former version after an update attempt, fetch the parent repository result only for metadata such as `version`, `type`, `tags`, and status; keep request content from the test fixture/content row.
