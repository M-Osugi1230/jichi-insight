import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


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


def test_initiative_01_has_ten_reviewed_targets():
    catalog = load("data/entities/policy/fukuoka_prefecture_initiative_01_targets.json")
    assert validate("schemas/policy_target_catalog.schema.json", catalog) == []
    assert catalog["policy_initiative_id"] == "policy-initiative-fukuoka-prefecture-01"
    assert catalog["source_page"] == 1
    assert catalog["printed_page"] == 315
    assert len(catalog["items"]) == 10
    assert [item["target_number"] for item in catalog["items"]] == list(range(1, 11))
    assert all(item["actual_linkage_status"] == "not_linked" for item in catalog["items"])
    assert all(item["evaluation_status"] == "not_assessed" for item in catalog["items"])


def test_target_values_preserve_components_and_period_scopes():
    items = load("data/entities/policy/fukuoka_prefecture_initiative_01_targets.json")[
        "items"
    ]
    assert [(component["baseline_value"], component["target_value"]) for component in items[0]["components"]] == [(5, 6), (2, 6)]
    assert [(component["baseline_value"], component["target_value"]) for component in items[1]["components"]] == [(1, 6), (1, 6)]
    assert items[4]["components"][0]["preferred_direction"] == "decrease"
    for item in items[7:10]:
        component = item["components"][0]
        assert component["baseline_scope"] == "annual"
        assert component["target_scope"] == "five_year_cumulative"


def test_policy_target_sources_initiative_and_evidence_are_complete():
    catalog = load("data/entities/policy/fukuoka_prefecture_initiative_01_targets.json")
    packet = load(
        "data/entities/policy/fukuoka_prefecture_initiative_01_target_evidence_packet.json"
    )
    source_ids = {
        source["id"] for source in load("data/catalog/policy_sources.json")["records"]
    }
    initiative_ids = {
        item["id"]
        for item in load(
            "data/entities/policy/fukuoka_prefecture_policy_initiatives.json"
        )["items"]
    }
    assert catalog["policy_initiative_id"] in initiative_ids
    assert set(catalog["source_ids"]) <= source_ids
    assert validate("schemas/evidence_packet.schema.json", packet) == []
    assert packet["subject_id"] == catalog["id"]
    assert packet["open_questions"]
    for claim in packet["claims"]:
        assert set(claim["source_ids"]) <= source_ids
