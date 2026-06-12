from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_expected_directories_exist():
    for rel in ["skills", "plugins", "bundles", "manifests", "docs", "scripts"]:
        assert (ROOT / rel).is_dir(), rel


def test_core_package_files_exist():
    expected = [
        "skills/software-development/planning-workflows/SKILL.md",
        "skills/software-development/plan-doc/SKILL.md",
        "skills/software-development/plan-code/SKILL.md",
        "skills/software-development/plan-clean/SKILL.md",
        "skills/software-development/plan-issues/SKILL.md",
        "skills/software-development/simplify/SKILL.md",
        "skills/autonomous-ai-agents/claude-i/SKILL.md",
        "plugins/hermes-planning-guards/plugin.yaml",
        "plugins/hermes-planning-guards/hermes_planning_guards/plugin.py",
    ]
    for rel in expected:
        assert (ROOT / rel).is_file(), rel
