import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TARGET_CATALOG_PATHS = [
    "data/entities/policy/fukuoka_prefecture_initiative_01_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_02_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_03_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_04_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_05_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_06_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_07_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_08_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_09_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_10_targets.json",
]
TARGET_EVIDENCE_PATHS = [
    "data/entities/policy/fukuoka_prefecture_initiative_01_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_02_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_03_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_04_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_05_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_06_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_07_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_08_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_09_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_10_target_evidence_packet.json",
]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(schema_path: str, value):
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    return list(validator.iter_errors(value))


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


def test_target_values_preserve_components_period_scopes_and_missing_baselines():
    initiative_01 = load(TARGET_CATALOG_PATHS[0])["items"]
    first_values = [
        (component["baseline_value"], component["target_value"])
        for component in initiative_01[0]["components"]
    ]
    second_values = [
        (component["baseline_value"], component["target_value"])
        for component in initiative_01[1]["components"]
    ]
    assert first_values == [(5, 6), (2, 6)]
    assert second_values == [(1, 6), (1, 6)]
    assert initiative_01[4]["components"][0]["preferred_direction"] == "decrease"
    for item in initiative_01[7:10]:
        component = item["components"][0]
        assert component["baseline_scope"] == "annual"
        assert component["target_scope"] == "five_year_cumulative"

    initiative_02 = load(TARGET_CATALOG_PATHS[1])["items"]
    missing_baseline_targets = {12, 17}
    for item in initiative_02:
        component = item["components"][0]
        if item["target_number"] in missing_baseline_targets:
            assert component["baseline_value"] is None
            assert component["baseline_unit"] is None
            assert component["baseline_period"] is None
            assert component["baseline_scope"] == "not_available"
    assert initiative_02[0]["components"][0]["target_value"] == 300
    assert initiative_02[4]["components"][0]["target_value"] == 532
    assert initiative_02[5]["components"][0]["target_value"] == 72.0

    initiative_03 = load(TARGET_CATALOG_PATHS[2])["items"][0]
    component = initiative_03["components"][0]
    assert component["baseline_value"] is None
    assert component["baseline_scope"] == "not_available"
    assert component["target_value"] == 11000
    assert component["target_scope"] == "five_year_cumulative"

    initiative_04 = load(TARGET_CATALOG_PATHS[3])["items"]
    migration = initiative_04[0]["components"][0]
    fan_club = initiative_04[1]["components"][0]
    assert (migration["baseline_value"], migration["target_value"]) == (876, 5000)
    assert migration["baseline_scope"] == "annual"
    assert migration["target_scope"] == "five_year_cumulative"
    assert (fan_club["baseline_value"], fan_club["target_value"]) == (2270, 8000)
    assert fan_club["baseline_scope"] == "cumulative"
    assert fan_club["target_scope"] == "cumulative"

    initiative_05 = load(TARGET_CATALOG_PATHS[4])["items"]
    online = initiative_05[0]["components"][0]
    dx = initiative_05[1]["components"][0]
    assert (online["baseline_value"], online["target_value"]) == (25.8, 100)
    assert online["target_period"] == "R7年度"
    assert dx["label"] == "全国参考値"
    assert dx["baseline_value"] == 9
    assert dx["baseline_period"] is None
    assert dx["target_value"] == 40

    initiative_06 = load(TARGET_CATALOG_PATHS[5])["items"]
    emissions = initiative_06[0]["components"][0]
    renewable = initiative_06[1]["components"][0]
    assert (emissions["baseline_value"], emissions["target_value"]) == (22.9, 38.3)
    assert emissions["baseline_period"] == "H30年度"
    assert (renewable["baseline_value"], renewable["target_value"]) == (269, 405)
    assert renewable["target_unit"] == "万kW"

    initiative_07 = load(TARGET_CATALOG_PATHS[6])["items"]
    assert [item["components"][0]["target_value"] for item in initiative_07] == [
        500,
        200,
        75,
        80,
    ]
    for item in initiative_07:
        component = item["components"][0]
        assert component["baseline_scope"] == "annual"
        assert component["target_scope"] == "five_year_cumulative"

    initiative_08 = load(TARGET_CATALOG_PATHS[7])["items"]
    assert [item["components"][0]["target_value"] for item in initiative_08] == [
        500,
        300,
        1000,
        120,
        150,
        250,
    ]
    for item in (initiative_08[0], initiative_08[2], initiative_08[3], initiative_08[4]):
        component = item["components"][0]
        assert component["baseline_scope"] == "annual"
        assert component["target_scope"] == "five_year_cumulative"
    for item in (initiative_08[1], initiative_08[5]):
        component = item["components"][0]
        assert component["baseline_scope"] == "snapshot"
        assert component["target_scope"] == "snapshot"

    initiative_09 = load(TARGET_CATALOG_PATHS[8])["items"]
    assert [item["target_number"] for item in initiative_09] == list(range(35, 41))
    assert [item["components"][0]["target_value"] for item in initiative_09] == [
        1047,
        400,
        250,
        420,
        6000,
        60,
    ]
    assert initiative_09[0]["components"][0]["target_scope"] == "cumulative"
    assert initiative_09[1]["components"][0]["target_scope"] == "annual"
    assert initiative_09[2]["components"][0]["target_scope"] == "five_year_cumulative"
    assert initiative_09[3]["components"][0]["target_scope"] == "cumulative"
    assert initiative_09[4]["components"][0]["baseline_value"] is None
    assert initiative_09[4]["components"][0]["baseline_scope"] == "not_available"
    assert initiative_09[5]["components"][0]["target_scope"] == "cumulative"

    initiative_10 = load(TARGET_CATALOG_PATHS[9])["items"]
    assert [item["target_number"] for item in initiative_10] == list(range(41, 50))
    assert [item["components"][0]["target_value"] for item in initiative_10] == [
        50800,
        78000,
        65,
        200000,
        400000,
        400,
        800,
        1772,
        17,
    ]
    assert initiative_10[0]["components"][0]["baseline_period"] == "R2年"
    assert initiative_10[1]["components"][0]["baseline_period"] == "R1年"
    assert initiative_10[2]["components"][0]["label"] == "参考値"
    assert initiative_10[2]["components"][0]["baseline_period"] == "R1年度"
    for item in (initiative_10[3], initiative_10[4], initiative_10[8]):
        component = item["components"][0]
        assert component["baseline_scope"] == "cumulative"
        assert component["target_scope"] == "cumulative"
    for item in (initiative_10[0], initiative_10[1], initiative_10[5], initiative_10[6], initiative_10[7]):
        component = item["components"][0]
        assert component["baseline_scope"] == "annual"
        assert component["target_scope"] == "annual"


def test_relisted_targets_are_not_duplicated():
    all_items = [
        item
        for path in TARGET_CATALOG_PATHS
        for item in load(path)["items"]
    ]
    initiative_09_names = {
        item["indicator_name_original"]
        for item in load(TARGET_CATALOG_PATHS[8])["items"]
    }
    initiative_10_names = [
        item["indicator_name_original"]
        for item in load(TARGET_CATALOG_PATHS[9])["items"]
    ]
    assert "県産農林水産物の輸出額" not in initiative_09_names
    assert "新規就業者数（農林漁業）" not in initiative_09_names
    assert sum(
        item["indicator_name_original"] == "県産農林水産物の輸出額"
        for item in all_items
    ) == 1
    assert sum(
        item["indicator_name_original"] == "新規就業者数（農林漁業）"
        for item in all_items
    ) == 1
    assert initiative_10_names.count("旅行消費単価（日本人）") == 1
    assert initiative_10_names.count("旅行消費単価（通常入国外国人）") == 1
    assert initiative_10_names.count("リピーター率") == 1
    assert "延べ宿泊者数（外国人）" not in initiative_10_names
    assert sum(
        item["indicator_name_original"] == "延べ宿泊者数（外国人）"
        for item in all_items
    ) == 1


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
