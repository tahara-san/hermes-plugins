---
name: plan-clean
description: "Use when you need the plan-clean workflow. Classify and conservatively clean task directories and out-of-scope issue logs."
version: 1.0.0
author: Hermes Agent + tahara-san
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cleanup, planning, tasks, safety]
    related_skills: [planning-workflows]
---

# plan-clean

## Overview

This is a stable public entrypoint for the `plan-clean` workflow. The canonical workflow details live in `planning-workflows` at:

```text
references/plan-clean/plan-clean.md
```

Load and follow `planning-workflows` when you need the complete umbrella context.

## When to Use

Classify and conservatively clean task directories and out-of-scope issue logs.

## Required Behavior

1. Treat `plan-clean` as a workflow contract, not a suggestion.
2. Load or consult `planning-workflows` and its `plan-clean/plan-clean.md` reference when details matter.
3. Fail closed if a required artifact, blocker gate, review, or verification step cannot be completed.
4. Report exact files changed, verification commands/results, review artifacts, and deviations.

## Invocation

Preferred form:

```text
/plan-clean <request>
```

In WebUI or any surface where that command is not listed, write `Use the plan-clean skill to <request>` instead. Do not use the retired generic dispatcher syntax.

## Common Pitfalls

- Treating this wrapper as a separate source of truth from `planning-workflows`.
- Skipping required gates because the request looked small.
- Reporting success without durable artifacts or real verification output.
