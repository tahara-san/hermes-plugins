# Plan-code review bundles: avoid truncation and stale approvals

Use when generating mandatory review bundles for `/plan-code` phases, especially when the working tree contains untracked new files or a large diff.

## Lesson

Hermes helper outputs and tool summaries can silently cap large `git diff` results. If a generated bundle contains markers such as `[OUTPUT TRUNCATED ...]`, the review is not self-contained: Claude Code Opus 4.8 @ xhigh effort or a delegate may need extra repo reads, stall on permission prompts, or approve against incomplete context.

## Bundle generation pattern

- Generate the bundle from an uncapped local process (for example Python `subprocess.check_output`) rather than a helper path that caps stdout.
- Include:
  - `git status --short`
  - `git diff --stat`
  - tracked diff for the relevant paths (`git diff --no-ext-diff -- <paths...>`)
  - full contents of relevant untracked files (source, tests, task docs, review artifacts)
  - exact verification commands/results
- After writing the bundle, programmatically assert it contains no truncation markers, e.g. fail if `[OUTPUT TRUNCATED` appears.
- If a reviewer reports bundle truncation, regenerate a fresh bundle and rerun the review lane; do not count the truncated-bundle approval as final if any source/test/doc cleanup follows.

## Stale-review rule

If a reviewer returns `PASS` but you apply even a small cleanup afterward (for example aligning a test fixture shape with production payload shape), mark that pass as superseded, rerun verification, regenerate the bundle, and rerun all mandatory review lanes. This applies even when the finding was labeled non-blocking, because the reviewed source tree changed.
