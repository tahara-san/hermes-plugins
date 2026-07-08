# Handling mid-task contract changes in plan-code workflows

Use this when the user changes a requirement after implementation/review has already started.

## Required sequence

1. Treat the latest user instruction as the new contract, even if it contradicts the plan-doc or earlier review outcome.
2. Convert the change into a failing regression test before editing code when feasible.
3. Update implementation narrowly to satisfy the new contract.
4. Scan for callers and compatibility paths that still encode the old contract.
5. Update plan artifacts (`spec.md`, `todo.md`, `notes.md`) so they no longer contain stale acceptance criteria.
6. Rerun impacted verification and live probes.
7. Regenerate review artifacts from the final state only; exclude stale prior review bundles/verdicts from the new bundle.
8. Rerun independent review after every post-review code or contract change.

## Examples of contract-change evidence

- A formerly retained compatibility endpoint is removed: add a test that authenticated calls to the old endpoint return not found and cannot trigger side effects.
- A query contract tightens: add malformed/duplicate/extra-query tests and live probes.
- A public/auth boundary changes: prove both allowed and denied actors, including direct storage checks for "no row created".

## Pitfalls

- Do not leave older plan-doc wording like "keep compatibility unless proven safe" after the user explicitly says not to keep compatibility.
- For UI/order/contract changes after a previous final review, do a semantic stale-doc sweep before regenerating the bundle: `spec.md`, `todo.md`, `notes.md`, kickoff prompts, final-report text, and active review aggregates. Search not only exact strings, but equivalent prose and headings such as "current order" that now describe historical state. If preserving old evidence, relabel it clearly as "original", "historical", or "superseded" so reviewers cannot read it as active contract.
- If a reviewer approves the code but flags stale task-doc wording as non-blocking, treat that as a post-review artifact change for plan-code finalization: save the reviewer artifact as superseded, patch the docs, rerun `git diff --check`, regenerate the implementation bundle, and rerun both mandatory review legs. Do not count the stale approval toward the final aggregate.
- Do not trust a review that was run against a superseded bundle; regenerate after docs/tests/code are coherent.
- Do not report the task complete until the active task list, docs, review artifact, and git state all reflect the latest contract.
- If a reviewer returns an "informational" or non-blocking note that reveals a cheap contract hardening (for example a supposedly role-agnostic ID branch still applying optional role filters), prefer fixing it before the final report rather than carrying the edge as a risk. Treat that as a post-review change: add/adjust a focused regression, rerun verification, regenerate the bundle, and rerun all mandatory review legs.
