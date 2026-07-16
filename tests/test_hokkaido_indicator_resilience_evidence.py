import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
EVIDENCE = POLICY / "hokkaido_indicator_resilience_evidence_packets.json"
CATALOG = POLICY / "hokkaido_indicator_catalog_resilience.json"
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_schema_coverage_and_pages():
    packets = load(EVIDENCE)
    items = {item["id"]: item for item in load(CATALOG)["items"]}
    validator = Draft202012Validator(load(SCHEMA))
    assert len(packets) == 6
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == set(items)
    for packet in packets:
        item = items[packet["subject_id"]]
        assert packet["open_questions"] == []
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == [
                "policy-source-hokkaido-indicators-resilience"
            ]
            assert f"PDFページ{item['source_page']}" in claim["location_note"]
            assert claim["decision"] == "accepted"


def test_evidence_preserves_quality_boundaries():
    packets = {packet["subject_id"]: packet for packet in load(EVIDENCE)}
    notes = {}
    for number in range(86, 92):
        packet = packets[f"policy-indicator-hokkaido-{number}"]
        series_claim = next(
            claim for claim in packet["claims"] if claim["field"] == "series"
        )
        notes[number] = series_claim["review_note"]
    assert "3月末基準日" in notes[86]
    assert "翌年公表" in notes[87]
    assert "データなし年" in notes[88]
    assert "地域別内訳" in notes[89]
    assert "対象15病院" in notes[90]
    assert "前年4月1日基準" in notes[91]
