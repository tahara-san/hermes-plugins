# hermes-plugins

Reusable Hermes Agent skills, workflow bundles, and plugins maintained by tahara-san.

## Packages in this repo

### `hermes-planning-workflows`

Contract-first planning workflows for Hermes Agent:

- `planning-workflows` — umbrella skill for planning, execution, cleanup, and issue conversion.
- `plan-doc` — user-facing wrapper for creating `tasks/<task-name>/spec.md` and TODO docs.
- `plan-code` — user-facing wrapper for executing task docs with simplify/review/verification gates.
- `plan-clean` — user-facing wrapper for conservative task-directory cleanup.
- `plan-issues` — user-facing wrapper for converting out-of-scope issue logs into dependency-ordered plans with one bounded task-local review at a time.
- `plan-commit` — commit/push workflow for completed plan-code tasks, including optional task-artifact cleanup.
- `simplify` — behavior-preserving cleanup review before independent review.
- `claude-i` — interactive Claude Code orchestration through tmux.
- `hermes-planning-guards` — plugin hooks for `.env*` protection and out-of-scope issue reminders.

## Install / use

Install individual skills from this repository with Hermes skill installation flows, or add this repository as a tap when supported by your Hermes version:

```bash
hermes skills tap add tahara-san/hermes-plugins
```

You can also install a direct skill URL, for example:

```bash
hermes skills install https://raw.githubusercontent.com/tahara-san/hermes-plugins/main/skills/software-development/plan-doc/SKILL.md
```

See [`docs/install.md`](docs/install.md) and [`docs/invocation-guide.md`](docs/invocation-guide.md).

## Repository layout

```text
skills/      Publishable Hermes skills, grouped by category.
plugins/     Installable Hermes plugins.
bundles/     Bundle manifests and docs for related skill/plugin sets.
manifests/   Machine-readable repository index files.
docs/        Human-facing installation, invocation, and development docs.
scripts/     Validation and packaging helpers.
tests/       Repo-level tests.
```

## Development

Run validation locally:

```bash
python3 scripts/validate_skills.py
python3 -m pytest -q
```

No secrets belong in this repository. Example env files may be named `.env.sample` or `.env.example`.
