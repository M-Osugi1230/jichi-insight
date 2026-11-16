from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/toyonaka_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/toyonaka_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/toyonaka-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/toyonaka_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/toyonaka_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/toyonaka-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/toyonaka-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/toyonaka-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/toyonaka-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.toyonaka.osaka.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_toyonaka_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "272035"
    assert completion["name_ja"] == "豊中市"
    assert completion["completed_at"] == "2026-11-16"


def test_toyonaka_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_toyonaka_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-272035"
    # Toyonaka is a core city, so the municipality type is
    # "core_city" as inventoried.
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_toyonaka_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "272035"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "豊中市"
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
        "toyonaka-current-plan-period": "accepted",
        "toyonaka-current-policy-structure": "accepted",
        "toyonaka-progress-governance-framework": "accepted",
        "toyonaka-plan-transition": "accepted",
        "toyonaka-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The succession of basic plans is recorded only as a
    # version chronology, never by mapping the current plan's
    # framework back onto a previous plan period.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "toyonaka-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_toyonaka_current_plan_structure_is_the_latter_basic_plan():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "第4次豊中市総合計画 後期基本計画"
    assert plan["vision"] == "みらい創造都市 とよなか ～明日がもっと楽しみなまち～"
    assert plan["start_fiscal_year"] == 2023
    assert plan["end_fiscal_year"] == 2027
    assert structure["counts"] == {
        "basic_goals": 5,
        "basic_plan_measures": 16,
    }
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "toyonaka-fourth-latter-plan"

    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "第1章 子ども・若者が夢や希望をもてるまちづくり",
        "第2章 安全に安心して暮らせるまちづくり",
        "第3章 活力ある快適なまちづくり",
        "第4章 いきいきと心豊かに暮らせるまちづくり",
        "第5章 施策推進に向けた取組み",
    ]
    # The 16 measures of the latter basic plan are enumerated
    # in full (3+4+5+2+2 across the five chapters). The leading
    # project is kept outside the measure count.
    assert sum(len(field["measures"]) for field in fields) == 16

    plan_review = load(PLAN_REVIEW)
    identity = next(
        record
        for record in plan_review["records"]
        if record["id"] == "toyonaka-current-plan-period"
    )
    assert identity["value"] == "2018年度～2027年度"


def test_toyonaka_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "政策評価" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 sits inside the latter basic plan period, so the
    # plan version is the same; the linkage stays not_assessable
    # because no official total-level mapping exists.
    assert "計画versionは同一" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_toyonaka_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-272035-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at sen-yen (thousand-yen)
    # precision, so the amount is kept at that precision and never
    # expanded into synthetic yen.
    assert budget["amount_yen"] == 206_946_719_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["toyonaka-budget-2026"]
    # Enacted as bill 市議案第8号, passed as proposed on
    # 2026-03-23 at the March 2026 regular session per the
    # council's official voting-results list.
    assert "市議案第8号" in budget["note"]
    assert "令和8年3月23日" in budget["note"]
    assert "原案可決" in budget["note"]

    revenue = by_id["jp-local-272035-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-272035-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in the
    # official settlement book, so these are the exact published
    # totals and their difference must equal the balance of
    # 5,472,555,198 yen printed in that book. The real balance is
    # confirmed at thousand-yen precision (4,930,077 thousand yen)
    # in the real-balance statement itself, so it is kept at that
    # precision.
    assert revenue["amount_yen"] == 197_263_021_788
    assert expenditure["amount_yen"] == 191_790_466_590
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 5_472_555_198
    assert expenditure["amount_yen"] + 4_049_909_000 + 11_524_209_410 == 207_364_585_000
    # The settlement certification bill is bill 市議案第74号 and
    # was voted NOT certified (不認定) on 2025-11-28 at the
    # December 2025 regular session. The records must state the
    # rejection and must never present the settlement as
    # certified: the wording 認定された must not appear.
    assert "市議案第74号" in revenue["note"]
    assert "不認定" in revenue["note"]
    assert "認定された" not in revenue["note"]
    assert "4,930,077千円" in revenue["note"]
    assert "市議案第74号" in expenditure["note"]
    assert "不認定" in expenditure["note"]
    assert "認定された" not in expenditure["note"]


def test_toyonaka_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-272035-fiscal-2026-total-expenditure"
    )
    # The final cross-check against the budget explanation book
    # (事項別明細書) at section level remains an explicit open
    # residual; the supplementary-budget history is deferred
    # depth.
    assert len(budget_packet["open_questions"]) == 1
    assert "事項別明細書" in budget_packet["open_questions"][0]
    assert "市議案第8号" in budget_packet["claims"][0]["statement"]
    assert "206,946,719千円" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-272035-fiscal-2024-total-revenue"
    )
    # The claim records the non-certification itself and the
    # real balance at its published thousand-yen precision; it
    # must never present the settlement as certified.
    assert "市議案第74号" in revenue_packet["claims"][0]["statement"]
    assert "不認定" in revenue_packet["claims"][0]["statement"]
    assert "認定された" not in revenue_packet["claims"][0]["statement"]
    assert "令和7年11月28日" in revenue_packet["claims"][0]["statement"]
    assert "4,930,077千円" in revenue_packet["claims"][0]["statement"]
    # Two open residuals remain: the content of the mayor's
    # measures in response to the non-certification, and the
    # final cross-check against the settlement book (事項別明細書).
    assert len(revenue_packet["open_questions"]) == 2
    assert any(
        "不認定" in question for question in revenue_packet["open_questions"]
    )
    assert any(
        "事項別明細書" in question for question in revenue_packet["open_questions"]
    )

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-272035-fiscal-2024-total-expenditure"
    )
    assert len(expenditure_packet["open_questions"]) == 1
    assert "市議案第74号" in expenditure_packet["claims"][0]["statement"]
    assert "不認定" in expenditure_packet["claims"][0]["statement"]
    assert "認定された" not in expenditure_packet["claims"][0]["statement"]


def test_toyonaka_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 5,
        "basic_plan_measures": 16,
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
    # was passed as proposed under bill 市議案第8号.
    assert "千円精度のまま記録し、円単位を合成していない" in boundary
    assert "市議案第8号" in boundary
    assert "原案可決" in boundary
    # The FY2024 settlement was voted NOT certified under bill
    # 市議案第74号 on 2025-11-28, and the boundary must never
    # present it as certified.
    assert "市議案第74号" in boundary
    assert "不認定となった" in boundary
    assert "認定された" not in boundary
    assert "4,930,077千円" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_toyonaka_candidate_records_delegated_review():
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
    assert "市議案第8号" in note
    assert "市議案第74号" in note
    # The note records the non-certification and never presents
    # the settlement as certified.
    assert "不認定" in note
    assert "認定された" not in note
    assert candidate["publication"]["eligible"] is False


def test_toyonaka_and_previous_thirty_five_are_reviewed_complete_and_suita_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    toyonaka = by_code["272035"]
    assert toyonaka["status"] == "reviewed_complete"
    assert toyonaka["completion_path"] == "data/catalog/toyonaka_phase15_completion.json"
    assert (ROOT / toyonaka["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010", "192015", "202010", "202029",
        "212016", "232017", "232025", "232033", "232114", "242012",
        "252018",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 37
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 30
    assert queue["summary"]["next_official_code"] == "272078"
