import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOGS = [
    POLICY / "miyagi_kpi_catalog_pillar1.json",
    POLICY / "miyagi_kpi_catalog_measure1.json",
    POLICY / "miyagi_kpi_catalog_measure2.json",
    POLICY / "miyagi_kpi_catalog_measure3.json",
]
EVIDENCE = [
    POLICY / "miyagi_kpi_pillar1_evidence_packets.json",
    POLICY / "miyagi_kpi_measure1_evidence_packets.json",
    POLICY / "miyagi_kpi_measure2_evidence_packets.json",
    POLICY / "miyagi_kpi_measure3a_evidence_packets.json",
    POLICY / "miyagi_kpi_measure3b_evidence_packets.json",
]
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_schema_coverage_and_locations():
    groups = [item for path in CATALOGS for item in load(path)["items"]]
    packets = [item for path in EVIDENCE for item in load(path)]
    validator = Draft202012Validator(load(SCHEMA))

    assert len(packets) == 23
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        group["id"] for group in groups
    }
    assert len({packet["id"] for packet in packets}) == 23

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
