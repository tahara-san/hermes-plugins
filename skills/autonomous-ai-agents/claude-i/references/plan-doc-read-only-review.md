# Plan-doc read-only review with Claude Code

Use this pattern when the user asks for a Claude Code review of task planning docs (`/plan-doc`, `tasks/<slug>/spec.md`, `todo.md`) rather than implementation code.

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
- Judge the plan against its explicit stated scope, not an imagined ideal plan.
- A finding is **blocking** only when it is grounded in the bundle, names a concrete failure mode, violates an explicit requirement/acceptance criterion/repository rule/verification guarantee, and is material — it can cause unsafe implementation, incorrect commands, wrong authorization or data-integrity behavior, a missing decision that forces the implementer to invent material behavior, or a required verification that cannot establish the promised guarantee.
- Do **not** turn wording style, formatting, naming, optional readability, extra hardening beyond adequate coverage, speculation without an evidenced failure path, or unsupported-environment portability into blocking findings. Report those as non-blocking suggestions.
- `APPROVED` is the correct verdict when only non-blocking suggestions remain.
- Each blocking finding must state its evidence, failure mode, the violated requirement, and the required correction. Do not return `CHANGES_REQUIRED` with an empty or unexplained blocking list.
- Return a bounded verdict format with no preamble before the verdict line, for example:

```text
VERDICT: APPROVED or CHANGES_REQUIRED

BLOCKING FINDINGS:
- If none, write "None". Otherwise: evidence, failure mode, violated requirement, required correction.

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

Do not patch by default. Classify each suggestion with the blocker predicate above and record one disposition per item in the round ledger — the ledger is review-evidence, so writing it does not stale anything.

Patch the task docs only for a confirmed blocker. Any judged-product change makes the approval stale even when it is documentation-only, so regenerate the bundle and rerun Claude review on the final docs before claiming the gate passed.

If the verdict is `APPROVED` with only non-blocking polish, the gate is done. Save those suggestions in the review artifact with a disposition such as "left as non-blocking implementation guidance" and do not edit again — editing here is exactly what creates the endless stale-review loop.

If Claude returns `CHANGES_REQUIRED` on a finding you adjudicate as failing the blocker predicate, do not override the verdict and do not edit the docs to appease it. Save the adjudication, then run one bounded same-byte clarification rerun of this lane against the unchanged bundle, restating the materiality policy. If it still returns `CHANGES_REQUIRED`, stop and escalate to the user.

## Artifact

Save the final verdict under the task directory, for example:

```text
tasks/<slug>/reviews/claude-plan-doc-review.md
```

Include timestamp, reviewer (`Claude Code via claude-i interactive tmux`), scope, bundle path, static scan result, final verdict, and concise summary.