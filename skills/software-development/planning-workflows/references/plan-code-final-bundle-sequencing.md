# Plan-code final bundle sequencing and artifact consistency

Use when a completed `/skill plan-code` task has implementation reviews, final review artifacts, TODO/final-report reconciliation, and an artifact-consistency gate.

## Problem this prevents

A final implementation review bundle can embed stale task-doc snapshots. If `todo.md` or `final-report.md` is updated after the bundle is reviewed, artifact-consistency can correctly fail even when source code was approved.

A second, subtler failure happens when the bundle is refreshed after reviewer artifacts are saved: the aggregate review may claim reviewers approved `final-implementation-review-bundle.md`, but the bundle timestamp/content postdates the raw reviewer artifacts. That makes the approval stale by sequencing, even if source code did not change.

## Safe sequence

1. Put task docs into their intended final state before final implementation review:
   - `todo.md` has no real unchecked work except status legend examples.
   - `final-report.md` exists and names verification commands/results, review artifact paths, deviations, and unrelated dirty/untracked paths.
   - Any earlier failed consistency/review artifacts are clearly marked historical or initial-failed.
2. Generate `reviews/final-implementation-review-bundle.md` once from the current source, tests, task docs, final report, status, static scan, and verification evidence.
3. Validate the bundle before dispatch:
   - no `- [ ]` real TODO lines from stale snapshots;
   - no truncation/dedup placeholders;
   - unrelated dirty/untracked paths are explicitly classified and excluded from task ownership.
4. Run both mandatory review legs against that exact bundle.
5. Save raw reviewer artifacts after they return.
6. Write `reviews/final-review.json` as an aggregate artifact that references the reviewed bundle and raw reviewer artifacts. It is expected for the aggregate artifact to postdate the raw reviews.
7. Run a final artifact-consistency review that excludes itself. It should accept that `final-review.json` postdates the reviews, but it should fail if the reviewed bundle postdates the reviews.

## If consistency fails

- If it finds stale unchecked TODOs or stale final-report text inside the bundle: save the failed consistency artifact, update docs if needed, regenerate the bundle, and rerun both mandatory review legs.
- If it finds that the bundle was regenerated after reviewer artifacts: do **not** edit the bundle again; rerun both mandatory review legs against the current bundle, then update only the aggregate `final-review.json`.
- If you edit source/tests/task docs after reviewer approval, verification and both review legs are stale. Rerun the relevant verification and review gates before claiming completion.

## Final report wording

Report the resolved failure honestly, for example:

- “Initial artifact-consistency failed because the bundle embedded a stale TODO snapshot; saved as `artifact-consistency-review.initial-failed.json`, refreshed the bundle, and reran mandatory reviews.”
- “Final consistency passed after review reruns; no source/test implementation files changed after final approval.”
