---
name: plan-commit
description: Use when the user asks to commit and push an implemented plan-code task; by default also remove the implemented task directory and any tracked out-of-scope issue files resolved by the task, then push cleanup on the current branch.
version: 1.0.2
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, plan-code, commit, push, task-cleanup]
    related_skills: [planning-workflows, github-operations, requesting-code-review]
---

# Plan Commit

## Overview

Use this skill for committing and pushing an implemented `tasks/<slug>/` plan-code task. The default completion mode is now:

1. **Implementation/artifact commit** — commit and push the implementation, completed task artifacts, and any exact tracked `tasks/out-of-scope-issues/...` files that the implementation resolved and therefore deleted.
2. **Cleanup commit** — after the implementation commit is safely pushed, remove the implemented task directory, commit that deletion, and push again.

Only preserve the completed task directory when the user explicitly asks to keep task artifacts in the repository. Only keep resolved out-of-scope issue files when the user explicitly says they should remain open/tracked despite the task resolving them.

The target branch is the **current checked-out branch**. Do not assume `main` or `master`; the user's active development branch is often `dev` or `develop`.

This is a git side-effect workflow. Be conservative: inspect scope, stage only intended files, verify staged contents, push, read back branch state, then perform task-directory cleanup only after the implementation commit is safely pushed.

## When to Use

Use when the user says things like:

- `commit and push` after an implemented plan-code task is ready — use the default two-step flow: implementation/artifact commit, then cleanup commit removing the implemented task directory.
- `plan-commit tasks/<slug>`
- "commit and push this task"
- "commit/push and clean up the implemented task directory"
- "finish the task with the two-commit cleanup flow"
- "commit but keep the task directory" — only in this explicit preservation case, skip the cleanup commit and report that artifacts remain tracked.

Do **not** use for:

- Plan-only work.
- Ordinary ad-hoc commit requests that are not tied to a completed plan-code task.
- Dirty worktrees where intended scope cannot be separated from unrelated local edits.
- Failed or incomplete plan-code tasks unless the user explicitly asks to commit a blocker artifact instead of a completed implementation.

## Required Inputs

- Task directory path: usually `tasks/<slug>/`.
- Current git repository and branch.
- Existing completed implementation and final task artifacts.

If the user gives only a task slug, resolve it as `tasks/<slug>/` in the active workspace.

## Core Contract

- Target branch = current branch from `git branch --show-current` / `git status --short --branch`.
- Do not switch to `main`/`master` unless the user explicitly asks.
- Do not commit or push unrelated dirty files.
- Do not use `git add -A` or `git add .` in a dirty repository with unrelated work.
- First commit includes the implemented code/tests, the completed task directory artifacts, and exact tracked out-of-scope issue file deletions that this implementation resolves.
- If the user only asked to "commit and push" for a completed plan-code task, still run the default cleanup commit after the implementation commit is pushed.
- Skip the task-directory cleanup commit only when the user explicitly asks to preserve/keep the task artifacts.
- Second cleanup commit removes only the implemented task directory.
- If the task directory is currently untracked but is part of the intended completed task artifact, include it in the first commit so the second cleanup commit has a real tracked deletion.
- If the task directory is not tracked after the first push, local removal is possible but there may be no deletion commit; report that honestly.
- When commit-readiness requires multiple independent reviewer lanes against the same immutable bundle, launch every required independent review lane before waiting for, polling, monitoring, adjudicating, or fixing findings from any one lane. Do not serialize Codex and Claude Code merely because their tmux panes are monitored separately.

## Step 0 — Load Related Guidance

For explicit plan-code tasks, follow `planning-workflows` and especially its commit-readiness rules. For GitHub push/auth behavior, follow `github-operations`. If mandatory reviews or final consistency artifacts are missing, run or repair them before committing rather than committing stale artifacts.

## Step 1 — Discover Branch, Upstream, and Scope

Run:

```bash
git status --short --branch
git branch --show-current
git remote -v
git status --short tasks
git ls-files --others --exclude-standard tasks
```

Then inspect intended task docs:

```bash
git ls-files -- tasks/<slug>
git status --short -- tasks/<slug>
```

Classify:

- in-scope implementation files;
- in-scope task artifacts under `tasks/<slug>/`;
- exact tracked out-of-scope issue files under `tasks/out-of-scope-issues/...` that this task resolves and should delete in the implementation commit;
- unrelated dirty tracked files;
- unrelated untracked task directories.

