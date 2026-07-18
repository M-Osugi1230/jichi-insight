import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOGS = [
    POLICY / "miyagi_kpi_catalog_pillar1.json",
    POLICY / "miyagi_kpi_catalog_measure1.json",
    POLICY / "miyagi_kpi_catalog_measure2.json",
    POLICY / "miyagi_kpi_catalog_measure3.json",
    POLICY / "miyagi_kpi_catalog_measure4.json",
    POLICY / "miyagi_kpi_catalog_measure5.json",
    POLICY / "miyagi_kpi_catalog_pillar2.json",
    POLICY / "miyagi_kpi_catalog_measure6.json",
    POLICY / "miyagi_kpi_catalog_measure7.json",
    POLICY / "miyagi_kpi_catalog_measure8.json",
    POLICY / "miyagi_kpi_catalog_measure9.json",
    POLICY / "miyagi_kpi_catalog_pillar3.json",
    POLICY / "miyagi_kpi_catalog_measure10.json",
    POLICY / "miyagi_kpi_catalog_measure11.json",
    POLICY / "miyagi_kpi_catalog_measure12.json",
    POLICY / "miyagi_kpi_catalog_measure13.json",
]
EVIDENCE = [
    POLICY / "miyagi_kpi_pillar1_evidence_packets.json",
    POLICY / "miyagi_kpi_measure1_evidence_packets.json",
    POLICY / "miyagi_kpi_measure2_evidence_packets.json",
    POLICY / "miyagi_kpi_measure3a_evidence_packets.json",
    POLICY / "miyagi_kpi_measure3b_evidence_packets.json",
    POLICY / "miyagi_kpi_measure4_evidence_packets.json",
    POLICY / "miyagi_kpi_measure5_evidence_packets.json",
    POLICY / "miyagi_kpi_pillar2_evidence_packets.json",
    POLICY / "miyagi_kpi_measure6_evidence_packets.json",
    POLICY / "miyagi_kpi_measure7_evidence_packets.json",
    POLICY / "miyagi_kpi_measure8_evidence_packets.json",
    POLICY / "miyagi_kpi_measure9_evidence_packets.json",
    POLICY / "miyagi_kpi_pillar3_evidence_packets.json",
    POLICY / "miyagi_kpi_measure10_evidence_packets.json",
    POLICY / "miyagi_kpi_measure11_evidence_packets.json",
    POLICY / "miyagi_kpi_measure12_evidence_packets.json",
    POLICY / "miyagi_kpi_measure13_evidence_packets.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_reviewed_groups_series_and_evidence_are_contiguous():
    groups = [item for path in CATALOGS for item in load(path)["items"]]
    series = [entry for group in groups for entry in group["series"]]
    packets = [packet for path in EVIDENCE for packet in load(path)]
    assert [group["target_group_number"] for group in groups] == list(range(1, 101))
    assert [entry["series_number"] for entry in series] == list(range(1, 120))
    assert len({group["id"] for group in groups}) == 100
    assert len({entry["id"] for entry in series}) == 119
    assert len(packets) == 100
    assert len({packet["id"] for packet in packets}) == 100
    assert {packet["subject_id"] for packet in packets} == {
        group["id"] for group in groups
    }


def test_manifest_matches_reviewed_files():
    manifest = load(ROOT / "data/catalog/miyagi_policy_review_manifest.json")
    groups = [item for path in CATALOGS for item in load(path)["items"]]
    series = [entry for group in groups for entry in group["series"]]
    packets = [packet for path in EVIDENCE for packet in load(path)]
    assert manifest["reviewed_target_group_count"] == len(groups) == 100
    assert manifest["reviewed_indicator_series_count"] == len(series) == 119
    assert manifest["kpi_evidence_packet_count"] == len(packets) == 100
    assert manifest["remaining_target_group_count"] == 28
    assert manifest["remaining_indicator_series_count"] == 30
