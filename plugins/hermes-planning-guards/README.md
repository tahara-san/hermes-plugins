# hermes-planning-guards

Hermes plugin for planning workflow guardrails.

## Hooks

- `pre_tool_call` — blocks direct tool access to protected `.env*` files while allowing `.env.sample` / `.env.example` and source files such as `.env.ts`.
- `pre_llm_call` — injects a reminder to log out-of-scope findings under `tasks/out-of-scope-issues/` instead of silently dropping or fixing unrelated issues.
- `post_tool_call` — tracks successful write-like tool calls that touch `tasks/out-of-scope-issues/` during the current turn.
- `pre_verify` — approximates the Claude planner Stop hook for coding turns: when a draft final response mentions issue-like language (`pre-existing`, `out-of-scope`, `follow-up`, `no-op`, `skipped`, or `code smell`) without touching an out-of-scope issue file, Hermes keeps the turn going with an instruction to log the issue or explicitly state why no issue exists.
- `transform_llm_output` — provides a visible fallback note for non-coding or otherwise non-verified turns that mention issue-like language without a logged issue file.
- `on_session_end` — clears in-memory turn tracking state.

Dependabot alert/advisory counts remain exempt from forced issue-file logging unless the user explicitly asks to triage or fix them.

## Why plugin hooks?

The original local version used shell hooks with absolute machine paths. This plugin registers hooks programmatically, so it can be installed and shared without editing path-specific config.

## Compatibility CLIs

The package also exposes module CLIs for test/debug compatibility:

```bash
python -m hermes_planning_guards.block_env_files
python -m hermes_planning_guards.out_of_scope_reminder
```

> Security note: this guard is defense-in-depth, not a sandbox or complete security boundary. It blocks obvious protected `.env*` tool targets and command text, but cannot prevent every shell indirection, glob expansion, or future tool surface. The out-of-scope tracker likewise recognizes obvious Hermes write/patch/terminal path references; it is workflow enforcement, not a complete shell parser.
