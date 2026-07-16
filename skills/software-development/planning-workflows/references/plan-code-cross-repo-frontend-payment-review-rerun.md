# Plan-code cross-repo frontend payment review reruns

Use this when a `plan-code` phase implements frontend Stripe/PaymentElement UX in a companion repo while task docs/review artifacts live in another repo, and a mandatory review lane finds late blockers after verification was already green.

## Pattern

1. **Treat every post-review source/test/i18n change as staling all current review lanes.** Save superseded/pending artifacts for any reviewer already launched against the old bundle.
2. **Fix review blockers with RED/GREEN tests, not just code patches.** Useful blocker classes from this session:
   - mocked translation functions hid missing real catalog keys → add a real catalog coverage test and register the namespace in every locale index;
   - frontend strict schemas matched one backend response shape but rejected a sibling/list shape → add schema/model tests for both live backend cardinalities;
   - frontend UI implemented a required-payment path only for designated questions while the product contract allowed optional payment for open questions → add tests for both required and optional publish payloads;
   - frontend mirror schemas added new payment record types but left provider/source enums too narrow → compare backend repository/API schemas for provider/status/type enums, then add RED/GREEN frontend schema/model regressions for backend-emitted Stripe-backed records (for example `provider: 'stripe'` on `buffTip` / `questionPledge`) before widening the enum.
3. **Rerun proportional verification before regenerating the bundle.** At minimum: blocker-focused tests, expanded focused phase suite, lint/i18n, full unit suite when the phase TODO requires it, build, and `git diff --check`.
4. **Regenerate a self-contained current-tree bundle after all fixes.** Include task docs, scoped diffs, intended untracked files, verification evidence, static scan results, and explicit exclusions for unrelated dirty files. Keep the bundle reviewable: if a lockfile or other huge generated artifact dominates the bundle, include its scoped diff/stat but omit the full source snapshot, and explicitly state that omission so reviewers do not infer missing source context. Validate the final bundle for truncation/cache markers and current verification counts before dispatch.
5. **Rerun every mandatory review lane against the regenerated bundle.** Launch the interactive Codex TUI and Claude Code Fable 5 @ xhigh effort lanes before waiting on either. Do not count stale approvals or any result from before the fixes.
6. **If the interactive Codex TUI is still pending after Claude Code passes, save a pending artifact with the tmux session, raw pane capture, and bundle identity, then leave the review TODO in progress.** Do not mark phase docs complete until the parseable attested Codex verdict is saved or explicitly waived.

## Interactive Claude Code specifics

- Verify the banner shows the requested model/effort before sending the substantive prompt.
- For large bundles, Claude Code may read the bundle in chunks and ask multiple read permissions. Prefer granting session-level read access to the prepared `reviews/` directory, then approve only narrowly justified read-only backend/source inspections that verify contract alignment.
- If it keeps exploring after the bounded contract checks, interrupt and request a no-tools verdict from reviewed context. Do not let optional read-only inspection become an unbounded second implementation audit.
- Save both raw pane and structured verdict artifacts immediately yourself from Hermes (do not ask the reviewer to write files). If Claude leaves a suggested follow-up such as “Save the verdict JSON…” in the input line after returning a verdict, clear it before `/exit`, then exit/kill the tmux session and verify the worktree was not modified by the read-only review.

## Finalization guard

Do not update phase TODO/progress to complete after only one lane passes. First save both parseable verdicts, then create an aggregate review artifact. If task docs/review artifacts are edited after implementation approval, run the final artifact-consistency pattern before claiming `plan-code` completion.
