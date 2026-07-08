# Buffdemy2-web post-final E2E automation in plan-code

Use when a Buffdemy2-web `plan-code` task has already reached final review/artifact-consistency, then the user asks to automate a previously documented manual/browser smoke or add E2E coverage for the same UI contract.

## Pattern

1. Treat the new E2E/smoke as an in-scope post-final test change, not as a harmless documentation follow-up. Any source/test/task-doc edit after final review makes the aggregate review and artifact-consistency verdict stale.
2. Reuse the nearest existing E2E that already creates the needed live fixture before adding a new broad spec. For Question Buff modal coverage, `src/tests/e2e/auth/questionEcoCycle.spec.ts` already creates an `openPublic` question fixture and previously covered the old Buff flow.
3. Run a RED check before patching when an existing stale E2E should fail against the new contract. For stale Buff modal selectors, the expected RED is the old raw-input selector missing, e.g. `question-buff-button-input` not found.
4. Patch adjacent unit/integration tests that still assert removed selectors in the same pass. For Buff modal, `actionbar.test.tsx` may still expect old raw-input/submit selectors even if `buffAmountButton.test.tsx` is current.
5. For authenticated Playwright on Buffdemy2-web, use the canonical host/auth pattern:
   - `E2E_BASE_URL=http://host.docker.internal:3000`
   - confirm saved storage state cookies are scoped to `host.docker.internal`
   - set the test-only hardening flag for the runner and ensure the already-running app process was started with the matching server-side flag.
6. Inspect Playwright expansion with `--list` when needed. Use `--no-deps` only when setup/auth state is already present and the goal is the touched spec itself; record that focused evidence separately from full-suite evidence.
7. Rerun proportional verification after the E2E/test change: affected Vitest files, focused Playwright spec, `check:i18n`, lint, build, and `git diff --check`.
8. Regenerate the implementation review bundle and rerun mandatory review legs. Existing `final-review.json` and final artifact-consistency verdict are stale until fresh reviews pass and the final artifact-consistency gate reruns.

## Buff modal smoke assertions to automate

For the `open public question supports additive Buff and owner controls` path:

- open `question-buff-button`;
- assert `100`, `500`, `1,000`, and `Other` options exist and start with `aria-pressed=false`;
- assert custom input is initially absent;
- select `Other`, assert input appears, and validate representative invalid values such as `100` and `1,200`;
- switch to a preset and assert stale custom validation clears;
- continue to confirmation, assert paying amount, execute, assert dialog closes and footer total updates;
- reload and assert the persisted footer total.

## Pitfalls

- Do not leave final docs claiming manual smoke was unavailable after adding a passing Playwright smoke. Update `todo.md`, `final-report.md`, and review bundles before rerunning reviewers.
- Do not count older Claude/Codex approvals or artifact-consistency verdicts after adding E2E coverage; save them as historical/stale and rerun.
- If the focused Playwright command fails due to host/app setup, classify the environment blocker with evidence before changing tests. If it fails on removed selectors, that is a valid RED signal for stale E2E coverage.
- Avoid broad full-suite claims when the command used `--no-deps`; report it as focused smoke coverage for the touched spec.