import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
CATALOGS = [
    POLICY / "miyagi_kpi_catalog_measure4a.json",
    POLICY / "miyagi_kpi_catalog_measure4b.json",
    POLICY / "miyagi_kpi_catalog_measure5a.json",
    POLICY / "miyagi_kpi_catalog_measure5b.json",
]
EVIDENCE = [
    POLICY / "miyagi_kpi_measure4a_evidence_packets.json",
    POLICY / "miyagi_kpi_measure4b_evidence_packets.json",
    POLICY / "miyagi_kpi_group32_evidence_packet.json",
    POLICY / "miyagi_kpi_groups33_34_evidence_packets.json",
    POLICY / "miyagi_kpi_group35_evidence_packet.json",
    POLICY / "miyagi_kpi_group36_evidence_packet.json",
    POLICY / "miyagi_kpi_measure5_tail_evidence_packets.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def reviewed_groups():
    return [item for path in CATALOGS for item in load(path)["items"]]


def test_catalogs_match_schema_and_exact_sequences():
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    for path in CATALOGS:
        assert list(validator.iter_errors(load(path))) == []

    groups = reviewed_groups()
    series = [series for group in groups for series in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(24, 39))
    assert [item["series_number"] for item in series] == list(range(24, 41))
    assert all(group["source_page"] == 56 for group in groups)
    assert all(group["printed_page"] == 55 for group in groups)


def test_group_26_preserves_three_industries_and_periods():
    group = next(
        item for item in reviewed_groups() if item["target_group_number"] == 26
    )
    assert [series["series_number"] for series in group["series"]] == [26, 27, 28]
    assert [series["indicator_name_original"] for series in group["series"]] == [
        "第一次産業における新規就業者数（農業）（人）",
        "第一次産業における新規就業者数（水産業 ）（人）",
        "第一次産業における新規就業者数（林業）（人）",
    ]
    assert [
        [value["value"] for value in series["values"][:3]]
        for series in group["series"]
    ] == [[131, 154, 160], [31, 24, 54], [33, 69, 100]]
    assert group["series"][2]["values"][0]["period_original"] == "R4"
    assert group["series"][2]["values"][1]["period_original"] == "R5"


def test_all_late_targets_remain_not_set():
    groups = reviewed_groups()
    series = [series for group in groups for series in group["series"]]
    assert len(groups) == 15
    assert len(series) == 17
    assert all(group["target_setting_status"] == "partially_set" for group in groups)
    assert all(series["values"][3]["status"] == "not_set" for series in series)
    assert all(series["values"][3]["value"] is None for series in series)
    assert all(series["values"][3]["value_text_original"] == "-" for series in series)


def test_special_official_values_and_missing_unit_are_preserved():
    groups = {group["target_group_number"]: group for group in reviewed_groups()}
    assert groups[27]["series"][0]["values"][2]["value"] == 8.8
    assert groups[31]["series"][0]["values"][2]["value"] == 4900
    assert groups[32]["series"][0]["values"][2]["value"] == 21400
    assert groups[32]["series"][0]["values"][2]["value_text_original"] == "21400"
    assert groups[34]["series"][0]["values"][2]["value_text_original"] == "4126"
    assert groups[35]["series"][0]["unit_original"] == "単位記載なし"
    assert groups[35]["series"][0]["values"][0]["period_original"] == "R5"
    assert groups[35]["series"][0]["values"][1]["period_original"] == "R5"


def test_every_group_has_one_evidence_packet():
    packets = [packet for path in EVIDENCE for packet in load(path)]
    subjects = [packet["subject_id"] for packet in packets]
    expected = {f"policy-target-miyagi-{number}" for number in range(24, 39)}
    assert len(packets) == 15
    assert len(subjects) == len(set(subjects))
    assert set(subjects) == expected
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(packet["open_questions"] == [] for packet in packets)
    for packet in packets:
        assert packet["claims"][0]["source_ids"] == [
            "policy-source-miyagi-midterm-implementation-plan-2026"
        ]
