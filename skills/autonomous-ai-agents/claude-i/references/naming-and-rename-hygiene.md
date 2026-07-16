# Naming and Rename Hygiene for `claude-i`

Session learning: raw tokens in user chat can trigger skill loading/selection, so a broad local skill name like `claude` is too ambiguous. It can collide with upstream `claude-code`, creative `claude-*` skills, templates named `claude.md`, or future native commands.

## Durable rule

Use the explicit local skill name `claude-i` for the subscription-friendly interactive Claude Code workflow.

## Rename pattern used

When a broad alias exists locally:

1. Create the replacement class-level skill with the explicit name (`claude-i`).
2. Copy/adapt the same workflow content, replacing generic-dispatcher invocation text with `/claude-i` and adding ordinary-text loading for surfaces without a dynamic command.
3. Delete the broad local skill with `absorbed_into="claude-i"` so curator/downstream references can understand the consolidation.
4. Verify the autonomous-agent skill list shows `claude-i` and no local `claude` skill.
5. Update durable user preference memory to reference `/claude-i` or ordinary-text `claude-i` loading.

## Pitfall

If `skill_view("claude")` is ambiguous, load by categorized path such as `autonomous-ai-agents/claude` before migrating. Ambiguity is itself evidence that the bare name is unsafe.
