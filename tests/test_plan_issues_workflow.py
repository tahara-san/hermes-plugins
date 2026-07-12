from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "skills"
    / "software-development"
    / "planning-workflows"
    / "scripts"
    / "plan_issues_workflow.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("plan_issues_workflow", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def definitions(*items):
    return [
        {
            "name": name,
            "source_issues": [f"tasks/out-of-scope-issues/low/{name}.md"],
            "prerequisites": list(prerequisites),
        }
        for name, prerequisites in items
    ]


def seed_task_docs(tasks_root: Path, *slugs: str) -> None:
    for slug in slugs:
        task = tasks_root / slug
        task.mkdir(parents=True, exist_ok=True)
        (task / "spec.md").write_text(f"# {slug}\n")
        (task / "todo.md").write_text("# TODO\n")


def explicit_manifest(task_dir: Path, *relative_paths: str) -> Path:
    payload = {
        "evidence": [
            {"path": path, "reason": f"required evidence for {path}"}
            for path in relative_paths
        ]
    }
    path = task_dir / "evidence-manifest.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return path


def record_lane(
    module,
    tasks_root: Path,
    slug: str,
    *,
    lane: str,
    bundle_digest: str,
    verdict: str,
    blockers=(),
    non_blocking=(),
):
    attestation = module._REVIEW_ATTESTATIONS[lane]
    artifact = (
        tasks_root
        / slug
        / "reviews"
        / "raw"
        / f"{lane}-{bundle_digest}-{verdict.lower()}.txt"
    )
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        "\n".join(
            (
                "BEGIN_REVIEW_RESULT",
                f"BUNDLE_SHA256: {bundle_digest}",
                f"REVIEWER_MODE: {attestation['reviewer_mode']}",
                f"MODEL: {attestation['model']}",
                f"EFFORT: {attestation['effort']}",
                f"VERDICT: {'PASS' if verdict == 'APPROVED' else verdict}",
                "END_REVIEW_RESULT",
            )
        )
        + "\n"
    )
    return module.record_review(
        tasks_root,
        slug,
        lane=lane,
        bundle_digest=bundle_digest,
        verdict=verdict,
        reviewer_artifact=artifact,
        reviewer_mode=attestation["reviewer_mode"],
        model=attestation["model"],
        effort=attestation["effort"],
        blockers=blockers,
        non_blocking=non_blocking,
    )


def approve_current(module, tasks_root: Path, slug: str, manifest: Path):
    bundle = module.build_review_bundle(tasks_root, slug, manifest)
    for lane in ("codex", "claude"):
        record_lane(
            module,
            tasks_root,
            slug,
            lane=lane,
            bundle_digest=bundle.digest,
            verdict="APPROVED",
        )
    return module.aggregate_reviews(tasks_root, slug)


def test_dependency_graph_assigns_parallel_waves_and_later_dependents():
    module = load_module()

    layout = module.derive_task_layout(
        definitions(
            ("api-contract", ()),
            ("copy-cleanup", ()),
            ("client-integration", ("api-contract",)),
            ("e2e-rollout", ("client-integration", "copy-cleanup")),
        )
    )

    assert layout["api-contract"]["directory"] == "api-contract"
    assert layout["copy-cleanup"]["directory"] == "copy-cleanup"
    assert layout["client-integration"]["directory"] == "client-integration"
    assert layout["e2e-rollout"]["directory"] == "e2e-rollout"
    assert layout["api-contract"]["parallel_cohort"] == [
        "api-contract",
        "copy-cleanup",
    ]
    assert layout["e2e-rollout"]["direct_prerequisites"] == [
        "client-integration",
        "copy-cleanup",
    ]


@pytest.mark.parametrize("name", ["Bad_Name", "two--hyphens", "-leading", "trailing-"])
def test_task_names_must_be_descriptive_kebab_case(name: str):
    module = load_module()

    with pytest.raises(module.WorkflowError, match="kebab-case"):
        module.derive_task_layout(definitions((name, ())))


