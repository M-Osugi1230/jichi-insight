import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/saga-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/saga-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_candidate():
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def test_saga_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = load_candidate()

    assert candidate["candidate_id"] == "saga-phase15-review-candidate"
    assert candidate["official_code"] == "412015"
    assert candidate["name_ja"] == "佐賀市"
    assert candidate["phase"] == 15
    assert candidate["schema_version"] == 1
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["publication"]["eligible"] is False
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["reviewed_at"] == "2026-11-17"
    assert candidate["human_review"]["reviewer_note"]
    # The owner did not review the primary sources personally: on
    # 2026-11-15 the owner explicitly delegated the review to Muse in
    # chat, and the note must record that delegation rather than
    # claiming an owner review.
    assert "委任" in candidate["human_review"]["reviewer_note"]
    assert "レビューはあなたがやってください" in candidate["human_review"][
        "reviewer_note"
    ]


def test_saga_candidate_catalog_matches_phase14_inventory() -> None:
    candidate = load_candidate()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    sources = candidate["candidate_package"]["source_catalog"]["sources"]

    inventory_by_id = {source["id"]: source for source in inventory["sources"]}
    assert len(sources) == len(inventory_by_id) == 5
    for source in sources:
        assert source["id"] in inventory_by_id
        assert source["official_url"] == inventory_by_id[source["id"]]["official_url"]
        assert source["official_url"].startswith("https://www.city.saga.lg.jp/")
        assert source["verification_status"].startswith("primary_source_live_verified")


