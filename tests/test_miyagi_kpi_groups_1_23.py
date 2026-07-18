import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/entities/policy/miyagi_kpi_catalog_groups_1_23.json"
EVIDENCE = ROOT / "data/entities/policy/miyagi_kpi_groups_1_23_evidence_packets.json"
SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_miyagi_kpi_groups_1_23_match_schema_and_sequence():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []

    items = catalog["items"]
    assert catalog["target_group_number_start"] == 1
    assert catalog["target_group_number_end"] == 23
    assert catalog["series_number_start"] == 1
    assert catalog["series_number_end"] == 23
    assert [item["target_group_number"] for item in items] == list(range(1, 24))
    assert [item["series_number"] for item in items] == list(range(1, 24))
    assert len({item["id"] for item in items}) == 23


def test_miyagi_kpi_scope_boundaries_match_source_index():
    items = load(CATALOG)["items"]

    assert [item["target_group_number"] for item in items if item["scope_type"] == "pillar"] == [1, 2, 3]
    assert [item["target_group_number"] for item in items if item["measure_id"] == "policy-measure-miyagi-1"] == list(range(4, 10))
    assert [item["target_group_number"] for item in items if item["measure_id"] == "policy-measure-miyagi-2"] == list(range(10, 15))
    assert [item["target_group_number"] for item in items if item["measure_id"] == "policy-measure-miyagi-3"] == list(range(15, 24))


def test_miyagi_kpi_values_preserve_unset_final_targets_and_cumulative_scope():
    items = load(CATALOG)["items"]

    fully_set = [item["target_group_number"] for item in items if item["target_setting_status"] == "set"]
    partially_set = [item["target_group_number"] for item in items if item["target_setting_status"] == "partially_set"]
    assert fully_set == [1, 2, 3]
    assert partially_set == list(range(4, 24))

    for item in items[3:]:
        final_value = item["series"][0]["values"][3]
        assert final_value["role"] == "final_target"
        assert final_value["value"] is None
        assert final_value["status"] == "not_set"
        assert final_value["value_text_original"] == "-"

    cumulative_groups = {
        item["target_group_number"]
        for item in items
        if item["series"][0]["values"][0]["aggregation_scope"] == "cumulative_to_date"
    }
    assert cumulative_groups == {4, 5, 7, 9, 23}


def test_miyagi_kpi_evidence_is_one_packet_per_reviewed_indicator():
    items = load(CATALOG)["items"]
    evidence = load(EVIDENCE)

    assert len(evidence) == len(items) == 23
    assert {packet["subject_id"] for packet in evidence} == {item["id"] for item in items}
    assert all(packet["review_status"] == "reviewed" for packet in evidence)
    assert all(len(packet["claims"]) == 2 for packet in evidence)
