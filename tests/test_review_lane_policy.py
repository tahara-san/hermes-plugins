import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALL_SKILLS = ROOT / "skills"
SKILLS = ROOT / "skills" / "software-development"
CLAUDE_I_DIR = ROOT / "skills" / "autonomous-ai-agents" / "claude-i"
CLAUDE_I = CLAUDE_I_DIR / "SKILL.md"

INTERACTIVE_CODEX_CONTRACT_FILES = [
    SKILLS / "plan-issues" / "SKILL.md",
    SKILLS / "plan-doc" / "SKILL.md",
    SKILLS / "plan-code" / "SKILL.md",
    SKILLS / "plan-commit" / "SKILL.md",
    SKILLS / "planning-workflows" / "SKILL.md",
    SKILLS / "planning-workflows" / "references" / "codex-cli-review-lane.md",
    SKILLS / "planning-workflows" / "references" / "plan-issues" / "plan-issues.md",
    SKILLS
    / "planning-workflows"
    / "references"
    / "plan-issues-priority-grouped-conversion.md",
    SKILLS / "planning-workflows" / "references" / "plan-doc" / "plan-doc.md",
    SKILLS / "planning-workflows" / "references" / "plan-code" / "plan-code.md",
]

PARALLEL_REVIEW_CONTRACT_FILES = [
    CLAUDE_I,
    SKILLS / "plan-issues" / "SKILL.md",
    SKILLS / "plan-doc" / "SKILL.md",
    SKILLS / "plan-code" / "SKILL.md",
    SKILLS / "plan-commit" / "SKILL.md",
    SKILLS / "planning-workflows" / "SKILL.md",
    SKILLS / "planning-workflows" / "references" / "codex-cli-review-lane.md",
    SKILLS / "planning-workflows" / "references" / "plan-issues" / "plan-issues.md",
    SKILLS
    / "planning-workflows"
    / "references"
    / "plan-issues-priority-grouped-conversion.md",
    SKILLS / "planning-workflows" / "references" / "plan-doc" / "plan-doc.md",
    SKILLS / "planning-workflows" / "references" / "plan-code" / "plan-code.md",
]

TWO_LANE_RECONCILIATION_FILES = [
    SKILLS / "planning-workflows" / "SKILL.md",
    SKILLS
    / "planning-workflows"
    / "references"
    / "review-finding-disposition-and-convergence.md",
    SKILLS / "planning-workflows" / "references" / "codex-cli-review-lane.md",
    SKILLS / "planning-workflows" / "references" / "plan-doc" / "plan-doc.md",
    SKILLS / "planning-workflows" / "references" / "plan-code" / "plan-code.md",
    SKILLS
    / "planning-workflows"
    / "references"
    / "plan-code"
    / "references"
    / "phase-review-loop-discipline.md",
    SKILLS / "plan-issues" / "SKILL.md",
    SKILLS / "planning-workflows" / "references" / "plan-issues" / "plan-issues.md",
    CLAUDE_I_DIR / "references" / "implementation-diff-review-plan-code.md",
    CLAUDE_I_DIR / "references" / "plan-doc-read-only-review.md",
]

MIGRATED_CODEX_RECOVERY_REFERENCES = [
    SKILLS
    / "planning-workflows"
    / "references"
    / "plan-code-pending-delegate-review-blocker.md",
    SKILLS
    / "planning-workflows"
    / "references"
    / "plan-code-approved-companion-review-with-pending-codex.md",
    SKILLS
    / "planning-workflows"
    / "references"
    / "plan-doc-pending-delegate-review-blocker.md",
    SKILLS
    / "planning-workflows"
    / "references"
    / "plan-doc-review-hardening-and-pending-codex.md",
    SKILLS / "planning-workflows" / "references" / "scoped-plan-code-review-gates.md",
]

NONINTERACTIVE_CODEX_COMMAND = re.compile(
    r"\s*(?:\$\s*)?(?:codex\s+(?:exec|review)\b|npx\s+@openai/codex\b)",
    re.IGNORECASE,
)

DEPRECATED_CODEX_LABELS = re.compile(
    r"codex-style|codex cli process|async codex|codex delegate",
    re.IGNORECASE,
)

# `--fallback-model` is documented by Claude Code as "only works with --print".
# The interactive `claude-i` lane forbids print mode, so the flag can never
# deliver the promised fallback and must not appear in published skills.
PRINT_ONLY_FALLBACK_FLAG = "--fallback-model"

