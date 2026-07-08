# Buffdemy backend public user shape contract

Use this reference when a Buffdemy frontend/API task turns on whether a user field belongs in the public user shape, especially selector, mention, hydration, or profile identity flows.

## Pattern

1. Treat product/user direction about field visibility as the contract, but verify the live backend boundary before editing.
2. In `/workspace/dev/buffdemy-backend`, trace public reads to the centralized serializer:
   - `apps/api/src/routes/user/get.ts` for `/user` q-search, repeated `id` hydration, and public `/:id` reads.
   - `apps/api/src/routes/user/search/get.ts` for Elasticsearch candidate hydration when relevant.
   - `packages/mongo/src/repositories/user/userRepository.ts` for `userRepository.toShape('public', user)`.
   - `packages/mongo/src/repositories/user/userTypes.ts` for `PublicUserData`.
3. Prefer changing the centralized repository public shape and type over route-local filtering/shape adapters.
4. On the frontend, keep `src/app/api/user/route.ts` generic for role-filtered q-search and repeated-id hydration unless the user explicitly changes the architecture. Mention/no-role search may still intentionally narrow to mention identity fields.
5. Update tests at both levels:
   - repository test for `toShape('public')` including or omitting the target field;
   - API route tests for `/user?q=...&role=...` and repeated `id` hydration using the same canonical shape;
   - add `/user/search` or `/:id` tests only when the task specifically changes those paths or reviewers ask for direct coverage.
6. Keep UI acceptance separate from API response shape: a public API field may be returned but still not rendered in a selector UI.

## Verification notes

- Run backend tests from the package/service cwd inside the API container when host Bun is unavailable or root-level combined commands are too broad:
  - `docker compose exec -T -w /app/packages/mongo api bun run build`
  - `docker compose exec -T -w /app/apps/api api bun run build`
  - `docker compose exec -T -w /app api bun test packages/mongo/src/repositories/user/userRepository.test.ts`
  - `docker compose exec -T -w /app/apps/api api bun test src/test/routes/userPublicIdentity.test.ts`
  - `docker compose exec -T -w /app/apps/api api bun test src/test/routes/user.test.ts`
- If a root-level combined Bun API test is killed during startup but the package-local affected files pass, record the broad command as a verification deviation/blocker rather than chasing unrelated resource behavior.
- For frontend confirmation, a live proxy smoke through `host.docker.internal:3000/api/user?...` can prove the proxy currently forwards the backend public shape; pair it with `npm run lint` when task docs call for frontend verification.

## Review bundle scope

Both Buffdemy repos are often dirty. Build final review bundles from scoped intended backend files plus the active task directory, and explicitly label unrelated dirty files as out of scope. Do not include unrelated task dirs or backend changes in the implementation review bundle.