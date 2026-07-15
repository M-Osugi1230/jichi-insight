import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATHS = [
    f"data/entities/policy/fukuoka_prefecture_initiative_{number:02d}_targets.json"
    for number in range(13, 16)
]
EVIDENCE_PATHS = [
    "data/entities/policy/"
    f"fukuoka_prefecture_initiative_{number:02d}_target_evidence_packet.json"
    for number in range(13, 16)
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


def test_initiatives_13_to_15_are_valid_and_continuous():
    catalogs = [load(path) for path in CATALOG_PATHS]
    for catalog in catalogs:
        assert validate("schemas/policy_target_catalog.schema.json", catalog) == []
        assert catalog["source_page"] == 6
        assert catalog["printed_page"] == 320
        assert all(
            item["actual_linkage_status"] == "not_linked"
            for item in catalog["items"]
        )
        assert all(
            item["evaluation_status"] == "not_assessed"
            for item in catalog["items"]
        )

    assert [len(catalog["items"]) for catalog in catalogs] == [2, 3, 3]
    target_numbers = [
        item["target_number"]
        for catalog in catalogs
        for item in catalog["items"]
    ]
    assert target_numbers == list(range(69, 77))


def test_sports_culture_and_gender_values_preserve_source_semantics():
    sports, culture, gender = [load(path)["items"] for path in CATALOG_PATHS]

    assert [component(sports, index)["target_value"] for index in range(2)] == [
        405,
        100,
    ]
    assert component(sports)["label"] == "H30–R2平均"
    assert component(sports, 1)["target_unit"] == "%"
    assert all(
        item["indicator_name_original"]
        != "国民体育大会における男女総合成績順位"
        for item in sports
    )

    assert [component(culture, index)["target_value"] for index in range(3)] == [
        76.2,
        160000,
        210,
    ]
    assert component(culture, 1)["label"] == "H30–R2平均"
    assert component(culture, 2)["baseline_value"] is None
    assert component(culture, 2)["baseline_scope"] == "not_available"

    assert [component(gender, index)["target_value"] for index in range(3)] == [
        40.0,
        13.7,
        20.0,
    ]
    assert component(gender, 2)["baseline_period"] == "R3年度"
    assert component(gender, 2)["target_period"] == "R7年度"


def test_initiatives_13_to_15_have_evidence_and_valid_references():
    catalogs = [load(path) for path in CATALOG_PATHS]
    packets = [load(path) for path in EVIDENCE_PATHS]
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

    sports_evidence = packets[0]
    repeated_claim = next(
        claim for claim in sports_evidence["claims"] if claim["field"] == "target_count"
    )
    assert "指標5の再掲" in repeated_claim["review_note"]
