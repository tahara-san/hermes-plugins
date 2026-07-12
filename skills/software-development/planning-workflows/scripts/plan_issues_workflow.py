#!/usr/bin/env python3
"""Deterministic plan-issues ordering and task-local plan-review state.

This helper intentionally manages one conversion ledger and one current task at a
time. It does not discover/group issues or invoke reviewers; the governing skill
owns those judgment-heavy steps. The helper makes their filesystem state and
review transitions mechanically verifiable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from collections import namedtuple
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


class WorkflowError(RuntimeError):
    """A fail-closed workflow invariant was violated."""


BundleRecord = namedtuple(
    "BundleRecord", "version path digest bytes evidence_count manifest"
)

_KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_BUNDLE_VERSION = re.compile(
    r"(?:plan-)?review(?:-bundle)?-v(?P<version>[1-9][0-9]*)\.(?:md|json)$"
)
_STATUS_JSON = "plan-issues-status.json"
_STATUS_MD = "plan-issues-status.md"
_REQUIRED_LANES = ("codex", "claude")
_CLOSED_STATES = {"approved", "waived", "blocked_authorized"}
_LIVE_DOC_NAMES = ("spec.md", "todo.md", "task-metadata.json")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_DEPENDENCY_CONTRACT_MAX_BYTES = 16_384
_PLAN_PATH = re.compile(r"`(?P<path>[^`\n]+)`")
_REVIEW_ATTESTATIONS = {
    "codex": {
        "reviewer_mode": "interactive-codex-tui",
        "model": "gpt-5.6-sol",
        "effort": "xhigh",
    },
    "claude": {
        "reviewer_mode": "interactive-claude-code",
        "model": "claude-opus-4-8",
        "effort": "xhigh",
    },
}


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{uuid.uuid4().hex}")
    try:
        temporary.write_bytes(content)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _json_write(path: Path, value: Any) -> None:
    content = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    _atomic_write_bytes(path, content)


def _json_read(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise WorkflowError(f"required workflow file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WorkflowError(f"invalid JSON in {path}: {exc}") from exc


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _normalize_definitions(
    definitions: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for raw in definitions:
        name = str(raw.get("name", ""))
        if not _KEBAB.fullmatch(name):
            raise WorkflowError(
                f"task name must be kebab-case without repeated/edge hyphens: {name!r}"
            )
        if name in normalized:
            raise WorkflowError(f"duplicate task name: {name}")
        prerequisites = [str(value) for value in raw.get("prerequisites", [])]
        if len(prerequisites) != len(set(prerequisites)):
            raise WorkflowError(f"duplicate prerequisite on task {name}")
        normalized[name] = {
            "name": name,
            "source_issues": [str(value) for value in raw.get("source_issues", [])],
            "prerequisites": prerequisites,
        }

    known = set(normalized)
    for name, task in normalized.items():
        missing = sorted(set(task["prerequisites"]) - known)
        if missing:
            raise WorkflowError(
                f"task {name} references unknown prerequisites: {', '.join(missing)}"
            )
        if name in task["prerequisites"]:
            raise WorkflowError(f"dependency cycle detected: {name} -> {name}")
    return normalized


def _find_cycle(tasks: Mapping[str, Mapping[str, Any]]) -> list[str] | None:
    visiting: list[str] = []
    visited: set[str] = set()

    def visit(name: str) -> list[str] | None:
        if name in visiting:
            index = visiting.index(name)
            return visiting[index:] + [name]
        if name in visited:
            return None
        visiting.append(name)
        for prerequisite in tasks[name]["prerequisites"]:
            cycle = visit(prerequisite)
            if cycle:
                return cycle
        visiting.pop()
        visited.add(name)
        return None

    for task_name in tasks:
        cycle = visit(task_name)
        if cycle:
            return cycle
    return None


def derive_task_layout(
    definitions: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Validate a graph and assign longest-prerequisite-path implementation waves."""

    tasks = _normalize_definitions(definitions)
    cycle = _find_cycle(tasks)
    if cycle:
        raise WorkflowError(f"dependency cycle detected: {' -> '.join(cycle)}")

    order_cache: dict[str, int] = {}

    def order_for(name: str) -> int:
        if name not in order_cache:
            prerequisites = tasks[name]["prerequisites"]
            order_cache[name] = (
                1
                if not prerequisites
                else max(order_for(item) for item in prerequisites) + 1
            )
        return order_cache[name]

    directories = {name: name for name in tasks}
    cohorts: dict[int, list[str]] = {}
    for name in tasks:
        cohorts.setdefault(order_for(name), []).append(directories[name])
    for cohort in cohorts.values():
        cohort.sort()

    layout: dict[str, dict[str, Any]] = {}
    for name, task in tasks.items():
        order = order_for(name)
        layout[name] = {
            "name": name,
            "directory": directories[name],
            "implementation_order": order,
            "source_issues": task["source_issues"],
            "prerequisite_ids": list(task["prerequisites"]),
            "direct_prerequisites": [
                directories[prerequisite] for prerequisite in task["prerequisites"]
            ],
            "parallel_cohort": cohorts[order],
        }
    return layout


def _status_path(tasks_root: Path) -> Path:
    return tasks_root / _STATUS_JSON


def _load_status(tasks_root: Path) -> dict[str, Any]:
    status = _json_read(_status_path(tasks_root))
    if status.get("schema_version") != 1:
        raise WorkflowError("unsupported or missing plan-issues status schema_version")
    return status


def _task_entry(status: Mapping[str, Any], slug: str) -> dict[str, Any]:
    try:
        return status["tasks"][slug]
    except KeyError as exc:
        raise WorkflowError(f"unknown task slug: {slug}") from exc


def _current_slug(status: Mapping[str, Any]) -> str | None:
    value = status.get("current_task")
    return str(value) if value else None


