import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG_PATHS = [
    POLICY / "miyagi_kpi_catalog_pillar1.json",
    POLICY / "miyagi_kpi_catalog_measure1.json",
    POLICY / "miyagi_kpi_catalog_measure2.json",
    POLICY / "miyagi_kpi_catalog_measure3.json",
    POLICY / "miyagi_kpi_catalog_measure4.json",
    POLICY / "miyagi_kpi_catalog_measure5.json",
]
EVIDENCE_PATHS = [
    POLICY / "miyagi_kpi_pillar1_evidence_packets.json",
    POLICY / "miyagi_kpi_measure1_evidence_packets.json",
    POLICY / "miyagi_kpi_measure2_evidence_packets.json",
    POLICY / "miyagi_kpi_measure3a_evidence_packets.json",
    POLICY / "miyagi_kpi_measure3b_evidence_packets.json",
    POLICY / "miyagi_kpi_measure4_evidence_packets.json",
    POLICY / "miyagi_kpi_measure5_evidence_packets.json",
]
MANIFEST = ROOT / "data/catalog/miyagi_policy_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_reviewed_catalogs_cover_groups_1_to_38_without_gaps_or_duplicates():
    groups = [group for path in CATALOG_PATHS for group in load(path)["items"]]
    group_numbers = [group["target_group_number"] for group in groups]

    assert group_numbers == list(range(1, 39))
    assert len(group_numbers) == len(set(group_numbers)) == 38
    assert [group["id"] for group in groups] == [
        f"policy-target-miyagi-{number}" for number in range(1, 39)
    ]


def test_reviewed_catalogs_cover_series_1_to_40_without_gaps_or_duplicates():
    groups = [group for path in CATALOG_PATHS for group in load(path)["items"]]
    series = [item for group in groups for item in group["series"]]
    series_numbers = [item["series_number"] for item in series]

    assert series_numbers == list(range(1, 41))
    assert len(series_numbers) == len(set(series_numbers)) == 40
    assert [item["id"] for item in series] == [
        f"policy-indicator-miyagi-{number}" for number in range(1, 41)
    ]


def test_every_reviewed_group_has_exactly_one_evidence_packet():
    groups = [group for path in CATALOG_PATHS for group in load(path)["items"]]
    packets = [packet for path in EVIDENCE_PATHS for packet in load(path)]
    group_ids = [group["id"] for group in groups]
    subject_ids = [packet["subject_id"] for packet in packets]

    assert len(packets) == 38
    assert subject_ids == group_ids
    assert len(subject_ids) == len(set(subject_ids)) == 38
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(packet["open_questions"] == [] for packet in packets)


def test_manifest_counts_equal_reviewed_files_and_remaining_scope():
    manifest = load(MANIFEST)
    groups = [group for path in CATALOG_PATHS for group in load(path)["items"]]
    series = [item for group in groups for item in group["series"]]
    packets = [packet for path in EVIDENCE_PATHS for packet in load(path)]

    assert manifest["reviewed_target_group_count"] == len(groups) == 38
    assert manifest["reviewed_indicator_series_count"] == len(series) == 40
    assert manifest["kpi_evidence_packet_count"] == len(packets) == 38
    assert manifest["remaining_target_group_count"] == 128 - len(groups) == 90
    assert manifest["remaining_indicator_series_count"] == 149 - len(series) == 109


def test_group_26_is_first_reviewed_multi_series_group():
    groups = [group for path in CATALOG_PATHS for group in load(path)["items"]]
    multi_series = [
        (group["target_group_number"], len(group["series"]))
        for group in groups
        if len(group["series"]) > 1
    ]
    assert multi_series == [(26, 3)]
