from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/fukui_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/fukui_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/fukui-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/fukui_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/fukui_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/fukui-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/fukui-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/fukui-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/fukui-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.fukui.lg.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_fukui_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "182010"
    assert completion["name_ja"] == "福井市"
    assert completion["completed_at"] == "2026-11-16"


def test_fukui_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_fukui_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-182010"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_fukui_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "182010"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "福井市"
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
        "fukui-current-plan-period": "accepted",
        "fukui-current-policy-structure": "accepted",
        "fukui-progress-governance-framework": "accepted",
        "fukui-ninth-plan-transition": "accepted",
        "fukui-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The next (ninth) plan is recorded only as a version
    # chronology, never merged back into the eighth plan's
    # framework.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "fukui-ninth-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_fukui_plan_period_and_structure_are_reviewed():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "第八次福井市総合計画"
    assert plan["start_fiscal_year"] == 2022
    assert plan["end_fiscal_year"] == 2026
    assert plan["vision"] == "みんなが輝く 全国に誇れる ふくい"
    assert structure["counts"] == {"basic_goals": 4, "basic_plan_measures": 14}
    assert structure["review_status"] == "reviewed"

    # The plan is a five-year plan structured as vision /
    # priority policies / policies / measures with a separate
    # implementation plan. Its fields are the four published
    # fields and the measures under them are the 14 policies,
    # exactly as published in the city's official FY2024 KPI
    # report; the 53 measures and 64 KPIs beneath the policies
    # are not enumerated in v1.
    layers = {component["layer"] for component in plan["components"]}
    assert layers == {"comprehensive_plan", "implementation_plan"}
    assert plan["basic_goals"]["count"] == 4
    assert plan["basic_goals"]["names"] == [
        "社会基盤分野（快適に暮らすまち）",
        "市民福祉分野（住みよいまち）",
        "産業分野（活き活きと働くまち）",
        "教育分野（学び成長するまち）",
    ]
    assert plan["basic_goals"]["measures_count"] == 14
    assert plan["basic_goals"]["measures_per_goal"] == [3, 5, 3, 3]
    assert sum(plan["basic_goals"]["measures_per_goal"]) == 14
    assert plan["basic_goals"]["measures_by_goal"][1] == [
        "地域活性化に関する政策",
        "共生、協働に関する政策",
        "福祉に関する政策",
        "環境に関する政策",
        "防災、安全安心に関する政策",
    ]

    # The plan framework was confirmed from official
    # comprehensive-plan reports because retrieval of the plan
    # book pages failed; that provenance must stay explicit
    # instead of claiming confirmation from the plan book.
    assert "計画本編ページの取得が失敗" in plan["structure"]
    assert "計画本編ページの取得が失敗" in structure["review_boundary"]

    plan_review = load(PLAN_REVIEW)
    period = next(
        record
        for record in plan_review["records"]
        if record["id"] == "fukui-current-plan-period"
    )
    assert period["value"] == "2022年度～2026年度"


def test_fukui_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "総合計画レポート" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    assert "監査委員" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 is the third year of the plan period, but its
    # totals are section-level aggregates with no mapping to
    # individual policies, measures or KPIs.
    assert "款別" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_fukui_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-182010-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 137_700_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["fukui-budget-2026"]
    # Enactment is bill No. 1 (第1号議案), passed as proposed
    # (原案可決) on 2026-03-19 at the March 2026 regular
    # council session.
    assert "第1号議案" in budget["note"]
    assert "令和8年3月19日" in budget["note"]
    assert "原案可決" in budget["note"]

    revenue = by_id["jp-local-182010-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-182010-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in
    # the official settlement summary table (総表・その2), so
    # these are the exact published totals and their difference
    # must equal the published balance (差引・形式収支) of
    # 3,208,396,731 yen.
    assert revenue["amount_yen"] == 133_427_298_121
    assert expenditure["amount_yen"] == 130_218_901_390
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 3_208_396_731
    assert "第66号議案" in revenue["note"]
    assert "第66号議案" in expenditure["note"]
    assert "令和7年12月1日" in revenue["note"]


def test_fukui_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-182010-fiscal-2026-total-expenditure"
    )
    # The final cross-check against the budget book's bill text
    # and first table remains an explicit open residual, carried
    # over from the candidate.
    assert len(budget_packet["open_questions"]) == 1
    assert "第1号議案第1条" in budget_packet["open_questions"][0]
    assert "第1号議案" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-182010-fiscal-2024-total-revenue"
    )
    # The cross-check against the settlement detail book and
    # the inspection of the audit committee's opinion remain
    # explicit open residuals, carried over from the candidate.
    assert len(revenue_packet["open_questions"]) == 2
    assert "明細書" in revenue_packet["open_questions"][0]
    assert "監査委員" in revenue_packet["open_questions"][1]
    assert "第66号議案" in revenue_packet["claims"][0]["statement"]
    assert "令和7年12月1日" in revenue_packet["claims"][0]["statement"]

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-182010-fiscal-2024-total-expenditure"
    )
    assert expenditure_packet["open_questions"] == []


def test_fukui_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert completion["quality_gate"]["current_plan_period_reviewed"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 4,
        "basic_plan_measures": 14,
        "promoted_implementation_item_actual_records": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-plan-granular-kpi-and-project-linkage" in deferred_ids
    assert "plan-transition-version-depth" in deferred_ids
    assert "settlement-audit-opinion-inspection" in deferred_ids
    assert "current-plan-annual-evaluation-evidence" in deferred_ids
    assert "fiscal-detail-and-amendment-linkage" in deferred_ids
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
    # The plan framework's provenance stays honest: it was
    # confirmed from official reports after retrieval of the
    # plan book pages failed.
    assert "計画本編ページの取得が失敗" in boundary
    assert "第66号議案" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_fukui_candidate_records_delegated_review():
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
    assert "計画本編ページの取得が失敗" in note
    assert candidate["publication"]["eligible"] is False


def test_fukui_and_previous_twenty_four_are_reviewed_complete_and_kofu_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    fukui = by_code["182010"]
    assert fukui["status"] == "reviewed_complete"
    assert (
        fukui["completion_path"]
        == "data/catalog/fukui_phase15_completion.json"
    )
    assert (ROOT / fukui["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 30
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 37
    assert queue["summary"]["next_official_code"] == "232025"
