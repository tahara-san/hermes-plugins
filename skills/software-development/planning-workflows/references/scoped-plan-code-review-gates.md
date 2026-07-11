# Scoped plan-code review gates for ad-hoc diffs

Use this when the user asks for a `plan-code`-style simplify/review gate after a small implementation that was not started from an explicit `/plan-code` task directory, for example: "run simplify and review of plan-code skill flow".

## Classification

First distinguish the request from a full explicit `/plan-code` execution:

- Full `/plan-code`: user invokes `/plan-code`, names an existing `tasks/<slug>/`, or expects task docs/TODO/final-review artifacts under the repo.
- Scoped gate: current work is an ad-hoc diff, no task directory is in scope, and the user asks for the `plan-code` quality flow (simplify + review) rather than task-doc execution.

Do not fabricate task docs just to satisfy the full workflow when the session was not a task-doc plan-code run. Say clearly that you are running the scoped simplify/review gate, not a full task-directory plan-code completion.

## Procedure

1. Load `planning-workflows`, `simplify`, and `requesting-code-review`; load `claude-i` when the default review stack is requested or implied.
2. Identify the intended diff with `git status --short` and `git diff --name-only`; exclude unrelated dirty files.
3. Run the simplify gate on changed files. Apply only narrow, behavior-preserving simplifications. If no simplification is worth applying, explicitly record `KEEP`.
4. Run static scans on the intended diff's added lines.
5. Build a self-contained review bundle containing:
   - git status and changed file list
   - static scan results
   - verification commands/results already run
   - tracked diff for intended files
   - current snapshots of changed source/tests
   - adjacent reference component/source when the UI change is comparative
   - relevant tests/specs when UI text, test IDs, actionbars, or visible state changed
6. Validate the bundle for truncation markers before review.
7. Launch the pinned interactive Codex TUI against the immutable bundle using bare `codex` in managed tmux, GPT-5.6 SOL @ xhigh, and the read-only/artifact contract in `codex-cli-review-lane.md`. Save the CLI version, session name, model/effort banner, raw pane capture, bundle path/hash, and normalized fail-closed verdict. A started session or partial pane is not approval.
8. If available and not waived, launch Claude Code through `claude-i` against the same bundle in read-only mode **before waiting on or adjudicating the Codex lane**. Verify and record the model/effort banner before sending the prompt. Before launching, ensure there are no stale Claude/tmux review sessions for the same repo (`tmux ls` and kill/exit old sessions) so an earlier prompt cannot keep applying suggestions in the background. After both independent lanes have launched, monitor them separately. After the Claude review, immediately capture the verdict, exit/kill the session, and re-read `git status --short --branch` plus `git diff --name-status`; if any out-of-scope files changed, treat the Claude leg as side-effect contaminated, restore only those paths, regenerate the bundle from the cleaned tree, and rerun both stale review legs or explicitly document a user-approved waiver.
9. Save artifacts. For scoped gates, `/tmp/<task>-bundle.txt`, `/tmp/<task>-codex-tui-raw.txt`, `/tmp/<task>-codex-tui-review.json`, `/tmp/<task>-claude-review.md`, and `/tmp/<task>-aggregate.json` are acceptable when the user did not ask for committable task artifacts. For coupled multi-repo changes, prefer `/tmp/<task>-<repo>-bundle.txt` per repo plus a shared intent statement in every bundle/reviewer prompt.
10. If the scoped change spans multiple repositories, keep bundles, verification, staging, commits, pushes, and readbacks repo-local. Do not assume matching branch names; commit each repo on its current branch after its reviewed scope is staged explicitly. Use the multi-repo pattern in `requesting-code-review/references/multi-repo-contract-review-and-commit.md` for API-contract changes.
11. If review finds a real issue (including stale tests/selectors), fix it narrowly, run impacted verification, regenerate the bundle, and rerun both review legs on the final bundle. Do not count pre-fix approval or partial Claude output as final approval.
11. If any non-blocking suggestion is adopted, rerun impacted verification and both review legs because the approval is stale. Otherwise record suggestions without churn.
12. Finish with a compact audit that marks task docs/TODO as `no — scoped gate only`, not as failed workflow steps.

## Pitfalls

- Do not claim a full `/plan-code` task completed when no task docs existed or were updated.
- Do not add repo task artifacts for a small ad-hoc diff unless the user asked for a durable task directory.
- Do not let a passing interactive Codex TUI review substitute for the Claude leg when the default stack is requested and Claude is available.
- Do not leave stale interactive reviewer sessions alive while continuing cleanup/staging. A prior Claude Code session can act on an old queued prompt after you have regenerated a supposedly clean bundle; kill/exit stale sessions, restore out-of-scope changes, rerun verification, and rebuild the review bundle before committing.
- Do not implement optional reviewer suggestions after approval unless you are prepared to rerun all stale gates.
- When Claude review produces only non-blocking UI suggestions (for example label click-to-focus or duplicate id cleanup), record them and leave the approved diff untouched unless they are required for the user's requested behavior.
- If you run an artifact-consistency check, include every artifact referenced by final review/report docs in the consistency bundle (or explicitly mark it intentionally omitted); otherwise the consistency gate can fail even when source review passed.
