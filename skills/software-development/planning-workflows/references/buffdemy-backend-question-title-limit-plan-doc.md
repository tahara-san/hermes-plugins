# Buffdemy backend Question title-limit plan-doc pattern

Use when writing or reviewing a Buffdemy backend `plan-doc` for changing Question title length or similar schema limits that affect parent rows, content rows, API write schemas, and downstream side-effect consumers.

## Source surfaces to inventory

For Question title max changes, do not stop at the API route schema. Scan and record all of these surfaces:

1. Canonical shared limit/profile:
   - `packages/mongo/src/repositories/_utils/contentLimitConstants.ts`
   - `packages/mongo/src/repositories/_utils/contentLimitHelpers.ts`
2. API write schema and create/update routes:
   - `apps/api/src/routes/_schemas/question.ts`
   - `apps/api/src/routes/question/post.ts`
   - `apps/api/src/routes/question/[question]/put.ts`
3. Parent and content-row persistence schemas:
   - `packages/mongo/src/repositories/question/schema.ts`
   - `packages/mongo/src/repositories/questionContent/questionContentSchema.ts`
4. Tests with old boundary constants or literals:
   - `apps/api/src/test/routes/question.schema.test.ts`
   - `packages/mongo/src/repositories/_utils/questionContentLimitConstants.test.ts`
   - repository/content schema tests, creating them if no focused file exists.
5. Outbox/message/consumer side effects:
   - `packages/mongo/src/repositories/outboxMessage/payloads/question/published.ts`
   - `apps/outboxProcessor/src/handlers/question/published.ts`
   - `apps/outboxProcessor/src/handlers/question/searchPayload.ts`
   - `packages/rabbitmq/src/queues/job/search/messages/schema.ts`
   - `apps/unifiedConsumer/src/handlers/search/question/upsert.ts`
6. Cron/reconciliation fixtures and hydration consumers:
   - `apps/cronWorker/src/test/jobs/expireQuestions.test.ts`
   - `apps/cronWorker/src/test/jobs/reconcileUserStats.test.ts`
   - `apps/cronWorker/src/test/jobs/reconcileReactionStats.test.ts`
   - notification summary/feed/list/list-item tests that hydrate saved Question titles.

## Planning rules

- Prefer one canonical constant (for example `QUESTION_TITLE_MAX`) and make parent/content schemas derive from it; avoid duplicating new numeric limits in implementation files.
- Keep `question.published` payload shape stable unless the task explicitly requires a payload change. Current published payloads carry IDs/timestamps; downstream processors fetch saved Question/content rows for title-bearing work.
- Treat RabbitMQ search-message title validation as an explicit decision. The default is to leave it as a generic `z.string()` if producer/content schemas enforce the domain limit and consumers may process historical messages; if tightening message validation, require RabbitMQ schema tests and producer/consumer updates.
- Include no-side-effect API rejection tests for over-limit create/update: no parent Question, QuestionContent, or outbox rows should be created/changed after validation fails.
- If a suggested test file does not exist yet, state that the implementer must create it or place equivalent assertions in the closest existing test and record the final path in verification artifacts.
- Scope simplify-gate greps carefully: unrelated existing constants such as media-control string limits may legitimately be `128`; check for stale title-boundary `280/281` assertions and duplicated title-limit literals, not every `128` in the repo.

## Verification checklist

Focused verification should include all affected services, not just API/mongo/search:

```bash
cd /home/tahara/dev/buffdemy-backend
bun test packages/mongo/src/repositories/_utils/questionContentLimitConstants.test.ts
bun test packages/mongo/src/repositories/question/questionSchema.test.ts packages/mongo/src/repositories/questionContent/questionContentSchema.test.ts
bun test apps/api/src/test/routes/question.schema.test.ts apps/api/src/test/routes/question.routes.test.ts apps/api/src/test/outbox/question.outbox.test.ts
bun test apps/outboxProcessor/src/test/handlers/question/question.test.ts apps/outboxProcessor/src/test/scripts/reconcileSearchProjections.test.ts
bun test apps/unifiedConsumer/src/test/handlers/search/question.test.ts
bun test packages/rabbitmq/src/queues/job/search/messages/schema.test.ts
bun test apps/cronWorker/src/test/jobs/expireQuestions.test.ts apps/cronWorker/src/test/jobs/reconcileUserStats.test.ts apps/cronWorker/src/test/jobs/reconcileReactionStats.test.ts
```

Package/service checks should also include `apps/cronWorker`:

```bash
cd /home/tahara/dev/buffdemy-backend/packages/mongo && bun run build && bun run test
cd /home/tahara/dev/buffdemy-backend/apps/api && bun run build && bun run test
cd /home/tahara/dev/buffdemy-backend/apps/outboxProcessor && bun run build && bun run test
cd /home/tahara/dev/buffdemy-backend/apps/unifiedConsumer && bun run build && bun run test
cd /home/tahara/dev/buffdemy-backend/packages/rabbitmq && bun run build && bun run test
cd /home/tahara/dev/buffdemy-backend/apps/cronWorker && bun run build && bun run test
```

If local package commands are unavailable but Docker services are running, use the repo's per-service `docker compose exec -w /app/<service>` form and record any setup separately from product failures.
