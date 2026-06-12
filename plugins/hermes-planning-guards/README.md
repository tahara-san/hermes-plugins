# hermes-planning-guards

Hermes plugin for planning workflow guardrails.

## Hooks

- `pre_tool_call` — blocks direct tool access to protected `.env*` files while allowing `.env.sample` / `.env.example` and source files such as `.env.ts`.
- `pre_llm_call` — injects a reminder to log out-of-scope findings under `tasks/out-of-scope-issues/` instead of silently dropping or fixing unrelated issues.

## Why plugin hooks?

The original local version used shell hooks with absolute machine paths. This plugin registers hooks programmatically, so it can be installed and shared without editing path-specific config.

## Compatibility CLIs

The package also exposes module CLIs for test/debug compatibility:

```bash
python -m hermes_planning_guards.block_env_files
python -m hermes_planning_guards.out_of_scope_reminder
```

> Security note: this guard is defense-in-depth, not a sandbox or complete security boundary. It blocks obvious protected `.env*` tool targets and command text, but cannot prevent every shell indirection, glob expansion, or future tool surface.
