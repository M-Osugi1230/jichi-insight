import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure12.json"
EVIDENCE = POLICY / "miyagi_kpi_measure12_evidence_packets.json"
CATALOG_SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
ALL_CATALOGS = [
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
    CATALOG,
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure12_catalog_matches_schema_and_sequences():
    catalog = load(CATALOG)
    validator = Draft202012Validator(load(CATALOG_SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(catalog)) == []
    groups = catalog["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(85, 94))
    assert [item["series_number"] for item in series] == list(range(104, 113))
    assert all(group["scope_number"] == 12 for group in groups)
    assert all(group["source_page"] == 59 for group in groups)


def test_official_values_precision_and_rate_boundaries_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    series = {group["series"][0]["series_number"]: group["series"][0] for group in groups.values()}
    assert [value["value"] for value in series[104]["values"]] == [32.2, 31.9, 29.0, None]
    assert series[105]["values"][2]["value_text_original"] == "73.96"
    assert series[106]["unit_original"] == "人口10万対"
    assert [value["value"] for value in series[106]["values"]] == [17.6, 17.1, 12.1, None]
    assert [value["value"] for value in series[107]["values"]] == [108, 108, 108, None]
    assert "方向評価" in groups[85]["comparability_note_original"]
    assert "死亡者数へ変換しない" in groups[87]["comparability_note_original"]


def test_cumulative_and_same_period_boundaries_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert {
        number for number, group in groups.items()
        if group["series"][0]["aggregation_scope"] == "cumulative_to_date"
    } == {90, 91, 92, 93}
    assert [value["period_original"] for value in groups[89]["series"][0]["values"][:2]] == ["R6", "R6"]
    assert [value["period_original"] for value in groups[92]["series"][0]["values"][:2]] == ["R5", "R5"]
    assert [value["period_original"] for value in groups[93]["series"][0]["values"][:2]] == ["R5", "R5"]
    for group in groups.values():
        late = group["series"][0]["values"][3]
        assert late == {
            "role": "late_target",
            "period_original": "R12",
            "period_year": 2030,
            "value": None,
            "status": "not_set",
            "value_text_original": "-",
        }


def test_measure12_evidence_covers_all_groups():
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 9
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        f"policy-target-miyagi-{number}" for number in range(85, 94)
    }
    assert all(packet["review_status"] == "reviewed" for packet in packets)


def test_all_reviewed_batches_form_93_groups_and_112_series():
    groups = [group for path in ALL_CATALOGS for group in load(path)["items"]]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(1, 94))
    assert [item["series_number"] for item in series] == list(range(1, 113))
    assert all(group["actual_linkage_status"] == "not_linked" for group in groups)
    assert all(group["evaluation_status"] == "not_assessed" for group in groups)
