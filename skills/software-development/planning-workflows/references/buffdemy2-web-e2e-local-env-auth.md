# Buffdemy2-web E2E local base URL / auth-session alignment

Use this when a `plan-code` task needs to rerun Buffdemy2-web Playwright specs from Hermes/WSL and the focused spec fails before reaching product assertions.

## Durable pattern

1. **Classify the failure boundary before editing tests.**
   - `ECONNREFUSED host.docker.internal:3000` = dev-server/base-URL environment, not product behavior.
   - `auth_token_undefined`, `forbidden_fixture_owner`, or "Session not found in Redis" from test-only fixture routes = auth/session/base-URL alignment, not necessarily a spec failure.
   - Fixture requests taking ~90s with `ioredis` DNS/timeout logs usually mean a host-run Next server is using container-only `REDIS_URL=redis://redis:6379`.

2. **Respect cookie domain + Redis session coupling.**
   Playwright storage states are not just bearer tokens; the frontend session cookie domain and Redis session store must line up with the base URL that Playwright hits. A storage state scoped to `host.docker.internal` will not authenticate `localhost`/`127.0.0.1`, and a copied/rewritten cookie may still point at a Redis session that is absent from the server the local Next process uses.

3. **If running Next on a temporary local port, override server env as well as Playwright env.**
   A host-run Next process may need:
   ```bash
   REDIS_URL=redis://host.docker.internal:6379 \
   E2E_BASE_URL=http://localhost:<port> \
   AUTH_CALLBACK_URL=http://localhost:<port>/api/auth/callback \
   AUTH_POST_LOGOUT_REDIRECT_URL=http://localhost:<port> \
   npm run dev -- -H 0.0.0.0 -p <port>
   ```
   Then run Playwright with matching `E2E_BASE_URL`. If auth provider/callback preflight still fails, record an environment blocker; do not mutate specs to bypass auth.

4. **Select the actual Playwright project before diagnosing product failures.**
   Buffdemy2-web auth specs under `src/tests/e2e/auth/` belong to the `chromium-auth` project, not the public `chromium` project. A path that exists can still report “No tests found” when paired with the wrong project because Playwright filters by project `testDir`. Use `--list` with the intended project first, for example:
   ```bash
   E2E_BASE_URL=http://localhost:<port> npx playwright test src/tests/e2e/auth/<spec>.ts --project=chromium-auth --no-deps --list
   ```

5. **Distinguish stale storage state from auth-regeneration blockers.**
   A `--no-deps` run against a reachable localhost server can reach the app but still fail fixture routes with `forbidden_fixture_owner` or `auth_token_undefined`; that proves stale/mismatched storage state, not a product assertion failure. Rerun once with configured dependencies (omit `--no-deps`) to regenerate storage state. If setup then fails at Logto with `oidc.invalid_redirect_uri` because the localhost callback URI is not registered, classify it as an auth-provider configuration blocker and keep the E2E gate partial.

6. **Prefer regenerating storage state over cookie-domain hacks.**
   Temporary cookie-domain rewrites are useful only as a diagnostic to prove the boundary. They are not a completion signal. Restore the original `.playwright/.auth/*.json` files after the probe.

7. **Stop and document when the environment cannot satisfy preflight.**
   If auth regeneration fails because callbacks point to an unreachable host or Logto rejects the callback with `oidc.invalid_redirect_uri`, or profile preflight returns 404 for seeded users on the reachable base URL, mark focused E2E as environment-blocked with the exact preflight output. Do not claim historical E2E pass as fresh evidence.

8. **Treat delayed dev-server watch notifications as hints, not proof.**
   A background process may surface a `Local: http://localhost:<port>` watch match after the server was killed or after the relevant probe already failed. Before reopening E2E status, poll the process, probe the URL, and identify the live listener on the port. If the process is exited/killed, the port is closed, or the process output itself shows profile preflight `404`, record the notification as stale and do not rerun or upgrade E2E evidence from it. If an exited process log shows useful successful probes before shutdown (for example Webpack-mode `/api/auth/authorize` or test-only routes returning 200/307), record that only as historical corroboration of the route/mode boundary; do not treat it as live server readiness or rerun E2E unless a fresh listener is present.

9. **If Next dev pages work but every App Router API route 404s, test Webpack mode before chasing auth/product code.**
   In local Next 16/Turbopack runs, `/` or profile pages can render while `/api/user`, `/api/test-only/*`, and `/api/auth/*` all return the app's HTML 404. Restart the temporary server with `npm run dev -- --webpack -p <port>` (plus the same `REDIS_URL`, `E2E_BASE_URL`, callback, and allowed-origin overrides), then re-probe a simple test-only API route and `/api/auth/authorize`. If Webpack restores API routes, classify the earlier failure as dev-server mode/cache/environment evidence, not missing route/source code.

## Artifact guidance

For explicit `plan-code`, save a short verification summary under the task `reviews/` directory with:
- static/unit commands that passed,
- each base URL tried,
- auth/session/Redis evidence,
- whether auth state was restored,
- exact remaining environment requirement (for example reachable `host.docker.internal:3000` with live Redis sessions, or regenerated auth/callback config for the reachable URL).
