# Buffdemy2-web plan-code editor smoke pattern

Use this reference when a `plan-code` task changes Article/ArticleComment editor routes, owner actions, or save flows.

## Authenticated smoke setup

- Prefer the repo's stored Playwright auth states when present:
  - `.playwright/.auth/user1.json` / `test01-creator.json` for owner/creator flows.
  - `.playwright/.auth/user2.json` for non-owner checks.
  - no storage state for anonymous checks.
- Use `ignoreHTTPSErrors: true` when local auth/cert redirects are expected in dev.
- If the browser tool redirects to auth or hits local certificate interstitials, switch to a small Playwright script rather than treating browser auth state as authoritative.

## Owner / non-owner assertions

For owner-action menus:

1. Open a known owner-owned detail route.
2. Assert the owner sees the menu trigger and expected actions.
3. Assert the edit link href is canonical.
4. Open the same route as a non-owner and as anonymous; assert the menu trigger/actions are absent.

## Save/restore edit smoke

When verifying a live edit flow against shared fixtures, avoid leaving fixture data mutated:

1. Open the edit URL with the owner auth state.
2. Read the current editor text.
3. Save a temporary marker such as `smoke-${Date.now()}`.
4. Wait for navigation back to the detail route.
5. Assert the marker is visible and the existing `Edited` marker behavior appears.
6. Reopen edit, restore the original text, save again, and assert the marker is gone.
7. Capture console errors/warnings, but filter known unrelated media-player warnings only if explicitly named in the report.

## Translation-key pitfall

If a component changes from `useTranslations('namespace')` to root `useTranslations()` so it can render cross-namespace keys like `common.save`, every existing call in that component must become a full key (`article_editor.actions.comment_success`, etc.). Browser smoke should check console output for `IntlError: MISSING_MESSAGE` because lint/i18n parity can pass while runtime key resolution is wrong.
