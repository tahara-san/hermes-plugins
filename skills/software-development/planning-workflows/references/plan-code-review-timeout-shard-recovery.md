# Plan-code review timeout shard recovery

Use this when a mandatory `plan-code` Codex-style delegate review times out on a large final bundle, and follow-up sharded delegates also time out or return a mixed result.

## Pattern

1. Treat every timeout as a failed/incomplete gate, not approval.
2. Save the timeout as a durable artifact before retrying. Include:
   - delegation id;
   - reviewed bundle path;
   - status (`timeout` / no parseable verdict);
   - duration/API-call count if known;
   - exact narrower retry plan.
3. Split by coherent workstreams first. If those still time out, create **micro-bundles**:
   - one contract per bundle;
   - current source excerpts with enough context, not broad entire-repo dumps;
   - focused test excerpts that prove the contract;
   - latest verification output summary;
   - pointer to the full current final bundle for traceability;
   - no historical raw review artifacts unless the gate is artifact consistency.
4. If a sharded rerun returns mixed results (for example two timeouts and one `CHANGES_REQUIRED`):
   - save one consolidated result artifact preserving every shard status;
   - adjudicate the concrete finding against the live tree;
   - for valid blockers, add a RED regression that fails for the reviewed product reason;
   - patch minimally;
   - rerun focused GREEN plus proportional impacted suites/builds;
   - rerun simplify/static hygiene;
   - mark all earlier review attempts stale.
5. After any source/test/task-doc/review-artifact edit, regenerate the current final implementation bundle before dispatching another mandatory review.
6. Correct stale task docs immediately. If docs say the phase is complete or reviews passed but a later review timed out/failed or a post-review fix landed, uncheck completion/review rows and state the active blocker.
7. For the next review attempt, use bounded micro-shards rather than re-sending the timeout-prone broad bundle. Require parseable fail-closed JSON for every micro-shard; any timeout/failure keeps the lane blocked.

## Review artifact hygiene

- Keep historical failed/timeout artifacts for traceability, but label them superseded/stale in newer pending artifacts.
- Do not create an aggregate final-review artifact until every mandatory lane has a current passing verdict or an explicit user waiver.
- A companion reviewer being blocked by login/setup/usage limit does not satisfy or fail the Codex lane; record it separately.

## Example micro-shard scopes

For a large backend payment/cron phase:

- settlement/charge outcome classification and retry/backoff;
- Connect/API/webhook idempotency and auth boundaries;
- payout/repository recovery and atomicity.
