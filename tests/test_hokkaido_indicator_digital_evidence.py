import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = (
    ROOT
    / "data/entities/policy/hokkaido_indicator_digital_evidence_packets.json"
)
CATALOG_PATH = (
    ROOT / "data/entities/policy/hokkaido_indicator_catalog_digital.json"
)
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_digital_evidence_packets_match_schema():
    packets = load(EVIDENCE_PATH)
    validator = Draft202012Validator(load(SCHEMA_PATH))

    assert len(packets) == 3
    assert all(
        list(validator.iter_errors(packet)) == []
        for packet in packets
    )


def test_every_digital_indicator_has_one_evidence_packet():
    packets = load(EVIDENCE_PATH)
    catalog = load(CATALOG_PATH)

    assert {packet["subject_id"] for packet in packets} == {
        item["id"] for item in catalog["items"]
    }
    assert len({packet["id"] for packet in packets}) == 3
    assert all(packet["subject_type"] == "kpi" for packet in packets)
    assert all(packet["review_status"] == "reviewed" for packet in packets)


def test_evidence_uses_exact_source_pages():
    packets = load(EVIDENCE_PATH)
    items = {
        item["id"]: item
        for item in load(CATALOG_PATH)["items"]
    }

    for packet in packets:
        item = items[packet["subject_id"]]
        assert packet["open_questions"] == []
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == [
                "policy-source-hokkaido-indicators-digital"
            ]
            assert (
                f"PDFページ{item['source_page']}"
                in claim["location_note"]
            )
            assert claim["decision"] == "accepted"


def test_evidence_preserves_cumulative_and_missing_value_boundaries():
    packets = {
        packet["subject_id"]: packet
        for packet in load(EVIDENCE_PATH)
    }
    indicator30 = next(
        claim
        for claim in packets["policy-indicator-hokkaido-30"]["claims"]
        if claim["field"] == "series"
    )
    indicator31 = next(
        claim
        for claim in packets["policy-indicator-hokkaido-31"]["claims"]
        if claim["field"] == "series"
    )
    indicator32 = next(
        claim
        for claim in packets["policy-indicator-hokkaido-32"]["claims"]
        if claim["field"] == "series"
    )

    assert "5年間累計" in indicator30["statement"]
    assert "10年間累計" in indicator30["statement"]
    assert "達成率" in indicator30["review_note"]
    assert "0へ変換しない" in indicator31["review_note"]
    assert "区別" in indicator32["review_note"]
