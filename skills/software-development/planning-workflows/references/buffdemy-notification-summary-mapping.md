# Buffdemy notification summary mapping refactor notes

Use when planning or implementing Buffdemy notification summary key cleanup across `buffdemy2-web` and `buffdemy-backend`.

## Correct backend repo

The active backend for the V2 web notification summary contract is:

```text
/workspace/dev/buffdemy-backend
```

Do **not** use `/workspace/dev/buffdemy2-api` as evidence for this class of work unless the user explicitly asks about the legacy backend.

## Key backend files

```text
packages/mongo/src/repositories/notification/notificationSchema.ts
packages/mongo/src/repositories/notificationSummary/notificationSummarySchema.ts
packages/mongo/src/repositories/notificationSummary/notificationSummaryRepository.ts
apps/unifiedConsumer/src/handlers/mongo/notification/utils.ts
apps/unifiedConsumer/src/handlers/mongo/notification/create.ts
apps/api/src/routes/notificationSummary/index.ts
apps/outboxProcessor/src/handlers/article/published.ts
apps/outboxProcessor/src/handlers/articleComment/published.ts
apps/outboxProcessor/src/handlers/reaction/created.ts
apps/outboxProcessor/src/handlers/listItem/created.ts
apps/api/src/test/routes/notificationSummary.test.ts
apps/unifiedConsumer/src/test/handlers/mongo/notification.test.ts
```

## Current shape

Event types in `notificationSchema.ts` are already mostly clear:

```text
article.published
article.commented
article.reacted
article.added_to_list
article_comment.commented
article_comment.reacted
article_comment.added_to_list
user.followed
```

The confusing layer is `notificationSummarySchema.ts`:

```text
article.publishes
article.article
article.article_comment
article.list_adds
article_comment.article
article_comment.article_comment
article_comment.list_adds
user.follows
```

`apps/unifiedConsumer/src/handlers/mongo/notification/utils.ts` maps event types to those legacy summary types, and `apps/api/src/routes/notificationSummary/index.ts` currently emits stored `summaryType` values verbatim.

## Preferred public canonical mapping

The user's preferred format is target-first:

```text
<targetContentType>.<actionType>
```

Recommended public keys:

| Legacy summary type | Canonical public key |
| --- | --- |
| `article.publishes` | `article.publish` |
| `article.article` | `article.comment` |
| `article.article_comment` | `article.react` |
| `article.list_adds` | `article.listAdd` |
| `article_comment.article` | `articleComment.comment` |
| `article_comment.article_comment` | `articleComment.react` |
| `article_comment.list_adds` | `articleComment.listAdd` |
| `user.follows` | `user.follow` |

Use `articleComment` in public/frontend keys unless the user chooses `article_comment`, because the backend API target hydration already emits `type: 'articleComment'`.

## Migration vs pre-service reset decision

Before planning implementation, ask/confirm whether Buffdemy is still pre-service for notification data.

### If pre-service reset is allowed (current user preference)

Use a no-compatibility reset plan:

- replace `SUMMARY_TYPES` values at the source with canonical keys;
- update backend/frontend tests and fixtures to canonical keys only;
- reject old values such as `article.article`, `article_comment.article`, `article.list_adds`, and `user.follows`;
- do **not** add legacy alias maps;
- do **not** add dual-accept query parsing;
- do **not** add frontend legacy normalization;
- do **not** write a historical Mongo migration script;
- flush existing notification state and regenerate through normal app flows.

Collections identified from the repositories:

```text
notifications
notificationsummaries
```

Deletion must still be environment-gated: confirm the target dev database before flushing, record the exact command/output, and never guess a production connection string.

### If production/backward compatibility is required later

Use a staged compatibility plan instead:

- keep Mongo persisted legacy summary types initially;
- add API mapping helpers `toPublicSummaryType`, `toStorageSummaryType`, `isPublicSummaryType`;
- responses emit canonical public keys only after frontend dual-accept has shipped or behind a compatibility gate;
- queries accept canonical and legacy keys during rollout, down-converting canonical to storage keys;
- frontend normalizes legacy aliases defensively during rollout.

Only do a storage migration after explicit approval.

## Quick-content payload gotcha

For article comments, the outbox producer already sends the created comment ID:

```ts
payload: { article: articleId, comment: articleCommentId, doer: articleCommentOwnedById }
```

But current summary persistence stores only `payload.article` for legacy `ARTICLE_COMMENTS`. To let `article.comment` preview the comment body, persist a public-safe comment id such as:

```ts
payload.articleComment = payload.articleComment ?? payload.comment
```

Keep old rows fail-closed when `payload.articleComment` is missing; do not infer comment body from article id or notification text.

For replies (`articleComment.comment`), distinguish target/navigation from preview source: existing payload has `parentComment` and `createdComment`; preview should use the created reply body while navigation may point to the parent/thread. In the canonical reset implementation, keep parent/thread navigation in `payload.articleComment` and preview `payload.createdComment`.

## Frontend quick-content fail-closed requirements

When implementing the frontend side, verify these as contract tests rather than relying on visual smoke alone:

- schema accepts the eight canonical keys only and rejects legacy keys;
- no frontend code parses `summarySource` for type decisions;
- `article.comment` derives `/api/article-comment?id=<payload.articleComment>` from the payload, not from `payload.article` or `target._id`;
- `articleComment.comment` previews `payload.createdComment`;
- quick content fails closed for missing/malformed/stale IDs, wrong-ID responses, non-ok responses, malformed payloads, multi-item payloads, blank bodies, and fetch errors;
- failures render no preview, no fake fallback text, no user-visible error UI, and no retry loop.

Implementation pitfall: after removing Article-body quick-content expectations, check for dead `kind: 'article'` branches. If every supported preview fetch uses `/api/article-comment`, delete unreachable article-fetch code or record it as non-blocking cleanup.

## Plan-code review freshness pattern

For this class of multi-repo notification refactor, treat Claude Code Fable 5 @ xhigh effort review as stale after any post-review source, test, fixture, task note, or review artifact change. If late test cleanup occurs after approval, rerun focused frontend verification, rebuild the implementation-review bundle, and refresh the Claude Code Fable 5 @ xhigh effort review artifact before final signoff. After saving the final review artifact and checking off TODO rows, run one final read-only artifact-consistency check scoped to task docs/review artifacts to avoid self-referential stale-review loops.
