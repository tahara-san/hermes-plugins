# Buffdemy2-web editor-flow simplification notes

Use this reference when simplifying Article/ArticleComment editor paths or similar shared editor flows.

## Scope shape

When the user asks for a holistic simplify pass, do not stop at `git diff`. Map the full flow:

1. Entry component(s): e.g. `ArticleForm`, `ArticleCommentForm`.
2. Provider boundaries: shared `PaperState`, feature-specific source providers, modal/editor state.
3. Shared UI controls: toolbar button, picker, option menu, bottombar, file-drop wrapper.
4. Mutation boundaries: where staged local state becomes persistent paper state.
5. Save boundaries: Article/ArticleComment serialization should keep the intended payload shape.
6. Smoke-critical affordances: mouse/keyboard events, menu/dropdown triggers, modal close/back paths.

## Durable findings from the existing-media CC pass

- Staged existing media should remain outside `PaperState` until the final Insert/commit action.
- Re-check media-slot availability at every mutation boundary: upload/drop, existing-media insert, and duplicate/copy media.
- Shared state helpers that mutate arrays must call the relevant action (`actions.set(...)`); creating a copied array without committing is a no-op.
- UI guards and state guards should both protect limits where a shared state helper can be called from multiple menus/paths.
- Use `type="button"` on toolbar/dropdown buttons that live near editor forms to avoid accidental submits.
- When simplifying picker cards, avoid nesting native buttons around media preview components; use an accessible non-button card (`role="button"`, `tabIndex=0`, Enter/Space handling) if the preview can contain controls.
- For editor smoke, distinguish product behavior from automation artifacts. If a real click is flaky in one nested toolbar, verify the provider/source path with a targeted `mousedown` dispatch, but keep the caveat explicit.

## Verification pattern

For a non-trivial editor-flow simplify pass, use proportional gates:

- focused tests covering the changed feature/source/editor state
- regression tests for any shared state bug fixed during simplify
- `npm run lint`
- `npx tsc --noEmit`
- independent review after fixes; if the review finds a must-fix, fix it and re-review
- browser smoke for the most practical editor path; report any known automation caveat separately from product behavior
