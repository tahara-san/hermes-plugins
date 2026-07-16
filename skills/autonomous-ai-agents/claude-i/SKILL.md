---
name: claude-i
description: "Use Claude Code through subscription-friendly interactive tmux sessions; avoid `claude -p` print mode by default."
version: 1.0.1
author: Hermes Agent + local user preference
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Anthropic, Interactive, Tmux, Subscription-Friendly]
    related_skills: [claude-code, codex, opencode]
---

# claude-i — Interactive Claude Code Orchestration

Use this skill when the user explicitly asks Hermes to run, delegate to, review with, or orchestrate Claude Code through the local subscription-friendly workflow. It uses Claude Code's interactive TUI through `tmux` and avoids `claude -p` / `--print` by default.

This local skill replaces the ambiguous local `claude` skill name. Do not patch the upstream/hub/bundled `claude-code` skill just to encode this user's local subscription preference.

## Invocation Semantics in Hermes

Installed Hermes skills can expose dynamic slash commands; WebUI may not list every one in autocomplete.

Preferred user-facing invocation when the command is exposed:

```text
/claude-i
```

```text
Use claude-i to review this diff.
```

```text
Use claude-i to implement tasks/<task-name>/todo.md.
```

If `/claude-i` is not exposed on the current surface, use ordinary text such as `Use the claude-i skill to review this diff.`

Avoid broad trigger terms like bare `claude`, because they may collide with upstream `claude-code`, creative `claude-*` skills, templates, or future native commands.

### Naming and Alias Hygiene

Raw user-chat tokens can influence skill selection, so do not create broad local aliases like `claude` for this workflow. Keep the explicit name `claude-i` and prefer `/claude-i` or “Use the claude-i skill to …”. If a broad local alias already exists, migrate it by creating the explicit replacement, deleting the broad alias with `absorbed_into="claude-i"`, and verifying the skill list. See `references/naming-and-rename-hygiene.md` for the session-specific rename pattern and ambiguity pitfall.

## Core Rule

Do **not** use `claude -p` or `claude --print` unless the user explicitly asks for print mode or API-billed usage.

When Claude Code is one lane in a required multi-lane review, start its dedicated tmux session, verify the requested model/effort, and submit the immutable-bundle prompt before waiting for or monitoring any companion reviewer. Launch every required independent review lane before waiting for, polling, monitoring, adjudicating, or fixing findings from any one lane; do not run Claude Code to completion and only then launch Codex.

Default to one of these inside a managed `tmux` session:

```bash
claude
claude "initial prompt"
claude --model fable --fallback-model opus --effort xhigh  # Fable 5 default; latest Opus fallback
claude -c
claude -r <session-id-or-name>
```

## Prerequisites

- Claude Code installed: `npm install -g @anthropic-ai/claude-code`
- User has authenticated interactively with subscription/OAuth: run `claude` once and complete login.
- `tmux` available.
- `claude-i` is this workflow/skill name, not normally a shell executable. For plan-code review-gate availability checks, do **not** fail just because `command -v claude-i` is empty; confirm `tmux` and `claude` instead, then run interactive Claude Code through `claude` in tmux.
- Check status when needed:
  ```bash
  claude auth status --text
  claude --version
  claude doctor
  ```
- Authentication is scoped to the execution context/user running `claude`. If the user says Claude Code works on their host but Hermes reports `Not logged in`, first re-check `claude auth status --text` in Hermes' actual shell before asking for action. If still unauthenticated, offer two credential-safe paths: the user runs `claude auth login` in that same context, or the user runs the required interactive review on their already-authenticated host and provides the saved verdict artifact. Never ask the user to paste credentials, tokens, cookies, or OAuth secrets.

## Standard Hermes Workflow

### 1. Pick a stable tmux session name

Use a short project/task-specific name. Avoid collisions by including a timestamp or task slug.

```bash
tmux new-session -d -s claude-impl -x 160 -y 48
```

### 2. Launch Claude Code interactively in the project

