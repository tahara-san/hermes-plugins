# Plan-code final doc reconciliation and review retry

Use this when a large `plan-code` task appears complete, but the user says “continue”, “resume”, or “continue if there are remaining tasks” after final verification/review. The goal is to distinguish actual remaining implementation work from stale task-document wording and mandatory-review artifact gaps.

## Trigger signals

- Session TODOs are complete, but live task docs still contain stale phrases such as “remaining unchecked”, “are unchecked”, “still incomplete”, “not marked complete”, or old line-number references.
- A mandatory final review leg was previously blocked by a transient resource limit (for example subagent/API 429), and the user resumes the session.
- A final reviewer approves but gives small non-blocking doc-clarity suggestions that would make task docs less misleading.

## Recommended sequence

1. **Audit before acting**
   - Check session TODO state.
   - Scan only live task docs for unchecked rows; exclude `reviews/` and `verification/` artifacts unless the task specifically asks to audit artifact contents.
   - Scan live task docs for stale open-work phrases.
   - Run `git diff --check` before and after doc edits.

2. **Patch only misleading live docs**
   - Convert stale “current open work” wording into historical framing: “At refresh creation time…” / “This was later reconciled in…”
   - Remove brittle current line-number references from historical plans; refer to checklist names or sections instead.
   - Add forward pointers from older runtime/refresh plans to the final completion refresh when old milestone text could be misread as current.
   - Do not automatically edit dated review artifacts (`static-review.md`, raw Claude panes, superseded bundles) unless they are being treated as live task docs or directly mislead a commit bundle.

3. **Regenerate a narrow final bundle**
   - Bundle the final live-doc audit output, relevant excerpts, and the exact doc diff.
   - Explicitly state that review/verification artifacts are excluded from the live task-completion audit to avoid self-referential stale-review loops.
   - Include the audit result: unchecked live docs should be `none`.

4. **Rerun required review legs after any doc edit**
   - If Codex-style review was blocked by a transient limit, retry it on resume before claiming completion.
   - If a non-blocking reviewer suggestion is implemented, previous approvals are stale; rerun both required legs against the regenerated bundle.
   - If a reviewer returns further non-blocking suggestions about excluded/historical artifacts, prefer recording them instead of applying them when applying them would create another stale-review loop and they do not affect live task correctness.

5. **Close only after final artifact save**
   - Save the Codex-style artifact and Claude/other external-review artifact.
   - Mark any retry TODO complete only after the artifact exists.
   - Run a final local audit: `git diff --check`, unchecked live-doc scan, stale phrase scan, and artifact existence check.

## Pitfalls

- Do not mark a task incomplete just because old plan bodies still contain imperative steps; if a top execution-status or dated milestone clearly frames them as historical, that can be acceptable.
- Do not claim a mandatory review passed when the reviewer hit a resource limit. Save a blocker artifact and retry on resume.
- Do not implement every non-blocking suggestion in excluded artifacts; each edit restarts the mandatory review loop.
- Treat checked rows that document backend/test-data blockers as “reconciled”, not as green browser assertions. Keep that distinction explicit in docs and final reports.
