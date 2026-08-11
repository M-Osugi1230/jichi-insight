from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_ROOT = ROOT / "data/reviewed/sapporo-city"
QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
SOURCE_PATH = ROOT / "data/catalog/sapporo_city_finance_sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance):
    schema = load(ROOT / "schemas" / schema_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return list(validator.iter_errors(instance))


def test_sapporo_reviewed_identity_and_fiscal_records_match_shared_contracts():
    municipality = load(REVIEWED_ROOT / "municipality.json")
    records = load(REVIEWED_ROOT / "fiscal_records.json")
    packets = load(REVIEWED_ROOT / "evidence_packets.json")

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", record) == [] for record in records)
    assert all(validate("evidence_packet.schema.json", packet) == [] for packet in packets)
    assert municipality["official_code"] == "011002"
    assert len(records) == len(packets) == 3
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }


def test_sapporo_first_fiscal_values_and_states_are_exact():
    records = {record["id"]: record for record in load(REVIEWED_ROOT / "fiscal_records.json")}

    budget = records["jp-local-011002-fiscal-2026-total-revenue"]
    assert budget["stage"] == "initial_budget"
    assert budget["metric_label"] == "一般会計当初予算案"
    assert budget["amount_yen"] == 1_318_500_000_000
    assert "補正後予算" in budget["note"]

    revenue = records["jp-local-011002-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-011002-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 1_240_200_000_000
    assert expenditure["amount_yen"] == 1_230_300_000_000
    assert "概要値" in revenue["metric_label"]
    assert "概要値" in expenditure["metric_label"]


def test_sapporo_review_sources_are_official_and_record_level_locations_exist():
    sources = load(SOURCE_PATH)["records"]
    source_ids = {source["id"] for source in sources}
    assert source_ids == {
        "sapporo-city-home",
        "sapporo-city-budget-2026-page",
        "sapporo-city-settlement-2024-page",
    }
    assert all(source["url"].startswith("https://www.city.sapporo.jp/") for source in sources)

    packets = load(REVIEWED_ROOT / "evidence_packets.json")
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(
        claim["location_note"].startswith("公式ページ")
        for packet in packets
        for claim in packet["claims"]
    )


def test_sapporo_phase13_status_is_in_progress_not_complete():
    queue = load(QUEUE_PATH)
    sapporo = next(
        item for item in queue["execution_queue"] if item["official_code"] == "011002"
    )
    statuses = [item["status"] for item in queue["execution_queue"]]

    assert sapporo["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    )
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    )
    assert queue["summary"]["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    )
    assert queue["summary"]["next_official_code"] == "011002"
