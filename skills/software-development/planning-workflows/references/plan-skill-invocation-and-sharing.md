# Plan skill invocation and sharing

Hermes installations can expose skills in several ways:

- active top-level skills in `hermes skills list`;
- generic skill loading such as `/skill plan-doc`;
- direct slash-style skill commands when the current surface registers them;
- supporting reference files loaded through an umbrella skill.

This repository publishes wrapper skills for `plan-doc`, `plan-code`, `plan-clean`, and `plan-issues` so users get stable, discoverable entrypoints while `planning-workflows` remains the canonical umbrella.

Preferred invocation:

```text
/skill plan-doc <request>
/skill plan-code @tasks/<task-name>
/skill plan-clean <request>
/skill plan-issues <request>
```

Avoid relying on bare `/plan-doc` unless your Hermes surface confirms it is registered as a direct slash command.
