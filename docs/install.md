# Installation

## Skills

> Recommended: install/copy the whole `hermes-planning-workflows` bundle. Wrapper skills such as `plan-doc`, `plan-code`, `plan-clean`, and `plan-issues` require the umbrella `planning-workflows` skill references to be present; direct single-file wrapper installs are only shortcuts when the umbrella bundle is already installed.


Install a skill by direct `SKILL.md` URL:

```bash
hermes skills install https://raw.githubusercontent.com/tahara-san/hermes-plugins/main/skills/software-development/plan-doc/SKILL.md
```

If your Hermes version supports GitHub skill taps:

```bash
hermes skills tap add tahara-san/hermes-plugins
hermes skills search plan-doc
hermes skills install <result-id>
```

## Plugin

The plugin package lives at:

```text
plugins/hermes-planning-guards
```

Install it as a user plugin according to your Hermes plugin workflow. For local development, copy or symlink that directory under your Hermes user plugin directory and restart Hermes so plugin discovery reloads it.

## Recommended install set

- `planning-workflows`
- `plan-doc`
- `plan-code`
- `plan-clean`
- `plan-issues`
- `simplify`
- `claude-i`
- `hermes-planning-guards`
