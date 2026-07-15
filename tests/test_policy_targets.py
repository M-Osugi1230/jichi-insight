import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TARGET_CATALOG_PATHS = [
    f"data/entities/policy/fukuoka_prefecture_initiative_{number:02d}_targets.json"
    for number in range(1, 11)
]
TARGET_EVIDENCE_PATHS = [
    "data/entities/policy/"
    f"fukuoka_prefecture_initiative_{number:02d}_target_evidence_packet.json"
    for number in range(1, 11)
]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(schema_path: str, value):
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    return list(validator.iter_errors(value))


def component(items, index=0):
    return items[index]["components"][0]


def test_policy_target_fixture_is_valid():
    fixture = load("data/examples/policy_target_catalog.example.json")
    assert validate("schemas/policy_target_catalog.schema.json", fixture) == []
    assert fixture["items"][0]["actual_linkage_status"] == "not_linked"


def test_first_ten_initiatives_have_forty_nine_reviewed_targets():
    catalogs = [load(path) for path in TARGET_CATALOG_PATHS]
    for catalog in catalogs:
        assert validate("schemas/policy_target_catalog.schema.json", catalog) == []
        assert all(
            item["actual_linkage_status"] == "not_linked"
            for item in catalog["items"]
        )
        assert all(
            item["evaluation_status"] == "not_assessed"
            for item in catalog["items"]
        )

    assert [len(catalog["items"]) for catalog in catalogs] == [
        10,
        7,
        1,
        2,
        2,
        2,
        4,
        6,
        6,
        9,
    ]
    target_numbers = [
        item["target_number"]
        for catalog in catalogs
        for item in catalog["items"]
    ]
    assert target_numbers == list(range(1, 50))
    assert len(target_numbers) == len(set(target_numbers))
    assert [catalog["source_page"] for catalog in catalogs] == [
        1,
        2,
        2,
        2,
        2,
        2,
        2,
        3,
        3,
        4,
    ]
    assert [catalog["printed_page"] for catalog in catalogs] == [
        315,
        316,
        316,
        316,
        316,
        316,
        316,
        317,
        317,
        318,
    ]


