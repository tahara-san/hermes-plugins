# Plan-code phase review blocker fix + rerun pattern

Use when a mandatory plan-code review leg returns `CHANGES_REQUIRED` against a bundle that is already stale or superseded, but its concrete findings still apply to the current tree.

## Pattern

1. **Save the stale verdict as superseded, not active approval/failure.**
   - Record the delegation/session id, reviewed bundle path, return time, and why the bundle is stale.
   - Preserve the reviewer's concrete findings for adjudication.

2. **Adjudicate findings against the live tree.**
   - Do not dismiss a stale review solely because the bundle is stale.
   - For each concrete data-integrity/security/correctness finding, inspect current source/tests and decide whether it still applies.

3. **Fix valid blockers with TDD.**
   - Add focused RED regressions for every accepted blocker.
   - Confirm the tests fail for the product reason, then patch minimally.
   - Prefer narrow tests in existing phase-focused suites.

4. **Rerun proportional verification.**
   - Rerun impacted focused suites and builds.
   - If shared packages/routes are touched, rerun dependent app builds/suites as required by the task docs.

5. **Rerun `/simplify` after the fix.**
   - Save a fresh simplify artifact.
   - If no code cleanup is warranted, say so explicitly and include static/diff hygiene evidence.

6. **Regenerate the final bundle from the current tree.**
   - Exclude historical/stale review artifacts from active source judgment unless included only for disposition.
   - Include the superseded blocker artifact and fresh simplify/verification evidence.
   - Validate the bundle has no truncation/cache placeholders.

7. **Rerun every mandatory review lane.**
   - Prior approvals are stale after source/test/task-doc edits.
   - A fresh Codex-style delegate can run while the required Claude Code Opus 4.8 @ xhigh effort lane is blocked, but the phase remains incomplete until all mandatory lanes pass or the user explicitly waives/replaces one.

## Blocked reviewer artifacts

If an interactive Claude Code Opus 4.8 @ xhigh effort lane is blocked before reading the bundle (for example `Not logged in · Please run /login`):

- Save raw pane output and a structured blocker artifact.
- Record the actual model/banner observed.
- State that no verdict was produced and the bundle was not reviewed.
- Keep the phase incomplete; do not mark the review TODO complete.
- Resume by completing login and rerunning the same lane against the current regenerated bundle.

## Completion rule

Do not mark a phase complete after fixing stale-review blockers until:

- all post-fix verification passes,
- fresh simplify is saved,
- the final bundle is regenerated,
- all mandatory review lanes pass on that regenerated bundle, and
- no source/test/task-doc changes occur after those approvals.
