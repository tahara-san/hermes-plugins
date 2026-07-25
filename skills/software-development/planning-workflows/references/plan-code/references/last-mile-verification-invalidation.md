# Last-mile verification invalidation

Use this when a multi-phase `/plan-code` task is near completion and a reviewer or simplify pass suggests "small" final changes.

## Rule
Any **judged-product** edit after the most recent passing verification/review invalidates the corresponding gate, even if the edit is only an assertion, import cleanup, or harmless-looking simplification. Judged product means code, tests, fixtures, migrations, task docs, executable commands/contracts, intended commit artifacts, and any final report whose content is part of the task contract.

Writing **review-evidence** bytes does not invalidate anything: launch provenance, raw panes, normalized verdicts, disposition ledgers, gate JSON, cleanup evidence, supersession records, and parked-advisory issue files. Validate those deterministically (schema, referenced files, digest/size, model/effort and bundle identity, secret scan, no pending placeholders, task-scoped cleanup) instead of running another substantive review over them. See `../../review-finding-disposition-and-convergence.md`.

## The cheaper answer near the end
Before applying a late "small" edit, classify the suggestion that prompted it. If it fails the blocker predicate — optional assertion hardening, naming, readability, evidence polish — do not apply it at all. Record the disposition and leave the verified state intact. The rerun cost is the reason this rule exists; not making the edit removes the cost entirely.

Apply a late edit when it closes a confirmed blocker. Then pay the full rerun.

## Required sequence
1. Apply the final edit only if it closes a confirmed blocker **and** there is enough execution budget to re-run the affected focused tests and any stale review gate.
2. If the edit touches task assertions, component behavior, or public contracts, rerun the targeted suite before updating phase TODO files.
3. If the edit was review-driven, rerun simplify and independent review for the affected phase or holistic diff.
4. Update task TODO/progress immediately after the rerun passes.
5. If tool/context limits are likely, do not start extra nice-to-have test hardening before phase docs reflect the last verified state; leave it as a recorded disposition instead.

## Pitfall
Do not let a final small test-hardening edit happen after a passing review and focused test run without rerunning tests. If an interruption occurs in that gap, the task is not complete and the next session must resume from the unchecked task files and rerun verification first.
