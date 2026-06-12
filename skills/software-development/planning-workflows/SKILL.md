---
name: planning-workflows
description: "Use when planning, documenting, executing, cleaning, or converting implementation plans and task directories across Hermes-style workflows."
version: 1.0.0
author: Hermes Agent + tahara-san
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, implementation-plans, plan-mode, tasks, execution, cleanup]
    related_skills: [plan-doc, plan-code, plan-clean, plan-issues, simplify, claude-i, requesting-code-review, subagent-driven-development, test-driven-development]
---

# Planning Workflows

## Overview

This umbrella skill covers a family of contract-first planning workflows:

- writing implementation plans;
- creating structured task documents;
- executing existing plans phase-by-phase;
- converting out-of-scope issue logs into task plans;
- cleaning completed task directories conservatively.

It is the canonical source of truth for the `plan-doc`, `plan-code`, `plan-clean`, and `plan-issues` wrapper skills in this repository.

## When to Use

- The user wants a plan instead of implementation.
- The user asks to create `tasks/<task-name>/` planning documents.
- The user asks to execute an existing plan.
- The user asks to convert issue logs into task plans.
- The user asks to classify or clean task directories.
- The user asks for an implementation plan for another agent or developer.

## Entrypoints

Use the wrapper skill that matches the user's intent:

| Wrapper | Use for |
|---|---|
| `plan-doc` | Create/update task docs before implementation. |
| `plan-code` | Execute existing task docs with simplify/review/verification gates. |
| `plan-clean` | Classify and clean completed task directories. |
| `plan-issues` | Convert out-of-scope issue files into task plans. |

If a direct slash command is unavailable in a surface, use the generic form:

```text
/skill plan-doc <request>
/skill plan-code @tasks/<task-name>
```

See `references/plan-skill-invocation-and-sharing.md`.

## Core Contracts

### `plan-doc`

1. Stop before code changes unless the user explicitly authorizes implementation.
2. Create or update `tasks/<task-name>/spec.md`.
3. Create or update `todo.md`, `progress.md`, or phase TODO files.
4. Include goal, scope/out-of-scope, acceptance criteria, decisions/open gates, implementation phases, verification commands, review gates, and manual-handling notes.
5. Emit a copy-pasteable kickoff prompt for `plan-code`.
6. If review is mandatory, save review artifacts under `tasks/<task-name>/reviews/`.

Detailed reference: `references/plan-doc/plan-doc.md`.

### `plan-code`

1. Read task docs before editing implementation files.
2. Execute TODOs phase-by-phase.
3. Update progress as work completes.
4. Run simplify after implementation changes.
5. Run independent review gates before completion when required.
6. Run verification commands with real output.
7. Report completed phases, verification results, review verdicts, remaining risks, and deviations.

Detailed reference: `references/plan-code/plan-code.md`.

### `plan-issues`

1. Discover issue files under `tasks/out-of-scope-issues/`.
2. Filter exactly according to the user's request.
3. Deduplicate related findings.
4. Convert included issues into task docs via `plan-doc`.
5. Report skipped/manual issues separately.
6. Do not fix issues inline during conversion.

Detailed reference: `references/plan-issues/plan-issues.md`.

### `plan-clean`

1. Dry-run first.
2. Classify task directories as complete, complete-with-caveat, incomplete, ambiguous, or parked/deferred.
3. Inspect task docs and current code/tests when classification is uncertain.
4. Delete only confirmed paths under `tasks/`.
5. Keep ambiguity unless the user explicitly resolves it.

Detailed reference: `references/plan-clean/plan-clean.md`.

## Cross-Cutting Rules

- Planning output must be concrete enough for another capable agent to execute without rediscovery.
- Do not hide unresolved decisions; mark them as gates.
- Preserve out-of-scope findings for later triage instead of silently dropping them.
- Execution claims require real test/build/tool output.
- Cleanup is conservative: ambiguity means keep or ask, not delete.
- If code, tests, docs, or review artifacts change after a review, the review may be stale; rerun impacted verification/review before claiming completion.

## Supporting References

- `references/writing-plans/writing-plans.md` — general implementation-plan writing method.
- `references/plan-doc/plan-doc.md` — task-document creation workflow.
- `references/plan-code/plan-code.md` — plan execution workflow.
- `references/plan-clean/plan-clean.md` — task cleanup workflow.
- `references/plan-issues/plan-issues.md` — issue-to-plan conversion workflow.
- `references/plan-skill-invocation-and-sharing.md` — why wrappers exist and how to publish/call them.
- `references/generic/` — cross-cutting workflow patterns.

## Verification Checklist

- [ ] The correct mode was selected from the user's request.
- [ ] Plan/task docs include paths, commands, tests, acceptance criteria, and gates.
- [ ] Execution updated progress and verified with real outputs.
- [ ] Cleanup used dry-run/classification before any deletion.
- [ ] Any required review gate has a saved verdict artifact or an explicit blocker/waiver.
