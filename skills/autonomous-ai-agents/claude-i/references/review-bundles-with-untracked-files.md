# Review bundles with untracked files

For review gates, do not rely on `git diff` alone. New untracked files are omitted from normal diffs.

Recommended bundle sections:

```bash
{
  echo '===== git status --short ====='
  git status --short
  echo '===== tracked git diff ====='
  git diff --no-ext-diff -- .
  echo '===== untracked files ====='
  git ls-files --others --exclude-standard
  # append full contents of relevant untracked text files
} > /tmp/review-bundle.md
```

Tell the reviewer to prefer the prepared bundle and request direct file reads only for specific gaps.
