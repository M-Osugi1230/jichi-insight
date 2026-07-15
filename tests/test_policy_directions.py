import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(schema_path: str, value):
    return list(Draft202012Validator(load(schema_path), format_checker=FormatChecker()).iter_errors(value))


def test_policy_direction_fixture_is_valid():
    fixture = load("data/examples/policy_direction.example.json")
    assert validate("schemas/policy_direction.schema.json", fixture) == []
    assert fixture["evaluation_status"] == "not_assessed"


def test_fukuoka_policy_directions_match_official_order_and_contract():
    records = load("data/entities/policy/fukuoka_prefecture_policy_directions.json")
    assert len(records) == 4
    assert [record["display_order"] for record in records] == [1, 2, 3, 4]
    assert [record["title_original"] for record in records] == [
        "世界を視野に、未来を見据えて成長し、発展する",
        "誰もが住み慣れたところで働き、長く元気に暮らし、子どもを安心して産み育てることができる",
        "感染症や災害に負けない強靭な社会をつくる",
        "将来の発展を支える基盤をつくる",
    ]
    for record in records:
        assert validate("schemas/policy_direction.schema.json", record) == []
        assert record["municipality_id"] == "jp-local-400009"
        assert record["plan_period_start"] == 2022
        assert record["plan_period_end"] == 2026
        assert record["progress_linkage_status"] == "not_linked"
        assert record["evaluation_status"] == "not_assessed"


def test_policy_direction_sources_and_evidence_are_complete():
    records = load("data/entities/policy/fukuoka_prefecture_policy_directions.json")
    packets = load("data/entities/policy/fukuoka_prefecture_policy_direction_evidence_packets.json")
    source_ids = {source["id"] for source in load("data/catalog/policy_sources.json")["records"]}
    assert {packet["subject_id"] for packet in packets} == {record["id"] for record in records}
    for record in records:
        assert set(record["plan_source_ids"]) <= source_ids
    for packet in packets:
        assert validate("schemas/evidence_packet.schema.json", packet) == []
        assert packet["open_questions"]
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
