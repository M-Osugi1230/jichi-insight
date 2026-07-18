import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
CATALOGS = [
    POLICY / "miyagi_kpi_catalog_measure4.json",
    POLICY / "miyagi_kpi_catalog_measure5.json",
]
EVIDENCE_FILES = [
    POLICY / "miyagi_kpi_measure4_evidence_packets.json",
    POLICY / "miyagi_kpi_measure5_evidence_packets.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_schema_coverage_and_official_locations():
    groups = {
        group["id"]: group
        for path in CATALOGS
        for group in load(path)["items"]
    }
    packets = [packet for path in EVIDENCE_FILES for packet in load(path)]
    validator = Draft202012Validator(load(SCHEMA))

    assert len(groups) == 15
    assert len(packets) == 15
    assert {packet["subject_id"] for packet in packets} == set(groups)
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)

    for packet in packets:
        group = groups[packet["subject_id"]]
        assert packet["review_status"] == "reviewed"
        assert packet["open_questions"] == []
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == [
                "policy-source-miyagi-midterm-implementation-plan-2026"
            ]
            assert claim["decision"] == "accepted"
            assert claim["location_note"] == (
                "PDFページ56（印刷ページ55）"
                f"目標値No.{group['target_group_number']}"
            )


def test_evidence_preserves_multi_series_and_revised_values():
    packets = {
        int(packet["subject_id"].rsplit("-", 1)[1]): packet
        for path in EVIDENCE_FILES
        for packet in load(path)
    }

    group26 = next(claim for claim in packets[26]["claims"] if claim["field"] == "series")
    assert "農業" in group26["statement"]
    assert "現況値154人（R6）" in group26["statement"]
    assert "水産業" in group26["statement"]
    assert "現況値24人（R6）" in group26["statement"]
    assert "中期末54人（R9）" in group26["statement"]
    assert "林業" in group26["statement"]
    assert "現況値69人（R5）" in group26["statement"]
    assert "複数系列を一つの値へ圧縮しない" in group26["review_note"]

    assert "現況値67件（R6）" in next(
        claim for claim in packets[29]["claims"] if claim["field"] == "series"
    )["statement"]
    assert "中期末4,900経営体（R9）" in next(
        claim for claim in packets[31]["claims"] if claim["field"] == "series"
    )["statement"]
    assert "現況値377.8万人（R6）" in next(
        claim for claim in packets[36]["claims"] if claim["field"] == "series"
    )["statement"]


def test_evidence_records_non_normalization_boundaries():
    packets = {
        int(packet["subject_id"].rsplit("-", 1)[1]): packet
        for path in EVIDENCE_FILES
        for packet in load(path)
    }
    series_claims = {
        number: next(claim for claim in packet["claims"] if claim["field"] == "series")
        for number, packet in packets.items()
    }

    assert "公式値を補正しない" in series_claims[27]["review_note"]
    assert "公式値を補正しない" in series_claims[31]["review_note"]
    assert "原文へ追加しない" in series_claims[32]["review_note"]
    assert "中期末21400台/日" in series_claims[32]["statement"]
    assert "原文へ追加しない" in series_claims[34]["review_note"]
    assert "中期末4126万トン" in series_claims[34]["statement"]
    assert "単位を推測で補完しない" in series_claims[35]["review_note"]
    assert "後期末の『-』を0へ変換しない" in series_claims[35]["review_note"]

    assert all(
        "後期末の『-』を0へ変換しない" in claim["review_note"]
        for claim in series_claims.values()
    )
