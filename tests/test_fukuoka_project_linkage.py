import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog"
INDEX_PATH = CATALOG / "fukuoka_project_linkage.json"
INDEX_SCHEMA_PATH = ROOT / "schemas/fukuoka_project_linkage.schema.json"
PART_SCHEMA_PATH = ROOT / "schemas/fukuoka_project_linkage_part.schema.json"
TARGET_ROOT = ROOT / "data/entities/policy"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def linkage_records():
    index = load(INDEX_PATH)
    parts = [load(CATALOG / filename) for filename in index["part_files"]]
    records = [record for part in parts for record in part["records"]]
    return index, parts, records


def target_ids():
    result = set()
    for path in TARGET_ROOT.glob("fukuoka_prefecture_initiative_*_targets.json"):
        result.update(item["id"] for item in load(path)["items"])
    return result


def test_fukuoka_project_linkage_index_and_parts_match_schema():
    index_validator = Draft202012Validator(
        load(INDEX_SCHEMA_PATH), format_checker=FormatChecker()
    )
    part_validator = Draft202012Validator(
        load(PART_SCHEMA_PATH), format_checker=FormatChecker()
    )
    index, parts, _ = linkage_records()

    assert list(index_validator.iter_errors(index)) == []
    assert len(parts) == 3
    assert all(list(part_validator.iter_errors(part)) == [] for part in parts)
    assert [
        (part["record_number_from"], part["record_number_to"]) for part in parts
    ] == [(1, 100), (101, 200), (201, 266)]


def test_all_266_evaluated_projects_are_covered_once():
    index, _, records = linkage_records()
    numbers = [record["evaluation_number"] for record in records]
    record_ids = [record["id"] for record in records]

    assert index["evaluated_project_count"] == 266
    assert index["record_count"] == 266
    assert numbers == list(range(1, 267))
    assert len(record_ids) == len(set(record_ids)) == 266
    assert record_ids == [
        f"fukuoka-project-linkage-{number:03d}" for number in range(1, 267)
    ]
    assert all(record["department_office"] for record in records)


def test_candidate_classification_and_summary_are_conservative():
    index, _, records = linkage_records()
    statuses = Counter(record["linkage_status"] for record in records)

    assert statuses == {"linked": 1, "partial": 108, "not_linked": 157}
    assert index["summary"] == {
        "linked_record_count": 1,
        "partial_record_count": 108,
        "not_linked_record_count": 157,
    }
    assert index["status"] == "candidate_review"
    assert index["evaluation_status"] == "not_assessed"
    assert "candidate-only" in index["promotion_rule"]


def test_only_exact_full_name_candidate_has_both_unique_money_layers():
    _, _, records = linkage_records()
    exact = [record for record in records if record["linkage_status"] == "linked"]

    assert len(exact) == 1
    record = exact[0]
    assert record["evaluation_number"] == 178
    assert record["project_name"] == "県内送客促進事業"
    assert record["department_office"] == "商工部観光局 / 観光振興課"
    assert record["budget_matches"] == [
        {"pdf_page": 28, "matched_alias": "県内送客促進事業"}
    ]
    assert record["settlement_matches"] == [
        {"pdf_page": 189, "matched_alias": "県内送客促進事業"}
    ]
    assert "自動変換しない" in record["boundary"]


def test_target_candidates_are_exact_indicator_matches_and_do_not_assess_policy():
    index, _, records = linkage_records()
    catalog_target_ids = target_ids()
    matched_target_ids = {
        match["target_id"]
        for record in records
        for match in record["target_matches"]
    }

    assert len(catalog_target_ids) == 118
    assert len(matched_target_ids) == index["target_candidate_count"] == 17
    assert matched_target_ids <= catalog_target_ids
    assert all(
        match["match_basis"]
        == "normalized_full_indicator_in_evaluation_summary"
        for record in records
        for match in record["target_matches"]
    )


def test_source_roles_and_fiscal_periods_remain_separate():
    index, _, records = linkage_records()

    assert index["sources"] == {
        "evaluation": (
            "https://www.pref.fukuoka.lg.jp/uploaded/life/"
            "810515_62838386_misc.pdf"
        ),
        "budget": "https://www.pref.fukuoka.lg.jp/uploaded/attachment/278132.pdf",
        "settlement": "https://www.pref.fukuoka.lg.jp/uploaded/attachment/272597.pdf",
    }
    assert all(record["fy2025_project_cost_thousand_yen"] >= 0 for record in records)
    assert all(2 <= record["evaluation_summary_pdf_page"] <= 44 for record in records)
    assert not any("achievement" in record for record in records)
