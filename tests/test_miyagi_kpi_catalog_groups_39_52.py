import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
CATALOGS = [
    POLICY / "miyagi_kpi_catalog_pillar2.json",
    POLICY / "miyagi_kpi_catalog_measure6.json",
    POLICY / "miyagi_kpi_catalog_measure7.json",
]
EVIDENCE = [
    POLICY / "miyagi_kpi_pillar2_evidence_packets.json",
    POLICY / "miyagi_kpi_measure6_evidence_packets.json",
    POLICY / "miyagi_kpi_measure7_evidence_packets.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def groups():
    return [item for path in CATALOGS for item in load(path)["items"]]


def test_schema_sequence_scope_and_r7():
    validator = Draft202012Validator(load(SCHEMA), format_checker=FormatChecker())
    assert all(list(validator.iter_errors(load(path))) == [] for path in CATALOGS)
    items = groups()
    series = [entry for item in items for entry in item["series"]]
    assert [item["target_group_number"] for item in items] == list(range(39, 53))
    assert [entry["series_number"] for entry in series] == list(range(41, 58))
    assert [(item["scope_type"], item["scope_number"]) for item in items] == (
        [("pillar", 2)] * 2 + [("measure", 6)] * 5 + [("measure", 7)] * 7
    )
    assert all(item["source_page"] == 57 for item in items)
    r7_values = [
        value
        for entry in series
        for value in entry["values"]
        if value["period_original"] == "R7"
    ]
    assert len(r7_values) == 5
    assert all(value["period_year"] == 2025 for value in r7_values)


def test_multi_series_and_target_boundaries():
    items = {item["target_group_number"]: item for item in groups()}
    assert [entry["series_number"] for entry in items[40]["series"]] == [42, 43]
    assert [entry["series_number"] for entry in items[42]["series"]] == [45, 46]
    assert [entry["series_number"] for entry in items[49]["series"]] == [53, 54]
    assert items[39]["target_setting_status"] == "set"
    assert items[40]["target_setting_status"] == "set"
    assert all(
        item["target_setting_status"] == "partially_set"
        for number, item in items.items()
        if number >= 41
    )
    assert all(
        series["values"][3]["status"] == "not_set"
        for number, item in items.items()
        if number >= 41
        for series in item["series"]
    )
    assert items[39]["series"][0]["values"][3]["value"] == 1.6
    assert items[40]["series"][1]["values"][3]["value"] == 90.0


def test_cumulative_zero_and_non_monotonic_values_are_preserved():
    items = {item["target_group_number"]: item for item in groups()}
    assert items[44]["series"][0]["aggregation_scope"] == "cumulative_to_date"
    assert items[46]["series"][0]["aggregation_scope"] == "cumulative_to_date"
    zero = items[45]["series"][0]["values"][2]
    assert (zero["status"], zero["value"], zero["value_text_original"]) == (
        "numeric",
        0,
        "0",
    )
    for number in [40, 42, 49, 51]:
        assert any(
            series["values"][2]["value"] < series["values"][1]["value"]
            for series in items[number]["series"]
        )
        assert items[number]["comparability_note_original"] is not None


def test_evidence_and_review_status_are_complete():
    items = groups()
    packets = [packet for path in EVIDENCE for packet in load(path)]
    validator = Draft202012Validator(
        load(ROOT / "schemas/evidence_packet.schema.json")
    )
    assert len(packets) == 14
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        item["id"] for item in items
    }
    assert all(item["actual_linkage_status"] == "not_linked" for item in items)
    assert all(item["evaluation_status"] == "not_assessed" for item in items)
