import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/suita-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/suita-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate() -> dict:
    return load_json(CANDIDATE_PATH)


def test_suita_candidate_is_prepared_with_delegated_review_approved() -> None:
    payload = candidate()
    assert payload["official_code"] == "272051"
    assert payload["name_ja"] == "吹田市"
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
    assert payload["source_inventory_path"] == ("data/indexed/suita-city/source_inventory.json")


def test_suita_candidate_sources_match_phase14_inventory_exactly() -> None:
    payload = candidate()
    inventory = load_json(INVENTORY_PATH)
    inventory_sources = {source["id"]: source["official_url"] for source in inventory["sources"]}
    candidate_sources = {
        source["id"]: source["official_url"]
        for source in payload["candidate_package"]["source_catalog"]["sources"]
    }
    assert candidate_sources == inventory_sources
    assert candidate_sources == {
        "suita-fourth-plan": (
            "https://www.city.suita.osaka.jp/shisei/1018811/1018812/1018813/index.html"
        ),
        "suita-implementation-2026-2030": (
            "https://www.city.suita.osaka.jp/shisei/1018811/1018821/1018822/1041855.html"
        ),
        "suita-progress": (
            "https://www.city.suita.osaka.jp/shisei/1018811/1018812/1018813/1008520.html"
        ),
        "suita-budget-2026": (
            "https://www.city.suita.osaka.jp/shisei/1018870/1018873/1018875/1041852.html"
        ),
        "suita-settlement-2024": (
            "https://www.city.suita.osaka.jp/shisei/1018870/1018876/1040442.html"
        ),
    }
    assert all(
        url.startswith("https://www.city.suita.osaka.jp/") for url in candidate_sources.values()
    )


