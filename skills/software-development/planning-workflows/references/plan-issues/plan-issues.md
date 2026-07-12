---
name: plan-issues
id: planning-workflows-plan-issues
summary: Convert logged issues into dependency-ordered task plans with one bounded task-local review at a time.
tags: [planning, issues, review-gates, task-ordering]
---

# plan-issues workflow

## Purpose and authority

Convert eligible out-of-scope issue logs into actionable `plan-doc` task sets. This is planning-only work: do not implement source fixes during conversion.

This file is the canonical `plan-issues` contract. The public `plan-issues/SKILL.md` is only a wrapper. Also load the canonical `plan-doc` and reviewer-lane references before creating/reviewing task documents.

## Non-negotiable model

A multi-issue conversion may map or draft all task documents up front, but it reviews **one task document set at a time**:

1. select the current task from the conversion status ledger;
2. build one bounded immutable bundle for exactly one target slug;
3. launch Codex and Claude against that same digest before waiting on either lane;
4. save both complete results, aggregate, and close or reround that task;
5. only then move to the next task.

Do not generate or dispatch the next task while the current task remains unreviewed, reviewing, changes-required, or blocked without explicit user authorization. Never combine task reviews unless the user explicitly requests a combined bundle and records the deviation.

The shipped helper enforces the mechanical parts:

```text
skills/software-development/planning-workflows/scripts/plan_issues_workflow.py
```

## Source issue layouts and guard policy

Supported inputs:

- `tasks/out-of-scope-issues/<priority>/<YYYYMMDD>_<short-kebab>.md`
- `tasks/out-of-scope-issues/<priority>/manual/<YYYYMMDD>_<short-kebab>.md`
- legacy flat `tasks/out-of-scope-issues/<short-kebab>.md`
- legacy `tasks/out-of-scope-issues.md`

Valid priorities are `critical`, `high`, `medium`, `low`, `proposal`, and `other`. A manual-tier issue requires human investigation/intervention: surface it, but do not auto-plan or remove it.

During conversion, warnings, bugs, smells, skipped items, follow-ups, or potential problems outside the current task must be deduplicated and then logged individually under `tasks/out-of-scope-issues/<priority>/[manual/]`. Every issue file contains these sections in order: **Issue**, **Location**, **Severity**, **Context**, **Suggested Fix**. Do not log or update an issue solely for GitHub Dependabot alerts or security-advisory counts; those remain in GitHub unless the user explicitly asks to triage/fix them.

## Procedure

### 1. Discover and normalize

1. Resolve the project root and inspect `git status --short`; preserve unrelated dirty work.
2. Discover all matching issue files with exact file paths, including `manual/` entries.
3. Apply requested priority filters exactly. Warn on invalid filters or unrecognized subdirectories.
4. For flat layouts, derive priority from the issue's severity; default invalid/missing values to `other` with a warning.
5. Deduplicate a partial migration by normalized kebab: prefer the priority-bucketed path and leave the legacy duplicate untouched.
6. Exclude Dependabot-only tracking files/sections.
7. Normalize each issue to source path/section, priority, issue, location, severity, context, and suggested fix.
8. Compare existing task `spec.md`/`todo.md` files and skip already-covered issues. Keep skipped sources and report them.

Stop if no eligible issue remains.

### 2. Group and decide

Group only issues that share ownership, theme, surface, and implementation boundary. Keep medium-or-higher, architectural, multi-subsystem, or otherwise non-trivial issues separate by default.

Resolve product, ownership, migration/compatibility, and genuinely manual decisions before task creation. Batch related questions where the interface supports it, but do not hide unresolved decisions. Record answers per task group.

### 3. Build and validate the dependency graph

Use a stable kebab-case `name` for each group and list direct prerequisite names explicitly. The task path is always `tasks/<task-name>/`. Derive each numeric `implementation_order` as one plus the greatest prerequisite order; roots use `1`. This longest-path rule guarantees every dependent task is later than every direct and transitive prerequisite. Tasks share a metadata wave only when no dependency path connects them and their contracts, migrations, artifacts, or rollout state permit safe parallel implementation. Because order is metadata, graph correction requires no directory renaming.

Example definitions file:

```json
[
  {
    "name": "api-contract",
    "source_issues": ["tasks/out-of-scope-issues/high/20260712_api-contract.md"],
    "prerequisites": []
  },
  {
    "name": "copy-cleanup",
    "source_issues": ["tasks/out-of-scope-issues/low/20260712_copy-cleanup.md"],
    "prerequisites": []
  },
  {
    "name": "client-integration",
    "source_issues": ["tasks/out-of-scope-issues/medium/20260712_client.md"],
    "prerequisites": ["api-contract"]
  }
]
```

