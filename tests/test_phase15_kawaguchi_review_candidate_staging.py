"""Safety tests for Kawaguchi Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/kawaguchi-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/kawaguchi-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kawaguchi_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "kawaguchi-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "112038"
    assert candidate["name_ja"] == "川口市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/kawaguchi-city/source_inventory.json"
    )
    assert (ROOT / candidate["source_inventory_path"]).is_file()
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-15"
    assert candidate["human_review"]["reviewer_note"]
    assert "公開責任者" in candidate["human_review"]["reviewer_note"]
    assert candidate["publication"]["eligible"] is False


def test_kawaguchi_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.kawaguchi.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-15"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_kawaguchi_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-112038-fiscal-2026-total-expenditure",
        "jp-local-112038-fiscal-2024-total-revenue",
        "jp-local-112038-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-112038" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted (原案可決) as bill No. 18 at
    # the March regular council session of Reiwa 8, so it must not be
    # labelled as a draft proposal (予算案). The amount is the exact
    # sen-yen figure stated in Article 1 of the budget book (議案第18号).
    budget = by_id["jp-local-112038-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 256970000000

    # The FY2024 settlement totals are the exact yen-level figures in the
    # original settlement book. Their difference must equal the published
    # carry-over balance of 11,856,967,084 yen.
    revenue = by_id["jp-local-112038-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 259800531831
    expenditure = by_id["jp-local-112038-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 247943564747
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 11856967084

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

    # The FY2024 settlement was certified (認定) as bill No. 183
    # (議案第183号) on 2025-11-28 after continued review in the September
    # session, confirmed from the official bill book, the September
    # vote-result table, the mayor's address and public notice No. 848.
    # The former open question about the certification bill number and
    # date is therefore closed; only the December vote-result table's
    # 議決番号 remains unconfirmed.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-112038-fiscal-2024-total-revenue"
    )
    assert "議案第183号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年11月28日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "決算の認定に係る議案番号・議決日の確認。" not in (
        revenue_packet["open_questions"]
    )
    assert any(
        "議決番号は未確認" in question
        for question in revenue_packet["open_questions"]
    )
    assert "議案第183号" in revenue["note"]
    assert "議案第183号" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 belongs to the previous (fifth) plan period, so its linkage
    # to the sixth plan must stay explicitly not assessable.
    assert decisions["kawaguchi-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec for rec in plan_review["records"]
        if rec["id"] == "kawaguchi-current-plan-period"
    )
    assert period["value"] == "2026年度～2035年度"

    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第6次川口市総合計画"
    assert current_plan["start_fiscal_year"] == 2026
    assert current_plan["end_fiscal_year"] == 2035
    # Only the framework of the eight official "めざす姿" is recorded;
    # individual measures are not enumerated in this candidate.
    assert len(current_plan["basic_goals"]) == 8
    assert {goal["name_ja"] for goal in current_plan["basic_goals"]} == {
        "健康で、自分らしく生き生きと暮らせるまち",
        "誰もがお互いを認め合い、安心して暮らせるまち",
        "こどもをみんなで育み、こどもが輝き活躍するまち",
        "学びとスポーツ・文化に親しみ、自己実現ができるまち",
        "にぎわいと魅力があり、伝統と未来が響き合うまち",
        "都市と自然が調和した、うるおいとやすらぎのあるまち",
        "誰もが安全で快適に暮らせるまち",
        "持続可能で自立したまち",
    }
    assert all(goal["measures"] == [] for goal in current_plan["basic_goals"])


def test_kawaguchi_promotion_is_reflected_in_queue_state():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "112038"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/kawaguchi_phase15_completion.json"
    assert (ROOT / item["completion_path"]).is_file()
    assert queue["summary"]["reviewed_complete_count"] == 45
    assert queue["summary"]["pending_record_review_count"] == 22
    assert queue["summary"]["next_official_code"] == "282049"


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
