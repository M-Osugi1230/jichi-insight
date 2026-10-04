from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/akita-city/review_candidate.json"
CANDIDATE_SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_akita_candidate_staging_contract_validates():
    candidate = load(CANDIDATE)

    assert validate(CANDIDATE_SCHEMA, candidate) == []
    assert candidate["official_code"] == "052019"
    assert candidate["name_ja"] == "秋田市"
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["publication"]["eligible"] is False


def test_akita_candidate_does_not_promote_queue_state():
    queue = load(QUEUE)
    akita_row = next(
        item for item in queue["execution_queue"]
        if item["official_code"] == "052019"
    )

    assert akita_row["status"] == "pending_record_review"
    assert not akita_row.get("completion_path")

    morioka_row = next(
        item for item in queue["execution_queue"]
        if item["official_code"] == "032018"
    )

    assert morioka_row["status"] == "review_in_progress"
    assert not morioka_row.get("completion_path")


def test_candidate_staging_is_not_referenced_by_public_web_source():
    forbidden = "data/candidates"
    hits: list[str] = []

    for path in WEB_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx", ".js", ".mjs"}:
            continue
        if forbidden in path.read_text(encoding="utf-8"):
            hits.append(str(path.relative_to(ROOT)))

    assert hits == []


def test_prepared_akita_candidate_retains_human_boundary_and_evidence_shape():
    candidate = load(CANDIDATE)
    assert candidate["package_state"] == "prepared"

    package = candidate["candidate_package"]
    source_catalog = package["source_catalog"]
    plan_review = package["plan_review"]
    policy_structure = package["policy_structure"]
    progress_review = package["progress_review"]
    fiscal_records = package["fiscal_records"]
    evidence_packets = package["evidence_packets"]

    # Source Catalog assertions
    assert source_catalog["official_code"] == "052019"
    assert source_catalog["name_ja"] == "秋田市"
    assert len(source_catalog["sources"]) >= 5
    assert all(
        source["official_url"].startswith("https://")
        for source in source_catalog["sources"]
    )
    assert all(source["evidence_location"] for source in source_catalog["sources"])
    assert all(source["use_boundary"] for source in source_catalog["sources"])

    # Plan Review assertions
    assert plan_review["official_code"] == "052019"
    assert plan_review["name_ja"] == "秋田市"
    assert plan_review["review_status"] == "pending_record_review"
    assert len(plan_review["records"]) >= 4
    assert all(
        record["decision"] in {"needs_review", "not_assessable"}
        for record in plan_review["records"]
    )

    # Policy Structure assertions
    assert policy_structure["official_code"] == "052019"
    assert policy_structure["name_ja"] == "秋田市"
    current_plan = policy_structure["current_plan"]
    assert current_plan["start_fiscal_year"] == 2026
    assert current_plan["end_fiscal_year"] == 2030
    assert len(current_plan["basic_goals"]) == 4
    total_measures = sum(
        len(goal["measures"]) for goal in current_plan["basic_goals"]
    )
    assert total_measures == 12
    assert len(current_plan["management_principles"]) == 4

    # Progress Review assertions
    assert progress_review["official_code"] == "052019"
    assert progress_review["name_ja"] == "秋田市"
    assert progress_review["review_status"] == "review_candidate_staging"

    # Fiscal Records & Evidence Packets assertions
    assert len(fiscal_records) >= 3
    assert all(
        rec["municipality_id"] == "jp-local-052019" and rec["review_status"] == "needs_review"
        for rec in fiscal_records
    )

    assert len(evidence_packets) >= 3
    assert all(
        pkt["review_status"] == "needs_review"
        for pkt in evidence_packets
    )

    # Quality Boundaries & Deferred Depth assertions
    assert len(candidate["quality_boundaries"]) >= 4
    assert len(candidate["deferred_depth"]) >= 3

    # Human Review & Publication boundaries
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["publication"]["eligible"] is False