def _live_docs_digest(task_dir: Path) -> str:
    digest = hashlib.sha256()
    included = 0
    missing = [
        name for name in ("spec.md", "todo.md") if not (task_dir / name).is_file()
    ]
    if missing:
        raise WorkflowError(
            f"task must contain required authoritative spec.md and todo.md: {task_dir}"
        )
    for name in _LIVE_DOC_NAMES:
        path = task_dir / name
        if path.is_file():
            if path.is_symlink():
                raise WorkflowError(
                    f"authoritative task documents cannot be symlinks: {path}"
                )
            digest.update(name.encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
            included += 1
    contracts = task_dir / "dependency-contracts"
    if contracts.is_dir():
        for path in sorted(contracts.glob("*.json")):
            digest.update(path.relative_to(task_dir).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
            included += 1
    if not included:
        raise WorkflowError(f"task has no authoritative live documents: {task_dir}")
    return digest.hexdigest()


def _bundle_path(root: Path, slug: str, bundle: Mapping[str, Any]) -> Path:
    raw_path = str(bundle.get("path") or bundle.get("bundle_path") or "")
    if not raw_path:
        raise WorkflowError("current bundle path is missing")
    path = (root / raw_path).resolve()
    expected_root = (root / slug / "reviews" / "bundles").resolve()
    try:
        path.relative_to(expected_root)
    except ValueError as exc:
        raise WorkflowError(
            f"bundle path is outside the task bundle directory: {raw_path}"
        ) from exc
    return path


def _validate_bundle_integrity(
    root: Path, slug: str, bundle: Mapping[str, Any]
) -> Path:
    path = _bundle_path(root, slug, bundle)
    if path.is_symlink() or not path.is_file():
        raise WorkflowError(f"current immutable bundle is missing or unsafe: {path}")
    content = path.read_bytes()
    expected_bytes = bundle.get("bytes", bundle.get("bundle_bytes"))
    expected_digest = bundle.get("digest", bundle.get("bundle_digest"))
    if len(content) != expected_bytes or _sha256_bytes(content) != expected_digest:
        raise WorkflowError(
            f"current immutable bundle was modified after generation: {path}"
        )
    return path


def _reconcile_approved_state(root: Path, status: dict[str, Any]) -> bool:
    previous = _current_slug(status)
    stale: list[str] = []
    for slug in status.get("task_order", []):
        entry = status["tasks"][slug]
        if entry.get("state") != "approved":
            continue
        try:
            _validate_approval_chain(root, slug, entry)
        except (WorkflowError, OSError, KeyError, TypeError, ValueError, UnicodeError):
            stale.append(slug)

    if not stale:
        return False
    for slug in stale:
        entry = status["tasks"][slug]
        entry["state"] = "approval_stale"
        entry["blocker"] = "Approved bundle or authoritative documents no longer match."
        entry["next_action"] = (
            "Regenerate this task's explicit manifest and obtain fresh matching reviews."
        )
    if previous and previous not in stale:
        earliest = previous
    else:
        earliest = next(
            slug
            for slug in status["task_order"]
            if status["tasks"][slug]["state"] not in _CLOSED_STATES
        )
    if previous and previous != earliest:
        previous_entry = status["tasks"][previous]
        if previous_entry["state"] == "current":
            previous_entry["state"] = "pending"
    status["current_task"] = earliest
    return True


def refresh_status(tasks_root: Path | str) -> dict[str, Any]:
    """Recompute approval validity and refresh the human-readable ledger."""

    root = Path(tasks_root)
    status = _load_current_status(root)
    if _reconcile_approved_state(root, status):
        _persist(root, status)
    else:
        _render_ledger(root, status)
    return status


def _render_handoff(tasks_root: Path, slug: str, entry: Mapping[str, Any]) -> None:
    bundle = entry.get("current_bundle") or {}
    reviews = entry.get("reviews") or {}
    blockers = entry.get("blocker") or "None"
    content = f"""# Fresh-session handoff: {slug}

## Objective and Authoritative files

- Objective: implement the reviewed task in `{slug}` without importing unrelated work.
- Authoritative files: `spec.md`, `todo.md`, and `task-metadata.json`.

## Implementation order

- Implementation order: `{entry["implementation_order"]:02d}`
- Parallel cohort: {", ".join(entry["parallel_cohort"]) or "None"}
- Direct prerequisites: {", ".join(entry["direct_prerequisites"]) or "None"}

## Current review state

- Current bundle: `{bundle.get("path", "not generated")}`
- Current bundle digest: `{bundle.get("digest", "not generated")}`
- Codex lane: `{(reviews.get("codex") or {}).get("verdict", "not run")}`
- Claude lane: `{(reviews.get("claude") or {}).get("verdict", "not run")}`
- Aggregate state: `{entry["state"]}`
- Blocker: {blockers}

## Exact next action

{entry.get("next_action", "Generate the current task-local review bundle.")}

## Authorization and gates

- Planning authorization: planning only until the user explicitly authorizes implementation.
- Dependency gates: prerequisite contracts must bind matching approved bundles; unapproved prerequisites block implementation.
- Unrelated dirty work: exclude unrelated modified/untracked paths from bundles, edits, and delivery.
- Out-of-scope: deduplicate and log each non-exempt finding under `tasks/out-of-scope-issues/<priority>/[manual/]`; Dependabot-only counts are exempt.

## Required final report

Report changed files, verification output, exact bundle/hash and both lane verdicts, dependency gates, deviations, delivery state, and every out-of-scope issue created or updated.
"""
    _atomic_write_bytes(tasks_root / slug / "handoff.md", content.encode())


def _render_ledger(tasks_root: Path, status: Mapping[str, Any]) -> None:
    lines = [
        "# Plan-issues conversion status",
        "",
        "| Task | Source issues | Prerequisites | Parallel cohort | Bundle | Hermes/Codex verdict | Claude verdict | Blocker | Next action | Aggregate state |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    current = _current_slug(status)
    for slug in status["task_order"]:
        entry = status["tasks"][slug]
        bundle = entry.get("current_bundle") or {}
        reviews = entry.get("reviews") or {}
        state = entry["state"] + (" (current)" if slug == current else "")
        lines.append(
            "| "
            + " | ".join(
                [
                    slug,
                    "<br>".join(entry["source_issues"]) or "—",
                    ", ".join(entry["direct_prerequisites"]) or "—",
                    ", ".join(entry["parallel_cohort"]) or "—",
                    (
                        f"v{bundle.get('version')} `{str(bundle.get('digest', ''))[:12]}`"
                        if bundle
                        else "—"
                    ),
                    (reviews.get("codex") or {}).get("verdict", "—"),
                    (reviews.get("claude") or {}).get("verdict", "—"),
                    str(entry.get("blocker") or "—").replace("|", "\\|"),
                    str(entry.get("next_action") or "—").replace("|", "\\|"),
                    state,
                ]
            )
            + " |"
        )
    _atomic_write_bytes(tasks_root / _STATUS_MD, ("\n".join(lines) + "\n").encode())


def _persist(tasks_root: Path, status: dict[str, Any]) -> None:
    _json_write(_status_path(tasks_root), status)
    _render_ledger(tasks_root, status)
    for slug in status["task_order"]:
        task_dir = tasks_root / slug
        if task_dir.is_dir():
            _render_handoff(tasks_root, slug, status["tasks"][slug])


def _load_current_status(tasks_root: Path) -> dict[str, Any]:
    status = _load_status(tasks_root)
    if _reconcile_approved_state(tasks_root, status):
        _persist(tasks_root, status)
    return status


def initialize_conversion(
    tasks_root: Path | str,
    definitions: Sequence[Mapping[str, Any]],
    *,
    max_rounds: int = 2,
) -> dict[str, Any]:
    """Create all task shells only after the complete graph passes validation."""

    root = Path(tasks_root)
    if max_rounds < 1:
        raise WorkflowError("max_rounds must be at least 1")
    layout = derive_task_layout(definitions)
    ordered = sorted(
        layout.values(),
        key=lambda item: (item["implementation_order"], item["directory"]),
    )

    collisions = [
        item["directory"] for item in ordered if (root / item["directory"]).exists()
    ]
    if collisions:
        raise WorkflowError(
            "refusing to overwrite existing task directories: " + ", ".join(collisions)
        )

    # No filesystem writes occur before every graph/collision check above passes.
    root.mkdir(parents=True, exist_ok=True)
    task_entries: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(ordered):
        slug = item["directory"]
        task_dir = root / slug
        task_dir.mkdir()
        metadata = {
            "schema_version": 1,
            "stable_name": item["name"],
            "directory": slug,
            "implementation_order": item["implementation_order"],
            "source_issues": item["source_issues"],
            "prerequisite_ids": item["prerequisite_ids"],
            "direct_prerequisites": item["direct_prerequisites"],
            "parallel_cohort": item["parallel_cohort"],
        }
        _json_write(task_dir / "task-metadata.json", metadata)
        task_entries[slug] = {
            **metadata,
            "state": "current" if index == 0 else "pending",
            "current_bundle": None,
            "reviews": {},
            "blocker": None,
            "next_action": (
                "Create spec.md and todo.md, then generate this task-local bundle."
                if index == 0
                else "Wait for the current task to close."
            ),
            "failed_rounds": 0,
            "superseded_reviews": [],
        }

    status = {
        "schema_version": 1,
        "max_rounds": max_rounds,
        "task_order": [item["directory"] for item in ordered],
        "current_task": ordered[0]["directory"] if ordered else None,
        "tasks": task_entries,
    }
    _persist(root, status)
    return status


def _next_bundle_version(reviews_dir: Path) -> int:
    versions: list[int] = []
    if reviews_dir.is_dir():
        for path in reviews_dir.rglob("*"):
            if not path.is_file():
                continue
            match = _BUNDLE_VERSION.fullmatch(path.name)
            if match:
                versions.append(int(match.group("version")))
    return max(versions, default=0) + 1


def _plan_claim_paths(tasks_root: Path, slug: str) -> set[Path]:
    task_dir = (tasks_root / slug).resolve()
    project_root = tasks_root.resolve().parent
    claims: set[Path] = set()
    for document_name in ("spec.md", "todo.md"):
        document = task_dir / document_name
        for match in _PLAN_PATH.finditer(document.read_text()):
            raw = match.group("path").strip().rstrip(".,:;")
            if (
                not raw
                or any(character.isspace() for character in raw)
                or raw.startswith(("http://", "https://", "/", "-"))
                or any(character in raw for character in "*?<>|{}[]()")
            ):
                continue
            looks_like_path = "/" in raw or "." in Path(raw).name
            if not looks_like_path:
                continue
            candidate = (
                task_dir / raw
                if raw in _LIVE_DOC_NAMES or raw == "evidence-manifest.json"
                else project_root / raw
            ).resolve()
            try:
                candidate.relative_to(project_root)
            except ValueError as exc:
                raise WorkflowError(
                    f"plan-named path escapes project root in {document_name}: {raw}"
                ) from exc
            if not candidate.is_file():
                raise WorkflowError(
                    f"plan-named path is missing before dispatch: {raw} ({document_name})"
                )
            claims.add(candidate)
    return claims


def _validate_manifest(
    tasks_root: Path, slug: str, manifest_path: Path
) -> list[dict[str, Any]]:
    task_dir = (tasks_root / slug).resolve()
    project_root = tasks_root.resolve().parent
    payload = _json_read(manifest_path)
    evidence = payload.get("evidence") if isinstance(payload, dict) else None
    if not isinstance(evidence, list) or not evidence:
        raise WorkflowError("evidence manifest must contain a non-empty evidence list")

    validated: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for item in evidence:
        if not isinstance(item, dict):
            raise WorkflowError("each evidence manifest item must be an object")
        raw_path = str(item.get("path", ""))
        reason = str(item.get("reason", "")).strip()
        if not raw_path or not reason:
            raise WorkflowError("each evidence manifest item requires path and reason")
        path = (task_dir / raw_path).resolve()
        try:
            path.relative_to(project_root)
        except ValueError as exc:
            raise WorkflowError(
                f"manifest path escapes project root: {raw_path}"
            ) from exc
        if not path.exists():
            raise WorkflowError(f"manifest path does not exist: {raw_path}")
        if path.is_dir():
            raise WorkflowError(
                f"manifest directories are not allowed; enumerate exact files: {raw_path}"
            )
        relative_project = path.relative_to(project_root)
        try:
            path.relative_to(task_dir / "reviews")
            is_review_artifact = True
        except ValueError:
            is_review_artifact = False
        if is_review_artifact:
            raise WorkflowError(f"review artifacts are self-excluded: {raw_path}")
        if path in seen:
            raise WorkflowError(f"duplicate evidence manifest path: {raw_path}")
        seen.add(path)

        try:
            relative_tasks = path.relative_to(tasks_root.resolve())
        except ValueError:
            relative_tasks = None
        if (
            relative_tasks
            and relative_tasks.parts
            and relative_tasks.parts[0] != slug
            and path.name in {"spec.md", "todo.md"}
        ):
            raise WorkflowError(
                f"full neighboring plan files are forbidden; use a compact dependency contract: {raw_path}"
            )
        validated.append(
            {
                "requested_path": raw_path,
                "path": path,
                "display_path": relative_project.as_posix(),
                "reason": reason,
                "digest": _sha256_bytes(path.read_bytes()),
                "bytes": path.stat().st_size,
            }
        )
    return validated


def _validate_dependency_contract(
    root: Path,
    dependent_slug: str,
    prerequisite_slug: str,
    contract_path: Path,
) -> str:
    if contract_path.is_symlink() or not contract_path.is_file():
        raise WorkflowError(
            f"dependency contract is missing or unsafe for {prerequisite_slug}"
        )
    contract = _json_read(contract_path)
    aggregate_identity = str(contract.get("aggregate_identity", ""))
    aggregate_path = (root.parent / aggregate_identity).resolve()
    aggregate_root = (root / prerequisite_slug / "reviews" / "aggregates").resolve()
    try:
        aggregate_path.relative_to(aggregate_root)
    except ValueError as exc:
        raise WorkflowError(
            f"dependency contract aggregate identity is unsafe for {prerequisite_slug}"
        ) from exc
    if aggregate_path.is_symlink() or not aggregate_path.is_file():
        raise WorkflowError(
            f"dependency contract aggregate is missing for {prerequisite_slug}"
        )
    aggregate_bytes = aggregate_path.read_bytes()
    try:
        aggregate = json.loads(aggregate_bytes)
    except json.JSONDecodeError as exc:
        raise WorkflowError(
            f"dependency contract aggregate is invalid for {prerequisite_slug}"
        ) from exc
    material_digest = _sha256_bytes(
        json.dumps(
            contract.get("excerpts"),
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode()
    )
    if (
        contract.get("dependent_task") != dependent_slug
        or contract.get("prerequisite_task") != prerequisite_slug
        or contract.get("approved_bundle_digest") != aggregate.get("bundle_digest")
        or contract.get("approved_aggregate_digest") != _sha256_bytes(aggregate_bytes)
        or contract.get("material_contract_digest") != material_digest
    ):
        raise WorkflowError(
            f"dependency contract is stale or invalid for {prerequisite_slug}"
        )
    _validate_aggregate_evidence(root, prerequisite_slug, aggregate)
    if aggregate.get("state") != "approved":
        raise WorkflowError(
            f"dependency contract aggregate is not approved for {prerequisite_slug}"
        )
    return _relative(contract_path, root.parent)


def _dependency_bindings(
    root: Path,
    status: Mapping[str, Any],
    slug: str,
    evidence: Sequence[Mapping[str, Any]],
) -> tuple[list[str], list[dict[str, str]]]:
    entry = _task_entry(status, slug)
    evidence_paths = {Path(item["path"]).resolve() for item in evidence}
    contracts: list[str] = []
    gates: list[dict[str, str]] = []
    for prerequisite_slug in entry["direct_prerequisites"]:
        prerequisite = _task_entry(status, prerequisite_slug)
        state = prerequisite["state"]
        contract_path = (
            root / slug / "dependency-contracts" / f"{prerequisite_slug}.json"
        )
        if contract_path.exists():
            contract_identity = _validate_dependency_contract(
                root, slug, prerequisite_slug, contract_path
            )
            if contract_path.resolve() not in evidence_paths:
                raise WorkflowError(
                    f"dependency contract for {prerequisite_slug} must be in the explicit manifest"
                )
            contracts.append(contract_identity)
        elif state == "approved":
            raise WorkflowError(
                f"approved dependency contract is missing for {prerequisite_slug}"
            )
        elif state in {"waived", "blocked_authorized"}:
            gates.append(
                {
                    "prerequisite": prerequisite_slug,
                    "state": state,
                    "blocker": str(prerequisite.get("blocker") or "unspecified"),
                }
            )
        else:
            raise WorkflowError(
                f"dependency gate is not review-ready: {prerequisite_slug} ({state})"
            )
    return contracts, gates


def _ensure_current_task(status: Mapping[str, Any], slug: str) -> None:
    current = _current_slug(status)
    if current != slug:
        raise WorkflowError(
            f"current task is {current or 'none'}; do not generate or dispatch {slug}"
        )


def build_review_bundle(
    tasks_root: Path | str,
    slug: str | None,
    manifest_path: Path | str,
) -> BundleRecord:
    """Generate one bounded immutable bundle with task-local versioning."""

    if not slug or not isinstance(slug, str):
        raise WorkflowError("exactly one target slug is required")
    root = Path(tasks_root)
    status = _load_current_status(root)
    entry = _task_entry(status, slug)
    _ensure_current_task(status, slug)
    if entry["state"] in _CLOSED_STATES:
        raise WorkflowError(f"task is already closed: {slug}")

    task_dir = root / slug
    if not task_dir.is_dir():
        raise WorkflowError(f"task directory is missing: {task_dir}")
    current_live_digest = _live_docs_digest(task_dir)

    current_bundle = entry.get("current_bundle")
    current_reviews = entry.get("reviews") or {}
    if entry.get("failed_rounds", 0) >= status["max_rounds"]:
        raise WorkflowError(
            "review round cap reached; stop for a user checkpoint with root causes/options"
        )
    if current_bundle:
        _validate_bundle_integrity(root, slug, current_bundle)
        if current_reviews:
            if len(current_reviews) < len(_REQUIRED_LANES):
                raise WorkflowError(
                    "both current-bundle review lanes must complete before amending/regenerating"
                )
            if entry["state"] == "reviewing":
                raise WorkflowError(
                    "aggregate both current-bundle results before regenerating"
                )
        if current_live_digest == current_bundle.get("live_docs_digest"):
            raise WorkflowError(
                "authoritative docs must change after consolidated blockers before reround"
            )

    evidence = _validate_manifest(root, slug, Path(manifest_path))
    evidence_paths = {Path(item["path"]).resolve() for item in evidence}
    required_docs = {(task_dir / name).resolve() for name in ("spec.md", "todo.md")}
    if not required_docs.issubset(evidence_paths):
        raise WorkflowError(
            "explicit manifest must include the current task's spec.md and todo.md"
        )
    omitted_claims = sorted(
        _relative(path, root.parent)
        for path in _plan_claim_paths(root, slug) - evidence_paths
    )
    if omitted_claims:
        raise WorkflowError(
            "explicit manifest omitted plan-named paths: " + ", ".join(omitted_claims)
        )
    dependency_contracts, dependency_gates = _dependency_bindings(
        root, status, slug, evidence
    )
    version = _next_bundle_version(task_dir / "reviews")
    review_context: dict[str, Any] = {"coverage": "latest-state"}
    if current_bundle:
        previous_manifest = {
            item["path"]: item["digest"] for item in current_bundle.get("manifest", [])
        }
        current_manifest = {item["display_path"]: item["digest"] for item in evidence}
        review_context = {
            "coverage": "latest-state-plus-delta",
            "previous_bundle_digest": current_bundle["digest"],
            "changed_evidence": sorted(
                path
                for path, digest in current_manifest.items()
                if previous_manifest.get(path) != digest
            ),
            "removed_evidence": sorted(set(previous_manifest) - set(current_manifest)),
            "consolidated_blockers": [entry["blocker"]] if entry.get("blocker") else [],
        }

    lines = [
        f"# Immutable plan review bundle: {slug} v{version}",
        "",
        f"Target task: `{slug}`",
        "This bundle contains only the explicit evidence manifest below.",
        "",
    ]
    if current_bundle:
        lines.extend(
            [
                "## Current-only reround delta",
                "",
                f"- Previous bundle digest: `{current_bundle['digest']}`",
                "- Prior full bundles and prior raw review artifacts are intentionally excluded.",
                "- Changed current evidence: "
                + (", ".join(review_context["changed_evidence"]) or "none"),
                "- Removed evidence: "
                + (", ".join(review_context["removed_evidence"]) or "none"),
                "- Consolidated blockers addressed: "
                + ("; ".join(review_context["consolidated_blockers"]) or "none"),
                "",
            ]
        )
    lines.extend(["## Manifest", ""])
    for item in evidence:
        lines.append(
            f"- `{item['display_path']}` — {item['reason']} "
            f"(sha256 `{item['digest']}`, {item['bytes']} bytes)"
        )
    for item in evidence:
        lines.extend(
            [
                "",
                f"## Evidence: `{item['display_path']}`",
                "",
                f"Reason: {item['reason']}",
                "",
                "```text",
                item["path"].read_text(errors="replace").rstrip("\n"),
                "```",
            ]
        )
    content = ("\n".join(lines) + "\n").encode()
    bundles_dir = task_dir / "reviews" / "bundles"
    bundle_path = bundles_dir / f"plan-review-bundle-v{version}.md"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_bytes(bundle_path, content)
    digest = _sha256_bytes(content)
    manifest_record = [
        {
            "path": item["display_path"],
            "reason": item["reason"],
            "digest": item["digest"],
            "bytes": item["bytes"],
        }
        for item in evidence
    ]
    sidecar = {
        "schema_version": 1,
        "task": slug,
        "version": version,
        "path": _relative(bundle_path, root),
        "digest": digest,
        "bytes": len(content),
        "evidence_count": len(evidence),
        "manifest": manifest_record,
        "review_context": review_context,
        "live_docs_digest": current_live_digest,
        "dependency_contracts": dependency_contracts,
        "dependency_gates": dependency_gates,
    }
    _json_write(bundle_path.with_suffix(".json"), sidecar)

    entry["current_bundle"] = sidecar
    entry["reviews"] = {}
    entry["state"] = "reviewing"
    entry["blocker"] = None
    entry["next_action"] = (
        "Launch Codex and Claude against this exact digest, save both complete verdicts, "
        "then aggregate once."
    )
    _persist(root, status)
    return BundleRecord(
        version, bundle_path, digest, len(content), len(evidence), manifest_record
    )


def _parse_review_result(content: str) -> dict[str, str]:
    starts = re.findall(r"(?m)^BEGIN_REVIEW_RESULT\s*$", content)
    ends = re.findall(r"(?m)^END_REVIEW_RESULT\s*$", content)
    match = re.search(
        r"(?s)(?:\A|\n)BEGIN_REVIEW_RESULT\s*\n(.*?)\nEND_REVIEW_RESULT\s*\Z",
        content,
    )
    if len(starts) != 1 or len(ends) != 1 or match is None:
        raise WorkflowError(
            "reviewer artifact must contain exactly one review result block"
        )

    allowed = {"BUNDLE_SHA256", "REVIEWER_MODE", "MODEL", "EFFORT", "VERDICT"}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise WorkflowError("review result block contains a malformed field")
        key, value = (part.strip() for part in line.split(":", 1))
        if key not in allowed or key in fields or not value:
            raise WorkflowError(
                "review result block contains unknown, duplicate, or empty fields"
            )
        fields[key] = value
    if set(fields) != allowed:
        raise WorkflowError("review result block is missing required fields")
    return fields


def _validate_review_attestation(
    root: Path,
    slug: str,
    *,
    lane: str,
    bundle_digest: str,
    verdict: str,
    reviewer_artifact: Path | str,
    reviewer_mode: str,
    model: str,
    effort: str,
) -> dict[str, str]:
    expected = _REVIEW_ATTESTATIONS[lane]
    supplied = {
        "reviewer_mode": reviewer_mode,
        "model": model,
        "effort": effort,
    }
    for key, expected_value in expected.items():
        if supplied[key] != expected_value:
            raise WorkflowError(
                f"{lane} reviewer attestation requires {key}={expected_value}"
            )
    raw_path = Path(reviewer_artifact)
    path = (
        raw_path.resolve()
        if raw_path.is_absolute()
        else (root.parent / raw_path).resolve()
    )
    artifact_root = (root / slug / "reviews" / "raw").resolve()
    try:
        path.relative_to(artifact_root)
    except ValueError as exc:
        raise WorkflowError(
            f"reviewer artifact must be under {artifact_root}: {reviewer_artifact}"
        ) from exc
    if path.is_symlink() or not path.is_file():
        raise WorkflowError(f"reviewer artifact is missing or unsafe: {path}")

    try:
        content = path.read_text(errors="strict")
    except (OSError, UnicodeError) as exc:
        raise WorkflowError(f"reviewer artifact cannot be read safely: {path}") from exc
    fields = _parse_review_result(content)
    expected_fields = {
        "BUNDLE_SHA256": bundle_digest,
        "REVIEWER_MODE": reviewer_mode,
        "MODEL": model,
        "EFFORT": effort,
        "VERDICT": "PASS" if verdict == "APPROVED" else "CHANGES_REQUIRED",
    }
    if fields != expected_fields:
        raise WorkflowError(
            "review result block does not exactly match the recorded result"
        )
    return {
        "reviewer_artifact": _relative(path, root.parent),
        "reviewer_artifact_digest": _sha256_bytes(path.read_bytes()),
        **supplied,
    }


def _validate_aggregate_evidence(
    root: Path,
    slug: str,
    aggregate: Mapping[str, Any],
    *,
    status_reviews: Mapping[str, Any] | None = None,
    require_live_docs: bool = False,
) -> None:
    required_aggregate_fields = {
        "task",
        "version",
        "bundle_digest",
        "bundle_path",
        "bundle_bytes",
        "evidence_count",
        "manifest",
        "live_docs_digest",
        "lanes",
        "state",
    }
    if not required_aggregate_fields.issubset(aggregate):
        raise WorkflowError("aggregate is missing required approval-chain fields")
    if aggregate.get("task") != slug:
        raise WorkflowError("aggregate task identity does not match")
    _validate_bundle_integrity(root, slug, aggregate)
    lanes = aggregate.get("lanes")
    if not isinstance(lanes, Mapping) or set(lanes) != set(_REQUIRED_LANES):
        raise WorkflowError("aggregate must contain exactly both required review lanes")
    if status_reviews is not None and dict(lanes) != dict(status_reviews):
        raise WorkflowError("aggregate lanes do not match saved review results")

    blocking: list[str] = []
    changes_required = False
    for lane in _REQUIRED_LANES:
        review = lanes[lane]
        required_review_fields = {
            "task",
            "lane",
            "bundle_digest",
            "verdict",
            "blockers",
            "superseded",
            "reviewer_artifact",
            "reviewer_artifact_digest",
            "reviewer_mode",
            "model",
            "effort",
        }
        if (
            not isinstance(review, Mapping)
            or not required_review_fields.issubset(review)
            or review.get("task") != slug
            or review.get("lane") != lane
            or review.get("bundle_digest") != aggregate.get("bundle_digest")
            or review.get("superseded") is not False
            or review.get("verdict") not in {"APPROVED", "CHANGES_REQUIRED"}
        ):
            raise WorkflowError(f"saved {lane} review does not match the aggregate")
        attestation = _validate_review_attestation(
            root,
            slug,
            lane=lane,
            bundle_digest=str(review["bundle_digest"]),
            verdict=str(review["verdict"]),
            reviewer_artifact=str(review["reviewer_artifact"]),
            reviewer_mode=str(review["reviewer_mode"]),
            model=str(review["model"]),
            effort=str(review["effort"]),
        )
        if attestation["reviewer_artifact_digest"] != review.get(
            "reviewer_artifact_digest"
        ):
            raise WorkflowError(f"saved {lane} reviewer artifact was modified")
        blocking.extend(str(item) for item in review.get("blockers", []))
        changes_required = changes_required or review["verdict"] == "CHANGES_REQUIRED"

    expected_state = "changes_required" if blocking or changes_required else "approved"
    if aggregate.get("state") != expected_state:
        raise WorkflowError("aggregate state does not match its lane evidence")
    if require_live_docs:
        current_live_digest = _live_docs_digest(root / slug)
        if aggregate.get("live_docs_digest") != current_live_digest:
            raise WorkflowError(
                "aggregate does not bind the current authoritative documents"
            )


def _validate_approval_chain(
    root: Path, slug: str, entry: Mapping[str, Any]
) -> dict[str, Any]:
    bundle = entry.get("current_bundle") or {}
    _validate_bundle_integrity(root, slug, bundle)
    version = bundle.get("version")
    aggregate_path = root / slug / "reviews" / "aggregates" / f"v{version}.json"
    final_path = root / slug / "reviews" / "final-review.json"
    for path in (aggregate_path, final_path):
        if path.is_symlink() or not path.is_file():
            raise WorkflowError(
                f"approved review evidence is missing or unsafe: {path}"
            )
    aggregate = _json_read(aggregate_path)
    final = _json_read(final_path)
    if aggregate != final:
        raise WorkflowError(
            "final-review does not exactly match the approved aggregate"
        )
    if aggregate.get("bundle_digest") != bundle.get("digest"):
        raise WorkflowError("approved aggregate does not match the current bundle")
    _validate_aggregate_evidence(
        root,
        slug,
        aggregate,
        status_reviews=entry.get("reviews") or {},
        require_live_docs=True,
    )
    if aggregate.get("state") != "approved":
        raise WorkflowError("approval chain does not end in an approved aggregate")
    return aggregate


def record_review(
    tasks_root: Path | str,
    slug: str,
    *,
    lane: str,
    bundle_digest: str,
    verdict: str,
    reviewer_artifact: Path | str,
    reviewer_mode: str,
    model: str,
    effort: str,
    blockers: Iterable[str] = (),
    non_blocking: Iterable[str] = (),
) -> dict[str, Any]:
    root = Path(tasks_root)
    status = _load_current_status(root)
    entry = _task_entry(status, slug)
    _ensure_current_task(status, slug)
    if lane not in _REQUIRED_LANES:
        raise WorkflowError(f"unsupported review lane: {lane}")
    if not _DIGEST.fullmatch(bundle_digest):
        raise WorkflowError("bundle digest must be exactly 64 lowercase hex characters")
    normalized_verdict = verdict.upper()
    if normalized_verdict not in {"APPROVED", "CHANGES_REQUIRED"}:
        raise WorkflowError(f"unsupported review verdict: {verdict}")

    result = {
        "schema_version": 1,
        "task": slug,
        "lane": lane,
        "bundle_digest": bundle_digest,
        "verdict": normalized_verdict,
        "blockers": list(blockers),
        "non_blocking": list(non_blocking),
        "superseded": False,
    }
    current = entry.get("current_bundle")
    if not current:
        raise WorkflowError("no current review bundle exists")
    _validate_bundle_integrity(root, slug, current)
    result.update(
        _validate_review_attestation(
            root,
            slug,
            lane=lane,
            bundle_digest=bundle_digest,
            verdict=normalized_verdict,
            reviewer_artifact=reviewer_artifact,
            reviewer_mode=reviewer_mode,
            model=model,
            effort=effort,
        )
    )
    if entry["state"] != "reviewing":
        raise WorkflowError(f"task is not accepting reviews in state {entry['state']}")
    if bundle_digest != current.get("digest"):
        result["superseded"] = True
        superseded_dir = root / slug / "reviews" / "superseded"
        path = superseded_dir / f"delayed-{lane}-{bundle_digest}.json"
        if path.is_file():
            return _json_read(path)
        _json_write(path, result)
        relative_path = _relative(path, root)
        if relative_path not in entry.setdefault("superseded_reviews", []):
            entry["superseded_reviews"].append(relative_path)
        _persist(root, status)
        return result

    result["version"] = current["version"]
    existing = (entry.get("reviews") or {}).get(lane)
    if existing:
        comparable = {
            key: existing[key]
            for key in (
                "schema_version",
                "task",
                "lane",
                "bundle_digest",
                "verdict",
                "blockers",
                "non_blocking",
                "superseded",
                "version",
                "reviewer_artifact",
                "reviewer_artifact_digest",
                "reviewer_mode",
                "model",
                "effort",
            )
        }
        if comparable == result:
            return result
        raise WorkflowError(
            f"conflicting duplicate verdict for {lane} on current bundle digest"
        )
    verdict_path = (
        root / slug / "reviews" / "verdicts" / f"v{current['version']}-{lane}.json"
    )
    _json_write(verdict_path, result)
    entry.setdefault("reviews", {})[lane] = {
        **result,
        "path": _relative(verdict_path, root),
    }
    entry["next_action"] = (
        "Wait for and save the companion lane before editing or aggregating."
        if len(entry["reviews"]) < len(_REQUIRED_LANES)
        else "Aggregate both complete current-digest verdicts once."
    )
    _persist(root, status)
    return result


def _advance_after_close(status: dict[str, Any], slug: str) -> None:
    order = status["task_order"]
    index = order.index(slug)
    next_slug = next(
        (
            candidate
            for candidate in order[index + 1 :]
            if status["tasks"][candidate]["state"] not in _CLOSED_STATES
        ),
        None,
    )
    status["current_task"] = next_slug
    if next_slug:
        next_entry = status["tasks"][next_slug]
        next_entry["state"] = "current"
        next_entry["next_action"] = (
            "Create/finalize this task's docs and explicit manifest, then generate only "
            "this task's review bundle."
        )


def aggregate_reviews(tasks_root: Path | str, slug: str) -> dict[str, Any]:
    root = Path(tasks_root)
    status = _load_current_status(root)
    entry = _task_entry(status, slug)
    _ensure_current_task(status, slug)
    bundle = entry.get("current_bundle")
    if not bundle:
        raise WorkflowError("no current review bundle exists")
    _validate_bundle_integrity(root, slug, bundle)
    aggregate_path = (
        root / slug / "reviews" / "aggregates" / f"v{bundle['version']}.json"
    )
    if aggregate_path.is_file():
        existing = _json_read(aggregate_path)
        if existing.get("bundle_digest") != bundle.get("digest"):
            raise WorkflowError("existing aggregate does not match the current bundle")
        _validate_aggregate_evidence(
            root,
            slug,
            existing,
            status_reviews=entry.get("reviews") or {},
            require_live_docs=True,
        )
        return existing
    if entry["state"] != "reviewing":
        raise WorkflowError(f"task is not ready to aggregate in state {entry['state']}")
    missing = [lane for lane in _REQUIRED_LANES if lane not in entry.get("reviews", {})]
    if missing:
        raise WorkflowError(
            "cannot aggregate until both complete results are saved; missing: "
            + ", ".join(missing)
        )
    reviews = entry["reviews"]
    if any(
        reviews[lane]["bundle_digest"] != bundle["digest"] for lane in _REQUIRED_LANES
    ):
        raise WorkflowError("review verdict digest does not match the current bundle")
    for lane in _REQUIRED_LANES:
        review = reviews[lane]
        attestation = _validate_review_attestation(
            root,
            slug,
            lane=lane,
            bundle_digest=review["bundle_digest"],
            verdict=review["verdict"],
            reviewer_artifact=review["reviewer_artifact"],
            reviewer_mode=review["reviewer_mode"],
            model=review["model"],
            effort=review["effort"],
        )
        if attestation["reviewer_artifact_digest"] != review.get(
            "reviewer_artifact_digest"
        ):
            raise WorkflowError(f"saved {lane} reviewer artifact was modified")

    current_live_digest = _live_docs_digest(root / slug)
    if current_live_digest != bundle["live_docs_digest"]:
        raise WorkflowError(
            "live authoritative docs changed after bundle generation; current approval is stale"
        )

    blocking = [
        finding
        for lane in _REQUIRED_LANES
        for finding in reviews[lane].get("blockers", [])
    ]
    non_blocking = list(
        dict.fromkeys(
            finding
            for lane in _REQUIRED_LANES
            for finding in reviews[lane].get("non_blocking", [])
        )
    )
    changes_required = bool(blocking) or any(
        reviews[lane]["verdict"] == "CHANGES_REQUIRED" for lane in _REQUIRED_LANES
    )
    aggregate = {
        "schema_version": 1,
        "task": slug,
        "version": bundle["version"],
        "bundle_path": bundle["path"],
        "bundle_digest": bundle["digest"],
        "bundle_bytes": bundle["bytes"],
        "evidence_count": bundle["evidence_count"],
        "manifest": bundle["manifest"],
        "review_context": bundle.get("review_context", {"coverage": "latest-state"}),
        "live_docs_digest": current_live_digest,
        "lanes": {lane: reviews[lane] for lane in _REQUIRED_LANES},
        "blockers": blocking,
        "non_blocking": non_blocking,
        "state": "changes_required" if changes_required else "approved",
    }
    _validate_aggregate_evidence(
        root,
        slug,
        aggregate,
        status_reviews=reviews,
        require_live_docs=True,
    )
    _json_write(aggregate_path, aggregate)

    if changes_required:
        entry["state"] = "changes_required"
        entry["failed_rounds"] = entry.get("failed_rounds", 0) + 1
        entry["blocker"] = "; ".join(blocking) or "review changes required"
        entry["next_action"] = (
            "Consolidate all blocker-level findings into one amendment pass; optional "
            "non-blocking suggestions do not invalidate the bundle."
        )
    else:
        entry["state"] = "approved"
        entry["blocker"] = None
        entry["next_action"] = (
            "Task review closed; proceed only under implementation authorization."
        )
        _json_write(root / slug / "reviews" / "final-review.json", aggregate)
        _advance_after_close(status, slug)
    _persist(root, status)
    return aggregate


def mark_blocked(
    tasks_root: Path | str,
    slug: str,
    *,
    blocker: str,
    authorize_next: bool = False,
) -> dict[str, Any]:
    root = Path(tasks_root)
    status = _load_current_status(root)
    entry = _task_entry(status, slug)
    _ensure_current_task(status, slug)
    entry["blocker"] = blocker
    if authorize_next:
        entry["state"] = "blocked_authorized"
        entry["next_action"] = (
            "Durably blocked; revisit only after resolving the recorded gate."
        )
        _advance_after_close(status, slug)
    else:
        entry["state"] = "blocked"
        entry["next_action"] = (
            "Stop; obtain explicit user authorization before moving on."
        )
    _persist(root, status)
    return entry


def waive_current_task(
    tasks_root: Path | str, slug: str, *, reason: str
) -> dict[str, Any]:
    root = Path(tasks_root)
    status = _load_current_status(root)
    entry = _task_entry(status, slug)
    _ensure_current_task(status, slug)
    entry["state"] = "waived"
    entry["blocker"] = reason
    entry["next_action"] = (
        "Review explicitly waived; preserve this deviation in final reporting."
    )
    _advance_after_close(status, slug)
    _persist(root, status)
    return entry


def create_dependency_contract(
    tasks_root: Path | str,
    *,
    dependent_slug: str,
    prerequisite_slug: str,
    excerpts: Mapping[str, Any],
) -> Path:
    root = Path(tasks_root)
    status = _load_current_status(root)
    dependent = _task_entry(status, dependent_slug)
    prerequisite = _task_entry(status, prerequisite_slug)
    if prerequisite_slug not in dependent["direct_prerequisites"]:
        raise WorkflowError(
            f"{prerequisite_slug} is not a direct prerequisite of {dependent_slug}"
        )
    if prerequisite["state"] != "approved":
        raise WorkflowError(
            f"unapproved dependency must remain an implementation gate: {prerequisite_slug}"
        )
    final = _validate_approval_chain(root, prerequisite_slug, prerequisite)
    aggregate_path = (
        root
        / prerequisite_slug
        / "reviews"
        / "aggregates"
        / f"v{final['version']}.json"
    )
    aggregate_bytes = aggregate_path.read_bytes()
    if not isinstance(excerpts, Mapping) or not excerpts:
        raise WorkflowError("dependency contract excerpts must be a non-empty mapping")
    excerpt_bytes = json.dumps(
        excerpts, sort_keys=True, separators=(",", ":"), default=str
    ).encode()
    if len(excerpt_bytes) > _DEPENDENCY_CONTRACT_MAX_BYTES:
        raise WorkflowError(
            "dependency contract excerpts exceed the compact size limit"
        )

    payload = {
        "schema_version": 1,
        "dependent_task": dependent_slug,
        "prerequisite_task": prerequisite_slug,
        "approved_bundle_digest": final["bundle_digest"],
        "approved_live_docs_digest": final["live_docs_digest"],
        "approved_aggregate_digest": _sha256_bytes(aggregate_bytes),
        "aggregate_identity": _relative(aggregate_path, root.parent),
        "material_contract_digest": _sha256_bytes(excerpt_bytes),
        "excerpts": dict(excerpts),
    }
    path = root / dependent_slug / "dependency-contracts" / f"{prerequisite_slug}.json"
    _json_write(path, payload)
    return path


def _rollback_write(path: Path, content: bytes) -> None:
    """Best-effort low-level restore that is independent of the write injection seam."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.rollback-{uuid.uuid4().hex}")
    try:
        temporary.write_bytes(content)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _apply_metadata_transaction(root: Path, status: dict[str, Any]) -> None:
    """Persist generated metadata/status with rollback and no path mutation."""

    generated = [root / _STATUS_JSON, root / _STATUS_MD]
    generated.extend(
        path
        for slug in status["task_order"]
        for path in (root / slug / "task-metadata.json", root / slug / "handoff.md")
    )
    snapshots = {path: path.read_bytes() for path in generated if path.is_file()}
    try:
        for slug in status["task_order"]:
            entry = status["tasks"][slug]
            metadata = {
                key: entry[key]
                for key in (
                    "schema_version",
                    "stable_name",
                    "directory",
                    "implementation_order",
                    "source_issues",
                    "prerequisite_ids",
                    "direct_prerequisites",
                    "parallel_cohort",
                )
            }
            _json_write(root / slug / "task-metadata.json", metadata)
        _persist(root, status)
    except Exception:
        for path in generated:
            if path in snapshots:
                _rollback_write(path, snapshots[path])
            else:
                path.unlink(missing_ok=True)
        raise


def _migrated_status(
    status: Mapping[str, Any],
    layout: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    migrated = json.loads(json.dumps(status))
    migrated_tasks: dict[str, Any] = {}
    for old_slug in status["task_order"]:
        slug = old_slug
        entry = migrated["tasks"][old_slug]
        new_layout = layout[entry["stable_name"]]
        if slug != new_layout["directory"]:
            raise WorkflowError(
                "ordering migration requires stable task paths; directory renaming is not supported"
            )
        metadata_changed = any(
            entry.get(key) != new_layout[key]
            for key in (
                "implementation_order",
                "source_issues",
                "prerequisite_ids",
                "direct_prerequisites",
                "parallel_cohort",
            )
        )
        entry.update(
            {
                "directory": slug,
                "implementation_order": new_layout["implementation_order"],
                "source_issues": new_layout["source_issues"],
                "prerequisite_ids": new_layout["prerequisite_ids"],
                "direct_prerequisites": new_layout["direct_prerequisites"],
                "parallel_cohort": new_layout["parallel_cohort"],
            }
        )
        if metadata_changed and (
            entry.get("current_bundle")
            or entry.get("reviews")
            or entry["state"] == "approved"
        ):
            previous = entry.get("current_bundle") or {}
            invalidation = {
                "bundle_digest": previous.get("digest"),
                "bundle_path": previous.get("path"),
                "reason": "dependency metadata changed",
                "previous_state": entry["state"],
            }
            entry["review_invalidated_by_migration"] = invalidation
            if entry["state"] == "approved":
                entry["approval_invalidated_by_migration"] = invalidation
            entry["state"] = "pending"
            entry["current_bundle"] = None
            entry["reviews"] = {}
            entry["failed_rounds"] = 0
            entry["blocker"] = "Ordering migration requires fresh task-local review."
            entry["next_action"] = (
                "Regenerate this task's explicit manifest and review bundle."
            )
        migrated_tasks[slug] = entry

    migrated["tasks"] = migrated_tasks
    migrated["task_order"] = [
        item["directory"]
        for item in sorted(
            layout.values(),
            key=lambda item: (item["implementation_order"], item["directory"]),
        )
    ]
    current = next(
        (
            slug
            for slug in migrated["task_order"]
            if migrated["tasks"][slug]["state"] not in _CLOSED_STATES
        ),
        None,
    )
    migrated["current_task"] = current
    for slug, entry in migrated_tasks.items():
        if entry["state"] == "current" and slug != current:
            entry["state"] = "pending"
        if slug == current and entry["state"] == "pending":
            entry["state"] = "current"
    return migrated


def migrate_order(
    tasks_root: Path | str,
    definitions: Sequence[Mapping[str, Any]],
) -> dict[str, str]:
    """Update dependency order metadata without renaming stable task paths."""

    root = Path(tasks_root)
    status = _load_current_status(root)
    layout = derive_task_layout(definitions)
    old_by_name = {
        entry["stable_name"]: slug for slug, entry in status["tasks"].items()
    }
    if set(old_by_name) != set(layout):
        raise WorkflowError(
            "ordering migration definitions must match the existing conversion"
        )

    migrated = _migrated_status(status, layout)
    _apply_metadata_transaction(root, migrated)
    return {}


def adopt_legacy_conversion(
    tasks_root: Path | str,
    definitions: Sequence[Mapping[str, Any]],
    *,
    max_rounds: int = 2,
) -> dict[str, Any]:
    """Adopt stable legacy task directories without treating old reviews as current."""

    root = Path(tasks_root)
    if _status_path(root).exists():
        raise WorkflowError(
            "conversion status already exists; use migrate-order instead"
        )
    if max_rounds < 1:
        raise WorkflowError("max_rounds must be at least 1")
    layout = derive_task_layout(definitions)
    ordered = sorted(
        layout.values(),
        key=lambda item: (item["implementation_order"], item["directory"]),
    )
    entries: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(ordered):
        target_slug = item["name"]
        source = root / target_slug
        if not source.is_dir():
            raise WorkflowError(
                f"legacy adoption requires exactly one source directory for {item['name']}"
            )
        if source.is_symlink():
            raise WorkflowError(
                f"legacy adoption refuses symlink task directory: {source}"
            )
        for required in ("spec.md", "todo.md"):
            if not (source / required).is_file():
                raise WorkflowError(
                    f"legacy task {source.name} is missing required {required}"
                )
        historical = (
            [
                _relative(path, root.parent)
                for path in sorted((source / "reviews").rglob("*"))
                if path.is_file()
            ]
            if (source / "reviews").is_dir()
            else []
        )
        metadata = {
            "schema_version": 1,
            "stable_name": item["name"],
            "directory": target_slug,
            "implementation_order": item["implementation_order"],
            "source_issues": item["source_issues"],
            "prerequisite_ids": item["prerequisite_ids"],
            "direct_prerequisites": item["direct_prerequisites"],
            "parallel_cohort": item["parallel_cohort"],
        }
        entries[target_slug] = {
            **metadata,
            "state": "current" if index == 0 else "pending",
            "current_bundle": None,
            "reviews": {},
            "blocker": None,
            "next_action": (
                "Create an explicit manifest and generate this task-local bundle."
                if index == 0
                else "Wait for the current task to close."
            ),
            "failed_rounds": 0,
            "superseded_reviews": [],
            "legacy_review_artifacts": historical,
        }
    status = {
        "schema_version": 1,
        "max_rounds": max_rounds,
        "task_order": [item["directory"] for item in ordered],
        "current_task": ordered[0]["directory"] if ordered else None,
        "tasks": entries,
    }
    _apply_metadata_transaction(root, status)
    return status


def _load_json_argument(value: str) -> Any:
    path = Path(value)
    return _json_read(path) if path.is_file() else json.loads(value)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser(
        "init", help="validate graph and initialize task state"
    )
    init.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    init.add_argument("--definitions", required=True, help="JSON file or JSON value")
    init.add_argument("--max-rounds", type=int, default=2)

    adopt = subparsers.add_parser(
        "adopt-legacy", help="transactionally adopt stable legacy task directories"
    )
    adopt.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    adopt.add_argument("--definitions", required=True, help="JSON file or JSON value")
    adopt.add_argument("--max-rounds", type=int, default=2)

    bundle = subparsers.add_parser("bundle", help="generate one current task bundle")
    bundle.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    bundle.add_argument("--slug", required=True)
    bundle.add_argument("--manifest", type=Path, required=True)

    review = subparsers.add_parser("record-review", help="save one hash-bound verdict")
    review.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    review.add_argument("--slug", required=True)
    review.add_argument("--lane", choices=_REQUIRED_LANES, required=True)
    review.add_argument("--bundle-digest", required=True)
    review.add_argument(
        "--verdict", choices=("APPROVED", "CHANGES_REQUIRED"), required=True
    )
    review.add_argument("--reviewer-artifact", type=Path, required=True)
    review.add_argument("--reviewer-mode", required=True)
    review.add_argument("--model", required=True)
    review.add_argument("--effort", required=True)
    review.add_argument("--blocker", action="append", default=[])
    review.add_argument("--non-blocking", action="append", default=[])

    aggregate = subparsers.add_parser(
        "aggregate", help="aggregate both current verdicts"
    )
    aggregate.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    aggregate.add_argument("--slug", required=True)

    status = subparsers.add_parser(
        "status", help="rehash approvals and refresh the conversion ledger"
    )
    status.add_argument("--tasks-root", type=Path, default=Path("tasks"))

    block = subparsers.add_parser("block", help="durably block the current task")
    block.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    block.add_argument("--slug", required=True)
    block.add_argument("--reason", required=True)
    block.add_argument("--authorize-next", action="store_true")

    waiver = subparsers.add_parser("waive", help="record an explicit review waiver")
    waiver.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    waiver.add_argument("--slug", required=True)
    waiver.add_argument("--reason", required=True)

    contract = subparsers.add_parser(
        "dependency-contract", help="freeze approved dependency excerpts"
    )
    contract.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    contract.add_argument("--dependent", required=True)
    contract.add_argument("--prerequisite", required=True)
    contract.add_argument("--excerpts", required=True, help="JSON file or JSON value")

    migrate = subparsers.add_parser(
        "migrate-order", help="update corrected dependency-wave metadata"
    )
    migrate.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    migrate.add_argument("--definitions", required=True, help="JSON file or JSON value")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "init":
            result = initialize_conversion(
                args.tasks_root,
                _load_json_argument(args.definitions),
                max_rounds=args.max_rounds,
            )
        elif args.command == "adopt-legacy":
            result = adopt_legacy_conversion(
                args.tasks_root,
                _load_json_argument(args.definitions),
                max_rounds=args.max_rounds,
            )
        elif args.command == "bundle":
            bundle = build_review_bundle(args.tasks_root, args.slug, args.manifest)
            result = bundle._asdict()
            result["path"] = str(result["path"])
        elif args.command == "record-review":
            result = record_review(
                args.tasks_root,
                args.slug,
                lane=args.lane,
                bundle_digest=args.bundle_digest,
                verdict=args.verdict,
                reviewer_artifact=args.reviewer_artifact,
                reviewer_mode=args.reviewer_mode,
                model=args.model,
                effort=args.effort,
                blockers=args.blocker,
                non_blocking=args.non_blocking,
            )
        elif args.command == "aggregate":
            result = aggregate_reviews(args.tasks_root, args.slug)
        elif args.command == "status":
            result = refresh_status(args.tasks_root)
        elif args.command == "block":
            result = mark_blocked(
                args.tasks_root,
                args.slug,
                blocker=args.reason,
                authorize_next=args.authorize_next,
            )
        elif args.command == "waive":
            result = waive_current_task(args.tasks_root, args.slug, reason=args.reason)
        elif args.command == "dependency-contract":
            path = create_dependency_contract(
                args.tasks_root,
                dependent_slug=args.dependent,
                prerequisite_slug=args.prerequisite,
                excerpts=_load_json_argument(args.excerpts),
            )
            result = {"path": str(path)}
        elif args.command == "migrate-order":
            result = migrate_order(
                args.tasks_root, _load_json_argument(args.definitions)
            )
        else:  # pragma: no cover - argparse enforces this
            raise WorkflowError(f"unsupported command: {args.command}")
    except (WorkflowError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
