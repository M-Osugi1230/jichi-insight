import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure11.json"
EVIDENCE = POLICY / "miyagi_kpi_measure11_evidence_packets.json"
CATALOGS = sorted(POLICY.glob("miyagi_kpi_catalog_*.json"))
ACTUALS = sorted(POLICY.glob("miyagi_kpi_actuals_measure*_2024.json"))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure11_values_and_evidence():
    groups = load(CATALOG)["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == [81, 82, 83, 84]
    assert [item["series_number"] for item in series] == [99, 100, 101, 102, 103]
    expected = {
        99: [77.3, 76.5, 79.1, None],
        100: [81.4, 82.5, 82.6, None],
        101: [80.0, 80.0, 100, None],
        102: [55831, 47766, 72000, None],
        103: [373, 752, 790, None],
    }
    for item in series:
        assert [value["value"] for value in item["values"]] == expected[item["series_number"]]
    assert len(load(EVIDENCE)) == 4


def test_catalog_connections_match_reviewed_actual_records():
    groups = [group for path in CATALOGS for group in load(path)["items"]]
    connected_groups = {
        group["target_group_number"]
        for group in groups
        if group["actual_linkage_status"] == "linked"
    }
    expected_groups = {
        int(record["target_group_id"].rsplit("-", 1)[1])
        for path in ACTUALS
        for record in load(path)["records"]
        if record["linkage_status"] == "linked"
    }
    assert connected_groups == expected_groups
    assert all(group["evaluation_status"] == "not_assessed" for group in groups)
