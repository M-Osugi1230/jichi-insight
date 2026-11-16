import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/neyagawa-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/neyagawa-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate() -> dict:
    return load_json(CANDIDATE_PATH)


def test_neyagawa_candidate_is_prepared_with_delegated_review_approved() -> None:
    payload = candidate()
    assert payload["official_code"] == "272159"
    assert payload["name_ja"] == "寝屋川市"
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
    assert payload["source_inventory_path"] == (
        "data/indexed/neyagawa-city/source_inventory.json"
    )


def test_neyagawa_candidate_sources_match_phase14_inventory_exactly() -> None:
    payload = candidate()
    inventory = load_json(INVENTORY_PATH)
    inventory_sources = {
        source["id"]: source["official_url"] for source in inventory["sources"]
    }
    candidate_sources = {
        source["id"]: source["official_url"]
        for source in payload["candidate_package"]["source_catalog"]["sources"]
    }
    assert candidate_sources == inventory_sources
    assert candidate_sources == {
        "neyagawa-sixth-plan": (
            "https://www.city.neyagawa.osaka.jp/organization_list/keieikikaku/"
            "kikakuikka/soukei_jinkouvision_senryaku/"
            "sougoukeikaku_6_sougousenryaku_2/1616582538632.html"
        ),
        "neyagawa-budget-policy-2026": (
            "https://www.city.neyagawa.osaka.jp/organization_list/zaimu/zaiseika/"
            "yosan/yosanhenseihoushin/25799.html"
        ),
        "neyagawa-budget-2026": (
            "https://www.city.neyagawa.osaka.jp/organization_list/zaimu/zaiseika/"
            "yosan/yosan/R8tousyoyosan/26514.html"
        ),
        "neyagawa-settlement-2024": (
            "https://www.city.neyagawa.osaka.jp/organization_list/zaimu/zaiseika/"
            "kessann/kessan/reiwa5nenndokessann_2/index.html"
        ),
    }
    assert all(
        url.startswith("https://www.city.neyagawa.osaka.jp/")
        for url in candidate_sources.values()
    )
    by_id = {
        source["id"]: source
        for source in payload["candidate_package"]["source_catalog"]["sources"]
    }
    for verified_id in (
        "neyagawa-sixth-plan",
        "neyagawa-budget-policy-2026",
        "neyagawa-budget-2026",
        "neyagawa-settlement-2024",
    ):
        assert by_id[verified_id]["verification_status"] == (
            "primary_source_live_verified_2026-11-16"
        )