Preferred: start Claude first, then paste the task after the TUI is ready.

```bash
tmux send-keys -t claude-impl 'cd /path/to/project && claude' Enter
```

Alternative with an initial prompt, still **without `-p`**:

```bash
tmux send-keys -t claude-impl 'cd /path/to/project && claude "Review the current git diff and identify correctness issues."' Enter
```

### 3. Handle first-run dialogs

Capture the pane before sending blind keys:

```bash
tmux capture-pane -t claude-impl -p -S -80
```

Common dialogs:

- Workspace trust: default is usually “Yes, I trust this folder”; press `Enter`.
- Permission mode: prefer normal or auto-accept modes based on task risk; do not use `--dangerously-skip-permissions` unless the user explicitly approves.

### 4. Send prompts safely

For one-line prompts, use literal send-keys:

```bash
tmux send-keys -t claude-impl -l 'Implement the fix described in tasks/foo/todo.md. Follow AGENTS.md. Do not commit.'
tmux send-keys -t claude-impl Enter
```

For multiline prompts, write a temporary prompt file and paste it into tmux. This avoids shell quoting bugs and preserves Markdown/code blocks.

```bash
cat > /tmp/claude-task-prompt.md <<'EOF'
Implement the plan in tasks/foo/todo.md.

Rules:
- Follow AGENTS.md.
- Run focused tests.
- Do not commit unless explicitly asked.
- Report files changed and verification output.
EOF

tmux load-buffer /tmp/claude-task-prompt.md
tmux paste-buffer -t claude-impl
tmux send-keys -t claude-impl Enter
```

### 5. Monitor progress

```bash
tmux capture-pane -t claude-impl -p -S -120
```

Status hints:

- `❯` prompt/input box visible: Claude is waiting for input or finished the turn.
- Tool activity lines / spinner: Claude is still working.
- Permission prompt visible: decide whether to approve, deny, or modify based on user intent and safety.

Do not kill a slow Claude Code session just because it is quiet. Capture more pane history or wait/poll first.

### Effort/model confirmation for requested review gates

When the user requests a specific Claude Code model/effort, verify the TUI banner/status line before sending the substantive prompt. For this user's planning workflows, use Claude Code Fable 5 with xhigh effort for review gates unless the user explicitly selects another model for the current task/session. Launch with `claude --model fable --fallback-model opus --effort xhigh`: the aliases select the latest available Fable and, only when Fable is unavailable, the latest available Opus. A fallback is allowed, but the actual banner/model must be recorded in the review artifact. If neither Fable nor the latest Opus can run at xhigh effort, fail closed or obtain an explicit override.

1. Open `/model` when changing model, or `/effort` when changing effort.
2. Move the selector deliberately one key at a time, then capture the pane before confirming so the cursor is visible on the intended option.
3. Prefer control-key movement (`C-n`/`C-p`) if arrow-key `Down`/`Up` appears not to move in tmux.
4. Confirm session-only with `s` for task-specific overrides, then capture again to verify the banner/status changed (normally `Fable 5 with xhigh effort`; `Opus` is allowed only as the recorded automatic fallback).

Do not assume a combined key sequence such as `Down s`, `Right Enter`, or `Enter` moved the selector; it can confirm the old value. If Claude reports a model other than Fable 5 or the latest available Opus fallback, reopen `/model`, capture the intended cursor, and retry before counting the review. If Fable 5, its latest Opus fallback, or the requested xhigh-effort setting cannot be selected, fail closed or obtain explicit user approval for a substitution before counting the review leg; documentation alone is not sufficient to satisfy the gate.

### 6. Send follow-ups

```bash
tmux send-keys -t claude-impl -l 'Now run the relevant tests and fix any failures.'
tmux send-keys -t claude-impl Enter
```

Useful interactive slash commands inside Claude Code:

```text
/status
/context
/cost
/compact focus on remaining implementation work
/review
/security-review
/exit
```

### 7. Verify independently in Hermes

