import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
EVIDENCE = POLICY / "hokkaido_indicator_nature_environment_evidence_packets.json"
CATALOG = POLICY / "hokkaido_indicator_catalog_nature_environment.json"
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_schema_coverage_and_pages():
    packets = load(EVIDENCE)
    items = {item["id"]: item for item in load(CATALOG)["items"]}
    validator = Draft202012Validator(load(SCHEMA))
    assert len(packets) == 4
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == set(items)
    for packet in packets:
        item = items[packet["subject_id"]]
        assert packet["open_questions"] == []
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == [
                "policy-source-hokkaido-indicators-nature-environment"
            ]
            assert f"PDFページ{item['source_page']}" in claim["location_note"]
            assert claim["decision"] == "accepted"


def test_evidence_preserves_quality_boundaries():
    packets = {packet["subject_id"]: packet for packet in load(EVIDENCE)}
    notes = {}
    for number in range(99, 103):
        packet = packets[f"policy-indicator-hokkaido-{number}"]
        claim = next(item for item in packet["claims"] if item["field"] == "series")
        notes[number] = claim["review_note"]
    assert "物質別内訳" in notes[99]
    assert "河川・湖沼・海域" in notes[100]
    assert "範囲目標" in notes[101]
    assert "異なる公表時期" in notes[102]
