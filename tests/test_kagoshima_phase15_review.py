from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/kagoshima_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/kagoshima-city"
CANDIDATE = ROOT / "data/candidates/kagoshima-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kagoshima_review_package_is_the_sixty_sixth_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "kagoshima-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "462012",
        "name_ja": "鹿児島市",
        "completed_at": "2026-11-17",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/kagoshima_phase15_sources.json",
            "plan_review_path": "data/reviewed/kagoshima-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/kagoshima_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/kagoshima_current_progress_review_summary.json"
            ),
            "fiscal_records_path": (
                "data/reviewed/kagoshima-city/fiscal_records.json"
            ),
            "fiscal_evidence_path": (
                "data/reviewed/kagoshima-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 6,
                "basic_plan_measures": 0,
                "promoted_implementation_item_actual_records": 0,
                "fiscal_top_line_records": 3,
            },
        },
        "quality_gate": completion["quality_gate"],
        "deferred_depth": completion["deferred_depth"],
        "completion_boundary": completion["completion_boundary"],
    }

    queue = load(QUEUE)
    assert queue["summary"]["reviewed_complete_count"] == 68
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "462012"
    )
    assert entry["status"] == "reviewed_complete"
    assert (
        entry["completion_path"] == "data/catalog/kagoshima_phase15_completion.json"
    )


def test_kagoshima_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-462012"
    assert municipality["official_code"] == "462012"
    assert municipality["name_ja"] == "鹿児島市"
    assert municipality["prefecture_name_ja"] == "鹿児島県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == "https://www.city.kagoshima.lg.jp/"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-17"
    assert municipality["sources"] == [
        "kagoshima-city-home",
        "kagoshima-budget-2026",
        "kagoshima-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/kagoshima_phase15_sources.json")["sources"]
    assert len(sources) == 5
    for source in sources:
        assert source["official_url"].startswith(
            "https://www.city.kagoshima.lg.jp/"
        )
        assert "verification_status" not in source


def test_kagoshima_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/kagoshima_phase15_sources.json")
    assert catalog["id"] == "kagoshima-phase15-sources"
    assert catalog["name_ja"] == "鹿児島市"
    assert catalog["official_code"] == "462012"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-17"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "kagoshima-sixth-front-plan",
        "kagoshima-second-implementation",
        "kagoshima-latter-transition",
        "kagoshima-budget-2026",
        "kagoshima-settlement-2024",
    }
    assert by_id["kagoshima-sixth-front-plan"]["evidence_role"] == (
        "comprehensive_plan"
    )
    assert by_id["kagoshima-sixth-front-plan"]["format"] == "html"
    assert by_id["kagoshima-second-implementation"]["evidence_role"] == (
        "implementation_plan"
    )
    assert by_id["kagoshima-latter-transition"]["evidence_role"] == (
        "plan_transition"
    )
    assert by_id["kagoshima-budget-2026"]["evidence_role"] == "budget"
    assert by_id["kagoshima-settlement-2024"]["evidence_role"] == "settlement"


def test_kagoshima_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(record for record in records if record["fiscal_year"] == 2026)
    assert budget["id"] == "jp-local-462012-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 304_837_000_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["kagoshima-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # Bill No. 195 （定第195号議案） was recorded as 原案可決 (adopted as
    # proposed) in the council's official voting-attitude table, and
    # the bill number and vote date (2026-03-19) were confirmed in the
    # plenary minutes through a supplementary live-browser
    # investigation. The amount stays at the published sen-yen
    # precision.
    assert "定第195号議案" in text
    assert "原案可決" in text
    assert "2026年3月19日" in text
    assert "304,837,000千円" in text
    assert "千円単位" in text
    assert "当初予算の概要" in text
    assert "修正可決" not in text
    assert "修正議決" not in text

    revenue = next(
        record
        for record in records
        if record["fiscal_year"] == 2024 and record["metric"] == "total_revenue"
    )
    expenditure = next(
        record
        for record in records
        if record["fiscal_year"] == 2024 and record["metric"] == "total_expenditure"
    )
    assert revenue["amount_yen"] == 306_759_735_000
    assert expenditure["amount_yen"] == 296_622_819_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 10_136_916_000
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["kagoshima-settlement-2024"]
    assert expenditure["sources"] == ["kagoshima-settlement-2024"]
    # The FY2024 settlement bill (No. 56) was submitted to the Reiwa 7
    # 3rd regular session but was not put to a vote there, and was
    # certified on 2025-12-02 at the Reiwa 7 4th regular session. The
    # totals and the real balance stay at the sen-yen precision
    # printed in the settlement summary, and ordinary-account
    # aggregates are not used.
    assert "定第56号議案" in text
    assert "2025年12月2日" in text
    assert "認定" in text
    assert "歳入歳出差引額は10,136,916千円" in text
    assert "6,584,470千円" in text
    assert "普通会計ベース" in text
    assert "不認定" not in text


