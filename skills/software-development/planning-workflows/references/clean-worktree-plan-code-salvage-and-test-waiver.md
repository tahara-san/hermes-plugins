# Clean-worktree plan-code salvage and explicit test-waiver pattern

Use this when a `plan-code` request asks for a new worktree from a base branch, while the current checkout is dirty and/or an old stale worktree contains useful prior task artifacts.

## Pattern

1. **Create a clean worktree from the requested base**
   - Inspect current repo state and existing worktrees/branches first.
   - If the intended worktree path exists but has broken `.git` metadata, do **not** delete or overwrite it. Treat it as a stale artifact source and create a new clean path.
   - Copy only the task docs required by the plan (`tasks/<slug>/spec.md`, `todo.md`, etc.) into the new worktree before implementation.

2. **Salvage prior implementation carefully**
   - If a stale/broken worktree contains prior implementation files, compare it against the clean base and copy only files scoped to the current task.
   - Exclude unrelated task directories, old review artifacts tied to the stale path, and unrelated source changes.
   - Regenerate verification notes and review artifacts in the new worktree; do not reuse old approval artifacts as current gates.

3. **Handle explicit user test waivers without pretending tests passed**
   - If the user says to skip actual test runs, builds, servers, E2E, or container commands, do not run Docker/Bun/npm/Playwright suites or start/restart services. Treat phrases like “wait for my go” as a hard stop after implementation/static review.
   - Still run non-invasive static hygiene checks when safe, especially `git diff --check` / `git diff --cached --check`. Remember that `git diff --check` does not inspect untracked files; pair it with a changed-file scanner built from `git diff --name-only && git ls-files --others --exclude-standard` to catch trailing whitespace, conflict markers, generated truncation markers, direct console logging, stale error-wrapper fields, and forbidden `any` escape hatches in new files.
   - In task TODO/progress docs, mark implementation items completed when implemented, but leave runtime/typecheck/test/E2E/build criteria unchecked and explicitly annotated as deferred by user instruction. Do not mark the overall task complete until verification is later approved and run.
   - In `verification.md` or a task handoff/static-review artifact, list every deferred command and say it was not executed by explicit user instruction.
   - In PR/final text, state tests were skipped/deferred, not passed.

4. **Review gates still apply, but failed or waived legs stay visible**
   - Build a fresh review bundle from the clean worktree and current diff/untracked files.
   - If a reviewer finds a blocker, save the initial failing artifact, fix narrowly, regenerate the bundle, and rerun all required review legs.
   - If a reviewer times out or wedges, do not count it as approval. Either retry with a narrower static-only bundle or record the timeout as a deviation/blocker. A manual static pass can supplement the handoff, but it is not the same as a completed mandatory independent review unless the user explicitly waived that leg.
   - When runtime verification is waived, the review prompt must say “static/read-only only” and explicitly forbid tests/builds/servers/containers so reviewers do not violate the user’s running-environment constraint.
   - Save an artifact-consistency review after final task/review artifact edits when the workflow requires it. Exclude the consistency artifact itself from its own scope.

5. **Generated review bundles are commit artifacts**
   - Before committing, stage only intended paths and run `git diff --cached --check`.
   - Normalize generated Markdown bundles for trailing whitespace and trailing blank lines if the staged check fails.

## Pitfalls

- Reusing old review artifacts from a stale worktree as if they reviewed the new branch.
- Copying unrelated task directories or old cleanup artifacts into the clean PR worktree.
- Marking verification as passed when the user explicitly waived actual test execution.
- Editing source after final review because of optional reviewer suggestions; document non-blocking suggestions instead unless you are prepared to rerun verification and all mandatory review gates.
- Writing a static-review artifact that literally includes forbidden scan needles (for example generated truncation markers, direct logging calls, or untyped escape-hatch spellings) and then scanning all changed files for those strings. Either exclude the artifact from that needle scan or phrase the artifact semantically so it does not trip its own hygiene check.
- Updating task progress after the final review without recognizing it as a post-review artifact change. If the workflow requires final artifact consistency, include the intended final progress/TODO state before review or run one last docs-only consistency check afterward.
