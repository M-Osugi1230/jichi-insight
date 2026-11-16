from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/toyohashi_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/toyohashi_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/toyohashi-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/toyohashi_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/toyohashi_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/toyohashi-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/toyohashi-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/toyohashi-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/toyohashi-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.toyohashi.lg.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_toyohashi_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "232017"
    assert completion["name_ja"] == "豊橋市"
    assert completion["completed_at"] == "2026-11-16"


def test_toyohashi_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_toyohashi_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-232017"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_toyohashi_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "232017"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "豊橋市"
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
        "toyohashi-current-plan-period": "accepted",
        "toyohashi-current-policy-structure": "accepted",
        "toyohashi-progress-governance-framework": "accepted",
        "toyohashi-plan-transition": "accepted",
        "toyohashi-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The transition from the first-period to the latter basic plan
    # is recorded only as a version chronology, never by mapping the
    # latter plan's policies back onto the earlier period.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "toyohashi-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_toyohashi_current_plan_structure_is_the_latter_basic_plan():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "第6次豊橋市総合計画 後期基本計画"
    assert plan["vision"] == "未来を担う 人を育むまち・豊橋"
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2030
    assert structure["counts"] == {
        "basic_goals": 8,
        "basic_plan_measures": 38,
    }
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "toyohashi-sixth-latter-plan"

    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "豊かな人間性を備え、未来を創る人が育つまち",
        "活力みなぎり、はつらつと働けるまち",
        "命の安全、心の安心が確保されたまち",
        "みんなで支え合い、笑顔で健やかに暮らせるまち",
        "互いを尊重し合い、心豊かに暮らせるまち",
        "魅力にあふれ、いきいきとにぎわいあるまち",
        "自然と共生し、地球環境を大切にするまち",
        "暮らしの基盤が整った、便利で快適なまち",
    ]
    # The 38 policies of the latter basic plan are enumerated in
    # full (5+4+4+6+6+4+4+5).
    assert sum(len(field["measures"]) for field in fields) == 38

    strategy = plan["strategy_layer"]
    assert strategy["title"] == "まちづくり戦略"
    assert [item["name_ja"] for item in strategy["strategies"]] == [
        "安心に包まれた子育て・教育環境づくり",
        "希望に満ちた仕事づくり",
        "定住につながるまちの魅力づくり",
        "暮らしを支える都市空間づくり",
    ]
    # The four individual strategies carry 13 basic policies in
    # total (4+3+3+3).
    assert sum(len(item["basic_policies"]) for item in strategy["strategies"]) == 13

    plan_review = load(PLAN_REVIEW)
    identity = next(
        record
        for record in plan_review["records"]
        if record["id"] == "toyohashi-current-plan-period"
    )
    assert identity["value"] == "2026年度～2030年度"


