from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/hirakata_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/hirakata_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/hirakata-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/hirakata_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/hirakata_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/hirakata-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/hirakata-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/hirakata-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/hirakata-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.hirakata.osaka.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_hirakata_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "272108"
    assert completion["name_ja"] == "枚方市"
    assert completion["completed_at"] == "2026-11-16"


def test_hirakata_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_hirakata_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-272108"
    # Hirakata is a core city, so the municipality type is
    # "core_city" as inventoried.
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_hirakata_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "272108"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "枚方市"
    assert len(source_catalog["sources"]) == 5
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
        "hirakata-current-plan-period": "accepted",
        "hirakata-current-policy-structure": "accepted",
        "hirakata-progress-governance-framework": "accepted",
        "hirakata-plan-transition": "accepted",
        "hirakata-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The transition to the next comprehensive plan (starting
    # FY2028, now being formulated) is recorded only as a version
    # chronology, never by mapping the current plan's framework
    # forward into the next plan period.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "hirakata-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_hirakata_current_plan_structure_is_the_fifth_plan():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "第5次枚方市総合計画"
    assert plan["vision"] == "持続的に発展し、一人ひとりが輝くまち 枚方"
    assert plan["start_fiscal_year"] == 2016
    # The basic concept sets no fixed plan period, so the current
    # plan carries no end fiscal year.
    assert plan["end_fiscal_year"] is None
    assert plan["period_status"] == "verified_no_fixed_end"
    assert structure["counts"] == {
        "basic_goals": 32,
        "basic_plan_measures": 79,
    }
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "hirakata-fifth-plan"

    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "基本目標1-施策目標1 災害に対する備えができているまち",
        "基本目標1-施策目標2 災害時に、迅速・的確に対応できるまち",
        "基本目標1-施策目標3 暮らしに身近な安全が確保されたまち",
        "基本目標1-施策目標4 安全で快適な交通環境が整うまち",
        "基本目標1-施策目標5 快適で暮らしやすい環境を備えたまち",
        "基本目標2-施策目標6 誰もがいつまでも心身ともに健康に暮らせるまち",
        "基本目標2-施策目標7 公衆衛生や健康危機管理が充実したまち",
        "基本目標2-施策目標8 安心して適切な医療が受けられるまち",
        "基本目標2-施策目標9 高齢者が地域でいきいきと暮らせるまち",
        "基本目標2-施策目標10 障害者が自立し、社会参加ができるまち",
        "基本目標2-施策目標11 すべての人がお互いの人権を尊重しあうまち",
        "基本目標2-施策目標12 男女がともに参画し、個性を発揮できるまち",
        "基本目標2-施策目標13 平和の大切さを後世に伝えるまち",
        "基本目標3-施策目標14 安心して妊娠・出産できる環境が整うまち",
        "基本目標3-施策目標15 子どもたちが健やかに育つことができるまち",
        "基本目標3-施策目標16 子どもたちの生きる力を育む教育が充実したまち",
        "基本目標3-施策目標17 誰もが文化芸術やスポーツなどに親しみ、学び、感動できるまち",
        "基本目標4-施策目標18 人々が集い賑わい、魅力あふれる中心市街地のあるまち",
        "基本目標4-施策目標19 地域資源を生かし、人々の交流が盛んなまち",
        "基本目標4-施策目標20 いきいきと働くことのできるまち",
        "基本目標4-施策目標21 地域産業が活発に展開されるまち",
        "基本目標4-施策目標22 農を守り、生かすまち",
        "基本目標5-施策目標23 豊かな自然環境を大切にするまち",
        "基本目標5-施策目標24 まちなかのみどりを育てるまち",
        "基本目標5-施策目標25 ごみを減らし、資源の循環が進むまち",
        "基本目標5-施策目標26 安全で良好な生活環境が確保されたまち",
        "基本目標5-施策目標27 地球温暖化対策に取り組むまち",
        "基本目標5-施策目標28 美しく魅力あるまち並みが育まれるまち",
        "計画推進-計画推進29 市民との情報の共有化を進めます",
        "計画推進-計画推進30 市民による活発なまちづくり活動を支援します",
        "計画推進-計画推進31 持続可能な行財政運営を進めます",
        "計画推進-計画推進32 自治体間の広域連携や地方分権の推進を図ります",
    ]
    # The 79 policies of the basic plan and the Third Action Plan
    # are enumerated in full (15+16+18+10+10+10 across the five
    # basic goals and the plan-promotion units).
    assert sum(len(field["measures"]) for field in fields) == 79

    plan_review = load(PLAN_REVIEW)
    identity = next(
        record
        for record in plan_review["records"]
        if record["id"] == "hirakata-current-plan-period"
    )
    assert identity["value"] == (
        "基本構想は2016年度開始・計画期間を設定しない／基本計画は2016年度～2027年度"
        "／実行計画は4年間（現行は第3期・2024年度～2027年度）"
    )


