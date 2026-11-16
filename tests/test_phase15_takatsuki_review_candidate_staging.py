import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/takatsuki-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/takatsuki-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate() -> dict:
    return load_json(CANDIDATE_PATH)


def test_takatsuki_candidate_is_prepared_with_delegated_review_approved() -> None:
    payload = candidate()
    assert payload["official_code"] == "272078"
    assert payload["name_ja"] == "高槻市"
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
    assert payload["source_inventory_path"] == ("data/indexed/takatsuki-city/source_inventory.json")


def test_takatsuki_candidate_sources_match_phase14_inventory_exactly() -> None:
    payload = candidate()
    inventory = load_json(INVENTORY_PATH)
    inventory_sources = {source["id"]: source["official_url"] for source in inventory["sources"]}
    candidate_sources = {
        source["id"]: source["official_url"]
        for source in payload["candidate_package"]["source_catalog"]["sources"]
    }
    assert candidate_sources == inventory_sources
    assert candidate_sources == {
        "takatsuki-sixth-plan": "https://www.city.takatsuki.osaka.jp/site/keikaku/1228.html",
        "takatsuki-implementation-2026-2028": (
            "https://www.city.takatsuki.osaka.jp/site/keikaku/1229.html"
        ),
        "takatsuki-budget-2026": "https://www.city.takatsuki.osaka.jp/soshiki/7/67908.html",
        "takatsuki-settlement-2024": "https://www.city.takatsuki.osaka.jp/soshiki/7/67945.html",
    }
    assert all(
        url.startswith("https://www.city.takatsuki.osaka.jp/") for url in candidate_sources.values()
    )


