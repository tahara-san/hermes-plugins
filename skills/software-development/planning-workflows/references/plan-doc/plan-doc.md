# plan-doc reference

## Purpose

Create structured task documents under `tasks/<task-name>/` before implementation starts.

## Procedure

1. Derive or confirm a short kebab-case task name.
2. Inspect the project read-only so the plan is grounded in real code and tests.
3. Identify decisions, manual-handling needs, and out-of-scope boundaries.
4. Write `tasks/<task-name>/spec.md`.
5. Write `todo.md`, `progress.md`, or `todo-phase-N.md` files depending on plan size.
6. Include a dependency/parallelization assessment.
7. Include review gates and verification commands.
8. Emit a copy-pasteable kickoff prompt for `plan-code`.
9. Stop before implementation unless the user explicitly authorized combined planning and coding.

## Required `spec.md` Sections

- Goal
- Scope / Out of Scope
- Decisions and assumptions
- Manual-handling notes
- Technical approach
- Expected file changes
- Dependency and parallelization plan
- Verification commands
- Review gates

## Kickoff Prompt Template

```text
/skill plan-code @tasks/<task-name>

Execute every unchecked task/phase, run documented independent phases in parallel when safe, update progress after each phase, run simplify and required review gates, run verification, and stop only for genuine blockers or user decisions.
```

## Pitfalls

- Writing docs without inspecting the source.
- Starting implementation during planning.
- Hiding unresolved decisions.
- Forgetting a verification command.
- Creating duplicate task directories when the request is a refresh of existing docs.