def test_hirakata_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "実行計画" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 is inside the basic plan period and is the first year
    # of the Third Action Plan, so the plan version is the same;
    # the linkage stays not_assessable because no official
    # total-level mapping exists.
    assert "計画versionは同一" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_hirakata_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-272108-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at sen-yen (thousand-yen)
    # precision, so the amount is kept at that precision and never
    # expanded into synthetic yen.
    assert budget["amount_yen"] == 176_300_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["hirakata-budget-2026"]
    # Enacted as bill 議案第84号, passed as proposed at the March
    # 2026 regular session; both the wording and the voting date
    # were confirmed directly in the council's official
    # voting-results list, not inferred from the schedule.
    assert "議案第84号" in budget["note"]
    assert "令和8年3月27日" in budget["note"]
    assert "原案可決" in budget["note"]

    revenue = by_id["jp-local-272108-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-272108-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in the
    # official settlement book, so these are the exact published
    # totals and their difference must equal the printed balance
    # of 2,446,496,583 yen. The real balance is confirmed at yen
    # precision (1,938,746,472 yen) in the settlement summary
    # document, so it is kept at that precision; direct
    # confirmation of the real-balance statement itself in the
    # settlement book remains open.
    assert revenue["amount_yen"] == 167_040_111_596
    assert expenditure["amount_yen"] == 164_593_615_013
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2_446_496_583
    # The settlement certification bill is bill 認定第1号 and was
    # certified on 2025-10-17 at the September 2025 regular
    # session.
    assert "認定第1号" in revenue["note"]
    assert "令和7年10月17日）に認定された" in revenue["note"]
    assert "不認定" not in revenue["note"]
    assert "1,938,746,472円" in revenue["note"]
    assert "認定第1号" in expenditure["note"]
    assert "不認定" not in expenditure["note"]


def test_hirakata_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-272108-fiscal-2026-total-expenditure"
    )
    # One open residual remains: the final cross-check against the
    # budget book (事項別明細書) at section level.
    assert len(budget_packet["open_questions"]) == 1
    assert any(
        "事項別明細書" in question for question in budget_packet["open_questions"]
    )
    assert "議案第84号" in budget_packet["claims"][0]["statement"]
    assert "176,300,000千円" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-272108-fiscal-2024-total-revenue"
    )
    # The claim records the certification itself (bill 認定第1号)
    # and the real balance at its published yen precision.
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "不認定" not in revenue_packet["claims"][0]["statement"]
    assert "1,938,746,472円" in revenue_packet["claims"][0]["statement"]
    # Three open residuals remain: the final cross-check against
    # the settlement book (事項別明細書), the content of the audit
    # commissioners' review opinion, and direct confirmation of
    # the real-balance statement itself.
    assert len(revenue_packet["open_questions"]) == 3
    assert any(
        "事項別明細書" in question for question in revenue_packet["open_questions"]
    )
    assert any("監査委員" in question for question in revenue_packet["open_questions"])
    assert any(
        "実質収支に関する調書" in question
        for question in revenue_packet["open_questions"]
    )

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-272108-fiscal-2024-total-expenditure"
    )
    assert len(expenditure_packet["open_questions"]) == 1
    assert "164,593,615,013円" in expenditure_packet["claims"][0]["statement"]
    assert "認定第1号" in expenditure_packet["claims"][0]["statement"]
    assert "不認定" not in expenditure_packet["claims"][0]["statement"]


def test_hirakata_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 32,
        "basic_plan_measures": 79,
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
    # The budget stays at the published sen-yen precision and
    # was passed as proposed under bill 議案第84号.
    assert "千円精度のまま記録し、円単位を合成していない" in boundary
    assert "議案第84号" in boundary
    assert "原案可決" in boundary
    # The FY2024 settlement was certified under bill 認定第1号,
    # and the real balance is kept at yen precision.
    assert "認定第1号" in boundary
    assert "令和7年10月17日" in boundary
    assert "1,938,746,472円" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_hirakata_candidate_records_delegated_review():
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
    assert "議案第84号" in note
    assert "認定第1号" in note
    assert candidate["publication"]["eligible"] is False


def test_hirakata_and_previous_thirty_eight_are_reviewed_complete_and_yao_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    hirakata = by_code["272108"]
    assert hirakata["status"] == "reviewed_complete"
    assert hirakata["completion_path"] == "data/catalog/hirakata_phase15_completion.json"
    assert (ROOT / hirakata["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010", "192015", "202010", "202029",
        "212016", "232017", "232025", "232033", "232114", "242012",
        "252018", "272035", "272051", "272078",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 64
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 3
    assert queue["summary"]["next_official_code"] == "452017"