Claude Code self-reports are not enough. After Claude says it is done, Hermes must verify with real tools:

```bash
git diff --stat
git diff --check
# project-specific focused tests/builds
```

Read changed files or run tests directly from Hermes before telling the user the result is complete.

### 8. Clean up when done

Ask Claude to exit cleanly, then kill the tmux session if it remains.

```bash
tmux send-keys -t claude-impl '/exit' Enter
tmux kill-session -t claude-impl
```

## Permission Guidance

Prefer Claude Code’s interactive permission prompts over blanket bypass.

Safe defaults:

- Read-only review: approve file reads and harmless inspection commands.
- Implementation: approve edits in the intended project scope and focused test commands.
- Dangerous operations (`rm -rf`, credential access, force push, production deploys): deny or ask the user.
- Git commits/pushes: only if the user explicitly asked.

Avoid these flags by default:

```bash
--dangerously-skip-permissions
--permission-mode bypassPermissions
```

If the user explicitly wants faster autonomous editing, prefer Claude Code’s interactive permission configuration (`/permissions`, Shift+Tab permission modes) rather than `-p` automation.

### Read-only reviews: prevent stale-session side effects

Even when the prompt says "read-only" and "do not edit", treat Claude Code as an interactive agent process that may still have queued or stale instructions in an older tmux session. Before starting a new review for a repo, run `tmux ls` and close/kill old Claude sessions for that repo/task. After the review verdict is captured, exit or kill the session immediately, then verify `git status --short --branch` and `git diff --name-status` from Hermes before staging or committing. If any files changed unexpectedly, do not rationalize the review as clean: capture the pane as contaminated/stale evidence, kill the session, restore only out-of-scope paths, rerun affected verification, regenerate the bundle from the cleaned tree, and rerun the required review leg or record an explicit waiver.

### Review-Only Pattern Without `-p`

When the user requests a review of a full behavior/control/render flow, do not prompt Claude with only `git diff`. First build a self-contained full-flow bundle containing the relevant current source files, tests, adjacent comparable components, task/spec docs, verification evidence, and the intended behavior contract. Ask Claude to review that bundle read-only and to judge the full flow, not just changed lines.

When the user asks for a **diff-only** review after PRs/commits already exist, keep the scope narrower than a full plan-code bundle: build fresh base-to-head diff bundles (`git diff base...HEAD` plus status/stat/name-only and verification notes), ask for `VERDICT / BLOCKERS / NOTES / TESTING_GAPS`, and explicitly forbid edits/tests/builds/network. This avoids re-reviewing stale task artifacts and reduces interactive permission churn.

Interactive Claude reviews of large bundles can appear to hang while it performs repeated targeted read-only spot checks. Use a bounded review loop: approve only clearly read-only inspections that answer a specific stated uncertainty, but after a few spot checks or about 8-10 minutes ask Claude to stop further exploration and return the requested concise verdict. If a reviewer-found UI/lifecycle blocker depends on real component-wrapper semantics and the bundle only includes a mock, either include that real wrapper in the regenerated bundle or allow one bounded read-only inspection of the wrapper and record why the mock matches production. If the user has just complained about Claude review hangs or says to skip Claude for the session, honor that override until they explicitly ask to run Claude again.

```bash
tmux new-session -d -s claude-review -x 160 -y 48
tmux send-keys -t claude-review 'cd /path/to/repo && claude' Enter
sleep 5
cat > /tmp/claude-review-prompt.md <<'EOF'
Review the prepared bundle for correctness, security, data integrity, and missing tests.
Do not edit files.
Return prioritized findings with file paths and rationale.
EOF
tmux load-buffer /tmp/claude-review-prompt.md
tmux paste-buffer -t claude-review
tmux send-keys -t claude-review Enter
```

