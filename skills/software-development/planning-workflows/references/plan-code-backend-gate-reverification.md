# Plan-code backend gate re-verification

Use when an explicit `/plan-code` task is documented as blocked on an upstream backend/API contract before frontend or client work can begin.

## Pattern

1. Read the task `spec.md`, phase TODOs, and progress docs before implementation edits.
2. Treat the upstream gate as a blocking acceptance criterion, not a note. Do not start UI/client wiring until the documented backend option has actually landed.
3. Re-verify the current contract from source, not from stale task prose:
   - route indexes / route registration files;
   - shared route helpers that define path params and lookup semantics;
   - response/user schemas on both backend and frontend;
   - existing server actions or client API wrappers.
4. If the gate is still unmet, fail closed:
   - make no implementation edits;
   - update the task docs with dated re-verification evidence;
   - keep the phase TODO gate unchecked or mark it blocked with evidence;
   - run a lightweight artifact check such as scoped `git diff --check` on the edited docs;
   - final-report the blocker, exact evidence, changed task-doc paths, and next required upstream choice.
5. If a companion upstream task directory already exists (for example a backend plan-doc with its own `kickoff-prompt.md`), mention both artifacts distinctly:
   - the current task's generic handoff prompt path for explaining the dependency; and
   - the companion task's implementation kickoff prompt path for the agent/developer who will actually implement the upstream contract.
   When the user asks for "the kickoff prompt" after a blocked gate, prefer the companion implementation kickoff prompt over the generic handoff prompt, unless no companion kickoff exists.
6. If the gate is met, update the task docs first to record which option landed and then continue phase-by-phase.

## Buffdemy avatar/cover delete example

For `buffdemy2-web` avatar/cover delete UI work, the frontend remains blocked unless one of these is true:

- B1: backend has idless `DELETE /user/avatar` and `DELETE /user/cover` scoped to the authenticated user;
- B2: backend user image payload exposes the active `profileMedia._id` and frontend schema accepts it;
- B3: backend exposes an active-document fetch route returning the active `profileMedia._id`.

Evidence that the gate is still blocked includes: route indexes mounting only `post`, `[id]/put`, `[id]/delete`; delete helper registering `.delete('/:id')` and using `profileMediaRepository.findById(id)`; backend/frontend user image schemas exposing only `{ key, rootKey }`; frontend delete server actions still requiring `{ id }`.
