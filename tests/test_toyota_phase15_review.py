from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/toyota_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/toyota_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/toyota-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/toyota_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/toyota_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/toyota-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/toyota-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/toyota-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/toyota-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.toyota.aichi.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_toyota_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "232114"
    assert completion["name_ja"] == "豊田市"
    assert completion["completed_at"] == "2026-11-16"


def test_toyota_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_toyota_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-232114"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_toyota_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "232114"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "豊田市"
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
        "toyota-current-plan-period": "accepted",
        "toyota-current-policy-structure": "accepted",
        "toyota-progress-governance-framework": "accepted",
        "toyota-plan-transition": "accepted",
        "toyota-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The transition from the Eighth to the Ninth Comprehensive
    # Plan is recorded only as a version chronology, never by
    # mapping the current plan's framework back onto the previous
    # plan period.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "toyota-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_toyota_current_plan_structure_is_the_mirai_strategy_2030():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "第9次豊田市総合計画 ミライ実現戦略2030"
    assert plan["vision"] == "つながる つくる 暮らし楽しむまち・とよた"
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2029
    assert structure["counts"] == {
        "basic_goals": 5,
        "basic_plan_measures": 30,
    }
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "toyota-ninth-plan"

    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "取組目標① こどもが多様な生き方・暮らし方を選択できる",
        "取組目標② 誰もがつながり合いの中で安心して自分らしく暮らすことができる",
        "取組目標③ 産業中枢都市として深化し続ける",
        "取組目標④ 将来を展望した都市環境の形成を進める",
        "取組目標⑤ 脱炭素社会の実現に挑戦する",
    ]
    # The 30 policies of the Mirai Realization Strategy 2030 are
    # enumerated in full (8+5+5+8+4).
    assert sum(len(field["measures"]) for field in fields) == 30

    plan_review = load(PLAN_REVIEW)
    identity = next(
        record
        for record in plan_review["records"]
        if record["id"] == "toyota-current-plan-period"
    )
    assert identity["value"] == "2025年度～2029年度"


def test_toyota_progress_keeps_rolling_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "ローリング" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 is a settlement of the Eighth Comprehensive Plan
    # period, while the current (Ninth) plan starts in FY2025, so
    # the plan version differs.
    assert "第8次" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_toyota_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-232114-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at sen-yen (thousand-yen)
    # precision, so the amount is kept at that precision and never
    # expanded into synthetic yen.
    assert budget["amount_yen"] == 211_800_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["toyota-budget-2026"]
    # Enacted as bill No. 45 (議案第45号), passed as proposed
    # (原案可決) on 2026-03-18 at the March 2026 regular session
    # per the council's official voting-result table. In that
    # table the result and date cells for bill No. 45 use the
    # ditto mark (〃), resolving to the table's explicit first
    # entry, and the record must keep that reading explicit.
    assert "議案第45号" in budget["note"]
    assert "令和8年3月18日" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "〃" in budget["note"]

    revenue = by_id["jp-local-232114-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-232114-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in the
    # official settlement book, so these are the exact published
    # totals and their difference must equal the published
    # balance of 17,058,632,730 yen. The real balance is
    # 8,192,990 thousand yen per the audit committee's review
    # opinion, kept at sen-yen precision; the real-balance
    # statement itself has not been directly confirmed.
    assert revenue["amount_yen"] == 246_602_084_906
    assert expenditure["amount_yen"] == 229_543_452_176
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 17_058_632_730
    # The settlement certification bill is styled approval bill
    # No. 4 (承認第4号) in Toyota and was certified on
    # 2025-09-24 in the September 2025 regular session per the
    # council's official voting-result table (not rejected).
    assert "承認第4号" in revenue["note"]
    assert "令和7年9月24日" in revenue["note"]
    assert "8,192,990千円" in revenue["note"]
    assert "調書そのものの直接確認は未実施" in revenue["note"]
    assert "承認第4号" in expenditure["note"]


def test_toyota_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-232114-fiscal-2026-total-expenditure"
    )
    # Two open residuals remain: direct confirmation of the vote
    # from the March 2026 session's minutes (including the
    # reading of the ditto-mark cells), and the final cross-check
    # against the budget explanation book (事項別明細書) at
    # section level.
    assert len(budget_packet["open_questions"]) == 2
    assert any(
        "会議録" in question for question in budget_packet["open_questions"]
    )
    assert any(
        "事項別明細書" in question for question in budget_packet["open_questions"]
    )
    assert "議案第45号" in budget_packet["claims"][0]["statement"]
    assert "211,800,000千円" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]
    assert "令和8年3月18日" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-232114-fiscal-2024-total-revenue"
    )
    # The claim records the certification itself and the real
    # balance at its published sen-yen precision.
    assert "承認第4号" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "不認定" not in revenue_packet["claims"][0]["statement"]
    assert "令和7年9月24日" in revenue_packet["claims"][0]["statement"]
    assert "8,192,990千円" in revenue_packet["claims"][0]["statement"]
    # Two open residuals remain: the final cross-check against
    # the settlement book (事項別明細書) and the direct
    # confirmation of the real-balance statement itself.
    assert len(revenue_packet["open_questions"]) == 2
    assert any(
        "事項別明細書" in question for question in revenue_packet["open_questions"]
    )
    assert any(
        "実質収支に関する調書" in question
        for question in revenue_packet["open_questions"]
    )

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-232114-fiscal-2024-total-expenditure"
    )
    assert expenditure_packet["open_questions"] == []
    assert "承認第4号" in expenditure_packet["claims"][0]["statement"]


def test_toyota_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 5,
        "basic_plan_measures": 30,
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
    assert "議案第45号" in boundary
    # The FY2024 settlement was certified under approval bill
    # No. 4 on 2025-09-24, and the real balance is kept at
    # sen-yen precision; the real-balance statement itself has
    # not been directly confirmed.
    assert "承認第4号" in boundary
    assert "令和7年9月24日に認定された" in boundary
    assert "8,192,990千円" in boundary
    assert "調書そのものの直接確認は未実施" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_toyota_candidate_records_delegated_review():
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
    assert "議案第45号" in note
    assert "承認第4号" in note
    assert candidate["publication"]["eligible"] is False


def test_toyota_and_previous_thirty_two_are_reviewed_complete_and_tsu_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    toyota = by_code["232114"]
    assert toyota["status"] == "reviewed_complete"
    assert (
        toyota["completion_path"]
        == "data/catalog/toyota_phase15_completion.json"
    )
    assert (ROOT / toyota["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010", "192015", "202010", "202029",
        "212016", "232017", "232025", "232033",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 38
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 29
    assert queue["summary"]["next_official_code"] == "272108"