Hermes should then capture the pane, wait for completion, and independently inspect any cited findings before relaying them. For read-only review gates, save the raw pane and structured verdict artifacts from Hermes rather than asking Claude to write them; a post-verdict prompt suggestion like “Save the verdict JSON…” should be cleared with `Ctrl-U`, not submitted. Capture enough scrollback to include the explicit verdict/header; if the saved pane starts mid-output or Claude leaves an input prompt such as “save the verdict…”, record the artifact as incomplete or rerun/narrow the prompt rather than treating the partial pane as final approval. If the final answer scrolled out of tmux history, ask Claude to restate only the verdict structure without reads/edits/commands, then recapture; see `references/review-verdict-capture-recovery.md`. If the tmux session/pane disappeared before capture, recover the explicit verdict from Claude Code's local JSONL transcript store and save the transcript path in the artifact; see `references/claude-jsonl-verdict-recovery.md`. When recovering or structuring a JSONL verdict, validate the parsed fields against the raw text before marking a gate passed: normalize `BLOCKERS: none` to an empty blockers array and do not accidentally include explanatory approval prose between `BLOCKERS` and `NON_BLOCKING` as blockers. If Claude is still inside a read-only tool call after you queue a bounded “return verdict now” message, the queued text may not take effect until the tool exits; interrupt with `Ctrl-C`, then send a no-tools verdict request based only on reviewed context, and capture the resulting explicit `VERDICT` block before treating the gate as complete. After capturing a verdict, inspect the live input line before sending `/exit`; if Claude/autocomplete/queued text is sitting at the prompt (for example a suggested next action), clear it with `Ctrl-U` before exiting so the cleanup command does not accidentally submit a stale instruction. If the prompt line still visually shows the stale suggestion after clearing, do not submit anything; save artifacts from Hermes and kill/exit the session conservatively. After read-only reviews, re-check `git status --short`; Claude Code may write local permission metadata such as `.claude/settings.local.json` while approving read scopes. If it contains only review-session permission grants and is not an intended project artifact, remove it (and the empty `.claude/` directory if applicable) before reporting/staging so the review does not leave unrelated local metadata. If Claude returns a non-blocking suggestion and you implement it anyway, treat that as a post-review code change: rerun verification, rebuild the bundle, rerun Claude on the final bundle, and overwrite or remove stale Claude artifacts that describe the old code.

If a mandatory workflow gate accidentally used `claude -p` / print mode first, do not treat that artifact as satisfying an interactive `claude-i` requirement. Run the missing interactive tmux/PTY review, capture the banner/model and explicit verdict, then replace or supersede the print-mode artifact and update aggregate/task docs so they name the real review path.

### Review bundles with untracked files

For final review gates, do **not** rely on `git diff` alone when new files may be untracked: Claude will see the status entry but not the file contents, causing extra permission prompts and incomplete review context. Build a complete read-only bundle before launching Claude that includes:

1. `git status --short` and `git diff --stat` for each repository.
2. `git diff --no-ext-diff -- .` for tracked edits.
3. The full contents of relevant untracked files (new helpers, tests, task review artifacts, etc.), or an explicit `git diff --no-index /dev/null <file>` for each untracked file.
4. Exact verification commands/results and any known smoke blockers. When saving raw logs for quiet commands (for example `tsc --build`), append an explicit success/exit-code marker such as `RESULT: exit 0` after the command succeeds so Claude does not have to infer success from an otherwise-empty compiler log.
5. A post-write sanity check that the saved bundle contains no truncation markers such as `[OUTPUT TRUNCATED`. For large bundles, generate `git diff` via an uncapped local subprocess rather than a Hermes helper/tool-output path that may summarize or cap stdout.

Paste a prompt that tells Claude to prefer the prepared bundle and only request additional file reads for specific gaps. This reduces interactive permission churn and helps finish before Hermes/tool iteration limits. If the session is interrupted before Claude finishes, capture the pane to a markdown artifact with a clear `INCOMPLETE` verdict rather than losing the review trace.

### Plan-doc read-only review