def test_cycle_fails_before_any_task_directory_is_created(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"

    with pytest.raises(module.WorkflowError, match=r"dependency cycle.*alpha.*beta"):
        module.initialize_conversion(
            tasks_root,
            definitions(("alpha", ("beta",)), ("beta", ("alpha",))),
        )

    assert not tasks_root.exists() or not list(tasks_root.iterdir())


def test_initialization_writes_metadata_status_ledger_and_fresh_handoffs(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"

    module.initialize_conversion(
        tasks_root,
        definitions(
            ("api-contract", ()),
            ("copy-cleanup", ()),
            ("client-integration", ("api-contract",)),
        ),
    )

    metadata = json.loads(
        (tasks_root / "client-integration" / "task-metadata.json").read_text()
    )
    assert metadata["implementation_order"] == 2
    assert metadata["direct_prerequisites"] == ["api-contract"]
    assert metadata["parallel_cohort"] == ["client-integration"]

    ledger = (tasks_root / "plan-issues-status.md").read_text()
    assert "| Task | Source issues | Prerequisites | Parallel cohort | Bundle" in ledger
    assert "api-contract" in ledger
    assert "client-integration" in ledger
    assert "current" in ledger

    handoff = (tasks_root / "api-contract" / "handoff.md").read_text()
    for phrase in (
        "Authoritative files",
        "Implementation order",
        "Direct prerequisites",
        "Current bundle",
        "Codex lane",
        "Claude lane",
        "Exact next action",
        "Planning authorization",
        "Dependency gates",
        "Unrelated dirty work",
        "Out-of-scope",
        "Required final report",
    ):
        assert phrase in handoff


def test_review_bundle_requires_one_current_slug_and_explicit_existing_files(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ()), ("beta", ())))
    seed_task_docs(tasks_root, "alpha", "beta")

    alpha = tasks_root / "alpha"
    manifest = explicit_manifest(alpha, "spec.md", "missing.py")
    with pytest.raises(module.WorkflowError, match="manifest path does not exist"):
        module.build_review_bundle(tasks_root, "alpha", manifest)

    explicit_manifest(alpha, "spec.md", ".")
    with pytest.raises(module.WorkflowError, match="directories are not allowed"):
        module.build_review_bundle(tasks_root, "alpha", manifest)

    explicit_manifest(alpha, "spec.md", "../beta/spec.md")
    with pytest.raises(module.WorkflowError, match="full neighboring plan"):
        module.build_review_bundle(tasks_root, "alpha", manifest)

    explicit_manifest(alpha, "spec.md", "todo.md")
    with pytest.raises(module.WorkflowError, match="exactly one target slug"):
        module.build_review_bundle(tasks_root, None, manifest)


def test_bundle_versions_are_task_local_and_next_task_waits_for_current_close(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ()), ("beta", ())))
    seed_task_docs(tasks_root, "alpha", "beta")
    alpha_manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")
    beta_manifest = explicit_manifest(tasks_root / "beta", "spec.md", "todo.md")

    first = module.build_review_bundle(tasks_root, "alpha", alpha_manifest)
    record_lane(
        module,
        tasks_root,
        "alpha",
        lane="codex",
        bundle_digest=first.digest,
        verdict="CHANGES_REQUIRED",
        blockers=["missing rollback gate"],
    )
    record_lane(
        module,
        tasks_root,
        "alpha",
        lane="claude",
        bundle_digest=first.digest,
        verdict="APPROVED",
        non_blocking=["optional wording polish"],
    )
    aggregate = module.aggregate_reviews(tasks_root, "alpha")
    assert aggregate["state"] == "changes_required"

    with pytest.raises(module.WorkflowError, match="current task.*alpha"):
        module.build_review_bundle(tasks_root, "beta", beta_manifest)

    (tasks_root / "alpha" / "spec.md").write_text("# alpha\n\nFixed.\n")
    second = module.build_review_bundle(tasks_root, "alpha", alpha_manifest)
    assert second.version == 2
    for lane in ("codex", "claude"):
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane=lane,
            bundle_digest=second.digest,
            verdict="APPROVED",
        )
    assert module.aggregate_reviews(tasks_root, "alpha")["state"] == "approved"

    beta = module.build_review_bundle(tasks_root, "beta", beta_manifest)
    assert beta.version == 1
    assert "alpha" not in beta.path.read_text()


