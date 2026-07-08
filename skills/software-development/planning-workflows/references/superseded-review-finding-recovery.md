# Superseded review finding recovery

Use during `plan-code` when an async/fan-out review result returns after its review handle or bundle has already been superseded by later edits, verification, or a refreshed pending review.

## Rule

Do not ignore a superseded review solely because its handle/artifact is stale. Treat concrete findings as current-tree hypotheses:

1. Classify the result:
   - **Stale-only**: points at files/claims that no longer exist or were already fixed in the current tree.
   - **Concrete current-risk**: describes an invariant, test gap, or logic/security issue that can still be checked against current source.
2. For concrete current-risk findings, inspect the current implementation and tests before deciding.
3. If the finding is valid:
   - save the reviewer output as a `superseded_failed` or `superseded_blocking` artifact, not as an approval;
   - fix the smallest source/test/doc scope that addresses it;
   - add or update a regression test that would have caught it;
   - rerun impacted verification with real output;
   - update task notes/final report with the finding, fix, and post-fix verification;
   - mark any pending/final review artifacts dispatched before the fix as stale/superseded;
   - regenerate the final bundle from the current tree;
   - dispatch a fresh final reviewer against the refreshed bundle.
4. If the finding is invalid after current-tree inspection, save a short adjudication artifact explaining why and include that in the next final bundle.

## Example pattern

A review handle that had already been superseded returned `passed=false`, noting that backend minimum-length validation counted raw `trim()`ed text while frontend validation collapsed whitespace. Even though the handle was stale, the finding was real in the current tree. The fix was to align backend normalization with frontend visible-text counting, add create/update multi-paper separator regression tests, rerun backend aggregate verification, save the failed review as superseded, and regenerate/rerun the final review gate.

## Out-of-order async completions

When several review reruns were dispatched and their async completions arrive later/out of order:

1. Identify which bundle/tree each delegation reviewed from its dispatch context and timestamp.
2. Save every returned result durably, but label it by authority:
   - `SUPERSEDED_APPROVED_REVIEW` for stale passes that no longer cover the final bundle.
   - `SUPERSEDED_FAILED_REVIEW` for stale failures whose blocker has since been fixed.
   - canonical approval only for the latest required review leg that covers the current final bundle.
3. Update the live pending/blocker artifact with a trace of saved superseded results, but keep the current required delegation id as the missing leg until its own parseable verdict arrives or is waived.
4. For stale failures, verify the concrete finding against current docs/source before dismissing it. If fixed, record the exact current evidence (for example current line text and stale-pattern scan result). If still valid, fix and rerun the final bundle/reviews.
5. Do not promote a stale approved result merely because it arrived after the current pending artifact was written.

## Final artifact consistency nuance

After the canonical review finally arrives and final-review/TODO/notes are updated, run a deterministic artifact-consistency pass over active task docs and canonical review artifacts. Watch for stale-pending language and old-order literals that appear inside historical notes/checklists. If a simple scan is part of the gate, either scope it to active assertions or reword historical meta-notes so they do not embed the obsolete contract literally; otherwise the final docs can be internally correct but still fail repeatable stale-wording checks.

## Pitfalls

- Counting a stale dispatch as approval because a newer review is pending.
- Discarding a stale review's blocking logic finding without checking current source.
- Fixing the issue but leaving earlier pending-review artifacts looking current.
- Regenerating the bundle before updating task docs/final report with blocker/fix evidence.
- Leaving `deleg_<id> is still pending` text after that exact delegate returns and is saved.
- Embedding obsolete contract text in historical notes when final artifact checks search for that literal globally.
