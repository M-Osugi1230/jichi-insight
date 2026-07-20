import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure14.json"
EVIDENCE = POLICY / "miyagi_kpi_measure14_evidence_packets.json"
CATALOGS = sorted(POLICY.glob("miyagi_kpi_catalog_*.json"))
ACTUALS = sorted(POLICY.glob("miyagi_kpi_actuals_measure*_2024.json"))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure14_values_and_evidence():
    groups = load(CATALOG)["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(101, 105))
    assert [item["series_number"] for item in series] == list(range(120, 124))
    expected = {
        120: [105, 115, 121, None],
        121: [95.0, 96.1, 92, None],
        122: [11583, 11385, 10000, None],
        123: [47, 47, 40, None],
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