def test_nonblocking_feedback_does_not_invalidate_matching_approval(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")
    bundle = module.build_review_bundle(tasks_root, "alpha", manifest)

    record_lane(
        module,
        tasks_root,
        "alpha",
        lane="codex",
        bundle_digest=bundle.digest,
        verdict="APPROVED",
        non_blocking=["consider an extra test during implementation"],
    )
    record_lane(
        module,
        tasks_root,
        "alpha",
        lane="claude",
        bundle_digest=bundle.digest,
        verdict="APPROVED",
    )

    aggregate = module.aggregate_reviews(tasks_root, "alpha")
    assert aggregate["state"] == "approved"
    final = json.loads(
        (tasks_root / "alpha" / "reviews" / "final-review.json").read_text()
    )
    assert final["bundle_digest"] == bundle.digest
    assert final["live_docs_digest"]
    assert final["non_blocking"] == ["consider an extra test during implementation"]


def test_delayed_old_bundle_review_is_archived_and_cannot_change_current_state(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")

    old = module.build_review_bundle(tasks_root, "alpha", manifest)
    for lane in ("codex", "claude"):
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane=lane,
            bundle_digest=old.digest,
            verdict="CHANGES_REQUIRED",
            blockers=["old blocker"],
        )
    module.aggregate_reviews(tasks_root, "alpha")
    (tasks_root / "alpha" / "spec.md").write_text("# alpha\n\nFixed.\n")
    current = module.build_review_bundle(tasks_root, "alpha", manifest)

    stale = record_lane(
        module,
        tasks_root,
        "alpha",
        lane="codex",
        bundle_digest=old.digest,
        verdict="CHANGES_REQUIRED",
        blockers=["delayed old finding"],
    )
    assert stale["superseded"] is True
    assert list((tasks_root / "alpha" / "reviews" / "superseded").glob("*.json"))

    for lane in ("codex", "claude"):
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane=lane,
            bundle_digest=current.digest,
            verdict="APPROVED",
        )
    assert module.aggregate_reviews(tasks_root, "alpha")["state"] == "approved"


