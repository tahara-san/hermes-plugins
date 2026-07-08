# Planning Fixes for Canonicalized Aggregate Bugs

Use this reference when a user reports that a stats/counts/discovery view did not change after creating or updating records.

## Pattern

A common root cause is a split between:

- **Read/discovery path canonicalization**: the view or API lowercases, normalizes Unicode, dedupes, or otherwise canonicalizes lookup keys.
- **Write/aggregation path raw persistence**: create/update flows persist user-entered keys as-is, and aggregate stats are materialized under those raw keys.

Example shape from a tag-stats investigation:

- `/tags` rendered backend-provided `stats` unchanged.
- `/api/tags` normalized query names with a shared tag normalizer.
- Article save flow forwarded raw editor tag text to the backend.
- Reported articles used `VALORANT`, while canonical tag buckets used `valorant`.
- The likely user-visible symptom was split case-sensitive buckets, so canonical lowercase stats did not increment.

## Planning Checklist

1. Trace both the **stats read path** and the **record write/update path** before drafting fixes.
2. Identify the true source of truth for the stats. Do not plan client-side derived stats if the backend owns denormalized aggregates.
3. Add write-path canonicalization to prevent new bad records from the current client.
4. Add defensive canonicalization at the closest shared boundary before outbound persistence payloads.
5. Add mandatory tests proving create/update payloads are canonicalized, not just read-route or UI tests.
6. Preserve domain-specific limits/validation; do not blindly reuse a normalizer from a nearby feature if it has different caps or ordering semantics.
7. If existing records may already be split, mark backend canonicalization plus a recount/backfill/migration as required for a complete fix.
8. Verify against both the originally reported records and a fresh create/update after the fix.

## Plan Language to Use

Be explicit about partial versus complete fixes:

- Client/web normalization prevents new web-originated split buckets.
- Backend canonicalization protects every client and is the source-of-truth fix.
- A recount/backfill repairs existing denormalized stats and affected user/content tag records.

This distinction prevents a plan from sounding complete when it only stops future drift.