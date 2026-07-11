# Plan-doc review hardening with pending interactive Codex TUI

Use when an explicit `plan-doc` flow creates task docs, runs a companion Claude/CLI review, gets useful non-blocking plan-hardening suggestions, and the mandatory interactive Codex TUI review is still pending or was launched against a now-superseded bundle.

## Pattern

1. **Save the first reviewer artifact immediately**
   - If Claude/CLI returns `PASS` with non-blocking suggestions worth adopting, save it as an initial/superseded artifact rather than losing the verdict.
   - Mark why it is superseded: plan docs changed after the review.

2. **Patch only plan docs for valid hardening suggestions**
   - Incorporate small, risk-reducing clarifications (e.g. exact propagation seam, nested error-shape gate, serialization round-trip caveat, single owner for duplicate toast suppression).
   - Do not start implementation just because the reviewer named source files.

3. **Regenerate a fresh immutable bundle**
   - Prefer a new bundle path/version (e.g. `plan-doc-review-bundle-v2.md`). If the task convention uses a canonical bundle path (e.g. `plan-doc-review-bundle.md`), first copy the old bundle to an explicitly superseded path before overwriting the canonical current bundle.
   - Exclude prior review artifacts and old bundles from the reviewed content, or label them historical only, to avoid self-referential stale-review loops.
   - Re-run lightweight artifact checks (`git diff --check` scoped to the task docs, simple secret scan, placeholder/truncation scan) before dispatching reviewers.

4. **Rerun both required review legs on the current bundle**
   - An interactive Codex TUI launched against the pre-hardening bundle is not usable for the updated docs, even if it later returns PASS.
   - Start a fresh pinned Codex TUI session against the regenerated bundle and record the old session/artifacts as `SUPERSEDED_PENDING`/historical if it has not returned yet.
   - Rerun Claude/CLI against the regenerated bundle if the docs changed after its first review.
   - If the rerun reviewer approves with only polish-level non-blocking notes already covered by the active contract, record their disposition in the structured review artifact instead of editing again and creating another stale-review loop.

5. **If the current interactive Codex TUI is still pending, fail closed**
   - Save a pending artifact naming: current tmux session, current bundle path/hash, latest raw pane capture, completed companion review artifact, superseded older bundle/session if any, and exact resume steps.
   - Do not create a passing aggregate verdict while the required interactive Codex leg is absent. Either save a blocked aggregate verdict (e.g. `plan-review-blocked.json`) or a clearly named pending artifact (e.g. `codex-plan-doc-review-pending.json`) that prevents accidental completion claims.
   - Update `progress.md`/`todo.md` truthfully if those files exist: companion review PASS, Codex pending, aggregate blocked pending Codex verdict.
   - Final response must say the plan docs exist and companion review passed, but the full plan-doc review gate is incomplete/pending.

## Pitfalls

- Do not count a pre-hardening Codex TUI verdict as approval for v2 docs.
- Do not hide a pending mandatory review behind a passing Claude review.
- Do not keep editing task docs after the final review without regenerating the bundle and rerunning required reviews.
- Do not include stale historical bundles as live task-doc evidence in the regenerated review bundle.

## Minimal pending artifact fields

```json
{
  "status": "pending",
  "gate": "interactive-codex-tui-plan-doc-review",
  "tmux_session": "codex-plan-doc-current",
  "supersedes_tmux_session": "codex-plan-doc-old-if-any",
  "bundle_path": "tasks/<slug>/reviews/plan-doc-review-bundle-v2.md",
  "completed_companion_review": "tasks/<slug>/reviews/claude-plan-doc-review-v2.md",
  "reason": "interactive Codex TUI has not produced a parseable attested verdict yet",
  "resume_steps": [
    "Capture/recover the managed tmux session verdict",
    "Save the parseable Codex verdict artifact",
    "Patch docs and rerun both reviews if blockers require doc changes",
    "Only then replace the blocked aggregate with a passing aggregate"
  ]
}
```
