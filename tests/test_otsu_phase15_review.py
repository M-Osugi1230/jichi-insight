from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/otsu_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/otsu_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/otsu-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/otsu_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/otsu_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/otsu-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/otsu-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/otsu-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/otsu-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.otsu.lg.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_otsu_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "252018"
    assert completion["name_ja"] == "大津市"
    assert completion["completed_at"] == "2026-11-16"


def test_otsu_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_otsu_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-252018"
    # Otsu is both a core city and the prefectural capital, so
    # the municipality type is "core_city" as inventoried.
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_otsu_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "252018"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "大津市"
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
        "otsu-current-plan-period": "accepted",
        "otsu-current-policy-structure": "accepted",
        "otsu-progress-governance-framework": "accepted",
        "otsu-plan-transition": "accepted",
        "otsu-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The succession of action plans is recorded only as a
    # version chronology, never by mapping the current plan's
    # framework back onto a previous plan period.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "otsu-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_otsu_current_plan_structure_is_the_third_action_plan():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "大津市総合計画 第3期実行計画"
    assert (
        plan["vision"]
        == "ひと、自然、歴史の縁で織りなす 住み続けたいまち“大津再生” "
        "～コンパクトで持続可能なまちへの変革～"
    )
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2028
    assert structure["counts"] == {
        "basic_goals": 13,
        "basic_plan_measures": 32,
    }
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "otsu-general-plan-third-action"

    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "基本方針1-基本政策1 子どもの未来が輝くまちにします",
        "基本方針1-基本政策2 心豊かに暮らせる、福祉が充実したまちにします",
        "基本方針1-基本政策3 生き生きと健康に過ごせるまちにします",
        "基本方針1-基本政策4 つながりを大切にし、共に支え合うまちにします",
        "基本方針2-基本政策5 インバウンド観光で人が集い、にぎわうまちにします",
        "基本方針2-基本政策6 自然豊かな景観を守り育て、自然と共生するまちにします",
        "基本方針2-基本政策7 悠久の歴史と文化を大切にし、次代に継承します",
        "基本方針2-基本政策8 スポーツと文化で、生き生きと楽しむまちにします",
        "基本方針3-基本政策9 安心、安全に暮らすことのできるまちにします",
        "基本方針3-基本政策10 コンパクトで質の高い持続可能なまちにします",
        "基本方針3-基本政策11 経済が活性化し、元気なまちにします",
        "基本方針3-基本政策12 再生可能エネルギーの活用とごみの適正処理でクリーンなまちにします",
        "基本方針3-基本政策13 徹底した行財政改革を進め、確かな都市経営を進めます",
    ]
    # The 32 measures of the third action plan are enumerated
    # in full (11+8+13 across the three basic directions).
    assert sum(len(field["measures"]) for field in fields) == 32

    plan_review = load(PLAN_REVIEW)
    identity = next(
        record
        for record in plan_review["records"]
        if record["id"] == "otsu-current-plan-period"
    )
    assert identity["value"] == "2017年度～2028年度"


