import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/naha-city/review_candidate.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
INVENTORY = ROOT / "data/indexed/naha-city/source_inventory.json"


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


def test_naha_candidate_is_prepared_with_delegated_review_approved() -> None:
    data = candidate()
    assert data["candidate_id"] == "naha-phase15-review-candidate"
    assert data["official_code"] == "472018"
    assert data["name_ja"] == "那覇市"
    assert data["package_state"] == "prepared"
    assert data["status"] == "review_candidate"
    assert data["human_review"]["status"] == "approved"
    assert data["human_review"]["reviewed_at"] == "2026-11-17"
    note = data["human_review"]["reviewer_note"]
    assert "委任" in note
    assert "レビューはあなたがやってください" in note
    assert "所有者本人が一次資料を直接レビューしたものではない" in note
    assert data["publication"]["eligible"] is False


def test_naha_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["target_count"] == 68
    assert summary["reviewed_complete_count"] == 68
    assert summary["pending_record_review_count"] == 0
    assert summary["next_official_code"] is None
    entry = next(item for item in queue["execution_queue"] if item["official_code"] == "472018")
    assert entry["sequence"] == 67
    assert entry["name_ja"] == "那覇市"
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/naha_phase15_completion.json"


def test_naha_candidate_sources_match_phase14_inventory() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    inventory_sources = {
        source["id"]: source["official_url"] for source in inventory["sources"]
    }
    catalog_sources = candidate()["candidate_package"]["source_catalog"]["sources"]
    assert len(catalog_sources) == 5
    for source in catalog_sources:
        assert source["id"] in inventory_sources
        assert source["official_url"] == inventory_sources[source["id"]]
        assert source["official_url"].startswith("https://www.city.naha.okinawa.jp/")


def test_naha_candidate_records_current_plan_and_transition() -> None:
    current = candidate()["candidate_package"]["policy_structure"]["current_plan"]
    assert "第5次那覇市総合計画" in current["title"]
    assert current["start_fiscal_year"] == 2018
    assert current["end_fiscal_year"] == 2027
    assert current["period_status"] == "transition_or_unresolved"
    assert current["vision"] == (
        "なはで暮らし、働き、育てよう！笑顔広がる元気なまちNAHA みんなでつなごう市民力"
    )
    assert len(current["policy_fields"]) == 5
    assert all(field["measures"] == [] for field in current["policy_fields"])
    transition = plan_record("naha-plan-transition")
    assert transition["decision"] == "needs_review"
    assert "第6次那覇市総合計画" in transition["statement"]
    assert "策定が開始" in transition["statement"]


def test_naha_candidate_records_fy2026_budget_at_published_precision() -> None:
    budget = fiscal_record("jp-local-472018-fiscal-2026-total-expenditure")
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 185_220_000_000
    assert budget["value_status"] == "available"
    assert budget["review_status"] == "needs_review"
    assert "185,220,000千円" in budget["note"]
    assert "議案第22号" in budget["note"]
    assert "2026年3月17日" in budget["note"]
    assert "原案可決（賛成多数）" in budget["note"]
    assert "千円単位" in budget["note"]


def test_naha_candidate_records_fy2024_settlement_at_published_precision() -> None:
    revenue = fiscal_record("jp-local-472018-fiscal-2024-total-revenue")
    expenditure = fiscal_record("jp-local-472018-fiscal-2024-total-expenditure")
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 185_140_399_109
    assert expenditure["amount_yen"] == 178_147_629_486
    assert revenue["value_status"] == "available"
    assert expenditure["value_status"] == "available"
    assert "185,140,399,109円" in revenue["note"]
    assert "認定第1号" in revenue["note"]
    assert "2025年10月8日" in revenue["note"]
    assert "認定された" in revenue["note"]
    assert "実ブラウザによる補完調査" in revenue["note"]
    assert "178,147,629,486円" in expenditure["note"]
    assert "6,992,769,623円" in expenditure["note"]
    assert "5,963,603,975円" in expenditure["note"]


def test_naha_candidate_certification_outcome_confirmed() -> None:
    text = candidate_text()

    # The FY2024 settlement was submitted to the September 2025 session
    # as 認定第1号; a supplementary live-browser investigation then
    # confirmed from the council's official September 2025 session page
    # that it was certified on 2025-10-08 within that session (it was
    # not carried over to the November session), so the candidate
    # records that certification and its browser-supplement basis,
    # while never recording a non-certification outcome.
    assert "認定第1号" in text
    assert "2025年10月8日" in text
    assert "認定された" in text
    assert "実ブラウザによる補完調査" in text
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text
    # The formerly open question about the certification outcome is resolved.
    assert "認定の成否と議決日の特定" not in text
    packets = {
        packet["id"]: packet
        for packet in candidate()["candidate_package"]["evidence_packets"]
    }
    revenue_packet = packets["evidence-naha-city-2024-total-revenue"]
    assert revenue_packet["open_questions"] == [
        "決算事項別明細書の款別合計との最終突合。",
        "監査委員の決算審査意見書の内容精査。",
    ]


def test_naha_candidate_does_not_link_settlement_to_plan_by_total() -> None:
    linkage = plan_record("naha-fy2024-settlement-linkage")
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "第5次那覇市総合計画" in linkage["statement"]
    assert "not_assessable" in linkage["statement"]
    assert "認定されている" in linkage["statement"]


def test_naha_candidate_keeps_granular_and_reconciliation_depth_deferred() -> None:
    deferred = {item["id"] for item in candidate()["deferred_depth"]}
    assert deferred == {
        "current-plan-granular-policy-and-indicator-linkage",
        "fiscal-detail-reconciliation",
        "plan-transition-version-depth",
        "policy-outcome-causal-and-cross-city-comparability",
    }