If in-scope and unrelated edits overlap the same file and cannot be separated safely, stop and report the blocker.

### Planning guard — out-of-scope issue tracking

When commit-readiness exposes warnings, issues, code smells, bugs, skipped items, follow-ups, or potential problems outside the current task scope, do **not** silently ignore them and do **not** fix them inline unless the user explicitly asks.

Log each non-exempt finding as a separate Markdown file under:

```text
tasks/out-of-scope-issues/<priority>/<YYYYMMDD>_<short-kebab>.md
```

If the issue requires human investigation or intervention, use:

```text
tasks/out-of-scope-issues/<priority>/manual/<YYYYMMDD>_<short-kebab>.md
```

Priority must be one of: `critical`, `high`, `medium`, `low`, `proposal`, `other`.

Each file must contain these sections in order:

```markdown
**Issue**
**Location**
**Severity**
**Context**
**Suggested Fix**
```

Before creating a new file, check for an existing matching issue and update it instead of duplicating it. Mention logged out-of-scope issues in the final wrap-up.

Exception: do not create or update out-of-scope issue files solely for GitHub Dependabot alerts/security advisory counts. Dependabot alerts are already tracked in GitHub; mention them briefly in the wrap-up only when relevant, or work from GitHub/`gh`/`npm audit` when the user explicitly asks to triage or fix them.

## Step 2 — Reconcile Task Completion Before Staging

For multi-repo tasks where the task directory lives in one repo but implementation/test changes land in another, use `references/multi-repo-task-artifact-commit-readback.md`: commit/push the secondary repo's exact path scope first when appropriate, record that commit SHA/branch in the owning task artifacts, and include commit readback in pre-commit consistency bundles so a clean secondary repo status is not mistaken for a missing change. For the concrete backend-first/frontend-task-artifact pattern, especially when final docs must be patched after the secondary repo commit and generated bundles need whitespace normalization plus a post-normalization consistency rerun, use `references/multi-repo-backend-first-task-artifacts-2026-06.md`.

If the implementation source is already present in `HEAD` but the task directory artifacts are missing, untracked, or were removed by a prior cleanup, use `references/committed-implementation-recreated-task-artifacts.md`: rebuild the task artifacts from current source snapshots and durable evidence, recover async review verdicts from logs before marking gates pending, normalize generated bundles/logs, commit the reconstructed artifacts, then perform the normal task-directory deletion commit.

Before committing, verify the task is actually complete:

- `todo.md` has no unchecked real work items, ignoring status legend examples.
- Final report exists if required by the plan.
- Review artifacts named by the TODO/final report exist.
- Verification commands and results are documented.
- Any post-review artifact edits have a final artifact-consistency review or equivalent explanation.
- For documentation-only or boundary-audit tasks with many new untracked artifacts, do not rely on `git diff --stat` alone: untracked reports/reviews/issue files will be absent until staged. Use `git status --short -- <task> <issue-path>` and `git ls-files --others --exclude-standard <task>` to prove the artifact set before claiming scope.
- If a generated final review bundle is refreshed after review bookkeeping, normalize it immediately before staging and run `git diff --check -- <scoped paths>` plus `git diff --cached --check` after staging; embedded diff blocks frequently carry whitespace-only lines that only surface at commit time.

Useful checks:

```bash
grep -n '^- \[ \]' tasks/<slug>/todo.md || true
git diff --check -- <intended paths> tasks/<slug>
```

If task docs are stale, update them first and rerun required artifact consistency / review gates before committing rather than committing stale artifacts. In particular, final reports are often written before late consistency/pre-commit verdict artifacts exist; reconcile the final report's artifact list/review-artifact section to name the actual final canonical consistency verdicts before staging. Also check for stale pre-commit wording such as “No commit or push was performed”: if the user has now invoked `plan-commit`, rewrite that claim to scope it to pre-commit plan-code finalization and state that commit/push metadata belongs in the plan-commit final response. If a completed task resolves a tracked out-of-scope issue file, inspect the issue content to confirm it is the exact source issue, delete that issue file by default, include the deletion in the implementation commit (not the cleanup commit), and update the final report/artifact-consistency scope to name that resolved issue deletion before staging. Delete only exact linked/matching issue files; never sweep broad priority folders. Remove or supersede stale active pending-review markers only after the passing verdict exists, patch `spec.md`/`todo.md`/`final-report.md`/aggregate review JSON so they no longer claim the issues are merely preserved or mapped, then run a self-excluded artifact-consistency check over the final task docs before staging. Remove stale active `*pending*.json` markers only after the passed verdict artifacts exist, and mark superseded intermediate deltas as historical when later deltas replaced them. Rerun artifact consistency after this wording/artifact-list reconciliation before staging. See `references/plan-commit-precommit-artifact-reconciliation.md` for the compact checklist and `references/profile-feed-commit-readiness-2026-06.md` for a concrete recovery example covering stale final-review rows, recovered delegate verdicts, generated Markdown whitespace, and unrelated untracke... [truncated]

