import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/candidates/higashiosaka-city/review_candidate.json"
INVENTORY_PATH = ROOT / "data/indexed/higashiosaka-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate() -> dict:
    return load_json(CANDIDATE_PATH)


def test_higashiosaka_candidate_is_prepared_with_delegated_review_approved() -> None:
    payload = candidate()
    assert payload["official_code"] == "272272"
    assert payload["name_ja"] == "東大阪市"
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
        "data/indexed/higashiosaka-city/source_inventory.json"
    )


def test_higashiosaka_candidate_sources_match_phase14_inventory_exactly() -> None:
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
        "higashiosaka-third-plan": "https://www.city.higashiosaka.lg.jp/0000028226.html",
        "higashiosaka-second-implementation": (
            "https://www.city.higashiosaka.lg.jp/0000028226.html"
        ),
        "higashiosaka-budget-2026": "https://www.city.higashiosaka.lg.jp/0000000529.html",
        "higashiosaka-settlement-2024": (
            "https://www.city.higashiosaka.lg.jp/0000000531.html"
        ),
    }
    assert all(
        url.startswith("https://www.city.higashiosaka.lg.jp/")
        for url in candidate_sources.values()
    )
    by_id = {
        source["id"]: source
        for source in payload["candidate_package"]["source_catalog"]["sources"]
    }
    for verified_id in (
        "higashiosaka-third-plan",
        "higashiosaka-second-implementation",
        "higashiosaka-budget-2026",
    ):
        assert by_id[verified_id]["verification_status"] == (
            "primary_source_live_verified_2026-11-16"
        )
    assert by_id["higashiosaka-settlement-2024"]["verification_status"] == (
        "official_landing_not_live_verified_2026-11-16"
    )


