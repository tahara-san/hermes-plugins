import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills" / "software-development"
CLAUDE_I = ROOT / "skills" / "autonomous-ai-agents" / "claude-i" / "SKILL.md"

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
    SKILLS
    / "planning-workflows"
    / "references"
    / "scoped-plan-code-review-gates.md",
]

NONINTERACTIVE_CODEX_COMMAND = re.compile(
    r"\s*(?:\$\s*)?(?:codex\s+(?:exec|review)\b|npx\s+@openai/codex\b)",
    re.IGNORECASE,
)

DEPRECATED_CODEX_LABELS = re.compile(
    r"codex-style|codex cli process|async codex|codex delegate",
    re.IGNORECASE,
)


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
        SKILLS
        / "planning-workflows"
        / "references"
        / "codex-cli-review-lane.md"
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


def test_plan_issues_requires_ordered_task_directory_names():
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
        content = path.read_text()
        assert "<implementation-order>-<task-name>" in content, path
        assert "zero-padded" in content, path
        assert "same number" in content or "share a number" in content, path


def test_plan_issues_does_not_serialize_independent_task_reviews():
    paths = [
        SKILLS / "planning-workflows" / "SKILL.md",
        SKILLS / "planning-workflows" / "references" / "plan-issues" / "plan-issues.md",
        SKILLS
        / "planning-workflows"
        / "references"
        / "plan-issues-priority-grouped-conversion.md",
    ]
    forbidden = (
        "review them one by one",
        "do not move to the next generated task",
        "run review waves by implementation-order prefix",
        "wait for the wave",
    )
    for path in paths:
        content = path.read_text().lower()
        assert "implementation-order prefix does not impose review order" in content, path
        assert not any(phrase in content for phrase in forbidden), path


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
    assert "<implementation-order>-<task-name>" in content
    assert "does not delete" in content
    assert "managed tmux" in content
    assert "launched before waiting on either" in content


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
