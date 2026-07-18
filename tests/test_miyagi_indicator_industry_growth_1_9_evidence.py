import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_indicator_catalog_industry_growth_1_9.json"
EVIDENCE = POLICY / "miyagi_indicator_industry_growth_1_9_evidence_packets.json"
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_schema_coverage_and_source_location():
    catalog = load(CATALOG)
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(SCHEMA))
    items = {item["id"]: item for item in catalog["items"]}

    assert len(packets) == 9
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == set(items)
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(packet["open_questions"] == [] for packet in packets)

    for packet in packets:
        item = items[packet["subject_id"]]
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == [
                "policy-source-miyagi-midterm-implementation-plan-2026"
            ]
            assert "PDFページ56（冊子55ページ）" in claim["location_note"]
            assert claim["decision"] == "accepted"
        assert f"目標値No.{item['target_group_number']}" in packet["claims"][0][
            "location_note"
        ]


def test_evidence_preserves_hyphen_and_cumulative_boundaries():
    packets = {
        int(packet["subject_id"].rsplit("-", 1)[1]): packet
        for packet in load(EVIDENCE)
    }

    for number in range(4, 10):
        values_claim = next(
            claim
            for claim in packets[number]["claims"]
            if claim["field"] == "values"
        )
        assert "後期末目標-" in values_claim["statement"]
        assert "未設定" in values_claim["statement"]
        assert "補完" in values_claim["review_note"] or "目標未設定" in values_claim[
            "review_note"
        ]

    for number in (4, 5, 7, 9):
        values_claim = next(
            claim
            for claim in packets[number]["claims"]
            if claim["field"] == "values"
        )
        assert "累計値は単年度値へ変換せず" in values_claim["review_note"]
