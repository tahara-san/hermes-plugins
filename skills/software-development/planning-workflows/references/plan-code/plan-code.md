# plan-code reference

## Purpose

Execute a documented plan from `tasks/<task-name>/` or an equivalent in-context plan.

## Procedure

1. Read `spec.md` and TODO/progress files before editing implementation files.
2. Confirm acceptance criteria, review gates, verification commands, and blockers.
3. Execute tasks phase-by-phase.
4. Run independent phases in parallel only when the plan marks them safe.
5. Update TODO/progress files immediately after each completed phase.
6. Run `simplify` on changed files before review.
7. Run required independent review gates.
8. Rerun verification/review after post-review changes.
9. Run final verification commands with real output.
10. Final response must include completed phases, verification commands/results, review verdicts/artifacts, remaining risks, and deviations.

## Completion Rules

The task is not complete until:

- all executable TODOs are checked off or explicitly blocked;
- progress docs match the current code state;
- simplify/review gates are complete or waived by the user;
- final verification passes or an external blocker is documented;
- any post-review source/doc/test changes have been covered by rerun verification/review.

## Pitfalls

- Coding before reading the plan.
- Treating a review of docs as implementation completion.
- Forgetting untracked files in review bundles.
- Editing task docs after final review without a consistency check.
- Reporting success without real command output.
