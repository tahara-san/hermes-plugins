# Article ACL Comment-Gating Planning Notes

Use these notes when planning frontend work for Buffdemy Article / Article Comment ACL gating.

## Backend contract discovered

The frontend-visible backend ACL contract is documented in `../buffdemy-backend/docs/frontend-guides/article-acl-data-shapes.md` (not the shorter `../buffdemy-backend/docs/article-acl-data-shapes.md` path).

Article responses now expose both sanitized policy metadata (`acl`) and requester-specific effective permissions (`privileges`). The API field is spelled **`privileges`**.

```ts
type ContentAclAudience = 'all' | 'subscribed' | 'followed';

type PublicArticleAclRule = {
  allowedAudiences: ContentAclAudience[];
  hasUserAllowList: boolean;
  hasUserDenyList: boolean;
  version: number;
};

type PublicArticleAcl = {
  read: PublicArticleAclRule;
  write: PublicArticleAclRule;
  comment: { create: PublicArticleAclRule };
};

type ArticlePrivileges = {
  read: boolean;
  write: boolean;
  comment: { create: boolean };
};
```

Use `acl` for group-policy copy (for example “followers can comment”) and `privileges` for current-requester behavior (for example whether to show the comment composer). Raw `users.allow` / `users.deny` lists are intentionally not returned publicly.

`POST /article-comment` remains server-enforced against the root Article ACL and may return:
- `403 article_comment_acl_denied` — authenticated caller is not allowed by the Article ACL.
- `400 article_not_commentable` — target Article is not in a commentable state.

Article read/list endpoints may return successful placeholder Article responses when `privileges.read === false`; these are not not-found/error states. Placeholder/full responses are requester-contextual because `privileges` is personalized, so avoid shared public caching assumptions.

## Article public ACL preview migration

When the backend announces that Article fields are now public and excluded from ACL read control for content preview, plan against the new contract rather than old placeholder payload compatibility:

- Resolve the migration guide in the backend repo when the frontend path is missing or stale, e.g. `../buffdemy-backend/docs/frontend-guides/article-public-acl-preview-migration.md`; record the path you actually read in `spec.md`.
- Treat `article.privileges.read === false` as the only restricted-state branch. Do not infer restricted state from missing public fields, title placeholders, or legacy placeholder payloads.
- Do not plan compatibility shims for the old placeholder backend shape unless the user explicitly asks for migration/backward-compatibility code.
- For restricted Article detail/comment-parent rendering, plan a public preview that keeps backend-public Article metadata visible and renders only the first Paper as teaser content; avoid rendering the full `PaperViewer` when read is denied.
- Keep list/profile/feed scope narrow: public title/tags/stats/timestamp can remain visible, and the frontend may add a restricted marker; do not broaden feeds into full Paper teasers unless requested.
- Treat optional legacy fields such as `lastEditedAt` as existing optional model compatibility unless the migration guide explicitly makes them part of the new public preview contract.
- Keep content/security authority on the backend: frontend preview rendering is UX, not authorization.

## Planning implications

