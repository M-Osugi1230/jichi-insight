from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "data/reviewed/sapporo-city/plan_review.json"


def load():
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def test_sapporo_plan_review_preserves_evidence_roles():
    review = load()
    assert review["official_code"] == "011002"
    assert review["review_status"] == "review_in_progress"
    roles = {record["evidence_role"] for record in review["records"]}
    assert roles == {"current_plan_identity", "implementation_layer"}


def test_sapporo_action_plan_uses_final_599_project_count():
    review = load()
    record = next(
        item
        for item in review["records"]
        if item["id"] == "sapporo-action-plan-2023-project-count"
    )
    assert record["value"] == 599
    assert "確定版概要" in record["review_note"]


def test_sapporo_planned_cost_is_not_presented_as_fiscal_actual():
    review = load()
    record = next(
        item
        for item in review["records"]
        if item["id"] == "sapporo-action-plan-2023-planned-cost"
    )
    assert record["amount_yen"] == 1_785_400_000_000
    assert "単年度予算" in record["review_note"]
    assert "決算額" in record["review_note"]


def test_sapporo_plan_review_keeps_achievement_out_of_scope():
    review = load()
    boundary = review["quality_boundary"].lower()
    assert "does not infer policy achievement" in boundary
    assert "cross-city comparability" in boundary
