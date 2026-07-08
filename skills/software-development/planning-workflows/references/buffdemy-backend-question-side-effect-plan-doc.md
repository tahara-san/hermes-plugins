# Buffdemy backend Question side-effect gap-fill plan-doc pattern

Use when writing or reviewing Buffdemy backend `plan-doc` task bundles that fill Article-vs-Question creation-path side-effect gaps across Mongo, outboxProcessor, unifiedConsumer, Elasticsearch, Neo4j, and tests.

## Grouping pattern

For large Question creation parity work, split by side-effect domain instead of creating one giant task:

1. Core metadata parity: status logs, origin IP, language detection/cache initialization.
2. Mentions and notifications: mention normalization, `question.mentioned` outbox, notification fanout.
3. Search projection CRUD: Question ES model/messages/outbox fanout/unifiedConsumer handlers/stale protection.
4. Post-tag projections: global post-tag stats/search tag upserts and per-user post-tag stats/contentTags.
5. Neo4j graph projection: Question node, owner relationship, tag relationships.
6. Final outbox/test matrix: cross-cutting route outbox and handler fanout coverage after feature tasks land.

Put `spec.md`, `todo.md`, and `kickoff-prompt.md` in each task directory. Add a cross-task integration note whenever multiple tasks will touch `apps/outboxProcessor/src/handlers/question/published.ts` or `apps/outboxProcessor/src/test/handlers/question/question.test.ts`; recommend serial execution and make the final matrix task the convergence gate.

## Verification-command copy-pasteability

Reviewers should fail plan-docs when commands point to non-existent directory-style test paths. In this repo, several regression tests are flat files, so use exact paths when they exist:

- `apps/unifiedConsumer/src/test/handlers/search/article.test.ts`
- `apps/unifiedConsumer/src/test/handlers/search/postTag.test.ts`
- `apps/unifiedConsumer/src/test/handlers/mongo/postTag.test.ts`
- `apps/unifiedConsumer/src/test/handlers/mongo/userPostTagStat.test.ts`
- `apps/unifiedConsumer/src/test/handlers/neo4j/article.test.ts`
- `apps/outboxProcessor/src/test/handlers/question/question.test.ts`
- `apps/outboxProcessor/src/test/handlers/article/published.test.ts`

If the implementation will create a new test file (for example `question.test.ts` under search or neo4j), name that exact expected file path in the plan. If the implementer chooses a different file name or narrower test path, require them to record the exact final command in verification artifacts.

Add a prerequisite before Docker verification blocks: Docker Compose services must be running; if not, start the dev stack first and record setup separately from test failures.

## Known parity pitfalls to encode in specs

- Follower-publish notifications are an Article published-handler side effect but may be outside the user’s enumerated target list. Do not silently implement them inside an unrelated task; either promote them to an explicit task or mark them as a deferred matrix row with user-approved rationale.
- If an earlier task may create `apps/api/src/test/outbox/question.outbox.test.ts`, later matrix tasks should mark it `Create/modify` and explicitly preserve earlier tests, not `Create`.
- Reuse Article tag canonicalization for every Question projection path. Point implementers at `apps/outboxProcessor/src/handlers/article/tagUtils.ts` / `normalizeArticleEventTags`, or require extracting a shared equivalent. Do not let search, post-tag, and Neo4j tasks invent divergent canonicalization algorithms.
- For Question search projections, do not assume Article-like `questionVersion` / `contentVersion` fields already exist. Require implementers to verify current parent/content row fields and deliberately derive or introduce monotonic projection versions, then test the projection-version helper.
- Search and graph delete/unpublish cleanup may be conditional. Plans should require implementers to record the exact Article-parity audit decision in task notes/TODOs when those lifecycle paths are implemented or intentionally not applicable.

## Question tag-stat lifecycle parity plans

When planning Question post-tag/user-post-tag lifecycle parity against Article, separate "general user content stats" from "tag accounting". If the user says user stats are complete, do not expand scope into Article Comment or Question Answer; focus only on Article/Question tag-stat paths.

For pre-service/no-backward-compat Buffdemy backend work, encode hard payload changes rather than legacy unions:

- Add a Question tag-change event such as `question.hashtag_changed` for published -> published retags.
- Make `question.deleted` require `questionTags: string[]`; do not allow an optional legacy branch for old payloads.
- Require producers to emit canonical normalized tags in `questionTags`, `questionTagsBefore`, and `questionTagsAfter`; handlers may still normalize defensively at durable boundaries.
- For unpublish with simultaneous retag, cleanup must use pre-update tags (the tags that were counted while published), not the incoming draft tags.
- For published delete, cleanup must use pre-delete tags.
- Draft/non-published retags and deletes should not emit tag lifecycle events because publish-side counters were never incremented.

Plan-docs for this class should explicitly include these implementation gates:

1. Grep/enumerate every `QUESTION_DELETED` producer before implementation; making `questionTags` required will break any hidden emitter such as admin/account-deletion cascades.
2. Verify whether `presaveProps` includes `tags`; if not, fetch/carry the pre-save Question document explicitly so the "before" set is correct.
3. Preserve existing `QUESTION_PUBLISHED` publish-side tag fanout and add tests that cover both create-as-published and draft-to-published paths, not just retag/delete paths.
4. Live published retag should compute added/removed normalized sets; added tags increment global `postTag.stats.questionCount` and `userPostTagStat.stats.questionCount`, removed tags decrement both.
5. Live retag should update Neo4j `HAS_TAG` relationships to exactly match the new normalized tag set and refresh ready Question search content rows so indexed `tags` converge.
6. Be deliberate about `search.sendPostTagUpsert` for newly added tags during retag: Article's current hashtag-change handler may omit this, so if the Question plan includes it, mark it as an intentional correctness divergence rather than accidental Article-parity drift.
7. For search-row refresh compensation on retag, require implementers to confirm the delete-compensation semantics are safe for pre-existing rows and include exact `questionId`, `language`, `questionVersion`, and `contentVersion` fields.
8. Add a no-op route test where published Question tags are reordered/case-variant but the normalized set is unchanged, asserting no tag-change event is emitted.

## Review bundle pattern

For a multi-task plan-doc review bundle:

- Include the six task docs, package-script context, git status, scoped `git diff --check`, and a simple added-line security keyword scan.
- Exclude `reviews/` artifacts from semantic review, and state that exclusion explicitly to avoid self-referential stale-review loops.
- If a reviewer gives useful non-blocking suggestions and you patch docs, regenerate the bundle and rerun all required review legs before saving final aggregate approval.
