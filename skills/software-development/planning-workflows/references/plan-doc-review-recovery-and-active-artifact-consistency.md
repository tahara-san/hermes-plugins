# Plan-doc review recovery + active artifact consistency

Use this when a required `plan-doc` review leg returns useful non-blocking suggestions, an interactive reviewer finishes without a saved verdict artifact, or final artifact-consistency checks flag historical/superseded review files instead of active task docs.

## Pattern

1. **Save first-pass reviews before editing.**
   - If Claude/Codex approves but gives useful non-blocking suggestions that reduce ambiguity, save the raw output as `*-initial-superseded` or `*-final-superseded` before changing docs.
   - Patch only the task docs/bundle issues that materially help the implementer.
   - Regenerate the final bundle and rerun both required plan-doc review legs. A prior approval is stale after any task-doc edit.

2. **Make bundle evidence executable and inspectable.**
   - Generate review bundles from direct filesystem reads where possible, not cached/paginated tool snippets.
   - Validate the bundle before dispatching reviewers: no `READ_ERROR`, truncation markers, dedup/cache placeholders, or failed scan transcripts.
   - For static/secret scans, prefer computing the scan inside the bundle-generation script and embedding the result (`NO_FINDINGS` or concrete findings). Avoid brittle shell heredocs inside nested Python/tool scripts; a failed scan transcript is not evidence.

3. **Recover completed interactive reviews instead of rerunning blindly.**
   - A started tmux/TUI session is not approval, but its pane or saved transcript may contain a complete verdict.
   - For Codex, inspect the managed tmux session and capture a wide pane window; require the current bundle identity, GPT-5.6 SOL @ xhigh attestation, and explicit parseable verdict.
   - Save the raw pane and normalized verdict with the recovery path. If no complete verdict is recoverable, rerun bare interactive `codex` against the same current bundle; never substitute `delegate_task`, `codex exec`, or `codex review`.

4. **Defend bundles against terminal redaction.**
   - Hermes terminal output may mask secret-looking environment values (for example `TEST_E2E_AUTH_HARDENING=1` can display as `TEST_E2E_AUTH_HARDENING=***`). Reviewers can misread the masked display as the source value and fail realistic verification commands.
   - When a current runnable command includes an env var that may be redacted, add explicit prose to the review bundle stating the intended literal value and why it is safe/required.
   - Embed a raw ordinal/byte proof around the assignment from direct filesystem reads, e.g. show `[84, ..., 61, 49, 32, ...]` with `49` immediately after `=` for literal digit `1`.
   - Tell both the interactive Codex TUI and Claude Code reviewers not to fail solely on redacted terminal-rendered text; they should use the bundle prose plus ordinal proof to determine the actual source value.
   - If a reviewer already failed on redacted display, save that verdict as `CHANGES_REQUIRED`/superseded evidence, regenerate the bundle with the redaction note and ordinal proof, then rerun all required review legs on the new bundle.

5. **Scope final artifact-consistency to active artifacts.**
   - Historical/superseded bundles often intentionally contain stale markers, failed first attempts, old prompts, or superseded suggestions. Do not fail the final consistency gate on those files.
   - Check active files only: `spec.md`, `todo.md`, `kickoff-prompt.md`, `notes.md`, the final bundle, final raw review artifacts, and aggregate verdict.
   - Exclude `*-superseded*` artifacts and older bundles from active stale-marker scans, while keeping them as historical evidence.
   - Use precise stale markers (`READ_ERROR:`, `OUTPUT TRUNCATED`, `content_returned: false`, `refer to earlier read_file result`) rather than broad substrings like `dedup`, which can appear in valid prose such as "deduped".

## What to record in aggregate verdicts

- Final bundle path.
- Static-scan and `git diff --check` status.
- Raw interactive Codex TUI artifact path, normalized verdict path, and whether recovery was needed.
- Raw Claude Code artifact path and observed model/status.
- Superseded artifacts list.
- Whether any post-review edits occurred and why they do not stale the reviewed plan (for example, aggregate artifact creation or marking Phase 0 review rows complete after raw reviews pass).
- A final active-artifact consistency artifact path and verdict when review artifacts themselves are part of the task directory.