Before creating any task directory, run initialization from the project root (replace `<skill-dir>` with the loaded `planning-workflows` directory):

```bash
python3 <skill-dir>/scripts/plan_issues_workflow.py init \
  --tasks-root tasks \
  --definitions /absolute/path/to/definitions.json \
  --max-rounds 4
```

Initialization fails before directory creation on invalid kebab names, duplicates, unknown prerequisites, a dependency cycle, or target collisions. Successful output creates:

- `tasks/<task-name>/task-metadata.json` per task;
- `tasks/<task-name>/handoff.md` per task;
- `tasks/plan-issues-status.json` as machine state;
- `tasks/plan-issues-status.md` as the compact status ledger.

The ledger has one row per task: source issues, prerequisites, parallel cohort, current task-local bundle/hash, Codex verdict, Claude verdict, blocker, exact next action, and aggregate state.

### 4. Create task docs through plan-doc

For every initialized directory, invoke the `plan-doc` workflow to create `spec.md` and `todo.md`. Include:

- source issue mapping and current evidence;
- goal, scope, and out-of-scope boundaries;
- implementation-order sequence, parallel cohort, and direct prerequisites;
- acceptance criteria and decisions/open gates;
- phases and exact verification commands;
- migration/backward-compatibility constraints;
- dependency contracts/gates;
- simplify/review requirements;
- kickoff and final-report expectations.

Creating all docs up front does not authorize generating all bundles. The status ledger still exposes exactly one current task.

### 5. Create a bounded explicit evidence manifest

Start from the current task's claims. Put every exact repository-relative source, test, config, task-doc, or compact dependency-contract path named by `spec.md` or `todo.md` in inline code, then enumerate every one in the manifest with a reason. The helper extracts path-shaped inline-code claims from both authoritative documents, fails when a named path does not exist, and fails when an existing named path was omitted from the manifest.

Example `tasks/api-contract/evidence-manifest.json`:

```json
{
  "evidence": [
    {"path": "spec.md", "reason": "authoritative behavior and acceptance criteria"},
    {"path": "todo.md", "reason": "implementation and verification sequence"},
    {"path": "../../src/api.py", "reason": "current endpoint contract named by the plan"},
    {"path": "../../tests/test_api.py", "reason": "focused regression surface named by the plan"}
  ]
}
```

The current task must contain real, non-symlinked `spec.md` and `todo.md`, and the manifest must include both. The pre-dispatch gate fails when a path is missing, named by the plan but omitted, duplicated, outside the project root, a directory, inside the current task's `reviews/` tree, or another task's full `spec.md`/`todo.md`. A source path elsewhere in the project is not excluded merely because an unrelated ancestor is named `reviews`. Recursive whole-directory inclusion is forbidden by default. The review target is plan correctness and executability, not reproduction of a full codebase audit.

Generate only the current task:

```bash
python3 <skill-dir>/scripts/plan_issues_workflow.py bundle \
  --tasks-root tasks \
  --slug api-contract \
  --manifest tasks/api-contract/evidence-manifest.json
```

There is no generate-all default. `--slug` is mandatory. Version discovery scans only the selected task's `reviews/`; another task cannot increment it. The bundle sidecar records path, SHA-256 digest, bytes, evidence count, reasoned manifest, and live-doc digest.

### 6. Dispatch and record both current-digest lanes

For the current task only, launch every required independent review lane before waiting:

- Codex interactive TUI GPT-5.6 SOL/xhigh in managed `tmux`, following `../codex-cli-review-lane.md`;
- interactive Claude Code Opus 4.8/xhigh via `claude-i`.

Both lanes must review the exact immutable digest and return structured hash-bound verdicts. Preserve each complete raw pane/session transcript under the current task's `reviews/raw/` tree. Arbitrary transcript text may surround the result, but there must be exactly one canonical block and no duplicate, conflicting, unknown, missing, or malformed fields:

```text
BEGIN_REVIEW_RESULT
BUNDLE_SHA256: <64-character lowercase SHA-256>
REVIEWER_MODE: <exact pinned mode>
MODEL: <exact pinned model>
EFFORT: xhigh
VERDICT: PASS | CHANGES_REQUIRED
END_REVIEW_RESULT
```

