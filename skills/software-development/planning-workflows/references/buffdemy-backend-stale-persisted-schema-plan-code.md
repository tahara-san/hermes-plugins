# Buffdemy backend stale persisted-schema plan-code pattern

Use when a frontend/API smoke fails with a backend `target_*_fetch_failed`, route target hydration error, or repository `findById()` error, while current source/tests suggest the contract is otherwise correct.

## Trigger example

- Frontend proxy returns `500 target_content_fetch_failed` for a reaction/list/save-style route.
- Backend error debug content wraps a Zod/validation error from loading the target content document, not from querying the requested relation itself.
- The target document contains stale persisted fields from an older schema, e.g. legacy nested stats keys that strict current schemas reject.

## Plan-code sequence

1. **Classify the boundary before editing frontend code.** Trace client component -> frontend proxy -> backend route -> target-content repository load -> relation/reaction query. If the failure occurs while hydrating the target document, treat it as a backend persisted-shape/data-contract issue.
2. **Write RED coverage at both useful levels when cheap.**
   - Route regression: seed/create valid published/readable target, inject the stale persisted fields directly into Mongo, call the public route, assert it returns the intended non-500 result.
   - Schema regression: parse a representative persisted document with the stale fields and assert canonical output.
3. **Prefer narrow hydration normalization over broad schema weakening.** Use a Zod preprocess/normalizer to remove or map known legacy fields while preserving strict validation for unrelated keys. Avoid `.passthrough()` on the whole document unless the product intentionally allows arbitrary persisted fields.
4. **Only map legacy values when semantics are certain.** Otherwise drop known obsolete fields and let existing canonical defaults apply.
5. **Verify with focused tests and package-local builds.** For Buffdemy backend Docker dev, run inside the service from the package/app directory, e.g. `/app/packages/mongo` and `/app/apps/api`.
6. **Refresh stale live runtime before browser/proxy smoke.** If focused tests and package-local builds pass but the live frontend proxy still returns the old error, restart only the affected backend service (usually `docker compose restart api`) before changing more code.
7. **Record deviations in task artifacts.** Note host/container command differences, package-local build commands, and any required service restart.

## Review checklist

- The route test proves the original 500 path no longer happens.
- The schema test proves known stale fields are normalized and canonical fields remain.
- The implementation does not weaken unrelated strict schema validation.
- No frontend symptom suppression was added unless the backend boundary still legitimately returns an expected non-200.
- Live smoke uses the same frontend proxy URL that originally failed.
