# Frontend/backend contract prerequisite gating

Use this reference when a `/plan-code` task implements a frontend experience that depends on existing backend APIs, especially when the user explicitly forbids mock/local approximations.

## Gate before coding

1. Read the task/spec for required backend contracts: route paths, auth requirements, query params, request bodies, response shapes, pagination, stats fields, follow/mutation semantics, and error behavior.
2. Inspect the repository's documented/backend-facing API contracts and existing frontend proxy/client patterns before editing UI code.
3. Record the confirmed contracts in the task progress docs before moving to implementation.
4. If a required production backend contract is missing or ambiguous, stop and report the backend blocker. Do not build a local mock, synthetic fallback, speculative proxy, or UI-only approximation unless the user explicitly changes scope.
5. Treat auth requirements as part of the production contract, not as a test detail. If search/list/popular endpoints are strict-auth, unauthenticated UI and public E2E must show an auth-required state (or stop if that breaks scope) rather than using browser-side mocks/fallbacks to make public discovery appear supported.
6. If the backend exists but deterministic tests need helper states that production APIs cannot create, distinguish the narrower test-fixture gap from a production-contract blocker.

## Narrow-scope guard

When the user narrows a feature to discovery/listing only, preserve negative requirements in every implementer/reviewer prompt:

- forbidden routes or links (for example feed navigation)
- forbidden API surfaces to modify
- forbidden CTA wording that implies unavailable behavior
- forbidden article/content-feed changes

Include those negative requirements in independent review context; reviewers otherwise may treat absence of common navigation as an omission.

## Progress-doc pattern

In `progress.md` or the relevant phase TODO, write a concise contract note like:

```md
Backend contract gate: confirmed `<GET route>` for search/popular/stats and `<POST/DELETE route>` for follow state, including exact-combination semantics. No local mocks or feed routes introduced.
```

If blocked:

```md
Backend blocker: `<missing route/field/semantic>` is required by the plan. Stopped before UI implementation because the user forbids mock/local approximations.
```

## Review checklist

- [ ] UI/client code uses backend-returned stats rather than invented counts.
- [ ] Follow/unfollow controls call authenticated backend mutation/read contracts.
- [ ] UI, SSR fetches, client fallbacks, and E2E expectations match the confirmed auth contract for search/list/popular endpoints; public mocks do not mask strict-auth backend behavior.
- [ ] Exact-combination identity is deterministic and shared across read/mutate paths.
- [ ] No forbidden route, link, CTA, or adjacent feed/content behavior was added.
- [ ] Tests cover the backend proxy/helper contract or clearly document an external blocker.
