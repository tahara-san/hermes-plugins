---
name: plan-code
description: "Use when you need the plan-code workflow. Execute existing task planning documents with progress updates, simplify/review gates, and verification."
version: 1.0.1
author: Hermes Agent + tahara-san
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [implementation, planning, review-gates]
    related_skills: [planning-workflows]
---

# plan-code

## Overview

This is a stable public entrypoint for the `plan-code` workflow. The canonical workflow details live in `planning-workflows` at:

```text
references/plan-code/plan-code.md
```

Load and follow `planning-workflows` when you need the complete umbrella context.

## When to Use

Execute existing task planning documents with progress updates, simplify/review gates, and verification.

## Required Behavior

1. Treat `plan-code` as a workflow contract, not a suggestion.
2. Load or consult `planning-workflows` and its `plan-code/plan-code.md` reference when details matter.
3. Require the Codex-style Hermes delegate review lane to use **GPT 5.6 Sol @ xhigh effort**. It is a fresh `delegate_task` reviewer, not a local `codex` or `npx @openai/codex` binary; record the actual model and effort in the review artifact. Fail closed on a mismatch or unavailable required lane unless the user explicitly waives it.
4. Enforce mandatory out-of-scope issue tracking: do not silently ignore or fix out-of-scope findings inline; deduplicate first, then log each non-exempt finding under `tasks/out-of-scope-issues/<priority>/` (or `<priority>/manual/` for human intervention) with **Issue**, **Location**, **Severity**, **Context**, and **Suggested Fix** sections in that order. Do not create or update an issue file solely for Dependabot alerts/security-advisory counts.
5. Fail closed if a required artifact, blocker gate, review, or verification step cannot be completed.
6. Report exact files changed, verification commands/results, review artifacts, logged out-of-scope issues, and deviations.

## Invocation

Preferred form:

```text
/skill plan-code <request>
```

If your Hermes surface supports direct skill commands, `/`-style invocation may also be available.

## Common Pitfalls

- Treating this wrapper as a separate source of truth from `planning-workflows`.
- Skipping required gates because the request looked small.
- Reporting success without durable artifacts or real verification output.
