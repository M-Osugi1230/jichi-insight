import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/miyazaki-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/miyazaki-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_candidate():
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def test_miyazaki_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = load_candidate()

    assert candidate["candidate_id"] == "miyazaki-phase15-review-candidate"
    assert candidate["official_code"] == "452017"
    assert candidate["name_ja"] == "宮崎市"
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


def test_miyazaki_candidate_catalog_matches_phase14_inventory() -> None:
    candidate = load_candidate()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    sources = candidate["candidate_package"]["source_catalog"]["sources"]

    inventory_by_id = {source["id"]: source for source in inventory["sources"]}
    assert len(sources) == len(inventory_by_id) == 4
    for source in sources:
        assert source["id"] in inventory_by_id
        assert source["official_url"] == inventory_by_id[source["id"]]["official_url"]
        assert source["official_url"].startswith("https://www.city.miyazaki.miyazaki.jp/")
        assert source["verification_status"].startswith("primary_source_live_verified")


def test_miyazaki_candidate_plan_records_keep_framework_and_transition() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["plan_review"]["records"]
    }

    assert set(records) == {
        "miyazaki-current-plan-period",
        "miyazaki-current-policy-structure",
        "miyazaki-progress-governance-framework",
        "miyazaki-plan-transition",
        "miyazaki-fy2024-settlement-linkage",
    }
    period = records["miyazaki-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["evidence_role"] == "current_plan_identity"
    assert "第六次宮崎市総合計画" in period["statement"]
    assert "2025年度〜2034年度の10年間" in period["statement"]
    assert "基本構想" in period["statement"]
    assert "基本計画" in period["statement"]
    assert "verified_fixed_period" in period["statement"]
    structure = records["miyazaki-current-policy-structure"]
    assert structure["decision"] == "needs_review"
    assert "OPEN CITY MIYAZAKI" in structure["statement"]
    assert "政策1 経済成長をめざすまちづくり" in structure["statement"]
    assert "政策6 持続可能なまちづくり" in structure["statement"]
    governance = records["miyazaki-progress-governance-framework"]
    assert governance["decision"] == "needs_review"
    assert "施策評価" in governance["statement"]
    assert "内部評価及び外部評価" in governance["statement"]
    transition = records["miyazaki-plan-transition"]
    assert transition["decision"] == "needs_review"
    assert transition["evidence_role"] == "plan_transition"
    assert "第五次宮崎市総合計画" in transition["statement"]
    assert "2018年度" in transition["statement"]
    linkage = records["miyazaki-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "第五次宮崎市総合計画" in linkage["statement"]
    assert "第109号" in linkage["statement"]
    assert "認定されている" in linkage["statement"]
    assert "2025年10月7日" in linkage["statement"]


def test_miyazaki_candidate_policy_structure_keeps_six_fields() -> None:
    candidate = load_candidate()
    plan = candidate["candidate_package"]["policy_structure"]["current_plan"]

    assert plan["title"].startswith("第六次宮崎市総合計画")
    assert plan["vision"] == "挑戦し、成長する 開かれたまち ～ OPEN CITY MIYAZAKI ～"
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2034
    assert plan["period_status"] == "verified_fixed_period"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "経済成長をめざすまちづくり",
        "経済を支えるまちづくり",
        "市民の健康を守り、医療・福祉が充実したまちづくり",
        "支え合い、ともに生きるまちづくり",
        "次世代を育むまちづくり",
        "持続可能なまちづくり",
    ]
    principles = " ".join(plan["management_principles"])
    assert "基本計画" in principles
    assert "施策評価" in principles
    assert "流用しない" in principles


def test_miyazaki_candidate_fiscal_records_match_primary_sources() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }

    budget = records["jp-local-452017-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 204_000_000_000
    assert budget["review_status"] == "needs_review"
    assert "市長提出議案第2号" in budget["note"]
    assert "204,000,000千円" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "2026年3月13日" in budget["note"]
    assert "千円単位" in budget["note"]
    assert "当初予算案の概要" in budget["note"]

    revenue = records["jp-local-452017-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 206_745_695_721
    assert "第109号" in revenue["note"]
    assert "206,745,695,721円" in revenue["note"]
    assert "認定された" in revenue["note"]
    assert "2025年10月7日" in revenue["note"]
    assert "継続審査" in revenue["note"]
    assert "普通会計ベース" in revenue["note"]
    assert "第五次宮崎市総合計画" in revenue["note"]

    expenditure = records["jp-local-452017-fiscal-2024-total-expenditure"]
    assert expenditure["stage"] == "settlement"
    assert expenditure["amount_yen"] == 201_205_711_288
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 5_539_984_433


def test_miyazaki_candidate_keeps_difference_and_defers_real_balance() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }
    note = records["jp-local-452017-fiscal-2024-total-expenditure"]["note"]

    # The settlement book prints the balance of revenue over expenditure
    # (5,539,984,433 yen), which the candidate records, while the real
    # balance from the dedicated schedule stays unrecorded because that
    # schedule itself could not be checked (the audit opinion is
    # published as an image-only PDF).
    assert "差引残額は5,539,984,433円" in note
    assert "6,301,182,683円" in note
    assert "実質収支に関する調書そのものの値を確認できていないため記録しない" in note


def test_miyazaki_candidate_certification_outcome_confirmed() -> None:
    candidate = load_candidate()
    text = json.dumps(candidate, ensure_ascii=False)

    # The FY2024 settlement bill (No. 109) was carried over for
    # continued review at the Reiwa 7 4th regular session and then
    # certified at the Reiwa 7 5th extraordinary session, both
    # confirmed directly in the council's official voting results, so
    # the candidate records that outcome and never records a
    # non-certification or an amended-passage outcome.
    assert "第109号" in text
    assert "継続審査" in text
    assert "認定された" in text
    assert "2025年10月7日" in text
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_miyazaki_candidate_budget_vote_wording_is_recorded_as_published() -> None:
    candidate = load_candidate()
    packets = {
        packet["id"]: packet
        for packet in candidate["candidate_package"]["evidence_packets"]
    }
    claim = packets["evidence-miyazaki-city-2026-total-expenditure"]["claims"][0]

    assert claim["decision"] == "needs_review"
    assert "市長提出議案第2号" in claim["statement"]
    assert "原案可決" in claim["statement"]
    assert "2026年3月13日" in claim["statement"]
    assert "204,000,000千円" in claim["statement"]
    assert "当初予算案の概要" in claim["statement"]


def test_miyazaki_candidate_does_not_use_ordinary_account_aggregates() -> None:
    candidate = load_candidate()
    sources = {
        source["id"]: source
        for source in candidate["candidate_package"]["source_catalog"]["sources"]
    }

    boundary = sources["miyazaki-settlement-audit-2024"]["use_boundary"]
    assert "普通会計ベース" in boundary
    assert "混同しない" in boundary
    location = sources["miyazaki-settlement-audit-2024"]["evidence_location"]
    assert "決算書" in location
    assert "第109号" in location


def test_miyazaki_candidate_evidence_packets_cover_fiscal_records() -> None:
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


def test_miyazaki_candidate_progress_review_stays_staging() -> None:
    candidate = load_candidate()
    progress = candidate["candidate_package"]["progress_review"]

    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "施策評価" in framework["title"]
    assert "内部評価及び外部評価" in framework["evaluation_structure"]
    assert "令和8年度（令和7年度分）の施策評価" in framework["evaluation_structure"]


def test_miyazaki_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    assert queue["summary"]["reviewed_complete_count"] == 69
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "452017"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/miyazaki_phase15_completion.json"
