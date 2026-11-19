import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/naha-city"
CATALOG = ROOT / "data/catalog"
CANDIDATE = ROOT / "data/candidates/naha-city/review_candidate.json"
QUEUE = CATALOG / "phase15_core_capital_review_queue.json"
COMPLETION = CATALOG / "naha_phase15_completion.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fiscal_record(record_id: str) -> dict:
    records = load(REVIEWED / "fiscal_records.json")
    return next(record for record in records if record["id"] == record_id)


def plan_record(record_id: str) -> dict:
    review = load(REVIEWED / "plan_review.json")
    return next(record for record in review["records"] if record["id"] == record_id)


def test_naha_completion_is_the_sixty_seventh_reviewed_package():
    completion = load(COMPLETION)
    queue = load(QUEUE)

    assert completion["official_code"] == "472018"
    assert completion["status"] == "reviewed_complete"
    assert completion["completion_depth"] == "declared_review_package_v1"
    assert queue["summary"]["reviewed_complete_count"] == 69
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None

    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "472018"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/naha_phase15_completion.json"


def test_naha_reviewed_municipality_and_sources():
    municipality = load(REVIEWED / "municipality.json")
    catalog = load(CATALOG / "naha_phase15_sources.json")

    assert municipality["official_code"] == "472018"
    assert municipality["municipality_type"] == "city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["official_url"] == "https://www.city.naha.okinawa.jp/"
    assert municipality["sources"] == [
        "naha-city-home",
        "naha-budget-2026",
        "naha-settlement-2024",
    ]
    assert {source["id"] for source in catalog["sources"]} == {
        "naha-fifth-plan",
        "naha-implementation-2026-2028",
        "naha-sixth-plan-transition",
        "naha-budget-2026",
        "naha-settlement-2024",
    }
    roles = {source["id"]: source["evidence_role"] for source in catalog["sources"]}
    assert roles["naha-fifth-plan"] == "comprehensive_plan"
    assert roles["naha-implementation-2026-2028"] == "implementation_plan"
    assert roles["naha-sixth-plan-transition"] == "plan_transition"
    assert roles["naha-budget-2026"] == "budget"
    assert roles["naha-settlement-2024"] == "settlement"
    assert all(
        source["official_url"].startswith("https://www.city.naha.okinawa.jp/")
        for source in catalog["sources"]
    )


def test_naha_reviewed_fiscal_records_keep_published_precision():
    budget = fiscal_record("jp-local-472018-fiscal-2026-total-expenditure")
    revenue = fiscal_record("jp-local-472018-fiscal-2024-total-revenue")
    expenditure = fiscal_record("jp-local-472018-fiscal-2024-total-expenditure")

    assert budget["amount_yen"] == 185_220_000_000
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["review_status"] == "reviewed"
    budget_text = json.dumps(budget, ensure_ascii=False)
    assert "議案第22号" in budget_text
    assert "原案可決（賛成多数）" in budget_text
    assert "2026年3月17日" in budget_text
    assert "185,220,000千円" in budget_text
    assert "千円単位" in budget_text
    assert "組み替え動議" in budget_text
    assert "修正可決" not in budget_text
    assert "修正議決" not in budget_text

    assert revenue["amount_yen"] == 185_140_399_109
    assert expenditure["amount_yen"] == 178_147_629_486
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 6_992_769_623
    settlement_text = json.dumps(revenue, ensure_ascii=False) + json.dumps(
        expenditure, ensure_ascii=False
    )
    assert "認定第1号" in settlement_text
    assert "2025年10月8日" in settlement_text
    assert "認定された" in settlement_text
    assert "5,963,603,975円" in settlement_text
    assert "普通会計ベース" in settlement_text
    assert "不認定" not in settlement_text


def test_naha_evidence_packets_are_reviewed():
    packets = load(REVIEWED / "evidence_packets.json")

    assert len(packets) == 3
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(
        claim["decision"] == "accepted"
        for packet in packets
        for claim in packet["claims"]
    )
    text = json.dumps(packets, ensure_ascii=False)
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text


def test_naha_plan_review_keeps_fifth_plan_and_transition_separate():
    period = plan_record("naha-current-plan-period")
    structure = plan_record("naha-current-policy-structure")
    governance = plan_record("naha-progress-governance-framework")
    transition = plan_record("naha-plan-transition")
    linkage = plan_record("naha-fy2024-settlement-linkage")

    for record in (period, structure, governance, transition):
        assert record["decision"] == "accepted"
    assert "第5次那覇市総合計画" in period["statement"]
    assert "transition_or_unresolved" in period["statement"]
    assert "笑顔広がる元気なまちNAHA" in structure["statement"]
    assert "令和8年度実施計画" in governance["statement"]
    assert "第6次那覇市総合計画" in transition["statement"]
    assert "策定が開始" in transition["statement"]

    assert linkage["decision"] == "not_assessable"
    assert "第5次那覇市総合計画" in linkage["statement"]
    assert "not_assessable" in linkage["statement"]
    assert "認定第1号" in linkage["statement"]
    assert "認定されている" in linkage["statement"]


