---
name: plan-issues
description: "Use when you need the plan-issues workflow. Convert out-of-scope issue logs into implementation task plans without fixing them inline."
version: 1.0.4
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

This is a stable public entrypoint for the `plan-issues` workflow. The canonical workflow details live in `planning-workflows` at:

```text
references/plan-issues/plan-issues.md
```

Load and follow `planning-workflows` when you need the complete umbrella context.

## When to Use

Convert out-of-scope issue logs into implementation task plans without fixing them inline.

## Required Behavior

1. Treat `plan-issues` as a workflow contract, not a suggestion.
2. Load or consult `planning-workflows` and its `plan-issues/plan-issues.md` reference when details matter.
3. Also load and apply the `plan-doc` skill before creating any generated task docs; `plan-issues` is an issue-discovery/grouping wrapper, not a substitute for `plan-doc`.
4. Name every new generated task directory `tasks/<implementation-order>-<task-name>/`, using a zero-padded order such as `01-some-task-name`. Reuse the same number only when those tasks are safe to implement in parallel; increment the number when a task depends on an earlier implementation wave.
5. Require every generated plan's external **Codex interactive TUI review lane** to start bare `codex` in a managed `tmux` session with **GPT-5.6 SOL @ xhigh effort**, exactly as defined by `planning-workflows/references/codex-cli-review-lane.md`. Never use noninteractive `codex exec` or `codex review`: those paths cause severe timeout issues. Never use a Hermes `delegate_task` reviewer as this lane or its fallback. Claude Code is a separate interactive CLI lane run through `claude-i`.
6. Launch every required independent review lane before waiting for, polling, monitoring, adjudicating, or fixing findings from any one lane. Do not run Codex to completion and only then launch Claude Code, or vice versa.
7. Enforce mandatory out-of-scope tracking during conversion: deduplicate first; log each non-exempt finding under `tasks/out-of-scope-issues/<priority>/` or `<priority>/manual/` with **Issue**, **Location**, **Severity**, **Context**, and **Suggested Fix** in that order; exempt Dependabot-only alert/count findings; mention logged issues in the wrap-up.
8. Do not mark conversion complete unless every generated task plan was created through the `plan-doc` workflow or an explicit user waiver/blocker is recorded.
9. Fail closed if a required artifact, blocker gate, review, or verification step cannot be completed.
10. Report exact files changed, verification commands/results, review artifacts, logged out-of-scope issues, and deviations.

## Invocation

Preferred form:

```text
/skill plan-issues <request>
```

If your Hermes surface supports direct skill commands, `/`-style invocation may also be available.

## Common Pitfalls

- Treating this wrapper as a separate source of truth from `planning-workflows`.
- Skipping required gates because the request looked small.
- Reporting success without durable artifacts or real verification output.
