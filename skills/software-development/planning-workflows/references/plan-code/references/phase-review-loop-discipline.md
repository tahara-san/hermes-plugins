# Phase review loop discipline

Use this when `/plan-code` requires simplify, independent review, and Claude Code review after each phase/batch.

## Lesson

Treat the phase review gate as the union of all mandatory reviewers, not as a majority vote. If simplify says approved and Claude says approved, but the independent reviewer reports a concrete worth-addressing finding, the phase is still not ready for sign-off unless one of these happens:

1. Fix the finding.
2. Rerun the affected verification.
3. Rerun the affected mandatory review gate.
4. Only then update task TODO/progress files to complete.

Do not mark a phase complete while a mandatory reviewer has an unresolved worth-addressing finding, even if another reviewer labels similar concerns non-gating. If the finding is intentionally ignored, document it explicitly in the plan's ignored-warnings file or progress docs with rationale and user acceptance when needed.

## Concrete trigger pattern

A common failure mode in long plans:

- Phase implementation and targeted tests pass.
- Simplify returns `APPROVED`.
- Claude Code returns `APPROVED` with minor notes.
- Independent review finds a real semantic edge case.
- The agent updates progress or moves to the next phase anyway.

Correct behavior: stop phase advancement, patch the edge case, rerun targeted checks, then rerun simplify + independent review + Claude Code for the phase.

## Good status language under tool limits

If a tool-call/resource limit stops the session before the review loop is clean, report:

- phase is still `in_progress`, not complete;
- implementation/verification commands that actually passed;
- exact unresolved reviewer finding;
- exact next steps to resume.

Never imply completion just because most gates passed.
