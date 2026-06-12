# plan-clean reference

## Purpose

Classify and optionally clean task directories and out-of-scope issue logs.

## Classification

Use these categories:

- complete
- complete-with-caveat
- incomplete
- ambiguous
- parked/deferred

## Procedure

1. Dry-run first.
2. Read task docs and TODO/progress files.
3. Inspect current code/tests when docs may be stale.
4. Run proportional focused verification when safe.
5. Present classification and deletion candidates.
6. Delete only after explicit user confirmation.
7. Delete only paths under `tasks/`.

## Pitfalls

- Treating checked boxes as proof without checking current code.
- Deleting ambiguous work.
- Deleting source issue logs when the user only asked to clean generated task docs.
- Cleaning outside `tasks/`.
