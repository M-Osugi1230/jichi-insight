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
    # Aligned to "reviewed" when Sapporo's Phase 13 package was integrated
    # into the Phase 15 framework (owner decision, 2026-11-19, Issue #695);
    # the Phase 13 completion record had declared this package
    # reviewed_complete on 2026-08-18.
    assert review["review_status"] == "reviewed"
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
    # The amount is held in the Phase 15 value/unit fields (converted from
    # the Phase 13 amount_yen field at the Phase 15 integration, #695).
    assert record["value"] == 1_785_400_000_000
    assert record["unit"] == "yen"
    assert "単年度予算" in record["review_note"]
    assert "決算額" in record["review_note"]


def test_sapporo_plan_review_keeps_achievement_out_of_scope():
    review = load()
    boundary = review["quality_boundary"].lower()
    assert "does not infer policy achievement" in boundary
    assert "cross-city comparability" in boundary