def test_otsu_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "行政評価" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 is the final-year settlement of the second action
    # plan, so the plan version differs from the current third
    # action plan.
    assert "計画versionが異なる" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_otsu_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-252018-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at sen-yen (thousand-yen)
    # precision, so the amount is kept at that precision and never
    # expanded into synthetic yen.
    assert budget["amount_yen"] == 142_684_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["otsu-budget-2026"]
    # Enacted as bill No. 3 (議案第3号), passed on 2026-03-25 at
    # the February 2026 regular session. The council's published
    # result wording is only "可決（多数）" and does not state
    # 原案可決, so that wording must not be asserted anywhere.
    assert "議案第3号" in budget["note"]
    assert "令和8年3月25日" in budget["note"]
    assert "可決（多数）" in budget["note"]
    assert "『原案可決』とは表記していない" in budget["note"]
    assert "原案可決され" not in budget["note"]

    revenue = by_id["jp-local-252018-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-252018-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in the
    # official settlement book attached to bill No. 110, so these
    # are the exact published totals and their difference must
    # equal the balance of 2,976,660,134 yen printed in that book.
    # The real balance is confirmed only at thousand-yen
    # precision (2,791,920 thousand yen) in the audit
    # commissioners' settlement review opinion, so it is kept at
    # that precision and the yen value in the real-balance
    # statement itself stays unconfirmed.
    assert revenue["amount_yen"] == 146_909_564_029
    assert expenditure["amount_yen"] == 143_932_903_895
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2_976_660_134
    assert expenditure["amount_yen"] + 2_684_839_000 + 3_581_702_105 == 150_199_445_000
    # The settlement certification bill is bill No. 110
    # (議案第110号) and was certified on 2025-10-28 per the
    # council's official bill-result list (not rejected).
    assert "議案第110号" in revenue["note"]
    assert "令和7年10月28日" in revenue["note"]
    assert "2,791,920千円" in revenue["note"]
    assert "議案第110号" in expenditure["note"]


def test_otsu_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-252018-fiscal-2026-total-expenditure"
    )
    # Two open residuals remain: direct confirmation of the
    # 原案可決 wording in the plenary minutes (the published
    # wording is only 可決（多数）), and the final cross-check
    # against the budget explanation book (事項別明細書) at
    # section level.
    assert len(budget_packet["open_questions"]) == 2
    assert any(
        "原案可決" in question for question in budget_packet["open_questions"]
    )
    assert any(
        "事項別明細書" in question for question in budget_packet["open_questions"]
    )
    assert "議案第3号" in budget_packet["claims"][0]["statement"]
    assert "142,684,000千円" in budget_packet["claims"][0]["statement"]
    assert "可決（多数）" in budget_packet["claims"][0]["statement"]
    assert "原案可決され" not in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-252018-fiscal-2024-total-revenue"
    )
    # The claim records the certification itself and the real
    # balance at its published thousand-yen precision.
    assert "議案第110号" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "不認定" not in revenue_packet["claims"][0]["statement"]
    assert "令和7年10月28日" in revenue_packet["claims"][0]["statement"]
    assert "2,791,920千円" in revenue_packet["claims"][0]["statement"]
    # Two open residuals remain: the yen value in the
    # real-balance statement itself, and the final cross-check
    # against the settlement book (事項別明細書).
    assert len(revenue_packet["open_questions"]) == 2
    assert any(
        "実質収支" in question for question in revenue_packet["open_questions"]
    )
    assert any(
        "事項別明細書" in question for question in revenue_packet["open_questions"]
    )

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-252018-fiscal-2024-total-expenditure"
    )
    assert len(expenditure_packet["open_questions"]) == 1
    assert "議案第110号" in expenditure_packet["claims"][0]["statement"]


def test_otsu_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 13,
        "basic_plan_measures": 32,
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
    # The budget stays at the published sen-yen precision, and
    # the 原案可決 wording is not asserted.
    assert "千円精度のまま記録し、円単位を合成していない" in boundary
    assert "議案第3号" in boundary
    assert "『原案可決』の文言は断定せず未確認のまま保持する" in boundary
    # The FY2024 settlement was certified under bill No. 110 on
    # 2025-10-28, and the real balance is kept at thousand-yen
    # precision as published in the audit opinion.
    assert "議案第110号" in boundary
    assert "令和7年10月28日に認定された" in boundary
    assert "2,791,920千円" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_otsu_candidate_records_delegated_review():
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
    assert "議案第3号" in note
    assert "議案第110号" in note
    assert candidate["publication"]["eligible"] is False


def test_otsu_and_previous_thirty_four_are_reviewed_complete_and_toyonaka_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    otsu = by_code["252018"]
    assert otsu["status"] == "reviewed_complete"
    assert otsu["completion_path"] == "data/catalog/otsu_phase15_completion.json"
    assert (ROOT / otsu["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010", "192015", "202010", "202029",
        "212016", "232017", "232025", "232033", "232114", "242012",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 45
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 22
    assert queue["summary"]["next_official_code"] == "282049"
