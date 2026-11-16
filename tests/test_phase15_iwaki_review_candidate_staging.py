"""Safety tests for Iwaki Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/iwaki-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/iwaki-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_iwaki_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "iwaki-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "072044"
    assert candidate["name_ja"] == "いわき市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/iwaki-city/source_inventory.json"
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


def test_iwaki_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.iwaki.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-15"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_iwaki_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-072044-fiscal-2026-total-expenditure",
        "jp-local-072044-fiscal-2024-total-revenue",
        "jp-local-072044-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-072044" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted (原案可決) as bill No. 35 at
    # the February regular council session of Reiwa 8 (vote on
    # 2026-03-12), so it must not be labelled as a draft proposal
    # (予算案). The amount is the exact sen-yen figure stated in
    # Article 1 of the budget book (議案第35号).
    budget = by_id["jp-local-072044-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 159490126000

    # The FY2024 settlement totals are the exact yen-level figures in
    # the original settlement book. Their difference must equal the
    # published carry-over balance of 7,123,787,361 yen.
    revenue = by_id["jp-local-072044-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 162539391275
    expenditure = by_id["jp-local-072044-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 155415603914
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 7123787361

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

    # The FY2026 budget claim must record the enactment: bill No. 35,
    # passed as proposed on 2026-03-12.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-072044-fiscal-2026-total-expenditure"
    )
    assert "議案第35号" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]
    assert "議案第35号" in budget["note"]
    assert "令和8年3月12日" in budget["note"]

    # The FY2024 settlement was certified (認定) as bill No. 18
    # (議案第18号) on 2025-12-19 after continued review in the October
    # session, confirmed from the settlement book itself and the
    # council's official vote-result list.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-072044-fiscal-2024-total-revenue"
    )
    assert "議案第18号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年12月19日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "議案第18号" in revenue["note"]
    assert "議案第18号" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # Iwaki's framework has no fixed plan period, so no record may
    # invent one; the FY2024 settlement linkage to individual
    # management-guideline projects stays explicitly not assessable.
    assert decisions["iwaki-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    framework = next(
        rec for rec in plan_review["records"]
        if rec["id"] == "iwaki-policy-framework-identity"
    )
    assert framework["value"] == "固定の計画期間なし（終期を定めない）"

    # The current framework is the no-fixed-end 基本方針, NOT a
    # conventional fixed-period comprehensive plan: start and end
    # fiscal years must stay null.
    current_framework = package["policy_structure"]["current_framework"]
    assert current_framework["title"] == "いわき市まちづくりの基本方針"
    assert current_framework["period_status"] == "no_fixed_end"
    assert current_framework["start_fiscal_year"] is None
    assert current_framework["end_fiscal_year"] is None
    # Only the framework of the FY2026 management guideline (its five
    # pillars) is recorded; individual projects are not enumerated.
    layers = {
        layer["layer"]: layer
        for layer in current_framework["annual_layers"]
    }
    assert layers["management_guideline"]["fiscal_year"] == 2026
    assert layers["management_guideline"]["pillars"] == [
        "次世代を育てる",
        "命・暮らしを守る",
        "まちの魅力を高める",
        "豊かさを創る",
        "構造改革・DX推進事業",
    ]


def test_iwaki_promotion_is_reflected_in_queue_state():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "072044"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/iwaki_phase15_completion.json"
    assert (ROOT / item["completion_path"]).is_file()
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
