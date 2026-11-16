from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/kawaguchi_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/kawaguchi_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/kawaguchi-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/kawaguchi_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/kawaguchi_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/kawaguchi-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/kawaguchi-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/kawaguchi-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/kawaguchi-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIXES = (
    "https://www.city.kawaguchi.lg.jp/",
    "https://kawaguchi.gsl-service.net/",
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_kawaguchi_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "112038"
    assert completion["name_ja"] == "川口市"
    assert completion["completed_at"] == "2026-11-15"


def test_kawaguchi_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_kawaguchi_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-112038"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-15"


def test_kawaguchi_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "112038"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "川口市"
    assert len(source_catalog["sources"]) == 5
    assert len(plan_review["records"]) == 5
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-15"

    assert all(
        source["official_url"].startswith(OFFICIAL_PREFIXES)
        for source in source_catalog["sources"]
    )
    assert all(source["evidence_location"] for source in source_catalog["sources"])
    assert all(source["use_boundary"] for source in source_catalog["sources"])

    decisions = {record["id"]: record["decision"] for record in plan_review["records"]}
    assert decisions == {
        "kawaguchi-current-plan-period": "accepted",
        "kawaguchi-current-policy-structure": "accepted",
        "kawaguchi-implementation-plan-layer": "accepted",
        "kawaguchi-progress-governance": "accepted",
        "kawaguchi-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIXES)
        for record in plan_review["records"]
    )


def test_kawaguchi_current_policy_structure_matches_declared_depth():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]
    counts = structure["counts"]

    assert plan["title"] == "第6次川口市総合計画"
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2035
    assert counts == {"basic_goals": 8}
    assert plan["vision"] == "産業と文化と自然が調和した 輝きあふれるまち 川口"

    principles = plan["basic_principles"]
    assert principles["count"] == 3
    assert principles["names"] == [
        "市民とともに輝くまちづくり",
        "みんなの笑顔輝くまちづくり",
        "いつまでも輝き続けるまちづくり",
    ]

    goals = plan["basic_goals"]
    assert goals["names_enumerated_in_v1"] is True
    # The eight goal names are the official formulations from the city
    # plan page; paraphrased secondary lists must not be used.
    assert goals["names"] == [
        "健康で、自分らしく生き生きと暮らせるまち",
        "誰もがお互いを認め合い、安心して暮らせるまち",
        "こどもをみんなで育み、こどもが輝き活躍するまち",
        "学びとスポーツ・文化に親しみ、自己実現ができるまち",
        "にぎわいと魅力があり、伝統と未来が響き合うまち",
        "都市と自然が調和した、うるおいとやすらぎのあるまち",
        "誰もが安全で快適に暮らせるまち",
        "持続可能で自立したまち",
    ]
    assert "第5次" in structure["previous_plan"]["title"]
    assert structure["review_status"] == "reviewed"


def test_kawaguchi_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "令和8年度版" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    assert "市民意識調査" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "第5次" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_kawaguchi_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-112038-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 256_970_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == [
        "kawaguchi-budget-2026",
        "kawaguchi-budget-2026-enactment",
    ]
    # Vote date as printed on the official vote-result table.
    assert "2026年3月23日" in budget["note"]

    revenue = by_id["jp-local-112038-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-112038-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 259_800_531_831
    assert expenditure["amount_yen"] == 247_943_564_747
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 11_856_967_084


def test_kawaguchi_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-112038-fiscal-2026-total-expenditure"
    )
    assert budget_packet["open_questions"] == []
    assert "3月23日" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-112038-fiscal-2024-total-revenue"
    )
    # The December-session vote-table number for bill No. 183 remains
    # the one explicit open residual, carried over from the candidate.
    assert len(revenue_packet["open_questions"]) == 1
    assert "第183号" in revenue_packet["open_questions"][0]


def test_kawaguchi_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert completion["quality_gate"]["previous_plan_attribution_reviewed"] is True
    assert completion["review_package"]["counts"] == {
        "basic_goals": 8,
        "promoted_implementation_item_actual_records": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-plan-granular-kpi-and-project-linkage" in deferred_ids
    assert "current-plan-full-text-confirmation" in deferred_ids
    assert "settlement-certification-vote-table-number" in deferred_ids
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
    assert "第5次" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_kawaguchi_candidate_records_owner_approval():
    candidate = load(CANDIDATE)

    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-15"
    assert candidate["human_review"]["reviewer_note"]
    assert "公開責任者" in candidate["human_review"]["reviewer_note"]
    assert candidate["publication"]["eligible"] is False


def test_kawaguchi_and_previous_thirteen_are_reviewed_complete_and_iwaki_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    kawaguchi = by_code["112038"]
    assert kawaguchi["status"] == "reviewed_complete"
    assert kawaguchi["completion_path"] == "data/catalog/kawaguchi_phase15_completion.json"
    assert (ROOT / kawaguchi["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036",
        "092010", "102016", "102024", "112011",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 59
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 8
    assert queue["summary"]["next_official_code"] == "402036"
    assert by_code["122041"]["status"] == "reviewed_complete"
