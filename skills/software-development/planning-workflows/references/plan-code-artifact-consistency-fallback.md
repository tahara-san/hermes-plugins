# Plan-code artifact-consistency fallback

Use this reference when a completed `plan-code` task has already passed implementation verification and implementation reviews, but final task docs/review artifacts were edited afterward and need a narrow artifact-consistency gate.

## When this applies

- Source/test files did not change after implementation reviews.
- Final artifacts changed: `todo.md`, `final-report.md`, `final-review.json`, raw-review captures, or consistency bundles.
- The goal is to check artifact truthfulness, not re-review implementation logic.

## Safe sequence

1. Put live task docs into intended final state before the consistency gate.
2. Create a placeholder consistency artifact first, e.g. `reviews/artifact-consistency-review.json` with `passed: null` / `PENDING`.
3. Build a narrow consistency bundle from current task docs and review artifacts.
4. Exclude the consistency artifact itself from the bundle, or state clearly that it is a placeholder excluded from judgment, to avoid a self-referential stale loop.
5. Validate the bundle has no truncation/cache placeholders.
6. Ask a read-only reviewer to check only:
   - stale unchecked TODOs in live task docs;
   - contradictory completion/review claims;
   - missing artifact paths named by TODO/final report/final review;
   - overclaimed verification/deviations;
   - whether post-review artifact edits are represented clearly.
7. Overwrite the placeholder with the final verdict. Do not leave `passed: null` behind.

## Reviewer fallback

If an async `delegate_task` artifact-consistency reviewer does not start, complete, or re-enter the parent chat within a bounded window, do not count the dispatch as approval. Options:

- recover the completed subagent verdict from logs/session history if it exists; or
- use an already-available interactive `claude-i` read-only review as the consistency reviewer.

This fallback is appropriate for artifact-only consistency checks because it does not replace the mandatory implementation reviewers; it validates the final task-doc/review-artifact state after they passed.

## Handling historical bundle noise

Consistency scans often find old `- [ ]` checkboxes inside immutable review bundles or plan-doc bundles. Classify them carefully:

- **Live docs** (`todo.md`, `final-report.md`, current aggregate review) must not contain stale unchecked completion tasks.
- **Historical bundles** may contain earlier snapshots with unchecked boxes; warn if confusing, but do not treat them as blockers unless current docs cite them as live state.
- If an old bundle accidentally embeds unrelated task context, preserve it as historical evidence unless it causes a current claim to be false.

## Final report wording

Report this gate as an artifact-consistency review, not as another implementation review. State whether source/test files changed after implementation review. If only artifacts changed, note that no implementation-review rerun was needed and the consistency gate covered the final artifact state.
