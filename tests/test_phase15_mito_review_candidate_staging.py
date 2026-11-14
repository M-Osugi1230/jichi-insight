"""Non-public Phase 15 Mito scaffold contract tests."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/mito-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/mito-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_mito_candidate_schema_and_review_boundaries():
    candidate = read(CANDIDATE)
    validator = Draft202012Validator(read(SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(candidate)) == []
    assert candidate["official_code"] == "082015"
    assert candidate["name_ja"] == "水戸市"
    assert candidate["package_state"] == "scaffold"
    assert candidate["status"] == "review_candidate"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["human_review"]["reviewed_at"] is None
    assert candidate["publication"]["eligible"] is False


def test_mito_source_catalog_matches_existing_inventory():
    candidate = read(CANDIDATE)
    inventory = read(INVENTORY)
    sources = candidate["candidate_package"]["source_catalog"]["sources"]
    assert len(sources) == len(inventory["sources"]) == 4
    assert {(s["id"], s["official_url"]) for s in sources} == {
        (s["id"], s["official_url"]) for s in inventory["sources"]
    }
    assert all(
        s["official_url"].startswith("https://www.city.mito.lg.jp/")
        for s in sources
    )
    assert all(
        s["verification_status"] == "inventory_only_pending_primary_source_review"
        for s in sources
    )
    package = candidate["candidate_package"]
    assert package["fiscal_records"] == []
    assert package["evidence_packets"] == []
    plan = package["policy_structure"]["current_plan"]
    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2033
    layers = {s["id"]: s for s in sources}
    assert (
        layers["mito-implementation-2026-2028"]["effective_period"]
        == "2026年度～2028年度"
    )
    assert layers["mito-budget-2026"]["fiscal_year"] == 2026
    assert layers["mito-settlement-2024"]["fiscal_year"] == 2024


def test_mito_stays_pending_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        x for x in queue["execution_queue"] if x["official_code"] == "082015"
    )
    assert item["status"] == "pending_record_review"
    assert not item.get("completion_path")
    assert queue["summary"]["reviewed_complete_count"] < 67


def test_candidate_directory_not_imported_by_public_web():
    violations = []
    for path in WEB_ROOT.rglob("*"):
        if (
            path.is_file()
            and path.suffix in {".ts", ".tsx", ".js", ".mjs"}
            and "data/candidates" in path.read_text(encoding="utf-8")
        ):
            violations.append(str(path.relative_to(ROOT)))
    assert violations == []