- Treat backend as the security source of truth for create permission.
- Do not plan frontend-only ACL checks as authoritative authorization.
- Prefer `article.privileges.comment.create` to gate top-level and reply composers when the updated backend contract is available.
- For Article owner comment privileges specifically, owners may be allowed to create top-level comments and replies on their own **published** Articles when `article.privileges.comment.create === true`, even when raw public ACL metadata looks closed (`acl.comment.create.allowedAudiences === []`) or indicates a deny-list (`acl.comment.create.hasUserDenyList === true`). Plan UI against the requester-specific `privileges` boolean; use raw/public ACL metadata only to prove fixture setup or explain policy.
- Use `article.acl.comment.create.allowedAudiences` only for explanatory group-policy copy, not for current-user authorization.
- Keep Article content ACL out of scope unless explicitly requested; when the user says Article content ACL is not implemented yet, scope frontend planning to Article comment creation/read/reply behavior plus Article Comment create/read behavior.
- Ask for UX/spec details before writing the plan when behavior is product-visible: denied composer presentation, reply button behavior, i18n copy, whether Article read placeholders should suppress or still show comments, comment permalink behavior, pagination/load-more behavior, and error-state handling for 403/400 responses.
- Prefer incremental targeted clarification over a long wall of questions: ask the next blocking product/architecture question, incorporate the answer, then continue until the plan can be written safely.
- If the user chooses restricted Article detail behavior where `article.privileges.read === false` still shows readable comments, plan to fetch/render comments server-side as usual and render a minimal restricted Article summary/card above them. Do not treat the Article as missing or suppress comment reads.
- Preserve SSR by fetching Article + comments server-side and passing ACL/privileges into server-rendered or server-first components; keep client boundaries limited to editor expansion, optimistic insertion, load-more/reply toggles, and interactive actions.
- Prefer one shared restricted-Article rendering branch in the Article `Content` path (or a small component used by `Content`) so Article detail and comment permalink parent-Article views do not duplicate restricted-card behavior. Avoid rendering `PaperViewer` when `privileges.read === false`.
- Thread a single server-derived create permission prop (`canCreateComment` / `canCreateReply`) for composer/editor gating. Keep `isAuthenticated` only for anonymous-vs-authenticated messaging; do not recompute effective ACL permission from `useAuth()` in client components.
- Keep read-thread/permalink navigation independent from create permission: allowed viewers can see a reply-capable link; denied viewers with existing replies can see a read-only “View replies”/thread link; denied viewers with no replies do not need a reply-create affordance.
- For comment permalink pages, use `!!auth?.user` consistently rather than `Boolean(auth)` when deriving authenticated behavior, because a session wrapper may exist without a user.
- When planning update-path mechanics, account for existing remount keys before adding state reset effects. For Buffdemy Article comments, `<Comments key={articleProps._id}>` may already cover Article switches; `ArticleCommentView` still needs a local replies reset when the focal comment or `childComments` props change.
- Handle backend create denials via the existing `unwrapResult`/`AppError` flow and a tiny local error-code-to-i18n-key helper near the form actionbar; map `article_comment_acl_denied` and `article_not_commentable` specifically while leaving unknown save errors on the generic path.
- If a gate depends on effective viewer permissions that are not available on each comment/reply node, plan a server-side data propagation or response-shape update rather than moving the whole comment tree to client-only rendering.

## E2E planning implications for Article comment ACL

When planning Playwright coverage for Article comment ACL/comment-gating gaps:

- Prefer true integration E2E with a gated test-only fixture helper over Playwright route mocks when the target behavior includes SSR Article privileges, comment-thread rendering, or server-action denial toasts. Route mocks can miss backend/frontend contract issues and are brittle around Next.js server actions.
- If existing editor/UI helpers cannot create custom Article ACL state, plan a narrow `/api/test-only/...` fixture route that mirrors `src/app/api/test-only/_lib/isEnabled.ts` and existing test-only route patterns. Record the gate prerequisite explicitly: non-production runtime plus `TEST_E2E_AUTH_HARDENING=1`; the route should return 404 when disabled.
- Keep fixture routes constrained to named scenarios and known E2E users. Do not plan broad arbitrary-owner Article/comment mutation endpoints. Make the ownership/session path explicit: either use a user1-authenticated request context for user1-owned fixtures or restrict the route itself to known user1/user2 fixture operations.
- Include fixture cleanup or deterministic E2E prefixes so seeded Articles/comments do not silently pollute the E2E environment.
- For denied-viewer scenarios, seed fixtures as one user (for example user1) and assert as a distinct authenticated viewer (for example user2) to avoid owner bypass or self-created-resource behavior.
- For owner-override scenarios, seed/fetch/visit as the owner and make the published-Article precondition explicit. Before UI assertions, fetch `/api/article/?id=<articleId>` as the owner and assert both `status === 'published'` and `privileges.comment.create === true`; for closed ACL also assert `acl.comment.create.allowedAudiences === []`, and for explicit owner-deny coverage assert safe public deny-list metadata if exposed.
- For explicit owner deny-list coverage, prove both sides: a route/unit test should verify the test-only route wrote the owner ID into `users.deny`, while the owner API/E2E assertion verifies the backend still returns `privileges.comment.create === true`. Do not expose arbitrary ACL mutation request payloads just to make this easier.
- Before UI assertions, fetch or inspect the seeded Article as the relevant viewer when practical and verify effective `privileges.read` / `privileges.comment.create` matches the scenario.
- To E2E server-action denial copy for `article_comment_acl_denied` or `article_not_commentable`, plan a stale-permission/commentability flow: load while the composer is allowed/rendered, mutate ACL/status through the gated helper, then submit and assert the resolved user-facing copy. If the helper cannot safely create that state, document the E2E case as blocked and keep unit-level error-key mapping coverage as the fallback.
- In browser E2E, assert resolved locale copy or stable toast content rather than raw translation keys unless the app actually renders keys in that environment.
- If a generic API seeding proposal already exists under `tasks/out-of-scope-issues/proposal/`, update it only when new findings materially change it; do not duplicate out-of-scope issues.

