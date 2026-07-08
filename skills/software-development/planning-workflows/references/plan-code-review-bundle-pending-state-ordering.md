# Plan-code review bundle pending-state ordering

Use when a `plan-code` implementation is ready for mandatory review but async delegates, task TODOs, pending-review artifacts, or generated bundles have changed during finalization.

## Core lesson

Do not dispatch a replacement review before the live pending/review-state docs are in their intended current state. A small pending-artifact or TODO edit after bundle generation immediately makes the just-dispatched review stale, even if implementation source did not change.

## Recommended sequence

1. **Reconcile authority first**
   - Read the live `todo*.md` / `progress.md` review rows.
   - Read the current `reviews/*pending*.json` artifact.
   - Classify every known delegate id as current, superseded, blocked, or unrecovered.
   - Save superseded late results before creating a new current bundle.
2. **Patch live docs before bundle generation**
   - Update TODO/progress wording so it names the intended current reviewer/bundle state.
   - If the next delegate id is not known yet, write generic wording such as “replacement current-bundle delegate pending; see pending artifact” rather than hardcoding an id that will be wrong before dispatch.
   - Write the pending artifact in a stable pre-dispatch shape with `active_codex_delegate_id: null` or `status: READY_TO_DISPATCH_CURRENT_REVIEW`.
3. **Generate the review bundle from that stable state**
   - Include implementation source snapshots, task docs, and review authority artifacts.
   - Exclude old raw review prose unless the gate is artifact consistency.
   - Validate no truncation/cache placeholders and no self-referential stale bundle contents.
4. **Dispatch exactly one current replacement review**
   - Prompt against the newly generated immutable bundle path.
   - Immediately update only the pending artifact’s delegate-id field if needed.
   - If that post-dispatch update must be included in the reviewed artifact set, either use a placeholder-id scheme before dispatch or plan a final artifact-consistency pass; do not pretend the implementation review covered a changed artifact set.
5. **Handle late returns deterministically**
   - A late approval for an older bundle is `SUPERSEDED_APPROVED_REVIEW`, not current approval.
   - A late failure for an older bundle still gets finding-by-finding adjudication against the live tree.
   - Save the disposition and keep the current gate fail-closed until the current bundle’s verdict is saved.

## Stale-word scans in generated bundles

When the user has explicitly replaced a reviewer/tool/model name (for example replacing a prior reviewer with Claude Code Opus 4.8 xhigh), scan not only live docs but also generated review bundles and authority artifacts for the old term. Historical diff text inside bundles can reintroduce stale wording and confuse final artifact-consistency checks. Neutralize historical quotes in generated bundles when they are not material to the reviewer verdict, while preserving raw reviewer verdict artifacts separately if needed.

## Pitfalls

- Dispatching a new delegate and then editing `todo-phase-1.md` to name that delegate makes the bundle it is reviewing stale if the TODO is part of the intended artifact set.
- Regenerating a bundle after a pending artifact changes should supersede every delegate dispatched against the older bundle, even if it has not returned yet.
- Do not use old pending-artifact text as truth after context compaction; reconcile from live files and write a fresh authority artifact.
- If only task docs/review artifacts changed after source approval, source correctness may still be valid, but `final-review.json`/completion still needs a current artifact-consistency or current-bundle review path according to the task contract.
