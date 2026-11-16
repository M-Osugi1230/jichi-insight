import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/sasebo-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/sasebo-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_candidate():
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def test_sasebo_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = load_candidate()

    assert candidate["candidate_id"] == "sasebo-phase15-review-candidate"
    assert candidate["official_code"] == "422029"
    assert candidate["name_ja"] == "佐世保市"
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


def test_sasebo_candidate_catalog_matches_phase14_inventory() -> None:
    candidate = load_candidate()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    sources = candidate["candidate_package"]["source_catalog"]["sources"]

    inventory_by_id = {source["id"]: source for source in inventory["sources"]}
    assert len(sources) == len(inventory_by_id) == 4
    for source in sources:
        assert source["id"] in inventory_by_id
        assert source["official_url"] == inventory_by_id[source["id"]]["official_url"]
        assert source["official_url"].startswith("https://www.city.sasebo.lg.jp/")
        assert source["verification_status"].startswith("primary_source_live_verified")


def test_sasebo_candidate_plan_records_keep_framework_and_transition() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["plan_review"]["records"]
    }

    assert set(records) == {
        "sasebo-current-plan-period",
        "sasebo-current-policy-structure",
        "sasebo-progress-governance-framework",
        "sasebo-plan-transition",
        "sasebo-fy2024-settlement-linkage",
    }
    period = records["sasebo-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["evidence_role"] == "current_plan_identity"
    assert "第7次佐世保市総合計画" in period["statement"]
    assert "2020年度〜2027年度の8年間" in period["statement"]
    assert "前期2020年度〜2023年度" in period["statement"]
    assert "後期2024年度〜2027年度" in period["statement"]
    assert "verified_fixed_period" in period["statement"]
    structure = records["sasebo-current-policy-structure"]
    assert structure["decision"] == "needs_review"
    assert "キラっ都" in structure["statement"]
    assert "活力あふれる国際都市" in structure["statement"]
    assert "観光商工政策" in structure["statement"]
    governance = records["sasebo-progress-governance-framework"]
    assert governance["decision"] == "needs_review"
    assert "PDCAサイクル" in governance["statement"]
    assert "まち・ひと・しごと創生総合戦略" in governance["statement"]
    transition = records["sasebo-plan-transition"]
    assert transition["decision"] == "needs_review"
    assert transition["evidence_role"] == "plan_transition"
    assert "前期基本計画（2020年度〜2023年度" in transition["statement"]
    assert "後期基本計画（2024年度〜2027年度" in transition["statement"]
    linkage = records["sasebo-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "後期基本計画" in linkage["statement"]
    assert "第100号議案" in linkage["statement"]
    assert "継続審査" in linkage["statement"]
    assert "2025年12月4日" in linkage["statement"]
    assert "認定されている" in linkage["statement"]


def test_sasebo_candidate_policy_structure_keeps_four_fields() -> None:
    candidate = load_candidate()
    plan = candidate["candidate_package"]["policy_structure"]["current_plan"]

    assert plan["title"].startswith("佐世保市第7次総合計画")
    assert plan["vision"] == "海風薫り 世界へはばたく \"キラっ都\" SASEBO"
    assert plan["start_fiscal_year"] == 2020
    assert plan["end_fiscal_year"] == 2027
    assert plan["period_status"] == "verified_fixed_period"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "しごと 活力あふれる国際都市",
        "ひと 育み、学び、認め合う「人財」育成都市",
        "まち 西九州を牽引する創造都市",
        "くらし 地域が社会を築く安心都市",
    ]
    principles = " ".join(plan["management_principles"])
    assert "後期基本計画" in principles
    assert "PDCAサイクル" in principles
    assert "流用しない" in principles


def test_sasebo_candidate_fiscal_records_match_primary_sources() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }

    budget = records["jp-local-422029-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 133_877_303_000
    assert budget["review_status"] == "needs_review"
    assert "第18号議案" in budget["note"]
    assert "133,877,303千円" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "2026年3月23日" in budget["note"]
    assert "千円単位" in budget["note"]
    assert "逆算" in budget["note"]
    assert "直接確認は未実施" in budget["note"]

    revenue = records["jp-local-422029-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 130_949_847_225
    assert "第100号議案" in revenue["note"]
    assert "130,949,847,225円" in revenue["note"]
    assert "継続審査" in revenue["note"]
    assert "2025年9月26日" in revenue["note"]
    assert "2025年12月4日" in revenue["note"]
    assert "認定された" in revenue["note"]
    assert "普通会計ベース" in revenue["note"]
    assert "後期基本計画" in revenue["note"]

    expenditure = records["jp-local-422029-fiscal-2024-total-expenditure"]
    assert expenditure["stage"] == "settlement"
    assert expenditure["amount_yen"] == 127_473_906_421
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 3_475_940_804


def test_sasebo_candidate_keeps_real_balance_from_audit_opinion() -> None:
    candidate = load_candidate()
    records = {
        record["id"]: record
        for record in candidate["candidate_package"]["fiscal_records"]
    }
    note = records["jp-local-422029-fiscal-2024-total-expenditure"]["note"]

    assert "実質収支は2,738,920,535円" in note
    assert "737,020,269円" in note
    assert "円単位で印字された値のまま記録する" in note


def test_sasebo_candidate_certification_outcome_confirmed() -> None:
    candidate = load_candidate()
    text = json.dumps(candidate, ensure_ascii=False)

    # The FY2024 settlement bill (第100号議案) was carried over for
    # continued review at the September 2025 session; a supplementary
    # live-browser investigation then confirmed from the council's
    # official December 2025 session results that the bill was
    # certified on 2025-12-04, so the candidate records that
    # certification and its browser-supplement basis, while never
    # recording a non-certification outcome.
    assert "第100号議案" in text
    assert "継続審査" in text
    assert "2025年12月4日" in text
    assert "認定された" in text
    assert "実ブラウザによる補完調査" in text
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text
    # The formerly open question about the final outcome is resolved.
    assert "認定・不認定の最終結果" not in text
    assert "settlement-certification-final-outcome" not in text
    packets = {
        packet["id"]: packet
        for packet in candidate["candidate_package"]["evidence_packets"]
    }
    revenue_packet = packets["evidence-sasebo-city-2024-total-revenue"]
    assert revenue_packet["open_questions"] == [
        "決算事項別明細書の款別合計との最終突合。"
    ]


def test_sasebo_candidate_budget_vote_wording_is_recorded_as_published() -> None:
    candidate = load_candidate()
    packets = {
        packet["id"]: packet
        for packet in candidate["candidate_package"]["evidence_packets"]
    }
    claim = packets["evidence-sasebo-city-2026-total-expenditure"]["claims"][0]

    assert claim["decision"] == "needs_review"
    assert "第18号議案" in claim["statement"]
    assert "原案可決" in claim["statement"]
    assert "2026年3月23日" in claim["statement"]
    assert "133,877,303千円" in claim["statement"]
    assert "逆算" in claim["statement"]


def test_sasebo_candidate_does_not_use_ordinary_account_aggregates() -> None:
    candidate = load_candidate()
    sources = {
        source["id"]: source
        for source in candidate["candidate_package"]["source_catalog"]["sources"]
    }

    boundary = sources["sasebo-settlement-2024"]["use_boundary"]
    assert "普通会計ベース" in boundary
    assert "混同しない" in boundary
    location = sources["sasebo-settlement-2024"]["evidence_location"]
    assert "決算審査意見書" in location
    assert "第100号議案" in location


def test_sasebo_candidate_evidence_packets_cover_fiscal_records() -> None:
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


def test_sasebo_candidate_progress_review_stays_staging() -> None:
    candidate = load_candidate()
    progress = candidate["candidate_package"]["progress_review"]

    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "実施計画" in framework["title"]
    assert "PDCAサイクル" in framework["evaluation_structure"]
    assert "まち・ひと・しごと創生総合戦略" in framework["evaluation_structure"]


def test_sasebo_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    assert queue["summary"]["reviewed_complete_count"] == 67
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "422029"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/sasebo_phase15_completion.json"
