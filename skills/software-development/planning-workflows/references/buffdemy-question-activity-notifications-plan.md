# Buffdemy question activity notification plan-doc notes

Use when planning or reviewing Buffdemy backend/frontend notification work for Question, QuestionAnswer, or QuestionFollowUpComment activity.

## Existing pipeline to extend

Prefer the existing outbox -> outboxProcessor -> RabbitMQ notification-create -> unifiedConsumer pipeline:

1. API route emits a typed outbox message inside the write transaction.
2. `apps/outboxProcessor/src/handlers/...` validates the event and calls `messageHelper.mongo.sendNotificationCreate`.
3. `apps/unifiedConsumer/src/handlers/mongo/notification/create.ts` writes notifications, event receipts, and summaries.
4. Notification-summary API hydrates public-safe target/payload data for the frontend.

Do not bypass this with route-local direct notification writes.

## Notification event contract checklist

For each new question-family notification, plan all of these layers together:

- `packages/mongo/src/repositories/notification/notificationSchema.ts` event constant + payload schema.
- `packages/mongo/src/repositories/notificationSummary/notificationSummarySchema.ts` public summary type + payload schema.
- `packages/mongo/src/repositories/notification/notificationSummaryHelpers.ts` event -> summary mapping.
- `packages/mongo/src/repositories/notificationSummary/notificationSummaryTypes.ts` / exported payload unions.
- `packages/rabbitmq/src/queues/job/mongo/messages/schema.ts` compatibility via imported notification schema.
- `apps/unifiedConsumer/src/handlers/mongo/notification/create.ts` ObjectId flattening keys for child ids such as `questionAnswer` and `questionFollowUpComment`.
- `notificationSummaryRepository` payload-field extraction for raw payload fields such as `expiresAt`.

## Recipient safety rules

Question notification recipients must be fail-closed:

- Exclude the doer/self recipient for every fanout.
- Deduplicate per recipient after combining sources.
- Filter non-owner recipients by current question read ACL before notification-create fanout.
- Do not import API route helper modules into `outboxProcessor`; extract shared ACL filtering to package/shared code, using `evaluateQuestionReadAcl` and injected follow/subscription resolvers.
- For requested answerers, verify both negative and positive ACL behavior: denied custom-read ACL users receive no notification fanout, while a private/custom-ACL requested user who legitimately can read the question does receive the answer-request notification.

## Event-specific pitfalls

### Question answer requested

- Emit only when a question becomes published: create-as-published and draft-to-published.
- Do not re-emit on ordinary published-to-published edits.
- Named requested users only; group requested answerers are not direct notification recipients.
- Exclude rejected requested users and the question owner/doer.
- Carry `expiresAt` as a raw nonnegative millisecond timestamp; do not format prose in backend payloads.
- In summary persistence, keep `expiresAt` as a number, not `toObjectId`-coerced. Add collapse tests proving the latest deadline is retained.

### Question answered

- Notify the root question owner when a published answer is created/published.
- Skip self-answer notifications.
- Fetch/validate the current root question; fail closed if missing or no longer published.
- Existing `questionAnswer/published` fanout also updates graph/stat/search. Decide whether notification-send failure should fail the whole outbox event or be isolated from search fanout, and lock that decision with tests.

### Follow-up comment posted

- Add an outbox event for follow-up comment creation; the current direct repository write path lacks notification fanout.
- Notify the root question owner plus users who posted prior follow-up comments.
- Select prior commenters as of `questionFollowUpCommentCreatedAt`, not handler runtime; async processing must not notify users who commented after the event.
- Exclude comments with `createdAt >= questionFollowUpCommentCreatedAt` unless exact ordering is otherwise proven.
- Require the newly created follow-up comment to still be published/non-deleted at handler time.
- Filter prior commenters by current read ACL and skip those who lost access.

## Dedup and idempotency

Every notification-create job should use retry-stable per-recipient deduplication:

```ts
buildNotificationDedupId({
    outboxMessageId,
    eventType,
    eventSourceContentType,
    eventSourceContentId,
    ownedById,
});
```

Plan duplicate-delivery tests for each new fanout path to prove replaying the same outbox message does not create duplicate notifications.

## Frontend contract for question summaries

Default public summary target contract for these question-family events:

```ts
target: {
    type: 'question';
    _id: string;
    title: string;
    ownerName: string; // or a deliberately documented equivalent slug field
}
```

- Child ids such as `questionAnswer` and `questionFollowUpComment` stay in payload for optional previews/anchors.
- Frontend must not parse `summarySource` for routing/type decisions.
- If backend omits `target` because the current user can no longer read the question, frontend should render safe non-clickable fallback text.
- Treat degraded question targets carefully: schema may tolerate missing display/routing fields, but navigation must fail closed when `ownerName`/id is missing, blank, malformed, or when `target._id` and `payload.question` disagree.
- Add frontend schema/navigation/copy tests for malformed target, missing owner slug, omitted target, target/payload question-id mismatch, expired/future deadline rendering, and grouped-summary behavior.
- Deadline rendering should cover malformed/missing `expiresAt`, expired values, weeks/days/hours, and sub-hour future deadlines; never render negative time, `NaN`, or an awkward `0 hours` state.
- Prefer integer nonnegative millisecond `expiresAt` handling unless the backend contract deliberately allows fractional timestamps.
- Ensure the deadline/expired status is exposed accessibly, not only visually.
- If Japanese/product copy review is pending, still require placeholder/simple JA keys so translation-parity checks pass; record the copy review as a non-blocking product risk, not a reason to omit keys.

## Plan-doc review gotchas

When reviewing this class of plan-doc, treat these as blocker-level questions:

- Can a private requested answerer actually pass `evaluateQuestionReadAcl`, or will the planned ACL filter silently drop all intended recipients?
- Are follow-up commenters selected as-of event time rather than handler time?
- Is notification-summary target hydration ACL-aware and fail-closed?
- Are dedup IDs explicitly specified for answered/follow-up fanout, not just answer-request?
- Do verification commands point at real test files, or does implementation need to create/update those paths before final report?
