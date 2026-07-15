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


def test_policy_initiative_fixture_is_valid():
    fixture = load("data/examples/policy_initiative_catalog.example.json")
    assert validate("schemas/policy_initiative_catalog.schema.json", fixture) == []
    assert fixture["items"][0]["evaluation_status"] == "not_assessed"


def test_fukuoka_policy_initiatives_are_complete_and_ordered():
    catalog = load("data/entities/policy/fukuoka_prefecture_policy_initiatives.json")
    assert validate("schemas/policy_initiative_catalog.schema.json", catalog) == []
    items = catalog["items"]
    assert len(items) == 30
    assert [item["sequence_number"] for item in items] == list(range(1, 31))
    assert len({item["id"] for item in items}) == 30
    assert items[0]["title_original"] == "次代を担う「人財」の育成"
    assert items[11]["title_original"] == "健康づくり、安心で質の高い医療の提供"
    assert items[25]["title_original"] == "きめ細かな対応が必要な子どもの支援"
    assert items[29]["title_original"] == "生活と産業の発展を支える社会基盤の整備"
    assert all(item["progress_linkage_status"] == "not_linked" for item in items)
    assert all(item["evaluation_status"] == "not_assessed" for item in items)


def test_policy_initiatives_match_direction_ranges():
    items = load("data/entities/policy/fukuoka_prefecture_policy_initiatives.json")[
        "items"
    ]
    grouped = {}
    for item in items:
        grouped.setdefault(item["policy_direction_id"], []).append(
            item["sequence_number"]
        )
    assert grouped == {
        "policy-direction-fukuoka-prefecture-growth": list(range(1, 8)),
        "policy-direction-fukuoka-prefecture-livelihood": list(range(8, 27)),
        "policy-direction-fukuoka-prefecture-resilience": list(range(27, 30)),
        "policy-direction-fukuoka-prefecture-foundation": [30],
    }


def test_policy_initiative_sources_directions_and_evidence_are_complete():
    catalog = load("data/entities/policy/fukuoka_prefecture_policy_initiatives.json")
    packet = load(
        "data/entities/policy/fukuoka_prefecture_policy_initiative_evidence_packet.json"
    )
    source_ids = {
        source["id"] for source in load("data/catalog/policy_sources.json")["records"]
    }
    direction_ids = {
        direction["id"]
        for direction in load(
            "data/entities/policy/fukuoka_prefecture_policy_directions.json"
        )
    }
    assert set(catalog["plan_source_ids"]) <= source_ids
    assert set(catalog["progress_source_ids"]) <= source_ids
    assert {item["policy_direction_id"] for item in catalog["items"]} <= direction_ids
    assert validate("schemas/evidence_packet.schema.json", packet) == []
    assert packet["subject_id"] == catalog["id"]
    assert packet["open_questions"]
    for claim in packet["claims"]:
        assert set(claim["source_ids"]) <= source_ids