AUTOMATIC_FALLBACK_CLAIM = re.compile(
    r"automatic[a-z]*[^.\n]{0,80}\bopus\b|\bopus\b[^.\n]{0,40}automatic",
    re.IGNORECASE,
)

FABLE_PRIMARY_COMMAND = "claude --model claude-fable-5-1 --effort xhigh"
OPUS_FALLBACK_COMMAND = "claude --model claude-opus-4-8 --effort xhigh"

PRINT_MODE_MENTION = re.compile(r"claude\s+-p\b|`?--print`?", re.IGNORECASE)

PRINT_MODE_COMMAND = re.compile(
    r"\s*(?:\$\s*)?claude\s+(?:[^\n]*\s)?(?:-p|--print)\b",
    re.IGNORECASE,
)

# The files that define the interactive Fable -> Opus review-model policy in full.
AUTHORITATIVE_CLAUDE_MODEL_POLICY_FILES = [
    CLAUDE_I,
    CLAUDE_I_DIR / "references" / "read-only-fable5-plan-mode-review.md",
    SKILLS / "planning-workflows" / "SKILL.md",
    SKILLS
    / "planning-workflows"
    / "references"
    / "plan-code-opus-review-limit-and-rerun.md",
]

# Every file that restates the policy and must stay consistent with it.
INTERACTIVE_CLAUDE_MODEL_POLICY_FILES = AUTHORITATIVE_CLAUDE_MODEL_POLICY_FILES + [
    SKILLS / "planning-workflows" / "references" / "plan-doc" / "plan-doc.md",
    SKILLS / "planning-workflows" / "references" / "plan-code" / "plan-code.md",
]


def _all_skill_markdown() -> list[Path]:
    return sorted(ALL_SKILLS.rglob("*.md"))


def _fenced_lines(path: Path) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    fenced = False
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            lines.append((line_number, line))
    return lines


def _all_planning_markdown() -> list[Path]:
    roots = [
        SKILLS / "plan-issues",
        SKILLS / "plan-doc",
        SKILLS / "plan-code",
        SKILLS / "plan-commit",
        SKILLS / "planning-workflows",
    ]
    return sorted(path for root in roots for path in root.rglob("*.md"))


def _fenced_noninteractive_codex_commands(path: Path) -> list[tuple[int, str]]:
    commands: list[tuple[int, str]] = []
    fenced = False
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced and NONINTERACTIVE_CODEX_COMMAND.match(line):
            commands.append((line_number, line.strip()))
    return commands


def test_core_review_contract_requires_interactive_codex():
    for path in INTERACTIVE_CODEX_CONTRACT_FILES:
        assert "Codex interactive" in path.read_text(), path


def test_codex_interactive_lane_forbids_timeout_prone_noninteractive_commands():
    content = (
        SKILLS / "planning-workflows" / "references" / "codex-cli-review-lane.md"
    ).read_text()

    assert "severe timeout issues" in content
    assert "Do **not** use `codex exec`" in content
    assert "`codex review`" in content
    assert "tmux new-session" in content
    assert "tmux capture-pane" in content
    assert "tmux paste-buffer" in content


def test_planning_workflows_never_show_noninteractive_codex_commands():
    violations = [
        f"{path.relative_to(ROOT)}:{line}: {command}"
        for path in _all_planning_markdown()
        for line, command in _fenced_noninteractive_codex_commands(path)
    ]

    assert not violations, "\n".join(violations)


def test_planning_markdown_has_no_embedded_line_number_prefixes():
    violations = [
        str(path.relative_to(ROOT))
        for path in _all_planning_markdown()
        if re.search(r"(?m)^\d+\|", path.read_text())
    ]

    assert not violations, "\n".join(violations)


def test_planning_references_do_not_use_deprecated_codex_lane_labels():
    umbrella = SKILLS / "planning-workflows" / "SKILL.md"
    violations = []
    for path in _all_planning_markdown():
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            if not DEPRECATED_CODEX_LABELS.search(line):
                continue
            if path == umbrella and "historical evidence only" in line.lower():
                continue
            violations.append(f"{path.relative_to(ROOT)}:{line_number}: {line.strip()}")

    assert not violations, "\n".join(violations)


def test_legacy_codex_chunk_alias_is_not_an_active_instruction():
    path = SKILLS / "planning-workflows" / "references" / "plan-doc" / "plan-doc.md"
    assert "/codex-chunk" not in path.read_text()


def test_claude_code_cli_lane_remains_explicitly_supported():
    content = (SKILLS / "planning-workflows" / "SKILL.md").read_text()
    assert "Claude Code CLI" in content
    assert "claude-i" in content
    assert "intentionally uses" in content


