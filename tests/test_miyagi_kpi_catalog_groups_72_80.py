import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure10.json"
EVIDENCE = POLICY / "miyagi_kpi_measure10_evidence_packets.json"
CATALOGS = sorted(POLICY.glob("miyagi_kpi_catalog_*.json"))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure10_values_and_evidence():
    groups = load(CATALOG)["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(72, 81))
    assert [item["series_number"] for item in series] == list(range(90, 99))
    expected = {
        90: (7602, 7602, 8430, None),
        91: (68026, 67759, 71000, None),
        92: (2.29, 2.39, 2.70, None),
        93: (43, 50, 60, None),
        94: (276, 276, 363, None),
        95: (806, 961, 1330, None),
        96: (491, 492, 500, None),
        97: (16, 16, 30, None),
        98: (16586, 16586, 20000, None),
    }
    for item in series:
        assert tuple(value["value"] for value in item["values"]) == expected[item["series_number"]]
    assert len(load(EVIDENCE)) == 9


def test_linkage_boundary_through_measure3():
    groups = [group for path in CATALOGS for group in load(path)["items"]]
    linked = {
        group["target_group_number"]
        for group in groups
        if group["actual_linkage_status"] == "linked"
    }
    assert linked == {4, 5, 6, 8, 9, 10, 11, 12, 14, *range(15, 24)}
    assert all(group["evaluation_status"] == "not_assessed" for group in groups)
