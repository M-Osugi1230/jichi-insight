from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/neyagawa_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/neyagawa_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/neyagawa-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/neyagawa_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/neyagawa_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/neyagawa-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/neyagawa-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/neyagawa-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/neyagawa-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.neyagawa.osaka.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_neyagawa_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "272159"
    assert completion["name_ja"] == "寝屋川市"
    assert completion["completed_at"] == "2026-11-16"


def test_neyagawa_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_neyagawa_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-272159"
    # Neyagawa is a core city, so the municipality type is
    # "core_city" as inventoried.
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_neyagawa_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "272159"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "寝屋川市"
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
        "neyagawa-current-plan-period": "accepted",
        "neyagawa-current-policy-structure": "accepted",
        "neyagawa-progress-governance-framework": "accepted",
        "neyagawa-plan-transition": "accepted",
        "neyagawa-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The transition from the earlier implementation plan to the
    # latter implementation plan inside the Sixth Plan is recorded
    # only as a version chronology, never by mapping the earlier
    # period's results forward into the latter period.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "neyagawa-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_neyagawa_current_plan_structure_is_the_sixth_plan():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "第六次寝屋川市総合計画 後期実施計画"
    assert plan["vision"] == "新たな価値を創り、選ばれるまち 寝屋川"
    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2027
    assert plan["period_status"] == "verified_fixed_period"
    # Neyagawa's structure differs from a goal/policy hierarchy:
    # the five policy fields are the three key factors plus the
    # life-supporting and quality-of-life groups, and the measures
    # are the strategic plan's 19 measures.
    assert structure["counts"] == {
        "basic_goals": 5,
        "basic_plan_measures": 19,
    }
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "neyagawa-sixth-plan"

    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "ファクターI 子どもに最善を尽くす（訴求力のある施策）",
        "ファクターII 誰もが住みたくなるまちをつくる（訴求力のある施策）",
        "ファクターIII 命を全力で守り、豊かなくらしを実現する（訴求力のある施策）",
        "生活を支える施策",
        "くらしの質を高める施策",
    ]
    measures = [measure for field in fields for measure in field["measures"]]
    assert len(measures) == 19
    assert len(set(measures)) == 19

    plan_review = load(PLAN_REVIEW)
    identity = next(
        record
        for record in plan_review["records"]
        if record["id"] == "neyagawa-current-plan-period"
    )
    assert identity["value"] == (
        "基本戦略（基本構想・戦略プラン）は2021年度～2027年度（7年間）／"
        "実施計画は前期2021年度～2023年度（3年間）・後期2024年度～2027年度（4年間）"
    )


def test_neyagawa_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "PDCI" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 is the first year of the latter implementation plan,
    # so the plan version is the same as the current one; the
    # linkage still stays not_assessable because no official
    # total-level mapping exists.
    assert "計画の版は現行の後期実施計画と同一" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_neyagawa_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-272159-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at man-yen (ten-thousand-yen)
    # precision, so the amount is kept at that precision and the
    # sen-yen-precision exact total is left as an open question.
    assert budget["amount_yen"] == 109_730_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["neyagawa-budget-2026"]
    # Enacted as bill 議案第28号, passed as proposed at the March
    # 2026 regular session; both the wording and the voting date
    # were confirmed directly in the council's official list of
    # submitted items, not inferred from the schedule.
    assert "議案第28号" in budget["note"]
    assert "2026年3月25日" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "万円単位" in budget["note"]

    revenue = by_id["jp-local-272159-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-272159-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at sen-yen
    # (thousand-yen) precision, so the amounts are kept at that
    # precision and never expanded into synthetic yen; their
    # difference must equal the balance printed in the
    # real-balance statement (1,263,633 thousand yen), and the
    # real balance is 1,248,678 thousand yen.
    assert revenue["amount_yen"] == 106_597_604_000
    assert expenditure["amount_yen"] == 105_333_971_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1_263_633_000
    # The settlement certification bill is bill 認定第1号 and was
    # certified on 2025-12-03 at the December 2025 regular
    # session after continued review.
    assert "認定第1号" in revenue["note"]
    assert "2025年12月3日に認定された" in revenue["note"]
    assert "不認定" not in revenue["note"]
    assert "1,248,678千円" in revenue["note"]
    assert "認定第1号" in expenditure["note"]
    assert "不認定" not in expenditure["note"]


def test_neyagawa_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-272159-fiscal-2026-total-expenditure"
    )
    # Two open residuals remain: the exact sen-yen-precision
    # budget total in the initial budget book, and the final
    # cross-check against the budget book (事項別明細書).
    assert len(budget_packet["open_questions"]) == 2
    assert any("千円" in question for question in budget_packet["open_questions"])
    assert any(
        "事項別明細書" in question for question in budget_packet["open_questions"]
    )
    assert "議案第28号" in budget_packet["claims"][0]["statement"]
    assert "109,730,000千円" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-272159-fiscal-2024-total-revenue"
    )
    # The claim records the certification itself (bill 認定第1号)
    # and the real balance at its published sen-yen precision.
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "不認定" not in revenue_packet["claims"][0]["statement"]
    assert "106,597,604千円" in revenue_packet["claims"][0]["statement"]
    assert "1,248,678千円" in revenue_packet["claims"][0]["statement"]
    # Two open residuals remain: the final cross-check against the
    # settlement book (事項別明細書) and the content of the audit
    # commissioners' review opinion.
    assert len(revenue_packet["open_questions"]) == 2
    assert any(
        "事項別明細書" in question for question in revenue_packet["open_questions"]
    )
    assert any("監査委員" in question for question in revenue_packet["open_questions"])

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-272159-fiscal-2024-total-expenditure"
    )
    assert len(expenditure_packet["open_questions"]) == 1
    assert "105,333,971千円" in expenditure_packet["claims"][0]["statement"]
    assert "認定第1号" in expenditure_packet["claims"][0]["statement"]
    assert "不認定" not in expenditure_packet["claims"][0]["statement"]


def test_neyagawa_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 5,
        "basic_plan_measures": 19,
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
    # The budget stays at the published man-yen precision and
    # was passed as proposed under bill 議案第28号.
    assert "万円単位" in boundary
    assert "合成していない" in boundary
    assert "議案第28号" in boundary
    assert "原案可決" in boundary
    # The FY2024 settlement was certified under bill 認定第1号,
    # and the real balance is kept at sen-yen precision.
    assert "認定第1号" in boundary
    assert "2025年12月3日" in boundary
    assert "1,248,678千円" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_neyagawa_candidate_records_delegated_review():
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
    assert "議案第28号" in note
    assert "認定第1号" in note
    assert candidate["publication"]["eligible"] is False


def test_neyagawa_and_previous_forty_are_reviewed_complete_and_higashiosaka_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    neyagawa = by_code["272159"]
    assert neyagawa["status"] == "reviewed_complete"
    assert neyagawa["completion_path"] == "data/catalog/neyagawa_phase15_completion.json"
    assert (ROOT / neyagawa["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010", "192015", "202010", "202029",
        "212016", "232017", "232025", "232033", "232114", "242012",
        "252018", "272035", "272051", "272078", "272108", "272124",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 47
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 20
    assert queue["summary"]["next_official_code"] == "302015"
