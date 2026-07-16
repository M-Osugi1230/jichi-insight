import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = (
    ROOT / "data/entities/policy/hokkaido_indicator_food_evidence_packets.json"
)
EVIDENCE_SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"
CATALOG_PATH = ROOT / "data/entities/policy/hokkaido_indicator_catalog_food.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_food_indicator_evidence_packets_match_schema():
    packets = load(EVIDENCE_PATH)
    schema = load(EVIDENCE_SCHEMA_PATH)
    validator = Draft202012Validator(schema)

    assert len(packets) == 12
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)


def test_every_reviewed_food_indicator_has_one_evidence_packet():
    packets = load(EVIDENCE_PATH)
    catalog = load(CATALOG_PATH)

    assert {packet["subject_id"] for packet in packets} == {
        item["id"] for item in catalog["items"]
    }
    assert len({packet["id"] for packet in packets}) == 12
    assert all(packet["subject_type"] == "kpi" for packet in packets)
    assert all(packet["review_status"] == "reviewed" for packet in packets)


def test_evidence_claims_use_the_food_pdf_and_exact_page_locations():
    packets = load(EVIDENCE_PATH)
    catalog = load(CATALOG_PATH)
    items_by_id = {item["id"]: item for item in catalog["items"]}

    for packet in packets:
        item = items_by_id[packet["subject_id"]]
        assert len(packet["claims"]) == 2
        assert packet["open_questions"] == []
        for claim in packet["claims"]:
            assert claim["source_ids"] == [catalog["source_id"]]
            assert f"PDFページ{item['source_page']}" in claim["location_note"]
            assert claim["decision"] == "accepted"


def test_evidence_preserves_unset_targets_and_comparability_warnings():
    packets = load(EVIDENCE_PATH)
    packets_by_subject = {packet["subject_id"]: packet for packet in packets}

    for indicator_number in (3, 6, 10):
        packet = packets_by_subject[f"policy-indicator-hokkaido-{indicator_number}"]
        series_claim = next(
            claim for claim in packet["claims"] if claim["field"] == "series"
        )
        assert "未設定" in series_claim["statement"]
        assert series_claim["review_note"] == "未設定値を0へ変換しない。"

    for indicator_number in (7, 9):
        packet = packets_by_subject[f"policy-indicator-hokkaido-{indicator_number}"]
        series_claim = next(
            claim for claim in packet["claims"] if claim["field"] == "series"
        )
        assert "単純比較できない" in series_claim["review_note"]
