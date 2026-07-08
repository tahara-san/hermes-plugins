# Buffdemy2-web E2E stabilization pattern

Use this during `/plan-code` tasks that stabilize Buffdemy2-web Playwright/Vitest suites, especially when failures mix UI drift, cleanup leakage, dev overlays, frontend/backend schema contracts, and host-running dev-server instability.

## Durable lessons

- Treat `host.docker.internal` as the default target for host-running Buffdemy2-web services from Hermes/WSL. Use `E2E_BASE_URL=http://host.docker.internal:3000` in Playwright commands and normalize explicit browser/API contexts through the shared E2E base URL constant.
- If `host.docker.internal:3000` becomes unreachable mid-suite, do not treat the resulting full run as product evidence. Probe both `http://host.docker.internal:3000` and `http://127.0.0.1:3000`, save a blocker artifact, and state whether the run reached the changed specs. If it failed before the changed specs, rely only on focused green runs for task-scoped evidence and require a restored full-suite rerun before completion.
- Make cleanup failures visible. Replace silent teardown catches with a helper that records the target being cleaned, logs enough error detail, and fails the test after teardown if cleanup did not complete. Preserve explicitly expected missing-fixture cases, but log them as expected cleanup misses. For one-off debugging probes that create data, record any failed cleanup target/id in the task artifact if the dev server dies before retry.
- Before blaming UI locators, inspect the response contract. A server-side redirect or missing rendered item may come from frontend schema validation rejecting the backend response before hydration. Probe the corresponding `/api/...` route with the same storage state and compare it to the model schema.
- Check current frontend API helpers before asserting directly against a route. For ArticleComment reads, the app translates `rootArticle` to the backend wire query `article`; a direct `/api/article-comment?id=...` assertion can be invalid even though `/api/article/{articleId}/comment` or the app helper path is correct.
- Backend tiny/reference shapes may intentionally omit display-content fields. For Buffdemy list-item article references, backend `ArticleTinyData` is metadata-only and excludes `title`, `body`, `papers`. Frontend schemas/tests should accept this and assert the current fallback UI/link when the tiny shape is all that is available.
- Prefer scoped modal/dialog locators: existing `data-testid` values or accessible dialog names. Avoid broad `page.locator('[role="dialog"]')` in tests that can collide with unrelated Radix/Next/overlay portals.
- Stale seeded data should be cleaned by safe name patterns before serial E2E flows begin, then cleaned again in `afterAll`. De-duplicate IDs when desktop/mobile duplicate links render the same list.
- Dev-overlay dismissal should never hide the root cause. Capture/print overlay text before dismissing and cover Next.js portal overlays as well as native `<dialog>` overlays.
- Clipboard E2Es that run against `http://host.docker.internal` may not have `navigator.clipboard` because the origin is not a browser secure context even after Playwright grants clipboard permissions. For copy-button tests, prefer a tightly scoped `page.addInitScript` clipboard shim inside the specific test so the app's `writeText -> success toast` path remains covered without changing production code.
- For comment-posting specs, do not accept “some POST completed” plus visible body/editor text as sufficient setup proof. Poll `/api/article/{articleId}/comment` for the exact unique comment text before the serial suite advances; otherwise transient editor content or stale success toasts can create false positives.
- Mention tests need UI-shape and caret-aware helpers. Suggestion option accessible names may concatenate username and display name (for example `@test02test02`), so match by username prefix rather than a word boundary. If helper code clicks the editor after typing existing text, it can move the caret into the paragraph and corrupt queries such as `...332@test024625`; only click when the editor is not already focused and remove redundant clicks before over-limit queries. When asserting persisted mention nodes, traverse full paper/comment objects (`papers[*].bodyNodes`, attrs, nested content) rather than only a `.content` field.
- When a browser project is blocked by missing/corrupt Playwright browser payloads or native packages, ask the user before reinstalling packages in the ephemeral Hermes container. If approved, capture the exact setup command (`npx playwright install <browser> --force`, `npx playwright install-deps <browser>`, or the minimal apt packages) in the task artifact and rerun a tiny browser launch smoke before the full project.

## Verification recipe

1. Reproduce the failing focused spec with `E2E_BASE_URL=http://host.docker.internal:3000` and save an artifact under the task directory.
2. If a fixture/API route rejects data, add a focused route/model regression first, confirm RED, then patch the smallest contract mismatch.
3. If cleanup is involved, harden teardown before broad reruns so a later pass cannot mask leaked state.
4. Rerun focused suites in layers:
   - relevant Vitest model/route regressions;
   - focused Playwright spec(s);
   - neighboring drift specs;
   - repeatability run for serial stateful specs.
- For `plan-code`, keep full-suite evidence and focused evidence separate. If the full suite aborts from dev-server availability before hitting changed specs, mark the full-suite gate blocked, do not claim in-suite coverage, and regenerate review/final artifacts so they say exactly what happened.
- If a later full-suite rerun completes red but reaches all task-touched specs and those specs are absent from the final failure list, do **not** keep reporting the old environment blocker. Reclassify the full-suite gate as completed-red due to unrelated tracked failures, save a concise artifact listing the run summary plus touched-spec reach evidence, and update `todo.md`, `final-report.md`, `final-review.json`, and any out-of-scope issue context that still points at the old blocker.
6. Document environment-only browser-project blockers separately from test failures. Missing native browser dependencies can block WebKit/mobile verification, but Chromium/API/Vitest evidence should still be recorded honestly.

## Anti-patterns

- Do not change tests to match stale task docs when the live backend contract has intentionally changed; update the task docs/spec evidence instead.
- Do not leave `test.skip()` as a cleanup fallback if an existing helper can perform the cleanup path deterministically.
- Do not encode transient missing binaries or package-install permission failures as durable rules. Capture the setup command or blocker in the task artifact, not in the skill.
- Do not let an aborted full-suite log imply changed specs passed. Parse/check the log for whether the relevant spec names or test titles were reached before citing it.
