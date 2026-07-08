# Backend Gate Fail-Closed UI Pattern

Use this when a plan-code task has a frontend change that depends on a backend/API contract that may not have landed yet.

## Lesson

A backend gate that is unmet is a live product blocker, not only an E2E/manual-verification blocker. If the current backend still rejects a request shape, the frontend must fail closed and avoid sending that known-bad request until the backend contract is actually available.

## Pattern

1. Re-verify the backend gate against the live/current backend path, not just docs or task intent.
2. If the backend rejects the future request shape:
   - keep or add a UI guard that prevents users from submitting that request;
   - add a regression test that the guard stays disabled and the API call is not made;
   - keep redirect/success-path improvements only for backend-supported request shapes;
   - document live E2E as backend-blocked, not as passed or merely skipped.
3. Do not encode the future frontend behavior as active/live behavior until the backend accepts it.
4. If task docs originally describe the future behavior, add a clear current-contract section stating the fail-closed interim behavior.

## Example application

For a question publish flow where the future goal is optional details/content, if `/api/question` still returns `question_content_required` for empty/default details, Review-view Publish must remain disabled for empty details. Component tests should assert the disabled button does not call `fetch`. E2E can still verify publish redirect with details content, while empty-details live publish remains blocked on backend support.

## Review implication

If a non-blocking reviewer suggestion corrects stale docs after approval, either record it without adopting or, if adopted, regenerate the final bundle and run a narrow consistency review. Do not claim a prior approval covers artifacts edited after that approval.