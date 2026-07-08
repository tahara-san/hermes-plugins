# Capability-boundary `plan-code` pattern

Use this reference when executing a plan that changes an API capability boundary: anonymous vs authenticated access, cached-read vs fetch/write access, public response shape, or compatibility aliases.

## Pattern

1. **Confirm the live implementation target first.** If frontend and backend live in different repos or containers, prove which checkout is mounted/serving before editing. Record the path and branch in `tasks/<slug>/notes.md`.
2. **Turn the capability matrix into tests before implementation.** Cover each actor/state and side effect, not only response status:
   - anonymous cached valid hit succeeds;
   - anonymous uncached/stale/invalid/malformed input cannot trigger outbound fetches or writes;
   - pending/non-active users follow the anonymous/no-fetch boundary unless the spec explicitly allows them;
   - active authenticated users can perform the gated fetch/write path;
   - compatibility endpoints keep their previous stricter auth posture when retained.
3. **Assert absence of side effects.** Use mocks/spies for outbound clients and direct repository/DB counts for writes. A 404/401 alone is not enough proof that no scraper, network client, or persistence path ran.
4. **Gate writes immediately before the dangerous operation.** Place the auth/capability check in shared helper logic directly before origin-IP lookup, scraper/fetch client calls, and repository create/update calls. Do not rely solely on route shape if another compatibility route can reuse the helper.
5. **Return public shapes only.** When a save or normalization step fails after a successful fetch, fail closed or explicitly sanitize. Never return raw pre-save objects that may contain internal fields such as origin IPs, diagnostic metadata, credentials, or provider payloads.
6. **Review findings become RED tests.** When an independent review finds a boundary bug, reproduce it with a failing test before fixing. After the fix, rerun tests/build, live probes if applicable, regenerate the review bundle, and rerun review so the saved artifact is not stale.
7. **User overrides to the compatibility contract reset the gate.** If the user changes the decision after an implementation pass (for example from “keep a strict-auth compatibility endpoint” to “remove it”), treat that as a new contract: update spec/TODO/notes first, add a RED test for the old endpoint’s absence/no-side-effects, remove or migrate known callers, rerun focused build/tests/live probes, and rerun review on the final bundle.
8. **Cheap non-blocking review suggestions should be folded in before finalizing.** If a passed review suggests small acceptance-matrix tests, add them, rerun verification, regenerate the bundle, and rerun the final review rather than leaving obvious coverage gaps.
9. **Keep final review bundles free of stale artifacts.** When regenerating a review bundle after multiple review passes, exclude prior review verdict JSON/markdown from the bundle unless they are explicitly the subject of review; old verdicts can contain obsolete test counts or superseded acceptance criteria and confuse the reviewer. Include explicit caller-scan output instead of relying only on prose summaries when endpoint removal/migration is part of the contract.
10. **Scan live tests for removed capability symbols.** When deleting auth/cache helpers, exports, routes, or public capability names, run a live source+test symbol scan for the removed identifiers and include the results in the bundle. Stale tests outside the initially touched file list can still import deleted exports or assert the removed public behavior; rewrite or delete those tests before final review, then rerun focused tests/build and regenerate the bundle.

## Suggested task-doc evidence

Record in `notes.md` and `todo.md`:

- live repo/container path and whether a restart/reload was needed;
- RED test output before implementation, after user-driven contract overrides, and after reviewer-driven regression additions;
- final GREEN focused tests/build output;
- live probes proving cached anonymous success, anonymous miss no-write, active-auth fetch/write success, and absence/no-side-effects for any removed compatibility endpoint;
- explicit caller-scan evidence when a route is removed or callers are migrated;
- independent review artifact path and verdict;
- any stale out-of-scope issue removed because live code inspection proved the risk no longer applies.
