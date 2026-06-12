# Development guide

This repo is intended as an extensible monorepo for Hermes extensions.

## Add a skill

Place it under:

```text
skills/<category>/<skill-name>/SKILL.md
```

Supporting files should live under one of:

```text
references/
templates/
scripts/
assets/
```

Then update:

- `manifests/index.yaml`
- a package manifest under `manifests/` if the skill belongs to a bundle
- bundle docs if relevant

## Add a plugin

Place it under:

```text
plugins/<plugin-name>/
```

Recommended structure:

```text
plugin.yaml
README.md
pyproject.toml
<python_package>/
  __init__.py
  plugin.py
tests/
```

## Validate

```bash
python3 scripts/validate_skills.py
python3 -m pytest -q
```
