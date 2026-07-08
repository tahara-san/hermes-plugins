# Claude Code Review Gate via Hermes PTY Fallback

Use this reference when the user explicitly wants the `claude-i` subscription-friendly workflow, but `tmux` is not available in the current execution environment and waiting to install/configure tmux would block the task.

## Durable lesson

Do not switch to `claude -p` just because tmux orchestration is unavailable. Preserve the core `claude-i` invariant: run Claude Code interactively (`claude`, `claude "prompt"`, `claude -c`, or `claude -r`) and manage the session through an interactive terminal.

## Hermes PTY fallback recipe

1. Start Claude Code from the project directory with a tracked PTY background process:
   - command: `claude` or `claude "Review the current git diff..."`
   - `background=true`
   - `pty=true`
   - no `notify_on_complete` for long-lived interactive TUI sessions
2. Poll/log the process output until the TUI is ready or a permission/trust prompt appears.
3. Submit required trust/permission responses only after reading the prompt.
4. Submit a review prompt that explicitly says:
   - review current git diff only;
   - do not edit files;
   - check correctness, security, data integrity, and missing tests;
   - return blocking findings separately from non-blocking suggestions.
5. Continue polling until Claude clearly reports a final review verdict.
6. Independently verify any cited findings and run the relevant local checks before marking a review gate complete.
7. Exit with `/exit`; kill the tracked process only if it remains alive after a clean exit attempt.

## Pitfalls

- Interactive output can include spinners and screen-control sequences; use process logs/polls rather than assuming quiet output means completion.
- `process.submit(data="$(cat /tmp/prompt.md)")` sends the literal string; it does not shell-expand. Read the prompt content yourself, paste the actual text, or start Claude with `claude "short initial prompt pointing at /tmp/review-bundle.md"`.
- Some Claude PTYs treat normal submitted newlines as text-entry rather than final submit. If a prompt is visible but not executing, send a raw carriage return with `process(action="write", data="\r")`.
- For review-only gates, Claude may still ask for shell commands. Approve only project-scope reads/harmless inspection that match the prompt; deny broader commands and provide the missing evidence manually so it can finish from the bundle/source already read.
- TUI logs can mangle or bury the verdict. If the result is noisy, ask Claude for a final one-line verdict (`APPROVED` or `CHANGES_REQUIRED`) before exiting.
- Permission prompts may require explicit approval before Claude can inspect files. Approve only project-scope reads/harmless commands for review-only work.
- Claude self-report is not sufficient evidence. Keep exact local verification commands/results in the task notes or final report.
- This is a fallback, not a replacement for tmux. If repeated Claude orchestration is expected on the machine, install/configure tmux for the standard workflow.
