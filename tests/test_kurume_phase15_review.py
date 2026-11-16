from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/kurume_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/kurume-city"
CANDIDATE = ROOT / "data/candidates/kurume-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kurume_review_package_is_the_sixtieth_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "kurume-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "402036",
        "name_ja": "久留米市",
        "completed_at": "2026-11-17",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/kurume_phase15_sources.json",
            "plan_review_path": "data/reviewed/kurume-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/kurume_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/kurume_current_progress_review_summary.json"
            ),
            "fiscal_records_path": (
                "data/reviewed/kurume-city/fiscal_records.json"
            ),
            "fiscal_evidence_path": (
                "data/reviewed/kurume-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 10,
                "basic_plan_measures": 33,
                "promoted_implementation_item_actual_records": 0,
                "fiscal_top_line_records": 3,
            },
        },
        "quality_gate": completion["quality_gate"],
        "deferred_depth": completion["deferred_depth"],
        "completion_boundary": completion["completion_boundary"],
    }

    queue = load(QUEUE)
    assert queue["summary"]["reviewed_complete_count"] == 60
    assert queue["summary"]["pending_record_review_count"] == 7
    assert queue["summary"]["next_official_code"] == "412015"
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "402036"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/kurume_phase15_completion.json"


def test_kurume_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-402036"
    assert municipality["official_code"] == "402036"
    assert municipality["name_ja"] == "久留米市"
    assert municipality["prefecture_name_ja"] == "福岡県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == "https://www.city.kurume.fukuoka.jp/"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-17"
    assert municipality["sources"] == [
        "kurume-city-home",
        "kurume-budget-2026",
        "kurume-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/kurume_phase15_sources.json")["sources"]
    assert len(sources) == 4
    for source in sources:
        assert source["official_url"].startswith(
            "https://www.city.kurume.fukuoka.jp/"
        )
        assert "verification_status" not in source


def test_kurume_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/kurume_phase15_sources.json")
    assert catalog["id"] == "kurume-phase15-sources"
    assert catalog["name_ja"] == "久留米市"
    assert catalog["official_code"] == "402036"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-17"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "kurume-future-design-2035",
        "kurume-policy-evaluation",
        "kurume-budget-2026",
        "kurume-settlement-2024",
    }
    assert by_id["kurume-future-design-2035"]["evidence_role"] == (
        "comprehensive_plan"
    )
    assert by_id["kurume-future-design-2035"]["format"] == "html"
    assert by_id["kurume-policy-evaluation"]["evidence_role"] == "annual_progress"
    assert by_id["kurume-budget-2026"]["evidence_role"] == "budget"
    assert by_id["kurume-settlement-2024"]["evidence_role"] == "settlement"


def test_kurume_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(record for record in records if record["fiscal_year"] == 2026)
    assert budget["id"] == "jp-local-402036-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 167_760_000_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["kurume-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # Bill No. 45 (the regular budget) was adopted as proposed
    # （原案可決） on 2026-06-26 according to the council's official
    # vote record, and that wording is kept verbatim. Because a
    # mayoral election was scheduled, a provisional budget for April
    # to June (bill No. 6, 70,670,000 thousand yen) was enacted first;
    # the provisional and regular budgets are kept separate.
    assert "第45号議案" in text
    assert "原案可決" in text
    assert "2026年6月26日" in text
    assert "167,760,000千円" in text
    assert "暫定予算" in text
    assert "第6号議案" in text
    assert "70,670,000千円" in text
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
    assert revenue["amount_yen"] == 151_712_648_320
    assert expenditure["amount_yen"] == 150_433_124_636
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1_279_523_684
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["kurume-settlement-2024"]
    assert expenditure["sources"] == ["kurume-settlement-2024"]
    # The FY2024 settlement was certified (bill 認定第1号) on
    # 2025-10-15, not rejected. The totals stay at the yen precision
    # printed in the settlement book, and the real balance stays at
    # the thousand-yen precision printed in the settlement summary
    # documents; ordinary-account aggregate figures are not used as
    # general-account values.
    assert "認定第1号" in text
    assert "2025年10月15日" in text
    assert "1,011,356千円" in text
    assert "普通会計ベース" in text
    assert "不認定" not in text


