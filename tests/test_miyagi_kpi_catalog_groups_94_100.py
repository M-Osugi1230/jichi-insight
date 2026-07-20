import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure13.json"
EVIDENCE = POLICY / "miyagi_kpi_measure13_evidence_packets.json"
CATALOGS = sorted(POLICY.glob("miyagi_kpi_catalog_*.json"))
ACTUALS = sorted(POLICY.glob("miyagi_kpi_actuals_measure*_2024.json"))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure13_values_and_evidence():
    groups = load(CATALOG)["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(94, 101))
    assert [item["series_number"] for item in series] == list(range(113, 120))
    by_series = {item["series_number"]: item for item in series}
    assert [value["value"] for value in by_series[113]["values"]] == [31, 584, 5000, None]
    assert [value["value"] for value in by_series[114]["values"]] == [3, 3, 60, None]
    assert [value["value"] for value in by_series[115]["values"]] == [91.5, 92.8, 100, None]
    assert by_series[116]["values"][2]["value_text_original"] == "3939"
    assert [value["value"] for value in by_series[117]["values"]] == [2759, 2924, 2428, None]
    assert [value["value"] for value in by_series[119]["values"]] == [22973, 22973, 27000, None]
    assert len(load(EVIDENCE)) == 7


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
