---
name: plan-issues
description: "Use when converting out-of-scope issue logs into dependency-ordered, independently reviewable implementation task plans without fixing them inline."
version: 1.1.0
author: Hermes Agent + tahara-san
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, issues, out-of-scope, triage]
    related_skills: [planning-workflows, plan-doc]
---

# plan-issues

## Overview

This is the stable public entrypoint for `plan-issues`. The canonical workflow lives in `planning-workflows` at:

```text
references/plan-issues/plan-issues.md
```

`plan-issues` discovers, groups, orders, and maps issue logs. It invokes `plan-doc` for the actual documents and reviews **one task at a time**. It never fixes source issues inline.

## Required Behavior

1. **Canonical source.** Load `planning-workflows`, its `plan-issues/plan-issues.md` reference, `plan-doc`, and the governing reviewer references. Do not duplicate a weaker workflow in this wrapper.
2. **Guard policy.** Deduplicate before logging. Put each non-exempt finding at `tasks/out-of-scope-issues/<priority>/[manual/]YYYYMMDD_<short-kebab>.md` with **Issue**, **Location**, **Severity**, **Context**, and **Suggested Fix** in that order. The only priorities are `critical`, `high`, `medium`, `low`, `proposal`, and `other`. Do not create or update files solely for Dependabot alerts/security-advisory counts.
3. **Graph before directories.** Build and validate the complete dependency graph before writing task directories. Stop on an unknown prerequisite or dependency cycle. Use stable kebab-case paths `tasks/<task-name>/`; keep dependency-derived `implementation_order` waves and parallel cohorts in metadata/status only. Independent safe-parallel tasks may share a wave. Reordering metadata never requires directory renaming.
4. **Generated state.** Record direct prerequisites and parallel cohort in task metadata and the compact conversion status ledger. Generate the fresh-session handoff for each task.
5. **Strict task sequencing.** The status ledger identifies exactly one current task. Do not generate or dispatch the next task's bundle until the current task is approved, explicitly waived, or durably blocked and the user authorizes moving on. Implementation-order cohorts do not permit combined review campaigns.
6. **Task-local bundle.** Require exactly one target slug, real non-symlinked `spec.md` and `todo.md`, and an explicit bounded evidence manifest that includes both and every path-shaped inline-code claim in those docs. Fail before dispatch for missing or omitted plan-named paths, directories/recursive inclusion, current-task review artifacts, duplicate files, or full neighboring plan documents. Bundle version discovery is local to that task's `reviews/` directory.
7. **Two independent lanes within one task.** For the current immutable digest, launch every required independent review lane before waiting: Codex interactive TUI GPT-5.6 SOL/xhigh in managed `tmux`, plus interactive Claude Code Opus 4.8/xhigh through `claude-i`. Preserve each complete task-local transcript, but accept it only when it contains exactly one canonical `BEGIN_REVIEW_RESULT`/`END_REVIEW_RESULT` block whose digest, mode, model, effort, and verdict exactly match the recorded lane. The helper rehashes the transcript and bundle before aggregation. Never substitute `delegate_task`, `codex exec`, or `codex review` for the Codex lane.
8. **Bounded current-only rerounds.** Save both complete results before editing when practical, consolidate blocker findings into one amendment, and rerun both lanes only after an actual authoritative-doc blocker/contradiction fix. A reround bundles the latest authoritative state plus a concise finding-to-fix delta and historical paths/digests; prior full bundles and prior raw review artifacts remain historical and are not embedded. There is no separate artifact-consistency review: chain integrity is validated mechanically in the same aggregate/status gate. The default is two total rounds: the initial review plus at most one normal reround. Preserve optional suggestions as implementation-review attention points. Stop at the configured round cap for a user-visible checkpoint.
9. **Hash-bound finality.** Archive delayed old-digest results as superseded. They cannot update current status or trigger reruns by themselves. Write `final-review.json` only when both matching current-digest lanes approve and the live authoritative docs still match. Refresh status before trusting a saved ledger so post-approval bundle/doc changes are marked stale mechanically.
10. **Dependencies.** Reference approved prerequisites through compact size-bounded frozen contracts containing only required excerpts plus approved bundle/final-aggregate identity, and include each contract explicitly in the dependent manifest. A user-authorized durable block becomes an explicit downstream gate, never approval; any other unapproved prerequisite stops bundling. Never embed a full neighboring mutable plan.
11. **Order correction and legacy adoption.** If later evidence changes the dependency graph, use the helper's metadata-only migration. It updates dependency order/cohort metadata, handoffs, and ledgers atomically; stable task paths mean no directory renaming or path-reference rewrite. Adopt existing stable legacy tasks only through the explicit reviewed definitions command, preserving `reviews/` as history without granting current approval.
12. **Completion.** Every generated task must have a plan-doc result, review state, source mapping, exact next action, and truthful blocked/waived/approved status. Report exact files, commands/results, review artifacts, deviations, and out-of-scope files created or updated.

## Workflow Helper

Use the shipped helper for mechanical state transitions:

```text
planning-workflows/scripts/plan_issues_workflow.py
```

Its CLI validates graph initialization, generates one manifest-bounded bundle, records strictly attested hash-bound lane verdicts, validates the complete bundle→transcripts→aggregate→final approval chain, freezes dependency contracts, records blocked/waived closure, updates corrected ordering metadata, and explicitly adopts mapped legacy conversions. The canonical reference contains command examples and compatibility rules.

## Invocation

```text
/skill plan-issues <request or priority filters>
```

## Common Pitfalls

- Generating every task bundle because all task docs already exist.
- Treating implementation wave order as review-round order.
- Reusing one campaign version across unrelated tasks.
- Including whole directories or another task's complete live plan.
- Editing after the first reviewer returns instead of collecting both current-digest results.
- Churning approved docs for optional polish.
- Treating an old `final-review.json` as current without live-doc and bundle binding.
- Moving past a blocked current task without explicit user authorization.
