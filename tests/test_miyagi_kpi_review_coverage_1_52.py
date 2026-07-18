import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def reviewed_catalogs():
    catalogs = [
        load(path)
        for path in POLICY.glob("miyagi_kpi_catalog_*.json")
    ]
    return sorted(catalogs, key=lambda catalog: catalog["target_group_start"])


def reviewed_evidence_packets():
    paths = [
        *POLICY.glob("miyagi_kpi_measure*_evidence_packets.json"),
        *POLICY.glob("miyagi_kpi_pillar*_evidence_packets.json"),
    ]
    return [packet for path in paths for packet in load(path)]


def test_reviewed_groups_series_and_evidence_are_contiguous():
    groups = [group for catalog in reviewed_catalogs() for group in catalog["items"]]
    series = [entry for group in groups for entry in group["series"]]
    packets = reviewed_evidence_packets()
    assert [group["target_group_number"] for group in groups] == list(range(1, 107))
    assert [entry["series_number"] for entry in series] == list(range(1, 126))
    assert len({group["id"] for group in groups}) == 106
    assert len({entry["id"] for entry in series}) == 125
    assert len(packets) == 106
    assert len({packet["id"] for packet in packets}) == 106
    assert {packet["subject_id"] for packet in packets} == {
        group["id"] for group in groups
    }


def test_manifest_matches_reviewed_files():
    manifest = load(ROOT / "data/catalog/miyagi_policy_review_manifest.json")
    groups = [group for catalog in reviewed_catalogs() for group in catalog["items"]]
    series = [entry for group in groups for entry in group["series"]]
    packets = reviewed_evidence_packets()
    assert manifest["reviewed_target_group_count"] == len(groups) == 106
    assert manifest["reviewed_indicator_series_count"] == len(series) == 125
    assert manifest["kpi_evidence_packet_count"] == len(packets) == 106
    assert manifest["remaining_target_group_count"] == 22
    assert manifest["remaining_indicator_series_count"] == 24
