# Buffdemy backend Question author-content-required plan-doc pitfalls

Use when planning Buffdemy backend Question create/update changes that remove caller-supplied `title`, restore required Question body/content, add a minimum rendered-text requirement, or reverse prior title-only/optional-content work.

## Keep author minimums out of universal ready-row schemas

A 16-character/16-code-point minimum requested for caller-authored Question content is an **author write contract**, not automatically a universal `QuestionContent` ready-row contract.

In this repo, `questionContentReadySchema` and `questionContentReadyCreateInputSchema` are used beyond Question create/update author writes:

- ready-row reads/hydration such as `findReadyByQuestion()` and `batchFindReadyForQuestions()`;
- derived/manual/machine content rows written through generic content-row helpers such as `updateStatus()`;
- downstream fanout/content-resolution paths that parse existing ready rows.

Do not plan a blind `.min(16)` or equivalent on shared ready schemas unless the product explicitly wants to reject historical/derived ready rows and read paths. Scope the new minimum to `source: 'author'` writes, preferably at the Question repository derived-body validation and/or an author-only guard in `upsertAuthorRow()`.

## Close title-only behavior at the author boundary

When removing caller `title` and requiring content again:

- remove `title` from API write schemas and repository create/update inputs;
- reject caller `title` as an unknown property rather than ignoring it as a compatibility alias;
- make `papers`/content required at API level where practical, but keep repository validation authoritative;
- reject omitted papers, `[]`, default empty-editor papers, contentless papers, whitespace-only text, missing-media-only papers, and rendered-short text before parent/content/outbox side effects;
- remove or repurpose helper logic created only to support title-only acceptance, such as default-empty-paper intent helpers.

If `requireReadyPaperContent()` or a similar shared refinement contains an empty-array allowance (`papers.length === 0`), do not edit that shared refinement in place if it is used by reads/derived rows. Close the empty-content allowance with an author-scoped guard/refinement at the repository/upsert-author boundary instead.

## Define rendered-text length precisely

When a user specifies a rendered text minimum:

- measure text from the same rendered/editor extraction path used for persisted body text (for example `contentHelper.getTextFromNodes()`), not `JSON.stringify(bodyNodes)`;
- state the character unit explicitly. Default for this project: Unicode code points via a shared helper such as `Array.from(normalizedText).length`, not UTF-16 `String.length`, unless product chooses otherwise;
- pin the unit with tests, ideally including an emoji/non-BMP boundary case or direct helper assertion;
- if multiple papers are combined through `deriveQuestionBody()` with `\n\n` separators, document whether those persisted separators count toward the minimum and add a two-short-papers boundary test.

## Preserve derived title compatibility unless scope expands

Removing caller title does not necessarily mean removing persisted/public/search `title` fields. For Buffdemy Question plans, default to deriving persisted `QuestionDocument.title` / `QuestionContent.title` from valid author rendered content so existing response/search consumers continue to work. If an implementer proposes deleting those fields from responses/search messages, stop for a broader API/search/frontend compatibility decision.

## Tests and side effects to require

A good plan should require tests for:

- API schema/body rejection of unknown `title` and missing/empty content;
- direct repository create/update rejection outside the API route;
- rendered-text 15/16 boundary and JSON-long-but-rendered-short bodyNodes;
- emoji/code-point counting if code points are the selected unit;
- valid exactly-minimum content deriving deterministic title/body;
- invalid create/update leaving no parent Question, QuestionContent row, outbox message, mention fanout, search job, or stale-derived-content update;
- author `upsertAuthorRow()` rejecting sub-minimum author body while derived/manual/machine ready rows and ready-row reads remain unaffected;
- partial content-row updates preserving omitted body/papers.

## Review pattern

This class often needs review-driven plan refinements. If a reviewer returns `APPROVED_WITH_NOTES` but identifies concrete implementation footguns (for example shared ready schemas used by derived rows, ambiguous `String.length`, or strict-body rejection being optional), incorporate those footguns into `spec.md`, `todo.md`, `kickoff-prompt.md`, and `notes.md`; regenerate the bundle; and rerun both required plan-doc review legs before claiming approval.