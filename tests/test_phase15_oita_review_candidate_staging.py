import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/oita-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/oita-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_candidate():
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def test_oita_candidate_is_prepared_and_unpublished() -> None:
    candidate = load_candidate()

    assert candidate["candidate_id"] == "oita-phase15-review-candidate"
    assert candidate["official_code"] == "442011"
    assert candidate["name_ja"] == "大分市"
    assert candidate["phase"] == 15
    assert candidate["schema_version"] == 1
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["publication"]["eligible"] is False
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["reviewed_at"] is None
    assert candidate["human_review"]["reviewer_note"] is None


def test_oita_candidate_catalog_matches_phase14_inventory() -> None:
    candidate = load_candidate()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    sources = candidate["candidate_package"]["source_catalog"]["sources"]

    inventory_by_id = {source["id"]: source for source in inventory["sources"]}
    assert len(sources) == len(inventory_by_id) == 4
    for source in sources:
        assert source["id"] in inventory_by_id
        assert source["official_url"] == inventory_by_id[source["id"]]["official_url"]
        assert source["official_url"].startswith("https://www.city.oita.oita.jp/")
        assert source["verification_status"].startswith("primary_source_live_verified")


def test_oita_candidate_plan_records_keep_framework_and_transition() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["plan_review"]["records"]
    }

    assert set(records) == {
        "oita-current-plan-period",
        "oita-current-policy-structure",
        "oita-progress-governance-framework",
        "oita-plan-transition",
        "oita-fy2024-settlement-linkage",
    }
    period = records["oita-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["evidence_role"] == "current_plan_identity"
    assert "未来へつなぐ おおいたビジョン2034" in period["statement"]
    assert "2025年度〜2034年度の10年間" in period["statement"]
    assert "第1次基本計画（2025年度〜2029年度" in period["statement"]
    assert "第2次基本計画（2030年度〜2034年度" in period["statement"]
    assert "verified_fixed_period" in period["statement"]
    structure = records["oita-current-policy-structure"]
    assert structure["decision"] == "needs_review"
    assert "実感できるまち OITA" in structure["statement"]
    assert "豊かな個性をはぐくみ、ともに成長できるまち" in structure["statement"]
    assert "政策19 安定した生活基盤の形成" in structure["statement"]
    governance = records["oita-progress-governance-framework"]
    assert governance["decision"] == "needs_review"
    assert "行政評価" in governance["statement"]
    assert "114指標" in governance["statement"]
    transition = records["oita-plan-transition"]
    assert transition["decision"] == "needs_review"
    assert transition["evidence_role"] == "plan_transition"
    assert "おおいた創造ビジョン2024" in transition["statement"]
    assert "2016年度〜2024年度" in transition["statement"]
    linkage = records["oita-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "おおいた創造ビジョン2024" in linkage["statement"]
    assert "議第106号" in linkage["statement"]
    assert "認定されている" in linkage["statement"]


def test_oita_candidate_policy_structure_keeps_three_fields() -> None:
    candidate = load_candidate()
    plan = candidate["candidate_package"]["policy_structure"]["current_plan"]

    assert plan["title"].startswith("大分市総合計画「未来へつなぐ おおいたビジョン2034」")
    assert plan["vision"] == "誰もが\"幸せ\"を実感できるまち OITA"
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2034
    assert plan["period_status"] == "verified_fixed_period"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "豊かな個性をはぐくみ、ともに成長できるまち",
        "共生する社会を実現し、安心して暮らせるまち",
        "新たな価値を創造し、未来に挑戦できるまち",
    ]
    principles = " ".join(plan["management_principles"])
    assert "第1次基本計画" in principles
    assert "行政評価" in principles
    assert "流用しない" in principles


def test_oita_candidate_fiscal_records_match_primary_sources() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }

    budget = records["jp-local-442011-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 223_255_000_000
    assert budget["review_status"] == "needs_review"
    assert "議第1号" in budget["note"]
    assert "223,255,000千円" in budget["note"]
    assert "「可決」" in budget["note"]
    assert "2026年3月26日" in budget["note"]
    assert "千円単位" in budget["note"]
    assert "当初予算書" in budget["note"]

    revenue = records["jp-local-442011-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 226_470_701_000
    assert "議第106号" in revenue["note"]
    assert "226,470,701千円" in revenue["note"]
    assert "認定された" in revenue["note"]
    assert "議決日そのものは" in revenue["note"]
    assert "未確認" in revenue["note"]
    assert "普通会計ベース" in revenue["note"]
    assert "おおいた創造ビジョン2024" in revenue["note"]

    expenditure = records["jp-local-442011-fiscal-2024-total-expenditure"]
    assert expenditure["stage"] == "settlement"
    assert expenditure["amount_yen"] == 220_402_983_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 6_067_718_000


def test_oita_candidate_keeps_real_balance_from_settlement_summary() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }
    note = records["jp-local-442011-fiscal-2024-total-expenditure"]["note"]

    assert "実質収支は5,226,170千円" in note
    assert "841,548千円" in note
    assert "千円単位で印字された値のまま記録する" in note


def test_oita_candidate_certification_confirmed_but_vote_date_unconfirmed() -> None:
    candidate = load_candidate()
    text = json.dumps(candidate, ensure_ascii=False)

    # The FY2024 settlement bill (議第106号) was certified at the
    # Reiwa 7 3rd regular session, as stated on the Finance Division's
    # official page and the council's official committee schedule.
    # The exact vote date could not be confirmed from text-accessible
    # official sources, so it stays an open question, and the candidate
    # must never claim the settlement was rejected or amended.
    assert "議第106号" in text
    assert "認定された" in text
    assert "議決日そのものは" in text
    assert "未確認" in text
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_oita_candidate_budget_vote_wording_is_recorded_as_published() -> None:
    candidate = load_candidate()
    packets = {
        packet["id"]: packet
        for packet in candidate["candidate_package"]["evidence_packets"]
    }
    claim = packets["evidence-oita-city-2026-total-expenditure"]["claims"][0]

    assert claim["decision"] == "needs_review"
    assert "議第1号" in claim["statement"]
    assert "「可決」" in claim["statement"]
    assert "2026年3月26日" in claim["statement"]
    assert "223,255,000千円" in claim["statement"]
    assert "当初予算書" in claim["statement"]


def test_oita_candidate_does_not_use_ordinary_account_aggregates() -> None:
    candidate = load_candidate()
    sources = {
        source["id"]: source
        for source in candidate["candidate_package"]["source_catalog"]["sources"]
    }

    boundary = sources["oita-settlement-2024"]["use_boundary"]
    assert "普通会計ベース" in boundary
    assert "混同しない" in boundary
    location = sources["oita-settlement-2024"]["evidence_location"]
    assert "決算概要説明書" in location
    assert "議第106号" in location


def test_oita_candidate_evidence_packets_cover_fiscal_records() -> None:
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


def test_oita_candidate_progress_review_stays_staging() -> None:
    candidate = load_candidate()
    progress = candidate["candidate_package"]["progress_review"]

    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "114指標" in framework["title"]
    assert "行政評価" in framework["evaluation_structure"]
    assert "令和7年度末進ちょく状況" in framework["evaluation_structure"]


def test_oita_candidate_does_not_change_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    assert queue["summary"]["reviewed_complete_count"] == 63
    assert queue["summary"]["pending_record_review_count"] == 4
    assert queue["summary"]["next_official_code"] == "442011"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "442011"
    )
    assert entry["status"] == "pending_record_review"
    assert entry["completion_path"] is None
