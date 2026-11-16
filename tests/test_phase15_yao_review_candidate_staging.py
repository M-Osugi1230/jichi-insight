import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/yao-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/yao-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate() -> dict:
    return load_json(CANDIDATE_PATH)


def test_yao_candidate_is_prepared_and_pending_human_review() -> None:
    payload = candidate()
    assert payload["official_code"] == "272124"
    assert payload["name_ja"] == "八尾市"
    assert payload["status"] == "review_candidate"
    assert payload["package_state"] == "prepared"
    assert payload["human_review"]["required"] is True
    assert payload["human_review"]["status"] == "pending"
    assert payload["human_review"]["reviewed_at"] is None
    assert payload["human_review"]["reviewer_note"] is None
    assert payload["publication"]["eligible"] is False
    assert payload["source_inventory_path"] == "data/indexed/yao-city/source_inventory.json"


def test_yao_candidate_sources_match_phase14_inventory_exactly() -> None:
    payload = candidate()
    inventory = load_json(INVENTORY_PATH)
    inventory_sources = {source["id"]: source["official_url"] for source in inventory["sources"]}
    candidate_sources = {
        source["id"]: source["official_url"]
        for source in payload["candidate_package"]["source_catalog"]["sources"]
    }
    assert candidate_sources == inventory_sources
    assert candidate_sources == {
        "yao-sixth-latter-plan": (
            "https://www.city.yao.osaka.jp/shisei/seisaku_keikaku_zaisei/"
            "1009538/1009540/1017781.html"
        ),
        "yao-administrative-evaluation": (
            "https://www.city.yao.osaka.jp/shisei/seisaku_keikaku_zaisei/"
            "1009538/1009592/1009580.html"
        ),
        "yao-budget-2026": (
            "https://www.city.yao.osaka.jp/shisei/seisaku_keikaku_zaisei/"
            "1009738/1009740/1017102.html"
        ),
        "yao-settlement-2024": (
            "https://www.city.yao.osaka.jp/shisei/seisaku_keikaku_zaisei/"
            "1009738/1009743/1009747.html"
        ),
    }
    assert all(
        url.startswith("https://www.city.yao.osaka.jp/") for url in candidate_sources.values()
    )


