import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "data/entities/policy/"
    "hokkaido_indicator_sme_commerce_evidence_packets.json"
)
CATALOG = ROOT / "data/entities/policy/hokkaido_indicator_catalog_sme_commerce.json"
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_contract_and_coverage():
    packets = load(EVIDENCE)
    items = load(CATALOG)["items"]
    validator = Draft202012Validator(load(SCHEMA))

    assert len(packets) == 3
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        item["id"] for item in items
    }
    assert len({packet["id"] for packet in packets}) == 3


def test_evidence_pages_and_boundaries():
    items = {item["id"]: item for item in load(CATALOG)["items"]}
    packets = {packet["subject_id"]: packet for packet in load(EVIDENCE)}

    for subject_id, packet in packets.items():
        assert packet["open_questions"] == []
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == [
                "policy-source-hokkaido-indicators-sme-commerce"
            ]
            assert (
                f"PDFページ{items[subject_id]['source_page']}"
                in claim["location_note"]
            )
            assert claim["decision"] == "accepted"

    notes = []
    for number in (71, 72, 73):
        packet = packets[f"policy-indicator-hokkaido-{number}"]
        series_claim = next(
            claim for claim in packet["claims"] if claim["field"] == "series"
        )
        notes.append(series_claim["review_note"])

    assert "第3位" in notes[0]
    assert "振興局管内別" in notes[1]
    assert "空き店舗が解消されない原因" in notes[2]