def test_required_multi_lane_reviews_launch_before_waiting():
    contract = "launch every required independent review lane before waiting"
    for path in PARALLEL_REVIEW_CONTRACT_FILES:
        assert contract in path.read_text().lower(), path


def test_mixed_two_lane_verdicts_use_symmetric_reviewer_cross_assessment():
    for path in TWO_LANE_RECONCILIATION_FILES:
        content = path.read_text().lower()
        assert "meta-review" in content, path
        assert "cross-assessments" in content, path
        assert "before waiting" in content, path
        assert "passing lane" in content, path
        assert "failing lane" in content, path
        assert "`uphold`" in content, path
        assert "`object`" in content, path
        assert "passing-lane `object`" in content, path
        assert "failing-lane `uphold`" in content, path
        assert "next dual-lane round" in content, path


def test_two_lane_policy_has_no_sequential_reconsideration_contract():
    retired = (
        "failing-lane reconsideration",
        "failing_lane_reconsideration",
        "meta_reconsideration_pending",
        "passing-lane `object` then failing-lane `object`",
        "passing-lane `object` → failing-lane `object`",
    )
    violations = [
        f"{path.relative_to(ROOT)}: {phrase}"
        for path in TWO_LANE_RECONCILIATION_FILES
        for phrase in retired
        if phrase in path.read_text().lower()
    ]
    assert not violations, "\n".join(violations)


def test_two_lane_review_limit_is_six_rounds_excluding_meta_reviews():
    for path in TWO_LANE_RECONCILIATION_FILES:
        content = path.read_text().lower()
        assert "six dual-lane review rounds" in content, path
        assert "meta-reviews do not count" in content, path
        assert "ask the user to decide" in content, path


def test_two_lane_policy_has_no_legacy_remediation_round_accounting():
    forbidden = (
        "third bundle-mutating remediation round",
        "running bundle-mutating remediation count",
        "at most three bundle-mutating remediation rounds",
    )
    violations = [
        f"{path.relative_to(ROOT)}: {phrase}"
        for path in _all_planning_markdown()
        for phrase in forbidden
        if phrase in path.read_text().lower()
    ]
    assert not violations, "\n".join(violations)


def test_planning_workflow_policy_is_not_literal_truncated_output():
    path = SKILLS / "planning-workflows" / "SKILL.md"
    assert "[truncated]" not in path.read_text().lower()


def test_plan_issues_requires_stable_task_directory_names_and_graph_metadata():
    paths = [
        SKILLS / "plan-issues" / "SKILL.md",
        SKILLS / "planning-workflows" / "SKILL.md",
        SKILLS / "planning-workflows" / "references" / "plan-issues" / "plan-issues.md",
        SKILLS
        / "planning-workflows"
        / "references"
        / "plan-issues-priority-grouped-conversion.md",
    ]
    for path in paths:
        content = path.read_text().lower()
        assert "tasks/<task-name>/" in content, path
        assert "stable" in content, path
        assert "directory renaming" in content, path
        assert "dependency graph" in content, path
        assert "cycle" in content, path
        assert "parallel" in content and "share" in content, path


def test_plan_issues_reviews_one_current_task_with_parallel_lanes():
    paths = [
        SKILLS / "plan-issues" / "SKILL.md",
        SKILLS / "planning-workflows" / "SKILL.md",
        SKILLS / "planning-workflows" / "references" / "plan-issues" / "plan-issues.md",
        SKILLS
        / "planning-workflows"
        / "references"
        / "plan-issues-priority-grouped-conversion.md",
    ]
    forbidden_global_campaigns = (
        "before waiting on any generated-task review lane",
        "launch all generated-task reviewers",
        "generate all by default",
    )
    for path in paths:
        content = path.read_text().lower()
        assert "current task" in content, path
        assert "do not generate or dispatch the next task" in content, path
        assert (
            "launch every required independent review lane before waiting" in content
        ), path
        assert not any(phrase in content for phrase in forbidden_global_campaigns), path


def test_nested_out_of_scope_planning_reference_matches_plan_issues_contract():
    path = (
        SKILLS
        / "planning-workflows"
        / "references"
        / "writing-plans"
        / "references"
        / "out-of-scope-issue-planning.md"
    )
    content = path.read_text().lower()
    assert "tasks/<task-name>/" in content
    assert "stable" in content
    assert "does not delete" in content
    assert "managed tmux" in content
    assert "launched before waiting on either" in content


