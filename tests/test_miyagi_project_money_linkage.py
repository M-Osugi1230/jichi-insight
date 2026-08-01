import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog"
INDEX_PATH = CATALOG / "miyagi_project_money_linkage.json"
INDEX_SCHEMA_PATH = ROOT / "schemas/miyagi_project_money_linkage.schema.json"
PART_SCHEMA_PATH = ROOT / "schemas/miyagi_project_money_linkage_part.schema.json"
HIERARCHY_PATH = ROOT / "data/entities/policy/miyagi_policy_hierarchy.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def linkage_records():
    index = load(INDEX_PATH)
    parts = [load(CATALOG / filename) for filename in index["part_files"]]
    records = [record for part in parts for record in part["records"]]
    return index, parts, records


def hierarchy_ids():
    hierarchy = load(HIERARCHY_PATH)
    policy_ids = set()
    measure_ids = set()
    for direction in hierarchy["directions"]:
        for policy in direction["policies"]:
            policy_ids.add(policy["id"])
            measure_ids.update(measure["id"] for measure in policy["measures"])
    return policy_ids, measure_ids


def test_miyagi_money_index_and_parts_match_schema():
    index_validator = Draft202012Validator(
        load(INDEX_SCHEMA_PATH), format_checker=FormatChecker()
    )
    part_validator = Draft202012Validator(
        load(PART_SCHEMA_PATH), format_checker=FormatChecker()
    )
    index, parts, _ = linkage_records()

    assert list(index_validator.iter_errors(index)) == []
    assert len(parts) == 4
    assert all(list(part_validator.iter_errors(part)) == [] for part in parts)
    assert [
        (part["record_number_from"], part["record_number_to"]) for part in parts
    ] == [(1, 160), (161, 320), (321, 480), (481, 627)]


def test_all_627_budget_projects_are_covered_once():
    index, _, records = linkage_records()
    record_ids = [record["id"] for record in records]

    assert index["budget_record_count"] == 627
    assert index["settlement_record_count"] == 494
    assert index["record_count"] == 627
    assert len(record_ids) == len(set(record_ids)) == 627
    assert record_ids == [
        f"miyagi-project-money-linkage-{number:04d}"
        for number in range(1, 628)
    ]


def test_reviewed_classification_and_summary_are_consistent():
    index, _, records = linkage_records()
    statuses = Counter(record["linkage_status"] for record in records)
    bases = Counter(record["match_basis"] for record in records)

    assert statuses == {"linked": 238, "partial": 26, "not_linked": 363}
    assert bases == {
        "exact_name_measure_department_office": 238,
        "same_measure_organization_changed": 2,
        "exact_name_measure_changed_or_relisted": 24,
        "exact_name_not_found_in_fy2024_settlement": 363,
    }
    assert index["summary"] == {
        "linked_record_count": 238,
        "partial_record_count": 26,
        "not_linked_record_count": 363,
        "match_basis_counts": dict(sorted(bases.items())),
    }
    assert index["evaluation_status"] == "not_assessed"


def test_policy_and_measure_ids_reuse_the_reviewed_miyagi_hierarchy():
    _, _, records = linkage_records()
    policy_ids, measure_ids = hierarchy_ids()

    assert len(policy_ids) == 8
    assert len(measure_ids) == 18
    assert {record["policy_id"] for record in records} == policy_ids
    assert {record["measure_id"] for record in records} == measure_ids


def test_linked_partial_and_unresolved_money_boundaries_remain_distinct():
    _, _, records = linkage_records()

    for record in records:
        assert record["budget_period"] == "令和8年度"
        assert record["budget_amount_thousand_yen"] >= 0
        assert 1 <= record["budget_pdf_page"] <= 69
        if record["linkage_status"] == "linked":
            assert record["match_basis"] == "exact_name_measure_department_office"
            assert record["settlement_period"] == "令和6年度"
            assert record["settlement_amount_thousand_yen"] >= 0
            assert 1 <= record["settlement_pdf_page"] <= 210
            assert record["settlement_candidates"] == []
            assert "別年度の別金額" in record["boundary"]
        elif record["linkage_status"] == "partial":
            assert record["settlement_period"] is None
            assert record["settlement_amount_thousand_yen"] is None
            assert record["settlement_pdf_page"] is None
            assert record["settlement_candidates"]
            assert "確定できない" in record["boundary"]
        else:
            assert record["match_basis"] == "exact_name_not_found_in_fy2024_settlement"
            assert record["settlement_period"] is None
            assert record["settlement_amount_thousand_yen"] is None
            assert record["settlement_candidates"] == []


def test_official_sources_and_promotion_rule_are_conservative():
    index, _, _ = linkage_records()

    assert index["sources"]["budget"]["url"] == (
        "https://www.pref.miyagi.jp/documents/59763/"
        "r7hanneijyoukyousetumeisyo.pdf"
    )
    assert index["sources"]["settlement"]["url"] == (
        "https://www.pref.miyagi.jp/documents/59769/r7-seikatohyouka_1.pdf"
    )
    assert "same official measure" in index["promotion_rule"]
    assert "department" in index["promotion_rule"]
    assert "office" in index["promotion_rule"]
