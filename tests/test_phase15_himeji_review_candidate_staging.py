import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/himeji-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/himeji-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate() -> dict:
    return load_json(CANDIDATE_PATH)


def test_himeji_candidate_is_prepared_with_delegated_review_approved() -> None:
    payload = candidate()
    assert payload["official_code"] == "282014"
    assert payload["name_ja"] == "姫路市"
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
        "data/indexed/himeji-city/source_inventory.json"
    )


def test_himeji_candidate_sources_match_phase14_inventory_exactly() -> None:
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
        "himeji-basic-concept": "https://www.city.himeji.lg.jp/shisei/0000015166.html",
        "himeji-implementation-2026-2028": (
            "https://www.city.himeji.lg.jp/shisei/0000015569.html"
        ),
        "himeji-budget-2026": "https://www.city.himeji.lg.jp/shisei/0000032701.html",
        "himeji-settlement-2024": (
            "https://www.city.himeji.lg.jp/shisei/0000031944.html"
        ),
    }
    assert all(
        url.startswith("https://www.city.himeji.lg.jp/")
        for url in candidate_sources.values()
    )
    by_id = {
        source["id"]: source
        for source in payload["candidate_package"]["source_catalog"]["sources"]
    }
    for verified_id in (
        "himeji-basic-concept",
        "himeji-implementation-2026-2028",
        "himeji-budget-2026",
        "himeji-settlement-2024",
    ):
        assert by_id[verified_id]["verification_status"] == (
            "primary_source_live_verified_2026-11-16"
        )


def test_himeji_candidate_keeps_plan_review_records_explicit() -> None:
    payload = candidate()
    records = {
        record["id"]: record
        for record in payload["candidate_package"]["plan_review"]["records"]
    }
    assert set(records) == {
        "himeji-current-plan-period",
        "himeji-current-policy-structure",
        "himeji-progress-governance-framework",
        "himeji-plan-transition",
        "himeji-fy2024-settlement-linkage",
    }
    assert records["himeji-current-plan-period"]["decision"] == "needs_review"
    assert records["himeji-current-plan-period"]["value"] == (
        "基本構想は2021年度～2030年度（10年間）／"
        "実施計画は3年間（毎年度、掲載事業を更新）で"
        "現行は令和8年度～令和10年度（2026年度～2028年度）"
    )
    assert records["himeji-current-policy-structure"]["title"] == (
        "「ふるさと・ひめじプラン2030」の分野体系（9分野と分野目標）"
    )
    assert records["himeji-progress-governance-framework"]["title"] == (
        "総合計画の進行管理（3年ごとの政策評価と毎年度の事業PDCA）"
    )
    assert records["himeji-plan-transition"]["title"] == (
        "前総合計画「ふるさと・ひめじプラン2020」（2009年度～2020年度）からの移行"
    )
    assert "確認できていない" in records["himeji-plan-transition"]["statement"]
    linkage = records["himeji-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["title"] == (
        "令和6年度決算と姫路市総合計画「ふるさと・ひめじプラン2030」の分野体系の接続"
    )


def test_himeji_candidate_policy_structure_lists_fields() -> None:
    payload = candidate()
    plan = payload["candidate_package"]["policy_structure"]["current_plan"]
    assert plan["title"] == (
        "姫路市総合計画「ふるさと・ひめじプラン2030」実施計画（令和8年度～令和10年度）"
    )
    assert plan["vision"] == "ともに生き ともに輝く にぎわい交流拠点都市 姫路"
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2028
    assert plan["period_status"] == "verified_fixed_period"
    fields = plan["policy_fields"]
    assert len(fields) == 9
    assert len({field["id"] for field in fields}) == 9
    assert [field["name_ja"] for field in fields] == [
        "市民活動",
        "健康福祉",
        "教育",
        "環境",
        "産業",
        "観光・スポーツ",
        "都市基盤",
        "防災・安全安心",
        "行財政運営",
    ]
    # The per-field policies could not be transcribed reliably from the
    # basic concept booklet's two-column framework table, so they stay
    # deferred instead of being enumerated from an uncertain reading.
    assert all(field["measures"] == [] for field in fields)


