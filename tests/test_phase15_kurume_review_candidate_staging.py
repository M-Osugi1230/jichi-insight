import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/kurume-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/kurume-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_candidate():
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def test_kurume_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = load_candidate()

    assert candidate["candidate_id"] == "kurume-phase15-review-candidate"
    assert candidate["official_code"] == "402036"
    assert candidate["name_ja"] == "久留米市"
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


def test_kurume_candidate_catalog_matches_phase14_inventory() -> None:
    candidate = load_candidate()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    sources = candidate["candidate_package"]["source_catalog"]["sources"]

    inventory_by_id = {source["id"]: source for source in inventory["sources"]}
    assert len(sources) == len(inventory_by_id) == 4
    for source in sources:
        assert source["id"] in inventory_by_id
        assert source["official_url"] == inventory_by_id[source["id"]]["official_url"]
        assert source["official_url"].startswith("https://www.city.kurume.fukuoka.jp/")
        assert source["verification_status"].startswith("primary_source_live_verified")


def test_kurume_candidate_plan_records_keep_framework_and_transition() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["plan_review"]["records"]
    }

    assert set(records) == {
        "kurume-current-plan-period",
        "kurume-current-policy-structure",
        "kurume-progress-governance-framework",
        "kurume-plan-transition",
        "kurume-fy2024-settlement-linkage",
    }
    period = records["kurume-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["evidence_role"] == "current_plan_identity"
    assert "久留米未来デザイン計画2035" in period["statement"]
    assert "2026年度〜2035年度" in period["statement"]
    assert "前期5年間、2026年度〜2030年度" in period["statement"]
    assert "後期5年間、2031年度〜2035年度" in period["statement"]
    assert "verified_fixed_period" in period["statement"]
    structure = records["kurume-current-policy-structure"]
    assert structure["decision"] == "needs_review"
    assert "優しさ 豊かさ 輝き あふれるまち" in structure["statement"]
    assert "10の基本目標" in structure["statement"]
    assert "33の施策" in structure["statement"]
    governance = records["kurume-progress-governance-framework"]
    assert governance["decision"] == "needs_review"
    assert "政策評価制度" in governance["statement"]
    assert "まちづくり評価" in governance["statement"]
    assert "事業評価" in governance["statement"]
    transition = records["kurume-plan-transition"]
    assert transition["decision"] == "needs_review"
    assert transition["evidence_role"] == "plan_transition"
    assert "久留米市新総合計画" in transition["statement"]
    assert "第4次（令和2年度〜令和7年度）" in transition["statement"]
    linkage = records["kurume-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "第4次基本計画期間" in linkage["statement"]
    assert "認定第1号" in linkage["statement"]


def test_kurume_candidate_policy_structure_keeps_ten_goals() -> None:
    candidate = load_candidate()
    plan = candidate["candidate_package"]["policy_structure"]["current_plan"]

    assert plan["title"].startswith("久留米未来デザイン計画2035")
    assert plan["vision"] == "優しさ 豊かさ 輝き あふれるまち"
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2035
    assert plan["period_status"] == "verified_fixed_period"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "基本目標1「安全・安心な暮らし」を守る",
        "基本目標2「自分らしく輝き続けられる社会」をつくる",
        "基本目標3「つながり支え合う地域」をつくる",
        "基本目標4「未来を創り担うひと」を育む",
        "基本目標5「楽しく心豊かな暮らし」を実現する",
        "基本目標6「魅力ある快適な都市」をデザインする",
        "基本目標7「豊かな自然と恵まれた環境」を次世代につなぐ",
        "基本目標8「新たな価値、地域の稼ぐ力」を生み出す",
        "基本目標9「久留米ならではの魅力」を高め広げる",
        "基本目標10「スマートな行財政運営」に転換する",
    ]
    measures = [measure for field in fields for measure in field["measures"]]
    assert len(measures) == 33
    assert measures[0] == "防災"
    assert measures[-1] == "行財政"
    principles = " ".join(plan["management_principles"])
    assert "久留米市新総合計画" in principles
    assert "政策評価制度" in principles
    assert "流用しない" in principles


def test_kurume_candidate_fiscal_records_match_primary_sources() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }

    budget = records["jp-local-402036-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 167_760_000_000
    assert budget["review_status"] == "needs_review"
    assert "第45号議案" in budget["note"]
    assert "167,760,000千円" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "2026年6月26日" in budget["note"]
    assert "暫定予算" in budget["note"]
    assert "70,670,000千円" in budget["note"]
    assert "千円単位" in budget["note"]

    revenue = records["jp-local-402036-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 151_712_648_320
    assert "認定第1号" in revenue["note"]
    assert "151,712,648,320円" in revenue["note"]
    assert "2025年10月15日" in revenue["note"]
    assert "普通会計ベース" in revenue["note"]
    assert "第4次基本計画期間内" in revenue["note"]

    expenditure = records["jp-local-402036-fiscal-2024-total-expenditure"]
    assert expenditure["stage"] == "settlement"
    assert expenditure["amount_yen"] == 150_433_124_636
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1_279_523_684


def test_kurume_candidate_keeps_real_balance_from_settlement_summary() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }
    note = records["jp-local-402036-fiscal-2024-total-expenditure"]["note"]

    assert "実質収支は1,011,356千円" in note
    assert "翌年度へ繰り越すべき財源268,167千円" in note
    assert "千円単位の公表値のまま記録する" in note


def test_kurume_candidate_certification_was_directly_confirmed() -> None:
    candidate = load_candidate()
    text = json.dumps(candidate, ensure_ascii=False)

    assert "認定第1号" in text
    assert "2025年10月15日" in text
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_kurume_candidate_budget_vote_wording_is_recorded_as_published() -> None:
    candidate = load_candidate()
    packets = {
        packet["id"]: packet
        for packet in candidate["candidate_package"]["evidence_packets"]
    }
    claim = packets["evidence-kurume-city-2026-total-expenditure"]["claims"][0]

    assert claim["decision"] == "needs_review"
    assert "第45号議案" in claim["statement"]
    assert "原案可決" in claim["statement"]
    assert "2026年6月26日" in claim["statement"]
    assert "第6号議案" in claim["statement"]
    assert "70,670,000千円" in claim["statement"]


def test_kurume_candidate_does_not_use_ordinary_account_aggregates() -> None:
    candidate = load_candidate()
    sources = {
        source["id"]: source
        for source in candidate["candidate_package"]["source_catalog"]["sources"]
    }

    boundary = sources["kurume-settlement-2024"]["use_boundary"]
    assert "普通会計ベース" in boundary
    assert "混同しない" in boundary
    location = sources["kurume-settlement-2024"]["evidence_location"]
    assert "決算書" in location
    assert "認定第1号" in location


def test_kurume_candidate_evidence_packets_cover_fiscal_records() -> None:
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


def test_kurume_candidate_progress_review_stays_staging() -> None:
    candidate = load_candidate()
    progress = candidate["candidate_package"]["progress_review"]

    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "事業計画" in framework["title"]
    assert "政策評価制度" in framework["evaluation_structure"]
    assert "まちづくり評価" in framework["evaluation_structure"]


def test_kurume_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    assert queue["summary"]["reviewed_complete_count"] == 65
    assert queue["summary"]["pending_record_review_count"] == 2
    assert queue["summary"]["next_official_code"] == "462012"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "402036"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/kurume_phase15_completion.json"
