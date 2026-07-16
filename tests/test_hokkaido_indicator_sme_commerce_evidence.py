import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/entities/policy/hokkaido_indicator_sme_commerce_evidence_packets.json"
CATALOG = ROOT / "data/entities/policy/hokkaido_indicator_catalog_sme_commerce.json"
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def test_evidence_contract_and_coverage():
    packets = load(EVIDENCE)
    items = load(CATALOG)["items"]
    validator = Draft202012Validator(load(SCHEMA))
    assert len(packets) == 3
    assert all(list(validator.iter_errors(x)) == [] for x in packets)
    assert {x["subject_id"] for x in packets} == {x["id"] for x in items}
    assert len({x["id"] for x in packets}) == 3

def test_evidence_pages_and_boundaries():
    items = {x["id"]: x for x in load(CATALOG)["items"]}
    packets = {x["subject_id"]: x for x in load(EVIDENCE)}
    for subject, packet in packets.items():
        assert packet["open_questions"] == []
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == ["policy-source-hokkaido-indicators-sme-commerce"]
            assert f"PDFページ{items[subject]['source_page']}" in claim["location_note"]
            assert claim["decision"] == "accepted"
    notes = [next(c for c in packets[f"policy-indicator-hokkaido-{n}"]["claims"] if c["field"] == "series")["review_note"] for n in (71, 72, 73)]
    assert "第3位" in notes[0]
    assert "振興局管内別" in notes[1]
    assert "空き店舗が解消されない原因" in notes[2]
