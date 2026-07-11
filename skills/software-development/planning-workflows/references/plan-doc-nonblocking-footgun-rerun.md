# Plan-doc non-blocking footgun incorporation and rerun

Use this when a required `plan-doc` review returns `APPROVED` but includes concrete non-blocking suggestions that identify likely implementation footguns.

## Pattern

1. **Do not ignore concrete footguns just because the verdict passed.** If a suggestion names a real edit site, dangling reference, validation condition, stale label key, or verification ambiguity, patch the plan docs before handoff.
2. **Do not churn forever on optional polish.** If a reviewer explicitly says a suggestion is optional, non-gate-blocking, or not a coverage/correctness risk, record the disposition and stop patching for that suggestion. Rerun only for suggestions that identify a real implementation footgun or blocker.
3. **Save the initial reviews as superseded first.** Preserve both raw reviewer outputs under `tasks/<slug>/reviews/*initial-superseded*` with the reviewed bundle path, reviewer/model, verdict, and why it was superseded.
4. **Handle late historical async results by bundle identity, not arrival order.** If a legacy delegated review result arrives after newer bundles already exist, compare its reviewed bundle path/version to the current bundle. Save the result as `*vN-superseded*`; it is historical evidence and cannot satisfy the current interactive Codex gate. Still inspect its concrete findings against the current docs: if a footgun remains applicable, patch the current docs, mark any current pending/passed artifacts superseded, regenerate a new vN+1 bundle, and rerun both required review legs.
5. **Patch only the plan docs.** Keep changes at the implementation-instruction level: exact file/edit sites, validation gates, label/key hazards, verification output requirements, and smoke/auth caveats. Do not start implementation during `plan-doc`.
6. **Regenerate a compact review bundle.** The final bundle should include updated task docs plus relevant current source/test/i18n/package context, but prefer targeted excerpts over full-source dumps. Large full snapshots can wedge interactive reviewers; if a bundle exceeds what the review needs, replace it with a smaller vN bundle that states older bundles are superseded, includes exact file/line excerpts for evidence, and excludes review artifacts from the reviewed scope to avoid self-referential stale-review loops. For follow-up review bundles on untracked plan-doc files, do not rely on `git diff -- tasks/<slug>/...` as the only delta evidence because untracked files may produce an empty diff; include either saved before/after excerpts, a manual bullet list of changed requirements, or a real `git diff --no-index`/snapshot comparison so reviewers can trace the cleanup delta.
7. **Rerun every required review leg after substantive doc edits.** A passed-but-patched plan needs fresh interactive Codex TUI and Claude Code approval against the same regenerated bundle before claiming reviewed completion; launch both independent lanes before waiting on either.
8. **Save final raw artifacts and aggregate verdict.** The aggregate should name the final bundle, final raw artifacts, superseded initial artifacts, post-review-doc-edits=true, and reviews-rerun-after-doc-edits=true. Keep one canonical final bundle (for example `plan-review-bundle-vN.md`) and prune superseded bulky bundle drafts when they add size but no durable evidence; preserve concise superseded reviewer verdict artifacts when they explain why the plan changed.
9. **Run a final artifact-consistency check.** Create a narrow consistency JSON/MD that verifies required files exist and aggregate verdict is parseable/passing. Exclude the consistency artifact itself from its own scope.

## Good footguns to incorporate

- Safety filters that could turn the headline feature into a silent no-op. Add both negative and positive tests (for example, denied ACL recipients are skipped **and** legitimately readable private recipients are notified).
- Retry/idempotency details that are specified for one fanout path but missing from siblings. Require per-recipient stable dedup IDs and duplicate-delivery tests for every new event path.
- Shared-helper placement that crosses app boundaries. If a plan says to reuse an API route helper from a worker/outbox app, patch the plan to extract package/shared code instead of importing app-local route libs.
- Public payload field typing traps. If a new summary payload field is a timestamp or scalar, state that it is persisted raw and not passed through ObjectId coercion helpers.
- Public target-contract ambiguity. Pin exact target fields needed by the frontend (for example owner slug/name) and require fail-closed behavior for omitted/unreadable targets.
- Verification-command path drift. If a plan references test files that may not exist yet, add a final verification step requiring the implementer to confirm/create/update focused test paths before reporting results.
- Router/step rename fallout: initial step values, reset effects, and navigation guards that still reference removed steps.
- Validation gates tied to removed wizard steps, e.g. `currentStep !== 'options'` after consolidating an options screen into a compose screen.
- Step-label records reused as field/review labels, leaving dangling `labels.format` / `labels.schedule` references after step consolidation.
- Translation-key retention ambiguity: old keys may remain only if unused by the new UI and parity checks pass; tests/smoke should prove old step names no longer render.
- Verification wording like “when practical” without requiring exact captured output for either pass or blocker.
- Browser smoke probes that prove only reachability/redirect behavior, not authenticated rendering.
- UI plan/test observability mismatches after state changes, especially success flows that close/unmount a modal: require tests to assert pre-execute confirmation content before closing and post-execute observable state outside the modal (for example footer total + dialog absence), not unmounted in-modal counters or balances.
- Selected-state accessibility/test seams: if a plan requires `aria-pressed` or equivalent, pin whether the UI uses plain semantic buttons or a shared component that forwards the attribute, and require mocks to preserve the selected-state prop so tests can observe it.
- Validation-copy ambiguity when presets and custom input have different minimum rules: require a dedicated custom-input error message when `Other` rejects a value that a preset accepts (for example typed `100` rejected because custom values must be greater than 100).

## Final report note

Report both that initial reviews passed and that they were superseded by doc improvements, then name the final review artifacts and aggregate verdict. This avoids hiding the review history while still ensuring the handoff plan is the reviewed final plan.
