# plan-issues reference

## Purpose

Convert logged out-of-scope issue files into implementation task plans without fixing them inline.

## Procedure

1. Discover issue files under `tasks/out-of-scope-issues/`.
2. Apply the user's filters exactly.
3. Skip `manual/` files unless explicitly included.
4. Read included issues and normalize issue, location, severity, context, and suggested fix.
5. Deduplicate overlapping issues.
6. Inspect relevant source/test files before drafting the plan.
7. Create task docs through the `plan-doc` workflow.
8. Report included, skipped, duplicate, and manual issues.
9. Leave source issue files in place unless the user explicitly asks for cleanup.

## Pitfalls

- Planning from issue text alone without source inspection.
- Fixing issues inline during conversion.
- Deleting audit/source issue files by default.
- Treating manual/human-only items as agent-runnable tasks.
