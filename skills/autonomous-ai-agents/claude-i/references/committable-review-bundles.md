# Committable Review Bundles

Use this when a Claude Code review artifact/bundle will be committed as part of a task directory.

## Problem

Prepared review bundles often embed raw `git diff` output. Diff lines can contain trailing whitespace, and Markdown bundle generators can leave blank lines with spaces. If the bundle is staged, `git diff --cached --check` may fail even though the source code is clean.

## Pattern

1. Generate the review bundle before starting Claude so untracked files are included.
2. If the bundle is intended to be committed, normalize Markdown whitespace before staging:

```python
from pathlib import Path
for path in Path('tasks/<task>/reviews').glob('*.md'):
    text = path.read_text(errors='replace')
    lines = text.splitlines()
    path.write_text('\n'.join(line.rstrip() for line in lines) + '\n')
```

3. Save the Claude verdict artifact separately from the large bundle when possible.
4. Run `git diff --cached --check` after staging the final docs/artifacts and before commit.
5. If a late source/test/doc change happens after a required review, run a narrow delta review and save a separate artifact instead of editing the old approval in place.

## Pitfalls

- Do not use `git add tasks/<task>` blindly if the task directory contains stale or superseded review bundles that were not part of the final review scope.
- Do not update TODOs/review artifacts after the last mandatory review unless you either included the intended final state in the review bundle or run a final delta/artifact-consistency review.
- Treat generated review bundles as commit artifacts: whitespace, stale paths, and missing untracked contents can all block a clean commit or invalidate the review trail.
