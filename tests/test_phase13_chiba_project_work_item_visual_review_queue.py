from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/catalog/chiba_current_project_work_item_visual_review_queue.json"
MANIFEST = ROOT / "data/catalog/chiba_current_project_work_item_review_manifest.json"
BUILDER = ROOT / "scripts/build_chiba_work_item_visual_review_queue.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def projects_by_id(paths: list[str]):
    projects = {}
    for relative_path in paths:
        payload = load(ROOT / relative_path)
        for project in payload["projects"]:
            review_id = project["review_id"]
            assert review_id not in projects
            projects[review_id] = project
    return projects


def test_visual_review_queue_reconciles_all_10_pending_projects():
    queue = load(QUEUE)
    manifest = load(MANIFEST)
    queued_ids = [
        review_id
        for batch in queue["batches"]
        for review_id in batch["pending_review_ids"]
    ]
    manifest_ids = manifest["work_item_structuring"]["pending_review_ids"]

    assert queue["status"] == "ready_for_visual_confirmation"
    assert len(queued_ids) == len(set(queued_ids)) == 10
    assert set(queued_ids) == set(manifest_ids)
    assert [batch["pending_count"] for batch in queue["batches"]] == [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        10,
    ]
    assert sum(batch["pending_count"] for batch in queue["batches"]) == 10


def test_every_queued_id_resolves_to_pending_raw_evidence():
    queue = load(QUEUE)
    for batch in queue["batches"]:
        projects = projects_by_id(batch["review_paths"])
        for review_id in batch["pending_review_ids"]:
            project = projects[review_id]
            assert project["parse_status"] == "pending_visual_column_confirmation"
            assert project["raw_table_text"].strip()
            assert project["work_items"] == []


def test_visual_queue_contains_no_structured_project():
    queue = load(QUEUE)
    queued_ids = {
        review_id
        for batch in queue["batches"]
        for review_id in batch["pending_review_ids"]
    }
    manifest = load(MANIFEST)
    all_projects = projects_by_id(manifest["review_paths"])
    structured_ids = {
        review_id
        for review_id, project in all_projects.items()
        if project.get("parse_status") != "pending_visual_column_confirmation"
    }

    assert queued_ids.isdisjoint(structured_ids)
    assert len(all_projects) == 189
    assert len(structured_ids) == 179


def test_visual_queue_preserves_completed_source_capture_totals():
    queue = load(QUEUE)
    assert queue["source_capture"] == {
        "project_universe": 189,
        "projects_source_captured": 189,
        "projects_structured": 179,
        "structured_work_items": 385,
        "projects_pending_visual_column_confirmation": 10,
        "projects_not_yet_source_captured": 0,
    }


def test_visual_queue_is_linked_from_work_item_manifest():
    manifest = load(MANIFEST)

    assert manifest["visual_review_queue_path"] == (
        "data/catalog/chiba_current_project_work_item_visual_review_queue.json"
    )
    assert (ROOT / manifest["visual_review_queue_path"]).is_file()
    assert "visual review queue" in manifest["quality_boundary"]


def test_visual_queue_builder_is_deterministic_and_generated_file_is_current():
    result = subprocess.run(
        [sys.executable, str(BUILDER), "--check"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_next_visual_batch_starts_with_field08_official_order():
    queue = load(QUEUE)

    assert queue["execution_order"] == "official_field_and_project_order"
    assert all(batch["pending_count"] == 0 for batch in queue["batches"][:7])
    assert queue["next_batch"] == {
        "field_code": "8",
        "field_name": "地域経済",
        "pending_review_ids": [
            "chiba-f08-p004",
            "chiba-f08-p006",
            "chiba-f08-p008",
            "chiba-f08-p009",
            "chiba-f08-p010",
            "chiba-f08-p011",
            "chiba-f08-p013",
            "chiba-f08-p014",
            "chiba-f08-p021",
            "chiba-f08-p022",
        ],
    }
    assert "推定しない" in queue["resolution_rule"]
    assert "10事業" in queue["quality_boundary"]