If a required **Codex interactive TUI** review is marked pending/blocked, recover the managed tmux session before declaring the task not commit-ready: confirm it exists, capture a wide pane window, and compare its explicit verdict/bundle identity with the saved raw-pane and normalized-verdict artifacts. A tmux session name, startup banner, or partial pane is not approval. If no parseable final verdict can be recovered, save a pending/blocker artifact naming the session, raw pane, and bundle path; then rerun the same pinned interactive Codex flow against the current bundle when permitted. Never substitute a Hermes `delegate_task` reviewer, `codex exec`, `codex review`, or `npx @openai/codex` command. A project-sanctioned Hermes-native one-shot reviewer may be used only when the workflow explicitly permits an independent lane; it does not convert the missing interactive Codex verdict into approval. See `planning-workflows/references/codex-cli-review-lane.md`.

When reconciling checkboxes, also reconcile the explanatory child bullets and final status sections. A checked parent row with a stale nested note like "review not run", "review pending", old pass counts, old delegation IDs, or obsolete deviation text is still stale commit content. Do not mark a review gate complete until the actual final review artifact has returned and been saved; a dispatched/background review is not a passed review. For the concrete post-feedback correction pattern — prior approval staled by user/manual verification, non-blocking doc cleanup, generated bundle whitespace normalization, and final post-normalization staged consistency — see `references/post-feedback-correction-commit-readiness.md`.

### Commit-readiness can expose real implementation gaps

Do not treat unchecked TODOs as a paperwork problem by default. First compare each unchecked item against the current implementation and tests:

- If the code really implements it, reconcile the checkbox and document the evidence.
- If the item is intentionally out of scope or a truthful deviation, mark it explicitly as `[!]` with the reason and coverage substitute.
- If the item describes a required behavior that is still missing, **stop the commit flow**, implement the missing behavior/tests, rerun the affected verification, regenerate the review bundle/static scan, and rerun the required final review before staging.

This matters especially for data-integrity requirements that reviews may miss until commit prep (for example reconciliation sourcing from ledger rows instead of cumulative state rows). A passing prior review does not override an unchecked required TODO that current source contradicts.

### Post-review verification changes require delta review

If commit-readiness reruns force any source/test/doc change after the saved final review — even a "test-only" E2E narrowing or documentation reconciliation — do not rely silently on the older review bundle. If the change adopts a non-blocking reviewer suggestion in task docs/review artifacts, follow `references/plan-commit-post-review-doc-suggestion-loop.md`: save the finding, patch the contradiction narrowly, regenerate the bundle, run a final consistency review, and avoid adopting purely cosmetic suggestions that would create another stale-review loop.

Before staging:

- update the task docs and aggregate review JSON/report so they describe the exact final verification state;
- regenerate the final implementation bundle, or create a small `reviews/post-review-delta-bundle.md` containing the final delta and current verification results;
- get a bounded read-only delta review (Claude/delegate) over that bundle when the project requires review artifacts;
- save the raw delta review artifact and mention it in the aggregate final review JSON before staging.

This prevents committing task artifacts that claim an older broader smoke/review state than the exact diff being pushed.

### Pre-commit task artifact consistency review

