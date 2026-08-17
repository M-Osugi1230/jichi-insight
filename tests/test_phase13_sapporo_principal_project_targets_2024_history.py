from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "data/catalog/sapporo_principal_project_target_2024_review.json"
EVIDENCE = (
    ROOT / "data/evidence/sapporo_principal_project_target_2024_review_evidence.json"
)
CHANGE = (
    ROOT
    / "data/catalog/sapporo_principal_project_target_status_change_2024_2025.json"
)
READINESS = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_2024_historical_aggregate_is_exact_403_partition():
    history = load(HISTORY)
    universe = history["official_target_universe"]

    assert history["reporting_year"] == 2024
    assert history["measurement_fiscal_year"] == 2023
    assert universe["principal_project_target_count"] == 403
    assert universe["already_achieved_count"] == 9
    assert universe["achievement_expected_count"] == 392
    assert universe["achievement_difficult_expected_count"] == 2
    assert universe["official_expected_or_achieved_count"] == 401
    assert universe["official_expected_or_achieved_ratio_percent"] == 99.5
    assert 9 + 392 + 2 == 403


def test_2024_field_aggregates_reconcile_to_official_total():
    fields = load(HISTORY)["field_aggregates"]

    assert len(fields) == 8
    assert sum(row["target_count"] for row in fields) == 403
    assert sum(row["already_achieved_count"] for row in fields) == 9
    assert sum(row["achievement_expected_count"] for row in fields) == 392
    assert sum(row["achievement_difficult_expected_count"] for row in fields) == 2
    assert [row["target_count"] for row in fields] == [73, 62, 27, 43, 60, 35, 47, 56]


def test_2024_source_goal_numbering_anomaly_is_preserved_and_normalized():
    history = load(HISTORY)
    reconciliation = history["goal_numbering_reconciliation"]
    rows = history["source_report_basic_goal_rows"]

    assert len(rows) == 20
    assert reconciliation["source_goal_numbers_whose_labels_map_to_different_current_ids"] == [
        2,
        3,
        4,
        5,
        11,
        12,
        13,
        14,
        16,
        17,
    ]
    assert reconciliation["normalized_pair_swaps"] == [
        "2<->3",
        "4<->5",
        "11<->12",
        "13<->14",
        "16<->17",
    ]

    by_source = {row["source_goal_number"]: row for row in rows}
    assert by_source[2]["normalized_current_goal_id"] == 3
    assert by_source[3]["normalized_current_goal_id"] == 2
    assert by_source[11]["normalized_current_goal_id"] == 12
    assert by_source[12]["normalized_current_goal_id"] == 11


def test_2024_normalized_goal_target_counts_match_403_universe():
    normalized = load(HISTORY)["goal_numbering_reconciliation"][
        "normalized_current_target_counts"
    ]

    expected = {
        "1": 22,
        "2": 30,
        "3": 21,
        "4": 11,
        "5": 51,
        "6": 8,
        "7": 19,
        "8": 21,
        "9": 22,
        "10": 31,
        "11": 15,
        "12": 14,
        "13": 6,
        "14": 15,
        "15": 14,
        "16": 31,
        "17": 16,
        "18": 20,
        "19": 21,
        "20": 15,
    }
    assert normalized == expected
    assert sum(normalized.values()) == 403


def test_2024_report_reviews_only_two_explicit_difficult_projects():
    history = load(HISTORY)
    records = history["reviewed_individual_target_records"]

    assert len(records) == 2
    assert {record["project_id"] for record in records} == {
        "sapporo_ict_strategy_promotion",
        "school_facility_longevity_repair",
    }
    assert all(
        record["official_status"] == "achievement_difficult_expected"
        for record in records
    )
    assert history["summary"]["individual_target_records_reviewed"] == 2


def test_2024_evidence_does_not_increment_current_target_gate():
    evidence = load(EVIDENCE)
    readiness = load(READINESS)
    gate = next(
        item
        for item in readiness["blocking_gates"]
        if item["id"] == "principal-project-target-records"
    )

    assert evidence["publication_boundary"]["historical_layer_only"] is True
    assert evidence["publication_boundary"]["current_2025_gate_increment"] == 0
    assert gate["reviewed_scope"] == 8
    assert gate["remaining_scope"] == 395


def test_cross_year_comparison_preserves_two_continued_difficult_records():
    change = load(CHANGE)
    records = {record["project_id"]: record for record in change["records"]}

    assert change["summary"]["cross_year_individual_records"] == 2
    assert change["summary"]["continued_difficult_status_count"] == 2
    assert change["summary"]["forecast_decline_count"] == 2

    ict = records["sapporo_ict_strategy_promotion"]
    assert ict["report_2024"]["forecast_2027"] == 21
    assert ict["report_2025"]["forecast_2027"] == 16
    assert ict["forecast_change"] == -5

    longevity = records["school_facility_longevity_repair"]
    assert longevity["report_2024"]["forecast_2027"] == 20
    assert longevity["report_2025"]["forecast_2027"] == 15
    assert longevity["forecast_change"] == -5
