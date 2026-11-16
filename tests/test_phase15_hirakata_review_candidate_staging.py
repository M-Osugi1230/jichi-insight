import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/hirakata-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/hirakata-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate() -> dict:
    return load_json(CANDIDATE_PATH)


def test_hirakata_candidate_is_prepared_with_delegated_review_approved() -> None:
    payload = candidate()
    assert payload["official_code"] == "272108"
    assert payload["name_ja"] == "枚方市"
    assert payload["status"] == "review_candidate"
    assert payload["package_state"] == "prepared"
    assert payload["human_review"]["required"] is True
    assert payload["human_review"]["status"] == "approved"
    assert payload["human_review"]["reviewed_at"] == "2026-11-16"
    assert payload["human_review"]["reviewer_note"]
    # The owner did not review the primary sources personally: on
    # 2026-11-15 the owner explicitly delegated the review to Muse in
    # chat, and the note must record that delegation rather than
    # claiming an owner review.
    assert "委任" in payload["human_review"]["reviewer_note"]
    assert "レビューはあなたがやってください" in payload["human_review"]["reviewer_note"]
    assert payload["publication"]["eligible"] is False
    assert payload["source_inventory_path"] == ("data/indexed/hirakata-city/source_inventory.json")


def test_hirakata_candidate_sources_match_phase14_inventory_exactly() -> None:
    payload = candidate()
    inventory = load_json(INVENTORY_PATH)
    inventory_sources = {source["id"]: source["official_url"] for source in inventory["sources"]}
    candidate_sources = {
        source["id"]: source["official_url"]
        for source in payload["candidate_package"]["source_catalog"]["sources"]
    }
    assert candidate_sources == inventory_sources
    assert candidate_sources == {
        "hirakata-fifth-plan": "https://www.city.hirakata.osaka.jp/0000007699.html",
        "hirakata-third-action-plan": "https://www.city.hirakata.osaka.jp/0000049873.html",
        "hirakata-action-plan-update": "https://www.city.hirakata.osaka.jp/0000051624.html",
        "hirakata-budget-2026": "https://www.city.hirakata.osaka.jp/0000053350.html",
        "hirakata-settlement-2024": "https://www.city.hirakata.osaka.jp/0000052610.html",
    }
    assert all(
        url.startswith("https://www.city.hirakata.osaka.jp/") for url in candidate_sources.values()
    )


