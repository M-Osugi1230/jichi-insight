"""Safety tests for Shinjuku Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/shinjuku-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/shinjuku-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_shinjuku_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "shinjuku-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "131040"
    assert candidate["name_ja"] == "新宿区"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/shinjuku-city/source_inventory.json"
    )
    assert (ROOT / candidate["source_inventory_path"]).is_file()
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-16"
    assert candidate["human_review"]["reviewer_note"]
    # The owner did not review the primary sources personally: on
    # 2026-11-15 the owner explicitly delegated the review to Muse in
    # chat, and the note must record that delegation rather than
    # claiming an owner review.
    assert "委任" in candidate["human_review"]["reviewer_note"]
    assert "レビューはあなたがやってください" in candidate["human_review"]["reviewer_note"]
    assert candidate["publication"]["eligible"] is False


def test_shinjuku_sources_match_existing_official_inventory():
    candidate = read(CANDIDATE)
    inventory = read(INVENTORY)
    sources = candidate["candidate_package"]["source_catalog"]["sources"]
    expected = inventory["sources"]
    assert len(sources) == len(expected) == 4
    assert {source["id"] for source in sources} == {
        source["id"] for source in expected
    }
    actual_urls = {(source["id"], source["official_url"]) for source in sources}
    assert actual_urls == {
        (source["id"], source["official_url"]) for source in expected
    }
    assert all(
        source["official_url"].startswith("https://www.city.shinjuku.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_shinjuku_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-131040-fiscal-2026-total-expenditure",
        "jp-local-131040-fiscal-2024-total-revenue",
        "jp-local-131040-fiscal-2024-total-expenditure",
    }
    assert all(
        rec["municipality_id"] == "jp-local-131040" for rec in fiscal_records
    )
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted (可決) as bill No. 1
    # (第1号議案) at the 1st regular ward assembly session of 2026,
    # so it must not be labelled as a draft proposal (予算案). The
    # amount is the exact sen-yen total in Article 1 of the bill as
    # printed in the official budget book (187,835,560千円).
    budget = by_id["jp-local-131040-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 187835560000

    # The FY2024 settlement totals are published at yen precision in
    # the official settlement summary (決算総括). Their difference
    # must equal the published balance (差引額) of 5,941,823,769 yen.
    revenue = by_id["jp-local-131040-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 190137549271
    expenditure = by_id["jp-local-131040-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 184195725502
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 5941823769

    packets = package["evidence_packets"]
    assert {pkt["subject_id"] for pkt in packets} == set(by_id)
    assert all(pkt["subject_type"] == "fiscal_record" for pkt in packets)
    assert all(pkt["review_status"] == "needs_review" for pkt in packets)
    assert all(pkt["claims"] for pkt in packets)
    assert all(
        claim["decision"] == "needs_review" and bool(claim["location_note"])
        for pkt in packets
        for claim in pkt["claims"]
    )

    # The FY2026 budget claim must record the enactment: bill No. 1,
    # passed on 2026-03-24 (the session's final day).
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-131040-fiscal-2026-total-expenditure"
    )
    assert "第1号議案" in budget_packet["claims"][0]["statement"]
    assert "可決" in budget_packet["claims"][0]["statement"]
    assert "第1号議案" in budget["note"]
    assert "令和8年3月24日" in budget["note"]

    # The FY2024 settlement was certified as certification bill
    # No. 1 (認定第1号) on 2025-10-20 at the 3rd regular session
    # of 2025 (its final day), per the ward assembly's official
    # session page and deliberation-results document.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-131040-fiscal-2024-total-revenue"
    )
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年10月20日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "認定第1号" in revenue["note"]
    assert "認定第1号" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 falls inside the current comprehensive plan period,
    # but settlement totals are section-level aggregates with no
    # official mapping to individual measures or action-plan
    # projects, so the linkage stays explicitly not assessable.
    assert decisions["shinjuku-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "shinjuku-current-plan-period"
    )
    assert period["value"] == "2018年度～2027年度"

    # The current plan is the ward's comprehensive plan (FY2018 to
    # FY2027), which integrates the basic plan and the urban master
    # plan. Its basic plan sets 33 individual measures under five
    # basic policies, exactly as published in the official plan
    # overview; individual projects are not enumerated here.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "新宿区総合計画"
    assert current_plan["start_fiscal_year"] == 2018
    assert current_plan["end_fiscal_year"] == 2027
    assert current_plan["vision"] == "『新宿力』で創造する、やすらぎとにぎわいのまち"
    goals = current_plan["basic_goals"]
    assert [goal["name_ja"] for goal in goals] == [
        "暮らしやすさ1番の新宿",
        "新宿の高度防災都市化と安全安心の強化",
        "賑わい都市・新宿の創造",
        "健全な区財政の確立",
        "好感度1番の区役所",
    ]
    assert [len(goal["measures"]) for goal in goals] == [9, 3, 16, 2, 3]
    assert sum(len(goal["measures"]) for goal in goals) == 33


def test_shinjuku_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "131040"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/shinjuku_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 37
    assert queue["summary"]["pending_record_review_count"] == 30
    assert queue["summary"]["next_official_code"] == "272078"


def test_public_web_does_not_import_candidate_staging():
    violations = []
    for path in WEB_ROOT.rglob("*"):
        if (
            path.is_file()
            and path.suffix in {".ts", ".tsx", ".js", ".mjs"}
            and "data/candidates" in path.read_text(encoding="utf-8")
        ):
            violations.append(str(path.relative_to(ROOT)))
    assert violations == []
