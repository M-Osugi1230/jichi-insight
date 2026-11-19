import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/kagoshima-city/review_candidate.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
INVENTORY = ROOT / "data/indexed/kagoshima-city/source_inventory.json"


def candidate() -> dict:
    return json.loads(CANDIDATE.read_text(encoding="utf-8"))


def candidate_text() -> str:
    return CANDIDATE.read_text(encoding="utf-8")


def fiscal_record(record_id: str) -> dict:
    package = candidate()["candidate_package"]
    return next(record for record in package["fiscal_records"] if record["id"] == record_id)


def plan_record(record_id: str) -> dict:
    package = candidate()["candidate_package"]
    return next(record for record in package["plan_review"]["records"] if record["id"] == record_id)


def test_kagoshima_candidate_is_prepared_with_delegated_review_approved() -> None:
    data = candidate()
    assert data["candidate_id"] == "kagoshima-phase15-review-candidate"
    assert data["official_code"] == "462012"
    assert data["name_ja"] == "鹿児島市"
    assert data["package_state"] == "prepared"
    assert data["status"] == "review_candidate"
    assert data["human_review"]["status"] == "approved"
    assert data["human_review"]["required"] is True
    assert data["human_review"]["reviewed_at"] == "2026-11-17"
    assert data["human_review"]["reviewer_note"]
    # The owner did not review the primary sources personally: on
    # 2026-11-15 the owner explicitly delegated the review to Muse in
    # chat, and the note must record that delegation rather than
    # claiming an owner review.
    assert "委任" in data["human_review"]["reviewer_note"]
    assert "レビューはあなたがやってください" in data["human_review"]["reviewer_note"]
    assert data["publication"]["eligible"] is False


def test_kagoshima_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["target_count"] == 68
    assert summary["reviewed_complete_count"] == 68
    assert summary["pending_record_review_count"] == 0
    assert summary["next_official_code"] is None
    entry = next(item for item in queue["execution_queue"] if item["official_code"] == "462012")
    assert entry["name_ja"] == "鹿児島市"
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/kagoshima_phase15_completion.json"


def test_kagoshima_candidate_sources_match_phase14_inventory() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    inventory_sources = {
        source["id"]: source["official_url"] for source in inventory["sources"]
    }
    catalog_sources = candidate()["candidate_package"]["source_catalog"]["sources"]
    assert len(catalog_sources) == 5
    for source in catalog_sources:
        assert source["id"] in inventory_sources
        assert source["official_url"] == inventory_sources[source["id"]]
        assert source["official_url"].startswith("https://www.city.kagoshima.lg.jp/")


def test_kagoshima_candidate_records_current_plan_without_adopting_the_draft() -> None:
    current = candidate()["candidate_package"]["policy_structure"]["current_plan"]
    assert "第六次鹿児島市総合計画" in current["title"]
    assert current["start_fiscal_year"] == 2022
    assert current["end_fiscal_year"] == 2031
    assert current["period_status"] == "transition_or_unresolved"
    assert current["vision"] == "つながる人・まち 彩りあふれる 躍動都市・かごしま"
    assert len(current["policy_fields"]) == 6
    assert all(field["measures"] == [] for field in current["policy_fields"])
    transition = plan_record("kagoshima-plan-transition")
    assert transition["decision"] == "needs_review"
    assert "素案" in transition["statement"]
    assert "第五次鹿児島市総合計画" in transition["statement"]


def test_kagoshima_candidate_records_fy2026_budget_at_published_precision() -> None:
    budget = fiscal_record("jp-local-462012-fiscal-2026-total-expenditure")
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 304_837_000_000
    assert budget["value_status"] == "available"
    assert budget["review_status"] == "needs_review"
    assert "304,837,000千円" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "千円単位" in budget["note"]
    assert "定第195号議案" in budget["note"]
    assert "2026年3月19日" in budget["note"]
    assert "実ブラウザによる補完調査" in budget["note"]
    assert "未特定" not in budget["note"]


def test_kagoshima_candidate_records_fy2024_settlement_at_published_precision() -> None:
    revenue = fiscal_record("jp-local-462012-fiscal-2024-total-revenue")
    expenditure = fiscal_record("jp-local-462012-fiscal-2024-total-expenditure")
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 306_759_735_000
    assert expenditure["amount_yen"] == 296_622_819_000
    assert revenue["value_status"] == "available"
    assert expenditure["value_status"] == "available"
    assert "306,759,735千円" in revenue["note"]
    assert "認定" in revenue["note"]
    assert "定第56号議案" in revenue["note"]
    assert "2025年12月2日" in revenue["note"]
    assert "実ブラウザによる補完調査" in revenue["note"]
    assert "未特定" not in revenue["note"]
    assert "千円単位" in revenue["note"]
    assert "296,622,819千円" in expenditure["note"]
    assert "10,136,916千円" in expenditure["note"]
    assert "6,584,470千円" in expenditure["note"]


def test_kagoshima_candidate_bill_numbers_and_vote_dates_confirmed() -> None:
    text = candidate_text()

    # The FY2026 budget bill number (定第195号議案) and vote date
    # (2026-03-19, 原案可決) and the FY2024 settlement bill number
    # (定第56号議案) and certification date (2025-12-02, 認定) were not
    # reachable from text-accessible official sources, so a
    # supplementary live-browser investigation confirmed them from the
    # council's official minutes search system. The candidate records
    # those facts and their browser-supplement basis, while never
    # recording a non-certification or amended-passage outcome.
    assert "令和7年第4回定例会" in text
    assert "認定" in text
    assert "定第195号議案" in text
    assert "2026年3月19日" in text
    assert "原案可決（賛成多数）" in text
    assert "定第56号議案" in text
    assert "2025年12月2日" in text
    assert "認定（賛成多数）" in text
    assert "実ブラウザによる補完調査" in text
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text
    # The formerly open questions about the bill numbers and vote
    # dates are resolved.
    assert "未特定" not in text
    assert "一般会計予算の個別の議案番号と議決日の特定" not in text
    assert "認定の議決日の特定" not in text
    packets = {
        packet["id"]: packet
        for packet in candidate()["candidate_package"]["evidence_packets"]
    }
    assert packets["evidence-kagoshima-city-2026-total-expenditure"]["open_questions"] == [
        "当初予算書の歳入歳出予算事項別明細書の款別合計との最終突合。"
    ]
    assert packets["evidence-kagoshima-city-2024-total-revenue"]["open_questions"] == [
        "決算事項別明細書の款別合計との最終突合。"
    ]


def test_kagoshima_candidate_does_not_link_settlement_to_plan_by_total() -> None:
    linkage = plan_record("kagoshima-fy2024-settlement-linkage")
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "前期基本計画" in linkage["statement"]
    assert "not_assessable" in linkage["statement"]


def test_kagoshima_candidate_keeps_granular_and_reconciliation_depth_deferred() -> None:
    deferred = {item["id"] for item in candidate()["deferred_depth"]}
    assert deferred == {
        "current-plan-granular-policy-and-indicator-linkage",
        "fiscal-detail-reconciliation",
        "plan-transition-version-depth",
        "policy-outcome-causal-and-cross-city-comparability",
    }
