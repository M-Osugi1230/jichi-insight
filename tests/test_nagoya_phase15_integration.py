"""Issue #734: Nagoya integrated into the Phase 15 generic city framework.

Nagoya completed in Phase 13 and was outside the Phase 14 target universe,
so the Phase 15 queue originally held 67 cities (68 after Sapporo was
integrated under Issue #695). Under Issue #734 Nagoya was integrated as
the 69th city, reusing its Phase 13 reviewed package, and its ordinary-
account settlement detail (FY2022-2024, Issue #691 format) was registered
so the generic city page renders the fiscal detail. These tests pin that
integration contract.
"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
COMPLETION_PATH = ROOT / "data/catalog/nagoya_phase15_completion.json"
SOURCES_PATH = ROOT / "data/catalog/nagoya_phase15_sources.json"
PACKAGE = ROOT / "data/reviewed/nagoya-city"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_nagoya_is_the_69th_reviewed_complete_queue_row():
    queue = load(QUEUE_PATH)
    rows = queue["execution_queue"]
    assert len(rows) == 69
    assert queue["summary"]["target_count"] == 69
    assert queue["summary"]["reviewed_complete_count"] == 69

    nagoya = rows[-1]
    assert nagoya["sequence"] == 69
    assert nagoya["official_code"] == "231002"
    assert nagoya["name_ja"] == "名古屋市"
    assert nagoya["status"] == "reviewed_complete"
    assert nagoya["completion_path"] == "data/catalog/nagoya_phase15_completion.json"
    # The source inventory is the pre-existing indexed inventory.
    inventory = load(ROOT / nagoya["source_inventory_path"])
    assert inventory["official_code"] == "231002"
    assert inventory["status"] == "source_inventory_complete"


def test_nagoya_phase15_completion_validates_and_records_phase13_origin():
    completion = load(COMPLETION_PATH)
    schema = load(ROOT / "schemas/phase15_municipality_completion.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    assert list(validator.iter_errors(completion)) == []

    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "231002"
    # The integration history is recorded in the completion boundary: the
    # original completion is Phase 13 and the integration is Issue #734.
    boundary = completion["completion_boundary"]
    assert "Phase 13" in boundary
    assert "2026-11-19" in boundary
    assert "69自治体" in boundary

    package = completion["review_package"]
    for key in (
        "source_catalog_path",
        "plan_review_path",
        "policy_structure_path",
        "progress_review_path",
        "fiscal_records_path",
        "fiscal_evidence_path",
    ):
        assert (ROOT / package[key]).is_file(), key


def test_nagoya_phase15_sources_catalog_validates_and_resolves_package_ids():
    catalog = load(SOURCES_PATH)
    schema = load(ROOT / "schemas/phase15_source_catalog.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    assert list(validator.iter_errors(catalog)) == []

    catalog_ids = {source["id"] for source in catalog["sources"]}
    municipality = load(PACKAGE / "municipality.json")
    fiscal = load(PACKAGE / "fiscal_records.json")
    packets = load(PACKAGE / "evidence_packets.json")

    referenced = set(municipality["sources"])
    for record in fiscal:
        referenced.update(record["sources"])
    for packet in packets:
        for claim in packet["claims"]:
            referenced.update(claim["source_ids"])

    # Every referenced id resolves through the Phase 15 catalog.
    assert referenced - catalog_ids == set()


def test_nagoya_package_satisfies_the_generic_city_loader_contract():
    municipality = load(PACKAGE / "municipality.json")
    assert municipality["data_status"] == "reviewed"
    assert municipality["official_code"] == "231002"
    assert municipality["id"] == "jp-local-231002"

    plan_review = load(PACKAGE / "plan_review.json")
    assert plan_review["review_status"] == "reviewed"
    assert all(record["source_url"] for record in plan_review["records"])

    fiscal = load(PACKAGE / "fiscal_records.json")
    packets = load(PACKAGE / "evidence_packets.json")
    assert all(record["review_status"] == "reviewed" for record in fiscal)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in fiscal
    }


def test_nagoya_settlement_package_is_ready_for_fiscal_detail():
    # Registered by the Issue #734 integration in the Issue #691 format;
    # the generic city page renders the fiscal detail from this package.
    records = load(PACKAGE / "settlement_records.json")
    packets = load(PACKAGE / "settlement_evidence_packets.json")
    assert len(records) == 51
    assert all(
        record["review_status"] == "reviewed"
        and record["stage"] == "settlement"
        and record["account_type"] == "ordinary"
        for record in records
    )
    reviewed_subjects = {
        packet["subject_id"] for packet in packets if packet["review_status"] == "reviewed"
    }
    assert {record["id"] for record in records} <= reviewed_subjects

    # Arithmetic reconciliation registered with the records:
    # revenue - expenditure = formal balance, and formal balance minus
    # carryover resources = real balance, for every fiscal year.
    by_year_metric = {
        (record["fiscal_year"], record["metric"]): record for record in records
    }
    for year in (2022, 2023, 2024):
        revenue = by_year_metric[(year, "total_revenue")]["amount_yen"]
        expenditure = by_year_metric[(year, "total_expenditure")]["amount_yen"]
        formal = by_year_metric[(year, "formal_balance")]["amount_yen"]
        carryover = by_year_metric[(year, "carryover_resources")]["amount_yen"]
        real = by_year_metric[(year, "real_balance")]["amount_yen"]
        assert revenue - expenditure == formal
        assert formal - carryover == real