def test_neyagawa_candidate_keeps_plan_review_records_explicit() -> None:
    payload = candidate()
    records = {
        record["id"]: record
        for record in payload["candidate_package"]["plan_review"]["records"]
    }
    assert set(records) == {
        "neyagawa-current-plan-period",
        "neyagawa-current-policy-structure",
        "neyagawa-progress-governance-framework",
        "neyagawa-plan-transition",
        "neyagawa-fy2024-settlement-linkage",
    }
    assert records["neyagawa-current-plan-period"]["decision"] == "needs_review"
    assert records["neyagawa-current-plan-period"]["value"] == (
        "基本戦略（基本構想・戦略プラン）は2021年度～2027年度（7年間）／"
        "実施計画は前期2021年度～2023年度（3年間）・後期2024年度～2027年度（4年間）"
    )
    assert records["neyagawa-current-policy-structure"]["title"] == (
        "第六次総合計画の戦略プランの19施策（3つの最重要ファクター・"
        "生活を支える施策・くらしの質を高める施策）"
    )
    assert records["neyagawa-progress-governance-framework"]["title"] == (
        "後期実施計画の進捗管理（PDCIサイクルに基づく行政評価との一体的実施）"
    )
    assert records["neyagawa-plan-transition"]["title"] == (
        "第六次寝屋川市総合計画の実施計画の前期（2021〜2023年度）から"
        "後期（2024〜2027年度）への移行"
    )
    assert "確認できていない" in records["neyagawa-plan-transition"]["statement"]
    linkage = records["neyagawa-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["title"] == "令和6年度決算と第六次寝屋川市総合計画の施策体系の接続"


def test_neyagawa_candidate_policy_structure_lists_all_measures() -> None:
    payload = candidate()
    plan = payload["candidate_package"]["policy_structure"]["current_plan"]
    assert plan["title"] == "第六次寝屋川市総合計画 後期実施計画"
    assert plan["vision"] == "新たな価値を創り、選ばれるまち 寝屋川"
    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2027
    assert plan["period_status"] == "verified_fixed_period"
    fields = plan["policy_fields"]
    assert len(fields) == 5
    assert len({field["id"] for field in fields}) == 5
    measures = [measure for field in fields for measure in field["measures"]]
    assert len(measures) == 19
    assert len(set(measures)) == 19
    by_id = {field["id"]: field for field in fields}
    assert by_id["field-1"]["name_ja"] == (
        "ファクターI 子どもに最善を尽くす（訴求力のある施策）"
    )
    assert by_id["field-1"]["measures"] == [
        "施策1 安心して子どもを産み、育てる環境づくり",
        "施策2 寝屋川市だから学べる「寝屋川教育」",
        "施策3 子どもを全力で守り抜く",
    ]
    assert by_id["field-2"]["name_ja"] == (
        "ファクターII 誰もが住みたくなるまちをつくる（訴求力のある施策）"
    )
    assert by_id["field-2"]["measures"] == [
        "施策4 ポテンシャルをフル活用した都市基盤整備",
        "施策5 将来を見据えた公共施設の集約・複合化",
        "施策6 働く場の創出と多様な人材の育成・確保",
    ]
    assert by_id["field-3"]["name_ja"] == (
        "ファクターIII 命を全力で守り、豊かなくらしを実現する（訴求力のある施策）"
    )
    assert by_id["field-3"]["measures"] == [
        "施策7 災害から命を守るための対策",
        "施策8 防犯力向上による体感治安の改善",
        "施策9 健康寿命の延伸",
    ]
    assert by_id["field-4"]["name_ja"] == "生活を支える施策"
    assert by_id["field-4"]["measures"] == [
        "施策10 人権を尊重し、多様性を認め合う社会づくり",
        "施策11 誰もが安心して生活でき、共に支え合う地域づくり",
        "施策12 衛生的で快適な生活の確保",
        "施策13 環境を守り、日頃のくらしを良好に",
    ]
    assert by_id["field-5"]["name_ja"] == "くらしの質を高める施策"
    assert by_id["field-5"]["measures"] == [
        "施策14 学びによる市民文化の向上と発展",
        "施策15 豊かな自然があるくらし",
        "施策16 地域づくり・きずなづくり",
        "施策17 市民ニーズを捉えた行政サービスの充実",
        "施策18 市民ニーズの把握・情報発信力の強化",
        "施策19 未来へつなぐ行財政運営",
    ]


def test_neyagawa_candidate_fiscal_records_use_primary_source_values() -> None:
    payload = candidate()
    records = {
        record["id"]: record
        for record in payload["candidate_package"]["fiscal_records"]
    }
    assert set(records) == {
        "jp-local-272159-fiscal-2026-total-expenditure",
        "jp-local-272159-fiscal-2024-total-revenue",
        "jp-local-272159-fiscal-2024-total-expenditure",
    }
    budget = records["jp-local-272159-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["metric"] == "total_expenditure"
    assert budget["amount_yen"] == 109730000000
    assert budget["stage"] == "initial_budget"
    assert budget["value_status"] == "available"
    assert budget["review_status"] == "needs_review"
    assert budget["sources"] == ["neyagawa-budget-2026"]
    assert "議案第28号" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "2026年3月25日" in budget["note"]
    assert "万円単位" in budget["note"]
    # The FY2024 settlement values were confirmed in the supplementary
    # research from two primary sources that agree exactly: the settlement
    # book's real-balance statement (実質収支に関する調書) and the
    # September 2025 council reference material. Both publish at
    # thousand-yen precision, so the values stay at that precision and no
    # yen figure is synthesised; the ordinary-account (普通会計)
    # aggregates the city publishes are not used.
    revenue = records["jp-local-272159-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["metric"] == "total_revenue"
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 106597604000
    assert revenue["value"] is None
    assert revenue["value_status"] == "available"
    assert revenue["confidence"] == "medium"
    assert revenue["review_status"] == "needs_review"
    assert revenue["sources"] == ["neyagawa-settlement-2024"]
    assert "106,597,604千円" in revenue["note"]
    assert "1,263,633千円" in revenue["note"]
    assert "1,248,678千円" in revenue["note"]
    assert "認定第1号" in revenue["note"]
    assert "2025年12月3日" in revenue["note"]
    assert "千円精度" in revenue["note"]
    assert "普通会計" in revenue["note"]
    expenditure = records["jp-local-272159-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["stage"] == "settlement"
    assert expenditure["amount_yen"] == 105333971000
    assert expenditure["value"] is None
    assert expenditure["value_status"] == "available"
    assert expenditure["confidence"] == "medium"
    assert expenditure["review_status"] == "needs_review"
    assert expenditure["sources"] == ["neyagawa-settlement-2024"]
    assert "105,333,971千円" in expenditure["note"]
    assert "1,263,633千円" in expenditure["note"]
    assert "1,248,678千円" in expenditure["note"]
    assert "認定第1号" in expenditure["note"]
    assert "千円精度" in expenditure["note"]


def test_neyagawa_candidate_records_fy2024_certification() -> None:
    payload = candidate()
    package = payload["candidate_package"]
    settlement_texts = []
    for record in package["fiscal_records"]:
        if record["fiscal_year"] == 2024:
            settlement_texts.append(json.dumps(record, ensure_ascii=False))
    for packet in package["evidence_packets"]:
        if packet["subject_id"].startswith("jp-local-272159-fiscal-2024"):
            settlement_texts.append(json.dumps(packet, ensure_ascii=False))
    for record in package["plan_review"]["records"]:
        if record["id"] == "neyagawa-fy2024-settlement-linkage":
            settlement_texts.append(json.dumps(record, ensure_ascii=False))
    assert settlement_texts
    for text in settlement_texts:
        # The supplementary research confirmed from the council's official
        # bill lists that certification bill No. 1 was submitted to the
        # September 2025 session, kept under continued review, and
        # certified on 2025-12-03 in the December session. The outcome
        # must be recorded as a certification, never as a rejection.
        assert "認定第1号" in text
        assert "不認定" not in text
    whole_text = json.dumps(payload, ensure_ascii=False)
    assert "不認定" not in whole_text


def test_neyagawa_candidate_evidence_packets_point_at_primary_sources() -> None:
    payload = candidate()
    packets = {
        packet["id"]: packet
        for packet in payload["candidate_package"]["evidence_packets"]
    }
    assert set(packets) == {
        "evidence-neyagawa-city-2026-total-expenditure",
        "evidence-neyagawa-city-2024-total-revenue",
        "evidence-neyagawa-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-neyagawa-city-2026-total-expenditure"]["claims"][0]
    assert budget_claim["source_ids"] == ["neyagawa-budget-2026"]
    assert "109,730,000千円" in budget_claim["statement"]
    assert "議案第28号" in budget_claim["statement"]
    assert "原案可決" in budget_claim["statement"]
    revenue_claim = packets["evidence-neyagawa-city-2024-total-revenue"]["claims"][0]
    assert revenue_claim["source_ids"] == ["neyagawa-settlement-2024"]
    assert "106,597,604千円" in revenue_claim["statement"]
    assert "1,248,678千円" in revenue_claim["statement"]
    assert "認定第1号" in revenue_claim["statement"]
    assert "2025年12月3日" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-neyagawa-city-2024-total-expenditure"][
        "claims"
    ][0]
    assert expenditure_claim["source_ids"] == ["neyagawa-settlement-2024"]
    assert "105,333,971千円" in expenditure_claim["statement"]
    assert "1,263,633千円" in expenditure_claim["statement"]
    assert "認定第1号" in expenditure_claim["statement"]
    assert "2025年12月3日" in expenditure_claim["statement"]


def test_neyagawa_candidate_progress_review_stays_staging() -> None:
    payload = candidate()
    progress = payload["candidate_package"]["progress_review"]
    assert progress["id"] == "neyagawa-current-progress-review-summary"
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert framework["title"] == (
        "後期実施計画（令和6年度～令和9年度）とPDCIサイクルによる進捗管理"
    )


def test_neyagawa_promotion_is_reflected_in_review_queue() -> None:
    queue = load_json(QUEUE_PATH)
    assert queue["summary"]["target_count"] == 67
    assert queue["summary"]["reviewed_complete_count"] == 58
    assert queue["summary"]["pending_record_review_count"] == 9
    assert queue["summary"]["next_official_code"] == "392014"
    items = {item["official_code"]: item for item in queue["execution_queue"]}
    assert items["272159"]["name_ja"] == "寝屋川市"
    assert items["272159"]["status"] == "reviewed_complete"
    assert items["272159"]["completion_path"] == (
        "data/catalog/neyagawa_phase15_completion.json"
    )
