import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure15.json"
EVIDENCE = POLICY / "miyagi_kpi_measure15_evidence_packets.json"
CATALOG_SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure15_catalog_matches_schema_and_sequences():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(CATALOG_SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []
    groups = catalog["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(107, 114))
    assert [item["series_number"] for item in series] == list(range(126, 133))
    assert all(group["scope_number"] == 15 for group in groups)
    assert all(group["source_page"] == 60 for group in groups)


def test_measure15_values_units_and_periods_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    series = {
        group["series"][0]["series_number"]: group["series"][0]
        for group in groups.values()
    }
    assert [value["value"] for value in series[126]["values"]] == [33.0, 33.0, 60.0, None]
    assert [value["period_original"] for value in series[126]["values"][:2]] == ["R3", "R3"]
    assert [value["value"] for value in series[127]["values"]] == [3338, 3338, 6000, None]
    assert series[127]["unit_original"] == "ha/年"
    assert [value["value"] for value in series[128]["values"]] == [40420, 53050, 47041, None]
    assert series[128]["unit_original"] == "ＴＪ"
    assert series[131]["unit_original"] == "g/人･日"
    assert series[132]["unit_original"] == "千ｔ"


def test_measure15_direction_boundaries_and_missing_late_targets_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    value_pairs = {
        number: [value["value"] for value in groups[number]["series"][0]["values"][1:3]]
        for number in [109, 111, 112, 113]
    }
    assert value_pairs[109][0] > value_pairs[109][1]
    assert value_pairs[111][0] > value_pairs[111][1]
    assert value_pairs[112][0] < value_pairs[112][1]
    assert value_pairs[113][0] > value_pairs[113][1]
    for group in groups.values():
        late = group["series"][0]["values"][3]
        assert late["value"] is None
        assert late["status"] == "not_set"
        assert late["value_text_original"] == "-"
        assert group["actual_linkage_status"] == "linked"
        assert group["evaluation_status"] == "not_assessed"


def test_measure15_evidence_covers_all_groups():
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 7
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        f"policy-target-miyagi-{number}" for number in range(107, 114)
    }
    assert all(packet["review_status"] == "reviewed" for packet in packets)
