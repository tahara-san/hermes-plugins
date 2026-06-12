#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_DESCRIPTION = 1024
MAX_CONTENT = 100_000


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("missing closing frontmatter delimiter")
    raw = text[4:end]
    out: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith(" "):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip().strip('"\'')
    return out


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        fm = parse_frontmatter(text)
    except ValueError as exc:
        return [f"{path}: {exc}"]
    for key in ("name", "description"):
        if not fm.get(key):
            errors.append(f"{path}: missing {key}")
    if len(fm.get("description", "")) > MAX_DESCRIPTION:
        errors.append(f"{path}: description exceeds {MAX_DESCRIPTION} chars")
    if len(text) > MAX_CONTENT:
        errors.append(f"{path}: content exceeds {MAX_CONTENT} chars")
    name = fm.get("name", "")
    if name and not re.match(r"^[a-z0-9][a-z0-9_-]{0,63}$", name):
        errors.append(f"{path}: invalid skill name {name!r}")
    if not text.split("\n---\n", 1)[-1].strip():
        errors.append(f"{path}: empty body")
    return errors


def main() -> int:
    errors: list[str] = []
    for skill in sorted((ROOT / "skills").rglob("SKILL.md")):
        errors.extend(validate_skill(skill))
    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("Skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
