"""Safety tests for Kashiwa Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/kashiwa-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/kashiwa-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kashiwa_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "kashiwa-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "122173"
    assert candidate["name_ja"] == "柏市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/kashiwa-city/source_inventory.json"
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


def test_kashiwa_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.kashiwa.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_kashiwa_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-122173-fiscal-2026-total-expenditure",
        "jp-local-122173-fiscal-2024-total-revenue",
        "jp-local-122173-fiscal-2024-total-expenditure",
    }
    assert all(
        rec["municipality_id"] == "jp-local-122173" for rec in fiscal_records
    )
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted (原案可決) as bill No. 34
    # at the 1st regular council session of 2026 (vote on 2026-03-24),
    # so it must not be labelled as a draft proposal (予算案). The
    # amount is the exact sen-yen total in the official budget
    # overview's revenue/expenditure tables (191,224,000千円).
    budget = by_id["jp-local-122173-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 191224000000

    # The FY2024 settlement totals are published at yen precision in
    # the official settlement book's summary table. Their difference
    # must equal the published balance (歳入歳出差引残高) of
    # 7,204,778,434 yen.
    revenue = by_id["jp-local-122173-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 175594266737
    expenditure = by_id["jp-local-122173-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 168389488303
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 7204778434

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

    # The FY2026 budget claim must record the enactment: bill No. 34,
    # passed as proposed on 2026-03-24.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-122173-fiscal-2026-total-expenditure"
    )
    assert "議案第34号" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]
    assert "議案第34号" in budget["note"]
    assert "令和8年3月24日" in budget["note"]

    # The FY2024 settlement was certified (原案認定) as bill No. 16
    # on 2025-10-02 at the 3rd regular council session of 2025,
    # confirmed from the council's official vote-result list.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-122173-fiscal-2024-total-revenue"
    )
    assert "議案第16号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年10月2日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "議案第16号" in revenue["note"]
    assert "議案第16号" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 predates the 6th plan period (it belongs to the previous
    # 5th plan), so its totals must not be carried into the current
    # plan and the linkage stays explicitly not assessable.
    assert decisions["kashiwa-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "kashiwa-current-plan-period"
    )
    assert period["value"] == "2025年度～2034年度"

    # The current plan is the 6th comprehensive plan (basic concept
    # 2025-2034), with a five-year basic plan split into first and
    # second halves, and the future-city vision recorded verbatim
    # from the official plan.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "柏市第六次総合計画"
    assert current_plan["start_fiscal_year"] == 2025
    assert current_plan["end_fiscal_year"] == 2034
    assert current_plan["vision"] == (
        "柏に関わる一人ひとりが想いを実現できるまち"
        "～多様な価値や人々がつながり、新たな価値の創造に挑戦～"
    )
    # The first-period basic plan's policy framework is composed of
    # 22 fields (分野) with 66 measures (施策) in total, exactly as
    # published in the plan book's framework chart (pp. 30-33);
    # individual projects are not enumerated. The three basic goals
    # of the basic concept cut across the fields, so they are
    # recorded in management_principles instead of as goal parents.
    goals = current_plan["basic_goals"]
    assert [goal["name_ja"] for goal in goals] == [
        "子育て・子育ち",
        "学校教育",
        "教育環境",
        "健康づくり",
        "医療・介護",
        "地域福祉",
        "地域活動",
        "共生社会",
        "生涯学習・文化",
        "スポーツ",
        "都市整備",
        "道路・交通",
        "上下水道・雨水対策",
        "地域産業",
        "新産業",
        "農業振興",
        "防災",
        "消防・救急",
        "生活の安全",
        "自然との共生",
        "地球温暖化対策",
        "廃棄物処理",
    ]
    assert sum(len(goal["measures"]) for goal in goals) == 66


def test_kashiwa_promotion_is_reflected_in_queue_state():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "122173"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/kashiwa_phase15_completion.json"
    assert (ROOT / item["completion_path"]).is_file()
    assert queue["summary"]["reviewed_complete_count"] == 67
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None


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
