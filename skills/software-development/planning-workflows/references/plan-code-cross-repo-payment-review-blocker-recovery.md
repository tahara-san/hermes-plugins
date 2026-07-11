# Cross-repo payment review blocker recovery

Use this when a Buffdemy `plan-code` phase lives mostly in `buffdemy2-web`, task/review artifacts live in `buffdemy-backend`, and a mandatory review leg fails after another leg already approved.

## Pattern

1. **Save the failing reviewer artifact immediately.** Preserve the exact JSON/verdict and reviewer session identity. Mark any existing pending/approval artifacts stale once source/tests will change.
2. **Adjudicate against the live tree before coding.** Reviewers can mix current and stale evidence. If a finding is already fixed/covered, prove it with current source/tests and record the adjudication. Do not churn just to satisfy a stale/misread finding.
3. **For valid blockers, use RED/GREEN in the implementation repo.** Add the smallest regression near the affected component/model. Verify RED fails for the expected product reason, then patch production code and verify GREEN.
4. **Rerun proportional verification before review.** At minimum: the new focused regression, adjacent existing regression for related reviewer concern, full touched component/model suite, expanded phase-focused suite, lint/i18n, diff hygiene, full unit, and build when the prior bundle cited those gates.
5. **Regenerate the canonical bundle in the task-artifact repo.** Include: post-blocker adjudication, RED/GREEN evidence, latest verification output, in-scope frontend diff/untracked file contents, backend contract snapshots if the review depends on them, and live task docs. Validate no truncation/cache placeholders.
6. **Rerun every mandatory review lane on the regenerated bundle.** Launch the interactive Codex TUI and Claude Code Opus 4.8 @ xhigh effort lanes against that bundle before waiting on either. A prior approval from before the reviewer-driven source/test fix is stale. Do not update TODO/progress to complete until both fresh lanes pass.
7. **Save a new pending artifact if the interactive Codex TUI has not produced a parseable attested verdict.** Name the managed tmux session, raw pane capture, regenerated bundle path/hash, superseded artifacts, companion reviewer state, verification evidence, and exact resume steps.
8. **For interactive Claude Code Opus 4.8 @ xhigh effort, bound read-only exploration.** Approve prepared bundle reads and narrowly relevant source/status checks. If it roams after several checks, interrupt and request a no-tools verdict from reviewed context.

## Payment/UI example checklist

- If the blocker concerns component state initialized from props, add a rerender regression proving parent refresh/row reuse updates the visible control and modal totals.
- If target identity changes while a modal/payment session is open, reset/close modal state so stale `clientSecret`/record ids cannot cross reused rows.
- If the blocker concerns post-confirm polling errors, first check whether an existing regression already proves a user-visible recovery path. If it exists and passes, record that finding as already covered rather than changing behavior.
- If the blocker concerns a post-confirm poll completion after target reuse, treat it as a data-integrity blocker even if the server-side payment is already authoritative. Add a RED regression that leaves the status poll unresolved, rerenders/reuses the component for another target, resolves the old poll as success, and asserts the new target's visible totals and modal totals stay unchanged. Fix by capturing a lifecycle/target sequence before polling and re-checking it before optimistic success, error display, or step changes.
- If a stale/superseded reviewer finds a duplicate-submit bug in a payment editor/wizard, do not dismiss it because newer review work is pending. Add a RED regression that holds the Stripe confirmation promise unresolved, double-clicks Publish/Execute, and asserts the confirmation and backend mutation each happen at most once; then set a synchronous in-flight ref before the first awaited confirmation and rerun the proportional payment verification before regenerating the bundle.
- If a reviewer finds in-flight amount/session desynchronization, treat it as a payment data-integrity blocker, not UX polish. Add RED regressions that hold the tip/pledge/setup-intent create promise unresolved, prove amount controls cannot change or stale responses are dropped, and assert the mounted payment/review amount comes from the created session amount rather than live input state. Fix with a synchronous preparation ref, post-await selected-amount comparison, and session clearing on later amount edits.

## Artifact wording

Use precise status labels:
- `CHANGES_REQUIRED` reviewer artifacts are evidence, not final failure after the fix.
- `APPROVED` artifacts from before a source/test change are `stale/superseded`, even if their findings remain useful.
- The phase remains incomplete while a required interactive review leg is pending, even with green verification and a passing companion review.
