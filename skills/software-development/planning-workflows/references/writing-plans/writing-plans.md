# Writing Implementation Plans

## Overview

Use this reference when a task needs a high-quality implementation plan. The implementer should be able to execute the plan without guessing: exact files, precise tasks, concrete commands, expected outputs, tests, risks, and rollback notes.

## Core Principle

A good plan makes implementation obvious. If the implementer has to guess, the plan is incomplete.

## Plan Quality Rules

- Use bite-sized tasks: roughly 2–5 minutes of focused work each.
- Give exact file paths.
- Include complete code examples only when they reduce ambiguity.
- Include exact commands and expected outcomes.
- Prefer TDD for code-producing tasks.
- Separate decisions from assumptions.
- Mark unresolved decisions as gates.
- Include verification that proves the change works.

## Standard Structure

```markdown
# <Feature Name> Implementation Plan

## Goal
<What this achieves and why.>

## Scope
### In Scope
- ...

### Out of Scope
- ...

## Decisions
- ...

## Technical Approach
- ...

## Expected File Changes
| File | Change | Description |
|---|---|---|

## Tasks
### Phase 1: ...
- [ ] Write failing test ...
- [ ] Implement ...
- [ ] Verify ...

## Verification
- [ ] <command> passes
```

## Common Mistakes

- Vague tasks like “add auth” instead of file/function-level work.
- Missing failure-mode tests.
- Commands that only work from an unstated directory.
- Plans that silently choose product/API behavior without recording the decision.
- Plans that omit rollback or cleanup for risky changes.
