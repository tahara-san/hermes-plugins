# Backend-to-frontend contract handoff after backend plan-code

Use when a backend `plan-code` task finishes or reaches final review and the user asks for a handoff document so a frontend session can plan against the new API/contract.

## Pattern

1. Keep the handoff in the backend task directory, not only in chat, e.g. `tasks/<backend-task>/frontend-handoff.md`.
2. Ground the handoff in implemented backend source/tests, not just the original spec. Include:
   - endpoint and request-body changes;
   - runtime-authoritative behavior when schema/OpenAPI docs intentionally differ to preserve stable custom errors;
   - success response shape and newly relevant response fields;
   - stable error codes, HTTP status, structured `error.content`, and frontend UX guidance for each code;
   - backend verification/review artifact paths;
   - backend alignment gate for live frontend tests (ensure the frontend dev server points at the backend checkout containing the contract).
3. Write the handoff for a future frontend `plan-doc`/planning session, not as implementation instructions to edit immediately. Include a copy-paste kickoff prompt that starts read-only and asks the frontend session to locate call sites/types before coding.
4. If the handoff is created after final implementation review, refresh the final implementation/review bundle or clearly document that the handoff is a post-review documentation artifact. Do not imply the previous source review covered newly written handoff text unless the workflow requires/runs an artifact-consistency review.
5. If the task is likely to be `plan-commit` cleaned up, warn that the live working-tree path will disappear after the cleanup commit. Preserve a retrievable reference in the commit/cleanup report (for example `git show <implementation-sha>:tasks/<backend-task>/frontend-handoff.md`) or, if the user wants a live file, ask before copying the handoff to a non-task location.
6. Keep non-frontend backend details concise. Frontend needs contract, errors, UX implications, testing gates, and backend evidence — not the full backend implementation narrative.

## Pitfalls

- Do not tell frontend to blindly send a new context field from every media/upload caller; first require call-site discovery and non-target-flow classification.
- Do not turn backend runtime-only validation behavior into generated-schema truth. If backend intentionally keeps a broad schema to return stable `AppError` codes, call that out explicitly.
- Do not ask the frontend to compute authoritative rolling quotas locally when backend counts reservations/concurrency; frontend can display messages and use backend-provided reset metadata, but backend remains source of truth.
