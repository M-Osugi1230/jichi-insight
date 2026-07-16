import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data/catalog/hokkaido_indicator_relationship_index.json"
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_relationship_index.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hokkaido_indicator_relationship_index_matches_schema():
    index = load(INDEX_PATH)
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(index)) == []


def test_relationship_index_resolves_the_108_to_113_difference_exactly():
    index = load(INDEX_PATH)

    assert index["relationship_status"] == "completed"
    assert index["duplicate_inclusive_indicator_count"] - index[
        "expected_unique_indicator_count"
    ] == 5
    assert index["expected_extra_relationship_count"] == 5
    assert len(index["relationships"]) == 5
    assert "重複登録しない" in index["counting_boundary"]


def test_exact_multi_field_indicator_set_and_titles_are_preserved():
    index = load(INDEX_PATH)
    relationships = index["relationships"]

    assert [relationship["indicator_number"] for relationship in relationships] == [
        16,
        17,
        24,
        45,
        50,
    ]
    assert [relationship["indicator_title_original"] for relationship in relationships] == [
        "道内空港の利用者数",
        "クルーズ船の寄港回数",
        "バイオマス利活用率",
        "輸出額",
        "育児休業取得率",
    ]


def test_relationships_match_the_verified_page_index_and_policy_hierarchy():
    index = load(INDEX_PATH)
    page_index = load(ROOT / "data/catalog/hokkaido_indicator_page_index.json")
    hierarchy = load(ROOT / "data/entities/policy/hokkaido_policy_hierarchy.json")

    pages_by_number = {
        record["indicator_number"]: record for record in page_index["records"]
    }
    fields_to_direction = {
        field["id"]: direction["id"]
        for direction in hierarchy["directions"]
        for field in direction["fields"]
    }

    for relationship in index["relationships"]:
        page = pages_by_number[relationship["indicator_number"]]
        assert relationship["source_id"] == page["source_id"]
        assert relationship["page_number"] == page["page_number"]
        assert relationship["primary_policy_field_id"] == page["policy_field_id"]
        assert fields_to_direction[relationship["primary_policy_field_id"]] == (
            relationship["primary_policy_direction_id"]
        )
        assert fields_to_direction[relationship["additional_policy_field_id"]] == (
            relationship["additional_policy_direction_id"]
        )
        assert relationship["primary_policy_field_id"] != relationship[
            "additional_policy_field_id"
        ]


def test_four_relationships_cross_directions_and_one_stays_within_direction():
    relationships = load(INDEX_PATH)["relationships"]

    assert sum(
        relationship["relationship_scope"] == "cross_direction"
        for relationship in relationships
    ) == 4
    assert sum(
        relationship["relationship_scope"] == "within_direction"
        for relationship in relationships
    ) == 1

    within_direction = next(
        relationship
        for relationship in relationships
        if relationship["relationship_scope"] == "within_direction"
    )
    assert within_direction["indicator_number"] == 50
    assert within_direction["primary_policy_direction_id"] == (
        within_direction["additional_policy_direction_id"]
    )


def test_relationships_are_references_not_duplicate_kpi_records():
    index = load(INDEX_PATH)
    pairs = {
        (
            relationship["indicator_number"],
            relationship["additional_policy_field_id"],
        )
        for relationship in index["relationships"]
    }

    assert len(pairs) == 5
    assert all(
        relationship["review_status"] == "reviewed"
        and relationship["confidence"] == "high"
        for relationship in index["relationships"]
    )
    assert "baseline_value" not in index
    assert "target_value" not in index
    assert "actual_value" not in index


def test_relationship_sources_exist_in_the_central_policy_source_catalog():
    index = load(INDEX_PATH)
    catalog = load(ROOT / "data/catalog/policy_sources.json")
    sources_by_id = {source["id"]: source for source in catalog["records"]}

    for relationship in index["relationships"]:
        source = sources_by_id[relationship["source_id"]]
        assert source["municipality_key"] == "hokkaido-prefecture"
        assert source["source_role"] == "kpi_source"
        assert source["review_status"] == "verified"
