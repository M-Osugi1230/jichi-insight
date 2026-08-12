from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/catalog/sendai_survey_2025_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_survey_manifest_marks_summary_and_priority_scope_complete():
    manifest = load(MANIFEST_PATH)
    scope = manifest["reviewed_scope"]

    assert manifest["phase"] == 13
    assert manifest["official_code"] == "041009"
    assert manifest["status"] == "summary_and_priority_review_complete"
    assert manifest["parent_phase13_manifest_path"] == (
        "data/catalog/sendai_phase13_review_manifest.json"
    )
    assert (ROOT / manifest["summary_score_registry_path"]).is_file()
    assert (ROOT / manifest["summary_score_evidence_path"]).is_file()
    assert (ROOT / manifest["priority_policy_registry_path"]).is_file()
    assert (ROOT / manifest["priority_policy_evidence_path"]).is_file()

    assert scope["survey_methodology"] is True
    assert scope["current_state_summary_scores"] == 8
    assert scope["policy_evaluation_summary_scores"] == 26
    assert scope["summary_score_item_total"] == 34
    assert scope["priority_policy_multiple_response"] == 26
    assert scope["priority_policy_response_mode"] == "multiple_response_up_to_10"
    assert scope["response_category_distributions"] is False
    assert scope["attribute_cross_tabs"] is False
    assert scope["livability_and_attachment_items"] is False
    assert scope["foreign_resident_items"] is False
    assert scope["free_text"] is False


def test_sendai_survey_manifest_keeps_perception_and_priority_separate_from_administration():
    manifest = load(MANIFEST_PATH)
    boundary = manifest["quality_boundary"]
    actions = manifest["next_actions"]

    assert "administrative performance" in boundary
    assert "policy achievement" in boundary
    assert "causal attribution" in boundary
    assert "Jichi Insight ranking" in boundary
    assert any("単純集計CSV" in action for action in actions)
    assert any("クロス集計CSV" in action for action in actions)
    assert any("自動結合せず" in action for action in actions)
