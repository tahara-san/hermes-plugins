# Buffdemy MongoDB session-safe bulk-write refactors

Use this when a Buffdemy backend plan touches repository methods that fan out multiple MongoDB operations, especially through `Promise.all()` with an optional `ClientSession`.

## Durable lessons

- MongoDB `ClientSession` should not be shared across concurrent operations. Prefer one MongoDB command (`bulkWrite`, `updateMany`, aggregation, etc.) or a sequential path when a session is involved.
- For repository reorder-style operations, `bulkWrite()` can be a cleaner caller-agnostic fix than branching between parallel non-session behavior and sequential session behavior.
- Do not call `collection.bulkWrite([])`; return early for an empty operation list.
- First classify the semantic boundary. If the endpoint/repository contract is all-or-none, use `matchedCount` for existence/race checks and do not use `modifiedCount` when an update may be a no-op because the requested value is already present. If the plan/user explicitly chooses best-effort cosmetic semantics, do not validate `matchedCount`/`modifiedCount`; document the intentional no-validation choice with a short ADR-style comment.
- Preserve existing no-write semantics when the current implementation pre-validates all items before writing and the plan does not change that contract. A pure `bulkWrite` followed by `matchedCount` can partially update valid rows and then throw if another requested row is missing/deleted. Keep a session-aware validation read when the existing behavior rejects static invalid input before writes.
- Pass the optional `session` to both validation reads and writes. For best-effort paths with no validation read, pass it to the write command.
- Explicitly type bulk operations with MongoDB type-only imports such as `AnyBulkWriteOperation<TDocument>[]`; do not use `any`.
- Keep live-row guards (for example `status: { $ne: 'deleted' }`) in both validation filters and write filters when preserving soft-delete behavior.
- Avoid broadening validation to related target documents unless the plan explicitly calls for it. In list-item reorder flows, target article/comment availability is a rendering/population concern, not a reorder concern.

## Review checklist

1. Does the plan remove concurrent operations on one `ClientSession`?
2. Is the endpoint/repository contract all-or-none or best-effort cosmetic? Follow that contract instead of reflexively preserving or removing validation.
3. Does it handle empty arrays before `bulkWrite()`?
4. For all-or-none flows, does it use `matchedCount` rather than `modifiedCount` for not-found detection? For best-effort flows, is absence of count validation explicitly documented?
5. Does every async call use its own fresh error container?
6. Are bulk ops typed without `any`?
7. Are soft-delete/status guards preserved without adding unrelated target-content guards?
