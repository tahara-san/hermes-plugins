# Plan-doc superseded review drain

Use when an older review result returns after the live task docs have moved to a newer bundle version. Legacy delegated reviews may be retained as historical evidence, but they never satisfy the current interactive Codex TUI lane.

## Pattern

1. **Classify the returned review by bundle identity.** Compare its reviewed bundle path/hash with the current canonical bundle and pending artifact. An older result is superseded evidence, not current approval.
2. **Do not count stale approvals.** A passing review for `bundle-vN` does not satisfy the gate for `bundle-vN+1`.
3. **Disposition every concrete finding against the current docs.** Record whether each finding is already fixed, still applies, or is intentionally out of scope. Patch only concrete current-risk footguns.
4. **Save the old result durably.** Write a `*-vN-superseded.json` artifact containing the reviewer/session identity, reviewed bundle identity, raw verdict, `superseded: true`, and disposition.
5. **Update the current pending history.** Link the superseded artifact from the active pending aggregate so future agents can reconstruct the review sequence.
6. **If live docs changed, regenerate and rerun.** Any patch to `spec.md`, `todo.md`, or intended plan artifacts makes the current bundle stale. Regenerate the bundle, then launch the interactive Codex TUI and Claude Code lanes against that same immutable bundle before waiting on either.
7. **If live docs did not change, keep the current gate unchanged.** Run scoped artifact hygiene and report the current required review status.

## High-churn drain checklist

1. Keep one explicit current canonical bundle and one current pending aggregate. Older pending artifacts are history only.
2. Save every stale result separately and list it under `superseded_reviews`; never copy stale approval into current verdict fields.
3. If a stale finding still exposes a concrete footgun, patch the current docs, supersede every current-bundle review artifact, regenerate, and rerun both independent interactive lanes.
4. Do not write final `plan-review.json` until the current Codex and Claude artifacts identify the same finalized bundle and no post-review doc edits occurred.

## Current interactive Codex finalization checklist

1. Recover the managed tmux session and save its raw pane plus normalized verdict before writing the aggregate.
2. Prove it reviewed the current bundle by matching bundle path/hash and verify the GPT-5.6 SOL @ xhigh banner attestation. If docs or bundle changed after launch, classify the verdict as stale and rerun both required lanes.
3. If Codex passes and the Claude Code artifact for the same bundle is already saved, write `plan-review.json` and update the pending artifact to completed rather than leaving it active.
4. Review artifacts written after verdicts do not normally stale the product bundle when they are explicitly excluded as evidence-only files.
5. If any substantive task document changes after a finding, all approvals are stale and both lanes must rerun.

## Pitfalls

- A tmux session id, startup banner, or partial pane is not approval.
- Never replace the current interactive Codex lane with a legacy `delegate_task` result, `codex exec`, or `codex review`.
- Do not create the aggregate until both required current-bundle verdicts are saved or a lane is explicitly waived.
- Avoid self-referential bundle churn by excluding review evidence from reviewed product scope.
- Do not leave an active pending artifact after the aggregate has been saved.

## Final response shape

Report the superseded artifact paths, whether live docs changed, current canonical bundle path/hash, current required review status/session, and real scoped verification output.
