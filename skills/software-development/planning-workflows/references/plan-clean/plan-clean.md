---
name: plan-clean
description: Use when the user wants Hermes to clean a project's tasks/ directory (Claude Code /plan-clean style). Classifies task dirs and out-of-scope issue files as complete, incomplete, or ambiguous; supports dry-run; asks before deletion; deletes only confirmed paths inside tasks/.
version: 1.0.0
author: Hermes Agent (migrated from Claude Code planner plugin)
license: MIT
metadata:
  hermes:
    tags: [cleanup, planning, tasks, safety, claude-code-migration]
    related_skills: [plan-doc, plan-code, plan-issues]
---

# plan-clean

Classify and optionally remove completed task directories and stale out-of-scope issue files from `<project-root>/tasks/`.

## Core Rule

A task is complete only when every checkable item (`- [ ]`) in its plan files is checked (`- [x]`), including verification, testing, build, and QA items. Implementation done but verification pending is incomplete.

## Usage

```text
/plan-clean
/plan-clean --dry-run
```

Dry-run scans and reports only; it never deletes.

## Procedure

### Step 1: Locate `tasks/`

1. Find project root: `git rev-parse --show-toplevel 2><null-device> || pwd`.
2. Verify `<project-root>/tasks/` exists. If not, report nothing to clean.

### Step 2: Enumerate Candidates

Classify:

A. Task subdirectories: immediate dirs under `tasks/` except `out-of-scope-issues/` and hidden dirs.

B. Out-of-scope issue articles:
- `tasks/out-of-scope-issues/<priority>/<YYYYMMDD>_<short-kebab>.md`
- `tasks/out-of-scope-issues/<priority>/manual/<YYYYMMDD>_<short-kebab>.md`
- legacy `tasks/out-of-scope-issues/<short-kebab>.md`
- sections in `tasks/out-of-scope-issues.md`

Skip unrecognized nested subdirs with a warning. Never touch top-level files in `tasks/` other than section edits/deletion of `tasks/out-of-scope-issues.md` when explicitly approved.

### Step 3: Classify Task Subdirectories

For each task dir, read all `*.md` files.

Decision tree:

1. `git status --porcelain <dir>` shows uncommitted changes -> incomplete, keep.
2. `ignored-warnings.md` exists/linked and has unchecked items -> incomplete.
3. `progress.md` exists -> use the authoritative progress rule below.
4. Any unchecked `- [ ]` in plan files -> incomplete.
5. At least one checked `- [x]` and zero unchecked items -> complete candidate.
6. No checkboxes -> ambiguous unless it is clearly a stale scaffold/design artifact by the superseded-draft rule below.

Superseded-draft rule:
- If a task dir contains only design/scaffolding artifacts (for example `endpoints.md`, diagrams, or HTML visualizations) and no active `spec.md`/`progress.md`/`todo*.md`, verify against the current codebase before classifying.
- Compare the draft's intended resources/files/endpoints with live implementation, route mounting, repository exports, tests, and maintained docs. Use concrete file evidence.
- If the intended scaffold is implemented and maintained docs now exist elsewhere, classify as complete/stale cleanup candidate even when small implementation details drifted after the draft (for example server-derived fields replacing client-provided fields).
- If the implementation is only partial, no maintained docs supersede it, or the draft contains unresolved decisions, classify ambiguous/incomplete rather than deleting.
- See `references/superseded-scaffold-verification.md` for a concrete endpoint-scaffold cleanup example.

Soft downgrade: if currently complete but body text contains `TODO:`, `FIXME:`, `XXX:`, `pending`, `not yet`, `still need`, `blocker`, `blocked on`, `needs verification`, `needs testing`, `needs review`, or `awaiting`, downgrade to ambiguous and show the matched line. Treat this as evidence of a current unresolved state, not a blind substring rule: ignore matches inside already-checked checklist items, historical/context prose, or prescriptive plan guidance that describes what *would* be a blocker if encountered (for example, "missing ACL is a blocker" in an already-checked verification item). If in doubt, classify ambiguous rather than complete.

Authoritative `progress.md` rule:
- Complete only when every phase row/checklist indicates done and completion criteria have no unchecked items.
- Incomplete if any phase or completion criterion is open.
- Ambiguous if the progress format is unparseable.
- If `progress.md` proves complete, stale unchecked items in `todo-phase-N.md` are ignored but noted.

### Step 4: Classify Out-of-Scope Issues

Issue articles default to ambiguous. Promote to complete only if:
- a completed task's `spec.md` or `todo.md` references this issue path/anchor/kebab, or
- the issue body has a hard completion marker: `Status: Resolved`, `Status: Fixed`, `Status: Done`, `Status: Implemented`, or the same values case-insensitively (for example `Status: implemented`).

- Manual-tier files are recognized and classified by the same rules, but be extra conservative: default ambiguous unless a hard completion signal exists. Treat proposal-tier files with `Status: Implemented` as complete candidates even if the task directory that implemented them has already been removed; otherwise plan-clean will keep stale implemented proposal notes forever.
- For hard completion markers, accept exact values (`Status: Implemented`) and brief annotated values that start with a completion word, such as `Status: implemented in tasks/foo` or `Status: fixed by <commit>`. Do not accept unrelated prose where the completion word appears later in the sentence.

### Step 5: Build Report

Group report as:

```text
## Complete (will delete after confirmation)
- tasks/<task-a>/ — reason

## Incomplete (will keep)
- tasks/<task-b>/ — unchecked: "Run build"

## Ambiguous (asking before any action)
- tasks/<task-c>/ — pure prose, no checkboxes
```

Include concrete paths and reasons.

### Step 6: Confirm Before Deleting

If `--dry-run`, output the report and stop.

Otherwise:
1. Output the report.
2. For ambiguous entries, ask the user which, if any, should be deleted. Default is keep.
3. Present the final will-delete list with every path explicitly spelled out.
4. Ask for final approval before deletion. Any non-approval means no deletion.

### Step 7: Delete Approved Entries

Safety rules:
- Never delete outside `<project-root>/tasks/`.
- Resolve concrete absolute paths; reject paths with `..` or globs.
- Never delete top-level files in `tasks/` except approved `tasks/out-of-scope-issues.md` cleanup.
- Refuse to delete candidates with uncommitted changes.
- Leave empty directories in place, including priority buckets.

Actions:
- Task dir: remove the approved concrete task directory.
- Issue file: remove the approved concrete markdown file.
- Single-file issue section: use `patch` to remove only the approved section; delete the whole file only if it becomes empty or only a title.

### Step 8: Final Report

Summarize:
1. Total candidates scanned.
2. Deleted count and paths.
3. Kept incomplete count and reasons.
4. User-skipped ambiguous count and paths.
5. Reminder to commit removals; do not auto-commit.

## Common Pitfalls

- Deleting a task because implementation is done while tests/build checkboxes remain open.
- Treating pure prose plans as complete without user confirmation.
- Deleting out-of-scope issue source files that have no completed task or status marker.
- Missing lowercase or proposal-style completion markers such as `Status: implemented`; status matching should be case-insensitive and include implemented proposals.
- Using broad `rm -rf tasks/*`; always use concrete approved paths.
