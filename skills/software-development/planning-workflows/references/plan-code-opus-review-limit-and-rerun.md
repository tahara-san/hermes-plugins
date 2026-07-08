# Plan-code Opus 4.8 @ xhigh effort review limit, blocker, and rerun pattern

Use when a mandatory `/plan-code` review lane is explicitly overridden to Claude Code Opus 4.8 @ xhigh effort and the review hits usage limits, stalls while reading a large bundle, or returns `CHANGES_REQUIRED`.

## Pattern

1. **Preflight Claude Code availability before dispatching companion lanes when practical.** Start the Claude Code session, verify the requested Opus 4.8 @ xhigh effort banner, and confirm it is able to accept the review prompt (not blocked by login/setup/usage-limit prompts) before dispatching an async Codex-style delegate. If a companion lane is dispatched first and the Claude Code lane then blocks before verdict, any blocker artifacts or progress updates written afterward stale the already-dispatched companion review for final-completion purposes; save it as pending/stale, regenerate the bundle after artifact updates, and rerun both lanes.
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
7. **Treat all previous review lanes as stale after any source/test/task-doc change.** Dispatch a new Codex-style review against the regenerated bundle and rerun Claude Code on the same bundle. Save older delegate IDs/bundles as superseded; a pending delegate from the old bundle must not satisfy the current gate.
8. **Save both raw and structured artifacts.** Keep raw Claude Code pane output, then write a parseable verdict/blocker JSON that records `passed`, `status`, `bundle_path`, `raw_artifact`, `model_banner_observed`, findings, and summary.
9. **Do not advance phases while a required companion review is only dispatched.** If the Claude Code lane passes but the Codex-style rerun is pending, write a pending artifact naming the current delegation id, completed companion review, verification evidence, stale/superseded delegation ids, and resume steps.
10. **If the Codex-style delegate does not re-enter, exhaust review-preserving recovery before blocking.** Do a bounded wait, search session history/logs for the exact delegation id, and if no parseable verdict exists, try a narrower delegate review focused on the current blockers/fixes. If a local Codex fallback is available, it may be used only when it produces a parseable verdict against the current bundle; an auth/setup failure before verdict is not a review and should be recorded only as fallback failure evidence in the pending/blocker artifact.

## Pitfalls

- A Claude Code usage-limit prompt is not a reviewer verdict.
- A queued “save the verdict” or suggested next action in the Claude Code input line can accidentally submit stale instructions during cleanup. Clear the input (`Ctrl-U`) before `/exit`.
- Historical bundles, raw panes, and ordinary task-doc diffs can contain stale reviewer-model wording in removed lines. When the user changes the required review model mid-session, regenerate the active implementation bundle from current-file snapshots for task docs plus source diffs/snapshots, and mechanically verify the active bundle has no stale model-name hits before dispatching the rerun.
- If the source changes after a Codex-style delegate is dispatched, that delegate is stale even if it returns later with approval.
- If a Claude Code/Codex review returns `PASS` but you apply a follow-up cleanup afterward (even a small test-fixture alignment from a non-blocking observation), mark that pass as superseded, rerun verification, regenerate the bundle, and rerun every mandatory review lane against the new tree.
- Review bundles must be self-contained and untruncated. When generating large plan-code bundles, avoid capped helper output and assert the saved bundle contains no `[OUTPUT TRUNCATED` marker. See `references/plan-code-review-bundle-truncation.md`.
