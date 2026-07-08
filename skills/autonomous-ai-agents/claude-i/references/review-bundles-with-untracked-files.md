# Review bundles with untracked implementation files

Use this when asking interactive Claude Code to perform a read-only final review of local implementation work, especially before commit/push.

## Problem observed

`git diff` and `git diff --stat` do not include the contents of untracked files. If the implementation added new helper/test files and the review bundle only contains normal diffs, Claude will correctly say the bundle is incomplete and request direct file reads. In interactive Claude Code this can trigger many permission prompts and may exhaust the orchestrator's tool budget before a final verdict is captured.

## Bundle recipe

For each repo in scope, include:

1. Repository path, current branch/upstream, and `git status --short`.
2. `git diff --stat` and `git diff` for tracked modifications.
3. `git ls-files --others --exclude-standard` for untracked files.
4. For every relevant untracked file, include either:
   - full file content with a clear header, or
   - `git diff --no-index -- /dev/null <file> || true` output.
5. The task spec/todo/review artifacts if they are part of the gate.
6. Exact verification commands and real outputs.

Keep secrets out of the bundle. If auth/storage files are relevant, summarize their existence without printing tokens/cookies.

## Example shell fragment

```bash
{
  echo '# Repo: backend';
  git -C /workspace/dev/buffdemy-backend status --short;
  git -C /workspace/dev/buffdemy-backend diff --stat;
  git -C /workspace/dev/buffdemy-backend diff;
  git -C /workspace/dev/buffdemy-backend ls-files --others --exclude-standard | while read -r f; do
    case "$f" in
      apps/api/src/*|packages/*/src/*)
        echo "\n## Untracked: $f";
        git -C /workspace/dev/buffdemy-backend diff --no-index -- /dev/null "$f" || true;
        ;;
    esac
  done
} > /tmp/final-review-bundle.txt
```

## Claude prompt note

Tell Claude that the bundle is intended to be self-contained and that direct repository reads should only be requested if the bundle is missing a specific needed file. This keeps the review read-only and reduces permission churn.
