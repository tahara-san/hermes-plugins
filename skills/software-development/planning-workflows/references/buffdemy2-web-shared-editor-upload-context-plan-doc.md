# Buffdemy2-web shared editor upload-context plan-doc pitfall

Use when planning frontend media-upload changes in `buffdemy2-web`, especially Article editor upload contracts that touch `src/components/articleForm/components/paperEditor/**`, `LocalMedia`, or `Uploader.fetchPresigned()`.

## Problem pattern

The ArticleForm paper-editor stack is shared beyond Article creation/editing. A plan-doc that says “add `postType: 'article'` in `ItemEditor`, `useOnFiles`, or shared `PaperEditor`” can leak Article quota context into non-Article flows.

Current-source pattern observed:

- `QuestionEditor` imports shared `~/components/articleForm/components/paperEditor` and renders `<PaperEditor />` for question details.
- `AnswerEditor` imports the same shared `PaperEditor` for answer composition.
- `ArticleCommentForm` wraps and reuses shared `ItemEditor` from ArticleForm paper-editor components.
- Those shared paths create `new LocalMedia({ file, isLocal: true })`, leading to `LocalMedia.upload()` → `Uploader.fetchPresigned()` → media server action → backend `POST /media`.

## Plan-doc rule

For Article-only backend upload contracts:

1. **Do not hardcode Article context in shared components.** Shared `PaperEditor`, `ItemEditor`, `useOnFiles`, and `LocalMedia` defaults must stay neutral.
2. **Scope Article context at the true ArticleForm boundary.** Prefer an upload-context provider or prop set by `ArticleForm` around its `<PaperEditor />`; shared components only pass through the supplied context.
3. **Default non-Article wrappers to no `postType`.** `QuestionEditor`, `AnswerEditor`, `ArticleCommentForm`, and follow-up/comment wrappers must not inherit `postType: 'article'` unless a product/backend contract explicitly says they should.
4. **If backend rejects non-Article `/media` without a post type, block honestly.** Save a backend/product contract blocker instead of “fixing” those paths with `postType: 'article'`.
5. **Require wrapper-level tests.** Test both the positive Article wrapper and representative non-Article wrappers, not just uploader/unit absent-context behavior.

## Review/rebundle lesson

When any stale review returns for a superseded plan bundle, still disposition concrete findings against the current docs. If the finding exposes a live footgun (as this shared-editor context leak did), patch the docs, mark older review artifacts stale, regenerate the bundle, then launch both required interactive review legs against that same immutable bundle before waiting on either. A stale review cannot satisfy the gate, but its findings can still be valid.

## Implementation review pitfalls

When executing this class of upload-context task, reviewers can catch lifecycle bugs that simple prop/request tests miss:

1. **Mapped upload-error toasts need a long-lived owner.** If a transient component such as an upload fuse/progress widget owns quota/post-type toasts, it may unmount immediately when `LocalMedia.upload()` changes status to `UPLOAD_INITIATED`, before an async presign failure dispatches. Put the mapped-error toast handling in a component that remains mounted across `FILE_SPECIFIED` → `UPLOAD_INITIATED` → `ERROR` (for example `LocalMediaPreview`) and test that the generic toast is not duplicated.
2. **Manual upload and auto-upload must share the same error surface.** A regression that dispatches an error directly while the fuse is mounted is insufficient. Prefer a component/status-level test that represents `UploadButton` or fuse-triggered `media.upload()` after the status transition.
3. **Normalize the real server-action/API envelope.** Backend quota metadata may be nested inside server-action error content, e.g. `content.error.content`, not only on the immediate error object. Add normalizer tests using the real `serverAction.error` / API error shape so `resetAt`, `limit`, and `used` reach the `*_with_reset` i18n branch.
4. **Clear stale mapped errors.** Reset stored mapped upload error state at the start of a new upload and when later string/generic media errors are handled, so an old `suppressGenericToast` flag cannot hide unrelated future failures.