import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills" / "software-development"

CORE_REVIEW_FILES = [
    SKILLS / "plan-issues" / "SKILL.md",
    SKILLS / "plan-doc" / "SKILL.md",
    SKILLS / "plan-code" / "SKILL.md",
    SKILLS / "plan-commit" / "SKILL.md",
    SKILLS / "planning-workflows" / "SKILL.md",
    SKILLS / "planning-workflows" / "references" / "plan-issues" / "plan-issues.md",
    SKILLS / "planning-workflows" / "references" / "plan-issues-priority-grouped-conversion.md",
    SKILLS / "planning-workflows" / "references" / "plan-doc" / "plan-doc.md",
    SKILLS / "planning-workflows" / "references" / "plan-code" / "plan-code.md",
]

LOCAL_CODEX_PERMISSION_PATTERNS = [
    re.compile(r"try authenticated local Codex", re.IGNORECASE),
    re.compile(r"local Codex fallback[^\n]*(?:may|can|should) be used", re.IGNORECASE),
    re.compile(r"using a local Codex(?:/Claude)? fallback", re.IGNORECASE),
]


def _all_planning_markdown() -> list[Path]:
    roots = [
        SKILLS / "plan-issues",
        SKILLS / "plan-doc",
        SKILLS / "plan-code",
        SKILLS / "plan-commit",
        SKILLS / "planning-workflows",
    ]
    return sorted(path for root in roots for path in root.rglob("*.md"))


def _fenced_commands(path: Path) -> list[tuple[int, str]]:
    commands: list[tuple[int, str]] = []
    fenced = False
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced and re.match(
            r"\s*(?:\$\s*)?(?:codex\b|npx\s+@openai/codex\b)",
            line,
            re.IGNORECASE,
        ):
            commands.append((line_number, line.strip()))
    return commands


def test_core_review_contract_uses_unambiguous_hermes_delegate_name():
    for path in CORE_REVIEW_FILES:
        content = path.read_text()
        assert "Hermes delegated review" in content, path
        assert "Codex-style" not in content, path


def test_planning_workflows_never_authorize_local_codex_execution():
    violations: list[str] = []
    for path in _all_planning_markdown():
        content = path.read_text()
        for pattern in LOCAL_CODEX_PERMISSION_PATTERNS:
            if match := pattern.search(content):
                line = content.count("\n", 0, match.start()) + 1
                violations.append(f"{path.relative_to(ROOT)}:{line}: {match.group(0)}")
        for line, command in _fenced_commands(path):
            violations.append(f"{path.relative_to(ROOT)}:{line}: {command}")

    assert not violations, "\n".join(violations)


def test_legacy_codex_chunk_alias_is_not_an_active_instruction():
    path = SKILLS / "planning-workflows" / "references" / "plan-doc" / "plan-doc.md"
    assert "/codex-chunk" not in path.read_text()


def test_claude_code_cli_lane_remains_explicitly_supported():
    content = (SKILLS / "planning-workflows" / "SKILL.md").read_text()
    assert "Claude Code CLI" in content
    assert "claude-i" in content
    assert "intentionally uses" in content
