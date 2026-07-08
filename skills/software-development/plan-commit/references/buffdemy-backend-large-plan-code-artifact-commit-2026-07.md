# Buffdemy backend large plan-code artifact commit pattern (2026-07)

Use this when committing a large completed Buffdemy backend `plan-code` task whose implementation, task directory, generated review bundles, and verification logs are all still untracked/staged for the first implementation commit.

## Pattern captured

1. **Treat `/skill plan-commit` as the two-step flow** when invoked directly for a completed task: first commit/push implementation + task artifacts, then remove the completed task directory and push a cleanup commit.
2. **If the task directory is entirely untracked, include it in the implementation commit first.** This preserves review/spec/evidence history and gives the cleanup commit a real tracked deletion.
3. **Include sanctioned out-of-scope findings that were produced by the task** when they are under the repo's approved out-of-scope path (for Buffdemy backend: `tasks/out-of-scope-issues/<priority>/...`) and clearly discovered during the task. Do not absorb unrelated task dirs.
4. **Active TODO scans must ignore historical review bundles.** Broad `grep -R '^- [ ]' tasks/<slug>` will find stale embedded TODO snapshots inside generated review bundles. Verify active live docs directly (`progress.md`, `todo-phase-*.md`, `final-report.md` if present) and treat historical bundles as reference-only.
5. **Force-add ignored logs only under the intended task directory.** Use `git status --short --ignored -- tasks/<slug>` and force-add referenced verification logs/directories if the task artifacts cite them. Record their total size/count before staging.
6. **Normalize generated artifacts only after staged whitespace failure.** If `git diff --cached --check` fails only inside generated task bundles/logs, strip trailing line whitespace, excess blank EOF lines, CRLF, and `space-before-tab` inside `tasks/<slug>` artifacts/logs. Do not normalize source/test files or unrelated docs.
7. **Run a self-excluded pre-commit artifact-consistency review after normalization.** Create a pending placeholder and bundle that includes staged status, `git diff --cached --check`, active docs, and final consistency verdicts. Dispatch a read-only reviewer. Save/overwrite the placeholder only if the reviewer passes, then rerun JSON + staged whitespace checks before committing.

## Command skeleton

```bash
# discovery
git status --short --branch
git rev-list --left-right --count @{u}...HEAD
git status --short --ignored -- tasks/<slug>

# active docs only, not historical bundles
python3 - <<'PY'
from pathlib import Path
for p in [Path('tasks/<slug>/progress.md'), *sorted(Path('tasks/<slug>').glob('todo-phase-*.md'))]:
    bad=[(i,l) for i,l in enumerate(p.read_text().splitlines(),1) if l.startswith(('- [ ]','- [~]','- [!]'))]
    print(p, bad)
PY

# after explicit staging
git diff --cached --name-status
git diff --cached --check

# after generated-artifact normalization and self-excluded precommit review
git diff --cached --check
git commit -m "implement <task summary>"
git push

git rm -r --dry-run -- tasks/<slug>
git rm -r -- tasks/<slug>
git diff --cached --check
git commit -m "remove completed <slug> task artifacts"
git push
```

## Pitfalls

- Do not use `git add -A` in a dirty or large untracked task workspace.
- Do not let stale unchecked TODO rows inside old review bundles block commit-readiness when active task docs and final consistency verdicts are complete.
- Do not patch reviewed docs after the final consistency verdict merely to make grep output prettier; if commit-prep normalization touches task artifacts, add a narrow pre-commit consistency check instead of reopening implementation review.
- Do not delete the task directory before the first implementation commit if it was untracked; the cleanup commit would become impossible or misleading.
