import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/kochi-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/kochi-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_candidate():
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def test_kochi_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = load_candidate()

    assert candidate["candidate_id"] == "kochi-phase15-review-candidate"
    assert candidate["official_code"] == "392014"
    assert candidate["name_ja"] == "高知市"
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


def test_kochi_candidate_catalog_matches_phase14_inventory() -> None:
    candidate = load_candidate()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    sources = candidate["candidate_package"]["source_catalog"]["sources"]

    inventory_by_id = {source["id"]: source for source in inventory["sources"]}
    assert len(sources) == len(inventory_by_id) == 5
    for source in sources:
        assert source["id"] in inventory_by_id
        assert source["official_url"] == inventory_by_id[source["id"]]["official_url"]
        assert source["official_url"].startswith("https://www.city.kochi.kochi.jp/")
        assert source["verification_status"].startswith("primary_source_live_verified")


def test_kochi_candidate_plan_records_keep_framework_and_transition() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["plan_review"]["records"]
    }

    assert set(records) == {
        "kochi-current-plan-period",
        "kochi-current-policy-structure",
        "kochi-progress-governance-framework",
        "kochi-plan-transition",
        "kochi-fy2024-settlement-linkage",
    }
    period = records["kochi-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["evidence_role"] == "current_plan_identity"
    assert "2011高知市総合計画" in period["statement"]
    assert "2011年度～2030年度" in period["statement"]
    assert "後期2021年度～2030年度" in period["statement"]
    assert "第2次2024年度～2026年度" in period["statement"]
    assert "transition_or_unresolved" in period["statement"]
    structure = records["kochi-current-policy-structure"]
    assert structure["decision"] == "needs_review"
    assert "森・里・海と人の環" in structure["statement"]
    assert "6つの環" in structure["statement"]
    assert "14の政策" in structure["statement"]
    assert "維新・創生 高知市" in structure["statement"]
    governance = records["kochi-progress-governance-framework"]
    assert governance["decision"] == "needs_review"
    assert "事務事業評価" in governance["statement"]
    assert "PDCA" in governance["statement"]
    transition = records["kochi-plan-transition"]
    assert transition["decision"] == "needs_review"
    assert transition["evidence_role"] == "plan_transition"
    assert "高知市未来ビジョン（仮称）" in transition["statement"]
    assert "令和8年度末" in transition["statement"]
    assert "令和9年度～令和16年度" in transition["statement"]
    linkage = records["kochi-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "後期基本計画期間" in linkage["statement"]
    assert "市第165号" in linkage["statement"]


def test_kochi_candidate_policy_structure_keeps_six_rings_and_fourteen_policies() -> None:
    candidate = load_candidate()
    plan = candidate["candidate_package"]["policy_structure"]["current_plan"]

    assert plan["title"].startswith("2011高知市総合計画")
    assert plan["vision"] == "森・里・海と人の環 自由と創造の共生都市 高知"
    assert plan["start_fiscal_year"] == 2011
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "transition_or_unresolved"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "共生の環",
        "安心の環",
        "育みの環",
        "地産の環",
        "まちの環",
        "自立の環",
    ]
    measures = [measure for field in fields for measure in field["measures"]]
    assert len(measures) == 14
    assert measures[0] == "政策1 豊かな自然に親しみ、自然と共生するまち"
    assert measures[-1] == "政策14 多様な交流や、新たな人の流れが生まれ、自立したまち"
    principles = " ".join(plan["management_principles"])
    assert "令和8年度末" in principles
    assert "事務事業評価" in principles
    assert "流用しない" in principles


def test_kochi_candidate_fiscal_records_match_primary_sources() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }

    budget = records["jp-local-392014-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 168_400_000_000
    assert budget["review_status"] == "needs_review"
    assert "市第4号" in budget["note"]
    assert "168,400,000千円" in budget["note"]
    assert "可決（多数）" in budget["note"]
    assert "2026年3月26日" in budget["note"]
    assert "千円単位" in budget["note"]

    revenue = records["jp-local-392014-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 163_081_014_000
    assert "市第165号" in revenue["note"]
    assert "163,081,014千円" in revenue["note"]
    assert "認定（全員）" in revenue["note"]
    assert "普通会計ベース" in revenue["note"]
    assert "後期基本計画期間内" in revenue["note"]

    expenditure = records["jp-local-392014-fiscal-2024-total-expenditure"]
    assert expenditure["stage"] == "settlement"
    assert expenditure["amount_yen"] == 161_832_607_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1_248_407_000


def test_kochi_candidate_keeps_real_balance_from_audit_opinion() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }
    note = records["jp-local-392014-fiscal-2024-total-expenditure"]["note"]

    assert "実質収支は544,453千円" in note
    assert "翌年度へ繰り越すべき財源703,953千円" in note
    assert "印字値を保持する" in note


def test_kochi_candidate_certification_was_directly_confirmed() -> None:
    candidate = load_candidate()
    text = json.dumps(candidate, ensure_ascii=False)

    assert "市第165号" in text
    assert "認定（全員）" in text
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_kochi_candidate_budget_vote_wording_is_not_assumed() -> None:
    candidate = load_candidate()
    packets = {
        packet["id"]: packet
        for packet in candidate["candidate_package"]["evidence_packets"]
    }
    claim = packets["evidence-kochi-city-2026-total-expenditure"]["claims"][0]

    assert claim["decision"] == "needs_review"
    assert "市第4号" in claim["statement"]
    assert "可決（多数）" in claim["statement"]
    assert "2026年3月26日" in claim["statement"]
    assert "原案可決" not in claim["statement"]


def test_kochi_candidate_does_not_use_ordinary_account_aggregates() -> None:
    candidate = load_candidate()
    sources = {
        source["id"]: source
        for source in candidate["candidate_package"]["source_catalog"]["sources"]
    }

    boundary = sources["kochi-settlement-2024"]["use_boundary"]
    assert "普通会計ベース" in boundary
    assert "混同しない" in boundary
    location = sources["kochi-settlement-2024"]["evidence_location"]
    assert "決算カード（普通会計ベース）からは取得せず" in location
    assert "監査委員" in location


def test_kochi_candidate_evidence_packets_cover_fiscal_records() -> None:
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


def test_kochi_candidate_progress_review_stays_staging() -> None:
    candidate = load_candidate()
    progress = candidate["candidate_package"]["progress_review"]

    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "第2次" in framework["title"]
    assert "事務事業評価" in framework["evaluation_structure"]
    assert "PDCA" in framework["evaluation_structure"]


def test_kochi_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    assert queue["summary"]["reviewed_complete_count"] == 64
    assert queue["summary"]["pending_record_review_count"] == 3
    assert queue["summary"]["next_official_code"] == "452017"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "392014"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/kochi_phase15_completion.json"
