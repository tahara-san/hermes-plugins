# Plan-code Phase 0 backend blocker stop pattern

Use when an explicit `/plan-code` task has a documented Phase 0 backend/API/data-integrity gate that must be verified before frontend or client implementation.

## Pattern

1. Re-read the task docs before editing implementation files: `spec.md`, `todo.md`, backend handoff/instructions, and notes/progress.
2. Inspect the current authoritative backend/source files, not only prior task notes. Prefer exact route/schema/repository/index files over stale docs.
3. If the required contract is still missing, stop before frontend/client edits. Do not create a frontend-only bridge that would be unsafe to ship unless the user explicitly approves a prototype/deviation.
4. Make the blocker durable in the task directory:
   - mark the Phase 0 re-read item complete;
   - mark each unresolved backend/API gate as `[!]` with exact file-level evidence;
   - append a timestamped notes/progress section with the verification result;
   - update backend instructions/handoff docs with the current blockers and required backend work.
5. Run only lightweight artifact checks that are meaningful for documentation changes, such as `git diff --check` on the task directory. Do not claim implementation verification, simplify, or final review gates ran.
6. Final report should say clearly: blocked/not complete, no implementation files changed, which docs were updated, backend/frontend worktree status, and the exact next step needed to continue.

## Common evidence to record

- Missing session-derived current-user lookup (`mine=true`, `/me`, or equivalent) when the product requires loading the current user's existing child item.
- Missing uniqueness/data-integrity guarantee for one child item per `(parent, owner)`.
- Write guards that still reject required owner transitions such as unpublish/edit on terminal parents.
- Parent aggregate/status updates that decrement counts but do not restore state after an unpublish/revert transition.

## Pitfall

Do not satisfy the checklist by adding a capped public-list filter or by starting UI work while the backend gate remains unresolved. In plan-code, a Phase 0 backend blocker is a legitimate completed outcome for the turn, but it must be documented as a blocker artifact rather than a completed implementation.