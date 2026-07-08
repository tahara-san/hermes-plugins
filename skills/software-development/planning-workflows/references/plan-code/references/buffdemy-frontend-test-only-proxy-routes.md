# Buffdemy Frontend Test-Only Proxy Routes

Use this reference when implementing or debugging Buffdemy frontend E2E fixture routes that proxy to backend test-only endpoints.

## Pattern

Frontend App Router test-only fixture routes often live under `src/app/api/test-only/<fixture>/route.ts` and forward authenticated E2E setup/reset requests to the backend's `/test-only/<fixture>` endpoint.

A good proxy route should:

- Gate access with the same test-only environment flag expected by the surrounding E2E suite.
- Keep request schemas strict and narrow to the fixture contract.
- Preserve authenticated user context/identity headers needed by the backend fixture.
- Use the existing shared API proxy helper when available instead of hand-rolling fetch/response logic.
- Avoid broad fixture-owner changes unless the test explicitly needs them; for user-specific setup, fail closed to the intended fixture owner.

## 404 Diagnosis

When an E2E helper calls a frontend proxy such as `/api/test-only/subscription-billing-fixture` and receives a JSON body like:

```json
{
  "code": "not_found",
  "message": "Endpoint not found",
  "content": {
    "path": "/test-only/subscription-billing-fixture",
    "method": "POST"
  }
}
```

that usually means the frontend proxy route resolved and forwarded the request, but the backend process does not have the corresponding `/test-only/<fixture>` route registered or restarted with the required opt-in env. Do not keep debugging App Router route discovery until you verify the backend route is present in the same running backend process used by E2E.

## Verification Checklist

1. Confirm the frontend file exists at `src/app/api/test-only/<fixture>/route.ts` and exports the expected HTTP methods.
2. Confirm the frontend proxy route returns a frontend-side 404 only when the App Router route itself is missing.
3. If the response body reports `content.path: "/test-only/<fixture>"`, inspect the backend route registry/OpenAPI/source for that backend path.
4. Restart the actual E2E backend/app process with the required fixture gate env, then regenerate auth/setup state if the app origin or process changed.
5. Run the narrow Playwright spec with the fixture readiness env (for example `SUBSCRIPTION_BILLING_E2E_READY=1`) only after both proxy and backend fixture route are present.

## Out-of-Scope Handling

If the current frontend task cannot add the backend fixture route because it belongs to another repo/process or requires manual backend work, log a high-priority manual issue under `tasks/out-of-scope-issues/high/manual/` with:

- Issue
- Location
- Severity
- Context
- Suggested Fix

Update an existing matching issue instead of creating duplicates.