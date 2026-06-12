#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    files = []
    excluded_parts = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    excluded_name_suffixes = (".egg-info", ".dist-info")
    excluded_suffixes = {".pyc", ".pyo"}
    for base in ("skills", "plugins", "bundles", "manifests", "docs"):
        for p in sorted((ROOT / base).rglob("*")):
            if any(part in excluded_parts for part in p.parts):
                continue
            if any(part.endswith(excluded_name_suffixes) for part in p.parts):
                continue
            if p.suffix in excluded_suffixes:
                continue
            if p.is_file():
                files.append(str(p.relative_to(ROOT)))
    out = {"name": "hermes-planning-workflows", "file_count": len(files), "files": files}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
