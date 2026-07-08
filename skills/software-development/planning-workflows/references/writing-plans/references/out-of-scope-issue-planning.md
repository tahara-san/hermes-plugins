# Out-of-Scope Issue Planning Reference

Use this when a user asks for a Claude Code `/plan-issues`-style workflow in Hermes or another agent.

## Source workflow shape

The Claude planner plugin's `/plan-issues` flow does the following:

1. Scan issue logs in these layouts:
   - `tasks/out-of-scope-issues/<priority>/<YYYYMMDD>_<short-kebab>.md`
   - `tasks/out-of-scope-issues/<priority>/manual/<YYYYMMDD>_<short-kebab>.md`
   - legacy flat `tasks/out-of-scope-issues/*.md`
   - aggregate `tasks/out-of-scope-issues.md`
2. Resolve priority from the directory when using the priority-bucket layout.
3. Treat `manual/` as parked work requiring human handling: report it, but do not plan or delete it.
4. Apply user filters such as `medium`, `critical,high`, etc.
5. Deduplicate overlapping issue files, preferring the newer priority-bucket file over legacy flat files.
6. Group issues only when they share a concern and one task is clearer than multiple tasks.
7. Create a task plan via `/plan-doc` with:
   - issue summary
   - source file references
   - locations and severities
   - suggested fixes
   - pre-resolved decisions
   - manual-handling notes
8. Remove source issue files only after successful plan-doc creation and only when that cleanup is part of the requested flow.
9. Emit a kickoff prompt for `/plan-code`.

## Hermes adaptation

If operating in Hermes rather than Claude Code:

- Save the plan under `.hermes/plans/` unless the user requests project `tasks/<task-name>/` docs.
- You may use the Hermes `writing-plans` / `plan` skills instead of invoking Claude Code.
- Keep the conceptual gates from the Claude workflow:
  - plan first
  - simplification pass before review
  - Codex-style or independent review after simplification
  - revise and re-review until clean
  - targeted tests/build in the plan
- If a local reviewer binary is unavailable, do not encode that as a durable limitation. Use another independent-review mechanism for the session and note only the successful review pattern.

## Practical checklist

- [ ] List included issue files.
- [ ] List skipped files and why (`skip` prefix, manual tier, filtered priority, duplicate).
- [ ] Explain grouping decisions.
- [ ] Inspect target code/tests before drafting.
- [ ] Include exact files expected to change.
- [ ] Include regression tests that assert machine-readable behavior, not only status codes.
- [ ] Include project-specific build/test commands.
- [ ] Include simplification -> Codex/independent review ordering.
- [ ] Do not remove source issue files unless explicitly authorized.