def test_takatsuki_candidate_keeps_plan_review_records_explicit() -> None:
    payload = candidate()
    records = {
        record["id"]: record for record in payload["candidate_package"]["plan_review"]["records"]
    }
    assert set(records) == {
        "takatsuki-current-plan-period",
        "takatsuki-current-policy-structure",
        "takatsuki-progress-governance-framework",
        "takatsuki-plan-transition",
        "takatsuki-fy2024-settlement-linkage",
    }
    assert records["takatsuki-current-plan-period"]["decision"] == "needs_review"
    assert records["takatsuki-current-plan-period"]["value"] == "2021年度～2030年度"
    assert records["takatsuki-current-policy-structure"]["title"] == (
        "基本計画の8分野・全29施策・全139施策の方向"
    )
    assert records["takatsuki-progress-governance-framework"]["title"] == (
        "実施計画（3年ローリング）における主要事業の実績の振り返り（評価）による進行管理"
    )
    assert records["takatsuki-plan-transition"]["title"] == (
        "第5次高槻市総合計画（高槻市総合戦略プラン）から第6次高槻市総合計画への移行"
    )
    linkage = records["takatsuki-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["title"] == "令和6年度決算と第6次高槻市総合計画の8分野・29施策の接続"


def test_takatsuki_candidate_policy_structure_lists_all_policies_and_measures() -> None:
    payload = candidate()
    plan = payload["candidate_package"]["policy_structure"]["current_plan"]
    assert plan["title"] == "第6次高槻市総合計画"
    assert plan["vision"] == "輝く未来を創造する 関西の中央都市 高槻"
    assert plan["start_fiscal_year"] == 2021
    assert plan["end_fiscal_year"] == 2030
    fields = plan["policy_fields"]
    assert len(fields) == 29
    assert len({field["id"] for field in fields}) == 29
    measures = [measure for field in fields for measure in field["measures"]]
    assert len(measures) == 139
    assert len(set(measures)) == 139
    by_id = {field["id"]: field for field in fields}
    assert by_id["field-1"]["name_ja"] == "分野1-施策1-1 安全で快適な都市空間・住環境の創造"
    assert by_id["field-1"]["measures"] == [
        "「コンパクトシティ・プラス・ネットワーク」の推進",
        "富田地区における公共施設の再構築",
        "新名神高速道路関連道路における沿道まちづくりの取組の推進",
        "新駅設置と新たな市街地形成の検討",
        "風格と魅力あるまちなみや景観の形成",
        "住宅・建築物の耐震化の推進",
        "ブロック塀等の撤去",
        "住宅・住環境の向上",
    ]
    assert by_id["field-16"]["name_ja"] == "分野4-施策4-4 障がい者福祉の充実"
    assert "障がい者の地域移行の推進、地域生活の支援" in by_id["field-16"]["measures"]
    assert by_id["field-29"]["name_ja"] == "分野8-施策8-2 アセットマネジメントの推進"
    assert by_id["field-29"]["measures"] == [
        "施設管理における質の適正化と施設総量の適正化",
        "公有資産の戦略的な利活用の推進",
    ]


def test_takatsuki_candidate_fiscal_records_use_primary_source_values() -> None:
    payload = candidate()
    records = {record["id"]: record for record in payload["candidate_package"]["fiscal_records"]}
    assert set(records) == {
        "jp-local-272078-fiscal-2026-total-expenditure",
        "jp-local-272078-fiscal-2024-total-revenue",
        "jp-local-272078-fiscal-2024-total-expenditure",
    }
    budget = records["jp-local-272078-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["metric"] == "total_expenditure"
    assert budget["amount_yen"] == 151189961000
    assert budget["stage"] == "initial_budget"
    assert budget["value_status"] == "available"
    assert budget["review_status"] == "needs_review"
    assert budget["sources"] == ["takatsuki-budget-2026"]
    assert "議案第32号" in budget["note"]
    assert "令和8年2月25日に高槻市長濱田剛史から提出" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "千円精度のまま記録する" in budget["note"]
    revenue = records["jp-local-272078-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 147928131915
    assert revenue["stage"] == "settlement"
    assert revenue["value_status"] == "available"
    assert revenue["review_status"] == "needs_review"
    assert revenue["sources"] == ["takatsuki-settlement-2024"]
    assert "認定第1号" in revenue["note"]
    assert "令和7年12月3日に認定された" in revenue["note"]
    assert "実質収支額は実質収支に関する調書により3,523,157千円" in revenue["note"]
    assert "差引額5,122,447,000円" in revenue["note"]
    assert "不認定" not in revenue["note"]
    expenditure = records["jp-local-272078-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 142805684915
    assert expenditure["stage"] == "settlement"
    assert expenditure["sources"] == ["takatsuki-settlement-2024"]
    assert "差引額5,122,447,000円" in expenditure["note"]
    assert "認定第1号" in expenditure["note"]
    assert "不認定" not in expenditure["note"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 5122447000


def test_takatsuki_candidate_evidence_packets_point_at_primary_sources() -> None:
    payload = candidate()
    packets = {packet["id"]: packet for packet in payload["candidate_package"]["evidence_packets"]}
    assert set(packets) == {
        "evidence-takatsuki-city-2026-total-expenditure",
        "evidence-takatsuki-city-2024-total-revenue",
        "evidence-takatsuki-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-takatsuki-city-2026-total-expenditure"]["claims"][0]
    assert budget_claim["source_ids"] == ["takatsuki-budget-2026"]
    assert "151,189,961千円" in budget_claim["statement"]
    assert "原案可決" in budget_claim["statement"]
    revenue_claim = packets["evidence-takatsuki-city-2024-total-revenue"]["claims"][0]
    assert revenue_claim["source_ids"] == ["takatsuki-settlement-2024"]
    assert "147,928,131,915円" in revenue_claim["statement"]
    assert "認定された" in revenue_claim["statement"]
    assert "不認定" not in revenue_claim["statement"]
    expenditure_claim = packets["evidence-takatsuki-city-2024-total-expenditure"]["claims"][0]
    assert expenditure_claim["source_ids"] == ["takatsuki-settlement-2024"]
    assert "142,805,684,915円" in expenditure_claim["statement"]


def test_takatsuki_candidate_progress_review_stays_staging() -> None:
    payload = candidate()
    progress = payload["candidate_package"]["progress_review"]
    assert progress["id"] == "takatsuki-current-progress-review-summary"
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert framework["title"] == (
        "実施計画（3年ローリング）による進行管理（主要事業の実績の振り返り（評価））"
    )


def test_takatsuki_promotion_is_reflected_in_review_queue() -> None:
    queue = load_json(QUEUE_PATH)
    assert queue["summary"]["target_count"] == 67
    assert queue["summary"]["reviewed_complete_count"] == 59
    assert queue["summary"]["pending_record_review_count"] == 8
    assert queue["summary"]["next_official_code"] == "402036"
    items = {item["official_code"]: item for item in queue["execution_queue"]}
    assert items["272078"]["name_ja"] == "高槻市"
    assert items["272078"]["status"] == "reviewed_complete"
    assert items["272078"]["completion_path"] == (
        "data/catalog/takatsuki_phase15_completion.json"
    )