def test_reround_cap_stops_after_fourth_failed_review_and_requires_user_decision(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    status = module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    assert status["max_rounds"] == 4
    seed_task_docs(tasks_root, "alpha")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")

    for expected_version in (1, 2, 3, 4):
        bundle = module.build_review_bundle(tasks_root, "alpha", manifest)
        assert bundle.version == expected_version
        for lane in ("codex", "claude"):
            record_lane(
                module,
                tasks_root,
                "alpha",
                lane=lane,
                bundle_digest=bundle.digest,
                verdict="CHANGES_REQUIRED",
                blockers=[f"round {expected_version} blocker"],
            )
        assert module.aggregate_reviews(tasks_root, "alpha")["state"] == "changes_required"
        if expected_version < 4:
            (tasks_root / "alpha" / "spec.md").write_text(
                f"# alpha\n\nRound-{expected_version} blockers fixed.\n"
            )

    status = json.loads((tasks_root / "plan-issues-status.json").read_text())
    entry = status["tasks"]["alpha"]
    assert entry["failed_rounds"] == 3
    assert "ask the user to decide" in entry["next_action"]

    with pytest.raises(module.WorkflowError, match="review round cap.*user decision"):
        module.build_review_bundle(tasks_root, "alpha", manifest)


def test_dependency_contract_is_compact_frozen_and_approval_bound(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(
        tasks_root,
        definitions(("api", ()), ("client", ("api",))),
    )
    seed_task_docs(tasks_root, "api", "client")
    api_manifest = explicit_manifest(tasks_root / "api", "spec.md", "todo.md")
    approved = approve_current(module, tasks_root, "api", api_manifest)

    contract = module.create_dependency_contract(
        tasks_root,
        dependent_slug="client",
        prerequisite_slug="api",
        excerpts={"endpoint": "GET /v1/items", "invariant": "IDs are stable"},
    )
    payload = json.loads(contract.read_text())
    assert payload["approved_bundle_digest"] == approved["bundle_digest"]
    assert payload["excerpts"] == {
        "endpoint": "GET /v1/items",
        "invariant": "IDs are stable",
    }
    assert "# api" not in contract.read_text()


def test_order_correction_updates_metadata_without_renaming_stable_directories(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(
        tasks_root,
        definitions(("api", ()), ("client", ("api",))),
    )
    seed_task_docs(tasks_root, "api", "client")
    (tasks_root / "coverage.md").write_text(
        "See tasks/api/spec.md and tasks/client/todo.md.\n"
    )
    (tasks_root / "api" / "notes.md").write_text("Depends on tasks/client.\n")

    mapping = module.migrate_order(
        tasks_root,
        definitions(("client", ()), ("api", ("client",))),
    )

    assert mapping == {}
    assert (tasks_root / "api").is_dir()
    assert (tasks_root / "client").is_dir()
    assert "tasks/api/spec.md" in (tasks_root / "coverage.md").read_text()
    assert "tasks/client/todo.md" in (tasks_root / "coverage.md").read_text()
    assert "tasks/client" in (tasks_root / "api" / "notes.md").read_text()
    status = json.loads((tasks_root / "plan-issues-status.json").read_text())
    assert status["tasks"]["client"]["implementation_order"] == 1
    assert status["tasks"]["api"]["implementation_order"] == 2


def test_bundle_requires_authoritative_docs_and_allows_unrelated_reviews_paths(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    alpha = tasks_root / "alpha"
    (alpha / "spec.md").write_text("# alpha\n")
    manifest = explicit_manifest(alpha, "spec.md")

    with pytest.raises(module.WorkflowError, match="spec.md and todo.md"):
        module.build_review_bundle(tasks_root, "alpha", manifest)

    (alpha / "todo.md").write_text("# TODO\n")
    source = tmp_path / "src" / "reviews" / "check.py"
    source.parent.mkdir(parents=True)
    source.write_text("CHECK = True\n")
    manifest = explicit_manifest(
        alpha, "spec.md", "todo.md", "../../src/reviews/check.py"
    )
    assert module.build_review_bundle(tasks_root, "alpha", manifest).evidence_count == 3


def test_bundle_rejects_symlinked_authoritative_docs(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    alpha = tasks_root / "alpha"
    (alpha / "spec.md").write_text("# alpha\n")
    external_todo = tmp_path / "todo.md"
    external_todo.write_text("# TODO\n")
    (alpha / "todo.md").symlink_to(external_todo)
    manifest = explicit_manifest(alpha, "spec.md", "todo.md")

    with pytest.raises(module.WorkflowError, match="cannot be symlinks"):
        module.build_review_bundle(tasks_root, "alpha", manifest)


def test_record_review_rejects_malformed_bundle_digest(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")
    module.build_review_bundle(tasks_root, "alpha", manifest)

    for malformed in ("a" * 63, "A" * 64, "z" * 64, "../../escape"):
        with pytest.raises(module.WorkflowError, match="64 lowercase hex"):
            record_lane(
                module,
                tasks_root,
                "alpha",
                lane="codex",
                bundle_digest=malformed,
                verdict="APPROVED",
            )


def test_review_transitions_are_idempotent_and_require_real_amendment(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")

    with pytest.raises(module.WorkflowError, match="current review bundle"):
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane="codex",
            bundle_digest="a" * 64,
            verdict="APPROVED",
        )

    first = module.build_review_bundle(tasks_root, "alpha", manifest)
    for lane in ("codex", "claude"):
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane=lane,
            bundle_digest=first.digest,
            verdict="CHANGES_REQUIRED",
            blockers=["fix the contract"],
        )

    with pytest.raises(module.WorkflowError, match="aggregate.*before.*regenerating"):
        module.build_review_bundle(tasks_root, "alpha", manifest)

    first_aggregate = module.aggregate_reviews(tasks_root, "alpha")
    repeated = module.aggregate_reviews(tasks_root, "alpha")
    status = json.loads((tasks_root / "plan-issues-status.json").read_text())
    assert repeated == first_aggregate
    assert status["tasks"]["alpha"]["failed_rounds"] == 1

    with pytest.raises(module.WorkflowError, match="authoritative docs must change"):
        module.build_review_bundle(tasks_root, "alpha", manifest)

    (tasks_root / "alpha" / "spec.md").write_text("# alpha\n\nFixed.\n")
    second = module.build_review_bundle(tasks_root, "alpha", manifest)
    first_result = record_lane(
        module,
        tasks_root,
        "alpha",
        lane="codex",
        bundle_digest=second.digest,
        verdict="APPROVED",
    )
    assert (
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane="codex",
            bundle_digest=second.digest,
            verdict="APPROVED",
        )
        == first_result
    )
    with pytest.raises(module.WorkflowError, match="conflicting duplicate verdict"):
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane="codex",
            bundle_digest=second.digest,
            verdict="CHANGES_REQUIRED",
            blockers=["late conflict"],
        )


def test_blocked_authorized_dependency_becomes_explicit_gate(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(
        tasks_root, definitions(("api", ()), ("client", ("api",)))
    )
    seed_task_docs(tasks_root, "api", "client")
    module.mark_blocked(
        tasks_root,
        "api",
        blocker="external API decision pending",
        authorize_next=True,
    )
    manifest = explicit_manifest(tasks_root / "client", "spec.md", "todo.md")

    bundle = module.build_review_bundle(tasks_root, "client", manifest)
    sidecar = json.loads(bundle.path.with_suffix(".json").read_text())
    assert sidecar["dependency_gates"] == [
        {
            "prerequisite": "api",
            "state": "blocked_authorized",
            "blocker": "external API decision pending",
        }
    ]


def test_approved_dependency_requires_compact_aggregate_bound_contract(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(
        tasks_root, definitions(("api", ()), ("client", ("api",)))
    )
    seed_task_docs(tasks_root, "api", "client")
    approved = approve_current(
        module,
        tasks_root,
        "api",
        explicit_manifest(tasks_root / "api", "spec.md", "todo.md"),
    )
    client = tasks_root / "client"
    manifest = explicit_manifest(client, "spec.md", "todo.md")
    with pytest.raises(module.WorkflowError, match="dependency contract.*api"):
        module.build_review_bundle(tasks_root, "client", manifest)

    with pytest.raises(module.WorkflowError, match="compact size limit"):
        module.create_dependency_contract(
            tasks_root,
            dependent_slug="client",
            prerequisite_slug="api",
            excerpts={"oversized": "x" * 20_000},
        )

    contract = module.create_dependency_contract(
        tasks_root,
        dependent_slug="client",
        prerequisite_slug="api",
        excerpts={"endpoint": "GET /v1/items", "invariant": "IDs are stable"},
    )
    payload = json.loads(contract.read_text())
    assert payload["approved_aggregate_digest"]
    assert payload["approved_bundle_digest"] == approved["bundle_digest"]

    manifest = explicit_manifest(
        client, "spec.md", "todo.md", "dependency-contracts/api.json"
    )
    bundle = module.build_review_bundle(tasks_root, "client", manifest)
    sidecar = json.loads(bundle.path.with_suffix(".json").read_text())
    assert sidecar["dependency_contracts"] == [
        "tasks/client/dependency-contracts/api.json"
    ]


def test_order_migration_never_rewrites_stable_task_paths(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(
        tasks_root, definitions(("auth", ()), ("auth-cache", ()))
    )
    seed_task_docs(tasks_root, "auth", "auth-cache")
    coverage = tasks_root / "coverage.md"
    coverage.write_text(
        "tasks/auth/spec.md and tasks/auth-cache/spec.md and auth-cache\n"
    )

    module.migrate_order(
        tasks_root, definitions(("auth-cache", ()), ("auth", ("auth-cache",)))
    )

    content = coverage.read_text()
    assert "tasks/auth/spec.md" in content
    assert "tasks/auth-cache/spec.md" in content
    assert content == "tasks/auth/spec.md and tasks/auth-cache/spec.md and auth-cache\n"


def test_order_migration_rolls_back_metadata_on_write_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(
        tasks_root, definitions(("api", ()), ("client", ("api",)))
    )
    seed_task_docs(tasks_root, "api", "client")
    original_status = (tasks_root / "plan-issues-status.json").read_bytes()
    original_api_metadata = (tasks_root / "api" / "task-metadata.json").read_bytes()
    real_atomic_write = module._atomic_write_bytes

    def fail_status(path: Path, content: bytes):
        if path == tasks_root / "plan-issues-status.json":
            raise OSError("injected migration write failure")
        return real_atomic_write(path, content)

    monkeypatch.setattr(module, "_atomic_write_bytes", fail_status)
    with pytest.raises(OSError, match="injected migration write failure"):
        module.migrate_order(
            tasks_root,
            definitions(("client", ()), ("api", ("client",))),
        )

    assert (tasks_root / "api").is_dir()
    assert (tasks_root / "client").is_dir()
    assert (tasks_root / "plan-issues-status.json").read_bytes() == original_status
    assert (
        tasks_root / "api" / "task-metadata.json"
    ).read_bytes() == original_api_metadata


def test_order_migration_invalidates_approved_identity_but_preserves_history(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("api", ()), ("client", ())))
    seed_task_docs(tasks_root, "api", "client")
    approve_current(
        module,
        tasks_root,
        "api",
        explicit_manifest(tasks_root / "api", "spec.md", "todo.md"),
    )

    module.migrate_order(tasks_root, definitions(("client", ()), ("api", ("client",))))
    status = json.loads((tasks_root / "plan-issues-status.json").read_text())
    api = status["tasks"]["api"]
    assert api["state"] == "pending"
    assert api["current_bundle"] is None
    assert api["reviews"] == {}
    assert api["approval_invalidated_by_migration"]
    assert (tasks_root / "api" / "reviews" / "final-review.json").is_file()


def test_adopt_legacy_conversion_keeps_stable_paths_and_review_history(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    seed_task_docs(tasks_root, "api", "client")
    legacy_review = tasks_root / "api" / "reviews" / "legacy-v7.json"
    legacy_review.parent.mkdir(parents=True)
    legacy_review.write_text('{"historical": true}\n')
    coverage = tasks_root / "coverage.md"
    coverage.write_text("tasks/api/spec.md -> tasks/client/todo.md\n")

    status = module.adopt_legacy_conversion(
        tasks_root, definitions(("api", ()), ("client", ("api",)))
    )

    assert status["current_task"] == "api"
    assert (tasks_root / "api" / "reviews" / "legacy-v7.json").is_file()
    assert (tasks_root / "client" / "spec.md").is_file()
    assert coverage.read_text() == ("tasks/api/spec.md -> tasks/client/todo.md\n")
    assert status["tasks"]["api"]["legacy_review_artifacts"] == [
        "tasks/api/reviews/legacy-v7.json"
    ]


def test_bundle_integrity_and_approval_status_are_rehashed(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")
    bundle = module.build_review_bundle(tasks_root, "alpha", manifest)
    original = bundle.path.read_bytes()
    bundle.path.write_text("tampered\n")

    with pytest.raises(module.WorkflowError, match="bundle was modified"):
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane="codex",
            bundle_digest=bundle.digest,
            verdict="APPROVED",
        )

    bundle.path.write_bytes(original)
    for lane in ("codex", "claude"):
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane=lane,
            bundle_digest=bundle.digest,
            verdict="APPROVED",
        )
    bundle.path.unlink()
    with pytest.raises(module.WorkflowError, match="bundle is missing"):
        module.aggregate_reviews(tasks_root, "alpha")


def test_status_refresh_invalidates_post_approval_document_edits(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    approve_current(
        module,
        tasks_root,
        "alpha",
        explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md"),
    )
    (tasks_root / "alpha" / "spec.md").write_text("# alpha\n\nChanged.\n")

    status = module.refresh_status(tasks_root)

    entry = status["tasks"]["alpha"]
    assert entry["state"] == "approval_stale"
    assert status["current_task"] == "alpha"
    assert (
        "approval_stale (current)" in (tasks_root / "plan-issues-status.md").read_text()
    )


def test_plan_named_paths_must_exist_and_appear_in_manifest(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    source = tmp_path / "src" / "feature.py"
    source.parent.mkdir()
    source.write_text("ENABLED = True\n")
    spec = tasks_root / "alpha" / "spec.md"
    spec.write_text("# alpha\n\nChange `src/feature.py`.\n")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")

    with pytest.raises(
        module.WorkflowError, match="omitted plan-named paths.*feature.py"
    ):
        module.build_review_bundle(tasks_root, "alpha", manifest)

    spec.write_text("# alpha\n\nChange `src/missing.py`.\n")
    with pytest.raises(
        module.WorkflowError, match="plan-named path is missing.*missing.py"
    ):
        module.build_review_bundle(tasks_root, "alpha", manifest)


def test_review_recording_requires_pinned_artifact_attestation(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")
    bundle = module.build_review_bundle(tasks_root, "alpha", manifest)
    artifact = tasks_root / "alpha" / "reviews" / "raw" / "codex.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        f"BEGIN_REVIEW_RESULT\nBUNDLE_SHA256: {bundle.digest}\n"
        "REVIEWER_MODE: interactive-codex-tui\nMODEL: gpt-5.6-sol\n"
        "EFFORT: xhigh\nVERDICT: PASS\nEND_REVIEW_RESULT\n"
    )

    with pytest.raises(module.WorkflowError, match="requires model=gpt-5.6-sol"):
        module.record_review(
            tasks_root,
            "alpha",
            lane="codex",
            bundle_digest=bundle.digest,
            verdict="APPROVED",
            reviewer_artifact=artifact,
            reviewer_mode="interactive-codex-tui",
            model="gpt-5.5",
            effort="xhigh",
        )


def test_review_attestation_rejects_prompt_echo_without_one_exact_result_block(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    bundle = module.build_review_bundle(
        tasks_root,
        "alpha",
        explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md"),
    )
    attestation = module._REVIEW_ATTESTATIONS["codex"]
    artifact = tasks_root / "alpha" / "reviews" / "raw" / "prompt-only.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        f"Return BUNDLE_SHA256: {bundle.digest}\n"
        f"REVIEWER_MODE: {attestation['reviewer_mode']}\n"
        f"MODEL: {attestation['model']}\nEFFORT: {attestation['effort']}\n"
        "VERDICT: PASS | CHANGES_REQUIRED\n"
    )

    with pytest.raises(module.WorkflowError, match="exactly one review result block"):
        module.record_review(
            tasks_root,
            "alpha",
            lane="codex",
            bundle_digest=bundle.digest,
            verdict="APPROVED",
            reviewer_artifact=artifact,
            **attestation,
        )


def test_review_attestation_rejects_conflicting_result_blocks(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    bundle = module.build_review_bundle(
        tasks_root,
        "alpha",
        explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md"),
    )
    attestation = module._REVIEW_ATTESTATIONS["codex"]
    artifact = tasks_root / "alpha" / "reviews" / "raw" / "conflict.txt"
    artifact.parent.mkdir(parents=True)

    def result(verdict: str) -> str:
        return (
            f"BEGIN_REVIEW_RESULT\nBUNDLE_SHA256: {bundle.digest}\n"
            f"REVIEWER_MODE: {attestation['reviewer_mode']}\n"
            f"MODEL: {attestation['model']}\nEFFORT: {attestation['effort']}\n"
            f"VERDICT: {verdict}\nEND_REVIEW_RESULT\n"
        )

    artifact.write_text(result("PASS") + result("CHANGES_REQUIRED"))
    with pytest.raises(module.WorkflowError, match="exactly one review result block"):
        module.record_review(
            tasks_root,
            "alpha",
            lane="codex",
            bundle_digest=bundle.digest,
            verdict="APPROVED",
            reviewer_artifact=artifact,
            **attestation,
        )


@pytest.mark.parametrize("tamper_target", ["raw", "aggregate", "malformed"])
def test_status_refresh_revalidates_the_complete_approval_chain(
    tmp_path: Path, tamper_target: str
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    approved = approve_current(
        module,
        tasks_root,
        "alpha",
        explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md"),
    )
    if tamper_target == "raw":
        raw_path = tmp_path / approved["lanes"]["codex"]["reviewer_artifact"]
        raw_path.write_text(raw_path.read_text() + "tampered\n")
    else:
        aggregate_path = tasks_root / "alpha" / "reviews" / "aggregates" / "v1.json"
        aggregate = json.loads(aggregate_path.read_text())
        if tamper_target == "aggregate":
            aggregate["state"] = "changes_required"
        else:
            del aggregate["lanes"]
        aggregate_path.write_text(json.dumps(aggregate, indent=2) + "\n")

    status = module.refresh_status(tasks_root)
    assert status["tasks"]["alpha"]["state"] == "approval_stale"


def test_existing_aggregate_revalidates_saved_raw_artifacts(tmp_path: Path):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")
    bundle = module.build_review_bundle(tasks_root, "alpha", manifest)
    for lane in ("codex", "claude"):
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane=lane,
            bundle_digest=bundle.digest,
            verdict="CHANGES_REQUIRED" if lane == "codex" else "APPROVED",
            blockers=["fix contract"] if lane == "codex" else (),
        )
    aggregate = module.aggregate_reviews(tasks_root, "alpha")
    raw_path = tmp_path / aggregate["lanes"]["codex"]["reviewer_artifact"]
    raw_path.write_text(raw_path.read_text() + "tampered\n")

    with pytest.raises(module.WorkflowError, match="reviewer artifact"):
        module.aggregate_reviews(tasks_root, "alpha")


def test_dependency_contract_material_identity_isolated_from_unrelated_prose(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(
        tasks_root, definitions(("api", ()), ("client", ("api",)))
    )
    seed_task_docs(tasks_root, "api", "client")
    approve_current(
        module,
        tasks_root,
        "api",
        explicit_manifest(tasks_root / "api", "spec.md", "todo.md"),
    )
    contract = module.create_dependency_contract(
        tasks_root,
        dependent_slug="client",
        prerequisite_slug="api",
        excerpts={"endpoint": "GET /v1/items"},
    )
    client_manifest = explicit_manifest(
        tasks_root / "client",
        "spec.md",
        "todo.md",
        "dependency-contracts/api.json",
    )
    approve_current(module, tasks_root, "client", client_manifest)

    (tasks_root / "api" / "spec.md").write_text("# api\n\nUnrelated prose.\n")
    status = module.refresh_status(tasks_root)
    assert status["tasks"]["api"]["state"] == "approval_stale"
    assert status["tasks"]["client"]["state"] == "approved"

    payload = json.loads(contract.read_text())
    payload["excerpts"]["endpoint"] = "GET /v2/items"
    contract.write_text(json.dumps(payload, indent=2) + "\n")
    status = module.refresh_status(tasks_root)
    assert status["tasks"]["client"]["state"] == "approval_stale"


def test_frozen_contract_allows_current_dependent_bundle_after_prerequisite_prose_edit(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(
        tasks_root, definitions(("api", ()), ("client", ("api",)))
    )
    seed_task_docs(tasks_root, "api", "client")
    approve_current(
        module,
        tasks_root,
        "api",
        explicit_manifest(tasks_root / "api", "spec.md", "todo.md"),
    )
    module.create_dependency_contract(
        tasks_root,
        dependent_slug="client",
        prerequisite_slug="api",
        excerpts={"endpoint": "GET /v1/items"},
    )
    (tasks_root / "api" / "spec.md").write_text("# api\n\nUnrelated prose.\n")
    status = module.refresh_status(tasks_root)
    assert status["tasks"]["api"]["state"] == "approval_stale"
    assert status["current_task"] == "client"

    manifest = explicit_manifest(
        tasks_root / "client",
        "spec.md",
        "todo.md",
        "dependency-contracts/api.json",
    )
    bundle = module.build_review_bundle(tasks_root, "client", manifest)
    assert bundle.version == 1


def test_reround_bundle_contains_current_state_and_compact_delta_not_review_history(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    module.initialize_conversion(tasks_root, definitions(("alpha", ())))
    seed_task_docs(tasks_root, "alpha")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")
    first = module.build_review_bundle(tasks_root, "alpha", manifest)
    for lane in ("codex", "claude"):
        record_lane(
            module,
            tasks_root,
            "alpha",
            lane=lane,
            bundle_digest=first.digest,
            verdict="CHANGES_REQUIRED",
            blockers=["make rollback explicit"],
        )
    module.aggregate_reviews(tasks_root, "alpha")
    (tasks_root / "alpha" / "spec.md").write_text("# alpha\n\nRollback is explicit.\n")

    second = module.build_review_bundle(tasks_root, "alpha", manifest)
    content = second.path.read_text()
    sidecar = json.loads(second.path.with_suffix(".json").read_text())
    assert "## Current-only reround delta" in content
    assert first.digest in content
    assert "make rollback explicit" in content
    assert sidecar["review_context"]["coverage"] == "latest-state-plus-delta"
    assert sidecar["review_context"]["previous_bundle_digest"] == first.digest
    assert sidecar["review_context"]["changed_evidence"] == ["tasks/alpha/spec.md"]
    assert "reviews/raw/" not in content
    assert "BEGIN_REVIEW_RESULT" not in content


def test_migration_updates_metadata_without_rename_and_invalidates_active_review(
    tmp_path: Path,
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    initial = definitions(("alpha", ()))
    module.initialize_conversion(tasks_root, initial)
    seed_task_docs(tasks_root, "alpha")
    manifest = explicit_manifest(tasks_root / "alpha", "spec.md", "todo.md")
    bundle = module.build_review_bundle(tasks_root, "alpha", manifest)
    changed = [
        {
            "name": "alpha",
            "source_issues": ["tasks/out-of-scope-issues/high/alpha.md"],
            "prerequisites": [],
        }
    ]

    assert module.migrate_order(tasks_root, changed) == {}
    status = json.loads((tasks_root / "plan-issues-status.json").read_text())
    entry = status["tasks"]["alpha"]
    assert entry["source_issues"] == ["tasks/out-of-scope-issues/high/alpha.md"]
    assert entry["current_bundle"] is None
    assert entry["reviews"] == {}
    assert entry["review_invalidated_by_migration"]["bundle_digest"] == bundle.digest
    assert status["current_task"] == "alpha"


def test_legacy_adoption_rollback_removes_generated_files_from_unrenamed_tasks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    module = load_module()
    tasks_root = tmp_path / "tasks"
    seed_task_docs(tasks_root, "api", "client")
    real_atomic_write = module._atomic_write_bytes

    def fail_status(path: Path, content: bytes):
        if path == tasks_root / "plan-issues-status.json":
            raise OSError("injected adoption status failure")
        return real_atomic_write(path, content)

    monkeypatch.setattr(module, "_atomic_write_bytes", fail_status)
    with pytest.raises(OSError, match="injected adoption status failure"):
        module.adopt_legacy_conversion(
            tasks_root, definitions(("api", ()), ("client", ("api",)))
        )

    assert (tasks_root / "api").is_dir()
    assert (tasks_root / "client").is_dir()
    for task in (tasks_root / "api", tasks_root / "client"):
        assert not (task / "task-metadata.json").exists()
        assert not (task / "handoff.md").exists()
    assert not (tasks_root / "plan-issues-status.json").exists()
    assert not (tasks_root / "plan-issues-status.md").exists()


def test_plan_issues_policy_requires_task_local_serial_review_and_guard_rules():
    paths = [
        ROOT / "skills/software-development/plan-issues/SKILL.md",
        ROOT
        / "skills/software-development/planning-workflows/references/plan-issues/plan-issues.md",
        ROOT
        / "skills/software-development/planning-workflows/references/plan-issues-priority-grouped-conversion.md",
    ]
    for path in paths:
        content = path.read_text().lower()
        assert "one task" in content
        assert "current task" in content
        assert "exactly one target slug" in content
        assert "dependency graph" in content
        assert "cycle" in content
        assert "status ledger" in content
        assert "dependabot" in content
        assert "tasks/out-of-scope-issues/<priority>" in content

    canonical = paths[1].read_text().lower()
    assert "do not generate or dispatch the next task" in canonical
    assert "full neighboring plan" in canonical
    assert "user-visible checkpoint" in canonical
    assert "delayed" in canonical and "superseded" in canonical
