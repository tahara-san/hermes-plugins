# Generic selector search + identity lookup APIs

Use this when planning or executing backend support for autosuggest/multiselect selectors that need to render user/entity chips.

## Lesson

Avoid creating one tailored suggestion endpoint per frontend view when the underlying capability is reusable. Split the API by capability, not by screen:

1. **Search/autocomplete** for finding new selectable entities.
2. **Identity hydration/lookup** for resolving already-stored ids into stable chip labels.

For user selectors, first ask whether the product can constrain discovery to **username-only prefix search**. If yes, and an existing generic `GET /user?q=` username search already exists, prefer reusing it with generic filters instead of adding a new `/user/<view>-suggestion` route. Example:

```http
GET /user?q=<query>&role=creator&role=paidContentCreator&limit=5
```

Do **not** add a `shape`/`view` query parameter just to make one frontend selector lighter if response shapes are owned by repository/model serializers. Endpoint-local shape construction becomes another form of sprawl. If the user accepts the existing repository public shape and can ignore extra public fields, reuse that shape rather than adding a new selector-specific serializer.

If username-only search is not enough, a generic search capability path is still preferable to a view-tailored route, for example:

```http
GET /user/search?q=<query>&role=creator&role=paidContentCreator&limit=5
```

For hydration, prefer reusing an existing source-of-truth ID lookup when its semantics are acceptable. If `GET /user?id=<id>` already returns active public users with filter-miss semantics, it can be extended to repeated ids:

```http
GET /user?id=<id1>&id=<id2>
```

Only add a separate identity lookup endpoint when the product truly needs a different wire contract, such as unresolved rows, a narrower shape, or different privacy semantics.

## Decision ladder

1. **Can existing resource search support the selector by narrowing the product contract?**
   - Example: user accepts username-only search and explicitly does not want displayName search because it creates too many noisy hits.
   - Reuse existing `GET /user?q=` and add only generic, reusable filters such as repeated `role`, while preserving default behavior when those filters are absent.
   - Avoid `shape`/`view` params when they require endpoint-local response construction. If shape ownership belongs in repositories/models, use the existing public shape unless a real API-wide shape abstraction already exists.
2. **Can existing ID lookup semantics support hydration?**
   - If `GET /user?id=` already means active-public filter-miss lookup, extending it to repeated ids may be enough.
   - Preserve order/duplicates for resolved rows when repeated ids are accepted.
   - Be explicit that missing/non-active rows are omitted if you keep filter-miss semantics; frontend must compare requested ids to returned `_id`s to preserve unresolved legacy chips.
3. **If existing search is too broad or incompatible, add a generic capability endpoint** such as `/user/search`, not `/user/creator-suggestion`.
4. **Keep hydration separate from search** unless the stored value is itself the searchable key. Exact id hydration has different ordering, duplicate, and unresolved-row requirements, but it does not always require a new route if existing ID lookup semantics are acceptable.

## Why not one endpoint per view

A path like `/user/creator-suggestion` is easy to reason about for one task, but it does not scale when more views need similar selectors. If future views need users by role/status/capability, a generic bounded `/user` search mode or `/user/search` with explicit filters and shapes is a better class-level API.

## Why not force hydration through search

Hydration is not search. If the frontend already has stored ids, the backend should resolve those ids against the source of truth rather than use a relevance-ordered or eventually-consistent search index. Hydration usually needs:

- input order preservation;
- duplicate preservation;
- exact id validation;
- bounded batch size;
- uniform unresolved rows for missing/non-public records;
- narrow public shape;
- no viewer-specific auth shape.

Search indexes can help discover new candidates, but Mongo/source-of-truth lookup is usually safer for draft/edit hydration.

## Design checklist

For a generic selector search endpoint or existing-resource search extension:

