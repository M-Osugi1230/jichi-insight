import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "hokkaido_indicator_catalog_globalization.json"
SCHEMA = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_catalog_schema_sequence_and_pages():
    data = load(CATALOG)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(data)) == []
    assert (data["indicator_number_start"], data["indicator_number_end"]) == (84, 85)
    assert [item["indicator_number"] for item in data["items"]] == [84, 85]
    assert [item["source_page"] for item in data["items"]] == [1, 2]


def test_catalog_matches_verified_page_index():
    data = load(CATALOG)
    index = {
        item["indicator_number"]: item
        for item in load(ROOT / "data/catalog/hokkaido_indicator_page_index.json")[
            "records"
        ]
    }
    for item in data["items"]:
        page = index[item["indicator_number"]]
        assert page["source_id"] == data["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == data["policy_field_id"]


def test_exact_names_values_and_snapshot_scopes_are_preserved():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    assert [items[number]["indicator_name_original"] for number in (84, 85)] == [
        "日常的なコミュニケーションができる英語能力を有する生徒の割合",
        "外国人居住者数",
    ]
    assert [
        [value["value"] for value in items[number]["series"][0]["values"]]
        for number in (84, 85)
    ] == [[48.4, 60.0, 60.0], [45491, 56991, 68491]]
    assert all(
        items[number]["series"][0]["temporal_scope"] == "snapshot"
        for number in (84, 85)
    )
    assert all(
        value["aggregation_scope"] == "snapshot"
        for number in (84, 85)
        for value in items[number]["series"][0]["values"]
    )


def test_english_targets_preserve_at_least_semantics():
    item = next(
        item
        for item in load(CATALOG)["items"]
        if item["indicator_number"] == 84
    )
    values = item["series"][0]["values"]
    assert values[0]["operator"] == "exact"
    assert values[1]["operator"] == "at_least"
    assert values[2]["operator"] == "at_least"
    assert "6割以上" in item["target_setting_rationale_original"]


def test_reference_breakdowns_and_publication_year_are_separated():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    assert "各教育局管内" in items[84]["comparability_note_original"]
    assert "翌年8月頃" in items[84]["comparability_note_original"]
    assert "市区町村別" in items[85]["comparability_note_original"]
    assert "在留資格別" in items[85]["comparability_note_original"]
    assert "国籍・地域別" in items[85]["comparability_note_original"]
    assert "翌年7月頃" in items[85]["comparability_note_original"]
    assert all(len(items[number]["series"]) == 1 for number in (84, 85))


def test_catalog_keeps_actuals_and_evaluations_unlinked():
    items = load(CATALOG)["items"]
    assert all(item["actual_linkage_status"] == "not_linked" for item in items)
    assert all(item["evaluation_status"] == "not_assessed" for item in items)
