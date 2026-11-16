from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/kanazawa_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/kanazawa_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/kanazawa-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/kanazawa_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/kanazawa_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/kanazawa-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/kanazawa-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/kanazawa-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/kanazawa-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www4.city.kanazawa.lg.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_kanazawa_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "172014"
    assert completion["name_ja"] == "金沢市"
    assert completion["completed_at"] == "2026-11-16"


def test_kanazawa_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_kanazawa_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-172014"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_kanazawa_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "172014"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "金沢市"
    assert len(source_catalog["sources"]) == 4
    assert len(plan_review["records"]) == 5
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-16"

    assert all(
        source["official_url"].startswith(OFFICIAL_PREFIX)
        for source in source_catalog["sources"]
    )
    assert all(source["evidence_location"] for source in source_catalog["sources"])
    assert all(source["use_boundary"] for source in source_catalog["sources"])

    decisions = {record["id"]: record["decision"] for record in plan_review["records"]}
    assert decisions == {
        "kanazawa-current-plan-period": "accepted",
        "kanazawa-current-policy-structure": "accepted",
        "kanazawa-progress-governance-framework": "accepted",
        "kanazawa-plan-revision-chronology": "accepted",
        "kanazawa-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The plan's revisions are recorded only as a version chronology,
    # never merged back into the original plan's framework.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "kanazawa-plan-revision-chronology"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_kanazawa_plan_period_and_structure_are_reviewed():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "未来共創計画"
    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2033
    assert plan["vision"] == "未来を拓く世界の共創文化都市・金沢"
    assert structure["counts"] == {"basic_goals": 5, "basic_plan_measures": 21}
    assert structure["review_status"] == "reviewed"

    # The plan is a single ten-year action plan under the city vision,
    # not a basic-concept / basic-plan / implementation-plan layer
    # structure. Its basic goals are the city vision's five basic
    # policies and the measures under them are its 21 policy
    # directions, exactly as published; the measures, major projects
    # and KPIs beneath the policy directions are not enumerated in v1.
    layers = {component["layer"] for component in plan["components"]}
    assert layers == {"single_plan"}
    assert plan["basic_goals"]["count"] == 5
    assert plan["basic_goals"]["names"] == [
        "世界に誇る伝統と創造の文化が息づくまち ～魅力づくり～",
        "多様な人々が共生し、心豊かに暮らせるまち ～暮らしづくり～",
        "共に学び、未来を創る人を育むまち ～人づくり～",
        "創造・変革により成長するまち ～仕事づくり～",
        "活力と個性があふれ、安全で持続可能なまち ～都市づくり～",
    ]
    assert plan["basic_goals"]["measures_count"] == 21
    assert plan["basic_goals"]["measures_per_goal"] == [4, 4, 4, 4, 5]
    assert sum(plan["basic_goals"]["measures_per_goal"]) == 21

    plan_review = load(PLAN_REVIEW)
    period = next(
        record
        for record in plan_review["records"]
        if record["id"] == "kanazawa-current-plan-period"
    )
    assert period["value"] == "2024年度～2033年度"


def test_kanazawa_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "PDCA" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    assert "監査委員" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 is the first year of the plan period, but its totals are
    # section-level aggregates with no mapping to individual basic
    # policies, policy directions or KPIs.
    assert "款別" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_kanazawa_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-172014-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 207_800_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["kanazawa-budget-2026"]
    # Enactment is confirmed by the official city gazette (告示第56号);
    # the budget is a skeleton budget ahead of the mayoral election,
    # and its bill number and vote date stay explicitly unidentified
    # instead of being invented.
    assert "告示第56号" in budget["note"]
    assert "骨格予算" in budget["note"]
    assert "特定していない" in budget["note"]

    revenue = by_id["jp-local-172014-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-172014-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in the
    # official settlement summary table, so these are the exact
    # published totals and their difference must equal the published
    # balance (歳入歳出差引残額) of 8,476,976,027 yen.
    assert revenue["amount_yen"] == 218_624_336_395
    assert expenditure["amount_yen"] == 210_147_360_368
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 8_476_976_027
    assert "認定第1号" in revenue["note"]
    assert "認定第1号" in expenditure["note"]
    assert "12月定例月議会" in revenue["note"]


def test_kanazawa_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-172014-fiscal-2026-total-expenditure"
    )
    # Identifying the budget bill number and vote date, and the final
    # cross-check against the budget book's bill text, remain explicit
    # open residuals, carried over from the candidate.
    assert len(budget_packet["open_questions"]) == 2
    assert "議案番号" in budget_packet["open_questions"][0]
    assert "第1条" in budget_packet["open_questions"][1]
    assert "告示第56号" in budget_packet["claims"][0]["location_note"] or (
        "成立" in budget_packet["claims"][0]["statement"]
    )

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-172014-fiscal-2024-total-revenue"
    )
    # Identifying the certification date and the cross-check against
    # the settlement detail book remain explicit open residuals,
    # carried over from the candidate.
    assert len(revenue_packet["open_questions"]) == 2
    assert "認定日" in revenue_packet["open_questions"][0]
    assert "明細書" in revenue_packet["open_questions"][1]
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "12月定例月議会" in revenue_packet["claims"][0]["statement"]

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-172014-fiscal-2024-total-expenditure"
    )
    assert expenditure_packet["open_questions"] == []


def test_kanazawa_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert completion["quality_gate"]["current_plan_period_reviewed"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 5,
        "basic_plan_measures": 21,
        "promoted_implementation_item_actual_records": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-plan-granular-kpi-and-project-linkage" in deferred_ids
    assert "plan-revision-version-depth" in deferred_ids
    assert "settlement-audit-opinion-inspection" in deferred_ids
    assert "current-plan-annual-evaluation-evidence" in deferred_ids
    assert "fiscal-detail-and-amendment-linkage" in deferred_ids
    assert "policy-outcome-causal-and-cross-city-comparability" in deferred_ids
    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in completion["deferred_depth"]
    )

    boundary = completion["completion_boundary"]
    # The boundary must record the owner's delegation to Muse, not
    # an owner-conducted review.
    assert "委任" in boundary
    assert "所有者本人が一次資料を直接レビューしたものではない" in boundary
    assert "2026-11-15" in boundary
    assert "not_assessable" in boundary
    # The unidentified items must stay explicit: the budget bill
    # number and vote date, and the settlement certification date,
    # were not identified in the primary sources consulted.
    assert "告示第56号" in boundary
    assert "特定していない" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_kanazawa_candidate_records_delegated_review():
    candidate = load(CANDIDATE)

    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-16"
    note = candidate["human_review"]["reviewer_note"]
    assert note
    # The note records that the owner explicitly delegated the review
    # to Muse in chat on 2026-11-15, and that the owner did not
    # personally review the primary sources.
    assert "レビューはあなたがやってください" in note
    assert "委任" in note
    assert "所有者本人が一次資料を直接レビューしたものではない" in note
    assert candidate["publication"]["eligible"] is False


def test_kanazawa_and_previous_twenty_three_are_reviewed_complete_and_fukui_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    kanazawa = by_code["172014"]
    assert kanazawa["status"] == "reviewed_complete"
    assert (
        kanazawa["completion_path"]
        == "data/catalog/kanazawa_phase15_completion.json"
    )
    assert (ROOT / kanazawa["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 50
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 17
    assert queue["summary"]["next_official_code"] == "332020"
