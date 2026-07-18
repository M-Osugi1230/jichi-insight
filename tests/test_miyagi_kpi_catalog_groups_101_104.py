import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure14.json"
EVIDENCE = POLICY / "miyagi_kpi_measure14_evidence_packets.json"
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
    POLICY / "miyagi_kpi_catalog_measure13.json",
    CATALOG,
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure14_catalog_matches_schema_and_sequences():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(CATALOG_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(catalog)) == []
    groups = catalog["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(101, 105))
    assert [item["series_number"] for item in series] == list(range(120, 124))
    assert all(group["scope_number"] == 14 for group in groups)
    assert all(group["source_page"] == 59 for group in groups)


def test_measure14_values_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    series = {
        group["series"][0]["series_number"]: group["series"][0]
        for group in groups.values()
    }
    assert [value["value"] for value in series[120]["values"]] == [
        105,
        115,
        121,
        None,
    ]
    assert [value["value"] for value in series[121]["values"]] == [
        95.0,
        96.1,
        92,
        None,
    ]
    assert [value["value"] for value in series[122]["values"]] == [
        11583,
        11385,
        10000,
        None,
    ]
    assert [value["value"] for value in series[123]["values"]] == [47, 47, 40, None]


def test_direction_and_period_boundaries_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert (
        groups[102]["series"][0]["values"][2]["value"]
        < groups[102]["series"][0]["values"][1]["value"]
    )
    assert (
        groups[103]["series"][0]["values"][2]["value"]
        < groups[103]["series"][0]["values"][1]["value"]
    )
    assert (
        groups[104]["series"][0]["values"][0]["value"]
        == groups[104]["series"][0]["values"][1]["value"]
    )
    assert [
        value["period_original"] for value in groups[104]["series"][0]["values"][:2]
    ] == ["R5", "R6"]
    for group in groups.values():
        late = group["series"][0]["values"][3]
        assert late["value"] is None
        assert late["status"] == "not_set"
        assert late["value_text_original"] == "-"


def test_measure14_evidence_covers_all_groups():
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 4
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        f"policy-target-miyagi-{number}" for number in range(101, 105)
    }


def test_all_reviewed_batches_form_104_groups_and_123_series():
    groups = [group for path in ALL_CATALOGS for group in load(path)["items"]]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(1, 105))
    assert [item["series_number"] for item in series] == list(range(1, 124))
    assert all(group["actual_linkage_status"] == "not_linked" for group in groups)
    assert all(group["evaluation_status"] == "not_assessed" for group in groups)
