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
8. Preserve source issue files after plan-doc creation; `plan-issues` is docs-only and does not delete them.
9. Emit a kickoff prompt for `/plan-code`.

## Hermes adaptation

If operating in Hermes rather than Claude Code:

- Build and validate the complete dependency graph first and fail on any cycle. Save each plan under a stable `tasks/<task-name>/` path; record dependency-derived implementation waves and safe parallel cohorts in metadata only so reordering requires no directory renaming.
- Load and invoke the `plan-doc` workflow for every included task rather than hand-writing a weaker substitute.
- Initialize the compact status ledger and handoffs with `planning-workflows/scripts/plan_issues_workflow.py`, then keep exactly one current task.
- Keep the conceptual gates from the Claude workflow:
  - plan first
  - simplification pass before review
  - exactly one target slug and one bounded explicit evidence manifest
  - bare interactive Codex in managed tmux with GPT-5.6 SOL @ xhigh and Claude Code through `claude-i`, launched before waiting on either lane for the current task
  - save both complete matching-digest results, amend authoritative docs for consolidated blocker findings at most once in the normal flow, and default to two total rounds
  - do not generate or dispatch the next task until the current task closes or the user authorizes moving past a durable block
  - bind approved prerequisites through compact size-bounded contracts included in the dependent manifest; represent an authorized durable block as an explicit gate
  - update ordering metadata transactionally without directory renaming, and adopt existing stable legacy directories only through an explicit reviewed mapping while preserving review history
  - targeted tests/build in the plan
- If a required reviewer binary, authentication, pinned model/effort attestation, or parseable verdict is unavailable, fail closed unless the user explicitly waives the lane. Never substitute `delegate_task`, `codex exec`, or `codex review` for the interactive Codex lane.

## Practical checklist

- [ ] List included issue files.
- [ ] List skipped files and why (`skip` prefix, manual tier, filtered priority, duplicate).
- [ ] Explain grouping decisions.
- [ ] Inspect target code/tests before drafting.
- [ ] Include exact files expected to change.
- [ ] Include regression tests that assert machine-readable behavior, not only status codes.
- [ ] Include project-specific build/test commands.
- [ ] Include simplification followed by same-bundle parallel launch of interactive Codex and Claude Code reviews.
- [ ] Preserve source issue files.
