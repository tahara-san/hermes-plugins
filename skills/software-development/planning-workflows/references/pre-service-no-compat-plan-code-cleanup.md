# Pre-service no-compat cleanup during `plan-code`

Use when the user clarifies that the target feature is pre-service and the database/index can be flushed or recreated. The correct response is to remove compatibility paths rather than preserving fallbacks for stale payloads or old documents.

## Pattern

1. Reclassify the contract in task docs: fresh-state strict payloads, no role-less/stale event handling, no old-shape fallback.
2. Remove retained compatibility code at every boundary, not only the API route:
   - producer/outbox payload schemas;
   - queue/message schemas;
   - outboxProcessor fanout payload construction;
   - unifiedConsumer handler input assumptions;
   - Elasticsearch/model boundary types and document builders;
   - test fixtures that still encode old Mongo/search document shapes.
3. If a one-time rewrite/backfill/runbook was created before the clarification, execute it only if the user still wants it; otherwise remove it before commit. Do not leave disposable migration/runbook artifacts in the task directory when fresh-state reset is the accepted deployment model.
4. Tighten tests to reject partial or stale shapes rather than merely not using them.
5. Regenerate final bundles from current file contents, not tracked diff only, so removed lines do not keep stale compatibility text alive inside review artifacts.
6. Run a focused stale-shape scan over changed source/tests and the active task directory. Useful patterns include:
   - `backward|compat|legacy|backfill|migration`
   - `userRole ??|totalCount ??|value ??|createdAt &&`
   - `Partial<...DocumentProps>` where full replacement is required
   - optional fields that should now be required (`name?:`, `status?:`, `role?:`)
   - old fixtures like `contentTags: ['tag']` or Mongo `contentTags` using `{ value }`.
7. If broad repo scans find unrelated legacy/backfill code or unrelated untracked task directories, report them separately instead of rewriting them under the current task. Only modify unrelated artifacts when the user explicitly includes them.
8. Re-run impacted verification and review after cleanup. Ask reviewers to fail specifically on stale-shape support at every boundary.

## Pitfalls

- A message schema may be strict while the downstream model type still accepts partial replacement data. Tighten both.
- A handler may send complete payloads while tests still preserve old fixture shapes. Fix fixtures too, or future agents will reintroduce compatibility.
- Final review bundles that include raw diffs can preserve deleted `legacy`/`backfill` text. For stale-language review, bundle current file contents or clearly separate removed diff lines from current state.
- The substring `reset` can appear in unrelated identifiers such as `strictAuthPreset`; inspect matches before treating them as stale reset/backfill logic.