def test_target_values_preserve_period_scopes_and_missing_baselines():
    catalogs = [load(path)["items"] for path in TARGET_CATALOG_PATHS]

    initiative_01 = catalogs[0]
    first_values = [
        (item["baseline_value"], item["target_value"])
        for item in initiative_01[0]["components"]
    ]
    second_values = [
        (item["baseline_value"], item["target_value"])
        for item in initiative_01[1]["components"]
    ]
    assert first_values == [(5, 6), (2, 6)]
    assert second_values == [(1, 6), (1, 6)]
    assert component(initiative_01, 4)["preferred_direction"] == "decrease"
    for item in initiative_01[7:10]:
        value = item["components"][0]
        assert value["baseline_scope"] == "annual"
        assert value["target_scope"] == "five_year_cumulative"

    initiative_02 = catalogs[1]
    for item in initiative_02:
        value = item["components"][0]
        if item["target_number"] in {12, 17}:
            assert value["baseline_value"] is None
            assert value["baseline_unit"] is None
            assert value["baseline_period"] is None
            assert value["baseline_scope"] == "not_available"
    assert component(initiative_02)["target_value"] == 300
    assert component(initiative_02, 4)["target_value"] == 532
    assert component(initiative_02, 5)["target_value"] == 72.0

    initiative_03 = catalogs[2]
    assert component(initiative_03)["baseline_value"] is None
    assert component(initiative_03)["baseline_scope"] == "not_available"
    assert component(initiative_03)["target_value"] == 11000

    initiative_04 = catalogs[3]
    assert (component(initiative_04)["baseline_value"], component(initiative_04)["target_value"]) == (876, 5000)
    assert component(initiative_04)["target_scope"] == "five_year_cumulative"
    assert (component(initiative_04, 1)["baseline_value"], component(initiative_04, 1)["target_value"]) == (2270, 8000)

    initiative_05 = catalogs[4]
    assert (component(initiative_05)["baseline_value"], component(initiative_05)["target_value"]) == (25.8, 100)
    assert component(initiative_05)["target_period"] == "R7年度"
    assert component(initiative_05, 1)["label"] == "全国参考値"
    assert component(initiative_05, 1)["target_value"] == 40

    initiative_06 = catalogs[5]
    assert (component(initiative_06)["baseline_value"], component(initiative_06)["target_value"]) == (22.9, 38.3)
    assert component(initiative_06)["baseline_period"] == "H30年度"
    assert (component(initiative_06, 1)["baseline_value"], component(initiative_06, 1)["target_value"]) == (269, 405)

    initiative_07 = catalogs[6]
    assert [component(initiative_07, index)["target_value"] for index in range(4)] == [500, 200, 75, 80]
    for item in initiative_07:
        value = item["components"][0]
        assert value["baseline_scope"] == "annual"
        assert value["target_scope"] == "five_year_cumulative"

    initiative_08 = catalogs[7]
    assert [component(initiative_08, index)["target_value"] for index in range(6)] == [500, 300, 1000, 120, 150, 250]

    initiative_09 = catalogs[8]
    assert [item["target_number"] for item in initiative_09] == list(range(35, 41))
    assert [component(initiative_09, index)["target_value"] for index in range(6)] == [1047, 400, 250, 420, 6000, 60]
    assert component(initiative_09, 4)["baseline_value"] is None
    assert component(initiative_09, 4)["baseline_scope"] == "not_available"

    initiative_10 = catalogs[9]
    assert [item["target_number"] for item in initiative_10] == list(range(41, 50))
    assert [component(initiative_10, index)["target_value"] for index in range(9)] == [
        50800,
        78000,
        65.0,
        200000,
        400000,
        400,
        800,
        1772,
        17,
    ]
    assert component(initiative_10, 2)["label"] == "参考値"
    assert component(initiative_10, 3)["baseline_scope"] == "cumulative"
    assert component(initiative_10, 4)["target_scope"] == "cumulative"
    assert component(initiative_10, 5)["baseline_scope"] == "annual"
    assert component(initiative_10, 6)["target_scope"] == "annual"
    assert component(initiative_10, 8)["target_scope"] == "cumulative"


def test_relisted_targets_are_not_duplicated():
    all_items = [
        item
        for path in TARGET_CATALOG_PATHS
        for item in load(path)["items"]
    ]
    names = [item["indicator_name_original"] for item in all_items]

    initiative_09_names = {
        item["indicator_name_original"]
        for item in load(TARGET_CATALOG_PATHS[8])["items"]
    }
    assert "県産農林水産物の輸出額" not in initiative_09_names
    assert "新規就業者数（農林漁業）" not in initiative_09_names

    initiative_10_names = {
        item["indicator_name_original"]
        for item in load(TARGET_CATALOG_PATHS[9])["items"]
    }
    assert "延べ宿泊者数（外国人）" not in initiative_10_names

    for unique_name in [
        "県産農林水産物の輸出額",
        "新規就業者数（農林漁業）",
        "旅行消費単価（日本人）",
        "旅行消費単価（通常入国外国人）",
        "リピーター率",
        "延べ宿泊者数（外国人）",
    ]:
        assert names.count(unique_name) == 1


def test_policy_target_sources_initiatives_and_evidence_are_complete():
    catalogs = [load(path) for path in TARGET_CATALOG_PATHS]
    packets = [load(path) for path in TARGET_EVIDENCE_PATHS]
    source_ids = {
        source["id"] for source in load("data/catalog/policy_sources.json")["records"]
    }
    initiative_ids = {
        item["id"]
        for item in load(
            "data/entities/policy/fukuoka_prefecture_policy_initiatives.json"
        )["items"]
    }
    assert {catalog["policy_initiative_id"] for catalog in catalogs} <= initiative_ids
    assert {packet["subject_id"] for packet in packets} == {
        catalog["id"] for catalog in catalogs
    }
    for catalog in catalogs:
        assert set(catalog["source_ids"]) <= source_ids
    for packet in packets:
        assert validate("schemas/evidence_packet.schema.json", packet) == []
        assert packet["open_questions"]
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
