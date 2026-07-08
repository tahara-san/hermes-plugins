# Buffdemy2-web tag feed plan-doc gates

Use when writing or reviewing a `plan-doc` for `/tags/content` or other Buffdemy2-web tag feed work, especially when adding a new content type tab or hiding the existing refresh affordance.

## Lessons

1. **Removing Refresh changes E2E observability.**
   - Existing tag-feed E2E may click Refresh to trigger client-side `/api/article` requests that `page.route` can mock/inspect.
   - Once Refresh is hidden/removed, the first Article/Question results are usually server-side initial fetches and are not observable by Playwright `page.route` after navigation.
   - Move initial query-shape assertions into page/server tests (for example `src/app/tags/content/page.test.tsx`). Reserve Playwright network assertions for client-side pagination requests after scroll/tab interaction, or explicitly require a live seeded backend for SSR-rendered entries.

2. **Do not fake new tag content feeds by filtering another feed.**
   - A tag Question feed must query by normalized repeated `tags`, not by profile `ownedBy` plus client filtering.
   - Add a Phase 1 contract gate for the exact frontend proxy/backend query shape before deep UI work.
   - If live services are unavailable, document live smoke as blocked; never substitute frontend filtering as proof.

3. **Verify nested test IDs before making E2E assertions.**
   - Feed entry components may only expose wrapper IDs; full post chrome IDs can live deeper in shared renderers like `QuestionPost` or actionbar children.
   - Include the shared renderer source/tests in the plan-review bundle and make Phase 1 confirm exact selectors before implementation.

4. **Plan tab restructuring explicitly.**
   - Tag feed code can split `Tabs` into a header component while feed content lives elsewhere. A plan that adds tabs must state where tab state is lifted and how `TabsContent`/content switching is connected, not just “add a tab.”

5. **Be precise about cursor types and i18n keys.**
   - Match local API parsers: if `/api/question` parses `olderThan` as an integer, tag Question helpers should use numeric epoch-millisecond cursors and let the fetch layer serialize.
   - Name new translation keys in the plan (for example `feed.tabs.question` and Article/Question-specific empty/error keys) so implementation does not leave ambiguous shared copy.

## Plan-doc checklist additions

- [ ] Contract gate proves repeated `tags` + `status=published` + `sortBy=publishedAt` + pagination are supported for the new content type.
- [ ] Initial server fetch assertions live in page/server tests; Playwright only asserts client-visible requests unless a live seeded backend is available.
- [ ] Refresh absence is covered by acceptance criteria, component tests, and E2E/browser smoke.
- [ ] Shared renderer selectors are verified before E2E selector commitments.
- [ ] Tab state/content ownership is described concretely.
- [ ] Cursor type and i18n key names are explicit.