def test_saga_candidate_plan_records_keep_framework_and_transition() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["plan_review"]["records"]
    }

    assert set(records) == {
        "saga-current-plan-period",
        "saga-current-policy-structure",
        "saga-progress-governance-framework",
        "saga-plan-transition",
        "saga-fy2024-settlement-linkage",
    }
    period = records["saga-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["evidence_role"] == "current_plan_identity"
    assert "第3次佐賀市総合計画" in period["statement"]
    assert "2025年度〜2040年度の16年間" in period["statement"]
    assert "前期" in period["statement"]
    assert "2025年度〜2032年度の8年間" in period["statement"]
    assert "後期2033年度〜2040年度の8年間" in period["statement"]
    assert "verified_fixed_period" in period["statement"]
    structure = records["saga-current-policy-structure"]
    assert structure["decision"] == "needs_review"
    assert "佐賀らしさでみんなが上を向くまち" in structure["statement"]
    assert "10の分野" in structure["statement"]
    governance = records["saga-progress-governance-framework"]
    assert governance["decision"] == "needs_review"
    assert "行政評価" in governance["statement"]
    assert "未来共創プラン" in governance["statement"]
    assert "市民意向調査" in governance["statement"]
    transition = records["saga-plan-transition"]
    assert transition["decision"] == "needs_review"
    assert transition["evidence_role"] == "plan_transition"
    assert "第2次佐賀市総合計画" in transition["statement"]
    assert "2015年度〜" in transition["statement"]
    assert "2024年度" in transition["statement"]
    linkage = records["saga-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "最終年度" in linkage["statement"]
    assert "第60号議案" in linkage["statement"]


def test_saga_candidate_policy_structure_keeps_ten_fields() -> None:
    candidate = load_candidate()
    plan = candidate["candidate_package"]["policy_structure"]["current_plan"]

    assert plan["title"].startswith("第3次佐賀市総合計画")
    assert plan["vision"] == "佐賀らしさでみんなが上を向くまち"
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2040
    assert plan["period_status"] == "verified_fixed_period"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "01 子育て・教育",
        "02 健康・福祉",
        "03 文化・スポーツ",
        "04 経済・観光",
        "05 農林水産",
        "06 生活・環境",
        "07 コミュニティ",
        "08 防災・安全",
        "09 都市・交通",
        "10 行政経営",
    ]
    principles = " ".join(plan["management_principles"])
    assert "第2次佐賀市総合計画" in principles
    assert "行政評価" in principles
    assert "流用しない" in principles


def test_saga_candidate_fiscal_records_match_primary_sources() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }

    budget = records["jp-local-412015-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 119_800_000_000
    assert budget["review_status"] == "needs_review"
    assert "第1号議案" in budget["note"]
    assert "119,800,000千円" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "2026年3月24日" in budget["note"]
    assert "修正案" in budget["note"]
    assert "119,749,911千円" in budget["note"]
    assert "千円単位" in budget["note"]

    revenue = records["jp-local-412015-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 118_510_118_104
    assert "第60号議案" in revenue["note"]
    assert "118,510,118,104円" in revenue["note"]
    assert "2025年9月16日" in revenue["note"]
    assert "普通会計ベース" in revenue["note"]
    assert "第2次佐賀市総合計画の最終年度" in revenue["note"]

    expenditure = records["jp-local-412015-fiscal-2024-total-expenditure"]
    assert expenditure["stage"] == "settlement"
    assert expenditure["amount_yen"] == 116_749_721_609
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1_760_396_495


def test_saga_candidate_keeps_real_balance_from_audit_summary() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }
    note = records["jp-local-412015-fiscal-2024-total-expenditure"]["note"]

    assert "実質収支は1,161,595千円" in note
    assert "翌年度へ繰り越すべき財源598,801千円" in note
    assert "千円単位の公表値のまま記録する" in note


def test_saga_candidate_certification_was_directly_confirmed() -> None:
    candidate = load_candidate()
    text = json.dumps(candidate, ensure_ascii=False)

    assert "第60号議案" in text
    assert "2025年9月16日" in text
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_saga_candidate_budget_vote_wording_is_recorded_as_published() -> None:
    candidate = load_candidate()
    packets = {
        packet["id"]: packet
        for packet in candidate["candidate_package"]["evidence_packets"]
    }
    claim = packets["evidence-saga-city-2026-total-expenditure"]["claims"][0]

    assert claim["decision"] == "needs_review"
    assert "第1号議案" in claim["statement"]
    assert "原案可決" in claim["statement"]
    assert "2026年3月24日" in claim["statement"]
    assert "修正案" in claim["statement"]
    assert "119,749,911千円" in claim["statement"]


def test_saga_candidate_does_not_use_ordinary_account_aggregates() -> None:
    candidate = load_candidate()
    sources = {
        source["id"]: source
        for source in candidate["candidate_package"]["source_catalog"]["sources"]
    }

    boundary = sources["saga-settlement-2024"]["use_boundary"]
    assert "普通会計ベース" in boundary
    assert "混同しない" in boundary
    location = sources["saga-settlement-2024"]["evidence_location"]
    assert "決算審査意見書" in location
    assert "第60号議案" in location
    text = json.dumps(candidate, ensure_ascii=False)
    assert "118,508,922" in text  # ordinary-account value cited only as excluded


def test_saga_candidate_evidence_packets_cover_fiscal_records() -> None:
    candidate = load_candidate()
    package = candidate["candidate_package"]
    fiscal_ids = {record["id"] for record in package["fiscal_records"]}
    packet_subjects = {packet["subject_id"] for packet in package["evidence_packets"]}

    assert packet_subjects == fiscal_ids
    for packet in package["evidence_packets"]:
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
        assert packet["open_questions"]


def test_saga_candidate_progress_review_stays_staging() -> None:
    candidate = load_candidate()
    progress = candidate["candidate_package"]["progress_review"]

    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "未来共創プラン" in framework["title"]
    assert "行政評価" in framework["evaluation_structure"]
    assert "市民意向調査" in framework["evaluation_structure"]


def test_saga_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    assert queue["summary"]["reviewed_complete_count"] == 65
    assert queue["summary"]["pending_record_review_count"] == 2
    assert queue["summary"]["next_official_code"] == "462012"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "412015"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/saga_phase15_completion.json"