## Article smoke stabilization planning notes

When planning from an Article posting / visibility / comment ACL smoke log, keep the plan anchored to the logged evidence rather than re-running browser mutations in planning mode. Common stabilization findings and plan targets:

- First publish can fail with `type_required` even after selecting a type; plan a failing regression that selects a type, opens/closes Post settings, then sends once without reselecting. Inspect `ActionState.Provider`, `TypeState.Provider`, `OptionLabel`, `SaveButton`, and `VisibilityButton` before guessing at the root cause. Preserve backend `type_required` for truly missing type.
- Fresh Article settings can visually or behaviorally fall back to `Draft` after opening Post settings while the actionbar label shows `Everyone can see`; plan coverage that opening/closing settings is read-only unless an option is clicked and that publish status is not downgraded except for explicit Draft selection.
- Paid-content creator subscriber-only coverage should use the known `test03` paid-content creator fixture/profile when available; if `PAID_CONTENT_CREATOR_E2E_READY=1` is unavailable, document it as an environment blocker rather than removing the scenario.
- Transient duplicate comments after submit usually belong in the `Comments` optimistic/persisted merge path. Plan `_id` de-dup where persisted groups win once `initialComments` contains the newly saved comment, while preserving pagination and server-derived `canCreateComment` gating.
- Radix dialog warnings like `Missing Description or aria-describedby={undefined} for {DialogContent}` in Article Post settings should be planned as a narrow modal-description fix: add optional `description` support to the shared `Modal`, pass article-settings-specific i18n copy from `VisibilityButton`, keep the description visually unobtrusive if needed, and include console-warning plus component/a11y coverage when practical.

## Relevant frontend files observed

- Article page: `src/app/users/[username]/article/[articleId]/page.tsx`
- Comment permalink page: `src/app/users/[username]/article/[articleId]/comment/[commentId]/page.tsx`
- Article view: `src/components/content/article/article.tsx`
- Article form shell/state: `src/components/articleForm/articleForm.tsx`, `src/components/articleForm/state/action.tsx`, `src/components/articleForm/state/type.tsx`
- Article type selector: `src/components/articleForm/components/typeSelector/typeSelector.tsx`, `src/components/articleForm/components/typeSelector/components/optionLabel/optionLabel.tsx`
- Article actionbar/settings: `src/components/articleForm/components/actionbar/actionbar.tsx`, `src/components/articleForm/components/actionbar/components/saveButton/saveButton.tsx`, `src/components/articleForm/components/actionbar/components/visibilityButton/visibilityButton.tsx`
- Shared modal/dialog: `src/components/common/ui/modal.tsx`, `src/components/common/ui/dialog.tsx`
- Comment list: `src/components/content/article/components/comments/comments.tsx`
- Comment permalink view: `src/components/articleCommentView/articleCommentView.tsx`
- Comment actionbar/reply link: `src/components/content/article/components/comments/components/commentActionbar/commentActionbar.tsx`
- Comment form placeholder: `src/components/articleCommentFormPlaceholder/articleCommentFormPlaceholder.tsx`
- Article schema: `src/models/base/article/schema/apiSource.ts`
- Article model: `src/models/base/article/article.ts`
- Article comment server action: `src/server/actions/articleComment/articleComment.ts`
- E2E helpers/specs: `src/tests/e2e/helpers/article.ts`, `src/tests/e2e/auth/articleFormSettings.spec.ts`, `src/tests/e2e/auth-user3/articleFormSettings.spec.ts`, `src/tests/e2e/auth/articleCommentFeed.spec.ts`, `src/tests/e2e/auth-user2/articleCommentAcl.spec.ts`
