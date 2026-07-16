# Read-only Fable 5 plan-mode review pattern

For this user and Buffdemy workflows, use **Fable 5 at xhigh effort** as the default Claude Code review model, with the latest available Opus as the automatic fallback.

Use the main `claude-i` workflow:

- Launch interactive Claude Code with `claude --model fable --fallback-model opus --effort xhigh`.
- Verify the banner/status line shows `Fable 5` or, only when Fable is unavailable, the latest available `Opus` fallback.
- Run read-only plan/code reviews in plan mode where appropriate.
- Save the actual banner/model in the review artifact.

Record the actual banner/model in the review artifact; if neither allowed model can run at xhigh effort, fail closed unless the user explicitly overrides the lane.
