import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATHS = [
    f"data/entities/policy/fukuoka_prefecture_initiative_{number:02d}_targets.json"
    for number in range(16, 21)
]
EVIDENCE_PATHS = [
    "data/entities/policy/"
    f"fukuoka_prefecture_initiative_{number:02d}_target_evidence_packet.json"
    for number in range(16, 21)
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


def test_initiatives_16_to_20_are_valid_and_continuous():
    catalogs = [load(path) for path in CATALOG_PATHS]
    assert [len(catalog["items"]) for catalog in catalogs] == [7, 5, 1, 3, 7]
    target_numbers = [
        item["target_number"]
        for catalog in catalogs
        for item in catalog["items"]
    ]
    assert target_numbers == list(range(77, 100))
    assert [catalog["source_page"] for catalog in catalogs] == [6, 7, 7, 7, 7]
    assert [catalog["printed_page"] for catalog in catalogs] == [321, 322, 322, 322, 322]
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


def test_support_and_safety_targets_preserve_semantics():
    initiatives = [load(path)["items"] for path in CATALOG_PATHS]
    seniors, hardship, human_rights, international, safety = initiatives

    assert [component(seniors, index)["target_value"] for index in range(7)] == [
        35.78,
        0,
        664000,
        59000,
        9500,
        1.0,
        10,
    ]
    assert component(seniors, 1)["preferred_direction"] == "decrease"
    assert component(seniors, 4)["target_scope"] == "five_year_cumulative"
    assert component(seniors, 6)["target_unit"] == "位"
    assert component(seniors, 6)["preferred_direction"] == "decrease"
    assert all(
        item["indicator_name_original"]
        != "生涯現役チャレンジセンターによる進路決定者数"
        for item in seniors
    )

    assert [component(hardship, index)["target_value"] for index in range(5)] == [
        60,
        47.8,
        3.8,
        79.5,
        80.0,
    ]
    assert component(hardship, 2)["target_operator"] == "at_most"
    assert component(hardship, 1)["target_period"] == "R7年度"
    assert component(hardship, 2)["target_period"] == "R7年度"

    assert component(human_rights)["label"] == "H30–R2平均"
    assert component(human_rights)["target_value"] == 36500

    assert [component(international, index)["target_value"] for index in range(3)] == [
        1220,
        72,
        27,
    ]
    assert component(international, 2)["target_scope"] == "cumulative"

    assert [component(safety, index)["target_value"] for index in range(7)] == [
        190,
        60,
        23000,
        3.5,
        80,
        100,
        100,
    ]
    for index in range(5):
        assert component(safety, index)["target_operator"] == "at_most"
        assert component(safety, index)["preferred_direction"] == "decrease"
    assert component(safety, 4)["target_period"] == "R7年"
    assert all(
        item["indicator_name_original"] != "国際水準GAPの認証取得数"
        for item in safety
    )


def test_initiatives_16_to_20_have_evidence_and_valid_references():
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

    repeated_notes = " ".join(
        claim["review_note"] or ""
        for packet in packets
        for claim in packet["claims"]
    )
    assert "指標58の再掲" in repeated_notes
    assert "指標40の再掲" in repeated_notes