def test_suita_candidate_keeps_plan_review_records_explicit() -> None:
    payload = candidate()
    records = {
        record["id"]: record for record in payload["candidate_package"]["plan_review"]["records"]
    }
    assert set(records) == {
        "suita-current-plan-period",
        "suita-current-policy-structure",
        "suita-progress-governance-framework",
        "suita-plan-transition",
        "suita-fy2024-settlement-linkage",
    }
    assert records["suita-current-plan-period"]["decision"] == "needs_review"
    assert records["suita-current-plan-period"]["value"] == "2019年度～2028年度"
    assert records["suita-current-policy-structure"]["title"] == (
        "基本計画改訂版の8大綱・全19政策・全52施策"
    )
    assert records["suita-progress-governance-framework"]["title"] == (
        "PDCAサイクル（行政評価）による進行管理と進捗状況の公表"
    )
    assert records["suita-plan-transition"]["title"] == (
        "基本計画から基本計画改訂版への移行（中間見直し）"
    )
    linkage = records["suita-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["title"] == "令和6年度決算と基本計画改訂版の19政策・52施策の接続"


def test_suita_candidate_policy_structure_lists_all_policies_and_measures() -> None:
    payload = candidate()
    plan = payload["candidate_package"]["policy_structure"]["current_plan"]
    assert plan["title"] == "第4次吹田市総合計画 基本計画改訂版"
    assert plan["vision"] == "だれもが安心してすこやかで快適に暮らし続けられるまち"
    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2028
    fields = plan["policy_fields"]
    assert len(fields) == 19
    assert len({field["id"] for field in fields}) == 19
    measures = [measure for field in fields for measure in field["measures"]]
    assert len(measures) == 52
    assert len(set(measures)) == 52
    by_id = {field["id"]: field for field in fields}
    assert by_id["field-1"]["name_ja"] == "大綱1-政策1 平和と人権を尊重するまちづくり"
    assert by_id["field-1"]["measures"] == [
        "非核平和への貢献",
        "人権の保障",
        "男女共同参画の推進",
    ]
    assert by_id["field-8"]["name_ja"] == "大綱3-政策4 健康・医療のまちづくり"
    assert "健都を生かした健康づくりと医療イノベーションの促進" in (by_id["field-8"]["measures"])
    assert by_id["field-19"]["name_ja"] == "大綱8-政策1 行政資源の効果的活用"
    assert by_id["field-19"]["measures"] == [
        "効果的・効率的な行財政運営の推進",
        "公共施設の最適化",
        "働きやすい職場づくり・人材育成の推進",
        "ICTの利活用",
    ]


def test_suita_candidate_fiscal_records_use_primary_source_values() -> None:
    payload = candidate()
    records = {record["id"]: record for record in payload["candidate_package"]["fiscal_records"]}
    assert set(records) == {
        "jp-local-272051-fiscal-2026-total-expenditure",
        "jp-local-272051-fiscal-2024-total-revenue",
        "jp-local-272051-fiscal-2024-total-expenditure",
    }
    budget = records["jp-local-272051-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["metric"] == "total_expenditure"
    assert budget["amount_yen"] == 181996567000
    assert budget["stage"] == "initial_budget"
    assert budget["value_status"] == "available"
    assert budget["review_status"] == "needs_review"
    assert budget["sources"] == ["suita-budget-2026"]
    assert "議案第19号" in budget["note"]
    assert "令和8年2月18日に吹田市長後藤圭二から提出" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "千円精度のまま記録する" in budget["note"]
    revenue = records["jp-local-272051-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 179335489298
    assert revenue["stage"] == "settlement"
    assert revenue["value_status"] == "available"
    assert revenue["review_status"] == "needs_review"
    assert revenue["sources"] == ["suita-settlement-2024"]
    assert "認定第1号" in revenue["note"]
    assert "令和7年12月22日に認定された" in revenue["note"]
    assert "実質収支額は同報告書により259,882千円" in revenue["note"]
    assert "差引額844,652,846円" in revenue["note"]
    assert "不認定" not in revenue["note"]
    expenditure = records["jp-local-272051-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 178490836452
    assert expenditure["stage"] == "settlement"
    assert expenditure["sources"] == ["suita-settlement-2024"]
    assert "差引額844,652,846円" in expenditure["note"]
    assert "認定第1号" in expenditure["note"]
    assert "不認定" not in expenditure["note"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 844652846


def test_suita_candidate_evidence_packets_point_at_primary_sources() -> None:
    payload = candidate()
    packets = {packet["id"]: packet for packet in payload["candidate_package"]["evidence_packets"]}
    assert set(packets) == {
        "evidence-suita-city-2026-total-expenditure",
        "evidence-suita-city-2024-total-revenue",
        "evidence-suita-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-suita-city-2026-total-expenditure"]["claims"][0]
    assert budget_claim["source_ids"] == ["suita-budget-2026"]
    assert "181,996,567千円" in budget_claim["statement"]
    assert "原案可決" in budget_claim["statement"]
    revenue_claim = packets["evidence-suita-city-2024-total-revenue"]["claims"][0]
    assert revenue_claim["source_ids"] == ["suita-settlement-2024"]
    assert "179,335,489,298円" in revenue_claim["statement"]
    assert "認定された" in revenue_claim["statement"]
    assert "不認定" not in revenue_claim["statement"]
    expenditure_claim = packets["evidence-suita-city-2024-total-expenditure"]["claims"][0]
    assert expenditure_claim["source_ids"] == ["suita-settlement-2024"]
    assert "178,490,836,452円" in expenditure_claim["statement"]


def test_suita_candidate_progress_review_stays_staging() -> None:
    payload = candidate()
    progress = payload["candidate_package"]["progress_review"]
    assert progress["id"] == "suita-current-progress-review-summary"
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert framework["title"] == "PDCAサイクルによる進行管理（行政評価）"


def test_suita_promotion_is_reflected_in_review_queue() -> None:
    queue = load_json(QUEUE_PATH)
    assert queue["summary"]["target_count"] == 67
    assert queue["summary"]["reviewed_complete_count"] == 52
    assert queue["summary"]["pending_record_review_count"] == 15
    assert queue["summary"]["next_official_code"] == "342076"
    items = {item["official_code"]: item for item in queue["execution_queue"]}
    assert items["272051"]["name_ja"] == "吹田市"
    assert items["272051"]["status"] == "reviewed_complete"
    assert items["272051"]["completion_path"] == (
        "data/catalog/suita_phase15_completion.json"
    )
