from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/tsu_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/tsu_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/tsu-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/tsu_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/tsu_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/tsu-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/tsu-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/tsu-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/tsu-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.info.city.tsu.mie.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_tsu_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "242012"
    assert completion["name_ja"] == "津市"
    assert completion["completed_at"] == "2026-11-16"


def test_tsu_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_tsu_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-242012"
    # Tsu is a prefectural capital but not a core city, so the
    # municipality type stays "city" exactly as inventoried.
    assert municipality["municipality_type"] == "city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_tsu_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "242012"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "津市"
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
        "tsu-current-plan-period": "accepted",
        "tsu-current-policy-structure": "accepted",
        "tsu-progress-governance-framework": "accepted",
        "tsu-plan-transition": "accepted",
        "tsu-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The transition from the preceding plans to the current
    # plan, and the formulation of the next plan, are recorded
    # only as a version chronology, never by mapping the current
    # plan's framework back onto the previous plan period.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "tsu-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_tsu_current_plan_structure_is_the_second_basic_plan():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "津市総合計画 第2次基本計画"
    assert (
        plan["vision"]
        == "笑顔があふれ幸せに暮らせる県都 津市 ～夢や希望、明るい未来が広がるまちへ～"
    )
    assert plan["start_fiscal_year"] == 2018
    assert plan["end_fiscal_year"] == 2027
    # The Basic Concept above the Second Basic Plan sets no
    # fixed plan period, and that fact is kept as published
    # rather than collapsed into a fixed-period model.
    assert structure["basic_concept_period_status"] == "no_fixed_end"
    assert structure["counts"] == {
        "basic_goals": 19,
        "basic_plan_measures": 53,
    }
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "tsu-second-basic-plan"

    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "目標1-基本政策1 安心して子どもを生み育てられる環境の充実",
        "目標1-基本政策2 子どもたちの生きる力を育み成長を支える環境の充実",
        "目標2-基本政策1 社会の変化に対応した福祉の充実",
        "目標2-基本政策2 健康づくりの推進と医療体制の充実",
        "目標3-基本政策1 いざという時の備えの強化",
        "目標3-基本政策2 防犯・交通安全対策の強化",
        "目標4-基本政策1 環境にやさしい社会の形成",
        "目標4-基本政策2 持続可能な都市基盤の整備",
        "目標4-基本政策3 快適に暮らせる都市空間の形成",
        "目標5-基本政策1 生涯を通じた学びの推進",
        "目標5-基本政策2 スポーツや文化の輪が広がる社会の形成",
        "目標5-基本政策3 つながり広がるコミュニティの醸成",
        "目標5-基本政策4 誰もが尊重され暮らしやすい社会の実現",
        "目標6-基本政策1 働ける・働きたくなる環境の整備",
        "目標6-基本政策2 地域に根付く商工業の振興",
        "目標6-基本政策3 食の安定と暮らしを支える農林水産業の振興",
        "目標6-基本政策4 交流人口の拡大",
        "将来像の実現に向けて-1 市民の思いや願いに応える市役所",
        "将来像の実現に向けて-2 高みをめざす行政経営",
    ]
    # The 53 policies of the Second Basic Plan are enumerated
    # in full (5+8+5+12+10+9+4 across the six goals and the
    # cross-cutting block).
    assert sum(len(field["measures"]) for field in fields) == 53

    plan_review = load(PLAN_REVIEW)
    identity = next(
        record
        for record in plan_review["records"]
        if record["id"] == "tsu-current-plan-period"
    )
    assert identity["value"] == "2018年度～2027年度"


def test_tsu_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "事務事業評価" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 is a settlement inside the Second Basic Plan
    # period, so the plan version is the same; what is missing
    # is any official total-level mapping to the plan.
    assert "計画versionは同一" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_tsu_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-242012-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at sen-yen (thousand-yen)
    # precision, so the amount is kept at that precision and never
    # expanded into synthetic yen.
    assert budget["amount_yen"] == 124_187_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["tsu-budget-2026"]
    # Enacted as bill No. 39 (議案第39号), passed as proposed
    # (原案可決) on 2026-03-26 at the first regular session of
    # 2026 per the council's official voting-result table, with
    # the plenary minutes directly recording the passage as
    # proposed as well.
    assert "議案第39号" in budget["note"]
    assert "令和8年3月26日" in budget["note"]
    assert "原案可決" in budget["note"]

    revenue = by_id["jp-local-242012-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-242012-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in the
    # official settlement book, so these are the exact published
    # totals and their difference must equal the balance of
    # 466,767,600 yen recorded in the real-balance statement.
    # The real balance itself is 175,738,909 yen at yen
    # precision, exactly as published in that statement.
    assert revenue["amount_yen"] == 123_307_646_176
    assert expenditure["amount_yen"] == 122_840_878_576
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 466_767_600
    # The settlement certification bill is certification bill
    # No. 1 (認定第1号) and was certified on 2025-09-25 in the
    # third regular session of 2025 per the council's official
    # voting-result table (not rejected).
    assert "認定第1号" in revenue["note"]
    assert "令和7年9月25日" in revenue["note"]
    assert "175,738,909円" in revenue["note"]
    assert "認定第1号" in expenditure["note"]


def test_tsu_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-242012-fiscal-2026-total-expenditure"
    )
    # One open residual remains: the final cross-check against
    # the budget explanation book (事項別明細書) at section
    # level.
    assert len(budget_packet["open_questions"]) == 1
    assert any(
        "事項別明細書" in question for question in budget_packet["open_questions"]
    )
    assert "議案第39号" in budget_packet["claims"][0]["statement"]
    assert "124,187,000千円" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]
    assert "令和8年3月26日" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-242012-fiscal-2024-total-revenue"
    )
    # The claim records the certification itself and the real
    # balance at its published yen precision.
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "不認定" not in revenue_packet["claims"][0]["statement"]
    assert "令和7年9月25日" in revenue_packet["claims"][0]["statement"]
    assert "175,738,909円" in revenue_packet["claims"][0]["statement"]
    # Two open residuals remain: the final cross-check against
    # the settlement book (事項別明細書) and the contents of
    # the audit commissioners' settlement review opinion.
    assert len(revenue_packet["open_questions"]) == 2
    assert any(
        "事項別明細書" in question for question in revenue_packet["open_questions"]
    )
    assert any(
        "監査委員" in question for question in revenue_packet["open_questions"]
    )

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-242012-fiscal-2024-total-expenditure"
    )
    assert expenditure_packet["open_questions"] == []
    assert "認定第1号" in expenditure_packet["claims"][0]["statement"]


def test_tsu_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 19,
        "basic_plan_measures": 53,
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
    assert "議案第39号" in boundary
    # The FY2024 settlement was certified under certification
    # bill No. 1 on 2025-09-25, and the real balance is kept at
    # yen precision as published in the statement itself.
    assert "認定第1号" in boundary
    assert "令和7年9月25日に認定された" in boundary
    assert "175,738,909円" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_tsu_candidate_records_delegated_review():
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
    assert "議案第39号" in note
    assert "認定第1号" in note
    assert candidate["publication"]["eligible"] is False


def test_tsu_and_previous_thirty_three_are_reviewed_complete_and_otsu_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    tsu = by_code["242012"]
    assert tsu["status"] == "reviewed_complete"
    assert tsu["completion_path"] == "data/catalog/tsu_phase15_completion.json"
    assert (ROOT / tsu["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010", "192015", "202010", "202029",
        "212016", "232017", "232025", "232033", "232114",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 53
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 14
    assert queue["summary"]["next_official_code"] == "352012"
