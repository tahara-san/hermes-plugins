# Audit inventory checkpoints

Use this reference when a `plan-code` phase is an audit/inventory rather than code implementation.

## Grep cross-checks

- Make the inventory command and the cross-check command identical. If the plan says to exclude generated directories (for example `dist/` and `node_modules/`), show that exclusion in both the TODO text and the inventory cross-check section.
- Count the runtime matches with the exact command used for the inventory, then count table rows independently. Do not rely only on a generated summary.
- Generated output directories can contain extra matches that are outside scope; do not include them silently, and do not let reviewers run a broader command than the documented one without reconciling the difference.

## Classification consistency

- If the argument expression itself contains `.catch(`, classify the argument shape as `inline-catch-array`; do not call it `bare-array` just because the top-level argument starts with `[`.
- `built-variable` should mean the Promise.all* argument is a pre-built variable (for example `jobPromises`), not an inline `.map(...)` expression.
- For nested Promise.all* calls, classify each grep match against its own argument expression. The outer call should not inherit a style violation from a nested inner call.
- If a row is `Style violation? = yes`, the proposed action should not be `none` unless it is explicitly marked out-of-scope.

## Manual checkpoints

- At a user-review checkpoint, stop after producing the audit artifacts and review result. If a clarification tool times out or suggests "use best judgement", do not advance past a plan-mandated user signoff gate unless the plan explicitly permits no-user-input decisions for that gate.
