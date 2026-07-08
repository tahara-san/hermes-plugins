# Multi-repo backend-first task artifacts (2026-06 pattern)

Use this when the implementation lives in a secondary repo (for example backend) but the completed `tasks/<slug>/` artifacts live in the active/origin repo (for example frontend), and the user asks for the plan-commit two-step cleanup flow.

## Proven sequence

1. In the implementation repo, stage only the exact in-scope implementation/test paths.
2. Run staged readback before committing:
   - `git diff --cached --name-status`
   - `git diff --cached --stat`
   - `git diff --cached --check`
   - `git status --short --branch`
3. Commit and push the implementation repo first.
4. Read back the implementation commit:
   - `git status --short --branch`
   - `git rev-list --left-right --count @{u}...HEAD`
   - `git log --oneline --decorate -1 --name-status -- <scoped paths>`
5. In the task-artifact repo, patch `final-report.md` and `notes.md` with the implementation repo branch, commit SHA, push target, and scoped-path readback.
6. Regenerate/rerun a pre-commit artifact-consistency review over the live task docs plus implementation commit readback before staging the task directory.
7. Stage only `tasks/<slug>/` for the artifact commit. If `git diff --cached --check` fails only because generated Markdown review bundles contain trailing whitespace, normalize only those generated task artifacts, restage, and rerun the staged check.
8. Because normalization changes committed artifacts after the consistency verdict, run one final post-normalization artifact-consistency review over the staged task artifacts. Save that verdict as the canonical `reviews/final-artifact-consistency.json`.
9. Commit/push the task artifacts.
10. Only after the artifact commit is pushed and read back, dry-run and apply `git rm -r -- tasks/<slug>`, then commit/push the cleanup deletion.

## Pitfalls

- Do not leave a final report that says “No commit or push was performed” after committing the secondary repo first; patch it before artifact consistency.
- Do not let a clean secondary repo status make reviewers think the implementation disappeared; include commit readback, not just current status.
- Do not count the pre-normalization consistency verdict as final if generated bundles were edited for whitespace after it.
- Do not stage unrelated untracked task directories in the artifact repo; use exact `git add -- tasks/<slug>`.
