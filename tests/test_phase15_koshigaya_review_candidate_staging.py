"""Safety tests for Koshigaya Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/koshigaya-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/koshigaya-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_koshigaya_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "koshigaya-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "112224"
    assert candidate["name_ja"] == "越谷市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/koshigaya-city/source_inventory.json"
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


def test_koshigaya_sources_match_existing_official_inventory():
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
        source["official_url"].startswith(
            "https://www.city.koshigaya.saitama.jp/"
        )
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_koshigaya_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-112224-fiscal-2026-total-expenditure",
        "jp-local-112224-fiscal-2024-total-revenue",
        "jp-local-112224-fiscal-2024-total-expenditure",
    }
    assert all(
        rec["municipality_id"] == "jp-local-112224" for rec in fiscal_records
    )
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted (原案可決) as bill No. 25 at
    # the March 2026 regular council session (final-day vote on
    # 2026-03-18), so it must not be labelled as a draft proposal
    # (予算案). The amount is the exact sen-yen figure stated in
    # Article 1 of the official budget book (132,700,000千円).
    budget = by_id["jp-local-112224-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 132700000000

    # The FY2024 settlement totals are the exact yen-level figures in
    # the official settlement overview. Their difference must equal the
    # published balance of 8,510,841,322 yen.
    revenue = by_id["jp-local-112224-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 140215912093
    expenditure = by_id["jp-local-112224-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 131705070771
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 8510841322

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

    # The FY2026 budget claim must record the enactment: bill No. 25,
    # passed as proposed on 2026-03-18.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-112224-fiscal-2026-total-expenditure"
    )
    assert "第25号議案" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]
    assert "第25号議案" in budget["note"]
    assert "令和8年3月18日" in budget["note"]

    # The FY2024 settlement was certified (認定可決) as bill No. 101 on
    # 2025-09-25 at the September 2025 regular council session,
    # confirmed from the council's official vote-result document.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-112224-fiscal-2024-total-revenue"
    )
    assert "第101号議案" in revenue_packet["claims"][0]["statement"]
    assert "令和7年9月25日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "第101号議案" in revenue["note"]
    assert "第101号議案" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 belongs to the former (前期) basic plan period, so its
    # settlement must not be reused as results of the current latter
    # basic plan; the linkage stays explicitly not assessable.
    assert decisions["koshigaya-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "koshigaya-current-plan-period"
    )
    assert period["value"] == "2021年度～2030年度"

    # The current plan version is the latter basic plan (2026-2030) of
    # the fixed-period 5th comprehensive plan, with the future-city
    # vision recorded verbatim from the official plan summary.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第5次越谷市総合振興計画 後期基本計画"
    assert current_plan["start_fiscal_year"] == 2026
    assert current_plan["end_fiscal_year"] == 2030
    assert (
        current_plan["vision"]
        == "水と緑と太陽に恵まれた みんなが活躍する安全・安心・共生都市"
    )
    # The six basic goals of the latter basic plan and all 24 of their
    # top-level measures (大項目) are recorded exactly as published in
    # the official plan book; individual projects are not enumerated.
    goals = current_plan["basic_goals"]
    assert [goal["name_ja"] for goal in goals] == [
        "多様な人が交流し、参加と協働により発展するまちづくり",
        "みんなが健康で共生して住み続けられるまちづくり",
        "都市と自然が調和した集約と連携によるまちづくり",
        "持続可能で災害に強い安全・安心なまちづくり",
        "魅力ある資源を活かし、都市の活力を創造するまちづくり",
        "みんなが主体的に学び、生きがいを持って活躍できるまちづくり",
    ]
    assert sum(len(goal["measures"]) for goal in goals) == 24


def test_koshigaya_promotion_is_reflected_in_queue_state():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "112224"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/koshigaya_phase15_completion.json"
    assert (ROOT / item["completion_path"]).is_file()
    assert queue["summary"]["reviewed_complete_count"] == 18
    assert queue["summary"]["pending_record_review_count"] == 49
    assert queue["summary"]["next_official_code"] == "122173"


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
