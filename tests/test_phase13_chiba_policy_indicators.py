from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/reviewed/chiba-city/current_policy_indicators.json"
EVIDENCE = ROOT / "data/evidence/chiba_current_policy_indicators_evidence.json"
MANIFEST = ROOT / "data/catalog/chiba_phase13_policy_review_manifest.json"
PLAN_REVIEW = ROOT / "data/reviewed/chiba-city/plan_review.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fields_by_code(payload):
    return {row["field_code"]: row for row in payload["fields"]}


def quantitative_rows(payload):
    return [
        indicator for field in payload["fields"] for indicator in field["quantitative_indicators"]
    ]


def qualitative_rows(payload):
    return [
        factor for field in payload["fields"] for factor in field["qualitative_constituent_factors"]
    ]


def test_chiba_policy_indicator_field_counts_reconcile_to_40():
    payload = load(CATALOG)
    fields = fields_by_code(payload)
    counts = [len(fields[str(code)]["quantitative_indicators"]) for code in range(1, 9)]

    assert counts == [7, 3, 2, 14, 2, 3, 5, 4]
    assert sum(counts) == payload["quantitative_indicator_count"] == 40


def test_chiba_policy_indicator_ids_are_unique():
    indicators = quantitative_rows(load(CATALOG))
    ids = [row["id"] for row in indicators]

    assert len(ids) == len(set(ids)) == 40
    assert {row["indicator_type"] for row in indicators} == {"KGI", "KPI"}
    assert all(row["value_status"] == "reviewed" for row in indicators)
    assert all(row["source_location"].startswith("PDF p.") for row in indicators)


def test_chiba_overall_goal_preserves_operator_and_period():
    goal = load(CATALOG)["overall_goal_indicator"]

    assert goal["current"] == {"period": "2025年", "value": 74.3}
    assert goal["target"] == {"period": "2032年度末", "operator": "at_least", "value": 80.0}
    assert goal["source_location"] == "PDF p.137"


def test_chiba_nonstandard_indicator_periods_are_preserved():
    rows = {row["id"]: row for row in quantitative_rows(load(CATALOG))}

    assert rows["chiba-pi-f01-001"]["current"]["period"] == "2021年度"
    assert rows["chiba-pi-f01-001"]["target"]["period"] == "2025年度"
    assert rows["chiba-pi-f01-002"]["target"]["period"] == "2027年度"
    assert rows["chiba-pi-f08-001"]["current"]["period"] == "2020年度"
    assert rows["chiba-pi-f08-004"]["target"]["period"] == "2027年度"


def test_chiba_health_life_expectancy_stays_composite_and_text_target():
    health = {row["id"]: row for row in quantitative_rows(load(CATALOG))}["chiba-pi-f03-001"]

    assert health["current"]["value_status"] == "composite"
    assert health["current"]["components"]["健康寿命"] == {"男性": 80.04, "女性": 84.78}
    assert health["current"]["components"]["平均寿命"] == {"男性": 81.45, "女性": 88.1}
    assert health["target"]["value_status"] == "text"
    assert health["target"]["value_text"] == "平均寿命の増加分を上回る健康寿命の増加"


def test_chiba_education_multi_series_do_not_inflate_indicator_rows():
    field04 = fields_by_code(load(CATALOG))["4"]
    rows = {row["id"]: row for row in field04["quantitative_indicators"]}

    assert len(field04["quantitative_indicators"]) == 14
    assert len(rows["chiba-pi-f04-007"]["series"]) == 2
    assert len(rows["chiba-pi-f04-008"]["series"]) == 2
    assert len(rows["chiba-pi-f04-009"]["series"]) == 4
    assert len(rows["chiba-pi-f04-012"]["series"]) == 4


def test_chiba_qualitative_factors_are_not_fabricated_as_numeric_targets():
    payload = load(CATALOG)
    factors = qualitative_rows(payload)
    primary = [row for row in factors if row["primary"]]
    reposts = [row for row in factors if not row["primary"]]

    assert len(primary) == 6
    assert len(reposts) == 1
    assert payload["qualitative_constituent_factor_primary_count"] == 6
    assert payload["qualitative_constituent_factor_repost_occurrence_count"] == 1
    assert all(row["value_status"] == "qualitative_no_numeric_target" for row in factors)
    assert all("target" not in row for row in factors)


def test_chiba_field03_qualitative_repost_links_to_field05_primary():
    factors = {row["id"]: row for row in qualitative_rows(load(CATALOG))}
    repost = factors["chiba-qf-f03-r001"]
    primary = factors[repost["repost_of"]]

    assert repost["factor_name"] == primary["factor_name"]
    assert primary["id"] == "chiba-qf-f05-001"
    assert primary["primary"] is True


def test_chiba_policy_indicator_evidence_reconciles_catalog():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == "reviewed_complete"
    assert evidence["reconciliation"] == {
        "overall_goal_indicator_count": 1,
        "quantitative_indicator_count": 40,
        "quantitative_field_counts": [7, 3, 2, 14, 2, 3, 5, 4],
        "qualitative_constituent_factor_primary_count": 6,
        "qualitative_constituent_factor_repost_occurrence_count": 1,
    }
    assert len(evidence["fields"]) == 8


def test_chiba_manifest_links_completed_policy_indicator_layer():
    manifest = load(MANIFEST)
    fact = next(
        row for row in manifest["reviewed_facts"] if row["id"] == "chiba-current-policy-indicators"
    )

    assert manifest["policy_indicator_review_path"] == (
        "data/reviewed/chiba-city/current_policy_indicators.json"
    )
    assert fact["quantitative_indicator_count"] == 40
    assert fact["qualitative_constituent_factor_primary_count"] == 6
    assert fact["review_status"] == "reviewed_complete_policy_indicator_identity_and_values"


def test_chiba_plan_review_reflects_complete_project_work_item_structuring():
    review = load(PLAN_REVIEW)
    work_items = next(
        row for row in review["records"] if row["id"] == "chiba-current-project-work-items"
    )

    assert review["review_status"] == "review_in_progress_current_project_work_items_complete"
    assert work_items["source_captured_project_count"] == 189
    assert work_items["structured_project_count"] == 189
    assert work_items["pending_visual_column_confirmation_project_count"] == 0
    assert work_items["structured_work_item_count"] == 406
    assert work_items["decision"] == "accepted_complete_source_capture_and_structuring"
    assert "versioned linkage" in review["next_action"]
    assert "406 work items" in review["quality_boundary"]