The recorded CLI verdict must exactly match that one block. Prompt echoes and mode/model strings elsewhere in the transcript never count as attestation. Never use `delegate_task`, `codex exec`, or `codex review` as the Codex lane or fallback.

Save each verdict:

```bash
python3 <skill-dir>/scripts/plan_issues_workflow.py record-review \
  --tasks-root tasks \
  --slug api-contract \
  --lane codex \
  --bundle-digest <sha256> \
  --verdict APPROVED \
  --reviewer-artifact tasks/api-contract/reviews/raw/v1-codex.txt \
  --reviewer-mode interactive-codex-tui \
  --model gpt-5.6-sol \
  --effort xhigh

python3 <skill-dir>/scripts/plan_issues_workflow.py record-review \
  --tasks-root tasks \
  --slug api-contract \
  --lane claude \
  --bundle-digest <sha256> \
  --verdict CHANGES_REQUIRED \
  --reviewer-artifact tasks/api-contract/reviews/raw/v1-claude.txt \
  --reviewer-mode interactive-claude-code \
  --model claude-opus-4-8 \
  --effort xhigh \
  --blocker "Missing rollback decision gate" \
  --non-blocking "Consider an implementation-time edge test"
```

The helper rejects an unpinned model/effort/mode, a raw artifact outside the task-local review tree, an artifact that does not attest the exact digest and verdict, or a raw artifact modified after verdict recording. It also rehashes the immutable bundle before recording or aggregating. Do not edit after the first lane returns when the companion result can still be collected. The helper refuses a replacement bundle while exactly one current-bundle lane is saved.

### 7. Aggregate once, amend once, and bound rerounds

Aggregate after both complete current-digest results exist:

```bash
python3 <skill-dir>/scripts/plan_issues_workflow.py aggregate \
  --tasks-root tasks \
  --slug api-contract
```

- Any blocker or `CHANGES_REQUIRED` verdict keeps the same task current.
- Consolidate all blocker findings into one amendment pass.
- Regenerate and rerun both lanes only after blocker-level or contradiction fixes. The reround bundle is current-only: include the latest authoritative evidence plus a concise changed/removed-evidence and consolidated finding-to-fix delta. Keep prior full bundles and prior raw review artifacts as historical paths/digests; do not embed them in the reround.
- Preserve optional/non-blocking suggestions in the aggregate and handoff; they do not invalidate a matching approval or force plan churn.
- The default cap is four total review rounds: the initial round plus at most three normal blocker-driven amendment/rerounds. Regeneration fails unless the authoritative docs actually changed after the consolidated blocker result.
- If the fourth round does not pass, stop at a user-visible checkpoint and ask the user to decide how to proceed. Do not autonomously start another review round without an explicit user decision; report the consolidated root causes and options.

When both lanes approve the matching digest and live authoritative docs still match, the helper writes `reviews/final-review.json`, closes that task, and advances the ledger. A historical `final-review.json` never proves current approval by existence alone. Before trusting a saved ledger in a later session, run `python3 <skill-dir>/scripts/plan_issues_workflow.py status --tasks-root tasks`; it revalidates the complete bundle → two strict raw attestations/results → aggregate → `final-review.json` → live-doc chain and marks any missing, changed, mismatched, or unsafe approval stale. This mechanical chain gate means there is no separate artifact-consistency review and no third reviewer pass.

### 8. Handle delayed and superseded reviews

A delayed verdict whose digest is not current is written once under `reviews/superseded/`. It cannot update current lane state, aggregate state, or trigger a rerun by itself. Adjudicate only still-current blocker substance during the next deliberate amendment; never let a stale artifact advance or reopen a task mechanically.

### 9. Freeze dependency contracts instead of neighboring plans

A dependent task must not embed a prerequisite's mutable `spec.md` or `todo.md`. After a prerequisite is approved, freeze only required API/invariant excerpts plus its approved bundle and aggregate identity:

```bash
python3 <skill-dir>/scripts/plan_issues_workflow.py dependency-contract \
  --tasks-root tasks \
  --dependent client-integration \
  --prerequisite api-contract \
  --excerpts '{"endpoint":"GET /v1/items","invariant":"IDs are stable"}'
```

The dependent bundle manifest must explicitly include each required compact contract. Contract issuance requires a currently valid prerequisite approval. Consumption revalidates the frozen contract, its bound immutable bundle, both strict lane results, and the exact approved aggregate—but not later mutable prerequisite prose or cached prerequisite status. A later unrelated prose edit makes the prerequisite's own approval visibly stale without retroactively invalidating an already-issued downstream contract. Changing/corrupting the contract, its bound aggregate, raw evidence, approval identity, or frozen material fails closed; material changes require a new approval and contract. If a prerequisite is durably blocked and the user authorized moving on, the dependent bundle records an explicit blocker gate rather than treating that prerequisite as approved. Any other unapproved prerequisite without a valid frozen contract stops bundle generation.

