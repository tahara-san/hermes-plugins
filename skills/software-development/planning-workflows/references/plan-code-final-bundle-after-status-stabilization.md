# Plan-code final bundle after status stabilization

Use this pattern when a large plan-code task spans repos and verification keeps surfacing additional touched fixture/test files after the first final-review bundle.

## Problem signal

- `git status --short` after a seemingly complete verification shows new or previously unnoticed modified files.
- Additional fixture-only or adjacent test files were changed to satisfy a fresh contract.
- A review bundle has already been dispatched, but later verification evidence or task docs changed.

A dispatched reviewer is not a stable final gate if the bundle no longer matches the working tree.

## Pattern

1. Run `git status --short` in every involved repo immediately before bundle generation.
2. Treat every modified tracked file as either in-scope, adjacent fixture/test update caused by the contract, or pre-existing unrelated dirty work that is explicitly excluded/labeled.
3. Verify newly surfaced touched tests before adding them to the evidence summary.
   - For backend/Bun tests sharing the same test DB, avoid broad concurrent batches that can clean each other's fixtures. If a batched run fails suspiciously, rerun the touched file in isolation before editing code.
   - Use the correct service container for each app tree; API/repository tests and cron-worker tests may require different containers/mounts.
4. Only after status is stable, update task docs/final report with the new evidence.
5. Regenerate the final implementation bundle from current diffs and current task docs.
6. Supersede any pending review artifacts whose bundle was made before the latest evidence/doc change.
7. Launch every required independent final reviewer against the regenerated immutable bundle before waiting on any one lane, then save pending artifacts for any lane without a verdict.
8. Run `git diff --check` and `git status --short` again after writing pending artifacts.

## Pitfalls

- Do not count a pending reviewer session as approval. For Codex, require the interactive TUI raw pane, bundle identity, model/effort attestation, and parseable normalized verdict.
- Do not keep reusing an old approval or pending artifact after docs, tests, source, or verification evidence changed.
- Do not fix a batched test failure caused by shared-test-DB concurrency until an isolated run confirms the same failure.
- Do not run cron/app tests in the wrong container just because the repo path exists on the host; inspect service mounts or rerun in the service that owns that app tree.
