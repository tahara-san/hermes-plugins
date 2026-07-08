# Frontend shared-component surface audit for plan-doc

Use when a frontend `plan-doc` targets a component that looks like a single page/detail view but may be reused in feeds, cards, previews, modals, or other surfaces.

## Trigger

A plan changes layout/order/visual hierarchy of a reusable component, especially when the user says "only X post/component" and the apparent target file is shared.

## Pattern

1. **Find all current consumers before locking scope.**
   - Use Codebase Memory first when indexed, then exact file reads for each caller.
   - Direct import/caller search can matter more than route/page naming; a detail component may also power feed previews.
2. **Name each surface in the plan docs.**
   - Detail page, feed preview, profile card, modal, etc.
   - Include any caller-specific props that affect the redesign (collapsed height, hidden controls, variant classes, clamp prefixes).
3. **Make an explicit product decision.**
   - Default: if the target component is shared and the user asked for that component/post type generally, apply the redesign to all current surfaces.
   - If the desired behavior is detail-only, require an explicit variant prop or wrapper split; do not rely on caller-specific CSS/order side effects.
4. **Add coverage for every affected surface.**
   - Reuse existing surface tests when present instead of inventing a new location.
   - The verification command must actually run every touched test file; if coverage lands in a separate test file, broaden the command.
5. **Cite token/source evidence for visual-size claims.**
   - If a plan says a size token is "half" or "smaller," include the source file/values when known so implementers and reviewers can verify the claim.
6. **Handle review-driven doc polish as stale-review work.**
   - If a review approves but gives useful non-blocking doc hardening and you adopt it, save the approval as superseded, patch docs, regenerate the bundle, and rerun required review legs.

## Review/pending gate notes

- A dispatched delegate review is not approval. If it does not re-enter and cannot be recovered from logs/session history, save a `*-pending.json` artifact naming the delegation id, reviewed bundle, completed companion review, and exact resume steps.
- Do not create an aggregate plan-review verdict until all mandatory legs have a saved passing verdict or the user explicitly waives a leg.

## Example acceptance criteria additions

- The plan lists every current consumer of the target component.
- The target order/visual change is verified in both the detail view test and the feed/card/preview test.
- Non-target components (for example Article author rows when changing Question author rows) are explicitly out of scope and not edited.
