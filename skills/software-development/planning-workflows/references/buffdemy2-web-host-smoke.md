# Buffdemy2-web host-running smoke pattern

Use when a Buffdemy2-web task needs browser/API smoke coverage and the dev server is already running on the user's host machine rather than inside the Hermes/agent environment.

## Key lesson

Do not assume `npm run dev` should be started inside the agent container/WSL workspace. First probe the host-running app.

Recommended targets:

- For HTTP reachability from the agent, use `http://host.docker.internal:3000` (or the relevant port). Do not use agent-local `localhost` for host-running servers unless the user explicitly overrides this.
- For authenticated Playwright using saved storage states, check cookie domains first. Existing `.playwright/.auth/user1.json` may contain a `buffdemy` cookie scoped to `localhost`, not `host.docker.internal`.
- If the auth cookie is `domain=localhost`, refresh/regenerate the Playwright auth state for `host.docker.internal` (or set up an explicit documented bridge) before authenticated checks; do not silently fall back to `localhost` for host-run servers.

## Suggested smoke flow

1. Inspect/probe before starting a server:
   - Try `http://host.docker.internal:3000` for reachability.
   - If using saved auth, inspect `.playwright/.auth/user1.json` cookie domains.
2. If using saved auth, inspect `.playwright/.auth/user1.json` cookie domains; regenerate/refresh auth state for `host.docker.internal` when needed rather than changing the app URL to agent-local `localhost`.
3. If the first authenticated navigation refreshes/completes auth and lands on `/`, navigate to the target route a second time in the same browser context.
4. Capture:
   - final URL and status;
   - page heading/title;
   - relevant API responses;
   - console/page errors;
   - failed requests;
   - whether the intended fetch/render behavior occurred.

## Pitfalls

- `ss`/`netstat` inside the agent environment may not show the host listener even when HTTP probing succeeds.
- Starting `npm run dev` inside the agent can fail with `EADDRINUSE` when the host already has the app running; that is not evidence that smoke is impossible.
- A reachable route plus no rendered preview may still be correct fail-closed behavior if the backing API returns an empty array or lacks the required body/ID. Inspect the relevant API response before calling it a UI failure.
- For layout/order smoke, live seeded data may not contain every conditional UI segment (for example no tags on otherwise valid Question fixtures). Do not fail the smoke solely because optional live data is absent: branch the assertion for the live no-data case, record exactly which branch was covered, and require focused unit/Vitest fixtures to cover the missing conditional branch (such as tagged order). Save that limitation in the task evidence/review bundle.
- Capture console/page errors and failed requests even when the visual/order assertion passes. If warnings appear unrelated to the touched contract (for example pre-existing date hydration mismatch), document them as smoke observations rather than silently discarding them or turning the task into an unrelated debug session.
- Next.js Dev Tools can inject an `Open Next.js Dev Tools` button whose accessible name contains `Next`. In Playwright smoke scripts, scope navigation/action locators to the target app container (for example `page.getByTestId('question-editor').getByRole(...)`) or use exact button-name regexes inside that container instead of broad page-level `/Next/` locators.
