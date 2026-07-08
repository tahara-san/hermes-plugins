# Existing Task Plan Refresh Notes

Use this reference when a `/plan-doc` request maps to a task directory that already exists, or when context compaction/session handoff suggests planning files may already have been written.

## Durable Workflow

1. Resolve the active workspace and project root first.
2. Search `tasks/` for an existing directory whose slug or spec title matches the request before creating a new task folder.
3. If a matching directory exists, read at least:
   - `spec.md`
   - `progress.md` when present
   - all `todo.md` / `todo-phase-*.md` files
4. Check `git status --short` for the relevant task docs and likely implementation paths. Existing uncommitted code changes are important context for whether the plan is being created before implementation, refreshed mid-implementation, or merely verified after docs already exist.
5. Update existing docs in place only when requirements, decisions, phase tasks, verification gates, or resume instructions are missing or stale. Do not rewrite stable docs just to prove activity.
6. If the existing docs already capture the current request, report that you found and verified the matching task docs instead of creating a duplicate.

## Pitfalls

- Do not create `tasks/<new-slug>/` just because the user did not name the existing folder.
- Do not treat a context-compaction summary as proof of plan state; reload the task files and inspect the working tree.
- Do not overwrite existing phase TODO/progress structure with a fresh generic plan. Preserve checked/unchecked state and add explicit deltas.
- If implementation files are already modified, mention that the plan was verified against current working-tree state and avoid claiming a clean pre-implementation plan unless that is true.
