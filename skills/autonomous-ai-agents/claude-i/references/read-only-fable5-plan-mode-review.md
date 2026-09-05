# Read-only Fable 5.1 plan-mode review pattern

For this user and Buffdemy workflows, use **Fable 5.1 at xhigh effort** as the default Claude Code review model, and fall back to the latest available Opus only through an explicit interactive relaunch. Interactive Claude Code has no automatic model fallback: the print-only fallback-model flag is documented as “only works with --print”, and this workflow forbids `claude -p` / `--print`.

Use the main `claude-i` workflow:

- Launch interactive Claude Code with `claude --model claude-fable-5-1 --effort xhigh`.
- Verify the banner/status line shows `Fable 5.1` with the requested xhigh effort before sending the substantive review prompt.
- Run read-only plan/code reviews in plan mode where appropriate.
- Save the actual banner/model in the review artifact.

## Explicit Fable → Opus fallback

If Fable cannot initialize or cannot produce a qualifying review because it is unavailable or overloaded:

1. Capture and preserve the failed Fable session evidence: pane output, bundle path, attempted model/effort, and failure reason.
2. Close or supersede that failed interactive session.
3. Start a fresh interactive tmux session against the same immutable review bundle with `claude --model claude-opus-4-8 --effort xhigh`.
4. Verify and capture the actual model/effort banner before submitting the substantive review prompt.
5. Record whether Fable or Opus actually performed the review in the review artifact.
6. If neither Fable nor Opus can run at xhigh effort, fail closed unless the user explicitly waives or overrides the lane.

Do not substitute `claude -p` / `claude --print`, another noninteractive path, or a Hermes delegate for this fallback. In a parallel review gate, replace a Fable session that failed at launch/preflight with the fresh interactive Opus session before waiting on or adjudicating the companion Codex lane.
