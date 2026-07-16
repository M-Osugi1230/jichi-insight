import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
EVIDENCE = POLICY / "hokkaido_indicator_globalization_evidence_packets.json"
CATALOG = POLICY / "hokkaido_indicator_catalog_globalization.json"
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_schema_coverage_and_pages():
    packets = load(EVIDENCE)
    items = {item["id"]: item for item in load(CATALOG)["items"]}
    validator = Draft202012Validator(load(SCHEMA))
    assert len(packets) == 2
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == set(items)
    for packet in packets:
        item = items[packet["subject_id"]]
        assert packet["open_questions"] == []
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == [
                "policy-source-hokkaido-indicators-global"
            ]
            assert f"PDFページ{item['source_page']}" in claim["location_note"]
            assert claim["decision"] == "accepted"


def test_evidence_preserves_reference_and_timing_boundaries():
    packets = {packet["subject_id"]: packet for packet in load(EVIDENCE)}
    english = next(
        claim
        for claim in packets["policy-indicator-hokkaido-84"]["claims"]
        if claim["field"] == "series"
    )
    residents = next(
        claim
        for claim in packets["policy-indicator-hokkaido-85"]["claims"]
        if claim["field"] == "series"
    )
    assert "各教育局管内" in english["review_note"]
    assert "12月1日時点" in english["review_note"]
    assert "在留資格別" in residents["review_note"]
    assert "国籍・地域別" in residents["review_note"]
    assert "12月末時点" in residents["review_note"]