def test_toyohashi_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "ローリング" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 belongs to the first basic plan period, a different
    # plan version from the latter basic plan.
    assert "前期基本計画" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_toyohashi_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-232017-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at sen-yen (thousand-yen)
    # precision, so the amount is kept at that precision and never
    # expanded into synthetic yen.
    assert budget["amount_yen"] == 165_610_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["toyohashi-budget-2026"]
    # Enacted as bill No. 4 (議案第4号), passed as proposed on
    # 2026-03-24 at the March 2026 regular session.
    assert "議案第4号" in budget["note"]
    assert "令和8年3月24日" in budget["note"]
    assert "原案可決" in budget["note"]

    revenue = by_id["jp-local-232017-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-232017-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in the
    # official settlement appendix (the account-level table and the
    # section summary table agree), so these are the exact
    # published totals and their difference must equal the balance
    # of 2,115,423,672 yen, consistent with the published
    # 2,115,424 thousand yen (rounded) in the settlement summary.
    assert revenue["amount_yen"] == 153_279_132_232
    assert expenditure["amount_yen"] == 151_163_708_560
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2_115_423_672
    # The settlement certification bill (bill No. 95, 議案第95号)
    # was voted NOT certified (不認定) at the September 2025
    # regular session. The records must state the rejection and
    # must never present the settlement as certified.
    assert "議案第95号" in revenue["note"]
    assert "不認定" in revenue["note"]
    assert "議案第95号" in expenditure["note"]
    assert "不認定" in expenditure["note"]


def test_toyohashi_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-232017-fiscal-2026-total-expenditure"
    )
    # The final cross-check against the budget book
    # (事項別明細書) at section level remains an explicit open
    # residual, carried over from the candidate; the
    # supplementary-budget history is deferred depth.
    assert len(budget_packet["open_questions"]) == 1
    assert "事項別明細書" in budget_packet["open_questions"][0]
    assert "議案第4号" in budget_packet["claims"][0]["statement"]
    assert "165,610,000千円" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-232017-fiscal-2024-total-revenue"
    )
    # The claim records the non-certification itself.
    assert "議案第95号" in revenue_packet["claims"][0]["statement"]
    assert "不認定" in revenue_packet["claims"][0]["statement"]
    # Two open residuals remain: the exact vote date of bill
    # No. 95 is still unidentified (the mayor's 2025-09-29
    # notification date is not asserted as the vote date), and
    # the final cross-check against the settlement book
    # (事項別明細書) is still outstanding.
    assert len(revenue_packet["open_questions"]) == 2
    assert any(
        "議決年月日" in question for question in revenue_packet["open_questions"]
    )
    assert any(
        "事項別明細書" in question for question in revenue_packet["open_questions"]
    )

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-232017-fiscal-2024-total-expenditure"
    )
    assert expenditure_packet["open_questions"] == []
    assert "不認定" in expenditure_packet["claims"][0]["statement"]


def test_toyohashi_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 8,
        "basic_plan_measures": 38,
        "promoted_implementation_item_actual_records": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-plan-granular-kpi-and-project-linkage" in deferred_ids
    assert "settlement-values-and-budget-amendment-linkage" in deferred_ids
    assert "plan-transition-version-depth" in deferred_ids
    assert "policy-outcome-causal-and-cross-city-comparability" in deferred_ids
    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in completion["deferred_depth"]
    )

    boundary = completion["completion_boundary"]
    # The boundary must record the owner's delegation to Muse,
    # not an owner-conducted review.
    assert "委任" in boundary
    assert "所有者本人が一次資料を直接レビューしたものではない" in boundary
    assert "2026-11-15" in boundary
    assert "not_assessable" in boundary
    # The budget stays at the published sen-yen precision.
    assert "千円精度のまま記録し、円単位を合成していない" in boundary
    assert "議案第4号" in boundary
    # The FY2024 settlement was NOT certified: the boundary states
    # the rejection itself and never claims a certification.
    assert "議案第95号" in boundary
    assert "不認定となった" in boundary
    assert "認定されたとは記録しない" in boundary
    # The vote date of bill No. 95 stays unidentified; the
    # notification date is not asserted as the vote date.
    assert "議決年月日そのものは未特定のまま保持" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_toyohashi_candidate_records_delegated_review():
    candidate = load(CANDIDATE)

    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-16"
    note = candidate["human_review"]["reviewer_note"]
    assert note
    # The note records that the owner explicitly delegated the
    # review to Muse in chat on 2026-11-15, and that the owner
    # did not personally review the primary sources.
    assert "レビューはあなたがやってください" in note
    assert "委任" in note
    assert "所有者本人が一次資料を直接レビューしたものではない" in note
    assert "議案第4号" in note
    assert "不認定" in note
    assert candidate["publication"]["eligible"] is False


def test_toyohashi_and_previous_twenty_nine_are_reviewed_complete_and_okazaki_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    toyohashi = by_code["232017"]
    assert toyohashi["status"] == "reviewed_complete"
    assert toyohashi["completion_path"] == "data/catalog/toyohashi_phase15_completion.json"
    assert (ROOT / toyohashi["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010", "192015", "202010", "202029",
        "212016",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 30
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 37
    assert queue["summary"]["next_official_code"] == "232025"
