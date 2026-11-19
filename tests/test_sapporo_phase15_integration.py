"""Issue #695: Sapporo integrated into the Phase 15 generic city framework.

Sapporo completed in Phase 13 and was outside the Phase 14 target universe,
so the Phase 15 queue originally held 67 cities. By owner decision on
2026-11-19 Sapporo was integrated as the 68th city, reusing its Phase 13
reviewed package. These tests pin that integration contract.
"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
COMPLETION_PATH = ROOT / "data/catalog/sapporo_phase15_completion.json"
SOURCES_PATH = ROOT / "data/catalog/sapporo_phase15_sources.json"
PACKAGE = ROOT / "data/reviewed/sapporo-city"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_is_the_68th_reviewed_complete_queue_row():
    queue = load(QUEUE_PATH)
    rows = queue["execution_queue"]
    # Nagoya was appended as the 69th row by the Issue #734 integration;
    # Sapporo remains the 68th row.
    assert len(rows) == 69
    assert queue["summary"]["target_count"] == 69
    assert queue["summary"]["reviewed_complete_count"] == 69

    sapporo = rows[67]
    assert sapporo["sequence"] == 68
    assert sapporo["official_code"] == "011002"
    assert sapporo["name_ja"] == "札幌市"
    assert sapporo["status"] == "reviewed_complete"
    assert sapporo["completion_path"] == "data/catalog/sapporo_phase15_completion.json"
    # The source inventory is the pre-existing Phase 12 inventory.
    inventory = load(ROOT / sapporo["source_inventory_path"])
    assert inventory["official_code"] == "011002"
    assert inventory["status"] == "source_inventory_complete"


def test_sapporo_phase15_completion_validates_and_records_phase13_origin():
    completion = load(COMPLETION_PATH)
    schema = load(ROOT / "schemas/phase15_municipality_completion.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    assert list(validator.iter_errors(completion)) == []

    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "011002"
    # The integration history is recorded in the completion boundary: the
    # original completion is Phase 13 and the integration is the owner's
    # 2026-11-19 decision.
    boundary = completion["completion_boundary"]
    assert "Phase 13" in boundary
    assert "2026-11-19" in boundary
    assert "68自治体" in boundary

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


def test_sapporo_phase15_sources_catalog_validates_and_resolves_package_ids():
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

    # Every referenced id resolves through the Phase 15 catalog or the
    # documented "<city>-city-home" exception.
    assert referenced - catalog_ids == {"sapporo-city-home"}


def test_sapporo_package_satisfies_the_generic_city_loader_contract():
    municipality = load(PACKAGE / "municipality.json")
    assert municipality["data_status"] == "reviewed"
    assert municipality["official_code"] == "011002"
    assert municipality["id"] == "jp-local-011002"

    plan_review = load(PACKAGE / "plan_review.json")
    assert plan_review["review_status"] == "reviewed"
    assert all(record["source_url"] for record in plan_review["records"])

    fiscal = load(PACKAGE / "fiscal_records.json")
    packets = load(PACKAGE / "evidence_packets.json")
    assert all(record["review_status"] == "reviewed" for record in fiscal)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in fiscal
    }


def test_sapporo_settlement_package_is_ready_for_fiscal_detail():
    # Registered by PR #694; once Sapporo has a generic city page the
    # fiscal detail renders from this package.
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
