# Plan-code product-decision blockers

Use this when a `/plan-code` or task-execution flow stops because implementation would choose product/payment/privacy semantics rather than merely writing code.

## Pattern

1. **Explain the blocker as a contract gap, not as code failure.** Name the exact behavior the code currently cannot decide safely (for example currency source, data ownership, visibility, rollout/migration).
2. **Ask one decision question when possible.** Offer concrete product-contract options instead of a wall of questions. If the user's answer resolves only part of the contract, ask the next smallest decision question.
3. **Immediately convert the decision into task artifacts.** Patch `spec.md`, `todo.md`, blocker reports, and final-report/deviation text before coding so later review bundles preserve the approved contract.
4. **Resume tests-first once the gate is resolved.** Add RED tests for the approved behavior and for fail-closed behavior when the new source of truth is absent or unsupported.
5. **Keep old assumptions out of the live contract.** Remove or supersede stale country/client/legacy compatibility requirements if the user approved a different source of truth.
6. **If a mandatory review leg remains pending, say so plainly.** Implementation may be verified, but plan-code is not complete until required reviews pass or are waived.

## Example shape

When a task asks to replace a hard-coded value but no source of truth exists:

- Explain: "The blocker is product-contract ownership: code cannot choose whether this belongs to creator profile, payment/compliance data, purchaser checkout, or provider config."
- Ask: "Where should the selected value live for V1?" with 3-4 concrete choices.
- After answer: update task docs with `Resolved decisions`, mark the blocker resolved, and add tests for server-derived value, client-payload rejection, and missing-source fail-closed behavior.

## Pitfalls

- Do not invent a product contract to keep coding.
- Do not leave task docs in their old blocked state after the user answers.
- Do not describe the task as complete when product/verification is resolved but a mandatory review delegate is still pending.
- Do not ask the user to run commands when the remaining gate is agent-runnable; only ask for actual decisions or external observations.