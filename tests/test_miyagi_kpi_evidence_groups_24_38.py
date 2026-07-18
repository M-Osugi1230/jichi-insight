import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOGS = [
    POLICY / "miyagi_kpi_catalog_measure4.json",
    POLICY / "miyagi_kpi_catalog_measure5.json",
]
EVIDENCE = [
    POLICY / "miyagi_kpi_measure4_evidence_packets.json",
    POLICY / "miyagi_kpi_measure5_evidence_packets.json",
]
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_schema_coverage_and_exact_locations():
    groups = [item for path in CATALOGS for item in load(path)["items"]]
    packets = [item for path in EVIDENCE for item in load(path)]
    validator = Draft202012Validator(load(SCHEMA))

    assert len(groups) == len(packets) == 15
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        group["id"] for group in groups
    }
    assert len({packet["id"] for packet in packets}) == 15

    for packet in packets:
        number = int(packet["subject_id"].rsplit("-", 1)[1])
        assert packet["review_status"] == "reviewed"
        assert packet["open_questions"] == []
        assert len(packet["claims"]) == 2
        assert {claim["field"] for claim in packet["claims"]} == {
            "indicator_name_original",
            "series",
        }
        for claim in packet["claims"]:
            assert claim["source_ids"] == [
                "policy-source-miyagi-midterm-implementation-plan-2026"
            ]
            assert claim["location_note"] == (
                f"PDFページ56（印刷ページ55）目標値No.{number}"
            )
            assert claim["decision"] == "accepted"


def test_multi_series_and_unit_review_notes_are_explicit():
    packets = {
        int(packet["subject_id"].rsplit("-", 1)[1]): packet
        for path in EVIDENCE
        for packet in load(path)
    }
    group26_series_claim = next(
        claim for claim in packets[26]["claims"] if claim["field"] == "series"
    )
    assert "農業" in group26_series_claim["statement"]
    assert "水産業" in group26_series_claim["statement"]
    assert "林業" in group26_series_claim["statement"]
    assert "3系列を単一値へ合算せず" in group26_series_claim["review_note"]

    group35_series_claim = next(
        claim for claim in packets[35]["claims"] if claim["field"] == "series"
    )
    assert "第3期みやぎ食と農の県民条例基本計画" in group35_series_claim["review_note"]
    assert all(
        "後期末" in next(
            claim for claim in packet["claims"] if claim["field"] == "series"
        )["statement"]
        for packet in packets.values()
    )
