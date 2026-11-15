"""Safety tests for Takasaki Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/takasaki-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/takasaki-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_takasaki_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "takasaki-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "102024"
    assert candidate["name_ja"] == "高崎市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/takasaki-city/source_inventory.json"
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


def test_takasaki_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.takasaki.gunma.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-15"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_takasaki_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-102024-fiscal-2026-total-expenditure",
        "jp-local-102024-fiscal-2024-total-revenue",
        "jp-local-102024-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-102024" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted (可決) by the March council
    # session, so it must not be labelled as a draft proposal (予算案).
    budget = by_id["jp-local-102024-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 175220000000

    # The FY2024 settlement totals were certified (認定). The candidate
    # originally carried the settlement summary page's man-yen-rounded
    # values; they were corrected at promotion time to the verified
    # thousand-yen values from the comprehensive external audit report.
    revenue = by_id["jp-local-102024-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 183362219000
    assert "訂正" in revenue["note"]
    expenditure = by_id["jp-local-102024-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 177037888000
    assert "訂正" in expenditure["note"]

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

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    assert decisions["takasaki-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec for rec in plan_review["records"]
        if rec["id"] == "takasaki-current-plan-period"
    )
    assert period["value"] == "2018年度～2027年度"

    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "高崎市第6次総合計画"
    assert current_plan["start_fiscal_year"] == 2018
    assert current_plan["end_fiscal_year"] == 2027
    assert len(current_plan["basic_goals"]) == 4
    assert sum(len(goal["measures"]) for goal in current_plan["basic_goals"]) == 38


def test_takasaki_promotion_is_reflected_in_queue_state():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "102024"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/takasaki_phase15_completion.json"
    assert (ROOT / item["completion_path"]).is_file()
    assert queue["summary"]["reviewed_complete_count"] == 20
    assert queue["summary"]["pending_record_review_count"] == 47
    assert queue["summary"]["next_official_code"] == "132012"


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