def test_plan_issues_rerounds_are_current_only_and_cap_at_six_rounds():
    paths = [
        SKILLS / "plan-issues" / "SKILL.md",
        SKILLS / "planning-workflows" / "references" / "plan-issues" / "plan-issues.md",
        SKILLS
        / "planning-workflows"
        / "references"
        / "plan-issues-priority-grouped-conversion.md",
    ]
    for path in paths:
        content = path.read_text().lower()
        assert "current-only" in content, path
        assert "prior raw review artifacts" in content, path
        assert "no separate artifact-consistency review" in content, path
        assert "six dual-lane review rounds" in content, path
        assert "meta-reviews do not count" in content, path
        assert "ask the user to decide" in content, path

    cap_references = [
        SKILLS / "planning-workflows" / "SKILL.md",
        SKILLS
        / "planning-workflows"
        / "references"
        / "writing-plans"
        / "references"
        / "out-of-scope-issue-planning.md",
    ]
    for path in cap_references:
        content = path.read_text().lower()
        assert "six dual-lane review rounds" in content, path
        assert "meta-reviews do not count" in content, path
        assert "ask the user to decide" in content, path


def test_active_skills_never_use_print_only_fallback_model_flag():
    violations = [
        f"{path.relative_to(ROOT)}:{line_number}: {line.strip()}"
        for path in _all_skill_markdown()
        for line_number, line in enumerate(path.read_text().splitlines(), start=1)
        if PRINT_ONLY_FALLBACK_FLAG in line
    ]

    assert not violations, "\n".join(violations)


def test_active_skills_do_not_claim_automatic_interactive_opus_fallback():
    violations = [
        f"{path.relative_to(ROOT)}:{line_number}: {line.strip()}"
        for path in _all_skill_markdown()
        for line_number, line in enumerate(path.read_text().splitlines(), start=1)
        if AUTOMATIC_FALLBACK_CLAIM.search(line)
    ]

    assert not violations, "\n".join(violations)


def test_interactive_claude_lane_defines_both_explicit_model_commands():
    for path in INTERACTIVE_CLAUDE_MODEL_POLICY_FILES:
        content = path.read_text()
        assert FABLE_PRIMARY_COMMAND in content, path
        assert OPUS_FALLBACK_COMMAND in content, path


def test_interactive_claude_fallback_is_an_explicit_fresh_session_procedure():
    for path in INTERACTIVE_CLAUDE_MODEL_POLICY_FILES:
        content = path.read_text().lower()
        assert "no automatic model fallback" in content, path
        assert "fresh interactive" in content, path
        assert "same immutable" in content or "same bundle" in content, path


def test_interactive_claude_lane_records_the_actual_model_banner():
    for path in INTERACTIVE_CLAUDE_MODEL_POLICY_FILES:
        content = path.read_text().lower()
        assert "banner" in content, path
        assert "before the substantive prompt" in content or (
            "before sending the substantive" in content
        ), path
        assert "actually performed the review" in content or (
            "actual banner/model" in content
        ), path


def test_interactive_claude_fallback_fails_closed_without_a_waiver():
    for path in AUTHORITATIVE_CLAUDE_MODEL_POLICY_FILES:
        content = path.read_text().lower()
        assert "fail closed" in content, path
        assert "waive" in content or "override" in content, path


def test_interactive_claude_fallback_keeps_print_mode_prohibited():
    for path in INTERACTIVE_CLAUDE_MODEL_POLICY_FILES:
        assert PRINT_MODE_MENTION.search(path.read_text()), path

    violations = [
        f"{path.relative_to(ROOT)}:{line_number}: {line.strip()}"
        for path in _all_skill_markdown()
        for line_number, line in _fenced_lines(path)
        if PRINT_MODE_COMMAND.match(line)
    ]

    assert not violations, "\n".join(violations)


def test_interactive_claude_fallback_preserves_parallel_lane_contract():
    contract = "before waiting on or adjudicating the companion"
    for path in INTERACTIVE_CLAUDE_MODEL_POLICY_FILES:
        assert contract in path.read_text().lower(), path


def test_recovery_references_do_not_reinstate_delegated_codex_lane():
    forbidden = (
        "codex-style `delegate_task`",
        "codex-style hermes `delegate_task`",
        "run a codex-style independent review via `delegate_task`",
        '"delegation_id"',
        '"codex_delegate"',
    )
    for path in MIGRATED_CODEX_RECOVERY_REFERENCES:
        content = path.read_text().lower()
        assert "interactive codex" in content, path
        assert "tmux" in content, path
        assert not any(phrase in content for phrase in forbidden), path
