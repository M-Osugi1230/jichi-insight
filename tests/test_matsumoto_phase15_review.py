from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/matsumoto_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/matsumoto_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/matsumoto-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/matsumoto_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/matsumoto_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/matsumoto-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/matsumoto-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/matsumoto-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/matsumoto-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.matsumoto.nagano.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_matsumoto_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "202029"
    assert completion["name_ja"] == "松本市"
    assert completion["completed_at"] == "2026-11-16"


def test_matsumoto_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_matsumoto_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-202029"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_matsumoto_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "202029"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "松本市"
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
        "matsumoto-current-plan-period": "accepted",
        "matsumoto-current-policy-structure": "accepted",
        "matsumoto-progress-governance-framework": "accepted",
        "matsumoto-plan-transition": "accepted",
        "matsumoto-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The eleventh-to-twelfth basic plan transition is recorded
    # only as a version chronology, never merged into the
    # eleventh plan's framework.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "matsumoto-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_matsumoto_plan_period_and_structure_are_reviewed():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "松本市基本構想2030・第12次基本計画"
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2030
    assert plan["vision"] == "豊かさと幸せに 挑み続ける 三ガク都"
    assert structure["counts"] == {"basic_goals": 7, "basic_plan_measures": 47}
    assert structure["review_status"] == "reviewed"

    # The plan is a three-layer plan (basic concept, basic
    # plans, implementation plans). Its fields are the seven
    # published fields and the measures under them are the 47
    # published basic measures, exactly as published in the
    # twelfth basic plan's field volumes; all 47 measures are
    # enumerated in v1.
    layers = {component["layer"] for component in plan["components"]}
    assert layers == {"basic_concept", "basic_plan", "implementation_plan"}
    assert plan["basic_goals"]["count"] == 7
    assert plan["basic_goals"]["names"] == [
        "こども・若者・教育",
        "健康・医療・福祉",
        "住民自治・共生",
        "環境・エネルギー",
        "都市基盤・危機管理",
        "経済・産業",
        "文化・観光",
    ]
    assert plan["basic_goals"]["measures_count"] == 47
    assert plan["basic_goals"]["measures_per_goal"] == [7, 7, 7, 4, 12, 5, 5]
    assert sum(plan["basic_goals"]["measures_per_goal"]) == 47
    assert plan["basic_goals"]["measures_by_goal"][0] == [
        "結婚・出産・子育て支援の充実",
        "質の高い保育・幼児教育の実現",
        "個性と多様性を尊重する学校教育の推進",
        "子どもの権利保障と子ども福祉の推進",
        "若者が活躍できる環境づくり",
        "子ども・若者による居場所づくりの支援",
        "地域でともに学び合う生涯学習の実現",
    ]
    assert plan["basic_goals"]["measures_by_goal"][4][0] == "松本城を核としたまちづくり"
    assert len(plan["basic_goals"]["measures_by_goal"][4]) == 12

    plan_review = load(PLAN_REVIEW)
    period = next(
        record
        for record in plan_review["records"]
        if record["id"] == "matsumoto-current-plan-period"
    )
    assert period["value"] == "2026年度～2030年度"
    # The twelfth basic plan incorporates the third Matsumoto
    # regional-revitalization comprehensive strategy.
    assert "第3期松本版地方創生総合戦略" in period["statement"]


def test_matsumoto_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "成果指標" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    # The eleventh plan's progress evaluation exists, but its
    # indicator-level values are not promoted and have not been
    # reconciled against the settlement totals.
    assert "突合" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 belongs to the eleventh basic plan period (a
    # different plan version from the twelfth basic plan), and
    # its totals are section-level aggregates with no mapping
    # to individual measures or indicators.
    assert "款別" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_matsumoto_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-202029-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at sen-yen (thousand-yen)
    # precision in the city's official initial-budget overview,
    # so the amount is kept at that precision and never
    # expanded into synthetic yen.
    assert budget["amount_yen"] == 114_980_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["matsumoto-budget-2026"]
    # Enactment is bill No. 43 (議案第43号), voted on
    # 2026-03-16 at the February 2026 regular council session
    # and corroborated by the June 2026 supplementary-budget
    # overview's enacted base amount.
    assert "議案第43号" in budget["note"]
    assert "令和8年3月16日" in budget["note"]
    # The minutes-body wording 原案可決 was not directly
    # confirmed, so the note must keep that disclaimer.
    assert "直接確認できていない" in budget["note"]

    revenue = by_id["jp-local-202029-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-202029-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in
    # the appendix table of the audit commission's
    # settlement-review opinion (松監事第24号), so these are
    # the exact published totals and their difference must
    # equal the published balance (歳入歳出差引額) of
    # 2,924,821,106 yen.
    assert revenue["amount_yen"] == 116_331_387_915
    assert expenditure["amount_yen"] == 113_406_566_809
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2_924_821_106
    assert "議案第18号" in revenue["note"]
    assert "議案第18号" in expenditure["note"]
    assert "令和7年11月4日" in revenue["note"]


def test_matsumoto_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-202029-fiscal-2026-total-expenditure"
    )
    # The final cross-check against the budget explanatory
    # materials (事項別明細書) remains an explicit open residual,
    # carried over from the candidate.
    assert len(budget_packet["open_questions"]) == 1
    assert "事項別明細書" in budget_packet["open_questions"][0]
    assert "議案第43号" in budget_packet["claims"][0]["statement"]
    assert "114,980,000千円" in budget_packet["claims"][0]["statement"]
    # The claim records enactment without asserting the
    # unconfirmed 原案可決 wording.
    assert "成立" in budget_packet["claims"][0]["statement"]
    assert "原案可決" not in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-202029-fiscal-2024-total-revenue"
    )
    # The cross-check against the settlement detail book remains
    # an explicit open residual, carried over from the candidate.
    assert len(revenue_packet["open_questions"]) == 1
    assert "明細書" in revenue_packet["open_questions"][0]
    assert "議案第18号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年11月4日" in revenue_packet["claims"][0]["statement"]

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-202029-fiscal-2024-total-expenditure"
    )
    assert expenditure_packet["open_questions"] == []


def test_matsumoto_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert completion["quality_gate"]["current_plan_period_reviewed"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 7,
        "basic_plan_measures": 47,
        "promoted_implementation_item_actual_records": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-plan-granular-kpi-and-project-linkage" in deferred_ids
    assert "fiscal-detail-and-amendment-linkage" in deferred_ids
    assert "plan-transition-version-depth" in deferred_ids
    assert "current-plan-annual-evaluation-evidence" in deferred_ids
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
    assert "議案第43号" in boundary
    assert "議案第18号" in boundary
    # The unconfirmed 原案可決 wording is explicitly not asserted.
    assert "直接確認できていない" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_matsumoto_candidate_records_delegated_review():
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
    assert "議案第43号" in note
    assert candidate["publication"]["eligible"] is False


def test_matsumoto_and_previous_twenty_seven_are_reviewed_complete_and_gifu_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    matsumoto = by_code["202029"]
    assert matsumoto["status"] == "reviewed_complete"
    assert (
        matsumoto["completion_path"]
        == "data/catalog/matsumoto_phase15_completion.json"
    )
    assert (ROOT / matsumoto["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010", "192015", "202010",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 62
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 5
    assert queue["summary"]["next_official_code"] == "422029"
