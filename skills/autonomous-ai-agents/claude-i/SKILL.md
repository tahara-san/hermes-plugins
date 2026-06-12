---
name: claude-i
description: "Use Claude Code through subscription-friendly interactive tmux sessions; avoid claude -p / print mode by default."
version: 1.0.0
author: Hermes Agent + tahara-san
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding-agent, claude, anthropic, interactive, tmux, review]
    related_skills: [planning-workflows, plan-code, requesting-code-review]
---

# claude-i

## Overview

Use Claude Code through an interactive `tmux` session. This workflow avoids `claude -p` / `--print` by default and is intended for subscription-friendly Claude Code usage.

## When to Use

- The user asks to review with Claude Code.
- A planning workflow requires a Claude Code review gate.
- You need an interactive Claude Code implementation or review session.
- The user explicitly wants to avoid print/API-billed mode.

## Core Rule

Do not use:

```bash
claude -p
claude --print
```

unless the user explicitly asks for print mode.

## Standard Workflow

1. Start a tmux session:

   ```bash
   tmux new-session -d -s claude-review -x 160 -y 48
   ```

2. Launch Claude Code in the target repo:

   ```bash
   tmux send-keys -t claude-review 'cd /path/to/repo && claude' Enter
   ```

3. Capture the pane before sending prompts:

   ```bash
   tmux capture-pane -t claude-review -p -S -120
   ```

4. For multiline prompts, write a prompt file and paste it with tmux buffers.

5. Approve only read-only review actions for review gates.

6. Capture the final verdict to an artifact.

7. Verify any Claude claims independently with Hermes tools.

8. Exit and clean up the tmux session.

## Fable 5 / Effort Verification

When the user requires a specific Claude Code model or effort, verify the TUI banner/status line before sending the substantive prompt. If the requested model/effort cannot be selected, document the deviation and treat the gate as blocked unless the user waives it.

## Review Bundle Rule

For read-only reviews, build a self-contained bundle first. Include:

- git status;
- tracked diff;
- relevant untracked file contents;
- task/spec docs;
- verification commands and results;
- explicit intended behavior contract.

See `references/review-bundles-with-untracked-files.md`.

## Pitfalls

- Counting a partial or wedged Claude pane as approval.
- Forgetting untracked files in review bundles.
- Letting Claude edit files during a read-only review gate.
- Reporting Claude's self-report without independent verification.
- Leaving tmux sessions running after completion.
