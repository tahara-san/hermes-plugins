# Plan-code current-only rerun bundles after stale-doc review failures

Use this when a mandatory `plan-code` review fails on stale or contradictory task artifacts after implementation evidence is otherwise aligned.

## Pattern

1. **Save the failing verdict first.** Preserve the reviewer JSON/raw output as a durable failed artifact. If there was a pending placeholder, overwrite or patch it to `superseded_by_failed_verdict` so it cannot be counted as active approval.
2. **Patch the live authoritative docs narrowly.** Fix only the stale current-status wording the reviewer identified. Convert old probes/log conclusions to historical/superseded language instead of deleting useful diagnostic evidence.
3. **Regenerate a current-only rerun bundle.** Do not embed old full bundles wholesale if they contain stale status prose. Include:
   - current task docs/progress/TODO snippets,
   - current scoped source/test snippets,
   - current failed-verdict artifacts as historical context,
   - a short explicit current contract,
   - paths to raw historical logs rather than huge stale transcripts.
4. **Validate before dispatch.** Run `git diff --check`, JSON validation for verdict artifacts, marker scans (`[OUTPUT TRUNCATED]`, `content_returned: false`, `[MISSING]`), and targeted stale-phrase scans for the exact contradictions the prior reviewer cited.
5. **Dispatch a fresh read-only review against the current-only bundle.** Prior approvals/failures remain historical until the new current bundle passes.
6. **Save late pass verdicts before final consistency.** If the current-only rerun returns PASS after a pending placeholder or after a final-consistency placeholder/bundle already exists, first write the PASS artifact verbatim, overwrite or patch the pending placeholder to `superseded_by_passed_verdict`, and update active task docs to name the new authoritative reviewer/artifact. Do not count any older consistency placeholder or bundle that predates this PASS as covering the final active artifact state.
7. **Regenerate the active-scope consistency bundle after saving the PASS.** Include the new pass artifact, superseded pending artifact, failed historical verdicts, current live docs, and current evidence logs. Re-run JSON validation, `git diff --check`, missing/truncation marker scans, and targeted stale-phrase scans before dispatching final artifact consistency.
8. **Do not mark the phase complete after the implementation review alone.** If docs/review artifacts changed after review, run the final artifact-consistency gate.

## Payment/E2E-specific note

For Stripe real-card E2E, keep three statuses separate in the bundle and final report:

- deterministic mocked/ready-off Playwright evidence,
- real-card browser evidence that may stop at app `processing`,
- webhook/poll/manual Stripe gates.

If real-card confirmation reaches `Payment is processing...` but never reaches app success, classify it as webhook/poll completion evidence. State plainly whether the backend needs webhook processing: yes, either via real Stripe forwarding to `POST /webhook/stripe` or an explicitly enabled local/test injection endpoint when the repo provides one.
