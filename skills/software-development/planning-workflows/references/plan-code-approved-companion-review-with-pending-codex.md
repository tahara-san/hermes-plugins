# Plan-code: approved companion review while Codex-style delegate is pending

Use when a `plan-code` implementation is otherwise complete, automated verification is green, and the companion reviewer (for example `claude-i`) approves, but the mandatory Codex-style `delegate_task` review has not re-entered the parent session yet.

## Pattern

1. **Do not claim completion.** A dispatched delegate is not approval, and a companion approval does not satisfy the missing Codex-style leg.
2. **Save the companion approval immediately** as raw and structured artifacts, including bundle path, observed reviewer model/tool/effort, verdict, and all non-blocking suggestions/testing gaps. For interactive Claude Code Opus 4.8 @ xhigh effort lanes, capture the pane after the verdict, write a normalized JSON/markdown verdict yourself if the reviewer used prose, and clear/exit the TUI session so queued text does not accidentally execute later.
3. **During the companion review, keep commands bounded and read-only.** If the reviewer asks for a small inspection command against the prepared bundle/source, approve only when it is read-only and necessary for the verdict; do not let the companion reviewer rerun tests/builds or mutate files when Hermes already supplied verification evidence.
4. **Create a pending Codex artifact** such as `tasks/<slug>/reviews/codex-implementation-review-pending.json` with:
   - delegation id;
   - reviewed bundle path;
   - completed reviewer artifacts;
   - verification evidence;
   - exact resume steps.
5. **Leave aggregate review absent.** Do not create `final-review.json` until the Codex-style verdict is saved or explicitly waived.
6. **Mark TODO honestly.** Implementation and verification rows can be `[x]`; review/aggregate/final-report rows stay `[~]` pending.
7. **Avoid optional churn while pending.** If the companion reviewer returns non-blocking cleanup suggestions after approval, normally record them instead of applying them while the Codex leg is pending. Applying optional cleanup makes the bundle and companion approval stale and forces both reviews to rerun. Adopt only if the suggestion materially affects correctness/security or the user explicitly asks.
8. **Final response wording:** say implementation is complete and verified, but the task is blocked/pending on the mandatory Codex-style review. Include whether the agent is stuck or not, the pending artifact path, and the exact next step.

## Resume

When the delegate verdict returns:

- Save the parseable verdict under `tasks/<slug>/reviews/`.
- If it passes and no source/test/task-doc files changed since the reviewed bundle, create the aggregate `final-review.json`.
- If it fails, fix narrowly, rerun impacted verification, regenerate the implementation bundle, and rerun both mandatory review legs.
- After writing aggregate/final-report artifacts, run the final artifact-consistency gate when required by the task docs.
