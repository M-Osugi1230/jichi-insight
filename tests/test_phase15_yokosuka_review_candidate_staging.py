"""Safety tests for Yokosuka Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/yokosuka-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/yokosuka-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_yokosuka_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "yokosuka-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "142018"
    assert candidate["name_ja"] == "横須賀市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/yokosuka-city/source_inventory.json"
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


def test_yokosuka_sources_match_existing_official_inventory():
    candidate = read(CANDIDATE)
    inventory = read(INVENTORY)
    sources = candidate["candidate_package"]["source_catalog"]["sources"]
    expected = inventory["sources"]
    assert len(sources) == len(expected) == 5
    assert {source["id"] for source in sources} == {
        source["id"] for source in expected
    }
    actual_urls = {(source["id"], source["official_url"]) for source in sources}
    assert actual_urls == {
        (source["id"], source["official_url"]) for source in expected
    }
    assert all(
        source["official_url"].startswith(
            "https://www.city.yokosuka.kanagawa.jp/"
        )
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_yokosuka_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-142018-fiscal-2026-total-expenditure",
        "jp-local-142018-fiscal-2024-total-revenue",
        "jp-local-142018-fiscal-2024-total-expenditure",
    }
    assert all(
        rec["municipality_id"] == "jp-local-142018" for rec in fiscal_records
    )
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted (原案可決) as bill
    # No. 18 (議案第18号) at the March 2026 regular council
    # session (plenary vote on 2026-03-25), so it must not be
    # labelled as a draft proposal (予算案). The amount is the
    # exact sen-yen total in Article 1 of the bill as published
    # in the official budget book (180,120,000千円).
    budget = by_id["jp-local-142018-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 180120000000

    # The FY2024 settlement totals are published at yen precision
    # in the audit committee's official settlement-review opinion
    # (決算総括表, unit: yen). Their difference must equal the
    # published balance (収支差引額) of 5,898,493,304 yen.
    revenue = by_id["jp-local-142018-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 177898477901
    expenditure = by_id["jp-local-142018-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 171999984597
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 5898493304

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

    # The FY2026 budget claim must record the enactment: bill
    # No. 18, passed as proposed on 2026-03-25.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-142018-fiscal-2026-total-expenditure"
    )
    assert "議案第18号" in budget_packet["claims"][0]["statement"]
    assert "可決" in budget_packet["claims"][0]["statement"]
    assert "議案第18号" in budget["note"]
    assert "令和8年3月25日" in budget["note"]

    # The FY2024 settlement was certified as bill No. 100
    # (議案第100号) on 2025-10-07 at the September 2025 regular
    # council session, per the council's official vote results.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-142018-fiscal-2024-total-revenue"
    )
    assert "議案第100号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年10月7日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "議案第100号" in revenue["note"]
    assert "議案第100号" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 falls inside the current vision period, but
    # settlement totals are section-level aggregates with no
    # official mapping to individual projects, so the linkage
    # stays explicitly not assessable.
    assert decisions["yokosuka-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "yokosuka-current-plan-period"
    )
    assert period["value"] == "2022年度～2029年度"

    # The current plan is YOKOSUKA Vision 2030, an integrated
    # two-layer basic concept / basic plan (FY2022 to FY2029).
    # Its basic goals are the ten field-level future images
    # exactly as published in official city documents; the
    # per-field policy directions below them are not enumerated
    # in this candidate, so measures stay empty by design.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "YOKOSUKAビジョン2030"
    assert current_plan["start_fiscal_year"] == 2022
    assert current_plan["end_fiscal_year"] == 2029
    assert current_plan["vision"] == "変化を力に進むまち"
    goals = current_plan["basic_goals"]
    assert [goal["name_ja"] for goal in goals] == [
        "福祉 誰もが自分らしく幸せに生きられるまち",
        "子育て・教育 いくつになっても育てあうまち",
        "健康・医療 健康がすぐそばにあるまち",
        "コミュニティ 多様な力でつくるまち",
        "防災・安全 つながりと備えが安心を生むまち",
        "都市基盤・まちづくり 誰もが暮らしを愛せるまち",
        "産業振興 失敗を恐れない挑戦者を応援するまち",
        "観光・文化 ワクワクがあふれ出すまち",
        "海洋 可能性に満ちた海を活用するまち",
        "環境 「自分ごと」の意識が未来を守るまち",
    ]
    assert all(goal["measures"] == [] for goal in goals)


def test_yokosuka_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "142018"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/yokosuka_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 54
    assert queue["summary"]["pending_record_review_count"] == 13
    assert queue["summary"]["next_official_code"] == "352039"


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
