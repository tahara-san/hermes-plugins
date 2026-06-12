# Publishing checklist

Before publishing a skill or plugin from this repo:

- [ ] No secrets, tokens, credentials, private hostnames, or private workspace paths.
- [ ] No project-specific fixture users or private application names unless intentionally public.
- [ ] Every `SKILL.md` has valid frontmatter: `name`, `description`, `version`, `author`, `license`, and `metadata.hermes.tags`.
- [ ] Descriptions are 1024 characters or less.
- [ ] Supporting references are linked from a skill or manifest.
- [ ] Plugin tests pass.
- [ ] `python3 scripts/validate_skills.py` passes.
- [ ] `python3 -m pytest -q` passes.
- [ ] README/install docs mention optional dependencies and failure modes.
