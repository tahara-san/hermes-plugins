# Plan-Code Final Consistency Verdict Persistence

Use this when a `plan-code` task reaches the last artifact-consistency gate and the remaining work is saving, canonicalizing, or explaining the review verdict.

## Pattern

1. **Verify before reporting a blocker.** If the active/preserved task list says a consistency review is still `pending` or `in_progress`, first inspect the saved verdict artifacts. The task list may be stale after context compression or late artifact writes.
2. **Canonical verdict wins over stale task-list state.** Treat the review gate as unblocked when a canonical artifact records the current review bundle with `passed: true`, no blocking findings, and the expected delegation/reviewer id. Then update only the session/task-list state needed to reflect that truth.
3. **Avoid staling the just-passed review.** After a final artifact-consistency review passes, do not patch reviewed task docs, historical bundles, or superseded pending markers just to make scans prettier. Any live artifact edit after the review can stale the verdict. Prefer writing a self-excluded/canonical verdict artifact or updating ephemeral session TODO state.
4. **Preserve historical nested status literally when reviewed.** Older superseded files may contain nested strings like `"status": "pending"` describing what was true at that older checkpoint. If those files were included in the passing active-scope bundle as historical/reference-only evidence, do not rewrite them after the pass unless you are prepared to rerun consistency.
5. **Report the true remaining blocker.** If artifact consistency is passed, the blocker is whatever the verdict says remains open (for example user/manual/browser/Stripe gates), not the stale `consistency-rerun` line.

## Canonical artifact checklist

A durable final consistency verdict should include:

- reviewer/delegation id;
- reviewed bundle path;
- `passed: true` and `status: passed` for the canonical copy;
- empty `blocking_findings`;
- any non-blocking caveats;
- explicit note that the verdict artifact itself was excluded from the reviewed scope or overwrote a placeholder;
- phase/task completion status after review.

## Pitfall

Do not “clean up” historical artifacts immediately after a final consistency pass merely because a grep finds stale words. If the active bundle already scoped those artifacts as historical/reference-only, cleanup is a new artifact change and requires another consistency pass.