---
name: plan-issues
description: Use when the user wants Hermes to convert logged out-of-scope issue files into task plan directories (Claude Code /plan-issues style). Scans tasks/out-of-scope-issues layouts, filters by priority, groups and deduplicates issues, resolves decisions up front, explicitly invokes the `plan-doc` workflow, and reports skipped/manual issues.
version: 1.0.1
author: Hermes Agent (migrated from Claude Code planner plugin)
license: MIT
metadata:
  hermes:
    tags: [planning, issues, out-of-scope, triage, claude-code-migration]
    related_skills: [plan-doc, writing-plans, plan-code]
---

# plan-issues

Convert out-of-scope issue logs into actionable `tasks/<task-name>/` plan documents via the `plan-doc` workflow. This is document creation only; do not implement fixes.

## Supported Source Layouts

1. Current priority-bucketed layout:
   `tasks/out-of-scope-issues/<priority>/<YYYYMMDD>_<short-kebab>.md`

   Priorities: `critical`, `high`, `medium`, `low`, `proposal`, `other`.

   Manual-tier files may live at:
   `tasks/out-of-scope-issues/<priority>/manual/<YYYYMMDD>_<short-kebab>.md`
   These require human handling: surface them but do not auto-plan or remove.

2. Legacy flat layout:
   `tasks/out-of-scope-issues/<short-kebab>.md`

3. Single-file layout:
   `tasks/out-of-scope-issues.md`

## Usage

```text
/plan-issues [priority...]
```

Priority filters may be comma- or space-separated. If no filter is supplied, process all priorities.

## Procedure

### Step 1: Locate Issues

1. Find project root with `git rev-parse --show-toplevel 2><null-device> || pwd`.
2. Parse priority filters; ignore invalid tokens with a warning.
3. Discover issue files with `search_files('*.md', target='files', path='<root>/tasks/out-of-scope-issues')`; also check `tasks/out-of-scope-issues.md`.
4. Resolve priority:
   - Recognized priority subdir is authoritative.
   - `<priority>/manual/` resolves to parent priority and is manual-tier.
   - Unrecognized subdir is skipped with warning.
   - Flat/single-file entries use `Severity:`; missing or invalid defaults to `other` with warning.
5. Deduplicate partial migration overlap: if flat and priority-bucketed versions share the same kebab after stripping an optional date prefix, prefer the priority-bucketed file and leave the flat file untouched.
6. Skip files/sections whose only purpose is tracking GitHub Dependabot alerts or security advisory counts; Dependabot is already tracked in GitHub. If the user explicitly asks to triage/fix Dependabot, use GitHub/`gh`/`npm audit` as the source of truth instead of project issue files.
7. Apply the user's priority filter exactly.
8. If no matching issues remain, report and stop.

### Step 2: Read and Normalize

Normalize each issue to:
- source path / section
- resolved priority
- issue description
- location
- severity
- context
- suggested fix

For single-file layout, split by issue headings (`##` / `###`) or horizontal rules. If ambiguous, ask once.

### Step 3: Deduplicate Against Existing Tasks

Read existing `tasks/<task>/spec.md` or `todo.md` files. Skip issues already covered by a task. Keep skipped sources in place and report them.

### Step 4: Group Issues

Group low/proposal/small issues only when they share a theme and surface area. Keep separate any medium+ severity, architectural, multi-subsystem, or non-trivial issue.

Each group becomes one `plan-doc` task.

### Step 5: Generate Task Names

Derive max 4-5 word kebab-case names. Strip leading `YYYYMMDD_` from source filenames.

### Step 6: Up-Front Decision and Manual-Handling Gate

For each group, identify open decisions and manual-handling needs using the same categories as `plan-doc`.

Batch questions across groups with `clarify` where possible. Prefix each question with the group task name. Record answers keyed by group.

If there are no open decisions, state that and continue.

### Step 7: Invoke plan-doc Per Group

For each group, run the `plan-doc` workflow using a composed task description containing:
- issue summaries
- locations and severities
- suggested fixes
- source references
- `## Pre-resolved Decisions` block if Step 6 captured answers
- `## Manual-Handling Notes` block if relevant
- hard rules: no migration/backward-compatibility code unless explicitly requested; prefer direct elegant fixes

In Hermes, this means **load the `plan-doc` skill** and use its behavior directly in this session. Create the corresponding `tasks/<task-name>/` files through that workflow rather than hand-writing a weaker substitute. Every generated plan must run the **Hermes delegated review** as a fresh `delegate_task` reviewer using GPT 5.6 Sol @ xhigh effort. Never invoke, install, probe, or authenticate a local Codex executable; Claude Code is the separate CLI-based review lane through `claude-i`.

### Step 8: Source Issue Cleanup Policy

Default Hermes migration behavior: do not remove source issue logs unless the user explicitly requested cleanup/removal as part of this run.

If cleanup is explicitly requested, remove only issues whose `plan-doc` task completed successfully. Never remove:
- filtered-out issues
- skipped/already-covered issues
- warning/unrecognized-subdir issues
- partial-migration overlaps
- manual-tier files

Use concrete resolved paths only and verify every deletion is inside `<project-root>/tasks/`.

### Step 9: Final Report

Report:
1. Issues found with per-priority breakdown.
2. Filter result if a priority filter was applied.
3. Already-covered issues skipped.
4. Warning/skipped files, including Dependabot-tracking duplicates skipped because GitHub is the source of truth.
5. Cross-priority duplicate kebabs.
6. Manual-tier issues skipped.
7. Groups created and source files mapped into each.
8. Decisions captured and manual-handling notes.
9. Paths to new task directories.
10. Source issue files/sections removed, or state that none were removed.

### Step 10: Emit Kickoff Prompt

If tasks were created, emit:

```text
/plan-code @tasks/<task1>, @tasks/<task2>

- Automatically start next steps/phases/tasks unless a captured decision or manual-handling step blocks progress.
- Remove task files after completing the task if cleanup is desired.
- Do not create migration/backward-compatibility code unless explicitly requested.
```

## Common Pitfalls

- Planning manual-tier files that should be parked for human handling.
- Deleting issue source files just because plans were created.
- Applying a priority filter for planning but deleting unfiltered files.
- Grouping unrelated low-severity issues into one broad, vague task.
- Re-asking decisions already resolved in the plan-issues gate when invoking plan-doc.
- Planning or refreshing Dependabot/security advisory count issue files; Dependabot alerts are already tracked in GitHub unless the user explicitly asks for triage/fix work.
