# Plan-code final artifact-consistency active scope

Use this when a `plan-code` task has passed implementation reviews but final task docs/review artifacts still need reconciliation.

## Problem pattern

Final review artifacts are often written after the implementation review bundle. That creates two easy false-failure loops:

1. The aggregate verdict (`final-review.json`) can claim a timestamp earlier than a later fallback/raw reviewer artifact it cites.
2. Historical review bundles and raw reviewer transcripts can preserve pre-final task snapshots, such as unchecked TODO rows, pending `final-review.json`, or reviewer notes that say a gate is still pending. Those snapshots are valid evidence of what the reviewer saw, but they are not the live task state.

## Recommended sequence

1. Put live task docs into intended final state before consistency review:
   - `todo.md` real task rows checked or explicitly blocked/deviated.
   - `spec.md` acceptance criteria checked if the task is complete.
   - `final-report.md` says complete only after all required review/verification gates are represented.
2. Write raw reviewer artifacts and the aggregate `reviews/final-review.json`.
3. Ensure `final-review.json.timestamp_utc` is later than, or at least not older than, every raw/fallback artifact it aggregates.
4. Create or overwrite `reviews/final-artifact-consistency.json` only after the consistency verdict. If a placeholder is needed, explicitly exclude that verdict file from its own review scope.
5. Build the consistency bundle from **active artifacts**:
   - live `spec.md`, `todo.md`, `final-report.md`;
   - active raw verdict summaries or verdict JSONs;
   - aggregate `final-review.json`;
   - superseded/pending artifacts only if clearly marked superseded.
6. Validate the generated consistency bundle before dispatching a reviewer:
   - run a truncation/cache-marker scan (`[OUTPUT TRUNCATED`, `content_returned: false`, `refer to earlier read_file result`, `... omitted ...`);
   - run whitespace hygiene on the generated artifact itself (for example `git diff --no-index --check -- /dev/null <bundle>` and treat exit 0 or 1 as acceptable, but fail on check errors);
   - scan active docs/artifacts for exact stale blocker phrases named by prior failed consistency reviews;
   - normalize trailing whitespace inherited from quoted source excerpts rather than editing source files just to satisfy bundle hygiene.
7. If a reviewer was already dispatched against a generated bundle that then fails bundle hygiene, mark that dispatch and bundle as superseded, regenerate a clean bundle, and rerun the consistency review against the clean bundle. Do not let the dirty-bundle reviewer verdict satisfy the active gate.
8. Treat historical implementation bundles and raw transcript bodies as reference-only. Do not judge stale TODO snapshots inside them as live state when the active docs are current.
9. When a superseded failed review must be included for auditability, include a sanitized/adjudicated summary in the new bundle instead of embedding raw reviewer prose that quotes stale active-state wording. Raw stale phrases inside the replacement bundle can confuse the next artifact-consistency reviewer into treating already-fixed text as active state.
10. Preserve failed consistency attempts as `*-failed-superseded.json` if they explain why the live artifacts were patched.
11. Rerun consistency after every live doc/verdict artifact edit that changes completion state. Mark any pending review dispatched before those edits as superseded pending, and dispatch a fresh reviewer against a uniquely named replacement bundle.
12. After a consistency reviewer passes a bundle that explicitly excludes the verdict file to be written afterward, write only the excluded verdict/placeholder replacement artifacts. Do not make opportunistic cleanups to reviewed docs or historical/superseded artifacts after the pass, even if a grep finds confusing nested words like `pending`; those edits stale the just-passed review. If a cleanup is truly needed, treat it as a new artifact edit: regenerate the bundle and rerun consistency.
13. When checking for leftover pending placeholders, distinguish active top-level placeholder status from historical nested metadata. A superseded artifact may contain a nested `active_successor_review.status: pending` snapshot from the moment it was written; if the current reviewed bundle already scoped that artifact as historical/superseded, do not patch it after final consistency just to satisfy a naive string scan.

## Reviewer prompt note

Tell the reviewer explicitly:

- `final-artifact-consistency.json` is excluded from its own scope.
- Historical implementation bundles/raw reviewer transcripts are reference-only and may contain pre-final pending TODO text.
- Passing depends on active docs/verdict artifacts agreeing, not on historical snapshots being rewritten.

## Common blockers to fix

- `final-review.json` timestamp predates a cited fallback reviewer artifact.
- `spec.md` acceptance criteria remain unchecked while `todo.md` and `final-review.json` claim completion.
- A pending delegate artifact remains active instead of being marked `superseded_by_*` after a valid fallback review.
- The final report says “setup” or “pending” after the final consistency verdict has passed.
- An active evidence artifact included in the current consistency bundle still has present-tense “remaining blocker”, “still incomplete until manual gates”, or similar stale caveat wording that contradicts newer confirmation artifacts. If the file is meant to stay active, either update/scope that caveat before rerun or omit it from active evidence and cite it only as historical/superseded context; do not rely on the bundle header alone to override contradictory active excerpts.
