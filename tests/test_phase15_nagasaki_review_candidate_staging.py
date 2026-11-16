import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/nagasaki-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/nagasaki-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_candidate():
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def test_nagasaki_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = load_candidate()

    assert candidate["candidate_id"] == "nagasaki-phase15-review-candidate"
    assert candidate["official_code"] == "422010"
    assert candidate["name_ja"] == "長崎市"
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


def test_nagasaki_candidate_catalog_matches_phase14_inventory() -> None:
    candidate = load_candidate()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    sources = candidate["candidate_package"]["source_catalog"]["sources"]

    inventory_by_id = {source["id"]: source for source in inventory["sources"]}
    assert len(sources) == len(inventory_by_id) == 5
    for source in sources:
        assert source["id"] in inventory_by_id
        assert source["official_url"] == inventory_by_id[source["id"]]["official_url"]
        assert source["official_url"].startswith("https://www.city.nagasaki.lg.jp/")
        assert source["verification_status"].startswith("primary_source_live_verified")


def test_nagasaki_candidate_plan_records_keep_framework_and_transition() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["plan_review"]["records"]
    }

    assert set(records) == {
        "nagasaki-current-plan-period",
        "nagasaki-current-policy-structure",
        "nagasaki-progress-governance-framework",
        "nagasaki-plan-transition",
        "nagasaki-fy2024-settlement-linkage",
    }
    period = records["nagasaki-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["evidence_role"] == "current_plan_identity"
    assert "第五次総合計画" in period["statement"]
    assert "2022年度〜2030年度の9年間" in period["statement"]
    assert "前期2022年度〜2025年度の4年間" in period["statement"]
    assert "後期2026年度〜2030年度の5年間" in period["statement"]
    assert "verified_fixed_period" in period["statement"]
    structure = records["nagasaki-current-policy-structure"]
    assert structure["decision"] == "needs_review"
    assert "個性輝く世界都市" in structure["statement"]
    assert "8つのまちづくりの方針" in structure["statement"]
    assert "27の施策" in structure["statement"]
    governance = records["nagasaki-progress-governance-framework"]
    assert governance["decision"] == "needs_review"
    assert "毎年度評価" in governance["statement"]
    assert "長崎市総合計画審議会" in governance["statement"]
    assert "令和8年度分から" in governance["statement"]
    transition = records["nagasaki-plan-transition"]
    assert transition["decision"] == "needs_review"
    assert transition["evidence_role"] == "plan_transition"
    assert "前期基本計画（2022年度〜2025年度の4年間" in transition["statement"]
    assert "後期基本計画（2026年度〜2030年度の5年間" in transition["statement"]
    linkage = records["nagasaki-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "前期基本計画" in linkage["statement"]
    assert "第180号議案" in linkage["statement"]


def test_nagasaki_candidate_policy_structure_keeps_eight_fields() -> None:
    candidate = load_candidate()
    plan = candidate["candidate_package"]["policy_structure"]["current_plan"]

    assert plan["title"].startswith("長崎市第五次総合計画")
    assert plan["vision"] == "個性輝く世界都市"
    assert plan["start_fiscal_year"] == 2022
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "verified_fixed_period"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "方針A 独自の歴史・文化を活かし、多様な交流と満足を生み出すまち",
        "方針B 平和を愛し、平和の文化を育むまち",
        "方針C 人や企業に選ばれ、産業が進化し続けるまち",
        "方針D 環境と調和した持続可能なまち",
        "方針E だれもが安全安心で快適に暮らし続けられるまち",
        "方針F みんなで支え合い、だれもが健康にいきいきと暮らせるまち",
        "方針G 未来を創る人を育み、だれもが学び、楽しみ続けられるまち",
        "方針H 参画と協働によるまちづくりと確かな行政経営を進めるまち",
    ]
    principles = " ".join(plan["management_principles"])
    assert "前期基本計画" in principles
    assert "毎年度評価" in principles
    assert "流用しない" in principles


def test_nagasaki_candidate_fiscal_records_match_primary_sources() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }

    budget = records["jp-local-422010-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 227_560_000_000
    assert budget["review_status"] == "needs_review"
    assert "第13号議案" in budget["note"]
    assert "227,560,000千円" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "2026年3月12日" in budget["note"]
    assert "千円単位" in budget["note"]

    revenue = records["jp-local-422010-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 237_840_810_000
    assert "第180号議案" in revenue["note"]
    assert "2,378億4,081万円" in revenue["note"]
    assert "2025年11月25日" in revenue["note"]
    assert "普通会計ベース" in revenue["note"]
    assert "前期基本計画" in revenue["note"]

    expenditure = records["jp-local-422010-fiscal-2024-total-expenditure"]
    assert expenditure["stage"] == "settlement"
    assert expenditure["amount_yen"] == 234_412_110_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 3_428_700_000


def test_nagasaki_candidate_keeps_real_balance_from_audit_opinion() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }
    note = records["jp-local-422010-fiscal-2024-total-expenditure"]["note"]

    assert "実質収支は11億3,830万円" in note
    assert "約22億9,040万円" in note
    assert "万円単位の公表値のまま記録する" in note


def test_nagasaki_candidate_certification_was_directly_confirmed() -> None:
    candidate = load_candidate()
    text = json.dumps(candidate, ensure_ascii=False)

    assert "第180号議案" in text
    assert "2025年11月25日" in text
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_nagasaki_candidate_budget_vote_wording_is_recorded_as_published() -> None:
    candidate = load_candidate()
    packets = {
        packet["id"]: packet
        for packet in candidate["candidate_package"]["evidence_packets"]
    }
    claim = packets["evidence-nagasaki-city-2026-total-expenditure"]["claims"][0]

    assert claim["decision"] == "needs_review"
    assert "第13号議案" in claim["statement"]
    assert "原案可決" in claim["statement"]
    assert "2026年3月12日" in claim["statement"]
    assert "227,560,000千円" in claim["statement"]


def test_nagasaki_candidate_does_not_use_ordinary_account_aggregates() -> None:
    candidate = load_candidate()
    sources = {
        source["id"]: source
        for source in candidate["candidate_package"]["source_catalog"]["sources"]
    }

    boundary = sources["nagasaki-settlement-2024"]["use_boundary"]
    assert "普通会計ベース" in boundary
    assert "混同しない" in boundary
    location = sources["nagasaki-settlement-2024"]["evidence_location"]
    assert "決算審査意見書" in location
    assert "第180号議案" in location


def test_nagasaki_candidate_evidence_packets_cover_fiscal_records() -> None:
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


def test_nagasaki_candidate_progress_review_stays_staging() -> None:
    candidate = load_candidate()
    progress = candidate["candidate_package"]["progress_review"]

    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "実施計画" in framework["title"]
    assert "毎年度評価" in framework["evaluation_structure"]
    assert "長崎市総合計画審議会" in framework["evaluation_structure"]


def test_nagasaki_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    assert queue["summary"]["reviewed_complete_count"] == 64
    assert queue["summary"]["pending_record_review_count"] == 3
    assert queue["summary"]["next_official_code"] == "452017"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "422010"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/nagasaki_phase15_completion.json"