def test_yao_candidate_keeps_plan_review_records_explicit() -> None:
    payload = candidate()
    records = {
        record["id"]: record for record in payload["candidate_package"]["plan_review"]["records"]
    }
    assert set(records) == {
        "yao-current-plan-period",
        "yao-current-policy-structure",
        "yao-progress-governance-framework",
        "yao-plan-transition",
        "yao-fy2024-settlement-linkage",
    }
    assert records["yao-current-plan-period"]["decision"] == "needs_review"
    assert records["yao-current-plan-period"]["value"] == (
        "基本構想は2021年度～2028年度（8年間）／基本計画は前期2021年度～2024年度・"
        "後期2025年度～2028年度（各4年間）／実施計画は毎年度見直し"
    )
    assert records["yao-current-policy-structure"]["title"] == (
        "第6次総合計画の6つのまちづくりの目標（政策）と後期基本計画の33施策"
        "（マトリクス型施策体系）"
    )
    assert records["yao-progress-governance-framework"]["title"] == (
        "行政評価（施策評価・事務事業評価）による進行管理"
    )
    assert records["yao-plan-transition"]["title"] == (
        "第6次八尾市総合計画の基本計画の前期（2021〜2024年度）から"
        "後期（2025〜2028年度）への移行"
    )
    linkage = records["yao-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["title"] == "令和6年度決算と第6次八尾市総合計画の施策体系の接続"


def test_yao_candidate_policy_structure_lists_all_goals_and_measures() -> None:
    payload = candidate()
    plan = payload["candidate_package"]["policy_structure"]["current_plan"]
    assert plan["title"] == "第6次八尾市総合計画 後期基本計画"
    assert plan["vision"] == "つながり、かがやき、しあわせつづく、成長都市 八尾"
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2028
    assert plan["period_status"] == "verified_fixed_period"
    fields = plan["policy_fields"]
    assert len(fields) == 6
    assert len({field["id"] for field in fields}) == 6
    # The latter basic plan uses a matrix structure: each of the 33 measures
    # relates to one or more of the 6 goals, giving 83 goal-measure links.
    measures = [measure for field in fields for measure in field["measures"]]
    assert len(measures) == 83
    assert len(set(measures)) == 33
    assert not any("上水道" in measure for measure in measures)
    assert not any(measure.startswith("施策16 ") for measure in measures)
    by_id = {field["id"]: field for field in fields}
    assert by_id["field-1"]["name_ja"] == "目標1（政策1）未来への育ちを誰もが実感できるまち"
    assert by_id["field-1"]["measures"] == [
        "施策1 切れ目のない子育て支援の推進",
        "施策2 就学前教育・保育の充実",
        "施策3 子どもの学びと育ちの充実",
        "施策4 子ども・若者がチャレンジできる環境づくり",
        "施策6 歴史資産などの保全・活用・発信",
        "施策8 芸術文化の魅力を活かした豊かなまちづくり",
        "施策25 障がいのある人への支援の充実",
        "施策26 生活困窮者への支援",
        "施策28 平和意識の向上",
        "施策31 生涯学習とスポーツの振興",
    ]
    assert by_id["field-2"]["name_ja"] == "目標2（政策2）もしもの時への備えがあるまち"
    assert len(by_id["field-2"]["measures"]) == 18
    assert by_id["field-3"]["name_ja"] == "目標3（政策3）世界に魅力が広がるまち"
    assert len(by_id["field-3"]["measures"]) == 11
    assert by_id["field-4"]["name_ja"] == (
        "目標4（政策4）日常の暮らしが快適で環境にやさしいまち"
    )
    assert len(by_id["field-4"]["measures"]) == 16
    assert by_id["field-5"]["name_ja"] == (
        "目標5（政策5）つながりを創り育て自分らしさを大切にしあうまち"
    )
    assert len(by_id["field-5"]["measures"]) == 20
    assert by_id["field-6"]["name_ja"] == (
        "目標6（政策6）みんなの力でともにつくる持続可能なまち"
    )
    assert by_id["field-6"]["measures"] == [
        "施策5 やおプロモーションの推進",
        "施策21 地域医療体制の充実",
        "施策27 一人ひとりの人権が尊重される差別のない社会の推進",
        "施策28 平和意識の向上",
        "施策30 地域のまちづくり支援・市民活動の促進",
        "施策32 信頼される行政経営",
        "施策33 公共施設マネジメントの推進",
        "施策34 行財政改革の推進",
    ]


def test_yao_candidate_fiscal_records_use_primary_source_values() -> None:
    payload = candidate()
    records = {record["id"]: record for record in payload["candidate_package"]["fiscal_records"]}
    assert set(records) == {
        "jp-local-272124-fiscal-2026-total-expenditure",
        "jp-local-272124-fiscal-2024-total-revenue",
        "jp-local-272124-fiscal-2024-total-expenditure",
    }
    budget = records["jp-local-272124-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["metric"] == "total_expenditure"
    assert budget["amount_yen"] == 132613637000
    assert budget["stage"] == "initial_budget"
    assert budget["value_status"] == "available"
    assert budget["review_status"] == "needs_review"
    assert budget["sources"] == ["yao-budget-2026"]
    assert "議案第18号" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "千円精度のまま記録する" in budget["note"]
    revenue = records["jp-local-272124-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 126116660528
    assert revenue["stage"] == "settlement"
    assert revenue["value_status"] == "available"
    assert revenue["review_status"] == "needs_review"
    assert revenue["sources"] == ["yao-settlement-2024"]
    assert "認定第1号" in revenue["note"]
    assert "2025年10月22日に認定された" in revenue["note"]
    assert "実質収支額は同調書により1,797,799,491円" in revenue["note"]
    assert "差引額2,234,620,162円" in revenue["note"]
    assert "不認定" not in revenue["note"]
    expenditure = records["jp-local-272124-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 123882040366
    assert expenditure["stage"] == "settlement"
    assert expenditure["sources"] == ["yao-settlement-2024"]
    assert "差引額2,234,620,162円" in expenditure["note"]
    assert "認定第1号" in expenditure["note"]
    assert "不認定" not in expenditure["note"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2234620162


def test_yao_candidate_evidence_packets_point_at_primary_sources() -> None:
    payload = candidate()
    packets = {packet["id"]: packet for packet in payload["candidate_package"]["evidence_packets"]}
    assert set(packets) == {
        "evidence-yao-city-2026-total-expenditure",
        "evidence-yao-city-2024-total-revenue",
        "evidence-yao-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-yao-city-2026-total-expenditure"]["claims"][0]
    assert budget_claim["source_ids"] == ["yao-budget-2026"]
    assert "132,613,637千円" in budget_claim["statement"]
    assert "原案可決" in budget_claim["statement"]
    revenue_claim = packets["evidence-yao-city-2024-total-revenue"]["claims"][0]
    assert revenue_claim["source_ids"] == ["yao-settlement-2024"]
    assert "126,116,660,528円" in revenue_claim["statement"]
    assert "認定された" in revenue_claim["statement"]
    assert "不認定" not in revenue_claim["statement"]
    expenditure_claim = packets["evidence-yao-city-2024-total-expenditure"]["claims"][0]
    assert expenditure_claim["source_ids"] == ["yao-settlement-2024"]
    assert "123,882,040,366円" in expenditure_claim["statement"]
    assert "不認定" not in expenditure_claim["statement"]


def test_yao_candidate_progress_review_stays_staging() -> None:
    payload = candidate()
    progress = payload["candidate_package"]["progress_review"]
    assert progress["id"] == "yao-current-progress-review-summary"
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert framework["title"] == "行政評価（施策評価・事務事業評価）による進行管理"


def test_yao_candidate_does_not_change_review_queue() -> None:
    queue = load_json(QUEUE_PATH)
    assert queue["summary"]["target_count"] == 67
    assert queue["summary"]["reviewed_complete_count"] == 39
    assert queue["summary"]["pending_record_review_count"] == 28
    assert queue["summary"]["next_official_code"] == "272124"
    items = {item["official_code"]: item for item in queue["execution_queue"]}
    assert items["272124"]["name_ja"] == "八尾市"
    assert items["272124"]["status"] == "pending_record_review"
    assert items["272124"]["completion_path"] is None
