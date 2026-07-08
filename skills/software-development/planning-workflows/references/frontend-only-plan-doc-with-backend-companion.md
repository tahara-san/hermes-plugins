# Frontend-only plan-doc with a companion backend contract session

Use when a user asks for a frontend plan while explicitly saying backend work is happening elsewhere or is out of scope.

## Pattern

1. **State scope early**: this is a frontend-only `plan-doc`; backend edits, backend schema changes, migrations, and backend fixtures are out of scope.
2. **Inspect the frontend boundary** rather than backend internals as implementation targets:
   - frontend page/component that owns the UX;
   - frontend API proxy/route only to understand request/response shape;
   - frontend models/schemas that parse backend responses;
   - current focused tests/E2E that exercise the flow.
3. **Write an explicit backend dependency gate** in `spec.md`:
   - what contract must be true before live/E2E verification can pass;
   - what fields the frontend must receive to continue safely;
   - what to do if the backend contract is absent (usually mock/component proof + blocked live verification, not backend edits).
4. **Keep frontend response validation in scope, backend behavior out of scope**:
   - adjusting frontend parsers/models to tolerate the new backend response shape is frontend work;
   - fabricating backend data in a proxy, adding compatibility shims, or changing backend actions is not.
5. **Design URL/navigation behavior from authoritative response data only**:
   - prefer existing linker/model helpers;
   - do not guess owner IDs/usernames from arbitrary UI text or unauthoritative browser state;
   - if the saved response lacks URL-building fields, record a contract blocker instead of inventing a fallback.
6. **Tests should split deterministic frontend proof from backend-gated live proof**:
   - component/unit tests can mock the backend-accepted shape and assert validation/navigation behavior;
   - E2E/browser tests should run only when the companion backend contract is available, or be documented as blocked.

## Review artifact handling

For explicit `plan-doc`, if one required review leg passes but the Codex-style delegate review remains pending:

- save the completed raw review artifact immediately;
- save a `codex-*-pending.json` artifact naming the delegation id and bundle path;
- save a blocked aggregate (for example `plan-review-blocked.json`) instead of a passing aggregate;
- final response must say the plan docs exist but the full review gate is pending/blocked, not complete.

This is especially important for frontend/backend split plans: a pending review may still catch scope creep into backend work or unsafe fallback URL derivation.