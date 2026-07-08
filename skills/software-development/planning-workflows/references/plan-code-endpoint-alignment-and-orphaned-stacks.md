# Plan-code endpoint alignment and orphaned stack checks

Use this during `plan-code` execution/review when a task adds or tightens a frontend model/schema contract and verifies a backend route with a similar-but-not-identical resource name.

## Problem pattern

A task may say "QuestionComment" while the current live product path is `QuestionFollowUpComment`, or a legacy exported model may target `/question-comment` while the audited backend exposes `/question-follow-up-comment`. If the implementation updates the legacy model but verifies only the live route, the code can be internally consistent while the evidence overclaims end-to-end coverage.

## Required checks

1. Trace the frontend model to its API path module and exact backend path string.
2. Trace the backend route actually exposed in current source, not stale docs.
3. Search for live reachability from `src/app`, `src/components`, server/client model callers, and editor instantiation sites.
4. Distinguish these states in task docs and review bundles:
   - **live integrated stack**: frontend model path and backend route match and have UI/app callers;
   - **live adjacent stack**: a related current stack already satisfies the contract but is not the changed model;
   - **exported-but-orphaned stack**: exported models/actions exist, but no live UI/app/component callers and no matching backend route were found.
5. If a schema field is made required for an orphaned stack under a no-fallback/current-contract plan, document the residual parse-throw risk if that stack is later rewired to a backend route that omits the field.
6. Do not mark backend verification as proving a different frontend path. Say exactly which route was verified and why that is acceptable or a known gap.

## Review bundle guidance

Include the path mapping evidence, caller/reachability search summary, and the accepted testing gap when no matching live endpoint exists. Reviewers should not fail an intentional orphaned-stack alignment when it is clearly documented, but they should fail stale claims that imply live end-to-end coverage through a route that was not actually verified.

## Rerun-after-blocker review nuance

When a final implementation bundle is regenerated after a specific reviewer blocker, treat older failed/pending/superseded artifacts embedded in the bundle as historical context, not as active failures. Re-check whether the old finding still applies to the current source and whether focused regression coverage was added. If an auxiliary snapshot has a bundle hygiene error such as a `[missing file: ...]` placeholder for a moved/dynamic route, do not fail solely on that placeholder when the required contract is otherwise covered by current source, diff, tests, or a correct adjacent path trace; record it as a suggestion/testing gap. Fail closed only when the missing/misaligned snapshot prevents judging a required source-to-route contract.
