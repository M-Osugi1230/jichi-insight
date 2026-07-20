import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure12.json"
EVIDENCE = POLICY / "miyagi_kpi_measure12_evidence_packets.json"
CATALOGS = sorted(POLICY.glob("miyagi_kpi_catalog_*.json"))
ACTUALS = sorted(POLICY.glob("miyagi_kpi_actuals_measure*_2024.json"))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure12_values_and_evidence():
    groups = load(CATALOG)["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(85, 94))
    assert [item["series_number"] for item in series] == list(range(104, 113))
    by_series = {item["series_number"]: item for item in series}
    assert [value["value"] for value in by_series[104]["values"]] == [32.2, 31.9, 29.0, None]
    assert by_series[105]["values"][2]["value_text_original"] == "73.96"
    assert [value["value"] for value in by_series[106]["values"]] == [17.6, 17.1, 12.1, None]
    assert [value["value"] for value in by_series[107]["values"]] == [108, 108, 108, None]
    assert len(load(EVIDENCE)) == 9


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
