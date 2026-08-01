import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/tokyo_children_annual_actual_linkage.json"
SCHEMA_PATH = ROOT / "schemas/tokyo_children_annual_actual_linkage.schema.json"
TARGET_PATH = ROOT / "data/entities/policy/tokyo_policy_target_catalog_children.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def series_values(records: dict[int, dict], number: int) -> list[tuple[str, str]]:
    return [
        (item["actual_value_text"], item["actual_period"])
        for item in records[number]["linked_series"]
    ]


def test_tokyo_children_linkage_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(CATALOG_PATH))) == []


def test_all_eight_target_groups_are_covered_once():
    linkage = load(CATALOG_PATH)
    target_catalog = load(TARGET_PATH)
    records = linkage["records"]

    assert linkage["target_group_count"] == 8
    assert linkage["series_count"] == 9
    assert [record["target_group_number"] for record in records] == list(range(1, 9))
    assert [record["target_id"] for record in records] == [
        item["id"] for item in target_catalog["items"]
    ]
    assert len({record["id"] for record in records}) == 8


def test_six_groups_and_seven_series_are_linked_conservatively():
    linkage = load(CATALOG_PATH)
    records = linkage["records"]
    statuses = Counter(record["linkage_status"] for record in records)
    linked_series_count = sum(len(record["linked_series"]) for record in records)

    assert statuses == {"linked": 6, "partial": 2}
    assert linked_series_count == 7
    assert linkage["summary"] == {
        "linked_target_group_count": 6,
        "linked_series_count": 7,
        "partial_target_group_count": 2,
        "not_linked_target_group_count": 0,
    }
    assert linkage["evaluation_status"] == "not_assessed"
    assert all(record["evaluation_status"] == "not_assessed" for record in records)


def test_linked_values_and_periods_match_the_same_2050_tokyo_strategy_series():
    records = {
        record["target_group_number"]: record
        for record in load(CATALOG_PATH)["records"]
    }

    assert series_values(records, 1) == [("64.3", "2025年")]
    assert series_values(records, 2) == [("44.6", "2025年")]
    assert series_values(records, 3) == [("55.0", "2025年")]
    assert series_values(records, 5) == [("17.5", "2023年")]
    assert series_values(records, 6) == [
        ("64.2", "2022年"),
        ("33.9", "2022年"),
    ]
    assert series_values(records, 8) == [("14", "2024年")]
    assert all(
        "達成・未達は判定しない" in records[number]["boundary"]
        for number in (1, 2, 3, 5, 6, 8)
    )


def test_two_document_conflicts_remain_partial_without_overwrite():
    records = {
        record["target_group_number"]: record
        for record in load(CATALOG_PATH)["records"]
    }

    assert records[4]["partial_reason"] == "reporting_period_conflict"
    assert records[4]["conflict"] == {
        "source_value": "全公立小・中・高校で実施",
        "source_period": "2023年度実績",
        "catalog_period": "2024年度",
    }
    assert records[7]["partial_reason"] == "actual_value_and_period_conflict"
    assert records[7]["conflict"] == {
        "source_value": "44",
        "source_period": "2023",
        "catalog_value": "47",
        "catalog_period": "2024年",
    }
    for number in (4, 7):
        assert records[number]["linked_series"] == []
        assert "上書きせず接続を保留" in records[number]["boundary"]


def test_target_and_review_documents_are_same_strategy_but_separate_versions():
    linkage = load(CATALOG_PATH)

    assert linkage["target_source_version"] == (
        "2050東京戦略 政策目標一覧（令和8年1月）"
    )
    assert linkage["review_source_version"] == (
        "2050東京戦略 政策レビュー（2025年8月）"
    )
    assert "2050tokyo-seisakumokuhyo2026" in linkage["target_source_url"]
    assert "policy-review_2025" in linkage["review_source_url"]