def test_hirakata_candidate_keeps_plan_review_records_explicit() -> None:
    payload = candidate()
    records = {
        record["id"]: record for record in payload["candidate_package"]["plan_review"]["records"]
    }
    assert set(records) == {
        "hirakata-current-plan-period",
        "hirakata-current-policy-structure",
        "hirakata-progress-governance-framework",
        "hirakata-plan-transition",
        "hirakata-fy2024-settlement-linkage",
    }
    assert records["hirakata-current-plan-period"]["decision"] == "needs_review"
    assert records["hirakata-current-plan-period"]["value"] == (
        "基本構想は2016年度開始・計画期間を設定しない／基本計画は2016年度～2027年度"
        "／実行計画は4年間（現行は第3期・2024年度～2027年度）"
    )
    assert records["hirakata-current-policy-structure"]["title"] == (
        "基本計画の5つの基本目標・28の施策目標と4つの計画推進・全79施策"
    )
    assert records["hirakata-progress-governance-framework"]["title"] == (
        "実行計画の毎年度の検証・評価（PDCA）と予算編成に合わせた改訂による進行管理"
    )
    assert records["hirakata-plan-transition"]["title"] == (
        "第5次枚方市総合計画から次期総合計画（2028年度始期・策定中）への移行"
    )
    linkage = records["hirakata-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["title"] == "令和6年度決算と第5次枚方市総合計画の28の施策目標・79施策の接続"


def test_hirakata_candidate_policy_structure_lists_all_policies_and_measures() -> None:
    payload = candidate()
    plan = payload["candidate_package"]["policy_structure"]["current_plan"]
    assert plan["title"] == "第5次枚方市総合計画"
    assert plan["vision"] == "持続的に発展し、一人ひとりが輝くまち 枚方"
    assert plan["start_fiscal_year"] == 2016
    assert plan["end_fiscal_year"] is None
    assert plan["period_status"] == "verified_no_fixed_end"
    fields = plan["policy_fields"]
    assert len(fields) == 32
    assert len({field["id"] for field in fields}) == 32
    measures = [measure for field in fields for measure in field["measures"]]
    assert len(measures) == 79
    assert len(set(measures)) == 79
    by_id = {field["id"]: field for field in fields}
    assert by_id["field-1"]["name_ja"] == "基本目標1-施策目標1 災害に対する備えができているまち"
    assert by_id["field-1"]["measures"] == [
        "防災体制の強化",
        "防災意識の向上",
        "都市基盤の計画的な維持管理",
        "浸水被害の軽減",
    ]
    assert by_id["field-16"]["name_ja"] == (
        "基本目標3-施策目標16 子どもたちの生きる力を育む教育が充実したまち"
    )
    assert "子どもの健やかな身体の育成" in by_id["field-16"]["measures"]
    assert by_id["field-32"]["name_ja"] == (
        "計画推進-計画推進32 自治体間の広域連携や地方分権の推進を図ります"
    )
    assert by_id["field-32"]["measures"] == ["広域連携"]


def test_hirakata_candidate_fiscal_records_use_primary_source_values() -> None:
    payload = candidate()
    records = {record["id"]: record for record in payload["candidate_package"]["fiscal_records"]}
    assert set(records) == {
        "jp-local-272108-fiscal-2026-total-expenditure",
        "jp-local-272108-fiscal-2024-total-revenue",
        "jp-local-272108-fiscal-2024-total-expenditure",
    }
    budget = records["jp-local-272108-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["metric"] == "total_expenditure"
    assert budget["amount_yen"] == 176300000000
    assert budget["stage"] == "initial_budget"
    assert budget["value_status"] == "available"
    assert budget["review_status"] == "needs_review"
    assert budget["sources"] == ["hirakata-budget-2026"]
    assert "議案第84号" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "千円精度のまま記録する" in budget["note"]
    revenue = records["jp-local-272108-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 167040111596
    assert revenue["stage"] == "settlement"
    assert revenue["value_status"] == "available"
    assert revenue["review_status"] == "needs_review"
    assert revenue["sources"] == ["hirakata-settlement-2024"]
    assert "認定第1号" in revenue["note"]
    assert "令和7年10月17日）に認定された" in revenue["note"]
    assert "実質収支額は決算概要説明書の会計別収支表により1,938,746,472円" in revenue["note"]
    assert "差引額2,446,496,583円" in revenue["note"]
    assert "不認定" not in revenue["note"]
    expenditure = records["jp-local-272108-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 164593615013
    assert expenditure["stage"] == "settlement"
    assert expenditure["sources"] == ["hirakata-settlement-2024"]
    assert "差引額2,446,496,583円" in expenditure["note"]
    assert "認定第1号" in expenditure["note"]
    assert "不認定" not in expenditure["note"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2446496583


def test_hirakata_candidate_evidence_packets_point_at_primary_sources() -> None:
    payload = candidate()
    packets = {packet["id"]: packet for packet in payload["candidate_package"]["evidence_packets"]}
    assert set(packets) == {
        "evidence-hirakata-city-2026-total-expenditure",
        "evidence-hirakata-city-2024-total-revenue",
        "evidence-hirakata-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-hirakata-city-2026-total-expenditure"]["claims"][0]
    assert budget_claim["source_ids"] == ["hirakata-budget-2026"]
    assert "176,300,000千円" in budget_claim["statement"]
    assert "原案可決" in budget_claim["statement"]
    revenue_claim = packets["evidence-hirakata-city-2024-total-revenue"]["claims"][0]
    assert revenue_claim["source_ids"] == ["hirakata-settlement-2024"]
    assert "167,040,111,596円" in revenue_claim["statement"]
    assert "認定された" in revenue_claim["statement"]
    assert "不認定" not in revenue_claim["statement"]
    expenditure_claim = packets["evidence-hirakata-city-2024-total-expenditure"]["claims"][0]
    assert expenditure_claim["source_ids"] == ["hirakata-settlement-2024"]
    assert "164,593,615,013円" in expenditure_claim["statement"]
    assert "不認定" not in expenditure_claim["statement"]


def test_hirakata_candidate_progress_review_stays_staging() -> None:
    payload = candidate()
    progress = payload["candidate_package"]["progress_review"]
    assert progress["id"] == "hirakata-current-progress-review-summary"
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert framework["title"] == (
        "実行計画の毎年度の検証・評価（PDCA）と予算編成に合わせた改訂による進行管理"
    )


def test_hirakata_promotion_is_reflected_in_review_queue() -> None:
    queue = load_json(QUEUE_PATH)
    assert queue["summary"]["target_count"] == 67
    assert queue["summary"]["reviewed_complete_count"] == 43
    assert queue["summary"]["pending_record_review_count"] == 24
    assert queue["summary"]["next_official_code"] == "282022"
    items = {item["official_code"]: item for item in queue["execution_queue"]}
    assert items["272108"]["name_ja"] == "枚方市"
    assert items["272108"]["status"] == "reviewed_complete"
    assert items["272108"]["completion_path"] == (
        "data/catalog/hirakata_phase15_completion.json"
    )