When reviewing planning artifacts rather than implementation code, build a saved bundle that includes untracked task docs and package-script context; do not rely on `git diff` alone. Keep Claude read-only, approve only the prepared bundle read scope, and if you patch docs after Claude's first review, regenerate the bundle and rerun review before claiming approval. Save the final verdict under `tasks/<slug>/reviews/`. See `references/plan-doc-read-only-review.md` for the exact pattern.

If an interactive plan-doc review spends too long reading a large prepared bundle and never reaches a verdict, bound the review instead of waiting indefinitely: ask Claude to stop further exploration and return the requested verdict from the context already reviewed; if that prompt is queued behind a tool call, interrupt with `Ctrl-C` and send a no-tools verdict request. Save the raw pane including the interruption/recovery. If Claude still does not return an explicit verdict, save the artifact as `INCOMPLETE`/blocked rather than counting the launch as approval. See `references/plan-doc-review-stall-recovery.md` for the concise blocked-artifact pattern, including how to record the bundle path, observed model/banner, pending interactive Codex tmux session, incomplete pane artifact, and resume steps.

### Implementation-diff review bundles with untracked files

For read-only Claude review of implementation work, make the prepared bundle self-contained: include `git status`, `git diff`, `git diff --stat`, and the full contents or `git diff --no-index /dev/null <file>` output for every relevant untracked source/test/review artifact. Plain `git diff` omits untracked new files, which forces Claude to request direct repository reads and can stall behind repeated permission prompts. See `references/review-bundles-with-untracked-files.md` for a concise bundle recipe and pitfalls.

For `plan-code` delta rerounds, do not ask Claude to re-review the whole original bundle unless the delta rules require a full rerun. Build a smaller delta bundle containing the previous clean baseline summary, changed files, semantically affected unchanged files, no-baseline files, verification rerun output, and one delta-interactions section. Prompt Claude to judge both the changed content and whether the scoped delta is sufficient; unchanged carried-forward files should not be reopened unless Claude identifies a concrete coupling gap. If Claude starts broad exploration during a valid delta review, feed the prepared baseline evidence and ask for a bounded verdict from the scoped bundle.

For completed `plan-code` tasks, use `references/implementation-diff-review-plan-code.md`: bundle the implementation diff plus untracked task docs/review artifacts, save Claude's verdict under `tasks/<slug>/reviews/`, document non-blocking suggestion disposition, and do a final staged-file/whitespace check before commit.

When driving Claude from Hermes, prefer temporary prompt files under `/tmp` for paste-buffer input. If you save the prompt itself under `tasks/<slug>/reviews/` or another intended commit path, it becomes a new task artifact created after the bundle was generated; either include it in a regenerated final bundle/artifact-consistency review, or mark it explicitly as transient/superseded and keep it out of the intended commit. Do not let a post-review `claude-review-prompt.md` silently make the final reviewed bundle stale.

When review bundles or verdict artifacts are intended to be committed, also use `references/committable-review-bundles.md`: normalize trailing whitespace in generated Markdown bundles, avoid staging stale/superseded review files blindly, and run `git diff --cached --check` after the final artifact state is staged. If a late source/test/doc cleanup happens after approval, run and save a narrow delta review rather than claiming the older approval still covers the final diff.

For Buffdemy multi-repo plan-code reviews, use Claude Code Fable 5 with xhigh effort and automatic latest-Opus fallback unless the user explicitly selects another model for the task/session. Verify the Claude Code banner shows `Fable 5` or the latest available `Opus` fallback with the requested xhigh-effort setting before sending the substantive review prompt, and record the model/banner evidence in the review artifact.

Historical model-specific review references are superseded for this user’s planning workflows. An explicit user override wins for that task; verify the banner and save evidence rather than relying on stale skill wording.

### Fallback: tracked PTY when tmux is unavailable

`tmux` is the preferred orchestration layer. If it is missing and the user wants the Claude review/implementation gate completed now, either install `tmux` or run Claude Code in a Hermes-tracked PTY background process instead of falling back to `claude -p`.

Hermes PTY fallback pattern:

1. Start Claude with `terminal(background=true, pty=true)` from the target repository, e.g. `claude` or `claude "initial prompt"`; keep `notify_on_complete` off because interactive TUIs may be long-lived.
2. Use `process(action="poll")` / `process(action="log")` to read the TUI output and permission prompts.
3. Use `process(action="submit")` for one-line prompts and approvals; for multiline prompts, paste the full prompt as submitted input when the TUI is ready.
4. When Claude reports completion, verify the diff/tests independently in Hermes before updating task docs or telling the user it passed.
5. Exit Claude cleanly with `/exit`, then `process(action="kill")` only if the process remains alive.

See `references/pty-fallback-review.md` for a concise review-gate example and pitfalls from a real use.

## Implementation Pattern Without `-p`

```bash
tmux new-session -d -s claude-impl -x 160 -y 48
tmux send-keys -t claude-impl 'cd /path/to/repo && claude' Enter
sleep 5
cat > /tmp/claude-impl-prompt.md <<'EOF'
Implement the requested change in this repository.
Follow project instructions in AGENTS.md / CLAUDE.md.
Use the existing style and production-ready logic.
Run focused verification.
Do not commit or push unless explicitly asked.
When finished, summarize changed files and exact commands run.
EOF
tmux load-buffer /tmp/claude-impl-prompt.md
tmux paste-buffer -t claude-impl
tmux send-keys -t claude-impl Enter
```

## Pitfalls

1. `claude -p` / `--print` may use API/usage paths not covered by the user’s monthly subscription plan. Avoid it by default.
2. Use `/claude-i` when the current surface exposes the dynamic command. Otherwise use ordinary text such as `Use the claude-i skill to …`; do not use the retired generic dispatcher syntax.
3. `--max-turns`, `--max-budget-usd`, JSON output, and stream-json are print-mode features; do not rely on them in interactive mode.
4. Shell quoting is still a risk before text reaches tmux. Use `tmux send-keys -l` for one-liners and `tmux load-buffer` + `paste-buffer` for multiline prompts.
5. Interactive Claude can wait on permission dialogs. Always capture the pane before assuming it is stuck.
6. Tmux sessions persist after Hermes commands finish. Clean them up explicitly, especially before rerunning a review after a stale or interrupted verdict.
7. If Claude Code returns a transient provider error such as `529 Overloaded` during a mandatory review, a model-specific usage-limit prompt appears, or the TUI refuses the prompt with `Not logged in` before an explicit verdict, do not count the launch as approval. Save the pane/output as a blocked artifact with the bundle path, model banner, failure reason, and resume steps; retry the same review leg later against the same current bundle before claiming the gate is complete. If an interactive `/login` flow is needed, select the requested login method, capture the OAuth URL/code prompt, extract and present a clean unwrapped URL to the user, leave the tmux session alive waiting for the code when appropriate, and record that the review has not yet read the bundle. For Fable 5 @ xhigh reviews and their latest-Opus fallbacks, also follow `planning-workflows` → `references/plan-code-opus-review-limit-and-rerun.md` for stale companion delegates, rerun bundles, and pending-artifact sequencing.
8. A read-only review prompt is not a sandbox. Stale Claude sessions or queued follow-up prompts can still modify files later; verify the worktree after every Claude interaction and before staging.
9. Claude Code may modify files; Hermes must verify diffs/tests independently before reporting success.
10. Do not patch the upstream `claude-code` skill just to encode this local preference. Improve this local skill instead.

## Quick Checklist

- [ ] Load/use `/claude-i` when exposed, or say `Use the claude-i skill to …`, when avoiding `-p` matters.
- [ ] Start Claude Code with `claude`, `claude "prompt"`, `claude -c`, or `claude -r`, never `claude -p` by default.
- [ ] Orchestrate through tmux.
- [ ] Send prompts with `send-keys -l` or `load-buffer`/`paste-buffer`.
- [ ] Capture pane output and handle permission prompts.
- [ ] Verify results independently with Hermes tools.
- [ ] Exit/kill tmux session when complete.
