from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/funabashi_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/funabashi_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/funabashi-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/funabashi_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/funabashi_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/funabashi-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/funabashi-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/funabashi-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/funabashi-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.funabashi.lg.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_funabashi_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "122041"
    assert completion["name_ja"] == "船橋市"
    assert completion["completed_at"] == "2026-11-16"


def test_funabashi_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_funabashi_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-122041"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_funabashi_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "122041"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "船橋市"
    assert len(source_catalog["sources"]) == 4
    assert len(plan_review["records"]) == 4
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
        "funabashi-current-plan-period": "accepted",
        "funabashi-current-policy-structure": "accepted",
        "funabashi-implementation-plan-framework": "accepted",
        "funabashi-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )


def test_funabashi_plan_period_and_structure_are_reviewed():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "第3次船橋市総合計画"
    assert plan["start_fiscal_year"] == 2022
    assert plan["end_fiscal_year"] == 2031
    assert plan["vision"] == "人も まちも 輝く 笑顔あふれる 船橋"
    assert structure["counts"] == {"basic_goals": 24, "basic_plan_measures": 71}
    assert structure["review_status"] == "reviewed"

    # The basic plan is a single ten-year plan: no first/second-half
    # split is recorded in the components.
    layers = {component["layer"] for component in plan["components"]}
    assert layers == {"basic_concept", "basic_plan", "implementation_plan"}
    assert plan["basic_goals"]["count"] == 24
    assert plan["basic_goals"]["measures_count"] == 71
    assert sum(plan["basic_goals"]["measures_per_goal"]) == 71

    plan_review = load(PLAN_REVIEW)
    period = next(
        record
        for record in plan_review["records"]
        if record["id"] == "funabashi-current-plan-period"
    )
    assert period["value"] == "2022年度～2031年度"


def test_funabashi_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "実施計画" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    assert "監査委員" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 is inside the plan period; the non-assessment is about
    # the missing item-level linkage, not about the period.
    assert "計画期間外を理由とする未判定ではない" in linkage["boundary"]
    assert "対応付けは未実施" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_funabashi_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-122041-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 270_640_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["funabashi-budget-2026"]
    # Enacted as bill No. 1, passed on 2026-03-25.
    assert "議案第1号" in budget["note"]
    assert "令和8年3月25日" in budget["note"]

    revenue = by_id["jp-local-122041-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-122041-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement is published only at thousand-yen precision; the
    # amounts are kept at that precision and yen-level totals are not
    # synthesised.
    assert revenue["amount_yen"] == 249_314_444_000
    assert expenditure["amount_yen"] == 243_229_426_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 6_085_018_000
    assert "千円" in revenue["note"]
    assert "千円" in expenditure["note"]
    assert "合成していない" in revenue["note"]
    assert "認定第1号" in revenue["note"]
    assert "認定第1号" in expenditure["note"]


def test_funabashi_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-122041-fiscal-2026-total-expenditure"
    )
    assert budget_packet["open_questions"] == []
    assert "議案第1号" in budget_packet["claims"][0]["statement"]
    assert "可決" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-122041-fiscal-2024-total-revenue"
    )
    # The uninspected audit commission opinion remains the one
    # explicit open residual, carried over from the candidate.
    assert len(revenue_packet["open_questions"]) == 1
    assert "監査委員" in revenue_packet["open_questions"][0]
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年10月3日" in revenue_packet["claims"][0]["statement"]
    assert "千円" in revenue_packet["claims"][0]["statement"]


def test_funabashi_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert completion["quality_gate"]["current_plan_period_reviewed"] is True
    assert completion["review_package"]["counts"] == {
        "basic_goals": 24,
        "basic_plan_measures": 71,
        "promoted_implementation_item_actual_records": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-plan-granular-kpi-and-project-linkage" in deferred_ids
    assert "current-plan-full-text-confirmation" in deferred_ids
    assert "settlement-audit-opinion-inspection" in deferred_ids
    assert "settlement-yen-precision-confirmation" in deferred_ids
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
    assert "千円" in boundary
    assert "合成していない" in boundary
    assert "not_assessable" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_funabashi_candidate_records_delegated_review():
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


def test_funabashi_and_previous_seventeen_are_reviewed_complete_and_kashiwa_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    funabashi = by_code["122041"]
    assert funabashi["status"] == "reviewed_complete"
    assert (
        funabashi["completion_path"]
        == "data/catalog/funabashi_phase15_completion.json"
    )
    assert (ROOT / funabashi["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 34
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 33
    assert queue["summary"]["next_official_code"] == "252018"
    assert by_code["122173"]["status"] == "reviewed_complete"
