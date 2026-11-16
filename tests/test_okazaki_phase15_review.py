from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/okazaki_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/okazaki_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/okazaki-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/okazaki_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/okazaki_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/okazaki-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/okazaki-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/okazaki-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/okazaki-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.okazaki.lg.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_okazaki_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "232025"
    assert completion["name_ja"] == "岡崎市"
    assert completion["completed_at"] == "2026-11-16"


def test_okazaki_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_okazaki_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-232025"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_okazaki_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "232025"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "岡崎市"
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
        "okazaki-current-plan-period": "accepted",
        "okazaki-current-policy-structure": "accepted",
        "okazaki-progress-governance-framework": "accepted",
        "okazaki-plan-transition": "accepted",
        "okazaki-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The transition from the Future Investment Plan's first
    # period to its latter period is recorded only as a version
    # chronology, never by mapping the latter plan's initiatives
    # back onto the earlier period.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "okazaki-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_okazaki_current_plan_structure_is_the_latter_plan():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "第7次岡崎市総合計画 後期計画"
    assert plan["vision"] == "一歩先の暮らしで三河を拓く 中枢・中核都市おかざき"
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2030
    assert structure["counts"] == {
        "basic_goals": 10,
        "basic_plan_measures": 54,
    }
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "okazaki-seventh-latter-plan"

    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "暮らしを支える都市づくり（都市インフラ）",
        "暮らしを守る強靭な都市づくり（防災・強靭化）",
        "持続可能な循環型の都市づくり（環境・農山村）",
        "多様な主体が協働・活躍できる社会づくり（地域社会）",
        "健康で生きがいをもって活躍できる社会づくり（保健・医療・福祉）",
        "女性や子どもがいきいきと輝ける社会づくり（子育て・男女共同参画）",
        "誰もが学び活躍できる社会づくり（教育・文化）",
        "商業と観光が成長産業となる地域経済づくり（商業・観光）",
        "ものづくりが柱でありつづける地域経済づくり（工業）",
        "スマートでスリムな行政運営の確立（行政・パートナーシップ）",
    ]
    # The 54 main initiatives of the latter plan are enumerated
    # in full (7+6+4+4+5+5+6+6+4+7).
    assert sum(len(field["measures"]) for field in fields) == 54

    strategy = plan["strategy_layer"]
    assert strategy["title"] == "未来投資パッケージ"
    assert [item["name_ja"] for item in strategy["strategies"]] == [
        "未来のまちパッケージ",
        "未来のひとパッケージ",
        "未来のしごとパッケージ",
        "未来のパートナーシップパッケージ",
    ]
    # The packages' project lists themselves are deferred depth,
    # so no per-package basic policies are promoted in v1.
    assert all(item["basic_policies"] == [] for item in strategy["strategies"])

    plan_review = load(PLAN_REVIEW)
    identity = next(
        record
        for record in plan_review["records"]
        if record["id"] == "okazaki-current-plan-period"
    )
    assert identity["value"] == "2026年度～2030年度"


def test_okazaki_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "4グループ" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 belongs to the Future Investment Plan's first
    # period, a different plan version from the latter plan.
    assert "前期" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_okazaki_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-232025-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at sen-yen (thousand-yen)
    # precision, so the amount is kept at that precision and never
    # expanded into synthetic yen.
    assert budget["amount_yen"] == 154_850_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["okazaki-budget-2026"]
    # Enacted as bill No. 56 (第56号議案), voted on 2026-03-23,
    # the final day of the March 2026 regular session. The
    # session's voting-results list itself was not retrieved, so
    # the record must keep the 原案可決 wording explicitly
    # unconfirmed instead of asserting it.
    assert "第56号議案" in budget["note"]
    assert "令和8年3月23日" in budget["note"]
    assert "未確認のまま保持" in budget["note"]

    revenue = by_id["jp-local-232025-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-232025-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in the
    # official settlement overview (the summary table and the
    # account-level table agree), so these are the exact published
    # totals and their difference must equal the published balance
    # of 9,256,197,154 yen (real balance 6,459,331,285 yen after
    # carryover funding).
    assert revenue["amount_yen"] == 157_798_763_028
    assert expenditure["amount_yen"] == 148_542_565_874
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 9_256_197_154
    # The settlement certification bill (certification bill
    # No. 1, 認定第1号) was certified on 2025-09-30 in the
    # September 2025 regular session per the council's official
    # voting-results list.
    assert "認定第1号" in revenue["note"]
    assert "令和7年9月30日" in revenue["note"]
    assert "認定第1号" in expenditure["note"]


def test_okazaki_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-232025-fiscal-2026-total-expenditure"
    )
    # Two open residuals remain: direct confirmation of the
    # 原案可決 wording from the March 2026 session's
    # voting-results list, and the final cross-check against the
    # budget book (事項別明細書) at section level.
    assert len(budget_packet["open_questions"]) == 2
    assert any(
        "議決結果一覧表" in question for question in budget_packet["open_questions"]
    )
    assert any(
        "事項別明細書" in question for question in budget_packet["open_questions"]
    )
    assert "第56号議案" in budget_packet["claims"][0]["statement"]
    assert "154,850,000千円" in budget_packet["claims"][0]["statement"]
    assert "未確認" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-232025-fiscal-2024-total-revenue"
    )
    # The claim records the certification itself.
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "令和7年9月30日" in revenue_packet["claims"][0]["statement"]
    # Two open residuals remain: the final cross-check against
    # the settlement book (事項別明細書) and the audit
    # commissioners' settlement review opinion.
    assert len(revenue_packet["open_questions"]) == 2
    assert any(
        "事項別明細書" in question for question in revenue_packet["open_questions"]
    )
    assert any("監査委員" in question for question in revenue_packet["open_questions"])

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-232025-fiscal-2024-total-expenditure"
    )
    assert expenditure_packet["open_questions"] == []
    assert "認定第1号" in expenditure_packet["claims"][0]["statement"]


def test_okazaki_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 10,
        "basic_plan_measures": 54,
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
    assert "第56号議案" in boundary
    # The 原案可決 wording stays unconfirmed: the boundary must
    # not assert it as confirmed.
    assert "『原案可決』の文言は未確認のまま保持する" in boundary
    # The FY2024 settlement was certified under certification
    # bill No. 1 on 2025-09-30.
    assert "認定第1号" in boundary
    assert "令和7年9月30日に認定された" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_okazaki_candidate_records_delegated_review():
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
    assert "第56号議案" in note
    assert "認定第1号" in note
    assert candidate["publication"]["eligible"] is False


def test_okazaki_and_previous_thirty_are_reviewed_complete_and_ichinomiya_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    okazaki = by_code["232025"]
    assert okazaki["status"] == "reviewed_complete"
    assert okazaki["completion_path"] == "data/catalog/okazaki_phase15_completion.json"
    assert (ROOT / okazaki["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010", "192015", "202010", "202029",
        "212016", "232017",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 50
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 17
    assert queue["summary"]["next_official_code"] == "332020"
