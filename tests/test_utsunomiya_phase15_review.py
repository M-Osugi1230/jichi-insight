from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/utsunomiya_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/utsunomiya_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/utsunomiya-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/utsunomiya_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/utsunomiya_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/utsunomiya-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/utsunomiya-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/utsunomiya-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/utsunomiya-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_utsunomiya_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "092010"
    assert completion["name_ja"] == "宇都宮市"
    assert completion["completed_at"] == "2026-11-15"


def test_utsunomiya_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_utsunomiya_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-092010"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-15"


def test_utsunomiya_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "092010"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "宇都宮市"
    assert len(source_catalog["sources"]) == 6
    assert len(plan_review["records"]) == 5
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-15"

    assert all(
        source["official_url"].startswith("https://www.city.utsunomiya.lg.jp/")
        for source in source_catalog["sources"]
    )
    assert all(source["evidence_location"] for source in source_catalog["sources"])
    assert all(source["use_boundary"] for source in source_catalog["sources"])

    decisions = {record["id"]: record["decision"] for record in plan_review["records"]}
    assert decisions == {
        "utsunomiya-current-plan-period": "accepted",
        "utsunomiya-current-policy-structure": "accepted",
        "utsunomiya-basic-plan-phase-transition": "accepted",
        "utsunomiya-implementation-plan-layer": "accepted",
        "utsunomiya-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith("https://www.city.utsunomiya.lg.jp/")
        for record in plan_review["records"]
    )


def test_utsunomiya_current_policy_structure_matches_declared_depth():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]
    counts = structure["counts"]

    assert plan["title"] == "第6次宇都宮市総合計画"
    assert plan["start_fiscal_year"] == 2018
    assert plan["end_fiscal_year"] == 2027
    assert counts == {"policy_pillars": 6}
    # The six future-city pillar names are confirmed in the latter basic
    # plan itself, so they are enumerated; measures and KPIs are not.
    assert plan["policy_pillars"]["names_enumerated_in_v1"] is True
    assert plan["policy_pillars"]["names"] == [
        "子育て・教育の未来都市",
        "健康・福祉の未来都市",
        "安全・安心の未来都市",
        "魅力創造・交流の未来都市",
        "産業・環境の未来都市",
        "交通の未来都市",
    ]
    # The plan does not use a "basic goals" tier; do not invent one.
    assert "basic_goals" not in plan

    phases = structure["basic_plan_phases"]
    assert "後期基本計画（2023年度～2027年度）" in phases["second_phase"]
    assert structure["review_status"] == "reviewed"


def test_utsunomiya_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    assert "流用しない" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "後期基本計画" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_utsunomiya_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-092010-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 246_550_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == [
        "utsunomiya-budget-2026",
        "utsunomiya-budget-2026-enactment",
    ]

    revenue = by_id["jp-local-092010-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-092010-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # FY2024 values keep thousand-yen source precision.
    assert revenue["amount_yen"] == 242_716_210_000
    assert expenditure["amount_yen"] == 236_437_643_000


def test_utsunomiya_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-092010-fiscal-2026-total-expenditure"
    )
    # The vote was confirmed directly on the official council
    # meeting-result page, so no residual open question remains here.
    assert budget_packet["open_questions"] == []
    assert "直接確認" in budget_packet["claims"][0]["review_note"]


def test_utsunomiya_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert completion["quality_gate"]["settlement_source_precision_preserved"] is True
    assert completion["review_package"]["counts"] == {
        "future_cities": 6,
        "promoted_implementation_item_actual_records": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-plan-granular-kpi-and-project-linkage" in deferred_ids
    assert "current-plan-full-text-confirmation" in deferred_ids
    assert "settlement-yen-precision" in deferred_ids
    assert "current-plan-annual-evaluation-evidence" in deferred_ids
    assert "fiscal-detail-and-amendment-linkage" in deferred_ids
    assert "policy-outcome-causal-and-cross-city-comparability" in deferred_ids
    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in completion["deferred_depth"]
    )

    boundary = completion["completion_boundary"]
    assert "公開責任者" in boundary
    assert "2026-11-15" in boundary
    assert "not_assessable" in boundary
    assert "千円" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_utsunomiya_candidate_records_owner_approval():
    candidate = load(CANDIDATE)

    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-15"
    assert "公開責任者" in candidate["human_review"]["reviewer_note"]
    # The candidate file itself remains non-public staging material.
    assert candidate["publication"]["eligible"] is False


def test_utsunomiya_and_previous_nine_are_reviewed_complete_and_iwaki_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    utsunomiya = by_code["092010"]
    assert utsunomiya["status"] == "reviewed_complete"
    assert utsunomiya["completion_path"] == "data/catalog/utsunomiya_phase15_completion.json"
    assert (ROOT / utsunomiya["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 67
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None
    assert by_code["122041"]["status"] == "reviewed_complete"