### 10. Block, waive, or advance truthfully

A current task may advance only through approval, an explicit waiver, or durable blocking plus user authorization:

```bash
python3 <skill-dir>/scripts/plan_issues_workflow.py block \
  --tasks-root tasks --slug api-contract \
  --reason "Requires owner decision on public compatibility"

# Run only after the user explicitly authorizes moving on:
python3 <skill-dir>/scripts/plan_issues_workflow.py block \
  --tasks-root tasks --slug api-contract \
  --reason "Requires owner decision on public compatibility" \
  --authorize-next
```

Use `waive` only for an explicit current user waiver and preserve the reason as a deviation.

### 11. Correct ordering through explicit migration

If later dependency discovery changes ordering, update the definitions and run:

```bash
python3 <skill-dir>/scripts/plan_issues_workflow.py migrate-order \
  --tasks-root tasks \
  --definitions /absolute/path/to/corrected-definitions.json
```

The helper validates the corrected graph first, then transactionally updates task metadata, status, and handoffs. Stable `tasks/<task-name>/` paths are never renamed and task-path references are never rewritten during reordering. A write failure rolls generated metadata/handoffs/status back. Historical immutable review artifacts are not rewritten; any active or approved bundle/review identity affected by changed graph metadata is preserved as history, cleared from current state, and must receive a fresh task-local review.

`implementation_order` numbers represent implementation dependency waves only. Review retries, priority changes, or unrelated edits never change task paths.

For a pre-helper conversion with existing stable task directories, first review an explicit definitions mapping, then adopt it explicitly:

```bash
python3 <skill-dir>/scripts/plan_issues_workflow.py adopt-legacy \
  --tasks-root tasks \
  --definitions /absolute/path/to/definitions.json \
  --max-rounds 4
```

Adoption refuses missing, symlinked, or ambiguous legacy directories. It preserves existing `reviews/` trees as immutable history, records their exact paths in task state, creates metadata/handoffs/ledger state, and starts with one current task without treating legacy review artifacts as current approval. Stable names mean adoption performs no directory renaming.

### 12. Preserve source issues and report coverage

Do not remove source issue logs unless the user explicitly requested cleanup. If cleanup is authorized, remove only exact non-manual sources mapped to successfully created plan-doc tasks. Never remove filtered, skipped, already-covered, partial-migration, warning, manual-tier, or newly discovered issue files by glob. Update the coverage map before exact deletions and verify scoped status afterward.

Final reporting includes:

1. issue counts and priority filter;
2. skipped/already-covered/manual/Dependabot-only inputs;
3. groups and exact source mapping;
4. dependency graph, implementation waves, parallel cohorts, and cycle result;
5. decisions and manual gates;
6. status ledger and fresh-session handoff paths;
7. each task's current bundle path/hash/bytes/evidence count and both lane states;
8. blocker/next action/aggregate state per task;
9. source removals, or confirmation that none occurred;
10. out-of-scope issue files created or updated.

## Backward compatibility and existing reviews

- Existing task/review directories are preserved; the helper never treats old `final-review.json` existence as current approval.
- New bundle versions are discovered from the selected task's existing `reviews/` filenames, so legacy local `vN` history remains task-local and is not reset by another task.
- Existing untracked/unmanaged task directories are never silently adopted or renamed. Use `adopt-legacy` with a reviewed explicit definitions mapping; adoption preserves existing task-local review history without granting current approval.
- Ordering correction is explicit and metadata-only; stable task paths remain unchanged and historical immutable review artifacts remain historical rather than being rewritten to look current.
- Combined/global campaign artifacts may remain as history, but they cannot establish a current per-task approval. Rebuild one explicit task-local bundle before continuing.

## Common pitfalls

- Generating all bundles because all docs were mapped.
- Dispatching task B while task A is still reviewing or changes-required.
- Using one manually supplied version across unrelated tasks.
- Including whole directories or full neighboring plans.
- Discovering missing evidence one path at a time after dispatch instead of validating the full manifest first.
- Editing on the first reviewer response and discarding the companion lane's findings.
- Rerunning for optional polish or delayed stale artifacts.
- Silently renaming directories when the graph changes.
- Claiming approval from an unbound historical aggregate.
