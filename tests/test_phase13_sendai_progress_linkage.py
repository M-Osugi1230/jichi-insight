from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINKAGE_PATH = ROOT / "data/catalog/sendai_phase13_progress_linkage.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_phase13_progress_linkage_resolves_history_completion_and_children():
    linkage = load(LINKAGE_PATH)
    history_path = ROOT / linkage["canonical_parent_manifest_path"]
    completion_path = ROOT / linkage["completion_manifest_path"]

    assert linkage["phase"] == 13
    assert linkage["official_code"] == "041009"
    assert linkage["status"] == "reviewed_complete"
    assert history_path.is_file()
    assert completion_path.is_file()
    history = load(history_path)
    completion = load(completion_path)
    assert history["status"] == "review_in_progress"
    assert completion["status"] == "reviewed_complete"
    assert completion["review_package"]["review_history_manifest_path"] == (
        linkage["canonical_parent_manifest_path"]
    )

    survey_layers = [
        layer
        for layer in linkage["linked_layers"]
        if "review_manifest_path" in layer
    ]
    assert len(survey_layers) == 2
    for layer in survey_layers:
        child = load(ROOT / layer["review_manifest_path"])
        assert child["parent_phase13_manifest_path"] == (
            linkage["canonical_parent_manifest_path"]
        )
        assert (ROOT / layer["registry_path"]).is_file()
        assert (ROOT / layer["evidence_path"]).is_file()


def test_sendai_phase13_progress_linkage_derives_108_project_core_records():
    linkage = load(LINKAGE_PATH)
    project_files = sorted(
        (ROOT / "data/catalog").glob("sendai_challenge_project_reviews_part*.json")
    )
    records = [record for path in project_files for record in load(path)["records"]]
    layer = next(
        item
        for item in linkage["linked_layers"]
        if item["id"] == "challenge-project-core-review"
    )

    assert len(project_files) == 36
    assert len(records) == 108
    assert len({record["id"] for record in records}) == 108
    assert layer["reviewed_record_count"] == len(records)
    assert layer["source_record_count"] == 108
    assert layer["complete_at_declared_depth"] is True


def test_sendai_phase13_progress_linkage_derives_60_reviewed_survey_items():
    linkage = load(LINKAGE_PATH)
    summary_scores = load(
        ROOT / "data/catalog/sendai_survey_2025_summary_scores.json"
    )
    priority = load(ROOT / "data/catalog/sendai_survey_2025_priority_policy.json")
    current_items = summary_scores["current_state_items"]
    policy_items = summary_scores["policy_evaluation_items"]
    priority_items = priority["items"]

    assert len(current_items) == 8
    assert len(policy_items) == 26
    assert len(priority_items) == 26
    assert linkage["summary"]["citizen_survey_summary_items_reviewed"] == 34
    assert linkage["summary"]["citizen_survey_priority_items_reviewed"] == 26
    assert linkage["summary"]["survey_reviewed_item_total"] == 60
    assert len(current_items) + len(policy_items) + len(priority_items) == 60


def test_sendai_phase13_completion_keeps_layers_non_equivalent_and_depth_deferred():
    linkage = load(LINKAGE_PATH)
    roles = {layer["role"] for layer in linkage["linked_layers"]}
    boundary = linkage["quality_boundary"]

    assert roles == {
        "municipality_source_reported_project_self_evaluation",
        "citizen_perception_summary_scores",
        "citizen_stated_future_priority_multiple_response",
    }
    assert linkage["summary"]["municipality_phase13_complete"] is True
    assert linkage["remaining_gates"] == []
    assert len(linkage["deferred_depth"]) == 5
    assert "not collapsed" in boundary
    assert "declared Phase 13 v1 review package is complete" in boundary
    assert "deferred depth" in boundary
    assert "policy achievement" in boundary
    assert "causal attribution" in boundary
    assert "cross-city comparability" in boundary