def test_kagoshima_evidence_packets_confirm_fiscal_claims():
    packets = load(REVIEWED / "evidence_packets.json")
    assert len(packets) == 3
    amounts = set()
    for packet in packets:
        assert packet["review_status"] == "reviewed"
        assert packet["subject_type"] == "fiscal_record"
        for claim in packet["claims"]:
            assert claim["decision"] == "accepted"
            amounts.add(packet["subject_id"])
    assert amounts == {
        "jp-local-462012-fiscal-2026-total-expenditure",
        "jp-local-462012-fiscal-2024-total-revenue",
        "jp-local-462012-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "定第195号議案" in text
    assert "定第56号議案" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text
    assert "不認定" not in text


def test_kagoshima_plan_review_accepts_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-kagoshima-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-17"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["kagoshima-current-plan-period"]["decision"] == "accepted"
    assert "第六次鹿児島市総合計画" in by_id["kagoshima-current-plan-period"][
        "statement"
    ]
    assert "transition_or_unresolved" in by_id["kagoshima-current-plan-period"][
        "statement"
    ]
    assert by_id["kagoshima-current-policy-structure"]["decision"] == "accepted"
    assert "躍動都市・かごしま" in by_id["kagoshima-current-policy-structure"][
        "statement"
    ]
    assert "基本目標1 信頼とやさしさのある共創のまち" in by_id[
        "kagoshima-current-policy-structure"
    ]["statement"]
    assert "基本目標6 質の高い暮らしを支える快適なまち" in by_id[
        "kagoshima-current-policy-structure"
    ]["statement"]
    assert by_id["kagoshima-progress-governance-framework"]["decision"] == (
        "accepted"
    )
    assert "第2期実施計画" in by_id["kagoshima-progress-governance-framework"][
        "statement"
    ]
    assert by_id["kagoshima-plan-transition"]["decision"] == "accepted"
    assert "素案" in by_id["kagoshima-plan-transition"]["statement"]
    assert "第五次鹿児島市総合計画" in by_id["kagoshima-plan-transition"][
        "statement"
    ]
    linkage = by_id["kagoshima-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    # FY2024 falls within the current plan's front basic plan period,
    # but no official total-level mapping to the plan's basic-goal and
    # measure structure exists, so the linkage stays not_assessable.
    assert "前期基本計画" in linkage["statement"]
    assert "not_assessable" in linkage["statement"]
    assert "定第56号議案" in linkage["statement"]
    assert "認定されている" in linkage["statement"]


def test_kagoshima_policy_structure_keeps_six_fields():
    structure = load(ROOT / "data/catalog/kagoshima_current_policy_structure.json")
    assert structure["id"] == "kagoshima-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "kagoshima-sixth-front-plan"
    assert structure["counts"] == {"basic_goals": 6, "basic_plan_measures": 0}

    plan = structure["current_plan"]
    assert plan["title"].startswith("第六次鹿児島市総合計画")
    assert plan["start_fiscal_year"] == 2022
    assert plan["end_fiscal_year"] == 2031
    assert plan["period_status"] == "transition_or_unresolved"
    assert plan["vision"] == "つながる人・まち 彩りあふれる 躍動都市・かごしま"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "信頼とやさしさのある共創のまち",
        "自然と都市が調和したうるおいのあるまち",
        "魅力にあふれ人が集う活力あるまち",
        "自分らしく健やかに暮らせる安心安全なまち",
        "豊かな個性を育み未来を拓く誇りあるまち",
        "質の高い暮らしを支える快適なまち",
    ]
    measures = [measure for field in fields for measure in field["measures"]]
    assert measures == []
    principles = " ".join(plan["management_principles"])
    assert "後期基本計画" in principles
    assert "第2期実施計画" in principles
    assert "流用しない" in principles


def test_kagoshima_progress_review_keeps_implementation_plan_framework():
    progress = load(
        ROOT / "data/catalog/kagoshima_current_progress_review_summary.json"
    )
    assert progress["id"] == "kagoshima-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-17"

    framework = progress["current_implementation_plan"]
    assert "第2期実施計画" in framework["title"]
    assert "2022年度〜2031年度" in framework["period"]
    assert "基本目標別事業計画" in framework["rolling_structure"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "定第56号議案" in linkage["boundary"]
    assert "not_assessable" in linkage["boundary"]


def test_kagoshima_finance_sources_are_reviewed():
    finance = load(ROOT / "data/catalog/kagoshima_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-17"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "kagoshima-city-home",
        "kagoshima-budget-2026",
        "kagoshima-settlement-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "kagoshima-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith("https://www.city.kagoshima.lg.jp/")


def test_kagoshima_completion_marks_every_gate_and_defers_depth():
    completion = load(COMPLETION)
    assert set(completion["quality_gate"].values()) == {True}
    assert len(completion["quality_gate"]) == 13

    deferred = {item["id"]: item for item in completion["deferred_depth"]}
    assert set(deferred) == {
        "current-plan-granular-policy-and-indicator-linkage",
        "fiscal-detail-reconciliation",
        "plan-transition-version-depth",
        "policy-outcome-causal-and-cross-city-comparability",
    }
    assert all(
        item["status"] == "deferred_not_required_for_v1_completion"
        for item in deferred.values()
    )

    candidate = load(CANDIDATE)
    candidate_deferred = {item["id"]: item for item in candidate["deferred_depth"]}
    assert set(deferred) == set(candidate_deferred)
    for item_id, item in deferred.items():
        assert item["boundary"] == candidate_deferred[item_id]["boundary"]

    boundary = completion["completion_boundary"]
    assert "定第195号議案" in boundary
    assert "定第56号議案" in boundary
    assert "原案可決" in boundary
    assert "transition_or_unresolved" in boundary
    assert "不認定" not in boundary
    assert "修正可決" not in boundary


def test_kagoshima_review_records_delegation_not_owner_review():
    candidate = load(CANDIDATE)
    assert candidate["package_state"] == "prepared"
    assert candidate["publication"]["eligible"] is False
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-17"
    note = candidate["human_review"]["reviewer_note"]
    # The promotion rests on the owner's explicit 2026-11-15 delegation of
    # the review to Muse; the record must say so and must not present
    # the review as the owner's personal review of the primary sources.
    assert "委任" in note
    assert "レビューはあなたがやってください" in note
    assert "所有者本人が一次資料を直接レビューしたものではない" in note
    assert "定第195号議案" in note
    assert "定第56号議案" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "不認定" not in serialized
    assert "修正可決" not in serialized
