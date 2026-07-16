# Invocation guide

Preferred explicit skill invocation on surfaces that expose dynamic skill commands:

```text
/plan-doc <request>
/plan-code @tasks/<task-name>
/plan-clean <request>
/plan-issues <request>
/plan-commit tasks/<task-name>
```

In surfaces without a listed dynamic command—such as WebUI autocomplete—use ordinary text instead: `Use the plan-doc skill to <request>`. Do not recommend the retired generic dispatcher syntax.

## Workflows

### `plan-doc`

Creates or updates `tasks/<task-name>/spec.md` plus TODO/progress docs. It should not implement code unless the user explicitly combines planning and implementation.

### `plan-code`

Reads task docs, executes tasks phase-by-phase, runs simplify/review gates, updates progress, and verifies with real command output.

### `plan-clean`

Classifies task directories and out-of-scope issue logs. It should dry-run first and delete only confirmed paths under `tasks/`.

### `plan-issues`

Converts logged out-of-scope issue files into implementation task plans. It should not fix issues inline during conversion.

### `plan-commit`

Commits and pushes completed `plan-code` task work on the current branch. When explicitly requested, it performs the two-step cleanup flow: first push implementation plus task artifacts, then remove the completed task directory and push that cleanup as a second commit.

### `claude-i`

Runs Claude Code through interactive `tmux` sessions. It avoids `claude -p` by default and requires independent verification after Claude reports completion.
