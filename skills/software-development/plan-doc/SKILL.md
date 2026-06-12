---
name: plan-doc
description: "Use when you need the plan-doc workflow. Create or update task planning documents before implementation."
version: 1.0.0
author: Hermes Agent + tahara-san
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, task-docs, workflow]
    related_skills: [planning-workflows]
---

# plan-doc

## Overview

This is a stable public entrypoint for the `plan-doc` workflow. The canonical workflow details live in `planning-workflows` at:

```text
references/plan-doc/plan-doc.md
```

Load and follow `planning-workflows` when you need the complete umbrella context.

## When to Use

Create or update task planning documents before implementation.

## Required Behavior

1. Treat `plan-doc` as a workflow contract, not a suggestion.
2. Load or consult `planning-workflows` and its `plan-doc/plan-doc.md` reference when details matter.
3. Fail closed if a required artifact, blocker gate, review, or verification step cannot be completed.
4. Report exact files changed, verification commands/results, review artifacts, and deviations.

## Invocation

Preferred form:

```text
/skill plan-doc <request>
```

If your Hermes surface supports direct skill commands, `/`-style invocation may also be available.

## Common Pitfalls

- Treating this wrapper as a separate source of truth from `planning-workflows`.
- Skipping required gates because the request looked small.
- Reporting success without durable artifacts or real verification output.
