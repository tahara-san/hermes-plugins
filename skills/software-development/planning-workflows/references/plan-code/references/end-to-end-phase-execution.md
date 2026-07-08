# End-to-End Phase Execution Guardrails

Use this reference when executing a multi-phase task plan with `/plan-code` or `/goal`, especially after context compression or a preserved active task list.

## Failure mode to avoid
A task can be substantially implemented and verified but still not complete if the phase TODO/progress files are not reconciled, final review/verification is not run, or requested cleanup is not performed. Do not summarize partial progress as completion while any planned phase/task remains unchecked or pending.

## Required loop
1. Reload the task directory source of truth (`spec.md`, `progress.md`, `todo.md`, and/or every `todo-phase-N.md`).
2. Execute the next unchecked phase/task immediately unless it is blocked by an unresolved user decision, manual-handling requirement, external prerequisite, or unfixable verification failure.
3. After each phase or parallel batch:
   - run the documented targeted verification for that batch,
   - update the task files to mark completed items,
   - record blockers explicitly rather than leaving stale unchecked items.
4. Before final response:
   - search the task directory for unchecked boxes, `pending`, `in_progress`, `TODO`, and unresolved decision markers,
   - run simplify and independent review gates,
   - fix worth-addressing findings,
   - run final targeted/static/build verification,
   - only then perform requested task-file cleanup.
5. When a review-driven fix changes async/debounced/throttled React callbacks, verify both lifecycle cleanup and stale-closure behavior. A fix that preserves pending callbacks across rerenders must also make the callback read latest state/props/config (usually via refs) and should add a regression test for rerender-after-schedule behavior.
6. If tool/context limits interrupt execution, state that it is an infrastructure interruption, not completion; the next run must resume from task files, not from memory alone. If interruption happens after a partial edit, name the exact file(s), the partially applied change, and the next verification/review gate to run.

## E2E decision gates
When a plan says not to assume another E2E user, do not add or depend on one. If a paid/privileged role is needed for final E2E proof and no approved identity exists, document the blocker and verify the non-blocked scope with unit/component/static checks.