def test_kurume_evidence_packets_confirm_fiscal_claims():
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
        "jp-local-402036-fiscal-2026-total-expenditure",
        "jp-local-402036-fiscal-2024-total-revenue",
        "jp-local-402036-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "第45号議案" in text
    assert "認定第1号" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text
    assert "不認定" not in text


def test_kurume_plan_review_accepts_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-kurume-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-17"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["kurume-current-plan-period"]["decision"] == "accepted"
    assert "久留米未来デザイン計画2035" in by_id["kurume-current-plan-period"][
        "statement"
    ]
    assert "前期2026年度〜2030年度" in by_id["kurume-current-plan-period"][
        "value"
    ]
    assert "verified_fixed_period" in by_id["kurume-current-plan-period"][
        "statement"
    ]
    assert by_id["kurume-current-policy-structure"]["decision"] == "accepted"
    assert "10の基本目標" in by_id["kurume-current-policy-structure"][
        "statement"
    ]
    assert "優しさ 豊かさ 輝き あふれるまち" in by_id[
        "kurume-current-policy-structure"
    ]["statement"]
    assert by_id["kurume-progress-governance-framework"]["decision"] == (
        "accepted"
    )
    assert "政策評価制度" in by_id["kurume-progress-governance-framework"][
        "statement"
    ]
    assert by_id["kurume-plan-transition"]["decision"] == "accepted"
    assert "久留米市新総合計画" in by_id["kurume-plan-transition"]["statement"]
    assert "第4次（令和2年度〜令和7年度）" in by_id["kurume-plan-transition"][
        "statement"
    ]
    linkage = by_id["kurume-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    # FY2024 is a settlement within the previous plan's fourth basic
    # plan period and its plan version differs from the current plan,
    # so the linkage stays not_assessable.
    assert "第4次基本計画期間" in linkage["statement"]
    assert "not_assessable" in linkage["statement"]


def test_kurume_policy_structure_keeps_ten_goals_and_policy_fields():
    structure = load(ROOT / "data/catalog/kurume_current_policy_structure.json")
    assert structure["id"] == "kurume-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "kurume-future-design-2035"
    assert structure["counts"] == {"basic_goals": 10, "basic_plan_measures": 33}

    plan = structure["current_plan"]
    assert plan["title"].startswith("久留米未来デザイン計画2035")
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2035
    assert plan["period_status"] == "verified_fixed_period"
    assert plan["vision"] == "優しさ 豊かさ 輝き あふれるまち"
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


def test_kurume_progress_review_keeps_implementation_plan_framework():
    progress = load(
        ROOT / "data/catalog/kurume_current_progress_review_summary.json"
    )
    assert progress["id"] == "kurume-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-17"

    framework = progress["current_implementation_plan"]
    assert "事業計画" in framework["title"]
    assert "政策評価制度" in framework["title"]
    assert "第4次基本計画期間" in framework["period"]
    assert "まちづくり評価" in framework["rolling_structure"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "認定第1号" in linkage["boundary"]
    assert "not_assessable" in linkage["boundary"]


def test_kurume_finance_sources_are_reviewed():
    finance = load(ROOT / "data/catalog/kurume_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-17"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "kurume-city-home",
        "kurume-budget-2026",
        "kurume-settlement-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "kurume-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith("https://www.city.kurume.fukuoka.jp/")


def test_kurume_completion_marks_every_gate_and_defers_depth():
    completion = load(COMPLETION)
    assert set(completion["quality_gate"].values()) == {True}
    assert len(completion["quality_gate"]) == 13

    deferred = {item["id"]: item for item in completion["deferred_depth"]}
    assert set(deferred) == {
        "current-plan-granular-kpi-and-project-linkage",
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
    assert "第45号議案" in boundary
    assert "認定第1号" in boundary
    assert "原案可決" in boundary
    assert "暫定予算" in boundary
    assert "1,011,356千円" in boundary
    assert "verified_fixed_period" in boundary
    assert "不認定" not in boundary
    assert "修正可決" not in boundary


def test_kurume_review_records_delegation_not_owner_review():
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
    assert "第45号議案" in note
    assert "認定第1号" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "不認定" not in serialized
    assert "修正可決" not in serialized
