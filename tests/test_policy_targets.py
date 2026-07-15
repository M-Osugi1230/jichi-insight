import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TARGET_CATALOG_PATHS = [
    "data/entities/policy/fukuoka_prefecture_initiative_01_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_02_targets.json",
    "data/entities/policy/fukuoka_prefecture_initiative_03_targets.json",
]
TARGET_EVIDENCE_PATHS = [
    "data/entities/policy/fukuoka_prefecture_initiative_01_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_02_target_evidence_packet.json",
    "data/entities/policy/fukuoka_prefecture_initiative_03_target_evidence_packet.json",
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


def test_first_three_initiatives_have_eighteen_reviewed_targets():
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

    assert [len(catalog["items"]) for catalog in catalogs] == [10, 7, 1]
    target_numbers = [
        item["target_number"]
        for catalog in catalogs
        for item in catalog["items"]
    ]
    assert target_numbers == list(range(1, 19))
    assert [catalog["source_page"] for catalog in catalogs] == [1, 2, 2]
    assert [catalog["printed_page"] for catalog in catalogs] == [315, 316, 316]


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
