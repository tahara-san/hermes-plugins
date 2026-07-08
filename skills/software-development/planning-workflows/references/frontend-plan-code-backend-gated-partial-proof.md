# Frontend plan-code with backend-gated live proof

Use when an explicit `plan-code` task is frontend-only, but one acceptance criterion depends on a companion backend/API contract that may not have landed yet.

## Pattern

1. **Re-verify the backend gate from current source first** when accessible. Prefer route/schema/repository evidence over stale task prose.
2. **Classify the gate precisely**:
   - Full blocker: the frontend change cannot be implemented safely without the backend contract. Stop before implementation and update task docs with blocker evidence.
   - Partial live-proof blocker: the frontend can be implemented and deterministically tested with mocked/component/unit coverage, but live E2E for one path must wait for the backend. Continue only within frontend scope and document the live-proof blocker.
3. **Do not add frontend proxy/backend shims** to fake the missing backend contract. Keep request/response handling honest.
4. **Split proof by layer**:
   - Component/unit tests prove frontend validation, payload shape, navigation, and no-guess fallbacks.
   - Live E2E may still cover adjacent backend-supported behavior (for example redirect after publish with filled details), but it must not be cited as proof of the blocked backend-gated path.
5. **Update task docs before review** with:
   - current backend evidence and exact blocker code/path;
   - which acceptance criteria are proven by frontend tests;
   - which live/E2E criteria are blocked and when to rerun them;
   - any corrected verification command discovered during execution.
6. **Review bundle wording matters**: tell reviewers the missing backend path is intentionally documented as blocked, not silently satisfied. Include both the deterministic frontend proof and the backend blocker evidence.

## Playwright project pitfall

For Buffdemy2-web E2E specs, the project in a task doc may be stale. Before running or saving the final command, inspect/list the test with the actual Playwright project. Auth specs under `src/tests/e2e/auth/` normally run under `chromium-auth`, not public `chromium`. Use `--list` first when correcting the command, then record the final command and result.

## Completion rule

A task can be "frontend implemented, verified, review-pending/passed" while still carrying a backend live-proof deviation, but do not mark the backend-gated live acceptance criterion as complete until that backend path is actually available and exercised.