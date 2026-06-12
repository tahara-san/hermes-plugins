# Invocation guide

Preferred explicit skill invocation:

```text
/skill plan-doc <request>
/skill plan-code @tasks/<task-name>
/skill plan-clean <request>
/skill plan-issues <request>
```

If direct `/plan-doc` style commands are unavailable in a particular Hermes surface, use the generic `/skill <name>` form above.

## Workflows

### `plan-doc`

Creates or updates `tasks/<task-name>/spec.md` plus TODO/progress docs. It should not implement code unless the user explicitly combines planning and implementation.

### `plan-code`

Reads task docs, executes tasks phase-by-phase, runs simplify/review gates, updates progress, and verifies with real command output.

### `plan-clean`

Classifies task directories and out-of-scope issue logs. It should dry-run first and delete only confirmed paths under `tasks/`.

### `plan-issues`

Converts logged out-of-scope issue files into implementation task plans. It should not fix issues inline during conversion.

### `claude-i`

Runs Claude Code through interactive `tmux` sessions. It avoids `claude -p` by default and requires independent verification after Claude reports completion.