For completed `plan-code` task directories that are being committed as artifacts, run a small read-only artifact-consistency check after final TODO/final-report reconciliation and before staging when any task docs or review artifacts changed during commit readiness. The bundle should include the live `todo.md`, `final-report.md`, final review JSONs, aggregate review JSON, and a note that the future consistency verdict file is excluded from scope. Put `todo.md` and `final-report.md` into their intended final state before this review, even if they name the future self-excluded verdict. If the reviewer notes that the self-excluded verdict is checked before it exists, save the verdict immediately afterward and record that as the self-exclusion disposition rather than toggling the row again and creating another stale-doc loop. If the reviewer flags referenced raw artifacts that were omitted from the compact bundle, verify those files exist and record that disposition in the saved verdict. For generated bundle whitespace normalization and the final post-normalization consistency pattern, see `references/generated-artifact-normalization-and-postcheck.md`.

If the implementation source/test changes are already present in `HEAD` and only recreated task artifacts or issue files are dirty, do not build the review/commit evidence from `git diff` alone. Include current source snapshots and recent commit readback in the bundle, record the implementation commit SHA in the aggregate artifact, and exclude volatile delegate-id files such as `reviews/final-review.json` from the reviewed bundle when they would create a self-referential stale loop. See `references/head-committed-implementation-with-recreated-task-artifacts.md`.

If the consistency check fails on stale task-doc claims (for example a TODO still names an older `final-implementation-review-bundle.md` whose embedded verification counts predate later reviewer-driven fixes), patch the task docs to identify the actual final bundle and mark earlier bundles historical/superseded, save the failed consistency verdict as historical evidence, regenerate the consistency bundle, and rerun. Do not stage a task directory whose docs point at superseded verification/review artifacts as if they were final.

When generated review bundles are normalized during commit prep to satisfy `git diff --cached --check`, run one final **post-normalization** read-only consistency check over the staged task artifacts before committing. Save and stage that verdict as a commit-prep artifact. It does not need to trigger another full implementation review if the only change was whitespace normalization in generated task artifacts, but the final response should name the post-normalization check and its result. If the task `final-report.md` is intended to list every committed review artifact, update it before this final consistency check; otherwise clearly treat the post-normalization verdict as a commit-prep artifact rather than part of the implementation review gate.

When a completed task also deletes covered `tasks/out-of-scope-issues/...` files and a previously pending interactive Codex TUI review returns during commit readiness, save the late verdict only if it covers the current canonical bundle, remove/supersede pending markers, annotate unrelated already-absent issue rows without claiming they were completed by this task, normalize generated review bundles, and rerun a self-excluded artifact-consistency check before staging. Recover the tmux pane and saved raw/normalized artifacts rather than a background-process transcript. For a concrete small frontend example that combines recovered review verdicts, generated-bundle whitespace normalization, self-excluded post-normalization consistency, exact staging amid unrelated untracked task dirs, and `gh auth setup-git` push recovery, see `references/debug-console-hardening-commit-2026-07.md`.

When the user asks to remove every issue listed in a tracked coverage map and then delete/commit/push that map, use `references/coverage-map-issue-cleanup-commit.md`: parse the map, remove only listed issue files that still exist plus the map itself, verify all listed paths are absent, and stage/read back that exact deletion scope before committing.

For the combined pattern of asynchronous review recovery plus generated-artifact normalization, see `references/async-review-and-post-normalization-recovery-2026-06.md`. In particular: a dispatch id alone is not a pass; if the subagent session exists but has not persisted a final message, inspect logs for `Turn ended`, wait briefly if it is still working, then read/save the final JSON verdict before committing.

For sequential multi-task `plan-code` + `plan-commit` runs amid many untracked task dirs/source-issue deletions, use `references/sequential-plan-code-commit-with-pending-review.md`: commit one task at a time, stage only that task's source/artifacts/owned issue deletions, normalize generated bundles before the final post-normalization consistency verdict, and stop fail-closed on missing mandatory delegate reviews instead of advancing to the next task.

For batch sessions where several completed plan-code task directories are intentionally committed together, use `references/multi-task-plan-code-commit-with-artifact-consistency.md`: reconcile stale pending markers and active reviewer suggestions, run a combined per-task consistency check, normalize generated artifacts, then run a final staged post-normalization consistency check before the implementation commit and cleanup commit.

For the combined plain `commit and push` wording, unrelated dirty work, staged-only generated artifact whitespace failures, and post-normalization consistency-verdict recovery, see `references/plain-commit-and-post-normalization-2026-06.md`.

For the follow-on case where a plain implementation commit/push already succeeded and the user later invokes `/plan-commit`, use `references/delayed-plan-commit-cleanup-after-plain-push.md`: verify the pushed implementation commit and clean worktree, then run only the task-directory cleanup commit/push with a dry-run and staged deletion readback.