def test_higashiosaka_candidate_keeps_plan_review_records_explicit() -> None:
    payload = candidate()
    records = {
        record["id"]: record
        for record in payload["candidate_package"]["plan_review"]["records"]
    }
    assert set(records) == {
        "higashiosaka-current-plan-period",
        "higashiosaka-current-policy-structure",
        "higashiosaka-progress-governance-framework",
        "higashiosaka-plan-transition",
        "higashiosaka-fy2024-settlement-linkage",
    }
    assert records["higashiosaka-current-plan-period"]["decision"] == "needs_review"
    assert records["higashiosaka-current-plan-period"]["value"] == (
        "第3次総合計画は2021年度～2030年度（令和12年を目標年次）／"
        "実施計画は第1次2021年度～2023年度・第2次2024年度～2027年度"
        "（いずれも年度ごとの版（Ver.）で改定）"
    )
    assert records["higashiosaka-current-policy-structure"]["title"] == (
        "第3次総合計画の施策体系（7分野と3つの重点施策）"
    )
    assert records["higashiosaka-progress-governance-framework"]["title"] == (
        "実施計画の進捗管理（PDCAサイクルによる事業評価と評価指標達成状況の公表）"
    )
    assert records["higashiosaka-plan-transition"]["title"] == (
        "実施計画の第1次（2021〜2023年度）から第2次（2024〜2027年度）への移行と版の履歴"
    )
    assert "確認できていない" in records["higashiosaka-plan-transition"]["statement"]
    linkage = records["higashiosaka-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["title"] == "令和6年度決算と東大阪市第3次総合計画の施策体系の接続"


def test_higashiosaka_candidate_policy_structure_lists_fields() -> None:
    payload = candidate()
    plan = payload["candidate_package"]["policy_structure"]["current_plan"]
    assert plan["title"] == "東大阪市第3次総合計画 第2次実施計画"
    assert plan["vision"] == "つくる・つながる・ひびきあう ― 感動創造都市 東大阪 ―"
    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2027
    assert plan["period_status"] == "verified_fixed_period"
    fields = plan["policy_fields"]
    assert len(fields) == 7
    assert len({field["id"] for field in fields}) == 7
    assert [field["name_ja"] for field in fields] == [
        "人権・共生・協働",
        "子ども・子育て",
        "教育",
        "スポーツ・文化・産業",
        "健康・福祉",
        "都市・環境",
        "防災・治安",
    ]
    # The per-field measures could not be transcribed reliably from the
    # summary edition's vertical layout, so they stay deferred instead of
    # being enumerated from an uncertain reading.
    assert all(field["measures"] == [] for field in fields)


def test_higashiosaka_candidate_fiscal_records_use_primary_source_values() -> None:
    payload = candidate()
    records = {
        record["id"]: record
        for record in payload["candidate_package"]["fiscal_records"]
    }
    assert set(records) == {
        "jp-local-272272-fiscal-2026-total-expenditure",
        "jp-local-272272-fiscal-2024-total-revenue",
        "jp-local-272272-fiscal-2024-total-expenditure",
    }
    budget = records["jp-local-272272-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["metric"] == "total_expenditure"
    assert budget["amount_yen"] == 241023138000
    assert budget["stage"] == "initial_budget"
    assert budget["value_status"] == "available"
    assert budget["review_status"] == "needs_review"
    assert budget["sources"] == ["higashiosaka-budget-2026"]
    assert "241,023,138千円" in budget["note"]
    assert "千円単位" in budget["note"]
    # The supplementary research confirmed the budget bill in the council's
    # official bill list: bill No. 36 was passed with amendments (修正可決)
    # on 2026-03-26, not in its original form. The recorded amount is the
    # enacted post-vote figure (the supplementary budget book's 補正前の額).
    assert "議案第36号" in budget["note"]
    assert "修正可決" in budget["note"]
    assert "2026年3月26日" in budget["note"]
    assert "補正前の額" in budget["note"]
    assert "成立額" in budget["note"]
    assert "原案可決" not in budget["note"]
    revenue = records["jp-local-272272-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-272272-fiscal-2024-total-expenditure"]
    for record in (revenue, expenditure):
        assert record["fiscal_year"] == 2024
        assert record["stage"] == "settlement"
        assert record["value_status"] == "available"
        assert record["review_status"] == "needs_review"
        assert record["sources"] == ["higashiosaka-settlement-2024"]
        assert "千円" in record["note"]
        assert "東大阪監第846号" in record["note"]
    # The FY2024 certification was confirmed in the supplementary research
    # from the council's official bill lists: certification bill No. 1 was
    # kept under continued review in the September 2025 session and
    # certified on 2025-12-01 in the December session.
    for record in (revenue, expenditure):
        assert "認定第1号" in record["note"]
        assert "2025年12月1日" in record["note"]
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 233897034000
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 229860314000
    # The difference matches the formal balance (形式収支) printed in the
    # audit committee's settlement review opinion.
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 4036720000
    assert "3,767,144千円" in expenditure["note"]


def test_higashiosaka_candidate_records_fy2024_certification() -> None:
    payload = candidate()
    package = payload["candidate_package"]
    settlement_texts = []
    for record in package["fiscal_records"]:
        if record["fiscal_year"] == 2024:
            settlement_texts.append(json.dumps(record, ensure_ascii=False))
    for packet in package["evidence_packets"]:
        if packet["subject_id"].startswith("jp-local-272272-fiscal-2024"):
            settlement_texts.append(json.dumps(packet, ensure_ascii=False))
    for record in package["plan_review"]["records"]:
        if record["id"] == "higashiosaka-fy2024-settlement-linkage":
            settlement_texts.append(json.dumps(record, ensure_ascii=False))
    assert settlement_texts
    for text in settlement_texts:
        # The supplementary research confirmed from the council's official
        # bill lists that certification bill No. 1 was kept under continued
        # review in the September 2025 session and certified on 2025-12-01
        # in the December session. The outcome must be recorded as a
        # certification, never as a rejection.
        assert "認定第1号" in text
        assert "2025年12月1日" in text
        assert "不認定" not in text
    whole_text = json.dumps(payload, ensure_ascii=False)
    assert "不認定" not in whole_text
    # The FY2026 budget was passed with amendments (修正可決), so the
    # candidate must never describe it as passed in its original form.
    assert "修正可決" in whole_text
    assert "議案第36号" in whole_text
    assert "原案可決" not in whole_text


def test_higashiosaka_candidate_evidence_packets_point_at_primary_sources() -> None:
    payload = candidate()
    packets = {
        packet["id"]: packet
        for packet in payload["candidate_package"]["evidence_packets"]
    }
    assert set(packets) == {
        "evidence-higashiosaka-city-2026-total-expenditure",
        "evidence-higashiosaka-city-2024-total-revenue",
        "evidence-higashiosaka-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-higashiosaka-city-2026-total-expenditure"]["claims"][0]
    assert budget_claim["source_ids"] == ["higashiosaka-budget-2026"]
    assert "241,023,138千円" in budget_claim["statement"]
    assert "議案第36号" in budget_claim["statement"]
    assert "修正可決" in budget_claim["statement"]
    assert "2026年3月26日" in budget_claim["statement"]
    assert "原案可決" not in budget_claim["statement"]
    revenue_claim = packets["evidence-higashiosaka-city-2024-total-revenue"]["claims"][0]
    assert revenue_claim["source_ids"] == ["higashiosaka-settlement-2024"]
    assert "233,897,034千円" in revenue_claim["statement"]
    assert "認定第1号" in revenue_claim["statement"]
    assert "2025年12月1日" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-higashiosaka-city-2024-total-expenditure"][
        "claims"
    ][0]
    assert expenditure_claim["source_ids"] == ["higashiosaka-settlement-2024"]
    assert "229,860,314千円" in expenditure_claim["statement"]
    assert "4,036,720千円" in expenditure_claim["statement"]
    assert "3,767,144千円" in expenditure_claim["statement"]
    assert "認定第1号" in expenditure_claim["statement"]
    assert "2025年12月1日" in expenditure_claim["statement"]


def test_higashiosaka_candidate_progress_review_stays_staging() -> None:
    payload = candidate()
    progress = payload["candidate_package"]["progress_review"]
    assert progress["id"] == "higashiosaka-current-progress-review-summary"
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert framework["title"] == (
        "第2次実施計画（2024年度～2027年度・Ver.3.0）とPDCAサイクルによる進捗管理"
    )


def test_higashiosaka_promotion_is_reflected_in_review_queue() -> None:
    queue = load_json(QUEUE_PATH)
    assert queue["summary"]["target_count"] == 67
    assert queue["summary"]["reviewed_complete_count"] == 57
    assert queue["summary"]["pending_record_review_count"] == 10
    assert queue["summary"]["next_official_code"] == "382019"
    items = {item["official_code"]: item for item in queue["execution_queue"]}
    assert items["272272"]["name_ja"] == "東大阪市"
    assert items["272272"]["status"] == "reviewed_complete"
    assert items["272272"]["completion_path"] == (
        "data/catalog/higashiosaka_phase15_completion.json"
    )
