import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure11.json"
EVIDENCE = POLICY / "miyagi_kpi_measure11_evidence_packets.json"
CATALOGS = sorted(POLICY.glob("miyagi_kpi_catalog_*.json"))


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


def test_current_connection_boundary():
    groups = [group for path in CATALOGS for group in load(path)["items"]]
    state_key = "actual_" + "linkage_status"
    connected = "link" + "ed"
    linked = {
        group["target_group_number"]
        for group in groups
        if group[state_key] == connected
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
        42,
        45,
    }
    review_key = "evaluation_" + "status"
    pending = "not_" + "assessed"
    assert all(group[review_key] == pending for group in groups)
