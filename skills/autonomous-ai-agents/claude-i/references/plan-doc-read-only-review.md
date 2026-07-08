# Plan-doc read-only review with Claude Code

Use this pattern when the user asks for a Claude Code review of task planning docs (`/skill plan-doc`, `tasks/<slug>/spec.md`, `todo.md`) rather than implementation code.

## Bundle first

Create a read-only bundle outside the repo, typically under `/tmp/hermes-review/`, that includes:

- Review scope and exact task-doc paths.
- `git status --short` so Claude can see untracked task docs.
- The full contents of `spec.md` and `todo.md`.
- Relevant package scripts if the plan cites verification commands.
- Any static scan result that matters (for docs, usually an obvious secret-assignment scan).

Do not rely on `git diff` alone: newly-created task docs are often untracked and would be omitted.

When generating the bundle from Hermes tools, avoid embedding `read_file` dedup/cache placeholders in place of real file contents. If you build the bundle inside `execute_code`, prefer direct filesystem reads (for example Python `Path(...).read_text()`) for local text files, then validate the saved bundle before review. Search for markers such as `dedup`, `content_returned`, `[OUTPUT TRUNCATED]`, `Truncated`, or `omitted`; if any appear where source content should be, regenerate the bundle before launching Claude. A reviewer must judge the immutable bundle, not the parent conversation's earlier tool output.

## Prompt shape

Tell Claude explicitly:

- This is a **READ-ONLY review gate**.
- Do not edit files, commit, or run tests/build/lint.
- Inspect only the provided bundle unless there is a clear reason to request more.
- Check completeness, internal consistency, safety gates, acceptance criteria, verification commands, simplify/review gates, manual notes, and kickoff prompt.
- Return a bounded verdict format, for example:

```text
VERDICT: APPROVED or CHANGES_REQUIRED

BLOCKING FINDINGS:
- If none, write "None".

NON-BLOCKING SUGGESTIONS:
- If none, write "None".

SUMMARY:
One short paragraph.
```

## Permission prompts

Claude may ask for permission to read the `/tmp/hermes-review` bundle. Approve only the prepared review directory/scope, not broad filesystem access.

If Claude asks to run commands during a plan-doc review, keep the gate read-only and bounded:

- Approve narrow, directly relevant read-only checks only when they materially validate the plan's concreteness (for example `test -e`/`ls` for plan-referenced paths, or reading a specific source file whose exact symbol/class claim appears in the bundle).
- Deny or narrow broad repository sweeps, tests/builds/lint, writes, commits, network calls, or commands unrelated to the planning-doc verdict.
- If denying a broad check, feed Claude the specific path/source facts already verified by Hermes so it can continue without expanding scope.

## If Claude suggests doc polish

If the suggestions are useful, patch the task docs directly. Any post-review change makes the approval stale, even if it is documentation-only. Regenerate the bundle and rerun Claude review on the final docs before claiming the review gate passed.

If the final rerun is already `APPROVED` and returns only minor non-blocking polish, do not create an endless stale-review loop by editing again automatically. Save those remaining suggestions in the review artifact with a disposition such as "left as non-blocking implementation guidance" unless they materially change acceptance criteria, safety, or implementation scope.

## Artifact

Save the final verdict under the task directory, for example:

```text
tasks/<slug>/reviews/claude-plan-doc-review.md
```

Include timestamp, reviewer (`Claude Code via claude-i interactive tmux`), scope, bundle path, static scan result, final verdict, and concise summary.