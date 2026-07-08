# Plan-code doc-only review failure rerun

Use when a mandatory `plan-code` review fails even though implementation/test evidence is acceptable, because task docs or review summaries contain stale or contradictory status text.

## Pattern

1. **Save the failing reviewer verdict first.** Do not discard a `passed=false` result just because it is docs-only; it is durable evidence that the gate failed and why.
2. **Classify the failure boundary.** Separate:
   - implementation/security/data-integrity blockers (fix code/tests and rerun full or delta implementation review), from
   - stale task-doc/evidence contradictions (patch docs and run a narrow docs-rerun review).
3. **Verify the cited text against live files.** A reviewer may cite line numbers from the reviewed bundle. Re-read the current task docs/review summary before patching; the source may already have been corrected by a sibling step or prior resume action.
4. **Patch only current, active contradictions.** Convert stale historical checkpoints to past tense if they are useful history, but active status sections must state the latest truth.
5. **Search for stale phrases before rerun.** For E2E/status docs, scan for old blocker labels such as `auth/base-URL`, `fresh focused E2E remains open`, or any exact contradiction the reviewer cited.
6. **Generate a narrow docs-rerun bundle.** Include the failed verdict, corrected task docs/summaries, a stale-phrase scan, and only the code snippets needed to prove the status contract. State that this is a rerun for a docs-only failure, not a new implementation review.
7. **Dispatch a fresh mandatory review.** Do not count the prior failed verdict as approval. Leave the final/aggregate gate open until the rerun verdict is saved and passing.
8. **Then run artifact consistency.** Any doc/review artifact edits after the rerun still require the final consistency pattern for explicit `plan-code`.

## Pitfalls

- Do not answer the user as if the product failed when the reviewer failed only contradictory docs.
- Do not silently mark the gate green because the docs now look corrected; the mandatory review failed and must be rerun or explicitly waived.
- Do not over-broaden the rerun into unrelated code review if no implementation files changed after the prior implementation bundle.
