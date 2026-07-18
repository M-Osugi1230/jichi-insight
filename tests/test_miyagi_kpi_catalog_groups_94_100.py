import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure13.json"
EVIDENCE = POLICY / "miyagi_kpi_measure13_evidence_packets.json"
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
    POLICY / "miyagi_kpi_catalog_measure12.json",
    CATALOG,
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure13_catalog_matches_schema_and_sequences():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(CATALOG_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(catalog)) == []
    groups = catalog["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(94, 101))
    assert [item["series_number"] for item in series] == list(range(113, 120))
    assert all(group["scope_number"] == 13 for group in groups)
    assert all(group["source_page"] == 59 for group in groups)


def test_official_values_and_source_text_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    series = {
        group["series"][0]["series_number"]: group["series"][0]
        for group in groups.values()
    }
    assert [value["value"] for value in series[113]["values"]] == [31, 584, 5000, None]
    assert [value["value"] for value in series[114]["values"]] == [3, 3, 60, None]
    assert [value["value"] for value in series[115]["values"]] == [
        91.5,
        92.8,
        100,
        None,
    ]
    assert series[116]["values"][2]["value_text_original"] == "3939"
    assert series[117]["values"][2]["value_text_original"] == "2428"
    assert [value["value"] for value in series[117]["values"]] == [
        2759,
        2924,
        2428,
        None,
    ]
    assert [value["value"] for value in series[119]["values"]] == [
        22973,
        22973,
        27000,
        None,
    ]


def test_cumulative_same_period_and_non_monotonic_boundaries():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert groups[94]["series"][0]["aggregation_scope"] == "cumulative_to_date"
    assert [
        value["period_original"] for value in groups[95]["series"][0]["values"][:2]
    ] == ["R6", "R6"]
    assert [
        value["period_original"] for value in groups[100]["series"][0]["values"][:2]
    ] == ["R5", "R5"]
    assert (
        groups[98]["series"][0]["values"][2]["value"]
        < groups[98]["series"][0]["values"][1]["value"]
    )
    assert "方向評価せず" in groups[98]["comparability_note_original"]
    for group in groups.values():
        late = group["series"][0]["values"][3]
        assert late["value"] is None
        assert late["status"] == "not_set"
        assert late["value_text_original"] == "-"


def test_measure13_evidence_covers_all_groups():
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 7
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        f"policy-target-miyagi-{number}" for number in range(94, 101)
    }


def test_all_reviewed_batches_form_100_groups_and_119_series():
    groups = [group for path in ALL_CATALOGS for group in load(path)["items"]]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(1, 101))
    assert [item["series_number"] for item in series] == list(range(1, 120))
    assert all(group["actual_linkage_status"] == "not_linked" for group in groups)
    assert all(group["evaluation_status"] == "not_assessed" for group in groups)
