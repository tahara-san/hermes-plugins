# Plan-doc superseded reviews with valid current blockers

Use when a historical delegated `plan-doc` review returns after its reviewed bundle has already been superseded, but the stale review contains concrete blockers that may still apply to the current task docs. Such a legacy result is evidence only and never substitutes for the current interactive Codex TUI lane.

## Pattern

1. **Classify by delegation id and bundle authority.** If the returned delegation reviewed an older bundle, never count it as approval for the current plan-doc gate.
2. **Save the stale verdict before changing docs.** Persist the raw/structured result as a superseded review artifact with the delegation id, reviewed bundle path, and current adjudication.
3. **Adjudicate each finding against the active docs/source.** A superseded failure can still identify a real current plan defect, especially source-contract mismatches or under-specified rollback/failure semantics.
4. **Patch only valid current blockers.** If a stale finding still applies, update the active `spec.md` / `todo.md` / kickoff prompt narrowly. Mark every pending or passed review for the pre-patch current bundle as superseded.
5. **Regenerate one canonical bundle.** Preserve the previous bundle as superseded, then rebuild `reviews/plan-doc-review-bundle.md` from current active docs and relevant source. Validate no truncation/cache markers and run scoped `git diff --check`.
6. **Rerun both required plan-doc review lanes.** Launch the interactive Codex TUI and Claude Code lanes against the same regenerated bundle before waiting on either. Any approval or pending historical review for the pre-patch bundle is stale even if it returns later.
7. **Avoid infinite polish loops.** If a current reviewer approves and labels remaining notes as minor/non-blocking polish, record them in the reviewer JSON/aggregate rather than editing again, unless the note exposes a real implementation footgun that would materially change acceptance criteria or tests.

## Findings that should usually be adopted

- A current-source contract mismatch, such as a plan assuming one enum/currency/state while live schemas/tests support another.
- Missing rollback or failure semantics for an update path that can leave durable local state inconsistent with provider/external state.
- A test matrix omission for an edge case created by the plan itself, such as legacy unsynced records or unsupported-state rejection side effects.
- Ambiguous error code/status contracts when the plan expects tests to assert a stable API behavior.

## Findings that can usually be recorded without another rerun

- Harmless duplicate command flags when the command still works.
- Suggestions to spell out behavior already implied by acceptance criteria and explicitly classified by the reviewer as polish only.
- Naming/reference nits that resolve in the current repo context.

## Artifact checklist

- `codex-plan-doc-review-<delegation>-superseded*.json`: raw verdict plus current adjudication.
- `current-bundle-reviews-superseded-*.json`: names stale pending/completed review lanes after a live doc patch.
- `plan-doc-review-bundle-*-superseded.md`: previous bundle snapshot.
- Current `plan-doc-review-bundle.md`: rebuilt from active docs/source only.
- Current pending artifact names the active tmux session, raw pane capture, bundle identity, and resume steps.

## Pitfalls

- Do not dismiss a stale failed review solely because its bundle is old.
- Do not count a stale passing review after active docs changed.
- Do not patch every approved reviewer polish item; each doc edit stales the review gate. Adopt only footgun-level improvements, then stop once remaining suggestions are genuinely non-blocking.
- Do not create the aggregate plan-review artifact until both required current-bundle review lanes pass or a leg is explicitly waived.
