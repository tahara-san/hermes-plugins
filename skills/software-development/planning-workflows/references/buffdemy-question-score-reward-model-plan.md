# Buffdemy Question score/reward model planning notes

Use when planning Buffdemy backend/frontend work that changes `Question` / `QuestionAnswer` scoring, rewards, reactions, or list-save support.

## Current shape to verify first

- Backend `Question` already has `score`, `stats`, and `reward` (`packages/mongo/src/repositories/question/schema.ts`). Current `stats` is only `{ buffCount, answerCount }`; `score` exists but is not updated by the current stat pipeline.
- Backend `QuestionAnswer` already has Article-like engagement stats plus ranking (`stats: { reactionCount, reactionWeight, commentCount, listCount }`, `rank`), but no `score` / `rewardScore` parity field.
- `Reaction` currently supports storage targets `article`, `articleComment`, `question`, `questionAnswer`; guards allow `question + buff` and `questionAnswer + like`, but not `question + like` or `questionAnswer + buff`.
- Backend `ListItem` currently accepts only `article | articleComment` in schema/routes/target verifier/population, even if frontend schemas or components mention question-like targets. Treat that as a contract gap, not as completed support.
- Frontend Question models already mirror `score`, `stats`, `reward`; Question view actionbar uses `stats.buffCount` and already renders `ListButton targetContentType="question"`.
- Frontend QuestionAnswer entry currently renders Like + Copy only; adding list-save belongs in `src/components/content/question/components/threadEntry/threadEntry.tsx` after backend supports `questionAnswer` list items.

## Planning rule

Do not plan score fields as a UI-only/frontend-only change. The existing backend is event-driven:

1. API writes create outbox messages.
2. `apps/outboxProcessor` turns outbox events into Mongo stat jobs.
3. `apps/unifiedConsumer` applies stat updates through repository methods.
4. Repository methods update denormalized stats/rank/score.

A valid plan must update all boundaries, plus tests for created/updated/deleted deltas.

## Recommended data contract

Keep paid and non-paid effects separate:

- **Action ranking**: non-paid engagement (question likes, answers, question list saves, answer likes, answer list saves) plus any explicitly accepted paid-rank contribution.
- **Reward/Buff totals**: payment-backed Buff/tip/reward amounts (owner-funded reward, crowdfunding, answer gratuity).
- **Raw stats**: denormalized counters/weights used for reconciliation, sort, and display.

Default to preserving the existing `rank` concept for sorting. If the user explicitly says to remove post `score` fields and use `rank`, do **not** plan new `score`, `actionScore`, `rewardScore`, `scoreBreakdown`, or compatibility aliases. Use a compact pre-service contract instead:

```ts
type QuestionDocument = {
  rank: number;
  reward: number; // total paid Buff amount
  stats: {
    likeCount: number;
    likeWeight: number;
    listCount: number;
    answerCount: number;
    answerLikeCount: number;
    answerLikeWeight: number;
    answerListCount: number;
    buffCount: number;
    buffWeight: number;
    ownerBuffCount: number;
    ownerBuffWeight: number;
    communityBuffCount: number;
    communityBuffWeight: number;
  };
};

type QuestionAnswerDocument = {
  rank: number;
  reward: number; // answer gratuity Buff amount
  stats: {
    likeCount: number;
    likeWeight: number;
    listCount: number;
    buffCount: number;
    buffWeight: number;
  };
};
```

If backward compatibility is required, add explicit migration/dual-shape gates. If the user says the feature is pre-service and DB reset is acceptable, remove old-shape compatibility at every boundary instead of preserving stale `score` / object-shaped `reward` / `reactionCount` fields.

## Payment/reward pitfall

Do not use toggleable `Reaction` rows as the source of truth for paid rewards. Payment-backed rewards need an immutable ledger such as `rewardContributions` with target, payer, amount, currency, kind, payment status, and payment reference. Reactions may mirror/display a paid contribution, but payment totals must aggregate from captured ledger rows.

## Propagation rules to capture in the spec

- Direct Question like/list-save updates Question action stats and rank.
- Publishing a QuestionAnswer updates parent Question `answerCount` plus the answer's current visible like/list snapshot; deleting or unpublishing a published answer must reverse that snapshot. Exclude answer Buffs from parent Question reward/rank unless the product explicitly says otherwise.
- QuestionAnswer like updates QuestionAnswer stats/rank/action score and parent Question answer-reaction stats/action score only while the answer is published/visible; visibility transitions are handled by the publish/unpublish/delete snapshot cascade.
- QuestionAnswer list-save updates QuestionAnswer list stats/action score and parent Question answer-list-save stats/action score only while the answer is published/visible.
- QuestionAnswer gratuity should normally stay on the answer; if the product wants parent aggregation, expose it as a separate parent aggregate, not mixed with the Question reward pool.
- Paid Buff writes should be atomic: validate target/read privilege first, then debit wallet, write a negative ledger spend row, mutate/display the Reaction row if used, and enqueue outbox/stat work in the same transaction. Treat each successful Buff POST as additive unless an idempotency-key requirement is explicitly added.
- If Reaction rows are cumulative per user/target/type, stat fanout and reconciliation must use **per-transaction deltas** or immutable ledger rows for paid Buff count/amount; never use the cumulative Reaction weight as the Buff stat delta.

## Backend file families to include

- Mongo schemas/types/repositories for `question`, `questionAnswer`, `reaction`, `listItem`, and any wallet/ledger repositories used for paid Buffs.
- API routes and response builders: `reaction`, `listItem`, `question/_libs/response.ts`, `questionAnswer/_libs/response.ts`, and wallet routes if Buff spending is in scope.
- `apps/api/src/libs/targetContentHelper/targetContentHelper.ts` for list-item target verification.
- Outbox handlers for reaction and list-item create/update/delete.
- UnifiedConsumer Mongo stat handlers for question and questionAnswer.
- RabbitMQ Mongo stat message schemas derive from Mongo stat schemas, but handlers still need explicit root-question propagation logic.
- **CronWorker reconciliation is mandatory when stats/reward/rank shape changes.** Include `apps/cronWorker/src/jobs/reconcileReactionStats/reconcileReactionStats.ts` and its tests whenever Question/QuestionAnswer reaction fields are renamed or paid Buff totals move to a ledger. Current cron reconciliation covers `article`, `articleComment`, `question`, and `questionAnswer`; if left stale it can build-break or silently clobber new `reward` / `buffWeight` / owner-community fields.
- `reconcileListStats` currently reconciles `list.stats.contentCount`, not target-content `listCount`; explicitly decide whether target list-count and answer-rollup reconciliation stay event-driven or become new reconciliation scope.

## Frontend file families to include

- Base/client/server model schemas for Question and QuestionAnswer.
- `src/components/content/question/question.tsx` for Question actionbar/metadata display.
- `src/components/content/question/components/actionbar/actionbar.tsx` for direct Question actions.
- `src/components/content/question/components/threadEntry/threadEntry.tsx` for QuestionAnswer actionbar.
- `src/components/common/listButton/listButton.tsx` only if target type typing needs to change.
- i18n keys under question/questionAnswer translations.

## Clarification gates

Ask these before freezing the plan:

1. Should paid rewards influence discovery/ranking, or only display/payment? Default recommendation: display/payment only.
2. Should Question support normal non-paid likes in addition to Buffs?
3. Should direct Question list saves count in Question action score?
4. Should QuestionAnswer gratuity roll up to parent Question, or remain answer-only?
5. Is this pre-service/no-compat with reset/reconciliation allowed, or does it require migration/dual-shape compatibility?
