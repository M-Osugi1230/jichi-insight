from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_DIR = ROOT / "data/reviewed/sendai-city"
MUNICIPALITY_PATH = REVIEWED_DIR / "municipality.json"
FISCAL_PATH = REVIEWED_DIR / "fiscal_records.json"
EVIDENCE_PATH = REVIEWED_DIR / "evidence_packets.json"
PLAN_PATH = REVIEWED_DIR / "plan_review.json"
SOURCE_PATH = ROOT / "data/catalog/sendai_phase13_sources.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
MUNICIPALITY_SCHEMA_PATH = ROOT / "schemas/municipality.schema.json"
FISCAL_SCHEMA_PATH = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(instance, schema_path: Path):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_sendai_reviewed_municipality_and_fiscal_records_match_shared_schemas():
    municipality = load(MUNICIPALITY_PATH)
    fiscal_records = load(FISCAL_PATH)

    assert validate(municipality, MUNICIPALITY_SCHEMA_PATH) == []
    assert all(validate(record, FISCAL_SCHEMA_PATH) == [] for record in fiscal_records)
    assert municipality["official_code"] == "041009"
    assert municipality["name_ja"] == "仙台市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]


def test_sendai_reviewed_sources_are_official_and_declared_by_municipality():
    municipality = load(MUNICIPALITY_PATH)
    source_records = load(SOURCE_PATH)["records"]
    source_map = {record["id"]: record for record in source_records}

    assert len(source_map) == 8
    assert set(municipality["sources"]) == set(source_map)
    assert all(record["organization"] == "仙台市" for record in source_records)
    assert all(record["url"].startswith("https://www.city.sendai.jp/") for record in source_records)
    assert all(record["confidence"] == "high" for record in source_records)
    assert source_map["sendai-city-progress-2025-page"]["review_status"] == (
        "reviewed_aggregate_and_methodology"
    )
    assert source_map["sendai-city-challenge-project-self-evaluation-2024-report"][
        "review_status"
    ] == "partial_record_review_in_progress"
    assert source_map["sendai-city-challenge-project-self-evaluation-2024-report"][
        "page_count"
    ] == 126
    assert source_map["sendai-city-settlement-2024-general-account-pdf"][
        "review_status"
    ] == "reviewed_totals"


def test_sendai_fiscal_records_preserve_budget_and_settlement_states():
    records = {record["id"]: record for record in load(FISCAL_PATH)}

    budget = records["jp-local-041009-fiscal-2026-total-revenue"]
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_revenue"
    assert budget["amount_yen"] == 730_600_000_000
    assert set(budget["sources"]) == {
        "sendai-city-budget-2026-announcement",
        "sendai-city-budget-2026-enactment-page",
    }
    assert "原案通り可決" in budget["note"]

    revenue = records["jp-local-041009-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 627_113_991_995
    assert "調定額635,078,779,941円とは混同しない" in revenue["note"]

    expenditure = records["jp-local-041009-fiscal-2024-total-expenditure"]
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 619_037_397_835
    assert "翌年度繰越額36,135,812,450円" in expenditure["note"]


def test_sendai_fiscal_records_have_one_to_one_reviewed_evidence():
    records = load(FISCAL_PATH)
    packets = load(EVIDENCE_PATH)
    packet_map = {packet["subject_id"]: packet for packet in packets}

    assert len(records) == len(packets) == 3
    assert set(packet_map) == {record["id"] for record in records}
    assert all(validate(packet, EVIDENCE_SCHEMA_PATH) == [] for packet in packets)
    assert all(packet["subject_type"] == "fiscal_record" for packet in packets)
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(
        claim["decision"] == "accepted"
        for packet in packets
        for claim in packet["claims"]
    )


def test_sendai_plan_review_preserves_plan_layers_and_survey_methodology():
    plan = load(PLAN_PATH)
    records = {record["id"]: record for record in plan["records"]}

    assert plan["official_code"] == "041009"
    assert plan["review_status"] == "review_in_progress"
    assert records["sendai-basic-plan-period"]["value"] == "2021年度～2030年度"
    assert records["sendai-implementation-plan-period"]["value"] == (
        "2024年度～2026年度"
    )

    sample = records["sendai-2025-citizen-survey-sample"]
    assert sample["value"] == 6000
    assert sample["unit"] == "persons_sampled"

    period = records["sendai-2025-citizen-survey-period"]
    assert period["value"] == "2025-04-30/2025-05-29"

    responses = records["sendai-2025-citizen-survey-valid-responses"]
    assert responses["value"] == 2794
    assert responses["reported_rate_percent"] == 46.8
    assert "再計算しない" in responses["review_note"]


def test_sendai_source_reported_self_evaluation_is_exact_and_bounded():
    plan = load(PLAN_PATH)
    records = {record["id"]: record for record in plan["records"]}
    evaluation = records["sendai-2024-challenge-project-self-evaluation"]

    assert evaluation["value"] == 108
    assert evaluation["source_reported_breakdown"] == {
        "double_circle": 12,
        "circle": 89,
        "triangle": 7,
        "cross": 0,
    }
    assert sum(evaluation["source_reported_breakdown"].values()) == 108
    assert "自己評価" in evaluation["review_note"]
    assert "他都市比較指標には変換しない" in evaluation["review_note"]
    assert "not an independent Jichi Insight achievement judgment" in plan[
        "quality_boundary"
    ]


def test_sendai_manifest_and_phase13_queue_record_review_in_progress():
    manifest = load(MANIFEST_PATH)
    queue = load(QUEUE_PATH)
    sendai = next(
        item for item in queue["execution_queue"] if item["official_code"] == "041009"
    )
    statuses = [item["status"] for item in queue["execution_queue"]]
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    challenge_batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    cumulative_reviewed = sum(fact["value"] for fact in challenge_batches)
    remaining = 108 - cumulative_reviewed

    assert manifest["status"] == "review_in_progress"
    assert sendai["status"] == "review_in_progress"
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    ) == 2
    assert queue["summary"]["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    ) == 16
    assert facts["sendai-2026-general-account-initial-budget"]["value"] == (
        730_600_000_000
    )
    assert facts["sendai-2024-general-account-settlement-revenue"]["value"] == (
        627_113_991_995
    )
    assert facts["sendai-2024-general-account-settlement-expenditure"]["value"] == (
        619_037_397_835
    )
    assert facts["sendai-challenge-project-records-part1"]["value"] == 3
    assert cumulative_reviewed >= 3
    assert f"{cumulative_reviewed}事業を個票レビュー済み" in manifest["remaining_work"][0]
    assert f"残り{remaining}事業" in manifest["remaining_work"][0]
