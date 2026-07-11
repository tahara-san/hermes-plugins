# Plan-code final bundle scope and scan precision

Use when a `plan-code` task has post-review contract changes, regenerated implementation bundles, touched tests/callers, and negative scans such as “remove compatibility/fallback/migration code.”

## Problem this prevents

A final reviewer can approve implementation semantics but still find the bundle incomplete or misleading if:

- `git status` lists a modified file that is missing from the bundle diff/stat/snapshot because the path was mistyped.
- A broad stale-code scan finds unrelated helpers with the same name/class of operation and makes the bundle look dirty even though the targeted compatibility path is gone.
- A prior approved review is reused after a docs-only or bundle-only fix, even though the reviewed artifact no longer matches the final tree.

## Required sequence

1. Build the file list mechanically from the current tree before writing the final bundle:
   - `git diff --name-only`
   - intended untracked task artifacts via `git ls-files --others --exclude-standard -- tasks/<slug>`
   - any source/test file touched by a prop/API removal, even if it is “only a mock” test update.
2. Validate the bundle against that file list before dispatching reviews:
   - every modified tracked file appears in the diff/stat section;
   - every modified tracked file has a file snapshot under the exact repository path;
   - no snapshot says `[MISSING]`;
   - validation searches include common path typos, especially nested test paths such as `src/components/editors/answerEditor/answerEditor.test.tsx` vs `src/components/editors/answerEditor.test.tsx`.
3. When the requirement is “remove compatibility / migration / fallback code,” define the target boundary precisely in the bundle:
   - what exact prop/helper/old field is being removed;
   - which callsites are in scope;
   - which similarly named helpers are canonical current-shape construction, not compatibility.
4. Prefer targeted negative scans over broad repo-wide claims:
   - scan for the exact removed symbol everywhere (for example `fallbackBody`);
   - scan the old implementation file for its deleted helper (for example `QuestionPaperViewer` for `bodyNodesFromText`);
   - scan known callsites for old fields/props (for example `question.body` / `fallbackBody`);
   - scan relevant source surfaces for `compat|migration|migrate|deprecated` markers.
   - when the bundle includes task docs/progress files, report static scans separately for implementation source/tests versus task-doc prose. Classify safe test placeholders and doc-prose false positives (for example words like “any” or “TODO files”) explicitly so reviewers do not chase scan noise while still seeing the docs for contract review.
5. If a reviewer finds a bundle omission or misleading scan after approving the implementation:
   - save that reviewer output as superseded, even if it says `APPROVED`;
   - regenerate the bundle with the corrected path/scope language;
   - rerun both mandatory review legs against the corrected bundle.
6. Do not finalize on a started session alone. If the corrected interactive Codex TUI is pending, save a pending artifact naming the tmux session, raw pane capture, and exact bundle path/hash.

## Good bundle validation checklist

- [ ] `git diff --name-only` is a subset of bundle diff/stat paths.
- [ ] Each modified tracked file has a snapshot with the exact path.
- [ ] Bundle contains no `[MISSING]`, truncation markers, or cache/dedup placeholders.
- [ ] Negative scans are scoped to the old compatibility surface and do not overclaim unrelated current helpers.
- [ ] Verification evidence includes the focused tests that exercise the removed compatibility path and any caller mocks changed by the prop/API removal.
- [ ] Browser smoke deviations caused by missing live data are documented without treating them as proof of the unrendered branch.
