import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data/entities/policy/hokkaido_indicator_zero_carbon_evidence_packets.json"
CATALOG_PATH = ROOT / "data/entities/policy/hokkaido_indicator_catalog_zero_carbon.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_zero_carbon_evidence_packets_match_schema():
    packets = load(EVIDENCE_PATH)
    validator = Draft202012Validator(load(SCHEMA_PATH))
    assert len(packets) == 11
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)


def test_every_zero_carbon_indicator_has_one_evidence_packet():
    packets = load(EVIDENCE_PATH)
    catalog = load(CATALOG_PATH)
    assert {packet["subject_id"] for packet in packets} == {
        item["id"] for item in catalog["items"]
    }
    assert len({packet["id"] for packet in packets}) == 11
    assert all(packet["subject_type"] == "kpi" for packet in packets)
    assert all(packet["review_status"] == "reviewed" for packet in packets)


def test_evidence_uses_exact_source_pages_and_accepted_claims():
    packets = load(EVIDENCE_PATH)
    items = {item["id"]: item for item in load(CATALOG_PATH)["items"]}
    for packet in packets:
        item = items[packet["subject_id"]]
        assert packet["open_questions"] == []
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == [
                "policy-source-hokkaido-indicators-zero-carbon"
            ]
            assert f"PDFページ{item['source_page']}" in claim["location_note"]
            assert claim["decision"] == "accepted"


def test_evidence_preserves_special_zero_carbon_cases():
    packets = {packet["subject_id"]: packet for packet in load(EVIDENCE_PATH)}
    forest = next(
        claim
        for claim in packets["policy-indicator-hokkaido-20"]["claims"]
        if claim["field"] == "series"
    )
    biomass = next(
        claim
        for claim in packets["policy-indicator-hokkaido-24"]["claims"]
        if claim["field"] == "series"
    )
    assert "原文値" in forest["review_note"]
    assert "2系列" in biomass["review_note"]
    assert "参照" in biomass["review_note"]
