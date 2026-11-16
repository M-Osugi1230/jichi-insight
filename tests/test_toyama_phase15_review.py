from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/toyama_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/toyama_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/toyama-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/toyama_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/toyama_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/toyama-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/toyama-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/toyama-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/toyama-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.toyama.lg.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_toyama_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "162019"
    assert completion["name_ja"] == "富山市"
    assert completion["completed_at"] == "2026-11-16"


def test_toyama_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_toyama_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-162019"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_toyama_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "162019"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "富山市"
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
        "toyama-current-plan-period": "accepted",
        "toyama-current-policy-structure": "accepted",
        "toyama-implementation-plan-framework": "accepted",
        "toyama-next-plan-transition": "accepted",
        "toyama-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The third comprehensive plan is still being drafted, so its
    # record stays a transition record and is never promoted into
    # the current plan's structure.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "toyama-next-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_toyama_plan_period_and_structure_are_reviewed():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["title"] == "第2次富山市総合計画"
    assert plan["start_fiscal_year"] == 2017
    assert plan["end_fiscal_year"] == 2026
    assert plan["vision"] == "人・まち・自然が調和する活力都市とやま"
    assert structure["counts"] == {"basic_goals": 4, "basic_plan_measures": 14}
    assert structure["review_status"] == "reviewed"

    # The plan keeps its published three layers (basic concept,
    # basic plan, implementation plan). The basic goals are the
    # four town-development goals of the latter basic plan and the
    # measures under them are its 14 policies, exactly as
    # published; the 51 individual measures beneath the policies
    # are not enumerated in v1.
    layers = {component["layer"] for component in plan["components"]}
    assert layers == {
        "basic_concept",
        "basic_plan",
        "implementation_plan",
    }
    assert plan["basic_goals"]["count"] == 4
    assert plan["basic_goals"]["names"] == [
        "すべての人が輝き安心して暮らせるまち【人材・暮らし】",
        "安心・安全で持続性のある魅力的なまち【都市・環境】",
        "人が集い活気にあふれ希望に満ちたまち【活力・交流】",
        "共生社会を実現し誇りを大切にする協働のまち【協働・連携】",
    ]
    assert plan["basic_goals"]["measures_count"] == 14
    assert plan["basic_goals"]["measures_per_goal"] == [3, 4, 4, 3]
    assert sum(plan["basic_goals"]["measures_per_goal"]) == 14

    plan_review = load(PLAN_REVIEW)
    period = next(
        record
        for record in plan_review["records"]
        if record["id"] == "toyama-current-plan-period"
    )
    assert period["value"] == "2022年度～2026年度"


def test_toyama_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "実施計画" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    assert "監査委員" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    # FY2024 falls inside the latter basic plan period, but its
    # totals are section-level aggregates with no mapping to
    # individual goals, policies, measures or projects.
    assert "款別" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_toyama_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-162019-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 199_776_107_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["toyama-budget-2026"]
    # Enacted as bill No. 1, passed as proposed on 2026-03-24; the
    # amount carried forward to the March supplementary budget is
    # not part of the initial budget total.
    assert "議案第1号" in budget["note"]
    assert "令和8年3月24日" in budget["note"]
    assert "含まれていない" in budget["note"]

    revenue = by_id["jp-local-162019-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-162019-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement is published only at thousand-yen precision,
    # so the yen figures are the thousand-yen values converted
    # as-is, not synthesized yen totals; their difference must
    # equal the published balance of 4,119,305 thousand yen.
    assert revenue["amount_yen"] == 189_996_111_000
    assert expenditure["amount_yen"] == 185_876_806_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 4_119_305_000
    assert "千円単位" in revenue["note"]
    assert "合成していない" in revenue["note"]
    assert "認定第1号" in revenue["note"]
    assert "認定第1号" in expenditure["note"]
    assert "令和7年11月28日" in revenue["note"]


def test_toyama_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-162019-fiscal-2026-total-expenditure"
    )
    # Final confirmation of the vote proceedings against the
    # plenary session minutes remains the explicit open residual,
    # carried over from the candidate.
    assert len(budget_packet["open_questions"]) == 1
    assert "本会議録" in budget_packet["open_questions"][0]
    assert "議案第1号" in budget_packet["claims"][0]["statement"]
    assert "可決" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-162019-fiscal-2024-total-revenue"
    )
    # The cross-check against the settlement detail book remains
    # an explicit open residual, carried over from the candidate.
    assert len(revenue_packet["open_questions"]) == 1
    assert "明細書" in revenue_packet["open_questions"][0]
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年11月28日" in revenue_packet["claims"][0]["statement"]

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-162019-fiscal-2024-total-expenditure"
    )
    assert expenditure_packet["open_questions"] == []


def test_toyama_completion_quality_gate_and_deferred_depth_are_explicit():
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
    assert "current-plan-full-text-confirmation" in deferred_ids
    assert "next-plan-transition-depth" in deferred_ids
    assert "settlement-audit-opinion-inspection" in deferred_ids
    assert "current-plan-annual-evaluation-evidence" in deferred_ids
    assert "fiscal-detail-and-amendment-linkage" in deferred_ids
    assert "policy-outcome-causal-and-cross-city-comparability" in deferred_ids
    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in completion["deferred_depth"]
    )

    boundary = completion["completion_boundary"]
    # The boundary must record the owner's delegation to Muse, not
    # an owner-conducted review.
    assert "委任" in boundary
    assert "所有者本人が一次資料を直接レビューしたものではない" in boundary
    assert "2026-11-15" in boundary
    assert "not_assessable" in boundary
    # The settlement precision boundary must stay explicit: the
    # published figures are thousand-yen values and no yen totals
    # were synthesized.
    assert "千円単位" in boundary
    assert "合成" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_toyama_candidate_records_delegated_review():
    candidate = load(CANDIDATE)

    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-16"
    note = candidate["human_review"]["reviewer_note"]
    assert note
    # The note records that the owner explicitly delegated the review
    # to Muse in chat on 2026-11-15, and that the owner did not
    # personally review the primary sources.
    assert "レビューはあなたがやってください" in note
    assert "委任" in note
    assert "所有者本人が一次資料を直接レビューしたものではない" in note
    assert candidate["publication"]["eligible"] is False


def test_toyama_and_previous_twenty_two_are_reviewed_complete_and_kanazawa_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    toyama = by_code["162019"]
    assert toyama["status"] == "reviewed_complete"
    assert (
        toyama["completion_path"]
        == "data/catalog/toyama_phase15_completion.json"
    )
    assert (ROOT / toyama["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 24
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 43
    assert queue["summary"]["next_official_code"] == "182010"