For completed plan-code task directories that include final review artifacts plus generated bundles/logs, use `references/completed-plan-code-artifact-staging.md`: remove stale pending review markers after the final verdict is saved, force-add only referenced ignored verification logs, normalize generated bundle whitespace, and save a post-normalization consistency artifact before committing. For the exact generated-bundle whitespace + self-excluded verdict loop, use `references/generated-bundle-normalization-self-excluded-consistency.md`: normalize only generated artifacts, stage/read back, run a self-excluded consistency review, and record cosmetic nits instead of creating another post-review artifact loop. For large Buffdemy backend tasks whose whole task directory is still untracked, ignored verification logs are referenced, and a sanctioned out-of-scope issue was created during the task, use `references/buffdemy-backend-large-plan-code-artifact-commit-2026-07.md`: include the task directory and owned out-of-scope issue in the implementation commit first, active-scan only live docs (not historical review bundles), force-add intended ignored logs, normalize generated task artifacts only after staged whitespace failure, and run a self-excluded pre-commit consistency review before committing.

For small frontend/UI plan-code tasks with untracked task artifacts and generated Markdown review bundles, use `references/small-ui-plan-code-commit-with-generated-bundle-normalization.md`: commit source/tests plus task artifacts first, preserve stale async reviewer outputs as superseded when reviewer-driven test hardening happened after dispatch, normalize only generated bundle whitespace that fails staged checks, save a self-excluding post-normalization consistency artifact, then push the cleanup deletion commit.

## Step 3 — Stage the Implementation Commit Explicitly

Stage only intended implementation paths, the task directory, and exact resolved out-of-scope issue file deletions. Examples:

```bash
git add src/components/notification \
        src/models/base/notificationSummary \
        src/client/models/notificationSummary \
        src/i18n/translations/en/notification.json \
        src/i18n/translations/ja/notification.json \
        tasks/<slug>
```

Prefer exact paths from `git diff --name-only` and `git ls-files --others --exclude-standard` rather than broad pathspecs.

Verify staged scope:

```bash
git diff --cached --name-status
git diff --cached --stat
git diff --cached --check
git status --short --branch
git status --short tasks
```

Stop if unrelated files are staged.

## Step 4 — Commit and Push Implementation

Before committing, check upstream divergence and recent log. If the branch is already ahead before the task commit (for example `git rev-list --left-right --count @{u}...HEAD` reports `0 1`), do not reset or rewrite it; record the existing ahead commit(s) and tell the user that the implementation push will also publish those already-local commits. If that is not acceptable, stop before pushing and ask for direction.

Commit on the current branch:

```bash
git commit -m "implement <task summary>"
git push
```

If no upstream exists, set it for the current branch, not `main`/`master`:

```bash
branch=$(git branch --show-current)
git push -u origin "$branch"
```

Verify readback:

```bash
git status --short --branch
git log --oneline --decorate -3
```

If push fails due to auth/network, report the local commit SHA, ahead state, and exact push command; do not proceed to task-directory deletion until the implementation commit is pushed or the user explicitly waives that order.

## Step 5 — Remove the Implemented Task Directory

After the implementation commit is pushed, remove only the implemented task directory.

Before deletion, scan the task directory for handoff docs intended for a later session (for example `frontend-handoff.md`, `backend-contract.md`, or companion-repo instructions). If such a file exists, do not silently strand the user with a dead working-tree path: record the implementation commit SHA that contains it and mention the retrievable path in the final response (for example `git show <sha>:tasks/<slug>/frontend-handoff.md`). Only copy it to another live location if the user explicitly asks; the normal two-step cleanup still deletes the completed task directory.

Before cleanup, re-read the **entire** worktree, not just `tasks/<slug>`: `git status --short --branch`, `git diff --name-status`, and `git ls-files --others --exclude-standard`. If additional dirty/untracked in-scope source or test files appear after the implementation commit, stop cleanup and follow `references/post-implementation-commit-surfaced-delta.md`: restore any task-directory deletion state, classify the delta, ask the user if scope changed, rerun verification/reviews for any included follow-up, and commit/push that follow-up before deleting task artifacts.

When the user asks to "check whether this task is already complete; if so remove/commit/push," run a cleanup-only completion audit before deletion:

- read `todo.md`, `final-report.md`, `reviews/final-review.json`, and any final artifact-consistency verdict;
- confirm no unchecked real TODO rows remain and the final report/review artifacts say the task is complete;
- confirm the task artifacts were already included in a prior implementation commit with `git log --name-status -- tasks/<slug> <likely source paths>`;
- confirm the branch is synced with upstream before making the cleanup commit (`git rev-list --left-right --count @{u}...HEAD`);
- do not rerun expensive build/E2E gates solely for cleanup when current artifacts already record passing verification and no in-scope source/task files are dirty. Lightweight checks such as `git diff --check -- tasks/<slug>` and staged `git diff --cached --check` are still required.

First dry-run:

```bash
git rm -r --dry-run -- tasks/<slug>
```

The dry-run must list only `tasks/<slug>/...` paths. If it lists nothing, check tracking:

```bash
git ls-files -- tasks/<slug>
git status --short --ignored -- tasks/<slug>
```

If the directory is untracked/ignored only, remove it locally with `rm -rf tasks/<slug>` and report that there is no tracked deletion to commit. Otherwise apply:

```bash
git rm -r -- tasks/<slug>
```

Verify staged deletion:

```bash
git diff --cached --name-status
git diff --cached --stat
git diff --cached --check
git status --short --branch
```

Stop if any path outside `tasks/<slug>/` is staged for deletion or modification.

## Step 6 — Commit and Push Cleanup

Commit the task directory removal:

```bash
git commit -m "remove completed <slug> task artifacts"
git push
```

Verify readback:

```bash
git status --short --branch
git log --oneline --decorate -5
```

If push fails, report the local cleanup commit SHA, ahead state, and exact push command.

## Step 7 — Final Report

Report:

- Current branch and upstream target.
- Implementation commit SHA and push result.
- Cleanup commit SHA and push result, or why no cleanup commit existed.
- Task directory tracked/untracked status before cleanup.
- Exact resolved out-of-scope issue files deleted in the implementation commit, if any.
- Newly logged out-of-scope issue files, if any.
- Verification commands or commit-readiness checks run.
- When cleanup deletes committed task artifacts/review reports, include a concrete retrieval command for the implementation commit (for example `git show <implementation_sha>:tasks/<slug>/final-report.md`) so the user can inspect the now-removed artifacts later.
- Any unrelated dirty tracked files left untouched.
- Any unrelated untracked task directories left untouched.

## Common Pitfalls

