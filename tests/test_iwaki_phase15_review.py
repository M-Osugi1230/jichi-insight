from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/iwaki_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/iwaki_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/iwaki-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/iwaki_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/iwaki_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/iwaki-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/iwaki-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/iwaki-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/iwaki-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.iwaki.lg.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_iwaki_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "072044"
    assert completion["name_ja"] == "いわき市"
    assert completion["completed_at"] == "2026-11-15"


def test_iwaki_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_iwaki_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-072044"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-15"


def test_iwaki_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "072044"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "いわき市"
    assert len(source_catalog["sources"]) == 4
    assert len(plan_review["records"]) == 4
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-15"

    assert all(
        source["official_url"].startswith(OFFICIAL_PREFIX)
        for source in source_catalog["sources"]
    )
    assert all(source["evidence_location"] for source in source_catalog["sources"])
    assert all(source["use_boundary"] for source in source_catalog["sources"])

    decisions = {record["id"]: record["decision"] for record in plan_review["records"]}
    assert decisions == {
        "iwaki-policy-framework-identity": "accepted",
        "iwaki-management-guideline-framework": "accepted",
        "iwaki-annual-cycle-governance": "accepted",
        "iwaki-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )


def test_iwaki_framework_has_no_invented_plan_period():
    structure = load(STRUCTURE)
    framework = structure["current_framework"]

    assert framework["title"] == "いわき市まちづくりの基本方針"
    # Iwaki abolished the fixed-period comprehensive plan; the record
    # must keep the no-fixed-end status and null years rather than
    # inventing a plan period.
    assert framework["period_status"] == "no_fixed_end"
    assert framework["start_fiscal_year"] is None
    assert framework["end_fiscal_year"] is None
    assert structure["counts"] == {"management_guideline_pillars": 5}

    layers = {layer["layer"]: layer for layer in framework["annual_layers"]}
    guideline = layers["management_guideline"]
    assert guideline["fiscal_year"] == 2026
    assert guideline["pillars"] == [
        "次世代を育てる",
        "命・暮らしを守る",
        "まちの魅力を高める",
        "豊かさを創る",
        "構造改革・DX推進事業",
    ]
    assert structure["review_status"] == "reviewed"

    plan_review = load(PLAN_REVIEW)
    identity = next(
        record
        for record in plan_review["records"]
        if record["id"] == "iwaki-policy-framework-identity"
    )
    assert identity["value"] == "固定の計画期間なし（終期を定めない）"


def test_iwaki_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "経営指針" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    assert "監査委員" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "基本方針" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_iwaki_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-072044-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 159_490_126_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["iwaki-budget-2026"]
    # Enacted as bill No. 35, passed as proposed on 2026-03-12.
    assert "議案第35号" in budget["note"]
    assert "令和8年3月12日" in budget["note"]

    revenue = by_id["jp-local-072044-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-072044-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 162_539_391_275
    assert expenditure["amount_yen"] == 155_415_603_914
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 7_123_787_361
    assert "議案第18号" in revenue["note"]
    assert "議案第18号" in expenditure["note"]


def test_iwaki_evidence_packets_validate_and_match_fiscal_records():
    packets = load(EVIDENCE)
    fiscal_ids = {record["id"] for record in load(FISCAL)}

    assert len(packets) == 3
    for packet in packets:
        assert validate(EVIDENCE_SCHEMA, packet) == []
        assert packet["subject_id"] in fiscal_ids
        assert packet["review_status"] == "reviewed"
        assert all(claim["decision"] == "accepted" for claim in packet["claims"])
        assert all(claim["location_note"] for claim in packet["claims"])

    budget_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-072044-fiscal-2026-total-expenditure"
    )
    assert budget_packet["open_questions"] == []
    assert "議案第35号" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-072044-fiscal-2024-total-revenue"
    )
    # The uninspected audit commission opinion remains the one
    # explicit open residual, carried over from the candidate.
    assert len(revenue_packet["open_questions"]) == 1
    assert "監査委員" in revenue_packet["open_questions"][0]
    assert "議案第18号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年12月19日" in revenue_packet["claims"][0]["statement"]


def test_iwaki_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert completion["quality_gate"]["no_fixed_plan_period_preserved"] is True
    assert completion["review_package"]["counts"] == {
        "management_guideline_pillars": 5,
        "promoted_implementation_item_actual_records": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-plan-granular-kpi-and-project-linkage" in deferred_ids
    assert "settlement-audit-opinion-inspection" in deferred_ids
    assert "settlement-values-and-budget-amendment-linkage" in deferred_ids
    assert "policy-outcome-causal-and-cross-city-comparability" in deferred_ids
    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in completion["deferred_depth"]
    )

    boundary = completion["completion_boundary"]
    assert "公開責任者" in boundary
    assert "2026-11-15" in boundary
    assert "not_assessable" in boundary
    assert "固定" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_iwaki_candidate_records_owner_approval():
    candidate = load(CANDIDATE)

    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-15"
    assert candidate["human_review"]["reviewer_note"]
    assert "公開責任者" in candidate["human_review"]["reviewer_note"]
    assert "チャットで明示的に" in candidate["human_review"]["reviewer_note"]
    assert candidate["publication"]["eligible"] is False


def test_iwaki_and_previous_fourteen_are_reviewed_complete_and_koshigaya_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    iwaki = by_code["072044"]
    assert iwaki["status"] == "reviewed_complete"
    assert iwaki["completion_path"] == "data/catalog/iwaki_phase15_completion.json"
    assert (ROOT / iwaki["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036",
        "092010", "102016", "102024", "112011", "112038",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 41
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 26
    assert queue["summary"]["next_official_code"] == "272272"
    assert by_code["122041"]["status"] == "reviewed_complete"
