# Plan-code fresh-contract E2E/proxy cleanup after review

Use this when a plan-code task removes or renames a canonical field (for example removing caller-authored Question `title`) and late review finds stale tests or helper/proxy paths.

## Pattern

1. Treat stale E2E/proxy findings as in-scope when they touch the same write/read contract, even if the implementation review already passed.
2. Search likely E2E and test-only surfaces, not just unit tests:
   - Playwright specs under `src/tests/e2e/**`.
   - Test-only API proxy routes under `src/app/api/test-only/**`.
   - E2E helper modules that seed fixtures or fill editor fields.
   - Removed selectors/test IDs (for example `question-title`) and removed form labels/textboxes.
3. Patch the test/proxy boundary to match the fresh contract:
   - Replace removed detail-title assertions with durable body/content assertions (`question-body`, body text, or another visible contract signal).
   - Update wizard/editor E2E helpers to fill the surviving content editor instead of removed title inputs.
   - Remove stale fields from test-only proxy payloads before they reach backend create/update routes.
   - Add a unit regression that the proxy payload omits the removed field.
4. Prefer durable state assertions over transient toast/control-message assertions when the UI already reflects the successful operation (for example assert `question-status-badge = Canceled` instead of a vanished `question-control-message = Updated.`).
5. Verify proportionally:
   - Run the touched proxy/unit tests.
   - Run touched Playwright specs with `--list` first if dependencies may expand the run; use `--no-deps` when auth/setup state is already present and the goal is the touched specs themselves.
   - Rerun lint/build when route/schema/E2E helper types changed.
6. Any source/test/task-doc edit after a passing review makes that review stale. Save the passing review as superseded/stale, update task docs with the post-review cleanup and verification, regenerate the final bundle, and rerun the mandatory review gate.

## Pitfalls

- Do not count an approval from before E2E/proxy cleanup as final approval.
- Do not leave test-only proxies forwarding removed fields just because production UI stopped sending them; E2E fixtures can still exercise those proxies.
- Do not blindly rerun the same failing Playwright command. Inspect the failure context: a titleless/proxy fix may reveal a separate stale transient assertion that should be replaced with a durable state assertion.
- Distinguish similarly named selectors: a removed Question detail `question-title` may be stale, while an answer-editor heading/test ID can still be an intentional adjacent UI element.