def test_naha_policy_structure_counts_only_the_five_city_images():
    structure = load(CATALOG / "naha_current_policy_structure.json")

    assert structure["official_code"] == "472018"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "naha-fifth-plan"
    plan = structure["current_plan"]
    assert plan["title"].startswith("第5次那覇市総合計画")
    assert plan["start_fiscal_year"] == 2018
    assert plan["end_fiscal_year"] == 2027
    assert plan["period_status"] == "transition_or_unresolved"
    assert plan["vision"] == (
        "なはで暮らし、働き、育てよう！笑顔広がる元気なまちNAHA "
        "みんなでつなごう市民力"
    )
    assert [field["name_ja"] for field in plan["policy_fields"]] == [
        "多様なつながりで共に助け合い、認め合う安全安心に暮らせるまちNAHA",
        "互いの幸せを地域と福祉で支え合い誰もが輝くまちNAHA",
        "次世代の未来を拓き、豊かな学びと文化が薫る誇りあるまちNAHA",
        "ヒト・モノ・コトが集い、育ち、ひろがる万国津梁のまちNAHA",
        "自然環境と都市機能が調和した住みつづけたいまちNAHA",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    assert structure["counts"] == {"basic_goals": 5, "basic_plan_measures": 0}
    principles = " ".join(plan["management_principles"])
    assert "第6次" in principles
    assert "流用しない" in principles
    assert "令和8年度実施計画" in principles


def test_naha_progress_review_keeps_rolling_plan_and_linkage_honest():
    progress = load(CATALOG / "naha_current_progress_review_summary.json")

    assert progress["official_code"] == "472018"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    current = progress["current_implementation_plan"]
    assert "実施計画（3年ローリング）" in current["title"]
    assert "2026年度〜2028年度" in current["period"]
    assert "ローリング" in current["rolling_structure"]
    assert progress["fiscal_linkage"]["status"] == "not_assessable"
    assert "認定第1号" in progress["fiscal_linkage"]["boundary"]
    assert "not_assessable" in progress["fiscal_linkage"]["boundary"]


def test_naha_finance_source_records_exist():
    finance = load(CATALOG / "naha_city_finance_sources.json")

    assert {record["id"] for record in finance["records"]} == {
        "naha-city-home",
        "naha-budget-2026",
        "naha-settlement-2024",
        "naha-city-mic-settlement-card-fy2022",
        "naha-city-mic-settlement-card-fy2023",
        "naha-city-mic-settlement-card-fy2024",
        "naha-city-fiscal-situation-collection-fy2022",
        "naha-city-fiscal-situation-collection-fy2023",
        "naha-city-fiscal-situation-collection-fy2024",
    }
    assert all(
        record["url"].startswith(
            ("https://www.city.naha.okinawa.jp/", "https://www.soumu.go.jp/", "https://www.pref.okinawa.jp/")
        )
        for record in finance["records"]
    )


def test_naha_completion_gates_and_deferred_depth():
    completion = load(COMPLETION)
    candidate = load(CANDIDATE)

    gates = completion["quality_gate"]
    assert set(gates) == {
        "budget_enactment_state_preserved",
        "current_plan_period_reviewed",
        "current_plan_policy_structure_reviewed",
        "declared_package_schema_validated",
        "fiscal_states_and_years_separate",
        "implementation_plan_layer_reviewed",
        "individual_implementation_items_not_overpromoted",
        "no_causal_attribution_promoted",
        "no_cross_city_comparability_promoted",
        "no_independent_policy_achievement_promoted",
        "official_source_lineage_preserved",
        "regression_suite_required_before_merge",
        "settlement_linkage_not_assessable_preserved",
    }
    assert all(gates.values())

    assert {item["id"] for item in completion["deferred_depth"]} == {
        item["id"] for item in candidate["deferred_depth"]
    }
    assert all(
        item["status"] == "deferred_not_required_for_v1_completion"
        for item in completion["deferred_depth"]
    )
    assert {
        item["id"]: item["boundary"] for item in completion["deferred_depth"]
    } == {item["id"]: item["boundary"] for item in candidate["deferred_depth"]}
    boundary = completion["completion_boundary"]
    assert "議案第22号" in boundary
    assert "認定第1号" in boundary
    assert "transition_or_unresolved" in boundary
    assert "不認定" not in boundary
    assert "修正可決" not in boundary


def test_naha_review_records_the_delegation_not_owner_review():
    candidate = load(CANDIDATE)
    completion = load(COMPLETION)

    assert candidate["human_review"]["status"] == "approved"
    note = candidate["human_review"]["reviewer_note"]
    assert "委任" in note
    assert "レビューはあなたがやってください" in note
    assert "所有者本人が一次資料を直接レビューしたものではない" in note
    assert "議案第22号" in note
    assert "認定第1号" in note

    serialized = json.dumps(completion, ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "不認定" not in serialized
    assert "修正可決" not in serialized
