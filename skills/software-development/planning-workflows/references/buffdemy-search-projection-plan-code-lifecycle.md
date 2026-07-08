# Buffdemy Search Projection Plan-Code Lifecycle

Use this when executing or reviewing Buffdemy backend `plan-code` tasks that add or change Elasticsearch projections, RabbitMQ search jobs, outboxProcessor fanout, unifiedConsumer search handlers, or one-shot reconciliation/backfill commands.

## Lessons from search-projection lifecycle work

- Treat reset/backfill as an implementation gate, not just a deployment note. If reset is not explicitly chosen, implement a non-destructive reconciliation command and prove it in `--dry-run` mode.
- If a backfill command is added after a final review already passed, that review is stale. Regenerate the final bundle, rerun verification, and rerun both review legs.
- Final task docs are part of the reviewed artifact. Before final approval, remove stale wording like “decision unresolved” or “review must be rerun” once the blocker has been resolved. If final docs change after review, either rerun the full final review or run a scoped artifact-consistency review.

## Search projection reconciliation checklist

A one-shot reconciliation/backfill must converge stale search documents, not only enqueue happy-path upserts:

1. Read current Mongo source rows, not queued payload contents, as the source of truth.
2. Upsert only current `ready` content rows for visible/published parents and roots.
3. Enqueue versioned language deletes for current non-ready/stale/deleted content rows under still-published parents.
4. Enqueue a versioned parent/child delete when a published parent has no current content rows.
5. For child projections, if the root article/question is missing or no longer visible, enqueue a versioned child or root delete instead of skipping.
6. Preserve `--dry-run` so rollout can inspect counts without publishing RabbitMQ jobs.
7. Treat non-dry-run execution as an explicit deployment rollout step; it is not an implementation blocker once the command and dry-run evidence are present.

## Tests to require

- Focused command tests for ready upserts, hidden/non-visible parent deletes, dry-run no-send behavior, non-ready/stale language deletes, empty-content parent deletes, and missing-root child fallback deletes.
- Focused unifiedConsumer tests proving queued stale child upserts rebuild from current ready Mongo rows or delete candidates when current rows are non-ready/missing.
- OutboxProcessor tests proving root article/question delete/unpublish fanout includes versioned child search deletes.
- Static scan should catch `Number.MAX_SAFE_INTEGER` shortcuts; versioned deletes should use current parent/root/content versions instead.

## Review bundle notes

- Include the reconciliation script, its tests, package script, dry-run output, and review history in the final bundle.
- Exclude the bundle itself and unrelated task directories from the reviewed scope.
- If reviewers fail on backfill completeness, save the failed artifact as historical, patch the implementation/tests/docs, regenerate the bundle, and rerun reviews. Do not keep a pre-backfill or pre-fix review as the final verdict.
