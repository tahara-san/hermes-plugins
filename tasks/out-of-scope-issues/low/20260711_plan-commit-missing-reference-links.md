**Issue**

`plan-commit/SKILL.md` cites two local reference documents that do not exist, leaving dead guidance links in the skill.

**Location**

- `skills/software-development/plan-commit/SKILL.md` → `references/debug-console-hardening-commit-2026-07.md`
- `skills/software-development/plan-commit/SKILL.md` → `references/coverage-map-issue-cleanup-commit.md`

**Severity**

low

**Context**

A local-reference audit confirmed that both names are cited by the current `plan-commit` skill but neither target exists. `git show HEAD:skills/software-development/plan-commit/SKILL.md` confirmed both broken citations predate the active planning-workflow contract update, so they were not fixed inline with that change.

**Suggested Fix**

Determine whether each citation should point to an existing equivalent reference or whether the missing case-study document should be restored. Update or remove the citations, then add validation that resolves local Markdown reference paths from public skill entrypoints.
