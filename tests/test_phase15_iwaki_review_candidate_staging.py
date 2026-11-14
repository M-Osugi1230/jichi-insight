"""Safety tests for Iwaki Phase 15 non-public review scaffold."""

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


def test_iwaki_scaffold_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "iwaki-phase15-review-candidate"
    assert candidate["official_code"] == "072044"
    assert candidate["name_ja"] == "いわき市"
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "scaffold"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["human_review"]["reviewed_at"] is None
    assert candidate["publication"]["eligible"] is False


def test_iwaki_sources_match_existing_official_inventory_without_invented_values():
    candidate = read(CANDIDATE)
    inventory = read(INVENTORY)
    sources = candidate["candidate_package"]["source_catalog"]["sources"]
    expected = inventory["sources"]
    assert len(sources) == len(expected) == 4
    assert {source["id"] for source in sources} == {source["id"] for source in expected}
    actual_urls = {(source["id"], source["official_url"]) for source in sources}
    assert actual_urls == {
        (source["id"], source["official_url"]) for source in expected
    }
    assert all(
        source["official_url"].startswith("https://www.city.iwaki.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "inventory_only_pending_primary_source_review"
        for source in sources
    )
    package = candidate["candidate_package"]
    assert package["fiscal_records"] == []
    assert package["evidence_packets"] == []
    assert package["policy_structure"]["current_framework"]["start_fiscal_year"] is None
    assert package["policy_structure"]["current_framework"]["end_fiscal_year"] is None
    assert (
        package["policy_structure"]["current_framework"]["period_status"]
        == "verified_no_fixed_end"
    )
    layers = {source["id"]: source.get("fiscal_year") for source in sources}
    assert layers["iwaki-management-guideline-2026"] == 2026
    assert layers["iwaki-budget-2026"] == 2026
    assert layers["iwaki-settlement-2024"] == 2024


def test_iwaki_is_still_pending_in_canonical_queue():
    queue = read(QUEUE)
    item = next(row for row in queue["execution_queue"] if row["official_code"] == "072044")
    assert item["status"] == "pending_record_review"
    assert item["completion_path"] is None
    assert queue["summary"]["reviewed_complete_count"] < queue["summary"]["target_count"]


def test_public_web_does_not_import_candidate_staging():
    violations = []
    for path in WEB_ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".ts", ".tsx", ".js", ".mjs"}:
            if "data/candidates" in path.read_text(encoding="utf-8"):
                violations.append(str(path.relative_to(ROOT)))
    assert violations == []