0. **Commit-readiness may start with a pending final consistency delegate.** Before staging, recover/save any pending artifact-consistency delegate verdict from logs/session history; a dispatch id is not enough. If generated task artifacts then need whitespace normalization for `git diff --cached --check`, treat that as a post-verdict artifact edit: make a self-excluded precommit/post-normalization consistency bundle, recover/save its passing verdict, stage that verdict, then commit. After the cleanup push, a broad dirty worktree can remain; verify success with upstream divergence (`0 0`), empty cached diff, task-dir absence, and HEAD/upstream readback rather than requiring unrelated work to be clean.
0. **Cross-repo status/readback mismatch.** In multi-repo tasks, a secondary repo change may already be committed and pushed before the task-artifact repo is committed. Pre-commit consistency bundles must include the secondary repo commit SHA/path readback, not just current dirty status, or reviewers may falsely flag the docs as overclaiming.
1. **Assuming `main` or `master`.** The target is the current branch. The user often works on `dev` or `develop`.
2. **Deleting an untracked task directory before the implementation commit.** If the task directory is intended artifact content, first commit it with the implementation so the second `git rm -r --dry-run` / `git rm -r` cleanup commit has a real tracked deletion. Do not apply this to unrelated task directories.
3. **Cleanup deletion can include older tracked plan-doc artifacts.** In a two-step cleanup flow, the artifact commit may add only newly generated final reports/reviews while older `spec.md`, `todo.md`, plan-review artifacts, or initial review files were already tracked from earlier commits. The cleanup dry-run may therefore list more paths than the just-created artifact commit. That is acceptable when every path is under the exact completed `tasks/<slug>/` directory; verify with `git ls-files -- tasks/<slug>` and `git rm -r --dry-run -- tasks/<slug>`, not by comparing only to the previous commit's added files.
4. **Using broad staging commands.** `git add -A` can absorb unrelated task directories or another agent's dirty work.
4. **Skipping staged readback.** Always inspect `git diff --cached --name-status` and `git status --short` before each commit.
5. **Pushing cleanup before implementation push succeeded.** Preserve the user's requested order unless explicitly waived.
6. **Creating a fake deletion commit.** If `git rm --dry-run` finds no tracked paths, there may be no cleanup commit to make. Say so.
7. **Treating stale task docs as harmless.** Task docs and review artifacts are commit content; reconcile stale checkboxes and rerun required consistency gates before committing them.
8. **Generated artifact whitespace.** Saved Markdown bundles and raw command logs (for example full Playwright `.log` artifacts) often embed trailing whitespace or even `space before tab` sequences. If `git diff --cached --check` fails only inside intended generated task artifacts, normalize line-end whitespace and trailing empty lines for those intended artifacts, restage, and rerun the staged check. Do not bypass the check or normalize unrelated files. For source files that already use CRLF, do **not** normalize whole files to LF just to satisfy the default whitespace checker; that creates noisy all-file diffs. Prefer a scoped check that treats CR at EOL as acceptable, for example `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --cached --check`, then verify the staged stat remains minimal.
9. **Post-review normalization stales artifact claims unless checked.** When commit prep normalizes generated logs/review bundles after the final review, run a narrow read-only pre-commit artifact-consistency review over the staged state before committing. The prompt should explicitly exclude the future saved verdict file from its own reviewed scope. Save that verdict under the task `reviews/`, stage it, rerun `git diff --cached --check`, then commit. If the saved pre-commit verdict itself is followed by additional generated-artifact normalization, run one final post-normalization consistency check and stage that verdict too before committing.
10. **Ignoring unrelated dirty files.** Leave them unstaged and name them in the final report.
11. **Changing staged artifact membership after consistency approval.** If commit prep removes a superseded/historical bundle or otherwise changes which task artifacts will be committed after a consistency review passed, treat the approval as stale for the staged set. Rerun a final read-only artifact-consistency check against the exact staged artifact set, overwrite/restage the consistency verdict, and rerun `git diff --cached --check` before committing.
12. **Late async review completions after newer reviews/commits.** Background review delegates can re-enter the chat after the task has already advanced through later review bundles, implementation fixes, commits, and cleanup. Do not reopen a completed task from the late message alone. First compare the delegation's reviewed bundle/version/path and blocker text against the final committed implementation/review artifacts: `git status --short --branch`, `git log --oneline --decorate -5`, and `git show --name-only <implementation_sha> -- tasks/<slug>/reviews`. If the late review targets an older bundle (for example v1-v4) and a later canonical bundle/review (for example v5) explicitly fixed and passed the same issue, classify it as stale/superseded and report no action. If it targets the current canonical bundle or raises a genuinely new blocker not covered by the final artifacts, stop and perform a normal follow-up fix/review/commit rather than dismissing it.
13. **Follow-up refactors can hide behind mocked tests.** When a surfaced delta extracts a shared component or changes a prop gate, add a real-render boundary regression in addition to prop-wiring tests. Reviews can catch cases where `showControls=false` hides one child but leaves a sibling actionbar/control surface active; the fix needs source gating plus a test that proves the visible contract.
14. **Using the old preservation default.** For completed plan-code tasks, `commit and push` now means implementation/artifact commit plus cleanup commit by default. Preserve the task directory only when the user explicitly asks to keep it. Resolved out-of-scope issue files should be deleted by default only after confirming exact ownership/match; unrelated findings must be logged separately under `tasks/out-of-scope-issues/...` instead of fixed inline.

## Verification Checklist

- [ ] Current branch and upstream verified; no assumption of `main`/`master`.
- [ ] Task directory completion reconciled before first commit.
- [ ] First staged diff contains only intended implementation paths, task artifacts, and exact resolved out-of-scope issue deletions.
- [ ] `git diff --cached --check` passed before first commit.
- [ ] First commit pushed and read back.
- [ ] `git rm -r --dry-run -- tasks/<slug>` listed only the implemented task directory before cleanup.
- [ ] Cleanup staged diff contains only task-directory deletion.
- [ ] `git diff --cached --check` passed before cleanup commit.
- [ ] Cleanup commit pushed and read back, or no-op cleanup truthfully reported.
- [ ] Unrelated dirty/untracked files and task dirs reported.
