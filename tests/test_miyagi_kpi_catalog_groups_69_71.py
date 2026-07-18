import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_pillar3.json"
EVIDENCE = POLICY / "miyagi_kpi_pillar3_evidence_packets.json"
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
    CATALOG,
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_pillar3_catalog_matches_schema_and_exact_sequences():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(CATALOG_SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []

    groups = catalog["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == [69, 70, 71]
    assert [item["series_number"] for item in series] == [86, 87, 88, 89]
    assert all(group["scope_type"] == "pillar" for group in groups)
    assert all(group["scope_number"] == 3 for group in groups)
    assert all(group["source_page"] == 59 for group in groups)
    assert all(group["printed_page"] == 58 for group in groups)
    assert all(group["target_setting_status"] == "set" for group in groups)


def test_population_change_preserves_negative_values_and_explicit_zeros():
    group69 = load(CATALOG)["items"][0]
    values = group69["series"][0]["values"]
    assert [value["value"] for value in values] == [-1452, -2989, 0, 0]
    assert [value["value_text_original"] for value in values] == [
        "-1,452",
        "-2,989",
        "0",
        "0",
    ]
    assert all(value["status"] == "numeric" for value in values)
    assert "負値" in group69["comparability_note_original"]
    assert "明示的な0" in group69["comparability_note_original"]


def test_health_expectancy_preserves_sex_series_and_reiwa_one_baselines():
    group71 = load(CATALOG)["items"][2]
    assert [series["series_number"] for series in group71["series"]] == [88, 89]
    assert [series["indicator_name_original"] for series in group71["series"]] == [
        "健康寿命（日常生活に制限のない期間の平均）（男性）（年）",
        "健康寿命（日常生活に制限のない期間の平均）（女性）（年）",
    ]
    assert [value["period_original"] for value in group71["series"][0]["values"]] == [
        "R1",
        "R4",
        "R9",
        "R12",
    ]
    assert [value["period_year"] for value in group71["series"][0]["values"]] == [
        2019,
        2022,
        2027,
        2030,
    ]
    assert [value["value"] for value in group71["series"][0]["values"]] == [
        72.90,
        72.91,
        73.46,
        73.76,
    ]
    assert [value["value"] for value in group71["series"][1]["values"]] == [
        75.10,
        74.74,
        75.67,
        75.78,
    ]
    assert "男性・女性の2系列" in group71["comparability_note_original"]


def test_pillar3_evidence_covers_all_groups():
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 3
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        "policy-target-miyagi-69",
        "policy-target-miyagi-70",
        "policy-target-miyagi-71",
    }
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(packet["open_questions"] == [] for packet in packets)
    assert all(
        claim["location_note"].startswith("PDFページ59（印刷ページ58）目標値No.")
        for packet in packets
        for claim in packet["claims"]
    )


def test_all_reviewed_batches_form_71_groups_and_89_series():
    groups = [group for path in ALL_CATALOGS for group in load(path)["items"]]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(1, 72))
    assert [item["series_number"] for item in series] == list(range(1, 90))
    assert all(group["actual_linkage_status"] == "not_linked" for group in groups)
    assert all(group["evaluation_status"] == "not_assessed" for group in groups)
