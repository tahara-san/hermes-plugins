# Buffdemy2-web navigation simplification notes

Use this as a concrete reference when a task asks to simplify or restructure the global/app-shell navigation in `buffdemy2-web`.

## Pattern captured from session

- Desktop/global nav column simplification can mean removing a separate bottom/footer nav cluster and moving notification/profile actions into the primary nav block.
- Mobile nav may intentionally use two major containers instead of mirroring desktop:
  - top bar right actions: Search + Profile/sign-in
  - bottom bar: Home + List + Notification + More
- Keep profile behavior route-aware by reusing the existing user-menu/profile router rather than duplicating auth logic in the nav component.
- Reuse existing menu components when possible (for example, the nav-rail More sheet/menu) instead of creating a second mobile-only More implementation.
- Add/adjust i18n keys for nav labels instead of hardcoding English/Japanese strings.

## Verification pattern

For this class of UI layout change, prefer layered but focused verification:

1. Inspect `git diff --check` for whitespace/conflict issues.
2. Run the project i18n checker if translation keys changed.
3. Run focused component/unit tests that cover the changed nav/profile/menu behavior.
4. Run TypeScript typecheck when props or imports changed.
5. Use a focused Playwright/app-shell smoke test for mobile/tablet/desktop responsive layout when navigation structure changes.

Avoid claiming completion from code edits alone; navigation layout changes need at least one real smoke or targeted test result.