# Plan Skill Invocation and Sharing Notes

## Context

The planning workflows may exist in two forms at the same time:

1. An active class-level umbrella skill, currently `planning-workflows`.
2. Migrated focused entrypoints such as `plan-doc`, `plan-code`, `plan-clean`, `plan-issues`, and `writing-plans` stored as reference `.md` files under the umbrella.

This can make inventory/publishing work confusing: `hermes skills list` reports active top-level skills only, while `skill_view("plan-doc")` can still resolve a migrated flat `plan-doc.md` reference file because the skill loader supports legacy flat `<name>.md` lookup under the skills tree.

## Practical Invocation Guidance

For a user who wants the focused workflow, prefer the explicit generic skill form:

```text
/skill plan-doc <request>
/skill plan-code <request>
/skill plan-clean <request>
/skill plan-issues <request>
```

Do not assume direct slash aliases such as `/plan-doc` are registered merely because `skill_view("plan-doc")` succeeds. Direct dynamic slash commands are generated from active `SKILL.md` entries; in the consolidated layout the direct command is usually `/planning-workflows`, not `/plan-doc`.

If the user writes `skill /plan-doc <request>` or similar, treat it as intent to load `plan-doc`, but prefer to correct the durable recommendation to `/skill plan-doc <request>`.

## Inventory and Publishing Guidance

When inventorying local skills for sharing:

- Include active top-level skills from `hermes skills list`.
- Also inspect umbrella `references/` directories for migrated focused entrypoints with frontmatter `name:` values.
- Do not report archived original skills as simply “gone” if an active umbrella has preserved their reference content.
- For frequently used focused workflows, recommend publishing both:
  - the umbrella skill as the canonical class-level package; and
  - lightweight wrapper/alias skills for discoverability, if direct `/plan-doc` style UX matters.

For the planning family, public sharing should normally include `planning-workflows` plus wrapper/entrypoint coverage for `plan-doc`, `plan-code`, `plan-clean`, and `plan-issues`.