- Prefer generic filters over view-specific paths, e.g. repeated `role` values from a known enum.
- Do not introduce `shape`/`view` parameters unless the project already has a centralized serializer/shape abstraction for that resource. Avoid defining ad hoc wire shapes in endpoint handlers.
- If the existing repository public shape is acceptable, return it and let the frontend ignore unneeded public fields; adding a shape just to remove a trivial public field is usually complexity without durable value.
- Preserve the existing endpoint’s default behavior when the new generic filters are absent.
- If the product accepts username-only discovery, search only the canonical username field (`name`) and document that `displayName` is intentionally excluded.
- If display-name search is required, bound it carefully and expect noisier result sets; do not add it just because the field is public.
- Enforce active/public visibility on the server.
- Bound `q` length and `limit`; avoid broad empty queries and arbitrary `skip` unless the product requires pagination.
- Do not expose private index fields just because they exist in Elasticsearch.
- If Elasticsearch is used for candidate discovery, rehydrate/final-filter from the source database before returning public data.

For a generic identity lookup or repeated-id extension:

- Accept repeated ids when order/duplicate preservation matters.
- Limit batch size.
- Validate id syntax before DB calls.
- Decide explicitly between **filter-miss semantics** and **unresolved-row semantics**:
  - filter-miss: omit missing/inactive rows and let the frontend compare requested ids against returned `_id`s;
  - unresolved-row: return `{ id, resolved: false, reason: 'not_found_or_not_public' }` when the product needs explicit per-id status.
- Keep exact-id hydration role-agnostic unless the product explicitly asks for role-filtered hydration; ignore suggestion-only role params in the ID branch if necessary.
- Use the existing resource public shape unless a centralized narrow identity shape already exists; never expand to self/auth profile shape.

## Frontend plan refresh after backend gate resolves

When a frontend plan was previously blocked on backend selector support, and the backend lands a simpler generic contract, update the plan artifacts before implementation rather than carrying stale blocked wording forward:

1. Create or update `backend-contract.md` with the exact final endpoints, params, response shape, verification output, review verdict, and frontend constraints.
2. Patch `spec.md`, `todo.md`, and `progress.md` so the active contract is clear and the backend gate is marked resolved.
3. Mark any old handoff prompt as superseded if it requested now-rejected tailored endpoints.
4. If old plan-review bundles/artifacts still mention superseded endpoint options, do not rewrite the historical bundles; instead, mark the aggregate/current note as historical or stale and point future implementers to `backend-contract.md` as the active authority.
5. Run a docs-only stale-term/whitespace check over the active docs so outdated endpoint names (`/creator-suggestion`, `/public-identity`, `shape=identity`, etc.) do not remain in executable instructions.

When explaining “hydration” to implementers or users, avoid making it sound like a required special endpoint or shape. In selector plans, hydration often just means: stored IDs are resolved through a normal public user lookup so chips can render; save payloads remain ID-only.

## Buffdemy-specific note

In Buffdemy backend, existing `GET /user` already supports `q` as active-user username-prefix search and can be extended with generic repeated `role` filters for selector use. This is preferable when the product accepts username-only suggestions. Do not add `shape=identity` unless the repository layer owns that shape; endpoint-local public identity serializers are considered shape-logic sprawl for this codebase.

For exact-ID hydration, first evaluate whether existing `/user?id=` filter-miss semantics are acceptable. If they are, extend `GET /user?id=` to accept repeated ids, preserve order/duplicates for resolved active users, omit missing/non-active users, and document that the frontend preserves unresolved legacy ids by comparing requested IDs to returned `_id`s. Use a dedicated `/user/public-identity` or `/user/identity` route only when unresolved rows or a truly different centralized shape are required.

If using `GET /user` for selectors/hydration, add regression tests that:

- default `/user` behavior remains unchanged when `role` is absent;
- `role=creator&role=paidContentCreator` returns only active creator roles for username-prefix search;
- username-prefix matches work and displayName-only matches do not;
- `shape` is rejected if the project decided not to support it;
- the superseded tailored suggestion and identity paths are not exposed as successful routes;
- repeated-id hydration preserves resolved order/duplicates, enforces a max batch size, omits missing/non-active rows, and remains role-agnostic even if role params are present.
