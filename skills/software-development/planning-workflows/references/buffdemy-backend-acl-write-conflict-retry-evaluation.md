# Buffdemy backend ACL write-conflict retry evaluation

Use when planning or auditing a Buffdemy backend task that proposes adding retries for MongoDB `WriteConflict`, `TransientTransactionError`, or frontend-observed ACL fixture 500s.

## Core lesson

Do not start from “add a retry loop.” First trace the exact live backend flow and prove the retry boundary is clean, idempotent, and current. A broad handler retry can duplicate setup/reset work, mask legitimate errors, or paper over a wrong transaction boundary.

## Required trace

1. Map the frontend/proxy endpoint to current backend source. Do not assume stale frontend labels such as `finalize_acl` or old `articleAclFixture` names still exist in `/workspace/dev/buffdemy-backend`.
2. Separate flows explicitly:
   - production article save: `apps/api/src/routes/article/[id]/put.ts` → `outboxHelper.withOutboxTransaction(...)` → `articleRepository.updateWithOwnershipCheck(...)`;
   - current test-only fixture flows such as `apps/api/src/routes/testOnly/questionAclFixture/`;
   - older or missing frontend task-note labels that cannot be mapped to current backend code.
3. Inspect the transaction helper (`packages/mongo/src/client/index.ts`) and route/repository code for where Mongo errors are caught and wrapped.
4. Inspect side effects inside the retry candidate: outbox messages, content rows, notifications, feed/search/stat updates, fixture reset/delete/create operations, timestamps, random IDs, and external calls.

## AppError / Mongo retry-label pitfall

`AppError` preserves the raw error as `cause` / debug content, but it does not preserve Mongo driver's retry-label methods. If a `WriteConflict` is caught and wrapped as `AppError` inside a `session.withTransaction(...)` callback before escaping, the driver may not recognize it as retryable. The fix may be to let raw transient Mongo errors escape to the driver, not to add another outer loop.

## Boundary guidance

- Production article PUT ACL/save flow is already structurally transaction-scoped: read existing article, evaluate ACL, `formerVersion` optimistic concurrency check, article/content writes, derived-row stale marking, and outbox emits happen inside `withOutboxTransaction`. Avoid adding a second broad retry around this route unless evidence shows the driver retry is being defeated or exhausted.
- If a `formerVersion` mismatch appears after a retry/re-read, it should remain a legitimate `409`, not be hidden by retrying the whole API handler.
- Test-only fixture flows often include non-transactional reset/setup/delete/create steps around transaction-wrapped repository calls. Clean or serialize those boundaries first. Whole-handler retry can re-run resets and increase contention.
- If retry remains necessary after cleanup, keep it narrow: bounded attempts, jittered backoff, retry only Mongo transient/write-conflict signals, and only around proven-idempotent single statements or the minimal transaction callback. Never retry broad handlers that include external calls or fixture resets unless the whole flow is designed for replay.

## Plan-doc replacement pattern

When a draft task directory was created around the unsafe assumption “add a retry loop,” prefer replacing it with a new boundary-audit task instead of patching the misleading slug in place. If the user explicitly asks to remove the old task directly, delete only that directory and create a replacement such as `tasks/backend-acl-write-conflict-boundary-audit/` with:

- `spec.md` stating the old retry-led task is superseded and that implementation must fail closed until the live backend path is mapped;
- `todo.md` stop-gates for stale/missing backend labels, broad whole-handler retry without idempotency proof, and fixture-only vs production scope decisions;
- `notes.md` as the required Phase 0 evidence artifact before backend edits, including endpoint mapping, serving checkout, symbol-search results, production-vs-fixture decision, backend test runner, and whether the frontend helper's no-partial-commit comment was validated or corrected.

For plan-doc review, build a final bundle that includes untracked `spec.md`/`todo.md`/`notes.md`, frontend helper/source issue excerpts, backend symbol-search summary, frontend/backend git status, package scripts, and a lightweight secret scan. If an initial reviewer approval returns useful non-blocking refinements and you adopt them, mark that review superseded, regenerate the bundle, and rerun both required review legs. If the interactive Codex TUI verdict has not returned, save a pending artifact with the tmux session, final bundle path/hash, current raw pane capture, completed Claude artifact, and exact resume steps instead of creating an aggregate plan-review verdict.

## Implementation pattern: frontend stage label reaches production PUT

If the observed label (for example `finalize_acl`) is not found in the backend, inspect the frontend test-only route before declaring the issue stale. In `buffdemy2-web`, `/api/test-only/article-acl-fixture` can be implemented in the frontend app and use labels like `withFixtureStage('finalize_acl', ...)` around calls to backend production routes such as `PUT /article/:id`. In that case the correct backend scope is the production article update transaction, not a missing backend fixture route.

For production article update retry-label fixes, prefer preserving raw Mongo retryable errors at the narrow catch boundary inside the transaction callback over adding an outer retry loop. A concrete pattern from `/workspace/dev/buffdemy-backend`:

- `apps/api/src/routes/article/[id]/put.ts` calls `outboxHelper.withOutboxTransaction(...)`.
- `apps/api/src/routes/article/_libs/update/updateDocument/updateDocument.ts` calls `articleRepository.updateWithOwnershipCheck(...)` inside that callback.
- If `updateDocument()` catches repository errors and wraps them in `AppError(article_update_failed)` before rethrowing, Mongo driver's `session.withTransaction(...)` may not see `hasErrorLabel()` and may not retry.
- Fix narrowly by rethrowing raw retryable/write-conflict candidates before AppError wrapping (for example `hasErrorLabel('TransientTransactionError')`, `hasErrorLabel('UnknownTransactionCommitResult')`, `code === 112`, or `codeName === 'WriteConflict'`). Keep ACL-denial and ordinary-error behavior unchanged.
- Add RED/GREEN unit coverage for both the raw retryable escape and ordinary error wrapping. If time allows, separately exercise fallback branches (`code === 112`, `codeName === 'WriteConflict'`, `UnknownTransactionCommitResult`) instead of bundling every signal into one mocked error.

## Tests to require

- Concurrent fixture setup/reset stress reproduces the old failure and then passes without raw `WriteConflict` 500s when the failing path is fixture-only.
- Shared fixture users converge to one row per email under parallel setup when the failing path is fixture-only.
- Forced transient transaction error inside the transaction produces one logical set of durable side effects and no duplicate outbox messages.
- For production article update retry-label fixes, a focused unit/integration test proves retry-label-bearing Mongo errors escape unwrapped from the in-transaction catch boundary, while ordinary repository errors, ACL denials, and `formerVersion` mismatches still surface unchanged.
- Run the existing article update/outbox suite (or equivalent live-path regression) to prove no duplicate outbox messages or side-effect regressions.
- If frontend helper retries are retained, document why they remain test-harness resilience rather than production behavior, and correct comments that imply a broad backend retry exists when the actual fix is driver-level transaction retry-label preservation.
