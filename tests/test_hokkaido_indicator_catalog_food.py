import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/entities/policy/hokkaido_indicator_catalog_food.json"
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hokkaido_food_indicator_catalog_matches_schema():
    catalog = load(CATALOG_PATH)
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []


def test_food_catalog_covers_exact_indicator_sequence_and_pages():
    catalog = load(CATALOG_PATH)
    items = catalog["items"]

    assert catalog["indicator_number_start"] == 1
    assert catalog["indicator_number_end"] == 12
    assert len(items) == 12
    assert [item["indicator_number"] for item in items] == list(range(1, 13))
    assert [item["source_page"] for item in items] == list(range(1, 13))
    assert len({item["id"] for item in items}) == 12


def test_food_catalog_matches_verified_source_page_index():
    catalog = load(CATALOG_PATH)
    page_index = load(ROOT / "data/catalog/hokkaido_indicator_page_index.json")
    pages_by_number = {
        record["indicator_number"]: record for record in page_index["records"]
    }

    for item in catalog["items"]:
        page = pages_by_number[item["indicator_number"]]
        assert page["source_id"] == catalog["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == catalog["policy_field_id"]
        assert item["policy_field_ids"] == [catalog["policy_field_id"]]


def test_exact_indicator_names_are_preserved():
    items = load(CATALOG_PATH)["items"]

    assert [item["indicator_name_original"] for item in items] == [
        "食料自給率（カロリーベース）",
        "農業産出額",
        "道産農産物・農産加工品の輸出額",
        "漁業就業者1人当たりの漁業生産額",
        "栽培漁業生産量の割合",
        "道産水産物・水産加工品輸出額",
        "水産食料品製造業の付加価値額",
        "新規漁業就業者",
        "食品工業の付加価値額",
        "道産食品輸出額",
        "商談会等における道産食品等の国内成約件数",
        "北海道ＨＡＣＣＰの認証施設数",
    ]


def test_exact_current_intermediate_and_final_values_are_preserved():
    items = load(CATALOG_PATH)["items"]
    values_by_number = {
        item["indicator_number"]: [
            value["value"] for value in item["series"][0]["values"]
        ]
        for item in items
    }

    assert values_by_number == {
        1: [223, 244, 268],
        2: [12919, 13200, 13600],
        3: [124, None, None],
        4: [1151, 1114, 1326],
        5: [68.0, 68.5, 69.0],
        6: [1005, None, None],
        7: [1822, 1912, 2007],
        8: [144, 180, 180],
        9: [7303, 7700, 8100],
        10: [1298, None, None],
        11: [2621, 3923, 4300],
        12: [396, 490, 590],
    }


def test_unset_targets_remain_null_and_are_not_zeroed():
    items = load(CATALOG_PATH)["items"]
    unset_items = [
        item for item in items if item["target_setting_status"] == "not_set"
    ]

    assert [item["indicator_number"] for item in unset_items] == [3, 6, 10]
    for item in unset_items:
        intermediate, final = item["series"][0]["values"][1:]
        assert intermediate == {
            "role": "intermediate_target",
            "period": None,
            "value": None,
            "status": "not_set",
            "value_text_original": "―",
        }
        assert final == {
            "role": "final_target",
            "period": None,
            "value": None,
            "status": "not_set",
            "value_text_original": "―",
        }
        assert "引き続き検討" in item["target_setting_rationale_original"]


def test_units_periods_and_temporal_scopes_are_preserved():
    items = load(CATALOG_PATH)["items"]
    units = [item["series"][0]["unit_original"] for item in items]
    scopes = [item["series"][0]["temporal_scope"] for item in items]

    assert units == [
        "％",
        "億円",
        "億円",
        "万円",
        "％",
        "億円",
        "億円",
        "人",
        "億円",
        "億円",
        "件",
        "施設",
    ]
    assert scopes == [
        "fiscal_year",
        "calendar_year",
        "calendar_year",
        "calendar_year",
        "calendar_year",
        "calendar_year",
        "calendar_year",
        "fiscal_year",
        "calendar_year",
        "calendar_year",
        "fiscal_year",
        "snapshot",
    ]


def test_comparability_warnings_are_kept_for_changed_survey_populations():
    items = load(CATALOG_PATH)["items"]
    notes = {
        item["indicator_number"]: item["comparability_note_original"]
        for item in items
        if item["comparability_note_original"] is not None
    }

    assert set(notes) == {7, 9}
    assert all("単純比較できない" in note for note in notes.values())


def test_catalog_keeps_facts_separate_from_actuals_and_evaluation():
    catalog = load(CATALOG_PATH)

    assert catalog["review_status"] == "reviewed"
    assert catalog["confidence"] == "high"
    assert all(item["actual_linkage_status"] == "not_linked" for item in catalog["items"])
    assert all(item["evaluation_status"] == "not_assessed" for item in catalog["items"])
    assert all(item["review_status"] == "reviewed" for item in catalog["items"])
    assert all(item["confidence"] == "high" for item in catalog["items"])
    assert not any("score" in item for item in catalog["items"])
    assert not any("progress_rate" in item for item in catalog["items"])


def test_catalog_source_exists_and_is_the_food_kpi_pdf():
    catalog = load(CATALOG_PATH)
    sources = load(ROOT / "data/catalog/policy_sources.json")["records"]
    source = next(source for source in sources if source["id"] == catalog["source_id"])

    assert source["municipality_key"] == "hokkaido-prefecture"
    assert source["source_role"] == "kpi_source"
    assert source["format"] == "pdf"
    assert source["url"] == catalog["source_document_url"]
    assert source["review_status"] == "verified"
