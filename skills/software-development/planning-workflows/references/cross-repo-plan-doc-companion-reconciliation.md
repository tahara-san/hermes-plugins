# Cross-repo plan-doc companion reconciliation

Use when an explicit `plan-doc` task in one repo discovers an existing companion task directory or dirty implementation work in another repo for the same contract.

## Pattern

1. **Do not overwrite or absorb the companion task.** Treat it as the authoritative plan for its owning repo unless the user explicitly asks to merge/delete it.
2. Patch the origin repo's task docs to name the companion path and require `/plan-code` to read/reconcile it before editing that repo.
3. Record current dirty files in the companion repo as pre-existing work until scoped by `/plan-code`; do not stage or classify them as created by the current plan-doc turn.
4. Regenerate the plan-review bundle after adding the companion reference. Include:
   - origin task docs,
   - companion task docs,
   - `git status --short`/diff stat for both repos,
   - relevant source excerpts from both repos.
5. If a reviewer returns non-blocking plan-footgun notes and you patch docs, mark the old review artifact superseded, regenerate the bundle, and rerun required review legs. A pending Codex-style delegate verdict remains a blocker to aggregate completion.

## Done state

The final response must distinguish:

- task docs created/updated in the origin repo;
- companion task discovered/referenced, not overwritten;
- review legs completed vs pending;
- whether an aggregate plan-review artifact exists.

Do not claim the explicit `plan-doc` flow is complete while a mandatory review leg is only dispatched/pending.