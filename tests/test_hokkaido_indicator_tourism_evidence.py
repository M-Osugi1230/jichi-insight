import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = (
    ROOT / "data/entities/policy/hokkaido_indicator_tourism_evidence_packets.json"
)
CATALOG_PATH = ROOT / "data/entities/policy/hokkaido_indicator_catalog_tourism.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_tourism_evidence_packets_match_schema():
    packets = load(EVIDENCE_PATH)
    validator = Draft202012Validator(load(SCHEMA_PATH))
    assert len(packets) == 6
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)


def test_every_reviewed_tourism_indicator_has_one_evidence_packet():
    packets = load(EVIDENCE_PATH)
    catalog = load(CATALOG_PATH)

    assert {packet["subject_id"] for packet in packets} == {
        item["id"] for item in catalog["items"]
    }
    assert len({packet["id"] for packet in packets}) == 6
    assert all(packet["subject_type"] == "kpi" for packet in packets)
    assert all(packet["review_status"] == "reviewed" for packet in packets)


def test_evidence_claims_use_exact_source_pages():
    packets = load(EVIDENCE_PATH)
    catalog = load(CATALOG_PATH)
    items_by_id = {item["id"]: item for item in catalog["items"]}

    for packet in packets:
        item = items_by_id[packet["subject_id"]]
        assert packet["open_questions"] == []
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == [catalog["source_id"]]
            assert f"PDFページ{item['source_page']}" in claim["location_note"]
            assert claim["decision"] == "accepted"


def test_evidence_preserves_nulls_bounds_and_cross_field_references():
    packets = {
        packet["subject_id"]: packet for packet in load(EVIDENCE_PATH)
    }

    for number in (14, 15):
        series_claim = next(
            claim
            for claim in packets[f"policy-indicator-hokkaido-{number}"]["claims"]
            if claim["field"] == "series"
        )
        assert "0" in series_claim["review_note"] or "null" in series_claim["review_note"]

    for number in (13, 16):
        series_claim = next(
            claim
            for claim in packets[f"policy-indicator-hokkaido-{number}"]["claims"]
            if claim["field"] == "series"
        )
        assert "以上" in series_claim["statement"]

    for number in (16, 17):
        series_claim = next(
            claim
            for claim in packets[f"policy-indicator-hokkaido-{number}"]["claims"]
            if claim["field"] == "series"
        )
        assert "参照として保持" in series_claim["review_note"]
