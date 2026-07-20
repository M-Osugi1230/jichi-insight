import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_pillar3.json"
EVIDENCE = POLICY / "miyagi_kpi_pillar3_evidence_packets.json"
CATALOGS = sorted(POLICY.glob("miyagi_kpi_catalog_*.json"))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_pillar3_values_and_evidence():
    groups = load(CATALOG)["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == [69, 70, 71]
    assert [item["series_number"] for item in series] == [86, 87, 88, 89]
    assert [value["value"] for value in series[0]["values"]] == [-1452, -2989, 0, 0]
    assert [value["value"] for value in series[2]["values"]] == [72.90, 72.91, 73.46, 73.76]
    assert [value["value"] for value in series[3]["values"]] == [75.10, 74.74, 75.67, 75.78]
    assert len(load(EVIDENCE)) == 3


def test_linkage_boundary_through_measure5():
    groups = [group for path in CATALOGS for group in load(path)["items"]]
    linked = {
        group["target_group_number"]
        for group in groups
        if group["actual_linkage_status"] == "linked"
    }
    assert linked == {
        4,
        5,
        6,
        8,
        9,
        10,
        11,
        12,
        14,
        *range(15, 32),
        33,
        36,
        37,
        38,
    }
    assert all(group["evaluation_status"] == "not_assessed" for group in groups)
