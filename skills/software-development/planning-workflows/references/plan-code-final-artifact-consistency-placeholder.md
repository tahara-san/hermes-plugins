# Plan-code final artifact consistency placeholder pattern

Use this when a `/plan-code` implementation has already passed implementation verification and mandatory reviewers, but the workflow still needs to write final review artifacts and mark task TODOs complete. Those artifact/TODO writes happen after the implementation reviewers return, so they can otherwise create a self-referential stale-review loop.

## Trigger

- Implementation/source/tests are final and verified.
- Required implementation review legs have passed.
- You still need to save artifacts such as `codex-final-review.json`, `claude-final-review.md`, `final-review.json`, or update `todo.md` checkboxes.
- No source/test code should change after the implementation review.

## Pattern

1. Save raw reviewer artifacts immediately after each reviewer returns.
2. Save the aggregate `final-review.json` with:
   - bundle path;
   - static scan status;
   - verification command summaries;
   - paths/verdicts for both review legs;
   - explicit `source_or_test_changes_after_review: false` when true;
   - note that artifact/TODO changes still require a final artifact-consistency review.
3. Create `reviews/final-artifact-consistency-review.json` as a pending placeholder **before** the final consistency review.
4. Put `todo.md` and task progress docs into their intended final state before the consistency review:
   - check off review bundle/reviewer/final handoff items that are genuinely complete;
   - document that only artifacts/TODOs changed after implementation review;
   - state that the consistency artifact excludes itself from scope.
5. Run a read-only artifact-consistency review scoped only to task docs/review artifacts, explicitly excluding `final-artifact-consistency-review.json` itself.
6. Overwrite the placeholder with the passing consistency verdict.
7. After that, do not edit task artifacts again unless you rerun the consistency review.

## Review prompt requirements

Ask the consistency reviewer to verify:

- `todo.md` has no remaining real unchecked/in-progress/blocked task items.
- `final-review.json` is valid JSON, `passed: true`, and references raw reviewer artifacts.
- Raw reviewer artifacts exist and show passing/no-blocker verdicts.
- The final implementation bundle exists and records status/diff, static scan, verification evidence, and self-exclusion of generated final review artifacts.
- Post-review changes are artifact/TODO-only; no source/test changes occurred after implementation review.
- No task docs contradict the final implementation/review status.

## Pitfalls

- Do not count the consistency artifact as part of its own review scope.
- Do not mark review/TODO items complete after the consistency verdict; that makes the verdict stale.
- If the consistency review returns only a non-blocking wording/nit suggestion after passing, do not edit artifacts just to clean it up unless you are prepared to rerun the consistency gate. Prefer recording the accepted nit as a deviation in the final response.
- Do not rerun full implementation reviewers solely for artifact/TODO finalization when source/tests did not change; use the narrow read-only consistency gate instead.
- If a required reviewer verdict arrives after a consistency placeholder or consistency bundle was already created, treat the placeholder/bundle as stale. Save the verdict, supersede the pending reviewer artifact, update active docs to cite the authoritative verdict, then regenerate and revalidate the consistency bundle before dispatching or counting final artifact consistency.
- If you include an older implementation-review bundle inside the final artifact-consistency bundle, remember that it may embed stale task-doc snapshots (for example pre-final `[ ]` or `[~]` TODO rows). Prefer referencing the immutable implementation bundle by path plus current canonical artifacts, or annotate the historical excerpt clearly so reviewers do not mistake stale embedded rows for live task state.
- If you decide to implement a reviewer’s optional suggestion, that is a source/test change: rerun affected verification and all mandatory implementation review legs before returning to this pattern.
