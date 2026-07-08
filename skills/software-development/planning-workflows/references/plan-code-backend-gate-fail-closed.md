# Plan-code backend gate fail-closed pattern

Use this when a frontend plan-code task depends on a backend/API companion change, or when live/manual verification shows the backend contract is still unmet.

## Lesson

A documented backend blocker is not enough if the frontend change can still send a known-bad live request. If the current backend rejects the new request shape, the frontend must fail closed until the backend contract lands.

In the Buffdemy question publish flow, the task documented that backend `validateAndPreparePapers()` filtered empty/default papers and `QuestionRepository.createWithPapers()` returned `question_content_required`, but the frontend still enabled Review → Publish with empty details. Manual/live verification then hit `/api/question` and reproduced the backend error. The correction was to restore the publish disabled guard while keeping redirect behavior for backend-supported saves.

## Required sequence

1. Reverify the backend gate before enabling the frontend behavior.
   - Inspect the exact frontend API/proxy path and the backend route/repository validation it reaches.
   - Treat current live/manual API errors as authoritative even if component tests can mock the future contract.
2. If the backend gate is unmet, keep the live frontend fail-closed.
   - Do not enable buttons or flows that call a known-rejecting API shape.
   - Keep redirect/UI improvements only for backend-supported paths.
   - Component tests should assert the fail-closed behavior: disabled control and no `fetch`/mutation call.
3. Mark the future-contract test/E2E as blocked or deferred until the backend companion lands.
   - Do not claim live E2E coverage for the future contract.
   - Record the backend blocker and exact error/code.
4. If manual/user verification contradicts a completed review, treat all approvals as stale.
   - Add a RED regression for the live failure.
   - Fix narrowly.
   - Rerun impacted verification.
   - Regenerate the final bundle and rerun mandatory review legs before claiming completion.

## Bundle/review notes

The review bundle should state both the desired future contract and the current live contract. Ask reviewers to check that the implementation does not leak the future contract into live UI affordances before backend support is available.

Good corrected-contract phrasing:

- Current backend still rejects empty/default question details with `question_content_required`.
- While backend support is unmet, empty-details Publish must stay disabled and must not call `/api/question`.
- Successful publish redirect remains active for backend-supported saves with details content.
- Live empty-details E2E is blocked until backend accepts the request shape.
