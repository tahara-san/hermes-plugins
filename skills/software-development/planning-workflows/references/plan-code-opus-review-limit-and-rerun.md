# Plan-code Opus 4.8 @ xhigh effort review limit, blocker, and rerun pattern

Use when a mandatory `/plan-code` review lane is explicitly overridden to Claude Code Opus 4.8 @ xhigh effort and the review hits usage limits, stalls while reading a large bundle, or returns `CHANGES_REQUIRED`.

## Pattern

1. **Preflight both interactive reviewer CLIs before launch.** Confirm Claude Code can accept the prompt with the requested Opus 4.8 @ xhigh effort banner, and confirm bare `codex` can start in managed tmux with GPT-5.6 SOL @ xhigh. Finalize the immutable bundle, then launch both lanes before waiting on either. If a lane blocks and its artifact updates change the reviewed bundle, mark both reviews stale, regenerate the bundle, and rerun both lanes.
2. **Verify the model/effort before the substantive prompt.** Prefer launching interactive Claude Code directly with `claude --model opus --effort xhigh` inside tmux, then capture the banner/status showing `Opus 4.8 with xhigh effort` before sending the review bundle prompt. If the user changes the requested model or effort mid-task, apply it to the next Claude Code review, do not rewrite historical review artifacts, and record the new banner in the new raw/structured artifacts.
3. **If Claude Code hits a usage-limit prompt before verdict, fail closed.** Save the pane as a blocked artifact and write a structured blocker artifact naming:
   - reviewed bundle path;
   - observed model/banner;
   - failure mode (usage-limit prompt, no verdict);
   - companion review state;
   - exact resume choices (retry after reset, waiver, or replacement reviewer).
4. **When the user says the limit should be lifted, retry the same lane** against the current bundle. Do not count the earlier blocked attempt as approval.
5. **Bound large-bundle reads.** If Claude Code spends several minutes reading/exploring despite a read-only bundle prompt, ask it to stop exploration and return the requested verdict. If that queues behind a tool call, interrupt with `Ctrl-C`, then send a no-tools verdict request based only on already-loaded context.
6. **If Claude Code returns `CHANGES_REQUIRED`, fix the smallest worth-addressing findings.** Add focused regressions where practical, rerun impacted builds/tests, rerun simplify, and regenerate the review bundle.
7. **Treat all previous review lanes as stale after any source/test/task-doc change.** Start a new pinned interactive Codex TUI review against the regenerated bundle and rerun Claude Code on the same bundle, launching both before waiting on either. Save older tmux sessions/artifacts/bundles as superseded; a verdict from the old bundle must not satisfy the current gate.
8. **Save both raw and structured artifacts.** Keep raw Claude Code pane output, then write a parseable verdict/blocker JSON that records `passed`, `status`, `bundle_path`, `raw_artifact`, `model_banner_observed`, findings, and summary.
9. **Do not advance phases while a required Codex review has only started.** If the Claude Code lane passes but the interactive Codex TUI is pending, write a pending artifact naming the current tmux session, latest raw pane capture, completed companion review, verification evidence, stale/superseded session ids, and resume steps.
10. **If the interactive Codex TUI does not produce a verdict, exhaust bounded tmux recovery before blocking.** Capture a wide pane window and verify any final response against the bundle identity and model/effort attestation. If no parseable verdict exists, start a fresh pinned TUI session with a narrower self-contained bundle focused on the current blockers/fixes. Never substitute `delegate_task`, `codex exec`, or `codex review`. If no parseable attested verdict exists after bounded recovery and the narrower interactive rerun, save a pending/blocker artifact and stop fail-closed.

## Pitfalls

- A Claude Code usage-limit prompt is not a reviewer verdict.
- A queued “save the verdict” or suggested next action in the Claude Code input line can accidentally submit stale instructions during cleanup. Clear the input (`Ctrl-U`) before `/exit`.
- Historical bundles, raw panes, and ordinary task-doc diffs can contain stale reviewer-model wording in removed lines. When the user changes the required review model mid-session, regenerate the active implementation bundle from current-file snapshots for task docs plus source diffs/snapshots, and mechanically verify the active bundle has no stale model-name hits before dispatching the rerun.
- If the source changes after an interactive Codex review starts, that review is stale even if it later returns approval.
- If a Claude Code or interactive Codex review returns `PASS` but you apply a follow-up cleanup afterward (even a small test-fixture alignment from a non-blocking observation), mark that pass as superseded, rerun verification, regenerate the bundle, and rerun every mandatory review lane against the new tree.
- Review bundles must be self-contained and untruncated. When generating large plan-code bundles, avoid capped helper output and assert the saved bundle contains no `[OUTPUT TRUNCATED` marker. See `references/plan-code-review-bundle-truncation.md`.
