import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TARGET_CATALOG_PATHS = sorted(
    (ROOT / "data/entities/policy").glob(
        "fukuoka_prefecture_initiative_*_targets.json"
    )
)
NEW_TARGET_EVIDENCE_PATHS = [
    ROOT
    / (
        "data/entities/policy/"
        f"fukuoka_prefecture_initiative_{number:02d}_target_evidence_packet.json"
    )
    for number in range(11, 27)
]


def load(path: Path | str):
    file_path = path if isinstance(path, Path) else ROOT / path
    return json.loads(file_path.read_text(encoding="utf-8"))


def validate(schema_path: str, value):
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    return list(validator.iter_errors(value))


def test_policy_target_catalogs_are_continuous_through_one_hundred_eighteen():
    catalogs = [load(path) for path in TARGET_CATALOG_PATHS]
    assert len(catalogs) == 26
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
        14,
        5,
        2,
        3,
        3,
        7,
        5,
        1,
        3,
        7,
        2,
        1,
        3,
        2,
        6,
        5,
    ]
    assert [
        item["target_number"]
        for catalog in catalogs
        for item in catalog["items"]
    ] == list(range(1, 119))
    for catalog in catalogs:
        assert validate("schemas/policy_target_catalog.schema.json", catalog) == []


def test_initiative_eleven_preserves_period_scopes_and_missing_baseline():
    initiative = load(TARGET_CATALOG_PATHS[10])["items"]
    assert [item["target_number"] for item in initiative] == list(range(50, 64))
    assert [item["components"][0]["target_value"] for item in initiative] == [
        1900,
        91,
        81,
        5300,
        80,
        90,
        63,
        5000,
        10000,
        2.34,
        73,
        60,
        34.7,
        1500,
    ]
    assert initiative[0]["components"][0]["baseline_value"] is None
    assert initiative[0]["components"][0]["baseline_scope"] == "not_available"
    for index in (7, 8, 13):
        component = initiative[index]["components"][0]
        assert component["baseline_scope"] == "annual"
        assert component["target_scope"] == "five_year_cumulative"


def test_initiative_twelve_supports_conditional_and_bounded_targets():
    initiative = load(TARGET_CATALOG_PATHS[11])["items"]
    assert [item["target_number"] for item in initiative] == list(range(64, 69))

    health_components = initiative[0]["components"]
    assert [component["baseline_value"] for component in health_components] == [
        81.24,
        72.22,
        87.47,
        75.19,
    ]
    assert all(component["target_value"] is None for component in health_components)
    assert all(
        component["target_text"] == "平均寿命の増加分を上回る健康寿命の増加"
        for component in health_components
    )
    assert all(
        component["target_scope"] == "relative_condition"
        for component in health_components
    )

    assert initiative[1]["components"][0]["target_operator"] == "at_most"
    assert initiative[2]["components"][0]["target_operator"] == "at_most"
    assert initiative[1]["components"][0]["target_value"] == 12.5
    assert initiative[2]["components"][0]["target_value"] == 68.4
    assert initiative[3]["components"][0]["target_value"] == 80
    assert initiative[4]["components"][0]["target_value"] == 1680


def test_new_target_evidence_packets_and_references_are_valid():
    source_ids = {
        source["id"]
        for source in load("data/catalog/policy_sources.json")["records"]
    }
    initiative_ids = {
        item["id"]
        for item in load(
            "data/entities/policy/fukuoka_prefecture_policy_initiatives.json"
        )["items"]
    }
    catalogs = [load(path) for path in TARGET_CATALOG_PATHS[10:]]
    packets = [load(path) for path in NEW_TARGET_EVIDENCE_PATHS]

    assert {
        catalog["policy_initiative_id"] for catalog in catalogs
    } <= initiative_ids
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
