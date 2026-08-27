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


def test_visual_review_queue_is_complete_with_zero_pending_projects():
    queue = load(QUEUE)
    manifest = load(MANIFEST)
    queued_ids = [
        review_id for batch in queue["batches"] for review_id in batch["pending_review_ids"]
    ]

    assert queue["status"] == "complete"
    assert queued_ids == []
    assert manifest["work_item_structuring"]["pending_review_ids"] == []
    assert [batch["pending_count"] for batch in queue["batches"]] == [0] * 8
    assert queue["next_batch"] is None


def test_no_project_remains_pending_raw_evidence():
    manifest = load(MANIFEST)
    projects = projects_by_id(manifest["review_paths"])
    assert len(projects) == 189
    assert all(
        project.get("parse_status") != "pending_visual_column_confirmation"
        for project in projects.values()
    )


def test_all_projects_are_structured_when_visual_queue_is_complete():
    queue = load(QUEUE)
    manifest = load(MANIFEST)
    all_projects = projects_by_id(manifest["review_paths"])
    assert queue["status"] == "complete"
    assert len(all_projects) == 189
    assert all(project["work_items"] for project in all_projects.values())


def test_visual_queue_preserves_completed_source_capture_totals():
    queue = load(QUEUE)
    assert queue["source_capture"] == {
        "project_universe": 189,
        "projects_source_captured": 189,
        "projects_structured": 189,
        "structured_work_items": 406,
        "projects_pending_visual_column_confirmation": 0,
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


def test_completed_visual_queue_has_no_next_batch():
    queue = load(QUEUE)

    assert queue["execution_order"] == "official_field_and_project_order"
    assert all(batch["pending_count"] == 0 for batch in queue["batches"])
    assert queue["next_batch"] is None
    assert queue["status"] == "complete"
    assert "pending visual confirmationは0" in queue["quality_boundary"]
