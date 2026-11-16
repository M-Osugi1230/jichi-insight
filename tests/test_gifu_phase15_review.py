from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/gifu_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/gifu_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/gifu-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/gifu_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/gifu_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/gifu-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/gifu-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/gifu-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/gifu-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"

OFFICIAL_PREFIX = "https://www.city.gifu.lg.jp/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_gifu_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "212016"
    assert completion["name_ja"] == "岐阜市"
    assert completion["completed_at"] == "2026-11-16"


def test_gifu_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_gifu_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-212016"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-16"


def test_gifu_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "212016"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "岐阜市"
    assert len(source_catalog["sources"]) == 4
    assert len(plan_review["records"]) == 6
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
        "gifu-current-framework-period": "accepted",
        "gifu-current-policy-structure": "accepted",
        "gifu-future-creation-strategy": "accepted",
        "gifu-progress-governance-framework": "accepted",
        "gifu-plan-revision-transition": "accepted",
        "gifu-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith(OFFICIAL_PREFIX)
        for record in plan_review["records"]
    )

    # The concept revision in preparation is recorded only as a
    # transition chronology, never as the revised framework itself.
    transition = next(
        record
        for record in plan_review["records"]
        if record["id"] == "gifu-plan-revision-transition"
    )
    assert transition["evidence_role"] == "plan_transition"


def test_gifu_framework_has_no_invented_plan_period():
    structure = load(STRUCTURE)
    framework = structure["current_framework"]

    assert framework["title"] == "岐阜市未来のまちづくり構想"
    assert framework["vision"] == "人がつながる 創造が生まれる しなやかさのあるまち"
    # Gifu's top framework is a vision-type concept, not a
    # fixed-period comprehensive plan: it starts in FY2022, has no
    # fixed end year, and is reviewed every five years. The horizon
    # of around 2040 is a target horizon and must never be recorded
    # as a fixed plan end.
    assert framework["period_status"] == "no_fixed_end"
    assert framework["start_fiscal_year"] == 2022
    assert framework["end_fiscal_year"] is None
    assert structure["counts"] == {
        "basic_approaches": 4,
        "policy_fields": 5,
        "strategy_pillars": 3,
    }
    assert structure["review_status"] == "reviewed"

    assert framework["basic_approaches"] == [
        "オール岐阜のまちづくり",
        "シビックプライドの醸成",
        "DXと脱炭素化",
        "持続可能で選ばれるまち",
    ]
    fields = framework["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "教育・子育て",
        "健康・福祉・医療",
        "市民協働・防災・環境",
        "産業・労働・交流",
        "都市基盤整備・交通・中心市街地活性化",
    ]
    # Each field carries three citizen-survey-based indicators.
    assert all(len(field["indicators"]) == 3 for field in fields)

    strategy = framework["strategy_layer"]
    assert strategy["title"] == "岐阜市未来創生総合戦略"
    assert strategy["start_fiscal_year"] == 2024
    assert strategy["end_fiscal_year"] == 2027
    assert strategy["pillars"] == ["ひとの創生", "しごとの創生", "まちの創生"]

    plan_review = load(PLAN_REVIEW)
    identity = next(
        record
        for record in plan_review["records"]
        if record["id"] == "gifu-current-framework-period"
    )
    assert identity["value"] == "2022年度開始・固定終期なし（2040年頃を見据える）"


def test_gifu_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "懇談会" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    assert "懇談会" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "款別" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_gifu_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-212016-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    # The budget total is published at sen-yen (thousand-yen)
    # precision in the city's official initial-budget booklet, so
    # the amount is kept at that precision and never expanded into
    # synthetic yen.
    assert budget["amount_yen"] == 200_680_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == ["gifu-budget-2026"]
    # Enacted as bill No. 1 (第1号議案), passed as proposed on
    # 2026-03-27 at the first (March) 2026 regular session.
    assert "第1号議案" in budget["note"]
    assert "令和8年3月27日" in budget["note"]
    assert "原案のとおり可決" in budget["note"]

    revenue = by_id["jp-local-212016-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-212016-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # The settlement totals are published at yen precision in the
    # official settlement-by-account table, so these are the exact
    # published totals and their difference must equal the
    # published balance (歳入歳出差引額) of 6,686,174,381 yen.
    assert revenue["amount_yen"] == 198_779_091_770
    assert expenditure["amount_yen"] == 192_092_917_389
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 6_686_174_381
    assert "第107号議案" in revenue["note"]
    assert "第107号議案" in expenditure["note"]
    assert "令和7年9月25日" in revenue["note"]


def test_gifu_evidence_packets_validate_and_match_fiscal_records():
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
        if packet["subject_id"] == "jp-local-212016-fiscal-2026-total-expenditure"
    )
    # Enactment (bill No. 1, passed as proposed) and the agreement
    # with the budget explanatory book are already confirmed, so
    # no open question remains on the budget packet; the
    # supplementary-budget history is deferred depth.
    assert budget_packet["open_questions"] == []
    assert "第1号議案" in budget_packet["claims"][0]["statement"]
    assert "200,680,000千円" in budget_packet["claims"][0]["statement"]
    assert "原案のとおり可決" in budget_packet["claims"][0]["statement"]

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-212016-fiscal-2024-total-revenue"
    )
    # The final cross-check against the settlement detail book
    # (事項別明細書) remains an explicit open residual, carried
    # over from the candidate.
    assert len(revenue_packet["open_questions"]) == 1
    assert "事項別明細書" in revenue_packet["open_questions"][0]
    assert "第107号議案" in revenue_packet["claims"][0]["statement"]
    assert "令和7年9月25日" in revenue_packet["claims"][0]["statement"]

    expenditure_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-212016-fiscal-2024-total-expenditure"
    )
    assert expenditure_packet["open_questions"] == []


def test_gifu_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert completion["quality_gate"]["no_fixed_plan_period_preserved"] is True
    assert (
        completion["quality_gate"]["settlement_linkage_not_assessable_preserved"]
        is True
    )
    assert completion["review_package"]["counts"] == {
        "basic_approaches": 4,
        "policy_fields": 5,
        "strategy_pillars": 3,
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
    assert "第1号議案" in boundary
    assert "第107号議案" in boundary
    # The 2040 horizon is a target horizon, never a fixed end.
    assert "固定終期として記録しない" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_gifu_candidate_records_delegated_review():
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
    assert "第1号議案" in note
    assert candidate["publication"]["eligible"] is False


def test_gifu_and_previous_twenty_eight_are_reviewed_complete_and_toyohashi_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    gifu = by_code["212016"]
    assert gifu["status"] == "reviewed_complete"
    assert gifu["completion_path"] == "data/catalog/gifu_phase15_completion.json"
    assert (ROOT / gifu["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036", "072044",
        "082015", "092010", "102016", "102024", "112011", "112038",
        "112224", "122041", "122173", "131040", "132012", "142018",
        "162019", "172014", "182010", "192015", "202010", "202029",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 44
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 23
    assert queue["summary"]["next_official_code"] == "282030"
