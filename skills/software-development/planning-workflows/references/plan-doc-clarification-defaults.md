# Plan-doc clarification defaults pattern

Use this reference when a `plan-doc` session needs user interview details but the user does not answer every gate.

## Pattern

1. Ask one compact clarification at a time when the answer materially changes the plan.
2. If the clarification times out or the user asks the agent to choose, select the safest low-risk default that preserves the stated goal.
3. Record the fallback explicitly in the task docs as a decision, not as an unresolved open question.
4. Update both `spec.md` and `todo.md` so `/plan-code` sees the same resolved state.
5. Run a markdown/lightweight verification gate such as `git diff --check` on the touched task docs before reporting completion.

## Good default selection examples

- UI panels in content-heavy surfaces: collapsed by default when extra vertical space could distract from the primary content.
- Ambiguous label for auxiliary timeline/caption information: choose the broadest product-neutral label, e.g. `Timeline`, unless the user provided stronger product language.
- Click behavior not explicitly requested: keep display-only in v1 and document interactivity as future scope.
- Long lists in inline UI: use compact max-height/scroll behavior rather than expanding the whole feed/comment item.

## Final report expectation

For `plan-doc`, report files updated, resolved decisions, verification command/result, and the mandatory final self-audit. Do not imply implementation happened unless code was explicitly authorized.