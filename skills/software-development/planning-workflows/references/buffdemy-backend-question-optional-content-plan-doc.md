# Buffdemy backend Question optional content plan-doc pitfalls

Use when planning Buffdemy backend Question create/update changes that make `QuestionContent.body` or `QuestionContent.papers` optional, title-only, or otherwise loosen required content rules.

## Preserve raw caller intent before normalization

Do not let normalization/filtering erase the difference between:

- omitted `papers` or `papers: []` — intentional title-only content; and
- a non-empty raw `papers` array that later validates/filters to zero — attempted paper content that was empty, malformed, or unresolved.

In this repo, `validateAndPreparePapers` filters content-less paper inputs and unresolved media references. A plan that simply removes a `!validatedPapers.length` / `question_content_required` guard can silently convert malformed non-empty paper arrays into valid title-only Questions. Require implementers to track raw-paper intent before validation and add tests for non-empty raw arrays that validate to zero.

Also check any route-level preprocessing before repository calls. For Question create, mention normalization can sit between `body.papers` and the repository; the plan should state whether it preserves array length so the repository can still distinguish non-empty raw intent.

## Defaults belong to full rows, not partial updates

If `QuestionContent` create/upsert inputs get canonical defaults (`body: ''`, `papers: []`), keep partial update schemas partial. Do not default omitted `body`/`papers` in `questionContentUpdateSchema` or status-only update paths can accidentally `$set` existing content to empty.

Plans should require a regression test proving partial status/content-version updates preserve existing `body` and `papers` when those fields are omitted.

## Ready-schema relaxation must not over-loosen content-less arrays

For title-only Questions, the safe ready-content invariant is usually:

```ts
papers.length === 0 || hasReadyPaperContent(papers)
```

This allows the canonical title-only storage shape (`papers: []`, `body: ''`) while preserving rejection of non-empty but content-less arrays such as `[makePaper('')]`. Do not tell implementers to delete the existing content-required refinement outright; tell them to adapt it and preserve/update the existing negative test.

## Plan-doc review pattern for this class

When a reviewer finds one of these issues during plan-doc review:

1. Save the raw failing review artifact as initial/superseded.
2. Patch `spec.md`, `todo.md`, `kickoff-prompt.md`, and `notes.md` so the corrected invariant appears in every handoff surface.
3. Regenerate the plan-review bundle; mark any already-dispatched delegate review as stale if the bundle changed after dispatch.
4. Rerun both required review legs before writing an aggregate approval.
