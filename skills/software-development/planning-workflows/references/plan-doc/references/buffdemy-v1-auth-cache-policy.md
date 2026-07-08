# Buffdemy V1 API Auth + Cache Policy

Use this reference when planning Buffdemy work that touches API auth, frontend App Route proxies, cache headers, public/anonymous access, feeds/search/discovery, or backend response headers.

## Captured decision

For V1, Buffdemy should default application data APIs to authenticated access. Anonymous/public exposure should be deliberately minimal.

- App data APIs require auth by default.
- Do not expose anonymous feeds, searches, discovery lists, aggregate endpoints, or broad public app-data queries unless the user explicitly overrides this policy.
- The approved anonymous public-cache candidate is an **individual published article response** only.
- Do not add backend app caching logic for this policy. Caching should be implemented outside the app via CDN/proxy when explicitly needed.
- Backend route/header work may verify or preserve existing no-store/no-cache behavior, but should not introduce new cache strategies or public cache directives.

## Planning implications

When a regression appears because a frontend proxy calls a strict backend endpoint as anonymous/public:

1. Do not assume the backend endpoint should become public just because it returns a public-shaped DTO.
2. First decide whether the endpoint is part of the minimal anonymous exposure surface.
3. For V1, tag discovery/search, feeds, user/list discovery, subscription-tier lists, media metadata, and similar app-data discovery endpoints should usually remain auth-required.
4. Fix frontend App Route/server-model code to forward/derive the authenticated session when the backend contract is strict.
5. Remove public shared-cache headers from authenticated app-data proxies.
6. Keep unauthenticated page UX explicit: show sign-in prompts and avoid client-fetching private discovery data.

## Backend API header planning

When the user says to update backend-side API headers:

- Include tests/docs that assert strict-auth endpoints are non-public-cacheable.
- Prefer assertions for both `Cache-Control: no-store` and `CDN-Cache-Control: no-store` when the route test harness exposes headers.
- If headers are missing, fix using the existing no-store/no-cache preset or middleware behavior only.
- Do not add backend cache middleware/logic/public cache strategies as part of this policy.
- Update backend endpoint docs to state both auth mode and the V1 public-cache boundary.

## Example: tag discovery regression

If `/tags` fails because `/api/tags` proxies backend `/post-tag` using `auth: 'none'` while backend `/post-tag` and `/post-tag/search` use strict auth:

- Keep backend `/post-tag` and `/post-tag/search` strict.
- In the web server model/App Route, remove `auth: 'none'`, `force-cache`, `next.revalidate`, and public response cache policies.
- Verify authenticated users can load/search tags.
- Verify unauthenticated direct API calls do not expose tag data and are not public-cacheable.
- Update backend docs/tests for strict auth and no-store headers.
