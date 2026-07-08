# Buffdemy: drafting E2E specs before backend/fixtures are ready

Use this when the user asks to draft Playwright/E2E coverage early while backend fixture routes or APIs are not ready yet.

## Pattern

1. Keep the normal `/plan-code` discipline: write/execute a small plan, run simplify before independent review, and iterate on reviewer findings.
2. Do not run backend-dependent Playwright scenarios. Gate the suite with an explicit env var such as `SUBSCRIPTION_BILLING_E2E_READY=1` and use `test.skip(process.env.FLAG !== '1', reason)` so the drafted suite is inert by default.
3. Still run static checks on the drafted files:
   - narrow ESLint command for the new spec/helper files
   - targeted `tsc --noEmit` command for those files when full project checks are too broad
4. Put future backend fixture contracts in a test-only helper, not scattered through specs. Document expected endpoint, request/response shape, cleanup/reset behavior, auth/test gate assumptions, and deterministic IDs/names returned for assertions.
5. Avoid importing React component barrels or production model barrels from Playwright helpers/specs. Keep constants and fixture contracts in `src/tests/e2e/helpers/*`.
6. Use route interception for primary API failure paths, but match query-string variants explicitly. Prefer regex like `/\/api\/subscription(?:\?|$)/` over glob strings that miss `?id=...` requests.
7. For confirmation-dialog failure paths, close/dismiss the dialog after the failed request if the UI leaves it open, then assert the notice.
8. Scope status/alert assertions to the card/list item that triggered the action when multiple `role="status"` nodes can remain mounted.
9. For load-more tests, require fixture cardinality to exceed the page size before clicking load-more, and assert the first post-page item appears. Do not only assert a generic heading after clicking.
10. When a reviewer suggestion is applied after a clean review, rerun static checks and a quick final review for the changed files.

## Example fixture-helper contract fields

- `tierIds: string[]`
- `subscriptionIds: string[]`
- `incomingSubscriberNames: string[]`
- `billingRecordIds: string[]`
- path fields for public/settings/creator pages
- a shared `PAGE_SIZE` constant used both by fixture cardinality assertions and URL `skip` checks

## Verification boundary

If the backend is explicitly not ready, final verification is static-only. Report that E2E scenarios were intentionally not run and name the env flag/fixture endpoint needed to enable them later.
