# Last-mile verification invalidation

Use this when a multi-phase `/plan-code` task is near completion and a reviewer or simplify pass suggests "small" final changes.

## Rule
Any code or test edit after the most recent passing verification/review invalidates the corresponding gate, even if the edit is only an assertion, import cleanup, or harmless-looking simplification.

## Required sequence
1. Apply the final edit only if there is enough execution budget to re-run the affected focused tests and any stale review gate.
2. If the edit touches task assertions, component behavior, or public contracts, rerun the targeted suite before updating phase TODO files.
3. If the edit was review-driven, rerun simplify and independent review for the affected phase or holistic diff.
4. Update task TODO/progress immediately after the rerun passes.
5. If tool/context limits are likely, do not start extra nice-to-have test hardening before phase docs reflect the last verified state; leave it as a suggestion instead.

## Pitfall
Do not let a final small test-hardening edit happen after a passing review and focused test run without rerunning tests. If an interruption occurs in that gap, the task is not complete and the next session must resume from the unchecked task files and rerun verification first.