def test_himeji_candidate_fiscal_records_use_primary_source_values() -> None:
    payload = candidate()
    records = {
        record["id"]: record
        for record in payload["candidate_package"]["fiscal_records"]
    }
    assert set(records) == {
        "jp-local-282014-fiscal-2026-total-expenditure",
        "jp-local-282014-fiscal-2024-total-revenue",
        "jp-local-282014-fiscal-2024-total-expenditure",
    }
    budget = records["jp-local-282014-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["metric"] == "total_expenditure"
    assert budget["amount_yen"] == 261800000000
    assert budget["stage"] == "initial_budget"
    assert budget["value_status"] == "available"
    assert budget["review_status"] == "needs_review"
    assert budget["sources"] == ["himeji-budget-2026"]
    assert "261,800,000千円" in budget["note"]
    assert "千円単位" in budget["note"]
    # The bill number and the vote wording were confirmed in the council's
    # official results table; the wording is recorded as printed ("可決").
    assert "議案第1号" in budget["note"]
    assert "「可決」" in budget["note"]
    # The vote date was identified from the session schedule, so the final
    # confirmation against the council minutes stays explicitly pending.
    assert "会議録による最終確認は未実施" in budget["note"]
    revenue = records["jp-local-282014-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-282014-fiscal-2024-total-expenditure"]
    for record in (revenue, expenditure):
        assert record["fiscal_year"] == 2024
        assert record["stage"] == "settlement"
        assert record["value_status"] == "available"
        assert record["review_status"] == "needs_review"
        assert record["sources"] == ["himeji-settlement-2024"]
        assert "千円" in record["note"]
        assert "議案第90号" in record["note"]
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 254438371000
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 245476363000
    # The difference matches the formal balance (形式収支) printed in the
    # city's official settlement summary.
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 8962008000
    assert "5,797,686千円" in expenditure["note"]


def test_himeji_candidate_records_fy2024_certification_as_voted() -> None:
    payload = candidate()
    package = payload["candidate_package"]
    settlement_texts = []
    for record in package["fiscal_records"]:
        if record["fiscal_year"] == 2024:
            settlement_texts.append(json.dumps(record, ensure_ascii=False))
    for packet in package["evidence_packets"]:
        if packet["subject_id"].startswith("jp-local-282014-fiscal-2024"):
            settlement_texts.append(json.dumps(packet, ensure_ascii=False))
    for record in package["plan_review"]["records"]:
        if record["id"] == "himeji-fy2024-settlement-linkage":
            settlement_texts.append(json.dumps(record, ensure_ascii=False))
    assert settlement_texts
    for text in settlement_texts:
        # The FY2024 certification was confirmed in the council's official
        # results table (bill 90, certified); the candidate records exactly
        # that outcome and never the opposite one.
        assert "議案第90号" in text
        assert "認定" in text
    whole_text = json.dumps(payload, ensure_ascii=False)
    assert "不認定" not in whole_text


def test_himeji_candidate_evidence_packets_point_at_primary_sources() -> None:
    payload = candidate()
    packets = {
        packet["id"]: packet
        for packet in payload["candidate_package"]["evidence_packets"]
    }
    assert set(packets) == {
        "evidence-himeji-city-2026-total-expenditure",
        "evidence-himeji-city-2024-total-revenue",
        "evidence-himeji-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-himeji-city-2026-total-expenditure"]["claims"][0]
    assert budget_claim["source_ids"] == ["himeji-budget-2026"]
    assert "261,800,000千円" in budget_claim["statement"]
    assert "議案第1号" in budget_claim["statement"]
    revenue_claim = packets["evidence-himeji-city-2024-total-revenue"]["claims"][0]
    assert revenue_claim["source_ids"] == ["himeji-settlement-2024"]
    assert "254,438,371千円" in revenue_claim["statement"]
    assert "議案第90号" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-himeji-city-2024-total-expenditure"][
        "claims"
    ][0]
    assert expenditure_claim["source_ids"] == ["himeji-settlement-2024"]
    assert "245,476,363千円" in expenditure_claim["statement"]
    assert "8,962,008千円" in expenditure_claim["statement"]
    assert "5,797,686千円" in expenditure_claim["statement"]


def test_himeji_candidate_progress_review_stays_staging() -> None:
    payload = candidate()
    progress = payload["candidate_package"]["progress_review"]
    assert progress["id"] == "himeji-current-progress-review-summary"
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert framework["title"] == (
        "実施計画（2026年度～2028年度・3年ローリング）と政策評価・事業PDCAによる進行管理"
    )


def test_himeji_promotion_is_reflected_in_review_queue() -> None:
    queue = load_json(QUEUE_PATH)
    assert queue["summary"]["target_count"] == 67
    assert queue["summary"]["reviewed_complete_count"] == 43
    assert queue["summary"]["pending_record_review_count"] == 24
    assert queue["summary"]["next_official_code"] == "282022"
    items = {item["official_code"]: item for item in queue["execution_queue"]}
    assert items["282014"]["name_ja"] == "姫路市"
    assert items["282014"]["status"] == "reviewed_complete"
    assert items["282014"]["completion_path"] == (
        "data/catalog/himeji_phase15_completion.json"
    )
