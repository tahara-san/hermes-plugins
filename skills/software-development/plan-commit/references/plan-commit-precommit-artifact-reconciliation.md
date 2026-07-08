# Plan-commit pre-commit artifact reconciliation

Use this when `/skill plan-commit` is invoked after a completed plan-code task whose task directory will be committed as an artifact.

## Why

A plan-code task can be fully finalized before commit, but its artifacts may still contain wording that was true only before commit (for example "No commit or push performed") or historical pending-marker files that should not be committed as active state. Committing those artifacts without reconciliation makes the artifact set contradict the plan-commit result.

## Steps

1. Before staging, search the task directory for active stale state:
   - `*pending*.json` review marker files.
   - unchecked/in-progress TODO rows.
   - final-report/final-review wording like "placeholder pending", "No commit or push performed", or old live delta claims.
2. Remove stale pending marker artifacts only after confirming the corresponding final verdict artifacts exist and passed.
3. Re-scope old no-commit/no-push wording to pre-plan-commit state, e.g. "Before this `/skill plan-commit` invocation, no commit or push had been performed."
4. If later UI/fix deltas superseded earlier approved deltas, mark the older sections/artifacts as historical/superseded while keeping their verdicts as evidence.
5. If final artifact-consistency review files mention a self-excluded placeholder, update them after the actual passing verdict is saved so they no longer claim the placeholder is live.
6. Generate a small pre-commit artifact-consistency bundle over the live task docs/review JSONs and explicitly exclude the future pre-commit verdict from its own scope.
7. Dispatch a read-only consistency review and wait for a passing verdict before staging.
   - If it fails on stale wording only, save the failed verdict as `pre-commit-artifact-consistency-review-failed-vN.json`, patch the exact stale phrases, rebuild a new bundle, and rerun. Do not overwrite or discard the failed verdict; it explains why the artifact set changed.
8. Save the passing pre-commit consistency verdict, stage it with the implementation/task artifacts, then run staged readback and `git diff --cached --check`.
9. If staged whitespace checks fail only inside generated task/review Markdown, normalize those intended generated artifacts, restage, and run a final post-normalization staged consistency review before committing. Save and stage that verdict too; otherwise the staged artifact set changed after the pre-commit approval.

## Review prompt checklist

Ask the reviewer to verify:

- stale `*pending*.json` marker files are gone;
- `todo.md` has no real unchecked/in-progress/blocked rows;
- final-report/final-review scope old no-commit/no-push wording to pre-plan-commit state;
- final artifact-consistency verdict is passed and no longer claims a live placeholder;
- intermediate deltas are clearly historical/superseded by the current final delta;
- the future pre-commit verdict is excluded from its own reviewed scope;
- if generated artifacts were normalized after approval, the final staged post-normalization bundle shows only generated task/review Markdown changed, `git diff --cached --check` passed, and the future post-normalization verdict is excluded from its own scope.

## Pitfall

Do not stage or commit immediately after editing task docs during plan-commit readiness. Those edits are commit content. Run the pre-commit consistency review over the exact reconciled artifact set first.
