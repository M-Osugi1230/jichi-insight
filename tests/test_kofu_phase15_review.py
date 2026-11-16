from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/kofu_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/kofu_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/kofu-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/kofu_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/kofu_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/kofu-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/kofu-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/kofu-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/kofu-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.kofu.yamanashi.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_kofu_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "192015"
    assert completion["name_ja"] == "甲府市"
    assert completion["completed_at"] == "2026-11-16"


def test_kofu_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_kofu_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-192015"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_kofu_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "192015"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "甲府市"
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
        "kofu-current-plan-period": "accepted",
        "kofu-current-policy-structure": "accepted",
        "kofu-progress-governance-framework": "accepted",
        "kofu-sixth-plan-transition": "accepted",
        "kofu-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The previous (sixth) plan is recorded only as a version
    # chronology, never merged into the seventh plan's framework.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "kofu-sixth-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_kofu_plan_period_and_structure_are_reviewed():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "第七次甲府市総合計画"
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2035
    assert plan["vision"] == "幸せ実感 希望ある未来を創り続けるまち 甲府"
    assert structure["counts"] == {"basic_goals": 3, "basic_plan_measures": 18}
    assert structure["review_status"] == "reviewed"

    # The plan is a two-layer plan (basic concept plus a rolling
    # implementation plan). Its goals are the three published basic
    # goals and the measures under them are the 18 published
    # measures, exactly as published in the city's official plan
    # framework chart; the sub-measures beneath the measures and
    # the implementation plan's projects are not enumerated in v1.
    layers = {component["layer"] for component in plan["components"]}
    assert layers == {"basic_concept", "implementation_plan"}
    assert plan["basic_goals"]["count"] == 3
    assert plan["basic_goals"]["names"] == [
        "未来に輝く『ひと』を育む",
        "安全・安心で快適な『まち』を創る",
        "都市機能と自然が調和する甲府の『魅力』を磨く",
    ]
    assert plan["basic_goals"]["measures_count"] == 18
    assert plan["basic_goals"]["measures_per_goal"] == [6, 6, 6]
    assert sum(plan["basic_goals"]["measures_per_goal"]) == 18
    assert plan["basic_goals"]["measures_by_goal"][0] == [
        "誰もが学び、成長できる機会の創出",
        "自分らしく暮らせる福祉の充実",
        "子育て・子育ちを支える環境づくり",
        "互いを尊重し共生できる社会の実現",
        "地域とのつながり・愛着の醸成",
        "健康に生活できる環境の整備",
    ]

    plan_review = load(PLAN_REVIEW)
    period = next(
        record
        for record in plan_review["records"]
        if record["id"] == "kofu-current-plan-period"
    )
    assert period["value"] == "2026年度～2035年度"
    # The basic concept was enacted by the council as bill
    # No. 109 on 2025-12-17.
    assert "議案第109号" in period["statement"]


def test_kofu_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "ローリング" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    # FY2026 is the plan's first year, so no annual results under
    # the implementation plan have been published yet.
    assert "初年度" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 belongs to the sixth plan's period and does not
    # overlap the seventh plan; its totals are section-level
    # aggregates with no mapping to individual measures or
    # projects.
    assert "款別" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_kofu_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-192015-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at sen-yen (thousand-yen)
    # precision in the city's official initial-budget materials,
    # so the amount is kept at that precision and never expanded
    # into synthetic yen.
    assert budget["amount_yen"] == 91_787_060_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["kofu-budget-2026"]
    # Enactment is bill No. 5 (議案第5号), passed on 2026-03-25
    # at the March 2026 regular council session.
    assert "議案第5号" in budget["note"]
    assert "令和8年3月25日" in budget["note"]

    revenue = by_id["jp-local-192015-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-192015-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in
    # the audit commissioners' settlement-review opinion
    # (甲監発第24号), so these are the exact published totals and
    # their difference must equal the published balance
    # (歳入歳出差引額) of 1,605,557,300 yen.
    assert revenue["amount_yen"] == 91_644_865_806
    assert expenditure["amount_yen"] == 90_039_308_506
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1_605_557_300
    assert "議案第95号" in revenue["note"]
    assert "議案第95号" in expenditure["note"]
    assert "令和7年10月2日" in revenue["note"]


def test_kofu_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-192015-fiscal-2026-total-expenditure"
    )
    # The final cross-check against the budget book's explanatory
    # materials (事項別明細書) remains an explicit open residual,
    # carried over from the candidate.
    assert len(budget_packet["open_questions"]) == 1
    assert "事項別明細書" in budget_packet["open_questions"][0]
    assert "議案第5号" in budget_packet["claims"][0]["statement"]
    assert "91,787,060千円" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-192015-fiscal-2024-total-revenue"
    )
    # The cross-check against the settlement detail book remains
    # an explicit open residual, carried over from the candidate.
    assert len(revenue_packet["open_questions"]) == 1
    assert "明細書" in revenue_packet["open_questions"][0]
    assert "議案第95号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年10月2日" in revenue_packet["claims"][0]["statement"]

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-192015-fiscal-2024-total-expenditure"
    )
    assert expenditure_packet["open_questions"] == []


def test_kofu_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert completion["quality_gate"]["current_plan_period_reviewed"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_goals": 3,
        "basic_plan_measures": 18,
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
    assert "議案第5号" in boundary
    assert "議案第95号" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_kofu_candidate_records_delegated_review():
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
    assert "議案第5号" in note
    assert candidate["publication"]["eligible"] is False


def test_kofu_and_previous_twenty_five_are_reviewed_complete_and_nagano_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    kofu = by_code["192015"]
    assert kofu["status"] == "reviewed_complete"
    assert (
        kofu["completion_path"]
        == "data/catalog/kofu_phase15_completion.json"
    )
    assert (ROOT / kofu["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 58
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 9
    assert queue["summary"]["next_official_code"] == "392014"
