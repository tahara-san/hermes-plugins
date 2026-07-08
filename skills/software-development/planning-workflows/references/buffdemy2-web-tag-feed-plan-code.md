# Buffdemy2-web tag feed plan-code execution notes

Use when executing `/skill plan-code` for Buffdemy2-web `/tags/content` tag feed changes, especially adding/removing feed tabs, hiding Refresh, or wiring Question feeds.

## Lessons from tag Question feed execution

1. **Prove the API/proxy contract before UI work, but split proof by layer.**
   - Source-level `/api/question` evidence and route tests can prove repeated `tags`, `status=published`, `sortBy=publishedAt`, `sortDirection=desc`, `limit`, and integer `olderThan` forwarding.
   - Browser-side `page.route` cannot observe server-side initial fetches after Refresh is removed; page/server tests should assert initial query shapes.
   - Live browser smoke may land on auth-required state in an unauthenticated browser tool; authenticated Playwright storage-state smoke can cover the feed UI if it passes under the correct authenticated project.

2. **Keep Refresh removal honest.**
   - Remove visible Refresh UI/copy and reachable refresh handlers from the tag feed client, not just hide the button with CSS.
   - Search for stale refresh prop/copy references in tag feed components/tests before review.
   - Keep `newerThan` support only where still needed by existing Article hooks; do not cite its presence as a reachable tag-page refresh path if the UI no longer calls it.

3. **For multiple tab panels, own the Radix `Tabs` root at the feed client boundary and be cautious with `forceMount`.**
   - A header-only `Tabs` root with feed content outside it creates disconnected tab state. Hoist the `Tabs` root to the shared client boundary and let the sticky header render `TabsList` / `TabsTrigger` inside that parent context.
   - Do **not** use `forceMount` on an inactive feed tab merely to preserve state when the product contract says Article is the default visible feed. With the real Radix wrapper, `forceMount` can keep inactive Question content mounted/visible or trigger feed side effects before tab selection, breaking the Article-default contract.
   - Preserve inactive-tab state only when the UX explicitly requires it and add a real-component visibility/side-effect regression proving inactive panels stay hidden. Otherwise allow Radix to unmount inactive `TabsContent`.
   - In jsdom/component tests, Radix tab activation may be brittle without `@testing-library/user-event`. If using a Tabs mock, make sure it models the production lifecycle semantics that matter (including `forceMount` if the bug involves it), or complement the mock with a real-component/unit/E2E assertion or reviewer-documented inspection of the real wrapper.

4. **Avoid tags → profile component coupling for Question rendering.**
   - If the visual reference is the profile Question feed, extract a shared feed-entry renderer under the content/Question component tree and re-export from the old profile path.
   - Preserve the feed chrome/test IDs through that extraction: `question-feed-entry`, `question-post`, `question-author-row`, `question-metadata-row`, `question-actionbar`, and `question-feed-content-clamp*`.

5. **Treat reviewer non-blocking verification gaps carefully.**
   - If a reviewer suggests extra verification only (for example `npm run build` / typecheck) and no source/test/doc semantic change is needed, run the extra verification and record the result without changing implementation.
   - Do not implement optional code suggestions after an approval unless worth staling the review; if adopted, regenerate the bundle and rerun all mandatory review legs.
   - Conditional E2E assertions that fall back to empty state can be acceptable when unit/component tests prove renderer wiring, but record the limitation in notes/final artifacts.

## Verification checklist additions

- [ ] Focused page/unit/API tests cover initial Article + Question fetches, unauthenticated no-fetch, tag-only Question forwarding, Question pagination query, and Refresh absence.
- [ ] Existing Article tag feed hook tests still pass after shared helper edits.
- [ ] `npm run check:i18n`, `npm run lint`, and preferably `npm run build` pass before final review.
- [ ] `npx playwright test <tag spec> --list` is used to choose the authenticated project; run the focused spec with `--no-deps` when setup/auth prerequisites are already available.
- [ ] Component or E2E coverage proves the Question panel is absent on the default Article tab and appears only after selecting Question; if a mock Tabs component is used, either make it honor the real `forceMount` behavior or add separate real-component evidence.
- [ ] Review bundle explicitly includes untracked shared renderer/hook/test files and excludes unrelated task directories and historical review artifacts.
