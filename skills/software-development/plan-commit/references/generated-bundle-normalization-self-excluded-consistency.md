# Generated Bundle Normalization + Self-Excluded Consistency

Use during `plan-commit` when generated Markdown review bundles/logs are part of the first implementation commit.

## Trigger

- `git diff --cached --check` fails only inside intended generated task artifacts (review bundles, raw panes/logs, consistency bundles).
- Final review artifacts or TODO/final-report files were written after the implementation reviews and need a pre-commit artifact-consistency gate.
- A consistency verdict file itself would become part of the committed task directory.

## Pattern

1. **Stage only intended scope first**
   - Stage exact implementation paths and `tasks/<slug>/`.
   - Verify with `git diff --cached --name-status`.

2. **Normalize only generated artifacts that failed whitespace checks**
   - Strip trailing line whitespace and excess blank EOF lines only in generated review/log bundles.
   - Do not normalize source files or unrelated docs broadly.
   - Restage normalized files.
   - Rerun `git diff --cached --check`.

3. **Use a self-excluded placeholder for consistency verdicts**
   - Create `tasks/<slug>/reviews/precommit-artifact-consistency.json` or `post-normalization-artifact-consistency.json` with `verdict: PENDING`.
   - State explicitly: this verdict file is excluded from its own reviewed scope and will be overwritten after review.
   - Generate a consistency bundle that includes live task docs, canonical final review artifacts, staged status/check output, and referenced artifact existence.

4. **Review the exact staged artifact state**
   - Ask a read-only reviewer to check: no unfinished real TODOs, final report/final review agree, referenced artifacts exist, stale pending/blocked artifacts are marked historical, staged whitespace check passes.
   - Historical review bundles/raw panes should be reference-only and not judged for embedded stale prose.

5. **Save the verdict without creating another loop**
   - Overwrite the self-excluded placeholder with the approved verdict.
   - If the reviewer offers only cosmetic suggestions about historical artifact metadata, record them in `non_blocking`; do not patch more artifacts unless the inconsistency is blocking.
   - Restage the verdict and rerun `git diff --cached --check`.

6. **Commit after final staged readback**
   - `git diff --cached --name-status`
   - `git diff --cached --stat`
   - `git diff --cached --check`
   - `git status --short --branch`

## Pitfalls

- Generating a consistency bundle before its placeholder/verdict files are staged can make the bundle's status snapshot stale. Stage the placeholder/bundle, then regenerate/re-stage the bundle once if needed.
- Applying cosmetic reviewer suggestions after an approved consistency check creates another post-review artifact change. Prefer recording cosmetic suggestions in the verdict.
- Do not include the future consistency verdict file in its own judged scope; otherwise every saved verdict stales the approval.
