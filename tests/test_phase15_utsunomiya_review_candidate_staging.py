"""Safety tests for Utsunomiya Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/utsunomiya-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/utsunomiya-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_utsunomiya_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "utsunomiya-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "092010"
    assert candidate["name_ja"] == "宇都宮市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/utsunomiya-city/source_inventory.json"
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


def test_utsunomiya_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.utsunomiya.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-15"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_utsunomiya_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 1
    record = fiscal_records[0]
    assert record["municipality_id"] == "jp-local-092010"
    assert record["fiscal_year"] == 2026
    assert record["account_type"] == "general"
    assert record["stage"] == "initial_budget"
    assert record["metric"] == "total_expenditure"
    assert record["amount_yen"] == 246550000000
    assert record["review_status"] == "needs_review"
    # FY2024 settlement amounts were not extracted from the audit-opinion
    # PDF, so no settlement record may be invented for this candidate.
    assert all(rec["stage"] != "settlement" for rec in fiscal_records)

    packets = package["evidence_packets"]
    assert {pkt["subject_id"] for pkt in packets} == {
        "jp-local-092010-fiscal-2026-total-expenditure",
        "utsunomiya-settlement-audit-2024",
    }
    assert all(pkt["review_status"] == "needs_review" for pkt in packets)
    assert all(pkt["claims"] for pkt in packets)

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    assert decisions["utsunomiya-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )


def test_utsunomiya_promotion_is_reflected_in_queue_state():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "092010"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/utsunomiya_phase15_completion.json"
    assert (ROOT / item["completion_path"]).is_file()
    assert queue["summary"]["reviewed_complete_count"] == 10
    assert queue["summary"]["pending_record_review_count"] == 57
    assert queue["summary"]["next_official_code"] == "072044"


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
