import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = (
    ROOT
    / "data/entities/policy/"
    "hokkaido_indicator_children_parenting_evidence_packets.json"
)
CATALOG_PATH = (
    ROOT
    / "data/entities/policy/"
    "hokkaido_indicator_catalog_children_parenting.json"
)
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_children_parenting_evidence_packets_match_schema():
    packets = load(EVIDENCE_PATH)
    validator = Draft202012Validator(load(SCHEMA_PATH))

    assert len(packets) == 7
    assert all(
        list(validator.iter_errors(packet)) == []
        for packet in packets
    )


def test_every_children_parenting_indicator_has_one_evidence_packet():
    packets = load(EVIDENCE_PATH)
    catalog = load(CATALOG_PATH)

    assert {packet["subject_id"] for packet in packets} == {
        item["id"] for item in catalog["items"]
    }
    assert len({packet["id"] for packet in packets}) == 7
    assert all(packet["subject_type"] == "kpi" for packet in packets)
    assert all(packet["review_status"] == "reviewed" for packet in packets)


def test_evidence_uses_exact_source_pages_and_accepted_claims():
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
                "policy-source-hokkaido-indicators-children-parenting"
            ]
            assert (
                f"PDFページ{item['source_page']}"
                in claim["location_note"]
            )
            assert claim["decision"] == "accepted"


def test_evidence_preserves_special_cases():
    packets = {
        packet["subject_id"]: packet
        for packet in load(EVIDENCE_PATH)
    }

    fertility = next(
        claim
        for claim in packets["policy-indicator-hokkaido-46"]["claims"]
        if claim["field"] == "series"
    )
    waiting_children = next(
        claim
        for claim in packets["policy-indicator-hokkaido-49"]["claims"]
        if claim["field"] == "series"
    )
    parental_leave_name = next(
        claim
        for claim in packets["policy-indicator-hokkaido-50"]["claims"]
        if claim["field"] == "indicator_name_original"
    )
    parental_leave_series = next(
        claim
        for claim in packets["policy-indicator-hokkaido-50"]["claims"]
        if claim["field"] == "series"
    )
    foster_care = next(
        claim
        for claim in packets["policy-indicator-hokkaido-52"]["claims"]
        if claim["field"] == "series"
    )

    assert "推測で数値化せず" in fertility["review_note"]
    assert "0は欠損補完ではなく" in waiting_children["review_note"]
    assert "2政策分野" in parental_leave_name["review_note"]
    assert "男女を別系列" in parental_leave_series["review_note"]
    assert "条件目標" in foster_care["review_note"]
